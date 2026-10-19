"""Optional flybody physical adapter, independent of connectome source loading.

Use in an isolated compatible environment. Two explicit controllers exist:

- ``oscillator``: no RL policy; an engineered or measured wing pattern plus
  neural wing-yaw residuals and frequency modulation.
- ``flight-policy``: the published flybody flight-imitation policy (a learned
  low-level controller) tracks a reference trajectory whose heading and speed
  the neural readout steers. The policy, not MaleCNS, stabilizes the body.

Measured patterns and the policy require caller-pinned file identities.
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
# Draggable target goal limits (x, y, z) in centimeters. x and y are relative
# to the fly when the goal is set, so the goal stays reachable as it travels;
# z is absolute and kept above the floor.
TARGET_BOUNDS_CM = [[-10.0, 10.0], [-10.0, 10.0], [0.1, 5.0]]
TARGET_BOUNDS_FRAME = ["fly", "fly", "world"]


# Published artifacts from https://doi.org/10.25378/janelia.25309105 (v4).
# The policy was trained with this measured wing pattern; both are pinned.
FLIGHT_POLICY_SHA256 = "4e142f965ad8b0c943b639c16c06166adaf926420a9535edba2b71b11bfa8018"
WING_PATTERN_FMECH_SHA256 = "f97b975ef1b5adbe42c208ea9665f3c37fa432914f56f3943f1697cdb090d1ce"


def directory_sha256(path):
    """Content identity of a SavedModel directory: relative paths and bytes."""
    root = Path(path)
    digest = hashlib.sha256()
    files = sorted(file for file in root.rglob("*") if file.is_file())
    if not files:
        raise ValueError("empty policy directory")
    for file in files:
        digest.update(file.relative_to(root).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(file.read_bytes()).digest())
    return digest.hexdigest()


def _load_policy(tf, path):
    """Load the published SavedModel with a current TensorFlow Probability.

    The policy was exported by an older TFP that registered its output
    distribution type under the module path; current TFP uses a short name.
    """
    import tensorflow_probability as tfp
    tfp.distributions.Independent(tfp.distributions.Normal(tf.zeros(1), tf.ones(1)), 1)._type_spec
    try:
        from tensorflow.python.framework import type_spec_registry
        registry = type_spec_registry._NAME_TO_TYPE_SPEC
        current = registry["tfp.distributions.Independent_ACTTypeSpec"]
    except (ImportError, AttributeError, KeyError) as exc:
        raise ValueError("installed TensorFlow/TFP changed the private type-spec registry; "
                         "the legacy flight-policy loader shim needs updating") from exc
    legacy = "tensorflow_probability.python.distributions.independent.Independent_ACTTypeSpec"
    registry.setdefault(legacy, current)
    return tf.saved_model.load(str(path))


def validate_target(position_cm, fly_cm):
    if (type(position_cm) not in (list, tuple) or len(position_cm) != 3
            or any(type(v) not in (int, float) or not math.isfinite(v) for v in position_cm)):
        raise ValueError("finite target coordinates in centimeters required")
    offset = [v-(float(f) if frame == "fly" else 0.0)
              for v, f, frame in zip(position_cm, fly_cm, TARGET_BOUNDS_FRAME)]
    if any(not low <= v <= high for v, (low, high) in zip(offset, TARGET_BOUNDS_CM)):
        raise ValueError("target lies outside the bounded flight arena")
    return [float(v) for v in position_cm]


class _ReferenceRows:
    """Reference rows addressed by absolute control step, keeping a sliding window.

    flybody reads the reference by absolute step (one row, or a short forward
    slice from the current step), so rows behind the current step are dropped
    and memory stays bounded however long the episode runs.
    """

    def __init__(self, np, width, capacity=4096):
        self.np, self.rows, self.offset = np, np.zeros((capacity, width)), 0

    def reserve(self, index, oldest):
        """Make room for row ``index``, discarding rows before ``oldest``."""
        if index-self.offset < len(self.rows):
            return
        live = self.rows[oldest-self.offset:index-self.offset].copy()
        if len(live) >= len(self.rows)//2:
            self.rows = self.np.zeros((2*len(self.rows), self.rows.shape[1]))
        self.rows[:len(live)] = live
        self.offset = oldest

    def _local(self, row):
        if isinstance(row, slice):
            if row.step not in (None, 1) or row.start is None or row.stop is None:
                raise IndexError("reference rows support forward absolute slices only")
            local = slice(row.start-self.offset, row.stop-self.offset)
            first = local.start
        else:
            local = first = int(row)-self.offset
        if first < 0:
            raise IndexError("reference row already discarded")
        return local

    def _key(self, key):
        return (self._local(key[0]),)+key[1:] if isinstance(key, tuple) else self._local(key)

    def __getitem__(self, key):
        return self.rows[self._key(key)]

    def __setitem__(self, key, value):
        self.rows[self._key(key)] = value


class _PhysicalFlybodyBody:
    control_ms = 0.2

    def __init__(self, *, pattern_kind: str, wing_pattern_path=None,
                 expected_pattern_sha256=None, obstacle_cm=(0.5, 0.2, 1.0),
                 obstacle_radius_cm=0.08, initial_position_cm=(0.0, 0.0, 1.0),
                 target_speed_cm_s=50.0, controller="oscillator", policy_path=None,
                 expected_policy_sha256=None, reference_speed_cm_s=20.0,
                 maximum_yaw_rate_rad_s=20.0, maximum_speed_boost=0.5):
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
        if (type(target_speed_cm_s) not in (int, float) or not math.isfinite(target_speed_cm_s)
                or not 0 < target_speed_cm_s <= 1000):
            raise ValueError("positive bounded target speed required")
        validate_target(obstacle_cm, initial_position_cm)
        if controller not in ("oscillator", "flight-policy"):
            raise ValueError("explicit controller kind required")
        if controller == "flight-policy":
            if pattern_kind != "measured-pattern" or expected_pattern_sha256 != WING_PATTERN_FMECH_SHA256:
                raise ValueError("the flight policy was trained with the pinned measured wing pattern")
            if policy_path is None or expected_policy_sha256 is None:
                raise ValueError("flight policy path and SHA-256 required")
            policy_sha = directory_sha256(policy_path)
            if policy_sha != expected_policy_sha256:
                raise ValueError("flight policy identity mismatch")
            for value in (reference_speed_cm_s, maximum_yaw_rate_rad_s):
                if type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= 100:
                    raise ValueError("positive bounded reference speed and yaw rate required")
            # The policy tracked 30 cm/s but lost the reference at 40 cm/s in body-only checks.
            if (type(maximum_speed_boost) not in (int, float) or not math.isfinite(maximum_speed_boost)
                    or not 0 <= maximum_speed_boost <= 1):
                raise ValueError("speed boost must be a fraction in [0, 1]")
        elif policy_path is not None or expected_policy_sha256 is not None:
            raise ValueError("the oscillator controller cannot carry policy metadata")

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
            "target_motion": "user-set goal; mocap sphere moves toward it at a bounded speed in physics time",
            "target_speed_cm_s": target_speed_cm_s, "target_bounds_cm": TARGET_BOUNDS_CM,
            "target_bounds_frame": TARGET_BOUNDS_FRAME,
            "sex_transfer": "male connectome coupled to female anatomical body; unvalidated transfer",
            "sensory": "ground-truth sphere angular expansion and engineered bilateral bearing weights; not a retinal model",
            "controller": "no RL policy; explicit basal oscillator plus neural residuals"}
        if controller == "flight-policy":
            import tensorflow as tf
            self.identity["packages"]["tensorflow"] = tf.__version__
            self.identity.update({
                "controller": "published flybody flight-imitation policy (learned low-level controller) tracking a neural-steered reference trajectory",
                "policy_sha256": policy_sha, "policy_source": "https://doi.org/10.25378/janelia.25309105 trained-fly-policies/flight",
                "initial_velocity_cm_s": [reference_speed_cm_s, 0.0, 0.0], "initial_wing_phase": "seeded uniform",
                "reference": {"future_steps": 5, "height_cm": float(initial_position_cm[2]), "pitch_deg": 47.5,
                              "base_speed_cm_s": reference_speed_cm_s, "maximum_yaw_rate_rad_s": maximum_yaw_rate_rad_s,
                              "maximum_speed_boost": maximum_speed_boost,
                              "heading_rad": 0.0},
                "motor_boundary": ("engineered decoder: DNp03 left-minus-right command (wing-yaw-offset field / 0.15) sets "
                    "reference yaw rate, sign chosen so stronger left DNp03 turns right (away-from-loom hypothesis); "
                    f"DNg02 command (frequency field / 0.05) raises reference speed by up to {maximum_speed_boost:.0%}; the learned policy, "
                    "not MaleCNS, produces wing actuation and stabilizes flight")})
            self.policy = _load_policy(tf, policy_path)
            signature = self.policy.__call__.concrete_functions[0].structured_input_signature[0][0]
            self.policy_inputs = {name: tuple(spec.shape[1:]) for name, spec in signature.items()}
            self.identity["policy_inputs"] = sorted(self.policy_inputs)
            self.identity["policy_action"] = "mean of Independent(Normal); canonical [-1, 1] clipped and rescaled to the action spec"
            # Graph-compiled mean: identical output, about 3x faster than eager calls.
            policy = self.policy
            self.policy_mean = tf.function(lambda inputs: policy(inputs).mean())
            self.tf = tf
        self.controller = controller
        self.reference_speed = reference_speed_cm_s
        self.maximum_yaw_rate = maximum_yaw_rate_rad_s
        self.maximum_speed_boost = maximum_speed_boost
        self.initial_obstacle = np.array(obstacle_cm, dtype=float)
        self.obstacle = self.initial_obstacle.copy()
        self.goal = self.initial_obstacle.copy()
        self.radius = obstacle_radius_cm
        self.target_step_cm = target_speed_cm_s*self.control_ms/1000
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
        # A mocap body lets the target move between control steps without
        # becoming a dynamic object; it remains a collidable rigid sphere.
        self.target_body = arena.mjcf_model.worldbody.add("body", name="flight_target",
            mocap=True, pos=obstacle_cm)
        self.target_body.add("geom", name="flight_visual_obstacle", type="sphere",
            size=[obstacle_radius_cm], rgba=[0.95, 0.35, 0.08, 1], contype=1, conaffinity=1)

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

        if controller == "flight-policy":
            from flybody.quaternions import mult_quat
            from flybody.tasks.base import Flying as _Flying
            from flybody.tasks.flight_imitation import FlightImitationWBPG
            from flybody.tasks.task_utils import com2root
            pitch_quat = np.array([math.cos(math.radians(-47.5)/2), 0, math.sin(math.radians(-47.5)/2), 0])
            dt = self.control_ms/1000

            class SteeredFlightTask(FlightImitationWBPG):
                """Flight imitation with an online reference instead of a recorded one."""

                def __init__(self):
                    super().__init__(walker=FruitFly, arena=arena, wbpg=pattern, traj_generator=None,
                        terminal_com_dist=2.0, trajectory_sites=False, initialize_qvel=True,
                        force_actuators=False, disable_legs=True, time_limit=float("inf"),
                        joint_filter=0.0, future_steps=5)
                    # The tracking ghost stays in the model but is never rendered.
                    for geom in self._ghost.mjcf_model.find_all("geom"):
                        geom.group = 5
                    self.command = (0.0, reference_speed_cm_s)

                def _append_reference(self):
                    # flybody never reads rows behind the current control step.
                    oldest = max(0, self._step_counter-1)
                    self._ref_qpos.reserve(self._ref_len, oldest)
                    self._ref_qvel.reserve(self._ref_len, oldest)
                    yaw_rate, speed = self.command
                    heading = self.heading
                    quat = mult_quat(np.array([math.cos(heading/2), 0, 0, math.sin(heading/2)]), pitch_quat)
                    direction = np.array([math.cos(heading), math.sin(heading), 0.0])
                    k = self._ref_len
                    self._ref_qpos[k, :3] = com2root(self.reference_com, quat)
                    self._ref_qpos[k, 3:] = quat
                    self._ref_qvel[k] = [*(speed*direction), 0, 0, yaw_rate]
                    self.reference_com = self.reference_com + speed*dt*direction
                    self.heading = heading + yaw_rate*dt
                    self._ref_len += 1

                def initialize_episode_mjcf(self, random_state):
                    _Flying.initialize_episode_mjcf(self, random_state)
                    self.command = (0.0, reference_speed_cm_s)
                    self.heading = 0.0
                    self.reference_com = initial.copy()
                    self._ref_qpos, self._ref_qvel, self._ref_len = _ReferenceRows(np, 7), _ReferenceRows(np, 6), 0
                    for _ in range(self._future_steps+1):
                        self._append_reference()
                    self._traj_timesteps = 2**62
                    self._reached_traj_end = False

                def before_step(self, physics, action, random_state):
                    # Extend the preview so it always covers the next five steps.
                    self._append_reference()
                    super().before_step(physics, action, random_state)

            self.task = SteeredFlightTask()
        else:
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
        self.obstacle = self.initial_obstacle.copy()
        self.goal = self.initial_obstacle.copy()
        return self._observe()

    def set_target(self, position_cm):
        if self.closed or self.env is None:
            raise ValueError("body must be reset before moving the target")
        fly = self.task.walker.get_pose(self.env.physics)[0]
        self.goal = self.np.array(validate_target(position_cm, fly), dtype=float)
        return self.goal.tolist()

    def _move_target(self):
        delta = self.goal - self.obstacle
        distance = float(self.np.linalg.norm(delta))
        if distance == 0:
            return
        if distance <= self.target_step_cm:
            self.obstacle = self.goal.copy()
        else:
            self.obstacle = self.obstacle + delta*(self.target_step_cm/distance)
        self.env.physics.bind(self.target_body).mocap_pos = self.obstacle

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
            "image_url": "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii"),
            "camera": self._camera_geometry(camera)}}

    def _camera_geometry(self, camera):
        """Pose of the rendered view so the observer can map pointer drags to world points."""
        physics = self.env.physics
        bound = physics.bind(camera)
        return {"position_cm": [float(v) for v in bound.xpos],
                "xmat": [float(v) for v in bound.xmat],
                "fovy_deg": float(physics.model.cam_fovy[bound.element_id])}

    def _policy_action(self, spec):
        """Deterministic policy mean, rescaled like acme's CanonicalSpecWrapper(clip=True)."""
        np = self.np
        observation = self.timestep.observation
        inputs = {}
        for name, shape in self.policy_inputs.items():
            value = np.asarray(observation[name], dtype=np.float32)
            if value.shape != shape:
                raise ValueError(f"policy observation {name} has shape {value.shape}, expected {shape}")
            inputs[name] = self.tf.constant(value[None])
        canonical = np.clip(self.policy_mean(inputs).numpy()[0].astype(float), -1, 1)
        if canonical.shape != spec.shape:
            raise ValueError("policy action size differs from the body action spec")
        return spec.minimum + (canonical+1)/2*(spec.maximum-spec.minimum)

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
                "obstacle_angle_rad": angle, "target_cm": self.obstacle.tolist(),
                "target_goal_cm": self.goal.tolist(), "target_radius_cm": self.radius,
                "terminal": bool(self.terminal), **self._reference_state()}

    def _reference_state(self):
        if self.controller != "flight-policy":
            return {}
        yaw_rate, speed = self.task.command
        return {"reference": {"yaw_rate_rad_s": float(yaw_rate), "speed_cm_s": float(speed),
                              "heading_rad": float(self.task.heading),
                              "com_cm": [float(v) for v in self.task.reference_com]}}

    def advance(self, action):
        if self.closed or self.env is None or self.terminal:
            raise ValueError("body must be reset and nonterminal")
        required = {"left_wing_yaw_offset_rad", "right_wing_yaw_offset_rad", "frequency_fraction"}
        if set(action) != required or any(type(v) not in (int, float) or not math.isfinite(v) for v in action.values()):
            raise ValueError("finite allowlisted wing commands required")
        if abs(action["frequency_fraction"]) > 0.05 or any(abs(action[key]) > 0.15 for key in required if key != "frequency_fraction"):
            raise ValueError("wing command exceeds the frozen adapter bounds")
        spec = self.env.action_spec()
        if self.controller == "flight-policy":
            turn = action["left_wing_yaw_offset_rad"]/0.15
            power = max(0.0, action["frequency_fraction"])/0.05
            self.task.command = (-turn*self.maximum_yaw_rate, self.reference_speed*(1+self.maximum_speed_boost*power))
            controls = self._policy_action(spec)
            self._move_target()
            self.timestep = self.env.step(controls)
            self.terminal = self.timestep.last()
            return self._observe()
        controls = self.np.zeros(spec.shape)
        wing_indices = self.task.walker._action_indices["wings"]
        if len(wing_indices) != 6:
            raise ValueError("upstream wing actuator interface changed")
        controls[wing_indices[0]] = action["left_wing_yaw_offset_rad"]
        controls[wing_indices[3]] = action["right_wing_yaw_offset_rad"]
        self.task.frequency_fraction = action["frequency_fraction"]
        self._move_target()
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

    def set_target(self, position_cm):
        return self._call("set_target", list(position_cm))

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
