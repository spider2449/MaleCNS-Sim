"""Audit and export a portable Task 017 checkpoint recovery bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from malecns_sim.analysis.task017_portability import DEFAULT_CHECKPOINT_RELATIVE, write_recovery_bundle


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a portable, audited Task 017 recovery bundle.")
    parser.add_argument("destination", type=Path, help="New external bundle directory")
    parser.add_argument("--checkpoint", type=Path, default=ROOT / DEFAULT_CHECKPOINT_RELATIVE)
    args = parser.parse_args()
    bundle, manifest_path, manifest = write_recovery_bundle(args.checkpoint, args.destination, root=ROOT)
    print(json.dumps({
        "bundle": str(bundle),
        "bundle_sha256": manifest["bundle_sha256"],
        "manifest": str(manifest_path),
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "completed_units": manifest["completed_units"],
        "expected_units": manifest["expected_units"],
        "pending_count": manifest["pending_count"],
        "checkpoint_fingerprint": manifest["checkpoint_fingerprint"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
