"""Run the structural-only Task 009 analysis and write an ignored JSON report."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path

from malecns_sim.analysis.task009 import run_task009


ROOT = Path(__file__).resolve().parents[1]
ANNOTATION = ROOT / "data/raw/male-cns/v1.0/body-annotations-male-cns-v1.0-minconf-0.5.feather"
NEUROTRANSMITTER = ROOT / "data/raw/male-cns/v1.0/body-neurotransmitters-male-cns-v1.0.feather"
WEIGHTS = ROOT / "data/raw/male-cns/v1.0/connectome-weights-male-cns-v1.0-minconf-0.5.feather"
OUTPUT = ROOT / "data/derived/task009-results.json"


def _json_default(value):
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"unsupported JSON value: {type(value)!r}")


def main() -> None:
    result = run_task009(ANNOTATION, NEUROTRANSMITTER, WEIGHTS)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True, default=_json_default) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(OUTPUT), "fingerprints": result["fingerprints"], "repeat": result["repeat"]}, indent=2))


if __name__ == "__main__":
    main()
