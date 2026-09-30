from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from malecns_sim.analysis import task017
from malecns_sim.analysis.task017_scoring import _ReadOnlyCheckpoint, _digest


def test_scoring_digest_is_canonical_and_repeatable():
    left = {"b": 2, "a": [1, 3]}
    right = {"a": [1, 3], "b": 2}
    assert _digest("scoring-test-v1", left) == _digest("scoring-test-v1", right)
    assert _digest("scoring-test-v1", left) == _digest("scoring-test-v1", left)


@pytest.mark.parametrize(
    ("reference", "alternative", "expected"),
    [
        ("MIXED", "MIXED", 1.0),
        ("NETWORK_REDISTRIBUTION_COMPATIBLE", "MIXED", 0.5),
        ("SHORT_PATH_COMPATIBLE", "MIXED", 0.5),
        ("SHORT_PATH_COMPATIBLE", "NETWORK_REDISTRIBUTION_COMPATIBLE", 0.0),
        ("UNRESOLVED", "MIXED", 0.0),
    ],
)
def test_frozen_mechanism_compatibility_scores(reference, alternative, expected):
    assert task017._compatibility_score(reference, alternative) == expected


def test_read_only_checkpoint_fails_closed_on_missing_units(tmp_path: Path):
    checkpoint = _ReadOnlyCheckpoint(tmp_path, type("Audit", (), {"records": ()})())
    key = task017.Task017UnitKey("R0_REFERENCE_TASK005", "10313", "LEFT", 0, "task010_intervention")
    with pytest.raises(RuntimeError, match="refused missing checkpoint unit"):
        checkpoint.get(key, "unused")
    assert checkpoint.read_count == 1


def test_read_only_lookup_is_independent_of_journal_record_order(tmp_path: Path, monkeypatch):
    keys = (
        task017.Task017UnitKey("R0_REFERENCE_TASK005", "10313", "LEFT", 0, "task010_intervention"),
        task017.Task017UnitKey("R0_REFERENCE_TASK005", "10313", "LEFT", 1, "task010_intervention"),
    )
    records = tuple(
        {"key": key.as_record(), "unit_fingerprint": f"fingerprint-{index}", "result_artifact": f"{key.token}.npz"}
        for index, key in enumerate(keys)
    )
    monkeypatch.setattr(task017, "_read_result_artifact", lambda path: path.name)
    forward = _ReadOnlyCheckpoint(tmp_path / "first", SimpleNamespace(records=records))
    reversed_order = _ReadOnlyCheckpoint(tmp_path / "second", SimpleNamespace(records=tuple(reversed(records))))
    left = [forward.get(key, f"fingerprint-{index}") for index, key in enumerate(keys)]
    right = [reversed_order.get(key, f"fingerprint-{index}") for index, key in enumerate(keys)]
    assert left == right
