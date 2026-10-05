# Application A018U: downstream completion budget

Authorized A018U only. Dynamically derived root: D:/spider/working/MaleCNS-Sim.
Starting local HEAD, origin/master and live GitHub master all equal
0532d65793074907c484efa57494e6afd8e3abf4. Clean worktree, empty stash,
version 0.3.0 and zero tracked workflows. A18T-B remains authoritative.

## Frozen boundary and measurement design

Start: A018T global canonical int64 source/target/count columns returned.
End: Task008 PreparedNetwork and CPU PreparedRuntime constructed, preparation
fingerprint and runtime identity available. No initial_state or advance is called.
Cache and CUDA are disabled, as in A018R. Runtime owns a projection reference;
delay/refractory grid steps are scalar calculations. State/pending arrays belong
to initial_state and are outside this preparation boundary.

The bounded loader first reconstructs publication metadata through
_publication_from_retained and the empty-edge production normalization helper.
Task008 then reads annotations/evidence, selects publication neurons, calls
project_numeric_connectome (endpoint selection and repeated canonical grouping),
optionally threshold_curated_projection, signs, constructs the anatomical CSR and
unsigned fingerprint, constructs effective arrays/outgoing structure and signed/
effective identities, accounts ownership, builds PreparedNetwork and its digest,
then constructs PreparedRuntime and reads its identity/grid steps.

A018R stopped at 600.0037853 s inside SignedAnatomicalConnectome.from_projection,
entered at 588.2287435 s. Loader, metadata/evidence setup and initial projection
had returned. The exact statement within sign construction is not recorded;
neuron resolution, edge sign-list construction, signed-count construction and the
nested anatomical CSR/unsigned digest cannot be individually assigned historical
completion status. EffectiveSignedProjection and PreparedNetwork/Runtime did not
return. A018R remains A018R-TIME-LIMIT. Its loader 574.3467865 s includes merge
549.3997919 s; source/filter/local-group timers nest inside the loader. Projection
7.7788168 s and setup 6.1008513 s are separate subsequent intervals. Known
pre-sign nonmerge = 38.8289515 s; interrupted sign work >11.7750418 s.

Only generated Feather metadata is read by the new profiler. The production
loader is temporarily substituted with generated grouped arrays. No real source
path, data scan, download or preparation is used. The skipped post-merge metadata
helper is represented by its completed historical 8.1216501-s timer, included in
the known nonmerge interval, not assigned a synthetic zero cost.

Profile the actual production bodies by compiling their AST with probes between
top-level statements. No edge-loop tracing, changed expression, optimization or
production dispatch hook. Timers exclude measured probe bookkeeping; parent
intervals still include native work and function call overhead. Nested intervals
must not be added twice. Probe snapshots enumerate visible numeric array owners
by identity, following ndarray bases. Visible element counts include aliases;
they are diagnostic counts, not distinct graph cardinalities. Logical bytes
exclude Python object payloads and allocator internals. Temporary peak bytes are
null when not directly measured, not zero. Private/working-set snapshots are
boundary samples, not peak guarantees. Transient serialization/sort allocations
are audited structurally. Uninstrumented three-repeat medians are the timing
anchor; one separately instrumented run supplies stage decomposition. Probes
remain script-only and disabled in ordinary preparation.

Frozen series: N/E = 100/1000, 2000/100000, 20000/100000, 20000/1000000.
The equal-E neuron-axis pair separates metadata scaling. Six shapes: canonical
randomly distributed source-sorted keys, adversarial shuffled input, destination
clustering, source clustering, mixed signs, all excitatory. Mixed and sorted
share keys intentionally; mixed-sign coverage is present in every non-all-exc
shape. Each grouped pair is unique; the random input challenges projection
canonicalization before signing, not a claim that random order is canonical.
Labels cover acetylcholine, GABA, glutamate, unknown and missing labels; tests
also omit evidence rows and exercise ConservativeSignPolicy. Maximum generated
N=20000, E=1000000; no approach to full-real memory.

Budget policy: separate completed historical pre-sign work from new post-sign
stage projections. Full scale N=166700, grouped E=25582938; using grouped E for
all stages conservatively covers effective E=24904953. Scale O(N) metadata by N,
edge/byte work by E, sorting by E log2 E, and mixed N/E stages by the larger
factor. Use worst measured large-safe shape rates, never fastest samples. Assess
4x downstream rate uncertainty for conservative and 8x for stress; these are
engineering sensitivity margins, not empirical upper bounds or scientific
identity. Evaluate at least 120 s conservative headroom and the stress total.
If the evidence does not support these margins, use U2/U3/U5 instead of U1.

Final profiles, candidate disposition, budgets and validation follow below.

## Stage contracts and measured costs

The sign algorithm builds an evidence dictionary keyed by string neuron ID,
resolves each neuron once, creates SignResult records, then creates sign_by_id.
Its per-edge list converts a NumPy integer to Python int and string and performs
dictionary lookup twice for assigned signs, once for unresolved signs, followed
by int8 conversion. Unknown/missing evidence remains unresolved (int8 sentinel 2);
assigned is sign != 2. Signed counts use int64 zero ownership and masked int64
multiplication. No type-to-biological-identity remapping is introduced.
Resolution selects the first present field under the existing precedence; an
explicit unknown does not silently fall through. Shiu policy maps acetylcholine,
dopamine, octopamine, serotonin to +1, GABA/glutamate to -1. Conservative policy
assigns only acetylcholine +1 and GABA -1. Other cases remain unresolved.

**S1 primary**, coupled S2 list/container allocation: the edge expression takes
0.309-0.397 s at one million edges. No separate attribution percentage for lookup
versus int/string/list work is claimed. Metadata preparation is O(N) and is not
repeated per edge; S4 is not the sign hotspot. The complete sign body excluding
nested CSR/hash takes 0.379-0.504 s at N=20000/E=1000000.

Effective weights mask out unresolved signs, map both endpoint IDs with
searchsorted and int64 conversion, then compute exactly
count.astype(float64) * int8_sign * float_scale, left to right. No multiplication
reordering or fused expression. Source/target/effective arrays are permuted by
lexsort((target, source)). Extra masked source IDs and anatomical counts remain
local owners for sums. Threshold uses integer >= after grouping; signing follows
threshold. Masks, indexing copies and original dtype/operation order are intact.

The anatomical CSR is source-row/target-column. SciPy COO-to-CSR performs its
native ordering/duplicate consolidation, with index width chosen by SciPy;
sort_indices then canonicalizes. For these shapes indices/indptr are int32;
input positions are native intp and data float64. This is not incoming CSR.
There is **no separate incoming CSR owner or preparation stage**. Tests derive
an incoming transpose only to compare indptr/indices/data exactly.
Effective outgoing arrays use int64 source/target/indptr, float64 data, lexsort
once, add.at(source+1), and cumsum. This is a second independently ordered edge
representation. Reusing canonical order or deriving a transpose is not assumed
safe merely because two sparse matrices are mathematically equal.

Outgoing target and weight copies duplicate target/effective owners, costing
16*effective_E = 398479248 bytes at historical effective E=24904953 (about
0.371 GiB). They are copied after hashing, then all arrays are frozen. They could
be shared analytically, but would change owner identity/base/lifetime assumptions;
no such correction is implemented. Neuron IDs are also copied. Metadata ownership
includes immutable evidence/resolution/sign tuples and numeric provenance; no
cache writes occur. PreparedNetwork retains the signed connectome and effective
projection; PreparedRuntime retains the effective projection reference.

Unsigned hashing covers neuron IDs and all anatomical CSR arrays, length/dtype
framed. Signed hashing covers unsigned identity, resolution/sign policy IDs,
neuron/source/target/count arrays, signs, assigned mask and all evidence/resolution
records serialized with canonical JSON. It runs three times: effective digest,
stored signed-policy identity, PreparedNetwork digest. Each signed numeric pass
scans 8N+26E bytes (about 666 MB full grouped scale), plus JSON. Effective hashing
covers policy/resolution/scale/signed identity, neuron/source/target/effective/
indptr arrays: 16N+24*effective_E+8 bytes (about 600 MB). Unsigned numeric hashing
scans about 8N+4(N+1)+12E bytes for the observed int32 CSR width (about 309 MB).
Array tobytes creates a full-array serialization temporary; the largest count/
endpoint temporary is 8E (~205 MB). Signed JSON records, JSON string and encoded
bytes also allocate; their allocator peak is not directly measured. Hash coverage
is unchanged. Combined numeric hashing throughput is about 0.39-0.53 GB/s on
these large-safe stage timers, which include tobytes and digest updates; metadata
record construction/JSON are timed separately in the statement profiles.

Stage timings below are seconds from one separately instrumented run per shape.
Ranges cover all six shapes, rather than measurement confidence intervals.

| N/E | Sign | Weight/filter | Anatomical CSR | Outgoing | Digests | Runtime |
|---|---:|---:|---:|---:|---:|---:|
| 100/1000 | .00069-.00166 | .00010-.00013 | .00024-.00040 | .00009-.00016 | .00182-.00356 | .00009-.00013 |
| 2000/100000 | .0352-.0440 | .00223-.00476 | .00377-.00465 | .00224-.01068 | .0455-.0487 | .00014-.00016 |
| 20000/100000 | .0964-.1227 | .00273-.00455 | .00420-.00533 | .00163-.01494 | .280-.328 | .00015-.00017 |
| 20000/1000000 | .379-.504 | .0394-.0836 | .0720-.0824 | .0326-.1924 | .487-.527 | .00016-.00018 |

Uninstrumented total medians: small .00577-.00620 s, medium .12593-.14919 s,
neuron-axis .66594-.70676 s, large-safe 1.37285-1.71586 s. Same-process sequential
repeats, three each; no warmup exclusion or fastest-sample selection. Fixtures
are generated outside timers. Probe bookkeeping is .49-.58% of large-safe wall
time; it dominates tiny fixtures (39-71%), whose stage timings are therefore
**not** used for full-scale rates. Large stage rates are approximate measurements,
not claimed noise-free. Final measurement matrix ran without concurrent pytest or
build. Earlier exploratory matrices were discarded after adding missing unsigned
hash probes, neuron-axis coverage, compact records and runtime timing; only the
complete final matrix is evidence. The budget alone was recomputed afterward to
add the explicitly stronger 2x historical-work stress sensitivity, without changing
timing samples. Boundary-sampled process maxima: private 1158795264 bytes,
working set 298078208 bytes; neither certifies transient or full-real peaks.

Scaling evidence: metadata/resolution/JSON strongly depend on N and metadata
cardinality/length; tenfold N at fixed E materially increases sign and digests.
Edge lookup/list, masks/copies and count operations depend on E; searchsorted also
depends on log N and source/destination locality. Anatomical native CSR costs
depend on E, row distribution and index sorting. Outgoing lexsort is conservatively
modeled E log E; clustering is much cheaper, so no universal linear-sort assertion.
add.at is E, cumsum/indptr N. Hashes depend on bytes plus JSON metadata size. Runtime
object/identity/grid-step work is O(1), with no N/E delay-array allocation. Residual
function construction and metadata destruction are represented by a 5-s full-scale
base operational allowance. Uninstrumented totals corroborate the decomposition.
The largest aggregate downstream group is digest/identity; the edge sign list is
the largest single measured expression in the all-excitatory large-safe fixture.

## Candidate and implementation gate

| Candidate | Measured hotspot/correction | Risk | Expected time/memory effect | Complexity |
|---|---|---|---|---|
| Dense sign indexing | Remove per-edge Python string lookup | Missing/sentinel/index correctness | Reduce ~.3-.4 s/million; dense N signs and temporary E positions | Small/medium |
| Reuse signed fingerprint | Avoid three identical complete hashes | Cache invalidation/identity ownership | Remove two scans/JSON runs; retain one string | Small/medium |
| Reuse canonical permutation | Avoid outgoing lexsort | Filtering/canonical order/fallback contract | Up to ~.19 s/million; eliminate E intp permutation | Medium |
| Share immutable outgoing data | Avoid two copies | Owner/base/lifetime assumptions | Small time saving; -16 effective_E bytes | Medium |
| Hash direct buffers | Avoid tobytes temporary | Exact framing/endian/order/contiguity | Reduce serialization copies; -max array temporary | Medium |

These are bounded analytic candidates, not benchmarked implementations or claimed
speedups. Exactly **D3: NO OPTIMIZATION NEEDED; BUDGET ALREADY STRONGLY SUPPORTED**.
No candidate implemented, no production or experimental scientific behavior changed.
Exactly zero downstream optimizations. AST probes alter only script-local observation;
ordinary production code and all source graph/science modules remain byte unchanged.

## Exactness certification and memory

80 targeted tests compare instrumented functions against the unmodified production
oracle, with deterministic repeats. Cover all six shapes, empty/single/small/medium
and million-edge large-safe graphs; threshold 0/5; reference and Conservative policies;
excitatory/inhibitory/unknown/missing rows; repeated types and large 19-digit int64 IDs.
Compare exact neuron/edge ordering/counts, sign arrays/masks/signed counts, evidence/
sign records/policy/provenance, float64 effective bytes, anatomical CSR indptr/indices/
data, outgoing indptr/targets/weights, unsigned/signed/effective/prepared fingerprints,
runtime identity and delay/refractory grid steps. Derived incoming CSR is exact too.
All 24 measured scale/shape fixtures additionally pass a separate untimed replay:
every nested scientific dataclass field and array dtype/shape/bytes/writeability,
saved prepared fingerprint, runtime identity and grid steps match the oracle.
Replay certification is persisted in the measurement JSON outside timing samples.
No tolerance or mathematically-equivalent-only CSR acceptance. No scientific, sign,
weight, CSR, delay, identity or biological semantics change. Delay arrays are absent
at this boundary; grid-step identity is exact. Production default stays unchanged.

Production memory delta = 0 persistent, 0 temporary, 0 permutation, 0 lookup,
0 duplicated-CSR bytes. Script probes are not installed on the experimental real
route. Before/after structural model ~5.37 GiB; planning envelope ~6.371953 GiB;
unchanged 8-GiB hard cap; P1 modeled preserved. No new full-scale >=8-GiB model.
Full-real peak <=8 GiB proven: No. Numeric-owner samples exclude object and allocator
payloads and cannot replace that nonclaim. No broad ownership redesign.

## Full-scale completion model and disposition

Use grouped E=25582938 rather than effective E=24904953 even for effective owners.
For mixed stages use max(N ratio,E ratio)=25.582938 from N=20000/E=1000000; this
intentionally over-scales the N component (actual N ratio 8.335). Outgoing also
multiplies log2(full E)/log2(synthetic E). Each base group takes the worst large-safe
shape independently, so it is not an optimistic single-fixture sum. Scalar runtime
uses its worst measured constant. Misc base is at least 5 s, far above the raw
residual projection. Digits, metadata length/cardinality, locality, allocator/cache
and extrapolation uncertainty motivate the 4x and 8x sensitivity margins; these
factors are engineering assumptions, not measured probability bounds. Signed
numeric/JSON cost is measured, not silently assigned the available deadline slack.

| Stage | Base projection s | Conservative allowance s | Stress allowance s |
|---|---:|---:|---:|
| Sign construction, excluding CSR/hash | ~13 | ~52 | ~103 |
| Effective weight/filter/mapping | ~2.1 | ~8.6 | ~17 |
| Incoming CSR | 0; absent | 0; absent | 0; absent |
| Anatomical source-row CSR | ~2.1 | ~8.4 | ~17 |
| Effective outgoing construction/sort/copies | ~6.1 | ~24 | ~49 |
| Delay/runtime-ready | <.001 | <.001 | <.002 |
| All unsigned/signed/effective/prepared digests | ~13.5 | ~54 | ~108 |
| Misc/finalization operational allowance | 5 | 20 | 40 |
| Downstream total | ~42 | ~167 | ~334 |

The historical known pre-sign 38.8289515-s interval already includes projection,
metadata helper and evidence setup. Do not add synthetic metadata/projection again.
The anatomical CSR inside sign return was NOT separately completed historically;
it is correctly included above. The interrupted >11.7750418 s is a lower bound,
not another completed interval to add. Full-scale sign body plus its nested CSR/
hash projection exceeds that lower bound; history is not reinterpreted.

A018T merge projections remain simple 28.983115 s, throughput 21.952660 s,
conservative stress 57.966230 s. Cumulative synthetic speedup 18.955857x and real
merge baseline 549.399792 s preserved. Totals below are model outputs, not real times:

| Scenario | Combination | Total s | Headroom s |
|---|---|---:|---:|
| Best estimate | Historical known + simple merge + base downstream | ~110 | ~490 |
| Throughput sensitivity | Historical known + throughput merge + base downstream | ~102 | ~498 |
| Conservative | Historical known + stress merge + 4x downstream | ~264 | ~336 |
| Stress | 2x historical known + stress merge + 8x downstream | ~469 | ~131 |

Material engineering headroom criterion: at least 120 s in the conservative model,
and no stress-envelope overrun; the stress case itself also clears 120 s. This
keeps about one fifth of the cap available for unmodeled operational variation.
With doubled historical work and stressed merge, downstream could grow about
11.14x before crossing 600 s; 120-s headroom permits about 8.26x. The chosen 8x
stress sensitivity is therefore close to the stricter 120-s-headroom boundary,
which must be considered in future authorized preregistration. Long metadata,
allocator behavior or hardware contention outside the modeled envelope can still
invalidate the projection. This is sufficient engineering model support for a
contained attempt, not a certified full-real time or memory bound.

**U1: STRONG COMPLETION MODEL SUPPORTS FULL PREPARATION <600 S WITH MATERIAL HEADROOM.**
**A18U-A: DOWNSTREAM COMPLETION BUDGET CERTIFIED; REAL RETRY MODEL SUPPORTS <600-S ATTEMPT.**
600-s completion proven: **No**. No real retry performed or authorized by A018U.

Exactly one proposal: **A018UR: Full-Real Optimized Preparation Retry**, requiring
separate explicit user authorization. CPU only; at most one full-real preparation;
A015 early endpoint filter, A016 bounded Feather reader, A017 checked local grouping,
A018 bounded staged merge and A018T blockwise NumPy merge; no A018U scientific
optimization exists to add. Corrected existing Job Object watchdog; unchanged 8-GiB
and 600-s hard caps; no stateful advances, stimulation or Arena; stop immediately
after preparation; verify exact historical graph/prepared digests. No timeout
increase, default promotion, dataset scan or real execution in the present task.

## Firewall and publication

Full-real preparations, advances, real Arena/behavioral/scientific runs, raw downloads,
Task017 new units, Task017Q and archive writes: all **0**. Historical Task016 and
Task017 unchanged; Task017 remains **NOT_ROBUST**. B:/MaleCNS-Archive unchanged.
No biological claim. No GPU, raw data, archive, workflow, tag, release or version mutation.
Publish only this plan, measurement JSON, synthetic script and A018U tests, after
all requested validation passes; commit message: perf: characterize downstream
preparation budget. Push origin master and verify all three identities/clean state.

## Final validation

Targeted A018U: **80 passed**, including million-edge exactness and 19-digit IDs.
Every measured fixture oracle replay: **24/24 exact**.
Application regression selection: **943 passed**, covering A018T **283**, A018S
**95**, A018 **97**, A018R **8**, A017 **79**, A016 **68**, A015 **59**, A014 **12**,
A013 **17**, A011 **8**, and all other application regressions. The initial literal
PowerShell wildcard pytest invocation selected no tests and was replaced with an
explicit rg-derived path array; the successful application command covers all modules.
Existing A014 contained-tree memory/time/accounting-failure watchdog tests remain
**CERTIFIED_SYNTHETIC**; no redesign. Full pytest: **1190 passed, 14 expected skips**,
one existing Feather V1 deprecation warning, **181.50 s**. Includes stateful Task011
**9 passed** and all runtime/application tests; the unenabled real gate stays skipped.
Compileall src/scripts/tests PASS; tracked integrity PASS for all 9 frozen files and
internal identities; working/staged diff checks PASS; uv build PASS for 0.3.0 wheel
and source distribution. Version remains 0.3.0; tracked active workflows **0**.
No tag/release/version change. Final commit/ref and clean-state readback is returned
in the final report rather than embedded self-referentially in this committed plan.
