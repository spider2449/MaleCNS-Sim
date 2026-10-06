# Application Task A019M — Evidence-only further CPU O1 decision

## Authorization and starting gates

User explicitly authorized `授權 A019M`, including review documentation, commit
and push. Repository root derived with `git rev-parse --show-toplevel`:
`D:/spider/working/MaleCNS-Sim` (spider2449/MaleCNS-Sim).
Starting local HEAD = origin/master = live GitHub master =
`a0c0c87ff656e740654586a214affd4915887753`.
Worktree clean, staging empty, stash empty, package version 0.3.0, tracked
workflows 0. All start gates passed before mutation.

Plan: verify identities and clean-state gates; read committed F/G/H/I/J/L
reports and evidence; inspect current source statically; recompute existing
metrics; compare candidates and select one bounded next investment; write this
review; run only `git diff --check`; commit/push and verify final custody.
No Python imports, test discovery, diagnostic runner or registered payload reads.

## Evidence integrity and preserved result

Reviewed the committed reports:

- [A019F](2026-10-06-application-a019f-synthetic-cpu-advance-instrumentation.md)
  and [evidence](a019f-synthetic-cpu-evidence.json).
- [A019G](2026-10-06-application-a019g-cpu-substage-instrumentation.md)
  and [evidence](a019g-synthetic-substage-evidence.json).
- [A019H](2026-10-06-application-a019h-linear-local-instrumentation.md)
  and [evidence](a019h-linear-local-evidence.json).
- [A019I](2026-10-06-application-a019i-linear-o1-feasibility.md).
- [A019J](2026-10-06-application-a019j-membrane-o1-optimization.md),
  [summary](a019j-membrane-o1-evidence.json),
  [baseline](a019j-baseline-evidence.json),
  [optimized](a019j-optimized-evidence.json),
  [interleaved](a019j-interleaved-evidence.json) and
  [replay](a019j-replay-evidence.json) evidence.
- [A019L](2026-10-06-application-a019l-full-real-cpu-rebenchmark.md)
  and [evidence](a019l-full-real-cpu-rebenchmark-evidence.json).

These were tracked, unchanged files at the verified starting commit. Static
source review covered `dynamics/lif.py` and `dynamics/stimulus.py`. PowerShell
JSON parsing and decimal arithmetic only were used to inspect/recompute evidence.

Preserve **A019L-L1 / P2**. Baseline mean is 1.647739485 s per 20-ms call;
optimized mean is 1.094710500 s. Summing the 20 committed measured timings and
dividing by 20 reproduces 1.094710500 s. All 20 committed position-paired deltas
are negative: improved 20, regressed 0, tied 0. Exact historical replay PASS;
SAME scientific/model benchmark contract. Two independent 12-call states,
with ten measured calls each, remain the comparison unit; no continuous 480-ms
trajectory is inferred.

| Statistic | Change |
|---|---:|
| Mean | -33.5629% |
| Median | -33.0508% |
| p95 | -34.2297% |
| Maximum | -34.2399% |

Exact slowdown from the stated decimal mean:
**1.094710500 / 0.020 = 54.735525 times** the realtime threshold.
0/20 measured calls were <=20 ms. L1 is confirmed improvement under the certified,
qualified descriptive comparison, not realtime capability or isolated causal
attribution free of environmental uncertainty. Historical BLAS/thread/power/
priority metadata limitations remain as recorded by L.

## Remaining candidate evidence

**A — Linear input gathers.** H JSON gives G1/G2/G3 means
0.307560/1.715960/15.051990 ms, agreeing with 0.308/1.716/15.052 ms rounded.
G3 share is 28.32321986224504% of linear update. Current dense source still
executes `input_v, input_g = v[allowed], g[allowed]`: two independent
float64[K] Boolean-index copies, 16K bytes total, read-only consumers, released
after the call. Neuron sensitivity is supported; E0/E2 gather means
1.717240/1.648660 ms show no material positive activity sensitivity. Neurons
and edges co-vary in G, so independent edge sensitivity is unproven.
I's HIGH importance/HIGH burden/PARTIAL specificity/MEDIUM exact confidence/
HIGH validation/MEDIUM risk/NOT_READY conclusion remains intact.
Boolean indexing has no output destination. Integer-index packing adds an
index construction/scan and possibly internal buffering; a masked N-lane route
changes the ownership/traversal design. Neither is an established replacement.

**B — Indexed writeback.** H G3 share is 22.29444576999242% of linear update.
Current source retains ordered Boolean assignment into v then g, unique
destinations, same float64 dtype and disjoint sources. Assigned payload is
16K bytes; no explicit result-array allocation is available to remove. Native
buffering remains unknown. I's HIGH importance/LOW explicit allocation burden
(HIGH writes)/UNCLEAR specificity/LOW exact confidence/HIGH validation/HIGH
risk/NOT_READY conclusion is preserved. putmask alignment, N-shaped copyto and
accumulating scatter are not justified replacements for the packed assignment.

**C — schedule_events grid validation.** G JSON parent shares for G1/G2/G3,
E1/E2 are 89.0738/88.5393/88.2289/89.8733/90.2842%. The tiny five-event E0
case is 73.2510%, so the supplied approximate 88–90% description applies to
non-tiny event cases, not every case. No substantive contradiction was found.
F scheduling shares reach 52.8%/59.7% of advance for S2/S3-E2; G's fixed-graph
E family localizes event sensitivity while its fixed-60-event G family has
approximately stable grid-validation cost. These are synthetic observations.
Full-real D/L scheduling fractions remain unmeasured; no exact transformation
has been audited or selected.

Static source: every event invokes `_grid_steps`, which validates finite value
and dt, positive dt, computes `int(round(value / dt))`, checks nonnegative step
and `np.isclose(value, steps * dt, rtol=0, atol=1e-10)`, then checks the duration
endpoint. Frozen schedules normalize and sort times during construction, but
grid alignment depends on dt. This provides a small, explicit contract to audit;
it does not establish that validation can safely be skipped or cached.
dt-only checks are plausible invariant work for valid calls; time-grid conversion
depends on time and dt, and endpoint validity depends on duration. Callers can
change stimuli/dt/duration, and Poisson generation can supply newly generated
explicit schedules. Reuse across calls is therefore conditional, not proven.

## Post-A019J interpretation and scorecard

J's medium/larger synthetic OFF full-advance improvement was about 8%
(G2 mean -8.00%, G3 mean -7.62%; medians -8.19%/-8.37%). L's full-real
mean improvement was about 33.6%. Synthetic percentages localize work but are
not calibrated predictors of full-real benefit. This increases the value of
auditing exact transformations, without transferring membrane gains to another
operation. H/G shares predate J and are not current post-J proportions.
Gather 28% does not imply 28% full-real opportunity; grid validation 90% of
scheduling does not imply scheduling dominates full-real advance.

Ratings below concern the proposed replacement, not correctness of existing code.
Importance/localization are scoped to committed synthetic evidence. INDIRECT
means source-based plausibility on the dense full-real route, not measured share.

| Dimension | A gathers | B writeback | C grid validation |
|---|---|---|---|
| Measured importance | HIGH | HIGH | HIGH |
| Localization confidence | HIGH | HIGH | HIGH |
| Full-real relevance evidence | INDIRECT | INDIRECT | UNKNOWN |
| Transformation specificity | PARTIAL | UNKNOWN | PARTIAL |
| Exact-semantics confidence | MEDIUM | LOW | MEDIUM |
| Validation burden | HIGH | HIGH | MEDIUM |
| Implementation risk | MEDIUM | HIGH | MEDIUM |
| Expected information value of next task | MEDIUM | LOW | HIGH |
| Readiness | R2 | R4 | R2 |

C's PARTIAL/MEDIUM ratings are static-review judgments: the scalar validation
boundary and conditional invariants are identifiable, but no exact implementation
contract exists. UNKNOWN full-real relevance is retained despite the shared call
path because its event-dependent magnitude is unconstrained by internal D/L timing.
A has stronger dense-neuron relevance plausibility, but I already exposed its
packing and cost-transfer obstacles. C has the largest remaining feasibility
uncertainty that a narrowly scoped audit can resolve without redesigning dense
state ownership. Its MEDIUM validation burden assumes the boundary stays within
grid validation; a broader scheduler/cache redesign would raise it to HIGH.
B is R4 for now because no concrete removable work offsets its semantic risk.
No candidate is R1. R3 is not selected: existing localization suffices to choose
a bounded feasibility inquiry, although full-real benefit still requires later
evidence and is not authorized here.

## Diminishing returns and investment decision

To reach the mean 20-ms threshold from this mean would require approximately
98.1738% additional latency reduction. No remaining O1 evidence supports such
a gain. Another plausible O1 is unlikely to alter the product conclusion P2;
this is an engineering assessment, not proof that CPU realtime is impossible.
The defensible goal for this line is incremental practical CPU latency improvement.
L demonstrates that exact allocation/lifetime work can have practical value,
but does not justify pursuing every available operation or another expected 33% gain.

One bounded feasibility diagnostic still has engineering value: it can establish
whether a small validation transformation is exact and worthwhile, or terminate
that candidate cheaply before implementation. C outranks A by expected uncertainty
removed per engineering complexity, not synthetic stage size or ease of editing.
A's dynamic selection, packing representation, aliasing/order/lifetime, integer
index construction cost and exact replay remain unresolved and more invasive.
B has weaker specificity and higher replacement risk. Additional broad profiling
would leave these transformation questions unanswered. GPU may merit a separate
investment later, but no committed evidence here establishes GPU performance or
equivalence or shows GPU certification has higher expected value than this bounded
CPU feasibility audit. It is not selected or started.

**Disposition: A019M-B — ONE BOUNDED FEASIBILITY DIAGNOSTIC JUSTIFIED BEFORE
SECOND O1.** Direct optimization is not ready. Another implementation is conditional
on feasibility certification; a negative diagnostic outcome is acceptable.

Exactly one next task:
**A019N — bounded synthetic feasibility diagnostic of schedule_events() grid
validation.** Recommended only; not started or automatically authorized.

Its contract must establish exactly what validation computes, conditional
invariants, potential precomputation/cache scope, dynamic time/dt/endpoint checks,
lifetime/invalidation and bounded ownership. Preserve exception type/message and
validation order (including empty schedules, invalid dt, unknown IDs, off-grid and
endpoint cases), rounding/tolerance/signed-zero behavior, duplicate-event order,
sorted batch order and dtype. Any candidate prototype must preserve exact replay
of all state/results, continuation, refractory and pending-ring semantics across
chunks, and account for work moved into cache keys/construction or packing.
Use synthetic-only guard-first diagnostics, no production optimization or real
benchmark. Reject reuse if dependencies/invalidation or exact behavior cannot be
certified. This task selects no caching implementation in advance.

## Claim boundary, counters and closure

L proves full-real CPU performance improvement for the membrane O1 under the
certified comparison. It does not prove remaining bottleneck identity, full-real
gather/scheduling shares, another approximately 33% gain, realtime proximity,
GPU performance/equivalence, biological behavior or model validity.

| A019M activity | Count |
|---|---:|
| Synthetic benchmark runs | 0 |
| New instrumentation runs | 0 |
| Full-real preparations | 0 |
| Real advances | 0 |
| A019D/A019L reruns | 0 |
| GPU/CUDA runs | 0 |
| Arena runs | 0 |
| Interventions | 0 |
| Downloads | 0 |
| Archive writes | 0 |
| Registered payload reads | 0 |

Only this documentation file changes. Validation: documentation/static review
and `git diff --check`; no test suite or executable code changes. Authorized
closure: `docs: decide next CPU optimization step`, then `git push origin master`.
Final commit SHA and local/origin/live equality are reported externally to avoid
self-reference. Require clean worktree, empty staging/stash, version 0.3.0 and
tracked workflows 0 after push. No tag, release or version bump.
