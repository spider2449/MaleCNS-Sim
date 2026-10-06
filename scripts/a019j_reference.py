"""Frozen starting-SHA linear oracle for guarded synthetic certification only."""
import numpy as np
from malecns_sim.dynamics.lif import LIFParameters, REFERENCE_LIF_PARAMETERS, AdvanceTiming, _finite

def linear_state_update(
    v_mV: np.ndarray | float,
    g_mV: np.ndarray | float,
    *,
    parameters: LIFParameters = REFERENCE_LIF_PARAMETERS,
    dt_ms: float = 0.1,
    _timing: AdvanceTiming | None = None,
) -> tuple[np.ndarray | float, np.ndarray | float]:
    """Analytically integrate both coupled linear states over one timestep."""

    if _timing is not None:
        _timing.substart()
    dt = _finite(dt_ms, "dt_ms")
    if dt <= 0.0:
        raise ValueError("dt_ms must be positive")
    exp_m = np.exp(-dt / parameters.tau_membrane_ms)
    exp_s = np.exp(-dt / parameters.tau_synapse_ms)
    if np.isclose(parameters.tau_membrane_ms, parameters.tau_synapse_ms):
        g_coefficient = (dt / parameters.tau_membrane_ms) * exp_m
    else:
        g_coefficient = (
            exp_s - exp_m
        ) / (1.0 - parameters.tau_membrane_ms / parameters.tau_synapse_ms)
    if _timing is not None:
        _timing.substop("linear_update", "coefficients")
        _timing.substart()
    v_next = parameters.v_rest_mV + (np.asarray(v_mV) - parameters.v_rest_mV) * exp_m + np.asarray(g_mV) * g_coefficient
    if _timing is not None:
        _timing.substop("linear_update", "membrane")
        _timing.substart()
    g_next = np.asarray(g_mV) * exp_s
    if _timing is not None:
        _timing.substop("linear_update", "synaptic_decay")
        _timing.substart()
    if np.ndim(v_mV) == 0:
        if _timing is not None:
            _timing.substop("linear_update", "return_shape_check")
        return float(v_next), float(g_next)
    if _timing is not None:
        _timing.substop("linear_update", "return_shape_check")
    return v_next, g_next
