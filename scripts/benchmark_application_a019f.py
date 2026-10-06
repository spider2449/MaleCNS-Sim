"""Bounded in-memory synthetic CPU diagnostics; no dataset or backend routing."""
from __future__ import annotations

import argparse
from dataclasses import fields
import hashlib
import json
from pathlib import Path
from statistics import mean, median
from time import perf_counter_ns

import numpy as np

from malecns_sim.dynamics.lif import AdvanceTiming, EffectiveSignedProjection, PreparedRuntime
from malecns_sim.dynamics.stimulus import ExplicitStimulus, SpikeSchedule

SEED = 1906
CASES = [(scale, n, 8, activity) for scale, n in (("S1", 128), ("S2", 4096), ("S3", 32768))
         for activity in ("E0", "E1", "E2")] + [("S2-edge", 4096, 32, "E2")]
STATE_ARRAYS = ("v_mV", "g_mV", "refractory_until", "pending", "pending_event_counts")


def synthetic_case(n, degree, activity):
    """Generate immutable CSR arrays directly, using no source capabilities."""
    if n not in (128, 4096, 32768) or degree not in (8, 32) or activity not in ("E0", "E1", "E2"):
        raise ValueError("outside bounded synthetic matrix")
    rng = np.random.default_rng(SEED)
    ids = np.arange(1, n + 1, dtype=np.int64)
    source = np.repeat(np.arange(n, dtype=np.int64), degree)
    # Unique sorted targets per source; seed fixes the offset for each row.
    offsets = rng.integers(1, n - degree, size=n)
    targets = np.sort((np.arange(degree)[None, :] + offsets[:, None] + np.arange(n)[:, None]) % n, axis=1).ravel()
    weights = np.full(n * degree, 0.275, dtype=np.float64)
    indptr = np.arange(0, n * degree + 1, degree, dtype=np.int64)
    identity = hashlib.sha256(ids.tobytes() + targets.tobytes() + weights.tobytes()).hexdigest()
    for array in (ids, source, targets, weights, indptr):
        array.flags.writeable = False
    projection = EffectiveSignedProjection(
        ids, source, targets, weights, n * degree, 0, 0, 0.275,
        "synthetic-excitatory", "synthetic-resolved", identity, identity, identity,
        indptr, targets, weights,
    )
    count = 0 if activity == "E0" else max(1, n // (100 if activity == "E1" else 10))
    times = (0.0, 5.0, 10.0, 15.0, 19.9)
    stimulus = ExplicitStimulus(tuple(SpikeSchedule(int(i), times) for i in ids[:count]), weight_mV=30)
    return PreparedRuntime(projection), stimulus, count * len(times)


def exact(left, right):
    """Check dtype, shape and exact bytes, including output ordering."""
    if isinstance(left, np.ndarray):
        assert left.dtype == right.dtype and left.shape == right.shape
        assert left.tobytes() == right.tobytes()
    elif hasattr(left, "__dataclass_fields__"):
        for item in fields(left):
            exact(getattr(left, item.name), getattr(right, item.name))
    else:
        assert left == right


def equivalence(runtime, stimulus):
    off, on = runtime.initial_state(), runtime.initial_state()
    # Two chunks exercise nonempty pending/refractory continuation.
    for _ in range(2):
        timing = AdvanceTiming()
        a = runtime.advance(off, duration_ms=20, stimulus=stimulus, trace_neuron_ids=(1,))
        b = runtime.advance(on, duration_ms=20, stimulus=stimulus, trace_neuron_ids=(1,), timing=timing)
        exact(a, b)
        exact(off, on)
        assert timing.total_ns == sum(timing.stages_ns.values()) + timing.residual_ns
        assert timing.residual_ns >= 0
    return "exact bytes/state/output: two chunks"


def distribution(values):
    return dict(median=median(values), mean=mean(values), min=min(values), max=max(values))


def measure(runtime, stimulus, enabled):
    state = runtime.initial_state()
    runtime.advance(state, duration_ms=20, stimulus=stimulus)
    pending_before = int(state.pending_event_counts.sum(dtype=np.int64))
    timing = AdvanceTiming() if enabled else None
    start = perf_counter_ns()
    result = runtime.advance(state, duration_ms=20, stimulus=stimulus, timing=timing)
    wall = perf_counter_ns() - start
    return dict(wall_ns=wall, timing=timing.record() if timing else None,
                pending_before=pending_before, pending_after=int(state.pending_event_counts.sum(dtype=np.int64)),
                queued=result.queued_synaptic_event_count, delivered=result.delivered_synaptic_event_count,
                spikes=result.emitted_spike_count)


def run(warmups=3, repeats=10):
    import validation_firewall as firewall
    if not firewall.ACTIVE:
        raise RuntimeError("fail-closed source firewall required")
    rows = []
    for scale, n, degree, activity in CASES:
        runtime, stimulus, events = synthetic_case(n, degree, activity)
        replay = equivalence(runtime, stimulus)
        for _ in range(warmups):
            measure(runtime, stimulus, False)
            measure(runtime, stimulus, True)
        pairs = []
        for repeat in range(repeats):
            # Alternate paired order to reduce systematic drift.
            modes = (False, True) if repeat % 2 == 0 else (True, False)
            pair = {"repeat": repeat}
            for mode in modes:
                pair["on" if mode else "off"] = measure(runtime, stimulus, mode)
            pairs.append(pair)
        off = distribution([p["off"]["wall_ns"] for p in pairs])
        on = distribution([p["on"]["wall_ns"] for p in pairs])
        total = [p["on"]["timing"]["total_ns"] for p in pairs]
        stages = {}
        for stage in pairs[0]["on"]["timing"]["stages_ns"]:
            values = [p["on"]["timing"]["stages_ns"][stage] for p in pairs]
            stages[stage] = {**distribution(values), "mean_share": sum(values) / sum(total)}
        residual = [p["on"]["timing"]["residual_ns"] for p in pairs]
        delta = on["median"] - off["median"]
        rows.append(dict(case=f"{scale}-{activity}", neurons=n, edges=n*degree,
                         density=degree/n, input_events=events, duration_ms=20, seed=SEED,
                         graph_identity=runtime.projection.fingerprint, stimulus_identity=stimulus.fingerprint,
                         warmups=warmups, repeats=repeats, replay=replay, raw=pairs,
                         off_wall_ns=off, on_wall_ns=on, overhead_ns=delta,
                         overhead_percent=100*delta/off["median"],
                         total_ns=distribution(total), stages=stages,
                         residual_ns={**distribution(residual), "mean_share":sum(residual)/sum(total)}))
    return dict(schema="a019f-synthetic-cpu-evidence-v1", cases=rows,
                accounting="fail-closed guarded accounting, not independent native byte telemetry",
                counters=dict(full_real_preparations=0, real_advances=0, a019d_reruns=0, gpu_runs=0,
                              arena_runs=0, scientific_interventions=0, downloads=0, archive_writes=0),
                accepted_registered_reads={name:0 for name in (
                    "REAL_CONNECTIVITY", "REAL_ANNOTATION", "REAL_NEUROTRANSMITTER",
                    "REAL_NEURON_METADATA", "REAL_MAPPING", "REAL_PROVENANCE", "REAL_OTHER_REGISTERED_DATA")})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic", action="store_true", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = run()
    args.output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
