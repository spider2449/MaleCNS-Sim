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
def test_tree_memory_enforcement(mode, repeat):
    allocate = 'import os,time; x=bytearray(160*1024**2); print(os.getpid(),flush=True); time.sleep(8)'
    executable = sys._base_executable if mode == 'direct' else sys.executable
    if mode in ('child', 'replacement'):
        code = f'import subprocess,sys,time; p=subprocess.Popen([sys.executable,"-c",{allocate!r}]); ' + ('sys.exit(0)' if mode == 'replacement' else 'p.wait()')
    else:
        code = allocate
    result = investigation.supervise_synthetic([executable, '-c', code], cap=128*1024**2)
    assert result['classification'] == 'MEMORY_LIMIT', result
    assert result['offenders']
    assert result['orphans'] == []
    assert result['exit_code'] == (0 if mode == 'replacement' else 1)
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


def test_normal_exit():
    result = investigation.supervise_synthetic([sys.executable, '-c', 'print("normal")'])
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
