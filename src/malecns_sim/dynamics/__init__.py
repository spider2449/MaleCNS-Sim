"""Deterministic CPU reference neural dynamics."""

from malecns_sim.dynamics.lif import (
    EffectiveSignedProjection,
    LIFParameters,
    REFERENCE_LIF_PARAMETERS,
    SimulationResult,
    linear_state_update,
    simulate_lif,
)
from malecns_sim.dynamics.stimulus import (
    ExplicitStimulus,
    PoissonStimulus,
    SpikeSchedule,
)

__all__ = [
    "EffectiveSignedProjection",
    "ExplicitStimulus",
    "LIFParameters",
    "PoissonStimulus",
    "REFERENCE_LIF_PARAMETERS",
    "SimulationResult",
    "SpikeSchedule",
    "linear_state_update",
    "simulate_lif",
]
