# A019I bounded synthetic allocation/lifetime feasibility

Authorization: user explicitly authorized A019I, including diagnostics/tests/report
commit and push. Starting local HEAD = origin/master = live GitHub master =
`7bea40680fcb27e3682c0eddaba6226f01a2adbf`. Root derived by
`git rev-parse --show-toplevel`: D:/spider/working/MaleCNS-Sim.
Worktree, staging and stash empty; package 0.3.0; tracked workflows zero.

Plan: verify gates; inspect the three source regions and immediate callers;
activate the existing fail-closed firewall before Python imports/collection;
probe ownership and structural payload sizes; test an isolated exact-order
workspace prototype; score candidates; record one target and next task;
run guarded targeted tests, compileall and diff check; commit/push and verify.
No production implementation, scientific model or benchmark contract changes.

Classification: **A019I-B — FIRST CPU O1 TRANSFORMATION READY; MEMBRANE TARGET SELECTED.**
Preserve A019H-B and its residual reduction from 17.4–31.4% to 1.930–8.885%.
Instrumentation remains OFF by default. No new timing study was performed.

## Source and ownership map

Source: `src/malecns_sim/dynamics/lif.py`, unchanged at the starting SHA.
Dense caller: PreparedRuntime.advance (438–457) -> simulate_lif ->
linear_state_update (129–178). Dense candidate spans: mask/gathers/writeback
581–606; membrane expression 157; synaptic decay 162. Alternate caller:
simulate_lif_active around 787–797, not the measured dense runtime route.

N = 128 / 4096 / 32768 for G1/G2/G3; K = count_nonzero(allowed), 0 <= K <= N.
The following counts exclude ndarray headers, allocator padding, scalar Python
objects, NumPy iterator internals and unrelated event/trace operations.

| Object / expression | Type / elements | Allocation, view, copy, alias | Producer / consumer / mutation / lifetime / reuse |
|---|---|---|---|
| state.v_mV, state.g_mV | float64[N] each | persistent owned runtime arrays; local v/g alias state | initial_state -> direct input, linear caller, firing, trace; mutable across advance calls; never use as scratch |
| state.refractory_until | int64[N] | persistent runtime array | reset -> mask comparisons; mutable across calls; not scratch |
| refractory_free_mask | bool[N] | allocated per advance, independent | setup -> OR mask; read-only thereafter; advance lifetime |
| step > refractory_until | bool[N] | new comparison result, no state alias | comparison -> OR; expression lifetime; potentially reusable but outside selected target |
| allowed = comparison OR free mask | bool[N] | new independent result; no integer index array | OR -> any, gathers, assignment, firing; iteration/advance local; retained until reassignment |
| input_v=v[allowed], input_g=g[allowed] | float64[K] each | two new Boolean advanced-index copies, owned and independent | dense caller -> linear arithmetic; read-only; released by del after return; workspace reuse needs different packing primitive |
| np.asarray(input_v/input_g) | float64[K] | identical object in this ndarray path, no copy | expression consumers only; no independent lifetime/storage |
| t1 = v - rest | float64[K] | new independent array | subtract -> multiply; expression lifetime |
| t2 = t1 * exp_m | float64[K] | new independent array | multiply -> add; expression lifetime |
| t3 = rest + t2 | float64[K] | new independent array | add -> final add; expression lifetime |
| t4 = g * coefficient | float64[K] | new independent array | multiply -> final add; expression lifetime |
| v_next = t3 + t4 | float64[K] | new independent array | add -> tuple -> updated_v -> v[allowed]; read-only output |
| g_next = g * exp_s | float64[K] | new independent array | decay -> tuple -> updated_g -> g[allowed]; read-only output |
| updated_v, updated_g | float64[K] references | alias returned arrays, not runtime state | dense writeback copies values; locals persist until next result assignment or function return |
| returned tuple | two references | small new Python tuple, no payload copy | caller unpack; call-return lifetime |
| coefficients / dt | scalar numbers | scalar calculations and np.isclose internals | linear function; per-call lifetime; no neuron-sized payload |
| active_positions | int64[A] | np.fromiter new array from a set | alternate caller -> refractory gather and position gather; unique positions, set iteration order retained |
| alternate refractory gather / comparison / OR | int64[A], bool[A], bool[A] | advanced-index copy and independent masks | alternate caller -> allowed_positions; iteration lifetime |
| allowed_positions | int64[K] | active_positions[allowed] new copy | alternate gather and writeback; unique subset in original order; iteration lifetime |
| alternate v/g gathers | float64[K] each | integer advanced-index copies | linear consumer and writeback; independent; alternate route not optimized |

NumPy advanced indexing produces copies; Boolean 1-D selection traverses selected
positions in increasing array order. The probes establish OWNDATA, shares_memory
false and np.asarray identity for the current ndarray inputs, including empty
selection. A basic slice of each prototype scratch buffer is a view and aliases
only its private owner. No inference from process-memory deltas is used.

Output lifetime is particularly important: current outputs remain referenced
across iterations, but the dense caller never consumes previous updated arrays
after both assignments. Private scratch may therefore be overwritten only at
the next update, after those writes complete. It must belong to one advance,
not a global cache or publicly returned reusable linear_state_update result.
The public scalar/general-array function must retain its existing independent
output behavior. Concurrent advances must never share a workspace.

## Allocation and structural scaling

Exact observed ndarray payload sizes are in `a019i-feasibility-evidence.json`.
Creation counts and pass counts below are source-derived semantic counts,
not allocator-level telemetry. Copied gather payload = 16K bytes; writeback
assigned payload = 16K bytes. Internal scatter buffering is UNKNOWN; absence
of an explicit ndarray allocation does not prove zero native allocations.

| Full selection upper bound, per update | G1 | G2 | G3 |
|---|---:|---:|---:|
| N / fixed scheduled events | 128 / 60 | 4096 / 60 | 32768 / 60 |
| two gather arrays, 16N bytes | 2048 | 65536 | 524288 |
| membrane five allocation payloads, 40N bytes | 5120 | 163840 | 1310720 |
| decay output, 8N bytes | 1024 | 32768 | 262144 |
| two scratch buffers, 16N bytes | 2048 | 65536 | 524288 |
| one mask, N bytes | 128 | 4096 | 32768 |
| comparison + OR cumulative payload, 2N bytes | 256 | 8192 | 65536 |
| writeback assigned values, 16N bytes | 2048 | 65536 | 524288 |

Two persistent state arrays occupy 16N bytes; refractory state 8N bytes;
refractory-free mask N bytes per advance. Dense linear selection uses no
integer-index payload. Integer alternate selection adds 8A and 8K bytes plus
its refractory gather/masks. K varies with refractory activity: these are
bounds and controlled empty/full/mixed probe sizes, not claims of actual
full selection throughout G advances.

Membrane evaluation is already native vectorized NumPy: subtract, multiply,
add rest, multiply g, final add. Five K-sized ufunc passes and five arrays;
four intermediate arrays plus one output. Decay adds one pass and output.
The final addition can have t3, t4 and output simultaneously alive (24K bytes).
Across expression evaluation, allocation payload totals are not peak live
memory. Paired gathers scan the N mask twice and copy two K payloads; writeback
scans it twice and writes two K payloads. No edge traversal occurs here.
No independent edge sensitivity or full-real scaling claim is made.

## Feasibility by candidate

Input gathers: Boolean indexing, always independent copies in this path.
Consumers only read them, so writable independent input storage is not required.
NumPy Boolean indexing has no destination argument. Replacing it with flatnonzero
plus take(out=) requires an additional intp[K] index, mask scan and packing;
take may internally buffer (especially default raise mode). Buffer reuse can
reduce visible allocations but does not establish removal of comparable work.
Computing over all N using where= avoids packing but changes traversal, evaluates
different lanes unless every operation is masked, and changes scratch/writeback
design. It is a separate, insufficiently specified transformation here. No
reduction occurs in the linear arithmetic; retaining elementwise operation order
is still required. Read-only input views alone cannot express arbitrary masks.

Membrane M1/M2: two private capacity-N float64 buffers sliced to K, out= ufuncs
in the exact original operand/order sequence. Buffer a holds subtract, multiply,
rest addition, final v; buffer b holds g contribution, then g decay after final
v has consumed that contribution. No scratch overlaps input or runtime state.
The prototype keeps coefficients and equal-tau branch unchanged. It removes
six per-call result payload allocations (48K bytes cumulative) after workspace
setup; it retains all six arithmetic passes. No fusion or model change is needed.
M3 reassociation/FMA/expression fusion can change rounding and is rejected as
an exact O1 target. M4 changed integration/model/parameters is forbidden.

Writeback: `v[allowed]=updated_v` followed by `g[allowed]=updated_g` performs
assignment to original arrays, not a persistent gathered destination. Same
float64 dtype, disjoint source arrays, unique Boolean-selected destinations,
no duplicates or reduction. Current implementation already creates no explicit
writeback result ndarray. np.putmask repeats/truncates values according to its
different value-alignment rules; np.copyto(where=) needs N-shaped compatible
sources and does not accept arbitrary K-shaped packed outputs. Integer scatter
would require index creation; no concrete removable work is established.
Alternate active indices are unique because they originate from a set, but
general repeated-index replacement must preserve assignment behavior. Probe
shows repeated-index assignment differs from np.add.at accumulation; alternatives
that accumulate, reorder duplicate writes or change casting/aliasing are rejected.
Original assignment order is retained by the selected membrane proposal.

## Isolated prototype and validation burden

`scripts/diagnose_application_a019i.py` is outside the production path. Its
Workspace is installed only temporarily in-process during synthetic probes,
restoring the original function in finally. No production file is edited.
No prototype timing or production speedup claim.

Exact dtype/shape/byte comparisons: G1/G2/G3 at 60 events, two 20ms chunks per
case, every state/result dataclass field including traces, pending/refractory
state and event outputs; empty/full/mixed masks; strict step > refractory_until
boundary with refractory-free override; equal/unequal taus; signed zeros,
infinities, NaNs, subnormals; explicit scratch/input overlap rejection.
These prove bounded feasibility on the current NumPy/platform, not universal
bitwise equivalence for every public input type/platform. Runtime caller inputs
are contiguous float64 gathers. A019J must preserve public scalar, arbitrary
array and active-caller behavior, error behavior, instrumentation ON/OFF replay,
continuation, per-advance ownership, variable K and exact starting-SHA replay.
No global workspace and no output escaping before scratch reuse are acceptable.

## Candidate scorecard and target gate

| Candidate | Importance | Allocation/copy | Specificity | Exact confidence | Validation | FP/order/alias risk | O1 readiness |
|---|---|---|---|---|---|---|---|
| A input gathers | HIGH | HIGH | PARTIAL | MEDIUM | HIGH | MEDIUM | NOT_READY |
| B membrane | HIGH | HIGH | CONCRETE | HIGH within dense float64 scope | MEDIUM | LOW with private ownership | READY |
| C indexed writeback | HIGH | LOW explicit allocation, HIGH assigned payload; native UNKNOWN | UNCLEAR | LOW for replacement | HIGH | HIGH for alternate scatter | NOT_READY |

A019H G3 linear shares: gathers 28.323%, membrane 25.603%, writeback 22.294%.
G1/G2/G3 gather means: 0.308/1.716/15.052ms. E0/E2 showed no material positive
activity sensitivity. These historical task evidence measurements are reused,
not remeasured. Importance is HIGH for the large bounded case, not all sizes.

All eight target gates pass for membrane: directly measured material work;
five concrete avoidable membrane allocations; exact ordered out= sequence;
bounded bitwise equivalence; private lifetime/alias contract; unchanged model
and benchmark; exact replay is testable; gather/writeback alternatives are less
specific. Material work removed is allocation/deallocation, not arithmetic
passes. Actual speedup and allocator overhead remain unmeasured and uncertain.
The decay output reuses consumed membrane scratch as a lifetime consequence,
not a separately selected optimization target.

Exactly one next task: **A019J — bounded CPU O1 optimization of the ordered
membrane ufunc expression using two private per-advance float64 scratch buffers
and out=, reusing the consumed g-contribution buffer for decay, with exact replay
certification.** Do not start A019J automatically.

## Validation and closure

Guarded targeted tests: 15 passed (A019I plus A019C-R2 firewall tests). Diagnostic
runner PASS. Firewall active before imports and collection; denial tests cover
all seven categories before content access. compileall src scripts tests PASS;
git diff --check PASS. Accounting qualifier: **fail-closed guarded accounting,
not independent native byte telemetry**.

Execution counters: full-real preparations=0; real advances=0; A019D reruns=0;
GPU runs=0; Arena runs=0; interventions=0; downloads=0; archive writes=0.
Accepted registered reads: REAL_MAPPING=0; REAL_PROVENANCE=0;
REAL_NEUROTRANSMITTER=0; REAL_ANNOTATION=0; REAL_CONNECTIVITY=0;
REAL_NEURON_METADATA=0; REAL_OTHER_REGISTERED_DATA=0.
Synthetic evidence-file writes are diagnostic artifacts, not archive writes.

Authorized closure includes exactly this report, diagnostic script, targeted
test and machine-readable evidence. Production/model optimization: No.
No tag/release/version bump; 0.3.0 and zero workflows retained. Final commit
identity, push equality and clean state are reported after push to avoid
self-referential commit hashes in this file.
