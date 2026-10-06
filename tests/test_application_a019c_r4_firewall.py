"""R4 bootstrap matrix, using only synthetic workloads and denied path probes."""
import os
import subprocess
import sys

import pytest
import pyarrow as pa
import pyarrow.feather as feather
import pyarrow._feather as native
import validation_firewall as guard


def test_parent_native_control_and_categories(tmp_path):
    assert guard.ACTIVE
    assert pa.__version__ == '25.0.1'
    source = tmp_path / 'synthetic.feather'
    feather.write_feather(pa.table({'sentinel': [19]}), source)
    assert native.FeatherReader(str(source), use_memory_map=False,
                               use_threads=True).read().to_pydict() == {'sentinel': [19]}
    for name in ('connectome-weights.feather', 'annotation.feather',
                 'neurotransmitter.feather', 'metadata.json', 'provenance.json',
                 'mapping.json', 'other.bin'):
        with pytest.raises(guard.SourceAccessDenied):
            (guard.ROOT / 'data' / name).read_bytes()
        with pytest.raises(guard.SourceAccessDenied):
            native.FeatherReader(str(guard.ROOT / 'data' / name),
                                 use_memory_map=False, use_threads=True).read()


@pytest.mark.parametrize('activation', [None, 'corrupt'])
@pytest.mark.parametrize('worker', [False, True])
def test_required_child_rejects_before_workload(tmp_path, activation, worker):
    marker = tmp_path / 'workload-executed'
    workload = [str(guard.ROOT / 'scripts/benchmark_application_a019.py'),
                '--worker', '--firewall-bootstrap-probe'] if worker else [
                    '-c', f"from pathlib import Path; Path({str(marker)!r}).write_text('executed')"]
    command = guard.guarded_command([sys.executable, *workload])
    env = dict(os.environ)
    env.pop('MALECNS_A019C_R2_FIREWALL', None)
    env.pop('PYTHONPATH', None)
    if activation is not None:
        env['MALECNS_A019C_R2_FIREWALL'] = activation
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    assert result.returncode == 78
    assert 'FIREWALL_REQUIRED_BUT_NOT_ACTIVE' in result.stderr
    assert not marker.exists()
    assert 'A019_WORKER_GUARDED_BEFORE_WORKLOAD' not in result.stdout


def test_normal_public_native_child(tmp_path):
    source = tmp_path / 'child.feather'
    code = f'''import validation_firewall as g
import pyarrow as pa
import pyarrow.feather as f
import pyarrow._feather as n
assert g.ACTIVE
source = {str(source)!r}
f.write_feather(pa.table({{"sentinel": [19]}}), source)
assert f.read_table(source).to_pydict() == {{"sentinel": [19]}}
assert n.FeatherReader(source, use_memory_map=False, use_threads=True).read().to_pydict() == {{"sentinel": [19]}}
for reader in (f.read_table, lambda p: n.FeatherReader(p, use_memory_map=False, use_threads=True).read()):
    try:
        reader(str(g.ROOT/'data/raw/male-cns/v1.0/connectome-weights-male-cns-v1.0-minconf-0.5.feather'))
    except g.SourceAccessDenied:
        pass
    else:
        raise AssertionError('registered source accepted')
print('GUARDED SYNTHETIC WORKLOAD EXECUTED')
'''
    result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'GUARDED SYNTHETIC WORKLOAD EXECUTED' in result.stdout


def test_actual_worker_startup():
    result = subprocess.run([sys.executable,
        str(guard.ROOT / 'scripts/benchmark_application_a019.py'),
        '--worker', '--firewall-bootstrap-probe'], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'A019_WORKER_GUARDED_BEFORE_WORKLOAD' in result.stdout


def test_inherited_activation_removed_parent_rejects(monkeypatch):
    monkeypatch.delenv('MALECNS_A019C_R2_FIREWALL')
    with pytest.raises(guard.SourceAccessDenied):
        subprocess.run([sys.executable, '-c', "print('WORKLOAD')"])
