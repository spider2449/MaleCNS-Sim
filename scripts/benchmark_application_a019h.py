"""Bounded linear-local diagnostics reusing the guarded A019G matrix runner."""
import argparse
import json
from pathlib import Path
import benchmark_application_a019g as previous

CASES = [row for row in previous.CASES if row[0] != "E1"]
OLD = ("mask", "coefficients", "membrane", "synaptic_decay", "writeback")
NEW = ("allowed_reduction", "input_gather", "return_shape_check")
SOURCE_MAP = [
    dict(function="simulate_lif", span="lif.py:581-589", operation="parent entry, mask timer setup and np.any(allowed)",
         shape="allowed bool[N] -> bool scalar", boundary="Python -> NumPy reduction", allocation="scalar only; mask temporaries already in mask", indexing=False, reduction=True,
         timing="allowed_reduction; entry/hooks remain residual"),
    dict(function="simulate_lif", span="lif.py:592-599", operation="v[allowed], g[allowed], call keyword binding and tuple unpack",
         shape="two float64[N] -> two float64[K], K=count_nonzero(allowed)", boundary="Python -> NumPy advanced indexing -> Python call",
         allocation="two existing gathered arrays; no additional array copy", indexing=True, reduction=False,
         timing="input_gather; call entry/unpack/cleanup remain residual"),
    dict(function="linear_state_update", span="lif.py:141-143", operation="function entry and first substart",
         shape="two float64[K] arguments", boundary="Python", allocation="call frame", indexing=False, reduction=False,
         timing="residual; no clean exclusive interval without nested hooks"),
    dict(function="linear_state_update", span="lif.py:154-169", operation="between timers, np.ndim(v_mV), branch and tuple return",
         shape="ndim scalar; tuple of two float64[K] arrays", boundary="Python -> NumPy shape inspection -> Python",
         allocation="return tuple; scalar path float conversion; ndarray path no semantic copy", indexing=False, reduction=False,
         timing="return_shape_check; tuple return and hook bookkeeping remain residual"),
    dict(function="simulate_lif", span="lif.py:599-606", operation="gather reference release, writeback timer hooks, parent close",
         shape="two gathered float64[K] released; v/g float64[N]", boundary="Python refcount/NumPy indexed writeback",
         allocation="no new semantic array; indexed scatter already in writeback", indexing=True, reduction=False,
         timing="writeback unchanged; cleanup/hooks remain residual"),
    dict(function="PreparedRuntime.advance", span="lif.py:438-457", operation="runtime checks, simulate_lif arguments and result return",
         shape="state N; pending ring_size x N", boundary="Python", allocation="call frames/result reference", indexing=False, reduction=False,
         timing="outside linear parent; existing full advance residual"),
    dict(function="simulate_lif_active", span="lif.py:787-794", operation="active_positions, refractory gathers, allowed_positions, linear arguments/writeback",
         shape="active int64[A], allowed bool[A], arguments float64[K]", boundary="Python -> NumPy indexing",
         allocation="fromiter and gathered arrays", indexing=True, reduction=False,
         timing="alternate immediate caller; not used by PreparedRuntime.advance or this matrix; unchanged"),
]


def metadata():
    return dict(authorization="user authorized A019H including commit/push",
                starting_sha="cabe0d750ee9cc830a9fd8be889f69acb940af92",
                source_module="src/malecns_sim/dynamics/lif.py", source_map=SOURCE_MAP,
                old_residual_percent_range=[17.4, 31.4], new_substages=list(NEW),
                classification="A019H-B", semantics="exact ON/OFF and starting-SHA OFF replay PASS; no changed array/FP/event operations",
                default="OFF", reconciliation_error_ns=0,
                target_proven=False,
                target_gate="Gathers directly measured, concrete and substantial at G2/G3; membrane and writeback remain substantial alternatives. No unique first target justified.",
                next_task="A019I — bounded synthetic allocation/lifetime and contract-preserving feasibility diagnostic of linear input gathers versus membrane evaluation and indexed writeback; no optimization",
                limitations=["G neurons and edges co-vary; source confirms no edge access in linear operations",
                             "No calibrated statistical confidence; measured intervals include hook entry overhead",
                             "Call/return, reference cleanup and timer bookkeeping remain residual, not localized as other",
                             "No full-real inference, schedule reinstrumentation or optimization"],
                scaling={"input_gather":"neuron-sensitive", "allowed_reduction":"mixed", "return_shape_check":"unclear",
                         "mask":"neuron-sensitive", "membrane":"neuron-sensitive", "writeback":"neuron-sensitive",
                         "synaptic_decay":"neuron-sensitive", "coefficients":"fixed/per-call"})


def run(warmups=3, repeats=10):
    old = previous.CASES
    try:
        previous.CASES = CASES
        evidence = previous.run(warmups, repeats)
    finally:
        previous.CASES = old
    evidence["schema"] = "a019h-linear-local-evidence-v1"
    evidence.update(metadata())
    for row in evidence["cases"]:
        raw = row["raw"]
        parent = [p["on"]["timing"]["stages_ns"]["linear_update"] for p in raw]
        summary = {}
        for label, names in (("previous_named_sum", OLD), ("newly_explained", NEW)):
            values = [sum(p["on"]["timing"]["substages_ns"]["linear_update"][n] for n in names) for p in raw]
            summary[label] = dict(previous.base.distribution(values), parent_share=sum(values)/sum(parent))
        summary["parent"] = previous.base.distribution(parent)
        summary["remaining"] = row["substage_summary"]["linear_update"]["residual"]
        row["linear_local_summary"] = summary
        for pair in raw:
            t = pair["on"]["timing"]
            assert t["total_ns"] == sum(t["stages_ns"].values()) + t["residual_ns"]
    evidence["new_residual_percent_range"] = [
        100 * min(r["linear_local_summary"]["remaining"]["parent_share"] for r in evidence["cases"]),
        100 * max(r["linear_local_summary"]["remaining"]["parent_share"] for r in evidence["cases"]),
    ]
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic", action="store_true", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(run(), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
