"""Opt-in synthetic preparation profiling and Windows process-tree containment."""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import numpy as np

_spec = importlib.util.spec_from_file_location('a013_memory', Path(__file__).with_name('benchmark_application_a013.py'))
_a013 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a013)
WindowsMemory = _a013.WindowsMemory


class ProcessJob:
    """Launch suspended, assign before execution, and contain all descendants."""

    def __init__(self, command):
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
        self.kernel.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
        self.kernel.QueryInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p)
        self.kernel.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
        self.kernel.SetInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD)
        self.kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        self.handle = self.kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        self.process = None
        try:
            class BasicLimits(ctypes.Structure):
                _fields_ = [('process_time', ctypes.c_longlong), ('job_time', ctypes.c_longlong),
                            ('flags', wintypes.DWORD), ('minimum_ws', ctypes.c_size_t),
                            ('maximum_ws', ctypes.c_size_t), ('active_processes', wintypes.DWORD),
                            ('affinity', ctypes.c_size_t), ('priority', wintypes.DWORD), ('scheduling', wintypes.DWORD)]
            class ExtendedLimits(ctypes.Structure):
                _fields_ = [('basic', BasicLimits), ('io', ctypes.c_ulonglong * 6),
                            ('process_memory', ctypes.c_size_t), ('job_memory', ctypes.c_size_t),
                            ('peak_process_memory', ctypes.c_size_t), ('peak_job_memory', ctypes.c_size_t)]
            limits = ExtendedLimits()
            limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE; breakaway is not enabled.
            if not self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
                raise ctypes.WinError(ctypes.get_last_error())
            self.process = subprocess.Popen(command, creationflags=4, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if not self.kernel.AssignProcessToJobObject(self.handle, int(self.process._handle)):
                raise ctypes.WinError(ctypes.get_last_error())
            ntdll = ctypes.WinDLL('ntdll')
            ntdll.NtResumeProcess.argtypes = (wintypes.HANDLE,)
            if ntdll.NtResumeProcess(int(self.process._handle)) != 0:
                raise OSError('cannot resume contained process')
        except BaseException:
            self.close()
            raise

    def pids(self):
        # A bounded inventory overflow is a watchdog failure, never a partial sum.
        class Inventory(ctypes.Structure):
            _fields_ = [('assigned', wintypes.DWORD), ('count', wintypes.DWORD), ('ids', ctypes.c_size_t * 256)]
        value = Inventory()
        if not self.kernel.QueryInformationJobObject(self.handle, 3, ctypes.byref(value), ctypes.sizeof(value), None):
            raise ctypes.WinError(ctypes.get_last_error())
        if value.count > 256 or value.assigned > 256:
            raise OSError('process inventory overflow')
        return list(value.ids[:value.count])

    def snapshot(self):
        rows = {}
        for pid in self.pids():
            monitor = WindowsMemory(pid)
            try:
                rows[pid] = monitor.snapshot()
            finally:
                monitor.close()
        return {'processes': rows, **{key: sum(row[key] for row in rows.values()) for key in ('private_bytes', 'working_set')}}

    def close(self):
        if self.handle:
            if not self.kernel.TerminateJobObject(self.handle, 1):
                raise ctypes.WinError(ctypes.get_last_error())
            if self.process is not None:
                if self.process.poll() is None:
                    self.process.terminate()
                self.process.wait(timeout=5)
            deadline = time.monotonic() + 5
            while self.pids() and time.monotonic() < deadline:
                time.sleep(0.01)
            if self.pids():
                raise OSError('contained process remains after termination')
            self.kernel.CloseHandle(self.handle)
            self.handle = None


def supervise_synthetic(command, cap=256 * 1024**2, timeout=10):
    job = ProcessJob(command)
    result = {'classification': 'NORMAL_EXIT', 'samples': [], 'launcher_pid': job.process.pid}
    started = time.monotonic()
    try:
        while job.pids():
            snapshot = job.snapshot()
            result['samples'].append(snapshot)
            if max(snapshot['private_bytes'], snapshot['working_set']) > cap:
                result['classification'] = 'MEMORY_LIMIT'
                result['offenders'] = [pid for pid, row in snapshot['processes'].items() if max(row['private_bytes'], row['working_set']) > cap]
                break
            if time.monotonic() - started > timeout:
                result['classification'] = 'TIME_LIMIT'
                break
            time.sleep(0.02)
    except Exception as exc:
        result.update(classification='WATCHDOG_FAILURE', error=repr(exc))
    finally:
        job.close()
    result['orphans'] = []  # close verifies the job inventory is empty.
    result['exit_code'] = job.process.returncode
    return result


class PreparationProbe:
    """Explicit scoped tracing of preparation boundaries and live local arrays."""
    names = {'load_male_cns_v1_numeric', '_aggregate_numeric_edges', 'project_numeric_connectome', 'from_projection', 'from_signed_connectome', 'prepare_network'}

    def __init__(self):
        self.rows = []
        self.seen = set()

    def __enter__(self):
        if sys.gettrace() is not None:
            raise RuntimeError('refuse to replace an existing tracer')
        self.monitor = WindowsMemory(os.getpid())
        sys.settrace(self.trace)
        return self

    def trace(self, frame, event, arg):
        if frame.f_code.co_name in self.names and 'malecns_sim' in frame.f_code.co_filename:
            key = (id(frame), event, frame.f_lineno)
            if key in self.seen:
                return self.trace
            self.seen.add(key)
            arrays = {name: {'shape': list(value.shape), 'dtype': str(value.dtype), 'bytes': value.nbytes, 'object_id': id(value), 'owns_data': bool(value.flags.owndata)}
                      for name, value in frame.f_locals.items() if isinstance(value, np.ndarray)}
            tables = {name: {'bytes': value.nbytes, 'rows': value.num_rows} for name, value in frame.f_locals.items() if hasattr(value, 'num_rows') and hasattr(value, 'nbytes')}
            containers = {name: {'count': len(value), 'shallow_bytes': sys.getsizeof(value)}
                          for name, value in frame.f_locals.items() if isinstance(value, (list, tuple, dict, set))}
            self.rows.append({'stage': frame.f_code.co_name, 'event': event, 'line': frame.f_lineno, 'arrays': arrays, 'tables': tables, 'containers': containers, **self.monitor.snapshot()})
            return self.trace
        return None

    def __exit__(self, *args):
        sys.settrace(None)
        self.monitor.close()


def synthetic_files(directory, edges, neurons=1000):
    import pyarrow as pa
    import pyarrow.feather as feather
    from malecns_sim.analysis.task007 import MALE_CNS_ANNOTATION_COLUMNS
    rng = np.random.default_rng(14)
    annotation = directory / 'annotation.feather'
    nt = directory / 'nt.feather'
    weights = directory / 'weights.feather'
    ids = np.arange(1, neurons + 1, dtype=np.int64)
    columns = {name: [None] * neurons for name in MALE_CNS_ANNOTATION_COLUMNS}
    columns.update({'bodyId': ids, 'type': ['synthetic'] * neurons, 'superclass': ['synthetic'] * neurons, 'status': ['synthetic'] * neurons})
    feather.write_feather(pa.table(columns), annotation)
    feather.write_feather(pa.table({'body': ids, 'consensus_nt': ['acetylcholine' if i % 2 else 'gaba' for i in ids]}), nt)
    feather.write_feather(pa.table({'body_pre': rng.integers(1, neurons + 1, edges), 'body_post': rng.integers(1, neurons + 1, edges), 'weight': rng.integers(1, 10, edges)}), weights)
    return annotation, nt, weights


def measure(edges):
    from malecns_sim.analysis.task008 import prepare_network
    with tempfile.TemporaryDirectory(prefix='a014-synthetic-') as directory:
        files = synthetic_files(Path(directory), edges)
        with PreparationProbe() as probe:
            prepared = prepare_network(*files)
        peak = max(probe.rows, key=lambda row: row['private_bytes'])
        return {'input_edges': edges, 'prepared_edges': prepared.projection.effective_weights_mV.size,
                'fingerprint': prepared.fingerprint, 'final_effective_bytes': prepared.memory_bytes,
                'peak_private_bytes': peak['private_bytes'], 'peak_working_set': max(row['working_set'] for row in probe.rows),
                'peak_stage': peak['stage'], 'trace': probe.rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--synthetic-edges', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.synthetic_edges <= 200000:
        parser.error('synthetic edge bound is 1..200000')
    if args.output.exists():
        parser.error('refuse to overwrite evidence')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(measure(args.synthetic_edges), indent=2) + '\n')


if __name__ == '__main__':
    main()
