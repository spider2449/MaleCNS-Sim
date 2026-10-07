# A022 — CPU resumable runtime public API contract

Date: 2026-10-07. Authorization: user explicitly authorized **授權 A022**, design-only/API-contract-only inspection, this report, commit and push. **A022-A — CPU RESUMABLE PUBLIC API CONTRACT READY; RELEASE API IMPLEMENTATION MAY BEGIN**. This document freezes an intended contract, not an implemented or tested new API.

## Starting gates and review method

Root derived using `git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`; origin is spider2449/MaleCNS-Sim. Local HEAD = origin/master = live GitHub master = **d7cb48f3cb22248a211aaf3bd32857d405a9ebb1**. Worktree clean, staging empty, stash empty, package version **0.3.0**, tracked workflows **0**. All required gates passed before mutation.

Plan: inspect named source/export/test/documentation text; compare proven semantics with the proposed boundary; decide ownership, time, input/output, errors and compatibility; write this file only; run `git diff --check`; commit/push and verify final identity and cleanliness. No Python invocation, imports, test discovery, executable firewall bootstrap, registered catalog/payload access or native-read telemetry. Zero reads below are task activity counters, not a new firewall certification. Memory supplied navigation; repository text is authority.

Preserve [A021](2026-10-07-application-a021-release-scope-readiness.md): **A021-B**, release bundle **R1 CPU resumable runtime + R4 reproducibility/performance evidence**, CPU previously **API-B**, GPU **GREL-B**, closed-loop **CREL-B**, version previously **VERSION-C**. Preserve [A020](2026-10-07-application-a020-roadmap-decision.md) and its scientific-roadmap gates. No scientific/model behavior is redesigned.

Evidence reviewed: [A011](2026-10-02-application-a011-closed-loop-arena.md), A021's A012–A018 preparation/identity adjudication, [A019L](2026-10-06-application-a019l-full-real-cpu-rebenchmark.md), [A019T](2026-10-06-application-a019t-cpu-gpu-resumable-equivalence.md), [A019V](2026-10-06-application-a019v-synthetic-cpu-gpu-performance.md), and [A019Y](2026-10-07-application-a019y-trace-observer-disposition.md). CPU exact whole/chunk continuity is synthetic certification. Bounded full-real D/L replay is two independent fresh 12-call/240-ms states, 24 aggregate calls, not a 480-ms trajectory; it does not prove full-real whole/chunk equivalence or concurrent multi-state capacity. GPU retains bounded EQ-B certification; performance work remains paused.

## Current implementation inventory

P0 means existing explicitly exported/documented surface to preserve, not every accessible attribute becoming stable. P1 is a supported candidate through a wrapper; P2 experimental; P3 implementation detail; P4 must stay outside the new contract because of compatibility debt. Direct module importability alone is not public support.

| Symbol / module | Visibility and callers | Mutation / ownership / tests | Class and naming decision |
| --- | --- | --- | --- |
| `EffectiveSignedProjection`, `LIFParameters`, reference constants / `dynamics.lif` | Root/dynamics exports; one-shot engines, runtime, preparation, Task005+ tests | Frozen dataclasses; projection arrays marked read-only by factory, but direct construction permits bad structures/aliases; tests construct fixtures and inspect CSR | P0 legacy model surface; accepted as factory input, no new promise for its raw layout |
| `PreparedNetwork` / `analysis.task008` | Direct module, architecture; analysis trials, `ProductionEngine.prepare`, benchmarks | Frozen envelope holds projection, signed graph, timings, cache metadata and optional CUDA graph; shallow freeze is not deep ownership | P4; INTERNAL envelope, name must not become new supported handle |
| `prepare_network` / `analysis.task008` | Direct module/documented architecture route, application service and historical scripts | Reads pinned files, curates/signs/projects; optional cache writes and CUDA upload; returns envelope | P3 for new runtime boundary; preserve legacy route without stabilizing its whole signature |
| `PreparedRuntime` / `dynamics.lif` | Direct module, not root/dynamics export; Arena, A011/J/T/V and benchmark callers | Frozen fields retain supplied projection; constructor validation deferred; identity is projection/parameter/dt tuple | P1; suitable name for opaque public facade in a new module |
| `SimulationState` / `dynamics.lif` | Direct module; runtime/loop and continuity tests | Mutable dataclass, writable v/g/refractory/pending/count arrays and timestep; public constructor allows arbitrary buffers | P1 opaque handle name; underlying fields P4 |
| `initial_state()` / `dynamics.lif.PreparedRuntime` | Runtime method; Arena/tests/benchmarks | Fresh independent arrays at rest, g/pending zero, deadlines -1, time zero | P1; preserve defaults and independent allocation |
| `advance()` / same | Runtime method; Arena/tests/benchmarks | Mutates supplied state via `simulate_lif`; accepts explicit chunk-relative stimulus; returns separately allocated `SimulationResult` | P1 narrow wrapper; exclude timing, silencing and trace arguments |
| `simulate_lif`, `simulate_lif_active`, `linear_state_update` / `dynamics.lif` | Existing dynamics exports; root exports first/third; application one-shot service, analyses/tests | Existing validated integrator and scratch implementation; `_state`, `_timing`, `_scratch` are internal seams | P0 preserve existing public behavior; private seams P4 |
| `SpikeSchedule`, `ExplicitStimulus`, `PoissonStimulus` / `dynamics.stimulus` | Root/dynamics exports; engines, adapters/tests | Immutable normalized tuples; sorted times/schedules, duplicate impulses retained; some ID inputs currently coerced through int | P0 reuse explicit types without tightening legacy constructors; Poisson generation outside advance |
| `schedule_events`, `_grid_steps`, `validate_refractory_ids` / `dynamics.stimulus` | Direct module helpers; CPU/GPU loops/tests | Packs local steps into NumPy positions/weights; rejects unknown IDs/endpoint/grid errors before loop | P3 packing, P4 array/dtype layout; no public packed type |
| `SimulationResult`, `SparseTrace` / `dynamics.lif` | SimulationResult root/dynamics, SparseTrace dynamics exports; service/analysis/tests | Frozen records with owned output arrays, most marked read-only; trace IDs are separately copied; diagnostics/fingerprints and count arrays included | P0 legacy outputs retained; P3 as new facade implementation source; do not broaden stable runtime output to all fields |
| `AdvanceTiming`, stages/substages and timer hooks / `dynamics.lif` | Direct module, profiler/benchmark/test callers | Mutable timing accumulators; scratch and stage boundaries track implementation | P4 INTERNAL, not supported runtime arguments |
| `GPUPreparedRuntime`, `GPUSimulationState` / `dynamics.cuda` | Direct module; A019S/T/V tests/scripts | Strict owner token/backing/device; lock, close, failure poisoning, retained device buffers | P2 EXPERIMENTAL-PUBLIC via explicitly experimental facade; storage/kernel/CSR/pool helpers P4 |
| `ArenaSession`, `ArenaState`, encode/decode / `application.arena` | Direct module, server and A011 tests | Mutable synthetic session/world and fixed engineered adapters | P2 example surface; adapter Python symbols P3 INTERNAL |

`tests/test_application_a011.py` compares membrane, conductance, refractory and pending arrays and directly edits a sibling state's v array to prove isolation. `test_application_a019j.py` inspects scratch aliases and ordered NumPy operations. S/T tests inspect GPU backing/lifetime/state arrays and tolerances. These are engineering regression oracles, not a reason to support those fields publicly. Application `ProductionEngine.simulate` remains one-shot; Arena uses the resumable seam. No new general workbench scenario UI is implied.

## Final public object model and construction authority

Canonical new supported import path: **`malecns_sim.runtime`**. Add only this module's explicit exports; no new root-level aliases are required. Its facade types are distinct from the legacy `dynamics.lif` dataclasses, whose imports/signatures remain unchanged. Avoid renaming the proven loop or changing legacy fingerprint ownership behavior.

Intended signatures (design pseudocode, not executable implementation):

```python
from malecns_sim.runtime import prepare_runtime
from malecns_sim import ExplicitStimulus, SpikeSchedule

runtime = prepare_runtime(projection, parameters=parameters, dt_ms=0.1)
state = runtime.initial_state()
result = runtime.advance(state, duration_ms=20.0, stimulus=ExplicitStimulus())
```

`prepare_runtime(projection: EffectiveSignedProjection, *, parameters: LIFParameters = REFERENCE_LIF_PARAMETERS, dt_ms: float = 0.1) -> PreparedRuntime` is CPU-only. No backend selector, file paths, cache option, stochastic initialization, intervention, profiler or trace option. It validates/snapshots normalized execution structures once, then wraps the existing dense CPU runtime. Preparation here means binding an already prepared model projection, not loading raw MaleCNS sources. A signed graph can use the existing `EffectiveSignedProjection.from_signed_connectome` route; the legacy file route can supply `prepared.projection` as a migration bridge. Dataset curation/source validation is not relocated into this factory.

Only the factory constructs supported `PreparedRuntime`; only `runtime.initial_state()` constructs supported `SimulationState`; only `advance()` produces supported `AdvanceResult`. Public direct constructors for these handles/result are unsupported and must reject attempts rather than accept partial fields. Users may directly instantiate existing stimulus/schedule/parameter types. New handles use object identity equality/hash only; no structural equality, pickle/serialization, deepcopy/copy/clone, persistence, cross-process transfer or subclassing contract. AdvanceResult has immutable value equality/hash over its specified fields; no persistence schema is promised. Legacy input dataclass equality/hash/persistence is not broadened by this design.

## PreparedNetwork disposition

**INTERNAL**, explicitly not promoted. Its graph-name/preparation fingerprint is a different layer from the effective projection fingerprint; timings, raw signed graph, cache and optional device graph create unnecessary lock-in. The new factory accepts the already exported model projection and returns a narrower runtime. No new prepared-network type/factory or serialized prepared-runtime format is required.

The runtime retains an owned normalized snapshot, not raw source tables/files or the PreparedNetwork envelope. Validate sorted unique non-boolean integer IDs, consistent finite topology/weights and CSR/index bounds, parameter weight agreement, positive finite dt and grid-representable delay/refractory constants before returning. Copy execution arrays so later caller writes/replacements or writable aliases cannot affect a runtime. Do not re-curate, re-sign, change numerical order, optimize, or replace graph/model identities. A projection may prepare multiple independent runtimes; equal graph/model identity does not authorize exchanging states.

## PreparedRuntime ownership, lifetime and resources

**STABLE-PUBLIC** opaque CPU type. Public read-only properties: `backend: str` fixed to `"cpu"`, `dt_ms: float`, `neuron_ids: tuple[int, ...]` in ascending order, `projection_fingerprint: str`, `parameter_fingerprint: str`. Fingerprints expose existing effective-model identity, not source verification, state compatibility, cache keys or a trajectory fingerprint. Retain their existing algorithms; no new combined fingerprint schema.

Shared immutable execution data belongs to the runtime. Every state strongly retains its owner/backing; states remain valid after the caller drops the runtime variable. Users may regain no owner property through the stable state API: to advance, retain the runtime reference. Runtime can outlive any number of discarded states and remains reusable; discarding one state cannot alter siblings or the runtime. Each runtime has a private owner token; equal fingerprints across different runtime objects are insufficient for state admission.

CPU uses ordinary reference/GC cleanup, **no close(), release(), or context manager**. Dropping all relevant references frees resources subject to Python GC, without a prompt-release or hard-memory-cap promise. There is no CPU use-after-close condition because no supported close exists. Explicit close is not imposed merely for GPU alignment. Failed states are unusable as specified below and are discarded; runtime can create replacements. Factory/initial allocation failure yields no usable partial handle.

Process-local, externally serialized operations only: concurrent/reentrant calls on the same runtime, including different states, are unsupported. No thread-safe execution, multiprocessing transfer, interruption/cancellation, deadline enforcement or async API is promised. Sequential interleaving of independent states is supported. Supervision belongs outside this in-process API.

## SimulationState and initial_state contract

**STABLE-PUBLIC** opaque handle for one independent mutable trajectory. No writable public fields/buffer views. Selected read-only properties are `timestep: int` and `time_ms: float`; timestep is canonical and time_ms is derived as timestep * owner.dt_ms. All membrane, synaptic/conductance, refractory, pending/delayed and event-count arrays remain private.

`PreparedRuntime.initial_state() -> SimulationState` has no parameters. Every successful call creates a fresh handle and disjoint mutable dynamics buffers, time/timestep zero, v at model resting voltage, g/pending/counts zero and refractory deadlines at the existing default. It creates no seed, RNG stream or customization authority. Custom initial conditions, reset-in-place, clone/copy, restoration and checkpoints are **DEFERRED**. To reset a trajectory, request a fresh state.

Sibling states share only immutable runtime data; advancing A does not advance/change B. Independent deterministic replay follows for equal explicit inputs and configuration in the supported numerical environment. Preserve existing exact synthetic chunk continuity, including pending delays crossing boundaries; no cross-platform bitwise guarantee is added. A state can be admitted only to the exact owning public runtime, not a matching CPU runtime or a GPU runtime.

Inspection is **STATEVIEW-C**: timestep/time_ms only. No public numerical snapshot/trace API in this release; broader snapshot support is DEFERRED. Failed-state time properties raise RuntimeError because partially mutated buffers and canonical time may disagree. Prior independent results remain valid.

## advance mutation and failure contract — ADV-A

`PreparedRuntime.advance(state: SimulationState, *, duration_ms: float, stimulus: ExplicitStimulus = ExplicitStimulus()) -> AdvanceResult` mutates the supplied state in place and returns chunk output, never a new state. Preserve the existing input/direct delivery, integration, threshold/reset, refractory and delayed enqueue ordering; do not add a second simulator.

Complete supported input/owner/time/grid/identifier validation and event packing before any trajectory mutation. Invalid input leaves state and time unchanged. Successful call advances exactly the validated integer number of steps and returns output for that interval. No hard 20-ms restriction; advance-many calls form one continuous trajectory.

Current loop mutates buffers during execution, increments timestep after the loop, then allocates/assembles output. Thus execution or result-allocation failure cannot promise rollback; it can occur after partial mutation or after full time progression without a returned result. Public facade must mark that state failed on any exceptional exit after handing control to the mutating loop (including MemoryError or interruption), re-raise, and reject subsequent advances. Conservative poisoning is allowed even if an internal failure happened before the first write. It must not mark sibling states or the immutable CPU runtime failed. No transactional recovery/retry on the failed state. Preflight MemoryError before loop entry leaves the trajectory reusable. Result conversion failure also poisons the state. This is an explicit bounded wrapper delta, not existing CPU poisoning certification.

## Duration and canonical time

Accept finite Python int/float duration and dt values, excluding bool; values are milliseconds. Duration strictly positive; zero/negative/nonfinite values raise ValueError, unsupported types TypeError. Public facade validates types rather than silently accepting strings. Grid steps use the existing nearest-integer conversion with `rtol=0`, absolute tolerance **1e-10 ms** for reconstruction `steps * dt_ms`; no floor/truncation. Require at least one step, so positive values rounding to zero are rejected. Non-grid values raise ValueError. Validate step/end-time bounds against signed int64 used by output timestamps before mutation; overflow raises ValueError. dt is fixed for runtime lifetime.

Canonical time is nonnegative integer `timestep`; displayed milliseconds are derived, never accumulated floats. If start timestep is S and duration gives N steps, success ends at S+N. Input local grid steps are **0..N-1**, time interval **[0, N*dt)**. Output spike timesteps are absolute **S+1..S+N**, interval **(S*dt, (S+N)*dt]**. An output at chunk end occurs only in that chunk. A direct input at chunk endpoint is excluded and must be supplied at local zero in the next chunk. Pending synaptic input due at the new boundary is retained for the next advance. Derived duration/result time is canonical N*dt, not the possibly tolerance-offset spelling of user input.

## Public events versus internal packing

Reuse **ExplicitStimulus** containing immutable **SpikeSchedule** values: `SpikeSchedule(neuron_id, spike_times_ms)` and `ExplicitStimulus(schedules=(), weight_mV=None, refractory_free_neuron_ids=())`. Existing constructor normalization stays unchanged. Public runtime accepts these constructed objects, not NumPy matrices, packed arrays, dict records, generators of records or PoissonStimulus. Types/dtypes/shapes of raw arrays therefore have no supported event meaning. The facade checks the normalized contents/types/IDs/times before packing; it does not recover information already coerced by a legacy constructor (for example int conversion of an ID).

Times are chunk-relative finite nonnegative milliseconds on the duration grid. Unknown schedule or refractory-free IDs raise KeyError, even for an empty schedule; timestamps at/beyond endpoint raise ValueError, no silent filtering. Empty stimulus is valid. Constructor sorting and all duplicate schedules/times are retained; each occurrence contributes one configured direct voltage impulse. Internal aggregation is by neuron and timestep, independent of schedule presentation order, with existing summation semantics. Output firing still follows the model's threshold/refractory rules; multiple inputs do not promise multiple output spikes.

`weight_mV=None` uses the model synaptic-weight constant; explicit finite weight including zero/negative retains existing model semantics. Refractory-free IDs retain existing bypass behavior and are an explicit model-input option, not a biological encoder claim. The supported runtime adds no per-call silencing or adapter authority. Seeded Poisson input may be generated once over a complete horizon using the legacy helper and sliced externally into explicit chunks; advance does not generate/reseed it.

`schedule_events` dictionaries, position arrays, float weight arrays, lookup/grid helpers and GPU event packs are **INTERNAL**. Packing happens before mutation and is not persistable/public input. No packed dtype/shape/layout stability promise.

## AdvanceResult contract

New **STABLE-PUBLIC** frozen `AdvanceResult`, produced only by advance. Exact public fields:

| Field | Type and meaning |
| --- | --- |
| `start_timestep`, `end_timestep` | Python int, S and S+N |
| `dt_ms`, `duration_ms` | Python float, fixed dt and canonical N*dt |
| `spike_neuron_ids` | tuple[int, ...], one neuron ID per emitted spike |
| `spike_timesteps` | tuple[int, ...], matching absolute output steps |

Read-only derived properties: `start_time_ms`, `end_time_ms`, `spike_times_ms: tuple[float, ...]`, `emitted_spike_count: int`. Events sorted by absolute timestep then neuron ID using the existing canonicalization. Empty output has empty tuples. No dense count array, decoder values, pending counters, diagnostic timings, trace histories, stimulus/simulation digest or new replay identity in this minimal result. Counts can be derived from emitted records; runtime neuron_ids identifies silent neurons.

Tuples contain detached Python scalars: no state/scratch/device/legacy result-array alias, no writable views and no dtype contract. Result owns independent immutable values and survives later advance, state failure, GC and sibling execution. Materialization/copying is explicit future work with output-memory overhead, not a free performance claim. Legacy SimulationResult stays unchanged for existing one-shot/internal callers. Do not repurpose its chunk fingerprint as a complete trajectory identity.

## Errors and cleanup boundary

Stable categories use built-in exceptions; no new hierarchy or exact message guarantee is needed. A category is part of this API only for the defined condition, not every internal exception. Validate factory, initial_state and advance before returning usable partially initialized objects or mutating trajectories.

| Condition | Current static behavior | Intended public category |
| --- | --- | --- |
| Wrong input type / unsupported stimulus / wrong state type | `_finite`/stimulus TypeError; arbitrary state may AttributeError | TypeError, ERR-STABLE; facade fixes wrong-state admission |
| Invalid duration/dt/grid/nonfinite/overflow | ValueError; CPU lacks complete overflow admission | ValueError, ERR-STABLE, preflight |
| Unknown normalized neuron IDs | KeyError in schedule/ID helper | KeyError, ERR-STABLE, preflight |
| State/runtime owner mismatch | CPU ValueError on fingerprint tuple; GPU strict owner | ValueError, ERR-STABLE; public facade uses exact owner |
| Invalid projection/parameter configuration | ValueError or downstream structural errors | TypeError for wrong kind, ValueError for invalid structures, ERR-CATEGORY-STABLE at factory |
| Failed state | No CPU status; GPU ValueError/RuntimeError depending path | RuntimeError, ERR-STABLE for subsequent CPU advance/time inspection |
| CPU released/closed handle | No such lifecycle | Not applicable; no invented close error |
| Allocation/resource exhaustion | MemoryError or native/process failure | MemoryError when Python allocation reports it, ERR-CATEGORY-STABLE; no guarantee for OS kill/native crash |
| Backend execution or output assembly failure | Internal exceptions; state may have changed | Propagate original exception, ERR-INTERNAL type/message; poison state; subsequent use RuntimeError |
| Timeout/resource supervisor stop | Application/supervisor layer | Outside runtime; preserve existing ApplicationError/ErrorCode contracts separately |
| GPU device/busy/closed/failed | Existing ValueError/RuntimeError and private backing | Experimental category mapping only; no CPU lifecycle expansion |

Where several inputs are invalid, validation precedence/message text is unspecified. No swallowing KeyboardInterrupt/SystemExit or converting unrelated errors into misleading input errors. Cleanup does not guarantee recovery from process termination or native failure. CPU runtime remains reusable after an individual state fails, subject to host resource availability.

## Backend-neutral semantics and release surface table

Semantic boundary is factory-created owner, fresh independent state, explicit local input, canonical integer time, ADV-A continuation, detached canonical result and preflight error categories. CPU is the supported implementation. Future GPU facade can implement the same semantic operations/fields while retaining separate device construction and close; backend labels need not imply substitutability of state objects, numeric bitwise equality, memory cost or performance.

Intended optional facade: **`malecns_sim.experimental.gpu.prepare_gpu_runtime(projection, *, parameters=REFERENCE_LIF_PARAMETERS, dt_ms=0.1)`**, returning existing-name GPUPreparedRuntime/GPUSimulationState facades with equivalent minimal advance/result input/output semantics. Preserve current-device construction/lazy optional dependency, owner/device validation and explicit idempotent close with use-after-close errors. No new stable GPU factory options, device migration or CPU backend selector. Retain existing device implementation and EQ-B certified backend; facade bridging is additive. Context-manager support is DEFERRED rather than imposed. Exact new experimental factory and facade behavior must be verified later; this design makes no fresh GPU certification claim.

| Surface | Final disposition |
| --- | --- |
| `runtime.prepare_runtime`, `runtime.PreparedRuntime`, `runtime.SimulationState`, `runtime.AdvanceResult` | STABLE-PUBLIC, new narrow facade |
| `PreparedRuntime.initial_state`, `PreparedRuntime.advance` and specified read-only properties | STABLE-PUBLIC |
| `ExplicitStimulus`, `SpikeSchedule`, `LIFParameters`, reference parameters and existing projection input | STABLE-PUBLIC within specified supported use; retain legacy exports |
| Existing one-shot root/dynamics exports and documented application contracts | STABLE-PUBLIC existing behavior preserved; not enlarged to runtime diagnostics |
| `experimental.gpu.prepare_gpu_runtime`, `GPUPreparedRuntime`, `GPUSimulationState` facades, close | EXPERIMENTAL-PUBLIC; lazy optional GPU path |
| PreparedNetwork, legacy preparation envelope/timings/cache/CUDA graph | INTERNAL for new runtime API; existing import path retained |
| Legacy lif runtime/state dataclasses, raw buffers, owner tokens, packed events | INTERNAL; raw state/packing fields must remain private |
| Instrumentation, scratch, kernels, device backing, CSR/event packing, pool helpers | INTERNAL |
| CPU backend selector, custom initial state, clone/copy, persistence, snapshots/traces, GPU context managers | DEFERRED; no promised implementation |
| Fixed engineered synthetic Arena example | EXPERIMENTAL-PUBLIC example behavior/documentation only, CREL-B |
| ArenaSession/encode/decode and arbitrary closed-loop adapters | INTERNAL; no supported general adapter API |

GPU stays **GREL-B**, equivalent only under bounded **EQ-B** (exact discrete outputs and bounded floating comparisons in certified fixtures), not universal interchangeability. A019V CPU won all 80 bounded paired positions; no full-real GPU benchmark/speedup or realtime promise. Closed-loop remains **CREL-B engineered synthetic example-only**. No biological brain reconstruction, digital twin, behavior prediction, validated biological sensory encoder/motor decoder, biological realtime or mechanism proof.

## 0.4.x compatibility and v0.3.0 migration

STABLE-PUBLIC new names/import path, keyword signatures/defaults, event acceptance within the specified domain, result fields/types/order/ownership, lifecycle and semantic behavior are preserved throughout **0.4.x**. Patch releases may fix bugs to meet this contract; they cannot silently change the contract or scientific equations. Optional additive fields/methods may be introduced with defaults and release notes without removing/changing existing meaning; no extra required arguments. Do not promise numerical byte identity across platforms/dependency releases beyond the established supported environment/evidence.

Deprecations require release-note and API-doc notice, an actionable migration and a retained working path throughout 0.4.x; no removal before a later minor under a separately decided policy. No indefinite promise beyond this series. Experimental APIs may change with explicit release-note notice. INTERNAL APIs have no compatibility promise; this task nevertheless directs A023 to preserve existing internal import/signatures and scientific regression oracles to keep the delta additive. Error category guarantees do not freeze strings/validation precedence.

**COMPAT-A — additive / backward-compatible minor**. Existing root/dynamics one-shot names, event/result dataclasses, application exports, CLI commands and defaults remain valid. No current public name is deprecated, no user migration is mandatory, no production rename. Opt-in resumable users import the new runtime module, prepare once from their existing projection, create state and call advance repeatedly; use AdvanceResult instead of assuming legacy dense counts/traces/fingerprints. Existing direct lif-runtime callers may retain their old path; adopting the new opaque facade is optional and requires removing raw state-array assumptions. New strict owner admission applies only to the new facade.

## Version gate and required release documentation

**VERSION-0.4-A — recommend 0.4.0** as the candidate version once bounded implementation and later release gates pass. **This 0.4.0 is the resumable application/runtime release. It is NOT resurrection of earlier unresolved v0.4 scientific roadmap work.** Package remains 0.3.0. Recommendation is not release authorization, a version bump, tag, publication or certification of an unbuilt artifact.

Minimum later docs (do not author full tutorials in A022): prepare-once/advance-many synthetic quick-start using existing projection construction and explicit events; lifecycle prose/diagram; fresh-state independence and sequential interleaving example; ADV-A and poisoning/no rollback; duration tolerance and input/output endpoints; duplicates/weight/refractory options; detached result/count derivation; errors/GC/thread-process exclusions; migration from v0.3.0; CPU host/resource/performance disclosures linked to D/L with two fresh 240-ms trajectories; optional experimental GPU dependency/device/close/EQ-B and CPU-faster disclosure; engineered synthetic Arena and scientific nonclaims; reproducibility/evidence custody guidance without routine real execution. Explain legacy file-preparation bridge without presenting it as a newly supported dataset-loading API. Update stale scope wording without rewriting historical scientific conclusions.

## Bounded future implementation delta

One cohesive **A023** implements this contract; no runtime redesign or optimization:

1. Add `malecns_sim.runtime` factory and opaque facade types, explicit minimal module exports/docstrings. Validate/copy an already prepared projection once, bind private exact-owner token, retain owner backing in state; preserve existing lif constructors/imports/loop/identities. Add canonical read-only properties and no direct partial construction.
2. Add immutable detached AdvanceResult tuple conversion, preflight duration/event/type/ID/overflow admission, unchanged event packing/model call and conservative failed-state marking around loop/result assembly. Keep timing, arrays, silencing, traces and preparation diagnostics outside supported signatures. No legacy stimulus constructor coercion changes.
3. Add lazy `malecns_sim.experimental.gpu` facade/import boundary around retained backend with minimal aligned semantic input/output, existing owner/device/close behavior and explicit experimental documentation. No kernel/performance edits or new device model; keep old cuda import paths.
4. Add meaningful contract/compatibility tests for valid construction and rejected malformed topology, input-before-mutation, exact-owner rejection even for equal identities, sibling isolation and delayed/refractory chunk continuity, detached tuple result/order/endpoints, overflow, loop/output failure poisoning, factory alias isolation, unchanged v0.3 imports/one-shot behavior, and GPU boundary/lazy optionality/close using synthetic or fake-device scope. Preserve independent numerical oracles; do not merely mirror wrapper implementation.
5. Add the minimal API/migration/support documentation above and connect existing R4 evidence. No metadata/dependency/version edits, dataset access, benchmarks/profiling, full-real reruns or release execution.

A023 tests/executable validation require separate explicit A023 authorization and a guard-first zero-real-source validation plan; synthetic simulation tests are not authorized by A022. GPU facade alignment must not relabel legacy device certification as a new passing artifact. Defer installed-wheel/build/publication gates to their explicitly authorized task. No deprecation shim is needed because legacy names remain untouched.

## Release API acceptance gate and terminal decision

| Required gate | Decision |
| --- | --- |
| Stable object model | PASS: factory-only opaque runtime/state and minimal result |
| Ownership/lifetime | PASS: owned immutable projection snapshot, exact owner, retained backing, fresh state |
| Advance mutation | PASS: ADV-A, preflight rejection, failed-state poisoning, no rollback |
| Duration/time | PASS: ms grid tolerance, canonical integer steps, explicit endpoints |
| Events | PASS: existing immutable ExplicitStimulus/SpikeSchedule, private packing |
| Results | PASS: detached immutable tuple records and exact fields |
| Errors | PASS: stable built-in categories, execution exceptions internal |
| Backend-neutral boundary | PASS: common semantics without transferable state/device guarantees |
| GPU boundary | PASS: optional experimental facade, retained EQ-B backend |
| Compatibility | PASS: stable 0.4.x policy, no internal/experimental stability invention |
| Migration | PASS: COMPAT-A, additive facade, no public deprecation |
| Implementation delta | PASS: one bounded A023, no model/optimization/release changes |

Overall **PASS (design completeness only)**. **A022-A — CPU RESUMABLE PUBLIC API CONTRACT READY; RELEASE API IMPLEMENTATION MAY BEGIN**. CPU intended supported core can become API-A after implementation/verification; current code remains API-B until then. 0.4.0 is now the recommended candidate, not finalized/released software.

Exact next task: **A023 — bounded implementation of the stable CPU resumable runtime public API, experimental GPU boundary, compatibility tests, and minimal public exports; no version bump or release execution.** Do not start A023 automatically. Release execution authorized: **No**. Version bump performed: **No**.

## Zero-execution counters and documentation validation

Simulations = 0; tests = 0; builds = 0; CPU/GPU timing = 0; profiler runs = 0; full-real preparations = 0; real advances = 0; registered payload reads = 0; downloads = 0; archive writes = 0; interventions = 0; Arena runs = 0. Only repository source/docs/tests read as text and Git remote ref checks were used; no raw payload, archive or retained binary profiler trace was opened.

Only this report changes. `git diff --check` and staged diff-check must pass before commit; final custody/identity is verified and reported after push outside this file to avoid a self-referential commit SHA. No tests/builds or executable checks are substituted for this design-only validation.
