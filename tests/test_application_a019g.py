"""Controlled matrix and exclusive substage certification."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import benchmark_application_a019g as h
from malecns_sim.dynamics import lif


def test_controlled_matrix_exact_replay_and_determinism():
    graphs, events = [], []
    for name, n, degree, count in h.CASES:
        runtime, stimulus, event_count = h.synthetic_case(n, degree, count)
        duplicate, repeated, repeated_count = h.synthetic_case(n, degree, count)
        assert runtime.identity == duplicate.identity
        assert stimulus.fingerprint == repeated.fingerprint
        assert event_count == repeated_count == count * 5
        batches = lif.schedule_events(stimulus, neuron_positions=runtime.projection.neuron_ids,
                                      duration_steps=200, dt_ms=0.1)
        assert sum(positions.size for positions, _ in batches.values()) == event_count
        assert h.base.equivalence(runtime, stimulus)
        if name.startswith("G"):
            events.append(event_count)
        else:
            graphs.append(runtime.identity)
    assert events == [60, 60, 60]
    assert len(set(graphs)) == 1


def test_substage_schema_reconciliation_and_reset():
    runtime, stimulus, _ = h.synthetic_case(128, 8, 12)
    timing = lif.AdvanceTiming()
    for _ in range(2):
        runtime.advance(runtime.initial_state(), duration_ms=20, stimulus=stimulus, timing=timing)
        record = timing.record()
        for parent, names in lif.ADVANCE_SUBSTAGES.items():
            assert tuple(record["substages_ns"][parent]) == names
            assert all(value >= 0 for value in record["substages_ns"][parent].values())
            assert record["substage_residual_ns"][parent] >= 0
            assert sum(record["substages_ns"][parent].values()) + record["substage_residual_ns"][parent] == record["stages_ns"][parent]
        timing.substages_ns["linear_update"]["membrane"] = 10**20


def test_runner_fail_closed_and_no_catalog(monkeypatch):
    import validation_firewall as firewall
    from malecns_sim.application.workbench import DatasetCatalog
    def forbidden(*args, **kwargs):
        raise AssertionError("registered catalog accessed")
    monkeypatch.setattr(DatasetCatalog, "local", forbidden)
    monkeypatch.setattr(h, "CASES", [("G1", 128, 8, 12)])
    evidence = h.run(0, 2)
    assert all(value == 0 for value in evidence["counters"].values())
    assert all(value == 0 for value in evidence["accepted_registered_reads"].values())
    monkeypatch.setattr(firewall, "ACTIVE", False)
    with pytest.raises(RuntimeError, match="firewall required"):
        h.run(0, 1)
    with pytest.raises(ValueError, match="bounded synthetic"):
        h.synthetic_case(1000000, 8, 12)


def test_cli_synthetic_only(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["a019g", "--output", "unused.json"])
    with pytest.raises(SystemExit):
        h.main()
    monkeypatch.setattr(sys, "argv", ["a019g", "--synthetic", "--output", "unused.json", "--source", "data"])
    with pytest.raises(SystemExit):
        h.main()
