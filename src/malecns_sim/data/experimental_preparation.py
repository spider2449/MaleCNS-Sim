"""Opt-in A015 endpoint filtering prototype; never selected by production.

This all-column-buffer prototype certifies scientific content, not raw graph
diagnostics. It deliberately leaves the bounded source-reader task separate.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile

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
