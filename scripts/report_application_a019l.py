"""Offline descriptive adjudication of the single recorded A019L attempt."""
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'docs/plans/a019l-full-real-cpu-rebenchmark-evidence.json'
PLAN = ROOT / 'docs/plans/2026-10-06-application-a019l-full-real-cpu-rebenchmark.md'
FROZEN = dict(min=1.515181500, median=1.642870550, mean=1.647739485,
    max=1.774488700, p95=1.741707810, population_std=0.062658750363,
    CV_percent=3.802709768953, A_mean=1.613853650, B_mean=1.681625320)


def summarize(values):
    ordered = sorted(values)
    mean = statistics.mean(values)
    std = statistics.pstdev(values)
    return dict(min=min(values), median=statistics.median(values), mean=mean,
        max=max(values), p95=ordered[18] + 0.05 * (ordered[19] - ordered[18]),
        population_std=std, CV_percent=100 * std / mean,
        A_mean=statistics.mean(values[:10]), B_mean=statistics.mean(values[10:]),
        counts=dict(le_20ms=sum(x <= .020 for x in values),
            gt_20ms=sum(x > .020 for x in values), ge_30s=sum(x >= 30 for x in values)))


def adjudicate(evidence, baseline):
    rows = [r for r in evidence.get('steps', []) if not r['warmup']]
    values = [r['seconds']['total'] for r in rows]
    evidence['frozen_a019d_statistics'] = FROZEN
    evidence['measured_timings_seconds'] = values
    complete = evidence.get('classification') == 'A19C-A' and len(values) == 20
    if not complete:
        evidence['L_classification'] = 'A019L-L4'
        evidence['P_classification'] = None
        raw = evidence.get('classification')
        mapping = dict(PREPARATION_TIMEOUT='A019L-PREPARATION-TIME-LIMIT',
            ADVANCE_TIMEOUT='A019L-ADVANCE-TIME-LIMIT', IDENTITY_MISMATCH='A019L-PREPARATION-IDENTITY-FAILURE',
            HARNESS_FAILURE='A019L-PREPARATION-ERROR', WATCHDOG_FAILURE='A019L-PROCESS-CONTAINMENT-FAILURE')
        evidence['terminal_result'] = mapping.get(raw, raw if str(raw).startswith('A019L-') else 'A019L-L4-INVALID-COMPARISON')
        return evidence
    stats = summarize(values)
    old = [r['seconds']['total'] for r in baseline['steps'] if not r['warmup']]
    pairs = [dict(state=r['sequence'], measured_index=(i % 10) + 1,
        old_seconds=o, new_seconds=n, delta_seconds=n-o, percent_change=100*(n-o)/o)
        for i, (r, o, n) in enumerate(zip(rows, old, values, strict=True))]
    deltas = {k: dict(delta_seconds=stats[k]-FROZEN[k],
        percent_change=100*(stats[k]-FROZEN[k])/FROZEN[k])
        for k in ('mean', 'median', 'p95', 'max', 'A_mean', 'B_mean')}
    exact = all(r['replay'] == d['replay'] for r, d in zip(evidence['steps'], baseline['steps'], strict=True))
    faster = [sum(p['delta_seconds'] < 0 for p in pairs[i:i+10]) for i in (0, 10)]
    slower = [sum(p['delta_seconds'] > 0 for p in pairs[i:i+10]) for i in (0, 10)]
    trimmed = sum(sorted((o-n for o, n in zip(old, values)), reverse=True)[3:])
    tail = stats['max'] > 1.05*FROZEN['max'] or stats['p95'] > 1.05*FROZEN['p95']
    valid = (exact and evidence['advances_completed'] == evidence['advances_started'] == 24
        and all(r['seconds']['total'] < 30 for r in evidence['steps'])
        and evidence['a019l_environment_preconsumption']['comparable']
        and all(evidence['gates'].values()) and evidence['watchdog']['orphans'] == [])
    gate = dict(valid=valid, exact_historical_replay=exact, improved_by_state=faster,
        regressed_by_state=slower, savings_after_removing_three_largest=trimmed,
        material_tail_regression=tail,
        mean_at_least_5pct_lower=stats['mean'] <= .95*FROZEN['mean'],
        median_at_least_5pct_lower=stats['median'] <= .95*FROZEN['median'])
    l1 = (valid and gate['mean_at_least_5pct_lower'] and gate['median_at_least_5pct_lower']
        and stats['A_mean'] < FROZEN['A_mean'] and stats['B_mean'] < FROZEN['B_mean']
        and sum(faster) >= 16 and min(faster) >= 8
        and statistics.median(p['percent_change'] for p in pairs) < 0 and trimmed > 0 and not tail)
    l3 = (valid and stats['mean'] >= 1.05*FROZEN['mean'] and stats['median'] >= 1.05*FROZEN['median']
        and stats['A_mean'] > FROZEN['A_mean'] and stats['B_mean'] > FROZEN['B_mean']
        and sum(slower) >= 16 and min(slower) >= 8)
    classification = 'A019L-L4' if not valid else 'A019L-L1' if l1 else 'A019L-L3' if l3 else 'A019L-L2'
    evidence.update(current_statistics=stats, paired_deltas=pairs, aggregate_deltas=deltas,
        CV_change_percentage_points=stats['CV_percent']-FROZEN['CV_percent'],
        paired_summary=dict(improved=sum(faster), regressed=sum(slower), tied=20-sum(faster)-sum(slower),
            mean_percent_change=statistics.mean(p['percent_change'] for p in pairs),
            median_percent_change=statistics.median(p['percent_change'] for p in pairs)),
        preregistered_gates=gate, L_classification=classification,
        P_classification=('P1' if stats['counts']['le_20ms'] == 20 else 'P2') if valid else None,
        exact_historical_replay='PASS' if exact else 'FAIL',
        terminal_result=classification)
    return evidence


if __name__ == '__main__':
    evidence = json.loads(PATH.read_text())
    baseline = json.loads((ROOT / 'docs/plans/2026-10-06-application-a019d-evidence.json').read_text())
    adjudicate(evidence, baseline)
    evidence.update(retry_count=0, runtime_reset=False, runtime_recreated=False,
        continuous_480_ms=False, scientific_nonclaims=[
            'biological realtime', 'behavior prediction', 'mechanism', 'brain reconstruction',
            'GPU implications', 'hardware-independent speedup', 'inferential significance'],
        final_custody=dict(commit_sha='reported externally to avoid self-reference',
            push='verify local/origin/live after commit', version='0.3.0', workflows=0))
    for r in evidence.get('steps', []):
        r.update(simulated_start_ms=(r['interval']-1)*20, simulated_end_ms=r['interval']*20,
            timeout_status='PASS' if r['seconds']['total'] < 30 else 'FAIL',
            resource_status='PASS' if max(r['memory'][k] for k in ('private_bytes', 'working_set')) <= 8589934592 else 'FAIL')
    PATH.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    lines = ['\n## Terminal recorded outcome\n',
        f"**{evidence['L_classification']} / {evidence['P_classification']}**. Raw harness: {evidence['classification']}.",
        '\nConsumption: ' + json.dumps(evidence.get('consumption')),
        '\nPreparation: ' + json.dumps({k:evidence.get(k) for k in ('preparations', 'preparation_seconds', 'preparation_start_utc', 'preparation_end_utc', 'gates')}),
        '\nContained-tree peaks: ' + json.dumps(evidence['watchdog']['peaks']),
        '\nCurrent measured statistics: ' + json.dumps(evidence.get('current_statistics')),
        '\nFrozen D statistics: ' + json.dumps(FROZEN),
        '\nAggregate deltas: ' + json.dumps(evidence.get('aggregate_deltas')),
        '\nPaired summary: ' + json.dumps(evidence.get('paired_summary')),
        '\nPreregistered gate evidence: ' + json.dumps(evidence.get('preregistered_gates')),
        '\n| State | Call | Kind | Simulated ms | Total wall s |', '|---|---:|---|---|---:|']
    for r in evidence.get('steps', []):
        lines.append(f"| {r['sequence']} | {r['interval']} | {'warmup' if r['warmup'] else 'measured'} | {r['simulated_start_ms']}/{r['simulated_end_ms']} | {r['seconds']['total']:.9f} |")
    lines += ['\nAll per-pair deltas, source identities, environment matrix, full state/output/pending replay records and cleanup evidence are preserved in [machine-readable evidence](a019l-full-real-cpu-rebenchmark-evidence.json).',
        '\nOne preparation/network/runtime, two fresh states, 24 calls; A released before B. No runtime reset/recreation, cloning or continuous 480-ms trajectory. Retry count 0. GPU/Arena/intervention/download/archive counts 0.',
        '\nHistorical BLAS/thread/power/priority metadata is absent. This qualified descriptive comparison measures this workload and configuration; it is not a randomized causal attribution or hardware-independent result. All scientific nonclaims above remain preserved.',
        '\nCustody: containing commit and final local/origin/live SHA are reported externally; no self-referential SHA is embedded. Final version 0.3.0; workflows 0; no tag/release/version bump.']
    PLAN.write_text(PLAN.read_text(encoding='utf-8') + '\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({k:evidence.get(k) for k in ('L_classification','P_classification','current_statistics','paired_summary','aggregate_deltas','consumption','preparation_seconds')}))
