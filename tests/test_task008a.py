import json
from pathlib import Path

import pytest

from malecns_sim.analysis.task008a import (
    CURRENT_TASK008_SIDE_FIELD,
    POPULATION_SIDE_CORRECTION_REQUIRED,
    UNRESOLVED,
    VALID_AS_RUN,
    SugarCandidateAuditRecord,
    build_laterality_audit,
    classify_task008_side_rule,
    population_symmetric_difference,
)


def _candidate(
    body_id,
    soma_side=None,
    root_side="L",
    *,
    instance="LB3a_L",
    entry_nerve="MxLbN",
    type_name="LB3a",
):
    return SugarCandidateAuditRecord(
        body_id=str(body_id),
        type=type_name,
        instance=instance,
        flywire_type="LB3",
        superclass="cb_sensory",
        cell_class="gustatory",
        subclass="labellar bristle",
        soma_side=soma_side,
        root_side=root_side,
        soma_neuromere=None,
        entry_nerve=entry_nerve,
        receptor_type=None,
        matching_notes=None,
        status="Traced",
        status_label=None,
        exit_nerve=None,
        soma_location=None,
        to_soma_location=None,
        synonyms=None,
        vfb_id=None,
        hemibrain_type=None,
        manc_type=None,
        manc_body_id=None,
    )


def test_crosstab_and_mismatched_side_detection_are_explicit():
    audit = build_laterality_audit(
        [_candidate(3, "R", "L", instance="LB3a_R"), _candidate(1), _candidate(2, "L", "L")],
        all_lb3_count=3,
    )
    assert [(cell.side, cell.root_side, cell.count) for cell in audit.crosstab] == [
        ("<missing>", "L", 1),
        ("L", "L", 1),
        ("R", "L", 1),
    ]
    assert audit.nonmissing_mismatch_body_ids == ("3",)


def test_missing_side_handling_and_deterministic_candidate_ordering():
    audit = build_laterality_audit(
        [_candidate(20, root_side="R", instance="LB3a_R"), _candidate(2), _candidate(10)],
        all_lb3_count=3,
    )
    assert tuple(item.body_id for item in audit.candidates) == ("2", "10", "20")
    assert audit.missing_soma_side_body_ids == ("2", "10", "20")
    assert audit.missing_root_side_body_ids == ()


def test_soma_and_root_population_construction_and_symmetric_difference():
    audit = build_laterality_audit(
        [
            _candidate(1, "L", "L"),
            _candidate(2, "R", "R", instance="LB3a_R"),
            _candidate(3, "L", "R", instance="LB3a_L"),
        ],
        all_lb3_count=3,
    )
    assert audit.soma_left_body_ids == ("1", "3")
    assert audit.root_left_body_ids == ("1",)
    assert audit.intersection_body_ids == ("1", "2")
    assert population_symmetric_difference(audit) == {
        "left_soma_only": ("3",),
        "left_root_only": (),
        "right_soma_only": (),
        "right_root_only": ("3",),
    }


def test_side_rule_provenance_and_non_circular_decision_model():
    assert CURRENT_TASK008_SIDE_FIELD == "rootSide"
    assert classify_task008_side_rule("rootSide", "rootSide") == VALID_AS_RUN
    assert classify_task008_side_rule("somaSide", "rootSide") == POPULATION_SIDE_CORRECTION_REQUIRED
    assert classify_task008_side_rule("rootSide", None) == UNRESOLVED
    with pytest.raises(ValueError, match="cannot consult dynamics"):
        classify_task008_side_rule("rootSide", "rootSide", dynamics_consulted=True)


def test_instance_suffix_is_corroboration_only_and_not_side_selection():
    audit = build_laterality_audit(
        [_candidate(1, root_side="L", instance="LB3a_R"), _candidate(2, root_side="R", instance=None)],
        all_lb3_count=2,
    )
    assert audit.instance_suffix_mismatch_body_ids == ("1",)
    assert audit.instance_missing_body_ids == ("2",)
    assert audit.root_left_body_ids == ("1",)
    assert audit.root_right_body_ids == ("2",)


def test_task008_result_preservation_manifest_is_explicit():
    manifest = json.loads(
        Path("data/provenance/task008a-preserved-task008.json").read_text(encoding="utf-8")
    )
    assert manifest["current_side_field"] == "rootSide"
    assert manifest["backend"] == "cuda-float64"
    assert manifest["task008_result_file_sha256"] == (
        "30dc0b57be64a8272a77763bc28d25409b6a6e489e15f87ef91a4ea785a80595"
    )
    assert len(manifest["sugar_left_body_ids"]) == 42
    assert len(manifest["sugar_right_body_ids"]) == 43
    assert set(manifest["seed_manifest_sha256"]) == {
        "primary",
        "mirror_100hz",
        "normalized_100hz",
        "min_synapses_5_100hz",
        "repeat_100hz",
    }


def test_population_audit_fingerprint_is_stable_without_a_correction():
    candidates = [_candidate(2, root_side="R", instance="LB3a_R"), _candidate(1)]
    first = build_laterality_audit(candidates, all_lb3_count=2)
    second = build_laterality_audit(tuple(reversed(candidates)), all_lb3_count=2)
    assert first.fingerprint == second.fingerprint
