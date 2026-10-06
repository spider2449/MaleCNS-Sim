# A019U evidence-only GPU performance gate

Authorization: **授權 A019U**. Root derived with `git rev-parse --show-toplevel`:
D:/spider/working/MaleCNS-Sim. Starting local HEAD = origin/master = live GitHub
master = **2112b0b84cec931ababb98850ce6223b9cd47371**. Worktree, staging and
stash empty; package version 0.3.0; tracked workflows 0.

Plan: read named committed reports/evidence and source as text, verify certified
source identities, audit measurement/resource readiness, freeze future timing
rules and select one next task. Write only this report, run `git diff --check`,
commit/push and verify final custody. No imports, GPU queries, test collection,
payload discovery, preparation or timing execution. No implementation changes.

## Decision and correctness integrity

**A019U-A — BOUNDED SYNTHETIC GPU PERFORMANCE BENCHMARK JUSTIFIED FIRST.**
Path S; **SYN-A**, **HARNESS-B**, **VRAM-B**. Correctness is no longer the
bounded synthetic blocker. Direct full-real benchmarking is not ready today:
the CPU-specific recorder needs a bounded GPU adapter, synthetic timing
validation and measured resource preflight. These are small benchmark-work
requirements, not an unresolved production correctness defect requiring U-C.

Exactly one next task: **A019V — bounded synthetic CPU/GPU resumable-state
performance benchmark under the certified EQ-B application contract**.
Synthetic workloads only; no real data. This recommendation does not execute V
or authorize a later real attempt automatically.

[A019T](2026-10-06-application-a019t-cpu-gpu-resumable-equivalence.md) and its
[JSON](a019t-cpu-gpu-resumable-equivalence-evidence.json) preserve
**A019T-A / EQ-B CERTIFIED**, rtol=atol=2e-13. C1-C10, 19 admission cases,
delay/ring and refractory pass; discrete mismatches, voltage, conductance,
pending-weight errors and repeated-chunk drift are zero. C3/C5/C7 fresh-state
repeats are byte-exact; isolation and release-A/continue-B pass. No correctness
preflight was rerun. Current Git blobs match T exactly: CPU lif.py
`25de1770f4736df94bf5899ba7aa5ce57d77fca6`, GPU cuda.py
`b8b0577ef663eca4d107cd69e1c805c59ee0bc78`, stimulus.py
`e2a6c96ba736b17240ca90421f8076548b84e372`.

The authoritative optimized CPU reference is [A019L-L1 / P2](2026-10-06-application-a019l-full-real-cpu-rebenchmark.md),
not A019D: 20 measured calls, mean 1.094710500 s, median 1.099888450 s,
p95 1.145525860 s, max 1.166905800 s; 20 improved/0 regressed versus D;
54.735525x realtime slowdown. Scientific/model semantics remain the same
certified application contract. D is pre-membrane-O1 historical context only.

## Static production audit

Authority: [cuda.py](../../src/malecns_sim/dynamics/cuda.py), especially
GPUPreparedRuntime construction, initial_state, advance, _advance_device and
close; [A019S](2026-10-06-application-a019s-resumable-gpu-implementation.md).

| Surface | Classification | Finding |
|---|---|---|
| Runtime construction / CSR upload | BENCHMARK-SAFE | One runtime; uploads CSR and ordered incoming arrays once, compiles ordered RawKernel, creates explicit nonblocking stream and synchronizes |
| initial_state | BENCHMARK-SAFE | Independent device arrays, initialization sync before return; report separately |
| Repeated advance / dynamic residence | BENCHMARK-SAFE | Same v/g/deadlines/pending/count pointers and absolute timestep; no hidden state/runtime recreation |
| Per-call events, masks, scratch | BENCHMARK-OVERHEAD | Host admission/packing, device event/mask uploads and fresh work buffers are production costs |
| Output materialization | BENCHMARK-OVERHEAD | Spike positions/steps, scalar queued/delivered counters and requested traces read back; host canonicalization, bincount, freezing and digest included |
| Final stream synchronization | BENCHMARK-OVERHEAD | Unconditional public advance completion boundary; also at construction, initial_state and close |
| Dynamic indexing / flatnonzero | UNKNOWN | Boolean compaction and variable-size results may cause internal synchronization; count and contribution not established statically |
| Full-state/debug/assertion readbacks | BENCHMARK-SAFE | None in production advance; test snapshots explicitly external |
| Per-call graph upload / ordered RawKernel compile | BENCHMARK-SAFE | Neither occurs; CuPy operation kernels may compile lazily on first use |
| Release/lifetime | BENCHMARK-SAFE | State close syncs and releases private references; shared backing remains; no global pool reclamation |

The path is safe to measure as the public production operation, with the above
overheads retained. This is not a performance result. Full required spike
counts are built on the host from copied spike positions, not copied from a
device count array. No voltage/conductance/deadline/ring host round trip occurs
in production. The ordered scheduler scans incoming edges for every target
each timestep, including quiet steps; historical active-source atomic scheduling
is a different performance architecture. No optimization is performed here.

## First-use boundaries and required axes

RawKernel `.compile()` is explicit in runtime construction. Cache hit/miss,
NVRTC/module loading, CuPy import/context initialization, allocation and stream
creation can affect cold preparation. Existing S/T evidence establishes that
compilation worked on CuPy 14.2.0, runtime API 12090, driver API 13000, RTX 3060;
it supplies no cost measurement. CuPy ufunc/reduction/compaction kernels and
allocator expansion can first appear during initial_state or warmup advance.
Do not assume RawKernel compilation eliminates all first-advance costs.

Future boundaries:

1. Record fresh-worker startup/import/context separately, cache policy and
   environment. Record host projection preparation separately from GPU runtime
   construction/upload. Aggregate cold readiness must include both; do not hide
   context setup by an unreported preflight. GPU runtime timer begins before
   construction and ends after its synchronized return.
2. Time each initial_state call from entry through synchronized return.
3. One runtime; independent A then B, A released before B; each state has two
   individually reported warmups and ten measured 20-ms chunks at dt=0.1 ms.
   No reset between chunks, no extra warmups substituted into this trajectory.
   Any separate diagnostic warmup uses another explicitly reported fixture.
4. Primary advance wall timer starts immediately before public advance and ends
   after returned SimulationResult and its stream synchronization. Include
   validation, host packing, allocation, H2D events/masks, device work, D2H
   results, host output assembly/digest and required internal waits. Slice the
   pre-generated schedule outside this timer, consistently with L. Any historical
   outer encoding/readout timer must also be retained: L statistics use t0-t5
   total (pack, advance, readout, speed and bookkeeping). Future full-real
   L speedup and realtime classifications must use that matching total, with
   public advance reported separately; never divide L total by GPU core time.
5. EQ-B snapshots, comparison, serialization/report writing and cleanup occur
   outside primary timers. No test snapshot inside advance measurement. Substage
   diagnostics must not insert barriers into primary calls or be substituted for
   wall time; use a separately labeled synthetic diagnostic pass if needed.

| Axis | Requirement | Measurement status / boundary |
|---|---|---|
| Host preparation and GPU construction/upload | REQUIRED | Separate wall intervals plus cold aggregate |
| initial_state | REQUIRED | Synchronized wall interval for A and B |
| Warmup advance | REQUIRED | All four calls individually retained |
| Repeated advance | REQUIRED | All 20 public-boundary wall times |
| H2D event transfer | REQUIRED inclusion; OPTIONAL isolated attribution | Included in advance; current API has no isolated timer |
| Device compute | OPTIONAL isolated attribution | Stream events/profiling need bounded harness diagnostics; not current API telemetry |
| D2H outputs/readback | REQUIRED inclusion; OPTIONAL isolated attribution | Includes spikes, counters, requested traces and host assembly |
| Public synchronization | REQUIRED | Final backing.stream.synchronize before timestep publication/return |
| Peak GPU memory | REQUIRED | Sample worker/device use and pool used/reserved, baseline and attribution limits; not currently recorded by resumable API |
| Host private/working set | REQUIRED if available | Existing Windows contained-tree sampling can be reused |
| Exact per-operation implicit-wait decomposition | NOT CURRENTLY MEASURABLE | No existing instrumentation; no invented additive stage totals |

## Synthetic value and full-real readiness

**SYN-A**: synthetic work can verify wall timers against asynchronous completion,
expose first-use compilation/cache artifacts, quantify event/output overhead,
exercise allocation and the ordered incoming scan, and discover pathological
performance before consuming a real attempt. Paired optimized CPU/GPU synthetic
work can establish speed on those fixtures only. Include small controls and
bounded increasing N/E, degree skew, quiet/active propagation, event density,
pending/refractory continuity and output density. A generated full-scale shape
can exercise similar CSR/ring structure without real topology or activity.
Bounds and fixture sizes must be preregistered in V before execution.

A synthetic slowdown, unstable timing, dominant transfers, failed allocation
or invalid harness would change the decision to spend a real attempt. Successful
synthetic timing would justify considering a separate real gate; it cannot
predict full-real speedup or demonstrate full-real EQ-B.

| A019L-style requirement | Readiness | Evidence / remaining gap |
|---|---|---|
| Same registered source set | READY statically | Existing certified bounded CPU preparation route; no sources opened in U |
| Same graph identity | READY statically | Shared projection constructor seam; require G1-G6 and projection identity on any future authorized attempt |
| Same schedule generation / 948 events | READY | Existing freeze_schedule and chunk slicing, identical frozen A/B windows |
| 20-ms chunks / 24 advances | READY | Public API supports 200 steps per chunk; two 12-call sequences, not continuous 480 ms |
| No reset / pending / refractory | READY | S/T bounded certification and retained source implementation |
| Same output contract | READY | SimulationResult boundary certified on bounded matrix |
| Full-scale EQ-B comparison capability | PARTIAL | T has synthetic snapshots; full-real recorder assumes NumPy and exact CPU replay; GPU snapshots need explicit outside-timer conversion and frozen tolerance rules |
| Bounded resource supervision | PARTIAL | Windows Job, timeouts and host caps exist; GPU telemetry/preflight and fail-closed bounds need adapter validation |
| Cleanup / no orphan | PARTIAL | Job containment and scoped GPU close exist independently; integrated GPU worker failure/cleanup unvalidated |
| Direct full-real GPU timing adapter | MISSING | No directly usable resumable GPU benchmark entry point |

Direct full-real benchmark: **NOT READY**. Current static semantics support
construction from the certified prepared projection, but the missing adapter
and partial supervision/comparison integration prevent a readiness claim.

## Structural GPU memory

Current L [evidence](a019l-full-real-cpu-rebenchmark-evidence.json) records
N=166,700, E=24,904,953 (preparation_identity_contract uses effective_weights
size, equal to outgoing CSR edge size), dt=0.1 ms, delay=1.8 ms, R=19.
Effective projection identity:
`ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f`;
prepared-network identity:
`d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495`.
These are distinct contract layers. Schedule identity:
`6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a`.

| Allocation | Structural bytes |
|---|---:|
| Outgoing int32 pointers/targets, float64 weights | 4(N+1)+12E = 299,526,240 |
| Incoming int64 offsets, int32 sources, int64 ordinals | 8(N+1)+12E = 300,193,044 |
| Total immutable graph | 12(N+1)+24E = 599,719,284 |
| Per-state v/g/deadlines | 24N = 4,000,800 |
| Per-state pending weights/counts | 12RN = 38,007,600 |
| Total per-state | 42,008,400 |
| Two simultaneous states (graph shared) | 84,016,800 mutable bytes |
| Named call masks/scratch/queued arrays | 26N+16 = 4,334,216 |
| Event positions/multiplicities | 16U; U admitted unique step/target pairs, <=948 for the whole frozen schedule |
| Trace outputs | 16K(S+1), S=200; K fixed identically to CPU |
| Spike lists | 16M, M<=NS; plus concatenation buffers of comparable size |

Graph + one state + named call arrays = **646,061,900 bytes (616.13 MiB)**,
before dynamic indexing/reduction temporaries, traces, spike concatenations,
device metadata, CUDA context/modules and allocator reservation. Worst loose
spike-list bound is 533,440,000 bytes per 200-step chunk, with additional
concatenation storage. This is accounting, not measured peak or a complete cap.
Host retains projection and temporary sorting/source/offset arrays during upload;
host peak cannot be inferred from device accounting. A019L's 5,441,220,608-byte
contained private peak is historical CPU context, not a GPU host-memory bound.

A can be closed before B creation without releasing the runtime. This avoids
logical A/B state duplication; allocator caching may still reserve released
memory. Against the known RTX 3060 12 GB VRAM, **VRAM-B — plausible but needs
measured preflight**. Base arrays have substantial structural headroom, but
unknown pool/context/output peaks and GPU supervision prevent VRAM-A.

## Harness and comparison contract

**HARNESS-B — small bounded benchmark harness needed.**
[benchmark_application_a019.py](../../scripts/benchmark_application_a019.py)
accepts a runtime factory but its Recorder, weakrefs, NumPy initialization checks
and historical state_evidence are CPU-specific. L additionally demands exact
CPU historical replay. T is a correctness suite with external snapshots, not a
performance harness. Task007c times legacy one-shot/batch simulation and uses
cache/data paths; it must not be run or repurposed unchanged for resumable timing.
Reuse containment/schedule/metrics concepts; add bounded synthetic GPU lifecycle,
timing and memory reporting in V, with no production change or tuning.

CPU reference for V is the optimized implementation at V's starting SHA,
behaviorally equivalent to L. Prefer paired synthetic execution on identical
fixtures/environment; record order, dependency/source identities, cache policy,
GPU/CPU settings and background load. Do not divide L full-real timings by
synthetic timings and call that speedup. For a future full-real task, compare
primarily against frozen L; a same-session CPU full-real control requires
explicit separate authorization. Never silently rerun D/L.

Required metrics: preparation and initial-state times; all warmup times; all 20
measured times; measured min, median, mean, max, p95, population std, CV,
A mean/B mean; counts <=0.020 s, >0.020 s, >=30 s. Specify percentile method
as linear interpolation (20 values: sorted[18]+0.05*(sorted[19]-sorted[18])),
consistently with L, and retain precision/raw values. For matching full-real
workload, report L mean/GPU mean and L median/GPU median; realtime ratio
GPU mean/0.020. Include output configuration, memory peaks and qualified
environment comparability. No statistical significance claim.

Frozen performance outcomes: **GPU-P1** every measured call <=20 ms;
**GPU-P2** at least one >20 ms and all <30 s;
**GPU-P3** any advance >=30 s/timeout or resource failure. Invalid comparison
is separately G5; warmup/preparation failure must be recorded rather than
excluded to manufacture a successful measured distribution.

Frozen benefit labels: **G1** meaningful consistent large benefit; **G2** faster
but modest benefit; **G3** comparable/mixed with no material benefit; **G4**
material regression; **G5** invalid workload/environment/harness comparison.
No percentage thresholds are justified by current GPU evidence. These are
descriptive labels: report raw ratios, per-state consistency, tails and ambiguity;
do not manufacture a numerical G1/G2 cutoff or claim preregistered quantitative
benefit significance. Any future quantitative gate must be justified and frozen
before that task's timing execution.

## Historical disposition and attempt economics

[Task007c](2026-09-21-task-007c-gpu-acceleration-gate.md): 166,700 neurons,
6,113,545 effective edges, sugar 100 Hz schedule, one-shot 100/1,000-ms trials
and batch-30 independent 100-ms trials. CPU/GPU: 7.318/1.660 s (4.41x),
86.408/15.139 s (5.71x), serial-30/batch-30 221.810/7.263 s (30.54x).
Every result is **HIST-P1** qualitative plausibility and **HIST-P3** not comparable
to current application timing. GPU CSR/dense ring/batching observations are
**HIST-P2** architecture evidence only. No resumable application state contract
was present; old atomic active-source kernel, pre-O1 CPU, different graph and
trial structure preclude expected-speedup transfer.

Historical allocation deltas approximately 74 MiB graph, 48 MiB graph plus
one-trial state/delay, 1,209 MiB batch-30; report theoretical values 94.7/40.1/
1,202 MiB, runtime sample 2,484 MiB and 4.13 trials/s batch-30. Preserve the
report's differing allocation conventions; none is current VRAM peak. Generation:
CuPy 14.2.0/cupy-cuda12x, Toolkit/NVRTC 12.4, linked runtime 12.9 (local 12.4
also reported), driver 581.15/CUDA compatibility 13.0, compute capability 8.6.
These are committed historical environment facts, not refreshed observations.

Full-real memory is plausible, but timing harness trust, implicit waits,
first-use behavior and integrated cleanup remain unmeasured. A bounded
synthetic benchmark can cheaply prevent avoidable asynchronous timing mistakes,
allocation failures or clearly poor performance. It can change whether a real
attempt is worth spending. Hence synthetic-first is substantive, not ritual.
Only actual real topology/activity performance remains inherently real-specific.

## Validation, counters and custody

Documentation/static review only. `git diff --check`: PASS. No executable code
changed; no tests or compileall executed. Source review used named tracked text
and committed evidence only; no Python/CuPy import or registered directory
traversal. Zero reads describe explicit command scope, not independent native
byte telemetry or a newly certified firewall.

GPU performance runs=0; CPU performance runs=0; synthetic timing runs=0;
kernel timing=0; full-real preparations=0; real advances=0; A019D/A019L reruns=0;
registered payload reads=0; Arena/interventions/downloads/archive writes=0;
tuning=0; tags/releases/version bumps=0.

Allowed claim: bounded synthetic CPU/GPU resumable application EQ-B certification
is preserved. No GPU speedup, realtime, full-real GPU equivalence, full-real
benchmark readiness or biological realtime claim is made.

Commit/push authorized. Containing commit SHA and final local/origin/live equality
are reported externally to avoid self-reference. Final worktree/staging/stash
must be empty, version 0.3.0, tracked workflows 0. No tag or release.
