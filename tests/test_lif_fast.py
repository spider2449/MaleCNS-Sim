"""Synthetic-only equivalence of the lean advance against the reference simulator."""

import numpy as np

from malecns_sim.dynamics.lif import EffectiveSignedProjection, PreparedRuntime
from malecns_sim.dynamics.lif_fast import advance_lean
from malecns_sim.dynamics.stimulus import ExplicitStimulus, SpikeSchedule


def _projection(n=60, seed=7):
    rng = np.random.default_rng(seed)
    sources, targets = [], []
    for source in range(n):
        for target in rng.choice(n, size=6, replace=False):
            sources.append(source)
            targets.append(int(target))
    sources, targets = np.array(sources), np.array(targets)
    weights = rng.choice([-1.0, 1.0], size=sources.size) * 4.0
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.add.at(indptr, sources + 1, 1)
    indptr = np.cumsum(indptr)
    return EffectiveSignedProjection(
        neuron_ids=np.arange(100, 100 + n, dtype=np.int64),
        source_positions=sources.astype(np.int64), target_positions=targets.astype(np.int64),
        effective_weights_mV=weights, outgoing_indptr=indptr,
        outgoing_targets=targets.astype(np.int64), outgoing_weights_mV=weights,
        synaptic_weight_mV=0.275, fingerprint="synthetic-fast", unsigned_graph_fingerprint="synthetic-fast",
        signed_policy_fingerprint="synthetic-fast", sign_policy_id="synthetic-fast",
        resolution_policy_id="synthetic-fast", excluded_unresolved_edge_count=0,
        excluded_anatomical_weight=0, included_anatomical_weight=0)


def _chunk_stimulus(index):
    schedules = tuple(SpikeSchedule(100 + (index * 5 + k) % 60, (0.0, 0.1)) for k in range(4))
    return ExplicitStimulus(schedules, weight_mV=8.0, refractory_free_neuron_ids=(105, 110))


def test_lean_advance_matches_reference_state_and_spikes():
    engine = PreparedRuntime(_projection())
    reference, lean = engine.initial_state(), engine.initial_state()
    total_spikes = 0
    for index in range(40):
        stimulus = _chunk_stimulus(index)
        expected = engine.advance(reference, duration_ms=2.0, stimulus=stimulus)
        actual = advance_lean(engine, lean, duration_ms=2.0, stimulus=stimulus)
        assert np.array_equal(actual.spike_neuron_ids, expected.spike_neuron_ids)
        assert np.array_equal(actual.spike_timesteps, expected.spike_timesteps)
        for name in ("v_mV", "g_mV", "refractory_until", "pending", "pending_event_counts"):
            assert np.array_equal(getattr(lean, name), getattr(reference, name)), name
        assert lean.timestep == reference.timestep
        total_spikes += expected.emitted_spike_count
    # The fixture must exercise spiking, refractory masking and delayed delivery.
    assert total_spikes > 50
