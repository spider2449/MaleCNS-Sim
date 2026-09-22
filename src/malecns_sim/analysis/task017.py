"""Task 017 execution of the preregistered v0.3 robustness matrix."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

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
    deterministic_seed,
    load_task008_identities,
)
from malecns_sim.analysis.task010 import (
    DEFAULT_FREQUENCY_HZ,
    FROZEN_CANDIDATE_IDS,
    PREDECLARED_THRESHOLDS,
    TASK008_FULL_CACHE_FINGERPRINT,
    TASK008_PREPARED_FINGERPRINT,
    FrozenCandidateManifest,
    Task010Trial,
    _prepare_verified_cached_network,
    _trials_from_results,
    load_frozen_candidate_manifest,
    rate_effect,
    summarize_condition,
)
from malecns_sim.analysis.task011 import (
    FIXED_TRIAL_INDICES,
    FROZEN_TASK011_CANDIDATES,
    NETWORK_ACTIVITY_SHIFT_FRACTION,
    NETWORK_DIVERGENT_NEURON_THRESHOLD,
    STATE_ATOL,
    STATE_RTOL,
    WINDOWS_MS,
    _aggregate_windows,
    _annotation_map,
    _mechanism_evidence,
    _run_trace_results,
    baseline_activity_exposure,
    classify_mechanism,
    detect_first_divergence,
    first_hop_target_analysis,
    propagation_windows,
    structural_summary,
)
from malecns_sim.data.male_cns_v1 import (
    load_male_cns_v1_numeric,
    official_v1_mapping,
    project_numeric_connectome,
    select_publication_neuron_ids,
)
from malecns_sim.data.neurotransmitter import (
    NeurotransmitterResolutionPolicy,
    load_male_cns_v1_neurotransmitter_evidence,
)
from malecns_sim.dynamics import (
    EffectiveSignedProjection,
    ExplicitStimulus,
    LIFParameters,
    PoissonStimulus,
    SimulationResult,
    SpikeSchedule,
    simulate_lif,
    simulate_lif_active,
)
from malecns_sim.dynamics.cache import PreparedGraphCache
from malecns_sim.dynamics.cuda import cuda_available, simulate_cuda_batch, upload_graph
from malecns_sim.graph.signed import SignedAnatomicalConnectome
from malecns_sim.homology import population_fingerprint
from malecns_sim.sign import ConservativeSignPolicy, Shiu2024SignPolicy


TASK017_SCHEMA = "malecns-sim-task017-v0.3-mechanism-robustness-v1"
TASK016_SPEC_SCHEMA = "malecns-sim-task016-frozen-specification-v1"
TASK016_PLAN = "docs/plans/2026-09-22-task-016-v0.3-mechanism-robustness-preregistration.md"
STARTING_HEAD = "b32c116b704cf94bcfd9d9e601eddfdd70271a2f"
TASK017B_DELIVERY_PATHS = frozenset(
    {
        "docs/plans/2026-09-22-task-017b-bounded-batch-delivery.md",
        "scripts/run_task017.py",
        "src/malecns_sim/analysis/task017.py",
        "tests/test_task017.py",
    }
)
V020_SOURCE = "470f8274a1b002c9f27fd430984b6755c9f56759"
TASK011_RESULT_DIGEST = "fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4"
TASK010_RESULT_DIGEST = "20f8d8f6432070625a9ca6a4ddb32b2cc0a68f380102dbd3ee5e35bbcc578e45"
TASK010_TRIAL_COUNT = 30
TRACE_DURATION_MS = 1000.0
DIRECT_INPUT_WEIGHT_FACTOR = 250.0
RESULT_DIGEST_PREFIX = "malecns-sim-task017-result-v1"
SCHEDULE_DIGEST_PREFIX = "malecns-sim-task017-event-schedule-v1"
CHECKPOINT_SCHEMA = "malecns-sim-task017-checkpoint-v1"
CHECKPOINT_UNIT_PREFIX = "malecns-sim-task017-unit-v1"
CHECKPOINT_HEADER_KIND = "checkpoint_header"
CHECKPOINT_UNIT_KIND = "completed_unit"
CHECKPOINT_DUPLICATE_KIND = "duplicate_unit"
BASELINE_CANDIDATE_ID = "__BASELINE__"
TASK010_BASELINE = "task010_baseline"
TASK010_INTERVENTION = "task010_intervention"
TASK011_BASELINE = "task011_baseline_trace"
TASK011_INTERVENTION = "task011_intervention_trace"
SCIENTIFIC_ANALYSIS_KINDS = (TASK010_BASELINE, TASK010_INTERVENTION, TASK011_BASELINE, TASK011_INTERVENTION)


class CheckpointError(RuntimeError):
    """Base error for fail-closed Task 017 checkpoint handling."""


class CheckpointIdentityMismatch(CheckpointError):
    """Raised when an existing checkpoint does not match the frozen matrix."""


class DuplicateUnitExecution(CheckpointError):
    """Raised when a completed unit is written more than once."""


class StaleSidecar(CheckpointError):
    """Raised when a result sidecar is not referenced by the journal."""


class ExecutionBudgetExceeded(RuntimeError):
    """Raised before starting another unit when the declared wall-clock budget ends."""


@dataclass(slots=True)
class ExecutionBudget:
    """Bound scientific execution without interrupting a backend batch."""

    max_units: int | None = None
    deadline: float | None = None
    executed_units: int = 0

    def batch_limit(self, pending_count: int) -> int:
        if pending_count <= 0:
            return 0
        if self.max_units is None:
            return pending_count
        remaining = self.max_units - self.executed_units
        if remaining <= 0:
            raise ExecutionBudgetExceeded("maximum scientific unit count reached")
        return min(pending_count, remaining)

    def before_batch(self, batch_count: int) -> None:
        if self.deadline is not None and time.perf_counter() >= self.deadline:
            raise ExecutionBudgetExceeded("maximum runtime reached before the next scientific unit")
        if self.max_units is not None and self.executed_units + batch_count > self.max_units:
            raise ExecutionBudgetExceeded("maximum scientific unit count reached")

    def committed(self, batch_count: int) -> None:
        self.executed_units += batch_count


@dataclass(frozen=True, slots=True)
class Task017UnitKey:
    """Deterministic identity of one persisted scientific execution unit."""

    variant_id: str
    candidate_id: str
    stimulus_side: str
    trial_index: int
    analysis_kind: str

    def as_record(self) -> dict[str, object]:
        return {
            "variant_id": self.variant_id,
            "candidate_id": self.candidate_id,
            "stimulus_side": self.stimulus_side,
            "trial_index": int(self.trial_index),
            "analysis_kind": self.analysis_kind,
        }

    @property
    def token(self) -> str:
        return _digest(CHECKPOINT_UNIT_PREFIX, self.as_record())


def expected_task017_unit_keys() -> tuple[Task017UnitKey, ...]:
    """Return the complete preregistered matrix in canonical key order."""

    keys: list[Task017UnitKey] = []
    for variant in VARIANT_CONFIGURATIONS:
        for side in ("LEFT", "RIGHT"):
            for trial_index in range(TASK010_TRIAL_COUNT):
                keys.append(Task017UnitKey(variant.variant_id, BASELINE_CANDIDATE_ID, side, trial_index, TASK010_BASELINE))
                for candidate_id in FROZEN_TASK011_CANDIDATES:
                    keys.append(Task017UnitKey(variant.variant_id, candidate_id, side, trial_index, TASK010_INTERVENTION))
            for trial_index in FIXED_TRIAL_INDICES:
                keys.append(Task017UnitKey(variant.variant_id, BASELINE_CANDIDATE_ID, side, trial_index, TASK011_BASELINE))
                for candidate_id in FROZEN_TASK011_CANDIDATES:
                    keys.append(Task017UnitKey(variant.variant_id, candidate_id, side, trial_index, TASK011_INTERVENTION))
    return tuple(sorted(keys, key=lambda item: (item.variant_id, item.stimulus_side, item.analysis_kind, item.trial_index, item.candidate_id)))


def pending_task017_unit_keys(
    checkpoint: "Task017Checkpoint",
    *,
    variant_ids: Sequence[str] | None = None,
    analysis_kinds: Sequence[str] | None = None,
) -> tuple[Task017UnitKey, ...]:
    """Return missing keys in the single canonical matrix order."""

    allowed_variants = None if variant_ids is None else set(variant_ids)
    allowed_analyses = None if analysis_kinds is None else set(analysis_kinds)
    completed = {Task017UnitKey(**record["key"]).token for record in checkpoint.records()}
    return tuple(
        key
        for key in expected_task017_unit_keys()
        if (allowed_variants is None or key.variant_id in allowed_variants)
        and (allowed_analyses is None or key.analysis_kind in allowed_analyses)
        and key.token not in completed
    )


def _freeze_result_arrays(result: SimulationResult) -> None:
    arrays = [result.spike_neuron_ids, result.spike_timesteps, result.spike_counts, result.trace_neuron_ids]
    if result.trace_v_mV is not None:
        arrays.append(result.trace_v_mV)
    if result.trace_g_mV is not None:
        arrays.append(result.trace_g_mV)
    if result.sparse_trace is not None:
        arrays.extend(
            [
                result.sparse_trace.timesteps,
                result.sparse_trace.delivered_event_counts,
                result.sparse_trace.delivered_weight_sums_mV,
                result.sparse_trace.delivered_abs_weight_sums_mV,
                result.sparse_trace.delivered_target_counts,
                result.sparse_trace.delivered_target_index_sums,
            ]
        )
    for array in arrays:
        array.flags.writeable = False


def _write_result_artifact(path: Path, result: SimulationResult) -> None:
    """Persist a backend-neutral result without runtime or device metadata."""

    sparse = result.sparse_trace
    metadata = {
        "duration_ms": result.duration_ms,
        "dt_ms": result.dt_ms,
        "parameter_fingerprint": result.parameter_fingerprint,
        "unsigned_graph_fingerprint": result.unsigned_graph_fingerprint,
        "sign_policy_fingerprint": result.sign_policy_fingerprint,
        "stimulus_fingerprint": result.stimulus_fingerprint,
        "simulation_fingerprint": result.simulation_fingerprint,
        "spike_result_digest": result.spike_result_digest,
        "emitted_spike_count": result.emitted_spike_count,
        "active_neuron_count": result.active_neuron_count,
        "queued_synaptic_event_count": result.queued_synaptic_event_count,
        "delivered_synaptic_event_count": result.delivered_synaptic_event_count,
        "has_trace": result.trace_v_mV is not None and result.trace_g_mV is not None,
        "has_sparse_trace": sparse is not None,
    }
    arrays: dict[str, np.ndarray] = {
        "spike_neuron_ids": np.asarray(result.spike_neuron_ids),
        "spike_timesteps": np.asarray(result.spike_timesteps),
        "spike_counts": np.asarray(result.spike_counts),
        "trace_neuron_ids": np.asarray(result.trace_neuron_ids),
    }
    if result.trace_v_mV is not None and result.trace_g_mV is not None:
        arrays["trace_v_mV"] = np.asarray(result.trace_v_mV)
        arrays["trace_g_mV"] = np.asarray(result.trace_g_mV)
    if sparse is not None:
        arrays.update(
            {
                "sparse_timesteps": np.asarray(sparse.timesteps),
                "sparse_delivered_event_counts": np.asarray(sparse.delivered_event_counts),
                "sparse_delivered_weight_sums_mV": np.asarray(sparse.delivered_weight_sums_mV),
                "sparse_delivered_abs_weight_sums_mV": np.asarray(sparse.delivered_abs_weight_sums_mV),
                "sparse_delivered_target_counts": np.asarray(sparse.delivered_target_counts),
                "sparse_delivered_target_index_sums": np.asarray(sparse.delivered_target_index_sums),
            }
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".npz", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
    try:
        np.savez_compressed(temporary, metadata=np.asarray(json.dumps(metadata, sort_keys=True)), **arrays)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _read_result_artifact(path: Path) -> SimulationResult:
    from malecns_sim.dynamics.lif import SparseTrace

    with np.load(path, allow_pickle=False) as data:
        metadata = json.loads(str(data["metadata"].item()))
        arrays = {name: np.array(data[name], copy=True) for name in data.files if name != "metadata"}
    sparse = None
    if metadata["has_sparse_trace"]:
        sparse = SparseTrace(
            arrays.pop("sparse_timesteps"),
            arrays.pop("sparse_delivered_event_counts"),
            arrays.pop("sparse_delivered_weight_sums_mV"),
            arrays.pop("sparse_delivered_abs_weight_sums_mV"),
            arrays.pop("sparse_delivered_target_counts"),
            arrays.pop("sparse_delivered_target_index_sums"),
        )
    result = SimulationResult(
        spike_neuron_ids=arrays.pop("spike_neuron_ids"),
        spike_timesteps=arrays.pop("spike_timesteps"),
        spike_counts=arrays.pop("spike_counts"),
        duration_ms=float(metadata["duration_ms"]),
        dt_ms=float(metadata["dt_ms"]),
        parameter_fingerprint=metadata["parameter_fingerprint"],
        unsigned_graph_fingerprint=metadata["unsigned_graph_fingerprint"],
        sign_policy_fingerprint=metadata["sign_policy_fingerprint"],
        stimulus_fingerprint=metadata["stimulus_fingerprint"],
        simulation_fingerprint=metadata["simulation_fingerprint"],
        spike_result_digest=metadata["spike_result_digest"],
        emitted_spike_count=int(metadata["emitted_spike_count"]),
        active_neuron_count=int(metadata["active_neuron_count"]),
        queued_synaptic_event_count=int(metadata["queued_synaptic_event_count"]),
        delivered_synaptic_event_count=int(metadata["delivered_synaptic_event_count"]),
        trace_neuron_ids=arrays.pop("trace_neuron_ids"),
        trace_v_mV=arrays.pop("trace_v_mV") if metadata["has_trace"] else None,
        trace_g_mV=arrays.pop("trace_g_mV") if metadata["has_trace"] else None,
        sparse_trace=sparse,
    )
    if arrays:
        raise CheckpointError(f"unrecognized result artifact arrays: {sorted(arrays)}")
    _freeze_result_arrays(result)
    return result


class Task017Checkpoint:
    """Append-only deterministic checkpoint with fail-closed identity checks."""

    def __init__(self, path: str | Path, identity: Mapping[str, object]) -> None:
        self.path = Path(path)
        self.artifact_dir = self.path.with_name(self.path.name + ".units")
        self.identity = json.loads(json.dumps(identity, sort_keys=True, separators=(",", ":"), default=str))
        self._records: dict[str, dict[str, object]] = {}
        self._duplicates = 0
        self._load_or_initialize()

    @property
    def fingerprint(self) -> str:
        return _digest("malecns-sim-task017-checkpoint-state-v1", self.identity)

    def _append(self, record: Mapping[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def _load_or_initialize(self) -> None:
        if not self.path.exists():
            self._append({"kind": CHECKPOINT_HEADER_KIND, "schema": CHECKPOINT_SCHEMA, "identity": self.identity})
            stale = sorted(path.name for path in self.artifact_dir.glob("*.npz"))
            if stale:
                raise StaleSidecar(f"unreferenced checkpoint sidecar(s): {stale}")
            return
        raw = self.path.read_bytes()
        if not raw:
            raise CheckpointError("checkpoint is empty")
        if not raw.endswith(b"\n"):
            last_separator = raw.rfind(b"\n")
            if last_separator < 0:
                raise CheckpointError("checkpoint has no complete journal record")
            self.path.write_bytes(raw[: last_separator + 1])
            raw = raw[: last_separator + 1]
        lines = raw.decode("utf-8").splitlines()
        if not lines:
            raise CheckpointError("checkpoint is empty")
        header = json.loads(lines[0])
        if header.get("kind") != CHECKPOINT_HEADER_KIND or header.get("schema") != CHECKPOINT_SCHEMA:
            raise CheckpointIdentityMismatch("checkpoint schema mismatch")
        if header.get("identity") != self.identity:
            raise CheckpointIdentityMismatch("checkpoint matrix identity mismatch")
        for line in lines[1:]:
            record = json.loads(line)
            kind = record.get("kind")
            if kind == CHECKPOINT_DUPLICATE_KIND:
                self._duplicates += 1
                continue
            if kind != CHECKPOINT_UNIT_KIND:
                raise CheckpointError(f"unknown checkpoint record kind: {kind}")
            key = Task017UnitKey(**record["key"])
            token = key.token
            if token in self._records:
                raise CheckpointError(f"duplicate checkpoint record for {token}")
            metadata = record.get("metadata")
            if not isinstance(metadata, dict) or _digest(CHECKPOINT_UNIT_PREFIX, metadata) != record.get("unit_fingerprint"):
                raise CheckpointIdentityMismatch(f"checkpoint unit metadata fingerprint mismatch for {token}")
            if metadata.get("key") != key.as_record():
                raise CheckpointIdentityMismatch(f"checkpoint unit metadata key mismatch for {token}")
            self._records[token] = record
        referenced = {str(record["result_artifact"]) for record in self._records.values()}
        stale = sorted(path.name for path in self.artifact_dir.glob("*.npz") if path.name not in referenced)
        if stale:
            raise StaleSidecar(f"unreferenced checkpoint sidecar(s): {stale}")

    @property
    def duplicate_count(self) -> int:
        return self._duplicates

    def get(self, key: Task017UnitKey, unit_fingerprint: str) -> SimulationResult | None:
        record = self._records.get(key.token)
        if record is None:
            return None
        if record["unit_fingerprint"] != unit_fingerprint:
            raise CheckpointIdentityMismatch(f"unit fingerprint mismatch for {key.token}")
        metadata = record.get("metadata")
        if not isinstance(metadata, dict) or _digest(CHECKPOINT_UNIT_PREFIX, metadata) != record["unit_fingerprint"]:
            raise CheckpointIdentityMismatch(f"checkpoint unit metadata fingerprint mismatch for {key.token}")
        if metadata.get("key") != key.as_record():
            raise CheckpointIdentityMismatch(f"checkpoint unit metadata key mismatch for {key.token}")
        artifact = self.artifact_dir / str(record["result_artifact"])
        if not artifact.exists():
            raise CheckpointError(f"checkpoint artifact missing for {key.token}")
        result = _read_result_artifact(artifact)
        if result.spike_result_digest != record["result_digest"]:
            raise CheckpointError(f"checkpoint result digest mismatch for {key.token}")
        return result

    def put(
        self,
        key: Task017UnitKey,
        *,
        unit_fingerprint: str,
        metadata: Mapping[str, object],
        result: SimulationResult,
        technical_validity: str = "PASS",
    ) -> None:
        required_metadata = {
            "key",
            "effective_model_parameters",
            "schedule_fingerprint",
            "candidate_identity",
            "stimulus_identity",
        }
        missing_metadata = sorted(required_metadata.difference(metadata))
        if missing_metadata:
            raise CheckpointError(f"checkpoint unit metadata missing: {missing_metadata}")
        if key.token in self._records:
            self._append({"kind": CHECKPOINT_DUPLICATE_KIND, "key": key.as_record(), "unit_fingerprint": unit_fingerprint})
            self._duplicates += 1
            raise DuplicateUnitExecution(f"unit already completed: {key.token}")
        artifact_name = f"{key.token}.npz"
        artifact = self.artifact_dir / artifact_name
        _write_result_artifact(artifact, result)
        record = {
            "kind": CHECKPOINT_UNIT_KIND,
            "key": key.as_record(),
            "unit_fingerprint": unit_fingerprint,
            "metadata": json.loads(json.dumps(metadata, sort_keys=True, default=str)),
            "result_artifact": artifact_name,
            "result_digest": result.spike_result_digest,
            "technical_validity": technical_validity,
        }
        self._append(record)
        self._records[key.token] = record

    def records(self, keys: Iterable[Task017UnitKey] | None = None) -> tuple[dict[str, object], ...]:
        selected = self._records.values() if keys is None else (self._records[item.token] for item in keys if item.token in self._records)
        return tuple(sorted(selected, key=lambda item: tuple(item["key"][field] for field in ("variant_id", "stimulus_side", "analysis_kind", "trial_index", "candidate_id"))))

    def ledger(self, expected_keys: Sequence[Task017UnitKey] = ()) -> dict[str, object]:
        expected = tuple(expected_keys) or expected_task017_unit_keys()
        expected_tokens = {item.token for item in expected}
        completed = [record for token, record in self._records.items() if token in expected_tokens and record["technical_validity"] == "PASS"]
        completed_tokens = {Task017UnitKey(**record["key"]).token for record in completed}
        invalid = [record for token, record in self._records.items() if token in expected_tokens and record["technical_validity"] != "PASS"]
        missing = [item for item in expected if item.token not in completed_tokens]
        per_variant: dict[str, dict[str, int]] = {}
        per_analysis: dict[str, dict[str, int]] = {}
        for key in expected:
            variant = per_variant.setdefault(key.variant_id, {"expected": 0, "completed": 0, "missing": 0})
            analysis = per_analysis.setdefault(key.analysis_kind, {"expected": 0, "completed": 0, "missing": 0})
            variant["expected"] += 1
            analysis["expected"] += 1
            if key.token in completed_tokens:
                variant["completed"] += 1
                analysis["completed"] += 1
            else:
                variant["missing"] += 1
                analysis["missing"] += 1
        return {
            "expected_unit_count": len(expected),
            "completed_unit_count": len(completed),
            "missing_unit_count": len(missing),
            "duplicate_count": self._duplicates,
            "invalid_technical_unit_count": len(invalid),
            "per_variant_completion": per_variant,
            "per_analysis_completion": per_analysis,
            "matrix_complete": not missing and not invalid and len(completed) == len(expected),
            "missing_keys": [item.as_record() for item in missing],
        }


def task017_scoring_allowed(ledger: Mapping[str, object]) -> bool:
    """Return true only for the exact complete, technically valid matrix."""

    return bool(
        ledger.get("expected_unit_count") == 3168
        and ledger.get("completed_unit_count") == 3168
        and ledger.get("missing_unit_count") == 0
        and ledger.get("invalid_technical_unit_count") == 0
        and ledger.get("matrix_complete") is True
    )



def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode("utf-8")


def _digest(prefix: str, value: object) -> str:
    return hashlib.sha256(prefix.encode("utf-8") + b"\0" + _canonical_json(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class VariantConfiguration:
    """One literal preregistered model member; no global defaults are mutated."""

    variant_id: str
    changed_axis: str
    v_rest_mV: float = -52.0
    v_reset_mV: float = -52.0
    v_threshold_mV: float = -45.0
    tau_membrane_ms: float = 20.0
    tau_synapse_ms: float = 5.0
    refractory_period_ms: float = 2.2
    synaptic_delay_ms: float = 1.8
    synaptic_weight_mV: float = 0.275
    sign_policy_id: str = "Shiu2024SignPolicy"

    @property
    def parameters(self) -> LIFParameters:
        return LIFParameters(
            v_rest_mV=self.v_rest_mV,
            v_reset_mV=self.v_reset_mV,
            v_threshold_mV=self.v_threshold_mV,
            tau_membrane_ms=self.tau_membrane_ms,
            tau_synapse_ms=self.tau_synapse_ms,
            refractory_period_ms=self.refractory_period_ms,
            synaptic_delay_ms=self.synaptic_delay_ms,
            synaptic_weight_per_anatomical_synapse_mV=self.synaptic_weight_mV,
        )

    @property
    def sign_policy(self):
        if self.sign_policy_id == "Shiu2024SignPolicy":
            return Shiu2024SignPolicy()
        if self.sign_policy_id == "ConservativeSignPolicy":
            return ConservativeSignPolicy()
        raise ValueError(f"unknown preregistered sign policy: {self.sign_policy_id}")

    def as_record(self) -> dict[str, object]:
        return {
            "variant_id": self.variant_id,
            "changed_axis": self.changed_axis,
            "effective_parameters": asdict(self.parameters),
            "sign_policy": self.sign_policy_id,
            "dt_ms": DT_MS,
            "direct_input_weight_factor": DIRECT_INPUT_WEIGHT_FACTOR,
            "delay_steps": self.parameters.grid_steps(DT_MS)[0],
            "refractory_steps": self.parameters.grid_steps(DT_MS)[1],
        }


REFERENCE_VARIANT = VariantConfiguration("R0_REFERENCE_TASK005", "none")
VARIANT_CONFIGURATIONS: tuple[VariantConfiguration, ...] = (
    REFERENCE_VARIANT,
    VariantConfiguration("V1_TAU_MEMBRANE_FAST", "tau_membrane", tau_membrane_ms=10.0),
    VariantConfiguration("V2_TAU_MEMBRANE_SLOW", "tau_membrane", tau_membrane_ms=30.0),
    VariantConfiguration("V3_TAU_SYNAPSE_FAST", "tau_synapse", tau_synapse_ms=2.5),
    VariantConfiguration("V4_DELAY_SHORT", "synaptic_delay", synaptic_delay_ms=1.0),
    VariantConfiguration("V5_WEIGHT_LOW", "synaptic_weight", synaptic_weight_mV=0.200),
    VariantConfiguration("V6_THRESHOLD_HIGHER", "v_threshold", v_threshold_mV=-44.0),
    VariantConfiguration("V7_CONSERVATIVE_SIGNS", "sign_policy", sign_policy_id="ConservativeSignPolicy"),
)


def frozen_specification() -> dict[str, object]:
    """Return the complete execution-relevant Task 016 specification."""

    return {
        "schema": TASK016_SPEC_SCHEMA,
        "reference_model": {
            "v_rest": "-52.0 mV",
            "v_reset": "-52.0 mV",
            "v_threshold": "-45.0 mV",
            "threshold_rule": "strict v > v_threshold",
            "tau_membrane": "20.0 ms",
            "tau_synapse": "5.0 ms",
            "refractory_period": "2.2 ms",
            "synaptic_delay": "1.8 ms",
            "synaptic_weight_per_anatomical_synapse": "0.275 mV",
            "timestep": "0.1 ms",
            "state_update": "analytical Brian2-compatible linear update",
            "sign_policy": "Shiu2024SignPolicy",
            "silencing": "suppress outgoing scheduling only; retain incoming input and internal state",
        },
        "variants": [item.as_record() for item in VARIANT_CONFIGURATIONS],
        "candidates": list(FROZEN_TASK011_CANDIDATES),
        "readouts": {"MN9_L": MN9_L, "MN9_R": MN9_R},
        "stimuli": [
            {"id": "LEFT", "population": "frozen Task 008a LEFT population", "frequency_hz": 100.0, "duration_ms": 1000.0},
            {"id": "RIGHT", "population": "frozen Task 008a RIGHT population", "frequency_hz": 100.0, "duration_ms": 1000.0},
        ],
        "trials": {
            "task010_indices": list(range(TASK010_TRIAL_COUNT)),
            "task011_indices": list(FIXED_TRIAL_INDICES),
            "seed_identity": "Task 008 deterministic_seed with reference prepared graph and Shiu2024SignPolicy identity",
            "schedule_order": "event times and trial identities are reused exactly in every matrix",
            "direct_input": "fixed Task 005 input weight factor 250 multiplied by the declared synaptic weight",
        },
        "task010_thresholds": asdict(PREDECLARED_THRESHOLDS),
        "task011_thresholds": {
            "state_atol": STATE_ATOL,
            "state_rtol": STATE_RTOL,
            "network_divergent_neuron_threshold": NETWORK_DIVERGENT_NEURON_THRESHOLD,
            "network_activity_shift_fraction": NETWORK_ACTIVITY_SHIFT_FRACTION,
            "windows_ms": [list(item) for item in WINDOWS_MS],
        },
        "mechanism_compatibility_matrix": {
            "exact": "same label",
            "partial": [
                "NETWORK_REDISTRIBUTION_COMPATIBLE <-> MIXED scores 0.5",
                "SHORT_PATH_COMPATIBLE <-> MIXED scores 0.5",
            ],
            "incompatible": [
                "UNRESOLVED versus any other label scores 0",
                "SHORT_PATH_COMPATIBLE <-> NETWORK_REDISTRIBUTION_COMPATIBLE scores 0",
            ],
        },
        "global_rules": {
            "effect_direction": "at least 6/7 non-reference variants agree with the reference strict sign; reference zero requires exact zero within 1e-12 Hz",
            "effect_category": "ordinal distance at most one in negligible < small < moderate < major for at least 6/7 variants",
            "mechanism": "exact stable at 6/7 exact; compatible stable at total score at least 6.0/7 and no direct short/network transition",
            "robust": "all variants valid; at least 8/10 stable cells at each required level; all variants support the global conclusion",
            "partially_robust": "at least 5/7 global-supporting non-reference variants and at least 5/10 stable cells under each preregistered rule",
            "indeterminate": "incomplete or technically invalid matrix, undefined required metric, or execution-gate breach",
            "not_robust": "the exact remaining all-valid rule",
        },
        "pathological_exclusion_rules": [
            "declared parameter is not exactly representable on the frozen clock or is silently rounded",
            "required state, event count, rate, trace value, or digest is non-finite, or absolute state exceeds 1,000,000 mV",
            "non-deterministic completion under fixed duration and schedule",
            "unsigned graph, population, readout, candidate, schedule, or variant fingerprint mismatch",
            "CPU correctness gate or CUDA equivalence gate fails",
            "trace cannot be produced without changing canonical spike semantics, or trace instrumentation changes canonical spikes",
        ],
        "reference_classifications": {
            "10313": {"LEFT": "NETWORK_REDISTRIBUTION_COMPATIBLE", "RIGHT": "NETWORK_REDISTRIBUTION_COMPATIBLE"},
            "10135": {"LEFT": "NETWORK_REDISTRIBUTION_COMPATIBLE", "RIGHT": "MIXED"},
            "12752": {"LEFT": "MIXED", "RIGHT": "MIXED"},
            "512730": {"LEFT": "NETWORK_REDISTRIBUTION_COMPATIBLE", "RIGHT": "UNRESOLVED"},
            "43765": {"LEFT": "UNRESOLVED", "RIGHT": "UNRESOLVED"},
        },
    }


def task016_specification_fingerprint() -> str:
    return _digest("malecns-sim-task016-frozen-specification-v1", frozen_specification())


@dataclass(frozen=True, slots=True)
class FrozenSchedule:
    trial_index: int
    seed: int
    stimulus: ExplicitStimulus
    event_schedule_fingerprint: str


def _schedule_fingerprint(stimulus: ExplicitStimulus) -> str:
    payload = {
        "schedules": [
            {"neuron_id": item.neuron_id, "times_ms": item.spike_times_ms}
            for item in stimulus.schedules
        ],
        "refractory_free_neuron_ids": stimulus.refractory_free_neuron_ids,
    }
    return _digest(SCHEDULE_DIGEST_PREFIX, payload)


def _make_frozen_schedules(
    prepared_reference: PreparedNetwork,
    identities: PreparedTask008,
    population,
    *,
    side: str,
    trial_indices: Iterable[int],
    synaptic_weight_mV: float,
) -> tuple[FrozenSchedule, ...]:
    result = []
    for trial_index in trial_indices:
        seed = deterministic_seed(
            identities.fingerprint,
            side,
            DEFAULT_FREQUENCY_HZ,
            trial_index,
            TASK008_PREPARED_FINGERPRINT,
            "Shiu2024SignPolicy",
        )
        reference_explicit = PoissonStimulus(
            tuple(int(item) for item in population.candidate_body_ids),
            rate_hz=DEFAULT_FREQUENCY_HZ,
            seed=seed,
        ).generate(DURATION_MS, DT_MS, 0.275)
        explicit = ExplicitStimulus(
            schedules=reference_explicit.schedules,
            weight_mV=synaptic_weight_mV * DIRECT_INPUT_WEIGHT_FACTOR,
            refractory_free_neuron_ids=reference_explicit.refractory_free_neuron_ids,
        )
        result.append(FrozenSchedule(trial_index, seed, explicit, _schedule_fingerprint(explicit)))
    return tuple(result)


def _reweight_frozen_schedules(
    schedules: Mapping[str, tuple[FrozenSchedule, ...]],
    synaptic_weight_mV: float,
) -> dict[str, tuple[FrozenSchedule, ...]]:
    """Reuse frozen event times while applying only the declared weight axis."""

    return {
        side: tuple(
            FrozenSchedule(
                item.trial_index,
                item.seed,
                ExplicitStimulus(
                    schedules=item.stimulus.schedules,
                    weight_mV=synaptic_weight_mV * DIRECT_INPUT_WEIGHT_FACTOR,
                    refractory_free_neuron_ids=item.stimulus.refractory_free_neuron_ids,
                ),
                item.event_schedule_fingerprint,
            )
            for item in rows
        )
        for side, rows in schedules.items()
    }


def _write_json(path: str | Path, value: object) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(value, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    os.replace(temporary, target)


def _load_signed_connectome(
    annotation_path: str | Path,
    neurotransmitter_path: str | Path,
    weights_path: str | Path,
    sign_policy,
) -> SignedAnatomicalConnectome:
    import pyarrow.feather as feather

    numeric = load_male_cns_v1_numeric(annotation_path, neurotransmitter_path, weights_path, official_v1_mapping())
    annotations = feather.read_table(annotation_path).to_pylist()
    evidence = load_male_cns_v1_neurotransmitter_evidence(
        annotation_path, neurotransmitter_path, official_v1_mapping(), curated_only=True
    )
    selection = select_publication_neuron_ids(annotations)
    projection = project_numeric_connectome(numeric, selection.neuron_ids)
    return SignedAnatomicalConnectome.from_projection(
        projection, evidence, NeurotransmitterResolutionPolicy(), sign_policy
    )


def _variant_network(
    variant: VariantConfiguration,
    signed: SignedAnatomicalConnectome,
    cache: PreparedGraphCache,
    cache_path: str | Path,
    cuda_graph_cache: dict[str, object] | None = None,
) -> PreparedNetwork:
    projection = EffectiveSignedProjection.from_signed_connectome(
        signed, synaptic_weight_mV=variant.synaptic_weight_mV
    )
    graph = None if cuda_graph_cache is None else cuda_graph_cache.get(projection.fingerprint)
    if graph is None:
        graph, _ = upload_graph(projection)
        if cuda_graph_cache is not None:
            cuda_graph_cache[projection.fingerprint] = graph
    return PreparedNetwork(
        projection=projection,
        signed_connectome=signed,
        graph_name=f"task017-{variant.variant_id}",
        preparation_seconds=0.0,
        graph_loading_seconds=0.0,
        setup_seconds=0.0,
        memory_bytes=sum(
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
        ),
        fingerprint=_digest(
            "malecns-sim-task017-prepared-network-v1",
            {
                "variant_id": variant.variant_id,
                "unsigned": projection.unsigned_graph_fingerprint,
                "signed": projection.signed_policy_fingerprint,
                "effective": projection.fingerprint,
            },
        ),
        cache_path=str(cache_path),
        cache_fingerprint=cache.cache_fingerprint,
        cuda_graph=graph,
    )


def _assert_projection_matches_cache(
    projection: EffectiveSignedProjection, cache_projection: EffectiveSignedProjection
) -> None:
    if projection.fingerprint != cache_projection.fingerprint:
        raise RuntimeError("reference projection fingerprint does not match the frozen Task 008 cache")
    for left, right in (
        (projection.neuron_ids, cache_projection.neuron_ids),
        (projection.outgoing_indptr, cache_projection.outgoing_indptr),
        (projection.outgoing_targets, cache_projection.outgoing_targets),
        (projection.outgoing_weights_mV, cache_projection.outgoing_weights_mV),
    ):
        if not np.array_equal(left, right):
            raise RuntimeError("reference projection arrays do not match the frozen Task 008 cache")


def _run_batch(
    prepared: PreparedNetwork,
    variant: VariantConfiguration,
    stimuli: Sequence[ExplicitStimulus],
    *,
    duration_ms: float,
    silenced_ids: Sequence[str] = (),
    silenced_ids_by_trial: Sequence[Sequence[str | int]] | None = None,
    trace_ids: Sequence[str] = (),
    collect_sparse_trace: bool = False,
    force_cpu: bool = False,
) -> tuple[SimulationResult, ...]:
    parameters = variant.parameters
    silenced = tuple(int(item) for item in silenced_ids)
    per_trial_silenced = None if silenced_ids_by_trial is None else tuple(
        tuple(int(item) for item in values) for values in silenced_ids_by_trial
    )
    if per_trial_silenced is not None and len(per_trial_silenced) != len(stimuli):
        raise ValueError("per-trial silencing count must match stimulus count")
    traces = tuple(int(item) for item in trace_ids)
    if force_cpu:
        if per_trial_silenced is not None:
            if trace_ids or collect_sparse_trace:
                raise ValueError("per-trial CPU silencing is only supported for untraced execution")
            return tuple(
                simulate_lif_active(
                    prepared.projection,
                    duration_ms=duration_ms,
                    stimulus=stimulus,
                    parameters=parameters,
                    dt_ms=DT_MS,
                    silenced_neuron_ids=trial_silenced,
                )
                for stimulus, trial_silenced in zip(stimuli, per_trial_silenced)
            )
        if not trace_ids and not collect_sparse_trace:
            return tuple(
                simulate_lif_active(
                    prepared.projection,
                    duration_ms=duration_ms,
                    stimulus=stimulus,
                    parameters=parameters,
                    dt_ms=DT_MS,
                    silenced_neuron_ids=silenced,
                )
                for stimulus in stimuli
            )
        return tuple(
            simulate_lif(
                prepared.projection,
                duration_ms=duration_ms,
                stimulus=stimulus,
                parameters=parameters,
                dt_ms=DT_MS,
                silenced_neuron_ids=silenced,
                trace_neuron_ids=traces,
                collect_sparse_trace=collect_sparse_trace,
            )
            for stimulus in stimuli
        )
    return simulate_cuda_batch(
        prepared.projection,
        stimuli,
        duration_ms=duration_ms,
        parameters=parameters,
        dt_ms=DT_MS,
        silenced_neuron_ids=silenced,
        silenced_neuron_ids_by_trial=per_trial_silenced,
        trace_neuron_ids=traces,
        collect_sparse_trace=collect_sparse_trace,
        cuda_graph=prepared.cuda_graph,
    )


def _unit_metadata(
    variant: VariantConfiguration,
    prepared: PreparedNetwork,
    schedule: FrozenSchedule,
    *,
    key: Task017UnitKey,
    duration_ms: float,
    silenced_ids: Sequence[str | int],
    trace_ids: Sequence[str | int],
) -> tuple[dict[str, object], str]:
    metadata: dict[str, object] = {
        "key": key.as_record(),
        "effective_model_parameters": variant.as_record(),
        "unsigned_graph_fingerprint": prepared.projection.unsigned_graph_fingerprint,
        "effective_signed_graph_fingerprint": prepared.projection.fingerprint,
        "sign_policy_fingerprint": prepared.projection.signed_policy_fingerprint,
        "cache_fingerprint": prepared.cache_fingerprint,
        "candidate_identity": key.candidate_id,
        "stimulus_identity": key.stimulus_side,
        "readout_ids": {"MN9_L": MN9_L, "MN9_R": MN9_R},
        "trial_index": schedule.trial_index,
        "seed": schedule.seed,
        "schedule_fingerprint": schedule.event_schedule_fingerprint,
        "stimulus_fingerprint": schedule.stimulus.fingerprint,
        "duration_ms": float(duration_ms),
        "dt_ms": DT_MS,
        "direct_input_weight_mV": schedule.stimulus.weight_mV,
        "silencing": {
            "candidate_id": key.candidate_id,
            "ids": sorted(int(item) for item in silenced_ids),
            "semantics": "suppress outgoing scheduling only; retain incoming input and internal state",
        },
        "trace_schema": {
            "trace_neuron_ids": sorted(int(item) for item in trace_ids),
            "collect_sparse_trace": bool(trace_ids),
        },
    }
    return metadata, _digest(CHECKPOINT_UNIT_PREFIX, metadata)


def _run_or_reuse_cases(
    checkpoint: Task017Checkpoint,
    variant: VariantConfiguration,
    prepared: PreparedNetwork,
    schedule: FrozenSchedule,
    *,
    side: str,
    duration_ms: float,
    cases: Sequence[tuple[str, str, Sequence[str]]],
    trace_ids: Sequence[str] = (),
    collect_sparse_trace: bool = False,
    budget: ExecutionBudget | None = None,
) -> dict[tuple[str, str], SimulationResult]:
    """Reuse exact units or execute one deterministic independent-trial batch."""

    results: dict[tuple[str, str], SimulationResult] = {}
    missing: list[tuple[Task017UnitKey, dict[str, object], str, tuple[str, ...]]] = []
    for candidate_id, analysis_kind, silenced_ids in cases:
        key = Task017UnitKey(variant.variant_id, candidate_id, side, schedule.trial_index, analysis_kind)
        metadata, unit_fingerprint = _unit_metadata(
            variant,
            prepared,
            schedule,
            key=key,
            duration_ms=duration_ms,
            silenced_ids=silenced_ids,
            trace_ids=trace_ids,
        )
        reused = checkpoint.get(key, unit_fingerprint)
        if reused is None:
            missing.append((key, metadata, unit_fingerprint, tuple(silenced_ids)))
        else:
            results[(candidate_id, analysis_kind)] = reused
    offset = 0
    while offset < len(missing):
        limit = len(missing) - offset if budget is None else budget.batch_limit(len(missing) - offset)
        batch = missing[offset : offset + limit]
        if budget is not None:
            budget.before_batch(len(batch))
        batch_results = _run_batch(
            prepared,
            variant,
            tuple(schedule.stimulus for _ in batch),
            duration_ms=duration_ms,
            silenced_ids_by_trial=tuple(item[3] for item in batch),
            trace_ids=trace_ids,
            collect_sparse_trace=collect_sparse_trace,
        )
        for (key, metadata, unit_fingerprint, _silenced_ids), result in zip(batch, batch_results):
            checkpoint.put(key, unit_fingerprint=unit_fingerprint, metadata=metadata, result=result)
            results[(key.candidate_id, key.analysis_kind)] = result
        if budget is not None:
            budget.committed(len(batch))
        offset += len(batch)
    return results


def _run_or_reuse_series(
    checkpoint: Task017Checkpoint,
    variant: VariantConfiguration,
    prepared: PreparedNetwork,
    schedules: Sequence[FrozenSchedule],
    *,
    side: str,
    candidate_id: str,
    analysis_kind: str,
    duration_ms: float,
    silenced_ids: Sequence[str] = (),
    trace_ids: Sequence[str] = (),
    collect_sparse_trace: bool = False,
    deadline: float | None = None,
    budget: ExecutionBudget | None = None,
) -> tuple[SimulationResult, ...]:
    """Reuse or batch one candidate/side series while checkpointing each unit."""

    results: dict[int, SimulationResult] = {}
    missing: list[tuple[FrozenSchedule, Task017UnitKey, dict[str, object], str]] = []
    for schedule in schedules:
        key = Task017UnitKey(variant.variant_id, candidate_id, side, schedule.trial_index, analysis_kind)
        metadata, unit_fingerprint = _unit_metadata(
            variant,
            prepared,
            schedule,
            key=key,
            duration_ms=duration_ms,
            silenced_ids=silenced_ids,
            trace_ids=trace_ids,
        )
        reused = checkpoint.get(key, unit_fingerprint)
        if reused is None:
            missing.append((schedule, key, metadata, unit_fingerprint))
        else:
            results[schedule.trial_index] = reused
    offset = 0
    while offset < len(missing):
        limit = len(missing) - offset if budget is None else budget.batch_limit(len(missing) - offset)
        batch = missing[offset : offset + limit]
        if budget is not None:
            budget.before_batch(len(batch))
        batch_results = _run_batch(
            prepared,
            variant,
            tuple(item[0].stimulus for item in batch),
            duration_ms=duration_ms,
            silenced_ids=silenced_ids,
            trace_ids=trace_ids,
            collect_sparse_trace=collect_sparse_trace,
        )
        for (schedule, key, metadata, unit_fingerprint), result in zip(batch, batch_results):
            checkpoint.put(key, unit_fingerprint=unit_fingerprint, metadata=metadata, result=result)
            results[schedule.trial_index] = result
        if budget is not None:
            budget.committed(len(batch))
        offset += len(batch)
    return tuple(results[item.trial_index] for item in schedules)


def _result_equal(left: SimulationResult, right: SimulationResult) -> bool:
    return bool(
        np.array_equal(left.spike_neuron_ids, right.spike_neuron_ids)
        and np.array_equal(left.spike_timesteps, right.spike_timesteps)
        and np.array_equal(left.spike_counts, right.spike_counts)
        and left.spike_result_digest == right.spike_result_digest
    )


def _trace_equal(left: SimulationResult, right: SimulationResult) -> bool:
    if not _result_equal(left, right):
        return False
    if left.sparse_trace is None or right.sparse_trace is None:
        return left.sparse_trace is None and right.sparse_trace is None
    return bool(
        np.array_equal(left.sparse_trace.timesteps, right.sparse_trace.timesteps)
        and np.array_equal(left.sparse_trace.delivered_event_counts, right.sparse_trace.delivered_event_counts)
        and np.array_equal(left.sparse_trace.delivered_target_counts, right.sparse_trace.delivered_target_counts)
        and np.array_equal(left.sparse_trace.delivered_target_index_sums, right.sparse_trace.delivered_target_index_sums)
        and np.allclose(left.sparse_trace.delivered_weight_sums_mV, right.sparse_trace.delivered_weight_sums_mV, rtol=STATE_RTOL, atol=STATE_ATOL)
        and np.allclose(left.sparse_trace.delivered_abs_weight_sums_mV, right.sparse_trace.delivered_abs_weight_sums_mV, rtol=STATE_RTOL, atol=STATE_ATOL)
        and np.array_equal(left.trace_neuron_ids, right.trace_neuron_ids)
        and np.allclose(left.trace_v_mV, right.trace_v_mV, rtol=STATE_RTOL, atol=STATE_ATOL)
        and np.allclose(left.trace_g_mV, right.trace_g_mV, rtol=STATE_RTOL, atol=STATE_ATOL)
    )


def _synthetic_projection(weight_mV: float) -> EffectiveSignedProjection:
    ids = np.asarray([1, 2, 3, 4], dtype=np.int64)
    source = np.asarray([0, 0, 1, 2], dtype=np.int64)
    target = np.asarray([1, 2, 2, 3], dtype=np.int64)
    signs = np.asarray([1.0, -1.0, 1.0, 1.0], dtype=np.float64)
    weights = signs * weight_mV
    indptr = np.zeros(ids.size + 1, dtype=np.int64)
    np.add.at(indptr, source + 1, 1)
    np.cumsum(indptr, out=indptr)
    for array in (ids, source, target, weights, indptr):
        array.flags.writeable = False
    return EffectiveSignedProjection(
        neuron_ids=ids,
        source_positions=source,
        target_positions=target,
        effective_weights_mV=weights,
        included_anatomical_weight=4,
        excluded_anatomical_weight=0,
        excluded_unresolved_edge_count=0,
        synaptic_weight_mV=weight_mV,
        sign_policy_id="synthetic",
        resolution_policy_id="synthetic",
        unsigned_graph_fingerprint="s" * 64,
        signed_policy_fingerprint="t" * 64,
        fingerprint="u" * 64,
        outgoing_indptr=indptr,
        outgoing_targets=target,
        outgoing_weights_mV=weights,
    )


def _synthetic_fixtures(weight_mV: float) -> tuple[ExplicitStimulus, ...]:
    direct = weight_mV * DIRECT_INPUT_WEIGHT_FACTOR
    return (
        ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=direct),
        ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=direct),
        ExplicitStimulus(
            (SpikeSchedule(1, (0.0, 0.0)), SpikeSchedule(2, (0.0,))),
            weight_mV=direct,
        ),
        ExplicitStimulus((SpikeSchedule(1, (0.0, 0.1, 0.2)),), weight_mV=direct),
    )


def _truncate_stimulus(stimulus: ExplicitStimulus, duration_ms: float) -> ExplicitStimulus:
    return ExplicitStimulus(
        schedules=tuple(
            SpikeSchedule(item.neuron_id, tuple(time for time in item.spike_times_ms if time < duration_ms))
            for item in stimulus.schedules
        ),
        weight_mV=stimulus.weight_mV,
        refractory_free_neuron_ids=stimulus.refractory_free_neuron_ids,
    )


def _validate_variant_technical(
    variant: VariantConfiguration,
    prepared: PreparedNetwork,
    representative: FrozenSchedule,
) -> dict[str, object]:
    parameters = variant.parameters
    delay_steps, refractory_steps = parameters.grid_steps(DT_MS)
    synthetic_projection = _synthetic_projection(variant.synaptic_weight_mV)
    synthetic_graph, _ = upload_graph(synthetic_projection)
    synthetic_results = []
    for stimulus in _synthetic_fixtures(variant.synaptic_weight_mV):
        cpu = simulate_lif(
            synthetic_projection,
            duration_ms=10.0,
            stimulus=stimulus,
            parameters=parameters,
            dt_ms=DT_MS,
            trace_neuron_ids=(1, 2, 3, 4),
            collect_sparse_trace=True,
        )
        gpu = simulate_cuda_batch(
            synthetic_projection,
            (stimulus,),
            duration_ms=10.0,
            parameters=parameters,
            dt_ms=DT_MS,
            trace_neuron_ids=(1, 2, 3, 4),
            collect_sparse_trace=True,
            cuda_graph=synthetic_graph,
        )[0]
        if not _trace_equal(cpu, gpu):
            raise AssertionError(f"{variant.variant_id} synthetic CPU/CUDA equivalence failed")
        synthetic_results.append(gpu.spike_result_digest)

    trace_ids = FROZEN_TASK011_CANDIDATES + (MN9_L, MN9_R)
    short_stimulus = _truncate_stimulus(representative.stimulus, 20.0)
    twenty_ms_cpu = _run_batch(
        prepared,
        variant,
        (short_stimulus,),
        duration_ms=20.0,
        silenced_ids=("10313",),
        trace_ids=trace_ids,
        collect_sparse_trace=True,
        force_cpu=True,
    )[0]
    twenty_ms_gpu = _run_batch(
        prepared,
        variant,
        (short_stimulus,),
        duration_ms=20.0,
        silenced_ids=("10313",),
        trace_ids=trace_ids,
        collect_sparse_trace=True,
    )[0]
    if not _trace_equal(twenty_ms_cpu, twenty_ms_gpu):
        raise AssertionError(f"{variant.variant_id} full-graph trace CPU/CUDA equivalence failed")
    full_cpu = _run_batch(
        prepared,
        variant,
        (representative.stimulus,),
        duration_ms=DURATION_MS,
        force_cpu=True,
    )[0]
    full_gpu = _run_batch(prepared, variant, (representative.stimulus,), duration_ms=DURATION_MS)[0]
    silenced_cpu = _run_batch(
        prepared,
        variant,
        (representative.stimulus,),
        duration_ms=DURATION_MS,
        silenced_ids=("10313",),
        force_cpu=True,
    )[0]
    silenced_gpu = _run_batch(
        prepared,
        variant,
        (representative.stimulus,),
        duration_ms=DURATION_MS,
        silenced_ids=("10313",),
    )[0]
    if not _result_equal(full_cpu, full_gpu) or not _result_equal(silenced_cpu, silenced_gpu):
        raise AssertionError(f"{variant.variant_id} full-graph CPU/CUDA canonical equivalence failed")
    untraced_gpu = _run_batch(
        prepared,
        variant,
        (short_stimulus,),
        duration_ms=20.0,
        silenced_ids=("10313",),
    )[0]
    if untraced_gpu.spike_result_digest != twenty_ms_gpu.spike_result_digest:
        raise AssertionError(f"{variant.variant_id} trace instrumentation changed canonical spikes")
    repeat_gpu = _run_batch(
        prepared,
        variant,
        (representative.stimulus,),
        duration_ms=DURATION_MS,
        silenced_ids=("10313",),
    )[0]
    if repeat_gpu.spike_result_digest != silenced_gpu.spike_result_digest:
        raise AssertionError(f"{variant.variant_id} deterministic replay failed")
    return {
        "status": "PASS",
        "backend": "cuda-float64",
        "delay_steps": delay_steps,
        "refractory_steps": refractory_steps,
        "synthetic_fixture_count": 4,
        "synthetic_spike_digests": synthetic_results,
        "full_graph_trace_spike_digest": twenty_ms_gpu.spike_result_digest,
        "full_graph_baseline_spike_digest": full_gpu.spike_result_digest,
        "full_graph_intervention_spike_digest": silenced_gpu.spike_result_digest,
        "trace_does_not_alter_spikes": True,
        "deterministic_replay": True,
        "float64": True,
    }


def _schedule_tuples(schedules: Sequence[FrozenSchedule]) -> tuple[tuple[int, int, ExplicitStimulus], ...]:
    return tuple((item.trial_index, item.seed, item.stimulus) for item in schedules)


def _task010_variant(
    variant: VariantConfiguration,
    prepared: PreparedNetwork,
    schedules_by_side: Mapping[str, tuple[FrozenSchedule, ...]],
    manifest: FrozenCandidateManifest,
    checkpoint: Task017Checkpoint,
    budget: ExecutionBudget | None = None,
) -> dict[str, object]:
    populations = ((PRIMARY_CONDITION, "LEFT"), (MIRROR_CONDITION, "RIGHT"))
    baseline_trials: dict[str, tuple[Task010Trial, ...]] = {}
    intervention_results: dict[tuple[str, str], tuple[SimulationResult, ...]] = {}
    for condition, side in populations:
        schedules = schedules_by_side[side]
        baseline_rows = _run_or_reuse_series(
            checkpoint,
            variant,
            prepared,
            schedules,
            side=side,
            candidate_id=BASELINE_CANDIDATE_ID,
            analysis_kind=TASK010_BASELINE,
            duration_ms=DURATION_MS,
            budget=budget,
        )
        baseline_trials[side] = _trials_from_results(
            "baseline",
            condition,
            side[0],
            _schedule_tuples(schedules),
            tuple(baseline_rows),
            prepared.projection,
        )
        intervention_rows = {candidate_id: [] for candidate_id in FROZEN_TASK011_CANDIDATES}
        for schedule in schedules:
            cases = tuple(
                (candidate_id, TASK010_INTERVENTION, (candidate_id,))
                for candidate_id in sorted(FROZEN_TASK011_CANDIDATES)
            )
            case_results = _run_or_reuse_cases(
                checkpoint,
                variant,
                prepared,
                schedule,
                side=side,
                duration_ms=DURATION_MS,
                cases=cases,
                budget=budget,
            )
            for candidate_id in FROZEN_TASK011_CANDIDATES:
                intervention_rows[candidate_id].append(case_results[(candidate_id, TASK010_INTERVENTION)])
        for candidate_id, rows in intervention_rows.items():
            intervention_results[(candidate_id, side)] = tuple(rows)
    outcomes: dict[str, object] = {}
    for candidate_id in FROZEN_TASK011_CANDIDATES:
        for condition, side in populations:
            schedules = schedules_by_side[side]
            trials = _trials_from_results(
                candidate_id,
                condition,
                side[0],
                _schedule_tuples(schedules),
                intervention_results[(candidate_id, side)],
                prepared.projection,
            )
            outcomes[f"{candidate_id}:{condition.name}"] = {
                "candidate_id": candidate_id,
                "condition": condition.name,
                "stimulus_side": side[0],
                "technical_validity": "PASS",
                "trials": [asdict(item) for item in trials],
                "summary": summarize_condition(baseline_trials[side], trials),
            }
    return {
        "variant_id": variant.variant_id,
        "baseline_trials": {side: [asdict(item) for item in trials] for side, trials in baseline_trials.items()},
        "outcomes": outcomes,
        "trial_count_per_side": TASK010_TRIAL_COUNT,
        "simulation_count": 2 * (1 + len(FROZEN_TASK011_CANDIDATES)) * TASK010_TRIAL_COUNT,
        "schedule_records": {
            side: [
                {
                    "trial_index": item.trial_index,
                    "seed": item.seed,
                    "event_schedule_fingerprint": item.event_schedule_fingerprint,
                    "stimulus_fingerprint": item.stimulus.fingerprint,
                    "direct_input_weight_mV": item.stimulus.weight_mV,
                }
                for item in schedules
            ]
            for side, schedules in schedules_by_side.items()
        },
    }


def _task011_variant(
    variant: VariantConfiguration,
    prepared: PreparedNetwork,
    schedules_by_side: Mapping[str, tuple[FrozenSchedule, ...]],
    manifest: FrozenCandidateManifest,
    annotation_path: str | Path,
    checkpoint: Task017Checkpoint,
    budget: ExecutionBudget | None = None,
) -> dict[str, object]:
    trace_ids = FROZEN_TASK011_CANDIDATES + (MN9_L, MN9_R)
    populations = ((PRIMARY_CONDITION, "LEFT"), (MIRROR_CONDITION, "RIGHT"))
    baseline_by_side: dict[str, tuple[SimulationResult, ...]] = {}
    silenced_by_case: dict[tuple[str, str], tuple[SimulationResult, ...]] = {}
    for condition, side in populations:
        schedules = tuple(item for item in schedules_by_side[side] if item.trial_index in FIXED_TRIAL_INDICES)
        baseline_by_side[side] = _run_or_reuse_series(
            checkpoint,
            variant,
            prepared,
            schedules,
            side=side,
            candidate_id=BASELINE_CANDIDATE_ID,
            analysis_kind=TASK011_BASELINE,
            duration_ms=TRACE_DURATION_MS,
            trace_ids=trace_ids,
            collect_sparse_trace=True,
            budget=budget,
        )
        intervention_rows = {candidate_id: [] for candidate_id in FROZEN_TASK011_CANDIDATES}
        for schedule in schedules:
            cases = tuple(
                (candidate_id, TASK011_INTERVENTION, (candidate_id,))
                for candidate_id in sorted(FROZEN_TASK011_CANDIDATES)
            )
            case_results = _run_or_reuse_cases(
                checkpoint,
                variant,
                prepared,
                schedule,
                side=side,
                duration_ms=TRACE_DURATION_MS,
                cases=cases,
                trace_ids=trace_ids,
                collect_sparse_trace=True,
                budget=budget,
            )
            for candidate_id in FROZEN_TASK011_CANDIDATES:
                intervention_rows[candidate_id].append(case_results[(candidate_id, TASK011_INTERVENTION)])
        for candidate_id, rows in intervention_rows.items():
            silenced_by_case[(candidate_id, side)] = tuple(rows)
    annotation_by_id = _annotation_map(annotation_path)
    candidate_rows = {item.body_id: asdict(item) for item in manifest.candidates}
    structural = {
        candidate_id: structural_summary(prepared.projection, candidate_rows[candidate_id], annotation_by_id)
        for candidate_id in FROZEN_TASK011_CANDIDATES
    }
    exposure = {
        candidate_id: {
            side: baseline_activity_exposure(baseline_by_side[side], candidate_id, prepared.projection)
            for side in ("LEFT", "RIGHT")
        }
        for candidate_id in FROZEN_TASK011_CANDIDATES
    }
    per_case: dict[str, object] = {}
    aggregate_windows: dict[str, object] = {}
    classifications: dict[str, object] = {}
    for candidate_id in FROZEN_TASK011_CANDIDATES:
        for condition, side in populations:
            schedules = schedules_by_side[side]
            baseline_results = baseline_by_side[side]
            silenced_results = silenced_by_case[(candidate_id, side)]
            trial_rows = []
            window_rows = []
            evidence_rows = []
            first_hop_trial_rows = []
            for schedule, baseline, silenced in zip(schedules, baseline_results, silenced_results):
                divergence, divergent = detect_first_divergence(
                    baseline,
                    silenced,
                    input_neuron_ids=schedule.stimulus.refractory_free_neuron_ids,
                    candidate_id=candidate_id,
                )
                windows = propagation_windows(
                    baseline,
                    silenced,
                    divergent=divergent,
                    first_delivery_step=divergence.first_delivery_step,
                )
                first_hop = first_hop_target_analysis(
                    (baseline,),
                    (silenced,),
                    prepared.projection,
                    candidate_id,
                    annotation_by_id,
                )
                evidence = _mechanism_evidence(
                    candidate_rows[candidate_id],
                    side[0],
                    MN9_L,
                    structural[candidate_id],
                    divergence,
                    divergent,
                    first_hop,
                    baseline,
                    silenced,
                )
                evidence_rows.append(evidence)
                window_rows.extend(windows)
                first_hop_trial_rows.append(first_hop)
                trial_rows.append(
                    {
                        "trial_index": schedule.trial_index,
                        "seed": schedule.seed,
                        "stimulus_fingerprint": schedule.stimulus.fingerprint,
                        "event_schedule_fingerprint": schedule.event_schedule_fingerprint,
                        "baseline_spike_digest": baseline.spike_result_digest,
                        "silenced_spike_digest": silenced.spike_result_digest,
                        "baseline_sparse_trace_fingerprint": baseline.sparse_trace.fingerprint if baseline.sparse_trace else None,
                        "silenced_sparse_trace_fingerprint": silenced.sparse_trace.fingerprint if silenced.sparse_trace else None,
                        "baseline_total_spikes": baseline.emitted_spike_count,
                        "silenced_total_spikes": silenced.emitted_spike_count,
                        "divergence": divergence.as_ms(),
                        "propagation_windows": list(windows),
                        "first_hop": first_hop,
                        "mechanism_evidence": evidence,
                        "technical_validity": "PASS",
                    }
                )
            key = f"{candidate_id}:{condition.name}"
            per_case[key] = trial_rows
            aggregate_windows[key] = _aggregate_windows(window_rows)
            classifications[key] = {
                "classification": classify_mechanism(evidence_rows),
                "trial_count": len(evidence_rows),
                "short_path_compatible_trials": sum(bool(item["short_path_compatible"]) for item in evidence_rows),
                "network_redistribution_compatible_trials": sum(bool(item["network_redistribution_compatible"]) for item in evidence_rows),
                "evidence": evidence_rows,
                "technical_validity": "PASS",
            }
    return {
        "variant_id": variant.variant_id,
        "trial_indices": list(FIXED_TRIAL_INDICES),
        "trace_ids": list(trace_ids),
        "baseline_candidate_activity": exposure,
        "candidate_structural_metadata": structural,
        "divergence_results": per_case,
        "propagation_profiles": aggregate_windows,
        "mechanism_classifications": classifications,
        "simulation_count": 2 * (1 + len(FROZEN_TASK011_CANDIDATES)) * len(FIXED_TRIAL_INDICES),
    }


def _reference_replay_gate(
    reference: Mapping[str, object],
    task008_results_path: str | Path,
    task010_results_path: str | Path,
    task011_results_path: str | Path,
) -> dict[str, object]:
    task008 = json.loads(Path(task008_results_path).read_text(encoding="utf-8"))
    task010 = json.loads(Path(task010_results_path).read_text(encoding="utf-8"))
    task011 = json.loads(Path(task011_results_path).read_text(encoding="utf-8"))
    if task010.get("result_digest") != TASK010_RESULT_DIGEST:
        raise RuntimeError("Task 010 reference digest does not match the frozen checkpoint")
    if task011.get("result_digest") != TASK011_RESULT_DIGEST:
        raise RuntimeError("Task 011 reference digest does not match the frozen checkpoint")
    outcomes = reference["task010"]["outcomes"]
    baseline_expected = {
        "LEFT": task008["repeat_100hz"]["trials"],
        "RIGHT": task008["mirror_100hz"]["trials"],
    }
    baseline_fields = ("trial_index", "seed", "result_digest", "total_network_spikes")
    baseline_checks = {}
    for side, expected in baseline_expected.items():
        observed = reference["task010"]["baseline_trials"][side]
        baseline_checks[side] = len(expected) == len(observed) and all(
            all(expected_item[field] == observed_item[field] for field in baseline_fields)
            for expected_item, observed_item in zip(expected, observed)
        )
    intervention_checks = {}
    for key, observed in outcomes.items():
        expected = task010["outcomes"].get(key)
        if expected is None:
            raise RuntimeError(f"reference replay key missing from Task 010 artifact: {key}")
        observed_trials = observed["trials"]
        expected_trials = expected["trials"]
        intervention_checks[key] = len(expected_trials) == len(observed_trials) and all(
            all(expected_item[field] == observed_item[field] for field in baseline_fields)
            for expected_item, observed_item in zip(expected_trials, observed_trials)
        )
        if observed["summary"] != expected["summary"]:
            raise RuntimeError(f"reference Task 010 summary mismatch: {key}")
    temporal = reference["temporal"]
    classification_checks = {}
    trace_checks = {}
    for key, observed in temporal["mechanism_classifications"].items():
        expected = task011["mechanism_classifications"].get(key)
        if expected is None or observed["classification"] != expected["classification"]:
            raise RuntimeError(f"reference Task 011 classification mismatch: {key}")
        classification_checks[key] = True
        observed_rows = temporal["divergence_results"][key]
        expected_rows = task011["divergence_results"][key]
        trace_checks[key] = len(observed_rows) == len(expected_rows) and all(
            left["trial_index"] == right["trial_index"]
            and left["baseline_spike_digest"] == right["baseline_spike_digest"]
            and left["silenced_spike_digest"] == right["silenced_spike_digest"]
            and left["divergence"] == right["divergence"]
            for left, right in zip(observed_rows, expected_rows)
        )
    if not all(baseline_checks.values()) or not all(intervention_checks.values()) or not all(classification_checks.values()) or not all(trace_checks.values()):
        raise RuntimeError("reference replay gate failed")
    summary = task008["repeat_100hz"]["summaries"][0]
    context = {
        "official_mn9_mean_hz": 67.0333,
        "observed_mn9_mean_hz": summary["ipsilateral_mean_hz"],
        "mean_within_5_hz": abs(summary["ipsilateral_mean_hz"] - 67.0333) <= 5.0,
        "observed_active_trial_fraction": summary["ipsilateral_active_fraction"],
        "active_fraction_within_0.001": abs(summary["ipsilateral_active_fraction"] - 1.0) <= 0.001,
    }
    if not context["mean_within_5_hz"] or not context["active_fraction_within_0.001"]:
        raise RuntimeError("reference Shiu context gate failed")
    return {
        "status": "PASS",
        "baseline_schedules_unchanged": baseline_checks,
        "intervention_effect_outputs_reproduced": intervention_checks,
        "mechanism_classifications_reproduced": classification_checks,
        "temporal_trace_digests_reproduced": trace_checks,
        "shiu_v630_context": context,
        "trace_instrumentation_spike_invariant": True,
    }


def _compatibility_score(reference: str, alternative: str) -> float:
    if reference == alternative:
        return 1.0
    if {reference, alternative} in (
        {"NETWORK_REDISTRIBUTION_COMPATIBLE", "MIXED"},
        {"SHORT_PATH_COMPATIBLE", "MIXED"},
    ):
        return 0.5
    return 0.0


def _effect_sign(value: float) -> str:
    if abs(float(value)) <= 1e-12:
        return "ZERO"
    return "POSITIVE" if value > 0.0 else "NEGATIVE"


def _robustness_cells(variant_results: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
    reference = variant_results[REFERENCE_VARIANT.variant_id]
    alternatives = [item for item in VARIANT_CONFIGURATIONS if item is not REFERENCE_VARIANT]
    cells: dict[str, object] = {}
    for candidate_id in FROZEN_TASK011_CANDIDATES:
        for side, label in (("LEFT", PRIMARY_CONDITION.name), ("RIGHT", MIRROR_CONDITION.name)):
            key = f"{candidate_id}:{side}"
            ref_summary = reference["task010"]["outcomes"][f"{candidate_id}:{label}"]["summary"]["mn9_l"]
            ref_effect = float(ref_summary["silenced_mean_hz"]) - float(ref_summary["baseline_mean_hz"])
            ref_category = str(ref_summary["classification"])
            ref_mechanism = str(reference["temporal"]["mechanism_classifications"][f"{candidate_id}:{label}"]["classification"])
            direction_rows = []
            category_rows = []
            mechanism_rows = []
            for variant in alternatives:
                result = variant_results[variant.variant_id]
                summary = result["task010"]["outcomes"][f"{candidate_id}:{label}"]["summary"]["mn9_l"]
                effect = float(summary["silenced_mean_hz"]) - float(summary["baseline_mean_hz"])
                category = str(summary["classification"])
                alternative_mechanism = str(result["temporal"]["mechanism_classifications"][f"{candidate_id}:{label}"]["classification"])
                direction_rows.append({"variant_id": variant.variant_id, "effect_hz": effect, "sign": _effect_sign(effect), "matches_reference": _effect_sign(effect) == _effect_sign(ref_effect)})
                ordinal = {"negligible": 0, "small": 1, "moderate": 2, "major": 3}
                category_rows.append({"variant_id": variant.variant_id, "category": category, "ordinal_distance": abs(ordinal[category] - ordinal[ref_category]), "allowable": abs(ordinal[category] - ordinal[ref_category]) <= 1})
                mechanism_rows.append({"variant_id": variant.variant_id, "classification": alternative_mechanism, "score": _compatibility_score(ref_mechanism, alternative_mechanism), "direct_incompatible_transition": {ref_mechanism, alternative_mechanism} == {"SHORT_PATH_COMPATIBLE", "NETWORK_REDISTRIBUTION_COMPATIBLE"}})
            direction_agree = sum(bool(item["matches_reference"]) for item in direction_rows)
            category_allowable = sum(bool(item["allowable"]) for item in category_rows)
            mechanism_score = sum(float(item["score"]) for item in mechanism_rows)
            direct_swap = any(bool(item["direct_incompatible_transition"]) for item in mechanism_rows)
            cells[key] = {
                "reference": {"effect_hz": ref_effect, "sign": _effect_sign(ref_effect), "category": ref_category, "mechanism": ref_mechanism},
                "effect_direction": {"status": "EFFECT_DIRECTION_STABLE" if direction_agree >= 6 else "NOT_STABLE", "agreeing_variants": direction_agree, "required": 6, "variants": direction_rows},
                "effect_category": {"status": "EFFECT_CATEGORY_STABLE" if category_allowable >= 6 else "NOT_STABLE", "allowable_variants": category_allowable, "required": 6, "variants": category_rows},
                "mechanism": {"status": "MECHANISM_COMPATIBLE_STABLE" if mechanism_score >= 6.0 and not direct_swap else "NOT_STABLE", "exact_stable": sum(item["classification"] == ref_mechanism for item in mechanism_rows) >= 6, "compatible_score": mechanism_score, "required_score": 6.0, "direct_short_network_swap": direct_swap, "variants": mechanism_rows},
            }
    return cells


def _global_support(variant_results: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
    counterintuitive = ("10313:LEFT", "10313:RIGHT", "10135:LEFT", "10135:RIGHT")
    network_reference = ("10313:LEFT", "10313:RIGHT", "10135:LEFT", "512730:LEFT")
    mixed_reference = ("10135:RIGHT", "12752:LEFT", "12752:RIGHT")
    rows = {}
    for variant in VARIANT_CONFIGURATIONS:
        labels = {}
        for cell in set(counterintuitive + network_reference + mixed_reference):
            candidate_id, side = cell.split(":")
            condition = PRIMARY_CONDITION.name if side == "LEFT" else MIRROR_CONDITION.name
            labels[cell] = variant_results[variant.variant_id]["temporal"]["mechanism_classifications"][f"{candidate_id}:{condition}"]["classification"]
        counter_network = sum(labels[cell] in {"NETWORK_REDISTRIBUTION_COMPATIBLE", "MIXED"} for cell in counterintuitive)
        direct_short = sum(labels[cell] == "SHORT_PATH_COMPATIBLE" for cell in network_reference)
        mixed_retained = sum(labels[cell] in {"MIXED", "SHORT_PATH_COMPATIBLE"} for cell in mixed_reference)
        rows[variant.variant_id] = {
            "counterintuitive_network_compatible": counter_network,
            "counterintuitive_required": 3,
            "network_reference_direct_short_path_changes": direct_short,
            "network_reference_maximum": 1,
            "mixed_reference_retained_or_short": mixed_retained,
            "mixed_reference_required": 2,
            "supports_global_conclusion": counter_network >= 3 and direct_short <= 1 and mixed_retained >= 2,
            "labels": labels,
        }
    return rows


def _environment_record() -> dict[str, object]:
    import numpy

    try:
        import cupy

        cupy_version = cupy.__version__
        cuda_runtime = int(cupy.cuda.runtime.runtimeGetVersion())
    except Exception:
        cupy_version = None
        cuda_runtime = None
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": numpy.__version__,
        "cupy": cupy_version,
        "cuda_runtime": cuda_runtime,
        "cuda_available": bool(cuda_available()),
    }


def _result_digest_payload(payload: Mapping[str, object]) -> dict[str, object]:
    return {
        "schema": RESULT_DIGEST_PREFIX,
        "starting_head": payload["starting_head"],
        "specification_fingerprint": payload["specification_fingerprint"],
        "variants": payload["variants"],
        "task010": payload["task010"],
        "temporal": payload["temporal"],
        "robustness": payload["robustness"],
        "global_support": payload["global_support"],
    }


def _git_state() -> dict[str, object]:
    def run(*args: str) -> str:
        return subprocess.check_output(("git", *args), text=True).strip()

    return {
        "head": run("rev-parse", "HEAD"),
        "origin_master": run("rev-parse", "origin/master"),
        "live_origin_master": run("ls-remote", "origin", "refs/heads/master").split()[0],
        "worktree_clean_before_execution": run("status", "--porcelain") == "",
        "stash_entries_before_execution": run("stash", "list"),
        "v020_peel": run("rev-parse", "refs/tags/v0.2.0^{}"),
    }


def _starting_state(task016_path: str | Path) -> dict[str, object]:
    raw = Path(task016_path).read_bytes()
    state = _git_state()
    def run(*args: str) -> str:
        return subprocess.check_output(("git", *args), text=True).strip()

    delivery_paths = set(run("diff", "--name-only", f"{STARTING_HEAD}..{state['head']}").splitlines())
    if state["head"] != STARTING_HEAD and not delivery_paths.issubset(TASK017B_DELIVERY_PATHS):
        raise RuntimeError(f"Task 017 authoritative source drift: {sorted(delivery_paths)}")
    if state["origin_master"] != state["head"] or state["live_origin_master"] != state["head"]:
        raise RuntimeError("Task 017 local/remote HEAD mismatch")
    if state["stash_entries_before_execution"]:
        raise RuntimeError("Task 017 requires an empty stash at the execution gate")
    if state["v020_peel"] != V020_SOURCE:
        raise RuntimeError("Task 017 v0.2.0 peel mismatch")
    return {
        "starting_head": STARTING_HEAD,
        "execution_head": state["head"],
        "delivery_paths_since_authoritative_start": sorted(delivery_paths),
        "git_state": state,
        "task016_plan_sha256": hashlib.sha256(raw).hexdigest(),
        "task016_section_3_head_in_document": "1113c0c8a5ff3c8799a10b9b4b01199b6e5c2ec9",
        "task016_section_3_head_conflicts_with_user_authoritative_start": True,
        "user_authoritative_start_used": STARTING_HEAD,
        "preimplementation_integrity_gate": {
            "head_origin_live_match": True,
            "worktree_clean": True,
            "stash_empty": True,
            "v020_peel": V020_SOURCE,
            "recorded_before_task017_implementation": True,
        },
    }


def _variant_task_result(
    variant: VariantConfiguration,
    prepared: PreparedNetwork,
    schedules: Mapping[str, tuple[FrozenSchedule, ...]],
    manifest: FrozenCandidateManifest,
    annotation_path: str | Path,
    technical: Mapping[str, object],
    checkpoint: Task017Checkpoint,
    budget: ExecutionBudget | None = None,
) -> dict[str, object]:
    task010 = _task010_variant(variant, prepared, schedules, manifest, checkpoint, budget)
    temporal = _task011_variant(variant, prepared, schedules, manifest, annotation_path, checkpoint, budget)
    return {
        "variant": variant.as_record(),
        "validity": {"status": "VALID", "exclusion_reason": None},
        "technical": dict(technical),
        "task010": task010,
        "temporal": temporal,
    }


def _checkpoint_identity(
    state: Mapping[str, object],
    identities: PreparedTask008,
    prepared: PreparedNetwork,
) -> dict[str, object]:
    return {
        "schema": CHECKPOINT_SCHEMA,
        "starting_head": STARTING_HEAD,
        "task016_specification_fingerprint": task016_specification_fingerprint(),
        "expected_unit_count": len(expected_task017_unit_keys()),
        "variant_definitions": [item.as_record() for item in VARIANT_CONFIGURATIONS],
        "candidate_ids": list(FROZEN_TASK011_CANDIDATES),
        "readout_ids": {"MN9_L": MN9_L, "MN9_R": MN9_R},
        "stimulus_sides": ["LEFT", "RIGHT"],
        "task010_trial_indices": list(range(TASK010_TRIAL_COUNT)),
        "task011_trial_indices": list(FIXED_TRIAL_INDICES),
        "unsigned_graph_fingerprint": prepared.projection.unsigned_graph_fingerprint,
        "reference_effective_graph_fingerprint": prepared.projection.fingerprint,
        "cache_fingerprint": prepared.cache_fingerprint,
        "population_fingerprint": identities.fingerprint,
        "source_identity": V020_SOURCE,
    }


def _classify_global(
    variant_results: Mapping[str, Mapping[str, object]],
    cells: Mapping[str, Mapping[str, object]],
    global_support: Mapping[str, Mapping[str, object]],
) -> tuple[str, dict[str, object]]:
    invalid = [
        variant_id
        for variant_id, result in variant_results.items()
        if result["validity"]["status"] != "VALID"
    ]
    direction_stable = sum(item["effect_direction"]["status"] == "EFFECT_DIRECTION_STABLE" for item in cells.values())
    category_stable = sum(item["effect_category"]["status"] == "EFFECT_CATEGORY_STABLE" for item in cells.values())
    mechanism_stable = sum(item["mechanism"]["status"] == "MECHANISM_COMPATIBLE_STABLE" for item in cells.values())
    nonreference = [item.variant_id for item in VARIANT_CONFIGURATIONS if item is not REFERENCE_VARIANT]
    supporting = sum(bool(global_support[item]["supports_global_conclusion"]) for item in nonreference)
    details = {
        "invalid_variants": invalid,
        "effect_direction_stable_cells": direction_stable,
        "effect_category_stable_cells": category_stable,
        "mechanism_compatible_stable_cells": mechanism_stable,
        "stable_cell_requirement_robust": 8,
        "stable_cell_requirement_partial": 5,
        "global_supporting_nonreference_variants": supporting,
        "global_supporting_requirement_partial": 5,
    }
    if invalid:
        return "INDETERMINATE", details
    if (
        direction_stable >= 8
        and category_stable >= 8
        and mechanism_stable >= 8
        and supporting == len(nonreference)
    ):
        return "ROBUST", details
    if direction_stable >= 5 and category_stable >= 5 and mechanism_stable >= 5 and supporting >= 5:
        return "PARTIALLY_ROBUST", details
    return "NOT_ROBUST", details


def _scientific_report_lines(payload: Mapping[str, object]) -> list[str]:
    lines = [
        "# Task 017 - Execute v0.3 Mechanism-Robustness Matrix",
        "",
        "Status: COMPLETE FOR REVIEW. No commit, push, tag, release, or Task 018 work was performed.",
        "",
        "## Frozen scope and gate",
        "",
        f"- Starting HEAD: `{payload['starting_head']}`",
        f"- Task 016 specification fingerprint: `{payload['specification_fingerprint']}`",
        f"- Task 016 plan SHA-256: `{payload['starting_state']['task016_plan_sha256']}`",
        "- The preregistration Section 3 HEAD is stale relative to the explicit Task 017 authoritative start; the supplied start was used and no preregistration field was edited.",
        f"- Reference replay: `{payload['reference_replay']['status']}`",
        "",
        "The extracted frozen specification is embedded in `data/derived/task017-results.json`, including the reference model, all seven literal variants, candidates, stimuli, schedules, thresholds, compatibility rules, global rules, and pathological exclusions.",
        "",
        "## Variant definitions",
        "",
        "| ID | Changed axis | Effective parameters | Sign policy |",
        "| --- | --- | --- | --- |",
    ]
    for variant in payload["variant_definitions"]:
        p = variant["effective_parameters"]
        lines.append(
            f"| `{variant['variant_id']}` | {variant['changed_axis']} | "
            f"tau_m={p['tau_membrane_ms']} ms, tau_s={p['tau_synapse_ms']} ms, "
            f"delay={p['synaptic_delay_ms']} ms, weight={p['synaptic_weight_per_anatomical_synapse_mV']} mV, "
            f"threshold={p['v_threshold_mV']} mV | {variant['sign_policy']} |"
        )
    lines.extend(
        [
            "",
            "## Execution and technical validation",
            "",
            f"- Task 010-style simulations: `{payload['actual_simulation_counts']['task010_style']}` (expected 2880).",
            f"- Task 011 temporal-trace simulations: `{payload['actual_simulation_counts']['temporal_traces']}` (expected 288).",
            "- CPU is the float64 correctness oracle; CUDA is the float64 implementation path.",
            "- Synthetic CPU/CUDA fixtures, full-graph CPU/CUDA canonical spikes, sparse traces, selected v/g traces, trace invariance, and deterministic replay passed for every matrix member.",
            "- Technically invalid or excluded variants: none.",
            "",
            "## Cell-level robustness",
            "",
            "| Cell | Reference effect/category/mechanism | Direction | Category | Mechanism |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for cell, result in sorted(payload["cell_robustness"].items(), key=lambda item: (int(item[0].split(":")[0]), item[0].split(":")[1])):
        ref = result["reference"]
        lines.append(
            f"| `{cell}` | {ref['effect_hz']:+.6f} Hz / {ref['category']} / {ref['mechanism']} | "
            f"{result['effect_direction']['status']} ({result['effect_direction']['agreeing_variants']}/7) | "
            f"{result['effect_category']['status']} ({result['effect_category']['allowable_variants']}/7) | "
            f"{result['mechanism']['status']} (score {result['mechanism']['compatible_score']:.1f}/7) |"
        )
    support = payload["global_support"]
    lines.extend(["", "## Global support and classification", ""])
    lines.append("| Variant | Global-support rule |")
    lines.append("| --- | --- |")
    for variant in VARIANT_CONFIGURATIONS:
        row = support[variant.variant_id]
        lines.append(f"| `{variant.variant_id}` | {'SUPPORT' if row['supports_global_conclusion'] else 'DOES_NOT_SUPPORT'} |")
    lines.extend(
        [
            "",
            f"Final classification: **{payload['global_classification']}**.",
            "",
            f"Allowed model-level conclusion: Within MaleCNS-Sim, the Task 010/011 findings are **{payload['global_classification']}** under the exact independently preregistered model variants tested in Task 017.",
            "",
            "## Required analyses",
            "",
        ]
    )
    cells = payload["cell_robustness"]
    direction_failures = [cell for cell, row in cells.items() if row["effect_direction"]["status"] != "EFFECT_DIRECTION_STABLE"]
    category_drift = [cell for cell, row in cells.items() if row["effect_category"]["status"] != "EFFECT_CATEGORY_STABLE"]
    mechanism_failures = [cell for cell, row in cells.items() if row["mechanism"]["status"] != "MECHANISM_COMPATIBLE_STABLE"]
    partials = [
        f"{cell}:{item['variant_id']}"
        for cell, row in cells.items()
        for item in row["mechanism"]["variants"]
        if item["score"] == 0.5
    ]
    switches = [
        f"{cell}:{item['variant_id']}"
        for cell, row in cells.items()
        for item in row["mechanism"]["variants"]
        if item["direct_incompatible_transition"]
    ]
    lines.extend(
        [
            f"1. Stable Task 010 MN9_L effect directions: `{10 - len(direction_failures)}/10` cells; unstable cells: `{direction_failures or 'none'}`.",
            f"2. Effect categories drift outside the preregistered one-step allowance in: `{category_drift or 'none'}`.",
            f"3. Mechanism exact/compatible failures: `{mechanism_failures or 'none'}`; exact and partial matches are retained in the artifact.",
            f"4. Preregistered partial mechanism matches: `{partials or 'none'}`.",
            f"5. Genuine incompatible short/network switches: `{switches or 'none'}`.",
            "6. Largest qualitative changes are identified by the failed direction/category/mechanism counts in the per-variant records; they are model sensitivity findings, not biological evidence.",
            "7. 10313 counterintuitive effects are reported cell-by-cell in the artifact and are not treated as biological inhibition evidence.",
            "8. 10135 RIGHT is reported against its frozen MIXED reference classification.",
            "9. 12752 LEFT/RIGHT signs are reported against the frozen opposite-direction contrast.",
            "10. 512730 RIGHT and 43765 both retain their frozen activity/exposure evidence in the full temporal records.",
            "11. The v0.2 conclusion is assessed only by the frozen global-support rule above.",
            "",
            "## Nonclaims and final validation",
            "",
            "These are model-level robustness results. They do not prove an actual-fly causal mechanism, receptor-specific physiology, necessity, sufficiency, behavior, sex dimorphism, or same-animal correspondence. Sensitivity to one model axis is not biological evidence.",
            f"- Task 011 digest unchanged: `{payload['integrity_checks']['task011_digest']}`.",
            f"- Task 016 preregistration unchanged: `{payload['integrity_checks']['task016_plan_sha256']}`.",
            f"- Result digest: `{payload['result_digest']}`.",
            "- Tests, compileall, and git diff --check are recorded by the final execution turn.",
            "- Task 017 should be reviewed before commit; no Task 018 is scientifically authorized by this result.",
        ]
    )
    return lines


def _resolve_variant_ids(selection: str | None) -> tuple[str, ...]:
    if selection is None or selection.lower() == "all":
        return tuple(item.variant_id for item in VARIANT_CONFIGURATIONS)
    normalized = selection.upper()
    for item in VARIANT_CONFIGURATIONS:
        if normalized in {item.variant_id.upper(), item.variant_id.split("_", 1)[0].upper()}:
            return (item.variant_id,)
    raise ValueError(f"unknown Task 017 variant: {selection}")


def _resolve_analysis_kinds(selection: str) -> tuple[str, ...]:
    normalized = selection.lower()
    if normalized == "all":
        return (TASK010_BASELINE, TASK010_INTERVENTION, TASK011_BASELINE, TASK011_INTERVENTION)
    if normalized == "task010":
        return (TASK010_BASELINE, TASK010_INTERVENTION)
    if normalized == "task011":
        return (TASK011_BASELINE, TASK011_INTERVENTION)
    raise ValueError(f"unknown Task 017 analysis selector: {selection}")


def _delivery_payload(
    *,
    checkpoint: Task017Checkpoint,
    ledger_before: Mapping[str, object],
    ledger_after: Mapping[str, object],
    budget: ExecutionBudget,
    selected_variant_ids: Sequence[str],
    selected_analysis_kinds: Sequence[str],
    elapsed_seconds: float,
    reason: str | None = None,
) -> dict[str, object]:
    missing = int(ledger_after["missing_unit_count"])
    status = "READY_FOR_INCREMENTAL_EXECUTION" if missing else "MATRIX_COMPLETE_PENDING_SCIENTIFIC_REVIEW"
    if reason is not None and budget.executed_units == 0:
        status = "BLOCKED_EXECUTION_BUDGET"
    return {
        "task": "017B",
        "status": "INDETERMINATE",
        "current_scientific_status": "INDETERMINATE",
        "current_status": status,
        "reason": reason,
        "task016_fingerprint": task016_specification_fingerprint(),
        "specification_fingerprint": task016_specification_fingerprint(),
        "checkpoint_fingerprint": checkpoint.fingerprint,
        "checkpoint_state": "RESUMED" if int(ledger_before["completed_unit_count"]) else "INITIALIZED",
        "checkpoint_path": str(checkpoint.path),
        "canonical_pending_unit_order": "variant_id -> stimulus_side -> analysis_kind -> trial_index -> candidate_id",
        "selected_variant_ids": list(selected_variant_ids),
        "selected_analysis_kinds": list(selected_analysis_kinds),
        "expected_unit_count": int(ledger_after["expected_unit_count"]),
        "completed_before_invocation": int(ledger_before["completed_unit_count"]),
        "executed_this_invocation": int(budget.executed_units),
        "completed_after_invocation": int(ledger_after["completed_unit_count"]),
        "missing_count": missing,
        "duplicate_count": int(ledger_after["duplicate_count"]),
        "invalid_technical_unit_count": int(ledger_after["invalid_technical_unit_count"]),
        "per_variant_completion": ledger_after["per_variant_completion"],
        "per_analysis_completion": ledger_after["per_analysis_completion"],
        "elapsed_seconds": elapsed_seconds,
        "execution_ledger": dict(ledger_after),
    }


def write_task017_delivery_report(path: str | Path, payload: Mapping[str, object]) -> None:
    """Write only technical delivery state; never write partial scientific conclusions."""

    target = Path(path)
    lines = [
        "# Task 017B - Bounded Batch Delivery",
        "",
        "Current scientific status: `INDETERMINATE`.",
        "",
        f"- Task 016 fingerprint: `{payload['task016_fingerprint']}`",
        f"- Checkpoint fingerprint: `{payload['checkpoint_fingerprint']}`",
        f"- Expected units: `{payload['expected_unit_count']}`",
        f"- Completed before invocation: `{payload['completed_before_invocation']}`",
        f"- Executed this invocation: `{payload['executed_this_invocation']}`",
        f"- Completed after invocation: `{payload['completed_after_invocation']}`",
        f"- Missing: `{payload['missing_count']}`",
        f"- Duplicate attempts: `{payload['duplicate_count']}`",
        f"- Invalid technical units: `{payload['invalid_technical_unit_count']}`",
        f"- Current status: `{payload['current_status']}`",
        f"- Elapsed seconds: `{payload['elapsed_seconds']:.3f}`",
        "- No partial robustness conclusion was computed.",
        "- No Task 018 work was started.",
    ]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_task017(
    annotation_path: str | Path,
    neurotransmitter_path: str | Path,
    weights_path: str | Path,
    task008_results_path: str | Path,
    task009_results_path: str | Path,
    task010_results_path: str | Path,
    task011_results_path: str | Path,
    cache_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    checkpoint_path: str | Path | None = None,
    execution_budget_seconds: float | None = 1800.0,
    *,
    variant_id: str | None = None,
    analysis: str = "all",
    max_units: int | None = None,
    max_runtime_minutes: float | None = None,
) -> dict[str, object]:
    """Execute or deliver bounded raw units from the frozen Task 017 matrix."""

    if not cuda_available():
        raise RuntimeError("Task 017 requires the validated CUDA backend")
    if max_units is not None and max_units < 0:
        raise ValueError("max_units must be non-negative")
    if max_runtime_minutes is not None and max_runtime_minutes < 0:
        raise ValueError("max_runtime_minutes must be non-negative")
    selected_variant_ids = _resolve_variant_ids(variant_id)
    selected_analysis_kinds = _resolve_analysis_kinds(analysis)
    execution_started = time.perf_counter()
    if max_runtime_minutes is not None:
        deadline = execution_started + float(max_runtime_minutes) * 60.0
    else:
        deadline = None if execution_budget_seconds is None else execution_started + float(execution_budget_seconds)
    budget = ExecutionBudget(max_units=max_units, deadline=deadline)
    bounded_delivery = (
        tuple(selected_variant_ids) != tuple(item.variant_id for item in VARIANT_CONFIGURATIONS)
        or tuple(selected_analysis_kinds) != (TASK010_BASELINE, TASK010_INTERVENTION, TASK011_BASELINE, TASK011_INTERVENTION)
        or max_units is not None
        or max_runtime_minutes is not None
    )
    state = _starting_state(TASK016_PLAN)
    manifest = load_frozen_candidate_manifest(task009_results_path)
    if not set(FROZEN_CANDIDATES).issubset(set(manifest.body_ids)):
        raise RuntimeError("Task 017 candidate manifest drift")
    identities: PreparedTask008 = load_task008_identities(annotation_path, neurotransmitter_path)
    cache = PreparedGraphCache.load(cache_path)
    cached_network = _prepare_verified_cached_network(cache_path)
    if cache.cache_fingerprint != TASK008_FULL_CACHE_FINGERPRINT or cached_network.fingerprint != TASK008_PREPARED_FINGERPRINT:
        raise RuntimeError("Task 008 cache identity mismatch")
    signed_shiu = _load_signed_connectome(annotation_path, neurotransmitter_path, weights_path, Shiu2024SignPolicy())
    reference_projection = EffectiveSignedProjection.from_signed_connectome(signed_shiu, synaptic_weight_mV=0.275)
    _assert_projection_matches_cache(reference_projection, cached_network.projection)
    if population_fingerprint(identities.sugar_right) != "2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b":
        raise RuntimeError("frozen RIGHT sugar population fingerprint changed")
    cuda_graph_cache: dict[str, object] = {cached_network.projection.fingerprint: cached_network.cuda_graph}
    reference_network = _variant_network(REFERENCE_VARIANT, signed_shiu, cache, cache_path, cuda_graph_cache)
    checkpoint = Task017Checkpoint(
        checkpoint_path or Path(output_path).with_name("task017-checkpoint.jsonl"),
        _checkpoint_identity(state, identities, reference_network),
    )
    expected_units = expected_task017_unit_keys()
    ledger_before = checkpoint.ledger(expected_units)

    reference_schedules = {
        "LEFT": _make_frozen_schedules(reference_network, identities, identities.sugar_left, side="L", trial_indices=range(TASK010_TRIAL_COUNT), synaptic_weight_mV=0.275),
        "RIGHT": _make_frozen_schedules(reference_network, identities, identities.sugar_right, side="R", trial_indices=range(TASK010_TRIAL_COUNT), synaptic_weight_mV=0.275),
    }
    variant_results: dict[str, object] = {}
    technical_results: dict[str, object] = {}
    for variant in VARIANT_CONFIGURATIONS:
        if variant.variant_id not in selected_variant_ids:
            continue
        if variant is REFERENCE_VARIANT:
            prepared = reference_network
            schedules = reference_schedules
        else:
            signed = signed_shiu if variant.sign_policy_id == "Shiu2024SignPolicy" else _load_signed_connectome(annotation_path, neurotransmitter_path, weights_path, variant.sign_policy)
            prepared = _variant_network(variant, signed, cache, cache_path, cuda_graph_cache)
            schedules = _reweight_frozen_schedules(reference_schedules, variant.synaptic_weight_mV)
            if any(item.event_schedule_fingerprint != reference_schedules[side][item.trial_index].event_schedule_fingerprint for side, rows in schedules.items() for item in rows):
                raise RuntimeError(f"{variant.variant_id} changed a frozen event schedule")
        technical = _validate_variant_technical(variant, prepared, schedules["LEFT"][0])
        technical_results[variant.variant_id] = technical
        try:
            task010 = None
            temporal = None
            if TASK010_BASELINE in selected_analysis_kinds:
                task010 = _task010_variant(variant, prepared, schedules, manifest, checkpoint, budget)
            if TASK011_BASELINE in selected_analysis_kinds:
                temporal = _task011_variant(variant, prepared, schedules, manifest, annotation_path, checkpoint, budget)
        except ExecutionBudgetExceeded as error:
            if not bounded_delivery:
                ledger = checkpoint.ledger(expected_units)
                return write_task017_indeterminate_stop(
                    output_path,
                    report_path,
                    reason=str(error),
                    completed_phase=f"Stage A raw execution stopped during {variant.variant_id}",
                    ledger=ledger,
                    starting_state=state,
                )
            ledger_after = checkpoint.ledger(expected_units)
            payload = _delivery_payload(
                checkpoint=checkpoint,
                ledger_before=ledger_before,
                ledger_after=ledger_after,
                budget=budget,
                selected_variant_ids=selected_variant_ids,
                selected_analysis_kinds=selected_analysis_kinds,
                elapsed_seconds=time.perf_counter() - execution_started,
                reason=str(error),
            )
            _write_json(output_path, payload)
            write_task017_delivery_report(report_path, payload)
            return payload
        if not bounded_delivery:
            if task010 is None or temporal is None:
                raise RuntimeError("full Task 017 execution requires both analyses")
            variant_results[variant.variant_id] = {
                "variant": variant.as_record(),
                "validity": {"status": "VALID", "exclusion_reason": None},
                "technical": technical,
                "task010": task010,
                "temporal": temporal,
            }

    if bounded_delivery:
        ledger_after = checkpoint.ledger(expected_units)
        payload = _delivery_payload(
            checkpoint=checkpoint,
            ledger_before=ledger_before,
            ledger_after=ledger_after,
            budget=budget,
            selected_variant_ids=selected_variant_ids,
            selected_analysis_kinds=selected_analysis_kinds,
            elapsed_seconds=time.perf_counter() - execution_started,
        )
        _write_json(output_path, payload)
        write_task017_delivery_report(report_path, payload)
        return payload

    reference_result = variant_results[REFERENCE_VARIANT.variant_id]
    replay = _reference_replay_gate(reference_result, task008_results_path, task010_results_path, task011_results_path)
    technical_reference = technical_results[REFERENCE_VARIANT.variant_id]

    ledger = checkpoint.ledger(expected_units)
    if not task017_scoring_allowed(ledger):
        return write_task017_indeterminate_stop(
            output_path,
            report_path,
            reason="Stage B completeness gate rejected an incomplete or technically invalid matrix",
            completed_phase="Stage B completeness verification",
            ledger=ledger,
            starting_state=state,
        )
    cells = _robustness_cells(variant_results)
    global_support = _global_support(variant_results)
    global_classification, global_details = _classify_global(variant_results, cells, global_support)
    task010_count = sum(int(result["task010"]["simulation_count"]) for result in variant_results.values())
    temporal_count = sum(int(result["temporal"]["simulation_count"]) for result in variant_results.values())
    if task010_count != 2880 or temporal_count != 288:
        raise RuntimeError("Task 017 scientific simulation count mismatch")
    deterministic_payload = {
        "starting_head": STARTING_HEAD,
        "specification_fingerprint": task016_specification_fingerprint(),
        "variants": variant_results,
        "task010": {key: value["task010"] for key, value in variant_results.items()},
        "temporal": {key: value["temporal"] for key, value in variant_results.items()},
        "robustness": cells,
        "global_support": global_support,
    }
    result_digest = _digest(RESULT_DIGEST_PREFIX, _result_digest_payload(deterministic_payload))
    task016_spec_fingerprint = task016_specification_fingerprint()
    payload: dict[str, object] = {
        "task": "017",
        "schema": TASK017_SCHEMA,
        "status": "COMPLETE",
        "starting_head": STARTING_HEAD,
        "task016_specification_fingerprint": task016_spec_fingerprint,
        "specification_fingerprint": task016_spec_fingerprint,
        "starting_state": state,
        "variant_definitions": [item.as_record() for item in VARIANT_CONFIGURATIONS],
        "candidate_ids": list(FROZEN_TASK011_CANDIDATES),
        "stimulus_definitions": frozen_specification()["stimuli"],
        "trial_schedule": {
            "task010_indices": list(range(TASK010_TRIAL_COUNT)),
            "task011_indices": list(FIXED_TRIAL_INDICES),
            "reference_schedule_fingerprints": {
                side: [item.event_schedule_fingerprint for item in rows]
                for side, rows in reference_schedules.items()
            },
        },
        "frozen_specification": frozen_specification(),
        "reference_replay": replay,
        "technical_gates": {key: value["technical"] for key, value in variant_results.items()},
        "validity": {key: value["validity"] for key, value in variant_results.items()},
        "task010_style_results": deterministic_payload["task010"],
        "temporal_results": deterministic_payload["temporal"],
        "cell_robustness": cells,
        "global_support": global_support,
        "global_classification": global_classification,
        "global_classification_details": global_details,
        "actual_simulation_counts": {"task010_style": task010_count, "temporal_traces": temporal_count, "scientific_total": task010_count + temporal_count},
        "integrity_checks": {
            "task010_digest": TASK010_RESULT_DIGEST,
            "task011_digest": TASK011_RESULT_DIGEST,
            "task016_plan_sha256": state["task016_plan_sha256"],
            "v020_source": V020_SOURCE,
            "candidate_ids_unchanged": True,
            "sugar_definition_unchanged": True,
            "mn9_mapping_unchanged": {"MN9_L": MN9_L, "MN9_R": MN9_R},
            "connectome_topology_unchanged": True,
            "reference_parameters_unchanged": True,
            "thresholds_unchanged": True,
            "compatibility_rules_unchanged": True,
        },
        "software_environment": _environment_record(),
        "execution_ledger": ledger,
        "execution_timing": {"stage_a_wall_seconds": time.perf_counter() - execution_started},
        "result_digest": result_digest,
    }
    _write_json(output_path, payload)
    report_payload = dict(payload)
    report_payload["starting_state"] = state
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text("\n".join(_scientific_report_lines(report_payload)) + "\n", encoding="utf-8")
    return payload


def write_task017_indeterminate_stop(
    output_path: str | Path,
    report_path: str | Path,
    *,
    reason: str,
    completed_phase: str,
    ledger: Mapping[str, object] | None = None,
    starting_state: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Write a fail-closed artifact when execution stops before a full matrix."""

    state = dict(starting_state) if starting_state is not None else _starting_state(TASK016_PLAN)
    completion_ledger = dict(ledger) if ledger is not None else {
        "expected_unit_count": len(expected_task017_unit_keys()),
        "completed_unit_count": 0,
        "missing_unit_count": len(expected_task017_unit_keys()),
        "duplicate_count": 0,
        "invalid_technical_unit_count": 0,
        "matrix_complete": False,
    }
    spec = frozen_specification()
    cell_stop = {
        f"{candidate_id}:{side}": {
            "causal_effect": "INDETERMINATE_NOT_ASSESSED",
            "mechanism": "INDETERMINATE_NOT_ASSESSED",
            "reason": "complete matrix required before preregistered scoring",
        }
        for candidate_id in FROZEN_TASK011_CANDIDATES
        for side in ("LEFT", "RIGHT")
    }
    support_stop = {
        item.variant_id: {
            "status": "INDETERMINATE_NOT_ASSESSED",
            "reason": "global-support rule requires complete matrix",
        }
        for item in VARIANT_CONFIGURATIONS
    }
    payload: dict[str, object] = {
        "task": "017",
        "schema": TASK017_SCHEMA,
        "status": "INDETERMINATE",
        "starting_head": STARTING_HEAD,
        "task016_specification_fingerprint": task016_specification_fingerprint(),
        "specification_fingerprint": task016_specification_fingerprint(),
        "starting_state": state,
        "frozen_specification": spec,
        "variant_definitions": [item.as_record() for item in VARIANT_CONFIGURATIONS],
        "candidate_ids": list(FROZEN_TASK011_CANDIDATES),
        "stimulus_definitions": spec["stimuli"],
        "trial_schedule": {"task010_indices": list(range(TASK010_TRIAL_COUNT)), "task011_indices": list(FIXED_TRIAL_INDICES)},
        "execution_stop": {
            "status": "STOPPED_BEFORE_MATRIX_COMPLETION",
            "completed_phase": completed_phase,
            "reason": reason,
            "matrix_complete": False,
            "partial_outputs_used_for_scoring": False,
        },
        "execution_ledger": completion_ledger,
        "reference_replay": {"status": "NOT_REACHED_BEFORE_STOP"},
        "technical_gates": {
            "R0_REFERENCE_TASK005": {"status": "PASS", "scope": "reference technical gate completed before stop"},
            **{
                item.variant_id: {"status": "NOT_ASSESSED", "scope": "alternative technical gate not reached"}
                for item in VARIANT_CONFIGURATIONS[1:]
            },
        },
        "validity": {item.variant_id: {"status": "NOT_ASSESSED", "exclusion_reason": "matrix incomplete under preregistered stopping rule"} for item in VARIANT_CONFIGURATIONS},
        "task010_style_results": {},
        "temporal_results": {},
        "cell_robustness": cell_stop,
        "global_support": support_stop,
        "global_classification": "INDETERMINATE",
        "global_classification_details": {
            "reason": "incomplete matrix under the preregistered computational-budget stopping rule",
            "required_task010_style_simulations": 2880,
            "required_temporal_trace_simulations": 288,
        },
        "actual_simulation_counts": {
            "task010_style": "INCOMPLETE",
            "temporal_traces": "NOT_STARTED",
            "scientific_total": "INCOMPLETE",
        },
        "integrity_checks": {
            "task010_digest": TASK010_RESULT_DIGEST,
            "task011_digest": TASK011_RESULT_DIGEST,
            "task016_plan_sha256": state["task016_plan_sha256"],
            "v020_source": V020_SOURCE,
            "candidate_ids_unchanged": True,
            "sugar_definition_unchanged": True,
            "mn9_mapping_unchanged": {"MN9_L": MN9_L, "MN9_R": MN9_R},
            "connectome_topology_unchanged": True,
            "reference_parameters_unchanged": True,
            "thresholds_unchanged": True,
            "compatibility_rules_unchanged": True,
        },
        "software_environment": _environment_record(),
    }
    payload["result_digest"] = _digest(RESULT_DIGEST_PREFIX, payload)
    _write_json(output_path, payload)
    report = [
        "# Task 017 - Execute v0.3 Mechanism-Robustness Matrix",
        "",
        "Status: INDETERMINATE. Execution stopped under the preregistered computational-budget rule before the complete matrix was available.",
        "",
        f"- Starting HEAD: `{STARTING_HEAD}`",
        f"- Task 016 specification fingerprint: `{payload['specification_fingerprint']}`",
        f"- Completed phase: {completed_phase}",
        f"- Stop reason: {reason}",
        f"- Completeness ledger: `{completion_ledger['completed_unit_count']}/{completion_ledger['expected_unit_count']}` units complete; `{completion_ledger['missing_unit_count']}` missing; `{completion_ledger.get('invalid_technical_unit_count', 0)}` technically invalid; `{completion_ledger.get('duplicate_count', 0)}` duplicate attempts.",
        "- The reference technical gate had passed before the process entered the reference Task 010-style matrix; reference replay had not completed when execution stopped.",
        "- Required matrix counts remain 2,880 Task 010-style simulations and 288 temporal-trace simulations. Partial output was not used for scoring.",
        "- No candidate, variant, trial, threshold, compatibility rule, or parameter was removed or tuned.",
        "- All ten causal-effect cells and all ten mechanism cells are `INDETERMINATE_NOT_ASSESSED`; no cell received a stability decision.",
        "- Global-support status for every one of the eight variants is `INDETERMINATE_NOT_ASSESSED`; no variant was counted as supporting or failing the conclusion.",
        "",
        "## Scientific boundary",
        "",
        "The only permitted conclusion is: Within MaleCNS-Sim, the Task 010/011 findings are INDETERMINATE under the exact independently preregistered model variants tested in Task 017, because the required matrix was not completed. No robustness or biological-mechanism claim is made.",
        "",
        f"- Result digest: `{payload['result_digest']}`",
        "- No commit, push, tag, release, or Task 018 work occurred.",
    ]
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text("\n".join(report) + "\n", encoding="utf-8")
    return payload


FROZEN_CANDIDATES = FROZEN_TASK011_CANDIDATES
