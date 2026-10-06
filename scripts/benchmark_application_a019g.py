"""Controlled synthetic substage diagnostics extending the A019F runner."""
import argparse
import json
from pathlib import Path
import benchmark_application_a019f as base
from malecns_sim.dynamics.stimulus import ExplicitStimulus, SpikeSchedule

CASES = [("G1", 128, 8, 12), ("G2", 4096, 8, 12), ("G3", 32768, 8, 12),
         ("E0", 4096, 8, 1), ("E1", 4096, 8, 40), ("E2", 4096, 8, 409)]
_original_case = base.synthetic_case


def synthetic_case(n, degree, count):
    if (n, degree, count) not in [row[1:] for row in CASES]:
        raise ValueError("outside bounded synthetic matrix")
    runtime, _, _ = _original_case(n, degree, "E0")
    times = (0.0, 5.0, 10.0, 15.0, 19.9)
    stimulus = ExplicitStimulus(tuple(SpikeSchedule(i, times) for i in range(1, count + 1)), weight_mV=30)
    return runtime, stimulus, count * len(times)


def run(warmups=3, repeats=10):
    old_case, old_cases = base.synthetic_case, base.CASES
    try:
        base.synthetic_case, base.CASES = synthetic_case, CASES
        evidence = base.run(warmups, repeats)
    finally:
        base.synthetic_case, base.CASES = old_case, old_cases
    evidence["schema"] = "a019g-synthetic-substage-evidence-v1"
    for row in evidence["cases"]:
        row["edges_per_neuron"] = row["edges"] // row["neurons"]
        row["substage_summary"] = {}
        for parent, names in row["raw"][0]["on"]["timing"]["substages_ns"].items():
            summaries = {}
            parent_total = sum(p["on"]["timing"]["stages_ns"][parent] for p in row["raw"])
            full_total = sum(p["on"]["timing"]["total_ns"] for p in row["raw"])
            for name in (*names, "residual"):
                values = [p["on"]["timing"]["substage_residual_ns"][parent] if name == "residual"
                          else p["on"]["timing"]["substages_ns"][parent][name] for p in row["raw"]]
                assert min(values) >= 0
                summaries[name] = dict(base.distribution(values), parent_share=sum(values)/parent_total,
                                       full_share=sum(values)/full_total)
            for pair in row["raw"]:
                t = pair["on"]["timing"]
                assert sum(t["substages_ns"][parent].values()) + t["substage_residual_ns"][parent] == t["stages_ns"][parent]
            row["substage_summary"][parent] = summaries
        row["overhead_class"] = "OHD-A" if row["overhead_percent"] <= 5 else "OHD-B" if row["overhead_percent"] <= 15 else "OHD-C"
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic", action="store_true", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(run(), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
