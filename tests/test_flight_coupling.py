"""Synthetic-only verification of the engineered flight coupling boundary."""

from dataclasses import replace
import math

import numpy as np
import pytest

from malecns_sim.application.flight import FlightMapping, FlightParameters, FlightSession
from malecns_sim.application.flight_populations import native_flight_mapping
from malecns_sim.data.model import CuratedNeuronProjection, NumericNormalizedConnectome
from malecns_sim.data.neurotransmitter import NeurotransmitterEvidence, NeurotransmitterResolutionPolicy
from malecns_sim.dynamics.lif import EffectiveSignedProjection
from malecns_sim.graph.signed import SignedAnatomicalConnectome
from malecns_sim.runtime import prepare_runtime
from malecns_sim.sign import Shiu2024SignPolicy


class SyntheticBody:
    identity = {"model": "synthetic-test-body-not-fly-physics"}
    control_ms = 0.2

    def reset(self, seed):
        self.time = self.x = self.turn = 0.0
        self.calls = 0
        self.closed = False
        self.break_clock = False
        return self.observe()

    def observe(self):
        return {"time_ms": self.time, "position_cm": [self.x, 0.0, 1.0],
                "quaternion_wxyz": [math.cos(self.turn/2), 0.0, 0.0, math.sin(self.turn/2)],
                "expansion_left_rad_s": 10.0, "expansion_right_rad_s": 0.0, "terminal": False}

    def advance(self, action):
        self.calls += 1
        self.time += 0.3 if self.break_clock else self.control_ms
        self.x += action["frequency_fraction"]
        self.turn += action["left_wing_yaw_offset_rad"]
        return self.observe()

    def render(self):
        return {"left": [[[0, 0, 0] for _ in range(32)] for _ in range(32)],
                "right": [[[255, 255, 255] for _ in range(32)] for _ in range(32)]}

    def close(self):
        self.closed = True


@pytest.fixture
def session():
    ids = np.arange(1, 7, dtype=np.int64)
    graph = NumericNormalizedConnectome(ids, np.array([1, 1, 2, 2]),
        np.array([3, 5, 4, 6]), np.array([100, 100, 100, 100]))
    curated = CuratedNeuronProjection(graph, 4, 4, 4, 0)
    signed = SignedAnatomicalConnectome.from_projection(curated,
        [NeurotransmitterEvidence(neuron_id=int(i), consensus_nt="acetylcholine") for i in ids],
        NeurotransmitterResolutionPolicy(), Shiu2024SignPolicy())
    runtime = prepare_runtime(EffectiveSignedProjection.from_signed_connectome(signed))
    mapping = FlightMapping((1,), (2,), (3,), (4,), (5,), (6,), "0"*64, "synthetic-test-mapping")
    parameters = FlightParameters(maximum_steps=120, input_weight_mV=100,
        maximum_input_hz=10000, expansion_gain_hz_per_rad_s=1000)
    value = FlightSession(runtime, mapping, SyntheticBody(),
        expected_projection_fingerprint=runtime.projection_fingerprint, parameters=parameters)
    yield value
    value.close()


def command(session, name):
    return session.command({"command": name, "generation": session.generation, "revision": session.revision})


def test_actual_resumable_neural_output_drives_supplied_body(session):
    for _ in range(100):
        session.step()
    assert session.neural.time_ms == pytest.approx(20)
    assert session.body.calls == 100
    assert session.observation["position_cm"][0] > 0
    assert session.latest["neural"]["filtered_rates_hz"]["turn_left"] > 0
    assert session.latest["neural"]["filtered_rates_hz"]["turn_right"] == 0
    assert session.latest["action"]["left_wing_yaw_offset_rad"] > 0
    assert session.latest["action"]["right_wing_yaw_offset_rad"] < 0
    assert session.diagnostics["input_events"] > 0
    assert session.diagnostics["population_spikes"]["sensory_left"] > 0
    assert session.diagnostics["population_spikes"]["turn_left"] > 0
    assert session.diagnostics["neural_wall_ms"] > 0
    assert session.diagnostics["body_wall_ms"] > 0


def test_exact_replay_and_detached_evidence(session):
    for _ in range(40):
        session.step()
    first = session.export()
    snapshot = session.snapshot()
    snapshot["body"]["position_cm"][0] = 999
    assert session.observation["position_cm"][0] != 999
    session.reset()
    for _ in range(40):
        session.step()
    assert first == session.export()


def test_batched_playback_preserves_each_control_interval_and_episode_limit(session):
    for _ in range(20):
        session.step()
    expected = [e for e in session.export()["events"] if e["kind"] == "control_step"]
    expected_body = session.snapshot()["body"]
    session.reset()
    command(session, "run")
    command(session, "tick")
    actual = [e for e in session.export()["events"] if e["kind"] == "control_step"]
    assert actual == expected
    assert session.snapshot()["body"] == expected_body
    assert session.neural.time_ms == pytest.approx(4)
    for _ in range(5):
        command(session, "tick")
    assert session.steps == 120 and session.body.calls == 120
    assert not session.running
    command(session, "tick")
    assert session.body.calls == 120


def test_continuous_session_crosses_600ms_and_keeps_bounded_event_history(session):
    session = FlightSession(session.runtime, session.mapping, SyntheticBody(),
        expected_projection_fingerprint=session.runtime.projection_fingerprint,
        parameters=replace(session.parameters, maximum_steps=None))
    command(session, "run")
    for _ in range(501):
        command(session, "tick")
    assert session.steps == 10020
    assert session.neural.time_ms == pytest.approx(2004)
    assert session.observation["time_ms"] == pytest.approx(2004)
    assert session.running and not session.failed
    record = session.export()
    assert len(record["events"]) == 10000
    assert record["retention"]["dropped_events"] > 0
    assert record["retention"]["complete_history"] is False
    command(session, "pause")
    before = session.steps
    command(session, "tick")
    assert session.steps == before
    session.close()


def test_pause_tick_and_render_do_not_advance_either_clock(session):
    command(session, "tick")
    session.frame()
    assert session.neural.time_ms == 0
    assert session.body.calls == 0
    command(session, "run")
    with pytest.raises(ValueError, match="Pause"):
        command(session, "step")
    command(session, "tick")
    command(session, "pause")
    before = session.snapshot()
    command(session, "tick")
    assert session.snapshot() == before


def test_decoder_control_preserves_neural_activity_but_removes_residuals(session):
    for _ in range(60):
        session.step()
    intact_counts = session.latest["neural"]["readout_counts"]
    intact_identity = session.identity
    session.reset()
    session.set_condition("decoder_masked")
    assert session.identity != intact_identity
    for _ in range(60):
        session.step()
    assert session.latest["neural"]["readout_counts"] == intact_counts
    assert all(value == 0 for value in session.latest["action"].values())
    assert session.observation["position_cm"][0] == 0


def test_disconnected_sensory_has_no_injected_events(session):
    session.set_condition("sensory_disconnected")
    for _ in range(60):
        session.step()
    assert session.latest["sensory"]["realized_events"] == []
    assert all(value == 0 for value in session.latest["neural"]["readout_counts"].values())


def test_no_retry_after_body_clock_failure(session):
    session.body.break_clock = True
    with pytest.raises(ValueError, match="body clock"):
        session.step()
    assert session.failed and not session.running
    neural_time = session.neural.time_ms
    with pytest.raises(ValueError, match="Reset"):
        session.step()
    assert session.neural.time_ms == neural_time
    session.reset()
    session.step()
    assert not session.failed


def test_missing_ids_or_projection_identity_rejected_before_body_reset(session):
    calls = session.body.calls
    with pytest.raises(ValueError, match="lacks"):
        FlightSession(session.runtime, replace(session.mapping, sensory_left=(100,)), session.body,
            expected_projection_fingerprint=session.runtime.projection_fingerprint)
    with pytest.raises(ValueError, match="identity"):
        FlightSession(session.runtime, session.mapping, session.body,
            expected_projection_fingerprint="wrong")
    assert session.body.calls == calls


def test_stale_commands_bounds_and_condition_freeze(session):
    stale = {"command": "step", "generation": session.generation, "revision": session.revision}
    command(session, "step")
    with pytest.raises(ValueError, match="current"):
        session.command(stale)
    with pytest.raises(ValueError, match="before execution"):
        session.set_condition("fixed_actuator")
    for _ in range(session.parameters.maximum_steps-1):
        session.step()
    with pytest.raises(ValueError, match="ended"):
        session.step()
    with pytest.raises(ValueError, match="cannot run"):
        command(session, "run")


def test_native_populations_are_not_synthetic_fixture_ids():
    mapping = native_flight_mapping()
    assert len(mapping.sensory_left) == 71
    assert len(mapping.sensory_right) == 55
    assert len(mapping.power_left) == 15 and len(mapping.power_right) == 14
    assert mapping.turn_left == (10752,) and mapping.turn_right == (10989,)
    all_ids = tuple(i for name in ("sensory_left", "sensory_right", "power_left", "power_right", "turn_left", "turn_right")
                    for i in getattr(mapping, name))
    mapping.validate(all_ids)
    assert min(all_ids) > 6


def test_invalid_parameters_rejected():
    for parameters in (FlightParameters(control_ms=.15), FlightParameters(rate_filter_ms=0),
                       FlightParameters(seed=True), FlightParameters(maximum_input_hz=20000),
                       FlightParameters(input_weight_mV=float("nan"))):
        with pytest.raises(ValueError):
            parameters.validate(.1)


def test_protected_http_session_and_unconfigured_route(session):
    import json
    import threading
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen
    from malecns_sim.application.server import LocalServer

    server = LocalServer(0, flight_session=session)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"

    def request(path, body=None, authenticated=True):
        headers = {"Content-Type": "application/json", "Origin": origin}
        if authenticated:
            headers["X-Local-Session"] = server.token
        req = Request(origin+path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
        with urlopen(req, timeout=5) as response:
            return json.load(response)

    try:
        with pytest.raises(HTTPError) as rejected:
            request("/api/flight", authenticated=False)
        assert rejected.value.code == 403
        snap = request("/api/flight")
        assert snap["configured"] and snap["simulation_ms"] == 0
        frame = request("/api/flight/frame")
        assert len(frame["eyes"]["left"]) == 32
        assert session.neural.time_ms == 0
        next_state = request("/api/flight", {"command": "step", "generation": snap["generation"], "revision": snap["revision"]})
        assert next_state["simulation_ms"] == .2
        assert len(request("/api/flight/events")["events"]) == 2
        with urlopen(origin+"/flight", timeout=5) as response:
            assert b"Physical body state" in response.read()
        server.flight = None
        assert request("/api/flight")["configured"] is False
        with pytest.raises(HTTPError) as missing:
            request("/api/flight", {"command": "step"})
        assert missing.value.code == 409
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
