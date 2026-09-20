"""Source neurotransmitter evidence and explicit resolution policies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from malecns_sim.data.male_cns_v1 import MaleCNSV1ColumnMapping


NT_SOURCE_FIELDS = (
    "consensus_nt",
    "predicted_nt",
    "celltype_predicted_nt",
)


@dataclass(frozen=True, slots=True)
class NeurotransmitterEvidence:
    """MaleCNS source metadata without a model-sign interpretation."""

    neuron_id: int | str
    consensus_nt: str | None = None
    predicted_nt: str | None = None
    celltype_predicted_nt: str | None = None
    predicted_nt_confidence: float | None = None
    celltype_predicted_nt_confidence: float | None = None
    ground_truth: str | None = None
    superclass: str | None = None

    def value_for(self, field: str) -> Any:
        if field not in NT_SOURCE_FIELDS:
            raise ValueError(f"unsupported neurotransmitter source field: {field!r}")
        return getattr(self, field)

    def confidence_for(self, field: str) -> float | None:
        if field == "predicted_nt":
            return self.predicted_nt_confidence
        if field == "celltype_predicted_nt":
            return self.celltype_predicted_nt_confidence
        if field == "consensus_nt":
            return None
        raise ValueError(f"unsupported neurotransmitter source field: {field!r}")


SUPPORTED_NEUROTRANSMITTERS = frozenset(
    {
        "acetylcholine",
        "gaba",
        "glutamate",
        "dopamine",
        "serotonin",
        "octopamine",
        "histamine",
    }
)
UNCLEAR_LABELS = frozenset({"", "unclear", "unknown", "unresolved", "none", "nan"})


def canonical_neurotransmitter(value: str | None) -> str | None:
    """Canonicalize a source label, returning ``None`` for unresolved labels."""

    if value is None:
        return None
    normalized = str(value).strip().lower().replace("γ-aminobutyric acid", "gaba")
    if normalized in UNCLEAR_LABELS:
        return None
    return normalized if normalized in SUPPORTED_NEUROTRANSMITTERS else None


@dataclass(frozen=True, slots=True)
class ResolvedNeurotransmitter:
    """A selected source label plus all evidence needed to audit the choice."""

    evidence: NeurotransmitterEvidence
    resolution_policy_id: str
    source_field: str | None
    source_label: str | None
    identity: str | None
    source_confidence: float | None

    @property
    def resolved(self) -> bool:
        return self.identity is not None


@dataclass(frozen=True, slots=True)
class NeurotransmitterResolutionPolicy:
    """Configurable, ordered source-field resolution with no implicit fallback."""

    policy_id: str = "MaleCNSV1ConsensusThenPredictedThenCelltype"
    precedence: tuple[str, ...] = NT_SOURCE_FIELDS

    def __post_init__(self) -> None:
        if not self.precedence:
            raise ValueError("neurotransmitter precedence cannot be empty")
        if len(set(self.precedence)) != len(self.precedence):
            raise ValueError("neurotransmitter precedence must not repeat fields")
        unknown = set(self.precedence) - set(NT_SOURCE_FIELDS)
        if unknown:
            raise ValueError(f"unsupported neurotransmitter source fields: {sorted(unknown)!r}")

    def resolve(self, evidence: NeurotransmitterEvidence) -> ResolvedNeurotransmitter:
        """Use the first present source value; explicit ``unclear`` stays unresolved."""

        selected_field: str | None = None
        selected_label: str | None = None
        selected_confidence: float | None = None
        for field in self.precedence:
            value = evidence.value_for(field)
            if value is not None and str(value).strip():
                selected_field = field
                selected_label = str(value).strip()
                selected_confidence = evidence.confidence_for(field)
                break
        return ResolvedNeurotransmitter(
            evidence=evidence,
            resolution_policy_id=self.policy_id,
            source_field=selected_field,
            source_label=selected_label,
            identity=canonical_neurotransmitter(selected_label),
            source_confidence=selected_confidence,
        )

    def resolve_many(
        self, evidence: Iterable[NeurotransmitterEvidence]
    ) -> tuple[ResolvedNeurotransmitter, ...]:
        return tuple(self.resolve(item) for item in evidence)


def load_male_cns_v1_neurotransmitter_evidence(
    annotation_path: str | Path,
    neurotransmitter_path: str | Path,
    mapping: "MaleCNSV1ColumnMapping | None" = None,
    *,
    curated_only: bool = False,
) -> tuple[NeurotransmitterEvidence, ...]:
    """Load source NT fields joined to annotations without assigning a sign."""

    import pyarrow.feather as feather

    if mapping is None:
        from malecns_sim.data.male_cns_v1 import official_v1_mapping

        mapping = official_v1_mapping()
    annotations = feather.read_table(annotation_path).to_pylist()
    neurotransmitters = feather.read_table(neurotransmitter_path).to_pylist()
    nt_id = mapping.neurotransmitter_body_id or mapping.annotation_body_id
    nt_by_id: dict[int, Mapping[str, Any]] = {
        int(row[nt_id]): row for row in neurotransmitters if row.get(nt_id) is not None
    }
    result: list[NeurotransmitterEvidence] = []
    for row in annotations:
        body_id = row.get(mapping.annotation_body_id)
        if body_id is None:
            raise ValueError(f"annotation body ID is null in {mapping.annotation_body_id!r}")
        superclass = row.get(mapping.annotation_class) if mapping.annotation_class else None
        if curated_only and not (isinstance(superclass, str) and superclass.strip()):
            continue
        nt_row = nt_by_id.get(int(body_id), {})
        result.append(
            NeurotransmitterEvidence(
                neuron_id=int(body_id),
                consensus_nt=nt_row.get("consensus_nt"),
                predicted_nt=nt_row.get("predicted_nt"),
                celltype_predicted_nt=nt_row.get("celltype_predicted_nt"),
                predicted_nt_confidence=(
                    float(nt_row["predicted_nt_confidence"])
                    if nt_row.get("predicted_nt_confidence") is not None
                    else None
                ),
                celltype_predicted_nt_confidence=(
                    float(nt_row["celltype_predicted_nt_confidence"])
                    if nt_row.get("celltype_predicted_nt_confidence") is not None
                    else None
                ),
                ground_truth=nt_row.get("ground_truth"),
                superclass=str(superclass).strip() if superclass is not None else None,
            )
        )
    return tuple(sorted(result, key=lambda item: int(item.neuron_id)))
