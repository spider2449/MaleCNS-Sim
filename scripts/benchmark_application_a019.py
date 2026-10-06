"""Forward A019 CPU harness; CLI accepts generated synthetic fixtures only."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import gc
import hashlib
import json
import os
from pathlib import Path
import queue
import sys
import tempfile
import threading
import time
import weakref

if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent / 'a019c_firewall'))
    if os.environ.get('MALECNS_A019C_R2_FIREWALL') != '1':
        print('FIREWALL_REQUIRED_BUT_NOT_ACTIVE', file=sys.stderr, flush=True)
        raise SystemExit(78)
    import validation_firewall as startup_guard
    startup_guard.install()
    if not startup_guard.ACTIVE:
        raise SystemExit(78)
    if '--firewall-bootstrap-probe' in sys.argv:
        print('A019_WORKER_GUARDED_BEFORE_WORKLOAD', flush=True)
        raise SystemExit(0)

import numpy as np

import benchmark_application_a013 as historical
from certify_application_a018ur import bounded_route, BoundedFallback, BATCH_ROWS, BLOCK_SIZE
from investigate_application_a014 import ProcessJob, synthetic_files
from preparation_identity_contract import expected_identity, observe_identity, compare_identity
from malecns_sim.application.preparation import REFERENCE_CONFIG
from malecns_sim.application.service import DatasetFiles, ProductionEngine
from malecns_sim.dynamics.lif import PreparedRuntime

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / 'docs/plans/2026-10-05-application-a019a-benchmark-contract.json'
SYNTHETIC_IDENTITY_PATH = ROOT / 'tests/fixtures/application-a019c-preparation-identity.json'
Stop = historical.Stop
require = historical.require


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load_contract():
    contract = json.loads(CONTRACT_PATH.read_text(encoding='utf-8'))
    require(contract['schema'] == 'application-stateful-benchmark-v1' and
            contract['preparation_count'] == contract['prepared_network_count'] == contract['prepared_runtime_count'] == 1 and
            contract['state_sequence_count'] == 2 and contract['total_advances'] == 24 and
            contract['maximum_consecutive_advances_per_state'] == 12 and not contract['continuous_480_ms'] and
            contract['retry_count'] == 0 and contract['dt_ms'] == historical.DT_MS,
            'A019C-CONTRACT-ALIGNMENT-FAILED', 'unsupported execution contract')
    for sequence, name in zip(contract['sequences'], ('A', 'B'), strict=True):
        require(sequence == dict(name=name, fresh_state=True, initial_timestep=0,
                    warmup_advances=2, measured_advances=10, total_advances=12,
                    advance_duration_ms=20, final_horizon_ms=240,
                    schedule_identity=contract['schedule']['identity']),
                'A019C-CONTRACT-ALIGNMENT-FAILED', 'unsupported sequence')
    require(all(contract['schedule'][key] == value for key, value in dict(
                identity=historical.SCHEDULE_ID, seed=1555062870, duration_ms=240,
                impulse_mV=68.75, left_rate_hz=100, right_rate_hz=0, left_neuron_count=42,
                right_neuron_count=0, generation_count=1, window_count=12, window_steps=200,
                event_count=948, side='LEFT', population='sugar', identical_frozen_windows=True,
                repack_each_call=True).items()),
            'A019C-CONTRACT-ALIGNMENT-FAILED', 'schedule contract changed')
    expected_identity()  # Validate the tracked full-real record without opening sources.
    return contract


@dataclass(frozen=True)
class Limits:
    preparation_s: float = 600
    advance_s: float = 30
    worker_s: float = 1500
    private_bytes: int = 8589934592
    working_set: int = 8589934592

    def check(self, memory, phase, elapsed, total):
        require(memory['private_bytes'] <= self.private_bytes and memory['working_set'] <= self.working_set,
                'MEMORY_LIMIT', 'contained tree memory cap')
        require(total <= self.worker_s, 'WORKER_TIMEOUT', 'whole worker deadline')
        if phase == 'prepare':
            require(elapsed <= self.preparation_s, 'PREPARATION_TIMEOUT', 'preparation deadline')
        if phase == 'advance':
            require(elapsed <= self.advance_s, 'ADVANCE_TIMEOUT', 'per-call deadline')


@dataclass(frozen=True)
class Source:
    files: DatasetFiles
    synthetic_root: Path | None

    def validate(self):
        if self.synthetic_root is not None:
            root = self.synthetic_root.resolve()
            require(not root.is_relative_to((ROOT / 'data').resolve()) and
                    self.files.manifest_digest == self.files.mapping_fingerprint == 'a019c-synthetic',
                    'A019C-REAL-DATA-FIREWALL-VIOLATION', 'synthetic source capability required')
            for path in (self.files.annotation, self.files.neurotransmitter, self.files.weights):
                require(path.resolve().is_relative_to(root) and path.is_file(),
                        'A019C-REAL-DATA-FIREWALL-VIOLATION', 'source outside synthetic capability')


def make_synthetic_source(directory):
    """44 neurons retain the exact frozen 42-member schedule and two readouts."""
    import pyarrow as pa
    import pyarrow.feather as feather
    ids = sorted(load_contract()['schedule']['member_ids'] + [10331, 16949])
    paths = synthetic_files(directory, 2000, len(ids))
    annotation = feather.read_table(paths[0]).to_pydict()
    annotation['bodyId'] = ids
    feather.write_feather(pa.table(annotation), paths[0])
    feather.write_feather(pa.table({'body': ids, 'consensus_nt': ['acetylcholine'] * len(ids)}), paths[1])
    edges = feather.read_table(paths[2]).to_pydict()
    for name in ('body_pre', 'body_post'):
        edges[name] = [ids[i - 1] for i in edges[name]]
    feather.write_feather(pa.table(edges), paths[2], chunksize=512)
    return Source(DatasetFiles(*paths, 'a019c-synthetic', 'a019c-synthetic'), directory)


def emit(phase, **details):
    print(json.dumps(dict(phase=phase, at=time.perf_counter(), pid=os.getpid(), **details)), flush=True)


def run_forward(source, expected=None, *, notify=lambda *a, **k: None,
                memory=lambda: {'private_bytes': 0, 'working_set': 0},
                runtime_factory=PreparedRuntime, limits=Limits(), real_authorized=False,
                available_physical_bytes=None, contained_watchdog=False):
    """One attempt, no retry. A019D must separately authorize a real capability."""
    c = load_contract()
    evidence = dict(schema='application-stateful-benchmark-evidence-v1',
        benchmark_contract_schema=c['schema'], benchmark_contract_identity=digest(c),
        preparation_identity_schema=c['preparation_identity_schema'],
        preparation_route='A015/A016/A017/A018/A018T/A018U/A018UJ',
        bounded_route_enabled=True, batch_rows=BATCH_ROWS, merge_block_size=BLOCK_SIZE,
        fallback=None, attempt_count=0, source_access_started=False, synthetic_source_accesses=0,
        preparations=0, prepared_network_count=0, prepared_runtime_count=0,
        simulation_state_count=0, advances_started=0, advances_completed=0, steps=[],
        limits=vars(limits), automatic_retry=False, classification='RUNNING', P1=None, P2=None,
        attempt_boundary='first bounded real edge-source access',
        timing_boundaries=dict(slicing='outside core timing', repacking='encode/total',
            output_assembly='advance', readout='total', verification='outside timing',
            warmups='individually timed; excluded from measured statistics'),
        firewall=dict(full_real_source_accesses=0, full_real_preparations=0, real_advances=0,
            gpu=0, real_arena_runs=0, real_experiments=0, raw_downloads=0, archive_writes=0))
    prepared = runtime = recorder = None
    started = time.perf_counter()
    phase_at = started
    current_phase = 'startup'

    def phase(name, **details):
        nonlocal phase_at, current_phase
        if current_phase == 'advance' and name == 'verification':
            limits.check(memory(), current_phase, time.perf_counter() - phase_at, time.perf_counter() - started)
        current_phase, phase_at = name, time.perf_counter()
        notify(name, **details)

    def checkpoint():
        limits.check(memory(), current_phase, time.perf_counter() - phase_at, time.perf_counter() - started)

    def route_event(kind, **details):
        if kind == 'source_access':
            evidence['source_access_started'] = True
            if source.synthetic_root is None:
                evidence['attempt_count'] = 1
                evidence['firewall']['full_real_source_accesses'] = 1
                evidence['firewall']['full_real_preparations'] = 1
            else:
                evidence['synthetic_source_accesses'] += 1
        if kind == 'fallback':
            evidence['fallback'] = details['trigger']
        notify('prepare' if current_phase == 'prepare' else current_phase, route_event=kind, attempt_count=evidence['attempt_count'], **details)

    try:
        source.validate()
        require(source.synthetic_root is not None or real_authorized,
                'REAL_EXECUTION_NOT_AUTHORIZED', 'separate A019D authorization required')
        if source.synthetic_root is None:
            require(contained_watchdog and available_physical_bytes is not None and
                    available_physical_bytes >= c['available_physical_min_bytes'],
                    'WATCHDOG_PREFLIGHT_FAILED', 'contained watchdog and 12 GiB available required')
            require(expected is None, 'IDENTITY_MISMATCH', 'real identity must use tracked canonical record')
        if source.synthetic_root is not None:
            require(expected is not None, 'IDENTITY_MISMATCH', 'synthetic identity injection required')
        expected = expected if expected is not None else expected_identity()
        schedule, windows = historical.freeze_schedule(c['schedule']['member_ids'])
        require(schedule.fingerprint == c['schedule']['identity'] and
                sum(len(s.spike_times_ms) for s in schedule.schedules) == c['schedule']['event_count'],
                'A019C-CONTRACT-ALIGNMENT-FAILED', 'frozen schedule mismatch')
        evidence['schedule'] = dict(identity=schedule.fingerprint, generation_count=1,
            seed=c['schedule']['seed'], horizon_ms=240, event_count=948,
            impulses_mV=c['schedule']['impulse_mV'], windows=[historical.pack(w, c['schedule']['member_ids']).fingerprint for w in windows])
        phase('prepare')
        checkpoint()
        evidence['preparations'] = 1
        metrics = evidence.setdefault('route_metrics', {})
        with bounded_route(metrics, route_event):
            prepared = ProductionEngine().prepare(source.files, 'cpu_reference')
        checkpoint()
        require(evidence['fallback'] is None, 'PREPARATION_FALLBACK', 'bounded route fallback')
        evidence['prepared_network_count'] = 1
        evidence['preparation_seconds'] = time.perf_counter() - phase_at
        phase('identity')
        observed = observe_identity(prepared, source.files, REFERENCE_CONFIG.digest)
        evidence['preparation_identity'] = observed
        evidence['gates'] = compare_identity(observed, expected)
        require(all(evidence['gates'].values()), 'IDENTITY_MISMATCH', 'G1-G6 mismatch')
        checkpoint()
        runtime = runtime_factory(prepared.projection, dt_ms=c['dt_ms'])
        evidence['prepared_runtime_count'] = 1
        refs, initials = [], []

        class Recorder:
            projection = runtime.projection

            def initial_state(self):
                require(not any(ref() is not None for ref in refs), 'STATE_LIFETIME', 'previous state still resident')
                state = runtime.initial_state()
                require(state.timestep == 0 and np.all(state.v_mV == REFERENCE_CONFIG.parameters.v_rest_mV) and
                        np.all(state.g_mV == 0) and np.all(state.refractory_until == -1) and
                        np.all(state.pending == 0) and np.all(state.pending_event_counts == 0),
                        'STATE_INITIALIZATION', 'noncanonical initial state')
                value = historical.state_evidence(state)
                if evidence['steps']:
                    last = evidence['steps'][-1]['replay']
                    require(value != dict(timestep=last['timestep'], arrays=last['arrays']), 'STATE_INITIALIZATION', 'B derived from A terminal')
                initials.append(value)
                refs[:] = [weakref.ref(getattr(state, name)) for name in historical.FIELDS]
                evidence['simulation_state_count'] += 1
                return state

            def advance(self, state, **kwargs):
                result = runtime.advance(state, **kwargs)
                if source.synthetic_root is None:
                    evidence['firewall']['real_advances'] += 1
                return result

        recorder = Recorder()
        historical.run_sequences(recorder, windows, c['schedule']['member_ids'], evidence,
                                 checkpoint, phase, memory)
        require(not any(ref() is not None for ref in refs) and initials[0] == initials[1],
                'STATE_LIFETIME', 'state release/initial replay failed')
        terminal = [dict(timestep=evidence['steps'][index]['replay']['timestep'],
                         arrays=evidence['steps'][index]['replay']['arrays']) for index in (11, 23)]
        evidence.update(final_states=terminal, state_a_released_before_b=True, states_coexist=False,
            max_consecutive_calls=12, final_horizons_ms=[240, 240], replay_sequence_identity=digest(
                [row['replay'] for row in evidence['steps'][:12]]), classification='A19C-A')
    except BoundedFallback as exc:
        evidence.update(classification='PREPARATION_FALLBACK', fallback=str(exc))
    except Stop as exc:
        evidence.update(classification=exc.classification, stop_detail=str(exc))
    except Exception as exc:
        evidence.update(classification='HARNESS_FAILURE', stop_detail=repr(exc))
    finally:
        prepared = runtime = recorder = None
        gc.collect()
        evidence['cleanup'] = 'released'
        try:
            phase('finished')
        except Exception as exc:
            evidence.update(classification='INSTRUMENTATION_FAILURE', stop_detail=repr(exc))
    return evidence


def supervise(command, output, limits=Limits()):
    """Corrected A014 Windows Job containment; one launch and fail closed."""
    require(not output.exists(), 'EVIDENCE_EXISTS', 'refusing retry/overwrite')
    job = ProcessJob(command)
    messages = queue.Queue()
    def reader():
        for line in job.process.stdout:
            messages.put(line)
    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    started = phase_at = time.perf_counter()
    phase, result, stop = 'startup', None, None
    peaks = dict(private_bytes=0, working_set=0)
    events, samples = [], 0
    try:
        while job.pids():
            while not messages.empty():
                message = json.loads(messages.get_nowait())
                require(message['pid'] in job.pids(), 'WATCHDOG_FAILURE', 'message outside contained tree')
                if message['phase'] == 'result':
                    result = message['evidence']
                else:
                    if message['phase'] != phase or 'interval' in message:
                        phase, phase_at = message['phase'], message['at']
                    events.append(message)
            snapshot = job.snapshot()
            samples += 1
            for key in peaks:
                peaks[key] = max(peaks[key], snapshot[key])
            limits.check(snapshot, phase, time.perf_counter() - phase_at, time.perf_counter() - started)
            if result is not None:
                break
            time.sleep(0.01)
    except Stop as exc:
        stop = exc
    except Exception as exc:
        stop = Stop('WATCHDOG_FAILURE', repr(exc))
    finally:
        job.close()
        thread.join(timeout=5)
    # Drain the final result after stdout closes on a normal short-lived worker.
    while not messages.empty():
        try:
            message = json.loads(messages.get_nowait())
            if message.get('phase') == 'result':
                result = message['evidence']
        except (ValueError, KeyError):
            stop = stop or Stop('WATCHDOG_FAILURE', 'invalid worker instrumentation')
    result = result or dict(schema='application-stateful-benchmark-evidence-v1', attempt_count=0)
    result['attempt_count'] = max(result.get('attempt_count', 0),
        max((event.get('attempt_count', 0) for event in events), default=0))
    if stop:
        result.update(classification=stop.classification, stop_detail=str(stop))
    elif result.get('classification') is None:
        result.update(classification='WATCHDOG_FAILURE', stop_detail='missing worker result')
    result['watchdog_preflight'] = 'contained suspended launch before source access'
    result['watchdog'] = dict(peaks=peaks, samples=samples, phase_events=events,
        process_containment='Windows Job Object', orphans=[], launches=1, limits=vars(limits))
    historical.dump(output, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--synthetic', action='store_true', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        with tempfile.TemporaryDirectory(prefix='a019c-synthetic-') as directory:
            source = make_synthetic_source(Path(directory))
            expected = json.loads(SYNTHETIC_IDENTITY_PATH.read_text())['expected']
            monitor = historical.WindowsMemory(os.getpid())
            try:
                result = run_forward(source, expected, notify=emit, memory=monitor.snapshot)
            finally:
                monitor.close()
            emit('result', evidence=result)
    else:
        result = supervise([sys.executable, str(Path(__file__).resolve()), '--synthetic',
                            '--worker', '--output', str(args.output)], args.output)
    return 0 if result['classification'] == 'A19C-A' else 1


if __name__ == '__main__':
    raise SystemExit(main())
