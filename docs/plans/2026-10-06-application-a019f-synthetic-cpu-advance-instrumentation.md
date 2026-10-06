# Application Task A019F — Bounded Synthetic CPU Advance Cost Instrumentation

## Authorization and baseline

User authorization: 授權 A019F. Synthetic-only CPU observation; no optimization.
Starting local HEAD, origin/master and live GitHub master all exactly
`0fbfc3e57ff263fb1f2a195e9671abcf77df7e7a`. Worktree and staging clean,
stash empty, package 0.3.0, active tracked workflows 0. Repository root was
obtained using `git rev-parse --show-toplevel`.

Preserve A019D-P2: historical mean 20-ms total-call wall 1.647739485 s;
coarse advance 1.647439540 s. Preserve A019E-B — INSTRUMENTATION REQUIRED
BEFORE OPTIMIZATION and T1 relatively stable systematic latency. Neither
history nor this synthetic matrix proves a full-real internal bottleneck.
No A019D boundary was changed or rerun.

## Source firewall and execution boundary

Before implementation inspection or Python validation, activated the existing
`scripts/a019c_firewall/sitecustomize.py` bootstrap:
`MALECNS_A019C_R2_FIREWALL=1`, `PYTHONPATH=<root>/scripts/a019c_firewall`.
Verified `validation_firewall.ACTIVE`. All Python commands, including collection,
benchmark, baseline replay, and compileall, used this bootstrap. Log was outside
the repository in the task's temporary directory. Source reads were limited to
code and task evidence. No registered payload inspection or catalog resolution.
Seven blocked test categories are deliberate before-content-read probes.
Accepted reads in all seven categories are zero.

Qualifier: **fail-closed guarded accounting, not independent native byte telemetry**.
Existing guard covers Python audit opens and public Arrow wrappers; arbitrary
native byte accesses are not independently certified. No native direct source
reader or child execution was used by this runner. It requires guard activation,
has no source argument, constructs in-memory immutable synthetic CSR arrays,
and rejects graph sizes outside the fixed bounded matrix.

## Actual call-path map and exclusive boundaries

Certified CPU path: `PreparedRuntime.advance()` → `simulate_lif()` →
`schedule_events()` / `validate_refractory_ids()` and, per timestep,
`linear_state_update()`, then `_canonicalize_spike_events()` and
`SimulationResult` materialization. GPU and `simulate_lif_active()` are untouched.

Exact boundaries below use executable statements rather than unstable line numbers.
All advance regions are in `src/malecns_sim/dynamics/lif.py::simulate_lif` unless
specified. Each can be observed without changing arithmetic or mutation order.

| Stage | First through last original operation | Included operations and boundaries |
|---|---|---|
| preparation | `parameters.grid_steps(dt_ms)` through `input_weight = ...` | Duration/weight validation, IDs, stimulus identity, existing input conversion; fingerprint JSON/hash Python/native boundary |
| event_schedule | Entire `event_batches = schedule_events(...)` call | `dynamics/stimulus.py::schedule_events`: ID search, per-event `_grid_steps`, ordered batch packing; NumPy searchsorted/isclose/asarray native boundaries |
| state_setup | `refractory_free = validate_refractory_ids(...)` through `delivered_events = 0` | Refractory/silenced/trace masks, state aliases, identity, ring size, optional trace allocation/initial gathers; resumable state is not copied |
| direct_input | `step = offset + local_step` through `v[direct_allowed] += direct[direct_allowed]` | Input lookup, bincount allocation, refractory gate, direct write; NumPy native operations |
| pending_delivery | `slot = step % ring_size` through `pending_event_counts[slot].fill(0)` | Ring dequeue, dense any/sum, refractory gate, synaptic gather/add/scatter, clear; optional sparse readout included |
| linear_update | `allowed = (step > refractory_until) ...` through `g[allowed] = updated_g` | Refractory mask, any, gathers, `linear_state_update()` coefficients/analytic membrane and synaptic update, scatters; these coupled equations are not artificial separate stages |
| spike_reset_enqueue | `fired = allowed & ...` through `queued_events += int(end - start)` | Threshold/flatnonzero, spike-output copies, reset/refractory writes, CSR slices, both ordered `np.add.at` calls and pending enqueue/counts; propagation and enqueue are one existing loop |
| trace | `if trace_v is not None` through `trace_g[:, local_step + 1] = ...` | Optional per-step state gathers/copies; benchmark traces disabled, equivalence tests enabled |
| output | `state.timestep += steps` through `SimulationResult(...)` construction | Bookkeeping, concatenate, lexsort canonicalization, searchsorted/bincount counts, metadata JSON/hash, byte digest, freezes, optional sparse trace and final trace-ID copy |
| residual | Total minus sum of all named intervals | Advance identity validation, hooks/accumulation, loop control and return plumbing; not double-counted |

`linear_state_update()` remains exactly the original coupled update. No outgoing
edge traversal occurs on quiet steps. Pending delivery is a dense ring scan;
there is no event-queue replacement. State is mutated in place; allocations and
copies are included with their owning operation instead of timed a second time.

## Instrumentation design and exact gate

`AdvanceTiming` is explicitly passed as `PreparedRuntime.advance(..., timing=...)`.
Default `None`; OFF never calls the clock. There are only observational branches
and timer hooks, with original statements and operation order preserved. No model,
algorithm, dt, weights, delay, threshold, event order, or pending semantics change.
No production application integration enables it. A record is per call, reusable
serially, and must not be shared across concurrent calls.

Timer: `time.perf_counter_ns()`. Total starts at `AdvanceTiming.begin()`'s first
clock read and ends at `finish()` after simulate returns. Stage intervals are
exclusive/nonoverlapping. Closing hook entry is inside its interval; accumulator
bookkeeping and transitions are residual. Result and timing-record serialization
are outside the advance total; outer wall includes the full advance invocation
and finish accounting, but excludes timing-record creation. Failed calls do not
provide a completed timing record and are never interpreted.

Reconciliation is exact integer accounting: `stage_sum_ns = sum(stages_ns)`;
`residual_ns = total_ns - stage_sum_ns`. All 100 final measured ON calls have
nonnegative residual and **zero reconciliation error**. Clock resolution/hook
cost is retained in stages/residual, never corrected with a invented fixed value.

Before each case's warmups/measurements, exact ON/OFF replay covered two successive
20-ms chunks: membrane, synaptic, refractory, pending weights/counts, timestep,
all output dataclass fields, spikes/order, trace arrays and event counters.
Array dtype/shape/bytes are checked without tolerance. Signed propagation,
refractory-free input and sparse delivery summaries are additionally covered by
targeted tests. OFF was independently replayed against the exact starting-SHA
module on S1 E0/E1/E2 over two chunks: exact bytes/state/output PASS.

## Workload and protocol

Seed 1906; deterministic unique sorted targets in each CSR row. Synthetic edges
are excitatory, 0.275 mV per edge. Reference parameters and dt=0.1 ms are unchanged.
Direct synthetic stimulus uses the existing fixture-style 30 mV input, without
parameter tuning, at 0, 5, 10, 15 and 19.9 ms for the first floor(N/100) E1 or
floor(N/10) E2 neurons; E0 has none. No silencing or scientific intervention.
A preceding uninstrumented 20-ms chunk establishes pending/refractory continuity;
the measured call advances the same workload another 20 ms (final time 40 ms).

Three OFF/ON warmup pairs, ten measured OFF/ON pairs per case; paired order
alternates. Each mode gets its own identical fresh state and precursor. State
allocation, graph generation and precursor are outside measured wall. The exact
equivalence gate precedes interpretation. A coarse exploratory matrix was followed
by the final finer matrix below; no numerical changes between them. Final raw and
summary data are in `a019f-synthetic-cpu-evidence.json`; every case/stage has median,
mean, min, max and mean share, with raw nanosecond records and identities.

| Case | Neurons | Edges | Density E/N² | Input events/call | Pending events before/after | Queued/delivered per call |
|---|---:|---:|---:|---:|---:|---:|
| S1-E0 | 128 | 1024 | 0.06250000 | 0 | 0/0 | 0/0 |
| S1-E1 | 128 | 1024 | 0.06250000 | 5 | 8/8 | 32/32 |
| S1-E2 | 128 | 1024 | 0.06250000 | 60 | 96/96 | 384/384 |
| S2-E0 | 4096 | 32768 | 0.00195312 | 0 | 0/0 | 0/0 |
| S2-E1 | 4096 | 32768 | 0.00195312 | 200 | 320/320 | 1280/1280 |
| S2-E2 | 4096 | 32768 | 0.00195312 | 2045 | 3272/3272 | 13088/13088 |
| S3-E0 | 32768 | 262144 | 0.00024414 | 0 | 0/0 | 0/0 |
| S3-E1 | 32768 | 262144 | 0.00024414 | 1635 | 2616/2616 | 10464/10464 |
| S3-E2 | 32768 | 262144 | 0.00024414 | 16380 | 26208/26208 | 104832/104832 |
| S2-edge-E2 | 4096 | 131072 | 0.00781250 | 2045 | 13088/13088 | 52352/52352 |

## Overhead and reconciliation

Descriptive overhead rubric: median ON minus median OFF <=5% is OHD-A;
>5% through 15% is OHD-B (use caution); >15% is OHD-C (no target attribution).
These are diagnostic thresholds, not scientific equivalence tolerances. Paired
raw data allow drift/noise review; no statistical confidence interval is claimed.
Overall OHD-B due to smoke cases; every medium/larger case is OHD-A. Instrumentation
is usable for localization. No per-stage overhead subtraction.

| Case | OFF median ms | ON median ms | Delta ms | Delta % / class | Residual mean share | Dominant stage: median ms / mean share |
|---|---:|---:|---:|---|---:|---|
| S1-E0 | 9.075 | 9.602 | 0.528 | 5.81% / OHD-B | 3.31% | linear_update: 6.561 / 68.3% |
| S1-E1 | 9.284 | 9.842 | 0.558 | 6.01% / OHD-B | 3.36% | linear_update: 6.474 / 65.7% |
| S1-E2 | 10.584 | 11.001 | 0.418 | 3.95% / OHD-A | 3.00% | linear_update: 6.386 / 58.0% |
| S2-E0 | 15.133 | 15.858 | 0.725 | 4.79% / OHD-A | 2.14% | linear_update: 11.072 / 69.9% |
| S2-E1 | 20.262 | 20.876 | 0.614 | 3.03% / OHD-A | 1.66% | linear_update: 11.152 / 53.6% |
| S2-E2 | 60.880 | 61.287 | 0.407 | 0.67% / OHD-A | 0.63% | event_schedule: 32.299 / 52.8% |
| S3-E0 | 89.094 | 89.802 | 0.708 | 0.80% / OHD-A | 0.61% | linear_update: 67.207 / 74.9% |
| S3-E1 | 113.485 | 114.857 | 1.372 | 1.21% / OHD-A | 0.50% | linear_update: 54.186 / 46.9% |
| S3-E2 | 444.880 | 447.019 | 2.139 | 0.48% / OHD-A | 0.20% | event_schedule: 266.353 / 59.7% |
| S2-edge-E2 | 64.154 | 64.991 | 0.837 | 1.30% / OHD-A | 0.55% | event_schedule: 31.949 / 49.1% |

Ranking uses medians; shares use sums of stage times divided by sums of total
instrumented times (equivalent to ratio of means). Residual is small enough that
no dominant stage is hidden there. Raw total, stage sum and residual are explicitly
recorded for every repeat. The accounting identity has a 0 ns numerical margin;
it does not assert timers themselves have zero uncertainty.

## Scaling and disposition

| Region | Classification | Evidence |
|---|---|---|
| preparation | mixed/unclear | Input fingerprint serialization grows with schedules; small absolute contribution after event batching split |
| event_schedule | roughly event sensitive | E2 median ~1.03/32.30/266.35 ms as events increase 60/2045/16380; same-neuron E1→E2 increases strongly; degree 8→32 leaves ~32 ms unchanged |
| state_setup | roughly graph-size sensitive | Dense masks and trace setup grow with neuron count; low share |
| direct_input | mixed/unclear | Event batching is elsewhere; five active windows trigger dense bincount and refractory gathers dependent on N |
| pending_delivery | roughly graph-size sensitive | E0 ~1.50/2.72/16.20 ms scans dense ring despite no delivered events; active S2→S3 rises similarly; little degree-only effect |
| linear_update | roughly graph-size sensitive | E0 ~6.56/11.07/67.21 ms; E2 ~6.39/11.13/53.52 ms, masks/refractory activity alter allowed count; degree-only case ~11.30 ms |
| spike_reset_enqueue | mixed/unclear | Strong event/activity dependence; S2-E2 degree 8→32 increases ~12.94→17.00 ms, queued edges 16360→65440; threshold scan also depends on N |
| trace | roughly fixed/per-call | Benchmark trace disabled: essentially 200 branch/hook intervals; enabled traces verified for equivalence but not ranked |
| output | mixed/unclear | Dense counts scale with N and output materialization with spikes; minor cost |
| residual | roughly fixed/per-call | Predominantly 200-step hook/loop overhead; decreases as share with size/activity |

These are qualitative observations, not a fitted model. N and input counts
co-vary in the scale series, and propagated spikes/pending counts can co-vary;
the one degree-only control helps but does not isolate every dimension. Quiet
S3 varied between the preliminary and final runs; CPU/system/cache effects remain
possible. Use the complete min/max distributions, not decimal precision as a
confidence claim.

**A019F-B — BOUNDED SYNTHETIC INSTRUMENTATION COMPLETE; MULTIPLE COST CENTERS
REMAIN PLAUSIBLE.** No one proven dominant optimization target is selected.
Linear updates dominate E0/E1; schedule_events dominates E2; threshold/reset/CSR
enqueue remains a substantial secondary center. Entire function regions contain
several concrete operations, and no fixed-event-count graph scaling is available
yet. Repeated coefficient work vs dense gathers/scatters, per-event grid validation
vs batch packing, and CSR loop vs accumulation are unresolved internally.
A019E was not reinterpreted as identifying a bottleneck.

Exactly one recommended next task:
**A019G — bounded synthetic substage instrumentation of linear_state_update()
and schedule_events(), with fixed-event-count graph scaling.** Diagnostic only;
not started. No optimization was implemented in A019F. O1 candidate operations
must preserve exact numerical/event semantics; no operation is yet selected under
all six target gates. GPU remains separately certified O2 work and was not used.

Important unknowns: full-real stage fractions, full-real event/activity mix,
full-real sparse topology and cache behavior, native instruction/allocation
attribution, and potential exact-equivalent optimization overhead. Synthetic
percentages do **not** reproduce or estimate A019D full-real percentages.

## Validation and counters

- Targeted plus selected regression suite: 16 passed. Includes 10 A019F tests,
  two parameterized continuity cases, state identity, analytic update, signed
  delay, and simultaneous events. Only named tests were executed from A011;
  none executes Arena. Existing scientific contract fixture tests are not
  scientific runs or interventions.
- Independent starting-SHA OFF replay: 3 activities × 2 chunks, exact PASS.
- `uv run python -m compileall src scripts tests`: PASS under guard.
- `git diff --check`: PASS.
- All execution counters: full-real preparations=0, real advances=0,
  A019D reruns=0, GPU runs=0, Arena runs=0, scientific interventions=0,
  downloads=0, archive writes=0.
- Accepted registered reads: connectivity=0, annotation=0, neurotransmitter=0,
  neuron metadata=0, mappings=0, provenance=0, other registered data=0.
  Fail-closed guarded accounting, not independent native byte telemetry.
- Task evidence writes are synthetic report artifacts, not archive writes.

## Closure

Authorized commit: `perf: instrument synthetic CPU advance costs`, followed by
`git push origin master`. No tag, release or version bump. Exact resulting SHA
and local/origin/live equality are verified after commit/push and reported in the
final response (the report cannot include its own commit hash without recursion).
Required final invariants: clean worktree/staging, empty stash, 0.3.0, workflows 0.
