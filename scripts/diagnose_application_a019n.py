"""Bounded synthetic dependency audit; no production optimization."""
import hashlib
import json
from dataclasses import replace
from pathlib import Path

import validation_firewall as guard

if not guard.ACTIVE:
    raise RuntimeError("active source firewall required before workload imports")

import numpy as np
from malecns_sim.dynamics import stimulus as source
from malecns_sim.dynamics import lif
import benchmark_application_a019f as graph


def split_grid(value_ms, dt_ms, name):
    """Isolated valid-float-dt prototype retaining event arithmetic verbatim.

    Admission is a diagnostic precondition, not an implemented runtime invariant.
    Non-admitted inputs use the complete original validator.
    """
    if type(dt_ms) is not float or not np.isfinite(dt_ms) or dt_ms <= 0:
        return ORIGINAL(value_ms, dt_ms, name)
    value = source._number(value_ms, name)
    dt = dt_ms
    steps = int(round(value / dt))
    if steps < 0 or not np.isclose(value, steps * dt, rtol=0.0, atol=1e-10):
        raise ValueError(f"{name}={value_ms!r} is not exactly representable on dt={dt_ms!r}")
    return steps


ORIGINAL = source._grid_steps


def packed(stimulus, dt=0.1, steps=200, prototype=False):
    old = source._grid_steps
    try:
        if prototype:
            source._grid_steps = split_grid
        return source.schedule_events(stimulus, neuron_positions=np.arange(1, 129),
                                      duration_steps=steps, dt_ms=dt)
    finally:
        source._grid_steps = old


def digest(batches):
    payload = b"".join(str(step).encode() + ids.tobytes() + weights.tobytes()
                       for step, (ids, weights) in batches.items())
    return hashlib.sha256(payload).hexdigest()


def outcome(stimulus, dt, steps, prototype):
    try:
        return ("ok", digest(packed(stimulus, dt, steps, prototype)))
    except (ValueError, TypeError, KeyError) as error:
        return (type(error).__name__, str(error))


def exact_batches(left, right):
    """Check ordered keys and array dtype/shape/bytes without digest inference."""
    assert list(left) == list(right)
    for step in left:
        for expected, actual in zip(left[step], right[step]):
            graph.exact(expected, actual)


def run():
    runtime, _, _ = graph.synthetic_case(128, 8, "E0")
    def events(times):
        return source.ExplicitStimulus((source.SpikeSchedule(1, times),), weight_mV=30)
    rows = []
    base = events((0., 5., 19.9))
    for name, payload, dt, steps in (
        ("A1", base, .1, 200), ("A2", base, .1, 200),
        ("B_fresh_state", base, .1, 200),
        ("C_count", events((0., 5., 5., 19.9)), .1, 200),
        ("D_times", events((0., 6., 19.9)), .1, 200),
        ("E_dt", events((0., 5., 19.8)), .2, 100),
        ("window", base, .1, 100),
    ):
        # Instrument the exact helper boundary and retain scalar results.
        calls = []
        old = source._grid_steps
        def observed(value, dt, label):
            result = old(value, dt, label)
            calls.append(dict(value=value, dt=dt, step=result,
                              reconstructed=result * dt, aligned=True))
            return result
        try:
            source._grid_steps = observed
            result = outcome(payload, dt, steps, False)
        finally:
            source._grid_steps = old
        left, right = packed(base), packed(base)
        assert left is not right and not np.shares_memory(left[0][0], right[0][0])
        rows.append(dict(case=name, intermediates=calls, result=result,
                         grid_calls=len(calls), dt_number_calls=len(calls),
                         packing_array_count=(2 * len(packed(payload, dt, steps))
                                              if result[0] == "ok" else 0),
                         result_identity_reused=False))
    boundary_cases = [(), (0.,), (5., 5., 0.), (19.9,), (20.,),
                      (np.nextafter(5., -np.inf),), (np.nextafter(5., np.inf),),
                      (5. - 2e-10,), (5. + 2e-10,)]
    checked = 0
    for times in boundary_cases:
        for dt in (.1, .2, 0., -1., float("nan"), True):
            payload = events(times)
            assert outcome(payload, dt, 200, False) == outcome(payload, dt, 200, True)
            if outcome(payload, dt, 200, False)[0] == "ok":
                exact_batches(packed(payload, dt), packed(payload, dt, prototype=True))
            checked += 1
    # Input constructors sort schedules/times and preserve duplicate occurrences.
    payload = source.ExplicitStimulus((source.SpikeSchedule(2, (5., 0.)),
                                      source.SpikeSchedule(1, (5., 5., 19.9))), weight_mV=30)
    assert packed(payload)[50][0].tolist() == [0, 0, 1]
    assert outcome(payload, .1, 200, False) == outcome(payload, .1, 200, True)
    exact_batches(packed(payload), packed(payload, prototype=True))
    replay = []
    for delay in (0., 1.8, 20.):
        configured = replace(runtime, parameters=replace(runtime.parameters, synaptic_delay_ms=delay))
        left, right = configured.initial_state(), configured.initial_state()
        assert not np.shares_memory(left.pending, right.pending)
        for chunk in range(2):
            expected = configured.advance(left, duration_ms=20, stimulus=payload, trace_neuron_ids=(1, 2))
            old = source._grid_steps
            try:
                source._grid_steps = split_grid
                actual = configured.advance(right, duration_ms=20, stimulus=payload, trace_neuron_ids=(1, 2))
            finally:
                source._grid_steps = old
            graph.exact(expected, actual)
            graph.exact(left, right)
            replay.append(dict(delay_ms=delay, chunk=chunk, exact=True,
                               pending_events=int(left.pending_event_counts.sum())))
    return dict(schema="a019n-feasibility-v1", classification="A019N-B", probes=rows,
                boundary_outcome_pairs=checked + 1, replay=replay,
                prototype="isolated valid-float dt split; admission still checked per event",
                allocation_accounting="source-level array constructions only; no allocator telemetry",
                synthetic_advances=12, full_real_preparations=0, real_advances=0,
                reruns_a019d_a019l=0, gpu_runs=0, arena_runs=0, interventions=0,
                downloads=0, archive_writes=0,
                accepted_registered_reads={name: 0 for name in (
                    "REAL_MAPPING", "REAL_PROVENANCE", "REAL_NEUROTRANSMITTER",
                    "REAL_ANNOTATION", "REAL_CONNECTIVITY", "REAL_NEURON_METADATA",
                    "REAL_OTHER_REGISTERED_DATA")},
                qualifier="fail-closed guarded accounting, not independent native byte telemetry")


if __name__ == "__main__":
    Path("docs/plans/a019n-feasibility-evidence.json").write_text(
        json.dumps(run(), indent=2) + "\n", encoding="utf-8")
