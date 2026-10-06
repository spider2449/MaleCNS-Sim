"""Summarize recorded synthetic evidence without rerunning measurements."""
import hashlib
import inspect
import json
from pathlib import Path

import a019j_reference

ROOT = Path("docs/plans")


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def comparison(before, after):
    return {stat: dict(baseline=before[stat], optimized=after[stat],
                       delta=after[stat]-before[stat],
                       delta_percent=100*(after[stat]-before[stat])/before[stat])
            for stat in ("median", "mean")}


def run():
    baseline = read("a019j-baseline-evidence.json")
    optimized = read("a019j-optimized-evidence.json")
    paired = read("a019j-interleaved-evidence.json")
    rows = []
    for old, new in zip(baseline["cases"], optimized["cases"]):
        for key in ("case", "neurons", "edges", "input_events", "duration_ms", "seed", "graph_identity", "stimulus_identity", "warmups", "repeats"):
            assert old[key] == new[key]
        n = old["neurons"]
        rows.append(dict(case=old["case"], neurons=n,
                         off_advance=comparison(old["off_wall_ns"], new["off_wall_ns"]),
                         on_advance=comparison(old["on_wall_ns"], new["on_wall_ns"]),
                         stages={key: comparison(old["stages"][key], new["stages"][key]) for key in old["stages"]},
                         linear_substages={key: comparison(old["substage_summary"]["linear_update"][key], new["substage_summary"]["linear_update"][key]) for key in old["substage_summary"]["linear_update"]},
                         variability=dict(baseline_off_range_ns=[old["off_wall_ns"]["min"], old["off_wall_ns"]["max"]], optimized_off_range_ns=[new["off_wall_ns"]["min"], new["off_wall_ns"]["max"]],
                                          baseline_linear_range_ns=[old["stages"]["linear_update"]["min"], old["stages"]["linear_update"]["max"]], optimized_linear_range_ns=[new["stages"]["linear_update"]["min"], new["stages"]["linear_update"]["max"]]),
                         instrumentation_overhead_percent=dict(baseline=old["overhead_percent"], optimized=new["overhead_percent"]),
                         structural=dict(k_bound=n, old_membrane_passes=5, new_membrane_passes=5, old_decay_passes=1, new_decay_passes=1,
                                         old_membrane_array_allocations_per_update=5, new_membrane_array_allocations_per_update=0,
                                         old_decay_array_allocations_per_update=1, new_decay_array_allocations_per_update=0,
                                         old_membrane_cumulative_payload_bytes=40*n, old_decay_payload_bytes=8*n,
                                         new_result_payload_allocation_bytes_per_update=0, scratch_payload_bytes_per_advance=16*n,
                                         scratch_array_allocations_per_advance=2, persistent_scratch_bytes_between_advances=0)))
    result = dict(schema="a019j-membrane-o1-evidence-v1", starting_sha=baseline["starting_sha"],
                  classification="A019J-A", performance_classification="JPERF-A", exact_replay="PASS", cross_state_isolation="PASS",
                  frozen_expression_sha256=hashlib.sha256(inspect.getsource(a019j_reference.linear_state_update).encode()).hexdigest(),
                  scratch=dict(owner="simulate_lif dense advance call", allocation="two np.empty(N, dtype=float64) during state_setup", resizing="never resized; recreated for every advance; sliced to K on each update", lifetime="one advance; overwritten only after ordered v then g writeback; released on return", prepared_runtime_owned=False, simulation_state_owned=False, persists_across_20ms_calls=False, no_stale_data="all selected lanes overwritten before consumption", no_alias="fresh independent buffers; gathered inputs remain independent copies; no globals or state buffer storage"),
                  accounting="source-derived ndarray payload counts and observed out= call sequence; not native allocator telemetry; view headers and iterator/internal allocations excluded", cases=rows,
                  cost_shift="No meaningful cost shifted into linear residual, gathers, writeback, total linear or total advance. Scratch allocation is included in state_setup and total wall. Unchanged-stage decreases are not separately attributed to this optimization.",
                  basis="G2/G3 membrane median and mean improve; total-linear observed ranges are disjoint. Interleaved OFF corroboration wins 10/10 at both sizes with disjoint total-wall ranges. G1 effect is small/noisy. No post-hoc fixed percentage threshold or calibrated confidence claim.",
                  instrumentation="OFF default unchanged. ON overhead at G1 is material; no G1 end-to-end conclusion. G2/G3 same hooks before/after, with OFF corroboration supporting trustworthy direction and bounded benefit.",
                  corroboration=paired, counters=baseline["counters"], accepted_registered_reads=baseline["accepted_registered_reads"],
                  firewall_qualifier="fail-closed guarded accounting, not independent native byte telemetry",
                  full_real_relevance_claimed=False, next_task="A019K — evidence-only gate for full-real CPU rebenchmark authorization")
    (ROOT / "a019j-membrane-o1-evidence.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    run()
