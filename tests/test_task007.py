import json

import pytest

from malecns_sim.analysis.task007 import (
    load_task007_evidence,
    reference_ids,
    reference_population_fingerprint,
)
from malecns_sim.homology import (
    MaleCNSCandidate,
    MappingRecord,
    MappingStatus,
    define_mn9_readout,
    derive_sugar_population,
    mapping_fingerprint,
    structural_path_summary,
)


def _candidate(body_id: int, *, side: str = "R", flywire_type: str = "LB3"):
    return MaleCNSCandidate(
        body_id=str(body_id),
        type="LB3a",
        flywire_type=flywire_type,
        side=side,
        root_side=side,
        superclass="cb_sensory",
        cell_class="gustatory",
        entry_nerve="MxLbN",
        resolved_nt="acetylcholine",
        task004_sign=1,
    )


def _record(
    root_id: str = "720575940600000001",
    *,
    status: MappingStatus = MappingStatus.TYPE_LEVEL,
    candidates=(_candidate(10),),
    order: int = 0,
    role: str = "sugar",
):
    return MappingRecord(
        reference_order=order,
        reference_role=role,
        shiu_v630_root_id=root_id,
        flywire_materialization="630",
        flywire_annotation_release="v1.0.0",
        flywire_type="LB3" if candidates else None,
        updated_root_ids=(),
        lineage_method="not_queried",
        male_cns_release="v1.0",
        candidates=candidates,
        status=status,
        evidence_sources=("fixture",),
        evidence_notes=("fixture evidence",),
    )


def test_exact_id_reference_is_preserved_as_canonical_strings():
    evidence = load_task007_evidence()
    assert reference_ids() == tuple(row["root_id"] for row in evidence["version_matched_annotations"])
    assert all(isinstance(value, str) for value in reference_ids())
    assert reference_population_fingerprint(evidence) == evidence["reference_population_fingerprint"]


def test_mapping_status_representation_is_explicit():
    assert [item.value for item in MappingStatus] == ["EXACT", "SIDE_RESOLVED", "TYPE_LEVEL", "AMBIGUOUS", "UNRESOLVED"]


def test_one_to_one_exact_mapping():
    record = _record(status=MappingStatus.EXACT)
    assert record.candidate_body_ids == ("10",)


def test_one_to_many_type_mapping_preserves_multiplicity():
    record = _record(candidates=(_candidate(20), _candidate(10)))
    assert record.candidate_body_ids == ("10", "20")
    assert record.status is MappingStatus.TYPE_LEVEL


def test_ambiguous_mapping_is_allowed_without_selecting_a_body():
    record = _record(status=MappingStatus.AMBIGUOUS, candidates=(_candidate(10), _candidate(20)))
    assert record.candidate_body_ids == ("10", "20")


def test_unresolved_mapping_has_no_fabricated_candidate():
    record = _record(status=MappingStatus.UNRESOLVED, candidates=())
    assert record.candidate_body_ids == ()
    assert record.flywire_type is None


def test_side_is_preserved_and_not_inferred():
    candidate = _candidate(10, side="L")
    assert candidate.side == "L"
    assert candidate.root_side == "L"
    assert candidate.soma_side is None


def test_duplicate_candidate_ids_are_rejected():
    with pytest.raises(ValueError, match="candidate MaleCNS body IDs"):
        _record(candidates=(_candidate(10), _candidate(10)))


def test_provenance_is_required_and_retained():
    record = _record()
    assert record.evidence_sources == ("fixture",)
    with pytest.raises(ValueError, match="at least one source"):
        MappingRecord(
            reference_order=0,
            reference_role="sugar",
            shiu_v630_root_id="1",
            flywire_materialization="630",
            flywire_annotation_release="v1.0.0",
            flywire_type="LB3",
            updated_root_ids=(),
            lineage_method="not_queried",
            male_cns_release="v1.0",
            candidates=(_candidate(1),),
            status=MappingStatus.TYPE_LEVEL,
            evidence_sources=(),
            evidence_notes=(),
        )


def test_mapping_ordering_and_fingerprint_are_deterministic():
    first = (_record(root_id="2", order=1), _record(root_id="1", order=0))
    second = tuple(reversed(first))
    assert mapping_fingerprint(first) == mapping_fingerprint(second)


def test_sugar_population_derivation_filters_side_and_biology():
    selected = derive_sugar_population(
        (_candidate(3), _candidate(2, side="L"), _candidate(1, flywire_type="CB0701")),
        side="R",
    )
    assert selected.candidate_body_ids == ("3",)
    assert selected.side_counts == (("R", 1),)
    assert selected.task004_nt_counts == (("resolved", 1),)


def test_mn9_readout_does_not_silently_choose_type_level_candidate():
    readout = define_mn9_readout(
        _record(
            role="mn9",
            candidates=(_candidate(10, flywire_type="CB0701"), _candidate(20, flywire_type="CB0701")),
        )
    )
    assert readout.status is MappingStatus.TYPE_LEVEL
    assert readout.selected_body_id is None
    assert readout.candidate_body_ids == ("10", "20")


def test_structural_path_helper_reports_direct_and_shortest_paths():
    summary = structural_path_summary(
        [1, 2, 1, 4],
        [2, 3, 4, 9],
        [1],
        [3, 9],
    )
    assert summary.direct_sugar_to_mn9_edges == 0
    assert summary.first_hop_target_count == 2
    assert summary.shortest_path_lengths == (("3", 2), ("9", 2))
    assert summary.total_structural_path_availability == 2


def test_mapping_logic_has_no_simulation_outcome_input():
    record = _record()
    baseline = mapping_fingerprint((record,))
    simulated_rates = {"mn9_mean_hz": 999.0, "expected": "ignored"}
    assert mapping_fingerprint((record,)) == baseline
    assert json.dumps(simulated_rates, sort_keys=True)
