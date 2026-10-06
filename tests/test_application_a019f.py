"""Exact CPU observation and bounded synthetic-runner certification."""
import inspect
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import benchmark_application_a019f as h
from malecns_sim.dynamics import lif


@pytest.mark.parametrize("activity", ["E0", "E1", "E2"])
def test_exact_chunk_replay_and_accounting(activity):
    runtime, stimulus, _ = h.synthetic_case(128, 8, activity)
    assert h.equivalence(runtime, stimulus)
    state = runtime.initial_state()
    timing = lif.AdvanceTiming()
    runtime.advance(state, duration_ms=20, stimulus=stimulus, timing=timing)
    record = timing.record()
    assert record["schema"] == "cpu-advance-timing-v1"
    assert tuple(record["stages_ns"]) == lif.ADVANCE_STAGES
    assert all(isinstance(x, int) and x >= 0 for x in record["stages_ns"].values())
    assert record["stage_sum_ns"] == sum(record["stages_ns"].values())
    assert record["total_ns"] == record["stage_sum_ns"] + record["residual_ns"]
    if activity != "E0":
        assert state.pending_event_counts.any()
        assert (state.refractory_until >= state.timestep).any()


def test_off_default_never_reads_clock(monkeypatch):
    runtime, stimulus, _ = h.synthetic_case(128, 8, "E2")
    def forbidden():
        raise AssertionError("disabled instrumentation called timer")
    monkeypatch.setattr(lif, "perf_counter_ns", forbidden)
    assert inspect.signature(runtime.advance).parameters["timing"].default is None
    a, b = runtime.initial_state(), runtime.initial_state()
    result = runtime.advance(a, duration_ms=20, stimulus=stimulus)
    reference = lif.simulate_lif(runtime.projection, duration_ms=20, stimulus=stimulus, _state=b)
    h.exact(result, reference)
    h.exact(a, b)


def test_runner_guard_and_bounds(monkeypatch):
    import validation_firewall as f
    assert f.ACTIVE
    with pytest.raises(f.SourceAccessDenied):
        open(f.ROOT / "data" / "male-cns-v1" / "annotation.feather", "rb")
    monkeypatch.setattr(f, "ACTIVE", False)
    with pytest.raises(RuntimeError, match="firewall required"):
        h.run()
    with pytest.raises(ValueError, match="bounded synthetic"):
        h.synthetic_case(1000000, 8, "E2")


def test_runner_uses_no_catalog_or_loader(monkeypatch):
    from malecns_sim.application.workbench import DatasetCatalog
    def forbidden(*args, **kwargs):
        raise AssertionError("registered catalog accessed")
    monkeypatch.setattr(DatasetCatalog, "local", forbidden)
    monkeypatch.setattr(h, "CASES", [("S1", 128, 8, "E2")])
    evidence = h.run(warmups=0, repeats=2)
    assert all(x == 0 for x in evidence["accepted_registered_reads"].values())
    assert len(evidence["cases"][0]["raw"]) == 2
    assert evidence["cases"][0]["raw"][0]["on"]["queued"] > 0

def test_record_reset_and_deterministic_clock(monkeypatch):
    clock = iter((100, 110, 150, 160, 180, 200))
    monkeypatch.setattr(lif, "perf_counter_ns", lambda: next(clock))
    timing = lif.AdvanceTiming()
    timing.begin()
    timing.start()
    timing.stop("preparation")
    timing.start()
    timing.stop("output")
    timing.finish()
    assert timing.total_ns == 100
    assert timing.stages_ns["preparation"] == 40
    assert timing.stages_ns["output"] == 20
    assert timing.residual_ns == 40
    snapshot = timing.record()
    timing.stages_ns["output"] = 0
    assert snapshot["stages_ns"]["output"] == 20


def test_all_registered_categories_denied():
    import validation_firewall as f
    for name in ("connectome", "annotation", "neurotransmitter", "metadata", "mapping", "provenance", "other"):
        with pytest.raises(f.SourceAccessDenied):
            open(f.ROOT / "data" / (name + ".feather"), "rb")


def test_cli_requires_synthetic_and_accepts_no_source(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["a019f", "--output", "unused.json"])
    with pytest.raises(SystemExit):
        h.main()
    monkeypatch.setattr(sys, "argv", ["a019f", "--synthetic", "--output", "unused.json", "--source", "data"])
    with pytest.raises(SystemExit):
        h.main()

def test_signed_sparse_delivery_and_reused_record():
    from test_task005 import _projection
    from malecns_sim.dynamics.stimulus import ExplicitStimulus, SpikeSchedule
    runtime = lif.PreparedRuntime(_projection(((1, 2, 100), (2, 3, 100), (3, 1, 20))))
    stimulus = ExplicitStimulus((SpikeSchedule(1, (0, 6.9, 9.9, 19.9)),), weight_mV=30,
                                refractory_free_neuron_ids=(1,))
    off, on = runtime.initial_state(), runtime.initial_state()
    timing = lif.AdvanceTiming()
    for _ in range(2):
        a = lif.simulate_lif(runtime.projection, duration_ms=20, stimulus=stimulus,
                             _state=off, collect_sparse_trace=True, trace_neuron_ids=(1, 2, 3))
        timing.begin()
        b = lif.simulate_lif(runtime.projection, duration_ms=20, stimulus=stimulus,
                             _state=on, collect_sparse_trace=True, trace_neuron_ids=(1, 2, 3), _timing=timing)
        timing.finish()
        h.exact(a, b)
        h.exact(off, on)
        assert b.delivered_synaptic_event_count > 0
        assert timing.total_ns == sum(timing.stages_ns.values()) + timing.residual_ns
        # Reuse must erase all preceding observations.
        timing.stages_ns["output"] = 10**20
