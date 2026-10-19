"""Lean chunk advance for the public CPU runtime.

This mirrors ``simulate_lif`` for the numerical state update but drops the
audit-only outputs (dense spike counts, result digest, fingerprints, traces).
State mutation and the emitted spike events are bit-identical to the reference.
The reference module stays untouched because frozen validation pins its source.
"""

from dataclasses import dataclass

import numpy as np

from malecns_sim.dynamics.lif import (
    SimulationState,
    PreparedRuntime,
    _canonicalize_spike_events,
    _validate_duration,
    linear_state_update,
)
from malecns_sim.dynamics.stimulus import ExplicitStimulus, schedule_events, validate_refractory_ids


@dataclass(frozen=True, slots=True)
class LeanAdvanceResult:
    """Canonically ordered spike events with absolute end-of-step timesteps."""

    spike_neuron_ids: np.ndarray
    spike_timesteps: np.ndarray


def advance_lean(engine: PreparedRuntime, state: SimulationState, *, duration_ms: float,
                 stimulus: ExplicitStimulus) -> LeanAdvanceResult:
    """Advance ``state`` in place by ``duration_ms`` and return the emitted spikes."""

    if state.runtime_identity != engine.identity:
        raise ValueError("state belongs to another prepared runtime")
    if not isinstance(stimulus, ExplicitStimulus):
        raise TypeError("advance requires explicit chunk-relative events")
    projection, parameters, dt_ms = engine.projection, engine.parameters, engine.dt_ms
    delay_steps, refractory_steps = parameters.grid_steps(dt_ms)
    steps = _validate_duration(duration_ms, dt_ms)
    ids = np.asarray(projection.neuron_ids, dtype=np.int64)
    n = ids.size
    input_weight = (parameters.synaptic_weight_per_anatomical_synapse_mV
                    if stimulus.weight_mV is None else stimulus.weight_mV)
    event_batches = schedule_events(stimulus, neuron_positions=ids, duration_steps=steps, dt_ms=dt_ms)
    free_ids = validate_refractory_ids(stimulus.refractory_free_neuron_ids, ids)
    free_mask = None
    if free_ids.size:
        free_mask = np.zeros(n, dtype=bool)
        free_mask[free_ids] = True

    offset = state.timestep
    v, g, refractory_until = state.v_mV, state.g_mV, state.refractory_until
    pending, pending_event_counts = state.pending, state.pending_event_counts
    ring_size = pending.shape[0]
    spike_ids: list[np.ndarray] = []
    spike_steps: list[np.ndarray] = []
    scratch = (np.empty(n, dtype=np.float64), np.empty(n, dtype=np.float64))
    allowed = np.empty(n, dtype=bool)

    def refresh_allowed(step: int) -> None:
        np.greater(step, refractory_until, out=allowed)
        if free_mask is not None:
            np.logical_or(allowed, free_mask, out=allowed)

    for local_step in range(steps):
        step = offset + local_step
        if local_step in event_batches:
            positions, _ = event_batches[local_step]
            direct = np.bincount(positions, minlength=n).astype(np.float64) * input_weight
            refresh_allowed(step)
            v[allowed] += direct[allowed]
        slot = step % ring_size
        due = pending[slot]
        if np.any(due) or np.any(pending_event_counts[slot]):
            refresh_allowed(step)
            g[allowed] += due[allowed]
            due.fill(0.0)
            pending_event_counts[slot].fill(0)
        refresh_allowed(step)
        if allowed.all():
            # Every neuron updates, so skip the gather/scatter copies.
            updated_v, updated_g = linear_state_update(
                v, g, parameters=parameters, dt_ms=dt_ms, _scratch=scratch)
            v[:] = updated_v
            g[:] = updated_g
        elif allowed.any():
            updated_v, updated_g = linear_state_update(
                v[allowed], g[allowed], parameters=parameters, dt_ms=dt_ms, _scratch=scratch)
            v[allowed] = updated_v
            g[allowed] = updated_g
        fired_positions = np.flatnonzero(allowed & (v > parameters.v_threshold_mV))
        if fired_positions.size:
            spike_ids.append(ids[fired_positions].copy())
            spike_steps.append(np.full(fired_positions.size, step + 1, dtype=np.int64))
            v[fired_positions] = parameters.v_reset_mV
            g[fired_positions] = 0.0
            refractory_until[fired_positions] = step + 1 + refractory_steps
            delivery_step = step + 1 + delay_steps
            if delivery_step < offset + steps + ring_size:
                event_slot = delivery_step % ring_size
                for source_position in fired_positions:
                    start, end = projection.outgoing_indptr[source_position:source_position + 2]
                    targets = projection.outgoing_targets[start:end]
                    weights = projection.outgoing_weights_mV[start:end]
                    np.add.at(pending[event_slot], targets, weights)
                    np.add.at(pending_event_counts[event_slot], targets, 1)
    state.timestep += steps
    if spike_ids:
        output_ids = np.concatenate(spike_ids)
        output_steps = np.concatenate(spike_steps)
    else:
        output_ids = np.empty(0, dtype=np.int64)
        output_steps = np.empty(0, dtype=np.int64)
    output_ids, output_steps = _canonicalize_spike_events(output_ids, output_steps)
    return LeanAdvanceResult(output_ids, output_steps)
