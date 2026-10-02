# MaleCNS simulation workbench user guide

## What this application can and cannot establish

This connectome simulation workbench supports virtual intervention screening,
computational hypothesis prioritization, comparison of model outputs, and
robustness evidence across explicitly defined model variants. It cannot establish
a digital twin, a reconstructed biological brain, behavior prediction, a proven
causal mechanism, direct inhibition solely from an output delta, necessity, or
biological robustness without separately justified evidence. Anatomical synapse
counts and model sign policies are not measured functional synaptic physiology.

## Install and start

Use Python 3.12 or newer and uv. In a development checkout:

```powershell
uv sync --frozen --group dev
uv run malecns-workbench
```

GPU-capable development setup is optional:

```powershell
uv sync --extra gpu --group dev
uv run --extra gpu --group dev python scripts/check_gpu.py
```

These GPU commands were checked against the current CLI/dependency contract;
A008 does not certify a new GPU execution. CPU reference is the normal supported
path. CUDA requires the GPU extra and a compatible CUDA/GPU environment;
unavailable CUDA is explicitly rejected. UI startup does not require CuPy.
A007A certifies configuration dispatch semantics, not broad CPU/CUDA numerical parity.

For a built wheel, first build in the checkout:

```powershell
uv build
```

Copy `dist/malecns_sim-0.3.0-py3-none-any.whl` to an independent directory.
From that directory, the following PowerShell sequence was tested with a clean
CPU-only environment (the wheel includes its HTML/CSS/JS assets):

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe malecns_sim-0.3.0-py3-none-any.whl
.venv/Scripts/python.exe -c "import malecns_sim; print(malecns_sim.__file__)"
.venv/Scripts/malecns-workbench.exe
```

The import must point inside this environment's site-packages. No editable
install or repository-relative static files are required. Installation downloads
Python dependencies if not cached; MaleCNS data is a separate prerequisite.
See [the reproducibility record](REPRODUCIBILITY.md) for the wheel certification.

Normal development startup is **`uv run malecns-workbench`**. It binds only to
127.0.0.1 and chooses an available ephemeral port by default. Open the complete
newly printed URL. Each process has its own server instance ID and local session
token; multiple instances are independent. Same-tab refresh is supported.
Stop with Ctrl+C for clean shutdown. An explicit fixed port is available:

```powershell
uv run malecns-workbench --port 48765
```

Use a fixed port only when needed and available.

## Local session and data

The printed URL carries a per-process local session token. Protected API calls
require it; Host/Origin checks remain active. Avoid copying the token into logs,
documentation or screenshots unnecessarily. A new server process means a new
session/token. The browser stores the token in session storage for same-tab
refresh; reopen the complete printed URL for a new tab or wrong session.

The registered dataset is `male-cns-v1`, displayed as **MaleCNS v1.0 curated
graph**. DatasetCatalog uses `MALECNS_DATA_ROOT` when set, otherwise `data`
under the process working directory. That root must contain `raw/male-cns/v1.0/`
with these exact provenance-matching local resources:

- `body-annotations-male-cns-v1.0-minconf-0.5.feather`
- `body-neurotransmitters-male-cns-v1.0.feather`
- `connectome-weights-male-cns-v1.0-minconf-0.5.feather`

These files are **not bundled in the wheel**. Use already acquired, registered
data; this guide supplies no download procedure. File presence permits catalog
availability; loading checks provenance/identity rather than treating arbitrary
same-named files as valid. If absent, the UI reports `DATASET_UNAVAILABLE` and
cannot define a real experiment. Installed UI/API startup remains possible.

Source reference counts describe the curated source graph, not necessarily the
signed prepared simulation graph. Use the backend result provenance fields
`prepared_neuron_count` and `prepared_edge_count` for actual prepared counts;
do not substitute source totals or displayed subgraph counts.
The historical full curated source reference is 166,700 neuron IDs and
25,582,938 edges; these are not a claim about a newly prepared execution.

## Operate a real experiment

1. Open the printed URL and check dataset availability in **Experiment setup**.
2. Choose **Side** (`LEFT sugar → MN9_R` or `RIGHT sugar → MN9_L`),
   **Frequency** (10/25/50/100/150/200 Hz), **Mode** (`Baseline` or
   `Outgoing silence: corresponding MN9`), **Backend** (`CPU reference` or
   available `CUDA`), and **Seed**. Production controls fix duration at 100 ms,
   dt at 0.1 ms and one trial; they do not offer arbitrary durations or traces.
3. Click **Validate** and inspect **Executed configuration preview**. Changing
   a selection requires validation again. Click **Run** only when you intend
   actual scientific execution.
4. Observe **Execution and result**, the status banner and **Execution timeline**.
   Inspect completed identity/output in **Run inspector**; use **Recent runs**
   to select retained runs. Completion follows result finalization/export.
5. Inspect the graph, recorded playback and controlled comparison below.
6. Optionally start an explicitly requested robustness sweep from a validated
   baseline; this can execute up to sixteen scientific child runs.
7. Download backend exports before stopping/releasing retained evidence.
   Run lists and robustness retention belong to the current server session;
   this UI does not offer importing an exported run into a later session.

A008 checked these controls against production HTML/JS and certified contracts;
it did not press Run or execute real MaleCNS simulations.

## Real execution phases

`VALIDATING` checks the experiment; `LOADING_DATA` loads registered inputs;
`PREPARING_NETWORK` constructs the prepared network; `RUNNING` executes the
simulation; `FINALIZING` builds and exports evidence. Terminal states are
`COMPLETED`, `FAILED`, and `CANCELLED`. These are actual phases, not simulated
progress. Elapsed time is wall-clock operational metadata, not simulation time.
There is no fake progress percentage. PREPARING_NETWORK can take a long time
on the large graph. Cancellation at cooperative boundaries is not necessarily
instantaneous during an opaque simulation.

## Graph and subgraph

**Schematic connectivity view — not anatomical position.** Coordinates are UI
layout coordinates; the renderer is not anatomical geometry or a 3D CNS
reconstruction. **Display filter** offers **Stimulus neighborhood**, **Target
neighborhood**, and **Combined context** with **Node cap** 80 or 160 and a
1,200-edge cap. Read truncation information. A bounded display context is not
automatically a biological pathway or the complete graph.

Use **Fit**, **Zoom In**, **Zoom Out**, drag/pan, **Find displayed neuron** and
the node list to inspect **Selected neuron**. Display filters and caps alter
the view, not backend scientific results.

## Recorded activity playback

**Recorded activity playback** uses sparse recorded output spike events.
Legal timestep k maps to post-update `k * dt_ms`; the legal grid includes the
final recorded update, not fabricated intermediate states. Use **Simulation
time**, **Play**, **Pause**, **Restart**, **Step −**, **Step +**, and **Speed**.
The raster and inspector are bound to the selected recorded result.

Selected voltage traces exist only when explicitly requested in the execution
contract; the normal production setup requests no selected voltage traces.
Unavailable trace is not zero trace. Recorded zero means an observed neuron
has no recorded spikes; unrecorded means the observation is unavailable.
Population bins are derived visualization for displayed neurons; changing
**Derived visualization bin width** does not change recorded events or digests.
The orange viewport ring shows recorded spikes in the active display time
window. There is no edge-propagation animation. **Playback is not reconstructed
biological signal propagation.** Requested stimulus frequency is not proof
of recorded realized input events; unavailable schedule observations stay unavailable.

## Baseline/intervention comparison

In **Compare · simulation outputs**, select a **Baseline completed run** and
use **Run paired intervention**, then select its **Intervention completed run**
and click **Compare**. This executes an outgoing-silence intervention when
requested: outgoing scheduling is suppressed while incoming state/input/spike
recording and structural edges remain present.

Arbitrary runs cannot simply be compared. Backend A006 pairing requires
controlled equality of dataset identity, stimulus, target, seed, actual realized
schedule, duration/dt, model/sign configuration and backend under its contract,
with only the permitted intervention difference. Matching requested frequency
or seed alone is insufficient. Preparation variants must match within a pair.
Use shared playback time, aligned rasters and schematic viewports to inspect
retained evidence; the backend supplies numeric deltas.

`ZERO_BASELINE` means the relative delta is unavailable/null because its
denominator is zero. Do not interpret it as 0%, infinity or 100%.
An observed simulation delta does not automatically establish biological causality.

## Robustness variant evidence

Use **Refresh sweeps** and **Retained sweep** for existing parent evidence.
**Create robustness sweep from validated baseline** exposes **Start Robustness
Sweep**, with explicit confirmation before real execution. Entering the panel
does not start a sweep. The parent owns at most 16 baseline/intervention
children, executes serially and can reuse only exact verified evidence.

The R0–V7 preset is `application-historical-variation-family-v1`. Each variant
changes only the listed reference setting; other reference settings remain:

| Variant | Exact definition |
|---|---|
| R0 | Reference: membrane tau 20 ms, synapse tau 5 ms, delay 1.8 ms, weight 0.275 mV, threshold −45 mV, Shiu2024SignPolicy |
| V1 | Membrane tau 10 ms |
| V2 | Membrane tau 30 ms |
| V3 | Synapse tau 2.5 ms |
| V4 | Synaptic delay 1.0 ms |
| V5 | Weight 0.200 mV; coupled direct input 50 mV under the ×250 rule |
| V6 | Threshold −44 mV |
| V7 | ConservativeSignPolicy |

Reference direct input is 68.75 mV (0.275 ×250); rest/reset are −52 mV,
refractory period 2.2 ms. V5 changes input amplitude as well as synaptic weight.
Schedule evidence compares actual neuron IDs/times, multiplicity, refractory-free
IDs, seed, duration and dt across variants; cross-variant event-time identity
excludes amplitude deliberately for V5. Full amplitude-inclusive schedules
are retained and must match within every A006 pair.

Select a matrix row to inspect **Variant evidence inspector**, signed backend
target spike-count deltas and retained comparison/playback/graph evidence.
Robustness graph snapshots use combined context/160 nodes and the edge cap.
Failures and unavailable evidence remain visible. **Cancel sweep** preserves
completed evidence at supported boundaries. **Release retained evidence**
releases the parent; export first if needed. **Export robustness result**
downloads the backend envelope.

**NO_AGGREGATE_RULE is the default and only supported aggregate policy.**
The application does not automatically report ROBUST or NOT_ROBUST for a new
sweep. Historical Task017 was a separate preregistered scientific robustness
experiment whose final result is NOT_ROBUST. Matching variant names does not
make a reusable application R0–V7 sweep identical to Task017's matrix, design,
denominators or frozen scoring. Task017Q remains Q1 — KEEP_DEFERRED.

## Synthetic review fixture

`scripts/review_application_a007c.py` is a developer/reviewer visualization
fixture: **SYNTHETIC REVIEW DATA**, not MaleCNS scientific results. It supplies
synthetic complete/reused and partial/failure evidence for UI inspection.
It must not be cited as biological or model result evidence. It is separate
from the normal real-experiment workflow and is not needed for installed UI startup.

## Export and auditability

**Download backend result** exports ExperimentResult; **Download backend
comparison** exports paired comparison evidence; **Export robustness result**
exports the parent spec, per-variant evidence and integrity envelope. Preserve
identities and provenance with each export. An authoritative contract digest
identifies canonical scientific content; a file SHA-256 identifies exact bytes.
They serve different purposes and need not be equal. Browser layout positions,
bins, highlighted windows and display filters are visualization data.
Authoritative scientific values come from backend result contracts; browser
visualization does not redefine results.

## Troubleshooting

| Symptom | Action or explanation |
|---|---|
| Dataset unavailable | Check the three registered Feather resources and data root; the wheel supplies no dataset. |
| CUDA unavailable | Use CPU reference or provision the optional GPU environment; startup needs no CuPy. |
| Long PREPARING_NETWORK | Inspect real phase/elapsed metadata and wait for preparation; no percentage is available. |
| Local session mismatch | Restart malecns-workbench and open the newly printed complete URL. |
| Explicit fixed-port collision | Stop the conflicting instance or restart with the normal automatic-port command. |
| Refresh/new tab uses wrong URL | Reopen the current server's printed URL; same-tab session storage belongs to that session. |
| Protected API/session error | Use the current token URL on 127.0.0.1; do not bypass Host/Origin/session checks. |
| ZERO_BASELINE | Relative delta is unavailable/null, not a percentage. |
| Comparison pair rejected | Use Run paired intervention and inspect dataset/configuration/realized-schedule identity; arbitrary pairs are invalid. |
| Robustness child failed/partial sweep | Inspect the row failure and retained evidence; missing values are unavailable, not zero. Export completed evidence; no aggregate verdict is inferred. |

## Local validation commands

These checkout commands were executed for A008; they do not run the opt-in
real-data full-graph experiment. GPU setup above was contract-checked only.

```powershell
uv run pytest
uv run python -m compileall src scripts tests
uv run python scripts/check_tracked_integrity.py
git diff --check
```

Validation is local; no active GitHub Actions workflow is used.
