# A019W evidence-only GPU performance disposition

Authorization: **授權 A019W**. Root derived with `git rev-parse --show-toplevel`:
`D:/spider/working/MaleCNS-Sim`, spider2449/MaleCNS-Sim. Starting local HEAD,
origin/master and live GitHub master all equal
`2ccf15dd7f283ab4b253eef3f325279d6c93f97a`. Worktree clean, staging/stash empty,
package version 0.3.0, tracked workflows 0. Gates passed before mutation.

Plan: review committed Q-V reports/evidence and named production/harness text;
calculate descriptive ratios from V JSON using PowerShell; map the certified
hot path; assess bounded hypotheses and choose one direction; write this report,
run `git diff --check`, commit/push and verify final custody. No Python imports,
test discovery, device queries, execution or registered payload inspection.

## Terminal decision

**A019W-B — GPU FULL-REAL PERFORMANCE LINE PAUSED; ONE BOUNDED BOTTLENECK
PROFILING DIAGNOSTIC JUSTIFIED.** Preserve **A019V-C / G4** and **NO FULL-REAL
ATTEMPT**. Preserve **A019T-A / EQ-B CERTIFIED** and **A019S-A**.
Backend disposition: **RETAIN-CERTIFIED**, within its bounded synthetic
certification scope. Current performance value is poor; correctness/reference
value remains high. Future architecture research value is conditional.

Exactly one next task: **A019X — bounded synthetic GPU profiling diagnostic of
per-timestep Python/CuPy kernel-launch dispatch overhead**. No optimization in
X; recommendation only, not automatically started or execution-authorized here.

## Evidence integrity

Reviewed [Q](2026-10-06-application-a019q-cpu-vs-gpu-direction-decision.md),
[R](2026-10-06-application-a019r-gpu-resumable-state-design.md),
[S](2026-10-06-application-a019s-resumable-gpu-implementation.md),
[T](2026-10-06-application-a019t-cpu-gpu-resumable-equivalence.md),
[U](2026-10-06-application-a019u-gpu-performance-gate.md),
[V](2026-10-06-application-a019v-synthetic-cpu-gpu-performance.md) and V's
[machine evidence](a019v-synthetic-cpu-gpu-performance-evidence.json).
Q paused ordinary CPU micro-optimization; R deliberately chose ordered
incoming scheduling for deterministic accumulation; S established retained
state/lifecycle; T certified EQ-B; U required synthetic-first measurement.

V JSON confirms 20 CPU-faster / zero GPU-faster paired positions per case for
both T5 and T6: totals **80/80 CPU wins**. Each case has 26 initial/chunk
comparisons, zero exact discrete mismatches, zero observed voltage/conductance/
pending-weight error and finite floats. Frozen rtol=atol=2e-13 retained.
Two independent A/B 240-ms trajectories each contain two warmups and ten
measured calls; 24 aggregate calls do not describe continuous 480-ms dynamics.

S4 T6 CPU mean **421.1778399985633 ms**, GPU mean **689.0900150006928 ms**;
T5 means **420.906895 / 688.810785 ms** (rounded). GPU T6-T5 means S1-S4:
**0.195490, 0.197625, 0.204465, 0.279230 ms**. Ordinary outer wrapper work
does not explain the regression inside synchronized public advance.

V's first incomplete attempt stopped on unsafe optional-field object-array
serialization after S1 GPU warmup 1. Safe JSON scalar encoding and its round-trip
test preceded a complete matrix restart. No partial timings enter the completed
results; earlier work could populate disk kernel cache. Static harness inspection
confirms pack before T5, production advance inside T5, readouts/bookkeeping inside
T6, and snapshots/comparison/memory sampling outside both. `git diff` from V's
starting `2d20bbb4d707e5343e24c382b491e9ec8ef7df20` to current HEAD under `src`
is empty; V's four-file commit contains harness/test/report/evidence only.
No production CPU/GPU changes during V.

S4 static pool used **354,022,912 B**, initialized-state used **386,128,384 B**,
minimum sampled device-free **10.603 GiB**; reserved maximum **393,326,080 B**.
Preserve **VRAM-B**: capacity did not limit this result. Boundary samples/pool
reservation do not establish true within-call native peak.

One factual qualification: the task calls S4 count-matched full scale, but U
explicitly records A019L N=166,700/E=24,904,953, and V explicitly notes the
difference. S4 is N=127,400/E=14,687,178, 948 events, synthetic topology. It
matches the requested S4 counts, not the committed A019L projection counts.
This discrepancy does not contradict V-C or supply positive GPU benefit; do
not silently treat S4 as an exact full-real count/identity match.

## Scale trend

Calculated from unrounded committed T6 means, GPU/CPU orientation:

| Case | N / E | GPU/CPU latency ratio |
|---|---:|---:|
| S1 | 128 / 1,024 | 39.475519x |
| S2 | 4,096 / 32,768 | 37.184461x |
| S3 | 32,768 / 262,144 | 7.785090x |
| S4 | 127,400 / 14,687,178 | 1.636102x |

Yes, relative performance improves across this matrix. S4 remains materially
slower: approximately 63.61% greater latency. GPU absolute means are not monotone
(S2 exceeds S3), and size, degree and activity are not independently controlled.
Four heterogeneous fixtures cannot justify a fitted/extrapolated crossover.
No extrapolation beyond S4 is justified. The large requested-count S4 result
materially reduces the value of consuming a real attempt, even with the count
qualification above; it does not predict the exact real latency ratio.

## Static certified GPU hot path

Authority: [cuda.py](../../src/malecns_sim/dynamics/cuda.py),
`GPUPreparedRuntime.advance/_advance_device` and `_ORDERED_SCHEDULE_SOURCE`;
[lif.py](../../src/malecns_sim/dynamics/lif.py), CPU `PreparedRuntime.advance`;
[V harness](../../scripts/benchmark_application_a019v.py). Legacy
`simulate_cuda_batch/schedule_active_edges` is a different, atomic path and is
not the certified V advance scheduler.

One 20-ms call at dt=0.1 ms executes **200 Python-loop timesteps**, under a
runtime lock on one explicit nonblocking stream. Host admission/unique-count
packing happens once per call. Compact event positions/multiplicities upload
once per occupied bin before the loop. No Python edge traversal on this path.

| Region | Per-step structure |
|---|---|
| Admission | Deadline comparison and Boolean OR; event-bin conditional gathers, compaction, integer-to-float conversion, multiplication and indexed voltage addition |
| Pending ring | View slot k%R, masked g/due gather and addition/writeback, integer delivered sum/update, two fills clearing weights/counts |
| Membrane | Six separate ordered subtract/multiply/add ufunc calls using two per-call scratch arrays; masked v/g gathers and writebacks |
| Spike | Threshold comparison/AND, flatnonzero dynamic compaction, host-visible size branch, optional per-spiking-step position/time arrays; two masked resets and deadline assignment |
| Propagation | One ordered RawKernel launch with 256 threads/block, one thread/target scanning its incoming list; queued-by-target integer reduction and counter update |
| Optional traces | Two indexed gathers/writebacks each step; absent in V |

The always-present path has six integration ufuncs, two reductions and two
counter updates, two fills, four mask expressions, one dynamic flatnonzero,
several masked gathers/writebacks/reset assignments and one RawKernel call:
roughly **25-35 source-level device operations per step**, or **5,000-7,000
per 20-ms call**, plus event/spike-dependent work. This is an approximate source
operation count, not a measured kernel count: indexing/compaction/reductions
can launch multiple kernels; implementation fusion/backend details are unknown.
Exactly **200 ordered RawKernel invocations** occur for nonempty V fixtures.
Arrays are length N (128 on S1 through 127,400 on S4), not edge-sized for ordinary
elementwise work. No CUDA graph replay, whole-step fusion or multi-stream overlap
appears in this loop.

Explicit synchronization is after public device work/materialization; construction,
initialization and close also synchronize outside measured advances. No explicit
per-step stream synchronization or `.item()`/`int(device_scalar)` appears.
Boolean indexing and flatnonzero dynamically size arrays; their internal count
reads may synchronize. `positions.size` is host shape metadata, not itself an
explicit device scalar read, but obtaining that shape may require completion.
Exact hidden-wait count is not established by repository text. End-of-call
`cp.asnumpy` materializes spikes/times and two one-element counters; optional
traces are absent in V. These transfers synchronize as needed before the final
stream completion boundary.

Ordered RawKernel object/compile is runtime construction work, reused by all
calls. CuPy-generated operation kernels may compile lazily and use cache;
source contains no repeated explicit compilation inside advance.

## Hypothesis dispositions

**GPU-H1: repeated per-timestep Python/CuPy dispatch and kernel-launch overhead
dominates a substantial part of the 200-step chunk. Support: MODERATE for the
causal hypothesis; STRONG for the structural many-operation premise.** Thousands
of operations on S1's 128 elements accompany 395.746-ms public latency, with
only 1,024 edges. GPU means stay in hundreds of milliseconds over very different
scales while CPU means grow markedly. This is consistent with a large fixed
per-step execution/dispatch floor, including compaction-related waits. It is
not proof of dominance: device indexing costs, background load and other kernels
remain alternatives. Profiling can directly falsify H1 if device execution,
especially ordered propagation, occupies nearly all critical-path time and host
dispatch gaps/short-kernel launch costs are small.

**Propagation hypothesis: MODERATE.** Certified scheduling is neither atomic
scatter nor CuPy add.at/segmented reduction. One custom kernel uses one writer
per target, serial ordered incoming-edge traversal, conditional weight gathering
through ordinals and dense ring/queued writes. Every incoming edge is inspected
every step even if no sources fire: S4 entails **2,937,435,600 edge-condition
visits per call**. CPU schedules only outgoing rows of fired nonsilenced sources.
That precise inactive-edge scan and per-target serial chain are plausible costs;
degree skew can introduce load imbalance, and indirect reads can affect locality.
14.7M edges provide substantial total inspection work but do not guarantee
efficient parallel active propagation. No measured kernel share or bandwidth
exists. This remains an alternative explanation, not a second proposed task.

**Allocation/temporary hypothesis: MODERATE for recurring cost, WEAK for
dominance.** Persistent graph and five state arrays retain pointers. Per-call
masks, two integration scratch buffers and queued arrays total about 26N+16 B
(S4 3,312,416 B), plus compact events and optional traces. Per-step allowed/fired
masks, masked gathers/compaction, reduction scratch and variable spike buffers
are temporary arrays; scratch v/g are reused through all 200 steps. No per-step
E-sized allocation or graph/state recreation appears. The pool can reuse storage
but does not remove allocation bookkeeping, compaction, launches or data movement.
Ample VRAM disproves a capacity explanation, not temporary execution cost.

**Transfer/synchronization: PLAUSIBLE SECONDARY COST.** Ordinary event uploads
are small: at most 16 bytes per unique bin/target pair, bounded by 948 events
over the entire S4 trajectory (15,168 B before masks/metadata). Output readback
is variable spike positions/times plus 16 counter bytes; no full dynamic state
or traces in V. Full int64[N] spike_counts is constructed on the host with
`np.bincount`, not transferred from the device. Output density still matters;
not every call's D2H is assumed tiny. Final synchronization primarily exposes
unfinished work and is required by public semantics. Hidden per-step waits are
plausible contributors to H1, with magnitude unknown. T6-T5 only excludes the
outer wrapper as primary; it does not isolate transfers already inside T5.
Do not remove required synchronization or output semantics.

## Warmup and residual uncertainty

**Warmup contamination: POSSIBLE RESIDUAL**, not material uncertainty invalidating
G4. S2 warmup A1=5.388857 s, A2=0.588763 s; its measured GPU T6 range is
0.577758-0.639286 s, A/B means 0.609934/0.616427 s. S4 measured range
0.673756-0.699086 s, A/B 0.691486/0.686694 s. No warmup-scale measured spike
appears. S1 range 0.348393-0.510172 s, A/B 0.351132/0.440359 s; S3 range
0.423137-0.659508 s, A/B 0.515226/0.622228 s. Later increases do not look like
a simple decaying first-call anomaly, but source/evidence cannot exclude delayed
specialization or other first-use effects. All variability retained; background
load and incidental compileall were uncontrolled. No stationarity claim or rerun.

Real topology/activity could alter degree skew, locality, firing density,
serial incoming-list imbalance and CPU active-edge work differently. No Q-V
committed controlled topology comparison demonstrates a beneficial effect for
the current certified architecture. Count mismatch adds uncertainty, not evidence
of a crossover. This uncertainty is insufficient to spend real data after 80/80
wins and S4 regression. A real run could answer its particular topology's latency,
but source-local synthetic profiling can answer H1 more cheaply without source
access, preparation or full-real comparison/supervision adapter work.
**Full-real attempt remains NOT JUSTIFIED.**

## Pause versus profile scorecard and diagnostic value

| Dimension | A: pause all GPU performance work now | B: one H1 diagnostic |
|---|---|---|
| Existing evidence | HIGH for current regression; MEDIUM for closing research | MEDIUM for causal H1; HIGH for many-operation premise |
| Information value | LOW additional causal information | HIGH |
| Engineering cost | LOW | MEDIUM |
| Risk of speculative optimization loop | LOW | LOW if evidence-only stop enforced |
| Probability next task changes direction | UNKNOWN | UNKNOWN |
| Need for real data | NO | NO |

All six diagnostic-value conditions hold: (1) H1 names the visible 200-step
dispatch structure; (2) tiny S1's hundreds-of-ms latency plausibly leaves a large
dispatch/short-operation floor; (3) host/device timeline and kernel duration/count
evidence can confirm/refute that critical-path explanation; (4) existing generated
fixtures suffice; (5) a dominant fixed dispatch floor would make architecture
research more concrete, whereas its absence weakens that investment premise;
(6) obtaining evidence requires no production optimization.

X should freeze a bounded synthetic observation protocol before execution, using
the unchanged certified advance and existing fixtures. Its single target is H1:
attribute host launch/dispatch gaps, short-kernel trains and compaction-induced
waits on the critical path of the 200-step call. Report ordered-kernel durations
only as the competing attribution needed to refute H1, not a broad search for
optimization opportunities. CUDA event timing alone cannot establish Python
dispatch gaps; a suitable bounded host/device timeline may be necessary.
Retain synchronized public semantics and separate profiler overhead from V's
historical wall timing. No tuning, kernel fusion, stream/block changes, new
real fixtures or automatic optimization follow-up. Failure to establish a large
H1 contribution should support pausing this architecture-investment line;
confirmation justifies a later evidence-only architecture feasibility decision,
not an assumed speedup. A019W itself runs none of these tools.

## Boundaries, validation and custody

Allowed conclusion: A019V demonstrated consistent synthetic regression for the
current EQ-B-certified GPU implementation, including requested-count S4 with
GPU public-call mean about 1.636x CPU. No claim that GPUs are generally unsuitable,
RTX 3060 cannot accelerate another architecture, full-real has this exact ratio,
dispatch is proven dominant, optimization cannot succeed, or CPU is realtime.
No universal correctness, biological implication or full-real readiness claim.

GPU runs=0; CPU runs=0; profiler runs=0; synthetic timing runs=0;
CUDA/CuPy preflights=0; full-real preparations=0; real advances=0;
A019D/A019L reruns=0; registered payload reads=0;
Arena/interventions/downloads/archive writes=0; implementation optimization=0;
kernel/block/stream tuning=0; tags/releases/version bumps=0.
These are performed-command-scope counters, not independently instrumented
native telemetry or a newly certified firewall. Only named committed text/JSON
and memory guidance were read; no production module was imported.

Documentation-only change. `git diff --check`: PASS. No tests/compileall needed
or executed. Commit only this report, push origin master, verify local/origin/live
equality, clean worktree/staging, empty stash, version 0.3.0 and workflows 0.
Containing commit and final identity are reported externally to avoid self-reference.
