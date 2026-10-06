"""Guarded synthetic scheduling dependency and exact-replay checks."""
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest
import validation_firewall as guard

assert guard.ACTIVE
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import diagnose_application_a019n as diagnostic


def test_dependencies_boundaries_and_exact_replay():
    evidence = diagnostic.run()
    rows = evidence["probes"]
    assert rows[0]["intermediates"] == rows[1]["intermediates"] == rows[2]["intermediates"]
    assert rows[0]["result"] == rows[1]["result"] == rows[2]["result"]
    assert rows[3]["grid_calls"] == 4
    assert rows[4]["intermediates"] != rows[0]["intermediates"]
    assert rows[5]["intermediates"][1]["step"] == 25
    assert rows[6]["result"][0] == "ValueError"
    assert evidence["boundary_outcome_pairs"] == 55
    assert all(row["exact"] for row in evidence["replay"])
    assert any(row["pending_events"] for row in evidence["replay"])
    assert not any(evidence["accepted_registered_reads"].values())


def test_firewall_before_registered_content():
    for name in ("mapping", "provenance", "neurotransmitter", "annotation",
                 "connectome", "neuron_metadata", "other"):
        with pytest.raises(guard.SourceAccessDenied):
            guard.check(guard.ROOT / "data" / (name + ".feather"))


def test_admission_and_selection_invalidation():
    runtime, _, _ = diagnostic.graph.synthetic_case(128, 8, "E0")
    invalid = replace(runtime, dt_ms=0.0)
    with pytest.raises(ValueError, match="positive"):
        invalid.initial_state()
    with pytest.raises(FrozenInstanceError):
        runtime.dt_ms = 0.2
    unknown = diagnostic.source.ExplicitStimulus(
        (diagnostic.source.SpikeSchedule(999, (0.,)),))
    assert diagnostic.outcome(unknown, .1, 200, False) == diagnostic.outcome(unknown, .1, 200, True)
    assert diagnostic.outcome(unknown, .1, 200, False)[0] == "KeyError"
