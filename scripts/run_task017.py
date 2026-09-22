"""Execute the preregistered Task 017 v0.3 robustness matrix."""

from __future__ import annotations

import json
from pathlib import Path

from malecns_sim.analysis.task017 import run_task017


ROOT = Path(__file__).resolve().parents[1]
ANNOTATION = ROOT / "data/raw/male-cns/v1.0/body-annotations-male-cns-v1.0-minconf-0.5.feather"
NEUROTRANSMITTER = ROOT / "data/raw/male-cns/v1.0/body-neurotransmitters-male-cns-v1.0.feather"
WEIGHTS = ROOT / "data/raw/male-cns/v1.0/connectome-weights-male-cns-v1.0-minconf-0.5.feather"
TASK008_RESULTS = ROOT / "data/derived/task008-results.json"
TASK009_RESULTS = ROOT / "data/derived/task009-results.json"
TASK010_RESULTS = ROOT / "data/derived/task010-results.json"
TASK011_RESULTS = ROOT / "data/derived/task011-results.json"
CACHE = ROOT / "data/derived/task008/full-prepared-graph.npz"
OUTPUT = ROOT / "data/derived/task017-results.json"
CHECKPOINT = ROOT / "data/derived/task017-checkpoint.jsonl"
REPORT = ROOT / "docs/plans/2026-09-22-task-017r-recover-v0.3-robustness-execution.md"


def main() -> None:
    result = run_task017(
        ANNOTATION,
        NEUROTRANSMITTER,
        WEIGHTS,
        TASK008_RESULTS,
        TASK009_RESULTS,
        TASK010_RESULTS,
        TASK011_RESULTS,
        CACHE,
        OUTPUT,
        REPORT,
        CHECKPOINT,
    )
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "report": str(REPORT),
                "specification_fingerprint": result["specification_fingerprint"],
                "result_digest": result["result_digest"],
                "global_classification": result["global_classification"],
                "task010_style_simulations": result["actual_simulation_counts"]["task010_style"],
                "temporal_trace_simulations": result["actual_simulation_counts"]["temporal_traces"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
