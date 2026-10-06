# A019V bounded synthetic CPU/GPU performance

Authorization: **授權 A019V**. Starting local/origin/live master:
`2d20bbb4d707e5343e24c382b491e9ec8ef7df20`. Clean worktree/staging/stash;
version 0.3.0; tracked workflows zero.

Frozen before measurement: S1=(128,1024), S2=(4096,32768),
S3=(32768,262144), S4=(127400,14687178). Balanced outgoing degree;
target=(source*17+local_edge*97+1)%N; weights cycle
0.275,-0.1375,0.06875,0.1375. All topology is generated in memory.
S1-S3 use 60 deterministic events spread across 240 ms and eight sources.
S4 uses the existing PoissonStimulus generator, synthetic IDs 1..42,
100 Hz, seed 1555062870, 240 ms, dt=0.1 ms. No forced event count.
Input amplitude 68.75 mV, source refractory exemption, two fixed readouts,
no traces. Order: S1 CPU/GPU; S2 GPU/CPU; S3 CPU/GPU; S4 GPU/CPU.
One runtime per backend/case; A then B released sequentially;
each state has two warmups and ten measured 20-ms advances.

Plan: establish guarded bootstrap; implement narrow generated-fixture harness
and contract tests; run harness and S/T regressions; execute exactly one
complete matrix; compare every initial/chunk state and all result fields
outside timers with frozen EQ-B rtol=atol=2e-13; report raw timing,
statistics, resources and terminal decision; compileall/diff check; commit/push.
No production implementation changes or tuning.

T0 includes synthetic graph and schedule construction. T1/T2 separately time
runtime construction; GPU import/context preflight is separately recorded.
T3 times initial_state. T4 retains all warmups. T5 times public advance
through returned materialized result and its production synchronization.
T6 adds per-call event repacking, two output count readouts and deterministic
ordinary bookkeeping. Snapshot, comparison, disk evidence and memory sampling
are outside T5/T6. First-backend snapshots are held in temporary synthetic
files and removed, avoiding simultaneous A/B mutable states.

Frozen bounds: construction 180 s, each advance 30 s, total 1800 s,
contained host private/working set 8 GiB. Existing Windows Job containment
supervises the worker. Pool used/reserved and memGetInfo observations at
lifecycle boundaries are not true native VRAM peak telemetry. No isolated
H2D/D2H attribution or extra hot-path barriers.

S4 requested counts differ from A019U's larger 166700/24904953 structural
estimate. Compare allocation formulas at their respective scales, without
claiming S4 is the current real projection.

## Completed disposition

**A019V-C — SYNTHETIC GPU PERFORMANCE DOES NOT JUSTIFY FULL-REAL ATTEMPT.**
**G4 — GPU REGRESSION.** All cases pass EQ-B, but GPU is slower at every
paired measured position (80 CPU-faster / 0 GPU-faster), both T5 and T6.
Exactly one next task: **A019W — evidence-only decision on pausing the GPU performance line**.
No full-real execution is authorized or performed.

Machine: Intel Core i9-7900X, 10 cores / 20 logical processors; RTX 3060
12 GiB, compute capability 8.6; driver 581.15, CUDA runtime API 12090,
driver API 13000, CuPy 14.2.0, NumPy 2.5.3.
Python 3.14.0 (main, Nov 19 2025, 22:43:52) [MSC v.1944 64 bit (AMD64)].
Fresh worker import/context preflight: 0.431360 s. Existing disk cache retained.
No CPU/GPU/stimulus production source edits. Source hashes and environment
are retained in [machine evidence](a019v-synthetic-cpu-gpu-performance-evidence.json).

## Public timing results

All times below are milliseconds, mean / median. Ratios are CPU/GPU;
values below 1 mean the GPU is slower. T6 is the primary boundary.

| Case | CPU T5 | GPU T5 | CPU T6 | GPU T6 | T6 mean / median ratio | GPU / CPU faster | Synthetic class |
|---|---:|---:|---:|---:|---:|---:|---|
| S1 | 9.844 / 9.811 | 395.550 / 351.384 | 10.025 / 9.992 | 395.746 / 351.588 | 0.025332 / 0.028419 | 0 / 20 | SYNTHETIC GPU-P2 |
| S2 | 16.306 / 16.162 | 612.983 / 613.427 | 16.490 / 16.340 | 613.180 / 613.620 | 0.026893 / 0.026629 | 0 / 20 | SYNTHETIC GPU-P2 |
| S3 | 72.853 / 72.662 | 568.522 / 603.549 | 73.053 / 72.854 | 568.727 / 603.742 | 0.128451 / 0.120671 | 0 / 20 | SYNTHETIC GPU-P2 |
| S4 | 420.907 / 421.955 | 688.811 / 688.284 | 421.178 / 422.210 | 689.090 / 688.580 | 0.611209 / 0.613160 | 0 / 20 | SYNTHETIC GPU-P2 |

Each backend has 24 calls, four retained warmups and 20 measured calls,
two fresh 240-ms trajectories A then B. All raw T5/T6 values, paired ratios,
min/median/mean/max/p95/population std/CV and A/B means are in JSON.
p95 uses linear interpolation. No outliers removed or slow calls rerun.

## Construction and state initialization

Times in seconds. CPU preparation is only the PreparedRuntime constructor;
the generated immutable projection is already built under T0.

| Case | T0 | CPU T1 | GPU T2 | CPU T3 A / B | GPU T3 A / B |
|---|---:|---:|---:|---:|---:|
| S1 | 0.004074 | 0.000006400 | 0.046148 | 0.000245 / 0.000179 | 0.017047 / 0.000410 |
| S2 | 0.003095 | 0.000006600 | 0.002380 | 0.000254 / 0.000271 | 0.000520 / 0.000599 |
| S3 | 0.020976 | 0.000003800 | 0.014569 | 0.000232 / 0.000289 | 0.005120 / 0.000836 |
| S4 | 1.108611 | 0.000005600 | 1.349245 | 0.000445 / 0.001010 | 0.004513 / 0.000570 |

## Warmup and harness history

The first incomplete attempt stopped after S1 GPU warmup 1 because absent
optional result fields had been serialized as unsafe object arrays.
Its approximately 5.575895-s GPU first advance is diagnostic history only.
After safe JSON scalar encoding and a round-trip test, the entire matrix
restarted. No partial attempt numbers enter the results. It could populate
the disk kernel cache; this is not virgin-cache compilation timing.

| Case | GPU T4 T5 seconds: A1, A2, B1, B2 |
|---|---|
| S1 | 0.503169, 0.355129, 0.352733, 0.352551 |
| S2 | 5.388857, 0.588763, 0.623330, 0.627116 |
| S3 | 0.619294, 0.426768, 0.649644, 0.611487 |
| S4 | 0.846517, 0.714045, 0.684755, 0.687349 |

S2 first warmup is 5.388857 s; its second is 0.588763 s. Remaining
lazy first-use costs are visible and excluded. Exact compilation/context
cost decomposition is unavailable. S1/S3 measured distributions vary and
all variability remains included; no stationarity or significance claim.
Existing interactive background load was not controlled. A brief compileall
ran during the matrix. This limits precision, but every measured CPU call
is faster than its paired GPU call, including S4.

## Equivalence and fixture identity

Every case compares initial state and all 12 chunk boundaries for both A/B:
26 comparisons, shapes/dtypes, timestep, refractory deadlines, pending
counts/bins, canonical spike ordering/multiplicity and every result field.
All discrete mismatches and voltage/conductance/pending-weight errors are
**zero**; floating values finite; frozen rtol=atol=2e-13 unchanged.
No benchmark-only snapshots occur within T5/T6.

| Case | Nodes / edges | Events | Projection SHA256 |
|---|---:|---:|---|
| S1 | 128 / 1024 | 60 | `356f66641e82475ac9682f722d11d9aac28e700786c4307d2cbdbe61e2fac132` |
| S2 | 4096 / 32768 | 60 | `343fd6f091cabfbb7c1fbd4b297825ba6b9c63861c67a9a0d7c5e061ebaddd71` |
| S3 | 32768 / 262144 | 60 | `314b3bb6e1af25f65ebc154df929a5b0b005f230835009b8773302aec302b09e` |
| S4 | 127400 / 14687178 | 948 | `aa03c559d83a266375c149142620f48cf024204abde0dcd2dd17affdc56ee39f` |

S1-S3 schedule identity: `c285702bf6eb084416c925a9223ad889302bc29b5c8b2171b76f70b1a4cb76fb`.
S4 schedule identity: `b85d4c444310aca3c6aa0b5fcfaa0625a17a319c5d6066064356baf9a68885b1`.
All 12 chunk identities/counts retained. No real neuron IDs, topology or
registered connectivity used. Execution order is the preregistered
CPU/GPU, GPU/CPU, CPU/GPU, GPU/CPU.

## Wrapper and transfer analysis

| Case | CPU T6-T5 ms | GPU T6-T5 ms |
|---|---:|---:|
| S1 | 0.180650 | 0.195490 |
| S2 | 0.184300 | 0.197625 |
| S3 | 0.200615 | 0.204465 |
| S4 | 0.270945 | 0.279230 |

Outer packing/readout/bookkeeping is small. The GPU regression is already
present in T5. T5 includes event admission/H2D, device computation, required
D2H/canonical materialization and final synchronization. No individual
transfer/kernel attribution is available; no claim that a particular
substage dominates. Current ordered incoming-edge scan executes every
timestep; source structure is context, not a measured causal breakdown.
No tuning or changed synchronization/output contracts.

## Device and host memory

All lifecycle samples are retained per case. The following are pool
used / reserved bytes; maximum reserved is a caching/high-water proxy,
not true native within-call peak.

| Case | Before | Static | A initial | A released | B initial | B released | Runtime closed | Pool reclaimed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| S1 | 0 / 0 | 27136 / 27136 | 59392 / 59392 | 27136 / 79872 | 59392 / 79872 | 27136 / 79872 | 0 / 79872 | 0 / 0 |
| S2 | 0 / 0 | 836608 / 836608 | 1868800 / 1868800 | 836608 / 2104320 | 1868800 / 2104320 | 836608 / 2104320 | 0 / 2104320 | 0 / 0 |
| S3 | 0 / 0 | 6685696 / 6685696 | 14943232 / 14943232 | 6685696 / 16784384 | 14943232 / 16784384 | 6685696 / 16784384 | 0 / 16784384 | 0 / 0 |
| S4 | 0 / 0 | 354022912 / 354022912 | 386128384 / 386128384 | 354022912 / 393326080 | 386128384 / 393326080 | 354022912 / 393326080 | 0 / 393326080 | 0 / 0 |

S4 max boundary-observed used **386128384 B**; max reserved
**393326080 B (375.105 MiB)**; minimum observed device-free
**11384389632 B (10.603 GiB)**. **VRAM-B**: fits with ample measured
headroom, but true within-call/native peak remains unobserved.
CUDA memGetInfo is device-wide; Windows/WDDM nvidia-smi and CUDA readings
have different scopes. Neither establishes isolated process peak.

S4 graph formula 354021084 B, one state 32104800 B, named call buffers
3312416 B: total **389438300 B (371.397 MiB)**. Observed static plus
state pool bytes exceed that base graph/state formula by only 2500 B.
Pool reservation includes scratch/caching. U's 646061900 B / 616.13 MiB
estimate used larger 166700/24904953 counts and cannot be compared as if
it described this S4. Context/modules and other device users are separate.

Contained host sampled private peak **2395545600 B**; working set peak **1229975552 B**,
over the complete matrix; conservative overall bound for S4, not isolated
native S4 peak. 834 samples at nominal 0.1 s; total wall 84.292 s.
Worker exited 0, Job closed with empty inventory, no orphan. A is released
before B; runtime graph and state pointers remain stable across chunks.
No graph reupload, reset or per-call runtime duplication; runtime close
returns used bytes to zero and explicit post-run pool reclamation returns
reserved bytes to zero. Temporary synthetic snapshots removed.

## Readiness, validation and custody

Harness is trustworthy for these synchronized wall-time measurements.
S4 allocation, completion, equivalence and cleanup pass; scaling narrows
the GPU deficit but never reverses it. No positive public-boundary benefit.
Full-real adapter/identity gates and integrated GPU failure supervision
remain unvalidated. A real performance attempt is low-value on this
evidence; A019W should make the evidence-only pause decision.

Final guarded tests: harness **6**, A019T **33**, A019S **33**, source/read
controls **14**, total **86 PASS**. Guard bootstrap **14 PASS** before
workload. Guarded compileall and git diff --check PASS.
CuPy CUDA_PATH detection warning only; all CUDA execution succeeds.
No second benchmark was run as validation.

Fail-closed guard active before imports and admitted worker execution.
Benchmark log has four activation records (two attempts, parent/worker),
zero denied payload-read events. Seven-category registered payload reads=0;
full-real preparations=0; real advances=0; A019D/A019L reruns=0;
Arena/interventions/downloads/archive writes=0. These are guarded-scope
counters, not independent native-byte telemetry. No full-real speedup,
full-real realtime, biological realtime, exact A019L ratio or scientific
implications claimed. Version remains 0.3.0; no workflows/tag/release.
Containing commit and final local/origin/live custody reported externally
to avoid self-reference.
