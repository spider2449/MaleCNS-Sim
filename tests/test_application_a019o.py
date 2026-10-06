"""Synthetic dt lifecycle, error timing and instrumentation contract checks."""
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest
import validation_firewall as guard

assert guard.ACTIVE
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import diagnose_application_a019o as diagnostic


def test_invalid_dt_lifecycle_and_failure_before_state_mutation():
    rows = {row["label"]: row for row in diagnostic.invalid_probes()}
    for label in ("zero", "negative", "nan", "inf", "negative_inf", "bool"):
        row = rows[label]
        assert row["runtime_constructed"]
        assert row["schedule_0"] == dict(outcome="ok", empty=True)
        expected = "TypeError" if label == "bool" else "ValueError"
        assert row["initial_state"]["outcome"] == expected
        assert row["schedule_1"]["outcome"] == expected
        assert row["all_state_fields_unchanged_on_failure"]
    assert rows["zero"]["initial_state"]["message"] == "dt_ms must be positive"
    assert rows["nan"]["initial_state"]["message"] == "dt_ms must be finite"
    assert rows["float"]["simulate"]["outcome"] == "ok"
    assert rows["np_float64"]["simulate"]["outcome"] == "ok"
    assert rows["numeric_string"]["initial_state"]["outcome"] == "ok"
    assert rows["numeric_string"]["simulate"]["outcome"] == "TypeError"


def test_frozen_runtime_is_not_normalized_admission():
    runtime, _, _ = diagnostic.prior.graph.synthetic_case(128, 8, "E0")
    candidate = replace(runtime, dt_ms="0.1")
    assert candidate.dt_ms == "0.1"
    candidate.initial_state()
    with pytest.raises(FrozenInstanceError):
        candidate.dt_ms = .2
    scalar = .1
    assert float(scalar) is scalar
    assert type(diagnostic.np.isfinite(scalar)) is diagnostic.np.bool_


def test_float_subclass_conversion_is_observable_and_mutable():
    class ChangingFloat(float):
        def __new__(cls):
            value = super().__new__(cls, .1)
            value.calls = 0
            return value

        def __float__(self):
            self.calls += 1
            return .1 if self.calls == 1 else .2

    dt = ChangingFloat()
    runtime, _, _ = diagnostic.prior.graph.synthetic_case(128, 8, "E0")
    candidate = replace(runtime, dt_ms=dt)
    payload = diagnostic.source.ExplicitStimulus((diagnostic.source.SpikeSchedule(1, (0., 5.)),))
    result = diagnostic.source.schedule_events(payload, neuron_positions=runtime.projection.neuron_ids,
                                              duration_steps=200, dt_ms=candidate.dt_ms)
    assert list(result) == [0, 25]
    assert candidate.dt_ms.calls == 2
    candidate.dt_ms.calls = 0
    assert float(candidate.dt_ms) == .1


def test_instrumentation_preserves_exact_grid_outcomes():
    samples = []
    instrumented = diagnostic.observed_grid(samples)
    for dt in (.1, .2, 0., -.1, float("nan"), float("inf"), True):
        for value in (0., 5., 19.9, 20., 5. - 2e-10, 5. + 2e-10,
                      diagnostic.np.nextafter(5., -diagnostic.np.inf),
                      diagnostic.np.nextafter(5., diagnostic.np.inf)):
            def outcome(function):
                try:
                    return ("ok", function(value, dt, "spike time"))
                except (TypeError, ValueError) as error:
                    return (type(error).__name__, str(error))
            assert outcome(instrumented) == outcome(diagnostic.source._grid_steps)
    assert samples and min(samples) >= 0


def test_seven_registered_categories_fail_closed():
    for name in ("mapping", "provenance", "neurotransmitter", "annotation",
                 "connectome", "neuron_metadata", "other"):
        with pytest.raises(guard.SourceAccessDenied):
            guard.check(guard.ROOT / "data" / (name + ".feather"))
