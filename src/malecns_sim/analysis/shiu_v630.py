"""Read-only reference summaries and bounded statistical comparisons."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from malecns_sim.dynamics.lif import SimulationResult


REFERENCE_RESULT_COLUMNS = ("t", "trial", "flywire_id", "exp_name")


@dataclass(frozen=True, slots=True)
class TrialSummary:
    condition: str
    duration_seconds: float
    trial_ids: np.ndarray
    mn9_spike_counts: np.ndarray
    mn9_firing_rates_hz: np.ndarray
    total_spike_counts: np.ndarray
    active_neuron_counts: np.ndarray
    input_spike_counts: np.ndarray | None = None

    def __post_init__(self) -> None:
        arrays = (
            self.trial_ids,
            self.mn9_spike_counts,
            self.mn9_firing_rates_hz,
            self.total_spike_counts,
            self.active_neuron_counts,
        )
        if len({array.size for array in arrays}) != 1:
            raise ValueError("trial summary arrays must have equal lengths")
        for array in arrays:
            array.flags.writeable = False
        if self.input_spike_counts is not None:
            if self.input_spike_counts.size != self.trial_ids.size:
                raise ValueError("input_spike_counts must match trial count")
            self.input_spike_counts.flags.writeable = False

    @property
    def trial_count(self) -> int:
        return int(self.trial_ids.size)

    @staticmethod
    def _mean(values: np.ndarray) -> float:
        return float(np.mean(values)) if values.size else 0.0

    @staticmethod
    def _std(values: np.ndarray) -> float:
        return float(np.std(values, ddof=0)) if values.size else 0.0

    @property
    def mn9_mean_firing_rate_hz(self) -> float:
        return self._mean(self.mn9_firing_rates_hz)

    @property
    def mn9_std_firing_rate_hz(self) -> float:
        return self._std(self.mn9_firing_rates_hz)

    @property
    def mn9_active_trial_fraction(self) -> float:
        return float(np.count_nonzero(self.mn9_spike_counts) / self.trial_count) if self.trial_count else 0.0

    @property
    def total_spike_mean(self) -> float:
        return self._mean(self.total_spike_counts)

    @property
    def total_spike_std(self) -> float:
        return self._std(self.total_spike_counts)

    @property
    def active_neuron_mean(self) -> float:
        return self._mean(self.active_neuron_counts)

    @property
    def active_neuron_std(self) -> float:
        return self._std(self.active_neuron_counts)


@dataclass(frozen=True, slots=True)
class MetricComparison:
    metric: str
    reference: float
    reproduction: float
    absolute_difference: float
    relative_difference: float | None


def _summary_from_frame(
    frame: pd.DataFrame,
    *,
    condition: str,
    mn9_id: int,
    duration_seconds: float,
) -> TrialSummary:
    if duration_seconds <= 0.0 or not np.isfinite(duration_seconds):
        raise ValueError("duration_seconds must be positive and finite")
    required = set(REFERENCE_RESULT_COLUMNS)
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"reference results are missing columns: {missing!r}")
    if frame.empty:
        raise ValueError("reference results contain no spikes")
    if frame["trial"].isna().any() or frame["flywire_id"].isna().any():
        raise ValueError("reference result IDs and trial values must be non-null")
    trial_values = np.sort(frame["trial"].astype(np.int64).unique())
    expected_trials = np.arange(trial_values[0], trial_values[-1] + 1, dtype=np.int64)
    if not np.array_equal(trial_values, expected_trials):
        raise ValueError("reference trial IDs must form a contiguous range")
    if (frame["t"].astype(float) < 0.0).any() or (frame["t"].astype(float) >= duration_seconds).any():
        raise ValueError("reference spike times fall outside the declared duration")
    grouped = frame.groupby("trial", sort=True)
    total = grouped.size().reindex(expected_trials, fill_value=0).to_numpy(dtype=np.int64)
    active = grouped["flywire_id"].nunique().reindex(expected_trials, fill_value=0).to_numpy(dtype=np.int64)
    mn9 = (
        frame.loc[frame["flywire_id"].astype(np.int64) == int(mn9_id)]
        .groupby("trial")
        .size()
        .reindex(expected_trials, fill_value=0)
        .to_numpy(dtype=np.int64)
    )
    return TrialSummary(
        condition=condition,
        duration_seconds=float(duration_seconds),
        trial_ids=expected_trials,
        mn9_spike_counts=mn9,
        mn9_firing_rates_hz=mn9.astype(np.float64) / duration_seconds,
        total_spike_counts=total,
        active_neuron_counts=active,
    )


def summarize_reference_parquet(
    path: str | Path,
    *,
    mn9_id: int,
    duration_seconds: float = 1.0,
) -> TrialSummary:
    """Summarize an official result parquet without modifying it."""

    frame = pd.read_parquet(path)
    condition_values = frame["exp_name"].dropna().unique().tolist() if "exp_name" in frame else []
    condition = str(condition_values[0]) if len(condition_values) == 1 else "reference"
    return _summary_from_frame(
        frame,
        condition=condition,
        mn9_id=mn9_id,
        duration_seconds=duration_seconds,
    )


def summarize_simulation_results(
    results: Iterable[SimulationResult],
    *,
    condition: str,
    mn9_id: int,
    duration_seconds: float,
    input_spike_counts: Iterable[int] | None = None,
) -> TrialSummary:
    """Summarize compact local results; each result is one fresh trial."""

    results = tuple(results)
    if not results:
        raise ValueError("at least one simulation result is required")
    input_counts = None if input_spike_counts is None else np.asarray(tuple(input_spike_counts), dtype=np.int64)
    if input_counts is not None and input_counts.size != len(results):
        raise ValueError("input_spike_counts must match result count")
    mn9 = np.asarray(
        [int(np.count_nonzero(result.spike_neuron_ids == int(mn9_id))) for result in results],
        dtype=np.int64,
    )
    total = np.asarray([result.emitted_spike_count for result in results], dtype=np.int64)
    active = np.asarray([result.active_neuron_count for result in results], dtype=np.int64)
    trial_ids = np.arange(len(results), dtype=np.int64)
    return TrialSummary(
        condition=condition,
        duration_seconds=float(duration_seconds),
        trial_ids=trial_ids,
        mn9_spike_counts=mn9,
        mn9_firing_rates_hz=mn9.astype(np.float64) / duration_seconds,
        total_spike_counts=total,
        active_neuron_counts=active,
        input_spike_counts=input_counts,
    )


def compare_summaries(
    reference: TrialSummary,
    reproduction: TrialSummary,
) -> tuple[MetricComparison, ...]:
    """Compare predeclared aggregate metrics using population SDs."""

    pairs = (
        ("mn9_mean_firing_rate_hz", reference.mn9_mean_firing_rate_hz, reproduction.mn9_mean_firing_rate_hz),
        ("mn9_std_firing_rate_hz", reference.mn9_std_firing_rate_hz, reproduction.mn9_std_firing_rate_hz),
        ("mn9_active_trial_fraction", reference.mn9_active_trial_fraction, reproduction.mn9_active_trial_fraction),
        ("total_spike_mean", reference.total_spike_mean, reproduction.total_spike_mean),
        ("total_spike_std", reference.total_spike_std, reproduction.total_spike_std),
        ("active_neuron_mean", reference.active_neuron_mean, reproduction.active_neuron_mean),
        ("active_neuron_std", reference.active_neuron_std, reproduction.active_neuron_std),
    )
    comparisons = []
    for metric, expected, actual in pairs:
        absolute = float(actual - expected)
        relative = None if expected == 0.0 else float(absolute / expected)
        comparisons.append(MetricComparison(metric, float(expected), float(actual), absolute, relative))
    return tuple(comparisons)
