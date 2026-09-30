"""Score the sealed Task 017 matrix without executing simulations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from malecns_sim.analysis.task017_scoring import write_scoring_artifact


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only preregistered Task 017 robustness scoring.")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/task017/robustness-scoring.json")
    args = parser.parse_args()
    payload = write_scoring_artifact(ROOT, args.output)
    scientific = payload["scientific_content"]
    print(
        json.dumps(
            {
                "output": args.output.relative_to(ROOT).as_posix() if args.output.is_relative_to(ROOT) else "external",
                "global_classification": scientific["global_classification"],
                "deterministic_scoring_digest": scientific["deterministic_scoring_digest"],
                "cells_scored": scientific["coverage"]["cells_scored"],
                "nonreference_variants_evaluated": scientific["coverage"]["nonreference_variants_evaluated"],
                "simulations_executed": scientific["execution_claims"]["simulation_count"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
