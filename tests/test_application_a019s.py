"""Bounded synthetic GPU self-continuity; no application equivalence claim."""

from dataclasses import replace
import hashlib

import numpy as np
import pytest

from malecns_sim.dynamics import cuda
from malecns_sim.dynamics.cuda import GPUPreparedRuntime
from malecns_sim.dynamics.lif import EffectiveSignedProjection, REFERENCE_LIF_PARAMETERS
from malecns_sim.dynamics.stimulus import ExplicitStimulus, SpikeSchedule


FIELDS = ("v_mV", "g_mV", "refractory_until", "pending", "pending_event_counts")


def projection(edges=()):
    """Construct only in-memory synthetic CSR, retaining duplicate edge order."""
    edges = sorted(edges, key=lambda edge: edge[0])
    sources = np.asarray([edge[0] for edge in edges], dtype=np.int64)
    targets = np.asarray([edge[1] for edge in edges], dtype=np.int64)
    weights = np.asarray([edge[2] for edge in edges], dtype=np.float64)
    pointers = np.concatenate(([0], np.cumsum(np.bincount(sources, minlength=4))))
    fingerprint = hashlib.sha256(repr(edges).encode()).hexdigest()
    return EffectiveSignedProjection(
        np.arange(1, 5, dtype=np.int64), sources, targets, weights,
        len(edges), 0, 0, 0.275, "synthetic", "synthetic", fingerprint,
        fingerprint, fingerprint, pointers, targets, weights)


def events(entries=(), weight=10.0, free=(), offset=0, end=None):
    schedules = tuple(SpikeSchedule(neuron, ((step - offset) * 0.1,))
                      for neuron, step in entries
                      if step >= offset and (end is None or step < end))
    return ExplicitStimulus(schedules, weight_mV=weight, refractory_free_neuron_ids=free)


def snapshot(state):
    import cupy as cp
    state._backing.stream.synchronize()
    return {name: cp.asnumpy(getattr(state, name)) for name in FIELDS}


def assert_snapshot_equal(left, right):
    for name in FIELDS:
        assert left[name].shape == right[name].shape
        assert left[name].dtype == right[name].dtype
        # Byte equality includes signed zero, not only numeric equality.
        assert left[name].tobytes() == right[name].tobytes(), name


CASES = [
    ("S1-empty", (), (), 1.0, (), (10, 10), None),
    ("S2-direct", (), ((1, 0),), 1.0, (), (10, 10), None),
    ("S3-delayed", ((0, 1, 0.275),), ((1, 0),), 10.0, (), (10, 10), None),
    ("conductance-retained", ((0, 1, 0.275),), ((1, 0),), 10.0, (), (20, 10, 10), None),
    ("S4-pending", ((0, 1, 0.275),), ((1, 0),), 10.0, (), (10, 5), None),
    ("S5-refractory", (), ((1, 0), (1, 10), (1, 23), (1, 24)), 10.0, (), (10, 14, 6), None),
    ("S7-repeated", ((0, 1, 27.5), (1, 2, -1.1), (2, 0, 27.5)),
     ((1, 0), (1, 25), (3, 40), (2, 66)), 10.0, (), (7, 13, 4, 26, 50), None),
    ("S9-output-S12-duplicates", ((0, 2, 1e16), (0, 2, 1.0), (1, 2, -1e16)),
     ((2, 0), (1, 0), (1, 0), (2, 0), (1, 2)), 10.0, (1, 2), (10, 20), None),
    ("zero-delay", ((0, 1, 0.275),), ((1, 0),), 10.0, (), (1, 1, 3),
     replace(REFERENCE_LIF_PARAMETERS, synaptic_delay_ms=0.0)),
    ("equal-tau", ((0, 1, 0.275),), ((1, 0),), 10.0, (), (10, 10),
     replace(REFERENCE_LIF_PARAMETERS, tau_synapse_ms=20.0)),
    ("near-equal-tau", ((0, 1, 0.275),), ((1, 0),), 10.0, (), (10, 10),
     replace(REFERENCE_LIF_PARAMETERS, tau_synapse_ms=20.00001)),
    ("near-threshold", (), ((1, 0),),
     float((REFERENCE_LIF_PARAMETERS.v_threshold_mV - REFERENCE_LIF_PARAMETERS.v_rest_mV)
           / np.exp(-0.1 / REFERENCE_LIF_PARAMETERS.tau_membrane_ms)), (), (1, 1, 2), None),
]


@pytest.mark.parametrize("name,edges,entries,weight,free,chunks,parameters", CASES,
                         ids=[case[0] for case in CASES])
def test_gpu_whole_vs_chunks_exact(name, edges, entries, weight, free, chunks, parameters, monkeypatch):
    runtime = GPUPreparedRuntime(projection(edges), parameters or REFERENCE_LIF_PARAMETERS)
    state, whole = runtime.initial_state(), runtime.initial_state()
    total = sum(chunks)
    reference = runtime.advance(whole, duration_ms=total * 0.1,
                                stimulus=events(entries, weight, free), trace_neuron_ids=(1, 2, 3, 4))
    graph = runtime._lifetime.backing.graph
    static_before = [cuda._cupy().asnumpy(array) for array in
                     (graph.indptr, graph.indices, graph.weights_mV,
                      state._backing.incoming_offsets, state._backing.incoming_sources,
                      state._backing.incoming_ordinals)]
    pointers = [getattr(state, field).data.ptr for field in FIELDS]
    backing = state._backing
    results, offset = [], 0
    first_snapshot = None
    for chunk in chunks:
        result = runtime.advance(state, duration_ms=chunk * 0.1,
                                 stimulus=events(entries, weight, free, offset, offset + chunk),
                                 trace_neuron_ids=(1, 2, 3, 4))
        results.append(result)
        offset += chunk
        assert state.timestep == offset
        assert state._backing is backing
        assert [getattr(state, field).data.ptr for field in FIELDS] == pointers
        # Independent whole-prefix state proves every boundary, including rings.
        prefix = runtime.initial_state()
        runtime.advance(prefix, duration_ms=offset * 0.1,
                        stimulus=events(entries, weight, free, 0, offset))
        assert_snapshot_equal(snapshot(state), snapshot(prefix))
        prefix.close()
        if first_snapshot is None:
            first_snapshot = snapshot(state)
    assert_snapshot_equal(snapshot(state), snapshot(whole))
    for field in ("spike_neuron_ids", "spike_timesteps"):
        np.testing.assert_array_equal(np.concatenate([getattr(r, field) for r in results]), getattr(reference, field))
    np.testing.assert_array_equal(sum(r.spike_counts for r in results), reference.spike_counts)
    for field in ("trace_v_mV", "trace_g_mV"):
        combined = np.concatenate([getattr(results[0], field)] +
                                  [getattr(r, field)[:, 1:] for r in results[1:]], axis=1)
        assert combined.tobytes() == getattr(reference, field).tobytes()
    for field in ("queued_synaptic_event_count", "delivered_synaptic_event_count"):
        assert sum(getattr(r, field) for r in results) == getattr(reference, field)
    static_after = [cuda._cupy().asnumpy(array) for array in
                    (graph.indptr, graph.indices, graph.weights_mV,
                     backing.incoming_offsets, backing.incoming_sources, backing.incoming_ordinals)]
    for before, after in zip(static_before, static_after):
        assert before.tobytes() == after.tobytes()
    if name in ("S3-delayed", "S4-pending"):
        assert first_snapshot["pending_event_counts"][0, 1] == 1
        assert first_snapshot["pending"][0, 1] == 0.275
        assert results[0].delivered_synaptic_event_count == 0
        if name == "S3-delayed":
            assert results[1].delivered_synaptic_event_count == 1
            assert snapshot(state)["g_mV"][1] > 0
        else:
            assert snapshot(state)["pending_event_counts"][0, 1] == 1
    if name == "S5-refractory":
        assert first_snapshot["refractory_until"][0] == 23
        assert reference.spike_timesteps.tolist() == [1, 25]
    if name == "S2-direct":
        assert first_snapshot["v_mV"][0] > runtime.parameters.v_rest_mV
    if name == "conductance-retained":
        assert first_snapshot["g_mV"][1] > 0
    if name == "zero-delay":
        assert first_snapshot["pending_event_counts"][0, 1] == 1
        assert results[0].delivered_synaptic_event_count == 0
        assert results[1].delivered_synaptic_event_count == 1
    if name == "S9-output-S12-duplicates":
        assert first_snapshot["pending_event_counts"][0, 2] == 3
        assert first_snapshot["pending"][0, 2] == 0.0
        assert results[0].spike_neuron_ids[:2].tolist() == [1, 2]
    # Neither a new state nor a graph/runtime may be created by advance.
    monkeypatch.setattr(GPUPreparedRuntime, "initial_state", lambda *_: pytest.fail("hidden new state"))
    monkeypatch.setattr(GPUPreparedRuntime, "__post_init__", lambda *_: pytest.fail("hidden new runtime"))
    monkeypatch.setattr(cuda, "CudaGraph", lambda *_: pytest.fail("hidden graph upload"))
    runtime.advance(state, duration_ms=0.1)
    state.close()
    whole.close()
    runtime.close()


def test_S6_S8_S10_isolation_and_release():
    runtime = GPUPreparedRuntime(projection(((0, 1, 0.275),)))
    a, b = runtime.initial_state(), runtime.initial_state()
    for field in FIELDS:
        assert getattr(a, field).data.ptr != getattr(b, field).data.ptr
    quiet = snapshot(b)
    runtime.advance(a, duration_ms=1.0, stimulus=events(((1, 0),)))
    assert_snapshot_equal(quiet, snapshot(b))
    runtime.advance(b, duration_ms=1.0, stimulus=events(((2, 0),)))
    saved_output = runtime.advance(a, duration_ms=0.1, trace_neuron_ids=(1,))
    output_bytes = saved_output.trace_v_mV.tobytes()
    backing = b._backing
    a.close()
    a.close()
    assert a.status == "released" and a.pending is None
    assert b._backing is backing and runtime._lifetime.backing is backing
    with pytest.raises((ValueError, RuntimeError), match="released"):
        runtime.advance(a, duration_ms=0.1)
    runtime.advance(b, duration_ms=2.0)
    assert b.timestep == 30
    assert saved_output.trace_v_mV.tobytes() == output_bytes
    for array in (saved_output.trace_v_mV, saved_output.trace_g_mV, saved_output.spike_counts,
                  saved_output.trace_neuron_ids, saved_output.spike_timesteps):
        assert not array.flags.writeable
    runtime.close()
    assert b._backing is backing
    with pytest.raises(RuntimeError, match="closed"):
        runtime.initial_state()
    with pytest.raises(RuntimeError, match="closed"):
        runtime.advance(b, duration_ms=0.1)
    b.close()


@pytest.mark.parametrize("stimulus,duration,error", [
    (events(((1, 10),)), 1.0, ValueError),
    (events(((99, 0),)), 1.0, KeyError),
    (ExplicitStimulus((SpikeSchedule(1, (0.05,)),)), 1.0, ValueError),
    (events(), 0.15, ValueError), (events(), 0.0, ValueError),
    ([], 1.0, TypeError),
])
def test_S11_validation_before_mutation(stimulus, duration, error):
    runtime = GPUPreparedRuntime(projection())
    state = runtime.initial_state()
    before = snapshot(state)
    with pytest.raises(error):
        runtime.advance(state, duration_ms=duration, stimulus=stimulus)
    assert state.timestep == 0 and state.status == "ready"
    assert_snapshot_equal(before, snapshot(state))
    # Last grid point before endpoint is accepted; endpoint rejected above.
    result = runtime.advance(state, duration_ms=1.0, stimulus=events(((1, 9),)))
    assert result.spike_timesteps.tolist() == [10]
    state.close()
    runtime.close()


def test_runtime_device_overflow_and_failed_state(monkeypatch):
    runtime, other = GPUPreparedRuntime(projection()), GPUPreparedRuntime(projection())
    state = runtime.initial_state()
    with pytest.raises(ValueError, match="another"):
        other.advance(state, duration_ms=0.1)
    state.device_id += 1
    with pytest.raises(ValueError, match="device"):
        runtime.advance(state, duration_ms=0.1)
    state.device_id -= 1
    state.timestep = np.iinfo(np.int64).max
    with pytest.raises(ValueError, match="int64"):
        runtime.advance(state, duration_ms=0.1)
    state.timestep = 0
    with state._backing.lock:
        with pytest.raises(RuntimeError, match="busy"):
            runtime.advance(state, duration_ms=0.1)
    def partial_failure(self, state, *args):
        state.v_mV.fill(42.0)
        raise RuntimeError("injected execution failure")
    monkeypatch.setattr(GPUPreparedRuntime, "_advance_device", partial_failure)
    with pytest.raises(RuntimeError, match="injected"):
        runtime.advance(state, duration_ms=0.1)
    assert state.status == "failed" and state.timestep == 0
    with pytest.raises(RuntimeError, match="failed"):
        runtime.advance(state, duration_ms=0.1)
    state.close()
    runtime.close()
    other.close()


def test_duplicate_multiplicity_is_single_multiplication():
    runtime = GPUPreparedRuntime(projection())
    a, b = runtime.initial_state(), runtime.initial_state()
    repeated = events(((1, 0),) * 10, weight=0.1)
    runtime.advance(a, duration_ms=0.1, stimulus=repeated)
    runtime.advance(b, duration_ms=0.1, stimulus=events(((1, 0),), weight=1.0))
    assert_snapshot_equal(snapshot(a), snapshot(b))
    a.close()
    b.close()
    runtime.close()


def test_fatal_failure_poisoning_and_wrong_current_device(monkeypatch):
    runtime = GPUPreparedRuntime(projection())
    a, b = runtime.initial_state(), runtime.initial_state()
    cp = cuda._cupy()
    original_device = cp.cuda.runtime.getDevice
    monkeypatch.setattr(cp.cuda.runtime, "getDevice", lambda: runtime.device_id + 1)
    with pytest.raises(ValueError, match="device"):
        runtime.advance(a, duration_ms=0.1)
    assert a.status == "ready" and a.timestep == 0
    monkeypatch.setattr(cp.cuda.runtime, "getDevice", original_device)
    class FatalError(RuntimeError):
        status = 700
    def fail(self, state, *args):
        raise FatalError("synthetic fatal context failure")
    monkeypatch.setattr(GPUPreparedRuntime, "_advance_device", fail)
    with pytest.raises(FatalError):
        runtime.advance(a, duration_ms=0.1)
    assert a.status == "failed" and a.timestep == 0
    with pytest.raises(RuntimeError, match="failed"):
        runtime.advance(b, duration_ms=0.1)
    with pytest.raises(RuntimeError, match="failed"):
        runtime.initial_state()
    a.close()
    b.close()
    runtime.close()


def test_sync_failure_invalidates_without_publishing_time(monkeypatch):
    runtime = GPUPreparedRuntime(projection())
    state = runtime.initial_state()
    backing = state._backing
    class FailingSync:
        def __enter__(self):
            return backing.stream.__enter__()
        def __exit__(self, *args):
            return backing.stream.__exit__(*args)
        def synchronize(self):
            raise RuntimeError("synthetic synchronization failure")
    replacement = replace(backing, stream=FailingSync())
    state._backing = runtime._lifetime.backing = replacement
    with pytest.raises(RuntimeError, match="synchronization"):
        runtime.advance(state, duration_ms=0.1)
    assert state.status == "failed" and state.timestep == 0
    with pytest.raises(RuntimeError, match="failed"):
        runtime.advance(state, duration_ms=0.1)
    state._backing = runtime._lifetime.backing = backing
    state.close()
    runtime.close()


def test_initial_allocation_failure_preserves_runtime_and_sibling(monkeypatch):
    runtime = GPUPreparedRuntime(projection())
    state = runtime.initial_state()
    before = snapshot(state)
    cp = cuda._cupy()
    original = cp.zeros
    def fail(*args, **kwargs):
        raise MemoryError("synthetic allocation failure")
    monkeypatch.setattr(cp, "zeros", fail)
    with pytest.raises(MemoryError, match="allocation"):
        runtime.initial_state()
    assert not runtime._lifetime.failed
    assert_snapshot_equal(before, snapshot(state))
    monkeypatch.setattr(cp, "zeros", original)
    sibling = runtime.initial_state()
    runtime.advance(state, duration_ms=0.1)
    state.close()
    sibling.close()
    runtime.close()


@pytest.mark.parametrize("time", [-0.1, float("nan"), float("inf")])
def test_invalid_event_values_rejected_by_shared_payload_contract(time):
    with pytest.raises(ValueError):
        SpikeSchedule(1, (time,))


@pytest.mark.parametrize("bad", [
    {"outgoing_targets": np.asarray([np.iinfo(np.int32).max], dtype=np.int64),
     "outgoing_indptr": np.asarray([0, 1, 1, 1, 1], dtype=np.int64),
     "outgoing_weights_mV": np.asarray([0.275])},
    {"outgoing_indptr": np.asarray([0, -1, 0, 0, 0], dtype=np.int64)},
    {"synaptic_weight_mV": 0.5},
])
def test_invalid_static_contract_rejected(bad):
    with pytest.raises(ValueError):
        GPUPreparedRuntime(replace(projection(), **bad))


@pytest.mark.parametrize("edges,entries", [
    ((), ()), ((), ((1, 0),)), (((0, 1, 0.275),), ((1, 0),)),
])
def test_legacy_gpu_small_valid_reference(edges, entries):
    p = projection(edges)
    stimulus = events(entries)
    old = cuda.simulate_cuda(p, duration_ms=3.0, stimulus=stimulus, trace_neuron_ids=(1, 2))
    runtime = GPUPreparedRuntime(p)
    state = runtime.initial_state()
    new = runtime.advance(state, duration_ms=3.0, stimulus=stimulus, trace_neuron_ids=(1, 2))
    for field in ("spike_neuron_ids", "spike_timesteps", "spike_counts"):
        np.testing.assert_array_equal(getattr(old, field), getattr(new, field))
    assert old.queued_synaptic_event_count == new.queued_synaptic_event_count
    assert old.delivered_synaptic_event_count == new.delivered_synaptic_event_count
    for field in ("trace_v_mV", "trace_g_mV"):
        np.testing.assert_allclose(getattr(old, field), getattr(new, field), rtol=2e-13, atol=2e-13)
    state.close()
    runtime.close()
