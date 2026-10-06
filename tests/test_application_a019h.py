"""Linear-local boundaries, baseline replay and guarded bounded matrix."""
import importlib.util
import os
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import benchmark_application_a019h as h
from malecns_sim.dynamics import lif


def test_new_schema_and_reconciliation(monkeypatch):
    monkeypatch.setattr(h, "CASES", [h.CASES[0]])
    evidence = h.run(0, 2)
    row = evidence["cases"][0]
    assert evidence["schema"] == "a019h-linear-local-evidence-v1"
    for pair in row["raw"]:
        t = pair["on"]["timing"]
        stages = t["substages_ns"]["linear_update"]
        assert all(stages[n] > 0 for n in h.NEW)
        assert sum(stages.values()) + t["substage_residual_ns"]["linear_update"] == t["stages_ns"]["linear_update"]
    assert all(v == 0 for v in evidence["accepted_registered_reads"].values())


def test_starting_commit_exact_replay():
    # Optional external frozen module, prepared from the authorized starting SHA.
    path = os.environ.get("A019H_BASELINE_MODULE")
    if not path:
        pytest.skip("external starting-SHA module is required for baseline certification")
    spec = importlib.util.spec_from_file_location("a019h_baseline", path)
    baseline = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = baseline
    spec.loader.exec_module(baseline)
    for _, n, degree, count in h.CASES:
        runtime, stimulus, _ = h.previous.synthetic_case(n, degree, count)
        a, b = runtime.initial_state(), runtime.initial_state()
        for _ in range(2):
            left = lif.simulate_lif(runtime.projection, duration_ms=20, stimulus=stimulus, _state=a, trace_neuron_ids=(1,))
            right = baseline.simulate_lif(runtime.projection, duration_ms=20, stimulus=stimulus, _state=b, trace_neuron_ids=(1,))
            h.previous.base.exact(left, right)
            h.previous.base.exact(a, b)


def test_scalar_return_exact():
    timing = lif.AdvanceTiming()
    timing.begin()
    assert lif.linear_state_update(-51., 2.) == lif.linear_state_update(-51., 2., _timing=timing)
    assert timing.substages_ns["linear_update"]["return_shape_check"] > 0


def test_cli_bounds(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["a019h", "--output", "unused.json"])
    with pytest.raises(SystemExit):
        h.main()
