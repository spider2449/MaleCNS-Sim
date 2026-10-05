# Application A019A — Stateful Benchmark Contract Adjudication

## Authorization, start gate and disposition

Authorized: 授權 A019A, contract/evidence adjudication only. Repository root derived
with `git rev-parse --show-toplevel`: D:/spider/working/MaleCNS-Sim.
Starting local HEAD = origin/master = live GitHub master =
`0fee2dfdddbfaac37bb5970ab6b73c3fbcc686e4`; clean worktree, empty stash,
version 0.3.0, zero tracked workflows. Prior A018UJ plan establishes A18UJ-A / R-A
and superseding A018UR-IDENTITY-ADJUDICATED-CERTIFIED.

Stopped A019 disposition supplied with this authorization: A19-F — BENCHMARK
CONTRACT OR METHOD INVALID. Its requested single 24-call, 480-ms trajectory
conflicts with A013. That stopped attempt had zero full-real source accesses,
preparations, advances, file changes and commits. A019A does not execute A019B.

**Verdict: A19A-A — A013 BENCHMARK CONTRACT RESOLVED; TWO-STATE EXECUTION
CONTRACT FROZEN. C1 — A013 explicitly requires two independent 240-ms states.**

## Authority and reconstruction

Inspected in priority order: tracked A013 plan
`docs/plans/2026-10-05-application-a013-real-stateful-advance-benchmark.md`, tracked
`scripts/benchmark_application_a013.py`, the frozen report embedded in that plan,
`tests/test_application_a013.py`, then A018UJ identity references. `git ls-files
'*a013*'` lists those three A013 files; no separately tracked A013 evidence JSON
exists. Ignored evidence and raw sources were not accessed.

Plan and harness agree on execution structure, workload, timing and lifetimes.
The current tracked harness incorporates later watchdog and identity repairs;
this adjudication distinguishes those from the originally reported failed
preparation. A013 historical real execution attempted one preparation, completed
none, and constructed no real state or real advancement. The contract below is
intended behavior, not a claim that replay was measured on real data.

Exact structure is option A with a precise distinction: one preparation yields
one PreparedNetwork; worker constructs **one PreparedRuntime** from its projection;
`run_sequences` constructs **two independent SimulationState objects** via that
same runtime's `initial_state()`. There are not two PreparedRuntime objects.
`prepare_once` budgets one `engine.prepare(files, 'cpu_reference')` call. Worker
then calls `PreparedRuntime(prepared.projection, dt_ms=DT_MS)` once and passes it
into `run_sequences`; the `for sequence in ('A', 'B')` loop calls
`runtime.initial_state()` separately for each sequence. Neither state derives
from the other. No reset, clone or copy of terminal state is used. The prepared
projection is reused and remains resident throughout.

## State contracts, schedule and purpose

Both states start at timestep 0 (0 ms), with membrane voltage -52 mV, synaptic
voltage zero, refractory-until -1, and both pending rings zero. Initialization
uses deterministic fresh NumPy allocations, no RNG. The real-size intended rings
are (19, 166700). Dummy position resets to (0.5, 0.5), heading zero.

| State | Construction | Warmups | Measured | Total calls | Call duration | Final horizon |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A | same runtime.initial_state(), fresh | 2 | 10 | 12 | 20 ms | 240 ms / timestep 2400 |
| B | same runtime.initial_state(), fresh | 2 | 10 | 12 | 20 ms | 240 ms / timestep 2400 |

Warmup state continues into measured intervals within each state. Total benchmark
calls = 24, maximum consecutive calls within one state = 12. A single continuous
480-ms trajectory is not part of A013 and is not permitted by this forward
contract. The sum of independent horizons is not one simulated trajectory.

The schedule targets the fixture's numerically sorted **42 LEFT sugar neurons**,
RIGHT count/rate zero, LEFT 100 Hz, seed 1555062870, impulse 68.75 mV
(0.275 mV times factor 250), refractory-free LEFT direct input, horizon 240 ms.
Frozen realization: 948 events, canonical integer-pair payload 15168 bytes,
identity `6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a`.
The JSON record includes the complete 42-member list.

`freeze_schedule` invokes PoissonStimulus.generate(240, 0.1, 0.275) once before
preparation/advancement; its local default_rng is initialized once from the seed.
No RNG regeneration/reset occurs between A/B. Event times are exactly the
seeded per-neuron grid realization: steps with rng.random(2400) < 0.01, times
step*0.1 ms. The schedule identity binds all times and neurons. Twelve frozen
integer slices use [200*k, 200*(k+1)); local times subtract 200*k then multiply
by 0.1 ms. Both states reuse the very same immutable windows. ExplicitStimulus
objects are freshly repacked per call, so identity/content is identical, not
Python object identity for each packed stimulus. Input-only regeneration from
tracked metadata is tested without source access or real network construction.

A/B purpose **is explicitly documented**: exact deterministic replay, including
pending-state replay, and separate plus pooled timing distributions. B's initial
state digests must match A's. Every corresponding interval compares exact state
component digests, timestep, input digest, full output counts/spike IDs/times,
targeted readout counts, pending summaries and dummy geometry. First differing
component stops execution without tolerance relaxation. Readouts are counts for
10331/16949; silence is allowed. No monolithic real comparison is performed.

## Timing, memory and ownership

perf_counter_ns brackets encode, advance, readout, decoder, environment, and total.
Frozen schedule generation and integer slicing are outside timers. Repacking
ExplicitStimulus from the slice is inside encode/total. Advance timing includes
the complete existing advance call, internal validation/fingerprinting/packing
and output assembly. Selecting two readout counts is outside advance but inside
readout/total; scalar threshold decoding and clamped x update have separate
stages. Heavy output processing (digests, scans, conservation checks, replay
comparison), memory snapshots, file writes and console formatting are outside
stage timers. Total spans all five contiguous stages and timer bookkeeping.
Warmup calls are timed and recorded but excluded from measured statistics.
p50/p95 use numpy.percentile(method='linear'); per-state and pooled raw samples,
min/mean/max and total_seconds/0.020 realtime factors are retained.

Preparation timeout 600 s includes opaque graph loading; advance timeout 30 s
per call; whole worker timeout 1500 s includes instrumentation/checkpoints.
External advance phase starts before encode and changes to verification after
all five stages, so watchdog phase accounting includes those surrounding stages;
completed-call advance duration is also checked separately. No retry.

Working set and private bytes each have an 8589934592-byte cap over preparation
and both sequences, with >=12884901888 available physical bytes before preparation.
Current supervisor monitors aggregate contained process-tree memory every 100 ms;
transient between-sample peaks cannot be fully intercepted. Original A013 failed
to monitor redirected worker memory correctly; its report remains immutable.
Samples occur pre-load, pre-preparation, post-preparation, after each initial
state, after every advance boundary and finally, plus concurrent external
samples/phase peaks. Opaque preparation has no post-load callback, so post-load
memory is not separately measurable. External sampler contention is a timing
limitation. Retained summary cap is 1 MiB; full outputs cap 1000000 spikes/call.
All existing finite/pending bounds, conservation and divergence stops remain.

Lifetime: prepared network/projection -> one runtime -> state A -> twelve calls
(each raw result deleted after evidence extraction) -> `del state` -> state B
fresh allocation -> twelve calls -> `del state`. State A is released before B;
A/B state arrays do not coexist in the harness. A digest/reference summaries,
timing rows and fixed inputs remain for B comparison. Prepared graph/runtime
remain resident. Results are not retained as raw buffers. The synthetic regression
uses weak references to prove A arrays are released before B initialization and
checks B's zero-time fresh arrays and initial digest against A.

## Frozen future A019B contract

Exact next task: **A019B — Full-Real Stateful Advance Benchmark Execution**.
Recommended as the corrected next benchmark task, subject to separate explicit
execution authorization. A019A grants none. Maximum one preparation/no retry,
one prepared graph, one runtime, two fresh states in A/B order, exact schedule
above, 2 warmups + 10 measured 20-ms calls/state, 240 ms/state, 24 aggregate calls,
12 consecutive/state. CPU reference only; no Arena, GPU, download or experiment.
Preserve all A013 timing/resource/output/pending/replay guards and exact input.

Use the certified optimized preparation path from A018UR with unchanged expected
identities adjudicated in A018UJ. Preserve 600-s preparation, 30-s advance,
1500-s whole-worker, 8-GiB process-tree memory and 12-GiB available-memory gates.
Require `preparation-identity-v1` and corrected like-layer G1–G6:
G1 dataset provenance, G2 preparation config, G3 unsigned graph, G4 effective
projection, G5 prepared-network envelope, G6 neuron/edge counts. Exact expected
values remain authoritative in the unchanged A018UJ identity JSON. Do not revive
cross-layer comparisons or alter identities, constants or scientific semantics.
Preparation certification does not certify real advancement performance.

Machine-readable record:
`docs/plans/2026-10-05-application-a019a-benchmark-contract.json`, schema
`application-stateful-benchmark-v1`. It is inert metadata, not an execution path.
No production code/default changed; historical A013 plan/harness/tests unchanged.

## Firewall and validation

A019A full-real source accesses/preparations/advances = 0/0/0. Real Arena,
real scientific experiments, GPU, downloads, Task017 new units, Task017Q, archive
writes and BANC = 0. Historical Task016 unchanged; Task017 unchanged / NOT_ROBUST;
B archive unchanged. No biological interpretation. No tag/release/version change.
Only this plan, forward JSON and synthetic A019A test are changed.

Validation results and publication closure are appended after checks complete.

A/B comparison is an exact replay gate, not a statistical A-versus-B speed
hypothesis test. Timing distributions are reported per sequence and pooled;
there is no A/B performance-equality threshold in the harness.

## Validation and publication closure

Final A019A targeted tests: **4 passed**. Requested combined targeted regressions
(with the initial three A019A tests): **857 passed in 129.46 s**. Full pytest
includes the final four-test A019A suite and all application/stateful regressions:
**1226 passed, 14 skipped in 185.25 s**. One expected Feather V1 deprecation
warning comes from the A016 rejection fixture. Skips: 11 unavailable CuPy/CUDA
cases, one disabled opt-in full-real graph gate, and two unavailable CUDA cases.
No opt-in real-data gate was enabled.

| Suite | Passed in full run |
| --- | ---: |
| A019A | 4 |
| A018UJ | 13 |
| A018UI | 11 |
| A018UR | 8 |
| A018U | 80 |
| A018T | 283 |
| A018S | 95 |
| A018 | 97 |
| A017 | 79 |
| A016 | 68 |
| A015 | 59 |
| A014 | 12 |
| A013 | 17 |
| A011 / reference LIF | 8 / 24 |
| All application test modules (including A019A) | 979 |

`uv run python -m compileall -q src scripts tests`: PASS.
`uv run python scripts/check_tracked_integrity.py`: PASS, nine tracked files and
internal identities. `git diff --check` and staged diff check: PASS.
`uv build`: PASS, 0.3.0 wheel and sdist. Scope verification against starting SHA:
production src/scripts, scientific artifacts/data, package version and historical
A013 plan/tests unchanged. Only the three new A019A files are staged.

Commit message: `docs: adjudicate stateful benchmark contract`; publish with
`git push origin master`. Exact resulting SHA and final local/origin/live equality
are reported in the external final response, avoiding a self-referential SHA.
No tag, release or version bump. A019B is recommended only with separate explicit
real-execution authorization; it has not been executed.
