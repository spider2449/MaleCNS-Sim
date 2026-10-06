"""Interleaved OFF corroboration; same bounded graph/event/protocol identities."""
import json
from pathlib import Path

import validation_firewall as guard
import benchmark_application_a019g as graph
import certify_application_a019j as certification
from malecns_sim.dynamics import lif


def run():
    if not guard.ACTIVE:
        raise RuntimeError("active source firewall required")
    production = lif.linear_state_update
    rows = []
    try:
        for name, n, degree, count in graph.CASES[:3]:
            runtime, stimulus, events = graph.synthetic_case(n, degree, count)
            for _ in range(3):
                for function in (certification.frozen, production):
                    lif.linear_state_update = function
                    graph.base.measure(runtime, stimulus, False)
            raw = []
            for repeat in range(10):
                pair = dict(repeat=repeat)
                modes = ("baseline", "optimized") if repeat % 2 == 0 else ("optimized", "baseline")
                for mode in modes:
                    lif.linear_state_update = certification.frozen if mode == "baseline" else production
                    pair[mode] = graph.base.measure(runtime, stimulus, False)
                raw.append(pair)
            rows.append(dict(case=name, events=events, graph_identity=runtime.projection.fingerprint,
                             stimulus_identity=stimulus.fingerprint, warmups=3, repeats=10, raw=raw,
                             summaries={mode: graph.base.distribution([p[mode]["wall_ns"] for p in raw])
                                        for mode in ("baseline", "optimized")},
                             paired_delta_ns=graph.base.distribution([p["optimized"]["wall_ns"]-p["baseline"]["wall_ns"] for p in raw])))
    finally:
        lif.linear_state_update = production
    return dict(cases=rows, limitation="Frozen expression wrapper and optimized advance scratch setup are included in both routes; corroboration only, primary baseline is pre-edit production.")


if __name__ == "__main__":
    Path("docs/plans/a019j-interleaved-evidence.json").write_text(json.dumps(run(), indent=2) + "\n", encoding="utf-8")
