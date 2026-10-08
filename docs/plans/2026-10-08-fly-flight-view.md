# Fly flight view

Date: 2026-10-08

## Requirement correction

The user rejected the independent flight/game interpretation: the view must
accompany a fly simulation coupled to this project. The prototype described
below is superseded and does not satisfy that requirement. Its static checks
are not evidence of neural, body, sensory, or biological flight simulation.
The prototype entry, static routes and three newly created assets were removed.
Existing accepted Arena behavior remains unchanged. Current research and the
user-selected real-MaleCNS direction are recorded in
`2026-10-08-malecns-flight-coupling.md`.

## Corrected architecture and next steps

1. Determine whether the requested initial scope is actual MaleCNS coupling or
   synthetic coupling for interface validation. The user was asked this explicitly.
2. Reuse the existing public `malecns_sim.runtime` prepare/advance/state contract;
   do not implement a separate neural engine in the browser.
3. Specify visual/mechanosensory input encoding, input neuron identities, motor
   readout identities, and the evidence supporting their roles. The existing
   sugar/MN9 workflow does not establish flight sensory or motor identities.
4. Specify an explicit body model, coordinates, units, initial conditions,
   aerodynamic forces, actuator mapping, fixed control interval, integration
   method, and environment feedback. Identify engineered assumptions separately
   from empirical parameters. No unverified neuron roles or arbitrary spike-to-
   flight equations may be presented as established fly biology.
5. The backend owns neural and body state, simulation time, and sensory feedback.
   The first-person view consumes authoritative poses and neural/action evidence.
   Camera settings affect presentation only. Remove navigation scores, manual
   locomotion, and animation-clock-generated body motion.
6. Bind network, mappings, body parameters, stimuli, initial state, interventions,
   and clocks into a versioned run identity. Preserve pause/step/reset and replay;
   record applied sensory events, neural output, actuator values, and body states.
7. Establish bounded execution and controls before real runs. Do not extrapolate
   synthetic or historical benchmark speed to full-real interactive flight.

## Current feasibility evidence

Source review confirms that `runtime.py` provides the resumable neural API.
`ArenaSession` in `application/arena.py` fixes a four-neuron synthetic graph and
engineered planar motor decoding; it is not a three-dimensional fly body model.
`application/workbench.py` offers the bounded sugar/MN9 experiment rather than a
flight input/readout contract. A012's proposal explicitly declines biological
steering reconstruction; A020 records real closed-loop integration as deferred.
No flight adapter, biological identity, or end-to-end flight result was verified.
No dataset payload access, runtime import, preparation, or simulation occurred
during this correction. The coupling choice and flight-specific scientific
contract remain unresolved; actual fly simulation is not implemented.

## Superseded prototype record

## Authorized scope

Build a fly-inspired first-person flight application. This is an engineered
visual and interaction demo, independent of connectome data and neural execution.
No biological fidelity or scientific flight result is claimed.

## Implementation

1. Preserve the incoming untracked release and validation records.
2. Add dependency-free Canvas 3D scenery, flight controls, ring navigation,
   telemetry, pause/reset, and an illustrative compound-eye overlay.
3. Provide a workbench link and an explicitly allowed static route. Support
   opening flight.html directly without a server or dataset access.
4. Check JavaScript syntax and interactions using only the new static assets.
   Inspect the rendered page in a browser; do not run scientific tests or builds.

## Controls

W/S adjusts forward drive; A/D or left/right arrows steers; up/down arrows
changes pitch; Space climbs; C descends; Shift boosts; P pauses; R resets.
On-screen held buttons provide pointer and touch control. Mouse drag looks
around while running. Blur or a hidden tab pauses and clears held input.

## Validation

- JavaScript syntax, Python server AST parsing, and git diff whitespace passed.
- The three new static files were served over loopback and verified byte-for-byte.
- A Node VM with a stubbed DOM/Canvas verified initial pause, forward movement,
  ring-plane crossing, keyboard pause, climb, steering, pitch, blur, reset,
  touch-input release, compound-overlay execution, FOV changes, and hidden-tab
  pause. These checks verify control logic, not actual browser rendering.
- Browser inventory was empty; visual rendering and real keyboard/touch browser
  acceptance remain unverified. No scientific tests, builds, dataset reads,
  neural execution, or dependency installation were performed.
- Incoming untracked release/validation files remain present. No commit or push.

## Opening the application

Open `src/malecns_sim/application/static/flight.html` directly in a browser.
The application has no external assets, API calls, or runtime dependencies.
An existing workbench server can also serve `/flight` after restart; the
workbench home page includes a link. Starting the scientific server is not
necessary for this demo.

The scene uses illustrative millimeter coordinates, not calibrated biological
geometry. Grass and flowers are scenery; terrain and garden bounds constrain
movement, while obstacle collision and aerodynamic dynamics are not modeled.
