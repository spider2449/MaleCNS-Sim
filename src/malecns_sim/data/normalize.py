"""Schema-explicit normalization from rows to deterministic internal records."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from malecns_sim.data.model import EdgeRecord, NeuronRecord, NormalizedConnectome


@dataclass(frozen=True, slots=True)
class NeuronColumns:
    """Canonical normalized column names or an explicit external mapping."""

    neuron_id: str = "neuron_id"
    cell_type: str | None = "cell_type"
    neurotransmitter: str | None = "neurotransmitter"
    ascending: str | None = "ascending"
    descending: str | None = "descending"
    sensory: str | None = "sensory"
    motor_related: str | None = "motor_related"


@dataclass(frozen=True, slots=True)
class EdgeColumns:
    """Column names for a connectivity table."""

    source_id: str = "source_id"
    target_id: str = "target_id"
    synapse_count: str = "synapse_count"


def _value(row: Mapping[str, Any], column: str | None, *, required: bool = True) -> Any:
    if column is None:
        return None
    try:
        return row[column]
    except (KeyError, TypeError) as exc:
        if not required:
            return None
        raise ValueError(f"required configured column is missing: {column!r}") from exc


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float):
        return math.isnan(value)
    return isinstance(value, str) and not value.strip()


def _normalize_id(value: Any, field_name: str) -> str:
    if _is_missing(value) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a non-empty neuron identifier")
    if isinstance(value, float):
        raise ValueError(
            f"{field_name} must not be converted through a floating-point value"
        )
    result = str(value).strip()
    if not result:
        raise ValueError(f"{field_name} must be a non-empty neuron identifier")
    return result


def _optional_text(value: Any) -> str | None:
    if _is_missing(value):
        return None
    return str(value).strip()


def _optional_bool(value: Any) -> bool | None:
    if _is_missing(value):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    normalized = str(value).strip().lower()
    if normalized in {"true", "t", "yes", "y", "1"}:
        return True
    if normalized in {"false", "f", "no", "n", "0"}:
        return False
    raise ValueError(f"cannot normalize {value!r} as a boolean classification")


def _synapse_count(value: Any) -> int:
    if isinstance(value, bool) or _is_missing(value):
        raise ValueError("synapse_count must be a non-negative integer")
    try:
        result = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("synapse_count must be a non-negative integer") from exc
    if isinstance(value, float) and not value.is_integer():
        raise ValueError("synapse_count must be a non-negative integer")
    if result < 0:
        raise ValueError("synapse_count must be a non-negative integer")
    return result


def _id_sort_key(identifier: str) -> tuple[int, int | str, str]:
    """Sort integer-like IDs numerically, then all other IDs lexically."""

    try:
        return (0, int(identifier), identifier)
    except ValueError:
        return (1, identifier, identifier)


def normalize_neurons(
    rows: Iterable[Mapping[str, Any]],
    columns: NeuronColumns | None = None,
) -> tuple[NeuronRecord, ...]:
    """Normalize and deterministically merge neuron rows.

    Repeated rows for an ID may fill previously absent metadata, but conflicting
    non-absent values are rejected to prevent silent biological data loss.
    """

    columns = columns or NeuronColumns()
    merged: dict[str, dict[str, Any]] = {}
    fields = (
        "cell_type",
        "neurotransmitter",
        "ascending",
        "descending",
        "sensory",
        "motor_related",
        "metadata",
    )
    for row in rows:
        neuron_id = _normalize_id(_value(row, columns.neuron_id), columns.neuron_id)
        current = merged.setdefault(neuron_id, {"neuron_id": neuron_id})
        values = {
            "cell_type": _optional_text(_value(row, columns.cell_type, required=False)),
            "neurotransmitter": _optional_text(
                _value(row, columns.neurotransmitter, required=False)
            ),
            "ascending": _optional_bool(_value(row, columns.ascending, required=False)),
            "descending": _optional_bool(_value(row, columns.descending, required=False)),
            "sensory": _optional_bool(_value(row, columns.sensory, required=False)),
            "motor_related": _optional_bool(
                _value(row, columns.motor_related, required=False)
            ),
            "metadata": (),
        }
        for field in fields:
            incoming = values[field]
            existing = current.get(field)
            if incoming is not None and existing is not None and incoming != existing:
                raise ValueError(f"conflicting {field} values for neuron {neuron_id!r}")
            if existing is None and incoming is not None:
                current[field] = incoming
    return tuple(
        NeuronRecord(**merged[neuron_id])
        for neuron_id in sorted(merged, key=_id_sort_key)
    )


def normalize_edges(
    rows: Iterable[Mapping[str, Any]],
    neuron_ids: Iterable[str],
    columns: EdgeColumns | None = None,
) -> tuple[EdgeRecord, ...]:
    """Normalize, validate endpoints, aggregate duplicates, and sort edges."""

    columns = columns or EdgeColumns()
    known_ids = set(neuron_ids)
    aggregated: dict[tuple[str, str], int] = {}
    for row in rows:
        source_id = _normalize_id(_value(row, columns.source_id), columns.source_id)
        target_id = _normalize_id(_value(row, columns.target_id), columns.target_id)
        unknown = {identifier for identifier in (source_id, target_id) if identifier not in known_ids}
        if unknown:
            raise ValueError(f"edge references unknown neuron ID(s): {sorted(unknown)!r}")
        key = (source_id, target_id)
        aggregated[key] = aggregated.get(key, 0) + _synapse_count(
            _value(row, columns.synapse_count)
        )
    return tuple(
        EdgeRecord(source_id, target_id, aggregated[(source_id, target_id)])
        for source_id, target_id in sorted(
            aggregated, key=lambda pair: (_id_sort_key(pair[0]), _id_sort_key(pair[1]))
        )
    )


def normalize_connectome(
    neuron_rows: Iterable[Mapping[str, Any]],
    edge_rows: Iterable[Mapping[str, Any]],
    *,
    neuron_columns: NeuronColumns | None = None,
    edge_columns: EdgeColumns | None = None,
    provenance: Mapping[str, str] | None = None,
) -> NormalizedConnectome:
    """Normalize both tables and preserve explicit adapter provenance."""

    neurons = normalize_neurons(neuron_rows, neuron_columns)
    edges = normalize_edges(edge_rows, (neuron.neuron_id for neuron in neurons), edge_columns)
    normalized_provenance = tuple(sorted((provenance or {}).items()))
    return NormalizedConnectome(neurons, edges, normalized_provenance)
