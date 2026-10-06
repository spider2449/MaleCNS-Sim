"""Guarded synthetic gather order, lifetime and exact replay checks."""
import sys
from pathlib import Path

import validation_firewall as guard

assert guard.ACTIVE
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import diagnose_application_a019p as diagnostic


def test_selection_bits_arithmetic_writeback_and_scratch_overlap():
    result = diagnostic.selection_probes()
    assert len(result["rows"]) == 18
    assert all(row["exact_bytes"] for row in result["rows"])
    assert result["both_scratch_reuse"].startswith("REJECT")


def test_changing_masks_consecutive_chunks_and_independent_states():
    rows = diagnostic.replay()
    assert len(rows) == 3
    assert all(row["chunks"] == 3 and row["cross_state_isolated"] for row in rows)
    assert all(len(row["observed_k"]) > 1 for row in rows)


def test_mask_cardinality_structural_payload_and_copy_ownership():
    for row in diagnostic.structural():
        assert row["observed_k_max"] == row["n"]
        assert row["observed_k_min"] < row["n"]
        for case in row["scenarios"]:
            assert case["total_bytes"] == 16 * case["k"]
            assert case["mask_bytes"] == row["n"]


def test_fail_closed_registered_source_categories():
    result = diagnostic.firewall()
    assert result["active"] and result["blocked_probes"] == 7
    assert len(result["accepted_registered_reads"]) == 7
    assert not any(result["accepted_registered_reads"].values())


def test_eager_masked_out_arithmetic_changes_exception_behavior():
    assert diagnostic.masked_alternative()["eager"].startswith("REJECT")
