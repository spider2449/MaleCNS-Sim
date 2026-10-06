# A019J bounded CPU membrane O1 optimization

Authorization: user explicitly authorized A019J including implementation, synthetic
validation, evidence, commit and push. Root derived by `git rev-parse --show-toplevel`:
D:/spider/working/MaleCNS-Sim. Starting local HEAD = origin/master = live GitHub
master = `4e6d88b8ee7ad2c38ea339038c912b305c969a5f`. Worktree, staging and stash
were empty; package version 0.3.0; tracked workflows zero.

Plan: verify start gates; activate the existing fail-closed firewall before Python
imports/collection; capture baseline before production edits; implement only ordered
membrane out= with two private scratch buffers; prove structural counts and exact
replay; repeat the same matrix; assess cost shift/overhead/variability; run targeted
regression, compileall and diff check; record classification; commit/push and verify.
All steps completed. No unrelated dirty files were present at closure review.

Outcome: **A019J-A — MEMBRANE O1 OPTIMIZATION COMPLETE; EXACT REPLAY PRESERVED;
SYNTHETIC PERFORMANCE IMPROVED. JPERF-A — MATERIAL SYNTHETIC IMPROVEMENT.**
Preserves A019I-B — FIRST CPU O1 TRANSFORMATION READY; MEMBRANE TARGET SELECTED.

## Implementation and lifetime

Only dense CPU `simulate_lif` uses the internal `_scratch` argument to
`linear_state_update`. Default public scalar/general-array behavior and the active
caller remain unchanged. Two separate `np.empty(N, dtype=np.float64)` buffers are
allocated during state_setup of each advance. Capacity does not change within a
call; each update uses K-sized basic-slice views. They are per advance, neither
PreparedRuntime-owned nor SimulationState-owned. They are released on return and
recreated for every subsequent 20-ms call, with no cross-call persistent scratch.
No global cache or state-owned array serves as scratch. Both buffers are independent
of each other, persistent state and unchanged Boolean gathers. The selected lanes
are fully overwritten before reading; changing K does not expose stale data.
Outputs are copied back to v then g before the next overwrite; no result contains
a scratch view. Separate calls/states cannot share these live buffer owners.

Exact sequence: subtract(v, rest, out=a); multiply(a, exp_m, out=a);
add(rest, a, out=a); multiply(g, coefficient, out=b); add(a, b, out=a);
then multiply(g, exp_s, out=b), after the g contribution is consumed.
All operands, coefficients, equal-tau branching, rounding sequence, writeback order,
gathers, indexed writes, scheduler, pending events, thresholds, refractory rules,
parameters, dt and chunk/call boundaries are preserved. No fusion/reassociation.
Production implementation changed; scientific/model semantics did not change.
The A019I isolated diagnostic accepts the new private keyword for compatibility;
its prototype still uses its own isolated scratch and does not consume production scratch.

## Structural proof

Membrane full-array passes: **5 -> 5**. Decay: **1 -> 1**. Arithmetic passes are
retained; none is fused or removed. Membrane ndarray payload allocations per
update: **5 -> 0**; decay: **1 -> 0**. New scratch setup: two arrays per advance.
Two slice-view headers per update remain, as do the tuple and existing gathers.
The targeted spy verifies all six ordered out= calls and their buffer destinations;
no explicit np.empty occurs inside the scratch update. This is structural payload
accounting, not native allocator telemetry or a claim of zero internal allocations.

| Full selection bound | Old membrane cumulative bytes | Old decay bytes | New result allocation bytes/update | Scratch bytes/advance | Scratch bytes between calls |
|---|---:|---:|---:|---:|---:|
| G1-12 | 5120 | 1024 | 0 | 2048 | 0 |
| G2-12 | 163840 | 32768 | 0 | 65536 | 0 |
| G3-12 | 1310720 | 262144 | 0 | 524288 | 0 |

Counts are for K=N upper bounds; actual payload scales with K. Old cumulative
allocation bytes are not peak live memory. Existing gathers retain two arrays,
16K bytes per update. ndarray headers, padding, iterator internals, native scatter
buffering and unrelated arrays are excluded. Scratch setup is included in measured
state_setup and complete wall time.

## Exact certification

PASS: frozen pre-A019J expression copied exactly from the starting SHA, with its
source text verified against the frozen git module. G1/G2/G3 each use two consecutive
20-ms chunks with normal/empty/full/mixed state-mask arrangements, and ON/OFF exact
comparisons. Equal-tau chunk replay also covers all three sizes; unequal taus use
the ordinary matrix. Direct empty/full/mixed selections cover strict refractory
boundaries and free override, signed zero, infinities, NaNs and subnormals. Every
state and result dataclass field is compared (dtype, shape and bytes for arrays):
membrane, synaptic, refractory, pending/delayed counts, event ordering, traces,
outputs and final timestep/time. Digests are recorded in a019j-replay-evidence.json.
The existing A019H test additionally compares against the entire starting-SHA
simulate_lif module. Cross-state buffer isolation/reuse and fresh state independence
PASS. Public outputs retain independent storage. No tolerance relaxation.

An initial certification harness invocation used an unsupported collect_sparse_trace
keyword on PreparedRuntime.advance; it raised before any comparison and was corrected.
There was no exact mismatch or production test regression. Final test run: 64 passed.

## Identical synthetic measurement protocol

G1/G2/G3 = 128/4096/32768 neurons, eight edges per neuron, seed 1906,
60 scheduled events, identical graph/stimulus fingerprints, 20-ms measured duration,
three warmups and ten measured calls per case. The established runner measures a
fresh state after one unmeasured continuation chunk and alternates paired OFF/ON
order. Baseline raw evidence was saved before production edits. All raw pairs and
mean/median/min/max remain in separate baseline/optimized JSON files. ON stage
measurements and OFF complete advance are distinguished below. Values are ms;
negative deltas mean improvement. Complete stage/substage/residual comparisons,
including mean deltas, are in a019j-membrane-o1-evidence.json.

| Case | Metric | Baseline median / mean | Optimized median / mean | Median delta ms / percent | Mean delta ms / percent |
|---|---|---:|---:|---:|---:|
| G1-12 | membrane ON | 1.16445 / 1.25638 | 1.10190 / 1.10166 | -0.06255 / -5.37% | -0.15472 / -12.31% |
| G1-12 | linear ON | 7.45105 / 8.12530 | 7.26750 / 7.26159 | -0.18355 / -2.46% | -0.86371 / -10.63% |
| G1-12 | advance OFF | 10.72020 / 11.02656 | 10.18730 / 10.30214 | -0.53290 / -4.97% | -0.72442 / -6.57% |
| G1-12 | advance ON | 12.20235 / 13.24301 | 11.93065 / 11.90683 | -0.27170 / -2.23% | -1.33618 / -10.09% |
| G2-12 | membrane ON | 2.52565 / 2.55166 | 1.93295 / 1.92862 | -0.59270 / -23.47% | -0.62304 / -24.42% |
| G2-12 | linear ON | 12.64020 / 12.78221 | 11.54320 / 11.54779 | -1.09700 / -8.68% | -1.23442 / -9.66% |
| G2-12 | advance OFF | 17.98855 / 18.27966 | 16.51505 / 16.81701 | -1.47350 / -8.19% | -1.46265 / -8.00% |
| G2-12 | advance ON | 19.57950 / 20.11320 | 18.09895 / 18.13163 | -1.48055 / -7.56% | -1.98157 / -9.85% |
| G3-12 | membrane ON | 13.76725 / 13.78495 | 11.38435 / 11.30717 | -2.38290 / -17.31% | -2.47778 / -17.97% |
| G3-12 | linear ON | 54.42995 / 54.47585 | 48.77710 / 48.66141 | -5.65285 / -10.39% | -5.81444 / -10.67% |
| G3-12 | advance OFF | 77.89165 / 78.31542 | 71.37445 / 72.35128 | -6.51720 / -8.37% | -5.96414 / -7.62% |
| G3-12 | advance ON | 80.15290 / 80.17384 | 73.33595 / 73.28399 | -6.81695 / -8.50% | -6.88985 / -8.59% |

## Variability, instrumentation and cost shift

G2/G3 membrane median and mean consistently improve. Their total-linear observed
baseline/optimized ranges are disjoint. Primary OFF total-wall ranges overlap,
so the sequential primary comparison alone would be weaker evidence. A documented
supplement uses the SAME graph/events/seed/duration/3-warmup/10-measurement matrix,
alternating frozen-expression/optimized OFF order. Both sizes win 10/10 pairs, with
disjoint total-wall ranges. It includes the frozen wrapper and scratch setup in both
routes, so it corroborates direction rather than replacing the pre-edit baseline.
No calibrated statistical confidence or universal speedup is claimed; no fixed
percentage threshold was invented. G1 is small/noisy and supports no material claim.

| Case | Baseline linear range ms | Optimized linear range ms | Baseline / optimized ON overhead percent |
|---|---:|---:|---:|
| G1-12 | 7.3391 - 13.9095 | 6.9421 - 7.5039 | 13.83 / 17.11 |
| G2-12 | 12.0168 - 15.1712 | 11.0412 - 11.9255 | 8.84 / 9.59 |
| G3-12 | 53.3310 - 55.4068 | 47.8739 - 49.5664 | 2.90 / 2.75 |

Instrumentation OFF default remains unchanged. G1 ON overhead is material, so G1
end-to-end effects are not trusted. G2/G3 overhead remains sufficiently stable for
same-hook stage direction, supported by the independent OFF corroboration.
Instrumentation does not invalidate this bounded classification.

| Case | Interleaved baseline / optimized OFF median ms | Paired delta median ms | Optimized wins |
|---|---:|---:|---:|
| G1 | 10.4674 / 10.3408 | -0.0388 | 6/10 |
| G2 | 17.2467 / 16.5725 | -0.6737 | 10/10 |
| G3 | 78.9288 / 74.2701 | -5.1111 | 10/10 |

No meaningful cost shift into linear residual, gathers, writeback, total linear or
total advance is observed. Both G2/G3 show decreases in those stage median and mean
values. Small G1 gather/writeback/shape changes are within the noisy small-case
context. Other stages and complete residual remain recorded, not hidden. Some
unchanged stages also decrease; their decreases are not separately attributed to
this transformation. Scratch setup is included, with no unmeasured persistent work.

## Validation, firewall and closure

64 targeted tests passed, zero skipped in the final run: A019J/I/F/G/H, A019C-R2,
Task005 CPU semantics, and selected A011 stateful continuity/initial-state tests.
The selected A011 tests perform CPU runtime checks only, no Arena execution.
uv run python -m compileall -q src scripts tests PASS; git diff --check PASS.
Firewall enabled before imports and collection using
MALECNS_A019C_R2_FIREWALL=1 and scripts/a019c_firewall on PYTHONPATH.
Full-real preparations=0; real advances=0; A019D reruns=0; GPU runs=0;
Arena runs=0; interventions=0; downloads=0; archive writes=0.
Accepted registered reads: REAL_CONNECTIVITY=0; REAL_ANNOTATION=0;
REAL_NEUROTRANSMITTER=0; REAL_NEURON_METADATA=0; REAL_MAPPING=0;
REAL_PROVENANCE=0; REAL_OTHER_REGISTERED_DATA=0.
Qualifier: fail-closed guarded accounting, not independent native byte telemetry.
Synthetic evidence writes are task artifacts, not archive writes.

Full-real relevance claimed: **No**. Synthetic performance is not full-real A019D
performance; no extrapolation, new real attempt, GPU run or biological interpretation.
Exactly one next task: **A019K — evidence-only gate for full-real CPU rebenchmark
authorization.** Review whether this synthetic effect justifies a separately
authorized full-real attempt. Do not directly rerun A019D or start A019K automatically.

Implementation intentionally retained for A019J-A/JPERF-A. Authorized closure is
limited to implementation, compatibility diagnostic adjustment, tests, frozen oracle,
synthetic runners and evidence/report. Commit/push identity and final clean-state
verification are reported after push to avoid self-referential commit hashes.
No tag/release/version bump; version 0.3.0 and tracked workflows zero retained.
