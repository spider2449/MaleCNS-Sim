"""Run the fixed Task 011 temporal mechanism audit."""

from __future__ import annotations

import json
from pathlib import Path

from malecns_sim.analysis.task011 import run_task011


ROOT = Path(__file__).resolve().parents[1]
ANNOTATION = ROOT / "data/raw/male-cns/v1.0/body-annotations-male-cns-v1.0-minconf-0.5.feather"
NEUROTRANSMITTER = ROOT / "data/raw/male-cns/v1.0/body-neurotransmitters-male-cns-v1.0.feather"
WEIGHTS = ROOT / "data/raw/male-cns/v1.0/connectome-weights-male-cns-v1.0-minconf-0.5.feather"
TASK008_RESULTS = ROOT / "data/derived/task008-results.json"
TASK009_RESULTS = ROOT / "data/derived/task009-results.json"
TASK010_RESULTS = ROOT / "data/derived/task010-results.json"
CACHE = ROOT / "data/derived/task008/full-prepared-graph.npz"
OUTPUT = ROOT / "data/derived/task011-results.json"


def main() -> None:
    result = run_task011(
        ANNOTATION,
        NEUROTRANSMITTER,
        WEIGHTS,
        TASK008_RESULTS,
        TASK009_RESULTS,
        TASK010_RESULTS,
        CACHE,
        OUTPUT,
    )
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "head": result["head"],
                "status": result["status"],
                "result_digest": result["result_digest"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
