"""A022 public compatibility contract using bounded synthetic projections."""

import copy
from dataclasses import FrozenInstanceError, replace
import pickle
import numpy as np
import pytest

import malecns_sim as legacy
from malecns_sim import ExplicitStimulus, SpikeSchedule
from malecns_sim import runtime as api
from malecns_sim.dynamics.lif import PreparedRuntime as Engine, simulate_lif
from test_task005 import _projection
from test_application_a011 import stimulus


def snapshot(state):
    raw = state._state
    return raw.timestep, tuple(getattr(raw, name).tobytes() for name in
                               ('v_mV', 'g_mV', 'refractory_until', 'pending', 'pending_event_counts'))


def test_public_boundary_and_legacy_compatibility():
    assert api.__all__ == ['prepare_runtime', 'PreparedRuntime', 'SimulationState', 'AdvanceResult']
    for name in ('PreparedNetwork', 'schedule_events', 'AdvanceTiming', 'ArenaSession', 'GPUPreparedRuntime'):
        assert not hasattr(api, name)
    for name in legacy.__all__:
        assert getattr(legacy, name) is not None
    from malecns_sim.experimental import gpu
    assert gpu.__all__ == ['prepare_gpu_runtime', 'GPUPreparedRuntime', 'GPUSimulationState']
    for cls in (api.PreparedRuntime, api.SimulationState, api.AdvanceResult,
                gpu.GPUPreparedRuntime, gpu.GPUSimulationState):
        with pytest.raises(TypeError):
            cls()


def test_lifecycle_ownership_and_opaque_properties():
    runtime = api.prepare_runtime(_projection())
    other = api.prepare_runtime(_projection())
    a, b = runtime.initial_state(), runtime.initial_state()
    assert type(runtime) is api.PreparedRuntime and type(a) is api.SimulationState
    assert a is not b and a.timestep == b.timestep == 0 and a.time_ms == 0.0
    assert runtime.backend == 'cpu' and runtime.neuron_ids == (1, 2, 3, 4)
    assert runtime.projection_fingerprint == other.projection_fingerprint
    before = snapshot(a)
    with pytest.raises(ValueError):
        other.advance(a, duration_ms=1)
    assert snapshot(a) == before
    for obj, name in ((a, 'timestep'), (a, 'time_ms'), (runtime, 'dt_ms'), (runtime, 'neuron_ids')):
        with pytest.raises(AttributeError):
            setattr(obj, name, 1)
    for obj in (a, runtime):
        for operation in (copy.copy, copy.deepcopy, pickle.dumps):
            with pytest.raises(TypeError):
                operation(obj)
        for name in ('v_mV', 'projection', 'close', '__enter__'):
            assert not hasattr(obj, name)
    result = runtime.advance(a, duration_ms=0.3)
    assert type(result) is api.AdvanceResult and a.timestep == 3
    assert a.time_ms == 3 * runtime.dt_ms and b.timestep == 0
    assert snapshot(b) == before


@pytest.mark.parametrize('duration,category', [(0, ValueError), (-1, ValueError),
    (float('nan'), ValueError), (float('inf'), ValueError), (0.15, ValueError),
    (1e-12, ValueError), (1e30, ValueError), (10**500, ValueError),
    (True, TypeError), ('1', TypeError), (None, TypeError)])
def test_duration_atomicity(duration, category):
    runtime = api.prepare_runtime(_projection())
    state = runtime.initial_state()
    before = snapshot(state)
    with pytest.raises(category):
        runtime.advance(state, duration_ms=duration)
    assert snapshot(state) == before
    assert runtime.advance(state, duration_ms=0.1).end_timestep == 1


@pytest.mark.parametrize('events,category', [(np.zeros((1, 2)), TypeError), ({}, TypeError),
    (ExplicitStimulus((SpikeSchedule(99, ()),)), KeyError),
    (ExplicitStimulus(refractory_free_neuron_ids=(99,)), KeyError),
    (ExplicitStimulus((SpikeSchedule(1, (1.0,)),)), ValueError),
    (ExplicitStimulus((SpikeSchedule(1, (0.15,)),)), ValueError)])
def test_event_atomicity(events, category):
    runtime = api.prepare_runtime(_projection())
    state = runtime.initial_state()
    before = snapshot(state)
    with pytest.raises(category):
        runtime.advance(state, duration_ms=1, stimulus=events)
    assert snapshot(state) == before and state.timestep == 0
    runtime.advance(state, duration_ms=1)


def test_malformed_normalized_schedule_and_overflow():
    runtime = api.prepare_runtime(_projection())
    state = runtime.initial_state()
    bad = ExplicitStimulus()
    object.__setattr__(bad, 'schedules', (object(),))
    with pytest.raises(TypeError):
        runtime.advance(state, duration_ms=1, stimulus=bad)
    state._state.timestep = np.iinfo(np.int64).max - 1
    before = snapshot(state)
    with pytest.raises(ValueError):
        runtime.advance(state, duration_ms=0.1)
    assert snapshot(state) == before


def test_result_duplicates_endpoints_order_and_detachment():
    runtime = api.prepare_runtime(_projection())
    state = runtime.initial_state()
    events = ExplicitStimulus((SpikeSchedule(2, (0,)), SpikeSchedule(1, (0, 0))), weight_mV=4)
    first = runtime.advance(state, duration_ms=0.1, stimulus=events)
    assert first.spike_neuron_ids == (1,) and first.spike_timesteps == (1,)
    assert first.start_timestep == 0 and first.end_timestep == 1
    assert first.duration_ms == first.dt_ms == 0.1
    assert first.spike_times_ms == (0.1,) and first.emitted_spike_count == 1
    with pytest.raises(FrozenInstanceError):
        first.duration_ms = 3
    frozen_hash = hash(first)
    second = runtime.advance(state, duration_ms=0.1, stimulus=ExplicitStimulus(
        (SpikeSchedule(3, (0,)), SpikeSchedule(2, (0,))), weight_mV=30))
    assert second.spike_neuron_ids == (2, 3) and second.spike_timesteps == (2, 2)
    assert second.start_time_ms == first.end_time_ms == 0.1
    assert hash(first) == frozen_hash and first.spike_timesteps == (1,)
    empty = runtime.advance(state, duration_ms=0.1)
    assert empty.spike_neuron_ids == empty.spike_timesteps == ()


def test_exact_scientific_continuity_and_replay():
    projection = _projection(((1, 2, 100), (2, 3, 100), (3, 1, 20)))
    runtime = api.prepare_runtime(projection)
    reference = simulate_lif(projection, duration_ms=100, stimulus=stimulus(0, 100))
    whole = runtime.initial_state()
    whole_result = runtime.advance(whole, duration_ms=100, stimulus=stimulus(0, 100))
    chunked = runtime.initial_state()
    ids, times, start = (), (), 0
    for duration in (7, 13, 4, 26, 50):
        result = runtime.advance(chunked, duration_ms=duration, stimulus=stimulus(start, duration))
        ids += result.spike_neuron_ids
        times += result.spike_timesteps
        start += duration
    assert ids == whole_result.spike_neuron_ids == tuple(reference.spike_neuron_ids)
    assert times == whole_result.spike_timesteps == tuple(reference.spike_timesteps)
    assert snapshot(chunked) == snapshot(whole)


def test_factory_snapshot_alias_isolation_and_configuration():
    original = _projection(((1, 2, 100),))
    p = replace(original, neuron_ids=original.neuron_ids.copy(),
                outgoing_weights_mV=original.outgoing_weights_mV.copy())
    runtime = api.prepare_runtime(p)
    p.neuron_ids[:] = 99
    p.outgoing_weights_mV[:] = 0
    assert runtime.neuron_ids == (1, 2, 3, 4)
    expected = Engine(original).advance(Engine(original).initial_state(), duration_ms=10, stimulus=stimulus(0, 10))
    actual = runtime.advance(runtime.initial_state(), duration_ms=10, stimulus=stimulus(0, 10))
    assert actual.spike_timesteps == tuple(expected.spike_timesteps)
    for broken in (replace(original, neuron_ids=np.array([1, 1, 3])),
                   replace(original, neuron_ids=np.array([True, False, True])),
                   replace(original, outgoing_indptr=np.array([0, 2, 1, 1])),
                   replace(original, outgoing_weights_mV=np.array([float('nan')])),
                   replace(original, outgoing_targets=np.array([0]))):
        with pytest.raises(ValueError):
            api.prepare_runtime(broken)
    with pytest.raises(TypeError):
        api.prepare_runtime(object())
    with pytest.raises(TypeError):
        api.prepare_runtime(original, dt_ms='0.1')
    with pytest.raises(ValueError):
        api.prepare_runtime(original, dt_ms=0.3)


@pytest.mark.parametrize('phase', ['loop', 'output'])
def test_execution_and_output_failure_poison_only_one_state(monkeypatch, phase):
    runtime = api.prepare_runtime(_projection())
    state, sibling = runtime.initial_state(), runtime.initial_state()
    def fail(*args, **kwargs):
        raise MemoryError('injected internal failure')
    with monkeypatch.context() as patch:
        patch.setattr(Engine, 'advance', fail) if phase == 'loop' else patch.setattr(api, '_result', fail)
        with pytest.raises(MemoryError):
            runtime.advance(state, duration_ms=1)
    for operation in (lambda: state.timestep, lambda: state.time_ms,
                      lambda: runtime.advance(state, duration_ms=1)):
        with pytest.raises(RuntimeError):
            operation()
    assert runtime.advance(sibling, duration_ms=1).end_timestep == 10
    assert runtime.initial_state().timestep == 0


def test_preflight_allocation_failure_does_not_poison(monkeypatch):
    runtime = api.prepare_runtime(_projection())
    state = runtime.initial_state()
    def fail(*args, **kwargs):
        raise MemoryError()
    with monkeypatch.context() as patch:
        patch.setattr(api._events, 'schedule_events', fail)
        with pytest.raises(MemoryError):
            runtime.advance(state, duration_ms=1)
    assert state.timestep == 0
    runtime.advance(state, duration_ms=1)


def test_experimental_gpu_synthetic_semantics():
    from malecns_sim.experimental.gpu import prepare_gpu_runtime, GPUSimulationState
    from malecns_sim.dynamics.cuda import _cupy
    try:
        cp = _cupy()
        if cp.cuda.runtime.getDeviceCount() == 0:
            pytest.skip('no GPU')
    except (ImportError, RuntimeError):
        pytest.skip('optional GPU unavailable')
    runtime = prepare_gpu_runtime(_projection(((1, 2, 100),)))
    other = prepare_gpu_runtime(_projection(((1, 2, 100),)))
    a, b = runtime.initial_state(), runtime.initial_state()
    try:
        assert type(a) is GPUSimulationState and runtime.backend == 'gpu'
        with pytest.raises(ValueError):
            other.advance(a, duration_ms=1)
        with pytest.raises(ValueError):
            runtime.advance(a, duration_ms=0.15)
        assert a.timestep == b.timestep == 0
        result = runtime.advance(a, duration_ms=10, stimulus=stimulus(0, 10))
        cpu = api.prepare_runtime(_projection(((1, 2, 100),)))
        expected = cpu.advance(cpu.initial_state(), duration_ms=10, stimulus=stimulus(0, 10))
        assert result == expected and a.timestep == 100 and b.timestep == 0
        runtime.close()
        runtime.close()
        with pytest.raises(RuntimeError):
            runtime.advance(b, duration_ms=1)
    finally:
        a.close()
        b.close()
        runtime.close()
        other.close()
