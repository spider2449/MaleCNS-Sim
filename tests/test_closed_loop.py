"""Synthetic-only checks of the generic closed loop with a fake environment."""

import numpy as np
import pytest

from malecns_sim.application.closed_loop import (
    ClosedLoop, ClosedLoopParameters, GroupRateDecoder, GroupRateEncoder, StepResult)
from malecns_sim.dynamics.lif import EffectiveSignedProjection
from malecns_sim.runtime import prepare_runtime

DRIVEN = tuple(range(100, 110))


def _projection(n=60):
    rng = np.random.default_rng(3)
    sources = np.repeat(np.arange(n), 4)
    targets = rng.integers(0, n, size=sources.size)
    weights = np.full(sources.size, 2.0)
    indptr = np.concatenate(([0], np.cumsum(np.bincount(sources, minlength=n)))).astype(np.int64)
    return EffectiveSignedProjection(
        neuron_ids=np.arange(100, 100 + n, dtype=np.int64), source_positions=sources.astype(np.int64),
        target_positions=targets.astype(np.int64), effective_weights_mV=weights, outgoing_indptr=indptr,
        outgoing_targets=targets.astype(np.int64), outgoing_weights_mV=weights, synaptic_weight_mV=0.275,
        fingerprint="synthetic-loop", unsigned_graph_fingerprint="synthetic-loop",
        signed_policy_fingerprint="synthetic-loop", sign_policy_id="synthetic-loop",
        resolution_policy_id="synthetic-loop", excluded_unresolved_edge_count=0,
        excluded_anatomical_weight=0, included_anatomical_weight=0)


class CountingEnvironment:
    """Ends after ``length`` steps; the observation is the number of commands received."""

    def __init__(self, length=5, fail_at=None):
        self.length, self.fail_at, self.commands, self.resets, self.closed = length, fail_at, [], 0, False

    def reset(self, seed):
        self.resets += 1
        self.commands = []
        return 0

    def step(self, command):
        if self.fail_at is not None and len(self.commands) == self.fail_at:
            raise RuntimeError("injected environment failure")
        self.commands.append(command)
        return StepResult(len(self.commands), reward=1.0, done=len(self.commands) >= self.length,
                          info={"n": len(self.commands)})

    def close(self):
        self.closed = True


def _loop(env, *, rate=200.0, weight=8.0, **kwargs):
    runtime = prepare_runtime(_projection())
    encoder = GroupRateEncoder({"in": DRIVEN}, lambda observation: {"in": rate}, weight_mV=weight)
    decoder = GroupRateDecoder({"out": DRIVEN}, lambda rates: rates["out"] > 0)
    return ClosedLoop(runtime, env, encoder, decoder, expected_projection_fingerprint=runtime.projection_fingerprint,
                      **kwargs)


def test_loop_advances_neural_clock_and_runs_to_the_end_of_the_episode():
    env = CountingEnvironment(length=5)
    loop = _loop(env, parameters=ClosedLoopParameters(neural_ms_per_step=2.0))
    records = loop.run()
    assert [r.step for r in records] == [1, 2, 3, 4, 5]
    assert [r.neural_time_ms for r in records] == pytest.approx([2.0, 4.0, 6.0, 8.0, 10.0])
    assert records[-1].done and len(env.commands) == 5 and records[0].info == {"n": 1}
    with pytest.raises(ValueError, match="ended"):
        loop.step()


def test_input_drives_spikes_and_the_decoder_reads_them():
    driven = _loop(CountingEnvironment(), parameters=ClosedLoopParameters(neural_ms_per_step=5.0)).run()
    assert sum(r.input_events for r in driven) > 0 and sum(r.network_spikes for r in driven) > 0
    assert all(r.command is True for r in driven[1:]) and driven[-1].evidence["spikes"]["out"] > 0
    silent = _loop(CountingEnvironment(), rate=0.0, parameters=ClosedLoopParameters(neural_ms_per_step=5.0)).run()
    assert sum(r.input_events + r.network_spikes for r in silent) == 0
    assert all(r.command is False for r in silent)


def test_reset_reproduces_the_episode_for_the_same_seed():
    loop = _loop(CountingEnvironment(), parameters=ClosedLoopParameters(neural_ms_per_step=5.0, seed=4))
    first = [(r.input_events, r.network_spikes, r.evidence["spikes"]["out"]) for r in loop.run()]
    loop.reset()
    again = [(r.input_events, r.network_spikes, r.evidence["spikes"]["out"]) for r in loop.run()]
    other = _loop(CountingEnvironment(), parameters=ClosedLoopParameters(neural_ms_per_step=5.0, seed=5))
    assert first == again
    assert first != [(r.input_events, r.network_spikes, r.evidence["spikes"]["out"]) for r in other.run()]


def test_maximum_steps_bounds_the_run_and_run_can_be_resumed():
    loop = _loop(CountingEnvironment(length=50), parameters=ClosedLoopParameters(neural_ms_per_step=1.0, maximum_steps=7))
    assert len(loop.run(3)) == 3 and len(loop.run()) == 4
    with pytest.raises(ValueError, match="ended"):
        loop.step()


def test_environment_failure_poisons_the_loop_until_reset():
    env = CountingEnvironment(length=9, fail_at=2)
    loop = _loop(env, parameters=ClosedLoopParameters(neural_ms_per_step=1.0))
    with pytest.raises(RuntimeError, match="injected"):
        loop.run()
    with pytest.raises(ValueError, match="reset"):
        loop.step()
    env.fail_at = None
    loop.reset()
    assert loop.step().step == 1


def test_construction_rejects_bad_identity_neurons_and_grid():
    runtime = prepare_runtime(_projection())
    encoder = GroupRateEncoder({"in": DRIVEN}, lambda observation: {"in": 1.0}, weight_mV=1.0)
    decoder = GroupRateDecoder({"out": DRIVEN}, lambda rates: 0)
    with pytest.raises(ValueError, match="identity"):
        ClosedLoop(runtime, CountingEnvironment(), encoder, decoder, expected_projection_fingerprint="other")
    stranger = GroupRateDecoder({"out": (999999,)}, lambda rates: 0)
    with pytest.raises(ValueError, match="lacks"):
        ClosedLoop(runtime, CountingEnvironment(), encoder, stranger,
                   expected_projection_fingerprint=runtime.projection_fingerprint)
    with pytest.raises(ValueError, match="whole number"):
        ClosedLoop(runtime, CountingEnvironment(), encoder, decoder,
                   expected_projection_fingerprint=runtime.projection_fingerprint,
                   parameters=ClosedLoopParameters(neural_ms_per_step=0.15))


def test_group_encoder_rejects_unknown_groups_and_nonfinite_rates():
    import random
    encoder = GroupRateEncoder({"in": DRIVEN}, lambda observation: observation, weight_mV=1.0)
    with pytest.raises(KeyError):
        encoder.encode({"other": 1.0}, steps=10, dt_ms=0.1, rng=random.Random(0))
    with pytest.raises(ValueError):
        encoder.encode({"in": float("nan")}, steps=10, dt_ms=0.1, rng=random.Random(0))
    stimulus = encoder.encode({"in": 1e9}, steps=1000, dt_ms=0.1, rng=random.Random(0))
    # Rates are capped at maximum_hz (200 Hz => about 0.02 events per 0.1 ms step per neuron).
    assert 0 < sum(len(s.spike_times_ms) for s in stimulus.schedules) < 10 * 1000 * 0.05
