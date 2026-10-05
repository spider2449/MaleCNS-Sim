"""Synthetic exactness and resident ownership certification for A018."""
import weakref
from functools import partial
from unittest.mock import patch

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import pytest

from test_application_a017 import FIXTURES, proposed, a015
from malecns_sim.data.integer_aggregation import group_integer_pairs, merge_integer_runs
from malecns_sim.data.staged_integer_merge import (
    merge_sorted_runs, merge_staged_integer_runs, experimental_load_staged_publication_numeric,
)
from malecns_sim.dynamics.lif import PreparedRuntime

LIMIT = int(np.iinfo(np.int64).max)
RUN_CASES = [
    [[(1, 2, 1)]],
    [[(1, 2, 1)], [(3, 4, 2)]],
    [[(1, 2, 1)], [(1, 2, 2)]],
    [[(1, 2, 1)]] * 33,
    [[(i, i+1, 1)] for i in range(33)],
    [[(i, 2, 1) for i in range(start, 30, 3)] for start in range(3)],
    [[(1, 1, 1), (9, 9, 2)]] * 9,
    [[], [(1, 2, 1)], [], [(2, 3, 2)], []],
    [[], [], []],
    [[(i, i, 1) for i in range(100)]] + [[(1, 1, 1)]] * 17,
    [[(1, 2, 1)]] * 5,
    [[(1, 2, 1)]] * 4,
    [[(1, 1, 1)]] * 7,
    [[(1, 2, LIMIT-1)], [(1, 2, 1)]],
    [[(i, j, 1) for i in range(4) for j in range(4)]] * 11,
    [[(i, 1, 1)] for i in range(17, -1, -1)],
    [],
    [[(1, 2, 0)], [(1, 2, 0)]],
    [[(LIMIT, LIMIT, 1)], [(0, LIMIT, 2)]],
    [[(i, i+1, 1) for i in range(1000)]] + [[(2000+i, 1, 1)] for i in range(31)],
]


def run(rows):
    values = np.array(rows, dtype=np.int64).reshape(-1, 3)
    return group_integer_pairs(*values.T)


@pytest.mark.parametrize("rows", RUN_CASES)
def test_runs_exact_deterministic_and_lifetime(rows):
    expected = merge_integer_runs([run(part) for part in rows])
    schedules = []
    for _ in range(2):
        inputs = [run(part) for part in rows]
        references = [[weakref.ref(a) for a in part] for part in inputs]
        metrics = {}
        def observe(current, following):
            for index, item in enumerate(current):
                if item is None and len(current) == len(references):
                    assert all(ref() is None for ref in references[index])
        with patch("numpy.concatenate", side_effect=AssertionError("global concatenation")):
            actual = merge_staged_integer_runs(inputs, metrics, observe)
        assert inputs == []
        for a, b in zip(actual, expected):
            np.testing.assert_array_equal(a, b)
            assert a.dtype == np.int64 and a.flags.owndata
        assert metrics["max_active_input_runs"] <= 2
        assert metrics["max_resident_payload_bytes"] <= 2 * metrics["initial_partial_bytes"]
        schedules.append(metrics["schedule"])
    assert schedules[0] == schedules[1]


@pytest.mark.parametrize("rows", FIXTURES)
@pytest.mark.parametrize("threshold", [0, 4, 5])
def test_downstream_partition_exact(tmp_path, rows, threshold):
    files = a015.a014.synthetic_files(tmp_path, 1, 4)
    first = None
    for size in (1, 2, 3, 7, 65536):
        feather.write_feather(pa.table({name: pa.array([row[i] for row in rows], type=pa.int64())
            for i, name in enumerate(("body_pre", "body_post", "weight"))}), files[2], chunksize=size)
        expected = proposed(files, size, min_synapses=threshold)
        actual = proposed(files, size, experimental_load_staged_publication_numeric, min_synapses=threshold)
        a015.assert_exact(expected, actual)
        if first is not None:
            a015.assert_exact(first, actual)
        first = actual
        left, right = PreparedRuntime(expected.projection), PreparedRuntime(actual.projection)
        assert left.identity == right.identity
        assert left.parameters.grid_steps(left.dt_ms) == right.parameters.grid_steps(right.dt_ms)


def test_overflow_rejection():
    with pytest.raises(OverflowError):
        merge_sorted_runs(run([(1, 2, LIMIT)]), run([(1, 2, 1)]))


def test_completed_stage_inputs_reclaimable():
    inputs = [run([(i, i+1, 1)]) for i in range(64)]
    stages = {id(inputs): {i: [weakref.ref(a) for a in item]
                           for i, item in enumerate(inputs)}}
    boundaries = []
    def observe(current, following):
        for index, references in stages[id(current)].items():
            if current[index] is None:
                assert all(reference() is None for reference in references)
        stages[id(following)] = {i: [weakref.ref(a) for a in item]
                                for i, item in enumerate(following)}
        boundaries.append(len(following))
    result = merge_staged_integer_runs(inputs, observer=observe)
    assert len(boundaries) == 63
    assert result[0].size == 64


@pytest.mark.parametrize("size", [1, 2, 3])
def test_overflow_loader_fallback(tmp_path, size):
    files = a015.a014.synthetic_files(tmp_path, 1, 4)
    feather.write_feather(pa.table({"body_pre": [1]*3, "body_post": [2]*3,
                                   "weight": [LIMIT, LIMIT, 3]}), files[2], chunksize=size)
    a015.assert_exact(proposed(files, size), proposed(files, size, experimental_load_staged_publication_numeric))


def test_schedule_partition_invariance():
    rows = [(i % 13, i % 7, 1) for i in range(1001)]
    expected = run(rows)
    for size in (1, 2, 4, 8, 16, 127, 1001):
        actual = merge_staged_integer_runs([run(rows[i:i+size]) for i in range(0, len(rows), size)])
        for a, b in zip(actual, expected):
            np.testing.assert_array_equal(a, b)


@pytest.mark.parametrize("fan_in", [2, 4, 8, 16])
def test_fan_in_composition_invariance(fan_in):
    # Alternative group boundaries compose the same certified binary primitive;
    # production still exposes only the selected binary-tree architecture.
    rows = [(i % 31, i % 19, i % 5) for i in range(1001)]
    expected = run(rows)
    current = [run(rows[i:i+7]) for i in range(0, len(rows), 7)]
    while len(current) > 1:
        current = [merge_staged_integer_runs(current[i:i+fan_in])
                   for i in range(0, len(current), fan_in)]
    for a, b in zip(current[0], expected):
        np.testing.assert_array_equal(a, b)


def test_production_default(tmp_path):
    from malecns_sim.analysis.task008 import prepare_network
    files = a015.a014.synthetic_files(tmp_path, 1, 4)
    with patch("malecns_sim.data.staged_integer_merge.merge_sorted_runs", side_effect=AssertionError("opt-in only")):
        prepare_network(*files)
