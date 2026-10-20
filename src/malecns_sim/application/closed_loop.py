"""Generic closed loop between a prepared public runtime and any step-wise environment.

One iteration is: encode the current observation into direct input spikes, advance
the neural state by a fixed amount of simulated neural time, decode the emitted
spikes into an environment command, and step the environment once. The environment
keeps its own clock; ``neural_ms_per_step`` is the explicit amount of neural time
spent per decision, not a claim about game time.

Encoders and decoders are engineering hypotheses. Nothing here is a validated
sensory transduction or motor interpretation, and the connectome has no plasticity,
so no learning takes place.
"""

from dataclasses import dataclass, field
import math
import random
import time
from typing import Any, Callable, Mapping, Protocol, Sequence

from malecns_sim.dynamics.stimulus import ExplicitStimulus, SpikeSchedule
from malecns_sim.runtime import PreparedRuntime


@dataclass(frozen=True, slots=True)
class StepResult:
    """Outcome of one environment step."""

    observation: Any
    reward: float = 0.0
    done: bool = False
    info: Mapping[str, Any] = field(default_factory=dict)


class Environment(Protocol):
    def reset(self, seed: int) -> Any:
        """Start an episode and return the first observation."""

    def step(self, command: Any) -> StepResult:
        """Apply one decoded command and return the result."""

    def close(self) -> None: ...


class SensoryEncoder(Protocol):
    def encode(self, observation: Any, *, steps: int, dt_ms: float, rng: random.Random) -> ExplicitStimulus:
        """Return chunk-relative direct input spikes for ``steps`` neural time steps."""


class MotorDecoder(Protocol):
    def decode(self, spike_counts: Mapping[int, int], duration_ms: float) -> tuple[Any, Mapping[str, Any]]:
        """Return ``(command, evidence)`` from per-neuron spike counts in the chunk."""


class GroupRateEncoder:
    """Independent Bernoulli spike trains per neuron at a rate chosen per named group.

    ``rates_hz(observation)`` maps group name to a rate in Hz. Rates are clipped to
    ``[0, maximum_hz]``. Spikes fall on the neural grid, so they are exact for any dt.
    """

    def __init__(self, groups: Mapping[str, Sequence[int]], rates_hz: Callable[[Any], Mapping[str, float]],
                 *, weight_mV: float, maximum_hz: float = 200.0):
        if not groups or any(not ids for ids in groups.values()):
            raise ValueError("nonempty neuron groups required")
        for value, name in ((weight_mV, "weight_mV"), (maximum_hz, "maximum_hz")):
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a positive finite number")
        self.groups = {name: tuple(int(i) for i in ids) for name, ids in groups.items()}
        self.rates_hz, self.weight_mV, self.maximum_hz = rates_hz, float(weight_mV), float(maximum_hz)

    @property
    def neuron_ids(self):
        return tuple(i for ids in self.groups.values() for i in ids)

    def encode(self, observation, *, steps, dt_ms, rng):
        schedules = []
        for name, rate in self.rates_hz(observation).items():
            if name not in self.groups:
                raise KeyError(f"unknown input group {name!r}")
            if not math.isfinite(rate):
                raise ValueError("input rates must be finite")
            probability = min(self.maximum_hz, max(0.0, rate)) * dt_ms / 1000
            for neuron in self.groups[name]:
                times = tuple(step * dt_ms for step in range(steps) if rng.random() < probability)
                if times:
                    schedules.append(SpikeSchedule(neuron, times))
        return ExplicitStimulus(tuple(schedules), weight_mV=self.weight_mV)


class GroupRateDecoder:
    """Mean per-neuron firing rate (Hz) of named groups, mapped to a command by ``command``."""

    def __init__(self, groups: Mapping[str, Sequence[int]], command: Callable[[Mapping[str, float]], Any]):
        if not groups or any(not ids for ids in groups.values()):
            raise ValueError("nonempty neuron groups required")
        self.groups = {name: tuple(int(i) for i in ids) for name, ids in groups.items()}
        self.command = command

    @property
    def neuron_ids(self):
        return tuple(i for ids in self.groups.values() for i in ids)

    def decode(self, spike_counts, duration_ms):
        spikes = {name: sum(spike_counts.get(i, 0) for i in ids) for name, ids in self.groups.items()}
        rates = {name: spikes[name] * 1000 / (duration_ms * len(ids)) for name, ids in self.groups.items()}
        return self.command(rates), {"rates_hz": rates, "spikes": spikes}


@dataclass(frozen=True, slots=True)
class ClosedLoopParameters:
    neural_ms_per_step: float = 10.0
    seed: int = 0
    maximum_steps: int | None = None

    def validate(self, dt_ms):
        if (type(self.neural_ms_per_step) not in (int, float) or not math.isfinite(self.neural_ms_per_step)
                or self.neural_ms_per_step <= 0):
            raise ValueError("neural_ms_per_step must be a positive finite number")
        steps = self.neural_ms_per_step / dt_ms
        if abs(steps - round(steps)) > 1e-9 or round(steps) < 1:
            raise ValueError("neural_ms_per_step must be a whole number of neural time steps")
        if type(self.seed) is not int:
            raise ValueError("integer seed required")
        if self.maximum_steps is not None and (type(self.maximum_steps) is not int or self.maximum_steps < 1):
            raise ValueError("maximum_steps must be a positive integer or None")


@dataclass(frozen=True, slots=True)
class StepRecord:
    step: int
    neural_time_ms: float
    observation: Any  # what the encoder saw for this step, before the command was applied
    command: Any
    reward: float
    done: bool
    info: Mapping[str, Any]
    evidence: Mapping[str, Any]
    input_events: int
    network_spikes: int
    spikes: tuple[tuple[int, float], ...]  # (neuron_id, absolute neural time ms) of watched neurons only
    neural_wall_ms: float
    environment_wall_ms: float


class ClosedLoop:
    """Serialized owner of one environment, one neural state and the encode/decode seam."""

    def __init__(self, runtime: PreparedRuntime, environment: Environment, encoder: SensoryEncoder,
                 decoder: MotorDecoder, *, expected_projection_fingerprint: str,
                 parameters: ClosedLoopParameters = ClosedLoopParameters(),
                 watch: Sequence[int] | None = None):
        if not isinstance(runtime, PreparedRuntime):
            raise TypeError("an already prepared public runtime is required")
        if runtime.projection_fingerprint != expected_projection_fingerprint:
            raise ValueError("prepared projection identity mismatch")
        parameters.validate(runtime.dt_ms)
        known = set(runtime.neuron_ids)
        for component in (encoder, decoder):
            missing = set(getattr(component, "neuron_ids", ())) - known
            if missing:
                raise ValueError(f"prepared network lacks {len(missing)} neurons used by the encoder/decoder")
        watched = set(getattr(encoder, "neuron_ids", ())) | set(getattr(decoder, "neuron_ids", ()))             if watch is None else {int(i) for i in watch}
        if watched - known:
            raise ValueError(f"prepared network lacks {len(watched - known)} watched neurons")
        self.watch = frozenset(watched)
        self.runtime, self.environment, self.encoder, self.decoder = runtime, environment, encoder, decoder
        self.parameters = parameters
        self.steps_per_decision = round(parameters.neural_ms_per_step / runtime.dt_ms)
        self.failed = True
        self.reset()

    def reset(self, seed: int | None = None):
        """Start a fresh episode with a fresh resting neural state; ``seed`` defaults to the parameter."""
        seed = self.parameters.seed if seed is None else seed
        if type(seed) is not int:
            raise ValueError("integer seed required")
        self.failed = True
        observation = self.environment.reset(seed)
        self.neural = self.runtime.initial_state()
        self.random = random.Random(seed)
        self.observation, self.step_count, self.done = observation, 0, False
        self.records: list[StepRecord] = []
        self.failed = False

    def step(self) -> StepRecord:
        if self.failed:
            raise ValueError("closed loop failed; explicit reset required")
        if self.done or (self.parameters.maximum_steps is not None
                         and self.step_count >= self.parameters.maximum_steps):
            raise ValueError("episode has ended")
        duration = self.parameters.neural_ms_per_step
        try:
            stimulus = self.encoder.encode(self.observation, steps=self.steps_per_decision,
                                           dt_ms=self.runtime.dt_ms, rng=self.random)
            started = time.perf_counter()
            result = self.runtime.advance(self.neural, duration_ms=duration, stimulus=stimulus)
            neural_ms = (time.perf_counter() - started) * 1000
            counts: dict[int, int] = {}
            for neuron in result.spike_neuron_ids:
                counts[neuron] = counts.get(neuron, 0) + 1
            command, evidence = self.decoder.decode(counts, duration)
            started = time.perf_counter()
            outcome = self.environment.step(command)
            environment_ms = (time.perf_counter() - started) * 1000
        except Exception:
            self.failed = True
            raise
        self.step_count += 1
        seen, self.observation, self.done = self.observation, outcome.observation, bool(outcome.done)
        record = StepRecord(
            step=self.step_count, neural_time_ms=result.end_time_ms, observation=seen, command=command,
            reward=float(outcome.reward), done=self.done, info=dict(outcome.info), evidence=dict(evidence),
            input_events=sum(len(s.spike_times_ms) for s in stimulus.schedules),
            network_spikes=result.emitted_spike_count,
            spikes=tuple((n, t) for n, t in zip(result.spike_neuron_ids, result.spike_times_ms) if n in self.watch),
            neural_wall_ms=neural_ms, environment_wall_ms=environment_ms)
        self.records.append(record)
        return record

    def run(self, maximum_steps: int | None = None, on_step: Callable[[StepRecord], None] | None = None):
        """Step until the episode ends or ``maximum_steps`` more steps ran; return the new records."""
        produced = []
        while not self.done and (maximum_steps is None or len(produced) < maximum_steps):
            if (self.parameters.maximum_steps is not None
                    and self.step_count >= self.parameters.maximum_steps):
                break
            record = self.step()
            produced.append(record)
            if on_step is not None:
                on_step(record)
        return produced

    def close(self):
        self.environment.close()
