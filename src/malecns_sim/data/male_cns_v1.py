"""Explicit MaleCNS v1.0 Feather inspection and adapter boundary.

The real schema is intentionally supplied as a mapping after inspection. This
prevents guessed column names from becoming project-wide assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from malecns_sim.data.model import NormalizedConnectome
from malecns_sim.data.normalize import EdgeColumns, NeuronColumns, normalize_connectome

ADAPTER_SCHEMA_VERSION = "malecns-v1-feather-explicit-mapping-v1"


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
