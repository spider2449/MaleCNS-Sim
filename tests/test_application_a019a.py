"""A019A forward-contract checks using tracked metadata and tiny synthetic data only."""
import json
import weakref
from pathlib import Path

import numpy as np

from malecns_sim.dynamics.lif import PreparedRuntime
from test_application_a013 import bench
from test_task005 import _projection

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'docs/plans/2026-10-05-application-a019a-benchmark-contract.json'


def test_frozen_two_state_contract():
    c = json.loads(CONTRACT.read_text(encoding='utf-8'))
    assert c['schema'] == 'application-stateful-benchmark-v1'
    assert c['classification'] == 'A19A-A' and c['trajectory_classification'] == 'C1'
    assert (c['preparation_count'], c['prepared_network_count'], c['prepared_runtime_count'], c['state_sequence_count']) == (1, 1, 1, 2)
    assert c['prepared_graph_reused'] and c['state_a_released_before_b']
    assert not c['states_coexist'] and not c['continuous_480_ms']
    assert c['total_advances'] == bench.MAX_ADVANCES == 24
    assert c['maximum_consecutive_advances_per_state'] == bench.STEPS == 12
    assert [s['name'] for s in c['sequences']] == ['A', 'B']
    for s in c['sequences']:
        assert s['fresh_state'] and s['initial_timestep'] == 0
        assert (s['warmup_advances'], s['measured_advances'], s['total_advances']) == (2, 10, 12)
        assert s['advance_duration_ms'] == bench.INTERVAL_MS == 20
        assert s['final_horizon_ms'] == 240
        assert s['schedule_identity'] == bench.SCHEDULE_ID
    assert (c['memory_cap_bytes'], c['preparation_timeout_s'], c['advance_timeout_s'], c['total_worker_timeout_s']) == (bench.MEMORY_CAP, bench.PREPARATION_CAP, bench.ADVANCE_CAP, bench.TOTAL_CAP)
    assert c['available_physical_min_bytes'] == bench.AVAILABLE_MIN
    assert c['preparation_identity_schema'] == 'preparation-identity-v1'
    assert c['preparation_identity_gates'] == ['G1', 'G2', 'G3', 'G4', 'G5', 'G6']
    identity = json.loads((ROOT / c['preparation_identity_record']).read_text())
    assert identity['schema'] == c['preparation_identity_schema']
    assert not c['execution_authorized'] and c['retry_count'] == c['arena_runs'] == 0
    assert c['backend'] == 'cpu_reference'


def test_historical_schedule_from_tracked_metadata_only():
    c = json.loads(CONTRACT.read_text())['schedule']
    fixture = json.loads((ROOT / 'tests/fixtures/application-a003r-reference-spec.json').read_text())
    assert c['member_ids'] == fixture['stimulus']['member_ids']
    assert (c['side'], c['population'], c['left_neuron_count'], c['right_neuron_count']) == ('LEFT', 'sugar', 42, 0)
    assert (c['left_rate_hz'], c['right_rate_hz'], c['seed'], c['impulse_mV'], c['duration_ms']) == (100, 0, 1555062870, 68.75, 240)
    schedule, windows = bench.freeze_schedule(c['member_ids'])
    assert schedule.fingerprint == c['identity'] == bench.SCHEDULE_ID
    assert sum(len(s.spike_times_ms) for s in schedule.schedules) == c['event_count'] == 948
    assert len(windows) == c['window_count'] == 12
    assert c['generation_count'] == 1 and c['identical_frozen_windows'] and c['repack_each_call']


def test_b_starts_fresh_after_a_released_using_same_runtime_and_graph():
    projection = _projection()
    runtime = PreparedRuntime(projection, dt_ms=0.1)
    initial_digests, terminal_times, array_refs, inputs = [], [], [], []

    class Recorder:
        projection = runtime.projection

        def initial_state(self):
            if array_refs:
                assert terminal_times == [2400]
                assert all(ref() is None for ref in array_refs)
            state = runtime.initial_state()
            assert state.timestep == 0
            assert np.all(state.v_mV == runtime.parameters.v_rest_mV)
            assert np.all(state.g_mV == 0) and np.all(state.refractory_until == -1)
            assert np.all(state.pending == 0) and np.all(state.pending_event_counts == 0)
            initial_digests.append(bench.state_evidence(state))
            array_refs[:] = [weakref.ref(getattr(state, name)) for name in bench.FIELDS]
            return state

        def advance(self, state, **kwargs):
            assert runtime.projection is projection
            inputs.append(kwargs['stimulus'].fingerprint)
            result = runtime.advance(state, **kwargs)
            if state.timestep == 2400:
                terminal_times.append(state.timestep)
            return result

    _, windows = bench.freeze_schedule((1,))
    evidence = dict(steps=[], advances_started=0, advances_completed=0)
    bench.run_sequences(Recorder(), windows, (1,), evidence, lambda: None,
                        lambda *a, **k: None, lambda: {}, readout_ids=(2, 3))
    assert initial_digests[0] == initial_digests[1]
    assert terminal_times == [2400, 2400]
    assert inputs[:12] == inputs[12:]
    assert evidence['replay'] == 'exact pass'
    assert all(ref() is None for ref in array_refs)


def test_a019a_checks_have_no_real_execution_and_preserve_defaults(monkeypatch):
    from malecns_sim.application.service import ProductionEngine
    from malecns_sim.application.workbench import DatasetCatalog
    from malecns_sim.application.preparation import REFERENCE_CONFIG

    def forbidden(*args, **kwargs):
        raise AssertionError('real preparation or catalog access forbidden in A019A')

    original_prepare = ProductionEngine.prepare
    config_digest = REFERENCE_CONFIG.digest
    with monkeypatch.context() as scoped:
        scoped.setattr(ProductionEngine, 'prepare', forbidden)
        scoped.setattr(DatasetCatalog, 'local', forbidden)
        test_frozen_two_state_contract()
        test_historical_schedule_from_tracked_metadata_only()
        test_b_starts_fresh_after_a_released_using_same_runtime_and_graph()
    assert ProductionEngine.prepare is original_prepare
    assert REFERENCE_CONFIG.digest == config_digest == 'a14d75e682b5201c022043725cdac945847962ebff64888008673cca7ded6bf9'
