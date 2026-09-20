"""Explicit and seeded stochastic input schedules for the reference engine."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable

import numpy as np


def _number(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True, slots=True)
class SpikeSchedule:
    """Input events for one neuron, sorted deterministically at construction.

    Duplicate times are retained: each occurrence is an independent direct
    voltage impulse, so duplicate events add their configured input weight.
    Grid alignment is checked by the simulator because it depends on ``dt``.
    """

    neuron_id: int
    spike_times_ms: tuple[float, ...]

    def __post_init__(self) -> None:
        if isinstance(self.neuron_id, bool):
            raise TypeError("neuron_id must be an integer")
        object.__setattr__(self, "neuron_id", int(self.neuron_id))
        times = tuple(_number(value, "spike time") for value in self.spike_times_ms)
        if any(value < 0.0 for value in times):
            raise ValueError("spike times must be non-negative")
        object.__setattr__(self, "spike_times_ms", tuple(sorted(times)))


@dataclass(frozen=True, slots=True)
class ExplicitStimulus:
    """Deterministic direct voltage impulses applied to selected neurons."""

    schedules: tuple[SpikeSchedule, ...] = ()
    weight_mV: float | None = None
    refractory_free_neuron_ids: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        schedules = tuple(self.schedules)
        if any(not isinstance(item, SpikeSchedule) for item in schedules):
            raise TypeError("schedules must contain SpikeSchedule values")
        object.__setattr__(
            self,
            "schedules",
            tuple(sorted(schedules, key=lambda item: (item.neuron_id, item.spike_times_ms))),
        )
        if self.weight_mV is not None:
            object.__setattr__(self, "weight_mV", _number(self.weight_mV, "weight_mV"))
        ids = tuple(sorted({int(value) for value in self.refractory_free_neuron_ids}))
        object.__setattr__(self, "refractory_free_neuron_ids", ids)

    @property
    def fingerprint(self) -> str:
        payload = {
            "kind": "explicit-direct-voltage-v1",
            "weight_mV": self.weight_mV,
            "refractory_free_neuron_ids": self.refractory_free_neuron_ids,
            "schedules": [
                {"neuron_id": item.neuron_id, "times_ms": item.spike_times_ms}
                for item in self.schedules
            ],
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()


@dataclass(frozen=True, slots=True)
class PoissonStimulus:
    """Reference-style direct Poisson input with an explicit NumPy seed.

    This reproduces the model's conceptual operation (one independent
    PoissonInput per target with ``N=1``), not Brian2's random-number stream.
    """

    neuron_ids: tuple[int, ...] = ()
    neuron_ids2: tuple[int, ...] = ()
    rate_hz: float = 150.0
    rate2_hz: float = 0.0
    weight_factor: float = 250.0
    seed: int = 0

    def __post_init__(self) -> None:
        first = tuple(sorted({int(value) for value in self.neuron_ids}))
        second = tuple(sorted({int(value) for value in self.neuron_ids2}))
        if set(first) & set(second):
            raise ValueError("Poisson target classes must be disjoint")
        object.__setattr__(self, "neuron_ids", first)
        object.__setattr__(self, "neuron_ids2", second)
        for field in ("rate_hz", "rate2_hz", "weight_factor"):
            value = _number(getattr(self, field), field)
            if value < 0.0:
                raise ValueError(f"{field} must be non-negative")
            object.__setattr__(self, field, value)
        if isinstance(self.seed, bool):
            raise TypeError("seed must be an integer")
        object.__setattr__(self, "seed", int(self.seed))

    def generate(self, duration_ms: float, dt_ms: float, synaptic_weight_mV: float) -> ExplicitStimulus:
        duration_steps = _grid_steps(duration_ms, dt_ms, "duration_ms")
        rng = np.random.default_rng(self.seed)
        schedules: list[SpikeSchedule] = []
        for neuron_id, rate in (
            *((neuron_id, self.rate_hz) for neuron_id in self.neuron_ids),
            *((neuron_id, self.rate2_hz) for neuron_id in self.neuron_ids2),
        ):
            probability = rate * dt_ms / 1000.0
            if probability > 1.0:
                raise ValueError("Poisson rate times dt must not exceed one event per timestep")
            steps = np.flatnonzero(rng.random(duration_steps) < probability)
            schedules.append(
                SpikeSchedule(neuron_id, tuple(float(step * dt_ms) for step in steps))
            )
        return ExplicitStimulus(
            schedules=tuple(schedules),
            weight_mV=float(synaptic_weight_mV) * self.weight_factor,
            refractory_free_neuron_ids=self.neuron_ids + self.neuron_ids2,
        )

    @property
    def fingerprint(self) -> str:
        payload = {
            "kind": "reference-poisson-direct-voltage-v1",
            "neuron_ids": self.neuron_ids,
            "neuron_ids2": self.neuron_ids2,
            "rate_hz": self.rate_hz,
            "rate2_hz": self.rate2_hz,
            "weight_factor": self.weight_factor,
            "seed": self.seed,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()


def _grid_steps(value_ms: float, dt_ms: float, name: str) -> int:
    value = _number(value_ms, name)
    dt = _number(dt_ms, "dt_ms")
    if dt <= 0.0:
        raise ValueError("dt_ms must be positive")
    steps = int(round(value / dt))
    if steps < 0 or not np.isclose(value, steps * dt, rtol=0.0, atol=1e-10):
        raise ValueError(f"{name}={value_ms!r} is not exactly representable on dt={dt_ms!r}")
    return steps


def schedule_events(
    stimulus: ExplicitStimulus,
    *,
    neuron_positions: np.ndarray,
    duration_steps: int,
    dt_ms: float,
) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    """Validate and pack schedules into deterministic timestep event batches."""

    batches: dict[int, list[tuple[int, float]]] = {}
    for schedule in stimulus.schedules:
        position = int(np.searchsorted(neuron_positions, schedule.neuron_id))
        if position >= neuron_positions.size or int(neuron_positions[position]) != schedule.neuron_id:
            raise KeyError(f"unknown neuron ID: {schedule.neuron_id}")
        for time_ms in schedule.spike_times_ms:
            step = _grid_steps(time_ms, dt_ms, "spike time")
            if step >= duration_steps:
                raise ValueError("stimulus spike time must be before the simulation endpoint")
            batches.setdefault(step, []).append((position, 1.0))
    return {
        step: (
            np.asarray([item[0] for item in events], dtype=np.int64),
            np.asarray([item[1] for item in events], dtype=np.float64),
        )
        for step, events in sorted(batches.items())
    }


def validate_refractory_ids(
    ids: Iterable[int], neuron_positions: np.ndarray
) -> np.ndarray:
    values = np.asarray(sorted({int(value) for value in ids}), dtype=np.int64)
    positions = np.searchsorted(neuron_positions, values)
    in_range = positions < neuron_positions.size
    if np.any(~in_range) or np.any(neuron_positions[positions[in_range]] != values[in_range]):
        raise KeyError("unknown refractory-free stimulus neuron ID")
    return positions
