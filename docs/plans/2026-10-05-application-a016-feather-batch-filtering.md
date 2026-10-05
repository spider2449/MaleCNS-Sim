# Application A016 — bounded Feather source-batch endpoint filtering

## Gate and decision

Dynamic root: `git rev-parse --show-toplevel` returned
`D:/spider/working/MaleCNS-Sim`. Starting local/origin/live master all equal
`727f241c4b3e1aac6f45cf8008b3b199832d077a`; clean worktree, empty stash,
version 0.3.0, zero tracked workflows. The tracked A015 plan establishes A15-B.

**A16-B — BOUNDED FEATHER BATCH FILTERING CERTIFIED; RETAINED/GROUPING MEMORY
REMAINS BLOCKER. P2**, conservative upper branch, not an observed real peak.
Architecture B is interpreted literally from the A015 option table: bounded
source batches, filter, concatenate retained rows, then group. No partial
aggregation, disk spill, runtime redesign or production dispatch switch.

## Authoritative physical access

Metadata-only inspection of the authoritative local minconf-0.5 weights file
(1,051,241,946 bytes) establishes ARROW1 file magic, Feather V2 / Arrow IPC,
IPC metadata V5, LZ4_FRAME compression, 2,318 physical record batches,
maximum 65,536 rows, final 9,772 rows, total 151,856,684 rows.
Schema: body_pre, body_post, weight, each int64; pandas schema metadata.
No dictionary columns. No real edge payload was read for this audit.

Installed PyArrow 25.0.1 exposes `ipc.open_file`, `num_record_batches`,
`get_batch` and `IpcReadOptions(included_fields=..., use_threads=False)`.
The original production and A015 routes call `feather.read_table(columns=...)`:
all selected columns materialize before validation/filtering. Projection alone
does not bound rows. Slicing that complete table would retain its owners.

The new metadata-only parser reads the IPC footer's block offsets and each
record-batch message header, never its body. Physical row admission happens
before opening the payload reader. Feather V1 and physical batches larger than
the configured limit fail explicitly. This is a narrow local IPC-file contract,
not a general hostile-file parser or Feather V1 streaming implementation.

## Reader, validation and ownership

`with edge_batches(path, columns, max_rows_per_batch) as batches` provides
deterministic physical source order and exactly three requested columns.
Projection is passed to the IPC reader, not applied after a full-file read.
Every physical batch must fit the limit; larger batches are rejected rather
than decompressed and sliced. The iterator, reader and OSFile lifetime is scoped
by the context manager. Exceptions and interrupted iteration close the generator
and source; no prepared result is returned on failure. Retry reopens the file
from batch zero. There is no retained graph publication or persistent temp state.

Each batch uses the original `_integer_column`: integer schema, no nulls,
int64 conversion; nonnegative count validation precedes filtering. Dictionary
and noninteger selected fields are rejected from the schema before payload
iteration. Excluded malformed rows still fail. For multiple simultaneous defects,
batch traversal can discover a different first defect than whole-column traversal;
acceptance/rejection and integer conversion semantics are preserved. Negative
endpoints retain A015's explicit full-reference fallback, because its historical
packed-key behavior cannot safely be replaced here. That exceptional route is
scientifically exact but carries **no bounded-memory claim**; the authoritative
release-shaped source contract uses nonnegative endpoints.

Universe is the same immutable sorted int64 annotation bodyId array for nonempty
stripped string superclass. Binary-search membership is unchanged. Both endpoints
must belong. No weight conversion, thresholding or regrouping occurs per batch.
Only masked numeric copies enter a retained tuple list. Empty retained batches
add nothing. Concatenation creates three owning int64 arrays in original retained
row order, temporarily overlapping the retained list. Then the identical A015
`_aggregate_numeric_edges` and shared metadata oracle run. Production downstream
projection, thresholding, signs, weights, CSR and identities remain the oracle.
The small temporary empty Feather used by A015 metadata normalization is reused
and removed by TemporaryDirectory; this is not retained-edge spilling.

Raw excluded-union and distinct-pair diagnostics remain unavailable, as explicitly
defined by A015's experimental publication contract. No default consumer is
redirected to this route. Batch size is operational and absent from scientific
identity. Default experimental limit: **65,536 rows**.

| Transition | Ownership / copy audit |
| --- | --- |
| Feather to physical IPC batch | Selected compressed buffers decompress into batch-local Arrow ownership; copy, no memory map or full source table |
| Arrow batch to Table/select | Shared Arrow buffers / view-like ownership, no row conversion |
| Arrow integer column to NumPy | Existing combine_chunks copies even a single chunk (distinct buffer addresses verified); native int64 to_numpy then views this copy; other integer widths conditionally copy on int64 cast |
| Membership | Batch-sized binary-search positions, indexed universe values and boolean masks; bounded temporary copies |
| NumPy to retained | Boolean fancy indexing copies eligible rows only |
| Retained list to concatenated NumPy | Copy; both owners coexist during concatenation |
| Concatenated rows to grouping | Existing stable grouping allocates sort/key/output temporaries; not zero-copy |

Arrow slicing is buffer-sharing and would keep its physical parent alive; the
route does not slice oversized physical batches. Required integer schemas exclude
dictionary decoding and Pandas conversion. Table columns are one physical chunk;
there is no full-file combine_chunks. Consumers release source arrays/table/mask
before advancing; the generator deletes its previous batch before `get_batch`.
Weakref tests verify old Table and membership mask reclamation. Final retained
arrays own numeric storage. Allocator caches may retain committed pages after
objects become reclaimable; these are different claims.

## Exact certification

For ordered R = batch1 || ... || batchN and a row predicate f, filtering distributes
over ordered concatenation. Thus retained pre/post/count sequences are exactly
equal, including contributions for pairs crossing arbitrary boundaries. Grouping
is performed once after concatenation, so original stable integer contribution
order and overflow behavior are unchanged. Thresholds remain after aggregation.

Tests exercise the A015 fixtures plus alternating retained/excluded duplicates,
one/two/many-boundary contributions, duplicates separated by excluded rows,
self edges, thresholds exactly reached and missed by one, first/last retained,
zero/all retained batches, small partial final batches, invalid excluded and
retained boundary rows, unknown/large IDs, negative fallback, empty inputs,
deterministic repeat and sizes 1/2/3/7/65,536. Results compare directly across
sizes as well as against reference. Numeric retained sequences, grouped counts,
neurons/order, edge order, anatomical and outgoing CSR indptr/indices/data,
weights, signs, NT metadata, delays via unchanged grid mapping and prepared/runtime
identities compare exactly without tolerance. Scale fixtures compare production
against batched output at 10k/100k/2M. No real preparation or runtime advance.

## Synthetic memory and time evidence

Fresh child process per measurement; seed 15, 100 eligible neurons, every tenth
raw row eligible at both endpoints, hence 90% exclusion. Generation precedes
baseline sampling. Sizes: 10k, 100k, 2M; retained counts 1k, 10k, 200k;
numeric retained bytes 24k, 240k, 4.8M. These are safe bounded synthetic files.
Temporary synthetic input files are deleted. Ignored local JSON evidence is under
`data/derived/a016/*-certified.json`. Reported peaks take the maximum of 1-ms
process samples and synchronous stage snapshots (both present in JSON).
Native transients between samples may be missed. Single runs, instrumented times,
allocator baselines and concurrent validation activity preclude statistical
performance or true peak claims.

| Raw rows | Route | Peak private bytes | Peak working set bytes | Wall seconds |
| ---: | --- | ---: | ---: | ---: |
| 10,000 | reference | 736,796,672 | 110,821,376 | .023362 |
| 10,000 | 64k batched | 733,958,144 | 109,203,456 | .035280 |
| 100,000 | reference | 783,589,376 | 132,423,680 | .104906 |
| 100,000 | 64k batched | 757,968,896 | 115,720,192 | .037494 |
| 2,000,000 | reference | 1,260,883,968 | 544,346,112 | 2.817778 |
| 2,000,000 | 64k batched | 811,966,464 | 131,043,328 | .147098 |

Largest private reduction **448,917,504 bytes (35.60%)**; working set reduction
**413,302,784 bytes (75.93%)**. Baselines were 790,716,416 / 110,780,416
reference versus 785,465,344 / 109,977,600 batched private / WS bytes.
Source-stage private snapshots 988,246,016 versus 802,340,864; integer-validation
918,433,792 versus 802,996,224. Batched highest recorded stage is grouping,
811,966,464 private / 131,043,328 WS. This demonstrates removal of full-R selected
column conversion, not independence of the retained/grouped graph from F.

| Configured limit at 2M | Physical rows | Peak private | Peak WS | Wall seconds |
| ---: | ---: | ---: | ---: | ---: |
| 16,384 | 16,384, regenerated synthetic file | 924,065,792 | 177,057,792 | .171284 |
| 65,536 | 65,536 | 811,966,464 | 131,043,328 | .147098 |
| 262,144 | 65,536 | 809,975,808 | 132,395,008 | .153684 |
| 1,048,576 | 65,536 | 813,457,408 | 131,907,584 | .146114 |

Larger limits do not enlarge existing physical batches. The 16k synthetic rewrite
leaves a higher allocator baseline (909,557,760 private / 161,062,912 WS), so its
absolute process peak does not imply larger batch workspace. The real file cannot
use a 16k admission limit without source re-encoding, which is not authorized.
64k is the smallest limit admitting the authoritative physical layout, with no
benefit established for a larger limit. Operational throughput at 2M: reference
~0.710M raw rows/s; batched ~13.60M raw rows/s, instrumented single-run evidence.

64k batched stage seconds: source iteration .025355; integer/count validation
.011030; endpoint filtering .042278; retained copying .005546; retained
concatenation .001355; shared downstream integer grouping .024445; total .147098.
Other time includes metadata, downstream signing/CSR and instrumentation. Reference
read_table source .026606, integer conversion .020451, raw unique primitives
2.284164 and sorting primitives .465544, downstream grouping .000779, total
2.817778. Production inline raw grouping is measured through its primitives;
production filters already grouped data in projection, so it has no directly
comparable pre-group membership or retained-concatenation stage. Primitive profile
times overlap outer grouping and must not be summed as disjoint phases.

## Updated full-scale lifetime model

Use frozen A015 R=151,856,684, N~166,700, C~25,582,938 distinct curated pairs,
E~24,904,953 effective edges, final ownership ~1.740 GiB. **F, eligible raw rows
before grouping, is unknown**: C <= F <= R. E is not F. No new real scan estimates F.

| Component | Logical bytes / bound |
| --- | --- |
| One selected source batch | 24b = 1,572,864 bytes at b=65,536 |
| NumPy conversion owner | additional 24b = 1,572,864 bytes with existing combine_chunks |
| Membership workspace | approximately 18b = 1,179,648 bytes plus bounded overlapping masks |
| Membership universe | 8N = 1,333,600 bytes |
| Retained accumulated numeric rows | 24F = .572..3.394 GiB |
| Concatenation coexistence | up to 48F = 1.144..6.789 GiB, plus tuple/array-per-batch overhead |
| Grouping explicit temporary envelope | up to 80F = 1.906..11.314 GiB, includes keys/order/starts/sorted rows/output, excludes native sort overhead |
| Required final state | ~1.740 GiB, unchanged; runtime/final ownership redesign excluded |

Selected raw/conversion/membership batch subtotal ~4.125 MiB, or ~5.397 MiB with
universe; decompressor overhead and metadata are additional. This source-side term
is O(b), not 24R plus O(R) membership. Footer admission metadata is O(batch count).
Retained-list and concat peaks still grow with F. Conservatively combining 24F
retained input, 80F grouping envelope and 1.740 GiB final ownership gives about
**4.218..16.449 GiB + baseline/native/metadata/allocator overhead**; not every
component necessarily coexists, so this is a conservative envelope, not a measured
or exact liveness maximum. Concatenation alone approaches 6.789 GiB at F=R.
Synthetic 10% retention cannot be assumed for real data. The upper branch remains
above 8 GiB: **P2**. No claim actual F realizes that branch. **<=8 GiB proven: No**.
Real retained multiplicity and native grouping peaks remain unresolved blockers.

## Exactly one next task

**A017 — Deterministic Chunk-Local Integer Aggregation and Merge.** Design and
certify reduction of retained duplicate accumulation with deterministic global
merge, preserving reference stable integer arithmetic/overflow, canonical ordering,
thresholds and diagnostics. New equivalence proof and bounded synthetic evidence
are required before implementation can justify a real retry proposal. Do not
implement or start A017 automatically. No A016R execution is proposed here.

## Firewall and validation

Full-real preparations and advances, real Arena/behavior/scientific experiments,
raw downloads, Task017 historical new units, Task017Q, archive writes and BANC:
all **0**. No biological claim, scientific model or biological identity change.
Historical Task016 unchanged; historical Task017 unchanged / NOT_ROBUST;
`B:\MaleCNS-Archive` unchanged. Production default unchanged. A014 watchdog is
unchanged and remains CERTIFIED_SYNTHETIC; no full-real watchdog certification.
No tag, release or version mutation.

Validation: A016 **68 passed**; A015 **59 passed** (combined 127);
A014 **12 passed**, A013 **17 passed**, A011 stateful-runtime **8 passed**
(combined 37). Application suite **301 passed**. Full pytest **548 passed,
14 skipped**: unavailable CUDA devices and the disabled opt-in real-data gate.
One expected PyArrow Feather V1 deprecation warning comes from the rejection
fixture. Compileall, tracked integrity (9 frozen tracked files and internal
identities), diff check and 0.3.0 sdist/wheel build PASS. No real-data gate enabled.
Authorized master commit/push and final local/origin/live identity are reported
in the final response; no tag or release is created.

## Local measurement evidence SHA256

| File under data/derived/a016 | SHA256 |
| --- | --- |
| 10000-batched-certified.json | 2D3011B86F2E892C3974A89B4F226A03DF8B9CC955A3BC6298F22D3F98054B9D |
| 10000-reference-certified.json | 39374245A687D313860A2B5796753E80FC84DD232C47E625185A7DDBAC74C4EA |
| 100000-batched-certified.json | 50C78D06E432990BC8903C8C4BC09AC29C8460B44B0E4A4C70CECF41637B9D55 |
| 100000-reference-certified.json | 291A54307689C4AF732803A6C57A327F713EBE183AB400864AA24428FB39CB78 |
| 2000000-b1048576-certified.json | 832E198F43183618A982BCBC08ED670BCF41174DD5E1127B0B12256FC842F5A4 |
| 2000000-b16384-certified.json | 1A5A9111DBD244385D812E05847BA37DAF5E86573777EF91377425661216BACC |
| 2000000-b262144-certified.json | 9B307ECA88007F1226B328EAA178235D2F9C7CADB29C3C0614A2EE8CCA10D7AA |
| 2000000-batched-certified.json | 7EAFCF5A17D6530296EDA1FBC1611686C0F27E97FE7D81DD61F491B480C97575 |
| 2000000-reference-certified.json | 7DCD39402016F6BF0506B0030D38C32DA65B10980FD87B258167ADF4F2769005 |
