"""Task 010 frozen-candidate causal perturbation analysis."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import median
from typing import Iterable, Mapping, Sequence
from types import SimpleNamespace

import numpy as np

from malecns_sim.analysis.task008 import (
    DT_MS,
    DURATION_MS,
    MIRROR_CONDITION,
    MN9_L,
    MN9_R,
    PRIMARY_CONDITION,
    PreparedNetwork,
    PreparedTask008,
    Task008Condition,
    deterministic_seed,
    load_task008_identities,
)
from malecns_sim.dynamics import (
    ExplicitStimulus,
    LIFParameters,
    PoissonStimulus,
    SimulationResult,
    simulate_lif,
)
from malecns_sim.dynamics.cache import PreparedGraphCache
from malecns_sim.dynamics.lif import EffectiveSignedProjection
from malecns_sim.homology import SugarPopulation, population_fingerprint


TASK010_SCHEMA = "malecns-sim-task010-frozen-candidate-causal-v1"
FROZEN_CANDIDATE_IDS = ("10135", "10313", "12752", "43765", "512730", "514753", "517861")
TASK008_FULL_CACHE_FINGERPRINT = "8064dbec4ecf5ac72a4ab23835e4fcbdc6cdcc5315a1b71f71c135de9eb8cf4d"
TASK008_PREPARED_FINGERPRINT = "d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495"
TASK008_UNSIGNED_GRAPH_FINGERPRINT = "fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4"
TASK008_SIGN_POLICY_FINGERPRINT = "861f07218122e122383d8465b30e65f5eb1d5b11a474b767a6312b3115ecaf25"
TASK008_EXPERIMENT_FINGERPRINT_KEY = "experiment_fingerprint"
DEFAULT_TRIAL_COUNT = 30
DEFAULT_FREQUENCY_HZ = 100.0
DEFAULT_DURATION_MS = 1000.0
PRELIGHT_DURATION_MS = 20.0


def _digest(prefix: str, payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(prefix.encode("utf-8") + b"\0" + encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class EffectThresholds:
    """Predeclared descriptive thresholds for one readout effect."""

    major_absolute_hz: float = 20.0
    major_percent: float = 50.0
    moderate_absolute_hz: float = 5.0
    moderate_percent: float = 20.0
    small_absolute_hz: float = 1.0
    small_percent: float = 5.0

    def classify(self, absolute_change_hz: float, absolute_percent: float | None) -> str:
        if absolute_change_hz >= self.major_absolute_hz or (
            absolute_percent is not None and absolute_percent >= self.major_percent
        ):
            return "major"
        if absolute_change_hz >= self.moderate_absolute_hz or (
            absolute_percent is not None and absolute_percent >= self.moderate_percent
        ):
            return "moderate"
        if absolute_change_hz >= self.small_absolute_hz or (
            absolute_percent is not None and absolute_percent >= self.small_percent
        ):
            return "small"
        return "negligible"


PREDECLARED_THRESHOLDS = EffectThresholds()


@dataclass(frozen=True, slots=True)
class FrozenCandidate:
    body_id: str
    type: str | None
    instance: str | None
    side: str | None
    superclass: str | None
    cell_class: str | None
    neurotransmitter: str | None
    homolog_body_id: str | None
    homolog_instance: str | None
    structural_metrics: tuple[Mapping[str, object], ...]
    reasons: tuple[str, ...]
    routes: tuple[str, ...]
    signed_proxy_values: tuple[tuple[str, int], ...]


@dataclass(frozen=True, slots=True)
class FrozenCandidateManifest:
    candidates: tuple[FrozenCandidate, ...]
    source_task009_fingerprint: str
    fingerprint: str

    @property
    def body_ids(self) -> tuple[str, ...]:
        return tuple(item.body_id for item in self.candidates)


@dataclass(frozen=True, slots=True)
class Task010Trial:
    candidate_id: str
    condition: str
    stimulus_side: str
    trial_index: int
    seed: int
    mn9_l_spikes: int
    mn9_r_spikes: int
    total_network_spikes: int
    active_neuron_count: int
    sugar_input_events: int
    queued_synaptic_events: int
    delivered_synaptic_events: int
    result_digest: str
    duration_ms: float = DEFAULT_DURATION_MS

    def rate_hz(self, neuron_id: str) -> float:
        spikes = self.mn9_l_spikes if neuron_id == MN9_L else self.mn9_r_spikes
        return float(spikes) * 1000.0 / self.duration_ms


@dataclass(frozen=True, slots=True)
class RateEffect:
    baseline_mean_hz: float
    silenced_mean_hz: float
    absolute_change_hz: float
    percent_change: float | None
    classification: str


@dataclass(frozen=True, slots=True)
class PairedMetricSummary:
    mean_delta: float
    median_delta: float
    minimum_delta: float
    maximum_delta: float
    standard_deviation: float


@dataclass(frozen=True, slots=True)
class PairedTrialSummary:
    mn9_l: PairedMetricSummary
    mn9_r: PairedMetricSummary
    total_network_spikes: PairedMetricSummary


def candidate_set_fingerprint(candidates: Sequence[FrozenCandidate]) -> str:
    return _digest("malecns-sim-task010-candidate-manifest-v1", [asdict(item) for item in candidates])


def _find_homolog(rows: Sequence[Mapping[str, object]], body_id: str) -> tuple[str | None, str | None]:
    for row in rows:
        if str(row.get("left_id")) == body_id:
            base = row.get("instance_base")
            return str(row.get("right_id")), f"{base}_R" if base else None
        if str(row.get("right_id")) == body_id:
            base = row.get("instance_base")
            return str(row.get("left_id")), f"{base}_L" if base else None
    return None, None


def load_frozen_candidate_manifest(task009_results_path: str | Path) -> FrozenCandidateManifest:
    """Load and validate the immutable Task 009 candidate artifact."""

    with Path(task009_results_path).open("r", encoding="utf-8") as handle:
        report = json.load(handle)
    candidate_rows = report.get("candidate_task010_intervention_list")
    if not isinstance(candidate_rows, list):
        raise ValueError("Task 009 candidate list is missing")
    ids = tuple(str(row.get("body_id")) for row in candidate_rows)
    if ids != FROZEN_CANDIDATE_IDS:
        raise ValueError(f"Task 009 candidate list mismatch: expected {FROZEN_CANDIDATE_IDS}, got {ids}")
    if len(set(ids)) != len(ids):
        raise ValueError("Task 009 candidate list contains duplicate body IDs")
    metadata_by_id: dict[str, Mapping[str, object]] = {}
    route_metrics_by_id: dict[str, list[Mapping[str, object]]] = {body_id: [] for body_id in ids}
    for route in report.get("full", {}).get("routes", []):
        for metric in route.get("intermediates", []):
            body_id = str(metric.get("intermediate_id"))
            if body_id in route_metrics_by_id:
                route_metrics_by_id[body_id].append(metric)
    for route_entries in report.get("full", {}).get("top_intermediates", {}).values():
        for metric_entries in route_entries.values():
            for entry in metric_entries:
                metadata = entry.get("metadata", {})
                body_id = str(metadata.get("body_id"))
                if body_id in FROZEN_CANDIDATE_IDS:
                    metadata_by_id[body_id] = metadata
    homolog_rows = report.get("full", {}).get("homolog_pairs", [])
    candidates: list[FrozenCandidate] = []
    for row in candidate_rows:
        body_id = str(row["body_id"])
        metadata = metadata_by_id.get(body_id)
        if metadata is None:
            raise ValueError(f"Task 009 metadata is missing frozen candidate {body_id}")
        homolog_body_id, homolog_instance = _find_homolog(homolog_rows, body_id)
        candidates.append(
            FrozenCandidate(
                body_id=body_id,
                type=metadata.get("type"),
                instance=metadata.get("instance"),
                side=metadata.get("side"),
                superclass=metadata.get("superclass"),
                cell_class=metadata.get("cell_class"),
                neurotransmitter=metadata.get("neurotransmitter"),
                homolog_body_id=homolog_body_id,
                homolog_instance=homolog_instance,
                structural_metrics=tuple(route_metrics_by_id[body_id]),
                reasons=tuple(row.get("reasons", ())),
                routes=tuple(row.get("routes", ())),
                signed_proxy_values=tuple((str(name), int(value)) for name, value in row.get("signed_proxy_values", ())),
            )
        )
    fingerprint = candidate_set_fingerprint(candidates)
    expected_source = report.get("fingerprints", {}).get("candidate_task010_intervention_list", "")
    return FrozenCandidateManifest(tuple(candidates), str(expected_source), fingerprint)


def validate_candidate_ids(candidate_ids: Iterable[str | int], known_neuron_ids: Iterable[str | int]) -> tuple[str, ...]:
    """Reject unknown intervention identities before a simulation starts."""

    normalized = tuple(str(int(value)) for value in candidate_ids)
    known = {str(int(value)) for value in known_neuron_ids}
    unknown = tuple(value for value in normalized if value not in known)
    if unknown:
        raise ValueError(f"unknown candidate neuron IDs: {unknown}")
    if len(set(normalized)) != len(normalized):
        raise ValueError("candidate intervention IDs must be unique")
    return normalized


def frozen_silencing_ids(manifest: FrozenCandidateManifest, body_ids: Iterable[str | int]) -> tuple[str, ...]:
    """Return an immutable validated outgoing-silencing mask identity."""

    requested = validate_candidate_ids(body_ids, manifest.body_ids)
    allowed = set(manifest.body_ids)
    if any(value not in allowed for value in requested):
        raise ValueError("intervention contains a neuron outside the frozen candidate set")
    return requested


def ensure_separate_output(output_path: str | Path, task008_results_path: str | Path) -> None:
    """Fail closed when a derived Task 010 path would overwrite Task 008."""

    if Path(output_path).resolve() == Path(task008_results_path).resolve():
        raise ValueError("Task 010 output must not overwrite Task 008 results")


def rate_effect(baseline_mean_hz: float, silenced_mean_hz: float, thresholds: EffectThresholds = PREDECLARED_THRESHOLDS) -> RateEffect:
    signed_change = float(silenced_mean_hz) - float(baseline_mean_hz)
    absolute_change = abs(signed_change)
    percent = None if baseline_mean_hz == 0.0 else 100.0 * signed_change / abs(float(baseline_mean_hz))
    absolute_percent = None if percent is None else abs(percent)
    return RateEffect(
        baseline_mean_hz=float(baseline_mean_hz),
        silenced_mean_hz=float(silenced_mean_hz),
        absolute_change_hz=absolute_change,
        percent_change=percent,
        classification=thresholds.classify(absolute_change, absolute_percent),
    )


def asymmetry_metric(mn9_l_hz: float, mn9_r_hz: float) -> float | None:
    denominator = float(mn9_l_hz) + float(mn9_r_hz)
    if denominator == 0.0:
        return None
    return (float(mn9_l_hz) - float(mn9_r_hz)) / denominator


def _paired_metric(values: Sequence[float]) -> PairedMetricSummary:
    if not values:
        raise ValueError("paired metric requires at least one value")
    array = np.asarray(values, dtype=np.float64)
    return PairedMetricSummary(
        mean_delta=float(array.mean()),
        median_delta=float(median(array.tolist())),
        minimum_delta=float(array.min()),
        maximum_delta=float(array.max()),
        standard_deviation=float(array.std(ddof=1)) if array.size > 1 else 0.0,
    )


def paired_trial_summary(baseline: Sequence[Task010Trial], silenced: Sequence[Task010Trial]) -> PairedTrialSummary:
    if len(baseline) != len(silenced) or not baseline:
        raise ValueError("paired trial sets must have equal nonzero length")
    pairs = []
    for left, right in zip(baseline, silenced):
        if (left.trial_index, left.seed) != (right.trial_index, right.seed):
            raise ValueError("paired trials must have identical trial indices and seeds")
        pairs.append((right, left))
    return PairedTrialSummary(
        mn9_l=_paired_metric([right.mn9_l_spikes - left.mn9_l_spikes for right, left in pairs]),
        mn9_r=_paired_metric([right.mn9_r_spikes - left.mn9_r_spikes for right, left in pairs]),
        total_network_spikes=_paired_metric([right.total_network_spikes - left.total_network_spikes for right, left in pairs]),
    )


def _make_schedules(
    prepared: PreparedNetwork,
    population: SugarPopulation,
    *,
    experiment_identity: str,
    side: str,
    trial_count: int,
    frequency_hz: float,
    duration_ms: float,
    parameters: LIFParameters,
) -> tuple[tuple[int, int, ExplicitStimulus], ...]:
    schedules = []
    for trial_index in range(trial_count):
        seed = deterministic_seed(
            experiment_identity,
            side,
            frequency_hz,
            trial_index,
            prepared.fingerprint,
            prepared.signed_connectome.sign_policy_id,
        )
        stimulus = PoissonStimulus(
            tuple(int(item) for item in population.candidate_body_ids),
            rate_hz=frequency_hz,
            seed=seed,
        ).generate(duration_ms, DT_MS, parameters.synaptic_weight_per_anatomical_synapse_mV)
        schedules.append((trial_index, seed, stimulus))
    return tuple(schedules)


def _run_results(
    prepared: PreparedNetwork,
    schedules: Sequence[tuple[int, int, ExplicitStimulus]],
    *,
    duration_ms: float,
    silenced_ids: Sequence[str] = (),
    force_cpu: bool = False,
) -> tuple[SimulationResult, ...]:
    parameters = LIFParameters()
    silenced = tuple(int(value) for value in silenced_ids)
    stimuli = tuple(item[2] for item in schedules)
    if prepared.cuda_graph is not None and not force_cpu:
        from malecns_sim.dynamics.cuda import simulate_cuda_batch

        return simulate_cuda_batch(
            prepared.projection,
            stimuli,
            duration_ms=duration_ms,
            parameters=parameters,
            dt_ms=DT_MS,
            silenced_neuron_ids=silenced,
            cuda_graph=prepared.cuda_graph,
        )
    return tuple(
        simulate_lif(
            prepared.projection,
            duration_ms=duration_ms,
            stimulus=stimulus,
            parameters=parameters,
            dt_ms=DT_MS,
            silenced_neuron_ids=silenced,
        )
        for stimulus in stimuli
    )


def _trials_from_results(
    candidate_id: str,
    condition: Task008Condition,
    stimulus_side: str,
    schedules: Sequence[tuple[int, int, ExplicitStimulus]],
    results: Sequence[SimulationResult],
    projection: EffectiveSignedProjection,
) -> tuple[Task010Trial, ...]:
    if len(schedules) != len(results):
        raise ValueError("schedule and result counts differ")
    positions = {int(body_id): index for index, body_id in enumerate(projection.neuron_ids.tolist())}
    left_position = positions[int(MN9_L)]
    right_position = positions[int(MN9_R)]
    trials = []
    for (trial_index, seed, stimulus), result in zip(schedules, results):
        trials.append(
            Task010Trial(
                candidate_id=candidate_id,
                condition=condition.name,
                stimulus_side=stimulus_side,
                trial_index=trial_index,
                seed=seed,
                mn9_l_spikes=int(result.spike_counts[left_position]),
                mn9_r_spikes=int(result.spike_counts[right_position]),
                total_network_spikes=int(result.emitted_spike_count),
                active_neuron_count=int(result.active_neuron_count),
                sugar_input_events=sum(len(item.spike_times_ms) for item in stimulus.schedules),
                queued_synaptic_events=int(result.queued_synaptic_event_count),
                delivered_synaptic_events=int(result.delivered_synaptic_event_count),
                result_digest=result.spike_result_digest,
                duration_ms=float(result.duration_ms),
            )
        )
    return tuple(trials)


def _mean_rate(trials: Sequence[Task010Trial], neuron_id: str) -> float:
    return float(np.mean([trial.rate_hz(neuron_id) for trial in trials]))


def summarize_condition(
    baseline: Sequence[Task010Trial],
    silenced: Sequence[Task010Trial],
    thresholds: EffectThresholds = PREDECLARED_THRESHOLDS,
) -> dict[str, object]:
    if not baseline or not silenced:
        raise ValueError("condition summaries require baseline and silenced trials")
    baseline_l = _mean_rate(baseline, MN9_L)
    baseline_r = _mean_rate(baseline, MN9_R)
    silenced_l = _mean_rate(silenced, MN9_L)
    silenced_r = _mean_rate(silenced, MN9_R)
    paired = paired_trial_summary(baseline, silenced)
    return {
        "mn9_l": asdict(rate_effect(baseline_l, silenced_l, thresholds)),
        "mn9_r": asdict(rate_effect(baseline_r, silenced_r, thresholds)),
        "baseline_total_network_spikes_mean": float(np.mean([trial.total_network_spikes for trial in baseline])),
        "silenced_total_network_spikes_mean": float(np.mean([trial.total_network_spikes for trial in silenced])),
        "baseline_active_neuron_count_mean": float(np.mean([trial.active_neuron_count for trial in baseline])),
        "silenced_active_neuron_count_mean": float(np.mean([trial.active_neuron_count for trial in silenced])),
        "baseline_delivered_event_count_mean": float(np.mean([trial.delivered_synaptic_events for trial in baseline])),
        "silenced_delivered_event_count_mean": float(np.mean([trial.delivered_synaptic_events for trial in silenced])),
        "baseline_asymmetry": asymmetry_metric(baseline_l, baseline_r),
        "silenced_asymmetry": asymmetry_metric(silenced_l, silenced_r),
        "paired": asdict(paired),
    }


def _cache_record(cache_path: str | Path) -> dict[str, object]:
    cache = PreparedGraphCache.load(cache_path)
    return {
        "path": str(Path(cache_path)),
        "cache_fingerprint": cache.cache_fingerprint,
        "identity": cache.identity.as_dict(),
        "projection_fingerprint": cache.projection_fingerprint,
        "neuron_count": int(cache.neuron_ids.size),
        "edge_count": int(cache.indices.size),
    }


def _prepare_verified_cached_network(cache_path: str | Path) -> PreparedNetwork:
    """Rehydrate the already verified Task 008 projection without source rereading."""

    started = time.perf_counter()
    cache = PreparedGraphCache.load(cache_path)
    identity = cache.identity
    if (
        identity.male_cns_release_identity != "MaleCNS-v1.0"
        or identity.curated_graph_fingerprint != TASK008_UNSIGNED_GRAPH_FINGERPRINT
        or identity.sign_policy_fingerprint != TASK008_SIGN_POLICY_FINGERPRINT
        or identity.unresolved_edge_policy != "MaleCNSV1ConsensusThenPredictedThenCelltype"
        or identity.min_synapses != 0
        or identity.synaptic_weight_mV != 0.275
        or identity.lif_parameter_identity != "shiu-reference-lif-parameters-v1"
        or cache.cache_fingerprint != TASK008_FULL_CACHE_FINGERPRINT
        or cache.projection_fingerprint != "ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f"
    ):
        raise RuntimeError("Task 008 cache provenance does not match the frozen baseline")
    projection = cache.to_projection()
    from malecns_sim.dynamics.cuda import cuda_available, upload_graph

    if not cuda_available():
        raise RuntimeError("Task 010 requires an available CUDA device")
    cuda_graph, upload_seconds = upload_graph(projection)
    signed_identity = SimpleNamespace(
        sign_policy_id="Shiu2024SignPolicy",
        unsigned_graph_fingerprint=TASK008_UNSIGNED_GRAPH_FINGERPRINT,
        signed_policy_fingerprint=TASK008_SIGN_POLICY_FINGERPRINT,
    )
    memory_bytes = sum(
        int(getattr(projection, field).nbytes)
        for field in (
            "neuron_ids",
            "source_positions",
            "target_positions",
            "effective_weights_mV",
            "outgoing_indptr",
            "outgoing_targets",
            "outgoing_weights_mV",
        )
    )
    return PreparedNetwork(
        projection=projection,
        signed_connectome=signed_identity,
        graph_name="full-cached",
        preparation_seconds=0.0,
        graph_loading_seconds=time.perf_counter() - started,
        setup_seconds=time.perf_counter() - started,
        memory_bytes=memory_bytes,
        fingerprint=TASK008_PREPARED_FINGERPRINT,
        cache_path=str(Path(cache_path)),
        cache_fingerprint=cache.cache_fingerprint,
        cuda_graph=cuda_graph,
    )


def _device_record() -> dict[str, object]:
    try:
        import cupy as cp

        properties = cp.cuda.runtime.getDeviceProperties(0)
        name = properties.get("name", b"") if isinstance(properties, dict) else b""
        if isinstance(name, bytes):
            name = name.decode("utf-8", errors="replace")
        return {"available": True, "device": str(name), "runtime_version": int(cp.cuda.runtime.runtimeGetVersion())}
    except Exception as exc:
        return {"available": False, "error": type(exc).__name__}


def run_silenced_cpu_gpu_preflight(
    prepared: PreparedNetwork,
    schedules: Sequence[tuple[int, int, ExplicitStimulus]],
    candidate_id: str,
    *,
    duration_ms: float = PRELIGHT_DURATION_MS,
) -> dict[str, object]:
    if prepared.cuda_graph is None:
        raise RuntimeError("Task 010 requires CUDA for the silencing preflight")
    bounded = tuple((index, seed, stimulus) for index, seed, stimulus in schedules)
    cpu = _run_results(prepared, bounded, duration_ms=duration_ms, silenced_ids=(candidate_id,), force_cpu=True)
    gpu = _run_results(prepared, bounded, duration_ms=duration_ms, silenced_ids=(candidate_id,))
    equality = []
    for left, right in zip(cpu, gpu):
        equality.append(
            bool(
                np.array_equal(left.spike_neuron_ids, right.spike_neuron_ids)
                and np.array_equal(left.spike_timesteps, right.spike_timesteps)
                and np.array_equal(left.spike_counts, right.spike_counts)
                and left.spike_result_digest == right.spike_result_digest
            )
        )
    if not all(equality):
        raise AssertionError("Task 010 CPU/GPU silencing preflight canonical spike-event mismatch")
    return {
        "candidate_id": candidate_id,
        "duration_ms": duration_ms,
        "trial_count": len(bounded),
        "backend": "cuda-float64",
        "canonical_spike_event_equal": True,
        "cpu_digests": [item.spike_result_digest for item in cpu],
        "gpu_digests": [item.spike_result_digest for item in gpu],
    }


def _replay_check(
    task008_results_path: str | Path,
    condition: Task008Condition,
    trials: Sequence[Task010Trial],
) -> dict[str, object]:
    with Path(task008_results_path).open("r", encoding="utf-8") as handle:
        report = json.load(handle)
    key = "repeat_100hz" if condition is PRIMARY_CONDITION else "mirror_100hz"
    expected = report[key]["trials"]
    observed = [asdict(item) for item in trials]
    fields = ("trial_index", "seed", "result_digest", "total_network_spikes")
    equal = len(expected) == len(observed) and all(
        all(expected_item[field] == observed_item[field] for field in fields)
        for expected_item, observed_item in zip(expected, observed)
    )
    if not equal:
        raise RuntimeError(f"Task 008 {condition.name} baseline replay mismatch")
    return {"condition": condition.name, "trial_count": len(observed), "exact_trial_replay": True}


def _atomic_write_json(path: str | Path, payload: object) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    os.replace(temporary, target)


def run_task010(
    annotation_path: str | Path,
    neurotransmitter_path: str | Path,
    weights_path: str | Path,
    task008_results_path: str | Path,
    task009_results_path: str | Path,
    cache_path: str | Path,
    output_path: str | Path,
    *,
    trial_count: int = DEFAULT_TRIAL_COUNT,
) -> dict[str, object]:
    """Execute the frozen Task 010 matrix and write a separate artifact."""

    ensure_separate_output(output_path, task008_results_path)
    manifest = load_frozen_candidate_manifest(task009_results_path)
    identities: PreparedTask008 = load_task008_identities(annotation_path, neurotransmitter_path)
    prepared = _prepare_verified_cached_network(cache_path)
    if prepared.cache_fingerprint != TASK008_FULL_CACHE_FINGERPRINT or prepared.fingerprint != TASK008_PREPARED_FINGERPRINT:
        raise RuntimeError("Task 008 prepared graph identity mismatch")
    validate_candidate_ids(manifest.body_ids, prepared.projection.neuron_ids)
    parameters = LIFParameters()
    populations = ((PRIMARY_CONDITION, identities.sugar_left, "L"), (MIRROR_CONDITION, identities.sugar_right, "R"))
    schedules_by_condition = {
        condition.name: _make_schedules(
            prepared,
            population,
            experiment_identity=identities.fingerprint,
            side=side,
            trial_count=trial_count,
            frequency_hz=DEFAULT_FREQUENCY_HZ,
            duration_ms=DEFAULT_DURATION_MS,
            parameters=parameters,
        )
        for condition, population, side in populations
    }
    baseline_trials: dict[str, tuple[Task010Trial, ...]] = {}
    for condition, _, side in populations:
        schedules = schedules_by_condition[condition.name]
        results = _run_results(prepared, schedules, duration_ms=DEFAULT_DURATION_MS)
        baseline_trials[condition.name] = _trials_from_results(
            "baseline", condition, side, schedules, results, prepared.projection
        )
    replay = {
        condition.name: _replay_check(task008_results_path, condition, baseline_trials[condition.name])
        for condition, _, _ in populations
    }
    preflight_schedules = _make_schedules(
        prepared,
        identities.sugar_left,
        experiment_identity=identities.fingerprint,
        side="L",
        trial_count=2,
        frequency_hz=DEFAULT_FREQUENCY_HZ,
        duration_ms=PRELIGHT_DURATION_MS,
        parameters=parameters,
    )
    preflight = run_silenced_cpu_gpu_preflight(prepared, preflight_schedules, "512730")
    outcomes: dict[str, object] = {}
    candidate_trial_sets: dict[str, dict[str, tuple[Task010Trial, ...]]] = {}
    for candidate in manifest.candidates:
        silenced_ids = frozen_silencing_ids(manifest, (candidate.body_id,))
        candidate_trial_sets[candidate.body_id] = {}
        for condition, _, side in populations:
            schedules = schedules_by_condition[condition.name]
            results = _run_results(
                prepared,
                schedules,
                duration_ms=DEFAULT_DURATION_MS,
                silenced_ids=silenced_ids,
            )
            trials = _trials_from_results(candidate.body_id, condition, side, schedules, results, prepared.projection)
            candidate_trial_sets[candidate.body_id][condition.name] = trials
            outcomes[f"{candidate.body_id}:{condition.name}"] = {
                "candidate_id": candidate.body_id,
                "condition": condition.name,
                "stimulus_side": side,
                "trials": [asdict(item) for item in trials],
                "summary": summarize_condition(baseline_trials[condition.name], trials),
            }
    joint_id = "+".join(manifest.body_ids)
    joint_trial_sets: dict[str, tuple[Task010Trial, ...]] = {}
    for condition, _, side in populations:
        schedules = schedules_by_condition[condition.name]
        results = _run_results(
            prepared,
            schedules,
            duration_ms=DEFAULT_DURATION_MS,
            silenced_ids=manifest.body_ids,
        )
        trials = _trials_from_results(joint_id, condition, side, schedules, results, prepared.projection)
        joint_trial_sets[condition.name] = trials
        outcomes[f"all-seven:{condition.name}"] = {
            "candidate_id": joint_id,
            "condition": condition.name,
            "stimulus_side": side,
            "trials": [asdict(item) for item in trials],
            "summary": summarize_condition(baseline_trials[condition.name], trials),
        }
    classifications = [
        (key, value["summary"]["mn9_l"]["classification"])
        for key, value in outcomes.items()
        if key.startswith(tuple(manifest.body_ids))
    ]
    strong_key = next((key for key, category in classifications if category in {"major", "moderate"}), f"512730:{PRIMARY_CONDITION.name}")
    negligible_key = next((key for key, category in classifications if category == "negligible"), f"10135:{PRIMARY_CONDITION.name}")
    repeat_targets = (strong_key, negligible_key, "all-seven:" + PRIMARY_CONDITION.name, "all-seven:" + MIRROR_CONDITION.name)
    repeats: dict[str, object] = {}
    for key in repeat_targets:
        if key.startswith("all-seven:"):
            candidate_id = joint_id
            condition_name = key.split(":", 1)[1]
            repeated_trials = _trials_from_results(
                candidate_id,
                PRIMARY_CONDITION if condition_name == PRIMARY_CONDITION.name else MIRROR_CONDITION,
                "L" if condition_name == PRIMARY_CONDITION.name else "R",
                schedules_by_condition[condition_name],
                _run_results(prepared, schedules_by_condition[condition_name], duration_ms=DEFAULT_DURATION_MS, silenced_ids=manifest.body_ids),
                prepared.projection,
            )
            original_trials = joint_trial_sets[condition_name]
        else:
            candidate_id, condition_name = key.split(":", 1)
            condition = PRIMARY_CONDITION if condition_name == PRIMARY_CONDITION.name else MIRROR_CONDITION
            repeated_trials = _trials_from_results(
                candidate_id,
                condition,
                "L" if condition is PRIMARY_CONDITION else "R",
                schedules_by_condition[condition_name],
                _run_results(prepared, schedules_by_condition[condition_name], duration_ms=DEFAULT_DURATION_MS, silenced_ids=(candidate_id,)),
                prepared.projection,
            )
            original_trials = candidate_trial_sets[candidate_id][condition_name]
        equal = [
            left.result_digest == right.result_digest
            and left.mn9_l_spikes == right.mn9_l_spikes
            and left.mn9_r_spikes == right.mn9_r_spikes
            and left.total_network_spikes == right.total_network_spikes
            for left, right in zip(original_trials, repeated_trials)
        ]
        if not all(equal):
            raise RuntimeError(f"Task 010 repeatability gate failed for {key}")
        repeats[key] = {"trial_count": len(equal), "identical": True, "result_digests_equal": equal}
    payload = {
        "task": "010",
        "schema": TASK010_SCHEMA,
        "status": "COMPLETE",
        "head": subprocess.check_output(("git", "rev-parse", "HEAD"), text=True).strip(),
        "candidate_manifest": {
            "candidates": [asdict(item) for item in manifest.candidates],
            "source_task009_fingerprint": manifest.source_task009_fingerprint,
            "fingerprint": manifest.fingerprint,
        },
        "thresholds": asdict(PREDECLARED_THRESHOLDS),
        "readouts": {"MN9_L": MN9_L, "MN9_R": MN9_R},
        "intervention_semantics": "Silenced neurons receive input, update, and may spike internally; only outgoing synaptic scheduling is suppressed.",
        "task008": {
            "experiment_fingerprint": identities.fingerprint,
            "left_population_fingerprint": population_fingerprint(identities.sugar_left),
            "right_population_fingerprint": population_fingerprint(identities.sugar_right),
            "prepared_fingerprint": prepared.fingerprint,
            "cache": _cache_record(cache_path),
            "backend": "cuda-float64",
            "device": _device_record(),
            "parameters": asdict(parameters),
            "frequency_hz": DEFAULT_FREQUENCY_HZ,
            "duration_ms": DEFAULT_DURATION_MS,
            "dt_ms": DT_MS,
            "trial_count": trial_count,
            "sign_policy": prepared.signed_connectome.sign_policy_id,
        },
        "baseline_replay": replay,
        "cpu_gpu_silencing_preflight": preflight,
        "outcomes": outcomes,
        "repeatability": repeats,
        "result_digest": _digest("malecns-sim-task010-result-v1", {"outcomes": outcomes, "repeats": repeats}),
    }
    _atomic_write_json(output_path, payload)
    return payload
