# Application Task A019O — dt validation diagnostic

Authorization: `授權 A019O`. Synthetic-only, source-local, diagnostic-only.
Starting root derived by git: D:/spider/working/MaleCNS-Sim. Local HEAD,
origin/master and live GitHub master all equal
`afa4a94f3324fa997ade5b12d4cd435f29448cf6`. Worktree/staging/stash empty;
package 0.3.0; tracked workflows zero.

Plan: audit the exact dt-only source operations and all construction routes;
probe invalid-input behavior behind the existing fail-closed firewall;
instrument the unchanged source in diagnostic memory and complement with
loop-amplified timings; assess admission and value without a percentage gate;
run targeted tests and existing boundary/replay checks, compileall and diff
check; commit/push the coherent result and verify identities. No production
optimization, real-data access, simulation rerun, GPU, Arena, download, archive
write, release, tag or version bump.

## Terminal decision

**A019O-D — DT HOT-PATH CONTRIBUTION TOO SMALL; GRID-VALIDATION O1
DEPRIORITIZED. VALUE-B.** No production optimization. Preserve A019N-B:
partial cacheability does not establish a complete transformation contract.
Admission gate FAIL/incomplete. No useful admission work is selected just to
save these scalar checks. Exactly one next task:
**A019P — bounded synthetic feasibility diagnostic of linear input gathers.**
This report does not authorize or start A019P. Grid validation is deprioritized
as the present second O1 target, not proved permanently unoptimizable.

## Exact source boundary and structural work

Unchanged `dynamics/stimulus.py:13–19,152–154`: `_number(dt_ms, "dt_ms")`
rejects built-in bool with TypeError `dt_ms must be a real number`; executes
`result = float(value)`; rejects `not np.isfinite(result)` with ValueError
`dt_ms must be finite`; returns a built-in float. Then `dt <= 0.0` rejects
zero/negative with ValueError `dt_ms must be positive`. Exceptions from custom
`float` conversion propagate. There are no derived scalar constants.

For every reached event in `schedule_events`, one helper call, one bool type
check, one float conversion, one NumPy finite check, one positive comparison.
For N accepted events: N of each per call; over 24 calls, sum(N_i) of each,
or 24N only for equal event counts. Cases here: 60/200/2045 per call and
1440/4800/49080 per 24 identical calls. This is structural arithmetic only,
not a full-real event count or speed projection. Zero events means zero dt
checks; unknown neuron lookup rejects before the first event dt check.

`float(existing built-in float)` reuses the scalar; conversion from int,
NumPy scalars or other objects may produce a new float. `np.isfinite(float)`
returns a NumPy Boolean scalar (also exercised in tests); bool/positive checks
produce scalar results. No explicit ndarray allocation occurs in this dt
portion. Native allocator activity or scalar allocation counts are not measured.
A hypothetical admitted built-in scalar removes N repetitions without removing
timestamp conversion/finite checking, division, round/int, negative-step check,
reconstruction, np.isclose, endpoint comparison, packing or lookup. All event
arithmetic remains D5/D6; dt is D2 only for ordinary immutable scalars. No D1/D3.

## Lifecycle and admission matrix

dt enters through ExperimentSpec constructor/JSON decoding, engine keyword
arguments, or direct PreparedRuntime construction/default. There is no single
mandatory normalizing admission boundary. Production annotations are float;
engine helpers accept non-bool float-convertible objects. This does not mean
every such object is supported throughout the engine: raw dt is also used in
duration arithmetic, identity and state updates.

| Creation/use route | Classification | Current boundary/invariant |
|---|---|---|
| ExperimentSpec direct construction, from_dict -> _decode -> _strict, dataclasses.replace; VariantExperimentSpec base | A1 for ordinary int/float; A2/A5 possible numeric subclasses | Frozen model validates `_finite(..., positive=True)` at models.py:268, but discards returned float; does not normalize retained dt. Service forwards raw spec.dt_ms to engines |
| PreparedNetwork factories / construction | Not a dt carrier | task008.py:124 has no dt field; graph preparation cannot admit a caller's later dt |
| PreparedRuntime(projection, parameters, dt), default dt; dataclasses.replace | A3, A4; A5 for custom conversion | Frozen slots, no __post_init__. Constructor retains raw input and permits zero/NaN/string; normal assignment forbidden, nested custom object state mutable |
| initial_state | Validation before state allocation, not admission | LIFParameters.grid_steps normalizes locally through lif._finite, validates positive and parameter alignment; original runtime field unchanged |
| advance / dense simulate_lif | A3 entry; defensive validation before events/state mutation | grid_steps at lif.py:499, duration at 510; schedule at 526; state access/allocation at 539 onward; local normalized dt is not propagated as runtime invariant |
| sparse simulate_lif_sparse_reference | A3 entry; defensive validation | Same parameter/duration checks at 740/751 before scheduling at 764; does not construct an admitted runtime |
| CUDA API / _prepare_stimulus (static inspection only) | A3 entry; defensive checks | Raw dt keyword; parameter grid/duration checks and shared scheduling; no universal CPU-runtime admission route. No import/execution of CUDA |
| schedule_events / PoissonStimulus.generate direct | A3, A5 | Public module functions normalize/check within _grid_steps, per event or generated duration; schedule zero-event path performs no dt validation |
| Benchmark/certification/test helpers | A3/A4 | A013, A018R/U/UR, A019F/J and application tests instantiate PreparedRuntime directly, often literal 0.1; literals do not enforce constructor admission |
| Internal simulate_lif runtime at lif.py:539 | A4 constructor route | Constructed after validation/scheduling, but no independent invariant; direct callers can bypass this preceding route |

Search covered constructors/call sites in src/scripts/tests, dt validators,
public application architecture and tests. No alternate runtime factory seals
the constructor. Arena's constructor was inspected as a call site only; no
Arena run. Normal built-in scalar dt cannot change through ordinary assignment
after runtime construction. Frozen dataclasses do not recursively freeze custom
objects, and deliberate object.__setattr__ bypass is not an admission guarantee.

Application JSON accepts finite int/float numbers, excludes bool, and checks
positive/alignment; original Python field type is retained. NumPy float64 .1
works in bounded engine probes. NumPy float32 .1 has a different exact value and
fails parameter alignment; int 1 fails 1.8-ms delay alignment. Numeric string
"0.1" works in scheduling and initial_state but fails duration division during
simulate_lif, so it is not full-engine supported input.

An isolated **float subclass**, within the declared numeric family, with a
stateful __float__ returns .1 then .2. Direct schedule accepts it and produces
steps [0,25] for timestamps [0,5]; repeated conversion is observable and nested
state is mutable even in a frozen runtime. This demonstrates accepted helper
behavior, not a new claim of documented full-engine support for arbitrary
conversion objects. Public documentation does not specify a subclass exclusion
or prove that changing this behavior is outside contract. A5 remains unresolved.

## Invalid-input semantics

All cases can be retained in a directly constructed runtime before rejection.
Machine evidence records exact current exception messages for each entrypoint.
Zero/negative: ValueError `dt_ms must be positive`; NaN/+inf/-inf: ValueError
`dt_ms must be finite`; built-in bool: TypeError `dt_ms must be a real number`.
initial_state rejects in grid_steps before allocation. Direct dense execution
rejects these at parameter grid validation before scheduling/state mutation;
all state dataclass fields are compared exactly on failure. Direct schedule
rejects at its first reached event; empty schedules return {} even for invalid
dt. Unknown IDs have lookup precedence. Earlier constructor validation changes
runtime existence, zero-event behavior and precedence; preservation is not proved.
Scheduling mutates only local batches prior to any later failure; immutable input
events remain untouched; no state is passed to scheduling.

Pre-existing A019N test explicitly constructs invalid dt=0 then expects
initial_state ValueError matching `positive`. A019N boundary regression compares
exact exception type/message at scheduling. Task005 tests grid-alignment/unknown
neuron messages, and A002 tests application invalid timing/spec exceptions.
No pre-existing requirement was found asserting that *all* invalid dt must be
rejected specifically in scheduling; this does not establish permission to
change existing tested constructor/initialization timing. Public error timing is
not documented as non-contractual. Proposed earlier admission therefore fails
both preservation/proven-noncontractual alternatives pending a separate decision.

## Admission safety gate

| Requirement | Status |
|---|---|
| Normalize exactly once at a mandatory boundary | FAIL: no current universal boundary |
| Finite/positive enforced there | FAIL at construction; later defensive checks exist |
| Immutable runtime-visible normalized scalar | PARTIAL: built-in scalars frozen; custom nested state not sealed |
| All routes admitted or retain defensive checks | PARTIAL: later defensive validation exists; no admitted fast path |
| Preserve supported conversion semantics | UNPROVED: accepted subclass behavior is observable |
| Unchanged valid schedule arithmetic | PASS for retained A019N split and source-local instrumentation; no admission transformation proved |
| Invalid behavior preserved or noncontractual | FAIL/incomplete: earlier errors change tested lifecycle |
| No state/event aliasing | PASS for diagnostic instrumentation and retained regression; no cache added |
| O(1) cached metadata | Feasible scalar only, not implemented |
| Exact replay certification | Available regression coverage; not certification of a new admission boundary |

Overall FAIL/incomplete. PreparedRuntime construction is the narrowest potential
owner for runtime-only admission, but is **not currently a proved safe boundary**.
Configuration parsing misses direct engine/runtime routes; PreparedNetwork has
no dt; a helper can be bypassed. No new boundary or persistent metadata is added.
No new admission prototype is justified by lifecycle evidence or measured value.

## Source-local timing and value

Diagnostic compiles the exact existing _grid_steps source in memory and inserts
two clock reads around only dt helper/positive checks. It temporarily substitutes
this helper and restores in finally; tracked source remains unchanged. Existing
schedule _timing boundary encloses the whole helper plus endpoint check. A local
recorder measures this boundary; per-event samples include clock overhead.
Alternating original/instrumented ordering, three warmups and 15 paired repeats
use one constant 4096-neuron/32768-edge graph/runtime, .1 dt and 200 steps.
Schedules use existing E2-style times [0,5,10,15,19.9], 12/40/409 target neurons.
No advance timing or real execution. Exact packed arrays/order are compared for
every instrumentation pair. Raw distributions and all per-event samples are
in [a019o-dt-validation-evidence.json](a019o-dt-validation-evidence.json).

| Events | Original whole grid median ms | Nested static dt median ms | Instrumented event remainder median ms | Nested fraction | Original schedule median ms | Added instrumentation median ms |
|---|---:|---:|---:|---:|---:|---:|
| 60 | .8692 | .0679 | .9362 | 6.801% | .9683 | .0980 |
| 200 | 2.8272 | .2108 | 2.8575 | 6.888% | 3.1187 | .2341 |
| 2045 (A019G E2 event count) | 29.5963 | 2.2260 | 29.5836 | 6.961% | 32.4436 | 1.5674 |

Remainder = instrumented grid minus nested static interval, not subtraction
from original baseline; it includes inserted clock/append overhead. Separately
computed medians need not add up. Original grid also includes boundary timer
overhead, so none of these is a claimed uninstrumented production cost.

Loop-amplified exact dt helper/positive expressions: 15 runs of 20000 iterations,
empty-loop subtraction, median .945035 microseconds/iteration, range
.915775–.988790. Wrapper/dispatch overhead remains. Empty timer-pair median
.100 microseconds. These intervals comfortably exceed timer resolution; nested
static estimates of roughly 1.05–1.13 microseconds/event are consistent in
scale with loops. The measured nested fraction is an overhead-inclusive
approximation, not exact production attribution. A loop-based scale comparison
to original grid is roughly 6–7%, not a speedup estimate. Full sample variation,
empty-loop times and added instrumentation costs remain in evidence.

**VALUE-B:** real measurable work, but approximately one microsecond per event
within roughly 14–15 microseconds of grid validation, and about 2 ms in the
high-event ~32-ms scheduling case. Most localized grid cost remains event
dependent. Saving this small scalar portion requires a new normalization/error
lifecycle contract across bypasses and conversion semantics. That complexity
is not justified here. This judgment uses magnitude, stable small fraction and
contract burden together, with no invented percentage threshold. Measurement
reliably establishes a small contribution; exact production fraction and total
speedup are unproved. The earlier 88–90% localization refers to the entire grid
substage and does not imply dt checks dominate it. No full-real projection.

## Verification and accounting

Targeted A019O + A019N suite: 8 passed. A019N's retained test-only split is a
regression only: 55 exact boundary/outcome comparisons; duplicate order;
fresh A/B states; two consecutive chunks; three delay configurations; exact
state/output bytes, nonempty pending rings, cross-state nonaliasing. This is
not a new admission prototype or admission certification. A019O adds exact
instrumentation outcomes at both nextafter neighbors, out-of-tolerance boundary
offsets, scalar variants, invalid lifecycle and state preservation, conversion
subclass and seven deliberately denied registered categories.

Guard installed by sitecustomize/mandatory guarded_child before workload imports
or pytest collection. Both evidence runs and targeted validation are guarded;
compileall uses the same entrypoint. Evidence runner uses only in-memory graph
fixtures. Across two evidence runs and two targeted suite runs: 32 completed
bounded synthetic advances (two valid dense probes per invalid-probe run,
plus twelve A019N replay advances per suite run), and 36 rejected dense calls
(nine per invalid-probe run, including numeric-string duration failure).
No scientific inference. Full-real preparations=0,
real advances=0, A019D/A019L reruns=0, GPU=0, Arena=0, interventions=0,
downloads=0, archive writes=0. All seven accepted registered-read categories=0.
Qualifier: **fail-closed guarded accounting, not independent native byte telemetry**.

Final targeted suite: 8 passed in 1.13 s. Guarded
`uv run python -m compileall src scripts tests`: PASS. `git diff --check`:
PASS. Changed scope is exactly this report, machine evidence, diagnostic script
and targeted tests; production src unchanged. No broader tests or real execution.
Commit/push custody is reported in the final response.
