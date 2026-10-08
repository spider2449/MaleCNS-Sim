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

## Dependency isolation

The physical adapter requires Python 3.12 and this exact upstream revision:

```powershell
uv venv --python 3.12 D:/spider/working/.codex-envs/malecns-flight-20261008
uv pip install --python D:/spider/working/.codex-envs/malecns-flight-20261008/Scripts/python.exe 'flybody @ git+https://github.com/TuragaLab/flybody@d015e9bfe441bd90ae431bac24c55cb74bdbce26' pyarrow pandas scipy
```

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
