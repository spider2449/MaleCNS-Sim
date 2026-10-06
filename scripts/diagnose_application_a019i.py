"""Guarded synthetic lifetime probes; never used by production entrypoints."""
import json
from pathlib import Path

import numpy as np
import validation_firewall as guard
from malecns_sim.dynamics import lif
import benchmark_application_a019g as graph


class Workspace:
    """Private per-advance scratch; returned views expire at the next call."""

    def __init__(self, capacity):
        self.v = np.empty(capacity, dtype=np.float64)
        self.g = np.empty(capacity, dtype=np.float64)

    def update(self, v, g, *, parameters=lif.REFERENCE_LIF_PARAMETERS,
               dt_ms=0.1, _timing=None):
        # Scope is the dense runtime's contiguous float64 gathered arrays only.
        assert v.dtype == g.dtype == np.float64 and v.shape == g.shape
        assert v.ndim == 1 and v.size <= self.v.size and _timing is None
        a, b = self.v[:v.size], self.g[:g.size]
        assert not any(np.shares_memory(x, y) for x in (a, b) for y in (v, g))
        dt = lif._finite(dt_ms, "dt_ms")
        if dt <= 0:
            raise ValueError("dt_ms must be positive")
        em = np.exp(-dt / parameters.tau_membrane_ms)
        es = np.exp(-dt / parameters.tau_synapse_ms)
        if np.isclose(parameters.tau_membrane_ms, parameters.tau_synapse_ms):
            coefficient = (dt / parameters.tau_membrane_ms) * em
        else:
            coefficient = (es - em) / (1.0 - parameters.tau_membrane_ms / parameters.tau_synapse_ms)
        np.subtract(v, parameters.v_rest_mV, out=a)
        np.multiply(a, em, out=a)
        np.add(parameters.v_rest_mV, a, out=a)
        np.multiply(g, coefficient, out=b)
        np.add(a, b, out=a)
        np.multiply(g, es, out=b)
        return a, b


def run():
    if not guard.ACTIVE:
        raise RuntimeError("active source firewall required")
    rows = []
    reference = lif.linear_state_update
    for name, n, degree, count in graph.CASES[:3]:
        runtime, stimulus, events = graph.synthetic_case(n, degree, count)
        workspace = Workspace(n)
        selections = []
        for mode in ("empty", "full", "mixed"):
            v = np.linspace(-80, 10, n, dtype=np.float64)
            g = np.linspace(-3, 4, n, dtype=np.float64)
            mask = np.zeros(n, dtype=bool) if mode == "empty" else np.ones(n, dtype=bool)
            if mode == "mixed":
                mask[::3] = False
            x, y = v[mask], g[mask]
            assert x.flags.owndata and y.flags.owndata
            assert not np.shares_memory(x, v) and not np.shares_memory(y, g)
            assert np.asarray(x) is x
            expected = reference(x, y)
            actual = workspace.update(x, y)
            for a, b in zip(expected, actual):
                graph.base.exact(a, b)
            v_before, g_before = v.copy(), g.copy()
            v[mask], g[mask] = actual
            v_before[mask], g_before[mask] = expected
            graph.base.exact(v, v_before)
            graph.base.exact(g, g_before)
            selections.append(dict(mode=mode, k=x.size, gather_bytes=x.nbytes+y.nbytes,
                                   mask_bytes=mask.nbytes, shares_state=False))
        left, right = runtime.initial_state(), runtime.initial_state()
        for _ in range(2):
            expected = runtime.advance(left, duration_ms=20, stimulus=stimulus, trace_neuron_ids=(1,))
            try:
                lif.linear_state_update = workspace.update
                actual = runtime.advance(right, duration_ms=20, stimulus=stimulus, trace_neuron_ids=(1,))
            finally:
                lif.linear_state_update = reference
            graph.base.exact(expected, actual)
            graph.base.exact(left, right)
        rows.append(dict(case=name, n=n, events=events, selections=selections,
                         full_selection_gather_bytes=16*n, membrane_output_bytes=8*n,
                         membrane_cumulative_array_payload_bytes=40*n,
                         decay_array_payload_bytes=8*n, workspace_bytes=16*n,
                         replay="two chunks exact state/result bytes"))
    return dict(schema="a019i-feasibility-v1", cases=rows,
                accounting="ndarray nbytes and source-derived payload counts; not allocator telemetry",
                classification="A019I-B", accepted_registered_reads={name: 0 for name in (
                    "REAL_MAPPING", "REAL_PROVENANCE", "REAL_NEUROTRANSMITTER", "REAL_ANNOTATION",
                    "REAL_CONNECTIVITY", "REAL_NEURON_METADATA", "REAL_OTHER_REGISTERED_DATA")})


if __name__ == "__main__":
    Path("docs/plans/a019i-feasibility-evidence.json").write_text(
        json.dumps(run(), indent=2) + "\n", encoding="utf-8")
