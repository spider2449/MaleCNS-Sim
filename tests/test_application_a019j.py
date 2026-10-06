"""Production scratch ownership and frozen-expression replay certification."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import certify_application_a019j as certification


def test_frozen_replay():
    assert certification.run()["replay"] == "PASS"


def test_scratch_private_per_advance_and_reused(monkeypatch):
    lif = certification.lif
    original = lif.linear_state_update
    workspaces = []
    current = []
    def observed(v, g, **kwargs):
        scratch = kwargs["_scratch"]
        current.append(scratch)
        assert all(a.dtype == np.float64 and a.shape == (128,) for a in scratch)
        assert not np.shares_memory(*scratch)
        assert all(not np.shares_memory(a, b) for a in scratch for b in (v, g, state.v_mV, state.g_mV))
        return original(v, g, **kwargs)
    monkeypatch.setattr(lif, "linear_state_update", observed)
    runtime, stimulus, _ = certification.graph.synthetic_case(128, 8, 12)
    for state in (runtime.initial_state(), runtime.initial_state()):
        for _ in range(2):
            current.clear()
            runtime.advance(state, duration_ms=20, stimulus=stimulus)
            assert len(current) > 1
            assert all(a is current[0] for a in current)
            workspaces.append(current[0])
    assert all(not np.shares_memory(a, b) for i, left in enumerate(workspaces)
               for right in workspaces[i + 1:] for a in left for b in right)


def test_public_outputs_remain_independent():
    lif = certification.lif
    v, g = np.arange(8, dtype=np.float64), np.arange(8, dtype=np.float64)
    first = lif.linear_state_update(v, g)
    saved = [a.copy() for a in first]
    second = lif.linear_state_update(v, g)
    for a, b in zip(first, saved):
        certification.graph.base.exact(a, b)
    assert all(not np.shares_memory(a, b) for a in first for b in (*second, v, g))


def test_ordered_out_operations_and_no_result_payload_allocation(monkeypatch):
    lif = certification.lif
    scratch = (np.empty(8), np.empty(8))
    v, g = np.arange(8, dtype=np.float64), np.arange(8, dtype=np.float64)
    expected = certification.frozen(v, g)
    calls = []
    for name in ("subtract", "multiply", "add"):
        original = getattr(np, name)
        def observed(*args, _name=name, _original=original, **kwargs):
            calls.append((_name, kwargs["out"]))
            return _original(*args, **kwargs)
        monkeypatch.setattr(np, name, observed)
    def forbidden(*args, **kwargs):
        raise AssertionError("no ndarray payload allocation in scratch update")
    monkeypatch.setattr(np, "empty", forbidden)
    actual = lif.linear_state_update(v, g, _scratch=scratch)
    assert [name for name, _ in calls] == ["subtract", "multiply", "add", "multiply", "add", "multiply"]
    assert [np.shares_memory(out, scratch[0]) for _, out in calls] == [True, True, True, False, True, False]
    for a, b in zip(expected, actual):
        certification.graph.base.exact(a, b)
