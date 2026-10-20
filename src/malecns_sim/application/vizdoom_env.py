"""ViZDoom environment for the generic closed loop (optional dependency, imported lazily).

The observation is ground truth from the game's label buffer: the horizontal position
of the monster relative to the crosshair. It is not a retinal or visual-system model.
The game clock is separate from neural time (see ``closed_loop``).
"""

import os
import struct
import zlib

import numpy as np

from malecns_sim.application.closed_loop import StepResult

BUTTONS = ("MOVE_LEFT", "MOVE_RIGHT", "ATTACK")


PNG_SIGNATURE = bytes([137, 80, 78, 71, 13, 10, 26, 10])
NO_FILTER = bytes([0])


def encode_png(rgb):
    """Encode an (height, width, 3) uint8 array as PNG bytes without an imaging dependency."""
    rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
    height, width, _ = rgb.shape
    raw = b"".join(NO_FILTER + rgb[row].tobytes() for row in range(height))

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    return (PNG_SIGNATURE + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


class ViZDoomBasic:
    """The bundled ``basic.cfg`` scenario: strafe left/right and shoot one monster."""

    def __init__(self, *, scenario="basic.cfg", frame_skip=4, window_visible=False):
        import vizdoom as vzd
        if type(frame_skip) is not int or frame_skip < 1:
            raise ValueError("frame_skip must be a positive integer")
        self._vzd, self.frame_skip = vzd, frame_skip
        game = vzd.DoomGame()
        game.load_config(os.path.join(vzd.scenarios_path, scenario))
        game.set_window_visible(bool(window_visible))
        game.set_labels_buffer_enabled(True)
        game.init()
        names = tuple(str(button).split(".")[-1] for button in game.get_available_buttons())
        if names != BUTTONS:
            game.close()
            raise ValueError(f"scenario buttons {names} differ from {BUTTONS}")
        self.game, self._last = game, {"monster_x": None, "tic": 0}

    def _observe(self):
        state = self.game.get_state()
        if state is None:
            return self._last
        width = self.game.get_screen_width()
        monster = None
        for label in state.labels:
            if label.object_name != "DoomPlayer":
                # Normalized to [-1, 1]; 0 is the crosshair column, positive is to the right.
                monster = (label.x + label.width / 2) / width * 2 - 1
                break
        self._last = {"monster_x": monster, "tic": int(state.tic)}
        return self._last

    def reset(self, seed):
        self.game.set_seed(seed)
        self.game.new_episode()
        return self._observe()

    def step(self, command):
        if len(command) != len(BUTTONS):
            raise ValueError("one boolean per button required")
        reward = self.game.make_action([int(bool(pressed)) for pressed in command], self.frame_skip)
        done = self.game.is_episode_finished()
        observation = self._last if done else self._observe()
        kills = int(self.game.get_game_variable(self._vzd.GameVariable.KILLCOUNT))
        return StepResult(observation, reward=reward, done=done,
                          info={"kills": kills, "total_reward": self.game.get_total_reward()})

    def frame_png(self):
        """The current game screen as PNG bytes, or None when the episode has ended."""
        state = self.game.get_state()
        if state is None:
            return None
        return encode_png(np.transpose(state.screen_buffer, (1, 2, 0)))

    def close(self):
        self.game.close()


def monster_bearing_rates(maximum_hz):
    """Input rate per side from the monster bearing; both sides stay silent when no monster is visible."""
    def rates(observation):
        x = observation["monster_x"]
        if x is None:
            return {"sensory_left": 0.0, "sensory_right": 0.0}
        return {"sensory_left": maximum_hz * (1 - x) / 2, "sensory_right": maximum_hz * (1 + x) / 2}
    return rates


def button_command(move_threshold_hz=0.0, attack_threshold_hz=0.0):
    """Press a button when its readout group fires above its threshold (0 Hz: any spike in the window).

    A group's rate is spikes * 1000 / (window ms * neurons), so with a 10 ms window and one neuron a single
    spike is 100 Hz and a threshold of 100 requires at least two spikes.
    """
    def command(rates):
        return (rates["move_left"] > move_threshold_hz, rates["move_right"] > move_threshold_hz,
                rates["attack"] > attack_threshold_hz)
    return command
