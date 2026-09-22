from __future__ import annotations

import json

import numpy as np
import pytest

from malecns_sim.analysis.task010 import (
    FROZEN_CANDIDATE_IDS,
    PREDECLARED_THRESHOLDS,
    FrozenCandidate,
    FrozenCandidateManifest,
    PairedMetricSummary,
    Task010Trial,
    asymmetry_metric,
    candidate_set_fingerprint,
    ensure_separate_output,
    frozen_silencing_ids,
    load_frozen_candidate_manifest,
    paired_trial_summary,
    rate_effect,
    validate_candidate_ids,
)
from malecns_sim.dynamics import ExplicitStimulus, LIFParameters, SpikeSchedule, simulate_lif
from malecns_sim.dynamics.lif import EffectiveSignedProjection


def _projection(edges: tuple[tuple[int, int, int], ...]) -> EffectiveSignedProjection:
    ids = np.asarray([1, 2, 3], dtype=np.int64)
    source = np.asarray([row[0] - 1 for row in edges], dtype=np.int64)
    target = np.asarray([row[1] - 1 for row in edges], dtype=np.int64)
    weights = np.asarray([row[2] * 0.275 for row in edges], dtype=np.float64)
    indptr = np.zeros(4, dtype=np.int64)
    for position in source:
        indptr[position + 1] += 1
    np.cumsum(indptr, out=indptr)
    order = np.lexsort((target, source)) if len(edges) else np.empty(0, dtype=np.int64)
    source = source[order]
    target = target[order]
    weights = weights[order]
    return EffectiveSignedProjection(
        neuron_ids=ids,
        source_positions=source,
        target_positions=target,
        effective_weights_mV=weights,
        included_anatomical_weight=sum(row[2] for row in edges),
        excluded_anatomical_weight=0,
        excluded_unresolved_edge_count=0,
        synaptic_weight_mV=0.275,
        sign_policy_id="test",
        resolution_policy_id="test",
        unsigned_graph_fingerprint="u" * 64,
        signed_policy_fingerprint="s" * 64,
        fingerprint="p" * 64,
        outgoing_indptr=indptr,
        outgoing_targets=target,
        outgoing_weights_mV=weights,
    )


def _trial(candidate_id: str, index: int, l: int, r: int, total: int) -> Task010Trial:
    return Task010Trial(
        candidate_id=candidate_id,
        condition="test",
        stimulus_side="L",
        trial_index=index,
        seed=100 + index,
        mn9_l_spikes=l,
        mn9_r_spikes=r,
        total_network_spikes=total,
        active_neuron_count=2,
        sugar_input_events=3,
        queued_synaptic_events=4,
        delivered_synaptic_events=5,
        result_digest=f"{index:064d}",
        duration_ms=1000.0,
    )


def test_frozen_candidate_manifest_is_literal_and_fingerprinted(tmp_path):
    rows = []
    for body_id in FROZEN_CANDIDATE_IDS:
        rows.append(
            {
                "body_id": body_id,
                "reasons": ["test"],
                "routes": [],
                "signed_proxy_values": [],
            }
        )
    report = {
        "candidate_task010_intervention_list": rows,
        "full": {
            "routes": [],
            "top_intermediates": {
                "route": {
                    "metric": [
                        {
                            "metadata": {
                                "body_id": body_id,
                                "type": "T",
                                "instance": "T_L",
                                "side": "L",
                                "superclass": "S",
                                "cell_class": "C",
                                "neurotransmitter": "acetylcholine",
                            },
                            "aggregate": {},
                        }
                        for body_id in FROZEN_CANDIDATE_IDS
                    ]
                }
            },
            "homolog_pairs": [],
        },
        "fingerprints": {"candidate_task010_intervention_list": "task009"},
    }
    path = tmp_path / "task009.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    manifest = load_frozen_candidate_manifest(path)
    assert manifest.body_ids == FROZEN_CANDIDATE_IDS
    assert manifest.fingerprint == candidate_set_fingerprint(manifest.candidates)
    assert len(manifest.fingerprint) == 64


def test_frozen_manifest_rejects_mutated_candidate_order(tmp_path):
    path = tmp_path / "task009.json"
    path.write_text(
        json.dumps({"candidate_task010_intervention_list": [{"body_id": body_id} for body_id in reversed(FROZEN_CANDIDATE_IDS)]}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="candidate list mismatch"):
        load_frozen_candidate_manifest(path)


def test_unknown_candidate_rejection_and_all_seven_mask():
    candidates = tuple(
        FrozenCandidate(body_id=body_id, type=None, instance=None, side=None, superclass=None, cell_class=None, neurotransmitter=None, homolog_body_id=None, homolog_instance=None, structural_metrics=(), reasons=(), routes=(), signed_proxy_values=())
        for body_id in FROZEN_CANDIDATE_IDS
    )
    manifest = FrozenCandidateManifest(candidates, "source", candidate_set_fingerprint(candidates))
    assert frozen_silencing_ids(manifest, FROZEN_CANDIDATE_IDS) == FROZEN_CANDIDATE_IDS
    with pytest.raises(ValueError, match="unknown candidate"):
        validate_candidate_ids(("999999",), FROZEN_CANDIDATE_IDS)
    with pytest.raises(ValueError, match="unknown candidate"):
        frozen_silencing_ids(manifest, ("10331",))


def test_outgoing_silencing_keeps_internal_spike_and_blocks_transmission():
    projection = _projection(((1, 2, 100),))
    stimulus = ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0)
    normal = simulate_lif(projection, duration_ms=2.1, stimulus=stimulus, trace_neuron_ids=(2,))
    silenced = simulate_lif(projection, duration_ms=2.1, stimulus=stimulus, silenced_neuron_ids=(1,), trace_neuron_ids=(2,))
    assert normal.spike_counts[0] == silenced.spike_counts[0] == 1
    assert normal.trace_g_mV is not None and np.any(normal.trace_g_mV != 0.0)
    assert silenced.trace_g_mV is not None and np.all(silenced.trace_g_mV == 0.0)


def test_effect_thresholds_and_zero_baseline_are_fixed():
    assert rate_effect(40.0, 10.0).classification == "major"
    assert rate_effect(20.0, 16.0).classification == "moderate"
    assert rate_effect(20.0, 19.0).classification == "small"
    assert rate_effect(0.0, 0.5).percent_change is None
    assert rate_effect(0.0, 0.5).classification == "negligible"
    assert PREDECLARED_THRESHOLDS.major_absolute_hz == 20.0


def test_paired_trial_aggregation_is_trial_aligned():
    baseline = (_trial("baseline", 0, 10, 5, 100), _trial("baseline", 1, 20, 7, 200))
    silenced = (_trial("candidate", 0, 8, 6, 90), _trial("candidate", 1, 15, 8, 180))
    summary = paired_trial_summary(baseline, silenced)
    assert isinstance(summary.mn9_l, PairedMetricSummary)
    assert summary.mn9_l.mean_delta == pytest.approx(-3.5)
    assert summary.mn9_l.median_delta == pytest.approx(-3.5)
    assert summary.total_network_spikes.minimum_delta == -20.0
    with pytest.raises(ValueError, match="identical trial indices"):
        paired_trial_summary(baseline, (_trial("candidate", 2, 8, 6, 90), _trial("candidate", 1, 15, 8, 180)))


def test_asymmetry_metric_handles_zero_denominator():
    assert asymmetry_metric(10.0, 2.0) == pytest.approx(8.0 / 12.0)
    assert asymmetry_metric(0.0, 0.0) is None


def test_task010_output_cannot_overwrite_task008(tmp_path):
    task008 = tmp_path / "task008-results.json"
    task008.write_text("{}", encoding="utf-8")
    ensure_separate_output(tmp_path / "task010-results.json", task008)
    with pytest.raises(ValueError, match="must not overwrite"):
        ensure_separate_output(task008, task008)


def test_cpu_gpu_silencing_equivalence_on_supported_runtime():
    try:
        from malecns_sim.dynamics.cuda import cuda_available, simulate_cuda_batch, upload_graph
    except Exception:
        pytest.skip("CUDA module unavailable")
    if not cuda_available():
        pytest.skip("CUDA device unavailable")
    projection = _projection(((1, 2, 100),))
    stimulus = ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0)
    cpu = simulate_lif(projection, duration_ms=2.1, stimulus=stimulus, silenced_neuron_ids=(1,))
    gpu = simulate_cuda_batch(
        projection,
        (stimulus,),
        duration_ms=2.1,
        parameters=LIFParameters(),
        silenced_neuron_ids=(1,),
        cuda_graph=upload_graph(projection)[0],
    )[0]
    assert np.array_equal(cpu.spike_neuron_ids, gpu.spike_neuron_ids)
    assert cpu.spike_result_digest == gpu.spike_result_digest
