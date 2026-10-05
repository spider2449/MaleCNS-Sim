"""Experimental A017 checked integer runs; no scientific transformations."""
from __future__ import annotations

import time
import numpy as np

from malecns_sim.data.male_cns_v1 import _integer_column
from malecns_sim.data.experimental_preparation import (
    NegativeEndpointFallback, endpoint_membership, _publication_from_retained,
)


def group_integer_pairs(source, target, counts):
    """Own sorted int64 columns, rejecting sums outside the exact int64 domain.

    No path creates a Python object per row. Potentially unsafe groups sum
    numeric 32-bit limbs in bounded blocks, with Python integers per block.
    """
    arrays = tuple(np.asarray(a) for a in (source, target, counts))
    limit = np.iinfo(np.int64).max
    if any(a.ndim != 1 or a.dtype.kind not in "iu" for a in arrays):
        raise ValueError("integer columns must be one-dimensional")
    if len({a.size for a in arrays}) != 1:
        raise ValueError("integer columns must have equal lengths")
    if any(np.any(a < 0) or np.any(a > limit) for a in arrays):
        raise ValueError("non-negative integer columns must fit int64")
    source, target, counts = (a.astype(np.int64, copy=False) for a in arrays)
    if not counts.size:
        return tuple(np.empty(0, dtype=np.int64) for _ in range(3))
    order = np.lexsort((target, source))
    pre, post, values = source[order], target[order], counts[order]
    starts = np.r_[0, np.flatnonzero((pre[1:] != pre[:-1]) | (post[1:] != post[:-1])) + 1]
    lengths = np.diff(np.r_[starts, values.size])
    maxima = np.maximum.reduceat(values, starts)
    risky = np.flatnonzero(maxima > limit // lengths)
    for group in risky:
        start = int(starts[group])
        end = start + int(lengths[group])
        total = 0
        for offset in range(start, end, 65536):
            block = values[offset:min(offset + 65536, end)]
            low = int(np.sum(block & np.int64(0xffffffff), dtype=np.uint64))
            high = int(np.sum(block >> 32, dtype=np.uint64))
            total += low + (high << 32)
            if total > limit:
                raise OverflowError("grouped synapse count exceeds int64")
    return pre[starts], post[starts], np.add.reduceat(values, starts)


def merge_integer_runs(runs, metrics=None):
    """Candidate A: concatenate compact partial runs, then checked canonical group."""
    started = time.perf_counter()
    columns = tuple(np.concatenate([run[i] for run in runs]) if runs else
                    np.empty(0, dtype=np.int64) for i in range(3))
    if metrics is not None:
        metrics["merge_input_bytes"] = sum(a.nbytes for a in columns)
        # Workspace excludes concatenated input and includes reduction output.
        metrics["merge_workspace_bound_bytes"] = 104 * columns[0].size
    runs.clear()
    result = group_integer_pairs(*columns)
    if metrics is not None:
        metrics["merge_seconds"] = time.perf_counter() - started
        metrics["final_grouped_bytes"] = sum(a.nbytes for a in result)
    return result


def aggregate_edge_batches(weights_path, universe, columns, max_rows_per_batch=65536,
                           metrics=None, observer=None):
    """Validate all rows, filter, and release raw copies after each local group.

    An optional synchronous observer receives arrays only for lifetime tests.
    It must not keep strong references. Numeric partial runs own their storage.
    """
    from malecns_sim.data.feather_batches import edge_batches
    metrics = {} if metrics is None else metrics
    runs = []
    metrics.update(retained_rows=0, partial_rows=0, partial_peak_bytes=0,
                   local_grouping_seconds=0.0, partial_accumulation_seconds=0.0,
                   chunk_retained_peak_bytes=0, chunk_aggregate_peak_bytes=0,
                   source_peak_bytes=0, mask_peak_bytes=0)
    with edge_batches(weights_path, columns, max_rows_per_batch) as batches:
        for table in batches:
            source, target, counts = (_integer_column(table, name) for name in columns)
            if np.any(counts < 0):
                raise ValueError("synapse counts must be non-negative")
            if np.any(source < 0) or np.any(target < 0):
                raise NegativeEndpointFallback()
            mask = endpoint_membership(source, universe) & endpoint_membership(target, universe)
            retained = source[mask], target[mask], counts[mask]
            metrics["source_peak_bytes"] = max(metrics["source_peak_bytes"], sum(a.nbytes for a in (source, target, counts)))
            metrics["mask_peak_bytes"] = max(metrics["mask_peak_bytes"], mask.nbytes)
            metrics["chunk_retained_peak_bytes"] = max(metrics["chunk_retained_peak_bytes"], sum(a.nbytes for a in retained))
            started = time.perf_counter()
            run = group_integer_pairs(*retained)
            metrics["local_grouping_seconds"] += time.perf_counter() - started
            if observer is not None:
                observer(table, mask, retained, run)
            metrics["retained_rows"] += retained[0].size
            metrics["partial_rows"] += run[0].size
            metrics["chunk_aggregate_peak_bytes"] = max(metrics["chunk_aggregate_peak_bytes"], sum(a.nbytes for a in run))
            del table, source, target, counts, mask, retained
            started = time.perf_counter()
            if run[0].size:
                runs.append(run)
            metrics["partial_accumulation_seconds"] += time.perf_counter() - started
            metrics["partial_peak_bytes"] = 24 * metrics["partial_rows"]
            del run
    return merge_integer_runs(runs, metrics)


def experimental_load_aggregated_publication_numeric(annotation_path, neurotransmitter_path,
        weights_path, mapping, *, max_rows_per_batch=65536, metrics=None):
    """Explicit opt-in seam; production preparation dispatch remains unchanged."""
    import pyarrow.feather as feather
    from malecns_sim.data.male_cns_v1 import select_publication_neuron_ids, load_male_cns_v1_numeric
    universe = select_publication_neuron_ids(
        feather.read_table(annotation_path).to_pylist(), body_id_column=mapping.annotation_body_id,
        superclass_column=mapping.annotation_class or "superclass", status_column=mapping.annotation_status,
    ).neuron_ids
    universe.flags.writeable = False
    try:
        grouped = aggregate_edge_batches(weights_path, universe,
            (mapping.edge_source_id, mapping.edge_target_id, mapping.edge_weight), max_rows_per_batch, metrics)
    except NegativeEndpointFallback:
        return load_male_cns_v1_numeric(annotation_path, neurotransmitter_path, weights_path, mapping)
    except OverflowError:
        # Preserve the oracle's modular arithmetic even for overflow-shaped
        # inputs. This exceptional reference route has A016 memory ownership,
        # and is not certified as the bounded A017 aggregation route.
        from malecns_sim.data.experimental_preparation import experimental_load_batched_publication_numeric
        if metrics is not None:
            metrics["overflow_reference_fallback"] = True
        return experimental_load_batched_publication_numeric(
            annotation_path, neurotransmitter_path, weights_path, mapping,
            max_rows_per_batch=max_rows_per_batch)
    return _publication_from_retained(annotation_path, neurotransmitter_path, weights_path,
                                     mapping, universe, grouped, grouped=True)
