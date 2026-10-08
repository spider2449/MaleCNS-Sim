# MaleCNS flight coupling: identity and model assessment

## Git handoff

Base: ca58e6a860705784210c45f1670774601f5d7e04 on master, matching fetched
origin/master before this task commit. Include the flight modules, authenticated
server routes, static observer, native population mapping, explicit real launcher,
guarded audit/body/profile scripts, plans, guide, fixtures, and task evidence.
Preserve pre-existing A025 scripts/evidence, publication plans, and docs/references
without staging them. No raw MaleCNS dataset or isolated dependency environment
is included in Git. The finite annotation audit record is included as provenance.

Final targeted validation: 44 Python tests passed across public runtime,
flight coupling, and workbench-session suites under the existing source firewall;
the JavaScript flight observer regressions passed. One existing CuPy CUDA-path
warning was emitted. Independent body-only checks established live frames,
cross-thread rendering, exact short replay, JPEG decoding, and 800-ms operation.
These are not autonomous/stable-flight certification or full-real performance
certification. Earlier real-source execution remains documented as historical
execution, distinct from guarded synthetic validation. Do not infer a complete
real-execution certification from source fingerprints or a successful launch.

## Third-person presentation follow-up

Continuous operation was explicitly requested. The default maximum_steps is
now None; the physics task and composer environment have no time limit. Optional
finite limits remain supported for fixtures. Pause, explicit stop, and physics
termination/failure remain authoritative. Event export retains a rolling 10000
events with dropped-event count and complete_history=false after eviction;
it is not represented as a complete trajectory archive. Validate a synthetic
coupled session beyond 600 ms and the isolated body beyond its old 0.6-s cutoff.
These checks establish continuity only, not stable or autonomous flight.

Silent-readout and runtime-overhead follow-up: cumulative applied input events,
LC4 spikes, selected motor spikes, and total network spikes distinguish absent
input from silent sensory or motor populations. Cumulative neural/body wall
times and per-frame render time are diagnostic measurements, separate from
deterministic scientific step evidence. No gain or neural model parameter was
tuned to create activity. A runtime membership cache replaces rebuilding the
166700-ID set on every control interval; the immutable owned snapshot retains
the same admission and identity rules, including the experimental GPU facade.
Guarded synthetic profiling measured 27.645 ms median for the old membership
rebuild versus 0.074 ms for cached full preflight; full empty-graph advance was
11.245 ms. These are synthetic overhead figures, not full-real performance or
real-time certification. The public runtime and flight suites passed 39 tests.

JPEG display correction: the existing CSP permits same-origin resources only,
so assigning a data URL to an HTML Image blocked compressed frames. Decode
base64 bytes into a Blob and createImageBitmap directly, then draw onto the
canvas. No image-resource load or CSP weakening is needed. The JavaScript
regression rejects Image construction while verifying the byte-decoding path.

Playback performance correction: each running tick advances up to 20 existing
0.2-ms control intervals (4 ms total), stopping at the original episode limit.
Manual step remains one interval. No sensory or motor update is skipped.
The primary 512px view is transmitted as quality-85 JPEG data rather than RGB
array JSON; auxiliary renders are omitted on this fast path. Display reports
measured simulation-time/wall-time ratio and displacement from the initial pose.
Matched sequential-versus-batched synthetic evidence and guarded JPEG decoding
checks validate the route. These changes do not prove real-time performance or
neural flight control. A tracking camera keeps the body centered while it moves.

Continuous display correction: retain the previous physical frame during a
pending camera request. Resize canvas buffers only when dimensions change and
replace pixels after full validation. A transient render failure retains the
last frame with its actual timestamp and a holding label. Delayed-frame and
temporary-failure regressions verify that configured playback never clears the
canvas between valid frames. This changes display continuity, not neural clocks.

The user selected a third-person primary view after reporting unreadable,
pixelated eye images. The primary camera now uses the upstream position-following
track3 view at 512x512 with four-sample antialiasing. Eye previews are 256x256 in
an auxiliary expandable section. Browser scaling uses normal interpolation.
Scene labels identify the checkerboard floor, blue gradient background, and
orange target sphere. Only environment group 0 is visible in eye previews;
the external camera includes cosmetic fly geometry in group 1.

Actual physical renders were inspected. Guarded body validation verifies live
third-person frames at 0, 10, and 36.2 ms, cross-caller rendering, and exact
10-ms replay. This check does not prepare or advance a real neural runtime.
Earlier launcher execution in this conversation did load the registered sources
and prepare 166700 real neurons; initial zero-real statements below describe
the earlier implementation phase, not the entire conversation.

Camera correction: replace the reset-only cached image with live rendering on
one persistent physics worker. Creation, reset, advance, render, and cleanup
all execute on that worker. Hide the fly's own geometry in eye rendering only,
preserving collisions and fluid forces. Validate changing frames and calls from
different caller threads with the guarded body-only smoke. Do not repeat a
full-real preparation for this camera check.

Date: 2026-10-08

## User-selected objective

Establish actual MaleCNS flight coupling. First confirm neurons, sensory input,
and a flight dynamics model, then implement. An independent browser flight game
or the existing four-neuron synthetic arena does not satisfy the objective.

The user subsequently selected engineered post-retinal injection, explicitly
labeling skipped phototransduction. Implement the coupling interfaces and an
optional flybody adapter without replacing the MaleCNS neural engine or inserting
a learned controller. LC4 is the initial bilateral visual-projection injection
candidate; use the native local labels and somaSide recorded in the audit.
Do not claim that geometry-derived expansion reconstructs LC4 physiology.

Implementation may validate synthetic neural fixtures and an isolated body-only
model. Full-real neural preparation and flight execution are still separate from
these checks and must use a finite supervised real-source route. The coupling
constructor accepts an already prepared public runtime; it never loads datasets.

An isolated Python 3.12 environment outside the checkout may install the author's
core flybody revision `d015e9bfe441bd90ae431bac24c55cb74bdbce26` and prerequisites.
No ML/RL extensions or pretrained controllers are part of the coupling.
The current Python 3.14 / NumPy 2.5.3 environment and project lockfile stay intact.

## Finite metadata admission

The first local audit may read exactly one registered annotation file:
`data/raw/male-cns/v1.0/body-annotations-male-cns-v1.0-minconf-0.5.feather`,
expected SHA-256
`2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`.
This metadata read follows the user's instruction to confirm neuronal identity;
it is not a real dynamics run or a new performance attempt. Do not claim zero
registered-source reads. Read once to an in-memory buffer; reject wrong identity
before parsing. Install read admission before importing the Arrow reader.
Do not read connectivity, neurotransmitter, mapping, other registered payloads,
archives, or external data roots. Do not import this project's runtime, discover
tests, prepare graphs, or execute neural/body models during the metadata audit.
Write a new finite audit record containing predicates, source identity, columns,
candidate IDs, side fields, and unresolved spatial/motor interpretation.

## Research and decision sequence

1. Review primary flight-control studies and official MaleCNS cell-type resources.
2. Resolve candidate populations against the admitted local annotation snapshot.
   Keep native `type` and `flywireType` matches separate; never silently select
   a walking neuron, infer actuator polarity from root/soma side, or substitute
   another dataset's body IDs.
3. Determine a sensory route and independently bound optical geometry. Raw
   pixels/hex-grid coordinates are not a calibrated retinal sampling map.
4. Assess the author's flybody/MuJoCo model and explicit wing actuation interface.
   Distinguish its female body and learned controllers from the male connectome.
5. Implement only mappings supported by explicit identities and parameters.
   The neural engine, body physics, and rendering have separate clocks/owners;
   display pacing cannot create motion or change neural schedules.
6. Before an actual model run, establish a finite source/preparation identity,
   bounded CPU resources/duration, explicit input realization, controls, and
   replay/evidence export. No inherited benchmark authorization is reused.

## Starting workspace

HEAD: `ca58e6a860705784210c45f1670774601f5d7e04`. Preserve the incoming A025
and publication files, `docs/references/`, and the superseded prototype record.
No reset, stash, commit, push, release change, or historical evidence rewrite.
The prototype's navigation controls are not part of the corrected application.

## Result

**IDENTITIES FOUND; FLIGHT COUPLING NOT IMPLEMENTATION-READY.** The annotation-only
audit passed its source SHA-256 check. One registered annotation file was opened
and parsed; no graph or neurotransmitter payload was read by this audit. Results
are in `docs/manifests/2026-10-08-flight-neuron-audit.json`. This is metadata
evidence, not a claim of zero registered reads or native-byte telemetry.

### Confirmed local annotation candidates

| Candidate | Local body IDs / counts | Confirmed boundary |
| --- | --- | --- |
| DNg02 subtypes | 29; somaSide L=15, R=14 | Native type prefix matches; not a balanced 15-pair assumption |
| DNp03 | L=10752, R=10989 | Soma side, not wing actuator polarity |
| DNa15 | L=10884, R=10837 | Native local label; literature alias DNae014 requires explicit cross-reference |
| DNb01 | L=10654, R=10759 | Native local label; no transmitter file inspected |
| DNp20 | L=10162, R=10059 | Orientation-related candidate, not calibrated pitch command |
| DNp22 | L=12306, R=11872 | Orientation-related candidate, not calibrated roll command |
| R1-R6 | 3377 native type matches | Distinct from the 6006 broader type/alias photoreceptor matches |

All finite regex predicates and exact matched native/alias labels are retained
in the audit. The 6006 photoreceptor matches include R7/R8 subtypes matched via
other label fields; do not use this number as the R1-R6 population. The wing-MN
label regex matched zero rows; this means that predicate did not resolve motor
neurons, not that wing motor neurons are absent. The source has
`assignedOlHex1`/`assignedOlHex2`; this audit retained their column names but did
not retain their per-neuron values or validate angular eye coordinates.

### Primary flight-circuit evidence

[Namiki et al. (2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9206711/)
supports DNg02 as a flight-related population regulating wingbeat amplitude.
It does not supply a universal local-LIF-spike-count to MuJoCo torque decoder.

[The 2025 flight-saccade study](https://www.sciencedirect.com/science/article/pii/S0960982224016415)
supports DNp03 involvement in looming-associated flight saccades and explicitly
reports behavioral-state dependence and incomplete explanatory power of its
activity. It does not justify instantaneous signed yaw from its soma side.

[Ros et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC10872223/) studies the
DNae014/DNb01 spontaneous-flight-turn network. The local DNa15 name and
DNae014 alias are also discussed in the
[flight-saccade report](https://pure.mpg.de/pubman/item/item_3630220_9/component/file_3630221/1-s2.0-S0960982224016415-main.pdf?mode=download).
The official [DNa15 cell-type page](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/DNa15_R.html)
and [DNp03 page](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/DNp03_R.html)
are cross-check resources; the hash-verified local snapshot owns the IDs above.

### Sensory input: initial assessment before route selection

[Photoreceptor experiments](https://pmc.ncbi.nlm.nih.gov/articles/PMC3432082/)
describe non-spiking photoreceptors and graded histamine release. Existing
`src/malecns_sim/sign.py` contains no histamine entry in Shiu2024SignPolicy or
ConservativeSignPolicy. Therefore preserving the current engine while driving
R1-R6 with arbitrary Poisson impulses does not establish physiological visual
transduction. No source neurotransmitter identities, outgoing paths, or effective
projection were inspected here; do not assert which particular edges a future
preparation will retain or remove.

Two distinct future designs must be explicit: a separately validated graded
photoreceptor/histamine front end, or an engineered post-retinal input boundary
on real visual interneurons. Neither may silently be called a full reconstructed
retina. The latter is technically compatible with chunk-local ExplicitStimulus,
but its injection cells, receptive fields, gains, dynamics, and bypassed stages
must be fixed before a run.

The [MaleCNS paper](https://doi.org/10.1016/j.cell.2026.08.015) describes an eye
map extended to male medulla-column ROIs. The authors' [eye-map repository](https://github.com/reiserlab/eyemap_T4)
provides related optical mapping methods. An external eye map still requires
its own pinned identity and a measured join to local neuron IDs; column indices
alone cannot establish gaze direction, acceptance angles, or handedness.

### Flight body: initial dependency assessment

The author's [flybody repository](https://github.com/TuragaLab/flybody) is the
appropriate body-model candidate because it exposes physical wing actuation and
MuJoCo flight environments. The [whole-body study](https://www.nature.com/articles/s41586-025-09029-4)
uses a female D. melanogaster body and learned control. Coupling it to this male
connectome is a cross-sex model transfer requiring an explicit scope statement.
Reusing its learned flight policy would not establish control by MaleCNS.

The inspected [flight constants](https://raw.githubusercontent.com/TuragaLab/flybody/main/flybody/tasks/constants.py)
set physics dt=0.05 ms, actuator control dt=0.2 ms, and nominal wingbeat=218 Hz.
The [Flying base class](https://raw.githubusercontent.com/TuragaLab/flybody/main/flybody/tasks/base.py)
exposes left/right wing yaw, roll and pitch joints and phenomenological fluid
forces. The [imitation task](https://raw.githubusercontent.com/TuragaLab/flybody/main/flybody/tasks/flight_imitation.py)
combines wing pattern and actuator corrections; this is not a direct DN decoder.
The [pattern generator](https://raw.githubusercontent.com/TuragaLab/flybody/main/flybody/tasks/pattern_generators.py)
explicitly labels its missing-data fallback as an artificial approximation.
Actual wing-pattern data, package/model revisions, asset hashes, actuator gains,
units and decoding must be bound; no silent artificial-pattern fallback is
accepted. The later user-selected engineered route permits an explicitly named
engineered oscillator with its limitation recorded in the model identity.

These are reviewed mutable upstream sources, not an installed or hash-pinned
dependency. The [upstream dependency declaration](https://raw.githubusercontent.com/TuragaLab/flybody/main/pyproject.toml)
pins NumPy 1.26.4 and depends on dm_control. Do not change this project's lockfile
or assume the current Windows/Python environment is compatible without an
isolated dependency assessment. No dependency was installed during this initial
research assessment. The later isolated installation is recorded separately.

### Implementation gate and proposed first experiment

The first scientific question should be bounded: whether a defined visual
perturbation changes identified flight-related neural activity and whether that
activity changes the explicitly coupled physical wing/body response. This is a
proposal, not an already authorized frozen experiment or a biological result.
Use matched intact, sensory-disconnected, decoder-masked and fixed-actuator
controls, plus exact input replay. A flat neural response, unstable body or no
coupling effect is a valid negative outcome; do not substitute walking neurons,
tune until a desired trajectory appears, or replace the network with a learned
controller after observing the result.

Outstanding implementation dependencies are:

- Retinal geometry and an explicit graded-vs-post-retinal sensory model choice.
- Flight-state modulation and the local-to-literature cell/side correspondence.
- Wing motor identities or a declared calibrated DN-to-actuator boundary.
- Actual wing kinematics, body version, units and sex-transfer limitations.
- Clock bridging: current neural grid is 0.1 ms, while the candidate body needs
  0.05-ms integration and 0.2-ms actuator updates. The old 20-ms arena interval
  is not automatically a flight-control interval. Rate filtering and held-action
  semantics need explicit design and validation.
- A bounded full-real execution route and measured cost for this new contract.

The autonomous game route was removed. The superseded plan records the
requirement correction. The same flight asset names now contain a scientific
observer for a host-injected session. Existing Arena logic is unchanged.

### Bounded checks

Under the unchanged A019C guarded-child entrypoint, in-memory fixture checks
passed native-versus-alias selection, walking-neuron exclusion, spatial-column
inventory, regular-file admission and hard-link rejection. Derived-record checks
passed source hash, one admitted registered-open event and candidate counts.
Script AST parsing and `git diff --check` passed. No registered payload was read
by those checks, and no project runtime was imported. The annotation audit itself
used the separate, explicitly finite annotation admission above.

After the audit, the script's read policy was additionally tightened to reject
relocated registered-release basenames. The source annotation was not reopened;
the existing audit record is from the earlier script revision. Neither script
revision changes the project's existing validation firewall.

## Engineered implementation

`application/flight.py` couples an already prepared public CPU runtime to a body
protocol, with audited native populations in `flight_populations.py`. It binds
effective projection and neural parameter fingerprints, body identity, explicit
gains, seeded input schedules, and control condition. No source loading or graph
preparation is performed. All mapped neurons must be present.

`flight_body.py` implements physical MuJoCo wing actuation at 0.2 ms and body
integration at 0.05 ms using the pinned flybody commit above. No learned policy
is loaded. The adapter exposes geometry-derived expansion and physical eye
images. Camera pixels do not drive the neural stimulus. Basal wing motion uses
an explicitly selected engineered oscillator.

The authenticated `/api/flight` routes expose a supplied session. The `/flight`
page displays clocks, sensory input, neural rates, actuator outputs, and eye
cameras. Absence of a host-supplied runtime is visible and execution stays
disabled. UI pacing does not integrate a pose or establish biological real time.

Eleven guarded synthetic-neural tests passed, including actual public LIF
execution, exact replay, controls, failure poisoning, mapped-ID admission,
clock continuity, and authenticated HTTP. JavaScript observer tests passed
request serialization, command-error stopping, and hidden-page pacing. These
checks do not establish real MaleCNS flight or stable physical flight.

See [the integration guide](../flight-coupling.md) for host injection and explicit
model boundaries. A bounded, certified full-real preparation/execution route
remains required before claiming a real-network flight experiment. No
connectivity or neurotransmitter payload was read and no real neural runtime
was prepared or advanced during this implementation.
