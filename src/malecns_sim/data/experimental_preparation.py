"""Opt-in A015/A016 endpoint filtering; never selected by production.

The full-column and bounded-batch routes certify publication scientific content,
not general raw graph diagnostics.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import time

import numpy as np

from malecns_sim.data.male_cns_v1 import (
    _aggregate_numeric_edges, _integer_column, load_male_cns_v1_numeric,
    select_publication_neuron_ids,
)


def endpoint_membership(values: np.ndarray, universe: np.ndarray) -> np.ndarray:
    """Exact vector membership in a sorted immutable int64 universe."""
    if not universe.size:
        return np.zeros(values.size, dtype=bool)
    positions = np.searchsorted(universe, values)
    valid = positions < universe.size
    positions = np.minimum(positions, universe.size - 1)
    return valid & (universe[positions] == values)


def experimental_load_publication_numeric(annotation_path, neurotransmitter_path,
                                          weights_path, mapping):
    """Filter validated rows before grouping, using the original metadata oracle.

    Input columns are still materialized in full (architecture A). No source
    download, runtime execution, global dispatch change, or cache is involved.
    Raw union/statistics are intentionally unavailable from this result.
    """
    import pyarrow as pa
    import pyarrow.feather as feather

    annotations = feather.read_table(annotation_path).to_pylist()
    universe = select_publication_neuron_ids(
        annotations, body_id_column=mapping.annotation_body_id,
        superclass_column=mapping.annotation_class or "superclass",
        status_column=mapping.annotation_status,
    ).neuron_ids
    universe.flags.writeable = False
    table = feather.read_table(weights_path, columns=[
        mapping.edge_source_id, mapping.edge_target_id, mapping.edge_weight,
    ])
    source = _integer_column(table, mapping.edge_source_id)
    target = _integer_column(table, mapping.edge_target_id)
    counts = _integer_column(table, mapping.edge_weight)
    if np.any(counts < 0):
        raise ValueError("synapse counts must be non-negative")
    # The reference loader's packed-key branch does not guard negative IDs.
    # Preserve its behavior rather than replacing it with the safer shared
    # grouping primitive for that unsupported release-shaped input domain.
    if np.any(source < 0) or np.any(target < 0):
        return load_male_cns_v1_numeric(
            annotation_path, neurotransmitter_path, weights_path, mapping,
        )
    mask = endpoint_membership(source, universe) & endpoint_membership(target, universe)
    retained = (source[mask], target[mask], counts[mask])
    del table, source, target, counts, mask
    return _publication_from_retained(annotation_path, neurotransmitter_path,
                                      weights_path, mapping, universe, retained)


def _publication_from_retained(annotation_path, neurotransmitter_path,
                               weights_path, mapping, universe, retained, *, grouped=False):
    import pyarrow as pa
    import pyarrow.feather as feather
    if grouped:
        source, target, counts = retained
    else:
        source, target, counts, _ = _aggregate_numeric_edges(*retained)
    del retained
    # Reuse the production annotation/NT normalization without duplicating it.
    with tempfile.TemporaryDirectory(prefix="malecns-a015-metadata-") as directory:
        empty_path = Path(directory) / "empty.feather"
        feather.write_feather(pa.table({name: pa.array([], type=pa.int64()) for name in (
            mapping.edge_source_id, mapping.edge_target_id, mapping.edge_weight,
        )}), empty_path)
        metadata = load_male_cns_v1_numeric(
            annotation_path, neurotransmitter_path, empty_path, mapping,
        )
    return replace(metadata, neuron_ids=universe, source_ids=source,
                   target_ids=target, synapse_counts=counts,
                   provenance=tuple((key, str(Path(weights_path)) if key == "weights_source" else value)
                                    for key, value in metadata.provenance))


def retain_edge_batches(weights_path, universe, columns, max_rows_per_batch=65536, metrics=None):
    """Validate every row, then copy only retained numeric rows in source order."""
    from malecns_sim.data.feather_batches import edge_batches
    retained = []
    def record(stage, started):
        if metrics is not None:
            metrics[stage] = metrics.get(stage, 0) + time.perf_counter() - started
    with edge_batches(weights_path, columns, max_rows_per_batch) as batches:
        while True:
            started = time.perf_counter()
            try:
                table = next(batches)
            except StopIteration:
                record("source_iteration", started)
                break
            record("source_iteration", started)
            started = time.perf_counter()
            source, target, counts = (_integer_column(table, name) for name in columns)
            if np.any(counts < 0):
                raise ValueError("synapse counts must be non-negative")
            # Negative endpoints require the A015 reference fallback, never
            # a silently different aggregation algorithm.
            if np.any(source < 0) or np.any(target < 0):
                raise NegativeEndpointFallback()
            record("raw_validation", started)
            started = time.perf_counter()
            mask = endpoint_membership(source, universe) & endpoint_membership(target, universe)
            record("endpoint_filter", started)
            started = time.perf_counter()
            if mask.any():
                retained.append((source[mask], target[mask], counts[mask]))
            record("retained_copy", started)
            del table, source, target, counts, mask
    started = time.perf_counter()
    result = tuple(np.concatenate([batch[i] for batch in retained]) if retained
                   else np.empty(0, dtype=np.int64) for i in range(3))
    record("retained_concatenation", started)
    return result


class NegativeEndpointFallback(ValueError):
    """The reference packed-key behavior requires full-source fallback."""


def experimental_load_batched_publication_numeric(annotation_path, neurotransmitter_path,
                                                  weights_path, mapping, *, max_rows_per_batch=65536, metrics=None):
    """Opt-in architecture B; retained batches concatenate before shared grouping."""
    import pyarrow.feather as feather
    annotations = feather.read_table(annotation_path).to_pylist()
    universe = select_publication_neuron_ids(
        annotations, body_id_column=mapping.annotation_body_id,
        superclass_column=mapping.annotation_class or "superclass",
        status_column=mapping.annotation_status,
    ).neuron_ids
    universe.flags.writeable = False
    try:
        retained = retain_edge_batches(weights_path, universe,
            (mapping.edge_source_id, mapping.edge_target_id, mapping.edge_weight), max_rows_per_batch, metrics)
    except NegativeEndpointFallback:
        return load_male_cns_v1_numeric(annotation_path, neurotransmitter_path, weights_path, mapping)
    return _publication_from_retained(annotation_path, neurotransmitter_path,
                                      weights_path, mapping, universe, retained)
