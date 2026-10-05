# Application A018 — bounded multi-stage deterministic integer merge

## Start gate and authorized scope

Repository root was derived with `git rev-parse --show-toplevel`:
`D:/spider/working/MaleCNS-Sim`. Local HEAD, origin/master and live GitHub
master all matched `f04e606ed9e7c449eb87a1667ae97d892e6c94cd`. Worktree clean,
stash empty, version 0.3.0, tracked workflows zero. The checked-in A017 plan
records **A17-B — AGGREGATION CERTIFIED; ADDITIONAL BOUNDED MERGE ARCHITECTURE
REQUIRED**, P2. These checks preceded mutation.

A018 changes only opt-in partial merging. A017 accepts an injectable merger,
defaulting to its unchanged concatenate/group implementation. A018's loader
selects the new merger explicitly. Production dispatch remains unchanged.
No source batching, endpoint filtering, local aggregation, scientific graph,
final CSR, runtime, LIF, Arena or watchdog implementation was redesigned.

## Exact A017 input contract

A run is a tuple of three owned one-dimensional equal-length int64 arrays:
`body_pre`, `body_post`, `count`; exactly 24 payload bytes per pair. Each pair
is ordered, internally unique, sorted by pre ascending then post ascending.
Endpoints and counts are non-negative and fit int64. Counts sum original
integer contributions, including contributions greater than one; they are
not row counts. Zero counts and self edges remain. Empty runs contain three
owned empty arrays; A017 ordinarily omits them from accumulation. A018 also
accepts explicit empty runs and an empty run list.

A017 local sorting/checking remains the authoritative validator. A018's
primitive consumes certified runs directly; arbitrary unvalidated triples
are outside its precondition. It does not reinterpret or copy input runs.
The mutable run list transfers ownership to the merger; callers must not
retain strong aliases when relying on the lifetime bound. One run transfers
directly; other outputs own exact-size storage. A017 releases batch/raw
buffers before calling the merger.

## Primitive and overflow proof

`merge_sorted_runs(left, right)` uses two deterministic cursor scans. The
first counts distinct output keys and checks equal-key sums using a transient
Python integer. The second writes three exact-size owned int64 arrays. Keys
are compared lexicographically; equal keys advance both cursors. There is no
sort, concatenate, threshold, float conversion, saturation, per-edge heap,
or retained Python object per edge. Scalar comparison objects are transient
and their number is fixed. Output dtype remains int64.

For admitted non-negative contributions, a safe final mathematical sum
implies every partial/intermediate sum is safe. Thus staged addition equals
A017's checked global integer reduction regardless of partition, schedule
or fan-in composition. The primitive raises the same `OverflowError` if an
equal-key sum exceeds INT64_MAX. Local overflow and staged overflow reach the
unchanged loader handler: fallback to A016/reference NumPy modular wrapping.
Negative endpoint fallback also remains unchanged. `[MAX, MAX, 3]` produces
the reference wrapped count 1 through fallback, at batch sizes 1,2,3.
The exceptional fallback is explicitly **not bounded A018 execution** and
can use reference concatenation. No full-real count-safety claim is made.

## Three architectures evaluated; exactly one implemented

Let A be group input rows, O output rows, P initial partial rows, N run count.

| Architecture | Payload/workspace and coexistence | Passes, CPU, determinism |
| --- | --- | --- |
| A: source-order two-way tree | Inputs 24A, exact output 24O, fixed scalar workspace; whole-stage owners included below | ceil(log2 N) stages; two scans per group, O(P log N), adjacent source-order tie policy |
| B: fixed K-way numeric cursor/heap | Inputs 24A, output 24O, O(K) numeric cursors/heap; no edge-object heap | ceil(logK N) stages; O(P log K) per stage with numeric heap; canonical run ordinal tie break; more implementation work |
| C: deterministic size-aware binary scheduling | Same binary primitive; O(N) run-size queue metadata, no edge-object heap | Potentially fewer visits for uneven sizes, O(N log N) scheduling; size then original ordinal tie break; less direct lifetime audit |

Selected **A**, fan-in **2**, including odd-run carry without copying. Stage
groups are adjacent source runs in original order; next-stage outputs preserve
that group order. Identical inputs give identical scalar schedule records and
arrays. Scheduling is operational and absent from scientific identity.

At N=2,318 physical runs, K=2/4/8/16 imply at most 12/6/4/3 stages.
Every option still needs a final exact output and input/output coexistence.
K=2 has two live group inputs and the simplest explicit count/overflow/lifetime
proof. K>2 was evaluated analytically, not implemented as a configurable
production route. Tests compose the binary primitive under K=2/4/8/16 group
boundaries and prove exact output invariance; this is not a K-way performance
certificate. Per-group input/output maxima are size-dependent, not constant
bytes independent of graph size. Cursor workspace is independent of total N.

## Resident memory bound in bytes

For a group in a stage, let U be unmerged rows outside the active group, A
the active two input rows, D completed next-stage rows, and O exact output rows.
The allocated array payload at coexistence is exactly:

`M_payload = 24 * (U + A + D + O)` bytes.

`U+A+D <= P`: a completed group replaces its inputs with no more rows.
`O <= A <= P`, so generic payload is at most **48P bytes**. If global distinct
cardinality C is available, every output is a subset of global keys, so
`O <= C`, giving the tighter **24(P+C) bytes**. Active group alone is
`24(A+O)`; with C known, A<=2C and O<=C, hence at most **72C bytes**.
The exact output is counted once, including within whole-stage coexistence.

On the tested 64-bit CPython/NumPy implementation, numeric cursors/scalars
have a conservative fixed 8,192-byte allowance. Run tuples, ndarray headers,
current/next list slots, scalar schedule/metrics records and integer objects
are conservatively allowed **2,048(N+1) bytes**. Each stage reduces run count;
total merge records <=N-1. A run's three empty ndarray headers are 336 bytes
on this platform; a triple tuple plus list slots and scalar schedule is well
below the allowance. No per-edge Python metadata is retained. Thus:

`M_owned_bound = 48P + 8192 + 2048(N+1)` bytes, generically;

`M_owned_bound = 24(P+C) + 8192 + 2048(N+1)` bytes, with known C.

The measured metric uses merge-record count plus two, <=N+1 for N>=1;
the N=0 case uses two slots. This is an allocated-object model, not an upper
bound on allocator-retained pages, interpreter baseline, metadata tables or
OS private bytes. Those are separate full-scale/process terms. There are no
hidden row-sized buffers. Maximum group input runs: **2**. All resident
current/next runs are honestly O(N), potentially N initially; bounded fan-in
does not claim that only two runs exist in the entire process.

## Release proof and no-global-concatenation proof

After exact output ownership is established, both current list slots become
None and local input references are deleted before the synchronous observer.
The output goes into the next-stage list, then its local reference is deleted.
At stage completion the old list is cleared; no previous array owner enters
metrics or schedule. Odd carries move the owner and clear its old slot.
One-run input is popped; the caller's list is empty after success. Weakref
tests establish dead merged input arrays at release boundaries. Observers
must not retain strong references. Tests also enforce two active group inputs
and the whole-stage <=48P payload bound. These prove reclaimability, not
immediate OS page return.

Simultaneously live run owners are counted from the measured initial run count
and the release transitions: a two-way output temporarily adds one owner,
then replacing two inputs decreases owners by one. Maximum whole-process run
owners is N+1 when N>=2 (one for N=0 or 1). Three-million-row high/moderate/
unique cases have 46 initial runs and at most 47 simultaneous owners; many
small has 2,930 initially / 2,931 maximum; few large has 12 / 13. These include
unmerged and completed runs. Active merge inputs remain exactly two. This
owner count is a transition-derived measurement, not OS allocator page count.

The A018 module never calls concatenate, local or global. The direct staged
tests patch `numpy.concatenate` to raise, including all-unique and empty cases.
A017 reference and exceptional overflow fallback intentionally remain separate.

## Exactness fixtures and downstream pipeline

Twenty adversarial run fixtures cover one run; disjoint and overlapping pairs;
33 same-pair runs; unique pairs; interleaved ranges; shared first/last keys;
mixed empty and all-empty runs; uneven sizes; threshold total 5 and miss 4;
self edges; safe MAX total; many-stage canonical output; reverse run order;
zero runs; zero counts; MAX endpoints; one giant run with 31 tiny runs.
Additional overflow primitive/fallback cases complete the required unsafe case.
Repeated executions compare schedule and output exactly. Composition tests
vary group boundaries 2/4/8/16. Source partitions 1,2,4,8,16,127,1001 give
the same table. Loader fixtures use physical Arrow partitions/batch admission
1,2,3,7,65536 and thresholds 0,4,5, retaining the shared downstream pipeline.

The 22 inherited logical A017 datasets, at three thresholds and five source
partitions, compare A017 and A018 prepared results exactly. The shared oracle
checks keys/counts, neuron order, topology, CSR indptr/indices/data, anatomical
counts, effective/outgoing weights, signs/NT records/masks, projection and
prepared fingerprints. PreparedRuntime identities and delay-grid steps are
also identical, without advancing those synthetic runtimes. No mismatch.
Production opt-in tests prove default preparation never calls the A018 primitive.

## Synthetic measurement method and evidence

`scripts/certify_application_a018.py --matrix` creates only numeric synthetic
partials, never opens real payloads. Fresh process per route/case; Windows
private bytes and working set sampled every 1 ms, including before/after.
100,000 / 1,000,000 / 3,000,000 logical input rows; five patterns:
high duplication (10 global pairs), moderate (10,000), unique (65,536-row
runs), many small unique (1,024-row runs), few large unique (250,000-row runs).
30 observations / 15 exact SHA-256 triple comparisons are in
`2026-10-05-application-a018-measurements.json`. Generation precedes baseline;
allocator retention can affect process peaks. Some timings overlap pytest;
they are indicative, not isolated CPU certification. Sampled peaks can miss
native transients; the payload bound does not depend on sampling.

Three-million-row results, bytes and merge-only seconds:

| Pattern | A017 private | A018 private | A017 working set | A018 working set | A017 seconds | A018 seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| High | 715407360 | 715403264 | 98000896 | 98246656 | .000267 | .002098 |
| Moderate | 732516352 | 726913024 | 115441664 | 109199360 | .035640 | 1.791902 |
| Unique | 1028485120 | 859762688 | 403030016 | 241344512 | .391767 | 21.384700 |
| Many small unique | 1029632000 | 861020160 | 411013120 | 241721344 | .427599 | 46.001115 |
| Few large unique | 1027432448 | 859488256 | 387588096 | 240967680 | .392625 | 13.688752 |

Unique-case private reduction: 168,722,432 bytes (16.405%). Working-set
reduction: 161,685,504 bytes (40.117%). High-case differences are baseline
noise, not a guaranteed improvement. A018 bounds still hold without compression.

| Pattern | Partial bytes | Stages | Groups by stage | Rows read (two scans) | Rows written | Max group input | Max output | Max completed next stage | Max coexistence payload |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| High | 11040 | 6 | 23,11,6,3,1,1 | 1800 | 450 | 480 | 240 | 5520 | 11280 |
| Moderate | 11040000 | 6 | 23,11,6,3,1,1 | 1800000 | 450000 | 480000 | 240000 | 5520000 | 11280000 |
| Unique | 72000000 | 6 | 23,11,6,3,1,1 | 33961472 | 16980736 | 72000000 | 72000000 | 72000000 | 144000000 |
| Many small unique | 72000000 | 12 | 1465,732,366,183,92,46,23,11,6,3,1,1 | 69951104 | 34975552 | 72000000 | 72000000 | 72000000 | 144000000 |
| Few large unique | 72000000 | 4 | 6,3,1,1 | 22000000 | 11000000 | 72000000 | 72000000 | 72000000 | 144000000 |

Rows read count logical input visits in both scans, not individual scalar
key loads. Carried odd runs are not scanned/copied. The reference consumes
each partial column once for concatenation then sorts/reduces; its unchanged
metrics do not instrument scalar read/write visits. Reference explicit merge
envelope is 128P plus native overhead: 384,000,000 bytes in the unique case,
versus A018's 144,000,000-byte payload plus bounded metadata/scalars.

Unique case certified: every retained pair is globally unique, compression
1.0x. Six-stage writes amplify to 5.66 times initial rows; twelve-stage many
small runs to 11.66 times. Scalar Python scanning costs materially more than
vectorized reference grouping. No 600-second full-scale time claim: even a
naive 50x extrapolation of the six-stage measurement exceeds 600 s, before
extra stages/downstream work. Real duplication could reduce visits but is
unknown. The time cap must terminate a future attempt that cannot finish.

## Full-scale staged resident model

Frozen inputs: R=151,856,684, C~25,582,938, N~166,700 neurons,
E~24,904,953 effective edges. C<=P<=R; at most 2,318 partial runs under
A016's physical batch layout. No real scan or imported synthetic compression.

| Component/stage | Model |
| --- | --- |
| A016 source batch including universe | ~5.397 MiB, native/metadata extra |
| A017 initial partials | 24P = 613,990,512..3,644,560,416 bytes, ~.572..3.394 GiB |
| Local grouping during collection | inherited bounded batch terms, retained <=1.5 MiB and grouping allowance <=6.5 MiB; source excluded from local workspace |
| Unmerged current runs | 24(U+A), <=24P; active inputs are a subset, not added twice |
| Active group inputs | <=48C = 1,227,981,024 bytes, ~1.144 GiB |
| Active exact output | <=24C = 613,990,512 bytes, ~.572 GiB |
| Active input/output workspace | <=72C = 1,841,971,536 bytes, ~1.716 GiB; no additional row workspace |
| Completed next-stage runs | 24D, <=24P; U+A+D<=P, never add two complete P owners |
| Whole merge coexistence | <=24(P+C) = 1,227,981,024..4,258,550,928 bytes, ~1.144..3.966 GiB, plus <=4.54 MiB headers/scalars |
| Final grouped table | ~.572 GiB, all previous partial inputs released |
| Final prepared ownership | ~1.740 GiB, downstream unchanged |

No batch source buffer coexists with merge in the implementation. Likewise
the final prepared graph does not coexist with all initial partials. The
unchanged downstream projection grouping has only C input rows. Retaining
the inherited conservative 104C grouping/work allowance, 24C input, an
additional 24C output ownership allowance and 1.740 GiB final ownership gives
**152C bytes + 1.740 GiB ~=5.362 GiB**. This deliberately overcounts some
downstream simultaneity; it does not reintroduce a P-sized sort. It is a
conservative model inherited from A017, not a newly audited native RSS bound.

Stage maximum is max(collection ~3.41, merge ~3.971, downstream ~5.362) GiB
before interpreter/native/metadata/allocator overhead. With an explicit
**1-GiB planning allowance** for those process terms, plus bounded source
allowance for conservatism, envelope is approximately **6.37 GiB**. The
allowance is a planning assumption, not a measured full-scale upper bound;
the measured merge-only baseline is around .67 GiB. Removing that assumption,
report **~5.37 GiB + unproven process overhead**. A watchdog remains required.

All in-memory partials themselves are acceptable in this model: worst 3.394
GiB; merge solved, partial storage accounted, downstream now dominant. No
disk/mmap/spill intermediate is needed by this model and none implemented.
The existing A015 metadata-only empty Feather helper is unchanged and is not
an intermediate edge run. Overflow fallback lies outside this model.

**P1 — strong bounded model supports a future real preparation proposal under
8 GiB. <=8 GiB proven: No.** This is a resident-memory prediction, not a
completion-time prediction, real overflow certificate, or production promotion.

## Decision and exact A018R proposal

**A18-A — BOUNDED MULTI-STAGE MERGE CERTIFIED; FULL-SCALE MODEL SUPPORTS REAL
RETRY PROPOSAL.** Semantic exactness and the unique-case payload/lifetime
bound are certified on synthetic inputs. Time amplification is substantial.

Proposal only, do not execute automatically: **A018R**, CPU only, at most one
full-real preparation; A016 bounded Feather batches; A015 validated endpoint
filtering; A017 checked local integer aggregation; A018 binary staged merge;
corrected contained-tree Windows Job Object watchdog; unchanged 8-GiB cap
and 600-second preparation cap; no GPU; no stateful advance; stop immediately
after preparation (or cap/error), report process-tree memory, fallback status,
pair/graph identity and prepared digest before any further authorization.
Overflow/reference fallback is not bounded: treat a flagged fallback as a
failed bounded-route certificate even if the watchdog allows completion.
No retries after timeout/error within that proposal. No raw download.

## Validation and firewall

Initial A018 targeted run: 92 passed. Initial selected A013–A018/A011 run:
335 passed. Initial full suite: 719 passed, 14 expected CUDA/opt-in real skips,
one existing Feather V1 deprecation warning. Four fan-in composition tests
were then added, followed by an across-stage weakref release test. Final A018
targeted run: **97 passed**. The complete suite was rerun after these additions.
Final full suite: **724 passed, 14 expected skips, 1 existing warning** in
112.39 seconds. Final selected prior regressions: **243 passed** in 47.91
seconds: A017 79, A016 68, A015 59, A014 12, A013 17, A011 8. All 477
application cases and all available stateful/runtime cases pass in the full
suite. The 14 skips are unavailable CUDA/device cases and the unenabled real
full-graph gate; none authorize real execution.
A014 contained-tree tests cover direct, launcher, descendant, replacement,
aggregate-tree cap, normal exit and injected accounting failure; expected
classification **CERTIFIED_SYNTHETIC**, no watchdog redesign.

Compileall, tracked integrity (9 pinned files/internal identities), diff check
and package build pass. Final validation/commit identities are reported in
the task response; no tag, release or version bump. Package stays 0.3.0.

Full-real preparations 0; full-real advances 0; real Arena, behavioral and
scientific experiments 0; raw downloads 0; new historical Task017 units 0;
Task017Q 0; archive writes 0; BANC 0. B:\MaleCNS-Archive unchanged. Historical
Task016 unchanged; historical Task017 unchanged / NOT_ROBUST. No biological
claim or scientific model/identity mutation. Synthetic preparation and
existing synthetic runtime regression execution are not real science runs.
