"""Offline audits of A019L custody, exact replay and descriptive adjudication."""
import copy
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from report_application_a019l import adjudicate, summarize
from preparation_identity_contract import compare_identity, expected_identity


def recorded():
    return json.loads((ROOT / 'docs/plans/a019l-full-real-cpu-rebenchmark-evidence.json').read_text(encoding='utf-8'))


def baseline():
    return json.loads((ROOT / 'docs/plans/2026-10-06-application-a019d-evidence.json').read_text())


def test_exact_contract_replay_and_custody():
    e, d = recorded(), baseline()
    assert e['attempt_count'] == e['preparations'] == e['prepared_network_count'] == e['prepared_runtime_count'] == 1
    assert e['simulation_state_count'] == 2
    assert e['advances_started'] == e['advances_completed'] == 24
    assert e['state_a_released_before_b'] and not e['states_coexist']
    assert e['final_horizons_ms'] == [240, 240] and e['max_consecutive_calls'] == 12
    assert e['schedule'] == d['schedule']
    assert e['preparation_identity'] == d['preparation_identity']
    assert all(e['gates'].values()) and e['merge_block_size'] == 16384
    assert e['bounded_route_enabled'] and e['fallback'] is None
    assert e['replay'] == 'exact pass' and e['a019d_exact_replay']['boundaries'] == 24
    for i, (r, old) in enumerate(zip(e['steps'], d['steps'], strict=True)):
        assert r['replay'] == old['replay']
        assert r['replay']['timestep'] == ((i % 12)+1)*200
        assert r['timeout_status'] == r['resource_status'] == 'PASS'
    assert e['watchdog']['orphans'] == [] and e['watchdog']['launches'] == 1
    assert all(x <= 8589934592 for x in e['watchdog']['peaks'].values())
    assert e['retry_count'] == 0 and not e['automatic_retry']
    assert e['cleanup'] == 'released'
    assert all(r['sha256'] == r['expected_sha256'] for r in e['sources'])
    assert e['external_cleanup']['remaining_adapter_processes'] == []


def test_offline_statistics_and_preregistered_decision():
    e = recorded()
    values = [r['seconds']['total'] for r in e['steps'] if not r['warmup']]
    assert e['current_statistics'] == summarize(values)
    fresh = adjudicate(copy.deepcopy(e), baseline())
    for key in ('L_classification', 'P_classification', 'paired_deltas', 'aggregate_deltas', 'paired_summary', 'preregistered_gates'):
        assert fresh[key] == e[key]
    assert len(e['paired_deltas']) == len(values) == 20
    assert e['current_statistics']['counts']['ge_30s'] == 0


def test_replay_failure_invalidates_comparison():
    e = copy.deepcopy(recorded())
    e['steps'][0]['replay']['timestep'] += 1
    adjudicate(e, baseline())
    assert e['L_classification'] == 'A019L-L4' and e['P_classification'] is None


def test_layer_distinction_and_wrong_layer_rejection():
    expected = expected_identity()
    assert all(compare_identity(expected, expected).values())
    wrong = dict(expected, prepared_network_digest=expected['effective_projection_fingerprint'])
    with pytest.raises(ValueError, match='effective fingerprint'):
        compare_identity(wrong, expected)
    wrong = dict(expected, effective_projection_fingerprint=expected['unsigned_graph_digest'])
    assert not compare_identity(wrong, expected)['G4']
