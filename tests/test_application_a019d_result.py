"""Offline audit of the single recorded A019D result; no source access."""
import json
from pathlib import Path

import numpy as np


def test_recorded_contract_and_exact_replay():
    root = Path(__file__).resolve().parents[1]
    evidence = json.loads((root / 'docs/plans/2026-10-06-application-a019d-evidence.json').read_text())
    assert evidence['classification'] == 'A19C-A'
    assert evidence['attempt_count'] == evidence['preparations'] == 1
    assert evidence['prepared_network_count'] == evidence['prepared_runtime_count'] == 1
    assert evidence['simulation_state_count'] == 2
    assert evidence['advances_started'] == evidence['advances_completed'] == 24
    assert all(evidence['gates'].values())
    assert evidence['final_horizons_ms'] == [240, 240]
    assert evidence['state_a_released_before_b'] and not evidence['states_coexist']
    assert evidence['max_consecutive_calls'] == 12
    assert evidence['replay'] == 'exact pass'
    assert evidence['final_states'][0] == evidence['final_states'][1]
    assert evidence['schedule']['generation_count'] == 1
    assert evidence['schedule']['event_count'] == 948
    assert evidence['schedule']['identity'] == '6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a'
    assert all(row['sha256'] == row['expected_sha256'] for row in evidence['sources'])
    for index, (a, b) in enumerate(zip(evidence['steps'][:12], evidence['steps'][12:], strict=True)):
        assert a['sequence'] == 'A' and b['sequence'] == 'B'
        assert a['warmup'] == b['warmup'] == (index < 2)
        assert a['replay'] == b['replay']
        assert a['replay']['timestep'] == (index + 1) * 200
    assert evidence['cleanup'] == 'released'
    assert evidence['watchdog']['orphans'] == []
    assert evidence['watchdog']['launches'] == 1
    assert not evidence['automatic_retry']
    assert all(value <= 8589934592 for value in evidence['watchdog']['peaks'].values())


def test_p2_uses_every_measured_total_wall_duration():
    root = Path(__file__).resolve().parents[1]
    evidence = json.loads((root / 'docs/plans/2026-10-06-application-a019d-evidence.json').read_text())
    values = [row['seconds']['total'] for row in evidence['steps'] if not row['warmup']]
    assert len(values) == 20
    assert all(0.020 < value < 30 for value in values)
    stats = evidence['distributions_seconds']['pooled']['total']
    assert stats['min'] == min(values) and stats['max'] == max(values)
    assert stats['mean'] == float(np.mean(values))
    assert stats['p50'] == float(np.median(values))
    assert stats['p95'] == float(np.percentile(values, 95, method='linear'))
