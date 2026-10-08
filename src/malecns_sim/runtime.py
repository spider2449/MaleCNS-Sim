"""Stable CPU prepare-once/advance-many API for already resolved projections.

Durations and input times are grid-aligned milliseconds. Input is chunk-local
and excludes the endpoint; output steps are absolute and include the endpoint.
Use sequential, process-local calls. CPU resources follow reference/GC lifetime.
Execution failure invalidates only the supplied state, without rollback.
"""

from dataclasses import dataclass as _dataclass, fields as _fields, replace as _replace
import math as _math
import numpy as _np
from malecns_sim.dynamics import lif as _lif
from malecns_sim.dynamics import stimulus as _events

__all__ = ["prepare_runtime", "PreparedRuntime", "SimulationState", "AdvanceResult"]

_LIMIT = int(_np.iinfo(_np.int64).max)


def _number(value, name):
    if type(value) not in (int, float):
        raise TypeError(f"{name} requires a Python int or float")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} is out of range") from exc
    if not _math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _steps(value, dt, name):
    ratio = value / dt
    if not _math.isfinite(ratio) or ratio > _LIMIT:
        raise ValueError(f"{name} exceeds timestep bounds")
    return _lif._exact_steps(value, dt, name)


def _snapshot(projection, parameters, dt_ms):
    if not isinstance(projection, _lif.EffectiveSignedProjection):
        raise TypeError("projection requires EffectiveSignedProjection")
    if not isinstance(parameters, _lif.LIFParameters):
        raise TypeError("parameters requires LIFParameters")
    parameters = _lif.LIFParameters(**{f.name: _number(getattr(parameters, f.name), f.name)
                                     for f in _fields(parameters)})
    dt = _number(dt_ms, "dt_ms")
    if dt <= 0:
        raise ValueError("dt_ms must be positive")
    for value in (parameters.synaptic_delay_ms, parameters.refractory_period_ms):
        if _steps(value, dt, "model interval") >= _LIMIT:
            raise ValueError("model interval exceeds timestep bounds")
    weight = _number(projection.synaptic_weight_mV, "synaptic weight")
    if not _np.isclose(weight, parameters.synaptic_weight_per_anatomical_synapse_mV,
                       rtol=0, atol=1e-15):
        raise ValueError("projection and parameter weights disagree")
    arrays = {}
    integer = ("neuron_ids", "source_positions", "target_positions", "outgoing_indptr", "outgoing_targets")
    for name in integer + ("effective_weights_mV", "outgoing_weights_mV"):
        raw = getattr(projection, name)
        if not isinstance(raw, _np.ndarray):
            raise TypeError("projection execution structures require arrays")
        if raw.ndim != 1 or raw.dtype.kind not in ("iu" if name in integer else "iuf"):
            raise ValueError("invalid projection array shape or kind")
        if not _np.all(_np.isfinite(raw)) or (name in integer and _np.any(raw > _LIMIT)):
            raise ValueError("invalid projection array values")
        array = _np.array(raw, dtype=_np.int64 if name in integer else _np.float64, copy=True)
        array.flags.writeable = False
        arrays[name] = array
    ids, src, dst = (arrays[n] for n in ("neuron_ids", "source_positions", "target_positions"))
    weights, ptr, targets, outgoing = (arrays[n] for n in
                                      ("effective_weights_mV", "outgoing_indptr", "outgoing_targets", "outgoing_weights_mV"))
    n, e = ids.size, src.size
    if (any(int(a) >= int(b) for a, b in zip(ids, ids[1:]))
            or dst.size != e or weights.size != e or targets.size != e or outgoing.size != e
            or _np.any(src < 0) or _np.any(src >= n) or _np.any(dst < 0) or _np.any(dst >= n)
            or ptr.shape != (n + 1,) or ptr[0] != 0 or ptr[-1] != e
            or _np.any(ptr < 0) or _np.any(ptr > e) or _np.any(ptr[1:] < ptr[:-1])):
        raise ValueError("invalid projection topology")
    if (not _np.array_equal(src, _np.repeat(_np.arange(n), _np.diff(ptr)))
            or not _np.array_equal(dst, targets) or not _np.array_equal(weights, outgoing)):
        raise ValueError("projection edge and CSR structures disagree")
    for name in ("fingerprint", "unsigned_graph_fingerprint", "signed_policy_fingerprint",
                 "sign_policy_id", "resolution_policy_id"):
        if not isinstance(getattr(projection, name), str):
            raise TypeError("projection identities require strings")
    return _replace(projection, **arrays), parameters, dt


class _Opaque:
    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        raise TypeError("use the runtime factory or runtime methods")

    def __copy__(self):
        raise TypeError("runtime handles cannot be copied")

    def __deepcopy__(self, memo):
        raise TypeError("runtime handles cannot be copied")

    def __reduce_ex__(self, protocol):
        raise TypeError("runtime handles cannot be serialized")


class SimulationState(_Opaque):
    """Opaque exact-owner trajectory; inspect only timestep and time_ms.

    Failed-state inspection raises RuntimeError. Request a fresh state to reset.
    """
    __slots__ = ("_owner", "_state", "_failed")

    @property
    def timestep(self):
        if self._failed:
            raise RuntimeError("state is poisoned")
        return int(self._state.timestep)

    @property
    def time_ms(self):
        return self.timestep * self._owner.dt_ms


@_dataclass(frozen=True, slots=True, init=False)
class AdvanceResult:
    """Immutable detached chunk output, ordered by timestep then neuron ID."""
    start_timestep: int
    end_timestep: int
    dt_ms: float
    duration_ms: float
    spike_neuron_ids: tuple[int, ...]
    spike_timesteps: tuple[int, ...]

    def __new__(cls, *args, **kwargs):
        raise TypeError("results are produced by advance")

    @property
    def start_time_ms(self):
        return self.start_timestep * self.dt_ms

    @property
    def end_time_ms(self):
        return self.end_timestep * self.dt_ms

    @property
    def spike_times_ms(self):
        return tuple(step * self.dt_ms for step in self.spike_timesteps)

    @property
    def emitted_spike_count(self):
        return len(self.spike_timesteps)


def _result(raw, start, steps, dt):
    result = object.__new__(AdvanceResult)
    values = (start, start + steps, dt, steps * dt,
              tuple(int(i) for i in raw.spike_neuron_ids),
              tuple(int(i) for i in raw.spike_timesteps))
    for name, value in zip((f.name for f in _fields(AdvanceResult)), values):
        object.__setattr__(result, name, value)
    return result


def _preflight(runtime, state, duration_ms, stimulus):
    if type(state) is not runtime._state_type:
        raise TypeError("state requires this backend's public state handle")
    if state._owner is not runtime:
        raise ValueError("state belongs to another runtime")
    start = state.timestep
    duration = _number(duration_ms, "duration_ms")
    if duration <= 0:
        raise ValueError("duration_ms must be positive")
    steps = _steps(duration, runtime.dt_ms, "duration")
    delay, refractory = runtime._engine.parameters.grid_steps(runtime.dt_ms)
    if steps < 1 or start + steps + max(delay, refractory) > _LIMIT:
        raise ValueError("duration exceeds timestep bounds")
    if not _math.isfinite((start + steps) * runtime.dt_ms):
        raise ValueError("end time is out of range")
    if not isinstance(stimulus, _events.ExplicitStimulus):
        raise TypeError("stimulus requires ExplicitStimulus")
    if type(stimulus.schedules) is not tuple or type(stimulus.refractory_free_neuron_ids) is not tuple:
        raise TypeError("malformed stimulus")
    if stimulus.weight_mV is not None:
        _number(stimulus.weight_mV, "weight_mV")
    for schedule in stimulus.schedules:
        if not isinstance(schedule, _events.SpikeSchedule) or type(schedule.neuron_id) is not int:
            raise TypeError("malformed schedule")
        if type(schedule.spike_times_ms) is not tuple:
            raise TypeError("malformed spike times")
        for time in schedule.spike_times_ms:
            value = _number(time, "spike time")
            if value < 0 or _steps(value, runtime.dt_ms, "spike time") >= steps:
                raise ValueError("spike time outside chunk")
    if any(type(i) is not int for i in stimulus.refractory_free_neuron_ids):
        raise TypeError("malformed refractory-free IDs")
    ids = runtime._engine.projection.neuron_ids
    known = getattr(runtime, "_known_ids", None)
    if known is None:
        # The owned projection is immutable; reuse membership across chunks.
        known = frozenset(runtime.neuron_ids)
        runtime._known_ids = known
    if any(schedule.neuron_id not in known for schedule in stimulus.schedules):
        raise KeyError("unknown stimulus neuron ID")
    if any(i not in known for i in stimulus.refractory_free_neuron_ids):
        raise KeyError("unknown refractory-free neuron ID")
    _events.schedule_events(stimulus, neuron_positions=ids, duration_steps=steps, dt_ms=runtime.dt_ms)
    _events.validate_refractory_ids(stimulus.refractory_free_neuron_ids, ids)
    stimulus.fingerprint
    return start, steps


class PreparedRuntime(_Opaque):
    """Opaque CPU runtime with shared owned execution structures.

    No close or context manager. States strongly retain their exact owner.
    """
    __slots__ = ("_engine", "_known_ids")
    _state_type = SimulationState

    @property
    def backend(self):
        return "cpu"

    @property
    def dt_ms(self):
        return self._engine.dt_ms

    @property
    def neuron_ids(self):
        return tuple(int(i) for i in self._engine.projection.neuron_ids)

    @property
    def projection_fingerprint(self):
        return self._engine.projection.fingerprint

    @property
    def parameter_fingerprint(self):
        return self._engine.parameters.fingerprint

    def initial_state(self):
        """Return a fresh independent state at timestep/time zero."""
        raw = self._engine.initial_state()
        state = object.__new__(self._state_type)
        state._owner, state._state, state._failed = self, raw, False
        return state

    def advance(self, state, *, duration_ms, stimulus=_events.ExplicitStimulus()):
        """Validate before mutation, advance in place and return detached output.

        Any ordinary execution/result exception poisons this state and propagates
        unchanged. Process-level interruption handling is outside this API.
        """
        start, steps = _preflight(self, state, duration_ms, stimulus)
        try:
            raw = self._engine.advance(state._state, duration_ms=steps * self.dt_ms, stimulus=stimulus)
            return _result(raw, start, steps, self.dt_ms)
        except Exception:
            state._failed = True
            raise


def prepare_runtime(projection, *, parameters=_lif.REFERENCE_LIF_PARAMETERS, dt_ms=0.1):
    """Snapshot an EffectiveSignedProjection once; never load source datasets.

    Existing v0.3 model/event exports remain valid. This factory is CPU-only.
    """
    snapshot, parameters, dt = _snapshot(projection, parameters, dt_ms)
    runtime = object.__new__(PreparedRuntime)
    runtime._engine = _lif.PreparedRuntime(snapshot, parameters, dt)
    runtime._known_ids = frozenset(int(i) for i in snapshot.neuron_ids)
    return runtime
