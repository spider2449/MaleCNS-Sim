"""Reproducible interval analysis of the two frozen A019X captures."""
from __future__ import annotations

import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'a019c_firewall'))
if os.environ.get('MALECNS_A019C_R2_FIREWALL') != '1':
    raise SystemExit('FIREWALL_REQUIRED_BUT_NOT_ACTIVE')
import validation_firewall as guard
guard.install()

import argparse
from collections import Counter
import hashlib
import json
import sqlite3

from profile_application_a019x import ROOT, dump, output_root, check_pins


def union(intervals, lo, hi):
    """Clip and merge activity intervals without double-counting overlap."""
    merged = []
    for start, end in sorted((max(a, lo), min(b, hi)) for a, b in intervals if b > lo and a < hi):
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def duration(intervals):
    return sum(end - start for start, end in intervals)


def complement(intervals, lo, hi):
    gaps = []
    cursor = lo
    for start, end in union(intervals, lo, hi):
        if start > cursor:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < hi:
        gaps.append((cursor, hi))
    return gaps


def intersection(left, right):
    """Intersect two merged timelines to separate API occupancy from GPU work."""
    overlap = []
    i = j = 0
    while i < len(left) and j < len(right):
        start, end = max(left[i][0], right[j][0]), min(left[i][1], right[j][1])
        if end > start:
            overlap.append((start, end))
        if left[i][1] <= right[j][1]:
            i += 1
        else:
            j += 1
    return overlap


def submission_gaps(operations, api_starts, lo, hi):
    """Conservative pre-submission idle prefixes on one ordered stream."""
    ordered = sorted(operations, key=lambda operation: (operation['start'], operation['end']))
    if any(right['start'] < left['end'] for left, right in zip(ordered, ordered[1:])):
        raise ValueError('STREAM_ACTIVITY_OVERLAP')
    gaps = []
    cursor = lo
    missing = 0
    for operation in ordered:
        if operation['end'] <= lo or operation['start'] >= hi:
            continue
        next_start = min(operation['start'], hi)
        if next_start > cursor:
            submitted = api_starts.get(operation['correlationId'])
            if submitted is None:
                missing += 1
            elif submitted > cursor:
                gaps.append((cursor, min(submitted, next_start)))
        cursor = max(cursor, operation['end'])
    # No next operation exists for the post-device tail; leave it unclassified.
    return union(gaps, lo, hi), missing


def analyze_case(output, case, worker):
    database = output / (case + '-TRACE.sqlite')
    connection = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    queries = []
    def query(sql, parameters=()):
        queries.append(dict(sql=sql, parameters=list(parameters)))
        return [dict(row) for row in connection.execute(sql, parameters)]
    try:
        schemas = query("SELECT name,sql FROM sqlite_master WHERE type='table'")
        names = {row['name'] for row in schemas}
        required = {'StringIds', 'NVTX_EVENTS', 'CUPTI_ACTIVITY_KIND_KERNEL',
                    'CUPTI_ACTIVITY_KIND_RUNTIME', 'TARGET_INFO_CUDA_CONTEXT_INFO',
                    'DIAGNOSTIC_EVENT', 'ENUM_DIAGNOSTIC_SEVERITY_LEVEL', 'META_DATA_EXPORT'}
        if not required.issubset(names):
            raise ValueError('MISSING_REQUIRED_TRACE_TABLES')
        strings = {row['id']: row['value'] for row in query('SELECT id,value FROM StringIds')}
        ranges = query('SELECT * FROM NVTX_EVENTS WHERE text=?', ('A019X_' + case + '_PUBLIC_ADVANCE',))
        if len(ranges) != 1 or ranges[0]['end'] is None:
            raise ValueError('PUBLIC_RANGE_MISSING_OR_AMBIGUOUS')
        boundary = ranges[0]
        lo, hi, thread = boundary['start'], boundary['end'], boundary['globalTid']
        if hi <= lo:
            raise ValueError('PUBLIC_RANGE_INVALID')
        contexts = query('SELECT * FROM TARGET_INFO_CUDA_CONTEXT_INFO WHERE processId=?', (worker['pid'],))
        if len(contexts) != 1:
            raise ValueError('WORKER_CONTEXT_AMBIGUOUS')
        context = contexts[0]['contextId']
        kernels = query('SELECT * FROM CUPTI_ACTIVITY_KIND_KERNEL WHERE contextId=? AND start>=? AND end<=?',
                        (context, lo, hi))
        processes = {row['globalPid'] for row in kernels}
        if len(processes) != 1:
            raise ValueError('KERNEL_PROCESS_AMBIGUOUS')
        process = next(iter(processes))
        scheduled = [row for row in kernels if strings[row['shortName']] == 'schedule_ordered']
        if len(scheduled) != 200:
            raise ValueError('ORDERED_SCHEDULER_COUNT_NOT_200')
        streams = {row['streamId'] for row in kernels}
        if len(streams) != 1:
            raise ValueError('MULTIPLE_KERNEL_STREAMS')
        stream = next(iter(streams))
        apis = query('SELECT * FROM CUPTI_ACTIVITY_KIND_RUNTIME WHERE globalTid=? AND end>? AND start<?',
                     (thread, lo, hi))
        if 'CUPTI_ACTIVITY_KIND_DRIVER' in names:
            apis += query('SELECT * FROM CUPTI_ACTIVITY_KIND_DRIVER WHERE globalTid=? AND end>? AND start<?',
                          (thread, lo, hi))
        api_starts = {}
        for row in apis:
            key = row['correlationId']
            api_starts[key] = min(row['start'], api_starts.get(key, row['start']))
        if not all(row['correlationId'] in api_starts for row in scheduled):
            raise ValueError('SCHEDULER_HOST_CORRELATION_INCOMPLETE')
        transfers, memsets = [], []
        for table, target in (('CUPTI_ACTIVITY_KIND_MEMCPY', transfers), ('CUPTI_ACTIVITY_KIND_MEMSET', memsets)):
            if table in names:
                target.extend(query('SELECT * FROM ' + table + ' WHERE globalPid=? AND end>? AND start<?',
                                    (process, lo, hi)))
        operations = kernels + transfers + memsets
        if any(row['contextId'] != context or row['streamId'] != stream for row in operations):
            raise ValueError('DEVICE_CONTEXT_OR_STREAM_MISMATCH')
        kernel_union = union([(row['start'], row['end']) for row in kernels], lo, hi)
        transfer_union = union([(row['start'], row['end']) for row in transfers], lo, hi)
        device_union = union([(row['start'], row['end']) for row in operations], lo, hi)
        api_union = union([(row['start'], row['end']) for row in apis], lo, hi)
        idle = complement(device_union, lo, hi)
        idle_in_api = intersection(idle, api_union)
        host_gaps, missing_gap_correlations = submission_gaps(operations, api_starts, lo, hi)
        span = hi - lo
        total = Counter()
        counts = Counter()
        short = []
        for row in kernels:
            name = strings[row['shortName']]
            total[name] += row['end'] - row['start']
            counts[name] += 1
            if row['end'] - row['start'] <= 10000:
                short.append(row['end'] - row['start'])
        api_total = Counter()
        api_counts = Counter()
        for row in apis:
            name = strings[row['nameId']]
            api_total[name] += max(0, min(row['end'], hi) - max(row['start'], lo))
            api_counts[name] += 1
        diagnostics = query('SELECT d.*,s.label severity_label FROM DIAGNOSTIC_EVENT d '
                            'JOIN ENUM_DIAGNOSTIC_SEVERITY_LEVEL s ON d.severity=s.id')
        problematic = [row for row in diagnostics if any(word in row['severity_label'].lower()
                       for word in ('warning', 'error', 'fatal')) or any(word in row['text'].lower()
                       for word in ('dropped', 'incomplete', 'lost events'))]
        metadata = query('SELECT * FROM META_DATA_EXPORT')
        response = dict(case=case, worker_pid=worker['pid'], global_pid=process, global_tid=thread,
                        context=context, stream=stream, public_range_ns=dict(start=lo, end=hi, duration=span),
                        schema=schemas, metadata=metadata, queries=queries, diagnostics=diagnostics,
                        diagnostic_problems=problematic, ordered_launches=len(scheduled), kernel_count=len(kernels),
                        memcpy_count=len(transfers), memset_count=len(memsets), api_count=len(apis),
                        kernel_union_ns=duration(kernel_union), transfer_union_ns=duration(transfer_union),
                        device_union_ns=duration(device_union), host_api_union_ns=duration(api_union),
                        gpu_idle_inside_host_api_ns=duration(idle_in_api),
                        gpu_idle_outside_host_api_ns=duration(idle) - duration(idle_in_api),
                        idle_ns=duration(idle), host_submission_idle_prefix_ns=duration(host_gaps),
                        missing_gap_correlations=missing_gap_correlations,
                        post_device_tail_ns=hi - max(row['end'] for row in operations),
                        ordered_kernel_ns=sum(row['end'] - row['start'] for row in scheduled),
                        short_kernel_threshold_ns=10000, short_kernel_count=len(short), short_kernel_ns=sum(short),
                        memcpy_bytes=sum(row['bytes'] for row in transfers),
                        kernel_summary=[dict(name=name, count=counts[name], duration_ns=value)
                                        for name, value in total.most_common()],
                        api_summary=[dict(name=name, count=api_counts[name], duration_ns=value)
                                     for name, value in api_total.most_common()],
                        interval_rules='clip to public NVTX range; interval unions; no host/device percentage addition; single ordered stream',
                        attribution_limit='Pre-submission idle time is not proof of Python execution; CPU scheduling/stacks and driver/profiler cost remain unmeasured.')
        response['trace_usable'] = not problematic and missing_gap_correlations == 0
        for key in ('kernel_union', 'transfer_union', 'device_union', 'host_api_union',
                    'idle', 'host_submission_idle_prefix', 'ordered_kernel', 'short_kernel',
                    'gpu_idle_inside_host_api', 'gpu_idle_outside_host_api'):
            response[key + '_fraction'] = response[key + '_ns'] / span
        return response
    finally:
        connection.close()


def run(output):
    check_pins()
    target = ROOT / 'docs/plans/a019x-synthetic-gpu-profiling-evidence.json'
    evidence = json.loads(target.read_text())
    assert evidence['complete'] and output == output_root(evidence['output'])
    frozen = json.loads((output / 'execution-contract.json').read_text())
    post_execution_changes = []
    for name, expected in frozen['hashes'].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != expected:
            retained_names = {
                str(ROOT / 'scripts/profile_application_a019x.py'): 'profile_application_a019x-executed.py',
                'docs/plans/2026-10-07-application-a019x-synthetic-gpu-profiling-protocol.md': 'protocol-executed.md',
            }
            assert name in retained_names, 'EXECUTION_CONTRACT_DRIFT'
            retained = output / retained_names[name]
            assert hashlib.sha256(retained.read_bytes()).hexdigest() == expected, 'EXECUTED_RUNNER_COPY_MISMATCH'
            post_execution_changes.append(dict(path=name, executed_copy=str(retained),
                change=('Post-run assignment-failure cleanup correction; no workload or capture rerun.'
                        if retained.suffix == '.py' else 'Post-run completion status and result link.')))
    all_usable = True
    distorted = False
    for case in evidence['cases']:
        try:
            case['timeline'] = analyze_case(output, case['case'], case['roles']['TRACE']['worker'])
            all_usable &= case['timeline']['trace_usable']
        except (ValueError, sqlite3.Error, KeyError) as exc:
            case['timeline'] = dict(trace_usable=False, blocker=repr(exc))
            all_usable = False
        distorted |= case['material_observer_effect']
    s1, s4 = evidence['cases']
    if not all_usable or distorted:
        classification = 'A019X-C'
        reason = 'Incomplete attribution or a material observer effect under the frozen protocol.'
    elif (s4['timeline']['host_submission_idle_prefix_fraction'] >= 0.5
          and s1['timeline']['host_submission_idle_prefix_fraction'] >= 0.5):
        classification = 'A019X-A'
        reason = 'Conservative host-submission idle prefixes exceed half of both observed public ranges; causal Python attribution remains qualified.'
    elif (s4['timeline']['device_union_fraction'] >= 0.8
          and s4['timeline']['host_submission_idle_prefix_fraction'] <= 0.1):
        classification = 'A019X-B'
        reason = 'Device activity dominates the observed S4 public range; H1 is not supported as the major explanation.'
    else:
        classification = 'A019X-C'
        reason = 'Intermediate or mixed attribution under the frozen decision thresholds.'
    evidence.update(classification=classification, disposition_reason=reason, analysis_complete=True,
                    production_unchanged=True, execution_contract=frozen,
                    post_execution_changes=post_execution_changes,
                    analysis_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    nonclaims=['full-real performance', 'Python-only causal dominance', 'profiler-corrected timing',
                               'realtime', 'biological interpretation', 'true native VRAM peak'])
    evidence['next_task'] = 'A019Y: evidence-only disposition of trace completeness and observer effects; no recapture, tooling installation or optimization automatically authorized'
    evidence['counters'] = dict(workload_workers=6, cpu_advances=6, gpu_advances=12, cuda_capture_ranges=2,
        full_real_preparations=0, real_advances=0, A019D_A019L_reruns=0, Arena=0, interventions=0,
        downloads=0, archive_writes=0, production_edits=0,
        registered_payload_reads={name: 0 for name in ('annotation', 'neurotransmitter', 'connectivity',
            'metadata', 'mapping', 'provenance', 'other')})
    evidence['accounting_qualifier'] = 'Fail-closed guarded-scope source-access accounting; not independent native-byte telemetry.'
    evidence['raw_manifest'] = [dict(path=str(path), bytes=path.stat().st_size,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in sorted(output.iterdir())
        if path.is_file() and path.name != 'raw-manifest.json']
    dump(output / 'raw-manifest.json', evidence['raw_manifest'])
    dump(target, evidence)
    for case in evidence['cases']:
        timeline = case['timeline']
        print(json.dumps(dict(case=case['case'], observer_ratio=case['observer_ratio'],
            material_observer_effect=case['material_observer_effect'],
            timeline={key: timeline.get(key) for key in ('trace_usable', 'ordered_launches', 'kernel_count',
                'device_union_fraction', 'host_submission_idle_prefix_fraction', 'ordered_kernel_fraction',
                'missing_gap_correlations', 'diagnostic_problems', 'blocker')})))
    print(classification + ': ' + reason)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    run(output_root(args.output))


if __name__ == '__main__':
    main()
