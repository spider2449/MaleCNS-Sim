"""Frozen, guarded synthetic resumable CPU/GPU public-boundary benchmark."""
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
from dataclasses import asdict, fields
import gc
import hashlib
import json
import platform
import queue
import tempfile
import threading
import time
import numpy as np

from malecns_sim.dynamics.lif import EffectiveSignedProjection, PreparedRuntime, REFERENCE_LIF_PARAMETERS
from malecns_sim.dynamics.stimulus import ExplicitStimulus, PoissonStimulus, SpikeSchedule

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'docs/plans/a019v-synthetic-cpu-gpu-performance-evidence.json'
CASES = (('S1', 128, 1024, ('CPU', 'GPU')),
         ('S2', 4096, 32768, ('GPU', 'CPU')),
         ('S3', 32768, 262144, ('CPU', 'GPU')),
         ('S4', 127400, 14687178, ('GPU', 'CPU')))
STATE_FIELDS = ('v_mV', 'g_mV', 'refractory_until', 'pending', 'pending_event_counts')
TOL = 2e-13
START_SHA = '2d20bbb4d707e5343e24c382b491e9ec8ef7df20'


def digest_arrays(arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(str((a.shape, str(a.dtype))).encode())
        h.update(memoryview(np.ascontiguousarray(a)).cast('B'))
    return h.hexdigest()


def fixture(n, e):
    """Balanced deterministic CSR; shared immutable arrays avoid host copies."""
    degree = np.full(n, e // n, dtype=np.int64)
    degree[:e % n] += 1
    ptr = np.concatenate((np.array([0], dtype=np.int64), np.cumsum(degree)))
    sources = np.repeat(np.arange(n, dtype=np.int64), degree)
    local = np.arange(e, dtype=np.int64) - ptr[sources]
    targets = (sources * 17 + local * 97 + 1) % n
    weights = np.asarray((0.275, -0.1375, 0.06875, 0.1375))[local % 4]
    ids = np.arange(1, n + 1, dtype=np.int64)
    identity = digest_arrays((ids, ptr, targets, weights))
    for array in (ids, sources, targets, weights, ptr):
        array.flags.writeable = False
    return EffectiveSignedProjection(ids, sources, targets, weights, e, 0, 0,
                                    0.275, 'synthetic', 'synthetic', identity,
                                    identity, identity, ptr, targets, weights)


def schedule(large):
    ids = tuple(range(1, 43 if large else 9))
    if large:
        full = PoissonStimulus(ids, rate_hz=100, seed=1555062870).generate(240, 0.1, 0.275)
    else:
        full = ExplicitStimulus(tuple(SpikeSchedule(ids[k % 8], (float(k * 40 * 0.1),))
                                      for k in range(60)), 68.75, ids)
    events = tuple((s.neuron_id, tuple(round(t / 0.1) for t in s.spike_times_ms))
                   for s in full.schedules)
    windows = tuple(tuple((neuron, tuple(step - k * 200 for step in steps
                                         if k * 200 <= step < (k + 1) * 200))
                          for neuron, steps in events) for k in range(12))
    return full, windows, ids


def pack(window, ids):
    return ExplicitStimulus(tuple(SpikeSchedule(neuron, tuple(step * 0.1 for step in steps))
                                  for neuron, steps in window), 68.75, ids)


def statistics(values):
    a = np.asarray(values, dtype=np.float64)
    assert a.shape == (20,) and np.all(np.isfinite(a)) and np.all(a > 0)
    return dict(min=float(a.min()), median=float(np.median(a)), mean=float(a.mean()),
                max=float(a.max()), p95=float(np.percentile(a, 95, method='linear')),
                population_std=float(a.std()), CV=float(a.std() / a.mean()),
                state_A_mean=float(a[:10].mean()), state_B_mean=float(a[10:].mean()),
                raw_seconds=a.tolist())


def compare_arrays(left, right):
    assert left.shape == right.shape and left.dtype == right.dtype, 'shape/dtype mismatch'
    if left.dtype.kind == 'f':
        finite = bool(np.all(np.isfinite(left)) and np.all(np.isfinite(right)))
        maximum = float(np.max(np.abs(left - right), initial=0))
        passed = finite and bool(np.allclose(left, right, rtol=TOL, atol=TOL))
        return dict(pass_eq_b=passed, max_abs=maximum, discrete_mismatches=0)
    count = int(np.count_nonzero(left != right))
    return dict(pass_eq_b=count == 0, discrete_mismatches=count)


def capture(state, result, cp=None):
    if cp is not None:
        state._backing.stream.synchronize()
    out = {name: (cp.asnumpy(getattr(state, name)) if cp is not None
                  else getattr(state, name)) for name in STATE_FIELDS}
    out['timestep'] = np.asarray(state.timestep, dtype=np.int64)
    if result is not None:
        for field in fields(result):
            value = getattr(result, field.name)
            out['result_' + field.name] = (value if isinstance(value, np.ndarray)
                                          else np.asarray(json.dumps(value, sort_keys=True)))
    return out


def memory(cp, label):
    free, total = cp.cuda.runtime.memGetInfo()
    pool = cp.get_default_memory_pool()
    return dict(point=label, pool_used=int(pool.used_bytes()), pool_reserved=int(pool.total_bytes()),
                device_free=int(free), device_total=int(total))


def emit(phase, **details):
    print(json.dumps(dict(phase=phase, at=time.perf_counter(), **details)), flush=True)


def write(evidence):
    TARGET.write_text(json.dumps(evidence, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def backend_run(backend, p, windows, ids, temporary, reference, cp):
    from malecns_sim.dynamics.cuda import GPUPreparedRuntime
    gpu = backend == 'GPU'
    record = dict(calls=[], initial_state_seconds=[], memory=[], comparisons=[], cleanup=[])
    if gpu:
        cp.get_default_memory_pool().free_all_blocks()
        record['memory'].append(memory(cp, 'before_runtime'))
    emit('prepare', backend=backend)
    start = time.perf_counter()
    runtime = GPUPreparedRuntime(p) if gpu else PreparedRuntime(p)
    record['runtime_seconds'] = time.perf_counter() - start
    if gpu:
        record['memory'].append(memory(cp, 'after_static_upload'))
    runtime_id = id(runtime)
    graph_pointers = None
    try:
        for sequence in ('A', 'B'):
            emit('prepare', backend=backend, state=sequence)
            start = time.perf_counter()
            state = runtime.initial_state()
            record['initial_state_seconds'].append(time.perf_counter() - start)
            pointers = tuple((getattr(state, f).data.ptr if gpu else
                              getattr(state, f).__array_interface__['data'][0]) for f in STATE_FIELDS)
            if gpu:
                graph = state._backing.graph
                current = tuple(a.data.ptr for a in (graph.indptr, graph.indices, graph.weights_mV,
                                state._backing.incoming_offsets, state._backing.incoming_sources,
                                state._backing.incoming_ordinals))
                if graph_pointers is None:
                    graph_pointers = current
                assert graph_pointers == current
                del graph
                record['memory'].append(memory(cp, sequence + '_initial_state'))
            try:
                for k in range(-1, 12):
                    result = None
                    if k >= 0:
                        emit('advance', backend=backend, state=sequence, chunk=k)
                        t0 = time.perf_counter()
                        stimulus = pack(windows[k], ids)
                        t1 = time.perf_counter()
                        result = runtime.advance(state, duration_ms=20, stimulus=stimulus)
                        t2 = time.perf_counter()
                        counts = tuple(int(result.spike_counts[pos]) for pos in (p.neuron_ids.size - 2,
                                                                                p.neuron_ids.size - 1))
                        speed = (counts[0] - counts[1]) / 20.0
                        bookkeeping = (speed * 0.02, speed * 0.02, state.timestep)
                        assert np.isfinite((*counts, *bookkeeping)).all()
                        t3 = time.perf_counter()
                        record['calls'].append(dict(state=sequence, chunk=k, warmup=k < 2,
                            T5=t2 - t1, T6=t3 - t0, packing=t1 - t0, readout_bookkeeping=t3 - t2,
                            event_digest=stimulus.fingerprint, readouts=counts))
                    emit('verify', backend=backend, state=sequence, chunk=k)
                    assert id(runtime) == runtime_id and state.timestep == (k + 1) * 200
                    assert pointers == tuple((getattr(state, f).data.ptr if gpu else
                               getattr(state, f).__array_interface__['data'][0]) for f in STATE_FIELDS)
                    if gpu:
                        record['memory'].append(memory(cp, f'{sequence}_chunk_{k}_before_snapshot'))
                    observed = capture(state, result, cp if gpu else None)
                    path = Path(temporary) / f'{sequence}_{k}.npz'
                    if reference:
                        np.savez(path, **observed)
                    else:
                        with np.load(path, allow_pickle=False) as saved:
                            assert set(saved.files) == set(observed)
                            checks = {name: compare_arrays(saved[name], value) for name, value in observed.items()}
                        record['comparisons'].append(dict(state=sequence, chunk=k, fields=checks,
                            pass_eq_b=all(row['pass_eq_b'] for row in checks.values())))
                    del observed, result
            finally:
                if gpu:
                    state.close()
                del state
                gc.collect()
                record['cleanup'].append(sequence + ' released before next state/runtime')
                if gpu:
                    record['memory'].append(memory(cp, sequence + '_released'))
    finally:
        if gpu:
            runtime.close()
        del runtime
        gc.collect()
        if gpu:
            record['memory'].append(memory(cp, 'runtime_closed'))
            cp.get_default_memory_pool().free_all_blocks()
            record['memory'].append(memory(cp, 'pool_reclaimed'))
    for boundary in ('T5', 'T6'):
        record[boundary] = statistics([row[boundary] for row in record['calls'] if not row['warmup']])
    record['wrapper_mean_seconds'] = record['T6']['mean'] - record['T5']['mean']
    record['stable_runtime_state_graph_pointers'] = True
    return record


def worker():
    evidence = dict(schema='application-a019v-synthetic-performance-v1', authorization='授權 A019V',
        starting_sha=START_SHA, harness_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        parameters=asdict(REFERENCE_LIF_PARAMETERS), tolerance=dict(rtol=TOL, atol=TOL),
        cases=[], classification='A019V-D', benefit='G5',
        counters=dict(full_real_preparations=0, real_advances=0, A019D_A019L_reruns=0,
            registered_payload_reads={name: 0 for name in ('annotation', 'neurotransmitter', 'connectivity',
                'metadata', 'mapping', 'provenance', 'other')}, Arena=0, interventions=0, downloads=0, archive_writes=0),
        accounting_qualifier='Fail-closed guarded-scope accounting; not independent native-byte telemetry.',
        nonclaims=['full-real speedup', 'full-real realtime', 'biological realtime', 'exact A019L speedup',
                   'scientific/behavioral implications', 'true native process/device VRAM peak'],
        timing_policy='T5 public synchronized advance; T6 packing/advance/two count readouts/bookkeeping; snapshots outside timers',
        percentile_method='linear', cache_policy='Existing on-disk CuPy cache retained; no cache clearing or tuning')
    write(evidence)
    try:
        emit('prepare', operation='GPU import/context preflight')
        start = time.perf_counter()
        import cupy as cp
        cp.cuda.runtime.free(0)
        device = cp.cuda.runtime.getDeviceProperties(0)
        evidence['preflight_seconds'] = time.perf_counter() - start
        evidence['environment'] = dict(python=sys.version, platform=platform.platform(),
            cpu=platform.processor(), numpy=np.__version__, cupy=cp.__version__,
            CUDA_runtime=cp.cuda.runtime.runtimeGetVersion(), CUDA_driver=cp.cuda.runtime.driverGetVersion(),
            GPU_name=device['name'].decode(), GPU_total_bytes=int(device['totalGlobalMem']),
            compute_capability=[device['major'], device['minor']],
            cpu_count=os.cpu_count(), threading_env={key: os.environ.get(key) for key in
                ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'CUPY_CACHE_DIR')})
        for name, n, e, order in CASES:
            emit('prepare', case=name, operation='synthetic fixture')
            start = time.perf_counter()
            p = fixture(n, e)
            full, windows, ids = schedule(name == 'S4')
            case = dict(name=name, neurons=n, edges=e, order=order, T0=time.perf_counter() - start,
                fixture_digest=p.fingerprint, schedule_digest=full.fingerprint,
                event_count=sum(len(s.spike_times_ms) for s in full.schedules), source_ids=ids,
                windows=[dict(event_count=sum(len(steps) for _, steps in w), digest=pack(w, ids).fingerprint)
                         for w in windows], topology='balanced degree; target=(source*17+local*97+1)%N',
                weights=[0.275, -0.1375, 0.06875, 0.1375], backends={})
            evidence['cases'].append(case)
            write(evidence)
            with tempfile.TemporaryDirectory(prefix='a019v-synthetic-') as temporary:
                for index, backend in enumerate(order):
                    case['backends'][backend] = backend_run(backend, p, windows, ids, temporary, index == 0, cp)
                    write(evidence)
            checks = case['backends'][order[1]]['comparisons']
            case['EQ_B'] = all(row['pass_eq_b'] for row in checks)
            if not case['EQ_B']:
                case['performance'] = 'PERFORMANCE-INVALID'
                evidence.update(classification='A019V-E', benefit='G5',
                    next_task='One bounded correctness diagnostic on the failing synthetic fixture')
                write(evidence)
                return
            cpu, gpu = (case['backends'][backend] for backend in ('CPU', 'GPU'))
            case['speedup'] = {}
            for boundary in ('T5', 'T6'):
                ratios = np.asarray(cpu[boundary]['raw_seconds']) / np.asarray(gpu[boundary]['raw_seconds'])
                case['speedup'][boundary] = dict(mean_ratio=cpu[boundary]['mean'] / gpu[boundary]['mean'],
                    median_ratio=cpu[boundary]['median'] / gpu[boundary]['median'],
                    paired_gpu_faster=int((ratios > 1).sum()), paired_cpu_faster=int((ratios < 1).sum()),
                    paired_equal=int((ratios == 1).sum()), paired_mean=float(ratios.mean()),
                    paired_median=float(np.median(ratios)), paired_ratios=ratios.tolist())
            case['GPU_P'] = ('SYNTHETIC GPU-P1' if gpu['T6']['max'] <= 0.020 else
                             'SYNTHETIC GPU-P2' if gpu['T6']['max'] < 30 else 'SYNTHETIC GPU-P3')
            samples = gpu['memory']
            case['memory_summary'] = dict(max_observed_pool_used=max(s['pool_used'] for s in samples),
                max_observed_pool_reserved=max(s['pool_reserved'] for s in samples),
                minimum_observed_device_free=min(s['device_free'] for s in samples),
                true_peak_observed=False, structural_graph_bytes=12*(n+1)+24*e,
                structural_state_bytes=24*n+12*19*n, structural_named_call_bytes=26*n+16)
            write(evidence)
            del p, full
            gc.collect()
        evidence['measurement_complete'] = True
        evidence['next_task'] = 'Evidence-only disposition after reviewing the complete frozen matrix'
        write(evidence)
    except Exception as exc:
        evidence['blocker'] = repr(exc)
        evidence['next_task'] = 'One bounded correction of the recorded benchmark blocker'
        write(evidence)
        raise
    finally:
        emit('done')


def supervise():
    """Reuse certified Job containment; enforce frozen time/host caps."""
    from investigate_application_a014 import ProcessJob
    command = guard.guarded_command([sys.executable, str(Path(__file__).resolve()), '--worker'])
    job = ProcessJob(command)
    messages = queue.Queue()
    def consume():
        for line in job.process.stdout:
            messages.put(line)
    reader = threading.Thread(target=consume, daemon=True)
    reader.start()
    start = phase_start = time.perf_counter()
    phase, outcome, samples = 'prepare', 'NORMAL_EXIT', []
    try:
        while job.pids():
            while not messages.empty():
                line = messages.get_nowait()
                print(line, end='', flush=True)
                try:
                    row = json.loads(line)
                    phase, phase_start = row['phase'], row['at']
                except (ValueError, KeyError):
                    pass
            sample = job.snapshot()
            samples.append(sample)
            now = time.perf_counter()
            if max(sample['private_bytes'], sample['working_set']) > 8 * 1024**3:
                outcome = 'HOST_MEMORY_LIMIT'
                break
            if now - start > 1800 or now - phase_start > (30 if phase == 'advance' else 180):
                outcome = 'TIME_LIMIT_' + phase
                break
            time.sleep(0.1)
    finally:
        job.close()
        reader.join(timeout=5)
        while not messages.empty():
            print(messages.get_nowait(), end='', flush=True)
    evidence = json.loads(TARGET.read_text(encoding='utf-8'))
    evidence['supervision'] = dict(outcome=outcome, worker_exit_code=job.process.returncode,
        orphan_pids=[], sampled_host_private_peak=max(s['private_bytes'] for s in samples),
        sampled_host_working_set_peak=max(s['working_set'] for s in samples),
        samples=len(samples), wall_seconds=time.perf_counter()-start, period_seconds=0.1,
        bounds=dict(advance_seconds=30, construction_seconds=180, total_seconds=1800, host_bytes=8*1024**3))
    write(evidence)
    if outcome != 'NORMAL_EXIT' or job.process.returncode != 0:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    worker() if args.worker else supervise()
