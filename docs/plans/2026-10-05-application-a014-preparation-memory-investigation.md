# Application A014 — CPU preparation memory investigation

## Authorization and disposition

Starting root derived by `git rev-parse --show-toplevel`: D:/spider/working/MaleCNS-Sim. Local HEAD, origin/master and live GitHub master all matched `4e2e10c3aa1cbef9e9e80b54981e20aefe1ef62e`; clean worktree, empty stash, package 0.3.0, zero tracked workflows. A013 report and harness read before pipeline analysis or mutation.

Decision: **A14-MEMORY-ARCHITECTURE-CHANGE-REQUIRED**; **M3**. Watchdog: **CERTIFIED_SYNTHETIC** for the new contained-tree implementation, not full-real certification. Retry: **P2**. GPU: **GPU_DOES_NOT_SOLVE_PREPARATION**. No production memory correction implemented. No scientific source code changed.

A013 remains **A013-MEMORY-LIMIT**, one attempted preparation, zero completed preparations, zero advances. Original result SHA-256 `16d1964ebb5db0aad133f28b9b3b429ac04c2fbf8b545811eeb9c311e4f9d56d`; adjudication SHA-256 `ea47944aefcccb196ef19d6869d9e136a11d3441bb2b0e07a8cba5ba1cc72f54`. Both local artifacts verified unchanged. A013 historical report unchanged. Original executed harness blob `401c8a6252bc9a11a186c33463776a0de653c8f6` remains available in Git history.

Original watchdog monitored launcher 12904 instead of worker 5036. Post-stop correction rebound to self-reported os.getpid(), tested only synthetically. That correction does not discover descendants, validate ancestry, or contain a replacement worker. A014 replaces future harness supervision with a Windows Job Object; existing PID helper remains for its historical regression. No real retry occurred because none was authorized, the cap had already been exceeded, and synthetic PID rebinding did not establish real resource enforcement.

A013 independently observed lower bounds: working set **22,016,323,584 bytes (20.5043 GiB)**; private bytes **24,040,083,456 bytes (22.3891 GiB)**. These are not true measured maxima. No stage of the interrupted opaque call was recorded; its exact location cannot be recovered from these snapshots.

## Production stage map and ownership

Path: ProductionEngine.prepare -> task008.prepare_network -> load_male_cns_v1_numeric -> publication selection/project_numeric_connectome -> SignedAnatomicalConnectome.from_projection -> EffectiveSignedProjection.from_signed_connectome -> PreparedNetwork -> PreparedRuntime.

| Stage | Inputs | Temporaries | Outputs and lifetime |
| --- | --- | --- | --- |
| Feather loading | local annotation, NT, raw weights | Arrow tables; combine_chunks; NumPy conversion; Python annotation/NT row dictionaries | three int64 raw edge arrays; tables live until loader return |
| Annotation identities | annotation/NT Arrow tables | to_pylist dictionaries, NT index dict, metadata tuples, seen-ID set | annotated NeuronRecords retained with numeric/signed network |
| Raw pair grouping | all raw source/target/count arrays | uint64 packed keys for IDs <2^32; otherwise 16-byte structured keys; np.unique outputs/counts; stable argsort intp permutation; sort workspace; duplicate branch sorted keys/starts | three sorted int64 arrays; raw arrays/table buffers can coexist during construction |
| Raw identity union | annotations plus raw endpoints | concatenate of both endpoint arrays, np.unique flattened/sorted copy and mask | unique raw neuron IDs; survives through prepare_network return via numeric |
| Curated selection | annotation rows | selection lists/sets | sorted curated int64 IDs, 166700 expected |
| Endpoint filtering | numeric raw graph and curated IDs | two np.isin operations, boolean masks, fancy-indexed three arrays | selected endpoint arrays; raw graph remains live in prepare_network |
| Curated regrouping | selected arrays | packed/structured keys, stable order, sorted keys, starts, three sorted copies | three unique int64 curated edge arrays; masks/temporaries die at return |
| Sign application | curated graph and NT evidence | per-neuron dictionaries; Python list of sign references per edge; masked counts and cast signs; products | int8 signs, boolean assigned mask, int64 signed counts; retained by PreparedNetwork |
| Unsigned CSR identity | curated graph | selected mask, searchsorted intp rows/cols, float64 values, SciPy conversion buffers, tobytes fingerprint copy | temporary CSR int32 indices/indptr for current bounds, float64 data; dies after fingerprint |
| Effective projection | signed graph | masked ID arrays, source/target int64 positions, float64 conversion/products, lexsort permutation, reordered copies, source_ids/anatomical arrays, source+1, hash byte copies; signed metadata JSON records repeatedly built | five int64/float64 edge arrays plus IDs and int64 indptr; retained |
| PreparedNetwork | signed and effective graph | final signed fingerprint JSON/byte copies; optional cache disabled in A013 | retains signed_connectome AND effective projection; numeric raw graph released after return |
| PreparedRuntime | effective projection | none of the raw loader intermediates required | holds projection and parameters; initial_state separately allocates neuron state and delay ring |

No pandas dataframe in this production path. No Python EdgeRecord per raw edge: the older object adapter is not called. Source annotation/NT dictionaries scale with annotation rows, not raw edge rows. No dense N×N adjacency. Delay is a scalar model constant; the stateful delay ring is N×19, constructed only after preparation. A013 never reached that allocation. Input-target mapping uses exact prepared IDs; no separate full edge input table.

## Memory accounting and static lifetime model

Frozen Task003 report: **R=151856684 raw segment edge rows**, **U approximately 88 million raw segment nodes**, **C=25582938 curated edges**, **N=166700 curated IDs**. Frozen Task008/A013 expected effective **E=24904953**. These are prior frozen dimensions, not A014 real-data measurements. Using only E to model loading is incorrect: R is about 6.1E.

Array headers are O(1), normally hundreds of bytes, versus O(R) buffers. NumPy fancy indexing always copies; astype(copy=False)/asarray may share only with matching dtype. Arrow combine_chunks may allocate distinct storage; conversion views retain their Arrow owner. Tables and conversion arrays must not automatically be added as independent bytes when shared. Instrumentation records owns_data and object IDs; object identity alone does not prove buffer independence. No dtype narrowing is justified here: raw body IDs and exact counts require established bounds; effective values/dynamics are float64 and remain unchanged.

| Structure | Logical bytes | Full-scale modeled contribution | Ownership/lifetime |
| --- | --- | --- | --- |
| Raw three int64 columns | 24R | 3,644,560,416 bytes / 3.394 GiB | required by current loader, not final runtime |
| Arrow three numeric columns | at least column widths ×R | up to another 24R for separate int64 chunks | may share with initial NumPy conversions; original tables persist to return |
| Packed pair key | 8R | 1.131 GiB | temporary |
| Structured pair key | 16R | 2.263 GiB | alternate branch; not simultaneously packed |
| unique keys + pair_counts | up to 16R packed / 24R structured | 2.263 / 3.394 GiB | temporary, remain until explicitly deleted after reordering |
| argsort permutation | 8R on this 64-bit host | 1.131 GiB | temporary, survives to loader return |
| Reordered raw columns | 24R | 3.394 GiB | coexist progressively with originals during replacement |
| Raw identity concatenate | 16R+8 annotations | 2.265 GiB | temporary |
| np.unique union flattened sorted input | approximately 16R | 2.263 GiB | temporary; uniqueness mask and output coexist |
| Unique raw IDs | 8U | about 0.656 GiB | raw numeric ownership until prepare return |
| Curated three int64 columns | 24C | 0.572 GiB | signed.connectome retains final arrays |
| Curated signs/counts/mask | 10C | 0.238 GiB | retained by signed.connectome |
| Effective arrays | 40E+8N+8(N+1) | **998865328 bytes / 0.930 GiB** | required by current effective representation; matches frozen Task008 memory_bytes |
| Effective outgoing target/weight duplicates | 16E | 398479248 bytes / 0.371 GiB | included within preceding 40E; independent copies |
| Temporary unsigned CSR | 12C+4(N+1) at current bounds | about 0.287 GiB | temporary, plus conversion rows/cols/values |
| Delay state ring, not preparation | 16×19N | 50676800 bytes / 0.047 GiB | pending float64 and int64 event counts, after initial_state |

Final PreparedNetwork also retains about **0.810 GiB** of curated anatomical/sign arrays plus neuron metadata/evidence objects. Thus memory_bytes describes effective arrays only, not all PreparedNetwork ownership. Effective source positions duplicate information encoded by indptr, but deleting them would change current public representation. signed_counts is retained although effective construction recomputes counts/sign products.

Python sign-list backing is approximately 8C pointers (~195 MiB) plus list overallocation; entries reuse sign values, not 25 million unique integer allocations. Annotation and NT row dictionaries, strings, NeuronRecords, sign/resolution objects and repeated fingerprint JSON records add O(annotation count) overhead. Deep ownership is not precisely measured for historical real objects. Hashing tobytes adds up to 8C/8E (~190 MiB) per copied array. A013's fixed stimulus is only 948 events; watchdog output and synthetic instrumentation cannot explain its tens of GiB.

| Stage | Live required/current representations | Temporary/duplicate buffers | Modeled peak, excluding unmeasured metadata/allocator overhead |
| --- | --- | --- | --- |
| Read/convert | raw numeric 3.394 GiB | Arrow chunks/consolidation 0–3.394 GiB extra | 3.4–6.8 GiB |
| Unique/group/sort raw edges | raw 3.394 GiB | key 1.131; unique+counts 2.263; order 1.131; reorder up to 3.394; Arrow extra 0–3.394; internal sort buffers additional | approximately 8–15+ GiB depending sharing and allocation lifetimes |
| Raw neuron union | sorted raw 3.394; unique output ~0.656 | order 1.131; concat 2.265; flattened unique 2.263; masks/workspace; original Arrow 0–3.394 | approximately 10–14+ GiB |
| Curated regrouping | raw 3.394+raw IDs .656; curated .572 | masked inputs .572; keys/order/starts/sorted buffers approximately 1–2 GiB | approximately 6–8+ GiB |
| Sign/CSR | raw ~4.05; curated .572; signs .238 | list .195, masked products/CSR rows/cols/data and hashes ~1 GiB | approximately 6–7+ GiB |
| Effective projection | raw ~4.05; curated/signed .810; effective .930 | lexsort/reordering/masked arrays/hash/JSON ~1–2 GiB | approximately 7–8+ GiB |
| After prepare return | effective .930 + signed .810 + metadata | allocator retention is not live scientific content | at least 1.74 GiB logical arrays |

**Root resource mechanism established:** full raw segment sorting/identity construction precedes curation and unnecessarily sets peak scale by R, not E. Multiple corrections are needed for a defensible 8-GiB envelope. **Exact observed >20-GiB peak is not fully explained by this static logical-byte model.** The model identifies sufficient overlapping allocations to violate 8 GiB, but does not honestly reproduce 24.040 GB private bytes. Arrow chunk ownership, NumPy sort/unique internals, allocator retention and actual interrupted stage were not captured in A013. They remain hypotheses, not invented measurements. Highest modeled stage is raw loading/grouping/identity union, not the final runtime. No conclusion that Python per-edge objects caused A013's peak.

## Bounded instrumentation and measurements

New script `scripts/investigate_application_a014.py`: importing does not load data or prepare a graph. CLI requires --synthetic-edges (1..200000) and a new output path. It generates temporary synthetic Feather tables and invokes the actual production prepare_network with default CPU/scientific settings. No accepted raw-data path option. PreparationProbe is scoped and opt-in, restores sys tracing, refuses an existing tracer, and uses native WindowsMemory counters. Trace records stage call/return/first visit to each source line, local array dtype/shape/nbytes/owner flag/object ID, Arrow logical size, and shallow container count/size. First/last appearances delimit local visibility; they do not prove allocator release or absence of references elsewhere. Trace records are retained instrumentation overhead.

Line-boundary process snapshots are sampled, not continuous private-byte peaks. Lifetime OS peak working set is also recorded. First-visit suppression bounds loop instrumentation and excludes repeated neuron-loop samples. Internal native allocation peaks between traced lines may be missed. Measurements are evidence of scale, not full-real certification.

Fresh process per scale, 1000 synthetic neurons, seed 14, duplicate pairs intentionally aggregated:

| Raw edges | Effective edges | Sampled peak private bytes | Sampled peak working set | Effective final bytes | Highest private stage |
| ---: | ---: | ---: | ---: | ---: | --- |
| 10000 | 9956 | 738537472 | 111370240 | 414248 | from_signed_connectome |
| 50000 | 48788 | 773582848 | 119164928 | 1967528 | from_signed_connectome |
| 200000 | 181272 | 802250752 | 146251776 | 7266888 | from_signed_connectome |

Ignored evidence SHA-256: small `14e305eb975b0fc751b7db5950f4f5768bb9719a4bb504953d898a56e46d8a66`; medium `b682d64b09d52099b94627521c9941c18f4903cffc9531f489db46a86df192e8`; larger `abfa23695f8109ca3bcf4a23db897d624a54af51ee9fae45357f9ec8cc900c48`. Captured before adding shallow-container fields; process/array tracing algorithm unchanged. No before/after memory correction comparison: **N/A**, no correction, reduction percentage N/A.

Scale: logical graph buffers grow linearly with edges and neurons. Sorting costs time approximately E log E but major explicit sort buffers are O(E), not E log E bytes. Small measured private-byte differences are baseline/allocator dominated and not proportional enough to fit precise full-real GiB. No dense N×delay preparation growth; that is later state creation. No precise full-real extrapolation from these three points.

Exact instrumented/uninstrumented fixture comparison: PreparedNetwork fingerprint; neuron order, source and target positions, CSR indptr/targets, effective/outgoing weights; presynaptic signs, assigned mask and signed counts all equal. Same parameters preserve scalar delays, sign policy and LIF equations. Input-target mapping is identical because IDs and positions are equal. No tolerance or dtype relaxation. M2-only before/after correction tests are inapplicable.

## Watchdog contract and synthetic certification

Selected **E: both aggregate contained-tree private bytes AND aggregate contained-tree working set must be <=8 GiB**. This preserves A013's original two-metric resource bound and extends scope to all descendants. Private bytes represent private committed allocation, including paged-out memory; working set sums resident per-process counters. Shared resident pages can be counted more than once in aggregate working set: intentionally conservative, not a unique physical-page estimate. Aggregate private allocation does not count shared mapping pages as private in each process. No attempt to subtract shared memory that could weaken enforcement.

ProcessJob launches CREATE_SUSPENDED, assigns the launcher to a Windows Job Object before interpreter execution, then resumes it. Descendants inherit membership; breakaway is not enabled. Inventory comes from the Job Object, not PID equality or a self-reported ancestry guess. Membership remains for children after their parent exits, including replacement/spawn. Worker phase PIDs must belong to the job. 256-member inventory overflow, query/accounting/assignment/resume failures fail closed. Job has KILL_ON_JOB_CLOSE; explicit termination kills the entire job and waits for empty inventory. Normal exit code is captured before cleanup. No dependency installed. The A013 harness now uses this same job containment/accounting but retains its 100-ms sampling interval and frozen limits.

Synthetic threshold 128 MiB, allocating worker 160 MiB; no multi-GiB test. Direct base interpreter, actual Windows virtualenv launcher -> worker, parent -> child and parent exits after spawn tested twice each. Child-heavy cases verify offender PID differs from small launcher and launcher private bytes stay below threshold where still present. Also tested two 60-MiB allocations against aggregate 128 MiB, normal exit, and injected accounting failure. Synthetic runner samples every 20 ms, terminates on either aggregate metric crossing, reports deterministic MEMORY_LIMIT / NORMAL_EXIT / WATCHDOG_FAILURE, verifies empty job inventory and records process exit. Offenders may be empty when only the sum exceeds cap, correctly classified as aggregate violation.

Result: all tested excess-memory cases classified MEMORY_LIMIT; normal exit 0 unaffected; accounting failure WATCHDOG_FAILURE; **no orphan contained process after termination**. This certifies synthetic process discovery, aggregate memory accounting and hard termination. It does not promise no transient overshoot between samples or certify actual full-real cap behavior. The original corrected PID-only algorithm alone remains insufficient for arbitrary trees.

## Five candidates and M3 next-task design

| Candidate | Exact problem/current contribution | Proposed correction and peak effect | Risk / complexity / final-state effect |
| --- | --- | --- | --- |
| 1 | Sort all 151.9M raw rows before discarding 126.3M endpoint rows; raw columns 3.394 GiB plus multi-GiB keys/orders | Filter publication endpoints in bounded Arrow batches before grouping, then exact curated aggregation; remove R-sized key/order/union intermediates | High identity/provenance risk if raw summaries differ; high complexity; scientific final state must remain exact |
| 2 | numeric raw graph survives until prepare_network returns, ~4.05 GiB arrays | Release raw numeric ownership after projection and frozen raw statistics extracted | Low-to-medium lifecycle risk; low complexity; preparation-only improvement, cannot solve initial loader peak |
| 3 | np.unique(return_counts=True) followed by a separate stable argsort over raw keys | One exact stable grouping pass with shared permutation/bounded workspace | Medium aggregation/order risk; medium complexity; temporary peak only, still R-sized |
| 4 | independent effective outgoing targets/weights copies, 16E =398479248 bytes | Share immutable sorted target/weight arrays after alias contract audit | Low scientific value risk but public ownership/mutation risk; medium complexity; final and peak improvement, insufficient alone |
| 5 | retains signed_counts and full signed anatomical representation alongside effective arrays (~.810 GiB) | Explicit compact runtime owner after provenance/identity evidence is frozen, without losing application consumers | High API/provenance compatibility risk; high complexity; final memory changes; no broad rewrite in A014 |

Exactly five candidates; none implemented. Index/float narrowing not selected: exact scientific/dtype identity safety is not yet proven. **M3**, rather than M2: early release/aliasing alone cannot fix raw construction peak. No speculative local production optimization.

Exact next task: **A015 — bounded publication-endpoint preparation design and synthetic equivalence certification**. Design an explicit compact preparation entry point that reads curated identities first, filters raw edges in bounded batches, and groups retained integer endpoints deterministically. Preserve exact current array dtypes, stable canonical order, duplicate summation, fingerprints, NT policy, weights/delays and isolated curated neurons. Separate required raw provenance/statistics from raw numeric graph ownership. Test excluded endpoints, duplicates across batches, large IDs triggering structured keys, zero/self edges, unresolved signs, isolates, integer overflow policy and every scientific array/fingerprint. Measure chunk-size and edge-count scaling under the contained watchdog; quantify native allocation gaps before predicting an 8-GiB envelope. Do not execute real data automatically.

P2: unchanged loader remains likely above the same 8-GiB cap, based on A013 observation and multiple R-sized live buffers; watchdog repair does not reduce preparation memory. Full-real <=8 GiB **not proven**. No A014R envelope proposed because P1 is not selected. Any later real preparation needs separate authorization after architectural equivalence and resource evidence.

GPU_DOES_NOT_SOLVE_PREPARATION: use_cuda is checked/uploaded only after the identical CPU loader, curation, sign and effective projection stages. An RTX 3060 12-GB device cannot eliminate this pre-upload host peak; upload adds device copies while host PreparedNetwork remains retained. Device runtime feasibility is separate and unmeasured; no CUDA executed. GPU would not automatically solve this blocker.

## Firewall and validation

Full-real preparations=0; full-real stateful advances=0; real Closed-Loop Arena=0; behavioral runs=0; real scientific Application experiments=0; Task017 units=0; Task017Q=0; downloads=0; archive writes=0; BANC=0. Task016 unchanged; Task017 unchanged / NOT_ROBUST; B:\MaleCNS-Archive unchanged and not accessed. No scientific configuration/model, graph membership/topology, weights/sign/delay semantics or output interpretation change. No tag, release or version bump.

Validation: targeted A014 **12 passed**; A013 **17 passed**; A011 **8 passed**; reference LIF/stateful tests **24 passed**; combined **61 passed in 4.18 s**. Full `uv run pytest -q`: **421 passed, 14 skipped in 59.17 s**, including all application regressions. Skips are unavailable CUDA tests and the disabled real-data gate; no real-data tests enabled. compileall PASS; tracked integrity PASS (nine frozen files/internal identities); diff check PASS; uv build PASS (0.3.0 wheel and sdist). Synthetic termination exit codes are asserted: 1 for killed launchers/direct parents, 0 for the already normally exited replacement parent; memory classification remains MEMORY_LIMIT in both cases.

Final tracked scope: this report, A014 instrumentation/tests, and A013 future watchdog supervision only. Historical A013 report/artifact bytes and all scientific production modules unchanged. Commit/push authorized after passing checks. Final commit identity and remote equality reported externally to avoid a self-referential tracked SHA.
