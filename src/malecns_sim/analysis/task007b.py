"""Narrow laterality evidence and resolution for Task 007b.

This module resolves only an organism-side correspondence.  It deliberately
does not accept simulation, connectivity, physiology, or dynamics evidence.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping, Sequence

from malecns_sim.homology import MaleCNSCandidate, MappingStatus, MappingRecord


TASK007B_EVIDENCE_PATH = Path("data/provenance/task007b-mn9-laterality-evidence.json")
MN9_REFERENCE_ROOT = "720575940660219265"
MN9_FLYWIRE_TYPE = "CB0701"


class OrganismSide(StrEnum):
    LEFT = "left"
    RIGHT = "right"


def normalize_side(value: object) -> OrganismSide:
    """Normalize only explicit anatomical-side labels."""

    text = str(value).strip().lower()
    aliases = {
        "l": OrganismSide.LEFT,
        "left": OrganismSide.LEFT,
        "left side": OrganismSide.LEFT,
        "left side of organism": OrganismSide.LEFT,
        "r": OrganismSide.RIGHT,
        "right": OrganismSide.RIGHT,
        "right side": OrganismSide.RIGHT,
        "right side of organism": OrganismSide.RIGHT,
    }
    try:
        return aliases[text]
    except KeyError as exc:
        raise ValueError(f"unsupported anatomical side: {value!r}") from exc


@dataclass(frozen=True, slots=True)
class LateralityEvidence:
    """One independently sourced, organism-side evidence statement."""

    source: str
    source_version: str
    source_url: str
    source_id: str
    organism_side: OrganismSide | str
    relationship_fields: tuple[tuple[str, str], ...] = ()
    coordinate_system_note: str | None = None
    contradictory: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "organism_side", normalize_side(self.organism_side))
        fields = tuple(sorted((str(key), str(value)) for key, value in self.relationship_fields))
        object.__setattr__(self, "relationship_fields", fields)


@dataclass(frozen=True, slots=True)
class MN9LateralityResolution:
    status: MappingStatus
    candidate_body_ids: tuple[str, ...]
    preferred_readout: str | None
    basis: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        ids = tuple(sorted({str(value) for value in self.candidate_body_ids}, key=int))
        object.__setattr__(self, "candidate_body_ids", ids)
        if self.preferred_readout is not None:
            preferred = str(self.preferred_readout)
            if preferred not in ids:
                raise ValueError("preferred readout must be one of the candidate IDs")
            object.__setattr__(self, "preferred_readout", preferred)
        if self.status is MappingStatus.SIDE_RESOLVED and self.preferred_readout is None:
            raise ValueError("SIDE_RESOLVED requires a preferred readout")


def _field(evidence: LateralityEvidence, name: str) -> str | None:
    return dict(evidence.relationship_fields).get(name)


def _type_candidates(candidates: Sequence[MaleCNSCandidate]) -> tuple[MaleCNSCandidate, ...]:
    return tuple(
        candidate
        for candidate in candidates
        if candidate.type == "MN9" and candidate.flywire_type == MN9_FLYWIRE_TYPE
    )


def _explicit_candidate_side(candidate: MaleCNSCandidate) -> OrganismSide | None:
    """Use source side columns only; never infer side from free text."""

    values = [value for value in (candidate.soma_side, candidate.root_side) if value is not None]
    if not values:
        return None
    normalized = {normalize_side(value) for value in values}
    if len(normalized) != 1:
        raise ValueError(f"candidate {candidate.body_id} has contradictory side columns")
    return next(iter(normalized))


def resolve_mn9_laterality(
    flywire_evidence: LateralityEvidence,
    shiu_evidence: LateralityEvidence,
    candidates: Sequence[MaleCNSCandidate],
) -> MN9LateralityResolution:
    """Apply the Task 007b three-source side-resolution rule."""

    type_candidates = _type_candidates(candidates)
    ids = tuple(candidate.body_id for candidate in type_candidates)
    provenance = (flywire_evidence.source_id, shiu_evidence.source_id)
    if not type_candidates:
        return MN9LateralityResolution(
            MappingStatus.UNRESOLVED, (), None, "no direct MN9/CB0701 type candidates", provenance
        )

    if (
        flywire_evidence.contradictory
        or shiu_evidence.contradictory
        or flywire_evidence.organism_side != shiu_evidence.organism_side
        or _field(flywire_evidence, "flywire_root") != MN9_REFERENCE_ROOT
        or _field(flywire_evidence, "flywire_type") != MN9_FLYWIRE_TYPE
        or _field(shiu_evidence, "stimulus_side") != OrganismSide.LEFT.value
        or _field(shiu_evidence, "mn9_relation") != "contralateral"
        or _field(shiu_evidence, "mn9_side") != OrganismSide.RIGHT.value
    ):
        return MN9LateralityResolution(
            MappingStatus.AMBIGUOUS,
            ids,
            None,
            "contradictory or incomplete independent laterality evidence blocks promotion",
            provenance,
        )

    side_candidates = tuple(
        candidate
        for candidate in type_candidates
        if _explicit_candidate_side(candidate) is flywire_evidence.organism_side
    )
    if len(side_candidates) == 1:
        selected = side_candidates[0].body_id
        return MN9LateralityResolution(
            MappingStatus.SIDE_RESOLVED,
            ids,
            selected,
            "VFB and Shiu both resolve the reference readout to the unique right-side MN9 candidate",
            provenance,
        )
    if len(side_candidates) > 1:
        return MN9LateralityResolution(
            MappingStatus.AMBIGUOUS,
            ids,
            None,
            "multiple direct MN9/CB0701 candidates share the resolved side",
            provenance,
        )
    if any(_explicit_candidate_side(candidate) is None for candidate in type_candidates):
        basis = "type candidates exist but no explicit candidate side is available"
    else:
        basis = "type candidates exist but none has the independently resolved side"
    return MN9LateralityResolution(MappingStatus.TYPE_LEVEL, ids, None, basis, provenance)


def apply_mn9_laterality(
    record: MappingRecord,
    resolution: MN9LateralityResolution,
) -> MappingRecord:
    """Return a narrow successor record without touching other mapping records."""

    if record.reference_role != "mn9":
        raise ValueError("Task 007b can update only the MN9 mapping record")
    by_id = {candidate.body_id: candidate for candidate in record.candidates}
    selected_ids = (
        (resolution.preferred_readout,)
        if resolution.status is MappingStatus.SIDE_RESOLVED
        else resolution.candidate_body_ids
    )
    selected = tuple(by_id[body_id] for body_id in selected_ids if body_id in by_id)
    if tuple(candidate.body_id for candidate in selected) != selected_ids:
        raise ValueError("laterality resolution candidates do not match the mapping record")
    notes = record.evidence_notes + (
        "Task 007b used independent VFB right-side and Shiu contralateral-left-stimulus evidence.",
        f"Preferred readout is MaleCNS body {resolution.preferred_readout} by organism laterality only.",
    )
    return MappingRecord(
        reference_order=record.reference_order,
        reference_role=record.reference_role,
        shiu_v630_root_id=record.shiu_v630_root_id,
        flywire_materialization=record.flywire_materialization,
        flywire_annotation_release=record.flywire_annotation_release,
        flywire_type=record.flywire_type,
        updated_root_ids=record.updated_root_ids,
        lineage_method=record.lineage_method,
        male_cns_release=record.male_cns_release,
        candidates=selected,
        status=resolution.status,
        evidence_sources=tuple(sorted(set(record.evidence_sources + resolution.provenance))),
        evidence_notes=notes,
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (tuple, list, set)):
        items = [_jsonable(item) for item in value]
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    if isinstance(value, StrEnum):
        return value.value
    return value


def normalize_laterality_evidence(payload: Mapping[str, Any]) -> dict[str, Any]:
    normalized = _jsonable(payload)
    if not isinstance(normalized, dict):
        raise TypeError("Task 007b evidence must normalize to an object")
    return normalized


def laterality_evidence_fingerprint(payload: Mapping[str, Any]) -> str:
    normalized = normalize_laterality_evidence(payload)
    normalized.pop("evidence_fingerprint", None)
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b"malecns-sim-task007b-mn9-laterality-v1\0" + encoded).hexdigest()


def load_task007b_provenance(path: str | Path = TASK007B_EVIDENCE_PATH) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    expected = laterality_evidence_fingerprint(payload)
    if payload.get("evidence_fingerprint") != expected:
        raise ValueError("Task 007b evidence fingerprint mismatch")
    return normalize_laterality_evidence(payload)


def resolve_task007b_provenance(
    payload: Mapping[str, Any],
    candidates: Sequence[MaleCNSCandidate],
) -> MN9LateralityResolution:
    """Resolve the checked-in compact provenance record against local rows."""

    vfb = payload["vfb_evidence"]
    shiu = payload["shiu_evidence"]
    vfb_fields = (
        ("flywire_root", str(vfb["flywire_root"])),
        ("flywire_type", str(vfb["flywire_type"])),
        ("has_soma_location", str(vfb["relationship_fields"]["has_soma_location"])),
    )
    shiu_fields = (
        ("stimulus_side", str(shiu["stimulus_side"])),
        ("mn9_relation", str(shiu["mn9_relation"])),
        ("mn9_side", str(shiu["mn9_side"])),
    )
    return resolve_mn9_laterality(
        LateralityEvidence(
            source=str(vfb["source"]),
            source_version=str(vfb["source_version"]),
            source_url=str(vfb["source_url"]),
            source_id=str(vfb["identifier"]),
            organism_side=str(vfb["organism_side"]),
            relationship_fields=vfb_fields,
        ),
        LateralityEvidence(
            source=str(shiu["source"]),
            source_version=str(shiu["source_version"]),
            source_url=str(shiu["source_url"]),
            source_id=str(shiu["source_location"]),
            organism_side=str(shiu["mn9_side"]),
            relationship_fields=shiu_fields,
            coordinate_system_note=str(shiu["coordinate_system_note"]),
        ),
        candidates,
    )
