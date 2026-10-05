"""Synthetic A017 exact integer and downstream certification."""
from functools import partial
from unittest.mock import patch
import weakref

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import pytest

from test_application_a015 import a015, CASES
from malecns_sim.analysis.task008 import prepare_network
from malecns_sim.data.integer_aggregation import (
    aggregate_edge_batches, group_integer_pairs, merge_integer_runs,
    experimental_load_aggregated_publication_numeric,
)
from malecns_sim.data.experimental_preparation import experimental_load_batched_publication_numeric
from malecns_sim.dynamics.lif import PreparedRuntime

FIXTURES = CASES + [
    [(1, 2, 1)] * 19,
    [(1, 2, 2), (2, 3, 1), (1, 2, 3)],
    [(1, 2, 2**32), (1, 2, 2**32)],
    [(pre, post, 1) for pre in range(1, 5) for post in range(1, 5)],
    [(999, 999, 3)] * 8 + [(1, 2, 4)],
]


def proposed(files, size, loader=experimental_load_aggregated_publication_numeric, **kwargs):
    with patch("malecns_sim.analysis.task008.load_male_cns_v1_numeric",
               partial(loader, max_rows_per_batch=size)):
        return prepare_network(*files, **kwargs)


@pytest.mark.parametrize("rows", FIXTURES)
@pytest.mark.parametrize("threshold", [0, 4, 5])
def test_exact_downstream(tmp_path, rows, threshold):
    files = a015.a014.synthetic_files(tmp_path, 1, 4)
    first = None
    for size in (1, 2, 3, 7, 65536):
        feather.write_feather(pa.table({name: pa.array([row[i] for row in rows], type=pa.int64())
            for i, name in enumerate(("body_pre", "body_post", "weight"))}), files[2], chunksize=size)
        reference = proposed(files, size, experimental_load_batched_publication_numeric, min_synapses=threshold)
        result = proposed(files, size, min_synapses=threshold)
        a015.assert_exact(reference, result)
        a015.assert_exact(prepare_network(*files, min_synapses=threshold), result)
        a015.assert_exact(result, proposed(files, size, min_synapses=threshold))
        if first is not None:
            a015.assert_exact(first, result)
        first = result
        left, right = PreparedRuntime(reference.projection), PreparedRuntime(result.projection)
        assert left.identity == right.identity
        assert left.parameters.grid_steps(left.dt_ms) == right.parameters.grid_steps(right.dt_ms)


def test_integer_domain_and_merge():
    rows = np.array([[3, 2, 2], [1, 2, 2], [1, 2, 3], [1, 1, 0]], dtype=np.int64)
    expected = group_integer_pairs(*rows.T)
    for sequence in (rows, rows[::-1]):
        for size in (1, 2, 3):
            runs = [group_integer_pairs(*sequence[i:i+size].T) for i in range(0, len(rows), size)]
            for actual, wanted in zip(merge_integer_runs(runs), expected):
                np.testing.assert_array_equal(actual, wanted)
    assert list(zip(expected[0], expected[1])) == [(1, 1), (1, 2), (3, 2)]
    np.testing.assert_array_equal(expected[2], [0, 5, 2])
    limit = np.iinfo(np.int64).max
    assert group_integer_pairs([1, 1], [2, 2], [limit-1, 1])[2][0] == limit
    assert group_integer_pairs([1, 2], [2, 2], [limit, limit])[2].tolist() == [limit, limit]
    with pytest.raises(OverflowError):
        group_integer_pairs([1, 1], [2, 2], [limit, 1])
    with pytest.raises(OverflowError):
        merge_integer_runs([group_integer_pairs([1], [2], [limit]), group_integer_pairs([1], [2], [1])])
    with pytest.raises(ValueError):
        group_integer_pairs(np.array([2**63], dtype=np.uint64), [2], [1])
    # Exercise two numeric limb blocks without making Python objects per row.
    counts = np.ones(70000, dtype=np.int64)
    counts[0] = limit - 69999
    endpoints = np.ones(counts.size, dtype=np.int64)
    assert group_integer_pairs(endpoints, endpoints, counts)[2][0] == limit
    counts[-1] += 1
    with pytest.raises(OverflowError):
        group_integer_pairs(endpoints, endpoints, counts)


def test_lifetime_bounds_and_no_partial_threshold(tmp_path):
    path = tmp_path / "edges.feather"
    feather.write_feather(pa.table({"body_pre": [1, 999, 1, 1, 1], "body_post": [2]*5,
                                   "weight": [1]*5}), path, chunksize=1)
    previous = []
    sizes = []
    def observe(table, mask, retained, run):
        assert all(ref() is None for ref in previous)
        previous[:] = [weakref.ref(a) for a in (table, mask, *retained)]
        assert all(a.flags.owndata and a.dtype == np.int64 for a in run)
        assert run[0].size <= retained[0].size <= 1
        sizes.append(run[2].tolist())
    metrics = {}
    grouped = aggregate_edge_batches(path, np.array([1, 2]),
        ("body_pre", "body_post", "weight"), 1, metrics, observe)
    assert all(ref() is None for ref in previous)
    assert sizes == [[1], [], [1], [1], [1]]
    assert grouped[2].tolist() == [4]
    assert metrics["partial_peak_bytes"] == 96
    assert metrics["chunk_retained_peak_bytes"] <= 24
    # Reverse physical partition lengths while preserving the source sequence.
    table = pa.table({"body_pre": [1, 999, 1, 1, 1], "body_post": [2]*5,
                      "weight": [1]*5})
    for lengths in ((1, 1, 3), (3, 1, 1)):
        with pa.OSFile(str(path), "wb") as stream:
            with pa.ipc.new_file(stream, table.schema) as writer:
                offset = 0
                for length in lengths:
                    writer.write_table(table.slice(offset, length))
                    offset += length
        for actual, expected in zip(aggregate_edge_batches(path, np.array([1, 2]),
                ("body_pre", "body_post", "weight"), 3), grouped):
            np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize("column,value", [("body_pre", None), ("body_post", None), ("weight", -1)])
def test_invalid_excluded_upstream(tmp_path, column, value):
    files = a015.a014.synthetic_files(tmp_path, 1, 4)
    columns = {"body_pre": [999], "body_post": [999], "weight": [1]}
    columns[column] = [value]
    feather.write_feather(pa.table({k: pa.array(v, type=pa.int64()) for k, v in columns.items()}), files[2])
    with pytest.raises(ValueError):
        proposed(files, 1)


@pytest.mark.parametrize("rows", [100000, 1000000, 3000000])
def test_scale_exact(tmp_path, rows):
    files = a015.synthetic_files(tmp_path, rows)
    a015.assert_exact(proposed(files, 65536, experimental_load_batched_publication_numeric), proposed(files, 65536))


def test_production_dispatch_unchanged(tmp_path):
    files = a015.a014.synthetic_files(tmp_path, 1, 4)
    with patch("malecns_sim.data.integer_aggregation.aggregate_edge_batches", side_effect=AssertionError("opt-in only")):
        prepare_network(*files)


@pytest.mark.parametrize("size", [1, 2, 3])
def test_overflow_oracle_fallback(tmp_path, size):
    files = a015.a014.synthetic_files(tmp_path, 1, 4)
    limit = np.iinfo(np.int64).max
    feather.write_feather(pa.table({"body_pre": [1]*3, "body_post": [2]*3,
                                   "weight": [limit, limit, 3]}), files[2], chunksize=size)
    a015.assert_exact(proposed(files, size, experimental_load_batched_publication_numeric),
                     proposed(files, size))


def test_high_cardinality_exact(tmp_path):
    files = a015.a014.synthetic_files(tmp_path, 1, 2000)
    pair = np.arange(100000, dtype=np.int64)
    feather.write_feather(pa.table({"body_pre": pair // 2000 + 1,
        "body_post": pair % 2000 + 1, "weight": np.ones(pair.size, dtype=np.int64)}), files[2])
    a015.assert_exact(proposed(files, 65536, experimental_load_batched_publication_numeric),
                     proposed(files, 65536))
