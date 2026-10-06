"""Fail-closed synthetic exact replay against the frozen A019I expression."""
from dataclasses import fields, replace
import hashlib
import json
from pathlib import Path

import numpy as np
import validation_firewall as guard
import a019j_reference as reference
import benchmark_application_a019g as graph
from malecns_sim.dynamics import lif

STARTING_SHA = "4e6d88b8ee7ad2c38ea339038c912b305c969a5f"


def digest(value):
    h = hashlib.sha256()
    def visit(item):
        if isinstance(item, np.ndarray):
            h.update(str((item.dtype.str, item.shape)).encode())
            h.update(item.tobytes())
        elif hasattr(item, "__dataclass_fields__"):
            for field in fields(item):
                h.update(field.name.encode())
                visit(getattr(item, field.name))
        else:
            h.update(repr(item).encode())
    visit(value)
    return h.hexdigest()


def frozen(v, g, *, _scratch=None, **kwargs):
    return reference.linear_state_update(v, g, **kwargs)


def run():
    if not guard.ACTIVE:
        raise RuntimeError("active source firewall required")
    production = lif.linear_state_update
    rows = []
    for name, n, degree, count in graph.CASES[:3]:
        runtime, stimulus, events = graph.synthetic_case(n, degree, count)
        for mode in ("normal", "empty", "full", "mixed"):
            states = [runtime.initial_state() for _ in range(3)]
            for state in states:
                if mode == "empty":
                    state.refractory_until[:] = 10000
                elif mode == "mixed":
                    state.refractory_until[::2] = 10000
                elif mode == "full":
                    state.v_mV[:] = -80
                    state.g_mV[:] = -2
            for chunk in range(2):
                results = []
                try:
                    lif.linear_state_update = frozen
                    results.append(runtime.advance(states[0], duration_ms=20, stimulus=stimulus, trace_neuron_ids=(1,)))
                    lif.linear_state_update = production
                    for index in (1, 2):
                        timing = lif.AdvanceTiming() if index == 2 else None
                        results.append(runtime.advance(states[index], duration_ms=20, stimulus=stimulus, trace_neuron_ids=(1,), timing=timing))
                finally:
                    lif.linear_state_update = production
                for index in (1, 2):
                    graph.base.exact(states[0], states[index])
                    graph.base.exact(results[0], results[index])
                rows.append(dict(case=name, mask=mode, chunk=chunk, events=events,
                                 state_digest=digest(states[0]), output_digest=digest(results[0]),
                                 optimized_state_digest=digest(states[1]), optimized_output_digest=digest(results[1]),
                                 instrumentation_on_state_digest=digest(states[2]), exact=True))
    tau_rows = []
    for name, n, degree, count in graph.CASES[:3]:
        base_runtime, stimulus, _ = graph.synthetic_case(n, degree, count)
        p = replace(base_runtime.parameters, tau_synapse_ms=base_runtime.parameters.tau_membrane_ms)
        runtime = lif.PreparedRuntime(base_runtime.projection, p)
        left, right = runtime.initial_state(), runtime.initial_state()
        for chunk in range(2):
            try:
                lif.linear_state_update = frozen
                expected = runtime.advance(left, duration_ms=20, stimulus=stimulus, trace_neuron_ids=(1,))
                lif.linear_state_update = production
                actual = runtime.advance(right, duration_ms=20, stimulus=stimulus, trace_neuron_ids=(1,))
            finally:
                lif.linear_state_update = production
            graph.base.exact(left, right)
            graph.base.exact(expected, actual)
            tau_rows.append(dict(case=name, chunk=chunk, equal_tau=True, state_digest=digest(left),
                                 optimized_state_digest=digest(right), output_digest=digest(expected),
                                 optimized_output_digest=digest(actual), exact=True))
    edge_rows = []
    v = np.array([-0., 0., -52., -80., np.inf, -np.inf, np.nan, 1e-300])
    g = np.array([0., -0., 2., -2., 0., 1., 3., 1e-300])
    refractory = np.array([0, 1, 2, 3, 0, 1, 2, 3])
    free = np.array([False, True, False, False, False, False, True, False])
    scratch = (np.empty(v.size), np.empty(v.size))
    for equal in (False, True):
        p = lif.REFERENCE_LIF_PARAMETERS
        if equal:
            p = replace(p, tau_synapse_ms=p.tau_membrane_ms)
        for step in range(5):
            mask = (step > refractory) | free
            for selection in (mask, np.zeros(v.size, dtype=bool), np.ones(v.size, dtype=bool)):
                x, y = v[selection], g[selection]
                with np.errstate(invalid="ignore"):
                    expected = frozen(x, y, parameters=p)
                    actual = production(x, y, parameters=p, _scratch=scratch)
                for a, b in zip(expected, actual):
                    graph.base.exact(a, b)
                edge_rows.append(dict(equal_tau=equal, step=step, k=x.size,
                                      membrane_digest=digest(actual[0]), synaptic_digest=digest(actual[1]), exact=True))
    return dict(starting_sha=STARTING_SHA, replay="PASS", state_isolation="PASS",
                cases=rows, equal_tau_chunks=tau_rows, edges=edge_rows,
                accounting="fail-closed guarded accounting, not independent native byte telemetry")


if __name__ == "__main__":
    Path("docs/plans/a019j-replay-evidence.json").write_text(json.dumps(run(), indent=2) + "\n", encoding="utf-8")
