# Application A018UR — full-real bounded preparation retry

## Preregistration (written before real execution; immutable parameters)

Explicit user authorization: **授權 A018UR**. Exactly one bounded full-real CPU
preparation attempt is authorized, with zero stateful advances and no retry.
Root dynamically derived using `git rev-parse --show-toplevel`:
`D:/spider/working/MaleCNS-Sim`. Starting local HEAD, origin/master and live
GitHub master all equal `9198ef6ab552b5d2327d7e960de7961b4d92b603`.
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
substitution selects the existing A018 staged loader with the A018T certified merger in task008;
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
accumulation (bounded numeric limbs for risky sums); A018T bounded blockwise NumPy two-key
merge with fixed block size 16384, fan-in **2**, adjacent source-order groups at each stage, odd-run carry
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
unsigned identity and prepared digest: **A018UR-PREPARATION-CERTIFIED**. Failure uses
exactly one of A018UR-DATASET-PROVENANCE-MISMATCH,
A018UR-WATCHDOG-PREFLIGHT-FAILED, A018UR-EXPECTED-IDENTITY-UNRESOLVED,
A018UR-MEMORY-LIMIT, A018UR-TIME-LIMIT, A018UR-BOUNDED-PATH-FALLBACK,
A018UR-GRAPH-IDENTITY-MISMATCH, A018UR-PREPARATION-ERROR. No parameter tuning.

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

## Additional frozen A018UR operational evidence

A018R/T/U tracked reports read; A018R-TIME-LIMIT preserved: exactly one previous
attempt, incomplete, merge 549.3997919 s, stop 600.0037853 s, private peak
5464100864 bytes, working-set peak 4421849088 bytes; no memory breach,
fallback or advances. A018U records A18U-A/U1. Memory P1 preserved.
A018T block size 16384, fan-in 2, adjacent source-order schedule unchanged;
checked int64 sums, canonical pre/post ordering, global-only threshold,
no per-edge Python merge objects and no unbounded global concatenate.
A018U adds no optimization: existing production downstream stays authoritative.
Frozen merge models: simple 28.983115 s; throughput 21.952660 s; stress
57.966230 s. Frozen total models: best ~110 s, conservative ~264 s,
stress ~469 s. Planning private envelope ~6.371953 GiB. Completion under
600 s is plausible with material headroom, not proven before this execution.
Source hashes above verified live before this preregistration. Registered
manifest/mapping/fixture evidence agrees with historical counts/config/digest.
Output: data/derived/application-a018ur/2026-10-05-result.json (ignored).
Exclusive persistent reservation prevents a second invocation. No full graph
artifact or archive write. Existing canonical PreparedNetwork fingerprint used.
Preparation interval includes runtime construction; verification follows while
memory monitoring continues. Sign/CSR/hash timers are inclusive: no heavy probes
added, unavailable substage times must remain unavailable, never inferred as zero.

Pre-run scope: only new report, new harness copied from certified A018R and
new synthetic tests. No src changes, production dispatch changes or watchdog
redesign. Synthetic preflight must pass again after this freeze before execution.

## Pre-execution synthetic preflight and scope inspection

After freezing parameters, A018UR 8 tests and existing A014 12 tests passed
(20 total). Watchdog classification before real execution: CERTIFIED_SYNTHETIC.
Containment, descendants, aggregate memory, termination, accounting failure and
empty cleanup inventory pass. Success rejects advance/initial_state/simulation;
identity mismatch, fallback triggers and timeout cleanup are tested. Optimized
block operations and fixed 128*16384 scratch prove A018T selection. CPU only,
no download entrypoint, unchanged/restored production loader. Diff inspected:
new harness changes only task labels, explicit certified merger/block selection,
strict deadline comparison and scalar provenance reporting. Source algorithms,
production defaults, scientific semantics and existing watchdog are unchanged.
Only the three declared new files exist. Attempts consumed before launch: 0.

## Frozen real outcome: A018UR-GRAPH-IDENTITY-MISMATCH

Verdict: bounded completed preparation, NOT certified. Exactly one attempt; no retry.
Preparation completed in 101.3569613 s; 600-s cap not hit. CPU only, production default unchanged.
No fallback event/trigger. All three source hashes rechecked by supervisor and matched.
Expected neuron/edge counts 166700/24904953 exactly match. Unsigned digest exactly matches.
Expected prepared digest: ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f.
Observed canonical prepared digest: d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495.
Digest match: NO. Scientific graph/preparation identity certified: NO. No equivalence substitution.
Config identity exactly matches a14d75e682b5201c022043725cdac945847962ebff64888008673cca7ded6bf9.
Registered manifest/mapping and Shiu2024SignPolicy/MaleCNSV1ConsensusThenPredictedThenCelltype match.
Finite effective/outgoing weights: true; no preparation exception or instrumentation error.
No runtime state created; nonfinite state is therefore not applicable.

### Stage timing

| Instrumented interval | Seconds |
|---|---:|
| publication_universe | 0.168241200 |
| source_iteration | 1.785816200 |
| endpoint_membership | 7.921831000 |
| local_aggregation | 3.810391300 |
| staged_merge | 26.881418300 |
| metadata_normalization | 8.232258400 |
| bounded_loader | 52.127387700 |
| downstream_projection_csr | 8.290157900 |
| sign_construction | 14.953194900 |
| effective_weights_outgoing_csr | 16.738436600 |
| Total preparation | 101.356961300 |
Timing completeness: partial decomposition, complete total. Sign construction includes anatomical CSR/unsigned hashing; effective weights includes outgoing CSR and signed/effective hashes. Digest/identity and runtime/finalization cannot be separated without adding probes.
Top-level unexplained timer residual = total minus bounded loader, projection, sign and effective/outgoing = 9.247784199999998 s; includes annotation/evidence setup, PreparedNetwork digest, runtime construction and wiring. Nested source/filter/group/merge timers must not be added to loader total.
Source processing boundary interval 15.1548503 s; endpoint timer excludes mask conjunction/copies/raw validation. Publication-universe timer is nested in initial setup.

### Sampled contained-tree memory

Peak private 5478465536 bytes (5.102218628 GiB; 63.777732849% of cap).
Peak working set 4465192960 bytes (4.158535004 GiB; 51.981687546% of cap).
8-GiB cap not hit. Both highest observed samples: effective_weights_outgoing_csr. Sampled operational evidence only; no unsampled instantaneous maximum claim.
| Stage label | Peak private bytes | Peak working set bytes |
|---|---:|---:|
| startup | 722255872 | 109953024 |
| before_dataset_load | 731201536 | 112259072 |
| bounded_loader | 3797716992 | 2771263488 |
| publication_universe | 1302409216 | 495927296 |
| source_batches | 1616556032 | 811503616 |
| source_processing | 1619972096 | 811843584 |
| staged_merge | 2219630592 | 1412325376 |
| metadata_normalization | 3606511616 | 2598252544 |
| downstream_projection_csr | 5469442048 | 4425830400 |
| sign_construction | 4833951744 | 3822145536 |
| effective_weights_outgoing_csr | 5478465536 | 4465192960 |
| prepared_resident | 4021874688 | 3007582208 |
| released | 1440043008 | 434024448 |
Prepared-resident stage sampled before release; boundary/stage labeling may lag events.

### Frozen model comparison

A018R private peak 5.088840485 GiB / working set 4.118167877 GiB, merge 549.399792 s; historical records unchanged.
| Merge model | Frozen seconds | Observed-minus-model % |
|---|---:|---:|
| simple | 28.983115 | -7.251452 |
| throughput | 21.95266 | 22.451759 |
| stress | 57.96623 | -53.625726 |
Real merge 26.8814183 s, 20.437902x faster than historical baseline. Closest merge branch: simple; residual -2.101696700 s.
| Total model | Frozen seconds | Observed-minus-model % |
|---|---:|---:|
| best | ~110 | -7.857308 |
| conservative | ~264 | -61.607212 |
| stress | ~469 | -78.388708 |
Closest requested total branch: best estimate; residual -8.643038700 s. Optional historical throughput-sensitivity ~102 s is closer, but the requested best/conservative/stress models remain frozen.
Private peak-minus-planning-envelope (~6.371953 GiB): -1.269734372 GiB. This unattributed model residual does not isolate allocator/native/metadata contributions or same-instant owners.

### Evidence custody and cleanup

Ignored evidence data/derived/application-a018ur/2026-10-05-result.json, 4905160 bytes, SHA256 44fb24c79ae0fa1ed751e7e39e040018e47009300a86151dec3d27f4a0dfe647; 4923 memory samples, 25 events.
Preregistered staged report blob: bd6ae5ed7a66d10bf7fd15318a9efa7f7ccf2767 (153 lines; result appended).
Prepared/runtime references released, gc collected, cleanup event observed. ProcessJob.close terminates contained tree and verifies empty inventory; orphans=[]; exit code 1 is expected job termination of parked worker after result, not preparation crash. Independent CIM inventory: no remaining A018UR Python process.
No prepared object persisted or reused. Local reservation/evidence retained; no archive writes.

### Exactly one next task

Recommend A018UI ? Exact Prepared-Identity Root-Cause Audit: read-only audit of historical canonical prepared identity versus optimized-route provenance/identity framing, using tracked evidence and synthetic fixtures. No full-real retry, no weaker digest, no advance. Separate authorization required. A019 is not recommended because A018UR certification failed.

### Scientific and archive firewall

Full-real preparations=1; advances=0; PreparedRuntime.advance=0; simulate_lif=0; simulate_cuda=0; Arena/behavior/scientific runs=0; MN9/sugar unmeasured; biological interpretation=none; downloads=0; Task017 new units=0; Task017Q=0; archive writes=0; BANC=0. Task016/Task017 unchanged; Task017 NOT_ROBUST; B archive untouched. No tag/release/version mutation.

### Memory at meaningful boundaries (first supervisor sample after event)

| Worker boundary | Private bytes | Working set bytes |
|---|---:|---:|
| prepare_start: before_dataset_load | 731201536 | 112259072 |
| boundary: publication_universe | 1292193792 | 485810176 |
| source_access: source_batches | 997130240 | 195596288 |
| boundary: source_processing | 1619972096 | 811843584 |
| boundary: staged_merge | 1671790592 | 817156096 |
| boundary: metadata_normalization | 2444689408 | 1449971712 |
| boundary: bounded_loader | 2444689408 | 1449971712 |
| boundary: downstream_projection_csr | 3408117760 | 2398564352 |
| boundary: sign_construction | 3670937600 | 2661142528 |
| boundary: effective_weights_outgoing_csr | 4880371712 | 3680493568 |
| prepare_done: prepared_resident | 3996913664 | 2985840640 |
| cleanup: released | 1440043008 | 434024448 |
Merge return is grouped-table complete; sign entry follows downstream projection return. Partial accumulation ends at source_processing. Boundary messages and sampling can lag; values are contained-tree samples, not exact instantaneous allocation totals.

### Ordinary regression validation

A018UR targeted: 8 passed. A014 watchdog: 12 passed; combined preflight 20 passed.
All application modules: 951 passed in 174.77 s, one expected Feather V1 deprecation warning. Includes A018U 80, A018T 283, A018S 95, A018 97, A017 79, A016 68, A015 59, A014 12, A013 17 and A011 8.
Compileall src/scripts/tests PASS; tracked integrity PASS (9 frozen files/internal identities); diff check PASS; uv build PASS (0.3.0 wheel/sdist).
An initial targeted command named nonexistent tests/test_task011_stateful.py and collected no tests. Corrected application selection passed; actual tests/test_task011.py is covered by full pytest. No real test gate enabled.

Reporting correction (parameters unchanged): the copied preregistration names
PowerShell Get-FileHash. This run actually verified SHA256 through the existing
verify_sources/_file_digest Python implementation invoked from PowerShell, before
preregistration and again in the supervisor. Hash values and expected identities
were frozen correctly. This correction is appended, not a preregistration rewrite.

Full pytest PASS: 1198 passed, 14 expected CUDA/unenabled-real skips, one
existing Feather V1 warning, 183.58 s. Stateful Task011 and A011 covered.
No full-real gate enabled; no second preparation. Final scope exactly three
new files; all historical source/artifacts remain untouched. Version 0.3.0,
tracked active workflows zero, stash empty. Commit/push authorized for this
complete bounded-stop record. Final exact Git identities are reported separately
to avoid self-referential commit metadata. No tag or release.
