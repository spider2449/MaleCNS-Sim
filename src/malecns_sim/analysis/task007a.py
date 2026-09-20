"""Deterministic public-evidence model for Task 007a.

Lineage, annotation/type, anatomy, morphology, and functional evidence are
kept in separate fields.  This module intentionally has no dependency on the
dynamics package and rejects dynamics evidence at the evidence boundary.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping, Sequence

from malecns_sim.homology import MappingStatus


TASK007A_LINEAGE_PATH = Path("data/provenance/task007a-lineage-evidence.json")
TASK007A_MN9_PATH = Path("data/provenance/task007a-mn9-evidence.json")
SUGAR_ROOT_ID = "720575940620900446"
MN9_CANDIDATE_IDS = ("10331", "16949")


class LineageRelation(StrEnum):
    ONE_TO_ONE = "ONE_TO_ONE"
    SPLIT = "SPLIT"
    MERGE = "MERGE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class LineageResult:
    """A lossless representation of one public lineage query result."""

    queried_root_id: str
    dataset: str
    materialization: str
    source_version: str
    source_url: str
    queried_at_utc: str
    valid_at_materialization: bool | None
    valid_at_query: bool | None
    relation: LineageRelation
    descendant_root_ids: tuple[str, ...]
    merged_parent_root_ids: tuple[str, ...]
    raw_result_category: str
    notes: tuple[str, ...]


def _canonical_id(value: int | str) -> str:
    text = str(value).strip()
    if not text.isdigit() or str(int(text)) != text:
        raise ValueError(f"IDs must use canonical decimal spelling: {value!r}")
    return text


def _ids(values: Sequence[int | str]) -> tuple[str, ...]:
    return tuple(sorted({_canonical_id(value) for value in values}, key=int))


def lineage_result(
    queried_root_id: int | str,
    *,
    dataset: str,
    materialization: str,
    source_version: str,
    source_url: str,
    queried_at_utc: str,
    valid_at_materialization: bool | None,
    valid_at_query: bool | None,
    descendant_root_ids: Sequence[int | str] = (),
    merged_parent_root_ids: Sequence[int | str] = (),
    raw_result_category: str,
    notes: Sequence[str] = (),
) -> LineageResult:
    """Normalize one-to-one, split, merge, and no-result representations."""

    descendants = _ids(descendant_root_ids)
    merged = _ids(merged_parent_root_ids)
    if merged:
        relation = LineageRelation.MERGE
    elif len(descendants) == 1:
        relation = LineageRelation.ONE_TO_ONE
    elif len(descendants) > 1:
        relation = LineageRelation.SPLIT
    else:
        relation = LineageRelation.UNRESOLVED
    return LineageResult(
        queried_root_id=_canonical_id(queried_root_id),
        dataset=str(dataset),
        materialization=str(materialization),
        source_version=str(source_version),
        source_url=str(source_url),
        queried_at_utc=str(queried_at_utc),
        valid_at_materialization=valid_at_materialization,
        valid_at_query=valid_at_query,
        relation=relation,
        descendant_root_ids=descendants,
        merged_parent_root_ids=merged,
        raw_result_category=str(raw_result_category),
        notes=tuple(str(note) for note in notes),
    )


@dataclass(frozen=True, slots=True)
class MN9CandidateEvidence:
    """One candidate row in the non-numeric MN9 evidence matrix."""

    body_id: str
    flywire_type_match: bool
    across_brain_mapping: str | None
    side: str | None
    motor_superclass: str | None
    manc_match: str | None
    neuronbridge_match: str | None
    morphology_support: str | None
    nerve_soma_support: str | None
    dimorphism_status: str | None
    contradictory_evidence: tuple[str, ...]
    evidence_sources: tuple[str, ...]
    individual_correspondence_indicated: bool = False
    individual_homolog_supported: bool = False
    other_candidates_ruled_out: bool = False
    ranking_only: bool = False
    dynamics_evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "body_id", _canonical_id(self.body_id))
        if self.dynamics_evidence:
            raise ValueError("dynamics evidence is not accepted for Task 007a identity")
        if not self.evidence_sources:
            raise ValueError("MN9 evidence requires at least one source")
        object.__setattr__(self, "contradictory_evidence", tuple(sorted(self.contradictory_evidence)))
        object.__setattr__(self, "evidence_sources", tuple(sorted(self.evidence_sources)))


@dataclass(frozen=True, slots=True)
class MN9EvidenceMatrix:
    candidates: tuple[MN9CandidateEvidence, ...]
    reference_flywire_type: str
    reference_functional_annotation: str
    final_status: MappingStatus

    def __post_init__(self) -> None:
        candidates = tuple(sorted(self.candidates, key=lambda item: int(item.body_id)))
        if tuple(item.body_id for item in candidates) != MN9_CANDIDATE_IDS:
            raise ValueError("the Task 007a MN9 matrix must contain exactly both candidates")
        object.__setattr__(self, "candidates", candidates)


def build_mn9_evidence_matrix(
    candidates: Sequence[MN9CandidateEvidence],
    *,
    reference_flywire_type: str = "CB0701",
    reference_functional_annotation: str = "ingestion motor neuron",
) -> MN9EvidenceMatrix:
    """Build the ordered matrix and apply the explicit resolution rules."""

    provisional = MN9EvidenceMatrix(
        candidates=tuple(candidates),
        reference_flywire_type=reference_flywire_type,
        reference_functional_annotation=reference_functional_annotation,
        final_status=MappingStatus.UNRESOLVED,
    )
    return MN9EvidenceMatrix(
        candidates=provisional.candidates,
        reference_flywire_type=provisional.reference_flywire_type,
        reference_functional_annotation=provisional.reference_functional_annotation,
        final_status=resolve_mn9_status(provisional),
    )


def resolve_mn9_status(matrix: MN9EvidenceMatrix) -> MappingStatus:
    """Resolve status without treating ranking or dynamics as identity proof."""

    candidates = matrix.candidates
    type_matches = [item for item in candidates if item.flywire_type_match]
    if not type_matches:
        return MappingStatus.UNRESOLVED
    exact = [
        item
        for item in type_matches
        if item.individual_homolog_supported
        and item.other_candidates_ruled_out
        and not item.ranking_only
    ]
    if len(exact) == 1 and all(
        item is exact[0] or item.other_candidates_ruled_out for item in type_matches
    ):
        return MappingStatus.EXACT
    if any(item.individual_correspondence_indicated for item in type_matches):
        return MappingStatus.AMBIGUOUS
    return MappingStatus.TYPE_LEVEL


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (tuple, list)):
        normalized = [_jsonable(item) for item in value]
        return sorted(normalized, key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    if isinstance(value, set):
        return _jsonable(sorted(value, key=str))
    if isinstance(value, StrEnum):
        return value.value
    return value


def normalize_evidence(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return a stable representation with sorted evidence collections."""

    normalized = _jsonable(payload)
    if not isinstance(normalized, dict):
        raise TypeError("Task 007a evidence must normalize to an object")
    return normalized


def evidence_fingerprint(payload: Mapping[str, Any]) -> str:
    """Fingerprint only normalized identity evidence and classifications."""

    normalized = normalize_evidence(payload)
    normalized.pop("evidence_fingerprint", None)
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b"malecns-sim-task007a-evidence-v1\0" + encoded).hexdigest()


def task007a_fingerprint(
    lineage_payload: Mapping[str, Any],
    mn9_payload: Mapping[str, Any],
) -> str:
    """Fingerprint the complete two-record Task 007a evidence boundary."""

    records = {
        "lineage": normalize_evidence(lineage_payload),
        "mn9": normalize_evidence(mn9_payload),
    }
    for record in records.values():
        record.pop("evidence_fingerprint", None)
        record.pop("combined_task007a_fingerprint", None)
    encoded = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b"malecns-sim-task007a-combined-v1\0" + encoded).hexdigest()


def load_task007a_provenance(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    expected = evidence_fingerprint(payload)
    stored = payload.get("evidence_fingerprint")
    if stored != expected:
        raise ValueError(f"Task 007a fingerprint mismatch: {stored!r} != {expected!r}")
    return normalize_evidence(payload)
