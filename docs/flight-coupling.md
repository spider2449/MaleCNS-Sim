# Engineered MaleCNS flight coupling

This application connects the public resumable neural runtime to physical wing
actuation. The browser observes model-owned poses and eye cameras. Run, pause,
single-step, and reset control execution; they do not steer the body.

## Model boundaries

`native_flight_mapping()` contains the audited MaleCNS v1.0 LC4, DNg02, and DNp03
body IDs. Construction rejects a prepared network missing any mapped neuron.
LC4 receives seeded spike schedules derived from obstacle angular expansion.
Phototransduction, retinal geometry, and upstream visual processing are bypassed.
The expansion features use physical geometry, not camera-pixel reconstruction.
Camera images are observational and do not supply the injected signal.

DNg02 rates modulate wingbeat frequency; the DNp03 bilateral rate difference
modulates opposite wing yaw offsets. These gains and side polarity are engineering
hypotheses. They are not calibrated physiological decoders. The body uses the
female flybody anatomy with a male neural network, an unvalidated sex transfer.
An explicitly selected engineered oscillator supplies basal wing motion. No
learned flight policy, target trajectory, or controller is loaded.

The neural grid must divide the 0.2-ms actuator interval exactly. The body
integrates at 0.05 ms. Rendering and browser pacing never advance scientific
time. Sessions run continuously by default until paused or stopped. Optional
finite maximum_steps may be supplied for bounded checks. Failure after
either subsystem mutates poisons the coupled state; reset is required, with no
automatic retry or rollback.

Event exports retain the most recent 10000 events and report dropped_events and
complete_history. Long-running exports are a rolling window, not a complete
trajectory archive. Physical termination remains authoritative even with no
time limit. Continuous operation does not establish stable flight.

## Interactive target

The observer may move the orange target sphere. Users can drag it in the body
view, on the plane at its current height. They can also drag on the top-down
path map or use the height slider. The browser only proposes a goal
(`target_cm`, centimeters). It travels as a `target` command or rides on the
next `tick` and never sets a pose. The session records each goal as a `target`
event at the current simulated time. The body then moves a mocap sphere toward
it at `target_speed_cm_s` (default 50) in physics time. No simulated time
passes while a goal is set. Goals are bounded to x, y within [-10, 10] cm of the
fly's position when the goal is set, and z in [0.1, 5] cm. Reset restores the
initial target.

The target moves at bounded speed, so it never jumps. LC4 input still comes only
from geometric looming as the target and the fly approach each other. A dragged
goal can therefore change the DNp03/DNg02 readout and the wing commands, and so
the path. This is not a pursuit or avoidance controller, and a visible path
change is not guaranteed. The frame response includes the third-person camera
pose, which the observer uses only to map pointer positions to world points.

## Dependency isolation

The physical adapter requires Python 3.12 and this exact upstream revision:

```powershell
uv venv --python 3.12 ../.codex-envs/malecns-flight-20261008
uv pip install --python ../.codex-envs/malecns-flight-20261008/Scripts/python.exe 'flybody @ git+https://github.com/TuragaLab/flybody@d015e9bfe441bd90ae431bac24c55cb74bdbce26' pyarrow pandas scipy
```

### Environment verified on 2026-10-19 (Windows 10, Python 3.12.10)

The whole launcher runs inside the flybody environment, because the physical body
is created in-process. The environment therefore needs this project as well. Keep
it outside the checkout so the project's Python 3.14 environment and lockfile stay
intact:

```powershell
python3.12 -m venv D:\spider\flybody-env
D:\spider\flybody-env\Scripts\python.exe -m pip install -e .          # from the repo root
D:\spider\flybody-env\Scripts\python.exe -m pip install 'git+https://github.com/TuragaLab/flybody.git@d015e9bfe441bd90ae431bac24c55cb74bdbce26'
D:\spider\flybody-env\Scripts\python.exe -m pip install 'numpy>=2'
# flight-policy controller only:
D:\spider\flybody-env\Scripts\python.exe -m pip install -c constraints.txt tensorflow tensorflow-probability tf-keras
```

`constraints.txt` contains the single line `numpy>=2`, so TensorFlow cannot
downgrade numpy again. The resulting versions were mujoco 3.16.0, dm_control
1.0.49, tensorflow 2.21.0, tensorflow-probability 0.25.0, tf-keras 2.21.0 and
numpy 2.5.4. Launch with that interpreter:

```powershell
D:\spider\flybody-env\Scripts\python.exe scripts\run_real_flight.py --controller flight-policy --open
```

Why numpy is upgraded: installing flybody downgrades numpy to 1.26.4, but this
project's pyarrow requires numpy 2, so `import malecns_sim.application` fails
with `pyarrow requires NumPy 2.0 or newer`. flybody's package metadata pins
`numpy==1.26.4`, so `pip check` reports a conflict. This is metadata only: with
numpy 2.5.4 the body, the flight-policy SavedModel and a full real-network run
all worked. Without the TensorFlow packages, `--controller flight-policy` cannot
start, and a missing `flybody` install fails with `PackageNotFoundError: No
package metadata was found for flybody`.

Preparing the registered network takes about 4.5-5.5 minutes before the server
prints its URL.

The adapter verifies the installed VCS commit and records model asset hashes,
dependency versions, units, initial conditions, pattern kind, and coupling gains.
A measured pattern additionally requires an explicit file and SHA-256. It never
silently substitutes an oscillator for a requested measured pattern.

## Host integration

The normal workbench does not prepare a real flight network. Its `/flight` page
reports an unconfigured session until a host supplies a prepared runtime.
The integration seam is:

```python
from malecns_sim.application.flight import FlightSession
from malecns_sim.application.flight_body import FlybodyBody
from malecns_sim.application.flight_populations import native_flight_mapping
from malecns_sim.application.server import LocalServer

body = FlybodyBody(pattern_kind="engineered-oscillator")
session = FlightSession(
    certified_runtime,
    native_flight_mapping(),
    body,
    expected_projection_fingerprint=certified_effective_projection_fingerprint,
)
server = LocalServer(0, flight_session=session)
try:
    print(f"http://127.0.0.1:{server.server_port}/flight#token={server.token}")
    server.serve_forever()
finally:
    server.server_close()
```

`certified_runtime` and its expected effective-projection fingerprint must come
from the project's separately approved, bounded preparation route. They are not
placeholder values to guess, and a matching fingerprint alone does not certify
source provenance or execution budgets. This module neither reads datasets nor
prepares graphs. Do not use a synthetic runtime with the native mapping.

The server protects snapshot, frame, command, and event export routes using its
existing loopback session token. Commands include the current generation and
revision. Stale commands are rejected. Reset starts a new generation.

For matched controls, select `sensory_disconnected`, `decoder_masked`, or
`fixed_actuator` with `session.set_condition(...)` before stepping. The latter
two both remove neural actuator residuals while retaining basal wing motion;
they are equivalent in this adapter. Exports include the condition and complete
step evidence. No control condition or successful synthetic test establishes
biological flight behavior.

## Validation scope

`tests/test_flight_coupling.py` exercises actual resumable LIF execution with a
small synthetic network and an explicitly synthetic body fixture. It checks
continuity, replay, controls, failure poisoning, identity admission, and HTTP
protection. `tests/js/flight_coupling.cjs` checks browser request serialization
and display pacing. `scripts/check_flight_body.py` is a separate guarded,
bounded physical-body and camera smoke. None executes a full-real MaleCNS
flight experiment or certifies stable flight.

## Learned flight-policy controller

The oscillator body has no feedback and loses height within tens of
milliseconds. `--controller flight-policy` instead uses the published flybody
flight-imitation policy (DOI 10.25378/janelia.25309105, `trained-fly-policies/flight`).
The policy was trained with the measured wing pattern `wing_pattern_fmech.npy`.
Both files are pinned by SHA-256 in `flight_body.py`:

```powershell
python scripts/fetch_flybody_assets.py            # -> data/flybody (gitignored)
python scripts/run_real_flight.py --controller flight-policy --open
```

The flight environment additionally needs TensorFlow and TensorFlow
Probability. Two combinations are known to work. The first is
`tensorflow-cpu==2.17.1` and `tensorflow-probability==0.24.0` with numpy kept at
flybody's pinned 1.26.4, which requires pyarrow below 20 because pyarrow 20+
requires numpy 2. The second, verified on 2026-10-19, is tensorflow 2.21.0,
tensorflow-probability 0.25.0 and tf-keras 2.21.0 with numpy 2.5.4 (see
"Environment verified" above).
The published SavedModel was exported by an older TFP. The loader therefore
registers the old `Independent` TypeSpec name before loading.

Division of labour:

- The policy tracks a reference trajectory with a 5-step (1 ms) preview. It
  flies at 1 cm height and 47.5° pitch with a base speed of 20 cm/s. The
  policy produces all wing and body actuation. Its deterministic mean action
  is used.
- MaleCNS steers only the reference. The decoded DNp03 left-minus-right command
  sets the reference yaw rate, up to 20 rad/s. `FlybodyBody(loom_response=...)`
  selects the sign: `"approach"` (default) makes stronger left DNp03 turn left,
  and `"avoid"` makes it turn right, the original away-from-loom hypothesis. Both
  are engineering hypotheses and the choice is recorded in the body identity. The DNg02 command raises
  reference speed by up to 50%, to 30 cm/s. In body-only checks, the policy
  tracked 30 cm/s but lost the reference and fell at 40 cm/s. The session spec's `motor_boundary` records this
  mapping.
- Termination follows the upstream task. The episode ends when thorax height
  drops below 0.2 cm or the body drifts more than 2 cm from the reference.

In this configuration, the flight is the policy's, not MaleCNS's. Only course
changes trace back to the neural readout. The policy was trained on recorded
trajectories of female flies. The reference is synthetic, so it lies within
but at the edge of that training distribution. In a body-only check without
the network, a straight reference held 20 cm/s at about 1.02 cm height for
300 ms. A saturated turn command produced a 115° heading change tracked
within 1 mm.
Each control step costs about 5 ms of wall time for the body and policy,
before neural time.
The launcher starts the target at (3.0, 0.3, 1.0) cm, ahead of the fly and
off the straight reference line.

### Target collision

By default the target is a pass-through visual stimulus
(`FlybodyBody(solid_target=False)`): the fly can fly through it. A solid sphere
(`solid_target=True`) ends the episode: a head-on hit at 1.5 cm knocked the policy
off balance within about 90 ms, and the episode ended after about 450 control
steps. Removing the 2 cm tracking-distance termination did not help, because the
fly still lost balance and fell, ending the episode at about 700 steps. So pass-through is
the only way to keep an episode alive after the fly reaches the target.

### Neural drive and input weight

On the real 166,700-neuron network the original `input_weight_mV=1.0` produced
almost no response. LC4 input is capped at 200 Hz, so the mean depolarisation is
about 0.2 events/ms x 1 mV x 20 ms = 4 mV, below the 7 mV gap to threshold.
Over a 190 ms episode the sensory cells fired 9 spikes, the single DNp03 turn
neuron fired once and the DNg02 power cells never fired. A sweep over 1, 2, 4,
7 and 10 mV over 300 ms found 2 mV to be the smallest value that drives the turn
neurons (5-8 turn spikes and a command near the 0.15 rad limit), so
`FlightParameters.input_weight_mV` now defaults to 2.0. At 2 mV with the default
`"approach"` sign, a target 0.6 cm to the left gave +3.9 cm of lateral
displacement, one to the right gave -1.2 cm, and a target dead ahead was passed
through, with no episode ending in any of them. The right side responds more
weakly. The sensory populations have 71 (left) and 55 (right) cells and the
cause of the asymmetry was not investigated. One run at 4 mV produced a burst
of 59,788 network spikes that did not repeat at 7 or 10 mV. DNg02 (power) cells
stayed silent in nearly every run, so speed is effectively not modulated. These
are diagnostics of one synthetic placement protocol, not a validated behavioural
model. The turn command also accumulates in the reference heading, so a course
change persists after the target is passed.
