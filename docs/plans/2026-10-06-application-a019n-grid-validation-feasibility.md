# Application Task A019N — Grid-validation feasibility

## Authorization, gates, and plan

User authorization: `授權 A019N`. Synthetic-only, feasibility-only; diagnostic,
tests, documentation, commit and push authorized. Root derived using
`git rev-parse --show-toplevel`: D:/spider/working/MaleCNS-Sim.
Starting local HEAD = origin/master = live GitHub master =
`f2ce4c705822b4cc074085ee3585ebe97e111dba`.
Worktree clean; staging empty; stash empty; version 0.3.0; tracked workflows 0.

Plan: verify gates; inspect exact source and caller boundaries; use existing
fail-closed firewall before workload imports/collection; probe dependencies and
isolated split equivalence; classify candidates; run targeted tests, compileall
and diff check; commit/push and verify custody. No production changes.

## Terminal result

**A019N-B — GRID VALIDATION PARTIALLY CACHEABLE; TRANSFORMATION CONTRACT STILL
INCOMPLETE.** No concrete second O1 selected. Preserve A019M-B and A019L-L1 / P2,
1.094710500 s per 20-ms call, 54.735525x slowdown. A019G's approximately 88–90%
is a synthetic scheduling proportion, never a full-real proportion.

## Exact source map and dependencies

Boundaries refer to unchanged starting source `src/malecns_sim/dynamics/stimulus.py`.
The grid_validation timer encloses lines 183–185: `_grid_steps` plus endpoint
comparison, not lookup, append, packing, delay validation, or ring scheduling.

| Operation and boundary | Inputs and result | Classification | Allocation / structure |
|---|---|---|---|
| `_number(time_ms, "spike time")`, 151 via 13–19 | bool rejection; float conversion; finite test; scalar float | D5 event-dynamic | Scalar conversion/NumPy finite scalar; no explicit ndarray construction |
| `_number(dt_ms, "dt_ms")`, 152 via 13–19 | bool rejection; float conversion; finite test; scalar float | D2 for normalized immutable built-in float runtime dt; otherwise D6 conversion can have dynamic behavior | Scalar conversion/finite test; no structural arrays |
| `dt <= 0`, 153–154 | validated dt; positive predicate / exception | D2 under same admission | Scalar comparison |
| `int(round(value / dt))`, 155 | timestamp and dt; integer step | D6: D2 dt + D5 timestamp | Scalar division, rounding, integer conversion |
| `steps < 0`, 156 | event-derived integer; predicate | D5 | Scalar comparison; short circuits isclose |
| `steps * dt`, 156 | integer and dt; reconstructed float | D6: D2 dt + D5 step | Scalar multiply |
| `np.isclose(value, steps * dt, rtol=0, atol=1e-10)`, 156 | timestamp, reconstruction, fixed tolerances; Boolean | D6: static tolerances + dynamic operands | NumPy internal temporary allocation not counted; no sorting/grouping |
| Exception formatting, 157 | offending timestamp/dt/name | D6, failure-only | String creation; no mutation |
| Return step, 158 | event-derived integer | D5 | Scalar return |
| `step >= duration_steps`, 184–185 | event step and current chunk endpoint; predicate / exception | D6: D5 step + D4 duration | Scalar compare, failure string |

All listed computations are pure/deterministic for ordinary admitted numeric
inputs, mutate nothing, and depend on neither topology, PreparedNetwork, state,
absolute simulated time, pending contents, neuron IDs, nor synaptic delay.
There is no D1 or D3 grid-validation result. D4 duration is chunk length, not
absolute start time. Direct arbitrary float-convertible objects can execute
conversion code; frozen outer dataclasses do not prove immutable nested inputs.

Outside this substage: lines 175–180 perform searchsorted neuron lookup against
an int64 ID array (D6 graph IDs + event neuron ID); 189 groups/appends by event
step; 194–201 sorts step keys and constructs int64 positions and float64 unit
weights, two arrays per occupied step. Those outputs are mutable fresh arrays.
Stimulus constructors at 34–42 and 55–65 sort times and schedules and preserve
duplicate times. Their schedule tuples are immutable under normal API use.

Immediate callers: dense `lif.simulate_lif` line 526 and sparse reference line
764. Dense preparation validates parameter grids at 499 and duration at 510;
input identity is computed before scheduling. State/pending access begins after
scheduling, at 539–546. `PreparedRuntime` is frozen (425–469), but has no
`__post_init__`: construction alone does not guarantee positive finite normalized
dt. `initial_state` and `advance` subsequently validate configuration.
Poisson generation calls `_grid_steps` at stimulus.py:114; A019N does not alter it.

## Recomputation and lifetime evidence

Machine-readable results: [a019n-feasibility-evidence.json](a019n-feasibility-evidence.json).
A1/A2 equivalent payload and B fresh-state context have identical intermediate
values and schedule digests. State is absent from schedule_events' signature;
fresh-state independence is additionally exercised in full synthetic replay.
Each three-event call repeats three dt conversions/checks, timestamp checks,
roundings, reconstructions and isclose calls. Three occupied bins construct six
packing arrays; repeated results are distinct objects with nonaliased buffers.
C duplicates an event (four helper calls); D changes timestamp (different step);
E changes dt to 0.2 (5 ms becomes step 25); shortening duration rejects the same
otherwise grid-valid 19.9-ms event. Partial rows before exceptions are retained.
Counters describe source operations and successful packing, not native allocator
telemetry. No claim of NumPy-internal allocation count or measured byte telemetry.

| Value | Narrowest safe reuse | Exact invalidation / sharing |
|---|---|---|
| Normalized positive finite dt fact | Per-call local now; PreparedRuntime only after a specified validating constructor boundary | New dt/configuration or non-normalized conversion object invalidates; ordinary float fact independent of fresh states, time, pending, events and selection |
| Fixed tolerance metadata | Module literal / per-call local | Already constants; no substantial cache work |
| Event conversion, integer step and grid predicate | Per-payload/per-call local | Timestamp values and dt invalidate; event count/order changes traversal |
| Endpoint acceptance | Per-call local | Duration/grid-step endpoint invalidates even if stimulus/dt identical |
| Neuron lookup / packed batches | Per-call local under present contract | ID array content/order and event neuron selection invalidate; mutable arrays can alias; packing is outside measured target |

Repeated identical payloads need not imply a runtime-static result. Caching full
batches would require an event-payload key, duration, graph IDs and dt, plus owned
immutable outputs or defensive copies. Identity-only caches can retain stale
references; graph ndarray buffers are not made immutable by a frozen runtime.
An unbounded key cache retains all activity history. No such cache is recommended.
No pending/state references are needed for scalar dt metadata. A scalar contract
would cost O(1) retained memory, with object overhead unmeasured. No event-array
cache or shared mutable state is implemented. Reuse across consecutive 20-ms calls
and fresh states is safe for admitted dt facts only; dynamic event/endpoint checks
must continue. Source/destination selection and delays do not invalidate dt facts,
but require their own independent validation outside this substage.

## Isolated prototype and exact checks

`split_grid` is diagnostic-only and temporarily substituted inside the diagnostic
process, restored in `finally`. It retains the original division, Python round,
integer conversion, multiply, np.isclose constants, negative-step and endpoint
checks. It admits built-in positive finite float dt, otherwise calls the complete
original validator. Admission remains checked per event: this is an equivalence
prototype, not an optimization or speed measurement. Moving admission earlier is
specifically the missing lifecycle contract; direct API error timing and zero-event
behavior must remain intact. No reciprocal multiplication substitution is proven.

55 boundary/outcome pairs compare exact packed arrays (dtype, shape, bytes, ordered
keys) on success and exact exception class/message on failure: zero/one/duplicate
and repeated-neuron events; sorted canonicalization of unsorted inputs; 0, 5, 19.9,
20 ms; nextafter neighbors of 5; offsets beyond 1e-10; dt 0.1/0.2/zero/negative/NaN/
bool. Explicit duplicate ordering at step 50 is [0, 0, 1]. No toleranced prototype
comparison is used; existing production isclose semantics are retained verbatim.

Three delay configurations (0, 1.8, 20 ms) each compare two independent states over
two consecutive 20-ms chunks: exact result dataclass fields and all state arrays,
including pending contents/counts, spike order/times, traces and runtime/schedule
identity. Pending events are nonzero, including carryover exceeding a chunk.
These are bounded representative delay/ring sizes: the API has no finite maximum
supported delay and no heterogeneous per-edge delay-bin configuration. No claimed
exhaustive maximum or unsupported multiple-delay-bin API coverage.

## Concrete candidates and scorecard

Columns: relevance, reusable fraction, specificity, exact confidence, invalidation,
persistent memory, validation burden, risk, readiness.

| Candidate | Relevance | Reusable | Specificity | Exact | Invalidation | Memory | Validation | Risk | O1 |
|---|---|---|---|---|---|---|---|---|---|
| C1/C4 normalize and validate built-in float dt once at runtime boundary, retain all event checks | LOW (localized but contribution unmeasured) | LOW structurally / cost UNKNOWN | PARTIAL | MEDIUM (prototype HIGH within admission) | LOW after constructor contract | LOW O(1) | MEDIUM | MEDIUM | NOT_READY |
| C6 memoize timestamp-to-step by exact timestamp/dt key | HIGH substage localization | UNKNOWN payload repetition | PARTIAL | MEDIUM | MEDIUM | HIGH if unbounded | HIGH | HIGH | NOT_READY |
| C2/C5 cache neuron positions/structural indexes | LOW: outside grid timer | UNKNOWN event selection | PARTIAL | LOW without buffer immutability | HIGH | MEDIUM | HIGH | HIGH | NOT_READY |
| C3 cache delay bins | LOW: absent from target | HIGH for configured delay | UNCLEAR for this target | LOW target applicability | LOW | LOW | MEDIUM | MEDIUM | NOT_READY |

For N events, scalar dt split could remove N repeated `_number(dt)` calls (bool,
float, finite) and N positivity comparisons, replacing them with one guaranteed
boundary validation. N event conversions, roundings, grid reconstruction/isclose
and endpoint checks remain. Frequency is N per explicit payload per 20-ms call,
not a proven full-real N. No explicit grid arrays/copies are eliminated by this
split. Timer localization alone does not identify what fraction is dt validation.
C6 adds hashing/key lookup, bounded eviction/ownership policy and payload retention;
no current workload repetition distribution proves relevance or safe memory bound.
C2/C5 and C3 do not remove the localized measured operations. Removing timestamp
finite/alignment/endpoint checks is rejected because callers can violate them.

Second O1 gate fails specificity/lifecycle and validation-contract completeness;
no cache owner is approved for implementation. Main uncertainty: relative cost of
static dt checks versus event-dynamic scalar isclose, and exact earlier admission
contract that preserves direct API behavior. Production speedup remains unproven.

Exactly one next task:
**A019O — bounded synthetic source-local diagnostic of dt-validation contribution
and runtime admission contract.** This is a diagnostic, not authorization to
implement an O1, rerun real data, or broaden the task.

## Execution accounting and validation

Guard active before workload imports/test collection through mandatory
`guarded_child.py` and `sitecustomize`, with MALECNS_A019C_R2_FIREWALL=1 and firewall
PYTHONPATH. Seven deliberate category checks reject registered paths before
content access. Diagnostic runner and targeted suite each perform 12 synthetic
advances (48 total across two suite runs and two evidence runs); bounded graph 128 neurons / 1024 edges, no preparation route.
No timing matrix or speed benchmark. All seven accepted registered-read categories
are 0. Full-real preparations, real advances, A019D/A019L reruns, GPU, Arena,
interventions, downloads and archive writes are each 0.
Qualifier: fail-closed guarded accounting, not independent native byte telemetry.

Targeted `tests/test_application_a019n.py`: 3 passed on final suite; initial two-test suite also passed. Evidence runner PASS.
`uv run python -m compileall src scripts tests` via guarded entrypoint: PASS.
`git diff --check`: PASS. No broader suite or real-data-dependent tests.

Commit/push custody will be recorded by the final response; no tag, release or
version change. Expected final changed scope is this report, evidence, diagnostic
and targeted test only.
