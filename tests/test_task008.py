import pytest
import numpy as np

from malecns_sim.analysis.task008 import (
    MIRROR_CONDITION,
    MN9_L,
    MN9_R,
    PRIMARY_CONDITION,
    PreparedNetwork,
    Task008Condition,
    TrialObservation,
    derive_task008_populations,
    deterministic_seed,
    normalized_rate,
    population_report,
    spearman_rank_association,
    summarize_trials,
)
from malecns_sim.data.model import CuratedNeuronProjection, NumericNormalizedConnectome
from malecns_sim.data.neurotransmitter import NeurotransmitterEvidence, NeurotransmitterResolutionPolicy
from malecns_sim.dynamics import EffectiveSignedProjection, ExplicitStimulus, LIFParameters, SpikeSchedule, simulate_lif, simulate_lif_active
from malecns_sim.graph.signed import SignedAnatomicalConnectome
from malecns_sim.sign import Shiu2024SignPolicy
from malecns_sim.homology import MaleCNSCandidate, MappingStatus


def _candidate(body_id, side, *, nt="acetylcholine", unresolved=False):
    return MaleCNSCandidate(
        body_id=str(body_id),
        type="LB3a",
        flywire_type="LB3",
        side=side,
        root_side=side,
        soma_side=None,
        superclass="cb_sensory",
        cell_class="gustatory",
        entry_nerve="MxLbN",
        consensus_nt=None if unresolved else nt,
        resolved_nt=None if unresolved else nt,
        task004_sign=None if unresolved else 1,
    )


def _signed_graph():
    ids = np.asarray([1, 2, 3], dtype=np.int64)
    connectome = NumericNormalizedConnectome(
        ids,
        np.asarray([1, 2, 3], dtype=np.int64),
        np.asarray([2, 3, 1], dtype=np.int64),
        np.asarray([5, 7, 11], dtype=np.int64),
    )
    projection = CuratedNeuronProjection(connectome, 3, 3, 3, 0)
    evidence = [
        NeurotransmitterEvidence(1, consensus_nt="acetylcholine"),
        NeurotransmitterEvidence(2, consensus_nt="histamine"),
        NeurotransmitterEvidence(3, consensus_nt="gaba"),
    ]
    signed = SignedAnatomicalConnectome.from_projection(
        projection, evidence, NeurotransmitterResolutionPolicy(), Shiu2024SignPolicy()
    )
    return signed, EffectiveSignedProjection.from_signed_connectome(signed)


def test_left_and_right_population_derivation_uses_exact_predicate_without_count_targeting():
    result = derive_task008_populations(
        [_candidate(101, "L"), _candidate(102, "R"), _candidate(103, "L", unresolved=True)],
        enforce_task007_right=False,
    )
    assert result.sugar_left.candidate_body_ids == ("101", "103")
    assert result.sugar_right.candidate_body_ids == ("102",)
    assert result.sugar_left.task004_nt_counts == (("resolved", 1), ("unresolved", 1))


def test_laterality_gate_and_readout_assignments_are_closed():
    assert PRIMARY_CONDITION.input_population == "sugar_left"
    assert (PRIMARY_CONDITION.contralateral_mn9, PRIMARY_CONDITION.ipsilateral_mn9) == (MN9_R, MN9_L)
    assert MIRROR_CONDITION.input_population == "sugar_right"
    assert (MIRROR_CONDITION.contralateral_mn9, MIRROR_CONDITION.ipsilateral_mn9) == (MN9_L, MN9_R)
    with pytest.raises(ValueError, match="laterality gate"):
        Task008Condition("bad", "sugar_right", MN9_R, MN9_L, "wrong", ())


def test_primary_cannot_be_right_sugar_to_right_mn9():
    with pytest.raises(ValueError, match="laterality gate"):
        Task008Condition("bad", "sugar_right", MN9_R, MN9_L, "ipsi", ())


def test_population_report_preserves_unresolved_outgoing_edges():
    signed, _ = _signed_graph()
    population = derive_task008_populations([_candidate(1, "L")], enforce_task007_right=False).sugar_left
    report = population_report("sugar_left", population, [_candidate(1, "L")], signed)
    assert report.root_side_counts == (("L", 1),)
    assert report.resolved_outgoing_edge_count == 1
    assert report.unresolved_outgoing_edge_count == 0
    assert report.total_outgoing_anatomical_weight == 5


def test_prepared_graph_identity_is_reusable_and_trial_state_is_not_part_of_it():
    signed, projection = _signed_graph()
    prepared = PreparedNetwork(projection, signed, "fixture", 1.0, 0.5, 1.5, 123, "a" * 64)
    assert prepared.projection is projection
    assert prepared.fingerprint == "a" * 64
    assert prepared.projection is prepared.projection


def test_deterministic_seed_derivation_is_identity_sensitive():
    args = ("experiment", "L", 100.0, 3, "g" * 64, "s" * 64)
    assert deterministic_seed(*args) == deterministic_seed(*args)
    assert deterministic_seed(*args[:-1], "t" * 64) != deterministic_seed(*args)


def test_rate_statistics_and_digest_are_deterministic():
    trials = [
        TrialObservation(100.0, 0, 1, 4, 1, 20, 5, 10, 30, 30, "a"),
        TrialObservation(100.0, 1, 2, 6, 0, 22, 6, 11, 32, 32, "b"),
    ]
    first = summarize_trials("primary", trials)
    second = summarize_trials("primary", trials)
    assert first == second
    assert first.contralateral_mean_hz == 5.0
    assert first.ipsilateral_active_fraction == 0.5
    assert first.contra_minus_ipsi_hz == 4.5


def test_aggregate_input_normalization_and_curve_association():
    assert normalized_rate(100.0, 42) == pytest.approx(50.0)
    assert spearman_rank_association((0, 1, 3), (0, 2, 5)) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        normalized_rate(100.0, 0)


def test_no_dynamics_based_identity_mutation_path_exists():
    result = derive_task008_populations([_candidate(101, "L"), _candidate(102, "R")], enforce_task007_right=False)
    before = result.sugar_left.candidate_body_ids
    assert result.sugar_left.candidate_body_ids == before
    assert MappingStatus.SIDE_RESOLVED.value == "SIDE_RESOLVED"


def test_no_parameter_tuning_path_in_reference_preparation():
    assert LIFParameters().synaptic_weight_per_anatomical_synapse_mV == 0.275
    assert LIFParameters().v_threshold_mV == -45.0


def test_active_reference_path_matches_dense_reference_output():
    _, projection = _signed_graph()
    stimulus = ExplicitStimulus((SpikeSchedule(1, (0.0, 3.0)),), weight_mV=10.0)
    dense = simulate_lif(projection, duration_ms=8.0, stimulus=stimulus)
    active = simulate_lif_active(projection, duration_ms=8.0, stimulus=stimulus)
    assert active.spike_neuron_ids.tolist() == dense.spike_neuron_ids.tolist()
    assert active.spike_timesteps.tolist() == dense.spike_timesteps.tolist()
    assert active.spike_counts.tolist() == dense.spike_counts.tolist()
    assert active.spike_result_digest == dense.spike_result_digest
