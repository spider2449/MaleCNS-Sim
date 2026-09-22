"""Execute the preregistered Task 017 v0.3 robustness matrix."""

from __future__ import annotations

import argparse
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
OUTPUT = ROOT / "data/derived/task017b-delivery.json"
CHECKPOINT = ROOT / "data/derived/task017-checkpoint.jsonl"
REPORT = ROOT / "data/derived/task017b-delivery-report.md"


def main() -> None:
    parser = argparse.ArgumentParser(description="Deliver bounded raw units from the frozen Task 017 matrix.")
    parser.add_argument("--variant", default=None, help="Frozen variant alias such as R0, V1, or the full variant ID.")
    parser.add_argument("--analysis", choices=("task010", "task011", "all"), default="all")
    parser.add_argument("--max-units", type=int, default=None)
    parser.add_argument("--max-runtime-minutes", type=float, default=None)
    args = parser.parse_args()
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
        variant_id=args.variant,
        analysis=args.analysis,
        max_units=args.max_units,
        max_runtime_minutes=args.max_runtime_minutes,
    )
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "report": str(REPORT),
                "specification_fingerprint": result["specification_fingerprint"],
                "current_scientific_status": result.get("current_scientific_status", result.get("global_classification")),
                "current_status": result.get("current_status"),
                "checkpoint_fingerprint": result.get("checkpoint_fingerprint"),
                "expected_unit_count": result.get("expected_unit_count"),
                "completed_before_invocation": result.get("completed_before_invocation"),
                "executed_this_invocation": result.get("executed_this_invocation"),
                "completed_after_invocation": result.get("completed_after_invocation"),
                "missing_count": result.get("missing_count"),
                "duplicate_count": result.get("duplicate_count"),
                "invalid_technical_unit_count": result.get("invalid_technical_unit_count"),
                "per_variant_completion": result.get("per_variant_completion"),
                "per_analysis_completion": result.get("per_analysis_completion"),
                "elapsed_seconds": result.get("elapsed_seconds"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
