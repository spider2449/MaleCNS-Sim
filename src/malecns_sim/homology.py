"""Evidence-preserving cross-dataset neuron homology primitives.

This module deliberately models identity evidence as separate layers.  A
FlyWire root, a FlyWire type, a MaleCNS body, and a population-level
functional role are not interchangeable identifiers.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, deque
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Iterable, Mapping, Sequence


class MappingStatus(StrEnum):
    """Evidence category, not a probability or biological certainty score."""

    EXACT = "EXACT"
    TYPE_LEVEL = "TYPE_LEVEL"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"


def _id(value: int | str) -> str:
    if isinstance(value, bool):
        raise TypeError("IDs must not be bool values")
    text = str(value).strip()
    if not text.isdigit():
        raise ValueError(f"ID must be a non-negative integer string: {value!r}")
    if str(int(text)) != text:
        raise ValueError(f"ID must use canonical decimal spelling: {value!r}")
    return text


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return int(value)


@dataclass(frozen=True, slots=True)
class MaleCNSCandidate:
    """A MaleCNS body and the source fields used to support its candidacy."""

    body_id: str
    type: str | None = None
    flywire_type: str | None = None
    side: str | None = None
    soma_side: str | None = None
    root_side: str | None = None
    superclass: str | None = None
    subclass: str | None = None
    cell_class: str | None = None
    supertype: str | None = None
    receptor_type: str | None = None
    entry_nerve: str | None = None
    soma_neuromere: str | None = None
    dimorphism: str | None = None
    matching_notes: str | None = None
    manc_type: str | None = None
    manc_body_id: str | None = None
    exit_nerve: str | None = None
    consensus_nt: str | None = None
    resolved_nt: str | None = None
    nt_source_field: str | None = None
    nt_source_confidence: float | None = None
    task004_sign: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "body_id", _id(self.body_id))
        if self.manc_body_id is not None:
            object.__setattr__(self, "manc_body_id", _id(self.manc_body_id))


@dataclass(frozen=True, slots=True)
class MappingRecord:
    """One historical reference neuron's complete mapping evidence."""

    reference_order: int
    reference_role: str
    shiu_v630_root_id: str
    flywire_materialization: str
    flywire_annotation_release: str
    flywire_type: str | None
    updated_root_ids: tuple[str, ...]
    lineage_method: str
    male_cns_release: str
    candidates: tuple[MaleCNSCandidate, ...]
    status: MappingStatus
    evidence_sources: tuple[str, ...]
    evidence_notes: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "shiu_v630_root_id", _id(self.shiu_v630_root_id))
        roots = tuple(_id(value) for value in self.updated_root_ids)
        if len(roots) != len(set(roots)):
            raise ValueError("updated root IDs must be unique")
        object.__setattr__(self, "updated_root_ids", roots)
        candidates = tuple(sorted(self.candidates, key=lambda item: int(item.body_id)))
        candidate_ids = tuple(item.body_id for item in candidates)
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("candidate MaleCNS body IDs must be unique")
        object.__setattr__(self, "candidates", candidates)
        if not self.evidence_sources:
            raise ValueError("mapping evidence must retain at least one source")
        if self.status is MappingStatus.EXACT and len(candidates) != 1:
            raise ValueError("EXACT mappings require exactly one candidate")
        if self.status is MappingStatus.UNRESOLVED and candidates:
            raise ValueError("UNRESOLVED mappings cannot contain candidates")
        if self.status is not MappingStatus.UNRESOLVED and not candidates:
            raise ValueError(f"{self.status} mappings require candidates")

    @property
    def candidate_body_ids(self) -> tuple[str, ...]:
        return tuple(item.body_id for item in self.candidates)


@dataclass(frozen=True, slots=True)
class SugarPopulation:
    """A later-simulation input population derived from identity evidence."""

    candidate_body_ids: tuple[str, ...]
    side_field: str
    side_counts: tuple[tuple[str, int], ...]
    type_counts: tuple[tuple[str, int], ...]
    receptor_type_counts: tuple[tuple[str, int], ...]
    entry_nerve_counts: tuple[tuple[str, int], ...]
    task004_nt_counts: tuple[tuple[str, int], ...]
    evidence_notes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MN9Readout:
    """Explicit later-simulation MN9 readout; no silent candidate selection."""

    status: MappingStatus
    candidate_body_ids: tuple[str, ...]
    selected_body_id: str | None
    evidence_notes: tuple[str, ...]

    def __post_init__(self) -> None:
        ids = tuple(_id(value) for value in self.candidate_body_ids)
        if ids != tuple(sorted(set(ids), key=int)):
            raise ValueError("MN9 candidates must be unique and numerically ordered")
        object.__setattr__(self, "candidate_body_ids", ids)
        if self.status is MappingStatus.EXACT and self.selected_body_id is None:
            raise ValueError("EXACT MN9 readouts require a selected body")
        if self.status is not MappingStatus.EXACT and self.selected_body_id is not None:
            raise ValueError("uncertain MN9 readouts must not select a body")


def ordered_records(records: Iterable[MappingRecord]) -> tuple[MappingRecord, ...]:
    result = tuple(sorted(records, key=lambda item: item.reference_order))
    if len({item.reference_order for item in result}) != len(result):
        raise ValueError("reference order values must be unique")
    if len({item.shiu_v630_root_id for item in result}) != len(result):
        raise ValueError("reference root IDs must be unique")
    return result


def _candidate_key(candidate: MaleCNSCandidate) -> dict[str, object]:
    return asdict(candidate)


def mapping_fingerprint(records: Iterable[MappingRecord]) -> str:
    """Hash a canonical, ordered representation of all mapping evidence."""

    payload = []
    for record in ordered_records(records):
        payload.append(
            {
                "reference_order": record.reference_order,
                "reference_role": record.reference_role,
                "shiu_v630_root_id": record.shiu_v630_root_id,
                "flywire_materialization": record.flywire_materialization,
                "flywire_annotation_release": record.flywire_annotation_release,
                "flywire_type": record.flywire_type,
                "updated_root_ids": record.updated_root_ids,
                "lineage_method": record.lineage_method,
                "male_cns_release": record.male_cns_release,
                "candidates": [_candidate_key(item) for item in record.candidates],
                "status": record.status.value,
                "evidence_sources": record.evidence_sources,
                "evidence_notes": record.evidence_notes,
            }
        )
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b"malecns-sim-task007-mapping-v1\0" + encoded).hexdigest()


def population_fingerprint(population: SugarPopulation) -> str:
    payload = asdict(population)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b"malecns-sim-task007-sugar-population-v1\0" + encoded).hexdigest()


def derive_sugar_population(
    candidates: Iterable[MaleCNSCandidate],
    *,
    side: str,
    side_field: str = "root_side",
    flywire_types: Sequence[str] = ("LB3",),
) -> SugarPopulation:
    """Select biologically filtered sugar candidates without using graph paths."""

    if side_field not in {"side", "soma_side", "root_side"}:
        raise ValueError("side_field must identify an explicit candidate side field")
    allowed = set(flywire_types)
    selected: dict[str, MaleCNSCandidate] = {}
    for candidate in candidates:
        value = getattr(candidate, side_field)
        if (
            candidate.flywire_type in allowed
            and candidate.superclass == "cb_sensory"
            and candidate.cell_class == "gustatory"
            and candidate.entry_nerve == "MxLbN"
            and value == side
        ):
            selected[candidate.body_id] = candidate
    ordered = tuple(sorted(selected.values(), key=lambda item: int(item.body_id)))

    def counts(values: Iterable[str | None]) -> tuple[tuple[str, int], ...]:
        counter = Counter(value if value is not None else "<missing>" for value in values)
        return tuple(sorted(counter.items()))

    nt_values = (
        "resolved" if candidate.resolved_nt is not None else "unresolved"
        for candidate in ordered
    )
    return SugarPopulation(
        candidate_body_ids=tuple(item.body_id for item in ordered),
        side_field=side_field,
        side_counts=counts(getattr(item, side_field) for item in ordered),
        type_counts=counts(item.type for item in ordered),
        receptor_type_counts=counts(item.receptor_type for item in ordered),
        entry_nerve_counts=counts(item.entry_nerve for item in ordered),
        task004_nt_counts=counts(nt_values),
        evidence_notes=(
            "Selected by cross-brain flywireType plus cb_sensory/gustatory/MxLbN metadata.",
            "Side filter uses rootSide because somaSide is absent for these MaleCNS candidates.",
            "No receptor identity is inferred when receptorType is missing.",
        ),
    )


def define_mn9_readout(record: MappingRecord) -> MN9Readout:
    """Convert an MN9 mapping record into an explicit later-readout contract."""

    selected = record.candidate_body_ids[0] if record.status is MappingStatus.EXACT else None
    return MN9Readout(
        status=record.status,
        candidate_body_ids=record.candidate_body_ids,
        selected_body_id=selected,
        evidence_notes=(
            "Task 008 must use every documented candidate unless a later identity task resolves the set.",
        ),
    )


@dataclass(frozen=True, slots=True)
class StructuralPathSummary:
    direct_sugar_to_mn9_edges: int
    first_hop_target_count: int
    shortest_path_lengths: tuple[tuple[str, int], ...]
    reachable_mn9_candidate_ids: tuple[str, ...]
    total_structural_path_availability: int
    first_hop_target_fingerprint: str


def structural_path_summary(
    source_ids: Iterable[int | str],
    target_ids: Iterable[int | str],
    sugar_ids: Iterable[int | str],
    mn9_ids: Iterable[int | str],
) -> StructuralPathSummary:
    """Measure directed structural paths on an already curated edge list.

    This helper performs no dynamics and has no scoring or identity-selection
    behavior.  It reports the shortest path to each requested MN9 candidate.
    """

    sources = tuple(_id(value) for value in source_ids)
    targets = tuple(_id(value) for value in target_ids)
    if len(sources) != len(targets):
        raise ValueError("source_ids and target_ids must have equal lengths")
    sugar = tuple(sorted({_id(value) for value in sugar_ids}, key=int))
    mn9 = tuple(sorted({_id(value) for value in mn9_ids}, key=int))
    adjacency: dict[str, set[str]] = {}
    direct = 0
    mn9_set = set(mn9)
    for source, target in zip(sources, targets):
        adjacency.setdefault(source, set()).add(target)
        if source in sugar and target in mn9_set:
            direct += 1

    first_hop = set().union(*(adjacency.get(item, set()) for item in sugar)) if sugar else set()
    distances: dict[str, int] = {}
    queue: deque[tuple[str, int]] = deque((item, 0) for item in sugar)
    visited = set(sugar)
    while queue:
        node, distance = queue.popleft()
        if node in mn9_set and node not in distances:
            distances[node] = distance
        for neighbor in adjacency.get(node, ()):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))
    reachable = tuple(sorted(distances, key=int))
    return StructuralPathSummary(
        direct_sugar_to_mn9_edges=direct,
        first_hop_target_count=len(first_hop),
        shortest_path_lengths=tuple((item, distances[item]) for item in reachable),
        reachable_mn9_candidate_ids=reachable,
        total_structural_path_availability=len(reachable),
        first_hop_target_fingerprint=_fingerprint_ids(first_hop),
    )


def _fingerprint_ids(ids: Iterable[int | str]) -> str:
    payload = "\n".join(sorted((_id(value) for value in ids), key=int)).encode("ascii")
    return hashlib.sha256(b"malecns-sim-task007-id-set-v1\0" + payload).hexdigest()
