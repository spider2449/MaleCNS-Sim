# Application A019R: resumable GPU runtime/state design

## Authorization and gates

Authorization: **授權 A019R**; design/feasibility only. Root derived with git rev-parse: D:/spider/working/MaleCNS-Sim. Starting local HEAD, origin/master and live GitHub master all **baf140b7ed8cc43a2b8544d48455d6ba5658acdc**. Worktree/staging/stash empty; version 0.3.0; tracked workflows 0.

**F1 — DESIGN READY. A019R-A — RESUMABLE GPU CONTRACT DESIGN READY; IMPLEMENTATION MAY BEGIN.** Bounded state ownership/time extraction and deterministic scheduling replacement are feasible; a wrapper alone is insufficient. No major backend redesign is required. This establishes a design, not implementation correctness.

Preserve [A019Q](2026-10-06-application-a019q-cpu-vs-gpu-direction-decision.md): A019Q-B; CPU O1 paused. Membrane CLOSED-SUCCESS; grid validation CLOSED-NOT-WORTHWHILE; gathers CLOSED-NO-SAFE-TRANSFORMATION; indexed writeback DEFERRED-HIGH-RISK; OPEN-HIGH-VALUE CPU target None. A019L-L1/P2 mean 1.094710500 s/20-ms call, slowdown 54.735525x. GPU has higher expected information value, not authorized performance work. Current application equivalence remains EQ-D.

## Static authority

Only explicitly named tracked source/tests/reports were inspected as text. No imports, Python, test collection, GPU queries, catalog discovery, registered data traversal or payload reads. Historical report reads do not mean their linked payloads were opened. No native-read telemetry/firewall certification claim.

- [lif.py](../../src/malecns_sim/dynamics/lif.py): EffectiveSignedProjection, LIFParameters.grid_steps, linear_state_update, SimulationState, PreparedRuntime.initial_state/advance, simulate_lif, _validate_duration, _canonicalize_spike_events, SimulationResult/SparseTrace.
- [stimulus.py](../../src/malecns_sim/dynamics/stimulus.py): ExplicitStimulus, schedule_events, _grid_steps, validate_refractory_ids.
- [task008.py](../../src/malecns_sim/analysis/task008.py): PreparedNetwork, prepare_network, run_cpu_gpu_preflight.
- [cuda.py](../../src/malecns_sim/dynamics/cuda.py): CudaGraph, upload_graph, _stimulus_inputs, _schedule_kernel/schedule_active_edges, simulate_cuda_batch/simulate_cuda, measure_memory.
- [service.py](../../src/malecns_sim/application/service.py): ProductionEngine.simulate one-shot dispatch; [arena.py](../../src/malecns_sim/application/arena.py): CPU runtime consumer, inspection only.
- [A011 tests](../../tests/test_application_a011.py): exact continuity and fresh-state isolation; [007c tests](../../tests/test_task007c.py): synthetic parity, masks/batch isolation and excluded opt-in real gate.

## Phase 1: CPU reference

N=neurons, E=effective CSR edges, D=delay steps, R=max(D+1,1), S=requested steps, K=traced neurons. Frozen dataclasses alone do not make their array contents immutable; static arrays must be treated readonly.

| Data/object | Ownership, lifetime, mutability | Shape/dtype/reset/boundary |
|---|---|---|
| PreparedNetwork | Shared frozen preparation descriptor | Host projection/signed_connectome, provenance/fingerprints, optional cuda_graph; no dynamic state |
| PreparedRuntime | Shared frozen projection/parameters/dt | Identity=(projection fingerprint, parameter fingerprint, dt); no reset in advance |
| SimulationState.timestep | State-owned mutable Python int | Initially 0; absolute grid steps; +=S after loop |
| v_mV/g_mV | Private state arrays | float64[N], rest/zero; updated in place, retained |
| refractory_until | Private state array | int64[N], -1; absolute inclusive deadline |
| pending/pending_event_counts | Private state arrays | float64/int32[R,N], zero; consumed slot cleared, future slots retained |
| schedule_events packing | Call-owned dict | Sorted local steps -> int64 positions/float64 unit entries; duplicate schedule entries preserved |
| masks/scratch | Call-owned | bool[N] masks; two float64[N] scratch arrays; never alias persistent state |
| SimulationResult | Frozen host outputs, not mutable-state views | int64 IDs/absolute steps/counts; optional float64[K,S+1] v/g traces, boundary column included |

advance accepts ExplicitStimulus only, mutates the same state and returns SimulationResult. RNG schedules are generated once externally and sliced, never reseeded per chunk. initial_state allocates all arrays independently; A/B cannot alias. Identity mismatch rejected. Canonical output order is (absolute timestep, neuron ID); counters reset per call. duration_ms is chunk duration; existing simulation fingerprint payload does not include offset; result digest uses absolute events/counts. Sparse times are offset..offset+S-1. CPU scientific semantics and error behavior are not redesigned.

## Phases 2-3: GPU map and resumable gaps

simulate_cuda delegates to simulate_cuda_batch. upload_graph creates device CSR int32 pointers/targets and float64 weights, then synchronizes null stream. Supplied CudaGraph survives calls. Every simulation invocation initializes fresh state, loops from zero, replaces local array references through cp.where and returns only results. Dynamic state cannot be resumed after return. CuPy pools may retain freed storage. measure_memory frees global pools; this must not become state cleanup.

| Current allocations | Source lifetime | Resume classification |
|---|---|---|
| CudaGraph indptr[N+1], indices[E], weights[E] | Graph/caller or local call | R1 shared runtime-static |
| v/g float64[B,N], refractory_until int64[B,N] | Call local, replaced during loop | R2 required private persistent state; owner currently absent |
| pending float64[B,R,N], pending_counts int32[B,R,N] | Call local, mutated/cleared | R2 required persistent state; retention absent |
| refractory_free/silenced bool[B,N] | Rebuilt per call | R3 call masks |
| allowed/fired/direct_allowed, updated_v/g, flat indices | Step local | R3 |
| d_trials/d_positions int64, d_values float64 | Per active step upload | R3 |
| queued uint64[B], delivered int64[B] | Call counters | R3 |
| trace_v/g float64[B,K,S+1] | Call outputs | R3 |
| sparse counts/targets/index sums int64[B,S], weight/abs sums float64[B,S] | Call outputs | R3 |
| target_positions int64[N] | Call immutable lookup | R1 candidate |
| spike flat positions/steps and concatenations int64 | Call output lists/buffers | R3 |
| ids/input_weights/prepared schedules, readback outputs | Host arrays | R4; no dynamic-state mirror |
| absolute timestep/cursor, owner/device identity, lifecycle status | Absent | R5 |

RawKernel schedule_active_edges traverses fired nonsilenced outgoing CSR rows; floating atomicAdd accumulates weights, integer atomics count edges. Direct input uses cp.add.at. Pending delivery, integration, strict threshold, reset and refractory assignment follow CPU sequence within a call. Poisson generation is host-side; no device RNG. Explicit synchronization is at upload and final null-stream boundary; asnumpy and dynamic flatnonzero/output sizing can also synchronize. No persistent allocation/free API.

| Required behavior | Current classification | Gap |
|---|---|---|
| Arbitrary start time | MISSING | Local zero origin |
| Membrane continuity | PARTIAL | Existing v not retained |
| Synaptic continuity | PARTIAL | Existing g not retained |
| Refractory continuity | PARTIAL | Local deadlines not retained |
| Pending continuity | PARTIAL | Rings not returned/retained |
| Ring phase | MISSING | Local step%R |
| New chunk events | PARTIAL | One-shot relative packing, no retained offset |
| Exact requested duration | SUPPORTED | Existing grid validation and S updates |
| Return without reset/repeated same state advance | MISSING | No state parameter/owner |
| Fresh independently retained second state | PARTIAL | Batch lanes/local initialization only |
| Release state without graph release | MISSING | No scoped lifecycle API |
| Deterministic output ordering | PARTIAL | Canonical sorting exists; atomic arithmetic order unspecified |

FIRST real architectural gap: invocation-owned mutable arrays and time/phase are unreachable after return. Graph reuse does not fix this. Dense ring storage itself is compatible and can be retained; numerical scheduling also requires a bounded replacement.

## Phases 4-5: object model and ownership

Reuse PreparedNetwork unchanged as the host scientific/provenance container. Optional cuda_graph supplies an identity/device-checked graph; do not attach mutable state to it. Add GPUPreparedRuntime and GPUSimulationState in dynamics/cuda.py. Public call matches CPU: initial_state(); advance(state, duration_ms=..., stimulus=ExplicitStimulus(...), trace_neuron_ids=..., silenced_neuron_ids=...). packed_events is an internal validated adapter product, not a competing scientific API. Mutate state in place, return existing SimulationResult. No hidden reprepare/reset; no performance timing hook needed.

Runtime freezes graph, parameters/dt, D/R/refractory steps, coefficient values, backend/device/graph identity and ordered static lookup. State has strict runtime owner token plus semantic identity/device, lifecycle status, host timestep and five device arrays. One retained state represents one trial with [N]/[R,N] arrays; batch API need not be redesigned. Serialize calls on a runtime stream/lock initially; forbid concurrent use of the same state. No clone/restore API required.

| Proposed allocation | Owner/lifetime/shape/dtype | Initialization/sharing/free |
|---|---|---|
| outgoing pointers/targets/weights | Runtime backing; [N+1]/[E]/[E], int32/int32/float64 | Upload once, readonly shared, final backing release |
| ordered incoming offsets/source/edge ordinal | Runtime; [N+1]/[E]/[E], int64/int32/int64 | Derive from CSR, readonly shared, final backing release |
| optional target indices | Runtime; [N], int64 | arange, readonly shared, final release |
| v/g | State; two [N], float64 | rest/zero, private mutable, state close |
| refractory_until | State; [N], int64 | -1, private mutable, state close |
| pending/counts | State; [R,N], float64/int32 | zero, private mutable, state close |
| packed steps/positions/multiplicities | Call; compact [U], int64 | Validated host upload, readonly during call, free after completion |
| allowed/fired/free/silenced masks | Call; up to four [N], bool | Computed/false then set, private, free after completion |
| membrane/decay work arrays | Call; two [N], float64 | Fully written before read, no aliases, free after completion |
| counters | Call; [1], int64/queued uint64 | Zero, private, readback/free |
| spike indices/steps | Call; variable [Q], int64 | Per-step/growable storage, readback/free |
| traces/sparse summaries | Call; [K,S+1]/[S], dtypes above | Boundary column from state, fill/readback/free |

Persistent duplication per state: **24N+12RN bytes**, excluding allocator/metadata/call outputs. A/B duplicate all mutable storage; shared base graph ~4(N+1)+12E bytes; incoming lookup adds ~8(N+1)+12E. No capacity/performance claim. Reject int32 graph overflow before narrowing, int64 timestep/deadline overflow and pending int32 count overflow before unsafe scheduling. initial_state always returns independent allocations; state A advance/close cannot mutate/invalidate B or graph.

## Phase 6: delay/pending contract

D uses existing parameters.grid_steps with exact-grid atol=1e-10 ms; R=max(D+1,1). At absolute k consume k%R, count every due edge even if refractory rejects its g write, then clear weights/counts. Integrate, spike at k+1, queue nonsilenced outgoing edges at k+1+D into that step%R. CPU delivery_step<offset+S+R bound holds for every in-chunk spike with this R; preserve/prove it. No endpoint flush or discard. D=0 queues for the following boundary, after clearing consumed slot. Zero weight from cancellation must still retain counts. Empty new inputs still drain pending slots and advance all dynamics.

CPU insertion: ascending fired source position, then stored outgoing CSR edge order; sequential additions begin from existing slot value. Dense pending stores aggregates, not ordered event lists. GPU's rings are structurally compatible but currently cannot preserve them across calls: ownership is the design blocker resolved here. Move both rings into state, leave entirely device-resident, derive cursor from timestep%R.

Deterministic future scheduler: group incoming CSR entries by target, sorted by (source position, outgoing edge ordinal). One device writer per target begins with existing pending[event_slot,target], sequentially adds each weight whose source fired and is nonsilenced, increments count per edge. This reproduces CPU per-target order, duplicate edges, cancellation and existing slot contents without floating atomics/tree reduction. Exact integer reductions count queued/delivered edges within admitted bounds. It may scan inactive edges: unmeasured performance risk. Legacy atomic scheduler is not admitted for certified advance; optimizing the ordered reference is deferred.

Direct duplicates likewise use CPU semantics: integer multiplicity per local bin/target, float64 conversion then multiplication by the single ExplicitStimulus weight, one addition to allowed voltage. Repeated floating add.at is not admitted. Original payload/order stays authoritative for identity.

Certification snapshots after synchronization: identity, timestep, derived cursor, D/R, full v/g/refractory/pending/count arrays with shapes/dtypes; device/backend metadata separately. Compare physical ring slot order, not sparse totals. Aggregate rings cannot expose event-list order; collision fixtures test the specified insertion order. Snapshots are test-only host copies, not mandatory per-call production transfers or durable checkpoint format.

## Phase 7: simulated time/event window

Canonical time is state.timestep, host Python integer constrained to signed int64 range; units steps. No separate float clock/device cursor. At local l in [0,S), k=offset+l controls refractory comparisons, ring slot, output k+1 and deadline k+1+refractory_steps. Publish offset+S after successful synchronization/readback. Derived ms=timestep*dt; time after chunk n exactly equals time before n+1.

Events are local milliseconds [0,duration_ms), packed with existing schedule_events/_grid_steps. Zero belongs to current chunk; endpoint rejected and supplied at next chunk zero. Output spike can be at chunk end; pending delivery at that endpoint waits for next call. Duration positive and grid aligned. Absolute sparse steps, trace boundary column retained. Parameters/dt immutable; no hidden origin/reseed/floor-delay semantics.

## Phase 8: transfers

Construction uploads graph/static incoming lookup once; retain host neuron ID lookup/fingerprints. Generate coefficients on host using the CPU NumPy exp and np.isclose equal-tau branch, pass scalars to device. initial_state fills device arrays from scalars and synchronizes before publishing success. Per advance upload compact validated external events/multiplicities, masks/trace positions and offset/S/scalars. Keep v/g/refractory/rings device-resident. Read back chunk spikes/counts/counters and requested traces only; existing SimulationResult requires full int64[N] spike_counts. Metadata/digests host-side. No mandatory full dynamical-state copies. Dynamic output sizing may synchronize scalar data. Use an explicit runtime stream and complete it before return/release; no ambient null-stream assumptions. Full snapshots only for certification.

## Phase 9: failure/resources

| Boundary | Required behavior |
|---|---|
| Runtime construction | Future authorized lazy device/CuPy selection; validate device, projection/graph identity, weight/model/grid/index bounds. Failed upload/compile/allocation/sync publishes no runtime, releases owned partial allocations |
| initial_state | Reject closed runtime; allocate private arrays; allocation/init sync failure frees partial state only unless context fatal |
| advance prelaunch | Reject wrong owner/runtime/device, released/failed state, concurrent use, invalid events/IDs/window/grid/overflow; preserve valid state |
| advance after launch | Kernel/allocation/sync/readback failure may partially mutate: mark state FAILED, reject reuse, no success/rollback claim. Context-fatal failure poisons runtime and all further device work |
| State close | Idempotent, complete its work then drop private references; never free shared graph/global pools; output host arrays survive |
| Runtime close | Reject new states/advances; states retain strong backing references so graph storage persists until last state closes/completion. Existing states cannot advance after explicit close |

Dropping caller runtime variable does not destroy backing while states retain it. Physical storage may remain cached by allocator; no global pool reclamation. No implicit CPU fallback/reset retry. CPU has no explicit close API; added device resource metadata does not change scientific semantics.

## Phase 10: numerical policy

Proposed future **EQ-B**, conditional on certification; present application still **EQ-D**. No EQ-A or aggregate EQ-C escape hatch. Current float64 is insufficient: GPU math.exp differs from CPU np.exp, GPU unequal-tau expression lacks CPU np.isclose branch, cp.where/expression ordering differs from CPU out= sequence, duplicate scatter differs from count*weight, floating atomics/reductions differ from ordered accumulation.

Future seam uses CPU-generated coefficients including equal/near-equal tau branch, ordered subtract/multiply/add stages, no fast math/fused contraction changing order, ordered pending scheduler and duplicate multiplication above. Sparse float summaries use fixed target-index order if exposed. Record/pin backend/device/CuPy/compiler policy. Same strict v>threshold, reset v then g=0, inclusive refractory clamp, direct/pending/integrate/spike ordering.

Across CPU/GPU, every v/g sample/final value, pending weight and optional sparse float summary must satisfy **abs(gpu-cpu)<=2e-13+2e-13*abs(cpu)** elementwise; finite only, no NaN acceptance. This extends the historical trace threshold as a proposed admission policy, not demonstrated full-state evidence. No widening after failure.

Exact: payload/order/identity, graph/model/grid, shapes/dtypes, timestep/cursor/D/R, refractory deadlines, pending counts/bin placement, canonical spike IDs/steps/counts/digest, queued/delivered counters, integer sparse summaries, buffer isolation, readonly outputs. Pending aggregate weights may use tolerance across backends; insertion order/structure remain exact. Existing CPU fingerprint payload retained; backend/device metadata separately assessed. Spike mismatch fails even when voltage tolerance passes.

Within fixed GPU backend/device, whole versus chunks and repeated fresh executions require **byte equality** of every persistent array and concatenated events/traces. Concatenate traces omitting subsequent boundary columns; sum chunk counters. No tolerant continuity/repeat requirement. Threshold-adjacent/collision tests are mandatory; passing finite synthetic cases cannot establish universal/full-real equivalence.

## Phase 11: historical evidence

| Artifact | Disposition/reuse |
|---|---|
| CudaGraph/upload/float64 dense rings | H1 directly relevant architecture; reuse storage/equations, not floating atomic admission |
| test_task007c synthetic parity and masks/isolation | H2 scoped numerical evidence; reuse fixture builders, exact spikes/counts, 2e-13 traces; add complete boundary snapshots |
| [007c report](2026-09-21-task-007c-gpu-acceleration-gate.md) | H2 reported old scoped parity; H3 old environment/memory/100-1000-ms speedups only; no current availability/speed inference |
| task008 preflight and Q's recorded Task010 preflight | H2 old exact short-output promises; real routes excluded from synthetic task; not stateful certification |
| Historical GPU_READY as application readiness | H4 obsolete for resumable contract; graph reuse/repeat digest do not prove boundary-state parity |
| A011 CPU tests | Reference continuity/isolation logic reusable; do not execute Arena or real-data routes |

Historical speedups are not A019L-comparable/current performance evidence. No historical payload was read.

## Phase 12: bounded implementation surface

| Expected file | Future change |
|---|---|
| src/malecns_sim/dynamics/cuda.py | New runtime/state types; allocation/identity/close; absolute-time loop adapter; ordered incoming scheduling; multiplicity input; coefficient branch/order; result/snapshot seam |
| src/malecns_sim/dynamics/__init__.py | Lazy exports if needed; preserve CPU import without CuPy |
| tests/test_application_a019s.py | New synthetic structural ownership/packing/time/lifecycle/fake-device failure tests |
| tests/test_task007c.py | Narrow reuse of synthetic fixtures/assertions if needed; never enable opt-in real gate |

No CPU equations/optimization, PreparedNetwork schema, preparation/cache payload, UI/service dispatch or Arena changes needed. Construct runtime from existing in-memory synthetic projection. Later separately authorized application integration can choose runtime behind the same semantics. Legacy batch one-shot can remain uncertified for resumable use. Derived incoming lookup does not change graph/model.

## Phase 13: certification matrix

All cases use same synthetic in-memory graph/model/events for CPU PreparedRuntime and GPUPreparedRuntime; GPU whole/chunks/repeat references too. Snapshot every boundary. E=all exact fields above; T=v/g/pending floats/traces at frozen tolerance across CPU/GPU, byte equality within GPU. Default dt=0.1 ms, D=18/R=19, refractory=22 steps. S below is steps; no timing requirements.

| Case | Fixture/chunks/end step | E/T and pending assertions |
|---|---|---|
| C1 empty | No edges/input; 10+10/end20 | E/T; both rings zero, rest v/zero g |
| C2 direct | No edges, subthreshold input at0; 10+10/end20 | E/T; rings zero, no reset |
| C3 delayed crossing | 1->2, source spikes at1; 10+10/end20 | E/T; slot19%19 occupied at10, delivered at19 in next chunk |
| C4 pending retained | Same edge; 10+5/end15 | E/T; count/weight retained at both boundaries; no new input |
| C5 refractory crossing | Source spike1; direct event10; 10+20/end30 | E/T; deadline23 retained at10, reject event10, test allowed24; empty-edge rings zero |
| C6 fresh A/B | A active/B empty; 10+10 each/end20 | E/T; disjoint device buffers; B snapshot unaffected by A; full independent rings |
| C7 3+ chunks | Cyclic graph/sliced schedule; 7+13+4+26+50/end100 | E/T; all physical slots match whole; terminal pending explicitly checked |
| C8 differing activity | Shared runtime, active/inhibitory/quiet state inputs; 10+20/end30 | E/T; no mask/input/state leakage; independent rings |
| C9 output/readback | Traces, duplicates, signed collisions; 10+20/end30 | E/T; canonical absolute spikes/digest/counts, immutable results, boundary traces, canceled-weight counts |
| C10 release A | A to10/close; B 10+20/end30 | E/T B; A use fails, shared graph/B pending survives; runtime close rejects later advance |

Supplement: zero delay, equal/near-equal tau, collision/duplicate edges and inputs, near-threshold exact spikes, invalid ID/endpoint/off-grid/negative/nonfinite payload, wrong owner/device, invalid duration, allocation/kernel/sync failure, overflow bounds, output lifetime. Assert each fixture actually establishes its intended pending/refractory/spike precondition.

Matrix is ready, not run. **A019S scope is implementation and synthetic structural tests only**, including host/fake-device ownership/lifecycle/packing/time checks. Actual GPU numerical C1-C10 execution requires a later separately authorized certification gate. Structural tests cannot establish GPU correctness. No implicit GPU/preflight or benchmark authority from this design.

## Phase 14: feasibility and next task

F1: ownership, retained pending/refractory/absolute time, transfers, failure lifetime, numerical admission policy and implementation boundary specified; no unresolved architectural blocker. Ordered scheduler might be slower than atomics; performance is unknown, not a correctness objection. Future certification failure may invalidate assumptions; design readiness is not implementation acceptance.

Exactly one recommendation: **A019S — bounded implementation of the resumable GPU PreparedRuntime/SimulationState contract, with synthetic structural tests only and no performance benchmarking.** Not automatically started. GPU performance benchmark authorized: **No**.

## Counters, claims and closure

GPU runs=0; CUDA/CuPy preflights=0; synthetic benchmark runs=0; full-real preparations=0; real advances=0; A019D/A019L reruns=0; registered payload reads (all categories)=0; Arena/interventions/downloads/archive writes=0. These describe performed command scope, not independent native telemetry.

Claims limited to feasibility, ownership/lifecycle design, proposed policy and plan. No CPU/GPU equivalence, GPU correctness/speedup/realtime/full-real readiness established. Documentation only; no tests, tags/releases/version bump.

Validate static report and git diff --check. Commit only this report: `docs: design resumable GPU application state`; push origin master. Final local/origin/live equality, clean worktree/staging/stash, version0.3.0/workflows0 and commit SHA reported externally to avoid self-reference.
