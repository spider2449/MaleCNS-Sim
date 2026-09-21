"""Measure the Task 007c cache and CUDA gate on the local MaleCNS release."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from malecns_sim.analysis.task007 import build_task007_result
from malecns_sim.data.male_cns_v1 import (
    load_male_cns_v1_numeric,
    official_v1_mapping,
    project_numeric_connectome,
    select_publication_neuron_ids,
    threshold_curated_projection,
)
from malecns_sim.data.neurotransmitter import (
    NeurotransmitterResolutionPolicy,
    load_male_cns_v1_neurotransmitter_evidence,
)
from malecns_sim.data.provenance import read_manifest
from malecns_sim.dynamics import EffectiveSignedProjection, ExplicitStimulus, PoissonStimulus, SpikeSchedule
from malecns_sim.dynamics.cache import PreparedGraphCache, write_prepared_cache
from malecns_sim.dynamics.cuda import measure_memory, simulate_cuda, simulate_cuda_batch, upload_graph
from malecns_sim.dynamics.lif import simulate_lif
from malecns_sim.graph.signed import SignedAnatomicalConnectome
from malecns_sim.sign import Shiu2024SignPolicy
import pyarrow.feather as feather


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "male-cns" / "v1.0"
CACHE_PATH = ROOT / "data" / "derived" / "task007c" / "prepared-graph.npz"


def build_projection() -> EffectiveSignedProjection:
    annotation = DATA / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    neurotransmitter = DATA / "body-neurotransmitters-male-cns-v1.0.feather"
    weights = DATA / "connectome-weights-male-cns-v1.0-minconf-0.5.feather"
    selection = select_publication_neuron_ids(feather.read_table(annotation).to_pylist())
    numeric = load_male_cns_v1_numeric(annotation, neurotransmitter, weights, official_v1_mapping())
    curated = threshold_curated_projection(project_numeric_connectome(numeric, selection), min_synapses=5)
    evidence = load_male_cns_v1_neurotransmitter_evidence(annotation, neurotransmitter, curated_only=True)
    signed = SignedAnatomicalConnectome.from_projection(
        curated,
        evidence,
        NeurotransmitterResolutionPolicy(),
        Shiu2024SignPolicy(),
    )
    return EffectiveSignedProjection.from_signed_connectome(signed)


def elapsed(function):
    started = time.perf_counter()
    value = function()
    return value, time.perf_counter() - started


def main() -> None:
    result: dict[str, object] = {
        "release": read_manifest(ROOT / "data" / "provenance" / "male-cns-v1.0.json").release,
        "cache_path": str(CACHE_PATH),
    }
    if CACHE_PATH.exists():
        cache, warm_existing_seconds = elapsed(lambda: PreparedGraphCache.load(CACHE_PATH))
        projection = cache.to_projection()
        result["cold_preparation_seconds"] = "measured separately at 262.97 seconds"
        result["cache_write_seconds"] = "measured during initial cache build"
        result["existing_cache_load_seconds"] = warm_existing_seconds
    else:
        projection, cold_seconds = elapsed(build_projection)
        result["cold_preparation_seconds"] = cold_seconds
        cache, write_seconds = elapsed(
            lambda: write_prepared_cache(
                CACHE_PATH,
                projection,
                male_cns_release_identity="MaleCNS-v1.0",
                min_synapses=5,
            )
        )
        result["cache_write_seconds"] = write_seconds
    result["neuron_count"] = int(projection.neuron_ids.size)
    result["edge_count"] = int(projection.outgoing_targets.size)
    result["cache_size_bytes"] = CACHE_PATH.stat().st_size
    result["cache_fingerprint"] = cache.cache_fingerprint
    loaded, warm_seconds = elapsed(
        lambda: PreparedGraphCache.load(CACHE_PATH, expected_identity=cache.identity)
    )
    result["warm_cache_load_seconds"] = warm_seconds
    cached_projection = loaded.to_projection()

    import cupy as cp

    cp.get_default_memory_pool().free_all_blocks()
    free_before_graph, _ = cp.cuda.Device().mem_info
    graph, upload_seconds = upload_graph(cached_projection)
    free_after_graph, _ = cp.cuda.Device().mem_info
    result["gpu_graph_upload_seconds"] = upload_seconds
    result["gpu_graph_memory"] = {
        "free_before_bytes": int(free_before_graph),
        "free_after_bytes": int(free_after_graph),
        "allocated_delta_bytes": int(free_before_graph - free_after_graph),
        "theoretical_bytes": int(
            cached_projection.outgoing_indptr.nbytes
            + cached_projection.outgoing_targets.nbytes
            + cached_projection.outgoing_weights_mV.nbytes
        ),
    }
    memory_reports = {}
    for batch_size in (1, 4, 8, 16, 30):
        try:
            report = measure_memory(cached_projection, batch_size=batch_size, include_delay_buffers=True)
            memory_reports[str(batch_size)] = asdict(report)
        except Exception as exc:
            memory_reports[str(batch_size)] = {"error": type(exc).__name__, "message": str(exc)}
    result["memory_reports"] = memory_reports

    task007 = build_task007_result(
        DATA / "body-annotations-male-cns-v1.0-minconf-0.5.feather",
        DATA / "body-neurotransmitters-male-cns-v1.0.feather",
    )
    sugar_ids = tuple(
        int(value)
        for value in task007.sugar_population.candidate_body_ids
        if int(value) in set(cached_projection.neuron_ids.tolist())
    )
    if not sugar_ids:
        sugar_ids = (int(cached_projection.neuron_ids[0]),)
    explicit = PoissonStimulus(sugar_ids, rate_hz=100.0, weight_factor=250.0, seed=600100).generate(100.0, 0.1, 0.275)
    simulate_cuda(cached_projection, duration_ms=100.0, stimulus=explicit, cuda_graph=graph)
    cpu_100, cpu_100_seconds = elapsed(lambda: simulate_lif(cached_projection, duration_ms=100.0, stimulus=explicit))
    gpu_100, gpu_100_seconds = elapsed(lambda: simulate_cuda(cached_projection, duration_ms=100.0, stimulus=explicit, cuda_graph=graph))
    result["cpu_100ms_seconds"] = cpu_100_seconds
    result["gpu_100ms_seconds"] = gpu_100_seconds
    result["gpu_100ms_digest"] = gpu_100.spike_result_digest
    result["cpu_100ms_digest"] = cpu_100.spike_result_digest

    cpu_1000, cpu_1000_seconds = elapsed(lambda: simulate_lif(cached_projection, duration_ms=1000.0, stimulus=PoissonStimulus(sugar_ids, rate_hz=100.0, weight_factor=250.0, seed=600100)))
    gpu_1000, gpu_1000_seconds = elapsed(lambda: simulate_cuda(cached_projection, duration_ms=1000.0, stimulus=PoissonStimulus(sugar_ids, rate_hz=100.0, weight_factor=250.0, seed=600100), cuda_graph=graph))
    result["cpu_1000ms_seconds"] = cpu_1000_seconds
    result["gpu_1000ms_seconds"] = gpu_1000_seconds
    result["gpu_1000ms_digest"] = gpu_1000.spike_result_digest
    result["cpu_1000ms_digest"] = cpu_1000.spike_result_digest

    batch_results = {}
    for batch_size in (1, 4, 8, 16, 30):
        schedules = tuple(
            PoissonStimulus(sugar_ids, rate_hz=100.0, weight_factor=250.0, seed=600100).generate(100.0, 0.1, 0.275)
            for _ in range(batch_size)
        )
        try:
            simulate_cuda_batch(cached_projection, schedules, duration_ms=100.0, cuda_graph=graph)
            _, seconds = elapsed(lambda: simulate_cuda_batch(cached_projection, schedules, duration_ms=100.0, cuda_graph=graph))
            batch_results[str(batch_size)] = {"seconds": seconds, "trials_per_second": batch_size / seconds}
        except Exception as exc:
            batch_results[str(batch_size)] = {"error": type(exc).__name__, "message": str(exc)}
    result["gpu_batch_100ms"] = batch_results
    result["float32"] = "not attempted; float64 is the scientific gate mode"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
