"""Windows audit identity controls, ordered before process bootstrap."""
import os
import ctypes
from ctypes import wintypes
import subprocess
import sys
import time

import pytest
import validation_firewall as guard


def retained_process_handles(job, pids):
    """Retain process identities so exit checks cannot confuse reused PIDs."""
    job.kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    job.kernel.OpenProcess.restype = wintypes.HANDLE
    job.kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    return [job.kernel.OpenProcess(0x100000, False, pid) for pid in pids]


def assert_exited_and_release(job, handles):
    try:
        assert all(handles)
        assert all(job.kernel.WaitForSingleObject(handle, 5000) == 0 for handle in handles)
    finally:
        for handle in handles:
            if handle:
                job.kernel.CloseHandle(handle)


@pytest.mark.parametrize('python,entry,tail,expected', [
    (r'C:\Python\python.exe', r'C:\repo\guarded_child.py', ['-c', 'print(19)'], True),
    (r'C:\Python Space\python.exe', r'C:\repo\guarded_child.py', ['-c', 'print(19)'], True),
    (r'C:\Python\python.exe', r'C:\repo space\guarded_child.py', ['-c', 'print(19)', 'ordinary arg'], True),
    (r'C:\Python Space\python.exe', r'C:\repo space\guarded_child.py', ['-c', 'print(19)', 'escaped "quote" and slash\\'], True),
])
def test_canonical_serialization(monkeypatch, python, entry, tail, expected):
    monkeypatch.setattr(sys, 'executable', python)
    monkeypatch.setattr(guard, 'CHILD_ENTRY', entry)
    argv = [python, entry, *tail]
    serialized = subprocess.list2cmdline(argv)
    assert guard.audit_argv(serialized) == argv
    assert guard.mandatory_child(serialized) is expected


@pytest.mark.parametrize('tail', [
    ['-c', 'guarded_child.py'],
    ['different_guarded_child.py', '-c', 'print(19)'],
    ['guarded_child.py.bak', '-c', 'print(19)'],
])
def test_false_positive_rejected(tail):
    assert not guard.mandatory_child(subprocess.list2cmdline([sys.executable, *tail]))


def test_malformed_rejected():
    assert not guard.mandatory_child('"unterminated')
    assert not guard.mandatory_child('')


def test_actual_windows_audit_serialization():
    observed = []
    sys.addaudithook(lambda event, args: observed.append(args)
                     if event == 'subprocess.Popen' else None)
    result = subprocess.run([sys.executable, '-c', 'print(19)', 'quoted ordinary arg'],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    executable, command, cwd, env = observed[-1]
    assert isinstance(command, str)
    assert guard.mandatory_child(command, executable)
    assert command == subprocess.list2cmdline(
        [sys.executable, guard.CHILD_ENTRY, '-c', 'print(19)', 'quoted ordinary arg'])


def test_actual_worker_bypass_rejected(monkeypatch):
    monkeypatch.setattr(guard, 'guarded_command', lambda command: command)
    with pytest.raises(guard.SourceAccessDenied, match='mandatory firewall entrypoint'):
        subprocess.run([sys.executable, str(guard.ROOT / 'scripts/benchmark_application_a019.py'),
                        '--worker', '--firewall-bootstrap-probe'], capture_output=True)


def test_script_path_with_spaces(tmp_path, monkeypatch):
    entry = tmp_path / 'guarded child directory' / 'guarded_child.py'
    entry.parent.mkdir()
    entry.write_bytes(__import__('pathlib').Path(guard.CHILD_ENTRY).read_bytes())
    monkeypatch.setattr(guard, 'CHILD_ENTRY', str(entry))
    payload = 'ordinary "quoted" value with trailing slash\\'
    result = subprocess.run([sys.executable, str(entry), '-c',
                             'import sys; print(repr(sys.argv[1]))', payload],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == repr(payload)


@pytest.mark.parametrize('activation', ['1', None, 'corrupt'])
def test_contained_actual_worker_startup(monkeypatch, activation):
    sys.path.insert(0, str(guard.ROOT / 'scripts'))
    from investigate_application_a014 import ProcessJob
    command = guard.guarded_command([
        sys.executable, str(guard.ROOT / 'scripts/benchmark_application_a019.py'),
        '--worker', '--firewall-bootstrap-probe'])
    if activation is None:
        monkeypatch.delenv('MALECNS_A019C_R2_FIREWALL')
    else:
        monkeypatch.setenv('MALECNS_A019C_R2_FIREWALL', activation)
    job = ProcessJob(command)
    worker_pid = job.process.pid
    before = job.pids()
    handles = retained_process_handles(job, before)
    try:
        output, _ = job.process.communicate(timeout=15)
        assert job.process.pid > 0
        assert job.process.returncode == (0 if activation == '1' else 78)
        if activation == '1':
            assert 'A019_WORKER_GUARDED_BEFORE_WORKLOAD' in output
        else:
            assert 'FIREWALL_REQUIRED_BUT_NOT_ACTIVE' in output
            assert 'A019_WORKER_GUARDED_BEFORE_WORKLOAD' not in output
    finally:
        job.close()
        assert_exited_and_release(job, handles)
    assert job.handle is None
    assert job.process.poll() == (0 if activation == '1' else 78)
    job.close()
    assert job.handle is None
    assert job.process.poll() == (0 if activation == '1' else 78)
    guard.record('contained_cleanup', parent_pid=os.getpid(), worker_pid=worker_pid,
                 child_pids=[], before_cleanup=before, after_cleanup=[],
                 exit_code=job.process.returncode, handle_released=True,
                 repeated_cleanup=True, orphan_scan='PASS')


@pytest.mark.parametrize('descendants', [1, 2])
def test_live_contained_descendant_cleanup(tmp_path, descendants):
    """Capture every live Job member and verify every retained identity exits."""
    sys.path.insert(0, str(guard.ROOT / 'scripts'))
    from investigate_application_a014 import ProcessJob
    import json
    markers = [tmp_path / f'descendant-{index}' for index in range(descendants)]
    root_marker = tmp_path / 'root-ready'
    child_codes = [
        f"import os, json, time; from pathlib import Path; Path({str(marker)!r}).write_text(json.dumps(dict(pid=os.getpid(), parent_pid=os.getppid()))); time.sleep(60)"
        for marker in markers]
    code = (
        "import subprocess, sys, time, os, json; from pathlib import Path; "
        f"children = [subprocess.Popen([sys.executable, '-c', child]) for child in {child_codes!r}]; "
        f"Path({str(root_marker)!r}).write_text(json.dumps(dict(pid=os.getpid(), parent_pid=os.getppid(), launched_children=[child.pid for child in children]))); time.sleep(60)")
    job = ProcessJob([sys.executable, '-c', code])
    handles = []
    try:
        deadline = time.monotonic() + 15
        observations = []
        while not all(marker.exists() for marker in [root_marker, *markers]) and time.monotonic() < deadline:
            observations.append(job.pids())
            time.sleep(0.01)
        before = sorted(set(job.pids()))
        handles = retained_process_handles(job, before)
        guard.record('live_tree_inventory', worker_pid=job.process.pid,
                     observations=observations, before_cleanup=before,
                     descendant_roles=descendants)
        assert all(marker.exists() for marker in [root_marker, *markers])
        roles = [json.loads(marker.read_text()) for marker in [root_marker, *markers]]
        assert job.process.pid in before
        assert len(before) >= 1
        assert all(role['pid'] in before for role in roles)
        assert all(pid in before for pid in roles[0]['launched_children'])
        assert all(role['parent_pid'] in before for role in roles[1:])
        assert set(job.pids()) == set(before)
        guard.record('live_tree_roles', worker_pid=job.process.pid, roles=roles)
    finally:
        job.close()
        assert_exited_and_release(job, handles)
    assert job.handle is None
    assert job.process.poll() is not None
    for pid in before:
        probe = job.kernel.OpenProcess(0x100000, False, pid)
        try:
            assert not probe or job.kernel.WaitForSingleObject(probe, 0) == 0
        finally:
            if probe:
                job.kernel.CloseHandle(probe)
    job.close()
    assert job.handle is None
    guard.record('live_tree_cleanup', parent_pid=os.getpid(), worker_pid=job.process.pid,
                 child_pids=[pid for pid in before if pid != job.process.pid],
                 before_cleanup=before, after_cleanup=[], exit_code=job.process.returncode,
                 handle_released=True, repeated_cleanup=True, orphan_scan='PASS')
