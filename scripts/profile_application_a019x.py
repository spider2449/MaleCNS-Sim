"""Bounded synthetic profiling with a fixed native launch contract."""
from __future__ import annotations

import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'a019c_firewall'))
if os.environ.get('MALECNS_A019C_R2_FIREWALL') != '1':
    raise SystemExit('FIREWALL_REQUIRED_BUT_NOT_ACTIVE')
import validation_firewall as guard
guard.install()
if not guard.ACTIVE:
    raise SystemExit(78)

import argparse
import ctypes
from ctypes import wintypes as w
import gc
import hashlib
import json
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
PYTHON = ROOT / '.venv/Scripts/python.exe'
ENTRY = ROOT / 'scripts/a019c_firewall/guarded_child.py'
NSYS = Path('C:/Program Files/NVIDIA Corporation/Nsight Systems 2025.5.2/target-windows-x64/nsys.exe')
CASES = {'S1': (128, 1024), 'S4': (127400, 14687178)}
ROLES = ('CPU', 'GPU', 'TRACE')
CONTROLS = ('success', 'failure', 'timeout', 'missing')
PINS = {
    'src/malecns_sim/dynamics/cuda.py': '793b4859ff11355611c788f222d82334b6da023b82504348e115996a9b5b8ddc',
    'src/malecns_sim/dynamics/lif.py': 'c8b2f10b37ecaecce14830b6b027e79e9474bf0f3a7c79b15b7115cb923b8d8e',
    'src/malecns_sim/dynamics/stimulus.py': '8a3d14f6d7f76cf4399fe94076b0f6f4d9adde63579bd3d303da30f6a3f5f94d',
    'scripts/benchmark_application_a019v.py': 'f96513c2f315bdc7af3a132e799c199e02406bebe2b87da37bf18e5addec4294',
    'scripts/a019c_firewall/validation_firewall.py': '170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af',
}


def dump(path, record):
    path.write_text(json.dumps(record, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def output_root(value):
    path = Path(value).resolve()
    guard.check(path)
    if path.parent != Path(tempfile.gettempdir()).resolve() or not path.name.startswith('malecns-a019x-'):
        raise ValueError('OUTPUT_OUTSIDE_TASK_TEMP_DIRECTORY')
    if not path.is_dir():
        raise ValueError('OUTPUT_DIRECTORY_MISSING')
    return path


def check_pins():
    for name, expected in PINS.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError('SOURCE_PIN_MISMATCH: ' + name)


def command(output, kind, case='', role=''):
    """Construct the entire allowed argv; callers cannot supply native options."""
    output = output_root(output)
    if kind == 'control':
        if case not in CONTROLS or role:
            raise ValueError('INVALID_CONTROL')
        target = [str(PYTHON), str(ENTRY), str(SELF), '--control-worker', case, '--output', str(output)]
        options = ['--trace=nvtx', '--capture-range=none']
        label = 'control-' + case
    elif kind == 'workload':
        if case not in CASES or role not in ROLES:
            raise ValueError('INVALID_WORKLOAD')
        target = [str(PYTHON), str(ENTRY), str(SELF), '--worker', '--case', case,
                  '--role', role, '--output', str(output)]
        if role != 'TRACE':
            return target
        options = ['--trace=cuda,nvtx', '--capture-range=cudaProfilerApi',
                   '--capture-range-end=stop', '--cuda-memory-usage=false',
                   '--cuda-trace-all-apis=false']
        label = case + '-' + role
    elif kind == 'export':
        if case not in CASES or role:
            raise ValueError('INVALID_EXPORT')
        return [str(NSYS), 'export', '--type=sqlite', '--force-overwrite=false',
                '--output=' + str(output / (case + '-TRACE.sqlite')),
                str(output / (case + '-TRACE.nsys-rep'))]
    else:
        raise ValueError('INVALID_LAUNCH_KIND')
    return [str(NSYS), 'profile', *options, '--sample=none', '--cpuctxsw=none',
            '--python-sampling=false', '--gpu-metrics-devices=none', '--gpuctxsw=false',
            '--kill=false', '--force-overwrite=false',
            '--output=' + str(output / label), *target]


def child_environment():
    """Remove interactive Python overrides before the fixed noninteractive launch."""
    env = dict(os.environ)
    for name in ('PYTHONHOME', 'PYTHONSTARTUP', 'PYTHONINSPECT'):
        env.pop(name, None)
    env['PYTHONPATH'] = str(ROOT / 'scripts/a019c_firewall')
    return env


def validate_launch(argv, output, kind, case='', role='', env=None):
    expected = command(output, kind, case, role)
    env = child_environment() if env is None else env
    if list(argv) != expected:
        raise ValueError('NATIVE_ARGV_NOT_EXACT')
    if not guard.ACTIVE or os.environ.get('MALECNS_A019C_R2_FIREWALL') != '1':
        raise ValueError('PARENT_GUARD_INACTIVE')
    required = None if kind == 'control' and case == 'missing' else '1'
    if env.get('MALECNS_A019C_R2_FIREWALL') != required:
        raise ValueError('CHILD_GUARD_ENVIRONMENT_INVALID')
    if env.get('PYTHONPATH') != str(ROOT / 'scripts/a019c_firewall'):
        raise ValueError('CHILD_PYTHONPATH_INVALID')
    if any(env.get(name) for name in ('PYTHONHOME', 'PYTHONSTARTUP', 'PYTHONINSPECT')):
        raise ValueError('CHILD_PYTHON_OVERRIDE')
    return expected


class NativeJob:
    """Exact task-local CreateProcessW launch; general guard policy stays intact."""

    def __init__(self, output, kind, case='', role='', env=None):
        from investigate_application_a014 import ProcessJob
        self.output = output_root(output)
        self.argv = validate_launch(command(output, kind, case, role), output, kind, case, role, env)
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        k = self.kernel
        k.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
        k.CreateJobObjectW.restype = w.HANDLE
        k.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
        k.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        k.QueryInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.c_void_p]
        k.TerminateJobObject.argtypes = [w.HANDLE, w.UINT]
        k.TerminateProcess.argtypes = [w.HANDLE, w.UINT]
        k.CloseHandle.argtypes = [w.HANDLE]
        k.ResumeThread.argtypes = [w.HANDLE]
        k.ResumeThread.restype = w.DWORD
        k.GetExitCodeProcess.argtypes = [w.HANDLE, ctypes.POINTER(w.DWORD)]
        k.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
        k.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, ctypes.c_void_p, w.DWORD, w.DWORD, w.HANDLE]
        k.CreateFileW.restype = w.HANDLE
        self.handle = k.CreateJobObjectW(None, None)
        self.process_handle = self.thread_handle = self.log_handle = self.input_handle = None
        self.pid = None
        self.exit_code = None
        self.assigned_before_resume = False
        self._pids = ProcessJob.pids
        self._snapshot = ProcessJob.snapshot
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        class Basic(ctypes.Structure):
            _fields_ = [('process_time', ctypes.c_longlong), ('job_time', ctypes.c_longlong),
                        ('flags', w.DWORD), ('minimum_ws', ctypes.c_size_t), ('maximum_ws', ctypes.c_size_t),
                        ('active_processes', w.DWORD), ('affinity', ctypes.c_size_t),
                        ('priority', w.DWORD), ('scheduling', w.DWORD)]
        class Limits(ctypes.Structure):
            _fields_ = [('basic', Basic), ('io', ctypes.c_ulonglong * 6),
                        ('process_memory', ctypes.c_size_t), ('job_memory', ctypes.c_size_t),
                        ('peak_process_memory', ctypes.c_size_t), ('peak_job_memory', ctypes.c_size_t)]
        class Security(ctypes.Structure):
            _fields_ = [('length', w.DWORD), ('descriptor', ctypes.c_void_p), ('inherit', w.BOOL)]
        class Startup(ctypes.Structure):
            _fields_ = [('cb', w.DWORD), ('reserved', w.LPWSTR), ('desktop', w.LPWSTR), ('title', w.LPWSTR),
                        ('x', w.DWORD), ('y', w.DWORD), ('xsize', w.DWORD), ('ysize', w.DWORD),
                        ('xchars', w.DWORD), ('ychars', w.DWORD), ('fill', w.DWORD), ('flags', w.DWORD),
                        ('show', w.WORD), ('reserved_size', w.WORD), ('reserved_pointer', ctypes.c_void_p),
                        ('stdin', w.HANDLE), ('stdout', w.HANDLE), ('stderr', w.HANDLE)]
        class Info(ctypes.Structure):
            _fields_ = [('process', w.HANDLE), ('thread', w.HANDLE), ('pid', w.DWORD), ('tid', w.DWORD)]
        k.CreateProcessW.argtypes = [w.LPCWSTR, w.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
                                    w.BOOL, w.DWORD, ctypes.c_void_p, w.LPCWSTR,
                                    ctypes.POINTER(Startup), ctypes.POINTER(Info)]
        label = '-'.join(filter(None, (kind, case, role)))
        self.log_path = self.output / (label + '-native.log')
        try:
            limits = Limits()
            limits.basic.flags = 0x2000
            if not k.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
                raise ctypes.WinError(ctypes.get_last_error())
            security = Security(ctypes.sizeof(Security), None, True)
            self.log_handle = k.CreateFileW(str(self.log_path), 0x40000000, 3, ctypes.byref(security), 1, 0x80, None)
            self.input_handle = k.CreateFileW('NUL', 0x80000000, 3, ctypes.byref(security), 3, 0x80, None)
            if any(value in (None, ctypes.c_void_p(-1).value) for value in (self.log_handle, self.input_handle)):
                raise ctypes.WinError(ctypes.get_last_error())
            startup = Startup()
            startup.cb, startup.flags = ctypes.sizeof(Startup), 0x100
            startup.stdin, startup.stdout, startup.stderr = self.input_handle, self.log_handle, self.log_handle
            info = Info()
            environment = child_environment() if env is None else dict(env)
            block = ctypes.create_unicode_buffer('\0'.join(key + '=' + value for key, value in
                                                    sorted(environment.items(), key=lambda item: item[0].upper())) + '\0\0')
            serialized = ctypes.create_unicode_buffer(subprocess.list2cmdline(self.argv))
            flags = 0x4 | 0x400 | 0x08000000
            if not k.CreateProcessW(self.argv[0], serialized, None, None, True, flags, block,
                                    str(ROOT), ctypes.byref(startup), ctypes.byref(info)):
                raise ctypes.WinError(ctypes.get_last_error())
            self.process_handle, self.thread_handle, self.pid = info.process, info.thread, int(info.pid)
            if not k.AssignProcessToJobObject(self.handle, self.process_handle):
                raise ctypes.WinError(ctypes.get_last_error())
            if self.pid not in self.pids():
                raise RuntimeError('SUSPENDED_ROOT_NOT_IN_JOB')
            self.assigned_before_resume = True
            if k.ResumeThread(self.thread_handle) == 0xffffffff:
                raise ctypes.WinError(ctypes.get_last_error())
            guard.record('a019x_exact_native_launch', argv=self.argv, cwd=str(ROOT),
                         root_pid=self.pid, assigned_before_resume=True)
        except BaseException:
            self.close()
            raise

    def pids(self):
        return self._pids(self)

    def snapshot(self):
        return self._snapshot(self)

    def poll(self):
        value = w.DWORD()
        if not self.kernel.GetExitCodeProcess(self.process_handle, ctypes.byref(value)):
            raise ctypes.WinError(ctypes.get_last_error())
        return None if value.value == 259 else int(value.value)

    def close(self):
        if self.handle:
            if not self.kernel.TerminateJobObject(self.handle, 1):
                raise ctypes.WinError(ctypes.get_last_error())
            deadline = time.monotonic() + 5
            while self.pids() and time.monotonic() < deadline:
                time.sleep(0.01)
            if self.pids():
                raise RuntimeError('CONTAINED_PROCESS_REMAINS')
            if self.process_handle:
                # Assignment failure can leave a suspended root outside the Job.
                if self.poll() is None:
                    if not self.kernel.TerminateProcess(self.process_handle, 1):
                        raise ctypes.WinError(ctypes.get_last_error())
                self.kernel.WaitForSingleObject(self.process_handle, 5000)
                self.exit_code = self.poll()
            self.kernel.CloseHandle(self.handle)
            self.handle = None
        for name in ('process_handle', 'thread_handle', 'log_handle', 'input_handle'):
            value = getattr(self, name, None)
            if value and value != ctypes.c_void_p(-1).value:
                self.kernel.CloseHandle(value)
            setattr(self, name, None)


def in_job():
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.GetCurrentProcess.restype = w.HANDLE
    k.IsProcessInJob.argtypes = [w.HANDLE, w.HANDLE, ctypes.POINTER(w.BOOL)]
    answer = w.BOOL()
    if not k.IsProcessInJob(k.GetCurrentProcess(), None, ctypes.byref(answer)) or not answer.value:
        raise RuntimeError('WORKER_NOT_CONTAINED')


def control_worker(output, mode):
    """Non-GPU rendezvous, guarded descendant and denied-source controls."""
    in_job()
    for name in ('connectome-weights.feather', 'annotation.feather', 'neurotransmitter.feather',
                 'metadata.json', 'provenance.json', 'mapping.json', 'other.bin'):
        try:
            (ROOT / 'data' / name).read_bytes()
        except guard.SourceAccessDenied:
            pass
        else:
            raise RuntimeError('REGISTERED_SOURCE_ACCEPTED')
    marker = output / ('control-' + mode + '-descendant.json')
    code = ("import os,time,json; from pathlib import Path; "
            "import validation_firewall as g; assert g.ACTIVE; "
            f"Path({str(marker)!r}).write_text(json.dumps(dict(pid=os.getpid(),parent=os.getppid()))); time.sleep(60)")
    child = subprocess.Popen([sys.executable, '-c', code])
    try:
        until = time.monotonic() + 15
        while not marker.exists() and time.monotonic() < until:
            time.sleep(0.01)
        if not marker.exists():
            raise RuntimeError('DESCENDANT_NOT_READY')
        dump(output / ('control-' + mode + '-ready.json'),
             dict(pid=os.getpid(), parent=os.getppid(), descendant=json.loads(marker.read_text()), guard=True))
        until = time.monotonic() + 60
        while not (output / ('control-' + mode + '-release')).exists() and time.monotonic() < until:
            time.sleep(0.02)
        if mode == 'failure':
            dump(output / 'control-failure-expected-error.json',
                 dict(error='EXPECTED_A019X_CONTROL_FAILURE', pid=os.getpid()))
            raise RuntimeError('EXPECTED_A019X_CONTROL_FAILURE')
        dump(output / ('control-' + mode + '-done.json'), dict(success=True, pid=os.getpid()))
    finally:
        child.terminate()
        child.wait(timeout=5)


def supervise(output, kind, case='', role='', timeout=300):
    environment = child_environment()
    if kind == 'control' and case == 'missing':
        environment.pop('MALECNS_A019C_R2_FIREWALL', None)
    job = NativeJob(output, kind, case, role, environment)
    result = dict(argv=job.argv, root_pid=job.pid, assigned_before_resume=job.assigned_before_resume,
                  inventory=[], samples=[], outcome='NORMAL_EXIT', log=str(job.log_path))
    start = phase_start = time.monotonic()
    phase = 'prepare'
    released = False
    try:
        while job.pids():
            inventory = job.pids()
            result['inventory'].append(inventory)
            result['samples'].append(job.snapshot())
            now = time.monotonic()
            if kind == 'control' and case != 'missing':
                ready = output / ('control-' + case + '-ready.json')
                if ready.exists() and not released:
                    roles = json.loads(ready.read_text())
                    if not all(pid in inventory for pid in (roles['pid'], roles['descendant']['pid'])):
                        raise RuntimeError('WORKER_OR_DESCENDANT_OUTSIDE_JOB')
                    result['roles'] = roles
                    released = True
                    if case != 'timeout':
                        (output / ('control-' + case + '-release')).write_text('release')
                    else:
                        timeout = now - start + 1
            if kind == 'workload':
                progress = output / (case + '-' + role + '-progress.json')
                if progress.exists():
                    row = json.loads(progress.read_text())
                    if row['phase'] != phase or row['at'] > phase_start:
                        phase, phase_start = row['phase'], row['at']
            last = result['samples'][-1]
            if max(last['private_bytes'], last['working_set']) > 8 * 1024**3:
                result['outcome'] = 'HOST_MEMORY_LIMIT'
                break
            if now - start > timeout or (kind == 'workload' and now - phase_start > (30 if phase == 'advance' else 180)):
                result['outcome'] = 'TIME_LIMIT'
                break
            if sum(path.stat().st_size for path in output.rglob('*') if path.is_file()) > 2 * 1024**3:
                result['outcome'] = 'OUTPUT_LIMIT'
                break
            time.sleep(0.1)
    finally:
        result['before_cleanup'] = job.pids()
        job.close()
        result.update(exit_code=job.exit_code, after_cleanup=[], handles_released=True,
                      wall_seconds=time.monotonic() - start)
        job.close()
        result['repeated_cleanup'] = True
        dump(output / ('-'.join(filter(None, (kind, case, role))) + '-supervision.json'), result)
    return result


def run_controls(output):
    check_pins()
    results = []
    for mode in CONTROLS:
        result = supervise(output, 'control', mode, timeout=60)
        log = Path(result['log']).read_text(encoding='utf-8', errors='replace')
        if mode == 'success':
            passed = result['outcome'] == 'NORMAL_EXIT' and result['exit_code'] == 0 and (output / 'control-success-done.json').exists()
        elif mode == 'failure':
            marker = output / 'control-failure-expected-error.json'
            passed = (result['outcome'] == 'NORMAL_EXIT' and result['exit_code'] != 0
                      and marker.exists() and json.loads(marker.read_text())['error'] == 'EXPECTED_A019X_CONTROL_FAILURE'
                      and not (output / 'control-failure-done.json').exists())
        elif mode == 'timeout':
            passed = result['outcome'] == 'TIME_LIMIT' and 'roles' in result
        else:
            passed = (result['outcome'] == 'NORMAL_EXIT' and result['exit_code'] == 78
                      and not (output / 'control-missing-ready.json').exists())
        result['pass'] = bool(passed)
        results.append(result)
        dump(output / 'native-controls.json', results)
        print(json.dumps(dict(control=mode, passed=passed, exit_code=result['exit_code'], outcome=result['outcome'])), flush=True)
        if not passed:
            raise RuntimeError('NATIVE_CONTROL_FAILED: ' + mode)


def worker(output, case, role):
    check_pins()
    in_job()
    import numpy as np
    import benchmark_application_a019v as bench
    gpu = role != 'CPU'
    cp = None
    label = case + '-' + role
    record = dict(case=case, role=role, calls=[], comparisons=[], cleanup=False, pid=os.getpid())
    def progress(phase):
        path = output / (label + '-progress.json')
        temporary = path.with_suffix('.tmp')
        dump(temporary, dict(phase=phase, at=time.monotonic()))
        temporary.replace(path)
    progress('prepare')
    if gpu:
        import cupy as cp
        from malecns_sim.dynamics.cuda import GPUPreparedRuntime
        record['environment'] = dict(python=sys.version, numpy=np.__version__, cupy=cp.__version__,
                                     runtime=cp.cuda.runtime.runtimeGetVersion(), driver=cp.cuda.runtime.driverGetVersion())
    projection = bench.fixture(*CASES[case])
    full, windows, ids = bench.schedule(case == 'S4')
    expected = {'S1': '356f66641e82475ac9682f722d11d9aac28e700786c4307d2cbdbe61e2fac132',
                'S4': 'aa03c559d83a266375c149142620f48cf024204abde0dcd2dd17affdc56ee39f'}
    assert projection.fingerprint == expected[case]
    record.update(projection_digest=projection.fingerprint, schedule_digest=full.fingerprint,
                  full_event_count=sum(len(s.spike_times_ms) for s in full.schedules))
    runtime = GPUPreparedRuntime(projection) if gpu else bench.PreparedRuntime(projection)
    state = runtime.initial_state()
    pointers = tuple(getattr(state, name).data.ptr for name in bench.STATE_FIELDS) if gpu else ()
    graph_pointers = tuple(a.data.ptr for a in (state._backing.graph.indptr, state._backing.graph.indices,
                           state._backing.graph.weights_mV, state._backing.incoming_offsets,
                           state._backing.incoming_sources, state._backing.incoming_ordinals)) if gpu else ()
    try:
        for chunk in range(-1, 3):
            result = None
            if chunk >= 0:
                stimulus = bench.pack(windows[chunk], ids)
                progress('advance')
                observed = role == 'TRACE' and chunk == 2
                if observed:
                    cp.cuda.profiler.start()
                if gpu and chunk == 2:
                    cp.cuda.nvtx.RangePush('A019X_' + case + '_PUBLIC_ADVANCE')
                try:
                    started = time.perf_counter()
                    result = runtime.advance(state, duration_ms=20, stimulus=stimulus)
                    elapsed = time.perf_counter() - started
                finally:
                    if gpu and chunk == 2:
                        cp.cuda.nvtx.RangePop()
                    if observed:
                        cp.cuda.profiler.stop()
                record['calls'].append(dict(chunk=chunk, warmup=chunk < 2, seconds=elapsed,
                                            event_digest=stimulus.fingerprint,
                                            event_count=sum(len(s.spike_times_ms) for s in stimulus.schedules)))
            progress('verify')
            assert state.timestep == (chunk + 1) * 200
            if gpu:
                assert pointers == tuple(getattr(state, name).data.ptr for name in bench.STATE_FIELDS)
                assert graph_pointers == tuple(a.data.ptr for a in (state._backing.graph.indptr,
                    state._backing.graph.indices, state._backing.graph.weights_mV, state._backing.incoming_offsets,
                    state._backing.incoming_sources, state._backing.incoming_ordinals))
            snapshot = bench.capture(state, result, cp)
            reference = output / (case + '-CPU-' + str(chunk) + '.npz')
            if role == 'CPU':
                np.savez(reference, **snapshot)
            else:
                with np.load(reference, allow_pickle=False) as saved:
                    assert set(saved.files) == set(snapshot)
                    checks = {key: bench.compare_arrays(saved[key], value) for key, value in snapshot.items()}
                passed = all(value['pass_eq_b'] for value in checks.values())
                record['comparisons'].append(dict(chunk=chunk, fields=checks, pass_eq_b=passed))
                assert passed, 'EQ_B_FAILURE'
            del snapshot, result
    finally:
        progress('cleanup')
        if gpu:
            state.close()
            runtime.close()
        del state, runtime
        gc.collect()
        if gpu:
            cp.get_default_memory_pool().free_all_blocks()
            record['pool_after_reclaim'] = int(cp.get_default_memory_pool().used_bytes())
        record['cleanup'] = True
        dump(output / (label + '-worker.json'), record)
    progress('done')


def batch(output):
    check_pins()
    controls = json.loads((output / 'native-controls.json').read_text())
    if len(controls) != 4 or not all(row['pass'] for row in controls):
        raise RuntimeError('NATIVE_BOOTSTRAP_NOT_CERTIFIED')
    evidence = dict(schema='application-a019x-profiling-v1', starting_sha='95f53df6703ac4aa03a66ff763c5a0427ebde2b2',
                    output=str(output), pins=PINS, cases=[], classification='A019X-C', complete=False)
    target = ROOT / 'docs/plans/a019x-synthetic-gpu-profiling-evidence.json'
    start = time.monotonic()
    try:
        for case in CASES:
            row = dict(case=case, roles={})
            evidence['cases'].append(row)
            for role in ROLES:
                if time.monotonic() - start > 900:
                    raise RuntimeError('BATCH_TIME_LIMIT')
                check_pins()
                supervision = supervise(output, 'workload', case, role)
                row['roles'][role] = dict(supervision=supervision)
                if supervision['outcome'] != 'NORMAL_EXIT' or supervision['exit_code'] != 0:
                    raise RuntimeError('WORKLOAD_STOP: ' + case + '-' + role)
                record = json.loads((output / (case + '-' + role + '-worker.json')).read_text())
                assert len(record['calls']) == 3 and record['cleanup']
                row['roles'][role]['worker'] = record
                dump(target, evidence)
            export = supervise(output, 'export', case, timeout=180)
            row['export'] = export
            if export['outcome'] != 'NORMAL_EXIT' or export['exit_code'] != 0:
                raise RuntimeError('EXPORT_FAILED: ' + case)
            ratio = row['roles']['TRACE']['worker']['calls'][2]['seconds'] / row['roles']['GPU']['worker']['calls'][2]['seconds']
            row.update(observer_ratio=ratio, material_observer_effect=abs(ratio - 1) > 0.25)
            dump(target, evidence)
        evidence['complete'] = True
        evidence['next_task'] = 'Analyze the two generated bounded host/device timelines under the frozen protocol'
    except BaseException as exc:
        evidence['blocker'] = repr(exc)
        raise
    finally:
        evidence['wall_seconds'] = time.monotonic() - start
        dump(target, evidence)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--control-worker', choices=CONTROLS)
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--role', choices=ROLES)
    parser.add_argument('--batch', action='store_true')
    args = parser.parse_args()
    output = output_root(args.output)
    if sum((args.controls, bool(args.control_worker), args.worker, args.batch)) != 1:
        parser.error('choose exactly one operation')
    if args.controls:
        run_controls(output)
    elif args.control_worker:
        control_worker(output, args.control_worker)
    elif args.worker:
        if not args.case or not args.role:
            parser.error('worker requires case and role')
        worker(output, args.case, args.role)
    else:
        batch(output)


if __name__ == '__main__':
    main()
