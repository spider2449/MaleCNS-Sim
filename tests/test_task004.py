import numpy as np
import pytest

from malecns_sim.data.male_cns_v1 import project_numeric_connectome
from malecns_sim.data.model import NumericNormalizedConnectome
from malecns_sim.data.neurotransmitter import (
    NeurotransmitterEvidence,
    NeurotransmitterResolutionPolicy,
    ResolvedNeurotransmitter,
    SUPPORTED_NEUROTRANSMITTERS,
)
from malecns_sim.graph.fingerprint import graph_fingerprint
from malecns_sim.graph.signed import SignedAnatomicalConnectome, signed_graph_fingerprint
from malecns_sim.graph.sparse import SparseDirectedGraph
from malecns_sim.sign import ConservativeSignPolicy, Shiu2024SignPolicy


def test_resolution_precedence_is_explicit_and_conflict_does_not_merge_fields():
    evidence = NeurotransmitterEvidence(
        1,
        consensus_nt="gaba",
        predicted_nt="acetylcholine",
        celltype_predicted_nt="glutamate",
    )
    result = NeurotransmitterResolutionPolicy().resolve(evidence)
    assert result.identity == "gaba"
    assert result.source_field == "consensus_nt"
    assert result.source_label == "gaba"


def test_resolution_falls_back_only_when_higher_precedence_is_absent():
    result = NeurotransmitterResolutionPolicy().resolve(
        NeurotransmitterEvidence(1, predicted_nt="GABA", celltype_predicted_nt="acetylcholine")
    )
    assert result.identity == "gaba"
    assert result.source_field == "predicted_nt"


def test_explicit_unclear_is_unresolved_and_does_not_fallback():
    result = NeurotransmitterResolutionPolicy().resolve(
        NeurotransmitterEvidence(1, consensus_nt="unclear", predicted_nt="gaba")
    )
    assert result.identity is None
    assert not result.resolved
    assert result.source_field == "consensus_nt"
    assert result.source_label == "unclear"


def test_confidence_and_ground_truth_are_preserved():
    evidence = NeurotransmitterEvidence(
        1,
        predicted_nt="acetylcholine",
        predicted_nt_confidence=0.8125,
        celltype_predicted_nt="gaba",
        celltype_predicted_nt_confidence=0.25,
        ground_truth="acetylcholine",
    )
    result = NeurotransmitterResolutionPolicy().resolve(evidence)
    assert result.source_confidence == 0.8125
    assert result.evidence.celltype_predicted_nt_confidence == 0.25
    assert result.evidence.ground_truth == "acetylcholine"


@pytest.mark.parametrize("label", sorted(SUPPORTED_NEUROTRANSMITTERS))
def test_each_supported_transmitter_label_is_canonicalized(label):
    result = NeurotransmitterResolutionPolicy().resolve(
        NeurotransmitterEvidence(1, consensus_nt=label.upper())
    )
    assert result.identity == label
    assert result.resolved


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("acetylcholine", 1),
        ("gaba", -1),
        ("glutamate", -1),
        ("dopamine", 1),
        ("octopamine", 1),
        ("serotonin", 1),
    ],
)
def test_shiu_compatible_sign_policy(label, expected):
    resolved = NeurotransmitterResolutionPolicy().resolve(
        NeurotransmitterEvidence(1, consensus_nt=label)
    )
    result = Shiu2024SignPolicy().sign_for(resolved)
    assert result.sign == expected
    assert result.policy_id == "Shiu2024SignPolicy"


@pytest.mark.parametrize("label", ["glutamate", "dopamine", "octopamine", "serotonin", "histamine"])
def test_conservative_policy_refuses_ambiguous_or_modulatory_labels(label):
    resolved = NeurotransmitterResolutionPolicy().resolve(
        NeurotransmitterEvidence(1, consensus_nt=label)
    )
    assert ConservativeSignPolicy().sign_for(resolved).sign is None


def _projection() -> object:
    connectome = NumericNormalizedConnectome(
        neuron_ids=np.asarray([1, 2, 3, 4], dtype=np.int64),
        source_ids=np.asarray([1, 2, 3, 4, 4], dtype=np.int64),
        target_ids=np.asarray([2, 2, 3, 4, 1], dtype=np.int64),
        synapse_counts=np.asarray([5, 7, 11, 13, 17], dtype=np.int64),
    )
    return project_numeric_connectome(connectome, np.asarray([1, 2, 3, 4], dtype=np.int64))


def _evidence():
    return [
        NeurotransmitterEvidence(1, consensus_nt="acetylcholine", superclass="sensory"),
        NeurotransmitterEvidence(2, consensus_nt="gaba", superclass="interneuron"),
        NeurotransmitterEvidence(3, consensus_nt="unclear", superclass="interneuron"),
        NeurotransmitterEvidence(4, consensus_nt="histamine", superclass="sensory"),
    ]


def _signed(policy):
    return SignedAnatomicalConnectome.from_projection(
        _projection(),
        _evidence(),
        NeurotransmitterResolutionPolicy(),
        policy,
    )


def test_unresolved_sign_behavior_and_presynaptic_sign_application():
    graph = _signed(Shiu2024SignPolicy())
    assert graph.presynaptic_signs.tolist() == [1, -1, 2, 2, 2]
    assert graph.signed_count(0) == 5
    assert graph.signed_count(1) == -7
    assert graph.signed_count(2) is None


def test_self_edges_use_the_presynaptic_sign():
    graph = _signed(Shiu2024SignPolicy())
    assert graph.connectome.source_ids[1] == graph.connectome.target_ids[1] == 2
    assert graph.signed_count(1) == -7
    assert graph.connectome.source_ids[2] == graph.connectome.target_ids[2] == 3
    assert graph.signed_count(2) is None


def test_signed_count_is_derived_and_anatomical_weights_are_unchanged():
    graph = _signed(Shiu2024SignPolicy())
    assert graph.anatomical_weights.tolist() == [5, 7, 11, 17, 13]
    assert graph.signed_counts.tolist() == [5, -7, 0, 0, 0]
    assert graph.coverage().signed_anatomical_weight == 12
    assert graph.coverage().unresolved_anatomical_weight == 41


def test_unsigned_anatomical_graph_fingerprint_remains_the_existing_graph_fingerprint():
    projection = _projection()
    unsigned = SparseDirectedGraph.from_curated_projection(projection)
    signed = _signed(Shiu2024SignPolicy())
    assert signed.unsigned_graph_fingerprint == graph_fingerprint(unsigned)
    assert signed.anatomical_weights.tolist() == projection.connectome.synapse_counts.tolist()


def test_sign_ordering_is_deterministic_even_when_evidence_input_is_shuffled():
    projection = _projection()
    policy = NeurotransmitterResolutionPolicy()
    first = SignedAnatomicalConnectome.from_projection(
        projection, _evidence(), policy, Shiu2024SignPolicy()
    )
    second = SignedAnatomicalConnectome.from_projection(
        projection, list(reversed(_evidence())), policy, Shiu2024SignPolicy()
    )
    assert first.presynaptic_signs.tolist() == second.presynaptic_signs.tolist()
    assert first.signed_counts.tolist() == second.signed_counts.tolist()


def test_signed_fingerprint_is_deterministic_and_policy_identity_is_part_of_it():
    first = _signed(Shiu2024SignPolicy())
    second = _signed(Shiu2024SignPolicy())
    conservative = _signed(ConservativeSignPolicy())
    assert signed_graph_fingerprint(first) == signed_graph_fingerprint(second)
    assert signed_graph_fingerprint(first) != signed_graph_fingerprint(conservative)


def test_resolved_record_type_keeps_source_provenance():
    result = NeurotransmitterResolutionPolicy().resolve(
        NeurotransmitterEvidence(9, consensus_nt="gaba", predicted_nt_confidence=0.1)
    )
    assert isinstance(result, ResolvedNeurotransmitter)
    assert result.evidence.neuron_id == 9
    assert result.resolution_policy_id == "MaleCNSV1ConsensusThenPredictedThenCelltype"
