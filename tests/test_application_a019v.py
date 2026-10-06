"""Contract checks for the frozen synthetic performance harness."""
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import benchmark_application_a019v as bench


def test_fixture_exact_counts_and_identity():
    a, b = bench.fixture(128, 1027), bench.fixture(128, 1027)
    assert a.fingerprint == b.fingerprint
    assert a.outgoing_indptr.shape == (129,)
    assert a.outgoing_indptr[-1] == a.outgoing_targets.size == 1027
    assert np.all((a.outgoing_targets >= 0) & (a.outgoing_targets < 128))
    assert a.outgoing_weights_mV.dtype == np.float64
    assert not a.outgoing_targets.flags.writeable
    assert a.target_positions is a.outgoing_targets
    assert np.max(np.diff(a.outgoing_indptr)) - np.min(np.diff(a.outgoing_indptr)) <= 1


def test_frozen_matrix_and_schedule():
    assert [(c[1], c[2]) for c in bench.CASES] == [(128, 1024), (4096, 32768),
        (32768, 262144), (127400, 14687178)]
    assert [c[3][0] for c in bench.CASES] == ['CPU', 'GPU', 'CPU', 'GPU']
    for large, count in ((False, 60), (True, 948)):
        full, windows, ids = bench.schedule(large)
        assert sum(len(s.spike_times_ms) for s in full.schedules) == count
        assert len(windows) == 12
        assert sum(len(steps) for w in windows for _, steps in w) == count
        assert all(0 <= step < 200 for w in windows for _, steps in w for step in steps)
        assert [bench.pack(w, ids).fingerprint for w in windows] == [
            bench.pack(w, ids).fingerprint for w in bench.schedule(large)[1]]


def test_statistics_keep_all_calls_and_population_std():
    values = np.arange(1, 21, dtype=float)
    record = bench.statistics(values)
    assert record['raw_seconds'] == values.tolist()
    assert record['p95'] == 19.05
    assert record['population_std'] == np.std(values, ddof=0)
    assert record['state_A_mean'] == 5.5
    assert record['state_B_mean'] == 15.5
    with pytest.raises(AssertionError):
        bench.statistics(values[:-1])


def test_eq_b_exact_and_frozen_float_policy():
    assert bench.compare_arrays(np.array([1]), np.array([2]))['discrete_mismatches'] == 1
    assert bench.compare_arrays(np.array([0.]), np.array([1e-13]))['pass_eq_b']
    assert not bench.compare_arrays(np.array([0.]), np.array([3e-13]))['pass_eq_b']
    assert not bench.compare_arrays(np.array([np.nan]), np.array([np.nan]))['pass_eq_b']
    with pytest.raises(AssertionError):
        bench.compare_arrays(np.array([1.]), np.array([1], dtype=np.int64))


def test_public_completion_source_contract():
    source = (bench.ROOT / 'src/malecns_sim/dynamics/cuda.py').read_text(encoding='utf-8')
    public = source.split('    def advance(self, state: GPUSimulationState', 1)[1].split(
        '    def _advance_device', 1)[0]
    assert public.index('backing.stream.synchronize()') < public.index('return result')


def test_result_snapshot_roundtrip_without_pickle(tmp_path):
    runtime = bench.PreparedRuntime(bench.fixture(128, 1024))
    state = runtime.initial_state()
    result = runtime.advance(state, duration_ms=0.1)
    snapshot = bench.capture(state, result)
    path = tmp_path / 'synthetic.npz'
    np.savez(path, **snapshot)
    with np.load(path, allow_pickle=False) as saved:
        assert all(bench.compare_arrays(saved[key], value)['pass_eq_b']
                   for key, value in snapshot.items())
