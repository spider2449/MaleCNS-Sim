"""Synthetic A013 certification; never load the real dataset or launch a worker."""
import ast
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from malecns_sim.dynamics.lif import PreparedRuntime
from test_task005 import _projection

PATH = Path(__file__).resolve().parents[1] / 'scripts/benchmark_application_a013.py'
spec = importlib.util.spec_from_file_location('a013', PATH)
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


def test_limits_and_cpu_only():
    assert (bench.MAX_PREPARATIONS, bench.MAX_ADVANCES, bench.SEQUENCES, bench.STEPS, bench.WARMUPS) == (1,24,2,12,2)
    assert (bench.INTERVAL_MS, bench.DT_MS) == (20,0.1)
    assert (bench.MEMORY_CAP, bench.PREPARATION_CAP, bench.ADVANCE_CAP, bench.TOTAL_CAP) == (8*1024**3,600,30,1500)
    assert bench.AVAILABLE_MIN == 12*1024**3
    source = PATH.read_text()
    assert "choices=['cpu_reference']" in source
    assert "required=True" in source and '--confirm-real-data-benchmark' in source


def test_one_preparation():
    calls = []
    engine = SimpleNamespace(prepare=lambda files, backend: calls.append((files,backend)))
    evidence = {'preparations': 0}
    bench.prepare_once(engine, 'local', evidence)
    with pytest.raises(bench.Stop, match='preparation budget'):
        bench.prepare_once(engine, 'local', evidence)
    assert calls == [('local','cpu_reference')]


@pytest.mark.parametrize('memory,phase,elapsed,total,classification', [
    ({'working_set':8*1024**3+1,'private_bytes':0},'advance',0,0,'A013-MEMORY-LIMIT'),
    ({'working_set':0,'private_bytes':8*1024**3+1},'prepare',0,0,'A013-MEMORY-LIMIT'),
    ({'working_set':0,'private_bytes':0},'prepare',601,601,'A013-PREPARATION-LIMIT'),
    ({'working_set':0,'private_bytes':0},'advance',31,31,'A013-ADVANCE-LIMIT'),
    ({'working_set':0,'private_bytes':0},'verification',0,1501,'A013-TOTAL-LIMIT')])
def test_watchdog_stops(memory,phase,elapsed,total,classification):
    with pytest.raises(bench.Stop) as caught:
        bench.guard(memory,phase,elapsed,total)
    assert caught.value.classification == classification
    assert caught.value.classification != 'A13-BENCHMARK-COMPLETE'


def test_percentiles_and_warmup_exclusion():
    assert bench.statistics([1,2,3,4]) == {'min':1,'p50':2.5,'p95':3.8499999999999996,'max':4,'mean':2.5}
    rows = [{'sequence':seq,'warmup':i<2,'seconds':{stage:10000 if i<2 else i for stage in bench.STAGES}}
            for seq in ('A','B') for i in range(12)]
    result = bench.distributions(rows)['pooled']['advance']
    assert result['max'] == 11 and result['mean'] == 6.5 and result['p50'] == 6.5
    assert result['p95'] == 11


def test_schedule_is_complete_grid_slices_and_reused():
    schedule, windows = bench.freeze_schedule((1,2))
    assert len(windows) == 12
    rebuilt = {item.neuron_id: [] for item in schedule.schedules}
    for k, window in enumerate(windows):
        for neuron, steps in window:
            assert all(0 <= step < 200 for step in steps)
            rebuilt[neuron].extend(step + k*200 for step in steps)
    assert rebuilt == {item.neuron_id:[round(t/0.1) for t in item.spike_times_ms] for item in schedule.schedules}
    assert schedule.weight_mV == 68.75
    assert bench.freeze_schedule((1,2))[1] == windows


def synthetic_run(corrupt=False):
    runtime = PreparedRuntime(_projection())
    states, calls = [], []
    class Recorder:
        projection = runtime.projection
        def initial_state(self):
            state = runtime.initial_state()
            if states:
                assert all(not np.shares_memory(getattr(state,name),getattr(states[-1],name)) for name in bench.FIELDS)
            states.append(state)
            return state
        def advance(self,state,**kwargs):
            calls.append((kwargs['duration_ms'],kwargs['stimulus'].fingerprint))
            result = runtime.advance(state,**kwargs)
            if corrupt and len(calls) == 13:
                state.g_mV[0] += 1
            return result
    evidence = {'steps': [], 'advances_started':0,'advances_completed':0}
    _, windows = bench.freeze_schedule((1,))
    bench.run_sequences(Recorder(),windows,(1,),evidence,lambda:None,lambda *a,**k:None,lambda:{},readout_ids=(2,3))
    return evidence, calls, states


def test_two_fresh_states_exact_twenty_four_advances_and_replay():
    evidence,calls,states = synthetic_run()
    assert len(calls) == evidence['advances_completed'] == 24
    assert all(duration==20 for duration,_ in calls)
    assert calls[:12] == calls[12:]
    assert len(states) == 2 and all(state.timestep==2400 for state in states)
    assert sum(row['warmup'] for row in evidence['steps']) == 4
    assert sum(not row['warmup'] for row in evidence['steps']) == 20
    assert evidence['replay'] == 'exact pass'
    assert 'biological_verdict' not in evidence


def test_mismatch_fails_at_first_component():
    with pytest.raises(bench.Stop) as caught:
        synthetic_run(corrupt=True)
    assert caught.value.classification == 'A013-DETERMINISM-FAIL'
    assert 'interval 1: arrays.g_mV' in str(caught.value)


def test_canonical_digest_exact_and_endian_stable():
    a = np.array([1.0,2.0],dtype='<f8')
    assert bench.array_digest(a) == bench.array_digest(a.astype('>f8'))
    b = a.copy()
    b[0] = np.nextafter(b[0],2)
    assert bench.array_digest(a) != bench.array_digest(b)


def test_pending_guard():
    state = PreparedRuntime(_projection()).initial_state()
    state.pending_event_counts[0,0] = -1
    with pytest.raises(bench.Stop) as caught:
        bench.pending_evidence(state,[],3)
    assert caught.value.classification == 'A013-PENDING-STATE-DIVERGENCE'


def test_no_download_arena_gpu_or_import_execution():
    tree = ast.parse(PATH.read_text())
    imports = [node.module or '' for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)]
    imports += [alias.name for node in ast.walk(tree) if isinstance(node,ast.Import) for alias in node.names]
    assert not any(any(token in name for token in ('arena','cuda','cupy','requests','urllib','http')) for name in imports)
    assert not any(isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) for node in tree.body)
    assert 'biological_verdict' not in PATH.read_text()


def test_refuse_existing_output(tmp_path):
    output = tmp_path / 'result.json'
    output.write_text('{}')
    with pytest.raises(bench.Stop,match='refusing'):
        bench.supervise(output)


def test_watchdog_binds_worker_not_launcher():
    closed = []
    launcher = SimpleNamespace(pid=100,close=lambda:closed.append(100))
    worker = SimpleNamespace(pid=200,close=lambda:closed.append(200))
    assert bench.bind_worker_monitor({'pid':200},launcher,lambda pid:worker) is worker
    assert closed == [100]
    assert bench.bind_worker_monitor({'pid':200},worker,lambda pid:pytest.fail('should reuse')) is worker


@pytest.mark.skipif(sys.platform != 'win32',reason='Windows native worker PID and termination test')
def test_native_watchdog_can_terminate_actual_redirected_python():
    # Preserve unbuffered IO without an interpreter option in the guarded payload.
    environment = dict(os.environ, PYTHONUNBUFFERED='1')
    code = '''import os,time
if os.environ.get('MALECNS_A019C_R2_FIREWALL') == '1':
    import validation_firewall as guard
    assert guard.ACTIVE
    guard.record('a013_workload_start', executable=__import__('sys').executable,
                 unbuffered=os.environ.get('PYTHONUNBUFFERED'))
print(os.getpid(),flush=True)
time.sleep(10)
'''
    process = subprocess.Popen([sys.executable,'-c',code],
                               stdout=subprocess.PIPE,text=True,env=environment)
    monitor = None
    try:
        actual_pid = int(process.stdout.readline())
        monitor = bench.WindowsMemory(actual_pid)
        assert monitor.pid == actual_pid
        assert actual_pid != os.getpid()
        assert actual_pid != process.pid, 'control must exercise the redirected worker'
        import ctypes
        from ctypes import wintypes
        image = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(len(image))
        query = monitor.kernel.QueryFullProcessImageNameW
        query.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                          ctypes.POINTER(wintypes.DWORD))
        assert query(monitor.handle, 0, image, ctypes.byref(size))
        assert Path(image.value).resolve() == Path(sys._base_executable).resolve()
        assert monitor.snapshot()['working_set'] > 0
        active = os.environ.get('MALECNS_A019C_R2_FIREWALL') == '1'
        if active:
            import validation_firewall as guard
            guard.record('a013_watchdog_armed', launcher_pid=process.pid,
                         actual_pid=actual_pid, actual_image=image.value)
        monitor.terminate()
        assert process.wait(timeout=5) == 1
        exit_code = wintypes.DWORD()
        get_exit = monitor.kernel.GetExitCodeProcess
        get_exit.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        assert get_exit(monitor.handle, ctypes.byref(exit_code))
        assert exit_code.value == 1, 'actual worker must have terminated'
        if active:
            guard.record('a013_watchdog_terminated', launcher_pid=process.pid,
                         actual_pid=actual_pid, launcher_exit=process.returncode,
                         worker_exit=exit_code.value, attempts=1, retry=False)
    finally:
        if monitor is not None:
            monitor.close()
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        process.stdout.close()
