"""Verify and atomically restore a portable Task 017 checkpoint bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from malecns_sim.analysis.task017_portability import restore_recovery_bundle


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify and import a Task 017 recovery bundle.")
    parser.add_argument("bundle_directory", type=Path, help="Directory containing the zip and recovery manifest")
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="Destination repository root")
    args = parser.parse_args()
    audit = restore_recovery_bundle(
        args.bundle_directory,
        args.repo_root,
        require_tracked_recovery_point=True,
    )
    print(json.dumps({
        "status": "RESTORED_AND_AUDITED",
        "completed_units": audit.completed_count,
        "expected_units": audit.expected_count,
        "pending_count": len(audit.pending_keys),
        "task016_fingerprint": audit.task016_fingerprint,
        "checkpoint_fingerprint": audit.fingerprint,
        "journal_sha256": audit.journal_sha256,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
