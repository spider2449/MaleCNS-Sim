"""Explicit MaleCNS v1.0 Feather inspection and adapter boundary.

The real schema is intentionally supplied as a mapping after inspection. This
prevents guessed column names from becoming project-wide assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

from malecns_sim.data.model import (
    CuratedNeuronProjection,
    CuratedNeuronSelection,
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


def select_publication_neuron_ids(
    annotation_rows: Iterable[Mapping[str, Any]],
    *,
    body_id_column: str = "bodyId",
    superclass_column: str = "superclass",
    status_column: str | None = "status",
) -> CuratedNeuronSelection:
    """Select the publication neuron identity set from inspected annotations.

    The Cell paper defines a body as a neuron when it has a non-empty
    ``superclass`` annotation. Status is reported for auditability but is not
    an inclusion predicate; in particular, ``Glia`` and missing status values
    are not silently removed from the publication-defined set.
    """

    rows = list(annotation_rows)
    retained: list[int] = []
    excluded: list[int] = []
    exclusion_counts: dict[str, int] = {"missing_superclass": 0}
    seen: set[int] = set()
    missing_status_count = 0
    glia_status_count = 0
    glia_retained_count = 0
    for row in rows:
        raw_id = row.get(body_id_column)
        if isinstance(raw_id, bool) or not isinstance(raw_id, (int, np.integer)):
            raise ValueError(
                f"configured annotation body ID must be an integer: {raw_id!r}"
            )
        body_id = int(raw_id)
        if body_id in seen:
            raise ValueError(f"duplicate annotation body ID: {body_id}")
        seen.add(body_id)

        superclass = row.get(superclass_column)
        included = isinstance(superclass, str) and bool(superclass.strip())
        if included:
            retained.append(body_id)
        else:
            excluded.append(body_id)
            exclusion_counts["missing_superclass"] += 1

        if status_column is not None:
            status = row.get(status_column)
            if status is None:
                missing_status_count += 1
            elif status == "Glia":
                glia_status_count += 1
                if included:
                    glia_retained_count += 1

    retained_ids = np.asarray(sorted(retained), dtype=np.int64)
    excluded_ids = np.asarray(sorted(excluded), dtype=np.int64)
    return CuratedNeuronSelection(
        neuron_ids=retained_ids,
        annotation_count=len(rows),
        excluded_ids=excluded_ids,
        exclusion_counts=tuple(sorted(exclusion_counts.items())),
        missing_status_count=missing_status_count,
        glia_status_count=glia_status_count,
        glia_retained_count=glia_retained_count,
    )


def _aggregate_numeric_edges(
    source_ids: np.ndarray,
    target_ids: np.ndarray,
    synapse_counts: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Sort and aggregate exact integer source-target rows."""

    source_ids = np.asarray(source_ids)
    target_ids = np.asarray(target_ids)
    synapse_counts = np.asarray(synapse_counts)
    if source_ids.dtype.kind not in "iu" or target_ids.dtype.kind not in "iu":
        raise ValueError("projected edge IDs must use integer arrays")
    if synapse_counts.dtype.kind not in "iu":
        raise ValueError("projected synapse counts must use an integer array")
    int64_max = np.iinfo(np.int64).max
    if any(
        array.dtype.kind == "u" and np.any(array > int64_max)
        for array in (source_ids, target_ids, synapse_counts)
    ):
        raise ValueError("projected integer values must fit in int64")
    if not (source_ids.size == target_ids.size == synapse_counts.size):
        raise ValueError("projected edge arrays must have equal lengths")
    if source_ids.size == 0:
        empty = np.asarray([], dtype=np.int64)
        return empty, empty.copy(), empty.copy(), 0

    source_ids = source_ids.astype(np.int64, copy=False)
    target_ids = target_ids.astype(np.int64, copy=False)
    synapse_counts = synapse_counts.astype(np.int64, copy=False)
    max_id = int(max(source_ids.max(initial=0), target_ids.max(initial=0)))
    min_id = int(min(source_ids.min(initial=0), target_ids.min(initial=0)))
    uint64_max = np.iinfo(np.uint64).max
    use_compact_key = min_id >= 0 and max_id + 1 <= uint64_max // max(max_id, 1)
    if use_compact_key:
        keys = source_ids.astype(np.uint64) * np.uint64(max_id + 1) + target_ids.astype(
            np.uint64
        )
        order = np.argsort(keys, kind="stable")
        sorted_keys = keys[order]
        starts = np.r_[0, np.flatnonzero(sorted_keys[1:] != sorted_keys[:-1]) + 1]
    else:
        keys = np.empty(source_ids.size, dtype=np.dtype([("source", "<i8"), ("target", "<i8")]))
        keys["source"] = source_ids
        keys["target"] = target_ids
        order = np.argsort(keys, order=("source", "target"), kind="stable")
        sorted_keys = keys[order]
        starts = np.r_[0, np.flatnonzero(sorted_keys[1:] != sorted_keys[:-1]) + 1]
    sorted_source = source_ids[order]
    sorted_target = target_ids[order]
    sorted_weights = synapse_counts[order]
    unique_source = sorted_source[starts]
    unique_target = sorted_target[starts]
    unique_weights = np.add.reduceat(sorted_weights, starts)
    duplicate_count = int(source_ids.size - unique_source.size)
    return unique_source, unique_target, unique_weights, duplicate_count


def project_numeric_connectome(
    connectome: NumericNormalizedConnectome,
    curated_neuron_ids: np.ndarray | CuratedNeuronSelection,
) -> CuratedNeuronProjection:
    """Project segment-level edges onto a curated neuron identity set."""

    if isinstance(curated_neuron_ids, CuratedNeuronSelection):
        curated_neuron_ids = curated_neuron_ids.neuron_ids
    curated_ids = np.asarray(curated_neuron_ids)
    if curated_ids.dtype.kind not in "iu":
        raise ValueError("curated neuron IDs must use an integer array")
    if curated_ids.dtype.kind == "u" and np.any(curated_ids > np.iinfo(np.int64).max):
        raise ValueError("curated neuron IDs must fit in int64")
    curated_ids = curated_ids.astype(np.int64, copy=False)
    if curated_ids.size and np.any(curated_ids[1:] <= curated_ids[:-1]):
        raise ValueError("curated neuron IDs must be unique and ascending")

    endpoint_mask = np.isin(connectome.source_ids, curated_ids) & np.isin(
        connectome.target_ids, curated_ids
    )
    source_ids, target_ids, synapse_counts, duplicate_count = _aggregate_numeric_edges(
        connectome.source_ids[endpoint_mask],
        connectome.target_ids[endpoint_mask],
        connectome.synapse_counts[endpoint_mask],
    )
    curated_id_set = set(curated_ids.tolist())
    projected = NumericNormalizedConnectome(
        neuron_ids=curated_ids.copy(),
        source_ids=source_ids,
        target_ids=target_ids,
        synapse_counts=synapse_counts,
        annotated_neurons=tuple(
            neuron
            for neuron in connectome.annotated_neurons
            if int(neuron.neuron_id) in curated_id_set
        ),
        provenance=connectome.provenance + (("projection", "publication-superclass"),),
    )
    return CuratedNeuronProjection(
        connectome=projected,
        raw_edge_count=connectome.edge_count,
        endpoint_edge_count=int(endpoint_mask.sum()),
        projected_edge_count=projected.edge_count,
        duplicate_pair_count=duplicate_count,
    )


def threshold_curated_projection(
    projection: CuratedNeuronProjection, *, min_synapses: int
) -> CuratedNeuronProjection:
    """Apply a connection-strength threshold after neuron projection."""

    if isinstance(min_synapses, bool) or not isinstance(min_synapses, int):
        raise TypeError("min_synapses must be an integer")
    if min_synapses < 0:
        raise ValueError("min_synapses must be a non-negative integer")
    selected = projection.connectome.synapse_counts >= min_synapses
    filtered = NumericNormalizedConnectome(
        neuron_ids=projection.connectome.neuron_ids.copy(),
        source_ids=projection.connectome.source_ids[selected],
        target_ids=projection.connectome.target_ids[selected],
        synapse_counts=projection.connectome.synapse_counts[selected],
        annotated_neurons=projection.connectome.annotated_neurons,
        provenance=projection.connectome.provenance
        + (("min_synapses", str(min_synapses)),),
    )
    return CuratedNeuronProjection(
        connectome=filtered,
        raw_edge_count=projection.raw_edge_count,
        endpoint_edge_count=projection.endpoint_edge_count,
        projected_edge_count=projection.projected_edge_count,
        duplicate_pair_count=projection.duplicate_pair_count,
        threshold=min_synapses,
    )
