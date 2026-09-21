"""Run the measured Task 008 conditions and write an ignored JSON artifact."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from malecns_sim.analysis.task008 import (
    DURATION_MS,
    MIRROR_CONDITION,
    PRIMARY_CONDITION,
    PRIMARY_FREQUENCIES_HZ,
    REFERENCE_V630_HZ,
    PreparedNetwork,
    load_task008_identities,
    normalized_rate,
    population_report,
    prepare_network,
    run_cpu_gpu_preflight,
    run_condition_trials,
    spearman_rank_association,
)


ROOT = Path(__file__).resolve().parents[1]
ANNOTATION = ROOT / "data/raw/male-cns/v1.0/body-annotations-male-cns-v1.0-minconf-0.5.feather"
NEUROTRANSMITTER = ROOT / "data/raw/male-cns/v1.0/body-neurotransmitters-male-cns-v1.0.feather"
WEIGHTS = ROOT / "data/raw/male-cns/v1.0/connectome-weights-male-cns-v1.0-minconf-0.5.feather"
OUTPUT = ROOT / "data/derived/task008-results.json"
FULL_CACHE = ROOT / "data/derived/task008/full-prepared-graph.npz"
THRESHOLD_CACHE = ROOT / "data/derived/task008/min-synapses-5-prepared-graph.npz"


def _condition_record(prepared: PreparedNetwork, summaries, trials, elapsed):
    return {
        "summaries": [asdict(item) for item in summaries],
        "trials": [asdict(item) for item in trials],
        "elapsed_seconds": elapsed,
        "fingerprint": prepared.fingerprint,
    }


def _prepared_record(prepared: PreparedNetwork):
    return {
        "graph_name": prepared.graph_name,
        "graph_loading_seconds": prepared.graph_loading_seconds,
        "preparation_seconds": prepared.preparation_seconds,
        "setup_seconds": prepared.setup_seconds,
        "memory_bytes": prepared.memory_bytes,
        "fingerprint": prepared.fingerprint,
        "cache_path": prepared.cache_path,
        "cache_fingerprint": prepared.cache_fingerprint,
        "backend": "cuda-float64" if prepared.cuda_graph is not None else "cpu",
        "unsigned_graph_fingerprint": prepared.signed_connectome.unsigned_graph_fingerprint,
        "signed_policy_fingerprint": prepared.projection.signed_policy_fingerprint,
        "effective_projection_fingerprint": prepared.projection.fingerprint,
        "neuron_count": int(prepared.projection.neuron_ids.size),
        "edge_count": int(prepared.projection.target_positions.size),
    }


def main() -> None:
    identities = load_task008_identities(ANNOTATION, NEUROTRANSMITTER)
    full = prepare_network(
        ANNOTATION,
        NEUROTRANSMITTER,
        WEIGHTS,
        graph_name="full",
        cache_path=FULL_CACHE,
        use_cuda=True,
    )
    left_report = population_report("sugar_left", identities.sugar_left, identities.candidates, full.signed_connectome)
    right_report = population_report("sugar_right", identities.sugar_right, identities.candidates, full.signed_connectome)
    preflight = run_cpu_gpu_preflight(
        full,
        identities.sugar_left,
        experiment_identity=identities.fingerprint,
        side="L",
    )
    primary_summaries, primary_trials, primary_elapsed = run_condition_trials(
        full,
        PRIMARY_CONDITION,
        identities.sugar_left,
        PRIMARY_FREQUENCIES_HZ,
        experiment_identity=identities.fingerprint,
        side="L",
    )
    repeat_summaries, repeat_trials, repeat_elapsed = run_condition_trials(
        full,
        PRIMARY_CONDITION,
        identities.sugar_left,
        (100.0,),
        experiment_identity=identities.fingerprint,
        side="L",
    )
    mirror_summaries, mirror_trials, mirror_elapsed = run_condition_trials(
        full,
        MIRROR_CONDITION,
        identities.sugar_right,
        (100.0,),
        experiment_identity=identities.fingerprint,
        side="R",
    )
    normalized_summaries, normalized_trials, normalized_elapsed = run_condition_trials(
        full,
        PRIMARY_CONDITION,
        identities.sugar_left,
        (100.0,),
        experiment_identity=identities.fingerprint + ":normalized-input",
        side="L",
        rate_multiplier=normalized_rate(100.0, len(identities.sugar_left.candidate_body_ids)) / 100.0,
    )
    threshold = prepare_network(
        ANNOTATION,
        NEUROTRANSMITTER,
        WEIGHTS,
        graph_name="min_synapses=5",
        min_synapses=5,
        cache_path=THRESHOLD_CACHE,
        use_cuda=True,
    )
    threshold_summaries, threshold_trials, threshold_elapsed = run_condition_trials(
        threshold,
        PRIMARY_CONDITION,
        identities.sugar_left,
        (100.0,),
        experiment_identity=identities.fingerprint + ":min_synapses=5",
        side="L",
    )
    primary_curve = [item.contralateral_mean_hz for item in primary_summaries]
    differences = [actual - reference for actual, reference in zip(primary_curve, REFERENCE_V630_HZ)]
    primary_100_trials = [item for item in primary_trials if item.frequency_hz == 100.0]
    repeat_determinism = {
        "repeat_digest_equal": repeat_summaries[0].result_digest
        == next(item for item in primary_summaries if item.frequency_hz == 100.0).result_digest,
        "repeat_trial_digests_equal": [
            left.result_digest == right.result_digest
            for left, right in zip(repeat_trials, primary_100_trials)
        ],
        "repeat_mn9_rates_equal": [
            (left.contralateral_spikes, left.ipsilateral_spikes)
            == (right.contralateral_spikes, right.ipsilateral_spikes)
            for left, right in zip(repeat_trials, primary_100_trials)
        ],
        "repeat_total_spike_counts_equal": [
            left.total_network_spikes == right.total_network_spikes
            for left, right in zip(repeat_trials, primary_100_trials)
        ],
    }
    if not all(
        [repeat_determinism["repeat_digest_equal"]]
        + repeat_determinism["repeat_trial_digests_equal"]
        + repeat_determinism["repeat_mn9_rates_equal"]
        + repeat_determinism["repeat_total_spike_counts_equal"]
    ):
        raise RuntimeError("Task 008 deterministic repeat gate failed")
    result = {
        "identities": asdict(identities),
        "experiment_fingerprint": identities.fingerprint,
        "population_reports": {"left": asdict(left_report), "right": asdict(right_report)},
        "full_prepared": _prepared_record(full),
        "threshold_prepared": _prepared_record(threshold),
        "preflight": preflight,
        "primary": _condition_record(full, primary_summaries, primary_trials, primary_elapsed),
        "repeat_100hz": _condition_record(full, repeat_summaries, repeat_trials, repeat_elapsed),
        "mirror_100hz": _condition_record(full, mirror_summaries, mirror_trials, mirror_elapsed),
        "normalized_100hz": _condition_record(full, normalized_summaries, normalized_trials, normalized_elapsed),
        "min_synapses_5_100hz": _condition_record(threshold, threshold_summaries, threshold_trials, threshold_elapsed),
        "reference_v630_hz": list(REFERENCE_V630_HZ),
        "primary_frequency_difference_hz": differences,
        "primary_spearman": spearman_rank_association(primary_curve, REFERENCE_V630_HZ),
        "determinism": repeat_determinism,
        "parameters": {
            "duration_ms": DURATION_MS,
            "dt_ms": 0.1,
            "v_rest_mV": -52.0,
            "v_reset_mV": -52.0,
            "v_threshold_mV": -45.0,
            "tau_membrane_ms": 20.0,
            "tau_synapse_ms": 5.0,
            "refractory_ms": 2.2,
            "delay_ms": 1.8,
            "synaptic_weight_mV": 0.275,
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "primary": [asdict(item) for item in primary_summaries], "mirror": [asdict(item) for item in mirror_summaries], "normalized": [asdict(item) for item in normalized_summaries], "threshold": [asdict(item) for item in threshold_summaries]}, indent=2, default=str))


if __name__ == "__main__":
    main()
