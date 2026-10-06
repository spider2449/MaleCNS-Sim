# Application Task A019P — input gather feasibility

Authorization: `授權 A019P`. Synthetic-only and feasibility-only. Starting
root derived with `git rev-parse --show-toplevel`:
`D:/spider/working/MaleCNS-Sim`. Local HEAD, origin/master and live GitHub
master equal `98e1854c10bfb42442bb198e110d5ccce9fb7f68`.
Worktree/staging/stash empty; package 0.3.0; tracked workflows zero.

Plan: inspect the current gathers and mask/cardinality lifetime; prove copy
ownership and structural payloads; evaluate compression, shared integer
indices, existing scratch reuse and full-array masking; run isolated source
clones and exact selection/arithmetic/writeback/chunk/state replay probes;
use a bounded interleaved local cost check; record one terminal decision and
one next task; run targeted guarded tests, compileall and diff check; commit,
push and verify identities. No production optimization or real/GPU execution.

Preserve A019O-D / VALUE-B and grid-validation O1 deprioritization. A019H
gather means remain G1 0.308 ms, G2 1.716 ms, G3 15.052 ms, with G3
28.323% of linear update. This supports neuron-count sensitivity, not
independent edge sensitivity or a full-real percentage. Preserve A019I's
HIGH relevance/burden, PARTIAL specificity, MEDIUM exact confidence/risk,
HIGH validation burden and NOT_READY historical classification.

## Terminal decision

**A019P-C — NO SAFE OR USEFUL GATHER O1 TRANSFORMATION JUSTIFIED.**
Exact compact replacements are feasible, but the concrete lower-allocation
paths are locally unfavorable for the measured, nearly full selections.
This is a decision about the current CPU O1 target, not a universal claim
that integer gathers can never help. Sparse G3 take is modestly favorable
in this microprobe; it does not justify production optimization of this
target. No second O1 target is ready. No production runtime file changed.

Exactly one next task: **A019Q — evidence-only decision on ending the current
CPU O1 line versus beginning GPU equivalence/certification work.**
This diagnostic does not authorize or start that task or any GPU execution.

## Exact current source and selection lifetime

`src/malecns_sim/dynamics/lif.py`, dense `simulate_lif`, line 611:
`input_v, input_g = v[allowed], g[allowed]`. Both sources alias the state's
`v_mV`/`g_mV`, contiguous float64[N]. The identical bool[N] mask is
`allowed = (step > refractory_until) | refractory_free_mask` (601).
K is the number of true entries. Each selected result is float64[K], in
ascending source-position order, Boolean advanced indexing, owns its data,
`.base is None`, and shares no source memory. Synthetic probes assert these
facts including empty direct selection. Two owning result arrays exist on
the taken production branch, with 8K bytes each, 16K total. Empty production
selection skips the branch and allocates neither result. These are structural
array/payload facts, not native allocator event counts or tracemalloc evidence.

`np.any(allowed)` (605) precedes both gathers; it supplies nonemptiness only,
not K. `linear_state_update` (614) reads the gathers without mutating them;
the A019J membrane scratch arithmetic follows coefficients, then membrane,
then synaptic decay. Gather references are explicitly deleted (615), before
ordered indexed writeback `v[allowed] = updated_v`, then `g[allowed] = updated_g`.
The A019J scratch tuple is allocated at 560, before the timestep loop; its
two float64[N] arrays are disjoint and private to this advance. No gathered
input escapes the linear call. Public state/result arrays retain their existing
ownership. The sparse-reference caller is outside this measured dense target.

Mask lifetime: **M5**, combining M4 timestep/dynamics-dependent comparison
with a per-advance static refractory-free override. Position/identity determines
which override entries are set by validated refractory-free neuron IDs.
Current absolute `step = state.timestep + local_step` and mutable
`state.refractory_until` determine the dynamic component. Spikes set refractory
deadlines after the linear update. Prior chunks preserve those deadlines and
the timestep offset. Graph, event activity and pending deliveries affect the
mask indirectly through state/spikes, not through a direct edge/event lookup
in this expression. K can fall on refractory onset and rise on deadline expiry;
the override forces its selected neurons to remain allowed. Neither graph
identity nor a previously cached mask guarantees current K.

No equivalent count or integer selection is available at this point. Earlier
delivery masks have the same form but exist only conditionally and supply no
cardinality. Later `fired_positions` is a different selection and occurs after
writeback. Current Boolean indexing internally determines shape; K becomes
available as gathered `.size` only after allocation. Compression needs a new
`count_nonzero` O(N) pass for `buffer[:K]`. Integer take obtains K from newly
materialized `flatnonzero(allowed).size`: full-mask count/packing work and
np.intp[K] storage, not a free existing index or reusable static selection.

## Structural G1/G2/G3 payloads

One unchanged synthetic 20-ms/200-step advance per established G case,
12 stimulated neurons, degree 8. Every step took the linear branch.

| Case | N / mask bytes | Observed K (step counts) | K/N range | Each gather bytes | Paired bytes per step | Paired cumulative payload |
|---|---:|---|---|---:|---:|---:|
| G1 | 128 | 116 (92), 128 (108) | .90625–1 | 928–1024 | 1856–2048 | 391936 |
| G2 | 4096 | 4084 (92), 4096 (108) | .9970703125–1 | 32672–32768 | 65344–65536 | 13089536 |
| G3 | 32768 | 32756 (92), 32768 (108) | .9996337890625–1 | 262048–262144 | 524096–524288 | 104839936 |

Evidence also records legal refractory-state masks for K=0, 1, N/2, N-1, N
at each N: set refractory deadlines above the current step on unselected
positions and below it on selected positions, with no override. Each has
N mask bytes and 8K bytes per gathered source. Empty selection is tested in
the actual source clone and skips all linear gathers. Actual consecutive
chunk replay exercises changing K, deadlines, spikes, pending events and
output order. Count diagnostics are instrumentation, not proposed production
work or a rerun of A019D/A019L.

## Candidates and exact implementation boundaries

A — `count_nonzero(mask)` and paired `np.compress(mask, source,
out=private_buffer[:K])`: the installed NumPy **2.5.3** accepts exactly sized
float64 views for K=0 through N and preserves order and bits. The view itself
does not allocate a variable-sized float payload. However, NumPy's matching
version source `PyArray_Compress` calls `PyArray_Nonzero` then
`PyArray_TakeFrom(..., NPY_RAISE)` independently for each source. The latter
forces an output copy even with `out`. Therefore this API still creates
variable float buffering, also constructs two index payloads and adds the
external count scan. Reject as an allocation-removal mechanism. There is no
`mode` argument to bypass compression's buffered take.

B — one new ascending `np.flatnonzero(mask)` np.intp[K] index, reused for
`np.take(v, indices, out=v_buffer[:K], mode="clip")` and the corresponding
g take. On this platform np.intp is 8 bytes. Indices are uniquely selected,
nonnegative and strictly below N by construction; duplicates cannot occur.
Clip's differing invalid-index policy is unreachable under that internal
contract. Both sources, destinations and indices are contiguous, aligned,
same required dtype; source/destination memory is disjoint. Matching NumPy
source does not force the float output buffer copy in this case. Default
`mode="raise"` would do so and is rejected. Packing is paid once for both
sources, but cannot survive a changing mask. It replaces two float result
payload allocations with one integer payload allocation, not all copying:
16K float bytes still must be read/written, plus 8K index payload and two
index traversals. Exact semantics solved; local cost fails the selection gate.

C — both existing scratch buffers have N capacity and are available at gather
time. Reusing *both* as their corresponding inputs fails: multiplication of
original g by the membrane coefficient overwrites scratch[1], then decay
rereads that changed g. A bounded counterexample confirms unequal decay
bytes. Swapping buffers would instead overwrite g during voltage subtraction.
No safe two-buffer reuse is claimed. A concrete voltage-only hybrid is safe:
shared new flatnonzero indices, take v into `membrane_scratch[0][:K]`, leave
`g[allowed]` as the independent second gather. First voltage subtraction can
read/write the same element in place; later arithmetic never rereads the
original v. Exact byte replay confirms the unchanged ufunc sequence and
writeback order. It removes one float result allocation with no new advance
buffer, but adds 8K indices and leaves 8K g payload. Local cost is unfavorable.

D — eager full-array arithmetic then masked writeback is rejected: an
unselected v=+inf, g=-inf raises FloatingPointError under `np.errstate(all="raise")`
where selected-only computation succeeds. It also evaluates six arithmetic
operations across N rather than K. Ufunc `where=mask` would need a separate
six-operation masked arithmetic/writeback contract and six full-mask
traversals; sparse work expands from K traversal toward N. It is only a
PARTIAL, HIGH-risk alternative here, not exact-certified or selected. No
production implementation or broad benchmark was attempted.

NumPy primary references: [compress API](https://numpy.org/doc/stable/reference/generated/numpy.compress.html),
[take API](https://numpy.org/doc/stable/reference/generated/numpy.take.html),
[matching 2.5.3 implementation](https://raw.githubusercontent.com/numpy/numpy/v2.5.3/numpy/_core/src/multiarray/item_selection.c).
Source/API analysis establishes buffering under these contracts; it does not
measure independent native allocation counts.

## Exact probes and isolated replay

`scripts/diagnose_application_a019p.py` requires the active firewall before
workload imports. Test-only source clones replace the gather statement and
insert private buffers; production source files and all downstream arithmetic,
writeback, event, pending and state statements remain unchanged. No model
parameter is changed. Compression, paired clip take and voltage-only scratch
reuse pass 18 selection cases: empty, one, sparse, mixed, alternating, full.
Byte comparisons cover repeated values, positive/negative zero, subnormal
values, distinct positive/negative quiet NaN payloads, signaling NaN, +/-inf.
Gather bits are unchanged; arithmetic's possible NaN quieting is compared
against the same production operations rather than promised absent.

Each candidate passes three consecutive 20-ms chunks on independent A/B
states, with initial changing refractory deadlines and synthetic conductance.
Every state/result field is compared exactly, including pending rings/counts,
spikes, timestamps, traces, fingerprints and output order; no tolerance.
Observed K includes 77, 85, 116, 120, 128. Fresh state remains unaffected;
a further fresh-state advance and a fully refractory empty-branch advance
exercise isolation. Retained scratch references prove four distinct advance
owners without relying on recycled allocator addresses. Direct probes verify
gather order, exact membrane/decay and indexed writeback bytes. Both-scratch
corruption is a candidate rejection, not a change to scientific/model semantics.

## Narrow local cost check

15 retained interleaved rounds, three warmups, 100 repetitions per operation,
alternating forward/reverse ordering. Private destination allocation is outside
timing. Raw ns samples, external count, index construction and destination-only
paired take timing are in machine evidence. Baseline and candidate totals are
timed directly; separate component medians are not added to manufacture totals.
Shared Python prototype dispatch is included, so these are local choice/rejection
measurements only, not production speedup or full-real estimates.

| N / selection / K | Baseline us | Compression us | Paired clip take us | Voltage scratch hybrid us |
|---|---:|---:|---:|---:|
| 4096 / sparse / 41 | 3.111 | 7.892 | 5.729 | 5.926 |
| 4096 / mixed / 2730 | 22.722 | 38.067 | 28.637 | 27.532 |
| 4096 / dense / 4055 | 8.414 | 49.606 | 38.554 | 24.759 |
| 4096 / full / 4096 | 7.559 | 49.526 | 37.969 | 24.036 |
| 32768 / sparse / 328 | 14.620 | 20.128 | 12.442 | 17.047 |
| 32768 / mixed / 21845 | 160.715 | 247.180 | 186.035 | 181.602 |
| 32768 / dense / 32440 | 58.495 | 347.457 | 261.940 | 170.171 |
| 32768 / full / 32768 | 53.553 | 355.532 | 269.279 | 175.865 |

At G3, external count costs about 1.7 us and index construction 6.7–21.2 us;
paired take destination writes alone cost 5.339–245.648 us (see exact raw evidence).
Dense/full degradation remains substantial before adding advance buffer setup.
The present target's observed density is even nearer full than the dense probe.
Sparse take's modest advantage prevents any blanket rejection of the mechanism,
but does not make it competitive on the measured target. No two competitive
choices remain for this O1 target, so A019P-D is not selected. Semantics are
solved for B and voltage-only C, but their current dense local disadvantage
is clear rather than an unresolved cardinality tradeoff; A019P-B is not selected.

## Memory and lifetime contract

No candidate needs persistent PreparedRuntime or SimulationState storage.
Baseline retains the existing 16N-byte A019J scratch per advance and 16K-byte
paired gathered payload per taken call. A/B prototypes add two private
advance-local float64[N] destination buffers, 16N bytes, allocated once for
that advance's fixed N, no growth/resize, released on return/error. Views live
only through linear evaluation/writeback and may be overwritten next timestep.
A adds sequential internal np.intp[K] indices and float64[K] buffered outputs
for each compression; cumulative construction is 16K index plus 16K float
bytes, in addition to destination writes and the cardinality scan.
B adds one 8K-byte integer payload per call and no new float result payload
under the verified clip/contiguous/nonalias contract. C's safe voltage-only
hybrid adds zero advance buffers and per-call 8K integer plus 8K g payload;
it reuses the already-owned first scratch buffer. All indices expire with the
gather helper; no cached selection, cross-state owner or persistent alias.
D eager would use full-N outputs/scratch rather than compact arithmetic;
the masked-ufunc variant has no certified owner/cleanup contract. No result
retention or state mutation beyond existing writeback is introduced.

## Candidate scorecard and selection gate

All rows have HIGH measured relevance and HIGH validation burden.

| Candidate | Allocation reduction | Extra mask/index work | Specificity | Exact confidence | Lifetime confidence | Risk | Local direction | O1 |
|---|---|---|---|---|---|---|---|---|
| A compression | LOW | HIGH | CONCRETE | HIGH | HIGH | MEDIUM | UNFAVORABLE | NOT_READY |
| B shared-index clip take | HIGH | MEDIUM | CONCRETE | HIGH | HIGH | MEDIUM | UNFAVORABLE for target | NOT_READY |
| C voltage scratch only | MEDIUM | MEDIUM | CONCRETE | HIGH | HIGH | MEDIUM | UNFAVORABLE | NOT_READY |
| C both scratch | HIGH intended | MEDIUM | CONCRETE | LOW | LOW | HIGH | UNCLEAR | NOT_READY |
| D eager full arrays | HIGH intended | HIGH full-array work | CONCRETE | LOW | MEDIUM | HIGH | UNFAVORABLE | NOT_READY |
| D masked ufuncs | HIGH intended | HIGH full-mask traversal | PARTIAL | LOW | MEDIUM | HIGH | UNCLEAR | NOT_READY |

B/C voltage solve selection order, float bits, known K/owner, unchanged
downstream order, isolation and exact test-only replay. Both fail gate 3:
new index/take work is not beneficial for the established dense target. A
also fails gate 2 because buffered float results remain; C both fails exact
semantics; D lacks exact-certified arithmetic and a concrete admitted contract.
Thus no candidate satisfies all eleven selection requirements. Main remaining
uncertainty is transfer of local timings to other densities/hardware; no
production, edge-independent or full-real performance conclusion is made.

## Firewall and validation

Every Python workload, test collection and compileall uses the existing
sitecustomize firewall plus mandatory guarded_child entrypoint, activation
`MALECNS_A019C_R2_FIREWALL=1`, PYTHONPATH `scripts/a019c_firewall`.
Only source code, safe tracked task documentation, in-memory arrays and newly
created diagnostic artifacts are inspected. No registered-data catalog or
registered path discovery is invoked. Seven deliberately nonexistent paths
under the denied data root prove fail-closed rejection before content reads.
Accepted reads in all seven categories are zero. Full-real preparations,
real advances, A019D/A019L reruns, GPU, Arena, interventions, downloads and
archive writes are all zero. Documentation pages were read through the web
tool; no dataset/package/source checkout or artifact download was performed.
Qualifier: fail-closed guarded accounting, not independent native byte telemetry.

Targeted validation: **20 passed** (`test_application_a019p.py`,
`test_application_a019j.py`, `test_application_a019c_r2_firewall.py`).
The diagnostic evidence runner completed successfully. Compileall:
**PASS**, using `uv run python` with guarded_child `-m compileall src scripts tests`
to preserve mandatory pre-import enforcement. No full-real benchmark or GPU.
Diff whitespace check: **PASS**. Authorized closure scope is exactly this plan,
its JSON evidence, the synthetic diagnostic script and its targeted tests.
Commit message: `perf: assess linear input gather optimization feasibility`.
Push is to origin/master; local/origin/live identities and clean
worktree/staging/stash are verified after push and reported with the commit SHA.
Version remains 0.3.0, tracked workflows zero; no tag/release/version bump.
