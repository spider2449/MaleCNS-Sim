"""Task 008a sensory laterality audit primitives."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import pyarrow.feather as feather


SUGAR_PREDICATE = {
    "flywireType": "LB3",
    "superclass": "cb_sensory",
    "class": "gustatory",
    "entryNerve": "MxLbN",
}
CURRENT_TASK008_SIDE_FIELD = "rootSide"
ANATOMICAL_SENSORY_SIDE_FIELD = "rootSide"
VALID_AS_RUN = "VALID_AS_RUN"
POPULATION_SIDE_CORRECTION_REQUIRED = "POPULATION_SIDE_CORRECTION_REQUIRED"
UNRESOLVED = "UNRESOLVED"


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _json_value(value: object) -> Any:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if hasattr(value, "item"):
        return _json_value(value.item())
    return value


@dataclass(frozen=True, slots=True)
class SugarCandidateAuditRecord:
    """All laterality-relevant source annotations for one sugar candidate."""

    body_id: str
    type: str | None
    instance: str | None
    flywire_type: str | None
    superclass: str | None
    cell_class: str | None
    subclass: str | None
    soma_side: str | None
    root_side: str | None
    soma_neuromere: str | None
    entry_nerve: str | None
    receptor_type: str | None
    matching_notes: str | None
    status: str | None
    status_label: str | None
    exit_nerve: str | None
    soma_location: Any
    to_soma_location: Any
    synonyms: str | None
    vfb_id: str | None
    hemibrain_type: str | None
    manc_type: str | None
    manc_body_id: str | None

    @classmethod
    def from_row(cls, row: Mapping[str, object]) -> "SugarCandidateAuditRecord":
        return cls(
            body_id=str(int(row["bodyId"])),
            type=_text(row.get("type")),
            instance=_text(row.get("instance")),
            flywire_type=_text(row.get("flywireType")),
            superclass=_text(row.get("superclass")),
            cell_class=_text(row.get("class")),
            subclass=_text(row.get("subclass")),
            soma_side=_text(row.get("somaSide")),
            root_side=_text(row.get("rootSide")),
            soma_neuromere=_text(row.get("somaNeuromere")),
            entry_nerve=_text(row.get("entryNerve")),
            receptor_type=_text(row.get("receptorType")),
            matching_notes=_text(row.get("matchingNotes")),
            status=_text(row.get("status")),
            status_label=_text(row.get("statusLabel")),
            exit_nerve=_text(row.get("exitNerve")),
            soma_location=_json_value(row.get("somaLocation")),
            to_soma_location=_json_value(row.get("tosomaLocation")),
            synonyms=_text(row.get("synonyms")),
            vfb_id=_text(row.get("vfbId")),
            hemibrain_type=_text(row.get("hemibrainType")),
            manc_type=_text(row.get("mancType")),
            manc_body_id=(
                str(int(row["mancBodyid"]))
                if row.get("mancBodyid") is not None
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SideCell:
    side: str
    root_side: str
    count: int
    body_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LateralityAudit:
    """Deterministic metadata-only comparison of soma and sensory-root sides."""

    all_lb3_count: int
    excluded_lb3_body_ids: tuple[str, ...]
    candidates: tuple[SugarCandidateAuditRecord, ...]
    crosstab: tuple[SideCell, ...]
    nonmissing_mismatch_body_ids: tuple[str, ...]
    missing_soma_side_body_ids: tuple[str, ...]
    missing_root_side_body_ids: tuple[str, ...]
    soma_left_body_ids: tuple[str, ...]
    soma_right_body_ids: tuple[str, ...]
    root_left_body_ids: tuple[str, ...]
    root_right_body_ids: tuple[str, ...]
    intersection_body_ids: tuple[str, ...]
    left_intersection_body_ids: tuple[str, ...]
    right_intersection_body_ids: tuple[str, ...]
    left_soma_only_body_ids: tuple[str, ...]
    left_root_only_body_ids: tuple[str, ...]
    right_soma_only_body_ids: tuple[str, ...]
    right_root_only_body_ids: tuple[str, ...]
    type_counts_by_side: tuple[tuple[str, tuple[tuple[str, int], ...]], ...]
    entry_nerve_counts_by_side: tuple[tuple[str, tuple[tuple[str, int], ...]], ...]
    instance_suffix_mismatch_body_ids: tuple[str, ...]
    instance_missing_body_ids: tuple[str, ...]

    @property
    def candidate_count(self) -> int:
        return len(self.candidates)

    @property
    def fingerprint(self) -> str:
        payload = asdict(self)
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(b"malecns-sim-task008a-laterality-v1\0" + encoded).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "fingerprint": self.fingerprint}


def _sorted_ids(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted((str(value) for value in values), key=int))


def _counts(values: Iterable[str | None]) -> tuple[tuple[str, int], ...]:
    counts = Counter(value if value is not None else "<missing>" for value in values)
    return tuple(sorted(counts.items()))


def _matches_sugar_predicate(row: Mapping[str, object]) -> bool:
    return all(_text(row.get(field)) == value for field, value in SUGAR_PREDICATE.items())


def load_sugar_candidate_audit(
    annotation_path: str | Path,
) -> tuple[int, tuple[str, ...], tuple[SugarCandidateAuditRecord, ...]]:
    """Load the complete LB3 pool and the pre-side-filter sugar candidate pool."""

    columns = [
        "bodyId", "type", "instance", "flywireType", "superclass", "class", "subclass",
        "somaSide", "rootSide", "somaNeuromere", "entryNerve", "receptorType",
        "matchingNotes", "status", "statusLabel", "exitNerve", "somaLocation",
        "tosomaLocation", "synonyms", "vfbId", "hemibrainType", "mancType", "mancBodyid",
    ]
    rows = feather.read_table(annotation_path, columns=columns).to_pylist()
    lb3_rows = [row for row in rows if _text(row.get("flywireType")) == "LB3"]
    selected = tuple(
        sorted(
            (SugarCandidateAuditRecord.from_row(row) for row in lb3_rows if _matches_sugar_predicate(row)),
            key=lambda item: int(item.body_id),
        )
    )
    selected_ids = {item.body_id for item in selected}
    excluded = _sorted_ids(
        str(row["bodyId"])
        for row in lb3_rows
        if str(int(row["bodyId"])) not in selected_ids
    )
    return len(lb3_rows), excluded, selected


def _side_ids(candidates: Iterable[SugarCandidateAuditRecord], field: str, side: str) -> tuple[str, ...]:
    return _sorted_ids(item.body_id for item in candidates if getattr(item, field) == side)


def build_laterality_audit(
    candidates: Iterable[SugarCandidateAuditRecord],
    *,
    all_lb3_count: int,
    excluded_lb3_body_ids: Iterable[str] = (),
) -> LateralityAudit:
    """Build all side comparisons without consulting graph or dynamics outputs."""

    ordered = tuple(sorted(candidates, key=lambda item: int(item.body_id)))
    by_cell = defaultdict(list)
    for item in ordered:
        by_cell[(item.soma_side or "<missing>", item.root_side or "<missing>")].append(item.body_id)
    crosstab = tuple(
        SideCell(soma, root, len(ids), _sorted_ids(ids))
        for (soma, root), ids in sorted(by_cell.items())
    )
    mismatch = _sorted_ids(
        item.body_id
        for item in ordered
        if item.soma_side is not None
        and item.root_side is not None
        and item.soma_side != item.root_side
    )
    missing_soma = _sorted_ids(item.body_id for item in ordered if item.soma_side is None)
    missing_root = _sorted_ids(item.body_id for item in ordered if item.root_side is None)
    soma_left = set(_side_ids(ordered, "soma_side", "L"))
    soma_right = set(_side_ids(ordered, "soma_side", "R"))
    root_left = set(_side_ids(ordered, "root_side", "L"))
    root_right = set(_side_ids(ordered, "root_side", "R"))
    side_fields = (
        ("soma_L", "soma_side", "L"),
        ("soma_R", "soma_side", "R"),
        ("root_L", "root_side", "L"),
        ("root_R", "root_side", "R"),
    )
    type_counts = tuple(
        (label, _counts(item.type for item in ordered if getattr(item, field) == side))
        for label, field, side in side_fields
    )
    nerve_counts = tuple(
        (label, _counts(item.entry_nerve for item in ordered if getattr(item, field) == side))
        for label, field, side in side_fields
    )
    suffix_mismatch = _sorted_ids(
        item.body_id
        for item in ordered
        if item.instance
        and item.instance.endswith(("_L", "_R"))
        and item.instance[-1] != item.root_side
    )
    return LateralityAudit(
        all_lb3_count=all_lb3_count,
        excluded_lb3_body_ids=_sorted_ids(excluded_lb3_body_ids),
        candidates=ordered,
        crosstab=crosstab,
        nonmissing_mismatch_body_ids=mismatch,
        missing_soma_side_body_ids=missing_soma,
        missing_root_side_body_ids=missing_root,
        soma_left_body_ids=_sorted_ids(soma_left),
        soma_right_body_ids=_sorted_ids(soma_right),
        root_left_body_ids=_sorted_ids(root_left),
        root_right_body_ids=_sorted_ids(root_right),
        intersection_body_ids=_sorted_ids((soma_left & root_left) | (soma_right & root_right)),
        left_intersection_body_ids=_sorted_ids(soma_left & root_left),
        right_intersection_body_ids=_sorted_ids(soma_right & root_right),
        left_soma_only_body_ids=_sorted_ids(soma_left - root_left),
        left_root_only_body_ids=_sorted_ids(root_left - soma_left),
        right_soma_only_body_ids=_sorted_ids(soma_right - root_right),
        right_root_only_body_ids=_sorted_ids(root_right - soma_right),
        type_counts_by_side=type_counts,
        entry_nerve_counts_by_side=nerve_counts,
        instance_suffix_mismatch_body_ids=suffix_mismatch,
        instance_missing_body_ids=_sorted_ids(item.body_id for item in ordered if item.instance is None),
    )


def classify_task008_side_rule(
    current_side_field: str,
    anatomically_supported_side_field: str | None,
    *,
    dynamics_consulted: bool = False,
) -> str:
    """Classify the current population using annotations only."""

    if dynamics_consulted:
        raise ValueError("laterality classification cannot consult dynamics")
    if anatomically_supported_side_field is None:
        return UNRESOLVED
    if current_side_field == anatomically_supported_side_field:
        return VALID_AS_RUN
    return POPULATION_SIDE_CORRECTION_REQUIRED


def population_symmetric_difference(audit: LateralityAudit) -> dict[str, tuple[str, ...]]:
    """Return exact set comparisons for soma-defined and root-defined sides."""

    return {
        "left_soma_only": audit.left_soma_only_body_ids,
        "left_root_only": audit.left_root_only_body_ids,
        "right_soma_only": audit.right_soma_only_body_ids,
        "right_root_only": audit.right_root_only_body_ids,
    }
