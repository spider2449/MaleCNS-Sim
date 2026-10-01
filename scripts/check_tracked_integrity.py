"""Verify tracked reproducibility evidence without external data or execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


PINNED_SHA256 = {
    "artifacts/task017/complete-matrix-manifest.json": "73c9e51ae06e7d924f80c75578536c6d1ce2b0cf5e2657041ddcfdf5a2262cd8",
    "artifacts/task017/recovery-manifest.json": "f65261013717d7cc7739cdfbdd4c6e4c002f0b22bc4edbba50ac1952d0810208",
    "artifacts/task017/robustness-scoring.json": "85b920b79cb941b9dae9648d655494f35e0694492ae02ea53a9da4d46343fa99",
    "artifacts/task018/execution-result.json": "b112712fc747c41332ebd5772c4ba24839f1c2f771e04533e34fdc24ca490e89",
    "data/provenance/male-cns-v1.0.json": "c1d1f347ab5937a0fda1b22609bbdbb551cdd21dac4750e357f4b215ec724517",
    "data/provenance/shiu-2024-v630.json": "32bfb588515dcd7c3a88e6ffcdd84b2a8d909b9a6aa0105d57e89e4ca75c63c7",
    "data/provenance/task008a-preserved-task008.json": "408328fbd55d7c9aae3b91c054841e890180ee07d4b7c7f03f1535fbbc963174",
    "data/derived/task008-results.json": "694698dbaa995e9eb563943fe58df14d3da2dd6f71aa9d21ecc205de43733691",
    "docs/plans/2026-09-30-task-018-mn9-anatomical-asymmetry-preregistration.md": "4f767ab2bfcbf5e5773a803ee6fdb601e39d5521d7f30a12d35a3a5506de5bb4",
}


def _require(condition: bool, object_name: str, check: str) -> None:
    if not condition:
        raise ValueError(f"{object_name}: {check}")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tracked_bytes(data: bytes) -> bytes:
    """Use Git's LF-normalized text identity across checkout configurations."""
    return data.replace(b"\r\n", b"\n")


def check(root: Path) -> list[str]:
    root = root.resolve()
    objects = {}
    for relative, expected in PINNED_SHA256.items():
        path = root / relative
        _require(path.is_file(), relative, "tracked file missing")
        data = path.read_bytes()
        _require(_sha256(_tracked_bytes(data)) == expected, relative, "SHA-256 differs from frozen tracked identity")
        if path.suffix == ".json":
            objects[relative] = json.loads(data)

    matrix = objects["artifacts/task017/complete-matrix-manifest.json"]
    recovery = objects["artifacts/task017/recovery-manifest.json"]
    scoring = objects["artifacts/task017/robustness-scoring.json"]
    task018 = objects["artifacts/task018/execution-result.json"]
    preserved = objects["data/provenance/task008a-preserved-task008.json"]
    _require(matrix["schema"] == "malecns-sim-task017-complete-matrix-v1", "Task 017 matrix", "schema mismatch")
    _require(matrix["completed"] == matrix["expected"] == 3168 and matrix["pending"] == 0, "Task 017 matrix", "completion mismatch")
    _require(matrix["complete_matrix_digest"] == matrix["canonical_record_set_digest"], "Task 017 matrix", "record digest mismatch")
    for field in ("task016_fingerprint", "checkpoint_fingerprint", "journal_sha256", "sidecar_inventory_sha256"):
        _require(matrix[field] == recovery[field], "Task 017 recovery", f"{field} mismatch")
    _require(recovery["schema_version"] == "malecns-sim-task017-recovery-point-v1", "Task 017 recovery", "schema mismatch")
    _require(recovery["completed_units"] == recovery["expected_units"] == 3168 and recovery["remaining_units"] == 0, "Task 017 recovery", "completion mismatch")
    _require(recovery["pending_unit_keys"] == [], "Task 017 recovery", "pending units present")
    _require(re.fullmatch(r"[0-9a-f]{64}", recovery["bundle_sha256"]) is not None, "Task 017 recovery", "external bundle digest malformed")
    _require(recovery["bundle_filename"] == "task017-recovery-bundle.zip", "Task 017 recovery", "bundle filename mismatch")
    provenance = scoring["provenance"]
    for field, expected in (
        ("complete_matrix_digest", matrix["complete_matrix_digest"]),
        ("complete_matrix_manifest_sha256", PINNED_SHA256["artifacts/task017/complete-matrix-manifest.json"]),
        ("journal_sha256", matrix["journal_sha256"]),
        ("sidecar_inventory_sha256", matrix["sidecar_inventory_sha256"]),
    ):
        _require(provenance[field] == expected, "Task 017 scoring", f"{field} mismatch")
    content = dict(scoring["scientific_content"])
    recorded = content.pop("deterministic_scoring_digest")
    encoded = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    computed = _sha256(content["schema"].encode("utf-8") + b"\0" + encoded)
    _require(recorded == computed, "Task 017 scoring", "deterministic scoring digest mismatch")
    _require(content["checkpoint_fingerprint"] == matrix["checkpoint_fingerprint"], "Task 017 scoring", "checkpoint fingerprint mismatch")
    _require(content["complete_matrix_digest"] == matrix["complete_matrix_digest"], "Task 017 scoring", "matrix digest mismatch")

    _require(task018["schema"] == "malecns-sim-task018-anatomical-asymmetry-v1", "Task 018", "schema mismatch")
    _require(task018["integrity_status"] == "PASS", "Task 018", "recorded integrity status mismatch")
    # Task 018 recorded the historical Windows CRLF working-file digest.
    male_manifest = _tracked_bytes((root / "data/provenance/male-cns-v1.0.json").read_bytes())
    _require(task018["manifest_sha256"] == _sha256(male_manifest.replace(b"\n", b"\r\n")), "Task 018", "raw-data manifest identity mismatch")
    prereg = "docs/plans/2026-09-30-task-018-mn9-anatomical-asymmetry-preregistration.md"
    _require(task018["preregistration_sha256"] == PINNED_SHA256[prereg], "Task 018", "preregistration identity mismatch")
    payload = {key: value for key, value in task018.items() if key != "result_digest"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    _require(task018["result_digest"] == _sha256(encoded), "Task 018", "result digest mismatch")

    for relative in ("data/provenance/male-cns-v1.0.json", "data/provenance/shiu-2024-v630.json"):
        manifest = objects[relative]
        _require(bool(manifest["files"]), relative, "empty file manifest")
        for entry in manifest["files"]:
            _require(re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is not None, relative, "external file digest malformed")
    task008_path = "data/derived/task008-results.json"
    task008_bytes = _tracked_bytes((root / task008_path).read_bytes())
    _require(preserved["task008_result_path"] == task008_path, "Task 008", "preserved result path mismatch")
    _require(preserved["task008_result_file_sha256"] == _sha256(task008_bytes.replace(b"\n", b"\r\n")), "Task 008", "historical result identity mismatch")
    return list(PINNED_SHA256)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        checked = check(args.root)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"Integrity FAIL: {error}")
        return 1
    print(f"Integrity PASS: {len(checked)} tracked files and internal identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
