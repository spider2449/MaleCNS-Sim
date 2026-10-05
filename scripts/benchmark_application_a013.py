"""Explicit opt-in, CPU-only A013 benchmark; importing never executes data work."""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone

import numpy as np

INTERVAL_MS = 20.0
DT_MS = 0.1
SEQUENCES = 2
STEPS = 12
WARMUPS = 2
MAX_PREPARATIONS = 1
MAX_ADVANCES = 24
MEMORY_CAP = 8 * 1024**3
PREPARATION_CAP = 600.0
ADVANCE_CAP = 30.0
TOTAL_CAP = 1500.0
AVAILABLE_MIN = 12 * 1024**3
PREPARED_ID = 'ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f'
SCHEDULE_ID = '6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a'
FIELDS = ('v_mV', 'g_mV', 'refractory_until', 'pending', 'pending_event_counts')
STAGES = ('encode', 'advance', 'readout', 'decoder', 'environment', 'total')


class Stop(RuntimeError):
    def __init__(self, classification, detail):
        super().__init__(detail)
        self.classification = classification


def require(condition, classification, detail):
    if not condition:
        raise Stop(classification, detail)


def dump(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def array_digest(array):
    value = np.asarray(array)
    canonical = np.ascontiguousarray(value.astype(value.dtype.newbyteorder('<'), copy=False))
    digest = hashlib.sha256(json.dumps([canonical.dtype.str, canonical.shape]).encode())
    digest.update(memoryview(canonical).cast('B'))
    return digest.hexdigest()


def state_evidence(state):
    return {'timestep': state.timestep, 'arrays': {name: array_digest(getattr(state, name)) for name in FIELDS}}


def statistics(values):
    return dict(zip(('min', 'p50', 'p95', 'max', 'mean'),
                    map(float, (np.min(values), np.percentile(values, 50, method='linear'),
                                np.percentile(values, 95, method='linear'), np.max(values), np.mean(values)))))


def distributions(records):
    measured = [row for row in records if not row['warmup']]
    return {group: {stage: statistics([row['seconds'][stage] for row in measured if group == 'pooled' or row['sequence'] == group])
                    for stage in STAGES}
            for group in ('A', 'B', 'pooled')
            if any(group == 'pooled' or row['sequence'] == group for row in measured)}


class WindowsMemory:
    """Platform-native process counters; no optional instrumentation dependency."""
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage',
            'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage',
            'PagefileUsage', 'PeakPagefileUsage', 'PrivateUsage')]

    class Status(ctypes.Structure):
        _fields_ = [('dwLength', wintypes.DWORD), ('dwMemoryLoad', wintypes.DWORD)] + [
            (name, ctypes.c_ulonglong) for name in ('ullTotalPhys', 'ullAvailPhys', 'ullTotalPageFile',
            'ullAvailPageFile', 'ullTotalVirtual', 'ullAvailVirtual', 'ullAvailExtendedVirtual')]

    def __init__(self, pid):
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.psapi = ctypes.WinDLL('psapi', use_last_error=True)
        self.kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        self.kernel.OpenProcess.restype = wintypes.HANDLE
        self.kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        self.psapi.GetProcessMemoryInfo.argtypes = (wintypes.HANDLE, ctypes.POINTER(self.Counters), wintypes.DWORD)
        self.kernel.GlobalMemoryStatusEx.argtypes = (ctypes.POINTER(self.Status),)
        self.kernel.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
        self.pid = pid
        self.handle = self.kernel.OpenProcess(0x1000 | 0x10 | 0x1, False, pid)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())

    def snapshot(self):
        counters = self.Counters()
        counters.cb = ctypes.sizeof(counters)
        if not self.psapi.GetProcessMemoryInfo(self.handle, ctypes.byref(counters), counters.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return {'working_set': counters.WorkingSetSize, 'peak_working_set': counters.PeakWorkingSetSize,
                'private_bytes': counters.PrivateUsage, 'commit_bytes': counters.PagefileUsage,
                'peak_commit_bytes': counters.PeakPagefileUsage}

    def available(self):
        status = self.Status()
        status.dwLength = ctypes.sizeof(status)
        if not self.kernel.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise ctypes.WinError(ctypes.get_last_error())
        return status.ullAvailPhys

    def close(self):
        self.kernel.CloseHandle(self.handle)

    def terminate(self):
        if not self.kernel.TerminateProcess(self.handle, 1):
            raise ctypes.WinError(ctypes.get_last_error())


def bind_worker_monitor(message, monitor, factory=WindowsMemory):
    """Bind to the self-reported worker PID, never assume launcher PID is Python."""
    if message['pid'] != monitor.pid:
        replacement = factory(message['pid'])
        monitor.close()
        return replacement
    return monitor


def guard(memory, phase, phase_elapsed, total_elapsed):
    require(max(memory['working_set'], memory['private_bytes']) <= MEMORY_CAP, 'A013-MEMORY-LIMIT', 'process exceeds 8 GiB')
    require(total_elapsed <= TOTAL_CAP, 'A013-TOTAL-LIMIT', 'worker exceeds 1500 seconds')
    if phase == 'prepare':
        require(phase_elapsed <= PREPARATION_CAP, 'A013-PREPARATION-LIMIT', 'prepare exceeds 600 seconds')
    if phase == 'advance':
        require(phase_elapsed <= ADVANCE_CAP, 'A013-ADVANCE-LIMIT', 'advance exceeds 30 seconds')


def freeze_schedule(ids):
    from malecns_sim.dynamics.stimulus import PoissonStimulus
    schedule = PoissonStimulus(tuple(ids), rate_hz=100, seed=1555062870).generate(240, DT_MS, 0.275)
    events = tuple((item.neuron_id, tuple(round(t / DT_MS) for t in item.spike_times_ms)) for item in schedule.schedules)
    windows = tuple(tuple((neuron, tuple(step - k * 200 for step in steps if k * 200 <= step < (k + 1) * 200))
                          for neuron, steps in events) for k in range(STEPS))
    return schedule, windows


def pack(window, ids):
    from malecns_sim.dynamics.stimulus import ExplicitStimulus, SpikeSchedule
    return ExplicitStimulus(tuple(SpikeSchedule(neuron, tuple(step * DT_MS for step in steps))
                                  for neuron, steps in window), 68.75, tuple(ids))


def prepare_once(engine, files, evidence, checkpoint=lambda: None):
    require(evidence['preparations'] < MAX_PREPARATIONS, 'A013-RUNTIME-CONTRACT-GAP', 'preparation budget exceeded')
    evidence['preparations'] += 1
    checkpoint()
    return engine.prepare(files, 'cpu_reference')


def pending_evidence(state, totals, expected_n):
    counts = state.pending_event_counts
    require(state.pending.shape == counts.shape == (19, expected_n), 'A013-PENDING-STATE-DIVERGENCE', 'pending shape changed')
    result = {'shape': list(counts.shape), 'ring_index': state.timestep % 19,
              'nonzero_weights': int(np.count_nonzero(state.pending)), 'nonzero_counts': int(np.count_nonzero(counts)),
              'occupied_slots': int(np.count_nonzero(np.any(counts != 0, axis=1))),
              'sum': int(counts.sum(dtype=np.int64)), 'max': int(counts.max()), 'min': int(counts.min())}
    require(result['min'] >= 0 and result['max'] <= 1000000 and result['sum'] <= 100000000,
            'A013-PENDING-STATE-DIVERGENCE', 'pending bounds violated')
    totals.append(result['sum'])
    require(not (len(totals) >= 4 and totals[-1] > 1000000 and
                 all(b >= 2 * a for a, b in zip(totals[-4:-1], totals[-3:]))),
            'A013-PENDING-STATE-DIVERGENCE', 'three consecutive pending doublings')
    return result


def compare(expected, actual, interval):
    for key in expected:
        if expected[key] != actual[key]:
            if isinstance(expected[key], dict):
                for name in expected[key]:
                    if expected[key][name] != actual[key][name]:
                        raise Stop('A013-DETERMINISM-FAIL', f'interval {interval}: {key}.{name}')
            raise Stop('A013-DETERMINISM-FAIL', f'interval {interval}: {key}')


def run_sequences(runtime, windows, ids, evidence, checkpoint, phase, memory, readout_ids=(10331, 16949)):
    require(len(windows) == STEPS, 'A013-RUNTIME-CONTRACT-GAP', 'exactly twelve frozen windows required')
    window_digests = [pack(window, ids).fingerprint for window in windows]
    positions = np.searchsorted(runtime.projection.neuron_ids, readout_ids)
    require(all(int(runtime.projection.neuron_ids[pos]) == neuron for pos, neuron in zip(positions, readout_ids)),
            'A013-RUNTIME-CONTRACT-GAP', 'missing readout')
    reference = []
    for sequence in ('A', 'B'):
        phase('initial_state')
        state = runtime.initial_state()
        initial = state_evidence(state)
        if sequence == 'A':
            evidence['initial_state'] = initial
        else:
            require(initial == evidence['initial_state'], 'A013-REPLAY-STATE-CONTRACT-GAP', 'initial states differ')
        evidence.setdefault('initial_memory', {})[sequence] = memory()
        sizes = {name: int(getattr(state, name).nbytes) for name in FIELDS}
        evidence['state_array_bytes'] = sizes
        x, y = 0.5, 0.5
        totals = []
        for index, window in enumerate(windows):
            phase('advance', sequence=sequence, interval=index + 1)
            evidence['advances_started'] += 1
            require(evidence['advances_started'] <= MAX_ADVANCES, 'A013-RUNTIME-CONTRACT-GAP', 'advance budget exceeded')
            # All heavy verification and evidence persistence occur after these timers.
            t0 = time.perf_counter_ns()
            stimulus = pack(window, ids)
            t1 = time.perf_counter_ns()
            result = runtime.advance(state, duration_ms=INTERVAL_MS, stimulus=stimulus)
            t2 = time.perf_counter_ns()
            counts = tuple(int(result.spike_counts[pos]) for pos in positions)
            t3 = time.perf_counter_ns()
            speed = 0.25 if sum(counts) >= 1 else 0.0
            t4 = time.perf_counter_ns()
            x = min(1.0, max(0.0, x + speed * 0.020))
            t5 = time.perf_counter_ns()
            phase('verification')
            seconds = dict(zip(STAGES, [(b - a) / 1e9 for a, b in ((t0,t1),(t1,t2),(t2,t3),(t3,t4),(t4,t5),(t0,t5))]))
            row = {'sequence': sequence, 'interval': index + 1, 'warmup': index < WARMUPS,
                   'seconds': seconds, 'memory': memory(), 'readout_counts': counts}
            evidence['steps'].append(row)
            evidence['advances_completed'] += 1
            require(seconds['advance'] <= ADVANCE_CAP, 'A013-ADVANCE-LIMIT', 'completed advance exceeds limit')
            for name in FIELDS:
                require(np.isfinite(getattr(state, name)).all(), 'A013-NONFINITE-STATE', name)
            for name in ('spike_counts',):
                require(np.isfinite(getattr(result, name)).all(), 'A013-NONFINITE-STATE', name)
            require(np.isfinite((x, y, speed, *counts)).all(), 'A013-NONFINITE-STATE', 'readout/bookkeeping')
            require(state.timestep == (index + 1) * 200, 'A013-RUNTIME-CONTRACT-GAP', 'wrong timestep')
            require(result.spike_neuron_ids.size <= 1000000, 'A013-OUTPUT-LIMIT', 'whole-network spike output')
            row['pending'] = pending_evidence(state, totals, runtime.projection.neuron_ids.size)
            row['output_array_bytes'] = {name: int(getattr(result, name).nbytes) for name in
                                        ('spike_neuron_ids', 'spike_timesteps', 'spike_counts')}
            row['whole_network_spikes'] = int(result.spike_neuron_ids.size)
            replay = {**state_evidence(state), 'input': stimulus.fingerprint,
                      'output': {name: array_digest(getattr(result, name)) for name in row['output_array_bytes']},
                      'readout': counts, 'dummy': (x, y, speed), 'pending': row['pending']}
            row['replay'] = replay
            require(replay['input'] == window_digests[index], 'A013-DETERMINISM-FAIL', 'frozen input changed')
            row['queued_events'] = int(result.queued_synaptic_event_count)
            row['delivered_events'] = int(result.delivered_synaptic_event_count)
            previous_pending = totals[-2] if len(totals) >= 2 else 0
            require(previous_pending + row['queued_events'] - row['delivered_events'] == row['pending']['sum'],
                    'A013-PENDING-STATE-DIVERGENCE', 'pending delivery accounting does not conserve events')
            if sequence == 'A':
                reference.append(replay)
            else:
                compare(reference[index], replay, index + 1)
            del result
            row['instrumentation_seconds'] = (time.perf_counter_ns() - t5) / 1e9
            retained = len(json.dumps(evidence, allow_nan=False).encode())
            require(retained <= 1024**2, 'A013-RETENTION-LIMIT', 'retained summaries exceed 1 MiB')
            evidence['retained_json_bytes'] = retained
            checkpoint()
        del state
    evidence['replay'] = 'exact pass'
    evidence['distributions_seconds'] = distributions(evidence['steps'])


def worker(output):
    import os
    from malecns_sim.application.workbench import DatasetCatalog, SOURCE_FILES
    from malecns_sim.application.service import ProductionEngine, _file_digest
    from malecns_sim.application.preparation import REFERENCE_CONFIG
    from malecns_sim.dynamics.lif import PreparedRuntime
    evidence = {'classification': 'RUNNING', 'backend': 'cpu_reference', 'preparations': 0,
                'advances_started': 0, 'advances_completed': 0, 'steps': [], 'numpy_version': np.__version__}
    monitor = WindowsMemory(os.getpid())
    checkpoint = lambda: dump(output, evidence)
    def phase(name, **details):
        print(json.dumps({'phase': name, 'at': time.perf_counter(), 'pid': os.getpid(), **details}), flush=True)
    try:
        phase('preflight')
        evidence['memory_pre_load'] = monitor.snapshot()
        evidence['available_physical_bytes'] = monitor.available()
        require(monitor.available() >= AVAILABLE_MIN, 'A013-AVAILABLE-MEMORY-BLOCKED', 'less than 12 GiB available')
        catalog = DatasetCatalog.local()
        require(catalog.available(), 'A013-DATASET-PROVENANCE-BLOCKED', 'local sources missing')
        paths = (catalog.files.annotation, catalog.files.neurotransmitter, catalog.files.weights)
        evidence['sources'] = [{'path': str(path.resolve()), 'sha256': _file_digest(path), 'bytes': path.stat().st_size}
                               for path in paths]
        require(all(row['sha256'] == sha for row, (_, sha) in zip(evidence['sources'], SOURCE_FILES)),
                'A013-DATASET-PROVENANCE-BLOCKED', 'source hash mismatch')
        root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
        fixture = json.loads((root / 'tests/fixtures/application-a003r-reference-spec.json').read_text())
        evidence['dataset'] = fixture['dataset']
        evidence['preparation_config'] = REFERENCE_CONFIG.to_dict()
        evidence['preparation_config_digest'] = REFERENCE_CONFIG.digest
        evidence['git_head'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        ids = fixture['stimulus']['member_ids']
        identities = catalog.populations()
        require(tuple(sorted(map(int, identities.sugar_left.candidate_body_ids))) == tuple(ids),
                'A013-DATASET-PROVENANCE-BLOCKED', 'LEFT membership mismatch')
        schedule, windows = freeze_schedule(ids)
        require(schedule.fingerprint == SCHEDULE_ID, 'A013-RUNTIME-CONTRACT-GAP', 'frozen schedule realization mismatch')
        evidence['schedule'] = {'digest': schedule.fingerprint, 'window_digests': [pack(w, ids).fingerprint for w in windows],
                                'seed': 1555062870, 'event_count': sum(len(s.spike_times_ms) for s in schedule.schedules),
                                'integer_event_payload_bytes': sum(len(s.spike_times_ms) for s in schedule.schedules) * 16,
                                'member_ids': ids, 'duration_ms': 240, 'left_hz': 100, 'right_hz': 0,
                                'weight_mV': 68.75, 'biological_meaning': False}
        require(REFERENCE_CONFIG.parameters.fingerprint == fixture['model']['fingerprint'],
                'A013-RUNTIME-CONTRACT-GAP', 'model identity')
        evidence['memory_pre_preparation'] = monitor.snapshot()
        evidence['preparation_start_utc'] = datetime.now(timezone.utc).isoformat()
        checkpoint()
        phase('prepare')
        started = time.perf_counter()
        prepared = prepare_once(ProductionEngine(), catalog.files, evidence, checkpoint)
        evidence['preparation_wall_seconds'] = time.perf_counter() - started
        phase('post_prepare')
        evidence['preparation_end_utc'] = datetime.now(timezone.utc).isoformat()
        evidence['memory_post_preparation'] = monitor.snapshot()
        evidence['memory_post_load'] = None
        evidence['graph_loading_seconds'] = prepared.graph_loading_seconds
        evidence['prepared'] = {'neurons': int(prepared.projection.neuron_ids.size),
                                'edges': int(prepared.projection.effective_weights_mV.size), 'fingerprint': prepared.fingerprint,
                                'graph_array_bytes': prepared.memory_bytes}
        checkpoint()
        require(evidence['preparation_wall_seconds'] <= PREPARATION_CAP, 'A013-PREPARATION-LIMIT', 'completed preparation exceeds limit')
        require(prepared.fingerprint == PREPARED_ID and evidence['prepared']['neurons'] == 166700 and
                evidence['prepared']['edges'] == 24904953 and
                prepared.projection.unsigned_graph_fingerprint == fixture['dataset']['projection_fingerprint'],
                'A013-DATASET-PROVENANCE-BLOCKED', 'prepared graph identity mismatch')
        runtime = PreparedRuntime(prepared.projection, dt_ms=DT_MS)
        run_sequences(runtime, windows, ids, evidence, checkpoint, phase, monitor.snapshot)
        evidence['classification'] = 'A13-BENCHMARK-COMPLETE'
    except Stop as exc:
        evidence['classification'], evidence['stop_detail'] = exc.classification, str(exc)
    except Exception as exc:
        evidence['classification'], evidence['stop_detail'] = 'A013-RUNTIME-CONTRACT-GAP', repr(exc)
    finally:
        evidence['memory_final'] = monitor.snapshot()
        checkpoint()
        monitor.close()
        phase('finished')
    return 0 if evidence['classification'] == 'A13-BENCHMARK-COMPLETE' else 1


def supervise(output):
    require(not output.exists() and not output.with_suffix('.worker.json').exists(),
            'A013-RUNTIME-CONTRACT-GAP', 'refusing an existing evidence path; no automatic retry')
    import importlib.util
    spec = importlib.util.spec_from_file_location('a014_watchdog', Path(__file__).with_name('investigate_application_a014.py'))
    watchdog = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(watchdog)
    output.parent.mkdir(parents=True, exist_ok=True)
    child_path = output.with_suffix('.worker.json')
    started = time.perf_counter()
    job = watchdog.ProcessJob([sys.executable, str(Path(__file__).resolve()), '--confirm-real-data-benchmark',
                      '--worker', '--output', str(child_path)])
    process = job.process
    messages = queue.Queue()
    def reader():
        for line in process.stdout:
            messages.put(line)
    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    phase, phase_at = 'startup', started
    peaks, samples, phase_peaks = {}, 0, {}
    stop = None
    logs = []
    events = []
    try:
        while job.pids():
            while not messages.empty():
                line = messages.get_nowait()
                try:
                    message = json.loads(line)
                    require(message['pid'] in job.pids(), 'A013-RUNTIME-CONTRACT-GAP',
                            'reported worker is outside contained process tree')
                    phase, phase_at = message['phase'], message['at']
                    events.append(message)
                    print(line.strip(), flush=True)
                except (ValueError, KeyError):
                    logs.append(line[:1000])
            try:
                tree_snapshot = job.snapshot()
                snapshot = {key: tree_snapshot[key] for key in ('working_set', 'private_bytes')}
            except OSError:
                if not job.pids():
                    break
                raise
            samples += 1
            for key, value in snapshot.items():
                peaks[key] = max(peaks.get(key, 0), value)
                phase_peaks.setdefault(phase, {})[key] = max(phase_peaks.get(phase, {}).get(key, 0), value)
            now = time.perf_counter()
            guard(snapshot, phase, now - phase_at, now - started)
            time.sleep(0.1)
    except Stop as exc:
        stop = exc
    except Exception as exc:
        stop = Stop('A013-RUNTIME-CONTRACT-GAP', f'watchdog failure: {exc!r}')
    finally:
        job.close()
    evidence = json.loads(child_path.read_text()) if child_path.exists() else {}
    if stop:
        evidence.update(classification=stop.classification, stop_detail=str(stop))
        attempted = [event for event in events if event['phase'] == 'advance']
        evidence['advances_started'] = max(evidence.get('advances_started', 0), len(attempted))
    elif process.returncode != 0 and evidence.get('classification') in (None, 'RUNNING', 'A13-BENCHMARK-COMPLETE'):
        evidence.update(classification='A013-RUNTIME-CONTRACT-GAP', stop_detail=f'worker exit {process.returncode}')
    evidence['watchdog'] = {'sample_interval_seconds': 0.1, 'samples': samples, 'peaks': peaks,
                            'memory_scope': 'aggregate contained process tree; working set and private bytes',
                            'phase_peaks': phase_peaks, 'wall_seconds': time.perf_counter() - started,
                            'worker_exit': process.returncode, 'logs': logs[-10:], 'phase_events': events}
    dump(output, evidence)
    print(evidence['classification'], flush=True)
    return 0 if evidence['classification'] == 'A13-BENCHMARK-COMPLETE' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--confirm-real-data-benchmark', action='store_true', required=True)
    parser.add_argument('--backend', choices=['cpu_reference'], default='cpu_reference')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    return worker(args.output) if args.worker else supervise(args.output)


if __name__ == '__main__':
    raise SystemExit(main())
