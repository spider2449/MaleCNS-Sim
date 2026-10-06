"""Bounded synthetic certification; no real source paths or runtime advances."""
import importlib.util
import os
from pathlib import Path
import sys

import numpy as np
import pytest

PATH = Path(__file__).resolve().parents[1] / 'scripts/investigate_application_a014.py'
spec = importlib.util.spec_from_file_location('a014', PATH)
investigation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(investigation)
pytestmark = pytest.mark.skipif(sys.platform != 'win32', reason='Windows process accounting')


@pytest.mark.parametrize('mode', ['direct', 'launcher', 'child', 'replacement'])
@pytest.mark.parametrize('repeat', range(2))
def test_tree_memory_enforcement(mode, repeat, monkeypatch, tmp_path):
    allocate = 'import os,time; x=bytearray(160*1024**2); print(os.getpid(),flush=True); time.sleep(8)'
    executable = sys._base_executable if mode == 'direct' else sys.executable
    if mode in ('child', 'replacement'):
        code = f'import subprocess,sys,time; p=subprocess.Popen([sys.executable,"-c",{allocate!r}]); ' + ('sys.exit(0)' if mode == 'replacement' else 'p.wait()')
    else:
        code = allocate
    command = [executable, '-c', code]
    if mode == 'replacement' and os.environ.get('MALECNS_A019C_R2_FIREWALL') == '1':
        import validation_firewall as guard
        import json
        handshake = tmp_path / 'replacement-control'
        workload = '''import os,time,subprocess,sys
from pathlib import Path
import validation_firewall as guard
assert guard.ACTIVE
try:
    open(guard.ROOT / 'data' / 'a019c-r13-replacement-probe.feather', 'rb')
except guard.SourceAccessDenied:
    pass
else:
    raise RuntimeError('replacement payload probe was not blocked')
probe = subprocess.run([sys.executable, '-c', 'import validation_firewall as g; g.check(g.ROOT / "data" / "a019c-r13-descendant-probe.feather")'], capture_output=True, text=True)
assert probe.returncode != 0 and 'SourceAccessDenied' in probe.stderr
handshake = Path(os.environ['MALECNS_A014_REPLACEMENT_HANDSHAKE'])
guard.record('replacement_ready', parent_pid=os.getppid(), executable=sys.executable)
handshake.with_suffix('.ready').write_text(str(os.getpid()), encoding='utf-8')
deadline = time.monotonic() + 10
while not handshake.with_suffix('.release').exists():
    assert time.monotonic() < deadline, 'replacement release timeout'
    time.sleep(0.01)
allocation = bytearray(160 * 1024**2)
guard.record('replacement_allocated', bytes=len(allocation))
handshake.with_suffix('.allocated').write_text(str(len(allocation)), encoding='utf-8')
print(os.getpid(), flush=True)
time.sleep(8)
'''
        code = ('import subprocess,sys,os; import validation_firewall as g; '
                f'p=subprocess.Popen([sys.executable,"-c",{workload!r}]); '
                'g.record("replacement_handoff", child_pid=p.pid, executable=sys.executable); sys.exit(0)')
        command = [executable, '-c', code]
        monkeypatch.setenv('MALECNS_A014_REPLACEMENT_HANDSHAKE', str(handshake))
        original_job = investigation.ProcessJob
        def replacement_job(argv):
            import time
            job = original_job(argv)
            try:
                deadline = time.monotonic() + 15
                ready = handshake.with_suffix('.ready')
                while not ready.exists():
                    assert time.monotonic() < deadline, 'replacement readiness timeout'
                    time.sleep(0.01)
                workload_pid = int(ready.read_text(encoding='utf-8'))
                assert workload_pid in job.pids()
                assert workload_pid != job.process.pid
                assert job.process.wait(timeout=5) == 0, 'original launcher must exit normally'
                handshake.with_suffix('.release').write_text('release', encoding='utf-8')
                allocated = handshake.with_suffix('.allocated')
                deadline = time.monotonic() + 10
                while not allocated.exists():
                    assert workload_pid in job.pids(), 'replacement exited before allocation'
                    assert time.monotonic() < deadline, 'replacement allocation timeout'
                    time.sleep(0.01)
                assert allocated.read_text(encoding='utf-8') == str(160 * 1024**2)
                guard.record('replacement_supervision_start', launcher_pid=job.process.pid,
                             launcher_exit=job.process.returncode, workload_pid=workload_pid,
                             inventory=job.pids(), attempt=1)
                return job
            except BaseException:
                job.close()
                raise
        monkeypatch.setattr(investigation, 'ProcessJob', replacement_job)
    if mode == 'direct' and os.environ.get('MALECNS_A019C_R2_FIREWALL') == '1':
        import validation_firewall as guard
        command = [str(Path(executable).resolve()), '-S', guard.DIRECT_ENTRY, guard.DIRECT_PURPOSE]
        handshake = tmp_path / 'direct-control'
        monkeypatch.setenv('MALECNS_A014_CONTROL_HANDSHAKE', str(handshake))
        original_job = investigation.ProcessJob
        def ready_job(argv):
            import time
            job = original_job(argv)
            try:
                for phase in ('ready', 'allocated'):
                    deadline = time.monotonic() + 10
                    marker = handshake.with_suffix('.' + phase)
                    while not marker.exists():
                        assert job.process.poll() is None, 'direct control exited before ' + phase
                        assert time.monotonic() < deadline, 'direct control readiness timeout'
                        time.sleep(0.01)
                    if phase == 'ready':
                        handshake.with_suffix('.release').write_text('release', encoding='utf-8')
                assert marker.read_text(encoding='utf-8') == str(160 * 1024**2)
                return job
            except BaseException:
                job.close()
                raise
        monkeypatch.setattr(investigation, 'ProcessJob', ready_job)
    result = investigation.supervise_synthetic(command, cap=128*1024**2)
    assert result['classification'] == 'MEMORY_LIMIT', result
    assert result['offenders']
    assert result['orphans'] == []
    assert result['exit_code'] == (0 if mode == 'replacement' else 1)
    if mode == 'replacement' and os.environ.get('MALECNS_A019C_R2_FIREWALL') == '1':
        assert int(handshake.with_suffix('.ready').read_text(encoding='utf-8')) in result['offenders']
        guard.record('replacement_result', result=result)
    if mode == 'direct':
        assert result['launcher_pid'] in result['offenders']
    if mode != 'direct':
        assert any(pid != result['launcher_pid'] for pid in result['offenders'])
        sample = result['samples'][-1]['processes']
        if result['launcher_pid'] in sample:
            assert sample[result['launcher_pid']]['private_bytes'] < 128*1024**2


def test_aggregate_limit_without_individual_offender():
    code = 'import subprocess,sys,time; x=bytearray(60*1024**2); p=subprocess.Popen([sys.executable,"-c","import time; x=bytearray(60*1024**2); time.sleep(8)"]); p.wait()'
    result = investigation.supervise_synthetic([sys.executable, '-c', code], cap=128*1024**2)
    assert result['classification'] == 'MEMORY_LIMIT'
    assert result['orphans'] == []


def test_normal_exit(monkeypatch, tmp_path):
    code = 'print("normal")'
    if os.environ.get('MALECNS_A019C_R2_FIREWALL') == '1':
        import validation_firewall as guard
        # This print-only control needs no native BLAS worker pool at startup.
        monkeypatch.setenv('OPENBLAS_NUM_THREADS', '1')
        completed = tmp_path / 'normal-completed.txt'
        code = ('import validation_firewall as g; assert g.ACTIVE; '
                'g.record("normal_ready"); g.record("normal_workload_start"); '
                'print("normal", flush=True); g.record("normal_completed"); '
                f'from pathlib import Path; Path({str(completed)!r}).write_text("normal", encoding="utf-8")')
    result = investigation.supervise_synthetic([sys.executable, '-c', code])
    if os.environ.get('MALECNS_A019C_R2_FIREWALL') == '1':
        guard.record('normal_result', result=result)
        assert completed.read_text(encoding='utf-8') == 'normal'
    assert result['classification'] == 'NORMAL_EXIT'
    assert result['exit_code'] == 0
    assert result['orphans'] == []


def test_accounting_failure_stops_tree(monkeypatch):
    def fail(self):
        raise OSError('injected accounting failure')
    monkeypatch.setattr(investigation.ProcessJob, 'snapshot', fail)
    result = investigation.supervise_synthetic([sys.executable, '-c', 'import time; time.sleep(8)'])
    assert result['classification'] == 'WATCHDOG_FAILURE'
    assert result['orphans'] == []


def test_instrumentation_opt_in_and_exact_identity(tmp_path):
    from malecns_sim.analysis.task008 import prepare_network
    files = investigation.synthetic_files(tmp_path, 2000, 100)
    assert sys.gettrace() is None
    before = prepare_network(*files)
    with investigation.PreparationProbe() as probe:
        after = prepare_network(*files)
    assert sys.gettrace() is None
    assert before.fingerprint == after.fingerprint
    for field in ('neuron_ids', 'source_positions', 'target_positions', 'effective_weights_mV', 'outgoing_indptr', 'outgoing_targets', 'outgoing_weights_mV'):
        np.testing.assert_array_equal(getattr(before.projection, field), getattr(after.projection, field))
    for field in ('presynaptic_signs', 'signed_counts', 'signed_edge_mask'):
        np.testing.assert_array_equal(getattr(before.signed_connectome, field), getattr(after.signed_connectome, field))
    assert before.projection.synaptic_weight_mV == after.projection.synaptic_weight_mV
    assert any(row['arrays'] for row in probe.rows)
    assert any(row['tables'] for row in probe.rows)
    assert {row['event'] for row in probe.rows} >= {'call', 'return'}
    assert all(row['private_bytes'] > 0 for row in probe.rows)
