"""ViZDoom adapter smoke checks; skipped unless the optional vizdoom package is installed."""

import pytest

from malecns_sim.application.vizdoom_env import BUTTONS, button_command, monster_bearing_rates


def _run_to_end(env, command):
    env.reset(1)
    steps, outcome = 0, None
    while steps < 400:
        outcome = env.step(command)
        steps += 1
        if outcome.done:
            return steps, outcome
    raise AssertionError("episode did not end")


def test_basic_scenario_resets_reproducibly_and_ends_by_timeout():
    pytest.importorskip("vizdoom")
    from malecns_sim.application.vizdoom_env import ViZDoomBasic
    env = ViZDoomBasic(frame_skip=4)
    try:
        first = env.reset(7)
        assert env.reset(7) == first and -1 <= first["monster_x"] <= 1
        steps, outcome = _run_to_end(env, (False, False, False))
        assert steps == 75 and outcome.done and outcome.info["kills"] == 0
        with pytest.raises(ValueError):
            env.step((True, False))
    finally:
        env.close()


def test_bearing_rates_and_button_command():
    rates = monster_bearing_rates(200.0)
    assert rates({"monster_x": None}) == {"sensory_left": 0.0, "sensory_right": 0.0}
    assert rates({"monster_x": -1.0}) == {"sensory_left": 200.0, "sensory_right": 0.0}
    assert rates({"monster_x": 0.0}) == {"sensory_left": 100.0, "sensory_right": 100.0}
    assert BUTTONS == ("MOVE_LEFT", "MOVE_RIGHT", "ATTACK")
    command = button_command(0.0)
    assert command({"move_left": 0.0, "move_right": 5.0, "attack": 0.0}) == (False, True, False)
