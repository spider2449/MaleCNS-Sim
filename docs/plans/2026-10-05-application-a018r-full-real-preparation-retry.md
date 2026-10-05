# Application A018R — full-real bounded preparation retry

## Preregistration (written before real execution; immutable parameters)

Explicit user authorization: **授權 A018R**. Exactly one bounded full-real CPU
preparation attempt is authorized, with zero stateful advances and no retry.
Root dynamically derived using `git rev-parse --show-toplevel`:
`D:/spider/working/MaleCNS-Sim`. Starting local HEAD, origin/master and live
GitHub master all equal `9f6770aaed9e292a3c25b9897dd89899f4712c5a`.
Initial worktree clean, stash empty, package 0.3.0, tracked workflows zero.

Tracked A015, A016, A017 and A018 reports and their existing implementations
were read. A018 records **A18-A — BOUNDED MULTI-STAGE MERGE CERTIFIED;
FULL-SCALE MODEL SUPPORTS REAL RETRY PROPOSAL**, **P1 — resident-memory model
only**. A018 full-real preparations and advances remain zero, production default
unchanged, corrected watchdog **CERTIFIED_SYNTHETIC**.

Historical real preparation evidence: tracked A003R and A004 reports, A013
preregistration, and `tests/fixtures/application-a003r-reference-spec.json`.
Authoritative expected prepared neurons **166700**, effective edges **24904953**,
canonical PreparedNetwork fingerprint/digest
`ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f`.
The existing prepared digest binds unsigned, signed and effective graph identities
and thus canonical neuron/edge ordering. No synthetic triple digest substitutes
for this historical identity. Expected unsigned projection fingerprint:
`fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4`.

Dataset family **MaleCNS-v1.0**; registered manifest
`e3c26d37039625e8a0623a7b6f83cb70d01663c99f8e32d4ffb2d79709b80631`;
official mapping `832d8428c458e59cfff7b52fc257a4ba3fd85fdd6f3ebf47f01e02e218f50269`.
All required files already exist at `data/raw/male-cns/v1.0`; PowerShell
Get-FileHash SHA256 matched the tracked fixture/A013/workbench evidence before
writing this section. No download or alternate weights file is permitted.

| Source | Bytes | Verified SHA256 |
| --- | ---: | --- |
| body-annotations-male-cns-v1.0-minconf-0.5.feather | 14483314 | 2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2 |
| body-neurotransmitters-male-cns-v1.0.feather | 43282834 | 95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621 |
| connectome-weights-male-cns-v1.0-minconf-0.5.feather | 1051241946 | e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1 |

Preparation: ProductionEngine.prepare(files, 'cpu_reference') with **no config
override**, full graph, min_synapses=0, no cache, use_cuda=False. A scoped harness
substitution selects only the existing A018 experimental loader in task008;
all downstream production preparation remains unchanged. Descriptive reference
configuration digest `a14d75e682b5201c022043725cdac945847962ebff64888008673cca7ded6bf9`.
LIF parameters: rest/reset -52 mV, threshold -45 mV, tau membrane 20 ms,
tau synapse 5 ms, refractory 2.2 ms, delay 1.8 ms, anatomical weight 0.275 mV.
Model fingerprint `037ed13cf919f0ef9ddfdb8f1876e7f1e4712a5c6deb1adbba0fc64e230b0d27`.
Sign policy Shiu2024SignPolicy; resolution
MaleCNSV1ConsensusThenPredictedThenCelltype. Runtime construction only,
dt=0.1 ms; no initial state, schedule, stimulus or advance.

Operational architecture: A015 exact early both-endpoint publication membership
using immutable sorted int64 universe, searchsorted and equality; A016 projected
Feather V2/Arrow IPC batches in source order, physical admission maximum **65536
rows**, use_threads=False; A017 np.lexsort local grouping with checked int64
accumulation (bounded numeric limbs for risky sums); A018 two-pass sorted integer
merge, fan-in **2**, adjacent source-order groups at each stage, odd-run carry
without copy. Overflow raises before exceptional reference fallback. Operational
batch/merge parameters do not enter scientific identity.

Hard memory cap **8589934592 bytes (8 GiB)** on either aggregate contained-tree
private bytes or aggregate working set, with unchanged A014 ProcessJob semantics:
launch suspended, assign Job Object, resume, descendants contained without
breakaway, KILL_ON_JOB_CLOSE, fail closed on inventory/accounting errors, terminate
whole job and verify empty inventory. Existing synthetic preflight must pass.
Real watchdog sampling interval 20 ms; observed peaks are sampled lower bounds,
not claims of capturing every transient. Shared working-set pages may count twice.

Hard preparation interval **600 seconds**, perf_counter_ns from immediately before
the scoped full prepare call, including metadata, source/filter/local aggregation,
merge, downstream/sign/CSR/digests and PreparedRuntime construction, through its
return. Identity verification/cleanup follow outside this preparation interval,
still under memory monitoring. A supervisor also imposes a fail-closed startup
and verification liveness timeout of 600 seconds each, without extending the
preparation interval. Once the worker enters full real source access, attempt=1.
No failure, interruption, fallback or instrumentation error permits retry.

Fallback detection: scoped interception of A017's full reference loader and A016
overflow/reference route raises a harness stop before either unbounded route runs;
records exact trigger. Shared scientific fallback behavior is unchanged outside
this harness. Unsupported Feather admission is preparation error, not substitution.

Timing uses low-overhead scoped wrappers around existing function/batch boundaries,
never line tracing inside merge loops. Existing numeric metrics are reused.
Source iteration, endpoint membership, local grouping, merge and downstream phases
are attempted; nested times cannot be summed as disjoint. Watchdog records tree
memory at boundary messages and periodic samples, including active merge progress.
Unavailable stages are reported honestly. No arrays are retained by instrumentation.

Success requires below-cap completion before timeout, no fallback, exact counts,
unsigned identity and prepared digest: **A018R-PREPARATION-CERTIFIED**. Failure uses
exactly one of A018R-DATASET-PROVENANCE-MISMATCH,
A018R-WATCHDOG-PREFLIGHT-FAILED, A018R-EXPECTED-IDENTITY-UNRESOLVED,
A018R-MEMORY-LIMIT, A018R-TIME-LIMIT, A018R-BOUNDED-PATH-FALLBACK,
A018R-GRAPH-IDENTITY-MISMATCH, A018R-PREPARATION-ERROR. No parameter tuning.

A018 model comparison fixed in advance: source ~5.397 MiB including universe;
partials ~0.572–3.394 GiB; active merge <=~1.716 GiB plus fixed overhead;
grouped table ~0.572 GiB; final ownership ~1.740 GiB; modeled envelope
~5.37 GiB plus unproven overhead; planning envelope ~6.37 GiB with explicit
1-GiB allowance. These are planning values, not expected measurements.

Firewall: full-real preparations <=1, completed <=1, stateful advances=0,
simulate_lif calls after preparation=0, PreparedRuntime.advance calls=0,
Arena/behavior/scientific experiments=0, MN9/sugar response unmeasured,
no biological interpretation, downloads=0, Task017 new units=0, Task017Q=0,
archive writes=0, BANC=0, Task016 unchanged, Task017 unchanged / NOT_ROBUST,
B:\MaleCNS-Archive unchanged. No huge prepared artifact/cache retained.
No GPU execution, tag, release or version change. Success recommends only
A019 — Full-Real Stateful Advance Benchmark Resume, requiring separate
authorization. Failure recommends exactly one bounded task based on its stage.

## Execution and validation evidence (append after preregistration)

### Pre-execution synthetic validation and scope audit

Before real execution: A018R **8 passed**; A018 **97**, A017 **79**, A016 **68**,
A015 **59**, A014 **12**, A013 **17**, A011 **8**; combined **348 passed**,
one existing Feather V1 fixture deprecation warning. The final A018R run after
the boundary-accounting adjustment passed all 8 cases. A014 preflight confirms
launcher/worker membership, descendant containment, aggregate accounting,
termination and empty post-termination inventory: **CERTIFIED_SYNTHETIC**.

Synthetic A018R coverage: explicit experimental selection, unchanged/restored
production loader, multiple physical source batches and binary merge, exact
8-GiB/600-s/65536 constants, negative and overflow fallback interception,
identity mismatch rejection, success with advance/initial_state/simulate_lif
patched to reject any call, failure cleanup, external timeout cleanup, prepared
memory capture handshake. Static call audit excludes simulation, schedule
generation and download entry points. Only synthetic inputs were prepared.

Metadata-only real layout verification (no edge payload preparation) confirms
2318 batches, maximum 65536, total 151856684 rows, Feather V2/Arrow IPC,
LZ4_FRAME, metadata V5. REFERENCE_CONFIG digest matches the preregistered value.
The mapping is the existing official_v1_mapping used by production; its registered
identity is from the frozen fixture, not a nonexistent mapping.fingerprint API.

Scope inspected before execution: exactly this report, a new one-shot harness,
and its synthetic tests. No src, existing algorithm, production dispatch, watchdog,
fixture, scientific artifact, package version or workflow changes. Diff check
passes. Real opt-in pytest environment gate is absent. Local/live master still
match starting HEAD. The supervisor rechecks all three hashes before reservation.
Ignored evidence path fixed to
`data/derived/application-a018r/2026-10-05-result.json`; exclusive reservation
prevents reusing it for a second invocation. Full-real attempts so far **0**.

### Frozen real outcome — A018R-TIME-LIMIT

**Bounded stop; preparation not certified.** Exactly **1** full-real attempt,
**0** completed preparations, **0** advances. No retry. Automatic contained-tree
watchdog terminated the job at **600.0037853 s** from the preregistered preparation
start (sampling/termination decision overshoot 0.0037853 s; no grace or cap increase).
This is interrupted wall time, not a completed preparation duration. Worker was
in **sign_construction** when stopped; no PreparedNetwork/PreparedRuntime returned.
No final prepared neuron/edge counts, graph identity, prepared digest, final
resident-state measurement or nonfinite runtime-state check can be reported.
Historical expected identities remain expectations, never measured results.

CPU only. The explicit bounded route used A015 endpoint filtering, A016 physical
65536-row admission, A017 checked int64 local aggregation and A018 fan-in-2
adjacent source-order staged merge. Production default and all certified algorithms
unchanged. Source hashes rechecked by supervisor and matched. Fallback detection
armed throughout; **no fallback event**, no exceptional reference execution,
no negative-endpoint/overflow trigger. No GPU, stimulus, sugar/MN9, state or advance.

Contained launcher **10644**, actual worker **17012**; Job Object inventory and
worker event PIDs verified. Supervisor **7384** is outside the measured worker job;
the contained launcher is included. **28846** periodic/boundary tree samples,
**79** events (including scalar merge progress), 20-ms nominal sample interval.
Aggregate sampled peak private **5464100864 bytes = 5.088840485 GiB**,
working set **4421849088 bytes = 4.118167877 GiB**. These are **63.6105061%**
and **51.4770985%** of the 8-GiB cap. **Memory cap not hit**. Both maxima were
sampled during **downstream_projection_csr**. No claim that unsampled transient
maxima were captured, and no full-preparation memory certificate from a time stop.

#### Stage timing

| Stage | Seconds | Coverage |
| --- | ---: | --- |
| Initial metadata/publication setup to source entry | 2.0502062 | Boundary interval; includes imports/wiring/bookkeeping and annotation load, not pure metadata CPU time |
| Publication universe selector | 0.1605220 | Nested in initial setup |
| Bounded source iteration | 1.7328719 | Iterator next calls; includes final StopIteration, excludes footer admission |
| Endpoint filtering | 7.7130780 | Both exact membership calls; mask conjunction/copy and raw validation not separately timed |
| Local aggregation | 3.7371656 | Scoped local-group calls; inherited metric including call overhead 3.7441228 |
| Partial accumulation | 0.0017392 | Existing A017 metric |
| Source processing overall | 14.7753751 | Source entry to source completion, includes validation/filter/copy/local aggregation |
| Staged merge | 549.3997919 | Complete wrapper interval; inherited merger metric 549.3997795 |
| Production metadata normalization helper | 8.1216501 | Complete reused empty-edge metadata helper |
| Bounded loader total | 574.3467865 | Inclusive; do not add nested stage times |
| Downstream production annotation/evidence setup | 6.1008513 | Loader return to projection entry; boundary interval |
| Downstream projection / anatomical CSR | 7.7788168 | Complete projection call; threshold=0, no separate threshold stage |
| Sign construction | Interrupted | Started at preparation +588.2287435 s; no return |
| Effective weight/outgoing CSR/runtime construction | Not reached | No completed prepared object |
| Total preparation | Interrupted at 600.0037853 | Includes entire bounded and downstream path; no completed duration |

Timing completeness: **partial**, with nested/inclusive times identified. Raw
validation, mask combination, copying and final graph fingerprint are not separate
timers. Sign/weight/final runtime stages cannot be assigned completed durations.
The merge alone consumes ~91.567% of the 600-second budget. Initial partial runs
had **25582938** retained rows and **25582938** partial rows: local compression
**1.0x**. All **2318** physical source batches were traversed; **2313** nonempty
partial runs entered **12** merge stages. Groups by stage:
1156,578,289,145,72,36,18,9,5,2,1,1. Merger read **611578710** logical input-row
visits over two scans and wrote **305789355** rows. These are operational counters,
not neural events. No scalar loop profiling or heavy tracing was added.

#### Stage memory (authoritative contained-tree samples)

Boundary measurements are the first supervisor sample following the worker event;
small message/sampling lag is possible. Stage maxima include all assigned processes
and may include boundary lag, allocator retention, native and metadata allocations.

| Boundary | Private bytes | Working set bytes |
| --- | ---: | ---: |
| Before dataset load | 862220288 | 140013568 |
| After publication universe | 1285922816 | 485515264 |
| Source entry | 993099776 | 196694016 |
| After source processing / before merge | 1609310208 | 809517056 |
| After staged merge / grouped columns | 1661739008 | 813830144 |
| After metadata normalization / loader return | 2434080768 | 1451429888 |
| Downstream projection entry | 2984738816 | 1805324288 |
| Downstream projection return / sign entry | 3406503936 | 2402484224 |
| Final sampled interrupted sign construction | 4113678336 | 3108073472 |
| Prepared graph/runtime / final prepared resident state | Unavailable | Unavailable |

| Observed stage | Peak private bytes | Peak working set bytes |
| --- | ---: | ---: |
| Publication universe | 1296134144 | 495648768 |
| Source batches / local partial accumulation | 1609310208 | 809418752 |
| Staged merge | 2208886784 | 1406943232 |
| Metadata normalization | 3601887232 | 2600882176 |
| Bounded loader-labeled samples | 3789709312 | 2766905344 |
| Downstream projection / anatomical CSR | 5464100864 | 4421849088 |
| Interrupted sign construction | 4274139136 | 3108073472 |

#### A018 model comparison

Observed numeric source-column peak **1572864 bytes**, mask **65536**, retained
chunk/aggregate **1572216** each. These agree with the 65536-row bounded payload
model; ~5.397 MiB includes several modeled owners and universe, not process bytes.
Observed initial partial storage and final grouped table both **613990512 bytes**
(~0.572 GiB), at the low end of A018's 0.572–3.394 GiB partial range. The actual
retained inputs exhibited no duplicate compression in local or global merging.
Maximum active group inputs **613990512**, output **613990512**, coexistence payload
**1227981024 bytes** (~1.144 GiB); within A018's modeled active <=1.716-GiB bound.
Maximum active fan-in=2; completed-next-stage bytes=613990512. The numeric
resident bound including scalar/container allowances was **1232728288 bytes**.

Observed merge process-private peak **2208886784** exceeds maximum modeled numeric
coexistence payload by **980905760 bytes (~0.913540 GiB)**. This comparison of
stage maxima is an **unattributed process-minus-payload difference**, not an exact
same-instant allocation residual. It includes interpreter/metadata/native/allocator
terms and cannot isolate their contributions from this evidence. No new process
overhead bound is proven.

Overall observed private peak **5.088840485 GiB** is approximately **0.28116 GiB
below** the preregistered ~5.37-GiB modeled envelope before unproven overhead,
and ~1.28116 GiB below the ~6.37-GiB planning envelope. That conservative envelope
deliberately overcounts downstream coexistence. It is consistent with observed
incomplete-run memory; it does **not** verify the unvisited final stages or the
~1.740-GiB final-state prediction. Time prediction was never part of P1: measured
merge cost confirms the tracked A018 CPU amplification concern.

#### Evidence custody and cleanup

Ignored original evidence: `data/derived/application-a018r/2026-10-05-result.json`,
**30397239 bytes**, SHA256
`5595dd15ff0f3aaaac00010a24ef6370f34255c186c1c5f038c3693048019f74`.
Contains all tree samples/events, original operational metrics/schedule, hash
verification and stop decision. Executed harness Git blob
`4b8b507875cf3e720514e25ee9bd311be092c6c8`.
The preregistered report plus preflight section was staged before execution as
Git blob `e6428a2372b53643b6b74a4422ae0228f6f880e7`; the result sections only
append to those frozen 146 lines.
Evidence and one-shot reservation retained locally to prevent reuse; no prepared
binary output, persistent graph cache, tracked huge artifact or B: archive write.
No evidence rewriting, tuning or second preparation after observing the stop.

ProcessJob.close terminated the complete contained job, verified empty inventory,
and returned exit code 1 (watchdog termination). Independent post-stop CIM inventory
found **no remaining A018R Python process**. OS teardown releases worker memory
and file handles. Metadata helper returned normally before the stop and removed
its temporary empty Feather. No prepared object exists to reuse for advances.

#### Exactly one next bounded task

Recommend **A018S — Bounded CPU Staged-Merge Time Optimization and Synthetic
Certification**: investigate the observed 549.400-second binary scalar merge,
certify one proposed CPU implementation against existing exact integer/order/
overflow/lifetime/graph contracts on synthetic inputs, and establish a new bounded
preparation-time proposal. Production default remains unchanged. Any new real
preparation requires separate explicit authorization. **Do not execute A018S
automatically.** A019 stateful resume is not recommended from this failed gate.

#### Final scientific firewall

Full-real preparation attempts **1**, completed **0**, stateful advances **0**,
simulate_lif calls after preparation **0**, PreparedRuntime.advance calls **0**,
real Arena **0**, real behavior **0**, real scientific experiments **0**,
MN9/sugar response measured **No**, biological interpretation **No**,
raw-data downloads **0**, Task017 new units **0**, Task017Q **0**, archive writes
**0**, BANC **0**. Historical Task016/Task017 and B archive unchanged;
Task017 remains **NOT_ROBUST**. No GPU, automatic retry, tag, release or version
mutation. These counts refer to full-real execution; ordinary synthetic regressions
exercise their established synthetic simulation fixtures only.

### Post-real validation and publication

Targeted A018R/A018/A017/A016/A015/A014/A013/A011: **348 passed**, one existing
Feather V1 warning, 49.85 s. Individual counts unchanged from preflight:
8/97/79/68/59/12/17/8. Compileall src/scripts/tests PASS; tracked integrity PASS
(9 frozen tracked files/internal identities); unstaged and staged diff checks PASS;
uv build PASS (0.3.0 sdist and wheel). Application selection: **486 passed,
260 deselected**, one existing warning, 101.76 s. Full `uv run pytest -q`:
**732 passed, 14 skipped**, one existing warning, 109.71 s. Skips: 13
unavailable CUDA/device cases and the unenabled full-real Task007c gate.
No full-real pytest gate enabled. No post-real preparation rerun.

Final scope audit: `git diff HEAD -- src artifacts data/provenance pyproject.toml
uv.lock .github` empty. Only the A018R report, harness and synthetic tests change.
Frozen scientific artifacts pass integrity checks. Source hash evidence remains
unchanged after tests. Version 0.3.0, workflows zero, stash empty. Immediately
before publication local/origin/live master still equal starting HEAD.
Authorized publication: commit `perf: record bounded real preparation retry`,
push origin master, then require local/origin/live equality and clean worktree/
empty stash. The exact final commit/push verification is reported in the final
task response to avoid a self-referential report commit hash. No tag/release.
