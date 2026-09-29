"""Read-only validation of the local Task 017 checkpoint."""

from __future__ import annotations

import argparse
from pathlib import Path

from malecns_sim.analysis.task017_portability import DEFAULT_CHECKPOINT_RELATIVE, main_audit


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Task 017 checkpoint records and sidecars without mutation.")
    parser.add_argument("--checkpoint", type=Path, default=ROOT / DEFAULT_CHECKPOINT_RELATIVE)
    args = parser.parse_args()
    main_audit(ROOT, args.checkpoint)


if __name__ == "__main__":
    main()
