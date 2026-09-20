import json

import pytest

from malecns_sim.analysis.task007a import (
    MN9CandidateEvidence,
    MN9_CANDIDATE_IDS,
    LineageRelation,
    build_mn9_evidence_matrix,
    evidence_fingerprint,
    lineage_result,
    normalize_evidence,
    task007a_fingerprint,
)
from malecns_sim.homology import MappingStatus


def _lineage(**kwargs):
    defaults = dict(
        dataset="flywire_fafb_production",
        materialization="630",
        source_version="test-v1",
        source_url="https://example.invalid/lineage",
        queried_at_utc="2026-09-20T00:00:00Z",
        valid_at_materialization=True,
        valid_at_query=None,
        raw_result_category="test",
    )
    defaults.update(kwargs)
    return lineage_result("720575940620900446", **defaults)


def _candidate(body_id, **kwargs):
    values = dict(
        flywire_type_match=True,
        across_brain_mapping="CB0701 -> MN9",
        side="R" if body_id == "16949" else "L",
        motor_superclass="cb_motor",
        manc_match="none",
        neuronbridge_match="no direct target match",
        morphology_support="qualitative only",
        nerve_soma_support="PhN; MN9 instance",
        dimorphism_status="isomorphic type evidence; candidate row missing",
        contradictory_evidence=(),
        evidence_sources=("fixture",),
    )
    values.update(kwargs)
    return MN9CandidateEvidence(body_id, **values)


def test_one_to_one_lineage_result_is_explicit():
    result = _lineage(descendant_root_ids=("9",))
    assert result.relation is LineageRelation.ONE_TO_ONE
    assert result.descendant_root_ids == ("9",)


def test_split_lineage_preserves_all_descendants():
    result = _lineage(descendant_root_ids=("11", "10", "11"))
    assert result.relation is LineageRelation.SPLIT
    assert result.descendant_root_ids == ("10", "11")


def test_merge_lineage_preserves_all_parents():
    result = _lineage(
        descendant_root_ids=("20",),
        merged_parent_root_ids=("18", "17"),
    )
    assert result.relation is LineageRelation.MERGE
    assert result.descendant_root_ids == ("20",)
    assert result.merged_parent_root_ids == ("17", "18")


def test_unresolved_lineage_does_not_infer_from_absence():
    result = _lineage(
        valid_at_query=None,
        descendant_root_ids=(),
        raw_result_category="authentication_required_no_payload",
        notes=("absence is not lineage",),
    )
    assert result.relation is LineageRelation.UNRESOLVED
    assert result.valid_at_query is None
    assert result.descendant_root_ids == ()


def test_version_provenance_is_retained():
    result = _lineage(source_version="v3.0.0", materialization="783")
    assert (result.source_version, result.materialization) == ("v3.0.0", "783")


def test_lineage_and_type_evidence_remain_separate():
    payload = {
        "lineage": {"relation": "UNRESOLVED", "descendants": []},
        "annotation": {"release": "v3.0.0", "cell_type": "LB3"},
    }
    normalized = normalize_evidence(payload)
    assert normalized["lineage"] != normalized["annotation"]
    assert normalized["annotation"]["cell_type"] == "LB3"


def test_mn9_evidence_matrix_is_canonical_and_complete():
    matrix = build_mn9_evidence_matrix((_candidate("16949"), _candidate("10331")))
    assert tuple(item.body_id for item in matrix.candidates) == MN9_CANDIDATE_IDS
    assert matrix.final_status is MappingStatus.TYPE_LEVEL


def test_contradictory_evidence_is_preserved():
    matrix = build_mn9_evidence_matrix(
        (
            _candidate("10331", contradictory_evidence=("reference is right; candidate is left",)),
            _candidate("16949"),
        )
    )
    assert matrix.candidates[0].contradictory_evidence == ("reference is right; candidate is left",)


def test_exact_rule_requires_individual_support_and_exclusion():
    matrix = build_mn9_evidence_matrix(
        (
            _candidate("10331", flywire_type_match=False, other_candidates_ruled_out=True),
            _candidate(
                "16949",
                individual_correspondence_indicated=True,
                individual_homolog_supported=True,
                other_candidates_ruled_out=True,
            ),
        )
    )
    assert matrix.final_status is MappingStatus.EXACT


def test_type_level_rule_keeps_multiple_valid_candidates():
    matrix = build_mn9_evidence_matrix((_candidate("10331"), _candidate("16949")))
    assert matrix.final_status is MappingStatus.TYPE_LEVEL


def test_ambiguous_rule_preserves_pointing_evidence_without_selection():
    matrix = build_mn9_evidence_matrix(
        (
            _candidate("10331", individual_correspondence_indicated=True),
            _candidate("16949", individual_correspondence_indicated=True),
        )
    )
    assert matrix.final_status is MappingStatus.AMBIGUOUS


def test_ranking_alone_cannot_select_a_winner():
    matrix = build_mn9_evidence_matrix(
        (
            _candidate("10331", ranking_only=True),
            _candidate("16949"),
        )
    )
    assert matrix.final_status is MappingStatus.TYPE_LEVEL


def test_dynamics_evidence_is_rejected_at_construction():
    with pytest.raises(ValueError, match="dynamics evidence"):
        _candidate("10331", dynamics_evidence=("mn9_mean_hz",))


def test_evidence_ordering_is_deterministic():
    first = normalize_evidence({"b": ["2", "1"], "a": {"y": 2, "x": 1}})
    second = normalize_evidence({"a": {"x": 1, "y": 2}, "b": ["1", "2"]})
    assert first == second


def test_task007a_fingerprint_is_deterministic_and_identity_sensitive():
    payload = {
        "lineage": {"root": "720575940620900446", "descendants": []},
        "mn9": {"status": "AMBIGUOUS", "candidates": ["10331", "16949"]},
    }
    first = evidence_fingerprint(payload)
    second = evidence_fingerprint(json.loads(json.dumps(payload)))
    assert first == second
    changed = dict(payload, mn9={"status": "TYPE_LEVEL", "candidates": ["10331", "16949"]})
    assert evidence_fingerprint(changed) != first


def test_combined_task007a_fingerprint_covers_both_records():
    lineage = {"root": "720575940620900446", "descendants": []}
    mn9 = {"status": "AMBIGUOUS", "candidates": ["10331", "16949"]}
    first = task007a_fingerprint(lineage, mn9)
    second = task007a_fingerprint(dict(reversed(tuple(lineage.items()))), dict(reversed(tuple(mn9.items()))))
    assert first == second
    assert task007a_fingerprint(lineage, {**mn9, "status": "TYPE_LEVEL"}) != first
