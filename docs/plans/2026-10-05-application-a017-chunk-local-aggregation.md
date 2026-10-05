# Application A017 — deterministic chunk-local integer aggregation

## Gate and scope

Starting local HEAD, origin/master and live GitHub master were all
`e279873333eae9a61fa23215d3e343262d47970a`. Worktree clean, stash empty,
package 0.3.0, tracked workflows zero. The A016 plan records the required
**A16-B — BOUNDED FEATHER BATCH FILTERING CERTIFIED; RETAINED/GROUPING MEMORY
REMAINS BLOCKER**, P2. Its 2,318 physical batches, maximum 65,536 rows,
required body_pre/body_post/weight columns, exact validated endpoint filtering
and source order remain authoritative. No real payload was inspected in A017.

This is an opt-in integer aggregation seam, with synthetic execution only.
Production dispatch, graph/runtime ownership, threshold, signs, weights,
delays, LIF, Arena and watchdog implementation are unchanged.

## Reference reconstruction

A016 `retain_edge_batches` validates every row before publication endpoint
filtering, retains owned numeric batch triples, concatenates once, and invokes
`_aggregate_numeric_edges` in `male_cns_v1.py`. Key: ordered
`(body_pre, body_post)`, never an undirected pair or cell type. Raw Arrow schema
is int64; `_integer_column` converts integer columns to int64, rejects nulls and
noninteger types; negative counts are rejected even on excluded rows. Negative
endpoints invoke the existing full-source reference fallback, including its
historical packed-key behavior. The release domain has non-negative endpoints.

`weight` is an integer synapse count/contribution associated with an endpoint
pair, not a floating scientific weight. A row can already contain multiple
synapses; duplicate pair rows add those counts, rather than counting rows.
Zero counts and self edges remain present at grouping. Both production loader
and projection group duplicate keys. Shared grouping uses stable sort of a
provably reversible uint64 packed key when its bounds allow it, otherwise
structured int64 pair keys. Output is lexicographic source then target,
with int64 source, target and `np.add.reduceat` int64 counts.

Reference overflow behavior is NumPy int64 modular wrap, without an explicit
overflow guard. It is NOT arbitrary-precision arithmetic. Multiple wraps can
return a positive value, so merely checking for negative grouped outputs is
insufficient. This observation is synthetic; no assertion about real maximum
grouped count is made.

Threshold is applied to the globally grouped projected counts using `>=`.
Sign lookup, signed counts, conversion to effective mV weights, CSR and delay
grid mapping follow that shared path. No chunk-local threshold, sign lookup,
floating conversion or self-edge removal is permitted.

## Algebra and overflow contract

For a pair k, partition its non-negative integer contributions into batches.
If its full mathematical sum is <= 2^63-1, every subset/intermediate sum is
also <= 2^63-1. Integer addition is associative and commutative on these
bounded sums. Therefore summing each batch then summing its partials equals
one global reduction, independently of partition and scheduling. Duplicate
keys are combined once globally; canonical sorting restores reference order.
Empty batches are the identity. Self keys obey the identical proof. Applying
threshold and scientific transformations only after this sum gives the same
downstream inputs. Endpoint filtering commutes with grouping because membership
depends exclusively on the two key endpoints; validation does not commute with
filtering and therefore remains upstream.

The exact accumulator/output dtype is **int64**, not int32. A single supported
row may be 2^63-1; tests use contributions above 2^32. Neither int32 safety nor
an unconditional real int64 mathematical bound follows from the available
metadata. R=151,856,684 and per-row bound 2^63-1 do not prove grouped safety.
No new real scan estimates maximum weight or count.

The local primitive proves safety dynamically. After lexsort and run boundary
detection, group length L and maximum contribution M establish safety when
M <= floor(INT64_MAX/L). Potentially unsafe groups use bounded numeric 32-bit
limb sums in blocks of 65,536, combining only block totals as Python integers
(no Python object per raw row). Low limbs are <=2^32-1 and high limbs <=2^31-1,
so each block's uint64 limb sums are <2^48 and <2^47 respectively. Their
recombination is an exact Python integer. If that exact sum exceeds
INT64_MAX, the primitive raises OverflowError before int64 reduction. Safe
groups are reduced with int64 `np.add.reduceat`. A large total over distinct
pairs is allowed; no overly restrictive whole-table bound is used.

Modulo 2^64 addition is also associative and commutative, so the reference's
wrapping aggregation admits a separate modular proof. To preserve the entire
reference loader behavior without promoting modular wrap to a scientific
count contract, overflow in the experimental loader explicitly falls back to
unchanged A016. Tests include `[INT64_MAX, INT64_MAX, 3]`, whose reference sum
wraps to 1, at batch sizes 1,2,3. This fallback is NOT a bounded A017 run and
inherits A016 raw retention. Negative endpoint fallback is likewise unchanged.
All memory/lifetime claims here refer to admitted non-negative, non-overflow
A017 runs. Fallback occurrence is flagged in metrics. No fallback was observed
in the synthetic scale measurements. Safe-domain aggregation is exactly proven;
full-real mathematical overflow safety is not proven.

## Local aggregator and representation

Selected local mechanism: `np.lexsort((post, pre))`, numeric run boundaries,
checked integer run reduction. It avoids unproved packed-key assumptions and
reuses the reference reduction semantics. Existing grouping would require
additional overflow auditing and key storage; structured unique/reduce adds
key temporaries; packed keys require reversible bounds. Selection is based on
explicit arithmetic and ownership, not a speed contest.

Each partial is three owned one-dimensional int64 arrays:
body_pre, body_post, count, 24 bytes per unique pair. Canonical order is ascending
pre then post. The list stores one triple per nonempty batch, not one Python
tuple/dict per raw row or edge. Empty runs are not retained. Local rows <= retained
rows <= physical batch rows <= admitted configured maximum. No worker scheduling
is introduced. Reordering partial runs gives the same sorted safe integer output.

## At most three merge alternatives

| Alternative | Memory and temporaries | Determinism / complexity / scaling |
| --- | --- | --- |
| A: concatenate partials, final group | 24P retained, coexistence during concat <=48P; numeric global grouping workspace grows with P | canonical exact safe sums, O(P log P), minimal vectorized implementation; P=sum of batch unique rows |
| B: k-way sorted merge | 24P partials, O(batch count) cursor/heap plus 24C output; input/output still coexist | canonical key and run tie break; O(P log batch count); Python per-output loop would threaten 600-s budget without native implementation |
| C: bounded multi-stage fan-in | local runs plus merge-level overlap; in-memory hierarchy still retains all unique keys in worst case | canonical safe sums, repeated reductions O(P times levels); needs explicit level/ownership/budget design |

**Only A is implemented experimentally.** It establishes the seam and strong
duplicate-case benefit with simple numeric operations. The minimum candidate
removes accumulated raw row ownership, but does not remove worst-case global
cardinality/workspace. `merge_integer_runs` concatenates partial columns, clears
the run list before grouping, and performs the same checked local primitive.
No threshold is applied. Disk spill/external sort is not implemented or authorized.
No claim A is a bounded full-scale merge is made.

## Downstream reuse and scientific equality

The only shared helper change adds a default-false `grouped` argument to
`_publication_from_retained`. A015/A016 still call the original aggregation.
A017 supplies already-grouped columns; metadata normalization is reused, then
the unchanged production preparation path performs projection/grouping,
threshold, signs, weights, CSR and runtime construction. This does not eliminate
the downstream projection regroup; it remains part of the conservative model.
No default production loader dispatch references A017.

Fixtures compare against BOTH unchanged full-source production and A016. The
comparison checks neuron order, grouped keys/counts, threshold-selected topology,
CSR indptr/indices/data, effective and outgoing weights, presynaptic/neuron signs,
NT records, signed counts/masks, projection/prepared fingerprints, runtime identity
and parameter delay grid. Runtime construction is synthetic; no stateful advance
is needed or performed by A017 certification.

22 table fixtures cover one/two/every-batch pairs, many tiny contributions, start/end
duplicates, all-same, all-unique, empty retained batches, globally crossed threshold,
globally missed threshold by one, counts above int32, self edges, retained/excluded
mix, large IDs, zero counts, empty dataset, single row and a dense small graph.
Additional tests cover invalid excluded null/negative rows, risky but safe int64
sums, local and merge overflow, unsigned bounds, reversed run order, repeated merge,
100k unique retained pairs, lifetime, production default, and overflow fallback.
Batch sizes 1,2,3,7,65536 vary physical partitioning without changing source order.
Reversing run/source order additionally establishes commutativity of grouping.
The lifetime test also writes real Arrow IPC physical partition lengths
(1,1,3) and (3,1,1) over exactly the same five source rows and compares results.
There are 79 targeted pytest cases, including 66 fixture/threshold cases.
All admitted exact comparisons pass; first mismatch: none. Explicit primitive
overflow rejection is intentional, with full loader reference fallback tested.

## Threshold proof

`[2,3]` split into chunks gives partials below 5 but global total 5, retained.
`[2,2]` gives global total 4, excluded at threshold 5. The lifetime observer sees
four independent partial counts of 1 merged to 4, including an intervening
excluded batch. No partial is filtered by count. Tests run thresholds 0,4,5
and compare the full scientific outputs, not only counts.

## Memory lifetime and instrumentation

Source table -> integer conversion arrays -> endpoint mask -> current retained
copies -> local owned aggregate. Table/conversions/mask/retained copies are deleted
before partial accumulation and before reading the next batch. Observer weakrefs
prove previous table, mask and retained copies are dead at the next observation
and after completion. Partial arrays do not reference retained buffers; owndata
and dtype are asserted. Reader admission and source lifetime remain A016-certified.

Metrics record source-column bytes, mask bytes, current retained peak, current
aggregate peak, accumulated partial rows/bytes, concatenated merge input,
conservative merge workspace, final table bytes, local grouping, accumulation
and merge time. Fresh-process Windows sampling every 1 ms records peak private
bytes and working set; before/after samples are included. These are sampled
process peaks, not guaranteed capture of every native allocator transient.
The logical merge workspace bound is 104P bytes excluding the concatenated
24P input, including numeric ordering/check/reduction/output temporaries, and
excluding native sort overhead. Thus total merge envelope is 128P plus overhead.
The final output is also listed separately; adding it again in the full model
is conservative rather than a claim all components coexist.

Downstream time is total preparation minus loader time; it includes production
projection regroup/CSR/state. Loader time includes metadata and filtering.
Recorded local/merge/accumulation timings are disjoint internal phases, but do
not sum to loader time. Reference has no chunk-local grouping or partial merge;
its batch filter/copy/concat times are recorded separately.

## Scale measurements and compression

Fresh child process per route/scale/pattern, synthetic Feather files only,
100k, 1M, 3M raw rows, physical batches 65,536. Patterns:
high=90% excluded with 10 retained keys; moderate=90% excluded with 1,000
retained keys; unique=90% excluded with unique retained pairs;
cardinality=50% excluded with unique retained pairs. Synthetic universe 2,000.
The last graph has 1.5M retained unique pairs. 24 observations / 12 paired
fingerprint comparisons are retained in `2026-10-05-application-a017-measurements.json`.
All paired prepared fingerprints are exact. Detailed array equivalence is tested
separately at up to 3M rows and 100k unique pairs.

The sampling run overlapped repository pytest, so time results are indicative
and include shared-machine scheduling noise. Each process's private/working-set
measurements remain process-specific. Input generation precedes the baseline;
allocator retention can influence whole-process peaks. Do not extrapolate small
private-byte differences as guaranteed memory savings.

At 3M rows the compression retained_raw_rows / sum(partial_unique_pairs) is
**652.174** high (300,000/460), **6.522** moderate (300,000/46,000), and **1.000**
for both unique patterns. Individual full batches have high ratios about 655.3,
moderate about 6.553, unique 1; the last shorter batch lowers the whole-run ratio.
At 100k/1M: high 500/625, moderate 5/6.25, unique 1. These are synthetic
structures, not evidence of likely real duplication.

| 3M pattern | A016 private bytes | A017 private bytes | A016 working set | A017 working set | Ref seconds | A017 seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| High | 779,218,944 | 774,438,912 | 130,867,200 | 122,605,568 | .2768 | .2487 |
| Moderate | 772,263,936 | 766,984,192 | 130,125,824 | 122,667,008 | .2609 | .2516 |
| Unique, 90% excluded | 805,900,288 | 808,534,016 | 158,920,704 | 163,438,592 | .5220 | .5507 |
| Unique, 50% excluded | 974,663,680 | 970,158,080 | 321,044,480 | 320,663,552 | 1.7961 | 1.9868 |

High-case absolute private reduction 4,780,032 bytes (0.6134%); working-set
reduction 8,261,632 bytes (6.3130%). Moderate improves, but unique 90%-exclusion
private and working set increase. Worst observed process peak is reference
974,663,680 private / 321,044,480 working set versus A017 970,158,080 /
320,663,552; private reduction 4,505,600 bytes (0.4623%), working set
380,928 bytes (0.1187%). Memory benefit is structure-dependent.

| 3M pattern | Raw retained bytes avoided as cross-batch owners | Partial bytes | Merge workspace bound | Final table bytes | Local seconds | Merge seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| High | 7,200,000 | 11,040 | 47,840 | 240 | .014904 | .000220 |
| Moderate | 7,200,000 | 1,104,000 | 4,784,000 | 24,000 | .012440 | .001435 |
| Unique, 90% excluded | 7,200,000 | 7,200,000 | 31,200,000 | 7,200,000 | .020621 | .028738 |
| Unique, 50% excluded | 36,000,000 | 36,000,000 | 156,000,000 | 36,000,000 | .108026 | .182297 |

Partial accumulation is .000031..000046 s in these 3M runs. Unique-case CPU
cost increases due to doing two sorts, and remains unbounded at real P. The
dominant residual logical stage is global cardinality / sort and downstream
projection/CSR ownership. Synthetic observed process peaks can instead be
dominated by interpreter/native baseline and allocator retention.

At 3M rows, loader / downstream times in seconds are respectively: high
reference .217189/.059616 and A017 .183151/.065548; moderate reference
.197353/.063574 and A017 .188328/.063305; unique 90%-excluded reference
.196640/.325375 and A017 .226084/.324629; unique 50%-excluded reference
.308139/1.487974 and A017 .502448/1.484388. Downstream scientific code is shared.

## Full-scale conservative model

Frozen A016 facts: R=151,856,684; N~166,700; C~25,582,938 curated distinct
pairs; E~24,904,953 effective edges; final state ~1.740 GiB.
Eligible raw rows F remain unknown: C <= F <= R. Let P=sum of batch-unique
retained pair rows. Then C <= P <= F, regardless of global duplication.
No real scan supports a measured/likely P. Synthetic high/moderate ratios
cannot be imported into this graph: for F=R, even the absolute theoretical
best global compression is R/C~5.936, and batch-local compression can be worse.

| Component | A017 estimate |
| --- | --- |
| Source/conversion/membership batch | unchanged ~4.125 MiB; ~5.397 MiB including universe; native decompressor/metadata extra |
| Current retained rows | <=24b =1.5 MiB |
| Current local aggregate | <=24b =1.5 MiB, owned, not both added twice to workspace |
| Local aggregate workspace | conservative <=104b =6.5 MiB, excluding current retained input; native sort extra |
| Accumulated partials / concatenated merge input | 24P=.572..3.394 GiB |
| Partial concat coexistence | <=48P=1.144..6.789 GiB; partial owners released before final sort |
| Merge workspace | 104P=2.478..14.708 GiB, excludes 24P input, includes output allowance; native sort extra |
| Final grouped table | 24C~.572 GiB, reported separately |
| Final prepared ownership | ~1.740 GiB, unchanged |

Conservative combined envelope: 128P + 24C + 1.740 GiB plus bounded
source/chunk terms and baseline/native/metadata/allocator overhead. Best
theoretical P=C gives ~5.362 GiB plus overhead; worst P=F=R gives
**~20.415 GiB**, or ~20.42 GiB with source allowance, plus overhead.
This is a conservative envelope, not an observed real peak or all-components
simultaneity claim. It is deliberately stricter than A016's 80F grouping model
because lexsort/check arrays have explicit allowances. The A016 prior envelope
~4.218..16.449 GiB remains historical and unchanged; comparing conservative
envelopes does not assert A017 would actually use more memory on real data.

**P2 — still predicts >8 GiB in the conservative branch. <=8 GiB proven: No.**
Optimistic theoretical duplication fits the numerical cap before overhead, but
neither the real P nor timing is known. Partial concat alone can approach 6.789
GiB. A017 does not justify a real retry proposal or default promotion.

## Decision and exactly one next task

**A17-B — AGGREGATION CERTIFIED; ADDITIONAL BOUNDED MERGE ARCHITECTURE REQUIRED.**
Certification covers non-negative safe int64 grouping, deterministic merge,
threshold and synthetic/reduced downstream exactness; exceptional overflow
preserves the reference via the explicitly non-bounded fallback. No full-real
overflow or memory certificate is claimed.

Exactly one next task: **A018 — Bounded Multi-Stage Deterministic Integer Merge**.
Design one opt-in native/numeric sorted-run fan-in with an explicit live-byte
budget; reuse the A017 arithmetic/overflow and downstream contracts, prove
canonical output and partition invariance, and certify synthetic duplicate and
unique cases against A016/A017. Model resident unique-state and output ownership
under the unchanged 8-GiB/600-s constraints before proposing any real run.
If conservative ownership requires external/disk-backed merge, classify that
as architecture escalation and stop for separate authorization. Do not implement
it here, do not automatically start A018, and do not run A017R.

## Firewall and validation

Full-real preparations 0; full-real advances 0; real Arena, behavioral runs and
scientific experiments 0; GPU executions 0; raw downloads 0; Task017 historical
new units 0; Task017Q 0; archive writes 0; BANC 0. Historical Task016 unchanged;
historical Task017 unchanged / NOT_ROBUST; B:\\MaleCNS-Archive unchanged.
No scientific model, identities, weights/sign/delay/threshold semantics or
biological claim changed. Existing synthetic regression suites may exercise
synthetic runtime behavior; this is not real certification.

Targeted A017: 79 passed. A016/A015/A014/A013 combined: 156 passed, one existing
Feather V1 deprecation warning. A014 contained-tree watchdog status remains
**CERTIFIED_SYNTHETIC**, with no real watchdog certification. Final full-suite,
stateful/application validation: 145 passed, including A011 stateful-runtime
regressions. Full pytest: 627 passed, 14 skipped, one existing Feather V1 warning.
The skipped tests require unavailable CUDA or the explicitly disabled real-data
gate; no GPU or real execution was enabled. Final targeted A017 additionally
covers the reversed physical partition test. Compileall PASS; tracked integrity
PASS (9 tracked files and internal identities); diff check PASS; uv build PASS
(sdist and wheel 0.3.0). Final published Git identity is returned in the task
report. Package stays 0.3.0, workflows zero, no tag/release/version mutation.
