"""A018S synthetic scientific-oracle, ownership and lifetime regressions."""
import weakref
from unittest.mock import patch
import numpy as np
import pytest
import test_application_a018 as baseline
import malecns_sim.data.single_pass_integer_merge as optimized
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
    with patch('numpy.concatenate', side_effect=AssertionError('unbounded concatenate')):
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
def test_prepared_scientific_oracle(tmp_path, rows, threshold):
    with patch.object(baseline, 'experimental_load_staged_publication_numeric',
                      optimized.experimental_load_single_pass_publication_numeric):
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
                      optimized.experimental_load_single_pass_publication_numeric):
        baseline.test_overflow_loader_fallback(tmp_path, size)
    with pytest.raises(OverflowError):
        optimized.merge_sorted_runs(baseline.run([(1, 2, baseline.LIMIT)]), baseline.run([(1, 2, 1)]))


def test_production_default(tmp_path):
    with patch.object(optimized, 'merge_sorted_runs', side_effect=AssertionError('experimental only')):
        baseline.test_production_default(tmp_path)
