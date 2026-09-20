import inspect

import pytest

from malecns_sim.analysis.task007b import (
    LateralityEvidence,
    OrganismSide,
    apply_mn9_laterality,
    laterality_evidence_fingerprint,
    normalize_laterality_evidence,
    normalize_side,
    resolve_mn9_laterality,
)
from malecns_sim.analysis.task007 import build_task007_result
from malecns_sim.homology import MaleCNSCandidate, MappingRecord, MappingStatus, define_mn9_readout


def _vfb(*, side="right", contradictory=False):
    return LateralityEvidence(
        source="Virtual Fly Brain",
        source_version="current",
        source_url="https://www.virtualflybrain.org/term/cb0701-vfb_fw000395/",
        source_id="VFB_fw000395",
        organism_side=side,
        relationship_fields=(
            ("flywire_root", "720575940660219265"),
            ("flywire_type", "CB0701"),
            ("has_soma_location", f"{side} side of organism"),
        ),
        contradictory=contradictory,
    )


def _shiu(*, side="right", stimulus="left", contradictory=False):
    return LateralityEvidence(
        source="Shiu et al. 2024 Nature",
        source_version="PMC11446845",
        source_url="https://pmc.ncbi.nlm.nih.gov/articles/PMC11446845/",
        source_id="Shiu-2024-Methods-sugar-MN9",
        organism_side=side,
        relationship_fields=(
            ("stimulus_side", stimulus),
            ("mn9_relation", "contralateral"),
            ("mn9_side", side),
        ),
        coordinate_system_note="true biological side after FAFB inversion",
        contradictory=contradictory,
    )


def _candidate(body_id, side=None, *, flywire_type="CB0701", cell_type="MN9"):
    return MaleCNSCandidate(
        body_id=str(body_id),
        type=cell_type,
        instance=(f"MN9_{side}" if side else None),
        flywire_type=flywire_type,
        soma_side=side,
        superclass="cb_motor",
        subclass="pm",
        exit_nerve="PhN",
    )


def test_laterality_evidence_representation_normalizes_explicit_relationships():
    evidence = _vfb(side="R")
    assert evidence.organism_side is OrganismSide.RIGHT
    assert dict(evidence.relationship_fields)["flywire_root"] == "720575940660219265"


def test_left_right_normalization_is_explicit_and_fail_closed():
    assert normalize_side("L") is OrganismSide.LEFT
    assert normalize_side("left side of organism") is OrganismSide.LEFT
    assert normalize_side("R") is OrganismSide.RIGHT
    with pytest.raises(ValueError):
        normalize_side("mirror-left")


def test_contradictory_side_evidence_blocks_promotion():
    result = resolve_mn9_laterality(_vfb(), _shiu(side="left", stimulus="left"), (_candidate(10331, "L"), _candidate(16949, "R")))
    assert result.status is MappingStatus.AMBIGUOUS
    assert result.preferred_readout is None


def test_unique_right_side_candidate_is_side_resolved():
    result = resolve_mn9_laterality(_vfb(), _shiu(), (_candidate(10331, "L"), _candidate(16949, "R")))
    assert result.status is MappingStatus.SIDE_RESOLVED
    assert result.preferred_readout == "16949"


def test_multiple_same_side_candidates_remain_ambiguous():
    result = resolve_mn9_laterality(_vfb(), _shiu(), (_candidate(16949, "R"), _candidate(20000, "R")))
    assert result.status is MappingStatus.AMBIGUOUS
    assert result.preferred_readout is None


def test_type_alone_does_not_resolve_without_explicit_candidate_side():
    result = resolve_mn9_laterality(_vfb(), _shiu(), (_candidate(10331), _candidate(16949)))
    assert result.status is MappingStatus.TYPE_LEVEL
    assert result.preferred_readout is None


def test_resolution_api_has_no_simulation_result_input():
    assert "simulation" not in inspect.signature(resolve_mn9_laterality).parameters
    with pytest.raises(TypeError):
        resolve_mn9_laterality(_vfb(), _shiu(), (_candidate(16949, "R"),), simulation_result={"mn9_hz": 999})


def test_coordinate_system_note_is_preserved():
    payload = {"shiu": {"coordinate_system_note": _shiu().coordinate_system_note}}
    normalized = normalize_laterality_evidence(payload)
    assert normalized["shiu"]["coordinate_system_note"] == "true biological side after FAFB inversion"


def test_laterality_fingerprint_is_deterministic():
    first = {"b": ["right", "left"], "a": {"source": "VFB", "side": "right"}}
    second = {"a": {"side": "right", "source": "VFB"}, "b": ["left", "right"]}
    assert laterality_evidence_fingerprint(first) == laterality_evidence_fingerprint(second)


def test_resolved_readout_retains_laterality_provenance():
    record = MappingRecord(
        reference_order=21,
        reference_role="mn9",
        shiu_v630_root_id="720575940660219265",
        flywire_materialization="630",
        flywire_annotation_release="v1.0.0",
        flywire_type="CB0701",
        updated_root_ids=(),
        lineage_method="not_queried",
        male_cns_release="v1.0",
        candidates=(_candidate(10331, "L"), _candidate(16949, "R")),
        status=MappingStatus.AMBIGUOUS,
        evidence_sources=("MaleCNS v1.0",),
        evidence_notes=("Task 007a ambiguity",),
    )
    resolution = resolve_mn9_laterality(_vfb(), _shiu(), record.candidates)
    resolved = apply_mn9_laterality(record, resolution)
    readout = define_mn9_readout(resolved)
    assert resolved.status is MappingStatus.SIDE_RESOLVED
    assert resolved.candidate_body_ids == ("16949",)
    assert readout.selected_body_id == "16949"
    assert "VFB_fw000395" in readout.provenance
    assert "Shiu-2024-Methods-sugar-MN9" in readout.provenance


def test_production_task007_readout_uses_only_the_resolved_mn9_body():
    result = build_task007_result(
        "data/raw/male-cns/v1.0/body-annotations-male-cns-v1.0-minconf-0.5.feather",
        "data/raw/male-cns/v1.0/body-neurotransmitters-male-cns-v1.0.feather",
    )
    assert result.mn9_readout.status is MappingStatus.SIDE_RESOLVED
    assert result.mn9_readout.candidate_body_ids == ("16949",)
    assert result.mn9_readout.selected_body_id == "16949"
    assert result.sugar_population_fingerprint == "2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b"
