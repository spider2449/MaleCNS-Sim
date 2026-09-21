"""Deterministic NumPy reference implementation of the Shiu LIF model."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Iterable

import numpy as np

from malecns_sim.graph.signed import SignedAnatomicalConnectome, signed_graph_fingerprint
from malecns_sim.dynamics.stimulus import (
    ExplicitStimulus,
    PoissonStimulus,
    schedule_events,
    validate_refractory_ids,
)


def _finite(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True, slots=True)
class LIFParameters:
    """Immutable reference constants, expressed in mV and ms."""

    v_rest_mV: float = -52.0
    v_reset_mV: float = -52.0
    v_threshold_mV: float = -45.0
    tau_membrane_ms: float = 20.0
    tau_synapse_ms: float = 5.0
    refractory_period_ms: float = 2.2
    synaptic_delay_ms: float = 1.8
    synaptic_weight_per_anatomical_synapse_mV: float = 0.275

    def __post_init__(self) -> None:
        for field_name in (
            "v_rest_mV",
            "v_reset_mV",
            "v_threshold_mV",
            "tau_membrane_ms",
            "tau_synapse_ms",
            "refractory_period_ms",
            "synaptic_delay_ms",
            "synaptic_weight_per_anatomical_synapse_mV",
        ):
            value = _finite(getattr(self, field_name), field_name)
            object.__setattr__(self, field_name, value)
        if self.tau_membrane_ms <= 0.0 or self.tau_synapse_ms <= 0.0:
            raise ValueError("time constants must be positive")
        if self.refractory_period_ms < 0.0 or self.synaptic_delay_ms < 0.0:
            raise ValueError("delay and refractory period must be non-negative")
        if self.synaptic_weight_per_anatomical_synapse_mV < 0.0:
            raise ValueError("synaptic weight must be non-negative")

    def grid_steps(self, dt_ms: float) -> tuple[int, int]:
        dt = _finite(dt_ms, "dt_ms")
        if dt <= 0.0:
            raise ValueError("dt_ms must be positive")
        return (
            _exact_steps(self.synaptic_delay_ms, dt, "synaptic delay"),
            _exact_steps(self.refractory_period_ms, dt, "refractory period"),
        )

    @property
    def fingerprint(self) -> str:
        payload = {
            "kind": "shiu-reference-lif-parameters-v1",
            "v_rest_mV": self.v_rest_mV,
            "v_reset_mV": self.v_reset_mV,
            "v_threshold_mV": self.v_threshold_mV,
            "tau_membrane_ms": self.tau_membrane_ms,
            "tau_synapse_ms": self.tau_synapse_ms,
            "refractory_period_ms": self.refractory_period_ms,
            "synaptic_delay_ms": self.synaptic_delay_ms,
            "synaptic_weight_per_anatomical_synapse_mV": self.synaptic_weight_per_anatomical_synapse_mV,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    # Short aliases keep the equations readable while the stored names retain
    # explicit units at the API boundary.
    @property
    def v_rest(self) -> float:
        return self.v_rest_mV

    @property
    def v_reset(self) -> float:
        return self.v_reset_mV

    @property
    def v_threshold(self) -> float:
        return self.v_threshold_mV

    @property
    def tau_membrane(self) -> float:
        return self.tau_membrane_ms

    @property
    def tau_synapse(self) -> float:
        return self.tau_synapse_ms

    @property
    def refractory_period(self) -> float:
        return self.refractory_period_ms

    @property
    def synaptic_delay(self) -> float:
        return self.synaptic_delay_ms


REFERENCE_LIF_PARAMETERS = LIFParameters()


def _exact_steps(value_ms: float, dt_ms: float, name: str) -> int:
    steps = int(round(value_ms / dt_ms))
    if not np.isclose(value_ms, steps * dt_ms, rtol=0.0, atol=1e-10):
        raise ValueError(f"{name}={value_ms} ms is not exactly representable at dt={dt_ms} ms")
    return steps


def linear_state_update(
    v_mV: np.ndarray | float,
    g_mV: np.ndarray | float,
    *,
    parameters: LIFParameters = REFERENCE_LIF_PARAMETERS,
    dt_ms: float = 0.1,
) -> tuple[np.ndarray | float, np.ndarray | float]:
    """Analytically integrate both coupled linear states over one timestep."""

    dt = _finite(dt_ms, "dt_ms")
    if dt <= 0.0:
        raise ValueError("dt_ms must be positive")
    exp_m = np.exp(-dt / parameters.tau_membrane_ms)
    exp_s = np.exp(-dt / parameters.tau_synapse_ms)
    if np.isclose(parameters.tau_membrane_ms, parameters.tau_synapse_ms):
        g_coefficient = (dt / parameters.tau_membrane_ms) * exp_m
    else:
        g_coefficient = (
            exp_s - exp_m
        ) / (1.0 - parameters.tau_membrane_ms / parameters.tau_synapse_ms)
    v_next = parameters.v_rest_mV + (np.asarray(v_mV) - parameters.v_rest_mV) * exp_m + np.asarray(g_mV) * g_coefficient
    g_next = np.asarray(g_mV) * exp_s
    if np.ndim(v_mV) == 0:
        return float(v_next), float(g_next)
    return v_next, g_next


@dataclass(frozen=True, slots=True)
class EffectiveSignedProjection:
    """Resolved simulation edges derived from, but not written into, anatomy."""

    neuron_ids: np.ndarray
    source_positions: np.ndarray
    target_positions: np.ndarray
    effective_weights_mV: np.ndarray
    included_anatomical_weight: int
    excluded_anatomical_weight: int
    excluded_unresolved_edge_count: int
    synaptic_weight_mV: float
    sign_policy_id: str
    resolution_policy_id: str
    unsigned_graph_fingerprint: str
    signed_policy_fingerprint: str
    fingerprint: str
    outgoing_indptr: np.ndarray
    outgoing_targets: np.ndarray
    outgoing_weights_mV: np.ndarray

    @classmethod
    def from_signed_connectome(
        cls, graph: SignedAnatomicalConnectome, *, synaptic_weight_mV: float = 0.275
    ) -> "EffectiveSignedProjection":
        weight = _finite(synaptic_weight_mV, "synaptic_weight_mV")
        if weight < 0.0:
            raise ValueError("synaptic weight must be non-negative")
        included = graph.signed_edge_mask
        connectome = graph.connectome
        source = np.searchsorted(connectome.neuron_ids, connectome.source_ids[included]).astype(np.int64)
        target = np.searchsorted(connectome.neuron_ids, connectome.target_ids[included]).astype(np.int64)
        effective = (
            connectome.synapse_counts[included].astype(np.float64) * graph.presynaptic_signs[included] * weight
        )
        order = np.lexsort((target, source))
        source, target, effective = source[order], target[order], effective[order]
        source_ids = connectome.source_ids[included]
        anatomical = connectome.synapse_counts[included]
        included_weight = int(anatomical.sum(dtype=np.int64))
        total_weight = int(connectome.synapse_counts.sum(dtype=np.int64))
        indptr = np.zeros(connectome.neuron_count + 1, dtype=np.int64)
        np.add.at(indptr, source + 1, 1)
        np.cumsum(indptr, out=indptr)
        arrays = [
            np.asarray(connectome.neuron_ids, dtype=np.int64),
            source,
            target,
            effective,
            indptr,
        ]
        digest = hashlib.sha256()
        digest.update(b"malecns-sim-effective-signed-projection-v1")
        for value in (graph.sign_policy_id, graph.resolution_policy_id, str(weight), signed_graph_fingerprint(graph)):
            encoded = value.encode("utf-8")
            digest.update(len(encoded).to_bytes(8, "little"))
            digest.update(encoded)
        for array in arrays:
            digest.update(str(array.dtype).encode("ascii"))
            digest.update(array.tobytes(order="C"))
        outgoing_targets = target.copy()
        outgoing_weights = effective.copy()
        for array in (source, target, effective, indptr, outgoing_targets, outgoing_weights):
            array.flags.writeable = False
        neuron_ids = np.asarray(connectome.neuron_ids, dtype=np.int64).copy()
        neuron_ids.flags.writeable = False
        return cls(
            neuron_ids=neuron_ids,
            source_positions=source,
            target_positions=target,
            effective_weights_mV=effective,
            included_anatomical_weight=included_weight,
            excluded_anatomical_weight=total_weight - included_weight,
            excluded_unresolved_edge_count=int((~included).sum()),
            synaptic_weight_mV=weight,
            sign_policy_id=graph.sign_policy_id,
            resolution_policy_id=graph.resolution_policy_id,
            unsigned_graph_fingerprint=graph.unsigned_graph_fingerprint,
            signed_policy_fingerprint=signed_graph_fingerprint(graph),
            fingerprint=digest.hexdigest(),
            outgoing_indptr=indptr,
            outgoing_targets=outgoing_targets,
            outgoing_weights_mV=outgoing_weights,
        )


@dataclass(frozen=True, slots=True)
class SimulationResult:
    """Compact immutable spike output and audit metadata."""

    spike_neuron_ids: np.ndarray
    spike_timesteps: np.ndarray
    spike_counts: np.ndarray
    duration_ms: float
    dt_ms: float
    parameter_fingerprint: str
    unsigned_graph_fingerprint: str
    sign_policy_fingerprint: str
    stimulus_fingerprint: str
    simulation_fingerprint: str
    spike_result_digest: str
    emitted_spike_count: int
    active_neuron_count: int
    queued_synaptic_event_count: int
    delivered_synaptic_event_count: int
    trace_neuron_ids: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int64))
    trace_v_mV: np.ndarray | None = None
    trace_g_mV: np.ndarray | None = None

    @property
    def spike_times_ms(self) -> np.ndarray:
        return self.spike_timesteps.astype(np.float64) * self.dt_ms


def _freeze(array: np.ndarray) -> np.ndarray:
    array.flags.writeable = False
    return array


def _canonicalize_spike_events(
    spike_neuron_ids: np.ndarray, spike_timesteps: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return spike events in the backend-independent canonical order."""

    if spike_neuron_ids.size < 2:
        return spike_neuron_ids, spike_timesteps
    order = np.lexsort((spike_neuron_ids, spike_timesteps))
    return spike_neuron_ids[order], spike_timesteps[order]


def _validate_duration(duration_ms: float, dt_ms: float) -> int:
    duration = _finite(duration_ms, "duration_ms")
    if duration <= 0.0:
        raise ValueError("duration_ms must be positive")
    return _exact_steps(duration, dt_ms, "duration")


def simulate_lif(
    projection: EffectiveSignedProjection,
    *,
    duration_ms: float,
    stimulus: ExplicitStimulus | Iterable = ExplicitStimulus(),
    parameters: LIFParameters = REFERENCE_LIF_PARAMETERS,
    dt_ms: float = 0.1,
    silenced_neuron_ids: Iterable[int] = (),
    trace_neuron_ids: Iterable[int] = (),
) -> SimulationResult:
    """Run the reference model using active spikes and a dense delay ring.

    At each boundary ``t=k*dt`` the order is: direct stimulus writes,
    delayed ``g`` writes, exact linear state update over the next interval,
    strict threshold test at ``t+dt``, reset/refractory assignment, then
    scheduling of outgoing events for ``t+dt+delay``. Variables marked
    ``unless refractory`` are clamped and incoming writes are ignored while
    ``t-lastspike <= refractory_period``; this is Brian's timestep-safe rule.
    """

    delay_steps, refractory_steps = parameters.grid_steps(dt_ms)
    if not np.isclose(
        projection.synaptic_weight_mV,
        parameters.synaptic_weight_per_anatomical_synapse_mV,
        rtol=0.0,
        atol=1e-15,
    ):
        raise ValueError(
            "projection synaptic weight does not match LIF parameter "
            "synaptic_weight_per_anatomical_synapse_mV"
        )
    steps = _validate_duration(duration_ms, dt_ms)
    ids = np.asarray(projection.neuron_ids, dtype=np.int64)
    n = ids.size
    explicit = stimulus
    if isinstance(stimulus, PoissonStimulus):
        explicit = stimulus.generate(duration_ms, dt_ms, parameters.synaptic_weight_per_anatomical_synapse_mV)
        stimulus_fingerprint = stimulus.fingerprint
    elif isinstance(stimulus, ExplicitStimulus):
        stimulus_fingerprint = stimulus.fingerprint
    else:
        explicit = ExplicitStimulus(tuple(stimulus))
        stimulus_fingerprint = explicit.fingerprint
    input_weight = parameters.synaptic_weight_per_anatomical_synapse_mV if explicit.weight_mV is None else explicit.weight_mV
    event_batches = schedule_events(explicit, neuron_positions=ids, duration_steps=steps, dt_ms=dt_ms)
    refractory_free = validate_refractory_ids(explicit.refractory_free_neuron_ids, ids)
    refractory_free_mask = np.zeros(n, dtype=bool)
    refractory_free_mask[refractory_free] = True
    silenced_ids = tuple(silenced_neuron_ids)
    trace_ids = tuple(trace_neuron_ids)
    silenced = validate_refractory_ids(silenced_ids, ids) if silenced_ids else np.empty(0, dtype=np.int64)
    silenced_mask = np.zeros(n, dtype=bool)
    silenced_mask[silenced] = True
    trace_positions = validate_refractory_ids(trace_ids, ids) if trace_ids else np.empty(0, dtype=np.int64)
    v = np.full(n, parameters.v_rest_mV, dtype=np.float64)
    g = np.zeros(n, dtype=np.float64)
    refractory_until = np.full(n, -1, dtype=np.int64)
    ring_size = max(delay_steps + 1, 1)
    pending = np.zeros((ring_size, n), dtype=np.float64)
    pending_event_counts = np.zeros((ring_size, n), dtype=np.int32)
    spike_ids: list[np.ndarray] = []
    spike_steps: list[np.ndarray] = []
    trace_v = np.empty((trace_positions.size, steps + 1), dtype=np.float64) if trace_positions.size else None
    trace_g = np.empty((trace_positions.size, steps + 1), dtype=np.float64) if trace_positions.size else None
    if trace_v is not None:
        trace_v[:, 0] = v[trace_positions]
        trace_g[:, 0] = g[trace_positions]
    queued_events = 0
    delivered_events = 0
    for step in range(steps):
        if step in event_batches:
            positions, _ = event_batches[step]
            direct = np.bincount(positions, minlength=n).astype(np.float64) * input_weight
            direct_allowed = (~(step <= refractory_until)) | refractory_free_mask
            v[direct_allowed] += direct[direct_allowed]
        slot = step % ring_size
        due = pending[slot]
        if np.any(due) or np.any(pending_event_counts[slot]):
            delivered_events += int(pending_event_counts[slot].sum(dtype=np.int64))
            allowed = (step > refractory_until) | refractory_free_mask
            g[allowed] += due[allowed]
            due.fill(0.0)
            pending_event_counts[slot].fill(0)
        allowed = (step > refractory_until) | refractory_free_mask
        if np.any(allowed):
            updated_v, updated_g = linear_state_update(v[allowed], g[allowed], parameters=parameters, dt_ms=dt_ms)
            v[allowed] = updated_v
            g[allowed] = updated_g
        fired = allowed & (v > parameters.v_threshold_mV)
        fired_positions = np.flatnonzero(fired)
        if fired_positions.size:
            spike_ids.append(ids[fired_positions].copy())
            spike_steps.append(np.full(fired_positions.size, step + 1, dtype=np.int64))
            v[fired_positions] = parameters.v_reset_mV
            g[fired_positions] = 0.0
            refractory_until[fired_positions] = step + 1 + refractory_steps
            delivery_step = step + 1 + delay_steps
            if delivery_step < steps + ring_size:
                event_slot = delivery_step % ring_size
                outgoing_allowed = ~silenced_mask[fired_positions]
                for source_position in fired_positions[outgoing_allowed]:
                    start, end = projection.outgoing_indptr[source_position:source_position + 2]
                    targets = projection.outgoing_targets[start:end]
                    weights = projection.outgoing_weights_mV[start:end]
                    np.add.at(pending[event_slot], targets, weights)
                    np.add.at(pending_event_counts[event_slot], targets, 1)
                    queued_events += int(end - start)
        if trace_v is not None:
            trace_v[:, step + 1] = v[trace_positions]
            trace_g[:, step + 1] = g[trace_positions]
    if spike_ids:
        output_ids = np.concatenate(spike_ids)
        output_steps = np.concatenate(spike_steps)
    else:
        output_ids = np.empty(0, dtype=np.int64)
        output_steps = np.empty(0, dtype=np.int64)
    output_ids, output_steps = _canonicalize_spike_events(output_ids, output_steps)
    counts = np.bincount(np.searchsorted(ids, output_ids), minlength=n).astype(np.int64)
    graph_payload = {
        "unsigned": projection.unsigned_graph_fingerprint,
        "signed": projection.signed_policy_fingerprint,
        "effective": projection.fingerprint,
        "parameters": parameters.fingerprint,
        "dt_ms": dt_ms,
        "delay_steps": delay_steps,
        "refractory_steps": refractory_steps,
        "duration_ms": duration_ms,
        "stimulus": stimulus_fingerprint,
        "silenced": tuple(int(ids[position]) for position in silenced),
    }
    simulation_fingerprint = hashlib.sha256(json.dumps(graph_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result_digest = hashlib.sha256(
        b"malecns-sim-spike-result-v1" + output_ids.tobytes() + output_steps.tobytes() + counts.tobytes()
    ).hexdigest()
    for array in (output_ids, output_steps, counts, trace_positions):
        _freeze(array)
    if trace_v is not None:
        _freeze(trace_v)
        _freeze(trace_g)
    return SimulationResult(
        spike_neuron_ids=output_ids,
        spike_timesteps=output_steps,
        spike_counts=counts,
        duration_ms=float(duration_ms),
        dt_ms=float(dt_ms),
        parameter_fingerprint=parameters.fingerprint,
        unsigned_graph_fingerprint=projection.unsigned_graph_fingerprint,
        sign_policy_fingerprint=projection.signed_policy_fingerprint,
        stimulus_fingerprint=stimulus_fingerprint,
        simulation_fingerprint=simulation_fingerprint,
        spike_result_digest=result_digest,
        emitted_spike_count=int(output_ids.size),
        active_neuron_count=int(np.count_nonzero(counts)),
        queued_synaptic_event_count=queued_events,
        delivered_synaptic_event_count=delivered_events,
        trace_neuron_ids=trace_positions,
        trace_v_mV=trace_v,
        trace_g_mV=trace_g,
    )


def simulate_lif_active(
    projection: EffectiveSignedProjection,
    *,
    duration_ms: float,
    stimulus: ExplicitStimulus | PoissonStimulus = ExplicitStimulus(),
    parameters: LIFParameters = REFERENCE_LIF_PARAMETERS,
    dt_ms: float = 0.1,
) -> SimulationResult:
    """Run the same reference equations while updating only active neurons.

    This execution path keeps the full immutable projection but avoids a dense
    membrane update for every curated neuron at every timestep. It is used by
    Task 008 for repeated trials and has no identity or parameter-selection
    behavior.
    """

    delay_steps, refractory_steps = parameters.grid_steps(dt_ms)
    if not np.isclose(
        projection.synaptic_weight_mV,
        parameters.synaptic_weight_per_anatomical_synapse_mV,
        rtol=0.0,
        atol=1e-15,
    ):
        raise ValueError(
            "projection synaptic weight does not match LIF parameter "
            "synaptic_weight_per_anatomical_synapse_mV"
        )
    steps = _validate_duration(duration_ms, dt_ms)
    ids = np.asarray(projection.neuron_ids, dtype=np.int64)
    n = ids.size
    if isinstance(stimulus, PoissonStimulus):
        explicit = stimulus.generate(duration_ms, dt_ms, parameters.synaptic_weight_per_anatomical_synapse_mV)
        stimulus_fingerprint = stimulus.fingerprint
    elif isinstance(stimulus, ExplicitStimulus):
        explicit = stimulus
        stimulus_fingerprint = stimulus.fingerprint
    else:
        explicit = ExplicitStimulus(tuple(stimulus))
        stimulus_fingerprint = explicit.fingerprint
    input_weight = parameters.synaptic_weight_per_anatomical_synapse_mV if explicit.weight_mV is None else explicit.weight_mV
    event_batches = schedule_events(explicit, neuron_positions=ids, duration_steps=steps, dt_ms=dt_ms)
    refractory_free = validate_refractory_ids(explicit.refractory_free_neuron_ids, ids)
    refractory_free_mask = np.zeros(n, dtype=bool)
    refractory_free_mask[refractory_free] = True
    v = np.full(n, parameters.v_rest_mV, dtype=np.float64)
    g = np.zeros(n, dtype=np.float64)
    refractory_until = np.full(n, -1, dtype=np.int64)
    ring_size = max(delay_steps + 1, 1)
    pending = np.zeros((ring_size, n), dtype=np.float64)
    pending_counts = np.zeros((ring_size, n), dtype=np.int32)
    pending_totals = np.zeros(ring_size, dtype=np.int64)
    active: set[int] = set()
    spike_ids: list[np.ndarray] = []
    spike_steps: list[np.ndarray] = []
    queued_events = 0
    delivered_events = 0
    for step in range(steps):
        for position, _ in zip(*event_batches.get(step, (np.empty(0, dtype=np.int64), np.empty(0, dtype=np.float64)))):
            position = int(position)
            if step > refractory_until[position] or refractory_free_mask[position]:
                v[position] += input_weight
                active.add(position)
        slot = step % ring_size
        if pending_totals[slot]:
            due_counts = pending_counts[slot]
            due_positions = np.flatnonzero(due_counts)
            if due_positions.size:
                allowed = (step > refractory_until[due_positions]) | refractory_free_mask[due_positions]
                allowed_positions = due_positions[allowed]
                g[allowed_positions] += pending[slot, allowed_positions]
                active.update(int(position) for position in allowed_positions)
            delivered_events += int(pending_totals[slot])
            pending[slot].fill(0.0)
            due_counts.fill(0)
            pending_totals[slot] = 0
        if active:
            active_positions = np.fromiter(active, dtype=np.int64)
            allowed = (step > refractory_until[active_positions]) | refractory_free_mask[active_positions]
            allowed_positions = active_positions[allowed]
            if allowed_positions.size:
                updated_v, updated_g = linear_state_update(v[allowed_positions], g[allowed_positions], parameters=parameters, dt_ms=dt_ms)
                v[allowed_positions] = updated_v
                g[allowed_positions] = updated_g
            fired_positions = allowed_positions[v[allowed_positions] > parameters.v_threshold_mV]
            if fired_positions.size:
                spike_ids.append(ids[fired_positions].copy())
                spike_steps.append(np.full(fired_positions.size, step + 1, dtype=np.int64))
                v[fired_positions] = parameters.v_reset_mV
                g[fired_positions] = 0.0
                refractory_until[fired_positions] = step + 1 + refractory_steps
                delivery_step = step + 1 + delay_steps
                if delivery_step < steps + ring_size:
                    event_slot = delivery_step % ring_size
                    for source_position in fired_positions:
                        start, end = projection.outgoing_indptr[source_position:source_position + 2]
                        targets = projection.outgoing_targets[start:end]
                        weights = projection.outgoing_weights_mV[start:end]
                        np.add.at(pending[event_slot], targets, weights)
                        np.add.at(pending_counts[event_slot], targets, 1)
                        queued_events += int(end - start)
                        pending_totals[event_slot] += int(end - start)
            keep = (
                (v[active_positions] != parameters.v_rest_mV)
                | (g[active_positions] != 0.0)
                | (refractory_until[active_positions] >= step)
            )
            active = set(int(position) for position in active_positions[keep])
    if spike_ids:
        output_ids = np.concatenate(spike_ids)
        output_steps = np.concatenate(spike_steps)
    else:
        output_ids = np.empty(0, dtype=np.int64)
        output_steps = np.empty(0, dtype=np.int64)
    output_ids, output_steps = _canonicalize_spike_events(output_ids, output_steps)
    counts = np.bincount(np.searchsorted(ids, output_ids), minlength=n).astype(np.int64)
    graph_payload = {
        "unsigned": projection.unsigned_graph_fingerprint,
        "signed": projection.signed_policy_fingerprint,
        "effective": projection.fingerprint,
        "parameters": parameters.fingerprint,
        "dt_ms": dt_ms,
        "delay_steps": delay_steps,
        "refractory_steps": refractory_steps,
        "duration_ms": duration_ms,
        "stimulus": stimulus_fingerprint,
        "silenced": (),
    }
    simulation_fingerprint = hashlib.sha256(json.dumps(graph_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result_digest = hashlib.sha256(
        b"malecns-sim-spike-result-v1" + output_ids.tobytes() + output_steps.tobytes() + counts.tobytes()
    ).hexdigest()
    for array in (output_ids, output_steps, counts):
        _freeze(array)
    return SimulationResult(
        spike_neuron_ids=output_ids,
        spike_timesteps=output_steps,
        spike_counts=counts,
        duration_ms=float(duration_ms),
        dt_ms=float(dt_ms),
        parameter_fingerprint=parameters.fingerprint,
        unsigned_graph_fingerprint=projection.unsigned_graph_fingerprint,
        sign_policy_fingerprint=projection.signed_policy_fingerprint,
        stimulus_fingerprint=stimulus_fingerprint,
        simulation_fingerprint=simulation_fingerprint,
        spike_result_digest=result_digest,
        emitted_spike_count=int(output_ids.size),
        active_neuron_count=int(np.count_nonzero(counts)),
        queued_synaptic_event_count=queued_events,
        delivered_synaptic_event_count=delivered_events,
    )
