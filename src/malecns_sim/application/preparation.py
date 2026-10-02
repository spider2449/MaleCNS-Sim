"""Application-owned immutable preparation and allowlisted variant identities."""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import math

from malecns_sim.data.neurotransmitter import NeurotransmitterResolutionPolicy
from malecns_sim.dynamics.lif import LIFParameters
from malecns_sim.sign import ConservativeSignPolicy, Shiu2024SignPolicy

from .errors import ApplicationError, ErrorCode
from .models import ExperimentSpec, canonical_bytes, _plain

PRESET_ID = "application-historical-variation-family-v1"
SCHEMA = "application-preparation-variant-v1"
SOURCE_COMMIT = "c02501e114b487a4c41926a4a04a950e06ce8b7c"
SIGN_POLICIES = {"Shiu2024SignPolicy": Shiu2024SignPolicy,
                 "ConservativeSignPolicy": ConservativeSignPolicy}


def digest(domain: str, value: object) -> str:
    return sha256(domain.encode() + b"\0" + canonical_bytes(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class PreparationConfig:
    parameters: LIFParameters = LIFParameters()
    sign_policy_id: str = "Shiu2024SignPolicy"
    resolution_policy_id: str = NeurotransmitterResolutionPolicy().policy_id
    direct_input_weight_factor: float = 250.0
    direct_input_rule: str = "derived-anatomical-weight-times-factor-v1"

    def __post_init__(self):
        if (not isinstance(self.parameters, LIFParameters)
                or not isinstance(self.sign_policy_id, str)
                or self.sign_policy_id not in SIGN_POLICIES
                or self.resolution_policy_id != NeurotransmitterResolutionPolicy().policy_id
                or type(self.direct_input_weight_factor) not in (int, float)
                or self.direct_input_weight_factor != 250.0
                or self.direct_input_rule != "derived-anatomical-weight-times-factor-v1"
                or not math.isfinite(self.direct_input_amplitude_mv)):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "unsupported preparation configuration")

    @property
    def canonical_bytes(self) -> bytes:
        return canonical_bytes(self)

    def to_dict(self) -> dict:
        return _plain(self)

    @property
    def sign_policy(self):
        return SIGN_POLICIES[self.sign_policy_id]()

    @property
    def direct_input_amplitude_mv(self):
        return self.parameters.synaptic_weight_per_anatomical_synapse_mV * self.direct_input_weight_factor

    @property
    def digest(self):
        return digest("application-preparation-config-v1", self)


REFERENCE_CONFIG = PreparationConfig()
OVERRIDES = (
    ("R0", ()),
    ("V1", (("tau_membrane_ms", 10.0),)),
    ("V2", (("tau_membrane_ms", 30.0),)),
    ("V3", (("tau_synapse_ms", 2.5),)),
    ("V4", (("synaptic_delay_ms", 1.0),)),
    ("V5", (("synaptic_weight_per_anatomical_synapse_mV", 0.200),)),
    ("V6", (("v_threshold_mV", -44.0),)),
    ("V7", (("sign_policy_id", "ConservativeSignPolicy"),)),
)
PROVENANCE = (("source_commit", SOURCE_COMMIT),
              ("definitions", "Task016 preregistration; Task017 VariantConfiguration (read-only)"))
PRESET_DIGEST = digest(PRESET_ID, {"reference": REFERENCE_CONFIG, "definitions": OVERRIDES,
                                  "provenance": PROVENANCE})


@dataclass(frozen=True, slots=True)
class PreparationVariant:
    schema_version: str
    preset_id: str
    preset_digest: str
    variant_id: str
    reference_digest: str
    overrides: tuple[tuple[str, float | str], ...]
    resolved_config: PreparationConfig
    provenance: tuple[tuple[str, str], ...]

    def __post_init__(self):
        expected = dict(OVERRIDES).get(self.variant_id) if isinstance(self.variant_id, str) else None
        if (expected is None or self.schema_version != SCHEMA or self.preset_id != PRESET_ID
                or self.preset_digest != PRESET_DIGEST or self.reference_digest != REFERENCE_CONFIG.digest
                or self.overrides != expected or self.provenance != PROVENANCE
                or self.resolved_config != _resolve_config(expected)):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "variant must match the exact preset definition")

    @property
    def canonical_bytes(self):
        return canonical_bytes(self)

    @property
    def digest(self):
        return digest(SCHEMA, self)

    def to_dict(self):
        return _plain(self)


def _resolve_config(overrides):
    values = dict(overrides)
    sign = values.pop("sign_policy_id", REFERENCE_CONFIG.sign_policy_id)
    return replace(REFERENCE_CONFIG, parameters=replace(REFERENCE_CONFIG.parameters, **values), sign_policy_id=sign)


def resolve_variant(preset_id: str, variant_id: str) -> PreparationVariant:
    if preset_id != PRESET_ID or not isinstance(variant_id, str) or variant_id not in dict(OVERRIDES):
        raise ApplicationError(ErrorCode.INVALID_SPEC, "unknown preparation preset or variant")
    overrides = dict(OVERRIDES)[variant_id]
    return PreparationVariant(SCHEMA, preset_id, PRESET_DIGEST, variant_id, REFERENCE_CONFIG.digest,
                              overrides, _resolve_config(overrides), PROVENANCE)


@dataclass(frozen=True, slots=True)
class ResolvedModel:
    parameters: LIFParameters
    fingerprint: str


@dataclass(frozen=True, slots=True)
class ResolvedSignPolicy:
    policy_id: str
    resolution_id: str


@dataclass(frozen=True, slots=True)
class VariantExperimentSpec:
    """Additive execution envelope; the historical experiment is never rewritten."""

    base_spec: ExperimentSpec
    variant: PreparationVariant
    schema_version: str = "application-variant-experiment-v1"

    def __post_init__(self):
        if (not isinstance(self.base_spec, ExperimentSpec) or not isinstance(self.variant, PreparationVariant)
                or self.schema_version != "application-variant-experiment-v1"
                or self.base_spec.model.parameters != REFERENCE_CONFIG.parameters
                or self.base_spec.robustness.kind != "none"):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "reference experiment and preset variant required")
        self.variant.resolved_config.parameters.grid_steps(self.base_spec.dt_ms)

    def __getattr__(self, name):
        return getattr(self.base_spec, name)

    @property
    def model(self):
        params = self.variant.resolved_config.parameters
        return ResolvedModel(params, params.fingerprint)

    @property
    def sign_policy(self):
        config = self.variant.resolved_config
        return ResolvedSignPolicy(config.sign_policy_id, config.resolution_policy_id)

    def to_dict(self):
        return _plain(self)

    @property
    def canonical_bytes(self):
        return canonical_bytes(self)

    @property
    def digest(self):
        return digest(self.schema_version, self)

    @classmethod
    def from_dict(cls, raw):
        if not isinstance(raw, dict) or set(raw) != {"base_spec", "variant", "schema_version"}:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "invalid variant experiment envelope")
        value = raw["variant"]
        if not isinstance(value, dict) or not {"preset_id", "variant_id"}.issubset(value):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "invalid variant definition")
        variant = resolve_variant(value["preset_id"], value["variant_id"])
        if canonical_bytes(value) != variant.canonical_bytes:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "variant definition mismatch")
        return cls(ExperimentSpec.from_dict(raw["base_spec"]), variant, raw["schema_version"])


def decode_variant_request(base_spec: ExperimentSpec, raw: dict) -> VariantExperimentSpec:
    """Minimal backend seam; clients can choose IDs, never model overrides."""
    if not isinstance(raw, dict) or set(raw) != {"preset_id", "variant_id"}:
        raise ApplicationError(ErrorCode.INVALID_SPEC, "only preset_id and variant_id are allowed")
    return VariantExperimentSpec(base_spec, resolve_variant(raw["preset_id"], raw["variant_id"]))
