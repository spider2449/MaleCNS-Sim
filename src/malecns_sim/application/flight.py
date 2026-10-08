"""Engineered post-retinal neural/body coupling; no dataset loading or autopilot.

Neural activity is computed by the public resumable runtime. The supplied body
owns physics and vision; neither rendering nor user controls integrate a pose.
Decoder gains are engineering hypotheses, not inferred biological parameters.
"""

from dataclasses import asdict, dataclass
from collections import deque
import copy
import hashlib
import json
import math
import random
import threading
import time
from typing import Protocol

from malecns_sim.runtime import PreparedRuntime
from malecns_sim.dynamics.stimulus import ExplicitStimulus, SpikeSchedule


@dataclass(frozen=True, slots=True)
class FlightMapping:
    sensory_left: tuple[int, ...]
    sensory_right: tuple[int, ...]
    power_left: tuple[int, ...]
    power_right: tuple[int, ...]
    turn_left: tuple[int, ...]
    turn_right: tuple[int, ...]
    annotation_sha256: str
    kind: str = "male-cns-lc4-dng02-dnp03-engineered-v1"

    def validate(self, known_ids):
        populations = [getattr(self, name) for name in (
            "sensory_left", "sensory_right", "power_left", "power_right", "turn_left", "turn_right")]
        combined = []
        for population in populations:
            if (type(population) is not tuple or not population
                    or any(type(value) is not int for value in population)
                    or tuple(sorted(set(population))) != population):
                raise ValueError("nonempty sorted unique integer populations required")
            combined.extend(population)
        if len(set(combined)) != len(combined):
            raise ValueError("flight populations must be disjoint")
        missing = set(combined) - set(known_ids)
        if missing:
            raise ValueError(f"prepared network lacks {len(missing)} mapped neurons")
        if (type(self.annotation_sha256) is not str or len(self.annotation_sha256) != 64
                or any(c not in "0123456789abcdef" for c in self.annotation_sha256)):
            raise ValueError("annotation SHA-256 required")


@dataclass(frozen=True, slots=True)
class FlightParameters:
    control_ms: float = 0.2
    maximum_steps: int | None = None
    playback_steps: int = 20
    seed: int = 0
    input_weight_mV: float = 1.0
    baseline_hz: float = 0.0
    expansion_gain_hz_per_rad_s: float = 50.0
    maximum_input_hz: float = 200.0
    rate_filter_ms: float = 20.0
    turn_gain_rad_per_hz: float = 0.001
    maximum_wing_offset_rad: float = 0.15
    power_gain_per_hz: float = 0.001
    maximum_frequency_fraction: float = 0.05

    def validate(self, neural_dt):
        for name, value in asdict(self).items():
            if name == "maximum_steps" and value is None:
                continue
            if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
                raise ValueError(f"invalid flight parameter {name}")
        if self.control_ms <= 0 or self.rate_filter_ms <= 0 or self.input_weight_mV <= 0:
            raise ValueError("positive neural/body intervals and input weight required")
        if self.maximum_steps is not None and (type(self.maximum_steps) is not int or self.maximum_steps < 1):
            raise ValueError("maximum_steps must be None or a positive integer")
        if type(self.playback_steps) is not int or not 1 <= self.playback_steps <= 20:
            raise ValueError("playback_steps must be an integer in [1, 20]")
        if type(self.seed) is not int or not 0 <= self.seed < 2**32:
            raise ValueError("uint32 seed required")
        ratio = self.control_ms / neural_dt
        if not math.isclose(ratio, round(ratio), rel_tol=0, abs_tol=1e-10) or ratio < 1:
            raise ValueError("control interval must align with the neural grid")
        if self.maximum_input_hz * neural_dt / 1000 > 1 or self.baseline_hz > self.maximum_input_hz:
            raise ValueError("input rate exceeds Bernoulli-grid bounds")


class FlightBody(Protocol):
    """Physics-owned poses and geometry-derived expansion, in explicit units."""

    identity: dict
    control_ms: float

    def reset(self, seed: int) -> dict: ...
    def advance(self, action: dict) -> dict: ...
    def render(self) -> dict: ...
    def close(self) -> None: ...


def validate_body_observation(value, expected_ms):
    if (type(value) is not dict or type(value.get("time_ms")) not in (float, int)
            or not math.isclose(value["time_ms"], expected_ms, abs_tol=1e-7)):
        raise ValueError("body clock differs from the coupled neural clock")
    for name, length in (("position_cm", 3), ("quaternion_wxyz", 4)):
        vector = value.get(name)
        if (type(vector) not in (list, tuple) or len(vector) != length
                or any(type(v) not in (float, int) or not math.isfinite(v) for v in vector)):
            raise ValueError(f"invalid body {name}")
    if not math.isclose(sum(v*v for v in value["quaternion_wxyz"]), 1, abs_tol=1e-5):
        raise ValueError("body orientation must be a unit quaternion")
    for name in ("expansion_left_rad_s", "expansion_right_rad_s"):
        expansion = value.get(name)
        if type(expansion) not in (float, int) or not math.isfinite(expansion) or expansion < 0:
            raise ValueError("nonnegative finite geometry expansion required")
    if type(value.get("terminal")) is not bool:
        raise ValueError("body termination flag required")
    return copy.deepcopy(value)


class FlightSession:
    """Serialized bounded coupling owner. Construction never prepares a graph."""

    def __init__(self, runtime: PreparedRuntime, mapping: FlightMapping, body: FlightBody,
                 *, expected_projection_fingerprint: str, parameters=FlightParameters()):
        if not isinstance(runtime, PreparedRuntime):
            raise TypeError("an already prepared public CPU runtime is required")
        if runtime.projection_fingerprint != expected_projection_fingerprint:
            raise ValueError("prepared projection identity mismatch")
        mapping.validate(runtime.neuron_ids)
        parameters.validate(runtime.dt_ms)
        if not math.isclose(body.control_ms, parameters.control_ms, abs_tol=1e-12):
            raise ValueError("body and neural control intervals differ")
        body_identity = json.loads(json.dumps(body.identity, allow_nan=False))
        self.runtime, self.mapping, self.body, self.parameters = runtime, mapping, body, parameters
        self.lock = threading.RLock()
        self.spec = {"schema": "engineered-flight-coupling-v1",
                     "projection_fingerprint": runtime.projection_fingerprint,
                     "parameter_fingerprint": runtime.parameter_fingerprint,
                     "neural_dt_ms": runtime.dt_ms, "mapping": asdict(mapping),
                     "body": body_identity, "coupling": asdict(parameters),
                     "sensory_boundary": "geometry-derived expansion injected into bilateral LC4; phototransduction, retinotopy and upstream motion computation bypassed",
                     "motor_boundary": "engineered DNg02 frequency and DNp03 differential wing offsets; no calibrated biological decoder",
                     "initial_condition": "fresh resting neural state; explicit body seed; no inferred flight-state drive"}
        self.identity = hashlib.sha256(json.dumps(self.spec, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        self.generation = self.revision = 0
        self.reset()

    def reset(self):
        with self.lock:
            self.running = False
            self.failed = True
            try:
                observation = validate_body_observation(self.body.reset(self.parameters.seed), 0)
                neural = self.runtime.initial_state()
            except Exception as exc:
                self.failure = str(exc)
                self.revision += 1
                raise
            self.neural = neural
            self.observation = observation
            self.random = random.Random(self.parameters.seed)
            self.filtered = {name: 0.0 for name in ("power_left", "power_right", "turn_left", "turn_right")}
            self.steps = 0
            self.latest = None
            self.diagnostics = {"input_events": 0, "all_network_spikes": 0,
                "population_spikes": {name: 0 for name in ("sensory_left", "sensory_right", "power_left", "power_right", "turn_left", "turn_right")},
                "neural_wall_ms": 0.0, "body_wall_ms": 0.0}
            self.failure = None
            self.events = deque([{"kind": "reset", "simulation_ms": 0.0}], maxlen=10000)
            self.dropped_events = 0
            self.condition = "intact"
            self.spec["condition"] = self.condition
            self._identify()
            self.failed = False
            self.generation += 1
            self.revision += 1

    def _identify(self):
        self.identity = hashlib.sha256(json.dumps(self.spec, sort_keys=True,
            separators=(",", ":"), allow_nan=False).encode()).hexdigest()

    def _record(self, event):
        if len(self.events) == self.events.maxlen:
            self.dropped_events += 1
        self.events.append(event)

    def _limit_reached(self):
        limit = self.parameters.maximum_steps
        return limit is not None and self.steps >= limit

    def _stimulus(self):
        p = self.parameters
        rates = [min(p.maximum_input_hz, p.baseline_hz + p.expansion_gain_hz_per_rad_s *
                     self.observation[f"expansion_{side}_rad_s"]) for side in ("left", "right")]
        schedules = []
        steps = round(p.control_ms / self.runtime.dt_ms)
        for population, rate in zip((self.mapping.sensory_left, self.mapping.sensory_right), rates):
            for neuron in population:
                times = tuple(step*self.runtime.dt_ms for step in range(steps)
                              if self.random.random() < rate*self.runtime.dt_ms/1000)
                if self.condition != "sensory_disconnected" and times:
                    schedules.append(SpikeSchedule(neuron, times))
        sensory = {"rates_hz": rates, "condition": self.condition,
                   "realized_events": [[schedule.neuron_id, list(schedule.spike_times_ms)] for schedule in schedules],
                   "input_weight_mV": p.input_weight_mV}
        return sensory, ExplicitStimulus(tuple(schedules), weight_mV=p.input_weight_mV)

    def _decode(self, result):
        p = self.parameters
        counts = {}
        for neuron in result.spike_neuron_ids:
            counts[neuron] = counts.get(neuron, 0) + 1
        alpha = -math.expm1(-p.control_ms / p.rate_filter_ms)
        raw = {}
        for name in self.filtered:
            population = getattr(self.mapping, name)
            raw[name] = sum(counts.get(neuron, 0) for neuron in population) * 1000 / (p.control_ms * len(population))
            self.filtered[name] += alpha * (raw[name] - self.filtered[name])
        turn = max(-p.maximum_wing_offset_rad, min(p.maximum_wing_offset_rad,
            p.turn_gain_rad_per_hz * (self.filtered["turn_left"] - self.filtered["turn_right"])))
        power = min(p.maximum_frequency_fraction, p.power_gain_per_hz *
                    (self.filtered["power_left"] + self.filtered["power_right"])/2)
        action = {"left_wing_yaw_offset_rad": turn, "right_wing_yaw_offset_rad": -turn,
                  "frequency_fraction": power}
        if self.condition in ("decoder_masked", "fixed_actuator"):
            action = {key: 0.0 for key in action}
        return {"population_rates_hz": raw, "filtered_rates_hz": dict(self.filtered),
                "sensory_spikes": {name: sum(counts.get(neuron, 0) for neuron in getattr(self.mapping, name))
                                   for name in ("sensory_left", "sensory_right")},
                "all_network_spikes": result.emitted_spike_count,
                "readout_counts": {str(neuron): counts.get(neuron, 0) for name in self.filtered
                                   for neuron in getattr(self.mapping, name)}}, action

    def step(self):
        with self.lock:
            if self.failed:
                raise ValueError("coupled state failed; explicit Reset required")
            if self._limit_reached() or self.observation["terminal"]:
                self.running = False
                raise ValueError("bounded flight episode has ended")
            try:
                before = copy.deepcopy(self.observation)
                sensory, stimulus = self._stimulus()
                neural_start = time.perf_counter()
                result = self.runtime.advance(self.neural, duration_ms=self.parameters.control_ms, stimulus=stimulus)
                neural_ms = (time.perf_counter()-neural_start)*1000
                if not math.isclose(result.end_time_ms, (self.steps+1)*self.parameters.control_ms, abs_tol=1e-7):
                    raise ValueError("neural clock mismatch")
                evidence, action = self._decode(result)
                body_start = time.perf_counter()
                observation = validate_body_observation(self.body.advance(action), result.end_time_ms)
                self.diagnostics["body_wall_ms"] += (time.perf_counter()-body_start)*1000
                self.diagnostics["neural_wall_ms"] += neural_ms
                self.diagnostics["input_events"] += sum(len(schedule.spike_times_ms) for schedule in stimulus.schedules)
                self.diagnostics["all_network_spikes"] += result.emitted_spike_count
                counts = {}
                for neuron in result.spike_neuron_ids:
                    counts[neuron] = counts.get(neuron, 0)+1
                for name in self.diagnostics["population_spikes"]:
                    self.diagnostics["population_spikes"][name] += sum(counts.get(neuron, 0) for neuron in getattr(self.mapping, name))
                self.observation = observation
                self.steps += 1
                self.latest = {"before": before, "sensory": sensory, "neural": evidence,
                               "start_timestep": result.start_timestep, "end_timestep": result.end_timestep,
                               "action": action, "after": copy.deepcopy(observation)}
                self._record({"kind": "control_step", "simulation_ms": result.end_time_ms,
                                    "evidence": copy.deepcopy(self.latest)})
                if self._limit_reached() or observation["terminal"]:
                    self.running = False
            except Exception as exc:
                self.failed, self.running = True, False
                self.failure = str(exc)
                self._record({"kind": "failed", "simulation_ms": self.steps*self.parameters.control_ms,
                                    "message": self.failure, "rollback": False})
                raise
            finally:
                self.revision += 1

    def command(self, request):
        with self.lock:
            if (type(request) is not dict or set(request) != {"command", "generation", "revision"}
                    or type(request["generation"]) is not int or type(request["revision"]) is not int
                    or request["generation"] != self.generation or request["revision"] != self.revision):
                raise ValueError("exact current generation/revision and command required")
            command = request["command"]
            if command == "reset":
                self.reset()
            elif command == "pause":
                self.running = False
                self._record({"kind": "pause", "simulation_ms": self.steps*self.parameters.control_ms})
                self.revision += 1
            elif command == "run":
                if self.failed or self.observation["terminal"] or self._limit_reached():
                    raise ValueError("flight episode cannot run")
                self.running = True
                self._record({"kind": "run", "simulation_ms": self.steps*self.parameters.control_ms})
                self.revision += 1
            elif command in ("step", "tick"):
                if command == "step" and self.running:
                    raise ValueError("Pause before manual Step")
                if command == "step":
                    self.step()
                elif self.running:
                    for _ in range(self.parameters.playback_steps):
                        self.step()
                        if not self.running:
                            break
            else:
                raise ValueError("unsupported flight command")
            return self.snapshot()

    def set_condition(self, condition):
        """Freeze a control condition before any interval; no mid-run tuning."""
        with self.lock:
            if self.steps or self.running or condition not in (
                    "intact", "sensory_disconnected", "decoder_masked", "fixed_actuator"):
                raise ValueError("select an allowlisted condition before execution")
            self.condition = condition
            self.spec["condition"] = condition
            self._identify()
            self._record({"kind": "condition", "simulation_ms": 0.0, "condition": condition})
            self.revision += 1

    def snapshot(self):
        with self.lock:
            return copy.deepcopy({"configured": True, "session_identity": self.identity,
                "spec": self.spec, "generation": self.generation, "revision": self.revision,
                "running": self.running, "failed": self.failed, "failure": self.failure,
                "simulation_ms": self.steps*self.parameters.control_ms,
                "body": self.observation, "latest": self.latest, "condition": self.condition,
                "diagnostics": self.diagnostics})

    def export(self):
        with self.lock:
            return copy.deepcopy({"session_identity": self.identity, "spec": self.spec, "events": list(self.events),
                "retention": {"maximum_events": self.events.maxlen, "dropped_events": self.dropped_events,
                              "complete_history": self.dropped_events == 0}})

    def close(self):
        with self.lock:
            self.running = False
            self.body.close()

    def frame(self):
        """Render only the current physics state; no neural or body advance."""
        with self.lock:
            start = time.perf_counter()
            frame = getattr(self.body, "render_encoded", self.body.render)()
            return {"session_identity": self.identity, "generation": self.generation,
                    "revision": self.revision, "simulation_ms": self.steps*self.parameters.control_ms,
                    "eyes": frame, "render_wall_ms": (time.perf_counter()-start)*1000}
