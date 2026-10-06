# A019K evidence-only full-real CPU rebenchmark gate

Authorization: user explicitly authorized `授權 A019K`, evidence-only review,
documentation, commit and push. No execution authorization is conveyed to A019L.
Root derived with `git rev-parse --show-toplevel`: D:/spider/working/MaleCNS-Sim.
Starting local HEAD = origin/master = live GitHub master =
`c29c6973247c785d40bf058bf5ba4e18aa8a5d30`. Worktree and staging clean, stash
empty, version 0.3.0, tracked workflows 0. All required starting gates passed.

Plan: verify identities and clean scope; read committed reports/evidence and source
without project imports or payload access; recompute recorded arithmetic with
isolated standard-library Python; adjudicate semantic and performance gates;
freeze a future contract and descriptive outcome rules; diff-check, commit, push
and verify final identities. This plan records the completed review.

## Decision

**A019K-A — FULL-REAL CPU REBENCHMARK JUSTIFIED. SAME-CONTRACT. PES-A.**
Exactly one recommended next task: **A019L — Full-Real CPU Rebenchmark After
Membrane O1 Optimization**, subject to separate explicit authorization.

The optimization is sufficiently safe for this gate: ordered operations, ownership
and exact synthetic replay support unchanged scientific semantics. Medium/larger
complete-advance benefits, interleaved corroboration and concrete allocation
removal justify measuring the remaining full-real uncertainty once. No unresolved
semantic or synthetic-evidence issue requires another synthetic task first.
This does not establish full-real benefit or predict an 8% A019D improvement.

## Evidence integrity and baseline

Primary committed evidence: [A019D report](2026-10-06-application-a019d-full-real-stateful-benchmark.md),
[A019D JSON](2026-10-06-application-a019d-evidence.json),
[A019E review](2026-10-06-application-a019e-a019d-p2-evidence-review.md),
[A019J report](2026-10-06-application-a019j-membrane-o1-optimization.md),
[J baseline](a019j-baseline-evidence.json), [J optimized](a019j-optimized-evidence.json),
[J replay](a019j-replay-evidence.json), [J interleaved](a019j-interleaved-evidence.json),
and [J summary](a019j-membrane-o1-evidence.json).
A019F-H instrumentation and A019I feasibility are supporting diagnostic history;
their synthetic attribution is not full-real attribution.

Verified A019D raw SHA256:
`ffe43022024d92063de118572d4e26ab93c6c3ec19137bfa2d2dd2f59c593ea4`.
J artifact SHA256 identities, computed from existing committed files:

| Artifact | SHA256 |
|---|---|
| baseline | 277d121e1d54f2e248774977de73babcc240f39fe2c7bfcdfd82b26a93f87c58 |
| optimized | 989f050385756a75115998594912158c4b097ba54c21d69c5c109d7ce6ebaf6b |
| replay | 6714677ecbb15944c7cc2a64908e829be4702800821333cd593009047e757832 |
| interleaved | 8925ea99fe3deead90be0837dc2ee9ed922a0e38b04811ca7126ec1a871f8388 |
| summary | e86410e154e8670e3e4d8f3ac5ccb6bfcfb44b4a90b219e85eac78fd44e4358e |

Preserved **A019D-P2 — FULL-REAL STATEFUL BENCHMARK COMPLETE**. Its attempt
was consumed and is not reusable. Preparation 101.304875 s; sampled contained-tree
peak private 5,473,751,040 bytes; working set 4,468,166,656 bytes. One preparation,
one network/runtime, two states, 24 advances. Raw A19C-A and null P1/P2 remain
unchanged; the report's P2 adjudication is preserved.

Isolated arithmetic verified 24 rows, 20 measured rows, twelve exact A/B replay
records including pending/delayed evidence, and these total-call statistics:

| Metric | Frozen A019D seconds |
|---|---:|
| min | 1.515181500 |
| median | 1.642870550 |
| mean | 1.647739485 |
| max | 1.774488700 |
| p95 | 1.741707810 |
| population std | 0.062658750363 |
| population CV | 3.802709768953% |
| A mean | 1.613853650 |
| B mean | 1.681625320 |

Counts <=20 ms / >20 ms / >=30 s = 0 / 20 / 0. p95 is linear interpolation
at sorted zero-based index 18.05, not nearest-rank percentile.

| Measured position | A seconds | B seconds |
|---|---:|---:|
| 1 | 1.6200414 | 1.6553535 |
| 2 | 1.6382754 | 1.6560338 |
| 3 | 1.5658390 | 1.6930420 |
| 4 | 1.5151815 | 1.6120948 |
| 5 | 1.5569737 | 1.6327310 |
| 6 | 1.6918164 | 1.7399825 |
| 7 | 1.6992220 | 1.7744887 |
| 8 | 1.6094614 | 1.6397771 |
| 9 | 1.6459640 | 1.7308286 |
| 10 | 1.5957617 | 1.6819212 |

## A019J integrity and evidence strength

Preserved A019J-A / JPERF-A. Raw before/after graph, stimulus, seed, duration,
warmup and repeat identities match. Recomputed OFF, membrane and linear means
and medians match the summary. Twenty-four ordinary chunk replay rows have equal
optimized/reference state/output digests and exact=true. Committed certification
also covers equal taus, empty/full/mixed masks, threshold/refractory edges,
special floating values and state isolation; source and tests were read statically.
Historical 64-test PASS is evidence, not a new A019K test run.

| Case | Membrane median ms before/after | Linear median ms before/after | OFF advance median ms before/after | OFF median / mean change |
|---|---|---|---|---|
| G1 | 1.16445 / 1.10190 | 7.45105 / 7.26750 | 10.72020 / 10.18730 | -4.97% / -6.57% |
| G2 | 2.52565 / 1.93295 | 12.64020 / 11.54320 | 17.98855 / 16.51505 | -8.19% / -8.00% |
| G3 | 13.76725 / 11.38435 | 54.42995 / 48.77710 | 77.89165 / 71.37445 | -8.37% / -7.62% |

Membrane median changes G1/G2/G3 = -5.37% / -23.47% / -17.31%.
Recomputed interleaved OFF wins: G1 6/10, G2 10/10, G3 10/10.
G2/G3 interleaved baseline/optimized medians are 17.2467/16.5725 and
78.9288/74.2701 ms. Primary sequential OFF ranges overlap; interleaved evidence
corroborates direction rather than substituting its wrapper timings for baseline.
No meaningful cost shift was observed, including scratch setup in total wall.
Unchanged-stage decreases are not separately attributed to the optimization.

Structural source/test review confirms five membrane result payload allocations
plus one decay result allocation per update become zero: combined **6 -> 0**.
Strict membrane-only accounting is **5 -> 0**, not six membrane arithmetic passes.
Five membrane passes and one decay pass remain. Two private float64 buffers are
created per advance, sliced to K, fully overwritten, and expire on return.
This excludes view headers and internal native allocation telemetry.

**PES-A**: G2/G3 end-to-end benefit is consistent in mean/median and all interleaved
pairs, supported by exact replay and a concrete mechanism. G1 is noisy, synthetic
graphs are smaller and differently active than full-real, and ON instrumentation
perturbs timings. These limitations prevent projection, but do not erase the
reason to measure whether the certified full-real workload benefits materially.

## Semantic-contract comparison

Reviewed A019D starting implementation `bb7a284c4e74f7c257880fd914b9ad9b99f7fd00`
against current source, and A019J's parent-to-commit production diff. The only
production files changed across the wider interval are lif.py and stimulus.py:
opt-in timing hooks and J scratch operations. Default timing is OFF; hooks can
still contribute branch overhead, which the full implementation comparison measures.
The benchmark/A013 forward harness and frozen contract are unchanged. The D
invocation adapter was added during D and is unchanged since its publication.

| Scientific component | Review |
|---|---|
| dt | Same 0.1 ms, 200 steps per 20-ms call |
| neuron/state equations | Same analytic coefficients and ordered rounding; no fusion/reassociation |
| synaptic dynamics | Same decay multiplication, after g contribution consumed |
| refractory semantics | Same strict boundary, masks and free override |
| thresholds/reset | Same comparisons, spike/reset/enqueue order |
| delays | Same quantization and ring routing |
| pending/delayed events | Same delivery, accounting, accumulation and retained state |
| schedule handling | Same lookup/grid validation, ordering and packing; OFF timing hooks |
| state initialization | Same canonical initial_state, independent A/B |
| chunk boundaries | Same persistent continuation, 20 ms, twelve calls/state |
| output semantics | Same canonical output, copies/digests; scratch does not escape |
| deterministic replay | Exact synthetic state/output certification; D exact A/B baseline |

**SAME-CONTRACT**. Full-real optimized-versus-D exact replay remains an A019L
acceptance requirement, not an accomplished A019K result.

## Frozen future A019L contract

Inherit the entire [frozen benchmark JSON](2026-10-05-application-a019a-benchmark-contract.json)
and [certified forward harness contract](2026-10-05-application-a019c-harness-contract.json),
including reference parameters, sign policy, delay rules, outputs and G1-G6
identity checks. Benchmark identity:
`95c5d61654cfc8b944dd8ffad987c0e3129c8eef2fa24512f57d7e90f997336a`.
No contract change is permitted to rescue an apples-to-apples comparison.

- Certified bounded CPU route, cpu_reference, batch 65,536, merge block 16,384,
  fallback hard stop; one preparation, PreparedNetwork 1, PreparedRuntime 1.
- Same registered male-cns v1.0 source set; source bytes/SHA256 must match D:
  annotation 14,483,314 / `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`;
  neurotransmitter 43,282,834 / `95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621`;
  edges 1,051,241,946 / `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1`.
  Preserve D preparation/provenance/graph identities, including prepared digest
  `d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495`,
  166,700 neurons and 24,904,953 effective edges. Identity layers are not interchangeable.
- Two fresh independent states: A then B, each 2 warmups + 10 measured x 20 ms,
  final 240 ms. Total 24 advances, max consecutive 12. A released before B.
  No reset/recreation, clone, coexistence or continuous 480-ms trajectory.
- One schedule: LEFT sugar 42, LEFT 100 Hz, RIGHT 0 Hz, seed 1555062870,
  impulse 68.75 mV, horizon 240 ms, 948 events. Same member IDs and windows;
  repack each call. Fingerprint
  `6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a`.
- Preparation/advance/worker timeouts 600/30/1500 s. Private and working-set caps
  each 8,589,934,592 bytes throughout aggregate contained-tree lifetime.
  Available physical preflight >=12 GiB; memory sampling 0.1 s.
- Same Windows Job contained suspended-launch supervision and cleanup checks,
  timers and OFF diagnostic mode. Total benchmark-call wall includes repacking,
  advance/output assembly, readout, decoder and dummy bookkeeping; exact
  verification is outside the timer. No Arena.
- Exact corresponding A/B replay at all twelve boundaries; additionally compare
  each recorded input/state/output/pending/timestep record against D, not only
  final states. No tolerance, alternate output mode or verification reduction.
- P1: every measured call <=0.020 s. P2: not every call <=0.020 s and all twenty
  measured calls <30 s. Warmups excluded from statistics; all 24 must complete
  within their deadlines. P1/P2 are reported separately from L outcomes.

## Environment comparability matrix

Statuses describe historical evidence and ability to match; MATCHABLE is not a
claim that a future run's environment has already been verified.

| Field | A019D evidence / historical reconstruction | Status | A019L requirement |
|---|---|---|---|
| CPU | Intel Core i9-7900X, 10 cores/20 logical | MATCHABLE | Record exact identity/topology; same host |
| OS | Windows 10 Pro 10.0.19045; raw Windows-10-10.0.19045-SP0 | MATCHABLE | Record edition/build and relevant updates |
| Python | 3.14.0, MSC v.1944, 64-bit AMD64; workspace .venv | MATCHABLE | Same build/architecture; record executable |
| NumPy | 2.5.3 | MATCHABLE | Same version and installed build identity |
| package lock | Git uv.lock blob b9d5025dcb340498b417baf42c15fb826d46fdf3 at D start and current; unchanged | MATCHABLE | Record lock blob/content hash and installed dependencies; lock alone does not prove installed equality |
| BLAS/runtime build and thread pools | Not captured in D | NOT_RECORDED_IN_A019D | Record NumPy configuration, linked runtime/build and thread pool information without tuning |
| repository | D start bb7a284c4e74f7c257880fd914b9ad9b99f7fd00; adapter published in 659b7f970ffb8f8ad9cd8c35a2d05296a4f88097; J implementation c29c6973247c785d40bf058bf5ba4e18aa8a5d30 | CHANGED | Intentional treatment; record future SHA and audit only accepted implementation/docs differences |
| dataset/source | Three source hashes above and G1-G6 recorded | MATCHABLE | Exact source and preparation identities |
| supervision | Certified Windows Job worker, aggregate-tree caps, 0.1-s samples | MATCHABLE | Same mode/polling/timer boundaries |
| thread environment | OMP_NUM_THREADS, OPENBLAS_NUM_THREADS, MKL_NUM_THREADS, BLIS_NUM_THREADS, NUMEXPR_NUM_THREADS, VECLIB_MAXIMUM_THREADS not captured | NOT_RECORDED_IN_A019D | Record values or explicit unset, plus affinity/process priority; no alternate settings |
| power/performance mode | Not captured | NOT_RECORDED_IN_A019D | Record existing power plan/performance mode; no tuning |
| thermal/frequency/load/allocator/cache | No controlled historical record | UNKNOWN | Record observable frequency/thermal/load, background jobs, uptime and memory pressure; state measurement limits |
| memory | 133,890,060 KiB visible; initial available probe 117,725,188,096 bytes; adapter available 117,545,050,112 bytes | MATCHABLE | Record total/available and paging pressure; identical availability not required, no material pressure change |

Known mismatch in CPU, OS/runtime/library build, thread configuration, supervision,
timer/output mode, source or workload invalidates direct attribution unless it is
demonstrably irrelevant by pre-execution static evidence. No corrective benchmark
or alternate setting is allowed. Severe contention, throttling or paging also
invalidates comparison. Missing historical BLAS/thread/power metadata alone does
not automatically force L4: same host/software route, unchanged lock and no known
material confound can support a qualified descriptive comparison. Record the
unknowns explicitly; plausible timing-confound uncertainty sends a completed run
to L2, while a demonstrated material mismatch sends it to L4.

## Predefined descriptive metrics and outcomes

Report all twenty measured wall times in A1-A10/B1-B10 order, min, median, mean,
max, linearly interpolated p95, population std and CV, A/B means and all three
threshold counts. Also report preparation/peaks and all warmup times separately.
For mean, median and p95 compute seconds delta L-D and percent 100*(L-D)/D;
negative is faster. For each matched state/position compute the same paired delta,
count faster/slower/tied positions and report paired median and A/B mean deltas.
Position pairing aligns workload, not independent randomized statistical pairs.
Use no significance claim or calibrated confidence interval from n=20.

The following conservative decision margins are frozen now, before execution.
Five percent is a practical review margin, motivated by D's 3.80% pooled CV and
4.20% later-B shift; it is not an estimated noise bound or significance threshold.
Define material tail regression as max OR p95 >105% of D. Evaluate validity first.

- **L1 — FULL-REAL BENEFIT CONFIRMED**: complete exact 24-call contract and
  exact D/A/B replay; no timeout/resource failure; sufficiently comparable
  environment; mean AND median at least 5% lower; A and B means both lower;
  >=16/20 positions faster with >=8/10 in each state; paired median lower;
  no material max/p95 regression. To exclude one/few-call dominance, remove
  the three largest positive savings (D-L), then require the remaining seventeen
  summed savings >0. This is a qualified descriptive workload benefit, not
  statistical significance or isolated causal proof.
- **L2 — FULL-REAL EFFECT SMALL / INCONCLUSIVE**: valid complete exact run
  that meets neither L1 nor L3, including small, mixed or insufficiently
  consistent changes, tail-only worsening, or residual environment uncertainty.
  Improvements below 5% may be real; this single attempt cannot confidently
  establish them under the chosen practical gate.
- **L3 — FULL-REAL PERFORMANCE REGRESSION**: valid complete exact run with
  mean AND median at least 5% higher, both A/B means higher, >=16/20 positions
  slower with >=8/10 in each state. Report tail regressions even if the complete
  pattern is mixed and classified L2.
- **L4 — INVALID COMPARISON**: contract/source/timer/material environment
  mismatch, failed exact replay, incomplete call structure or timeout/resource
  failure prevents the planned comparison. Preserve the underlying failure
  reason; L4 does not itself quantify an optimization regression.

These rules are exhaustive by L4 validity precedence, then L1, L3, otherwise L2.
P1/P2 remain separate; e.g. A019L-L1 / P2 confirms qualified full-real benefit
while retaining failure to meet every 20-ms deadline. Failed/incomplete runs
receive no successful P1/P2 completion classification. Reaching P1 is not required
for L1. No threshold or exclusion rule may be adjusted after seeing L timings.

## Future attempt policy, uncertainty and closure

A019L must separately authorize exactly ONE new full-real preparation. Its new
attempt is consumed at the first accepted registered real connectivity/edge
source access, including identity-verification access before preparation.
After consumption: no retry, second preparation, fallback variant, tuning,
alternate threads or parameter adjustment. A019D accounting cannot be reused.
Before consumption, verify frozen executable preparation/call route, source
registration and environment preflight; stop on mismatch. No contract repair in
the attempt. This review neither consumes nor authorizes that future attempt.

Main uncertainty: full-real graph/activity, memory and pending-event workload
may respond differently from G2/G3, with historical environmental metadata
incomplete and sequential timing drift unisolated. One optimized historical
comparison measures practical workload performance, not a randomized causal trial.
No proven full-real speedup, projected ~8% A019D speedup, realtime/biological
realtime, GPU equivalence, behavioral or mechanism implication is claimed.

A019K counters: full-real preparations 0; real advances 0; new real attempts
consumed 0; A019D reruns 0; GPU runs 0; Arena runs 0; interventions 0; downloads 0;
archive writes 0; registered real-data payload reads 0. Static file reads and
isolated JSON arithmetic only; no project imports, discovery, benchmark or tests.
Counters describe performed operations, not independent native telemetry.

Validation: recorded arithmetic/replay/identity assertions PASS; documentation
only; `git diff --check` required before commit and after staging. Only this plan
may change. No large suite, tag, release or version bump. Commit/push final SHA
and local/origin/live equality are reported externally to avoid self-reference;
final worktree/staging/stash must be empty, version 0.3.0, workflows 0.
