"""Optional flybody physical adapter, independent of connectome source loading.

Use in an isolated compatible environment. No RL policy or target trajectory is
loaded. An engineered wing oscillator requires explicit opt-in; measured wing
patterns instead require a caller-pinned file identity.
"""

import hashlib
import copy
import base64
import io
from concurrent.futures import ThreadPoolExecutor
from importlib import metadata
import json
import math
from pathlib import Path


FLYBODY_COMMIT = "d015e9bfe441bd90ae431bac24c55cb74bdbce26"


class _PhysicalFlybodyBody:
    control_ms = 0.2

    def __init__(self, *, pattern_kind: str, wing_pattern_path=None,
                 expected_pattern_sha256=None, obstacle_cm=(0.5, 0.2, 1.0),
                 obstacle_radius_cm=0.08, initial_position_cm=(0.0, 0.0, 1.0)):
        direct = metadata.distribution("flybody").read_text("direct_url.json")
        if not direct or json.loads(direct).get("vcs_info", {}).get("commit_id") != FLYBODY_COMMIT:
            raise ValueError("install the pinned upstream flybody commit in an isolated environment")
        if pattern_kind not in ("engineered-oscillator", "measured-pattern"):
            raise ValueError("explicit wing-pattern kind required")
        if pattern_kind == "measured-pattern":
            if wing_pattern_path is None or expected_pattern_sha256 is None:
                raise ValueError("measured pattern path and SHA-256 required")
            pattern_sha = hashlib.sha256(Path(wing_pattern_path).read_bytes()).hexdigest()
            if pattern_sha != expected_pattern_sha256:
                raise ValueError("wing pattern identity mismatch")
        else:
            if wing_pattern_path is not None or expected_pattern_sha256 is not None:
                raise ValueError("engineered oscillator cannot carry measured-pattern metadata")
            pattern_sha = None
        for vector in (obstacle_cm, initial_position_cm):
            if (type(vector) not in (tuple, list) or len(vector) != 3
                    or any(type(v) not in (int, float) or not math.isfinite(v) for v in vector)):
                raise ValueError("finite centimeter coordinates required")
        if (type(obstacle_radius_cm) not in (int, float) or not math.isfinite(obstacle_radius_cm)
                or not 0 < obstacle_radius_cm <= 1):
            raise ValueError("positive bounded obstacle radius required")

        import numpy as np
        from dm_control import composer
        from dm_control.locomotion.arenas import floors
        import flybody
        from flybody.fruitfly.fruitfly import FruitFly
        from flybody.tasks.base import Flying
        from flybody.tasks.pattern_generators import WingBeatPatternGenerator

        self.np = np
        asset_root = Path(flybody.__file__).parent / "fruitfly" / "assets"
        asset_records = {file.name: hashlib.sha256(file.read_bytes()).hexdigest()
                         for file in sorted(asset_root.iterdir()) if file.suffix in (".obj", ".xml")}
        self.identity = {"model": "flybody-mujoco-female-physical-v1", "flybody_commit": FLYBODY_COMMIT,
            "packages": {name: metadata.version(name) for name in ("flybody", "mujoco", "dm-control", "numpy")},
            "asset_sha256": asset_records, "pattern_kind": pattern_kind, "pattern_sha256": pattern_sha,
            "physics_dt_ms": 0.05, "control_dt_ms": self.control_ms, "nominal_wingbeat_hz": 218.0,
            "initial_position_cm": list(initial_position_cm), "initial_pitch_deg": 47.5,
            "initial_velocity_cm_s": [0.0, 0.0, 0.0], "initial_wing_phase": 0.0,
            "obstacle_cm": list(obstacle_cm), "obstacle_radius_cm": obstacle_radius_cm,
            "sex_transfer": "male connectome coupled to female anatomical body; unvalidated transfer",
            "sensory": "ground-truth sphere angular expansion and engineered bilateral bearing weights; not a retinal model",
            "controller": "no RL policy; explicit basal oscillator plus neural residuals"}
        self.obstacle = np.array(obstacle_cm, dtype=float)
        self.radius = obstacle_radius_cm
        initial = np.array(initial_position_cm, dtype=float)
        pattern = WingBeatPatternGenerator(base_pattern_path=wing_pattern_path)
        arena = floors.Floor()
        sky = next((texture for texture in arena.mjcf_model.asset.find_all("texture")
                    if texture.type == "skybox"), None)
        if sky is None:
            sky = arena.mjcf_model.asset.add("texture", name="flight_sky", type="skybox")
        sky.builtin = "gradient"
        sky.rgb1 = [0.45, 0.65, 0.85]
        sky.rgb2 = [0.85, 0.90, 0.95]
        sky.width, sky.height = 128, 768
        self.identity["display_background"] = "procedural blue gradient sky; visual orientation reference only"
        arena.mjcf_model.worldbody.add("geom", name="flight_visual_obstacle", type="sphere",
            pos=obstacle_cm, size=[obstacle_radius_cm], rgba=[0.95, 0.35, 0.08, 1],
            contype=1, conaffinity=1)

        class NeuralFlightTask(Flying):
            def __init__(self):
                super().__init__(walker=FruitFly, arena=arena, time_limit=float("inf"),
                    floor_contacts=True, disable_legs=True, joint_filter=0.0)
                self.frequency_fraction = 0.0

            def initialize_episode(self, physics, random_state):
                super().initialize_episode(physics, random_state)
                angle = math.radians(47.5)
                self.walker.set_pose(physics, initial, np.array([math.cos(angle/2), 0, -math.sin(angle/2), 0]))
                self.walker.set_velocity(physics, np.zeros(3), np.zeros(3))
                qpos, qvel = pattern.reset(initial_phase=0.0, return_qvel=True)
                physics.bind(self._wing_joints).qpos = qpos
                physics.bind(self._wing_joints).qvel = qvel
                self.frequency_fraction = 0.0

            def before_step(self, physics, action, random_state):
                corrected = action.copy()
                target = pattern.step(ctrl_freq=218.0*(1+self.frequency_fraction))
                corrected[self.walker._action_indices["wings"]] += target - physics.bind(self._wing_joints).qpos
                super().before_step(physics, corrected, random_state)

            def get_reward_factors(self, physics):
                return np.ones(1)

        self.task = NeuralFlightTask()
        # Hide self geometry in eye views without changing collision or fluid forces.
        from dm_control.mujoco import wrapper
        self.eye_scene = wrapper.MjvOption()
        self.eye_scene.geomgroup[:] = 0
        self.eye_scene.geomgroup[0] = 1
        self.overview_scene = wrapper.MjvOption()
        self.overview_scene.geomgroup[:] = 0
        self.overview_scene.geomgroup[0:2] = 1
        self.identity["eye_rendering"] = "native eye cameras; only environment render group 0 visible"
        self.identity["camera_resolution"] = [256, 256]
        self.identity["primary_view"] = "512px third-person track3 camera, position-following"
        self.identity["obstacle_display_color"] = "orange"
        self.task.root_entity.mjcf_model.visual.quality.offsamples = 4
        expected_wings = [f"wing_{axis}_{side}" for side in ("left", "right")
                          for axis in ("yaw", "roll", "pitch")]
        indices = self.task.walker._action_indices["wings"]
        actual_wings = [self.task.walker.actuators[index].name for index in indices]
        if actual_wings != expected_wings:
            raise ValueError("upstream wing actuator ordering changed")
        self.identity["wing_actuator_order"] = actual_wings
        self.identity["wing_gain"] = [float(self.task.walker.mjcf_model.find("default", axis).general.gainprm[0])
                                      for axis in ("yaw", "roll", "pitch")]
        self.composer = composer
        self.env = None
        self.closed = False

    def reset(self, seed):
        if self.closed:
            raise ValueError("body is closed")
        if self.env is not None:
            self.env.close()
        self.env = self.composer.Environment(task=self.task, time_limit=float("inf"),
            random_state=self.np.random.RandomState(seed), strip_singleton_obs_buffer_dim=True)
        if not math.isclose(self.env.physics.timestep()*1000, 0.05, abs_tol=1e-12):
            raise ValueError("upstream body physics timestep changed")
        if not math.isclose(self.env.control_timestep()*1000, self.control_ms, abs_tol=1e-12):
            raise ValueError("upstream actuator timestep changed")
        self.timestep = self.env.reset()
        # Make the physical camera observable in the small scientific preview.
        # The lighting changes presentation only; sensory injection still uses
        # geometry-derived expansion from the body state.
        self.env.physics.model.vis.headlight.ambient[:] = [0.45, 0.45, 0.45]
        self.env.physics.model.vis.headlight.diffuse[:] = [0.8, 0.8, 0.8]
        self.env.physics.model.vis.headlight.specular[:] = [0.2, 0.2, 0.2]
        self.previous_angle = None
        self.terminal = False
        return self._observe()

    def _capture_frame(self):
        physics = self.env.physics
        frames = {side: physics.render(height=256, width=256,
                    camera_id=int(physics.bind(getattr(self.task.walker, side+"_eye")).element_id),
                    scene_option=self.eye_scene).tolist()
                for side in ("left", "right")}
        camera = self.task.walker.mjcf_model.find("camera", "track3")
        frames["overview"] = physics.render(height=512, width=512,
            camera_id=int(physics.bind(camera).element_id), scene_option=self.overview_scene).tolist()
        return frames

    def render_encoded(self):
        """Send only the primary view as JPEG, avoiding RGB-array JSON overhead."""
        from PIL import Image
        physics = self.env.physics
        camera = self.task.walker.mjcf_model.find("camera", "track3")
        pixels = physics.render(height=512, width=512,
            camera_id=int(physics.bind(camera).element_id), scene_option=self.overview_scene)
        buffer = io.BytesIO()
        Image.fromarray(pixels).save(buffer, format="JPEG", quality=85)
        return {"overview": {"width": 512, "height": 512,
            "image_url": "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")}}

    def _observe(self):
        position, quat = self.task.walker.get_pose(self.env.physics)
        world_delta = self.obstacle - position
        local_delta = self.task.walker.transform_vec_to_egocentric_frame(self.env.physics, world_delta)
        distance = float(self.np.linalg.norm(world_delta))
        angle = 2*math.asin(min(1.0, self.radius/max(distance, 1e-12)))
        expansion = 0.0 if self.previous_angle is None else max(0.0, (angle-self.previous_angle)/(self.control_ms/1000))
        self.previous_angle = angle
        bearing = math.atan2(float(local_delta[1]), float(local_delta[0]))
        visible = float(local_delta[0]) > 0
        left = expansion*(1+math.sin(bearing))/2 if visible else 0.0
        right = expansion*(1-math.sin(bearing))/2 if visible else 0.0
        return {"time_ms": float(self.env.physics.data.time)*1000,
                "position_cm": position.tolist(), "quaternion_wxyz": quat.tolist(),
                "expansion_left_rad_s": left, "expansion_right_rad_s": right,
                "obstacle_angle_rad": angle, "terminal": bool(self.terminal)}

    def advance(self, action):
        if self.closed or self.env is None or self.terminal:
            raise ValueError("body must be reset and nonterminal")
        required = {"left_wing_yaw_offset_rad", "right_wing_yaw_offset_rad", "frequency_fraction"}
        if set(action) != required or any(type(v) not in (int, float) or not math.isfinite(v) for v in action.values()):
            raise ValueError("finite allowlisted wing commands required")
        if abs(action["frequency_fraction"]) > 0.05 or any(abs(action[key]) > 0.15 for key in required if key != "frequency_fraction"):
            raise ValueError("wing command exceeds the frozen adapter bounds")
        spec = self.env.action_spec()
        controls = self.np.zeros(spec.shape)
        wing_indices = self.task.walker._action_indices["wings"]
        if len(wing_indices) != 6:
            raise ValueError("upstream wing actuator interface changed")
        controls[wing_indices[0]] = action["left_wing_yaw_offset_rad"]
        controls[wing_indices[3]] = action["right_wing_yaw_offset_rad"]
        self.task.frequency_fraction = action["frequency_fraction"]
        self.timestep = self.env.step(controls)
        self.terminal = self.timestep.last()
        return self._observe()

    def render(self):
        if self.closed or self.env is None:
            raise ValueError("body is not ready to render")
        return self._capture_frame()

    def close(self):
        if self.env is not None:
            self.env.close()
        self.closed = True


class FlybodyBody:
    """Own every physics and GLFW operation on one persistent worker thread."""

    control_ms = 0.2

    def __init__(self, **kwargs):
        self._worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="flight-physics")
        try:
            self._body = self._worker.submit(_PhysicalFlybodyBody, **kwargs).result()
        except BaseException:
            self._worker.shutdown(wait=True)
            raise
        self.identity = copy.deepcopy(self._body.identity)
        self.np = self._body.np
        self.closed = False

    def _call(self, name, *args):
        if self.closed:
            raise ValueError("body is closed")
        return self._worker.submit(getattr(self._body, name), *args).result()

    def reset(self, seed):
        return self._call("reset", seed)

    def advance(self, action):
        return self._call("advance", copy.deepcopy(action))

    def render(self):
        return self._call("render")

    def render_encoded(self):
        return self._call("render_encoded")

    def close(self):
        if self.closed:
            return
        try:
            self._call("close")
        finally:
            self.closed = True
            self._worker.shutdown(wait=True)
