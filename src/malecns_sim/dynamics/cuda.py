"""Optional event-oriented CuPy backend for the Task 005 LIF model."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from threading import Lock
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
    _freeze,
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


_ORDERED_SCHEDULE_SOURCE = r"""
extern "C" __global__ void schedule_ordered(
    const bool* fired, const bool* silenced,
    const long long* offsets, const int* sources,
    const long long* ordinals, const double* weights,
    double* pending, int* counts, long long* queued,
    long long n, long long slot
) {
    long long target = (long long)blockDim.x * blockIdx.x + threadIdx.x;
    if (target >= n) return;
    long long index = slot * n + target;
    double value = pending[index];
    int count = counts[index];
    long long added = 0;
    for (long long i = offsets[target]; i < offsets[target + 1]; ++i) {
        int source = sources[i];
        if (fired[source] && !silenced[source]) {
            value += weights[ordinals[i]];
            ++count;
            ++added;
        }
    }
    pending[index] = value;
    counts[index] = count;
    queued[target] = added;
}
"""


@dataclass(frozen=True, slots=True)
class _GPUBacking:
    """Shared static buffers and serialized device execution resources."""

    graph: CudaGraph
    incoming_offsets: object
    incoming_sources: object
    incoming_ordinals: object
    stream: object
    kernel: object
    lock: object = field(default_factory=Lock)


@dataclass(slots=True)
class _GPULifetime:
    backing: _GPUBacking | None = None
    closed: bool = False
    failed: bool = False


@dataclass(slots=True)
class GPUSimulationState:
    """Private device dynamics retained across calls; close is idempotent.

    Like CPU SimulationState, arrays are observable for explicit inspection.
    Callers must not replace/mutate buffers, ownership or canonical time.
    """

    runtime_identity: tuple[str, str, float]
    device_id: int
    timestep: int
    v_mV: object
    g_mV: object
    refractory_until: object
    pending: object
    pending_event_counts: object
    _owner: object = field(repr=False)
    _backing: _GPUBacking | None = field(repr=False)
    status: str = "ready"

    def close(self) -> None:
        """Drop only this state's buffers, never shared/global pool storage."""
        backing = self._backing
        if backing is None:
            return
        if not backing.lock.acquire(blocking=False):
            raise RuntimeError("GPU runtime is busy")
        try:
            with _cupy().cuda.Device(self.device_id):
                backing.stream.synchronize()
        finally:
            self.status = "released"
            self.v_mV = self.g_mV = self.refractory_until = None
            self.pending = self.pending_event_counts = None
            self._backing = None
            backing.lock.release()


@dataclass(frozen=True, slots=True)
class GPUPreparedRuntime:
    """CPU-isomorphic resumable seam with device-specific concrete storage.

    The CPU concrete state assumes NumPy buffers and has no device lifecycle;
    this backend therefore uses separate concrete types with the same public
    initial_state/advance boundary. Static buffers are never written by advance.
    """

    projection: EffectiveSignedProjection
    parameters: LIFParameters = REFERENCE_LIF_PARAMETERS
    dt_ms: float = 0.1
    device_id: int = field(init=False)
    backend_identity: tuple[str, str, int] = field(init=False)
    delay_steps: int = field(init=False)
    refractory_steps: int = field(init=False)
    ring_size: int = field(init=False)
    _coefficients: tuple[float, float, float] = field(init=False, repr=False)
    _owner: object = field(default_factory=object, init=False, repr=False)
    _lifetime: _GPULifetime = field(default_factory=_GPULifetime, init=False, repr=False)

    def __post_init__(self) -> None:
        p = self.projection
        parameters = self.parameters
        delay, refractory = parameters.grid_steps(self.dt_ms)
        if not np.isclose(p.synaptic_weight_mV,
                          parameters.synaptic_weight_per_anatomical_synapse_mV,
                          rtol=0.0, atol=1e-15):
            raise ValueError("projection synaptic weight does not match LIF parameters")
        n, e = int(p.neuron_ids.size), int(p.outgoing_targets.size)
        limit = np.iinfo(np.int32).max
        if n > limit or e > limit:
            raise ValueError("GPU CSR exceeds int32 index bounds")
        if (p.outgoing_indptr.dtype.kind not in "iu" or p.outgoing_targets.dtype.kind not in "iu"
                or p.outgoing_indptr.shape != (n + 1,) or p.outgoing_indptr[0] != 0
                or p.outgoing_indptr[-1] != e or np.any(np.diff(p.outgoing_indptr) < 0)
                or np.any(p.outgoing_targets < 0) or np.any(p.outgoing_targets >= n)
                or p.outgoing_weights_mV.shape != (e,)
                or not np.all(np.isfinite(p.outgoing_weights_mV))):
            raise ValueError("invalid GPU CSR topology or weights")
        if delay + 1 > np.iinfo(np.int64).max or refractory > np.iinfo(np.int64).max:
            raise ValueError("GPU delay/refractory exceeds int64 bounds")
        sources = np.repeat(np.arange(n, dtype=np.int32), np.diff(p.outgoing_indptr))
        # Stable target grouping retains ascending source/outgoing CSR ordinal.
        ordinals = np.argsort(p.outgoing_targets, kind="stable").astype(np.int64)
        incoming_counts = np.bincount(p.outgoing_targets, minlength=n)
        # R=D+1 makes each enqueue reuse the just-cleared slot. Each slot
        # contains at most one step's incoming edges, bounded by E <= INT_MAX.
        offsets = np.concatenate(([0], np.cumsum(incoming_counts, dtype=np.int64)))
        cp = _cupy()
        device = int(cp.cuda.runtime.getDevice())
        stream = cp.cuda.Stream(non_blocking=True)
        with stream:
            graph = CudaGraph(cp.asarray(p.outgoing_indptr, dtype=cp.int32),
                              cp.asarray(p.outgoing_targets, dtype=cp.int32),
                              cp.asarray(p.outgoing_weights_mV, dtype=cp.float64), n, e)
            backing = _GPUBacking(graph, cp.asarray(offsets, dtype=cp.int64),
                                  cp.asarray(sources[ordinals], dtype=cp.int32),
                                  cp.asarray(ordinals, dtype=cp.int64), stream,
                                  cp.RawKernel(_ORDERED_SCHEDULE_SOURCE, "schedule_ordered",
                                               options=("--fmad=false",)))
            backing.kernel.compile()
        stream.synchronize()
        exp_m = float(np.exp(-self.dt_ms / parameters.tau_membrane_ms))
        exp_s = float(np.exp(-self.dt_ms / parameters.tau_synapse_ms))
        coefficient = ((self.dt_ms / parameters.tau_membrane_ms) * exp_m
                       if np.isclose(parameters.tau_membrane_ms, parameters.tau_synapse_ms)
                       else (exp_s - exp_m) / (1.0 - parameters.tau_membrane_ms / parameters.tau_synapse_ms))
        for name, value in (("device_id", device), ("backend_identity", ("cupy", cp.__version__, device)),
                            ("delay_steps", delay), ("refractory_steps", refractory),
                            ("ring_size", max(delay + 1, 1)), ("_coefficients", (exp_m, exp_s, coefficient))):
            object.__setattr__(self, name, value)
        self._lifetime.backing = backing

    @property
    def identity(self) -> tuple[str, str, float]:
        return (self.projection.fingerprint, self.parameters.fingerprint, self.dt_ms)

    def _checked_backing(self) -> _GPUBacking:
        if self._lifetime.closed or self._lifetime.failed:
            raise RuntimeError("GPU runtime is closed or failed")
        cp = _cupy()
        if int(cp.cuda.runtime.getDevice()) != self.device_id:
            raise ValueError("GPU runtime device mismatch")
        return self._lifetime.backing

    def _execution_failure(self, exc: BaseException) -> None:
        # CUDA context-fatal errors prohibit further runtime device work.
        if getattr(exc, "status", None) in (700, 710, 719):
            self._lifetime.failed = True

    def initial_state(self) -> GPUSimulationState:
        backing = self._checked_backing()
        if not backing.lock.acquire(blocking=False):
            raise RuntimeError("GPU runtime is busy")
        cp, n = _cupy(), self.projection.neuron_ids.size
        try:
            if self._checked_backing() is not backing:
                raise RuntimeError("GPU runtime backing changed")
            with backing.stream:
                state = GPUSimulationState(
                    self.identity, self.device_id, 0,
                    cp.full(n, self.parameters.v_rest_mV, dtype=cp.float64),
                    cp.zeros(n, dtype=cp.float64), cp.full(n, -1, dtype=cp.int64),
                    cp.zeros((self.ring_size, n), dtype=cp.float64),
                    cp.zeros((self.ring_size, n), dtype=cp.int32), self._owner, backing)
            backing.stream.synchronize()
            return state
        except BaseException as exc:
            self._execution_failure(exc)
            raise
        finally:
            backing.lock.release()

    def close(self) -> None:
        """Reject future calls; live states retain backing until their close."""
        backing = self._lifetime.backing
        if backing is None:
            return
        if not backing.lock.acquire(blocking=False):
            raise RuntimeError("GPU runtime is busy")
        try:
            with _cupy().cuda.Device(self.device_id):
                backing.stream.synchronize()
        finally:
            self._lifetime.closed = True
            self._lifetime.backing = None
            backing.lock.release()

    def advance(self, state: GPUSimulationState, *, duration_ms: float,
                stimulus: ExplicitStimulus = ExplicitStimulus(),
                silenced_neuron_ids: Iterable[int] = (),
                trace_neuron_ids: Iterable[int] = ()) -> SimulationResult:
        """Validate local input, mutate retained device state, return host output."""
        backing = self._checked_backing()
        if (not isinstance(state, GPUSimulationState) or state._owner is not self._owner
                or state.runtime_identity != self.identity or state._backing is not backing):
            raise ValueError("state belongs to another GPU prepared runtime or is released")
        if state.status != "ready":
            raise RuntimeError("GPU state is released or failed")
        if state.device_id != self.device_id:
            raise ValueError("GPU state device mismatch")
        if not isinstance(stimulus, ExplicitStimulus):
            raise TypeError("advance requires explicit chunk-relative events")
        steps = _validate_duration(duration_ms, self.dt_ms)
        limit = np.iinfo(np.int64).max
        if (type(state.timestep) is not int or state.timestep < 0
                or state.timestep + steps + max(self.delay_steps, self.refractory_steps) > limit
                or (steps + self.ring_size) * self.projection.outgoing_targets.size > limit):
            raise ValueError("GPU timestep or event counter exceeds int64 bounds")
        ids = self.projection.neuron_ids
        _, fingerprint, batches, free = _stimulus_inputs(
            stimulus, duration_ms=duration_ms, dt_ms=self.dt_ms,
            parameters=self.parameters, neuron_ids=ids)
        silenced = validate_refractory_ids(silenced_neuron_ids, ids)
        trace = validate_refractory_ids(trace_neuron_ids, ids)
        packed = {}
        for step, (positions, _) in batches.items():
            unique, counts = np.unique(positions, return_counts=True)
            packed[step] = (unique, counts.astype(np.int64))
        if not backing.lock.acquire(blocking=False):
            raise RuntimeError("GPU runtime is busy")
        launched = False
        try:
            if self._checked_backing() is not backing:
                raise RuntimeError("GPU runtime backing changed")
            if state.status != "ready" or state._backing is not backing:
                raise RuntimeError("GPU state is released or failed")
            if state.timestep + steps + max(self.delay_steps, self.refractory_steps) > limit:
                raise ValueError("GPU timestep exceeds int64 bounds")
            launched = True
            with backing.stream:
                result = self._advance_device(state, steps, duration_ms, stimulus,
                                              fingerprint, packed, free, silenced, trace)
            backing.stream.synchronize()
            state.timestep += steps
            return result
        except BaseException as exc:
            if launched:
                state.status = "failed"
                self._execution_failure(exc)
            raise
        finally:
            backing.lock.release()

    def _advance_device(self, state, steps, duration_ms, stimulus, fingerprint,
                        packed, free, silenced, trace) -> SimulationResult:
        cp, p, parameters = _cupy(), self.projection, self.parameters
        backing, n, offset = state._backing, p.neuron_ids.size, state.timestep
        v, g, deadlines = state.v_mV, state.g_mV, state.refractory_until
        pending, pending_counts = state.pending, state.pending_event_counts
        free_mask, silenced_mask = cp.zeros(n, dtype=cp.bool_), cp.zeros(n, dtype=cp.bool_)
        free_mask[cp.asarray(free)] = True
        silenced_mask[cp.asarray(silenced)] = True
        trace_positions = cp.asarray(trace)
        trace_v = cp.empty((trace.size, steps + 1), dtype=cp.float64) if trace.size else None
        trace_g = cp.empty_like(trace_v) if trace.size else None
        if trace.size:
            trace_v[:, 0], trace_g[:, 0] = v[trace_positions], g[trace_positions]
        scratch_v, scratch_g = cp.empty_like(v), cp.empty_like(g)
        queued_by_target = cp.zeros(n, dtype=cp.int64)
        queued, delivered = cp.zeros(1, dtype=cp.int64), cp.zeros(1, dtype=cp.int64)
        spike_positions, spike_steps = [], []
        exp_m, exp_s, coefficient = self._coefficients
        weight = parameters.synaptic_weight_per_anatomical_synapse_mV if stimulus.weight_mV is None else stimulus.weight_mV
        device_events = {step: (cp.asarray(pos), cp.asarray(counts)) for step, (pos, counts) in packed.items()}
        for local_step in range(steps):
            step = offset + local_step
            allowed = (step > deadlines) | free_mask
            if local_step in device_events:
                positions, counts = device_events[local_step]
                admitted = allowed[positions]
                selected = positions[admitted]
                v[selected] += counts[admitted].astype(cp.float64) * weight
            slot = step % self.ring_size
            due, counts = pending[slot], pending_counts[slot]
            g[allowed] += due[allowed]
            delivered += cp.sum(counts, dtype=cp.int64)
            due.fill(0.0)
            counts.fill(0)
            # Separate ufunc stages preserve the frozen equation operation order.
            cp.subtract(v, parameters.v_rest_mV, out=scratch_v)
            cp.multiply(scratch_v, exp_m, out=scratch_v)
            cp.add(parameters.v_rest_mV, scratch_v, out=scratch_v)
            cp.multiply(g, coefficient, out=scratch_g)
            cp.add(scratch_v, scratch_g, out=scratch_v)
            cp.multiply(g, exp_s, out=scratch_g)
            v[allowed], g[allowed] = scratch_v[allowed], scratch_g[allowed]
            fired = allowed & (v > parameters.v_threshold_mV)
            positions = cp.flatnonzero(fired)
            if positions.size:
                spike_positions.append(positions)
                spike_steps.append(cp.full(positions.size, step + 1, dtype=cp.int64))
            v[fired], g[fired] = parameters.v_reset_mV, 0.0
            deadlines[fired] = step + 1 + self.refractory_steps
            if n:
                backing.kernel(((n + 255) // 256,), (256,),
                               (fired, silenced_mask, backing.incoming_offsets,
                                backing.incoming_sources, backing.incoming_ordinals,
                                backing.graph.weights_mV, pending, pending_counts,
                                queued_by_target, np.int64(n),
                                np.int64((step + 1 + self.delay_steps) % self.ring_size)))
                queued += cp.sum(queued_by_target, dtype=cp.int64)
            if trace.size:
                trace_v[:, local_step + 1], trace_g[:, local_step + 1] = v[trace_positions], g[trace_positions]
        positions = cp.asnumpy(cp.concatenate(spike_positions)) if spike_positions else np.empty(0, dtype=np.int64)
        times = cp.asnumpy(cp.concatenate(spike_steps)) if spike_steps else np.empty(0, dtype=np.int64)
        output_ids, times = _canonicalize_spike_events(p.neuron_ids[positions], times)
        counts = np.bincount(positions, minlength=n).astype(np.int64)
        trace_ids = p.neuron_ids[trace].copy()
        host_v = cp.asnumpy(trace_v) if trace.size else None
        host_g = cp.asnumpy(trace_g) if trace.size else None
        for array in (output_ids, times, counts, trace_ids, host_v, host_g):
            if array is not None:
                _freeze(array)
        digest = hashlib.sha256(b"malecns-sim-spike-result-v1" + output_ids.tobytes()
                                + times.tobytes() + counts.tobytes()).hexdigest()
        return SimulationResult(
            spike_neuron_ids=output_ids, spike_timesteps=times, spike_counts=counts,
            duration_ms=float(duration_ms), dt_ms=float(self.dt_ms),
            parameter_fingerprint=parameters.fingerprint,
            unsigned_graph_fingerprint=p.unsigned_graph_fingerprint,
            sign_policy_fingerprint=p.signed_policy_fingerprint,
            stimulus_fingerprint=fingerprint,
            simulation_fingerprint=_simulation_fingerprint(
                p, parameters, dt_ms=self.dt_ms, duration_ms=duration_ms,
                delay_steps=self.delay_steps, refractory_steps=self.refractory_steps,
                stimulus_fingerprint=fingerprint, silenced=tuple(int(p.neuron_ids[i]) for i in silenced)),
            spike_result_digest=digest, emitted_spike_count=int(output_ids.size),
            active_neuron_count=int(np.count_nonzero(counts)),
            queued_synaptic_event_count=int(cp.asnumpy(queued)[0]),
            delivered_synaptic_event_count=int(cp.asnumpy(delivered)[0]),
            trace_neuron_ids=trace_ids, trace_v_mV=host_v, trace_g_mV=host_g)


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
    silenced_neuron_ids_by_trial: Iterable[Iterable[int]] | None = None,
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
    per_trial_silenced_input = None if silenced_neuron_ids_by_trial is None else tuple(
        tuple(int(value) for value in values) for values in silenced_neuron_ids_by_trial
    )
    if per_trial_silenced_input is not None and len(per_trial_silenced_input) != batch_size:
        raise ValueError("per-trial silencing count must match stimulus count")
    trace_ids_input = tuple(trace_neuron_ids)
    if per_trial_silenced_input is not None and silenced_ids_input:
        raise ValueError("use either shared or per-trial silencing, not both")
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
    if per_trial_silenced_input is not None:
        for trial, trial_ids in enumerate(per_trial_silenced_input):
            trial_positions = validate_refractory_ids(trial_ids, ids) if trial_ids else np.empty(0, dtype=np.int64)
            if trial_positions.size:
                silenced_mask[trial, cp.asarray(trial_positions)] = True
    elif silenced.size:
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
        if per_trial_silenced_input is not None:
            silenced_ids = tuple(sorted(per_trial_silenced_input[trial]))
        else:
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
    silenced_neuron_ids_by_trial: Iterable[Iterable[int]] | None = None,
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
        silenced_neuron_ids_by_trial=silenced_neuron_ids_by_trial,
        trace_neuron_ids=trace_neuron_ids,
        collect_sparse_trace=collect_sparse_trace,
        cuda_graph=cuda_graph,
    )[0]
