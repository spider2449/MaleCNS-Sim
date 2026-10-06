"""A019C certification uses generated Feather data and contained synthetic workers."""
import ast
import copy
import json
from pathlib import Path
import sys
from unittest.mock import patch

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import benchmark_application_a019 as h
from malecns_sim.analysis import task008
from malecns_sim.application.workbench import DatasetCatalog
from malecns_sim.data import male_cns_v1


@pytest.fixture
def fixture(tmp_path):
    source = h.make_synthetic_source(tmp_path)
    expected = json.loads(h.SYNTHETIC_IDENTITY_PATH.read_text())['expected']
    return source, expected


@pytest.fixture(autouse=True)
def firewall(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('A019C full-real catalog access forbidden')
    monkeypatch.setattr(DatasetCatalog, 'local', forbidden)
    original = h.ProductionEngine.prepare
    def guarded(self, files, *args, **kwargs):
        assert files.manifest_digest == files.mapping_fingerprint == 'a019c-synthetic'
        for path in (files.annotation, files.neurotransmitter, files.weights):
            assert not path.resolve().is_relative_to((h.ROOT / 'data').resolve())
        return original(self, files, *args, **kwargs)
    monkeypatch.setattr(h.ProductionEngine, 'prepare', guarded)


def test_full_structure_route_lifetime_replay_and_defaults(fixture):
    source, expected = fixture
    loader = task008.load_male_cns_v1_numeric
    original_runtime = h.PreparedRuntime
    calls = []
    def factory(*args, **kwargs):
        calls.append(1)
        return original_runtime(*args, **kwargs)
    with patch.object(h.historical, 'freeze_schedule', wraps=h.historical.freeze_schedule) as schedule, \
         patch.object(h.ProductionEngine, 'prepare', autospec=True, side_effect=h.ProductionEngine.prepare) as prepare:
        result = h.run_forward(source, expected, runtime_factory=factory)
        assert prepare.call_count == schedule.call_count == 1
    assert result['classification'] == 'A19C-A', result.get('stop_detail')
    assert calls == [1]
    assert task008.load_male_cns_v1_numeric is loader
    assert h.ProductionEngine().prepare(source.files, 'cpu_reference').fingerprint == expected['prepared_network_digest']
    assert result['preparation_route'] == 'A015/A016/A017/A018/A018T/A018U/A018UJ'
    assert result['bounded_route_enabled'] and result['fallback'] is None
    assert result['batch_rows'] == 65536 and result['merge_block_size'] == 16384
    metrics = result['route_metrics']
    assert metrics['block_operations'] > 0 and metrics['max_active_input_runs'] == 2
    assert metrics['block_workspace_bound_bytes'] == 128 * 16384
    assert all(result['gates'].values())
    assert result['preparations'] == result['prepared_network_count'] == result['prepared_runtime_count'] == 1
    assert result['simulation_state_count'] == 2
    assert result['state_a_released_before_b'] and not result['states_coexist']
    assert result['initial_state']['timestep'] == 0
    assert result['final_horizons_ms'] == [240, 240]
    assert result['max_consecutive_calls'] == 12
    assert result['advances_started'] == result['advances_completed'] == 24
    assert result['attempt_count'] == 0 and result['source_access_started']
    assert result['synthetic_source_accesses'] == 1
    assert result['cleanup'] == 'released' and result['replay'] == 'exact pass'
    assert result['final_states'][0] == result['final_states'][1] != result['initial_state']
    assert result['schedule']['event_count'] == 948
    assert result['schedule']['identity'] == h.load_contract()['schedule']['identity']
    assert result['schedule']['generation_count'] == 1
    a, b = result['steps'][:12], result['steps'][12:]
    assert any(row['queued_events'] > 0 for row in a)
    assert any(row['pending']['sum'] > 0 for row in a)
    for index, (left, right) in enumerate(zip(a, b)):
        assert left['sequence'] == 'A' and right['sequence'] == 'B'
        assert left['warmup'] == right['warmup'] == (index < 2)
        assert left['replay'] == right['replay']
        assert left['replay']['timestep'] == (index + 1) * 200 <= 2400
        assert left['replay']['input'] == result['schedule']['windows'][index]
    for sequence, rows in (('A', a), ('B', b)):
        assert result['distributions_seconds'][sequence]['advance']['mean'] == pytest.approx(
            np.mean([row['seconds']['advance'] for row in rows[2:]]))


@pytest.mark.parametrize('field,gate', [
    ('dataset_provenance_identity', 'G1'), ('preparation_config_identity', 'G2'),
    ('unsigned_graph_digest', 'G3'), ('effective_projection_fingerprint', 'G4'),
    ('prepared_network_digest', 'G5'), ('neurons', 'G6'), ('edges', 'G6')])
def test_each_gate_stops_before_runtime_one_preparation(fixture, field, gate):
    source, expected = fixture
    expected = copy.deepcopy(expected)
    expected[field] = -1 if field in ('neurons', 'edges') else 'wrong'
    with patch.object(h, 'PreparedRuntime', side_effect=AssertionError('runtime forbidden')):
        result = h.run_forward(source, expected, runtime_factory=h.PreparedRuntime)
    assert result['classification'] == 'IDENTITY_MISMATCH'
    assert not result['gates'][gate]
    assert result['preparations'] == 1 and result['prepared_runtime_count'] == 0
    assert result['cleanup'] == 'released'


@pytest.mark.parametrize('field,other', [('effective_projection_fingerprint', 'prepared_network_digest'),
                                       ('prepared_network_digest', 'effective_projection_fingerprint')])
def test_cross_layer_rejected(fixture, field, other):
    source, expected = fixture
    wrong = dict(expected, **{field: expected[other]})
    with pytest.raises(ValueError, match='effective fingerprint'):
        h.compare_identity(wrong, expected)
    result = h.run_forward(source, wrong)
    assert result['classification'] != 'A19C-A' and result['prepared_runtime_count'] == 0


@pytest.mark.parametrize('mode', ['negative', 'overflow'])
def test_fallback_hard_stop(fixture, mode):
    source, expected = fixture
    ids = h.load_contract()['schedule']['member_ids']
    values = ([-1], [ids[0]], [1]) if mode == 'negative' else ([ids[0]] * 2, [ids[1]] * 2, [2**63-1, 1])
    feather.write_feather(pa.table(dict(zip(('body_pre', 'body_post', 'weight'), values))), source.files.weights)
    result = h.run_forward(source, expected)
    assert result['classification'] == 'PREPARATION_FALLBACK'
    assert result['fallback'] and result['prepared_runtime_count'] == 0
    assert result['preparations'] == 1 and result['advances_started'] == 0


@pytest.mark.parametrize('failure', ['prepare', 'runtime', 'advance', 'memory', 'instrumentation', 'replay'])
def test_induced_failure_no_retry(fixture, failure):
    source, expected = fixture
    original = h.ProductionEngine.prepare
    count = []
    def prepare(self, *args, **kwargs):
        count.append(1)
        if failure == 'prepare':
            raise RuntimeError('forced preparation failure')
        return original(self, *args, **kwargs)
    def runtime_factory(*args, **kwargs):
        if failure == 'runtime':
            raise RuntimeError('forced runtime failure')
        return h.PreparedRuntime(*args, **kwargs)
    def memory():
        if failure == 'instrumentation':
            raise OSError('forced instrumentation failure')
        return dict(private_bytes=2 if failure == 'memory' else 0, working_set=0)
    with patch.object(h.ProductionEngine, 'prepare', prepare), \
         patch.object(h.PreparedRuntime, 'advance', side_effect=RuntimeError('forced advance')) if failure == 'advance' else patch.object(h, 'digest', wraps=h.digest), \
         patch.object(h.historical, 'compare', side_effect=h.Stop('REPLAY_MISMATCH', 'forced mismatch')) if failure == 'replay' else patch.object(h, 'load_contract', wraps=h.load_contract):
        result = h.run_forward(source, expected, runtime_factory=runtime_factory, memory=memory,
                               limits=h.Limits(private_bytes=1) if failure == 'memory' else h.Limits())
    assert result['classification'] != 'A19C-A'
    assert len(count) == result['preparations'] == (0 if failure in ('memory', 'instrumentation') else 1)
    assert not result['automatic_retry'] and result['cleanup'] == 'released'


@pytest.mark.parametrize('phase,elapsed,total,memory,classification', [
    ('prepare', 601, 601, (0, 0), 'PREPARATION_TIMEOUT'),
    ('advance', 31, 31, (0, 0), 'ADVANCE_TIMEOUT'),
    ('identity', 1, 1501, (0, 0), 'WORKER_TIMEOUT'),
    ('prepare', 0, 0, (8589934593, 0), 'MEMORY_LIMIT'),
    ('advance', 0, 0, (0, 8589934593), 'MEMORY_LIMIT')])
def test_exact_resource_limits(phase, elapsed, total, memory, classification):
    with pytest.raises(h.Stop) as error:
        h.Limits().check(dict(private_bytes=memory[0], working_set=memory[1]), phase, elapsed, total)
    assert error.value.classification == classification
    c = h.load_contract()
    assert vars(h.Limits()) == dict(preparation_s=c['preparation_timeout_s'], advance_s=c['advance_timeout_s'],
        worker_s=c['total_worker_timeout_s'], private_bytes=c['memory_cap_bytes'], working_set=c['memory_cap_bytes'])


@pytest.mark.parametrize('phase', ['prepare', 'advance', 'startup', 'memory'])
def test_contained_tree_forced_stops_no_orphan(tmp_path, phase):
    code = f'''import json,os,subprocess,sys,time
p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(15)'])
print(json.dumps(dict(phase={phase!r},pid=os.getpid(),at=time.perf_counter())),flush=True)
time.sleep(15)
'''
    limits = {'prepare': h.Limits(preparation_s=.15), 'advance': h.Limits(advance_s=.15),
              'startup': h.Limits(worker_s=.3), 'memory': h.Limits(private_bytes=1)}[phase]
    result = h.supervise([sys.executable, '-c', code], tmp_path / 'result.json', limits)
    assert result['classification'] == {'prepare': 'PREPARATION_TIMEOUT', 'advance': 'ADVANCE_TIMEOUT',
                                       'startup': 'WORKER_TIMEOUT', 'memory': 'MEMORY_LIMIT'}[phase]
    assert result['watchdog']['orphans'] == [] and result['watchdog']['launches'] == 1
    with pytest.raises(h.Stop, match='retry'):
        h.supervise([sys.executable, '-c', code], tmp_path / 'result.json', limits)


def test_synthetic_cli_contained_success(tmp_path):
    result = h.supervise([sys.executable, str(Path(h.__file__)), '--synthetic', '--worker',
                          '--output', str(tmp_path / 'result.json')], tmp_path / 'result.json')
    assert result['classification'] == 'A19C-A', result
    assert result['watchdog']['orphans'] == []
    assert result['watchdog']['samples'] > 0 and result['attempt_count'] == 0


def test_synthetic_source_guard_before_access(fixture):
    source, expected = fixture
    real = h.DatasetFiles(h.ROOT / 'data/raw/annotation.feather', source.files.neurotransmitter,
                          source.files.weights, 'a019c-synthetic', 'a019c-synthetic')
    with patch.object(h.ProductionEngine, 'prepare', side_effect=AssertionError('source access forbidden')):
        result = h.run_forward(h.Source(real, source.synthetic_root), expected)
    assert result['classification'] == 'A019C-REAL-DATA-FIREWALL-VIOLATION'
    assert result['preparations'] == 0 and not result['source_access_started']
    result = h.run_forward(h.Source(real, None), expected)
    assert result['classification'] == 'REAL_EXECUTION_NOT_AUTHORIZED'
    assert result['attempt_count'] == 0


def test_timing_structure_and_historical_default():
    import inspect
    sequence = inspect.getsource(h.historical.run_sequences)
    assert sequence.index('for index, window') < sequence.index('t0 =') < sequence.index('stimulus = pack')
    assert sequence.index('t1 =') < sequence.index('runtime.advance') < sequence.index('t2 =')
    assert sequence.index('counts = tuple') < sequence.index('t3 =') < sequence.index('t5 =')
    assert sequence.index('t5 =') < sequence.index('replay = {**state_evidence(state)')
    assert 'del result' in sequence and 'del state' in sequence
    prepare = inspect.getsource(h.historical.prepare_once)
    assert "engine.prepare(files, 'cpu_reference')" in prepare and 'bounded_route' not in prepare
    tree = ast.parse(Path(h.__file__).read_text())
    calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert not calls & {'reset', 'download', 'simulate_cuda', 'simulate_lif'}

def test_completed_preparation_deadline_before_runtime(fixture):
    source, expected = fixture
    result = h.run_forward(source, expected, limits=h.Limits(preparation_s=0))
    assert result['classification'] == 'PREPARATION_TIMEOUT'
    assert result['prepared_runtime_count'] == 0 and result['preparations'] <= 1


def test_completed_call_deadline_no_retry(fixture):
    source, expected = fixture
    result = h.run_forward(source, expected, limits=h.Limits(advance_s=0))
    assert result['classification'] == 'ADVANCE_TIMEOUT'
    assert result['advances_started'] == 1 and result['advances_completed'] == 0
    assert result['prepared_runtime_count'] == result['simulation_state_count'] == 1


def test_watchdog_instrumentation_failure_terminates_tree(tmp_path, monkeypatch):
    def broken(self):
        raise OSError('forced accounting failure')
    monkeypatch.setattr(h.ProcessJob, 'snapshot', broken)
    result = h.supervise([sys.executable, '-c', 'import time; time.sleep(15)'], tmp_path / 'result.json')
    assert result['classification'] == 'WATCHDOG_FAILURE'
    assert result['watchdog']['orphans'] == []


def test_contract_schema_matches_success_evidence(fixture):
    source, expected = fixture
    schema = json.loads((h.ROOT / 'docs/plans/2026-10-05-application-a019c-harness-contract.json').read_text())
    result = h.run_forward(source, expected)
    assert result['classification'] == 'A19C-A'
    assert set(schema['required']) <= set(result)
    assert schema['properties']['schema']['const'] == result['schema']
    assert result['firewall'] == dict(full_real_source_accesses=0, full_real_preparations=0,
        real_advances=0, gpu=0, real_arena_runs=0, real_experiments=0, raw_downloads=0, archive_writes=0)


def test_watchdog_child_memory_stop_aggregate_and_cleanup(tmp_path):
    code = "import subprocess,sys; p=subprocess.Popen([sys.executable,'-c','import time; x=bytearray(160*1024**2); time.sleep(15)']); p.wait()"
    result = h.supervise([sys.executable, '-c', code], tmp_path / 'result.json',
                         h.Limits(private_bytes=128*1024**2, working_set=128*1024**2))
    assert result['classification'] == 'MEMORY_LIMIT'
    assert max(result['watchdog']['peaks'].values()) > 128*1024**2
    assert result['watchdog']['orphans'] == [] and result['watchdog']['launches'] == 1
