"""Run the frozen Task 010 causal perturbation matrix."""

from __future__ import annotations

import json
from pathlib import Path

from malecns_sim.analysis.task010 import run_task010


ROOT = Path(__file__).resolve().parents[1]
ANNOTATION = ROOT / "data/raw/male-cns/v1.0/body-annotations-male-cns-v1.0-minconf-0.5.feather"
NEUROTRANSMITTER = ROOT / "data/raw/male-cns/v1.0/body-neurotransmitters-male-cns-v1.0.feather"
WEIGHTS = ROOT / "data/raw/male-cns/v1.0/connectome-weights-male-cns-v1.0-minconf-0.5.feather"
TASK008_RESULTS = ROOT / "data/derived/task008-results.json"
TASK009_RESULTS = ROOT / "data/derived/task009-results.json"
CACHE = ROOT / "data/derived/task008/full-prepared-graph.npz"
OUTPUT = ROOT / "data/derived/task010-results.json"


def main() -> None:
    result = run_task010(
        ANNOTATION,
        NEUROTRANSMITTER,
        WEIGHTS,
        TASK008_RESULTS,
        TASK009_RESULTS,
        CACHE,
        OUTPUT,
    )
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "head": result["head"],
                "candidate_manifest_fingerprint": result["candidate_manifest"]["fingerprint"],
                "result_digest": result["result_digest"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
