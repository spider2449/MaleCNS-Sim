"""Experimental optional GPU facade over the retained bounded EQ-B backend.

No automatic selection, performance claim or context manager. Construction uses
the current device and lazy optional dependency. Close resources explicitly.
"""

from malecns_sim import runtime as _runtime
from malecns_sim.dynamics import lif as _lif

__all__ = ["prepare_gpu_runtime", "GPUPreparedRuntime", "GPUSimulationState"]


class GPUSimulationState(_runtime.SimulationState):
    """Experimental exact-owner GPU trajectory with explicit close."""
    __slots__ = ()

    @property
    def timestep(self):
        if self._failed or self._state.status != "ready":
            raise RuntimeError("GPU state is closed or failed")
        return int(self._state.timestep)

    def close(self):
        """Idempotently release this state's device storage."""
        self._state.close()


class GPUPreparedRuntime(_runtime.PreparedRuntime):
    """Experimental GPU runtime; retained device/owner/busy rules apply."""
    __slots__ = ()
    _state_type = GPUSimulationState

    @property
    def backend(self):
        return "gpu"

    def advance(self, state, *, duration_ms, stimulus=_runtime._events.ExplicitStimulus()):
        # Reject closed/device/busy conditions before facade execution admission.
        backing = self._engine._checked_backing()
        if backing.lock.locked():
            raise RuntimeError("GPU runtime is busy")
        _, steps = _runtime._preflight(self, state, duration_ms, stimulus)
        if (steps + self._engine.ring_size) * self._engine.projection.outgoing_targets.size > _runtime._LIMIT:
            raise ValueError("GPU event counter exceeds int64 bounds")
        return super().advance(state, duration_ms=duration_ms, stimulus=stimulus)

    def close(self):
        """Idempotently close the runtime; live states retain their backing."""
        self._engine.close()


def prepare_gpu_runtime(projection, *, parameters=_lif.REFERENCE_LIF_PARAMETERS, dt_ms=0.1):
    """Prepare on the current GPU; experimental and never selected implicitly."""
    snapshot, parameters, dt = _runtime._snapshot(projection, parameters, dt_ms)
    from malecns_sim.dynamics.cuda import GPUPreparedRuntime as _Engine
    runtime = object.__new__(GPUPreparedRuntime)
    runtime._engine = _Engine(snapshot, parameters, dt)
    return runtime
