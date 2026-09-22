from __future__ import annotations

import numpy as np
import pytest

from malecns_sim.analysis.task011 import (
    FIXED_TRIAL_INDICES,
    FROZEN_TASK011_CANDIDATES,
    _annotation_map,
    baseline_activity_exposure,
    classify_mechanism,
    detect_first_divergence,
    fixed_trial_indices,
    first_hop_target_analysis,
    frozen_task011_candidate_ids,
    propagation_windows,
    structural_summary,
    validate_intervention_scope,
)
from malecns_sim.dynamics import ExplicitStimulus, LIFParameters, SpikeSchedule, simulate_lif
from malecns_sim.dynamics.lif import EffectiveSignedProjection


def _projection(edges: tuple[tuple[int, int, int], ...]) -> EffectiveSignedProjection:
    ids = np.asarray([1, 2, 3, 10331, 16949], dtype=np.int64)
    source = np.asarray([int(row[0]) for row in edges], dtype=np.int64)
    target = np.asarray([int(row[1]) for row in edges], dtype=np.int64)
    source_positions = np.searchsorted(ids, source)
    target_positions = np.searchsorted(ids, target)
    weights = np.asarray([row[2] * 0.275 for row in edges], dtype=np.float64)
    order = np.lexsort((target_positions, source_positions)) if edges else np.empty(0, dtype=np.int64)
    source_positions = source_positions[order]
    target_positions = target_positions[order]
    weights = weights[order]
    indptr = np.zeros(ids.size + 1, dtype=np.int64)
    np.add.at(indptr, source_positions + 1, 1)
    np.cumsum(indptr, out=indptr)
    return EffectiveSignedProjection(
        neuron_ids=ids,
        source_positions=source_positions,
        target_positions=target_positions,
        effective_weights_mV=weights,
        included_anatomical_weight=int(sum(abs(row[2]) for row in edges)),
        excluded_anatomical_weight=0,
        excluded_unresolved_edge_count=0,
        synaptic_weight_mV=0.275,
        sign_policy_id="test",
        resolution_policy_id="test",
        unsigned_graph_fingerprint="u" * 64,
        signed_policy_fingerprint="s" * 64,
        fingerprint="p" * 64,
        outgoing_indptr=indptr,
        outgoing_targets=target_positions,
        outgoing_weights_mV=weights,
    )


def _run_pair(projection: EffectiveSignedProjection):
    stimulus = ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0)
    baseline = simulate_lif(
        projection,
        duration_ms=10.0,
        stimulus=stimulus,
        trace_neuron_ids=(1, 2, 10331, 16949),
        collect_sparse_trace=True,
    )
    silenced = simulate_lif(
        projection,
        duration_ms=10.0,
        stimulus=stimulus,
        silenced_neuron_ids=(1,),
        trace_neuron_ids=(1, 2, 10331, 16949),
        collect_sparse_trace=True,
    )
    return baseline, silenced


def test_frozen_candidate_set_and_fixed_trials_are_literal():
    assert frozen_task011_candidate_ids() == ("10313", "10135", "12752", "512730", "43765")
    assert FIXED_TRIAL_INDICES == (0, 10, 20)
    assert fixed_trial_indices() == FIXED_TRIAL_INDICES
    with pytest.raises(ValueError, match="frozen"):
        fixed_trial_indices((0, 1, 2))


def test_sparse_trace_collection_is_present_and_does_not_change_spikes():
    projection = _projection(((1, 2, 100), (2, 10331, -2)))
    stimulus = ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0)
    plain = simulate_lif(projection, duration_ms=10.0, stimulus=stimulus)
    traced = simulate_lif(projection, duration_ms=10.0, stimulus=stimulus, collect_sparse_trace=True)
    assert traced.sparse_trace is not None
    assert np.array_equal(plain.spike_neuron_ids, traced.spike_neuron_ids)
    assert np.array_equal(plain.spike_timesteps, traced.spike_timesteps)
    assert plain.spike_result_digest == traced.spike_result_digest
    assert np.array_equal(traced.trace_neuron_ids, np.asarray([], dtype=np.int64))
    assert traced.sparse_trace.timesteps.size == 100
    assert traced.sparse_trace.fingerprint == traced.sparse_trace.fingerprint


def test_first_divergence_and_propagation_windows_use_exact_events():
    projection = _projection(((1, 2, 10000), (2, 10331, 10000)))
    baseline, silenced = _run_pair(projection)
    divergence, divergent = detect_first_divergence(
        baseline,
        silenced,
        input_neuron_ids=(1,),
        candidate_id="1",
    )
    assert divergence.first_delivery_step is not None
    assert divergence.first_downstream_spike_step is not None
    windows = propagation_windows(
        baseline,
        silenced,
        divergent=divergent,
        first_delivery_step=divergence.first_delivery_step,
    )
    assert len(windows) == 8
    assert windows[0]["start_ms"] == 0.0
    assert any(row["divergent_spike_events"] > 0 for row in windows)


def test_first_hop_target_extraction_reports_sign_and_routes():
    projection = _projection(((1, 2, 10000), (2, 10331, -10000)))
    baseline, silenced = _run_pair(projection)
    result = first_hop_target_analysis(
        (baseline,),
        (silenced,),
        projection,
        "1",
        {"2": {"type": "intermediate"}},
    )
    assert result["target_count"] == 1
    assert result["targets"][0]["connection_sign"] == "positive"
    assert result["targets"][0]["participates_known_two_hop_route_to_MN9_L"] is True
    assert result["targets"][0]["spikes_change"] is True


def test_structural_metadata_reports_short_path_and_task004_sign():
    projection = _projection(((1, 2, 100), (2, 10331, -2), (1, 10331, 3)))
    candidate = {"body_id": "1", "neurotransmitter": "GABA", "routes": ("L_sugar_to_MN9_L",)}
    summary = structural_summary(projection, candidate, {"2": {"type": "intermediate"}})
    assert summary["neurotransmitter"] == "GABA"
    assert summary["direct_edge_to_MN9_L"] is True
    assert summary["short_paths"]["MN9_L"]["shortest_known_path_length"] == 1
    assert summary["short_paths"]["MN9_L"]["negative_signed_route_count"] == 1


def test_delay_compatibility_uses_reference_delay():
    assert LIFParameters().synaptic_delay_ms == pytest.approx(1.8)
    assert LIFParameters().grid_steps(0.1)[0] == 18


def test_mechanism_classification_is_conservative():
    assert classify_mechanism(({"short_path_compatible": True, "network_redistribution_compatible": False},)) == "SHORT_PATH_COMPATIBLE"
    assert classify_mechanism(({"short_path_compatible": False, "network_redistribution_compatible": True},)) == "NETWORK_REDISTRIBUTION_COMPATIBLE"
    assert classify_mechanism(({"short_path_compatible": True, "network_redistribution_compatible": True},)) == "MIXED"
    assert classify_mechanism(({"short_path_compatible": False, "network_redistribution_compatible": False},)) == "UNRESOLVED"


def test_inactive_candidate_and_exact_null_have_no_exposure_or_divergence():
    projection = _projection(())
    stimulus = ExplicitStimulus(())
    baseline = simulate_lif(projection, duration_ms=5.0, stimulus=stimulus, collect_sparse_trace=True)
    silenced = simulate_lif(projection, duration_ms=5.0, stimulus=stimulus, silenced_neuron_ids=(1,), collect_sparse_trace=True)
    exposure = baseline_activity_exposure((baseline,), "1", projection)
    divergence, divergent = detect_first_divergence(baseline, silenced, candidate_id="1")
    assert exposure["spike_count_total"] == 0
    assert exposure["outgoing_delivered_event_count_total"] == 0
    assert divergence.first_delivery_step is None
    assert divergence.first_downstream_spike_step is None
    assert not divergent


def test_deterministic_trace_fingerprint_and_intervention_scope():
    projection = _projection(((1, 2, 1),))
    stimulus = ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0)
    first = simulate_lif(projection, duration_ms=3.0, stimulus=stimulus, collect_sparse_trace=True)
    second = simulate_lif(projection, duration_ms=3.0, stimulus=stimulus, collect_sparse_trace=True)
    assert first.sparse_trace is not None and second.sparse_trace is not None
    assert first.sparse_trace.fingerprint == second.sparse_trace.fingerprint
    assert validate_intervention_scope(FROZEN_TASK011_CANDIDATES) == FROZEN_TASK011_CANDIDATES
    with pytest.raises(ValueError, match="new intervention"):
        validate_intervention_scope(("999999",))
