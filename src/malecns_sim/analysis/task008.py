"""Task 008 sugar-to-MN9 experiment identities, statistics, and execution."""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from malecns_sim.analysis.task007 import (
    MALE_CNS_ANNOTATION_COLUMNS,
    load_male_cns_candidates,
)
from malecns_sim.data.male_cns_v1 import (
    official_v1_mapping,
    load_male_cns_v1_numeric,
    project_numeric_connectome,
    select_publication_neuron_ids,
    threshold_curated_projection,
)
from malecns_sim.data.neurotransmitter import (
    NeurotransmitterEvidence,
    NeurotransmitterResolutionPolicy,
    load_male_cns_v1_neurotransmitter_evidence,
)
from malecns_sim.dynamics import (
    EffectiveSignedProjection,
    LIFParameters,
    PoissonStimulus,
    PreparedGraphCache,
    simulate_lif_active,
)
from malecns_sim.graph.signed import SignedAnatomicalConnectome, signed_graph_fingerprint
from malecns_sim.homology import (
    MaleCNSCandidate,
    SugarPopulation,
    derive_sugar_population,
    population_fingerprint,
)
from malecns_sim.sign import Shiu2024SignPolicy


PRIMARY_FREQUENCIES_HZ = (10.0, 25.0, 50.0, 100.0, 150.0, 200.0)
REFERENCE_V630_HZ = (0.0, 0.0, 22.03, 67.4, 82.57, 93.13)
REFERENCE_SUGAR_COUNT = 21
TRIAL_COUNT = 30
DURATION_MS = 1000.0
DT_MS = 0.1
MN9_R = "16949"
MN9_L = "10331"
TASK007_RIGHT_POPULATION_FINGERPRINT = "2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b"


@dataclass(frozen=True, slots=True)
class Task008Condition:
    """An immutable, named input/readout contract."""

    name: str
    input_population: str
    contralateral_mn9: str
    ipsilateral_mn9: str
    side_relation: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        expected = {
            "sugar_left": (MN9_R, MN9_L),
            "sugar_right": (MN9_L, MN9_R),
        }
        try:
            contralateral, ipsilateral = expected[self.input_population]
        except KeyError as exc:
            raise ValueError("condition input population must be sugar_left or sugar_right") from exc
        if (self.contralateral_mn9, self.ipsilateral_mn9) != (contralateral, ipsilateral):
            raise ValueError("condition readout assignment violates the laterality gate")


PRIMARY_CONDITION = Task008Condition(
    name="primary_left_sugar_to_right_mn9",
    input_population="sugar_left",
    contralateral_mn9=MN9_R,
    ipsilateral_mn9=MN9_L,
    side_relation="left sugar -> right MN9",
    provenance=("Task 007 sugar mapping", "Task 007b side-resolved MN9 mapping"),
)
MIRROR_CONDITION = Task008Condition(
    name="mirror_right_sugar_to_left_mn9",
    input_population="sugar_right",
    contralateral_mn9=MN9_L,
    ipsilateral_mn9=MN9_R,
    side_relation="right sugar -> left MN9",
    provenance=("Task 007 sugar mapping", "Task 007b side-resolved MN9 mapping"),
)


@dataclass(frozen=True, slots=True)
class PopulationReport:
    name: str
    body_ids: tuple[str, ...]
    count: int
    type_counts: tuple[tuple[str, int], ...]
    flywire_type_counts: tuple[tuple[str, int], ...]
    soma_side_counts: tuple[tuple[str, int], ...]
    root_side_counts: tuple[tuple[str, int], ...]
    superclass_counts: tuple[tuple[str, int], ...]
    class_counts: tuple[tuple[str, int], ...]
    sensory_metadata: tuple[tuple[str, tuple[tuple[str, int], ...]], ...]
    resolved_nt_count: int
    unresolved_nt_count: int
    resolved_outgoing_edge_count: int = 0
    unresolved_outgoing_edge_count: int = 0
    resolved_outgoing_anatomical_weight: int = 0
    unresolved_outgoing_anatomical_weight: int = 0
    total_outgoing_anatomical_weight: int = 0
    fingerprint: str = ""


@dataclass(frozen=True, slots=True)
class PreparedNetwork:
    """Immutable signed projection reused by all trials in one graph condition."""

    projection: EffectiveSignedProjection
    signed_connectome: SignedAnatomicalConnectome
    graph_name: str
    preparation_seconds: float
    graph_loading_seconds: float
    setup_seconds: float
    memory_bytes: int
    fingerprint: str
    cache_path: str | None = None
    cache_fingerprint: str | None = None
    cuda_graph: object | None = None


@dataclass(frozen=True, slots=True)
class TrialObservation:
    frequency_hz: float
    trial_index: int
    seed: int
    contralateral_spikes: int
    ipsilateral_spikes: int
    total_network_spikes: int
    active_neuron_count: int
    sugar_input_events: int
    queued_synaptic_events: int
    delivered_synaptic_events: int
    result_digest: str
    duration_ms: float = DURATION_MS
    runtime_seconds: float = 0.0


@dataclass(frozen=True, slots=True)
class ConditionSummary:
    condition: str
    frequency_hz: float
    trial_count: int
    contralateral_mean_hz: float
    contralateral_std_hz: float
    contralateral_active_fraction: float
    ipsilateral_mean_hz: float
    ipsilateral_std_hz: float
    ipsilateral_active_fraction: float
    contra_minus_ipsi_hz: float
    total_network_mean_hz: float
    total_network_std_hz: float
    active_neuron_mean: float
    sugar_input_events_mean: float
    delivered_synaptic_events_mean: float
    result_digest: str


@dataclass(frozen=True, slots=True)
class PreparedTask008:
    candidates: tuple[MaleCNSCandidate, ...]
    sugar_left: SugarPopulation
    sugar_right: SugarPopulation
    primary: Task008Condition = PRIMARY_CONDITION
    mirror: Task008Condition = MIRROR_CONDITION

    def __post_init__(self) -> None:
        if not self.sugar_left.candidate_body_ids:
            raise ValueError("Task 008 is blocked: no defensible left sugar population")
        if self.primary.input_population != "sugar_left":
            raise ValueError("primary condition must use sugar_left")
        if self.primary.contralateral_mn9 != MN9_R or self.primary.ipsilateral_mn9 != MN9_L:
            raise ValueError("primary readout assignment violates the Task 007b laterality gate")
        if self.mirror.input_population != "sugar_right":
            raise ValueError("mirror condition must use sugar_right")
        if self.mirror.contralateral_mn9 != MN9_L or self.mirror.ipsilateral_mn9 != MN9_R:
            raise ValueError("mirror readout assignment is invalid")

    @property
    def fingerprint(self) -> str:
        payload = {
            "primary": asdict(self.primary),
            "mirror": asdict(self.mirror),
            "left": asdict(self.sugar_left),
            "right": asdict(self.sugar_right),
        }
        return _digest("malecns-sim-task008-experiment-v1", payload)


def _digest(prefix: str, payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(prefix.encode() + b"\0" + encoded).hexdigest()


def derive_task008_populations(
    candidates: Iterable[MaleCNSCandidate], *, enforce_task007_right: bool = True
) -> PreparedTask008:
    """Apply the Task 007 predicate on each explicit anatomical side."""

    candidates = tuple(candidates)
    sugar_candidates = tuple(item for item in candidates if item.flywire_type == "LB3")
    left = derive_sugar_population(sugar_candidates, side="L", side_field="root_side")
    right = derive_sugar_population(sugar_candidates, side="R", side_field="root_side")
    if enforce_task007_right and population_fingerprint(right) != TASK007_RIGHT_POPULATION_FINGERPRINT:
        raise ValueError("Task 007 right sugar population changed unexpectedly")
    return PreparedTask008(candidates, left, right)


def _counts(values: Iterable[str | None]) -> tuple[tuple[str, int], ...]:
    values = (value if value is not None else "<missing>" for value in values)
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return tuple(sorted(counts.items()))


def population_report(
    name: str,
    population: SugarPopulation,
    candidates: Iterable[MaleCNSCandidate],
    signed_connectome: SignedAnatomicalConnectome | None = None,
) -> PopulationReport:
    by_id = {item.body_id: item for item in candidates}
    selected = tuple(by_id[item] for item in population.candidate_body_ids)
    sensory = (
        ("receptorType", _counts(item.receptor_type for item in selected)),
        ("entryNerve", _counts(item.entry_nerve for item in selected)),
        ("somaNeuromere", _counts(item.soma_neuromere for item in selected)),
        ("dimorphism", _counts(item.dimorphism for item in selected)),
    )
    report = PopulationReport(
        name=name,
        body_ids=population.candidate_body_ids,
        count=len(selected),
        type_counts=_counts(item.type for item in selected),
        flywire_type_counts=_counts(item.flywire_type for item in selected),
        soma_side_counts=_counts(item.soma_side for item in selected),
        root_side_counts=_counts(item.root_side for item in selected),
        superclass_counts=_counts(item.superclass for item in selected),
        class_counts=_counts(item.cell_class for item in selected),
        sensory_metadata=sensory,
        resolved_nt_count=sum(item.resolved_nt is not None for item in selected),
        unresolved_nt_count=sum(item.resolved_nt is None for item in selected),
        fingerprint=population_fingerprint(population),
    )
    if signed_connectome is None:
        return report
    ids = np.asarray([int(item) for item in population.candidate_body_ids], dtype=np.int64)
    source_mask = np.isin(signed_connectome.connectome.source_ids, ids)
    assigned = source_mask & signed_connectome.signed_edge_mask
    unresolved = source_mask & ~signed_connectome.signed_edge_mask
    weights = signed_connectome.anatomical_weights
    return PopulationReport(
        **{
            **asdict(report),
            "resolved_outgoing_edge_count": int(assigned.sum()),
            "unresolved_outgoing_edge_count": int(unresolved.sum()),
            "resolved_outgoing_anatomical_weight": int(weights[assigned].sum(dtype=np.int64)),
            "unresolved_outgoing_anatomical_weight": int(weights[unresolved].sum(dtype=np.int64)),
            "total_outgoing_anatomical_weight": int(weights[source_mask].sum(dtype=np.int64)),
        }
    )


def deterministic_seed(
    experiment_identity: str,
    side: str,
    frequency_hz: float,
    trial_index: int,
    graph_fingerprint: str,
    sign_policy_fingerprint: str,
) -> int:
    """Derive a stable NumPy seed from every stochastic identity component."""

    payload = [experiment_identity, side, float(frequency_hz), int(trial_index), graph_fingerprint, sign_policy_fingerprint]
    digest = hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).digest()
    return int.from_bytes(digest[:8], "little", signed=False) & 0x7FFFFFFF


def normalized_rate(reference_rate_hz: float, population_count: int) -> float:
    if population_count <= 0:
        raise ValueError("population_count must be positive")
    return float(reference_rate_hz) * REFERENCE_SUGAR_COUNT / population_count


def run_trial(
    prepared: PreparedNetwork,
    condition: Task008Condition,
    population: SugarPopulation,
    *,
    frequency_hz: float,
    trial_index: int,
    experiment_identity: str,
    side: str,
    duration_ms: float = DURATION_MS,
    parameters: LIFParameters = LIFParameters(),
) -> TrialObservation:
    if condition.input_population == "sugar_right" and side != "R":
        raise ValueError("mirror condition side must be R")
    if condition.input_population == "sugar_left" and side != "L":
        raise ValueError("primary condition side must be L")
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
    )
    explicit = stimulus.generate(duration_ms, DT_MS, parameters.synaptic_weight_per_anatomical_synapse_mV)
    if prepared.cuda_graph is None:
        result = simulate_lif_active(
            prepared.projection,
            duration_ms=duration_ms,
            stimulus=explicit,
            parameters=parameters,
            dt_ms=DT_MS,
        )
    else:
        from malecns_sim.dynamics.cuda import simulate_cuda

        result = simulate_cuda(
            prepared.projection,
            duration_ms=duration_ms,
            stimulus=explicit,
            parameters=parameters,
            dt_ms=DT_MS,
            cuda_graph=prepared.cuda_graph,
        )
    counts = dict(zip(prepared.projection.neuron_ids.tolist(), result.spike_counts.tolist()))
    input_events = sum(len(item.spike_times_ms) for item in explicit.schedules)
    return TrialObservation(
        frequency_hz=float(frequency_hz),
        trial_index=int(trial_index),
        seed=seed,
        contralateral_spikes=int(counts.get(int(condition.contralateral_mn9), 0)),
        ipsilateral_spikes=int(counts.get(int(condition.ipsilateral_mn9), 0)),
        total_network_spikes=int(result.emitted_spike_count),
        active_neuron_count=int(result.active_neuron_count),
        sugar_input_events=int(input_events),
        queued_synaptic_events=int(result.queued_synaptic_event_count),
        delivered_synaptic_events=int(result.delivered_synaptic_event_count),
        result_digest=result.spike_result_digest,
        duration_ms=float(duration_ms),
    )


def summarize_trials(condition: str, trials: Sequence[TrialObservation]) -> ConditionSummary:
    if not trials:
        raise ValueError("at least one trial is required")
    durations = np.asarray([item.duration_ms for item in trials], dtype=np.float64)
    contra = np.asarray([item.contralateral_spikes for item in trials], dtype=np.float64) * 1000.0 / durations
    ipsi = np.asarray([item.ipsilateral_spikes for item in trials], dtype=np.float64) * 1000.0 / durations
    total = np.asarray([item.total_network_spikes for item in trials], dtype=np.float64) * 1000.0 / durations
    active = np.asarray([item.active_neuron_count for item in trials], dtype=np.float64)
    inputs = np.asarray([item.sugar_input_events for item in trials], dtype=np.float64)
    delivered = np.asarray([item.delivered_synaptic_events for item in trials], dtype=np.float64)
    deterministic_trials = []
    for item in trials:
        record = asdict(item)
        record.pop("runtime_seconds", None)
        deterministic_trials.append(record)
    digest = _digest("malecns-sim-task008-trials-v1", deterministic_trials)
    frequency = float(trials[0].frequency_hz)
    return ConditionSummary(
        condition=condition,
        frequency_hz=frequency,
        trial_count=len(trials),
        contralateral_mean_hz=float(contra.mean()),
        contralateral_std_hz=float(contra.std(ddof=1)) if len(contra) > 1 else 0.0,
        contralateral_active_fraction=float(np.mean(contra > 0.0)),
        ipsilateral_mean_hz=float(ipsi.mean()),
        ipsilateral_std_hz=float(ipsi.std(ddof=1)) if len(ipsi) > 1 else 0.0,
        ipsilateral_active_fraction=float(np.mean(ipsi > 0.0)),
        contra_minus_ipsi_hz=float(contra.mean() - ipsi.mean()),
        total_network_mean_hz=float(total.mean()),
        total_network_std_hz=float(total.std(ddof=1)) if len(total) > 1 else 0.0,
        active_neuron_mean=float(active.mean()),
        sugar_input_events_mean=float(inputs.mean()),
        delivered_synaptic_events_mean=float(delivered.mean()),
        result_digest=digest,
    )


def run_condition_trials(
    prepared: PreparedNetwork,
    condition: Task008Condition,
    population: SugarPopulation,
    frequencies_hz: Sequence[float],
    *,
    trial_count: int = TRIAL_COUNT,
    experiment_identity: str,
    side: str,
    rate_multiplier: float = 1.0,
    batch_size: int = TRIAL_COUNT,
) -> tuple[tuple[ConditionSummary, ...], tuple[TrialObservation, ...], float]:
    """Run fixed-seed trials while reusing one prepared network.

    A CUDA-backed network runs each frequency as one batch. The default batch
    size is the Task 008 requirement of 30 trials.
    """

    if trial_count <= 0:
        raise ValueError("trial_count must be positive")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if prepared.cuda_graph is not None and batch_size != trial_count:
        raise ValueError("CUDA Task 008 conditions must use one batch of all trials")
    started = time.perf_counter()
    all_trials: list[TrialObservation] = []
    summaries: list[ConditionSummary] = []
    for frequency in frequencies_hz:
        effective_frequency = float(frequency) * rate_multiplier
        prepared_inputs = []
        for trial_index in range(trial_count):
            seed = deterministic_seed(
                experiment_identity,
                side,
                effective_frequency,
                trial_index,
                prepared.fingerprint,
                prepared.signed_connectome.sign_policy_id,
            )
            stimulus = PoissonStimulus(
                tuple(int(item) for item in population.candidate_body_ids),
                rate_hz=effective_frequency,
                seed=seed,
            )
            explicit = stimulus.generate(DURATION_MS, DT_MS, LIFParameters().synaptic_weight_per_anatomical_synapse_mV)
            prepared_inputs.append((trial_index, seed, explicit))
        simulation_started = time.perf_counter()
        if prepared.cuda_graph is not None:
            from malecns_sim.dynamics.cuda import simulate_cuda_batch

            results = simulate_cuda_batch(
                prepared.projection,
                tuple(item[2] for item in prepared_inputs),
                duration_ms=DURATION_MS,
                parameters=LIFParameters(),
                dt_ms=DT_MS,
                cuda_graph=prepared.cuda_graph,
            )
        else:
            results = tuple(
                simulate_lif_active(
                    prepared.projection,
                    duration_ms=DURATION_MS,
                    stimulus=item[2],
                    parameters=LIFParameters(),
                    dt_ms=DT_MS,
                )
                for item in prepared_inputs
            )
        batch_runtime = time.perf_counter() - simulation_started
        trials = []
        for (trial_index, seed, explicit), result in zip(prepared_inputs, results):
            counts = dict(zip(prepared.projection.neuron_ids.tolist(), result.spike_counts.tolist()))
            trials.append(
                TrialObservation(
                    frequency_hz=effective_frequency,
                    trial_index=trial_index,
                    seed=seed,
                    contralateral_spikes=int(counts.get(int(condition.contralateral_mn9), 0)),
                    ipsilateral_spikes=int(counts.get(int(condition.ipsilateral_mn9), 0)),
                    total_network_spikes=int(result.emitted_spike_count),
                    active_neuron_count=int(result.active_neuron_count),
                    sugar_input_events=sum(len(item.spike_times_ms) for item in explicit.schedules),
                    queued_synaptic_events=int(result.queued_synaptic_event_count),
                    delivered_synaptic_events=int(result.delivered_synaptic_event_count),
                    result_digest=result.spike_result_digest,
                    duration_ms=DURATION_MS,
                    runtime_seconds=batch_runtime / len(results),
                )
            )
        all_trials.extend(trials)
        summaries.append(summarize_trials(condition.name, trials))
    return tuple(summaries), tuple(all_trials), time.perf_counter() - started


def spearman_rank_association(values: Sequence[float], reference: Sequence[float]) -> float:
    if len(values) != len(reference):
        raise ValueError("curves must have equal length")
    left = np.argsort(np.argsort(np.asarray(values, dtype=float), kind="stable"), kind="stable")
    right = np.argsort(np.argsort(np.asarray(reference, dtype=float), kind="stable"), kind="stable")
    if len(values) < 2:
        return 1.0
    return float(np.corrcoef(left, right)[0, 1])


def prepare_network(
    annotation_path: str | Path,
    neurotransmitter_path: str | Path,
    weights_path: str | Path,
    *,
    graph_name: str = "full",
    min_synapses: int = 0,
    cache_path: str | Path | None = None,
    use_cuda: bool = False,
) -> PreparedNetwork:
    """Load, curate, sign, and project once for immutable trial reuse."""

    import pyarrow.feather as feather

    start = time.perf_counter()
    numeric = load_male_cns_v1_numeric(
        annotation_path, neurotransmitter_path, weights_path, official_v1_mapping()
    )
    loaded = time.perf_counter()
    annotations = feather.read_table(annotation_path, columns=list(MALE_CNS_ANNOTATION_COLUMNS)).to_pylist()
    evidence = load_male_cns_v1_neurotransmitter_evidence(
        annotation_path, neurotransmitter_path, official_v1_mapping(), curated_only=True
    )
    selection = select_publication_neuron_ids(annotations)
    projection = project_numeric_connectome(numeric, selection.neuron_ids)
    if min_synapses:
        projection = threshold_curated_projection(projection, min_synapses=min_synapses)
    signed = SignedAnatomicalConnectome.from_projection(
        projection, evidence, NeurotransmitterResolutionPolicy(), Shiu2024SignPolicy()
    )
    prepared_projection = EffectiveSignedProjection.from_signed_connectome(signed)
    cache = None
    cache_target = Path(cache_path) if cache_path is not None else None
    if cache_target is not None:
        if cache_target.exists():
            expected = PreparedGraphCache.from_projection(
                prepared_projection,
                male_cns_release_identity="MaleCNS-v1.0",
                min_synapses=min_synapses,
            )
            cache = PreparedGraphCache.load(cache_target, expected_identity=expected.identity)
        else:
            cache = PreparedGraphCache.from_projection(
                prepared_projection,
                male_cns_release_identity="MaleCNS-v1.0",
                min_synapses=min_synapses,
            )
            cache.save(cache_target)
        prepared_projection = cache.to_projection()
    cuda_graph = None
    if use_cuda:
        from malecns_sim.dynamics.cuda import cuda_available, upload_graph

        if not cuda_available():
            raise RuntimeError("Task 008 requires an available CUDA device")
        cuda_graph, _ = upload_graph(prepared_projection)
    prepared = time.perf_counter()
    memory = sum(
        int(getattr(prepared_projection, field).nbytes)
        for field in ("neuron_ids", "source_positions", "target_positions", "effective_weights_mV", "outgoing_indptr", "outgoing_targets", "outgoing_weights_mV")
    )
    return PreparedNetwork(
        projection=prepared_projection,
        signed_connectome=signed,
        graph_name=graph_name,
        preparation_seconds=prepared - loaded,
        graph_loading_seconds=loaded - start,
        setup_seconds=prepared - start,
        memory_bytes=memory,
        fingerprint=_digest(
            "malecns-sim-task008-prepared-network-v1",
            {
                "graph": graph_name,
                "unsigned": signed.unsigned_graph_fingerprint,
                "signed": signed_graph_fingerprint(signed),
                "effective": prepared_projection.fingerprint,
            },
        ),
        cache_path=str(cache_target) if cache_target is not None else None,
        cache_fingerprint=cache.cache_fingerprint if cache is not None else None,
        cuda_graph=cuda_graph,
    )


def run_cpu_gpu_preflight(
    prepared: PreparedNetwork,
    population: SugarPopulation,
    *,
    experiment_identity: str,
    side: str,
    frequency_hz: float = 100.0,
    trial_count: int = 2,
    duration_ms: float = 20.0,
) -> dict[str, object]:
    """Require exact CPU/GPU equality for short, pre-generated schedules."""

    if prepared.cuda_graph is None:
        raise RuntimeError("Task 008 preflight requires a CUDA graph")
    parameters = LIFParameters()
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
        schedules.append(
            PoissonStimulus(tuple(int(item) for item in population.candidate_body_ids), rate_hz=frequency_hz, seed=seed).generate(
                duration_ms,
                DT_MS,
                parameters.synaptic_weight_per_anatomical_synapse_mV,
            )
        )
    cpu_results = tuple(
        simulate_lif_active(
            prepared.projection,
            duration_ms=duration_ms,
            stimulus=stimulus,
            parameters=parameters,
            dt_ms=DT_MS,
        )
        for stimulus in schedules
    )
    from malecns_sim.dynamics.cuda import simulate_cuda_batch

    gpu_results = simulate_cuda_batch(
        prepared.projection,
        tuple(schedules),
        duration_ms=duration_ms,
        parameters=parameters,
        dt_ms=DT_MS,
        cuda_graph=prepared.cuda_graph,
    )
    for cpu, gpu in zip(cpu_results, gpu_results):
        if not (
            np.array_equal(cpu.spike_neuron_ids, gpu.spike_neuron_ids)
            and np.array_equal(cpu.spike_timesteps, gpu.spike_timesteps)
            and np.array_equal(cpu.spike_counts, gpu.spike_counts)
            and cpu.spike_result_digest == gpu.spike_result_digest
        ):
            raise AssertionError("Task 008 CPU/GPU preflight canonical spike-event mismatch")
    return {
        "backend": "cuda-float64",
        "trial_count": trial_count,
        "duration_ms": duration_ms,
        "frequency_hz": frequency_hz,
        "canonical_spike_event_equal": True,
        "digests": [item.spike_result_digest for item in gpu_results],
        "total_spike_counts": [item.emitted_spike_count for item in gpu_results],
    }


def load_task008_identities(annotation_path: str | Path, neurotransmitter_path: str | Path) -> PreparedTask008:
    return derive_task008_populations(load_male_cns_candidates(annotation_path, neurotransmitter_path))


def memory_working_set_bytes() -> int | None:
    """Return the Windows process working set when the platform exposes it."""

    if os.name != "nt":
        return None
    import ctypes
    from ctypes import wintypes

    class _MemoryStatus(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("working_set_size", ctypes.c_size_t)]

    class _Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("page_fault_count", wintypes.DWORD), ("peak_working_set_size", ctypes.c_size_t), ("working_set_size", ctypes.c_size_t)]

    counters = _Counters()
    counters.cb = ctypes.sizeof(_Counters)
    if ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        return int(counters.working_set_size)
    return None
