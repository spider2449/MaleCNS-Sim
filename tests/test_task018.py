"""Synthetic checks for the frozen Task 018 partition and decision rule."""

from malecns_sim.analysis.task018 import canonical_json, partition, result_digest, sensitivity


def test_partition_aggregates_shared_unique_duplicate_and_autapse():
    edges = [(1, 10331, 3), (1, 10331, 4), (1, 16949, 2), (2, 10331, 6), (3, 16949, 3), (10331, 10331, 1)]
    result = partition(edges)
    assert (result["left_total"], result["right_total"], result["gap"]) == (14, 5, 9)
    assert result["components"] == {"shared": 5, "left_only": 7, "right_only": -3}
    assert result["partner_counts"] == {"left": 3, "right": 2, "shared": 1, "left_only": 2, "right_only": 1}
    assert result["partition_identity_verified"]
    assert result["classification"] == "LEFT_ONLY_INPUT_LARGEST"


def test_classification_all_positive_gap_branches_and_tie():
    assert partition([(1, 10331, 8), (1, 16949, 1)])["classification"] == "SHARED_PARTNER_DIFFERENCE_LARGEST"
    assert partition([(1, 10331, 6), (2, 16949, 4)])["classification"] == "LEFT_ONLY_INPUT_LARGEST"
    assert partition([(1, 10331, 5), (1, 16949, 1), (2, 10331, 4), (3, 16949, 5)])["classification"] == "RIGHT_ONLY_OFFSET_LARGEST"
    tied = partition([(1, 10331, 4), (2, 16949, 4), (3, 10331, 2), (3, 16949, 1)])
    assert tied["classification"] == "TIED_LARGEST_COMPONENTS"
    assert tied["tied_components"] == ["left_only", "right_only"]


def test_nonpositive_and_failure():
    assert partition([(1, 10331, 2), (2, 16949, 2)])["classification"] == "NO_LEFT_INCOMING_WEIGHT_EXCESS_IN_THIS_GRAPH"
    assert partition([(1, 16949, 3)])["fractions_null_reason"] == "reversed_gap"
    assert partition([])["fractions_null_reason"] == "zero_gap"
    assert partition([(1, 10331, 0)])["classification"] == "INDETERMINATE"
    assert partition([(1, 10331, 1)], left=1, right=1)["classification"] == "INDETERMINATE"


def test_sensitivity_aggregates_before_threshold_and_does_not_modify_primary():
    edges = [(1, 10331, 2), (1, 10331, 3), (1, 16949, 4), (2, 16949, 5)]
    primary = partition(edges)
    filtered = sensitivity(edges)
    assert filtered["label"] == "SENSITIVITY_MIN_SYNAPSES_5"
    assert filtered["left_total"] == 5
    assert filtered["right_total"] == 5
    assert filtered["partner_counts"]["shared"] == 0
    assert primary["classification"] == "NO_LEFT_INCOMING_WEIGHT_EXCESS_IN_THIS_GRAPH"


def test_order_and_canonical_digest():
    edges = [(2, 10331, 5), (1, 16949, 1), (3, 10331, 2)]
    assert partition(edges) == partition(reversed(edges))
    assert canonical_json({"b": 2, "a": 1}) == b'{"a":1,"b":2}'
    payload = {"b": 2, "a": 1}
    digest = result_digest(payload)
    assert result_digest({"a": 1, "b": 2, "result_digest": digest}) == digest
