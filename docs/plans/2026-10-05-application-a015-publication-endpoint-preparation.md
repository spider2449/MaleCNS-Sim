# Application A015 — publication endpoint preparation

## Gate and disposition

Root dynamically derived: `D:/spider/working/MaleCNS-Sim`. Starting local HEAD,
origin/master, and live GitHub master: `e195c7cc9db5d1752df1b6ca75ca929aaaa9cbbb`.
Clean worktree, empty stash, version 0.3.0, zero tracked Actions workflows.
Authoritative A014 report read: A14-MEMORY-ARCHITECTURE-CHANGE-REQUIRED, M3,
P2, CERTIFIED_SYNTHETIC. A013 remains A013-MEMORY-LIMIT; observed lower bounds
22.3891 GiB private and 20.5043 GiB working set, not recovered true maxima.

Decision: **A15-B — EARLY FILTER PROVEN EQUIVALENT; ADDITIONAL MEMORY
ARCHITECTURE WORK STILL REQUIRED**. Endpoint classification **E1** for the
publication input contract; **D1** for existing column projection; **P2** for
the implemented all-column-buffer architecture. No production default switch.
No full-real retry is proposed for execution by this task.

## Current authoritative semantics

`ProductionEngine.prepare -> task008.prepare_network ->
load_male_cns_v1_numeric -> select_publication_neuron_ids ->
project_numeric_connectome -> optional threshold_curated_projection ->
SignedAnatomicalConnectome.from_projection ->
EffectiveSignedProjection.from_signed_connectome -> PreparedNetwork ->
PreparedRuntime`.

Official mapping: annotation `bodyId`, raw `body_pre`, `body_post`, `weight`;
annotation `superclass`, `status`, `type`, `somaSide`; NT `body` and existing
prediction/confidence columns. Numeric columns must be integer, non-null, and
converted to int64; counts must be nonnegative. Validation includes excluded
rows. Annotation body IDs must be unique. NT metadata normalization and evidence
resolution remain the production implementations (including their precedence
and duplicate behavior).

The **publication neuron identity set** is precisely sorted annotation body IDs
whose `superclass` is a string with nonempty `strip()`. Status is audit-only:
Glia and missing status do not remove an otherwise included body. No biological
selection is added. It is fixed before observing edge totals or signs.

Despite the segment terminology, there is **no segment/root/body remapping** in
this path. Raw body IDs directly equal annotation IDs. Type labels, shared
superclasses, roots, or stale/merged identities do not create equivalence classes.
Distinct raw IDs cannot collapse into one publication ID under this contract.
Unknown non-null IDs are accepted raw endpoints and later excluded. Null IDs
are invalid, not silently irrelevant.

The numeric loader stably sorts pair keys, sums duplicate pair counts in int64,
and unions annotations with raw endpoints. For nonnegative IDs below 2^32 it
uses packed uint64 keys; larger IDs use structured source/target keys. Projection
uses membership at both endpoints and the existing exact integer aggregation
primitive. Neurons are ascending int64 IDs, including isolated eligible neurons.
Pairs are lexicographically source/target ordered. Self edges are retained.
Threshold `>= min_synapses` is applied **after** pair aggregation, never per row.

Signs depend on presynaptic publication IDs and frozen NT evidence/policies.
Missing evidence stays unresolved (sentinel 2); effective projection includes
assigned-sign edges, including neutral sign edges according to existing policy.
Weights are integer aggregated counts converted to float64, multiplied by sign,
then the unchanged scalar synaptic weight. Source/target positions use searchsorted
in ascending neuron IDs; effective lexsort and outgoing CSR construction are
unchanged. Anatomical CSR uses the existing sparse graph primitive. Delay is the
unchanged LIF parameter scalar/grid mapping, not a raw per-edge column.
No runtime state allocation or advance is needed for equivalence certification.

## Commutativity proof and boundaries

Let U be the annotation-derived publication universe and K(r)=(pre,post).
Let f(r) be `[pre in U and post in U]`. For every key k, f is constant on
the entire fiber `{r: K(r)=k}`. Hence the retained key fiber is either all of
that fiber or empty. Its original row order is unchanged. For every retained k,
`sum_int64(r.count for K(r)=k)` is exactly the same in reference and prototype.
Thus `FILTER(GROUP(R)) = GROUP(FILTER(R))` in scientific graph content.
This also preserves the reference int64 arithmetic behavior; no float raw-row
accumulation or tolerance is introduced. Stable grouping preserves contribution
order, including overflow behavior of the unchanged int64 primitive.

Changing packed-key radix after filtering does not change lexicographic pair
order for nonnegative IDs. The structured branch has the same pair order.
The reference packed branch lacks a negative-ID guard: the prototype detects
any negative raw endpoint and falls back to the complete reference loader rather
than claiming to repair that behavior. This preserves the reference output for
such inputs and provides no memory reduction for them.

Identity is equality, so it commutes trivially; there is no higher-level identity
relation through which an excluded row could contribute to a retained pair.
Thresholding commutes with moving endpoint filtering (not with moving threshold
before grouping). Self edges stay self edges. Same U preserves metadata/evidence
lookup and sign assignment; excluded rows never affect them. Same int64 counts
and shared float conversion preserve weights exactly. Same neuron order, pair
order, signs, parameters and downstream primitives preserve CSR, mappings,
delays and existing graph identities exactly.

Raw graph diagnostic counts/union are **not** equivalent: the prototype does not
construct the excluded raw union or count distinct excluded pairs. Its numeric
result is explicitly experimental publication content; it must not be substituted
for a general raw adapter consumer. PreparedNetwork does not carry those
projection diagnostic counts. Provenance path strings and annotation records are
preserved. A future default switch requires a separate raw-diagnostics contract
audit; this task does not authorize that switch.

## Executable oracle and fixtures

Production source is unchanged. Experimental loader is separate in
`data/experimental_preparation.py`. It uses the existing aggregate primitive,
publication selector, integer validation and original metadata loader (an empty
temporary synthetic edge file avoids copying annotation/NT normalization).
Only the synthetic script/test harness temporarily substitutes the loader in
the original prepare function, restoring it afterward. No UI or automatic dispatch.

There are **18 adversarial semantic fixtures**: 17 parametrized row fixtures
(each at thresholds 0, 4, 5) and one annotation-membership fixture. They cover
retained/retained, each excluded side, both excluded, duplicate contributions,
threshold boundary, retained self edge, unknown endpoint, unsorted input,
excitatory/inhibitory/policy-declined/unresolved sign lookup, zero/low counts, 1000 excluded
rows around one retained pair, separated contributions, large structured IDs,
empty edges, negative-ID reference fallback, whitespace superclass, retained
Glia/missing status, and distinct IDs with identical type labels. The latter
establishes why requested many-to-one identity and self-edge-after-collapse cases
are not expressible in the authoritative mapping. No fictitious mapping is tested
as if it were scientific behavior. Three additional invalid excluded-row fixtures
verify null pre/post and negative count rejection in both routes.

Exact comparison includes neuron membership/order, anatomical endpoint IDs/counts,
annotation records, sign metadata/results/masks/counts, source/target positions,
effective/outgoing weights, anatomical CSR indptr/indices/data, outgoing CSR,
node-index mapping, scalar weight, runtime identity and delay grid. Repeated
prototype output is compared exactly. Existing unsigned/signed/effective and
PreparedNetwork fingerprints are reused; no competing scientific digest added.
No mismatch and no floating tolerance. High-exclusion scales also compare exact
scientific output. All 59 A015 tests pass (final validation below).

## Representation, access and architecture

Selected membership: immutable sorted int64 U plus vectorized searchsorted and
exact equality. Logical full-scale U: 8*166700 = **1,333,600 bytes** (0.001242 GiB);
synthetic U is 100 IDs = 800 bytes. Index/boolean temporaries are separate.
Hash/set has Python-object overhead and less predictable memory. A dense bitmap
is unsuitable for sparse large body IDs. `np.isin` is exact but can choose its
own memory strategy; explicit binary search makes batch workspace visible.
Categorical lookup provides no semantic advantage over numeric index lookup.

**D1**: production Feather adapter already projects raw edges to three columns.
Minimum eligibility columns: body_pre/body_post; weight is additionally required
to validate all rows and aggregate retained ones. Annotation bodyId/superclass
defines U; other annotation and NT columns remain needed downstream. Annotation
and NT full table materialization is O(annotation), a separate smaller concern.
Current `read_table` is not a bounded source-batch reader; slicing its result
would not remove full materialization. Bounded reading needs a narrow extension
and Feather V1/V2/compression contract checks, not a storage rewrite.

| Option | Equivalence and order | Memory / work | Complexity |
| --- | --- | --- | --- |
| A: full columns, filter, group | Proven, stable retained rows, same int64 arithmetic | R-sized columns/membership; removes R-sized grouping/union | Implemented minimum equivalence prototype |
| B: bounded source batches, filter, concatenate, group | Same stable order if source batch order preserved | Bounded raw/workspace; retained rows and concatenate/group coexist; retained-row multiplicity must be modeled | One next bounded task |
| C: partial group per batch, merge | Integer sums can be exact, but needs explicit overflow/order and diagnostic proof | Bounds raw and reduces retained duplicates; repeated grouping | Deferred; not implemented |

**Chunking is required for a defensible memory envelope**, even though eligibility
itself is decidable before grouping. Selected implemented architecture is A;
selected next architecture is B. A alone removes the expensive whole-raw grouping
and raw identity union but is insufficient to support a capped real retry.
Final ownership stays unchanged: effective arrays 998,865,328 bytes (~0.930 GiB),
retained anatomical/sign arrays plus metadata ~0.810 GiB; outgoing copies
398,479,248 bytes are already within effective accounting. Final ~1.740 GiB is
comfortably below 8 GiB; compact final ownership is outside this task.

## Synthetic measurements

Fresh isolated process for every route/scale, seed 15, 100 eligible IDs, one in
ten raw rows eligible at both endpoints. Sizes 10k/100k/1M, never real source data.
Input generation occurs before pre-run sampling. Production A014 tracing is reused;
prototype function names are added on the instance, not by changing A014 code.
Snapshots are first-visit Python line samples and may miss native allocation peaks;
tracing and allocator retention affect totals. Times include tracing. One run per
cell, no statistical performance confidence claim. Whole-process peaks include
different baselines; do not fit full-real GiB from these points.

| Rows | Route | Before private / WS bytes | Sampled peak private / WS bytes | Seconds | Highest private stage |
| ---: | --- | --- | --- | ---: | --- |
| 10,000 | reference | 727232512 / 107024384 | 738394112 / 112304128 | 0.052782 | from_projection |
| 10,000 | prototype | 727048192 / 107003904 | 736501760 / 111583232 | 0.049670 | prepare_network |
| 100,000 | reference | 748195840 / 108834816 | 771993600 / 122281984 | 0.136781 | load_male_cns_v1_numeric |
| 100,000 | prototype | 749101056 / 109256704 | 767262720 / 117125120 | 0.072559 | prepare_network |
| 1,000,000 | reference | 764604416 / 108883968 | 901488640 / 228548608 | 1.438348 | load_male_cns_v1_numeric |
| 1,000,000 | prototype | 783040512 / 111251456 | 861110272 / 171458560 | 0.164020 | endpoint_membership |

Private peak reductions: 1,892,352 (0.2563%), 4,730,880 (0.6128%), and
**40,378,368 bytes (4.4791%)**. Largest working-set reduction:
57,090,048 bytes (24.9794%). Largest pre-run-adjusted private growth is
136,884,224 reference vs 78,069,760 prototype, a 58,814,464-byte decrease;
this is not a subtraction-based certification of true allocation peaks.
Time is faster in these bounded samples. The R-sized grouping/identity-union
stage disappears from the prototype; membership becomes the largest sampled
stage at 1M. Logical raw columns at 1M: 24,000,000 bytes; retained input columns:
2,400,000 bytes before duplicate collapse; membership U 800 bytes. Full line-level
raw/filter/group/final arrays and owners are retained in ignored local trace JSON.

Evidence SHA256 (ignored `data/derived/a015/<rows>-<route>.json`):

| Rows / route | SHA256 |
| --- | --- |
| 10k reference | C200F875BAAE27640F74D6C1B48792857895EA230E5E4885613536B928BD26BE |
| 10k prototype | 0EE3F5A5EC4697B803F31391472A0E38E5E02D35FEBD06439D46F934389FD05A |
| 100k reference | 476F4FC4950C5EE025F336B5864F5222EAA9A8C03B36FB601C19D1FA9A1A976C |
| 100k prototype | B2FEE835698F236872E6B9C68DBBCBF33D98171CA83747C5E1EF39698AAD419E |
| 1M reference | 383D320AC18FADB277937A35B50148736D42083ACE4D9A7F327E2259650B0405 |
| 1M prototype | D1A4C6D981281244FF14B6537E8D58DBFFCC8A69E9593D8911BB9C40CE481511 |

## Static full-scale model

R=151856684, N~166700, curated distinct C~25582938, effective E~24904953.
These are frozen prior evidence, not A015 real measurements. Let F be eligible
**raw** rows before duplicate aggregation; F is not established by C or E.

| Component | Exact logical formula / estimate |
| --- | --- |
| Required final ownership | .930 effective + .810 anatomical/sign/metadata ~1.740 GiB |
| Membership U | 8N = 1333600 bytes |
| Raw source buffers (A) | 24R = 3644560416 bytes = 3.394 GiB |
| Arrow conversion/consolidation duplication | 0..24R extra = 0..3.394 GiB; sharing is format-dependent |
| Membership temporary coexistence | approximately 16R + 2R = 2733420312 bytes = 2.546 GiB (positions/indexed values/booleans); implementation line dependent |
| Retained filtered rows | 24F; if F~C then .572 GiB; F can be much larger |
| Retained grouping explicit workspace | packed keys/sorted keys/order/starts up to 32F, sorted inputs 24F, unique output up to 24F; plus native sort workspace |
| Bounded source/chunk buffer (future B) | 24b plus Arrow duplication and membership workspace O(b); not implemented/certified |

Architecture A eligibility coexistence is approximately **5.94..9.34 GiB**
logical buffers, before baseline, metadata, allocator retention, and some masks.
Retained output can overlap source buffers during fancy indexing. Downstream
grouping scales with F and final construction has its own C/E temporaries.
Conservative predicted peak **>9.34 GiB plus overhead** on the duplicate-buffer
branch, potentially higher if F approaches R. This is a lifetime model range,
not a measured maximum or assertion every format duplicates Arrow buffers.
**P2**: implemented A still predicts >8 GiB under plausible coexistence.
**<=8 GiB proven: No**. No claim that the unexplained portion of A013's >20-GiB
lower bound has been quantitatively resolved. Synthetic reduction supports removal
of the raw grouping mechanism, not a precise real-memory bound.

## Exactly one next bounded task

**A016 — bounded Feather source-batch endpoint filtering certification (B)**.
Implement an opt-in projected batch iterator for supported local Feather formats,
validate every raw row (including excluded counts/nulls), preserve batch/input
order, concatenate only retained rows, and use existing stable int64 grouping.
Certify exact output against production and A015 across batch boundaries, duplicate
pairs, threshold boundaries, invalid excluded rows, signs/weights/CSR/digests.
Measure isolated synthetic peaks and retained-row multiplicity accounting; audit
raw diagnostic consumers and unsupported format behavior. Model a defensible
8-GiB envelope before proposing a separately authorized A015R-style real retry.
No real preparation, default switch, scientific change, final ownership change,
download, or real advance authorized. **Do not start A016 automatically.**

## Firewall and validation

A014 contained-tree Job Object watchdog is reused unchanged. Synthetic regressions
retain CERTIFIED_SYNTHETIC; no real 8-GiB enforcement certification.
Full-real preparation/advance, real Arena/behavior/experiment, Task017 units,
Task017Q, downloads, archive writes and BANC: all **0**. B archive unchanged.
Scientific model and biological identities unchanged. Historical Task016 unchanged;
Task017 unchanged / NOT_ROBUST. No tag/release/version mutation.

Validation: targeted A015 **59 passed**; A014 **12 passed** (11 watchdog + one
instrumentation), A013 **17 passed**, A011 stateful-runtime **8 passed** (combined
37 passed); existing Task008/008a **18 passed**; application suite **233 passed**;
full `uv run pytest -q` **480 passed, 14 skipped**. Skips are CUDA/unavailable-device
cases and the opt-in real-data gate, which was not enabled. Compileall src/scripts/
tests PASS; tracked integrity PASS (9 frozen tracked files and internal identities);
diff check PASS; `uv build` PASS (0.3.0 sdist and wheel). No validation accesses
the real source dataset. Final A015 publication uses the authorized master push;
the exact resulting commit and live identity are reported in the final response.
