import os
from pathlib import Path

import numpy as np
import pytest

from malecns_sim.data.model import CuratedNeuronProjection, NumericNormalizedConnectome
from malecns_sim.data.neurotransmitter import NeurotransmitterEvidence, NeurotransmitterResolutionPolicy
from malecns_sim.dynamics import (
    EffectiveSignedProjection,
    ExplicitStimulus,
    PreparedCacheIdentity,
    SpikeSchedule,
    PreparedGraphCache,
    simulate_lif,
    write_prepared_cache,
)
from malecns_sim.dynamics import cuda
from malecns_sim.dynamics.cuda import simulate_cuda, simulate_cuda_batch
from malecns_sim.graph.signed import SignedAnatomicalConnectome
from malecns_sim.sign import Shiu2024SignPolicy


def _projection(edges=((1, 2, 1), (1, 3, 1), (2, 3, 1))):
    labels = {1: "acetylcholine", 2: "gaba", 3: "acetylcholine", 4: "gaba"}
    ids = np.arange(1, max(labels) + 1, dtype=np.int64)
    source = np.asarray([edge[0] for edge in edges], dtype=np.int64)
    target = np.asarray([edge[1] for edge in edges], dtype=np.int64)
    counts = np.asarray([edge[2] for edge in edges], dtype=np.int64)
    connectome = NumericNormalizedConnectome(ids, source, target, counts)
    projection = CuratedNeuronProjection(connectome, len(edges), len(edges), len(edges), 0)
    evidence = [NeurotransmitterEvidence(neuron_id=i, consensus_nt=labels.get(i)) for i in ids]
    signed = SignedAnatomicalConnectome.from_projection(
        projection,
        evidence,
        NeurotransmitterResolutionPolicy(),
        Shiu2024SignPolicy(),
    )
    return EffectiveSignedProjection.from_signed_connectome(signed)


def _identity(projection):
    return PreparedCacheIdentity(
        male_cns_release_identity="male-cns-v1.0",
        curated_graph_fingerprint=projection.unsigned_graph_fingerprint,
        sign_policy_fingerprint=projection.signed_policy_fingerprint,
        unresolved_edge_policy=projection.resolution_policy_id,
        min_synapses=5,
        synaptic_weight_mV=projection.synaptic_weight_mV,
        lif_parameter_identity="shiu-reference-lif-parameters-v1",
    )


def test_prepared_cache_fingerprint_and_round_trip(tmp_path: Path):
    projection = _projection()
    path = tmp_path / "prepared.npz"
    written = write_prepared_cache(
        path,
        projection,
        male_cns_release_identity="male-cns-v1.0",
        min_synapses=5,
    )
    loaded = PreparedGraphCache.load(path, expected_identity=_identity(projection))
    restored = loaded.to_projection()
    assert loaded.cache_fingerprint == written.cache_fingerprint
    assert loaded.cache_fingerprint == PreparedGraphCache.load(path).cache_fingerprint
    assert restored.fingerprint == projection.fingerprint
    assert np.array_equal(restored.outgoing_indptr, projection.outgoing_indptr)
    assert np.array_equal(restored.outgoing_targets, projection.outgoing_targets)
    assert np.array_equal(restored.outgoing_weights_mV, projection.outgoing_weights_mV)


def test_prepared_cache_rejects_stale_identity(tmp_path: Path):
    projection = _projection()
    path = tmp_path / "prepared.npz"
    write_prepared_cache(path, projection, male_cns_release_identity="male-cns-v1.0", min_synapses=5)
    stale = PreparedCacheIdentity(
        male_cns_release_identity="male-cns-v1.1",
        curated_graph_fingerprint=projection.unsigned_graph_fingerprint,
        sign_policy_fingerprint=projection.signed_policy_fingerprint,
        unresolved_edge_policy=projection.resolution_policy_id,
        min_synapses=5,
        synaptic_weight_mV=projection.synaptic_weight_mV,
        lif_parameter_identity="shiu-reference-lif-parameters-v1",
    )
    with pytest.raises(ValueError, match="identity mismatch"):
        PreparedGraphCache.load(path, expected_identity=stale)


def test_cuda_module_imports_without_eager_cupy_dependency():
    assert hasattr(cuda, "simulate_cuda")


def _require_cuda():
    if not cuda.cuda_available():
        pytest.skip("CuPy or CUDA device is unavailable")


@pytest.mark.parametrize(
    "projection,stimulus,duration_ms",
    [
        (_projection(edges=()), ExplicitStimulus(), 1.0),
        (_projection(edges=()), ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=1.0), 0.2),
        (_projection(edges=()), ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=-1.0), 0.2),
        (_projection(edges=()), ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0), 0.2),
        (_projection(edges=()), ExplicitStimulus((SpikeSchedule(1, (0.0, 0.2, 2.3, 2.4)),), weight_mV=10.0), 2.5),
        (_projection(edges=((1, 2, 1),)), ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0), 2.1),
        (_projection(edges=((1, 1, 1),)), ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0), 2.1),
        (_projection(edges=((2, 1, 4),)), ExplicitStimulus((SpikeSchedule(2, (0.0,)),), weight_mV=10.0), 2.1),
        (_projection(edges=()), ExplicitStimulus((SpikeSchedule(1, (0.0, 0.0)), SpikeSchedule(2, (0.0,))), weight_mV=1.0), 0.2),
        (_projection(edges=((1, 2, 100), (2, 3, 100))), ExplicitStimulus((SpikeSchedule(1, (0.0,)),), weight_mV=10.0), 4.0),
    ],
)
def test_cuda_synthetic_equivalence(projection, stimulus, duration_ms):
    _require_cuda()
    cpu = simulate_lif(projection, duration_ms=duration_ms, stimulus=stimulus, trace_neuron_ids=(1, 2, 3))
    gpu = simulate_cuda(projection, duration_ms=duration_ms, stimulus=stimulus, trace_neuron_ids=(1, 2, 3))
    assert np.array_equal(gpu.spike_neuron_ids, cpu.spike_neuron_ids)
    assert np.array_equal(gpu.spike_timesteps, cpu.spike_timesteps)
    assert gpu.queued_synaptic_event_count == cpu.queued_synaptic_event_count
    assert gpu.delivered_synaptic_event_count == cpu.delivered_synaptic_event_count
    if cpu.trace_v_mV is not None:
        np.testing.assert_allclose(gpu.trace_v_mV, cpu.trace_v_mV, rtol=2e-13, atol=2e-13)
        np.testing.assert_allclose(gpu.trace_g_mV, cpu.trace_g_mV, rtol=2e-13, atol=2e-13)


def test_cuda_refractory_free_and_trial_isolation():
    _require_cuda()
    projection = _projection(edges=())
    blocked = ExplicitStimulus((SpikeSchedule(1, (0.0, 0.2)),), weight_mV=10.0)
    free = ExplicitStimulus((SpikeSchedule(1, (0.0, 0.2)),), weight_mV=10.0, refractory_free_neuron_ids=(1,))
    results = simulate_cuda_batch(projection, (blocked, free), duration_ms=0.4)
    assert results[0].spike_timesteps.tolist() == [1]
    assert results[1].spike_timesteps.tolist() == [1, 3]
    assert results[0].spike_result_digest == simulate_lif(projection, duration_ms=0.4, stimulus=blocked).spike_result_digest
    assert results[1].spike_result_digest == simulate_lif(projection, duration_ms=0.4, stimulus=free).spike_result_digest


@pytest.mark.skipif(os.environ.get("MALECNS_TASK007C_REAL") != "1", reason="set MALECNS_TASK007C_REAL=1 for the bounded full-graph gate")
def test_cuda_bounded_real_graph_equivalence():
    _require_cuda()
    from malecns_sim.data.male_cns_v1 import official_v1_mapping, project_numeric_connectome, threshold_curated_projection, load_male_cns_v1_numeric
    from malecns_sim.data.male_cns_v1 import select_publication_neuron_ids
    from malecns_sim.data.neurotransmitter import load_male_cns_v1_neurotransmitter_evidence

    root = Path("data/raw/male-cns/v1.0")
    annotation = root / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    neurotransmitter = root / "body-neurotransmitters-male-cns-v1.0.feather"
    weights = root / "connectome-weights-male-cns-v1.0-minconf-0.5.feather"
    import pyarrow.feather as feather

    selection = select_publication_neuron_ids(feather.read_table(annotation).to_pylist())
    numeric = load_male_cns_v1_numeric(annotation, neurotransmitter, weights, official_v1_mapping())
    projection = threshold_curated_projection(project_numeric_connectome(numeric, selection), min_synapses=5)
    signed = SignedAnatomicalConnectome.from_projection(
        projection,
        load_male_cns_v1_neurotransmitter_evidence(annotation, neurotransmitter, curated_only=True),
        NeurotransmitterResolutionPolicy(),
        Shiu2024SignPolicy(),
    )
    prepared = EffectiveSignedProjection.from_signed_connectome(signed)
    stimulus = ExplicitStimulus((SpikeSchedule(int(prepared.neuron_ids[0]), (0.0,)),), weight_mV=10.0)
    cpu = simulate_lif(prepared, duration_ms=10.0, stimulus=stimulus)
    gpu = simulate_cuda(prepared, duration_ms=10.0, stimulus=stimulus)
    repeat = simulate_cuda(prepared, duration_ms=10.0, stimulus=stimulus)
    assert np.array_equal(gpu.spike_neuron_ids, cpu.spike_neuron_ids)
    assert np.array_equal(gpu.spike_timesteps, cpu.spike_timesteps)
    assert gpu.spike_result_digest == repeat.spike_result_digest
