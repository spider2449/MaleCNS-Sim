"""Offline regression coverage for the tracked integrity gate."""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_tracked_integrity", ROOT / "scripts/check_tracked_integrity.py")
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def test_tracked_integrity_accepts_copy_and_rejects_corrupt_metadata(tmp_path: Path, monkeypatch):
    for relative in checker.PINNED_SHA256:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    assert len(checker.check(tmp_path)) == len(checker.PINNED_SHA256)

    relative = "artifacts/task017/recovery-manifest.json"
    target = tmp_path / relative
    metadata = json.loads(target.read_text(encoding="utf-8"))
    metadata["checkpoint_fingerprint"] = "0" * 64
    target.write_text(json.dumps(metadata), encoding="utf-8")
    with pytest.raises(ValueError, match="recovery-manifest.json: SHA-256 differs"):
        checker.check(tmp_path)

    # A re-pinned corrupt file must still fail its relationship to the matrix.
    monkeypatch.setitem(checker.PINNED_SHA256, relative, checker._sha256(target.read_bytes()))
    with pytest.raises(ValueError, match="Task 017 recovery: checkpoint_fingerprint mismatch"):
        checker.check(tmp_path)
