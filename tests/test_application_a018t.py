"""A018T synthetic scientific-oracle, ownership and lifetime regressions."""
import weakref
from functools import partial
from unittest.mock import patch
import numpy as np
import pytest
import test_application_a018 as baseline
import malecns_sim.data.blockwise_integer_merge as optimized
from malecns_sim.data.integer_aggregation import merge_integer_runs


@pytest.mark.parametrize('rows', baseline.RUN_CASES + [
    [[(i, i, 1) for i in range(10)]] * 40,
    [[(i, i, 1)] if i % 2 else [(0, 0, 1)] for i in range(31)],
])
def test_exact_oracle_ownership_release(rows):
    expected = merge_integer_runs([baseline.run(part) for part in rows])
    inputs = [baseline.run(part) for part in rows]
    refs = [weakref.ref(a) for part in inputs for a in part]
    metrics = {}
    actual = optimized.merge_staged_integer_runs(inputs, metrics)
    for a, b in zip(actual, expected):
        np.testing.assert_array_equal(a, b)
        assert a.flags.owndata and a.base is None and a.nbytes == a.size * 8
    assert not inputs
    if len(rows) > 1:
        assert all(ref() is None for ref in refs)
    assert metrics['max_resident_payload_bytes'] <= 3 * metrics['initial_partial_bytes']


@pytest.mark.parametrize('rows', baseline.FIXTURES)
@pytest.mark.parametrize('threshold', [0, 4, 5])
@pytest.mark.parametrize('block_size', [2, 7, 65536])
def test_prepared_scientific_oracle(tmp_path, rows, threshold, block_size):
    with patch.object(baseline, 'experimental_load_staged_publication_numeric',
                      partial(optimized.experimental_load_blockwise_publication_numeric,
                          merger=partial(optimized.merge_staged_integer_runs, block_size=block_size))):
        baseline.test_downstream_partition_exact(tmp_path, rows, threshold)


def test_compaction_releases_capacity():
    refs = []
    original = optimized.compact_output
    def observe(capacity, used):
        refs.extend(weakref.ref(a) for a in capacity)
        return original(capacity, used)
    with patch.object(optimized, 'compact_output', observe):
        result = optimized.merge_sorted_runs(baseline.run([(1, 1, 1)]), baseline.run([(1, 1, 2)]))
    assert all(ref() is None for ref in refs)
    assert all(a.flags.owndata and a.base is None and a.size == 1 for a in result)


def test_many_small_schedule_determinism():
    schedules = []
    for _ in range(2):
        inputs = [baseline.run([(i, i, 1)]) for i in range(2318)]
        metrics = {}
        output = optimized.merge_staged_integer_runs(inputs, metrics)
        np.testing.assert_array_equal(output[0], np.arange(2318))
        assert metrics['merge_stages'] == 12 and len(metrics['schedule']) == 2317
        schedules.append(metrics['schedule'])
    assert schedules[0] == schedules[1]


def test_partition_and_stage_release():
    with patch.object(baseline, 'merge_staged_integer_runs', optimized.merge_staged_integer_runs):
        baseline.test_schedule_partition_invariance()
        baseline.test_completed_stage_inputs_reclaimable()
        for fan_in in (2, 4, 8, 16):
            baseline.test_fan_in_composition_invariance(fan_in)


@pytest.mark.parametrize('size', [1, 2, 3])
def test_overflow_reference_fallback(tmp_path, size):
    with patch.object(baseline, 'experimental_load_staged_publication_numeric',
                      optimized.experimental_load_blockwise_publication_numeric):
        baseline.test_overflow_loader_fallback(tmp_path, size)
    with pytest.raises(OverflowError):
        optimized.merge_sorted_runs(baseline.run([(1, 2, baseline.LIMIT)]), baseline.run([(1, 2, 1)]))


def test_production_default(tmp_path):
    with patch.object(optimized, 'merge_sorted_runs', side_effect=AssertionError('experimental only')):
        baseline.test_production_default(tmp_path)

@pytest.mark.parametrize('block_size', [2, 3, 4, 7, 4096, 16384, 65536, 262144])
@pytest.mark.parametrize('shape', ['disjoint', 'overlap', 'alternating', 'same_pre', 'transition', 'uneven'])
def test_closed_boundaries(block_size, shape):
    keys = np.arange(91, dtype=np.int64)
    left_keys = keys if shape != 'alternating' else keys*2
    right_keys = keys if shape == 'overlap' else keys+45
    if shape == 'alternating':
        right_keys = keys*2+1
    if shape == 'uneven':
        right_keys = right_keys[:1]
    divisor = 1000 if shape == 'same_pre' else 7
    left = baseline.run(list(zip(left_keys//divisor, left_keys%divisor, np.ones(left_keys.size, dtype=np.int64))))
    right = baseline.run(list(zip(right_keys//divisor, right_keys%divisor, np.ones(right_keys.size, dtype=np.int64))))
    expected = merge_integer_runs([left, right])
    concatenate = np.concatenate
    def bounded(arrays, *args, **kwargs):
        assert sum(a.size for a in arrays) <= block_size
        assert all(a.dtype != object for a in arrays)
        return concatenate(arrays, *args, **kwargs)
    for _ in range(2):
        with patch('numpy.concatenate', bounded):
            actual = optimized.merge_sorted_runs(left, right, block_size=block_size)
        for a, b in zip(actual, expected):
            np.testing.assert_array_equal(a, b)
            assert a.flags.owndata and a.base is None
        assert not np.any((actual[0][1:] == actual[0][:-1]) & (actual[1][1:] == actual[1][:-1]))


def test_large_ids_and_invalid_block():
    left = baseline.run([(0, baseline.LIMIT, 1), (baseline.LIMIT, 0, baseline.LIMIT-1)])
    right = baseline.run([(baseline.LIMIT, 0, 1), (baseline.LIMIT, baseline.LIMIT, 0)])
    actual = optimized.merge_sorted_runs(left, right, block_size=2)
    expected = merge_integer_runs([left, right])
    for a, b in zip(actual, expected):
        np.testing.assert_array_equal(a, b)
    with pytest.raises(ValueError):
        optimized.merge_staged_integer_runs([], block_size=1)

@pytest.mark.parametrize('boundary', [0, 1, 2, 3, 4, 8])
def test_equal_key_on_either_slice_endpoint(boundary):
    left = baseline.run([(0, i, 1) for i in range(9)])
    right = baseline.run([(0, boundary, 2), (1, 0, 1)])
    expected = merge_integer_runs([left, right])
    for a, b in ((left, right), (right, left)):
        for size in (2, 4, 6, 8):
            actual = optimized.merge_sorted_runs(a, b, block_size=size)
            for column, wanted in zip(actual, expected):
                np.testing.assert_array_equal(column, wanted)


def test_seeded_partition_block_invariance():
    generator = np.random.default_rng(18018)
    columns = (generator.integers(0, 17, 2001, dtype=np.int64),
               generator.integers(0, 31, 2001, dtype=np.int64),
               generator.integers(0, 11, 2001, dtype=np.int64))
    expected = baseline.group_integer_pairs(*columns)
    for partition in (1, 13, 101, 2001):
        for block in (2, 7, 4096):
            inputs = [baseline.group_integer_pairs(*(c[i:i+partition] for c in columns))
                      for i in range(0, 2001, partition)]
            actual = optimized.merge_staged_integer_runs(inputs, block_size=block)
            for column, wanted in zip(actual, expected):
                np.testing.assert_array_equal(column, wanted)
