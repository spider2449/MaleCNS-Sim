"""Optional event-oriented CuPy backend for the Task 005 LIF model."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from time import perf_counter
from typing import Iterable

import numpy as np

from malecns_sim.dynamics.lif import (
    EffectiveSignedProjection,
    LIFParameters,
    REFERENCE_LIF_PARAMETERS,
    SimulationResult,
    SparseTrace,
    _canonicalize_spike_events,
    _validate_duration,
)
from malecns_sim.dynamics.stimulus import (
    ExplicitStimulus,
    PoissonStimulus,
    schedule_events,
    validate_refractory_ids,
)


_SCHEDULE_KERNEL_SOURCE = r"""
extern "C" __global__ void schedule_active_edges(
    const bool* fired,
    const bool* silenced,
    const int* indptr,
    const int* targets,
    const double* weights,
    double* pending,
    int* pending_counts,
    unsigned long long* queued_counts,
    int batch_size,
    long long neuron_count,
    long long ring_size,
    long long event_slot
) {
    long long flat = (long long)blockDim.x * blockIdx.x + threadIdx.x;
    long long total = (long long)batch_size * neuron_count;
    if (flat >= total) return;
    long long trial = flat / neuron_count;
    long long source = flat - trial * neuron_count;
    if (!fired[flat] || silenced[trial * neuron_count + source]) return;
    long long start = indptr[source];
    long long end = indptr[source + 1];
    unsigned long long edge_count = (unsigned long long)(end - start);
    atomicAdd(&queued_counts[trial], edge_count);
    for (long long edge = start; edge < end; ++edge) {
        long long target = targets[edge];
        long long offset = ((trial * ring_size + event_slot) * neuron_count) + target;
        atomicAdd(&pending[offset], weights[edge]);
        atomicAdd(&pending_counts[offset], 1);
    }
}
"""

_SCHEDULE_KERNEL = None


@dataclass(frozen=True, slots=True)
class CudaGraph:
    """Device-resident graph arrays uploaded once for repeated trial use."""

    indptr: object
    indices: object
    weights_mV: object
    neuron_count: int
    edge_count: int


@dataclass(frozen=True, slots=True)
class CudaMemoryReport:
    """Measured device allocation delta for a named state configuration."""

    label: str
    free_before_bytes: int
    free_after_bytes: int
    allocated_delta_bytes: int
    theoretical_bytes: int
    status: str = "measured"


def _cupy():
    try:
        import cupy as cp
    except Exception as exc:
        raise RuntimeError("CuPy is not available") from exc
    return cp


def cuda_available() -> bool:
    """Return whether CuPy can enumerate at least one CUDA device."""

    try:
        cp = _cupy()
        return int(cp.cuda.runtime.getDeviceCount()) > 0
    except Exception:
        return False


def upload_graph(projection: EffectiveSignedProjection) -> tuple[CudaGraph, float]:
    """Upload only immutable CSR arrays and return synchronized elapsed time."""

    cp = _cupy()
    started = perf_counter()
    graph = CudaGraph(
        indptr=cp.asarray(projection.outgoing_indptr, dtype=cp.int32),
        indices=cp.asarray(projection.outgoing_targets, dtype=cp.int32),
        weights_mV=cp.asarray(projection.outgoing_weights_mV, dtype=cp.float64),
        neuron_count=int(projection.neuron_ids.size),
        edge_count=int(projection.outgoing_targets.size),
    )
    cp.cuda.Stream.null.synchronize()
    return graph, perf_counter() - started


def _schedule_kernel(cp):
    global _SCHEDULE_KERNEL
    if _SCHEDULE_KERNEL is None:
        _SCHEDULE_KERNEL = cp.RawKernel(_SCHEDULE_KERNEL_SOURCE, "schedule_active_edges")
    return _SCHEDULE_KERNEL


def measure_memory(
    projection: EffectiveSignedProjection,
    *,
    batch_size: int = 1,
    include_delay_buffers: bool = True,
) -> CudaMemoryReport:
    """Measure a state allocation after graph upload without running a trial."""

    cp = _cupy()
    graph, _ = upload_graph(projection)
    device = cp.cuda.Device()
    free_before, _ = device.mem_info
    n = graph.neuron_count
    delay_steps, _ = REFERENCE_LIF_PARAMETERS.grid_steps(0.1)
    ring_size = max(delay_steps + 1, 1)
    theoretical = 2 * batch_size * n * 8 + batch_size * n * 8
    if include_delay_buffers:
        theoretical += batch_size * ring_size * n * (8 + 4)
    if theoretical > int(free_before * 0.80):
        return CudaMemoryReport(
            label=f"batch={batch_size},delay={include_delay_buffers}",
            free_before_bytes=int(free_before),
            free_after_bytes=int(free_before),
            allocated_delta_bytes=0,
            theoretical_bytes=int(theoretical),
            status="skipped-theoretical-capacity",
        )
    v = cp.zeros((batch_size, n), dtype=cp.float64)
    g = cp.zeros((batch_size, n), dtype=cp.float64)
    refractory = cp.full((batch_size, n), -1, dtype=cp.int64)
    pending = cp.zeros((batch_size, ring_size, n), dtype=cp.float64) if include_delay_buffers else None
    pending_counts = cp.zeros((batch_size, ring_size, n), dtype=cp.int32) if include_delay_buffers else None
    cp.cuda.Stream.null.synchronize()
    free_after, _ = device.mem_info
    del v, g, refractory, pending, pending_counts, graph
    cp.get_default_memory_pool().free_all_blocks()
    cp.get_default_pinned_memory_pool().free_all_blocks()
    return CudaMemoryReport(
        label=f"batch={batch_size},delay={include_delay_buffers}",
        free_before_bytes=int(free_before),
        free_after_bytes=int(free_after),
        allocated_delta_bytes=int(free_before - free_after),
        theoretical_bytes=int(theoretical),
    )


def _stimulus_inputs(
    stimulus: ExplicitStimulus | PoissonStimulus | Iterable,
    *,
    duration_ms: float,
    dt_ms: float,
    parameters: LIFParameters,
    neuron_ids: np.ndarray,
) -> tuple[ExplicitStimulus, str, dict[int, tuple[np.ndarray, np.ndarray]], np.ndarray]:
    if isinstance(stimulus, PoissonStimulus):
        explicit = stimulus.generate(duration_ms, dt_ms, parameters.synaptic_weight_per_anatomical_synapse_mV)
        fingerprint = stimulus.fingerprint
    elif isinstance(stimulus, ExplicitStimulus):
        explicit = stimulus
        fingerprint = stimulus.fingerprint
    else:
        explicit = ExplicitStimulus(tuple(stimulus))
        fingerprint = explicit.fingerprint
    batches = schedule_events(
        explicit,
        neuron_positions=neuron_ids,
        duration_steps=_validate_duration(duration_ms, dt_ms),
        dt_ms=dt_ms,
    )
    refractory_free = validate_refractory_ids(explicit.refractory_free_neuron_ids, neuron_ids)
    return explicit, fingerprint, batches, refractory_free


def _simulation_fingerprint(
    projection: EffectiveSignedProjection,
    parameters: LIFParameters,
    *,
    dt_ms: float,
    duration_ms: float,
    delay_steps: int,
    refractory_steps: int,
    stimulus_fingerprint: str,
    silenced: tuple[int, ...],
) -> str:
    payload = {
        "unsigned": projection.unsigned_graph_fingerprint,
        "signed": projection.signed_policy_fingerprint,
        "effective": projection.fingerprint,
        "parameters": parameters.fingerprint,
        "dt_ms": dt_ms,
        "delay_steps": delay_steps,
        "refractory_steps": refractory_steps,
        "duration_ms": duration_ms,
        "stimulus": stimulus_fingerprint,
        "silenced": silenced,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def simulate_cuda_batch(
    projection: EffectiveSignedProjection,
    stimuli: Iterable[ExplicitStimulus | PoissonStimulus | Iterable],
    *,
    duration_ms: float,
    parameters: LIFParameters = REFERENCE_LIF_PARAMETERS,
    dt_ms: float = 0.1,
    silenced_neuron_ids: Iterable[int] = (),
    trace_neuron_ids: Iterable[int] = (),
    collect_sparse_trace: bool = False,
    cuda_graph: CudaGraph | None = None,
) -> tuple[SimulationResult, ...]:
    """Run independent trials while sharing the uploaded CSR graph.

    The delay ring is dense in neuron space but only active outgoing CSR rows
    are traversed by the scheduling kernel. This keeps the edge operation
    event-oriented instead of performing a full sparse matrix multiplication.
    """

    cp = _cupy()
    stimuli = tuple(stimuli)
    if not stimuli:
        raise ValueError("at least one stimulus is required")
    if not np.isclose(
        projection.synaptic_weight_mV,
        parameters.synaptic_weight_per_anatomical_synapse_mV,
        rtol=0.0,
        atol=1e-15,
    ):
        raise ValueError("projection synaptic weight does not match LIF parameters")
    steps = _validate_duration(duration_ms, dt_ms)
    delay_steps, refractory_steps = parameters.grid_steps(dt_ms)
    ids = np.asarray(projection.neuron_ids, dtype=np.int64)
    n = ids.size
    batch_size = len(stimuli)
    prepared = tuple(
        _stimulus_inputs(
            stimulus,
            duration_ms=duration_ms,
            dt_ms=dt_ms,
            parameters=parameters,
            neuron_ids=ids,
        )
        for stimulus in stimuli
    )
    input_weights = np.asarray(
        [parameters.synaptic_weight_per_anatomical_synapse_mV if item[0].weight_mV is None else item[0].weight_mV for item in prepared],
        dtype=np.float64,
    )
    silenced_ids_input = tuple(silenced_neuron_ids)
    trace_ids_input = tuple(trace_neuron_ids)
    silenced = validate_refractory_ids(silenced_ids_input, ids) if silenced_ids_input else np.empty(0, dtype=np.int64)
    trace_positions = validate_refractory_ids(trace_ids_input, ids) if trace_ids_input else np.empty(0, dtype=np.int64)
    ring_size = max(delay_steps + 1, 1)
    graph = cuda_graph
    if graph is None:
        graph, _ = upload_graph(projection)
    kernel = _schedule_kernel(cp)
    v = cp.full((batch_size, n), parameters.v_rest_mV, dtype=cp.float64)
    g = cp.zeros((batch_size, n), dtype=cp.float64)
    refractory_until = cp.full((batch_size, n), -1, dtype=cp.int64)
    pending = cp.zeros((batch_size, ring_size, n), dtype=cp.float64)
    pending_counts = cp.zeros((batch_size, ring_size, n), dtype=cp.int32)
    refractory_free = cp.zeros((batch_size, n), dtype=cp.bool_)
    for trial, item in enumerate(prepared):
        if item[3].size:
            refractory_free[trial, cp.asarray(item[3])] = True
    silenced_mask = cp.zeros((batch_size, n), dtype=cp.bool_)
    if silenced.size:
        silenced_mask[:, cp.asarray(silenced)] = True
    trace_v = cp.empty((batch_size, trace_positions.size, steps + 1), dtype=cp.float64) if trace_positions.size else None
    trace_g = cp.empty((batch_size, trace_positions.size, steps + 1), dtype=cp.float64) if trace_positions.size else None
    sparse_timesteps = np.arange(steps, dtype=np.int64) if collect_sparse_trace else None
    sparse_delivered_counts = cp.zeros((batch_size, steps), dtype=cp.int64) if collect_sparse_trace else None
    sparse_delivered_weights = cp.zeros((batch_size, steps), dtype=cp.float64) if collect_sparse_trace else None
    sparse_delivered_abs_weights = cp.zeros((batch_size, steps), dtype=cp.float64) if collect_sparse_trace else None
    sparse_delivered_targets = cp.zeros((batch_size, steps), dtype=cp.int64) if collect_sparse_trace else None
    sparse_delivered_target_indices = cp.zeros((batch_size, steps), dtype=cp.int64) if collect_sparse_trace else None
    target_positions = cp.arange(n, dtype=cp.int64)
    if trace_positions.size:
        trace_v[:, :, 0] = v[:, cp.asarray(trace_positions)]
        trace_g[:, :, 0] = g[:, cp.asarray(trace_positions)]
    queued_counts = cp.zeros(batch_size, dtype=cp.uint64)
    delivered_counts = cp.zeros(batch_size, dtype=cp.int64)
    spike_flat_steps: list[object] = []
    spike_flat_positions: list[object] = []
    exp_m = math.exp(-dt_ms / parameters.tau_membrane_ms)
    exp_s = math.exp(-dt_ms / parameters.tau_synapse_ms)
    g_coefficient = (exp_s - exp_m) / (1.0 - parameters.tau_membrane_ms / parameters.tau_synapse_ms)
    threads = 256
    blocks = (batch_size * n + threads - 1) // threads
    for step in range(steps):
        direct_trial: list[int] = []
        direct_position: list[int] = []
        direct_values: list[float] = []
        for trial, item in enumerate(prepared):
            if step in item[2]:
                positions, _ = item[2][step]
                direct_trial.extend([trial] * positions.size)
                direct_position.extend(positions.tolist())
                direct_values.extend([input_weights[trial]] * positions.size)
        if direct_trial:
            d_trials = cp.asarray(direct_trial, dtype=cp.int64)
            d_positions = cp.asarray(direct_position, dtype=cp.int64)
            d_values = cp.asarray(direct_values, dtype=cp.float64)
            direct_allowed = (~(step <= refractory_until[d_trials, d_positions])) | refractory_free[d_trials, d_positions]
            cp.add.at(v, (d_trials[direct_allowed], d_positions[direct_allowed]), d_values[direct_allowed])
        slot = step % ring_size
        due = pending[:, slot, :]
        due_counts = pending_counts[:, slot, :]
        allowed = (step > refractory_until) | refractory_free
        if collect_sparse_trace:
            sparse_delivered_counts[:, step] = cp.sum(due_counts, axis=1, dtype=cp.int64)
            sparse_delivered_weights[:, step] = cp.sum(due, axis=1, dtype=cp.float64)
            sparse_delivered_abs_weights[:, step] = cp.sum(cp.abs(due), axis=1, dtype=cp.float64)
            sparse_delivered_targets[:, step] = cp.count_nonzero(due_counts, axis=1)
            sparse_delivered_target_indices[:, step] = cp.sum(
                due_counts * target_positions[None, :], axis=1, dtype=cp.int64
            )
        g = cp.where(allowed, g + due, g)
        delivered_counts += cp.sum(due_counts, axis=1, dtype=cp.int64)
        due.fill(0.0)
        due_counts.fill(0)
        updated_v = parameters.v_rest_mV + (v - parameters.v_rest_mV) * exp_m + g * g_coefficient
        updated_g = g * exp_s
        v = cp.where(allowed, updated_v, v)
        g = cp.where(allowed, updated_g, g)
        fired = allowed & (v > parameters.v_threshold_mV)
        flat = cp.flatnonzero(fired)
        if flat.size:
            spike_flat_positions.append(flat)
            spike_flat_steps.append(cp.full(flat.size, step + 1, dtype=cp.int64))
        v = cp.where(fired, parameters.v_reset_mV, v)
        g = cp.where(fired, 0.0, g)
        refractory_until = cp.where(fired, step + 1 + refractory_steps, refractory_until)
        event_slot = (step + 1 + delay_steps) % ring_size
        kernel(
            (blocks,),
            (threads,),
            (
                fired,
                silenced_mask,
                graph.indptr,
                graph.indices,
                graph.weights_mV,
                pending,
                pending_counts,
                queued_counts,
                batch_size,
                n,
                ring_size,
                event_slot,
            ),
        )
        if trace_positions.size:
            trace_v[:, :, step + 1] = v[:, cp.asarray(trace_positions)]
            trace_g[:, :, step + 1] = g[:, cp.asarray(trace_positions)]
    cp.cuda.Stream.null.synchronize()
    if spike_flat_positions:
        all_positions = cp.concatenate(spike_flat_positions)
        all_steps = cp.concatenate(spike_flat_steps)
    else:
        all_positions = cp.empty(0, dtype=cp.int64)
        all_steps = cp.empty(0, dtype=cp.int64)
    all_positions_host = cp.asnumpy(all_positions)
    all_steps_host = cp.asnumpy(all_steps)
    queued_host = cp.asnumpy(queued_counts).astype(np.int64)
    delivered_host = cp.asnumpy(delivered_counts)
    sparse_delivered_counts_host = cp.asnumpy(sparse_delivered_counts) if collect_sparse_trace else None
    sparse_delivered_weights_host = cp.asnumpy(sparse_delivered_weights) if collect_sparse_trace else None
    sparse_delivered_abs_weights_host = cp.asnumpy(sparse_delivered_abs_weights) if collect_sparse_trace else None
    sparse_delivered_targets_host = cp.asnumpy(sparse_delivered_targets) if collect_sparse_trace else None
    sparse_delivered_target_indices_host = cp.asnumpy(sparse_delivered_target_indices) if collect_sparse_trace else None
    results: list[SimulationResult] = []
    for trial, item in enumerate(prepared):
        trial_mask = (all_positions_host // n) == trial
        flat_positions = all_positions_host[trial_mask] % n
        output_steps = all_steps_host[trial_mask]
        output_ids = ids[flat_positions]
        output_ids, output_steps = _canonicalize_spike_events(output_ids, output_steps)
        counts = np.bincount(flat_positions, minlength=n).astype(np.int64)
        digest = hashlib.sha256(
            b"malecns-sim-spike-result-v1" + output_ids.tobytes() + output_steps.tobytes() + counts.tobytes()
        ).hexdigest()
        silenced_ids = tuple(int(ids[position]) for position in silenced) if silenced.size else ()
        simulation_fingerprint = _simulation_fingerprint(
            projection,
            parameters,
            dt_ms=dt_ms,
            duration_ms=duration_ms,
            delay_steps=delay_steps,
            refractory_steps=refractory_steps,
            stimulus_fingerprint=item[1],
            silenced=silenced_ids,
        )
        trace_v_host = cp.asnumpy(trace_v[trial]) if trace_v is not None else None
        trace_g_host = cp.asnumpy(trace_g[trial]) if trace_g is not None else None
        for array in (output_ids, output_steps, counts):
            array.flags.writeable = False
        trace_ids = ids[trace_positions].copy() if trace_positions.size else np.empty(0, dtype=np.int64)
        trace_ids.flags.writeable = False
        if trace_v_host is not None:
            trace_v_host.flags.writeable = False
            trace_g_host.flags.writeable = False
        sparse_trace = None
        if collect_sparse_trace:
            sparse_arrays = (
                sparse_timesteps.copy(),
                sparse_delivered_counts_host[trial],
                sparse_delivered_weights_host[trial],
                sparse_delivered_abs_weights_host[trial],
                sparse_delivered_targets_host[trial],
                sparse_delivered_target_indices_host[trial],
            )
            for array in sparse_arrays:
                array.flags.writeable = False
            sparse_trace = SparseTrace(*sparse_arrays)
        results.append(
            SimulationResult(
                spike_neuron_ids=output_ids,
                spike_timesteps=output_steps,
                spike_counts=counts,
                duration_ms=float(duration_ms),
                dt_ms=float(dt_ms),
                parameter_fingerprint=parameters.fingerprint,
                unsigned_graph_fingerprint=projection.unsigned_graph_fingerprint,
                sign_policy_fingerprint=projection.signed_policy_fingerprint,
                stimulus_fingerprint=item[1],
                simulation_fingerprint=simulation_fingerprint,
                spike_result_digest=digest,
                emitted_spike_count=int(output_ids.size),
                active_neuron_count=int(np.count_nonzero(counts)),
                queued_synaptic_event_count=int(queued_host[trial]),
                delivered_synaptic_event_count=int(delivered_host[trial]),
                trace_neuron_ids=trace_ids,
                trace_v_mV=trace_v_host,
                trace_g_mV=trace_g_host,
                sparse_trace=sparse_trace,
            )
        )
    return tuple(results)


def simulate_cuda(
    projection: EffectiveSignedProjection,
    *,
    duration_ms: float,
    stimulus: ExplicitStimulus | PoissonStimulus | Iterable = ExplicitStimulus(),
    parameters: LIFParameters = REFERENCE_LIF_PARAMETERS,
    dt_ms: float = 0.1,
    silenced_neuron_ids: Iterable[int] = (),
    trace_neuron_ids: Iterable[int] = (),
    collect_sparse_trace: bool = False,
    cuda_graph: CudaGraph | None = None,
) -> SimulationResult:
    """Run one trial on CUDA with the same public result shape as the CPU."""

    return simulate_cuda_batch(
        projection,
        (stimulus,),
        duration_ms=duration_ms,
        parameters=parameters,
        dt_ms=dt_ms,
        silenced_neuron_ids=silenced_neuron_ids,
        trace_neuron_ids=trace_neuron_ids,
        collect_sparse_trace=collect_sparse_trace,
        cuda_graph=cuda_graph,
    )[0]
