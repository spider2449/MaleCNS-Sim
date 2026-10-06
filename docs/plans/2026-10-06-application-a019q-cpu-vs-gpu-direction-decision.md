# Application Task A019Q — CPU versus GPU direction decision

## Authorization, gates and review plan

User authorization: `授權 A019Q`. Evidence-only static review and a documentation-only commit/push. Root derived with `git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`, repository spider2449/MaleCNS-Sim.

Starting local HEAD = origin/master = live GitHub master = `9d55122bff0e5e90d3ab4030f5a8004d00237ec5`. Worktree clean; staging and stash empty; package version 0.3.0; tracked workflows 0. All starting gates passed before mutation.

Plan: inspect committed A019F–P reports and current CPU/GPU source/tests without importing or executing them; classify CPU candidates, map GPU architecture and contract gaps, review numerical/performance evidence, select one prerequisite and one next task; write this report, run `git diff --check`, commit/push and verify final identities. No Python invocation, test discovery, GPU availability call, GPU preflight, catalog discovery or registered payload inspection.

## Preserved full-real result and CPU closure audit

Preserve [A019L](2026-10-06-application-a019l-full-real-cpu-rebenchmark.md) **A019L-L1 / P2** and its [committed evidence](a019l-full-real-cpu-rebenchmark-evidence.json). A019D mean 1.647739485 s; A019L mean 1.094710500 s; mean change -33.5629%; paired measured positions 20 improved, 0 regressed; exact historical replay PASS. One preparation/network/runtime and two fresh independent states, each 2 warmups + 10 measured 20-ms advances, remain the contract. The 24 calls are aggregate, not a continuous 480-ms trajectory.

Mean slowdown is 1.094710500 / 0.020 = **54.735525×**; 0/20 measured calls meet 20 ms. Practical latency materially improved; realtime capability did not. Preserve L's qualified descriptive comparison and missing historical BLAS/thread/power/priority metadata.

| CPU candidate | Classification | Evidence and present disposition |
|---|---|---|
| Membrane | CLOSED-SUCCESS | A019I selected the ordered private scratch/out= transformation; J implemented and exact-certified it; K admitted the same-contract rebenchmark; L confirmed full-real benefit. COMPLETE; do not reopen. |
| Grid validation | CLOSED-NOT-WORTHWHILE | N found partial cacheability but incomplete admission; O found dt-only checks approximately 6.8–7.0% of grid-validation cost, VALUE-B / A019O-D. Moving validation changes errors/lifecycle. Deprioritized; the old 88–90% parent localization does not establish a useful static cache. |
| Input gathers | CLOSED-NO-SAFE-TRANSFORMATION | P-C: no safe or useful gather O1 justified. Compact exact candidates lose on the dense target; both-scratch reuse corrupts decay; full-array replacement is unproved or changes error behavior. All candidates NOT_READY. No reopening without new external evidence. |
| Indexed writeback | DEFERRED-HIGH-RISK | I/M: HIGH importance, LOW/UNCLEAR replacement specificity, HIGH semantic risk/validation burden, R4. Current ordered v-then-g Boolean assignments remain; no subsequent concrete exact replacement emerged. |

P's G3 selection is approximately full (K near N). Its full-selection local probes in microseconds: Boolean baseline 53.553; compression 355.532; take 269.279; voltage-scratch hybrid 175.865. Additional K/index work, internal buffering and scratch lifetime conflicts explain rejection. These are historical local timings, not current full-real shares.

Review chain: [F](2026-10-06-application-a019f-synthetic-cpu-advance-instrumentation.md) localized multiple cost centers; [G](2026-10-06-application-a019g-cpu-substage-instrumentation.md) required finer residual attribution; [H](2026-10-06-application-a019h-linear-local-instrumentation.md) localized gathers/membrane/writeback; [I](2026-10-06-application-a019i-linear-o1-feasibility.md) selected membrane; [J](2026-10-06-application-a019j-membrane-o1-optimization.md) implemented it; [K](2026-10-06-application-a019k-full-real-rebenchmark-gate.md)/L validated the investment; [M](2026-10-06-application-a019m-further-o1-decision.md) selected the remaining bounded feasibility questions; [N](2026-10-06-application-a019n-grid-validation-feasibility.md)/[O](2026-10-06-application-a019o-dt-validation-diagnostic.md)/[P](2026-10-06-application-a019p-input-gather-feasibility.md) resolved those questions negatively for near-term O1.

No **OPEN-HIGH-VALUE** CPU candidate remains. F's scheduling, pending delivery and propagation observations are measurable regions, not newly established safe transformations. H/G shares predate J and cannot be transferred to current full-real proportions.

Another plausible scalar/NumPy O1 is unlikely to change P2. There is no remaining transformation with membrane's combination of specific removable work, ordered exact arithmetic, bounded ownership and demonstrated benefit. Another ordinary CPU diagnostic would largely revisit resolved uncertainties or expose the already-known writeback design risk; no evidence supports meaningful new information at comparable cost. Continued CPU micro-optimization is therefore no longer the best near-term investment. CPU remains useful and maintainable; the line is **paused**, not permanently closed or mathematically exhausted.

## Current GPU architecture map

Static source authority: [cuda.py](../../src/malecns_sim/dynamics/cuda.py), [lif.py](../../src/malecns_sim/dynamics/lif.py), [stimulus.py](../../src/malecns_sim/dynamics/stimulus.py), [task008.py](../../src/malecns_sim/analysis/task008.py), [application service](../../src/malecns_sim/application/service.py). No module was imported.

| Component | Current implementation and lifetime |
|---|---|
| Entry points | Lazy `_cupy`; `cuda_available`; `upload_graph`; `simulate_cuda` delegates to `simulate_cuda_batch`. `measure_memory` is an execution helper, not called here. |
| Prepared graph | `PreparedNetwork` carries CPU `EffectiveSignedProjection` plus optional `cuda_graph`; `prepare_network(use_cuda=True)` uploads it. `CudaGraph` holds device CSR indptr/targets int32 and weights float64 with neuron/edge counts. A caller-supplied graph can survive repeated one-shot trials. This is graph reuse, not state resume. |
| Initialization | Every batch call validates parameters/duration, constructs host schedules/masks, then allocates fresh device v at rest, g zero, refractory_until=-1, and zero pending rings/counts. |
| Neuron state | v/g float64[batch,N], refractory_until int64[batch,N]; refractory-free and silencing bool masks. No public GPU state owner or runtime identity/timestep object. |
| Propagation | Device `schedule_active_edges` RawKernel traverses fired, nonsilenced outgoing CSR rows. Floating atomicAdd accumulates signed weights; integer atomics track counts. Dense ring shape [batch,delay_steps+1,N], float64 weights and int32 counts. |
| Inputs | CPU `_stimulus_inputs` generates or accepts ExplicitStimulus and uses shared schedule_events. Direct trial/position/value lists are uploaded each active step; `cp.add.at` writes accepted impulses. Inputs are call-relative. |
| Dynamics/order | Direct writes, pending delivery, linear update, strict threshold, reset/refractory assignment and delayed scheduling. cp.where replaces local array references; float64 expressions differ from CPU out= operation sequence. |
| Outputs/readback | Synchronizes null stream; cp.asnumpy reads spikes, counters and optional traces/sparse summaries. Canonical spike sorting and host digest/result construction return SimulationResult objects only. Final v/g/refractory/pending arrays are not returned. |
| Allocation lifetime | Graph persists when caller retains it. Mutable state belongs to the invocation and is not reachable through the public result for continuation; CuPy pools may retain freed allocation storage. No explicit persistent-state close/clone/ownership contract exists. |
| Time/refractory/delay | Local `range(steps)` begins at zero on every call; refractory deadlines and ring slot phase are local. Pending events work within the call but are inaccessible beyond its return, including events queued past the horizon. |
| Fresh state/clone | One-shot calls initialize fresh arrays; batch lanes have historical isolation tests. No public initial_state or clone for independently retained resumable states. |
| Application integration | ProductionEngine.simulate dispatches to one-shot simulate_cuda with prepared.cuda_graph. CPU PreparedRuntime.advance is a separate stateful seam; no CUDA implementation of that seam was found. |

GPU advances cannot continue from a previous GPU state today. Reusing CudaGraph does not preserve simulated time, refractory, synaptic or pending state.

## CPU application contract versus GPU contract

Reference: CPU SimulationState/PreparedRuntime in lif.py; [A011 continuity tests](../../tests/test_application_a011.py); A019A/C/L frozen stateful benchmark. CPU state retains runtime identity, absolute timestep, v/g, refractory deadlines and pending weights/counts. advance requires explicit chunk-relative input and mutates the same state; stochastic schedules are generated once externally and sliced. A011 tests compare whole versus chunks, all persistent arrays and time, and fresh-state independence.

G1 = supported with existing tests (historical scope, not an A019 current certification); G2 = implemented without current certification; G3 = partial; G4 = missing; G5 = different contract requiring design.

| Required item | GPU class | Finding |
|---|---|---|
| One PreparedNetwork | G1 | Existing preparation/cache and one-shot full-graph gates support shared prepared projection/device graph; no current stateful certification. |
| One PreparedRuntime | G4 | No GPU runtime for this interface. |
| Fresh independent SimulationState objects | G4 | No exposed GPU state objects. |
| runtime.initial_state() | G4 | Fresh local allocation exists only inside simulation calls. |
| Repeated advance(state) | G4 | No state parameter/return or resumable advance. |
| Exact chunk continuity | G4 | No GPU chunk test/interface; repeated one-shot calls reset. |
| Current simulated-time continuity | G4 | No persistent absolute timestep. |
| Refractory continuity | G3 | Within-call deadlines exist; cross-call persistence missing. |
| Synaptic-state continuity | G3 | Within-call g exists; cross-call persistence missing. |
| Pending/delayed-event continuity | G3 | Within-call dense ring/counts exist; cross-chunk retention/phase missing. |
| Deterministic event ordering | G5 | Canonical output sorting exists; floating atomic accumulation order is not defined as CPU order. Sorting outputs cannot certify internal determinism. |
| Outputs per chunk | G3 | SimulationResult shape exists for one call, but absolute chunk time and retained boundary state are absent. |
| A/B state independence | G3 | One-shot batch isolation is tested; two independently retained resumable owners are missing. |
| No hidden reset/reprepare between chunks | G5 | Graph reuse avoids upload; state is explicitly reset each call. |
| State representation compatibility | G5 | CPU one-dimensional arrays versus GPU batch-dimensional arrays; snapshot/transfer/identity design needed. |
| Ownership/lifetime and transfer semantics | G5 | Graph reference and host result transfer exist; persistent state ownership, device affinity, synchronization/error lifetime need definition. |

No G1 row implies current A019 GPU certification. The decisive gap is architectural, not merely a missing test invocation.

## Numerical equivalence policy status

Existing [Task 007c tests](../../tests/test_task007c.py) require exact canonical spike IDs/timesteps and queued/delivered counts, with v/g traces `rtol=2e-13, atol=2e-13`. They cover duplicate input, inhibition, self-edge, refractory, delay and propagation fixtures. The optional real gate checks exact emitted spikes and repeated digest. Task008.run_cpu_gpu_preflight requires exact IDs, timesteps, counts and digest for pregenerated short schedules; Task010's silencing preflight likewise requires exact canonical events. These promises must not be silently loosened.

Historical scoped policy is **EQ-B** for float64 traces with exact discrete outputs; real preflights principally supply **EQ-C** output evidence. Neither promises byte-identical complete floating state (**EQ-A** is unsupported). GPU uses float64, but cp.add.at direct scatter differs from CPU bincount-and-multiply; parallel floating atomicAdd differs from CPU ordered accumulation; GPU reductions and elementwise execution can differ in rounding. Repeat-digest tests on selected workloads do not establish general deterministic internal state or cross-chunk numerical equivalence.

For the **current resumable CPU/GPU application contract, classification is EQ-D — current equivalence contract not established**. There is no tested persistent GPU boundary state to compare. CPU linear_state_update also handles equal membrane/synaptic time constants explicitly; CUDA currently uses the unequal-time-constant coefficient expression directly. Parameter coverage must therefore be explicit rather than assuming all CPU parameter combinations already match. Future design must explicitly freeze discrete exactness, continuous-state tolerances/meaning, chunk-versus-whole continuity and repeat determinism, including threshold-sensitive collision cases and pending buffers. It must resolve floating operation order without assuming impossible universal byte equality or weakening existing tests. This report does not enact a new tolerance policy.

## Historical GPU performance applicability

[Task 007c committed report](2026-09-21-task-007c-gpu-acceleration-gate.md) records 166,700 neurons / 6,113,545 effective CSR edges; one-shot 100/1000-ms trials and batched 30-trial runs, with 4.41× / 5.71× / 30.54× simulation speedups. Float64 device dynamics, graph reuse and within-trial delays make this **HISTORICAL-RELEVANT** architecture evidence. Those timings are **HISTORICAL-NOT-COMPARABLE** to A019L; none is CURRENTLY-CERTIFIED for the present application contract.

| Comparability condition | Result |
|---|---|
| Same graph size/identity | Same reported neuron count. L preparation identity reports 24,904,953 edges at its preparation layer, while 007c reports effective CSR edges; these are not sufficient same-layer identity proof. No historical-to-current effective graph identity certification established. |
| Same stateful application contract | No: independent one-shot trials/batches versus explicit retained runtime/state. |
| Same repeated 20-ms advance pattern | No: 100/1000-ms performance workloads. Historical 20-ms preflights are correctness checks, not repeated resumable performance evidence. |
| Same pending/delayed semantics | Within-trial ring mechanism relevant; cross-chunk retention untested/missing. |
| Same current implementation | Not established: historical checkpoint predates current CPU membrane optimization and resumable certification; no current same-contract measurement. |
| Same numerical contract | Historical exact outputs/tolerant traces; current full boundary-state equivalence is undefined. |

Historical acceleration supports investigating correctness/interface feasibility, not an A019L speedup prediction or realtime claim.

## Investment scorecard and first blocker

Ratings concern the next investment; evidence strength distinguishes strong CPU disposition evidence from weaker evidence for another CPU transformation. Expected GPU upside is architectural potential, not measured present latency.

| Dimension | A: continue CPU O1 | B: begin GPU correctness/equivalence work |
|---|---|---|
| Evidence strength | LOW for another transformation; HIGH for pause decision | MEDIUM: existing device implementation/history plus HIGH confidence in missing interface |
| Expected latency upside | LOW for current admitted candidates | HIGH potential; current achieved upside UNKNOWN |
| Contract readiness | LOW for another safe useful transformation | LOW for resumable application interface |
| Engineering complexity | HIGH for unresolved writeback alternatives | HIGH overall; first design task bounded |
| Scientific/model risk | HIGH for unproved scatter/order alternatives | MEDIUM: numerical/event mismatch risk, constrained by CPU semantics |
| Validation burden | HIGH | HIGH |
| Information value of next task | LOW | HIGH |
| Probability of changing practical product capability | LOW | UNKNOWN pending design/equivalence |

GPU correctness/contract work has higher expected engineering value because it addresses a qualitatively different execution frontier with identifiable existing building blocks, while near-term CPU transformation questions have been resolved or deferred. The 54.7× slowdown alone is not the reason to choose GPU.

Single highest-leverage blocker: **GPU-B1 — RESUMABLE STATE INTERFACE MISSING**. The interface must make retained arrays, absolute time/ring phase, ownership and initial-state isolation explicit before continuity/equivalence can be certified. Undefined numerical policy and missing continuity harness are downstream requirements within that design, not additional selected first blockers. No evidence requires a wholesale backend rewrite as the first step; feasibility must decide whether the existing one-shot loop can support the seam safely.

## Terminal disposition and exactly one next task

**A019Q-B — CURRENT CPU O1 LINE PAUSED; GPU RESUMABLE-STATE CONTRACT REQUIRES DESIGN BEFORE CERTIFICATION.**

Exactly one recommendation: **A019R — bounded design/feasibility task for a resumable GPU PreparedRuntime/SimulationState contract matching the certified CPU application semantics.**

Its concrete reviewable scope should define state fields/shapes/identity/device ownership, initial_state and fresh A/B isolation, absolute timestep and delayed-ring phase, refractory/g continuity, chunk-relative inputs and absolute outputs, transfer/synchronization/cleanup/error behavior, and whether snapshots/cloning are required or deferred. Freeze the numerical equivalence policy while retaining existing exact event and trace-test promises, and specify a synthetic continuity/isolation/collision certification matrix. State whether a narrow adaptation of existing CUDA code is feasible and identify the minimum implementation boundary. Performance benchmarking must wait for available resumable semantics, frozen equivalence policy and passing continuity/isolation tests.

A019R is recommended only; not started or automatically authorized. **GPU performance benchmark authorized: No.** This A019Q authorization includes no GPU execution, implementation, preflight or synthetic rerun.

## Nonclaims, counters and closure

Allowed retained claim: one exact-equivalent CPU membrane optimization produced a confirmed approximately 33.6% mean full-real latency reduction under the certified benchmark. No claim of mathematical CPU exhaustion, GPU speed under A019L, transferable historical speedup, current CPU/GPU equivalence, achievable realtime, biological realtime, broader behavior/scientific capability or model change.

| A019Q activity | Count |
|---|---:|
| Synthetic benchmark runs | 0 |
| GPU/CUDA/CuPy runs | 0 |
| Full-real preparations | 0 |
| Real advances | 0 |
| A019D/A019L reruns | 0 |
| Arena runs | 0 |
| Interventions | 0 |
| Downloads | 0 |
| Archive writes | 0 |
| Registered payload reads, all categories | 0 |

These counts describe the performed command scope: Git queries, PowerShell text inspection of tracked documentation/source/tests, and this report write. They are not independent native-read telemetry. Historical evidence references are report reads, not registered payload reads. No workload imports, test collection or executables were invoked; no task-wide execution firewall claim is made.

Only this plan/report changes. Documentation/static review and `git diff --check` are the required validation; no tests because no executable code changes. Commit message: `docs: decide CPU versus GPU optimization direction`; push to origin/master. Resulting commit SHA and verified local/origin/live equality are reported externally to avoid self-reference. Final requirements: clean worktree, empty staging/stash, version 0.3.0, tracked workflows 0; no tag, release or version bump.
