"""Explicit MaleCNS v1.0 Feather inspection and adapter boundary.

The real schema is intentionally supplied as a mapping after inspection. This
prevents guessed column names from becoming project-wide assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from malecns_sim.data.model import (
    NeuronRecord,
    NormalizedConnectome,
    NumericNormalizedConnectome,
)
from malecns_sim.data.normalize import EdgeColumns, NeuronColumns, normalize_connectome

ADAPTER_SCHEMA_VERSION = "malecns-v1-feather-explicit-mapping-v2"


@dataclass(frozen=True, slots=True)
class FeatherInspection:
    path: str
    row_count: int
    columns: tuple[str, ...]
    dtypes: tuple[tuple[str, str], ...]
    sample: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class MaleCNSV1ColumnMapping:
    """Column mapping recorded from an inspected release schema."""

    annotation_body_id: str
    edge_source_id: str
    edge_target_id: str
    edge_weight: str
    annotation_cell_type: str | None = None
    annotation_side: str | None = None
    annotation_class: str | None = None
    annotation_status: str | None = None
    neurotransmitter_body_id: str | None = None
    neurotransmitter_prediction_columns: tuple[str, ...] = ()
    neurotransmitter_probability_columns: tuple[str, ...] = ()


def official_v1_mapping() -> MaleCNSV1ColumnMapping:
    """Return the mapping measured from the official v1.0 Feather schemas."""

    return MaleCNSV1ColumnMapping(
        annotation_body_id="bodyId",
        edge_source_id="body_pre",
        edge_target_id="body_post",
        edge_weight="weight",
        annotation_cell_type="type",
        annotation_side="somaSide",
        annotation_class="superclass",
        annotation_status="status",
        neurotransmitter_body_id="body",
        neurotransmitter_prediction_columns=(
            "consensus_nt",
            "predicted_nt",
            "celltype_predicted_nt",
        ),
        neurotransmitter_probability_columns=(
            "predicted_nt_confidence",
            "celltype_predicted_nt_confidence",
        ),
    )


def inspect_feather(path: str | Path, *, sample_rows: int = 5) -> FeatherInspection:
    import pyarrow.feather as feather

    table = feather.read_table(path)
    sample = tuple(dict(row) for row in table.slice(0, sample_rows).to_pylist())
    return FeatherInspection(
        path=str(Path(path)),
        row_count=table.num_rows,
        columns=tuple(table.column_names),
        dtypes=tuple((field.name, str(field.type)) for field in table.schema),
        sample=sample,
    )


def _rows(path: str | Path) -> list[dict[str, Any]]:
    import pyarrow.feather as feather

    return feather.read_table(path).to_pylist()


def _metadata(row: dict[str, Any], columns: Iterable[str | None]) -> tuple[tuple[str, str], ...]:
    values = []
    for column in columns:
        if column is not None and column in row and row[column] is not None:
            values.append((column, str(row[column])))
    return tuple(sorted(values))


def load_male_cns_v1(
    annotation_path: str | Path,
    neurotransmitter_path: str | Path,
    weights_path: str | Path,
    mapping: MaleCNSV1ColumnMapping,
) -> NormalizedConnectome:
    """Load three inspected v1.0 Feather files into Task 001 records."""

    annotation_rows = _rows(annotation_path)
    neurotransmitter_rows = _rows(neurotransmitter_path)
    edge_rows = _rows(weights_path)
    nt_id = mapping.neurotransmitter_body_id or mapping.annotation_body_id
    nt_by_id: dict[str, dict[str, Any]] = {}
    for row in neurotransmitter_rows:
        body_id = row.get(nt_id)
        if body_id is None:
            continue
        body_key = str(body_id)
        if body_key in nt_by_id:
            raise ValueError(f"duplicate neurotransmitter body ID: {body_key!r}")
        nt_by_id[body_key] = row
    neuron_rows: list[dict[str, Any]] = []
    for row in annotation_rows:
        body_id = row.get(mapping.annotation_body_id)
        if body_id is None:
            raise ValueError(f"annotation body ID is null in {mapping.annotation_body_id!r}")
        body_key = str(body_id)
        nt_row = nt_by_id.get(body_key, {})
        prediction_values = [nt_row.get(column) for column in mapping.neurotransmitter_prediction_columns]
        prediction = next((value for value in prediction_values if value is not None), None)
        normalized = {
            "neuron_id": body_id,
            "cell_type": row.get(mapping.annotation_cell_type) if mapping.annotation_cell_type else None,
            "neurotransmitter": prediction,
            "metadata": _metadata(
                row,
                (mapping.annotation_side, mapping.annotation_class, mapping.annotation_status),
            )
            + _metadata(
                nt_row,
                mapping.neurotransmitter_prediction_columns
                + mapping.neurotransmitter_probability_columns,
            ),
        }
        neuron_rows.append(normalized)

    annotation_ids = {str(row["neuron_id"]) for row in neuron_rows}
    for edge in edge_rows:
        for column in (mapping.edge_source_id, mapping.edge_target_id):
            value = edge.get(column)
            if value is not None and str(value) not in annotation_ids:
                neuron_rows.append({"neuron_id": value})
                annotation_ids.add(str(value))

    normalized_edges = [
        {
            "source_id": row.get(mapping.edge_source_id),
            "target_id": row.get(mapping.edge_target_id),
            "synapse_count": row.get(mapping.edge_weight),
        }
        for row in edge_rows
    ]
    neurons = normalize_connectome(
        neuron_rows,
        normalized_edges,
        neuron_columns=NeuronColumns(
            neuron_id="neuron_id",
            cell_type="cell_type",
            neurotransmitter="neurotransmitter",
            ascending=None,
            descending=None,
            sensory=None,
            motor_related=None,
        ),
        edge_columns=EdgeColumns(),
        provenance={
            "adapter": ADAPTER_SCHEMA_VERSION,
            "annotation_source": str(Path(annotation_path)),
            "neurotransmitter_source": str(Path(neurotransmitter_path)),
            "weights_source": str(Path(weights_path)),
        },
    )
    # Add normalized source metadata after generic normalization while keeping
    # the existing model boundary immutable.
    metadata_by_id = {str(row["neuron_id"]): row.get("metadata", ()) for row in neuron_rows}
    return replace(
        neurons,
        neurons=tuple(
            replace(neuron, metadata=metadata_by_id.get(neuron.neuron_id, ()))
            for neuron in neurons.neurons
        ),
    )


def _integer_column(table: Any, column: str) -> np.ndarray:
    import pyarrow.types as types

    field = table.schema.field(column)
    if not types.is_integer(field.type):
        raise ValueError(f"configured integer column is not an integer: {column!r}")
    array = table[column].combine_chunks()
    if array.null_count:
        raise ValueError(f"configured integer column contains nulls: {column!r}")
    return np.asarray(array.to_numpy(zero_copy_only=False), dtype=np.int64)


def load_male_cns_v1_numeric(
    annotation_path: str | Path,
    neurotransmitter_path: str | Path,
    weights_path: str | Path,
    mapping: MaleCNSV1ColumnMapping,
) -> NumericNormalizedConnectome:
    """Load v1.0 Feather data into a compact exact-integer representation.

    This is the large-file counterpart to :func:`load_male_cns_v1`. It keeps
    all segment endpoints and weights in NumPy arrays, aggregates duplicate
    source-target pairs, and stores normalized annotation records without
    materializing one Python object per edge or segment.
    """

    import pyarrow.feather as feather

    annotation_table = feather.read_table(annotation_path)
    neurotransmitter_table = feather.read_table(neurotransmitter_path)
    edge_table = feather.read_table(
        weights_path,
        columns=[mapping.edge_source_id, mapping.edge_target_id, mapping.edge_weight],
    )
    for column in (
        mapping.annotation_body_id,
        mapping.edge_source_id,
        mapping.edge_target_id,
        mapping.edge_weight,
    ):
        table = annotation_table if column == mapping.annotation_body_id else edge_table
        if column not in table.column_names:
            raise ValueError(f"required configured column is missing: {column!r}")

    annotation_ids = _integer_column(annotation_table, mapping.annotation_body_id)
    source_ids = _integer_column(edge_table, mapping.edge_source_id)
    target_ids = _integer_column(edge_table, mapping.edge_target_id)
    synapse_counts = _integer_column(edge_table, mapping.edge_weight)
    if np.any(synapse_counts < 0):
        raise ValueError("synapse counts must be non-negative")

    annotation_rows = annotation_table.to_pylist()
    nt_id_array = _integer_column(neurotransmitter_table, mapping.neurotransmitter_body_id or mapping.annotation_body_id)
    nt_positions = {int(body_id): index for index, body_id in enumerate(nt_id_array)}
    nt_rows = neurotransmitter_table.to_pylist()
    annotation_neurons: list[NeuronRecord] = []
    seen_annotation_ids: set[int] = set()
    for row in annotation_rows:
        raw_id = row[mapping.annotation_body_id]
        if raw_id is None:
            raise ValueError(f"annotation body ID is null in {mapping.annotation_body_id!r}")
        body_id = int(raw_id)
        if body_id in seen_annotation_ids:
            raise ValueError(f"duplicate annotation body ID: {body_id}")
        seen_annotation_ids.add(body_id)
        nt_row = nt_rows[nt_positions[body_id]] if body_id in nt_positions else {}
        prediction = next(
            (nt_row.get(column) for column in mapping.neurotransmitter_prediction_columns if nt_row.get(column) is not None),
            None,
        )
        metadata = _metadata(
            row,
            (mapping.annotation_side, mapping.annotation_class, mapping.annotation_status),
        ) + _metadata(
            nt_row,
            mapping.neurotransmitter_prediction_columns + mapping.neurotransmitter_probability_columns,
        )
        annotation_neurons.append(
            NeuronRecord(
                neuron_id=str(body_id),
                cell_type=str(row[mapping.annotation_cell_type]).strip()
                if mapping.annotation_cell_type and row.get(mapping.annotation_cell_type) is not None
                else None,
                neurotransmitter=str(prediction).strip() if prediction is not None else None,
                metadata=metadata,
            )
        )

    max_id = int(max(source_ids.max(initial=0), target_ids.max(initial=0)))
    if max_id < 2**32:
        pair_keys = source_ids.astype(np.uint64) * np.uint64(max_id + 1) + target_ids.astype(np.uint64)
    else:
        pair_keys = np.empty(
            source_ids.size,
            dtype=np.dtype([("source", "<i8"), ("target", "<i8")]),
        )
        pair_keys["source"] = source_ids
        pair_keys["target"] = target_ids
    unique_keys, pair_counts = np.unique(pair_keys, return_counts=True)
    order = np.argsort(pair_keys, kind="stable")
    if unique_keys.size != pair_keys.size:
        sorted_keys = pair_keys[order]
        starts = np.r_[0, np.flatnonzero(sorted_keys[1:] != sorted_keys[:-1]) + 1]
        source_ids = source_ids[order][starts]
        target_ids = target_ids[order][starts]
        synapse_counts = np.add.reduceat(synapse_counts[order], starts)
    else:
        source_ids = source_ids[order]
        target_ids = target_ids[order]
        synapse_counts = synapse_counts[order]
    del pair_keys, unique_keys, pair_counts
    neuron_ids = np.unique(np.concatenate((annotation_ids, source_ids, target_ids)))
    return NumericNormalizedConnectome(
        neuron_ids=neuron_ids,
        source_ids=source_ids,
        target_ids=target_ids,
        synapse_counts=synapse_counts,
        annotated_neurons=tuple(sorted(annotation_neurons, key=lambda neuron: int(neuron.neuron_id))),
        provenance=tuple(
            sorted(
                {
                    "adapter": ADAPTER_SCHEMA_VERSION,
                    "annotation_source": str(Path(annotation_path)),
                    "neurotransmitter_source": str(Path(neurotransmitter_path)),
                    "weights_source": str(Path(weights_path)),
                }.items()
            )
        ),
    )
