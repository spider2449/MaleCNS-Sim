"""Versioned, strictly decoded application contracts and scientific identities."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, fields, is_dataclass
from importlib.metadata import version
from typing import Any, TypeVar
from uuid import UUID

from malecns_sim.dynamics.lif import LIFParameters
from malecns_sim.data.neurotransmitter import NeurotransmitterResolutionPolicy
from malecns_sim.sign import Shiu2024SignPolicy

from .errors import ApplicationError, ErrorCode

EXPERIMENT_SCHEMA = "application-experiment-v1"
RESULT_SCHEMA = "application-result-v1"
EVENT_SCHEMA = "application-event-v1"
MAX_DURATION_MS = 10_000.0
MAX_TRACES = 16
MAX_SPIKES = 1_000_000
ALLOWED_FREQUENCIES_HZ = (10.0, 25.0, 50.0, 100.0, 150.0, 200.0)


def _finite(value: Any, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ApplicationError(ErrorCode.INVALID_SPEC, f"{name} must be a finite number")
    if positive and value <= 0:
        raise ApplicationError(ErrorCode.INVALID_SPEC, f"{name} must be positive")
    return float(value)


def _hex(value: str, name: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ApplicationError(ErrorCode.INVALID_SPEC, f"{name} must be lowercase SHA-256")


def _ids(values: tuple[int, ...], name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(values, tuple) or (not values and not allow_empty) or any(type(i) is not int or i < 0 for i in values):
        raise ApplicationError(ErrorCode.INVALID_SPEC, f"{name} must contain nonnegative integer IDs")
    if values != tuple(sorted(set(values))):
        raise ApplicationError(ErrorCode.INVALID_SPEC, f"{name} must be unique and ordered")


def _grid(value: float, dt: float, name: str) -> None:
    if not math.isclose(value / dt, round(value / dt), abs_tol=1e-9, rel_tol=0):
        raise ApplicationError(ErrorCode.INVALID_SPEC, f"{name} must align to dt_ms")


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return {field.name: _plain(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if type(value) is float:
        if not math.isfinite(value):
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "nonfinite JSON number")
        return int(value) if value.is_integer() else value
    if value is None or type(value) in (str, int, bool):
        return value
    raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, f"unsupported JSON value: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    """Sorted UTF-8 JSON, compact separators, finite numbers, integral floats as integers."""
    return json.dumps(_plain(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _digest(domain: str, value: Any) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\0" + canonical_bytes(value)).hexdigest()


T = TypeVar("T")


def _strict(cls: type[T], raw: Any) -> T:
    if not isinstance(raw, dict) or set(raw) != {field.name for field in fields(cls)}:
        raise ApplicationError(ErrorCode.INVALID_SPEC, f"{cls.__name__} requires exact fields")
    return cls(**raw)


@dataclass(frozen=True, slots=True)
class DatasetIdentity:
    release: str
    manifest_digest: str
    annotation_sha256: str
    neurotransmitter_sha256: str
    weights_sha256: str
    projection_fingerprint: str
    mapping_fingerprint: str

    def __post_init__(self) -> None:
        if self.release != "MaleCNS-v1.0":
            raise ApplicationError(ErrorCode.INVALID_SPEC, "unsupported dataset release")
        for name in ("manifest_digest", "annotation_sha256", "neurotransmitter_sha256", "weights_sha256", "projection_fingerprint", "mapping_fingerprint"):
            _hex(getattr(self, name), name)


@dataclass(frozen=True, slots=True)
class SeedPolicy:
    kind: str
    trial_seeds: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.kind != "explicit" or not self.trial_seeds or any(type(s) is not int or s < 0 or s > 2**32 - 1 for s in self.trial_seeds):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "explicit uint32 trial seeds required")


@dataclass(frozen=True, slots=True)
class StimulusSpec:
    population_fingerprint: str
    member_ids: tuple[int, ...]
    side: str
    frequency_hz: float
    start_ms: float
    end_ms: float
    weight_factor: float
    input_semantics: str

    def __post_init__(self) -> None:
        _hex(self.population_fingerprint, "population_fingerprint")
        _ids(self.member_ids, "member_ids")
        if self.side not in ("L", "R"):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "stimulus side must be L or R")
        if _finite(self.frequency_hz, "frequency_hz") not in ALLOWED_FREQUENCIES_HZ:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "frequency_hz is outside the first-slice allowlist")
        _finite(self.start_ms, "start_ms")
        _finite(self.end_ms, "end_ms", positive=True)
        _finite(self.weight_factor, "weight_factor", positive=True)
        if self.start_ms < 0 or self.end_ms <= self.start_ms or self.weight_factor != 250.0:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "unsupported stimulus timing or weight factor")
        if self.input_semantics != "reference-poisson-direct-voltage-v1":
            raise ApplicationError(ErrorCode.INVALID_SPEC, "unsupported stimulus semantics")


@dataclass(frozen=True, slots=True)
class TargetSpec:
    neuron_id: int
    side_relation: str

    def __post_init__(self) -> None:
        if type(self.neuron_id) is not int or self.neuron_id not in (10331, 16949):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "target must be a frozen MN9 ID")
        if self.side_relation not in ("ipsilateral", "contralateral"):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "invalid target side relation")


@dataclass(frozen=True, slots=True)
class InterventionSpec:
    kind: str
    target_ids: tuple[int, ...]

    def __post_init__(self) -> None:
        _ids(self.target_ids, "intervention target_ids", allow_empty=True)
        if self.kind == "none" and not self.target_ids:
            return
        if self.kind == "outgoing_silence" and len(self.target_ids) == 1:
            return
        raise ApplicationError(ErrorCode.INVALID_SPEC, "invalid intervention")


@dataclass(frozen=True, slots=True)
class ModelSpec:
    parameters: LIFParameters
    fingerprint: str

    def __post_init__(self) -> None:
        if not isinstance(self.parameters, LIFParameters) or self.fingerprint != self.parameters.fingerprint:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "model fingerprint mismatch")
        if self.parameters.synaptic_weight_per_anatomical_synapse_mV != 0.275:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "prepare_network requires reference projection weight")


@dataclass(frozen=True, slots=True)
class SignPolicySpec:
    policy_id: str
    resolution_id: str

    def __post_init__(self) -> None:
        if self.policy_id != Shiu2024SignPolicy().policy_id or self.resolution_id != NeurotransmitterResolutionPolicy().policy_id:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "prepare_network supports only its reference sign/resolution policies")


@dataclass(frozen=True, slots=True)
class ObservablesSpec:
    spikes: bool
    trace_neuron_ids: tuple[int, ...]
    delivery_trace: bool
    population_bin_ms: float | None

    def __post_init__(self) -> None:
        if type(self.spikes) is not bool or not self.spikes or type(self.delivery_trace) is not bool:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "spikes are required; delivery_trace must be boolean")
        _ids(self.trace_neuron_ids, "trace_neuron_ids", allow_empty=True)
        if len(self.trace_neuron_ids) > MAX_TRACES:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "too many selected traces")
        if self.population_bin_ms is not None:
            _finite(self.population_bin_ms, "population_bin_ms", positive=True)


@dataclass(frozen=True, slots=True)
class RobustnessVariant:
    variant_id: str
    parameter_overrides: tuple[tuple[str, float], ...]
    trial_seeds: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.variant_id not in ("R0", "V1", "V2", "V3", "V4", "V5", "V6", "V7") or self.parameter_overrides != tuple(sorted(self.parameter_overrides)):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "invalid robustness variant")
        for name, value in self.parameter_overrides:
            if name not in {f.name for f in fields(LIFParameters)}:
                raise ApplicationError(ErrorCode.INVALID_SPEC, "unknown robustness parameter")
            _finite(value, name)
        SeedPolicy("explicit", self.trial_seeds)


@dataclass(frozen=True, slots=True)
class RobustnessRequest:
    kind: str
    variants: tuple[RobustnessVariant, ...]
    aggregate_rule_id: str | None

    def __post_init__(self) -> None:
        if self.kind == "none" and not self.variants and self.aggregate_rule_id is None:
            return
        if self.kind != "explicit" or not self.variants or self.variants[0].variant_id != "R0":
            raise ApplicationError(ErrorCode.INVALID_SPEC, "explicit robustness must begin with R0")
        if len({v.variant_id for v in self.variants}) != len(self.variants):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "duplicate robustness variant")


@dataclass(frozen=True, slots=True)
class ExperimentSpec:
    experiment_schema_version: str
    experiment_id: str
    dataset: DatasetIdentity
    backend: str
    seed_policy: SeedPolicy
    duration_ms: float
    dt_ms: float
    trial_count: int
    stimulus: StimulusSpec
    target: TargetSpec
    intervention: InterventionSpec
    model: ModelSpec
    sign_policy: SignPolicySpec
    observables: ObservablesSpec
    robustness: RobustnessRequest

    def __post_init__(self) -> None:
        for name, expected_type in (("dataset", DatasetIdentity), ("seed_policy", SeedPolicy), ("stimulus", StimulusSpec), ("target", TargetSpec), ("intervention", InterventionSpec), ("model", ModelSpec), ("sign_policy", SignPolicySpec), ("observables", ObservablesSpec), ("robustness", RobustnessRequest)):
            if not isinstance(getattr(self, name), expected_type):
                raise ApplicationError(ErrorCode.INVALID_SPEC, f"{name} has invalid type")
        if self.experiment_schema_version != EXPERIMENT_SCHEMA:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "unsupported experiment schema")
        try:
            UUID(self.experiment_id)
        except (TypeError, ValueError) as exc:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "experiment_id must be UUID") from exc
        if self.backend not in ("cpu_reference", "cuda"):
            raise ApplicationError(ErrorCode.UNSUPPORTED_BACKEND, "unsupported backend")
        _finite(self.duration_ms, "duration_ms", positive=True)
        _finite(self.dt_ms, "dt_ms", positive=True)
        if self.duration_ms > MAX_DURATION_MS:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "duration exceeds application cap")
        _grid(self.duration_ms, self.dt_ms, "duration_ms")
        try:
            self.model.parameters.grid_steps(self.dt_ms)
        except (TypeError, ValueError) as exc:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "model timing does not align to dt_ms") from exc
        if type(self.trial_count) is not int or not 1 <= self.trial_count <= 30 or len(self.seed_policy.trial_seeds) != self.trial_count:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "trial count or seed count invalid")
        if self.stimulus.end_ms > self.duration_ms:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "stimulus extends past duration")
        _grid(self.stimulus.start_ms, self.dt_ms, "start_ms")
        _grid(self.stimulus.end_ms, self.dt_ms, "end_ms")
        if self.stimulus.frequency_hz * self.dt_ms / 1000 > 1:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "Poisson probability exceeds one")
        if self.observables.population_bin_ms is not None:
            _grid(self.observables.population_bin_ms, self.dt_ms, "population_bin_ms")
        expected = 16949 if self.stimulus.side == "L" else 10331
        if self.target.neuron_id != (expected if self.target.side_relation == "contralateral" else (10331 if expected == 16949 else 16949)):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "target violates frozen laterality")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ExperimentSpec":
        if not isinstance(raw, dict) or set(raw) != {field.name for field in fields(cls)}:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "ExperimentSpec requires exact fields")
        try:
            return cls._decode(raw)
        except (KeyError, TypeError, ValueError) as exc:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "invalid nested ExperimentSpec fields") from exc

    @classmethod
    def _decode(cls, raw: dict[str, Any]) -> "ExperimentSpec":
        data = dict(raw)
        for key, typ in (("dataset", DatasetIdentity), ("seed_policy", SeedPolicy), ("stimulus", StimulusSpec), ("target", TargetSpec), ("intervention", InterventionSpec), ("sign_policy", SignPolicySpec), ("observables", ObservablesSpec)):
            item = dict(data[key])
            for name in ("trial_seeds", "member_ids", "target_ids", "trace_neuron_ids"):
                if name in item:
                    item[name] = tuple(item[name])
            data[key] = _strict(typ, item)
        model = dict(data["model"])
        model["parameters"] = _strict(LIFParameters, model["parameters"])
        data["model"] = _strict(ModelSpec, model)
        robust = dict(data["robustness"])
        robust["variants"] = tuple(_strict(RobustnessVariant, {**v, "parameter_overrides": tuple(tuple(p) for p in v["parameter_overrides"]), "trial_seeds": tuple(v["trial_seeds"])}) for v in robust["variants"])
        data["robustness"] = _strict(RobustnessRequest, robust)
        return _strict(cls, data)

    def to_dict(self) -> dict[str, Any]:
        return _plain(self)

    @property
    def canonical_bytes(self) -> bytes:
        return canonical_bytes(self)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes).hexdigest()


@dataclass(frozen=True, slots=True)
class RunIdentity:
    run_id: str
    spec_digest: str
    package_version: str
    schedule_fingerprints: tuple[str, ...]
    graph_fingerprint: str

    @classmethod
    def create(cls, spec: ExperimentSpec, schedule_fingerprints: tuple[str, ...], graph_fingerprint: str, package_version: str | None = None) -> "RunIdentity":
        package = package_version or version("malecns-sim")
        payload = {"spec_digest": spec.digest, "dataset": spec.dataset, "engine_version": package, "model": spec.model, "sign_policy": spec.sign_policy, "seeds": spec.seed_policy.trial_seeds, "backend": spec.backend, "schedules": schedule_fingerprints, "graph": graph_fingerprint, "result_schema_version": RESULT_SCHEMA}
        domain = "malecns-application-variant-run-v1" if getattr(spec, "schema_version", None) == "application-variant-experiment-v1" else "malecns-application-run-v1"
        return cls(_digest(domain, payload), spec.digest, package, schedule_fingerprints, graph_fingerprint)


@dataclass(frozen=True, slots=True)
class SpikeEvent:
    timestep: int
    neuron_id: int

    def __post_init__(self) -> None:
        if type(self.timestep) is not int or self.timestep < 0 or type(self.neuron_id) is not int or self.neuron_id < 0:
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "invalid spike event")


@dataclass(frozen=True, slots=True)
class SelectedTrace:
    neuron_id: int
    v_mV: tuple[float, ...]
    g_mV: tuple[float, ...]

    def __post_init__(self) -> None:
        if type(self.neuron_id) is not int or self.neuron_id < 0 or len(self.v_mV) != len(self.g_mV):
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "invalid selected trace")
        for item in self.v_mV + self.g_mV:
            if not isinstance(item, (int, float)) or not math.isfinite(item):
                raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "nonfinite selected trace")


@dataclass(frozen=True, slots=True)
class DeliverySample:
    timestep: int
    event_count: int
    weight_sum_mV: float
    abs_weight_sum_mV: float
    target_count: int
    target_index_sum: int

    def __post_init__(self) -> None:
        for name in ("timestep", "event_count", "target_count", "target_index_sum"):
            if type(getattr(self, name)) is not int or getattr(self, name) < 0:
                raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "invalid delivery sample")
        _finite(self.weight_sum_mV, "weight_sum_mV")
        _finite(self.abs_weight_sum_mV, "abs_weight_sum_mV")


@dataclass(frozen=True, slots=True)
class PopulationBins:
    bin_ms: float
    counts: tuple[int, ...]
    source_digest: str
    binning_version: str

    def __post_init__(self) -> None:
        _finite(self.bin_ms, "bin_ms", positive=True)
        _hex(self.source_digest, "source_digest")
        if any(type(n) is not int or n < 0 for n in self.counts):
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "invalid population bin")


@dataclass(frozen=True, slots=True)
class Comparison:
    baseline: float
    intervention: float
    absolute_delta: float
    relative_delta: float | None
    warning: str | None

    @classmethod
    def create(cls, baseline: float, intervention: float) -> "Comparison":
        b = _finite(baseline, "baseline")
        i = _finite(intervention, "intervention")
        return cls(b, i, i - b, None if b == 0 else (i - b) / b, "ZERO_BASELINE" if b == 0 else None)


@dataclass(frozen=True, slots=True)
class VariantResult:
    variant_id: str
    spec_digest: str
    target_spikes: int | None
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RobustnessResult:
    variants: tuple[VariantResult, ...]
    aggregate_rule_id: str | None
    aggregate_status: str


@dataclass(frozen=True, slots=True)
class TrialResult:
    trial_index: int
    seed: int
    schedule_fingerprint: str
    engine_digest: str
    target_spikes: int
    target_rate_hz: float
    target_spike_timesteps: tuple[int, ...]
    spikes: tuple[SpikeEvent, ...]
    selected_traces: tuple[SelectedTrace, ...]
    delivery_trace: tuple[DeliverySample, ...]

    def __post_init__(self) -> None:
        if type(self.trial_index) is not int or self.trial_index < 0 or type(self.seed) is not int or self.seed < 0:
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "invalid trial identity")
        if type(self.target_spikes) is not int or self.target_spikes < 0:
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "invalid target count")
        _hex(self.schedule_fingerprint, "schedule_fingerprint")
        _hex(self.engine_digest, "engine_digest")
        if self.spikes != tuple(sorted(self.spikes, key=lambda s: (s.timestep, s.neuron_id))):
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "spikes must use canonical order")
        if len(self.spikes) > MAX_SPIKES:
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "inline spike cap exceeded")
        if self.target_spike_timesteps != tuple(sorted(self.target_spike_timesteps)) or len(self.target_spike_timesteps) != self.target_spikes:
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "target response series/count mismatch")
        _finite(self.target_rate_hz, "target_rate_hz")


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    result_schema_version: str
    identity: RunIdentity
    executed_spec: ExperimentSpec
    status: str
    invocation_id: str
    started_at: str
    finished_at: str
    backend: str
    provenance: dict[str, Any]
    stimulus_summary: dict[str, Any]
    intervention_summary: dict[str, Any]
    trials: tuple[TrialResult, ...]
    visualization: tuple[PopulationBins, ...]
    comparison: Comparison | None
    robustness: RobustnessResult | None
    warnings: tuple[str, ...]
    error: dict[str, Any] | None
    authoritative_digest: str
    manifest_digest: str

    def authoritative_payload(self) -> dict[str, Any]:
        return {"identity": self.identity, "spec": self.executed_spec, "backend": self.backend, "stimulus": self.stimulus_summary, "intervention": self.intervention_summary, "trials": self.trials, "comparison": self.comparison, "robustness": self.robustness}

    def verify_integrity(self) -> None:
        if self.result_schema_version != RESULT_SCHEMA or self.identity.spec_digest != self.executed_spec.digest:
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "result schema or spec identity mismatch")
        if getattr(self.executed_spec, "schema_version", None) == "application-variant-experiment-v1":
            variant = self.executed_spec.variant
            if (self.provenance.get("variant_digest") != variant.digest
                    or self.provenance.get("preparation_config_digest") != variant.resolved_config.digest
                    or self.provenance.get("preparation_variant") != variant.to_dict()
                    or self.identity != RunIdentity.create(self.executed_spec, self.identity.schedule_fingerprints, self.identity.graph_fingerprint, self.identity.package_version)):
                raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "variant execution identity mismatch")
        if self.status not in ("COMPLETED", "FAILED", "CANCELLED") or (self.status == "COMPLETED" and self.error is not None) or (self.status != "COMPLETED" and self.error is None):
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "result terminal status/error mismatch")
        if self.authoritative_digest != _digest("malecns-application-authoritative-v1", self.authoritative_payload()):
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "authoritative digest mismatch")
        payload = self.to_dict()
        payload.pop("manifest_digest")
        if self.manifest_digest != _digest("malecns-application-manifest-v1", payload):
            raise ApplicationError(ErrorCode.RESULT_SERIALIZATION, "manifest digest mismatch")

    def to_dict(self) -> dict[str, Any]:
        return _plain(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ExperimentResult":
        data = dict(raw)
        data["identity"] = _strict(RunIdentity, {**data["identity"], "schedule_fingerprints": tuple(data["identity"]["schedule_fingerprints"])})
        if data["executed_spec"].get("schema_version") == "application-variant-experiment-v1":
            from .preparation import VariantExperimentSpec
            data["executed_spec"] = VariantExperimentSpec.from_dict(data["executed_spec"])
        else:
            data["executed_spec"] = ExperimentSpec.from_dict(data["executed_spec"])
        data["trials"] = tuple(_strict(TrialResult, {**t, "target_spike_timesteps": tuple(t["target_spike_timesteps"]), "spikes": tuple(_strict(SpikeEvent, s) for s in t["spikes"]), "selected_traces": tuple(_strict(SelectedTrace, {**v, "v_mV": tuple(v["v_mV"]), "g_mV": tuple(v["g_mV"])}) for v in t["selected_traces"]), "delivery_trace": tuple(_strict(DeliverySample, d) for d in t["delivery_trace"])}) for t in data["trials"])
        data["visualization"] = tuple(_strict(PopulationBins, {**v, "counts": tuple(v["counts"])}) for v in data["visualization"])
        if data["comparison"] is not None:
            data["comparison"] = _strict(Comparison, data["comparison"])
        if data["robustness"] is not None:
            r = data["robustness"]
            data["robustness"] = _strict(RobustnessResult, {**r, "variants": tuple(_strict(VariantResult, {**v, "warnings": tuple(v["warnings"])}) for v in r["variants"])})
        data["warnings"] = tuple(data["warnings"])
        result = _strict(cls, data)
        result.verify_integrity()
        return result

    @classmethod
    def create(cls, *, identity: RunIdentity, spec: ExperimentSpec, invocation_id: str, started_at: str, finished_at: str, provenance: dict[str, Any], stimulus_summary: dict[str, Any], intervention_summary: dict[str, Any], trials: tuple[TrialResult, ...], visualization: tuple[PopulationBins, ...] = (), warnings: tuple[str, ...] = (), status: str = "COMPLETED", error: dict[str, Any] | None = None) -> "ExperimentResult":
        base = cls(RESULT_SCHEMA, identity, spec, status, invocation_id, started_at, finished_at, spec.backend, provenance, stimulus_summary, intervention_summary, trials, visualization, None, None, warnings, error, "", "")
        authoritative = _digest("malecns-application-authoritative-v1", base.authoritative_payload())
        data = base.to_dict()
        data["authoritative_digest"] = authoritative
        data.pop("manifest_digest")
        manifest = _digest("malecns-application-manifest-v1", data)
        result = cls(RESULT_SCHEMA, identity, spec, status, invocation_id, started_at, finished_at, spec.backend, provenance, stimulus_summary, intervention_summary, trials, visualization, None, None, warnings, error, authoritative, manifest)
        result.verify_integrity()
        return result
