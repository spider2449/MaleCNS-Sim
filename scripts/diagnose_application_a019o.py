"""Bounded dt-only timing and admission probes; production stays unchanged."""
import inspect
import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from statistics import median
from time import perf_counter_ns

import validation_firewall as guard

if not guard.ACTIVE:
    raise RuntimeError("active source firewall required before workload imports")

import numpy as np
import diagnose_application_a019n as prior

source = prior.source


def static_dt(dt_ms):
    """Repeat exactly the production dt-only expressions, including helper call."""
    dt = source._number(dt_ms, "dt_ms")
    if dt <= 0.0:
        raise ValueError("dt_ms must be positive")
    return dt


class GridTimer:
    def __init__(self):
        self.grid_ns = 0

    def substart(self):
        self.started = perf_counter_ns()

    def substop(self, parent, name):
        elapsed = perf_counter_ns() - self.started
        if name == "grid_validation":
            self.grid_ns += elapsed


def observed_grid(samples):
    """Insert timers around exact source statements, retaining all arithmetic."""
    text = inspect.getsource(source._grid_steps)
    assert text.count('    dt = _number(dt_ms, "dt_ms")') == 1
    assert text.count('    steps = int(round(value / dt))') == 1
    text = text.replace('    dt = _number(dt_ms, "dt_ms")',
                        '    started = clock()\n    dt = _number(dt_ms, "dt_ms")')
    text = text.replace('    steps = int(round(value / dt))',
                        '    samples.append(clock() - started)\n    steps = int(round(value / dt))')
    namespace = dict(source.__dict__, clock=perf_counter_ns, samples=samples)
    exec(compile(text, "<a019o-source-local-instrumentation>", "exec"), namespace)
    return namespace["_grid_steps"]


def capture(call):
    try:
        value = call()
        return dict(outcome="ok", empty=value == {} if isinstance(value, dict) else None)
    except (ValueError, TypeError, OverflowError) as error:
        return dict(outcome=type(error).__name__, message=str(error))


def invalid_probes():
    runtime, _, _ = prior.graph.synthetic_case(128, 8, "E0")
    state = runtime.initial_state()
    rows = []
    for label, dt in (("float", .1), ("zero", 0.), ("negative", -.1),
                      ("nan", float("nan")), ("inf", float("inf")),
                      ("negative_inf", -float("inf")), ("int", 1),
                      ("np_float64", np.float64(.1)), ("np_float32", np.float32(.1)),
                      ("numeric_string", "0.1"), ("bool", True)):
        candidate = replace(runtime, dt_ms=dt)
        state = runtime.initial_state()
        state_before = deepcopy(state)
        before = [getattr(state, name).tobytes() for name in prior.graph.STATE_ARRAYS]
        row = dict(label=label, runtime_constructed=True,
                   retained_type=type(candidate.dt_ms).__name__,
                   initial_state=capture(candidate.initial_state),
                   simulate=capture(lambda: prior.lif.simulate_lif(
                       runtime.projection, duration_ms=20., dt_ms=dt, _state=state)))
        for count in (0, 1):
            payload = source.ExplicitStimulus((source.SpikeSchedule(1, (0.,) * count),))
            row[f"schedule_{count}"] = capture(lambda: source.schedule_events(
                payload, neuron_positions=runtime.projection.neuron_ids,
                duration_steps=200, dt_ms=dt))
        assert before == [getattr(state, name).tobytes() for name in prior.graph.STATE_ARRAYS]
        row["state_arrays_unchanged"] = True
        if row["simulate"]["outcome"] != "ok":
            prior.graph.exact(state_before, state)
            row["all_state_fields_unchanged_on_failure"] = True
        rows.append(row)
    return rows


def timing(repeats=15, loops=20000):
    runtime, _, _ = prior.graph.synthetic_case(4096, 8, "E0")
    original = source._grid_steps
    cases = []
    for count in (12, 40, 409):
        payload = source.ExplicitStimulus(tuple(source.SpikeSchedule(i, (0., 5., 10., 15., 19.9))
                                                  for i in range(1, count + 1)))
        raw = []
        for repeat in range(repeats + 3):
            pair = {}
            for mode in (("off", "on") if repeat % 2 else ("on", "off")):
                samples = []
                timer = GridTimer()
                try:
                    source._grid_steps = observed_grid(samples) if mode == "on" else original
                    started = perf_counter_ns()
                    result = source.schedule_events(payload, neuron_positions=runtime.projection.neuron_ids,
                                                    duration_steps=200, dt_ms=.1, _timing=timer)
                    total = perf_counter_ns() - started
                finally:
                    source._grid_steps = original
                pair[mode] = dict(schedule_ns=total, grid_ns=timer.grid_ns,
                                  static_samples_ns=samples, static_ns=sum(samples))
                if mode == "off":
                    baseline = result
                else:
                    observed = result
            prior.exact_batches(baseline, observed)
            if repeat >= 3:
                raw.append(pair)
        cases.append(dict(events=count * 5, raw=raw,
                          grid_median_ns=median(p["off"]["grid_ns"] for p in raw),
                          static_median_ns=median(p["on"]["static_ns"] for p in raw),
                          event_remainder_median_ns=median(p["on"]["grid_ns"] - p["on"]["static_ns"] for p in raw),
                          schedule_median_ns=median(p["off"]["schedule_ns"] for p in raw),
                          instrumented_fraction_median=median(p["on"]["static_ns"] / p["on"]["grid_ns"] for p in raw),
                          extra_instrumentation_ns=median(p["on"]["grid_ns"] - p["off"]["grid_ns"] for p in raw)))
    micro = []
    for _ in range(repeats):
        started = perf_counter_ns()
        for i in range(loops):
            pass
        empty = perf_counter_ns() - started
        started = perf_counter_ns()
        for i in range(loops):
            static_dt(.1)
        elapsed = perf_counter_ns() - started
        overhead = []
        for i in range(loops):
            started = perf_counter_ns()
            overhead.append(perf_counter_ns() - started)
        micro.append(dict(loops=loops, elapsed_ns=elapsed, empty_loop_ns=empty,
                          net_per_iteration_ns=(elapsed-empty)/loops,
                          timer_pair_median_ns=median(overhead)))
    return dict(cases=cases, micro_raw=micro, graph_neurons=4096, graph_edges=32768,
                timer="perf_counter_ns", warmups=3, repeats=repeats,
                caveat="Nested timing includes clock overhead; isolated loops include wrapper call. Neither is production speedup.")


def run():
    return dict(schema="a019o-dt-validation-v1", starting_sha="afa4a94f3324fa997ade5b12d4cd435f29448cf6",
                classification="A019O-D", value="VALUE-B", production_optimization=False,
                admission_gate="FAIL: incomplete current contract",
                prototype="No new admission prototype; A019N split replay retained as regression only",
                next_task="A019P — bounded synthetic feasibility diagnostic of linear input gathers",
                structural=dict(per_event=dict(bool_type_checks=1, float_conversions=1,
                                               finite_checks=1, positive_checks=1),
                                per_call="N of each; zero for N=0",
                                per_24_calls="sum(N_i) of each; 24*N only for equal event counts",
                                derived_constants=0, explicit_ndarray_allocations=0,
                                allocation_qualifier="float(existing built-in float) reuses object; np.isfinite returns np.bool_; native allocation count unmeasured"),
                invalid_dt=invalid_probes(), timing=timing(),
                full_real_preparations=0, real_advances=0, reruns_a019d_a019l=0,
                gpu_runs=0, arena_runs=0, interventions=0, downloads=0, archive_writes=0,
                accepted_registered_reads={name: 0 for name in (
                    "REAL_MAPPING", "REAL_PROVENANCE", "REAL_NEUROTRANSMITTER", "REAL_ANNOTATION",
                    "REAL_CONNECTIVITY", "REAL_NEURON_METADATA", "REAL_OTHER_REGISTERED_DATA")},
                qualifier="fail-closed guarded accounting, not independent native byte telemetry")


if __name__ == "__main__":
    Path("docs/plans/a019o-dt-validation-evidence.json").write_text(
        json.dumps(run(), indent=2) + "\n", encoding="utf-8")
