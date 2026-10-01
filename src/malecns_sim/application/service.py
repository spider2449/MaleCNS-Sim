"""Thin orchestration of registered data and the existing simulation engines."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol
from uuid import uuid4

import numpy as np

from malecns_sim.analysis.task008 import load_task008_identities, prepare_network
from malecns_sim.dynamics.lif import SimulationResult, simulate_lif
from malecns_sim.dynamics.stimulus import ExplicitStimulus, PoissonStimulus, SpikeSchedule
from malecns_sim.homology import population_fingerprint

from .errors import ApplicationError, ErrorCode
from .events import EventType, ExecutionEvent, Lifecycle, State
from .models import DeliverySample, ExperimentResult, ExperimentSpec, RunIdentity, SelectedTrace, SpikeEvent, TrialResult


@dataclass(frozen=True, slots=True)
class DatasetFiles:
    annotation: Path
    neurotransmitter: Path
    weights: Path
    manifest_digest: str
    mapping_fingerprint: str


class EngineAdapter(Protocol):
    def identities(self, files: DatasetFiles): ...
    def prepare(self, files: DatasetFiles, backend: str): ...
    def simulate(self, prepared, spec: ExperimentSpec, stimulus: ExplicitStimulus) -> SimulationResult: ...
    def cuda_available(self) -> bool: ...


class ProductionEngine:
    def identities(self, files: DatasetFiles):
        return load_task008_identities(files.annotation, files.neurotransmitter)

    def prepare(self, files: DatasetFiles, backend: str):
        return prepare_network(files.annotation, files.neurotransmitter, files.weights, use_cuda=backend == "cuda")

    def cuda_available(self) -> bool:
        from malecns_sim.dynamics.cuda import cuda_available
        return cuda_available()

    def simulate(self, prepared, spec: ExperimentSpec, stimulus: ExplicitStimulus) -> SimulationResult:
        kwargs = dict(duration_ms=spec.duration_ms, stimulus=stimulus, parameters=spec.model.parameters, dt_ms=spec.dt_ms, silenced_neuron_ids=spec.intervention.target_ids, trace_neuron_ids=spec.observables.trace_neuron_ids, collect_sparse_trace=spec.observables.delivery_trace)
        if spec.backend == "cuda":
            from malecns_sim.dynamics.cuda import simulate_cuda
            return simulate_cuda(prepared.projection, cuda_graph=prepared.cuda_graph, **kwargs)
        return simulate_lif(prepared.projection, **kwargs)


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_provenance() -> dict[str, str | bool | None]:
    try:
        source = Path(__file__).resolve()
        root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=source.parent, capture_output=True, text=True, timeout=2, check=True).stdout.strip()
        if not (Path(root) / "src" / "malecns_sim" / "application" / "service.py").samefile(source):
            return {"git_commit": None, "git_dirty": None}
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, timeout=2, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, timeout=2, check=True).stdout.strip())
        return {"git_commit": commit, "git_dirty": dirty}
    except (FileNotFoundError, subprocess.SubprocessError, OSError):
        return {"git_commit": None, "git_dirty": None}


def validate_experiment(spec: ExperimentSpec) -> ExperimentSpec:
    if not isinstance(spec, ExperimentSpec):
        raise ApplicationError(ErrorCode.INVALID_SPEC, "ExperimentSpec required")
    return spec


def _check_cancel(cancel_requested: Callable[[], bool] | None, lifecycle: Lifecycle, trial: int) -> None:
    if cancel_requested is not None and cancel_requested():
        lifecycle.transition(State.CANCELLED, payload={"completed_trials": trial})
        lifecycle.emit(EventType.RUN_CANCELLED, {"completed_trials": trial})
        raise ApplicationError(ErrorCode.CANCELLED, "cancelled at a trial boundary", lifecycle.state.value)


def _schedule(spec: ExperimentSpec, seed: int) -> ExplicitStimulus:
    # Generate only the active interval; shift the engine's explicit schedule to its requested start.
    active = spec.stimulus.end_ms - spec.stimulus.start_ms
    poisson = PoissonStimulus(spec.stimulus.member_ids, rate_hz=spec.stimulus.frequency_hz, seed=seed, weight_factor=spec.stimulus.weight_factor)
    generated = poisson.generate(active, spec.dt_ms, spec.model.parameters.synaptic_weight_per_anatomical_synapse_mV)
    schedules = tuple(SpikeSchedule(item.neuron_id, tuple(t + spec.stimulus.start_ms for t in item.spike_times_ms)) for item in generated.schedules)
    return ExplicitStimulus(schedules, generated.weight_mV, generated.refractory_free_neuron_ids)


def _trial(spec: ExperimentSpec, prepared, simulation: SimulationResult, schedule: ExplicitStimulus, index: int, seed: int) -> TrialResult:
    ids = prepared.projection.neuron_ids
    if (simulation.duration_ms != spec.duration_ms or simulation.dt_ms != spec.dt_ms or simulation.parameter_fingerprint != spec.model.fingerprint or simulation.unsigned_graph_fingerprint != prepared.projection.unsigned_graph_fingerprint or simulation.sign_policy_fingerprint != prepared.projection.signed_policy_fingerprint or simulation.stimulus_fingerprint != schedule.fingerprint):
        raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "engine result identity does not match executed inputs")
    if simulation.spike_neuron_ids.dtype.kind not in "iu" or simulation.spike_timesteps.dtype.kind not in "iu":
        raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "engine spike arrays must contain integers")
    spike_ids = tuple(int(i) for i in simulation.spike_neuron_ids)
    steps = tuple(int(i) for i in simulation.spike_timesteps)
    if len(spike_ids) != len(steps):
        raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "engine spike arrays differ in length")
    spikes = tuple(SpikeEvent(step, neuron) for step, neuron in zip(steps, spike_ids))
    if any(not 1 <= s.timestep <= round(spec.duration_ms / spec.dt_ms) for s in spikes):
        raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "spike timestep outside engine grid")
    known_ids = set(int(i) for i in ids)
    if any(s.neuron_id not in known_ids for s in spikes):
        raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "unknown spike neuron ID")
    position = int(np.searchsorted(ids, spec.target.neuron_id))
    count = int(simulation.spike_counts[position])
    traces: list[SelectedTrace] = []
    if simulation.trace_v_mV is not None and simulation.trace_g_mV is not None:
        for row, neuron in enumerate(simulation.trace_neuron_ids):
            traces.append(SelectedTrace(int(neuron), tuple(float(v) for v in simulation.trace_v_mV[row]), tuple(float(v) for v in simulation.trace_g_mV[row])))
    delivery: list[DeliverySample] = []
    sparse = simulation.sparse_trace
    if spec.observables.delivery_trace and sparse is None:
        raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "requested delivery trace missing from engine result")
    if sparse is not None:
        for values in zip(sparse.timesteps, sparse.delivered_event_counts, sparse.delivered_weight_sums_mV, sparse.delivered_abs_weight_sums_mV, sparse.delivered_target_counts, sparse.delivered_target_index_sums):
            delivery.append(DeliverySample(int(values[0]), int(values[1]), float(values[2]), float(values[3]), int(values[4]), int(values[5])))
    target_times = tuple(s.timestep for s in spikes if s.neuron_id == spec.target.neuron_id)
    if len(target_times) != count:
        raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "engine target spike count mismatch")
    return TrialResult(index, seed, schedule.fingerprint, simulation.spike_result_digest, count, count * 1000.0 / spec.duration_ms, target_times, spikes, tuple(traces), tuple(delivery))


def run_experiment(spec: ExperimentSpec, files: DatasetFiles, *, event_sink: Callable[[ExecutionEvent], None] | None = None, cancel_requested: Callable[[], bool] | None = None, engine: EngineAdapter | None = None) -> ExperimentResult:
    """Execute bounded trials; cancellation is checked before and after each opaque engine call."""
    engine = engine or ProductionEngine()
    invocation = str(uuid4())
    started = datetime.now(timezone.utc).isoformat()
    schedules = tuple(_schedule(spec, seed) for seed in spec.seed_policy.trial_seeds)
    identity = RunIdentity.create(spec, tuple(s.fingerprint for s in schedules), spec.dataset.projection_fingerprint)
    lifecycle = Lifecycle(identity.run_id, invocation, event_sink)
    lifecycle.emit(EventType.RUN_STARTED, {"backend": spec.backend})
    phase = State.CREATED
    completed: list[TrialResult] = []

    def partial_result(error: ApplicationError, status: str) -> ExperimentResult:
        return ExperimentResult.create(
            identity=identity, spec=spec, invocation_id=invocation, started_at=started,
            finished_at=datetime.now(timezone.utc).isoformat(), status=status,
            error=error.to_dict(), provenance={"dataset": spec.to_dict()["dataset"], **_git_provenance(), "engine_version": identity.package_version},
            stimulus_summary={"schedule_fingerprints": identity.schedule_fingerprints, "side": spec.stimulus.side, "frequency_hz": spec.stimulus.frequency_hz},
            intervention_summary={"kind": spec.intervention.kind, "target_ids": spec.intervention.target_ids},
            trials=tuple(completed),
        )

    try:
        lifecycle.transition(State.VALIDATING)
        phase = lifecycle.state
        validate_experiment(spec)
        if spec.robustness.kind != "none":
            raise ApplicationError(ErrorCode.UNSUPPORTED_OPERATION, "robustness execution is reserved for A007", phase.value)
        if spec.backend == "cuda" and not engine.cuda_available():
            raise ApplicationError(ErrorCode.GPU_UNAVAILABLE, "CUDA backend is unavailable", phase.value)
        _check_cancel(cancel_requested, lifecycle, 0)
        lifecycle.transition(State.LOADING_DATA)
        phase = lifecycle.state
        if files.manifest_digest != spec.dataset.manifest_digest or files.mapping_fingerprint != spec.dataset.mapping_fingerprint:
            raise ApplicationError(ErrorCode.DATASET_PROVENANCE, "registered dataset metadata mismatch", phase.value)
        for path, expected in ((files.annotation, spec.dataset.annotation_sha256), (files.neurotransmitter, spec.dataset.neurotransmitter_sha256), (files.weights, spec.dataset.weights_sha256)):
            if _file_digest(path) != expected:
                raise ApplicationError(ErrorCode.DATASET_PROVENANCE, "registered source file digest mismatch", phase.value)
        identities = engine.identities(files)
        population = identities.sugar_left if spec.stimulus.side == "L" else identities.sugar_right
        if population_fingerprint(population) != spec.stimulus.population_fingerprint or tuple(int(i) for i in population.candidate_body_ids) != spec.stimulus.member_ids:
            raise ApplicationError(ErrorCode.DATASET_PROVENANCE, "sugar population identity mismatch", phase.value)
        _check_cancel(cancel_requested, lifecycle, 0)
        lifecycle.transition(State.PREPARING_NETWORK)
        phase = lifecycle.state
        prepared = engine.prepare(files, spec.backend)
        projection = prepared.projection
        if projection.unsigned_graph_fingerprint != spec.dataset.projection_fingerprint:
            raise ApplicationError(ErrorCode.DATASET_PROVENANCE, "curated projection fingerprint mismatch", phase.value)
        if projection.sign_policy_id != spec.sign_policy.policy_id or projection.resolution_policy_id != spec.sign_policy.resolution_id:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "sign policy does not match prepared graph", phase.value)
        graph_ids = set(int(i) for i in projection.neuron_ids)
        if not set(spec.stimulus.member_ids).issubset(graph_ids) or spec.target.neuron_id not in graph_ids or not set(spec.intervention.target_ids).issubset(graph_ids) or not set(spec.observables.trace_neuron_ids).issubset(graph_ids):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "requested neuron absent from curated graph", phase.value)
        _check_cancel(cancel_requested, lifecycle, 0)
        lifecycle.transition(State.RUNNING, payload={"total_trials": spec.trial_count})
        phase = lifecycle.state
        for index, (seed, schedule) in enumerate(zip(spec.seed_policy.trial_seeds, schedules)):
            _check_cancel(cancel_requested, lifecycle, len(completed))
            lifecycle.emit(EventType.TRIAL_STARTED, {"trial_index": index, "total_trials": spec.trial_count})
            simulation = engine.simulate(prepared, spec, schedule)
            trial = _trial(spec, prepared, simulation, schedule, index, seed)
            completed.append(trial)
            lifecycle.emit(EventType.TRIAL_COMPLETED, {"trial_index": index, "completed_trials": len(completed), "total_trials": spec.trial_count, "engine_digest": trial.engine_digest})
            _check_cancel(cancel_requested, lifecycle, len(completed))
        lifecycle.transition(State.FINALIZING)
        phase = lifecycle.state
        result = ExperimentResult.create(identity=identity, spec=spec, invocation_id=invocation, started_at=started, finished_at=datetime.now(timezone.utc).isoformat(), provenance={"dataset": spec.to_dict()["dataset"], **_git_provenance(), "engine_version": identity.package_version, "graph_fingerprint": projection.fingerprint, "prepared_neuron_count": len(projection.neuron_ids), "prepared_edge_count": len(projection.source_positions)}, stimulus_summary={"schedule_fingerprints": identity.schedule_fingerprints, "side": spec.stimulus.side, "frequency_hz": spec.stimulus.frequency_hz, "member_count": len(spec.stimulus.member_ids)}, intervention_summary={"kind": spec.intervention.kind, "target_ids": spec.intervention.target_ids, "semantics": "suppress outgoing scheduling" if spec.intervention.kind == "outgoing_silence" else "none"}, trials=tuple(completed))
        lifecycle.transition(State.COMPLETED)
        lifecycle.emit(EventType.RUN_COMPLETED, {"result_digest": result.authoritative_digest, "completed_trials": len(completed)})
        return result
    except ApplicationError as exc:
        if exc.phase is None:
            exc.phase = lifecycle.state.value
        if lifecycle.state != State.CANCELLED and lifecycle.state not in (State.COMPLETED, State.FAILED):
            lifecycle.transition(State.FAILED, payload={"code": exc.code.value, "completed_trials": len(completed)})
            lifecycle.emit(EventType.RUN_FAILED, {"error": exc.to_dict(), "completed_trials": len(completed)})
        exc.partial_result = partial_result(exc, "CANCELLED" if lifecycle.state == State.CANCELLED else "FAILED")
        raise
    except Exception as exc:
        code = ErrorCode.DATASET_PROVENANCE if phase == State.LOADING_DATA else ErrorCode.PREPARATION_FAILED if phase == State.PREPARING_NETWORK else ErrorCode.RESULT_SERIALIZATION if phase == State.FINALIZING else ErrorCode.SIMULATION_FAILED
        error = ApplicationError(code, f"{phase.value} failed", phase.value)
        lifecycle.transition(State.FAILED, payload={"code": code.value, "completed_trials": len(completed)})
        lifecycle.emit(EventType.RUN_FAILED, {"error": error.to_dict(), "completed_trials": len(completed)})
        error.partial_result = partial_result(error, "FAILED")
        raise error from exc
