# Application A018T: bounded blockwise NumPy merge

Authorized A018T only. Starting three-way HEAD: 842e71123c90f7192a90eef8e205b0aebc5b61b8.
Clean worktree, empty stash, version 0.3.0, zero tracked workflows. Prior A18S-B preserved.

## Frozen block contract before certification

Inputs are canonical sorted internally unique int64 pairs with nonnegative int64 counts,
as admitted by A017. Negative endpoints are rejected upstream and use existing fallback.
Choose up to floor(B/2) rows from each run. Boundary is the smaller endpoint under
pre ascending, then post ascending. Numeric searchsorted on pre and then the contiguous
equal-pre post interval includes every key <= boundary. No remaining key can equal
an emitted key: each input is unique and every remaining key is strictly greater.
At least one side consumes its selected slice. Concatenation is bounded by B;
lexsort and numeric masks combine at most two contributions per key.

Candidate A: bounded concat/lexsort, with C boundary-guided closure, selected for testing.
Candidate B: structured keys/searchsorted rejected analytically: requires extra record
copies or new whole-run key ownership with no demonstrated benefit. No third implementation.
Output uses A018S upper capacity and exact compaction; no block-output list.
Overflow guard x > INT64_MAX-y precedes int64 addition; no reduction overflow occurs.
Both counts are nonnegative; at most two inputs per key, so safe sums are exact.
Threshold remains downstream after all stages. B is operational, absent from identity.

Preliminary workspace bound: 128B bytes plus fixed headers, including concatenate 24B,
permutation 8B, sorted copies 24B, equality/keep and comparison masks, duplicate indices,
guard gathers, addition gathers and grouped scatter copy. Temporaries die before compact.
Global conservative bound: 72P + 128B + 8192 + 2048(N+1); tight cardinality model:
24(P+3C) + 128B + overhead. Inputs/stage outputs follow unchanged A018S ownership.
No real data, native dependencies, multiprocessing, GPU, default promotion or cap changes.

Final synthetic measurements and decisions are recorded below.

## Exactness and complexity audit

Negative endpoints are not admitted by A017; synthetic negative-source loader fixtures
exercise the unchanged reference fallback. Maximum nonnegative int64 IDs, zero counts,
MAX-1 + 1, and unsafe MAX + 1 are covered. No narrower/float/hashed key representation.
No reduction API is used: adjacent equality can only describe one pair from each input.
The inequality guard uses nonnegative subtraction and rejects before vector addition.
For admitted totals, all intermediate sums are <= final sum under the unchanged binary
schedule; overflow timing inside a failed primitive is unobservable because no output
escapes and the unchanged loader invokes the reference fallback.

Proof of progress: the lesser selected endpoint is consumed on its own side, so every
non-final sorting block consumes at least floor(B/2) rows from one side. At a final
short slice it exhausts that side. Hence control cost is O(A/B + 1) per merge, plus
constant-size column loops and two tail-copy loops. Native work is six binary searches
per sorting block, three concatenates, lexsort of <=B pairs, masks and gathers, one
checked addition per equal pair, and scatter into the stage owner. Conservative sort
cost O(A log B); search O((A/B+1) log B); grouping/scatter O(A). NumPy may exploit
existing ordered regions but that is not a complexity assumption. Binary stage
amplification remains sum of active rows; no scheduling redesign or higher fan-in.
A018S has O(A) Python iterations, repeated scalar extraction/comparison/output stores.

Memory audit uses U outside active inputs, A active input rows, D completed stage rows,
O output rows, P initial partial rows, C globally unique cardinality, N initial runs.
Existing input payload is 24(U+A+D), capacity adds 24A. Block views retain already
counted owners; bounded temporaries add <=128B. During compaction, temporaries are
released and exact owners add 24O while capacity still lives. Conservative sum:
24(U+A+D+A+O)+128B+fixed/container overhead. U+A+D<=P, A<=2C, O<=C,
therefore <=24(P+3C)+128B+8192+2048(N+1). Without cardinality: <=72P+128B+overhead.

The 128B allowance includes concatenated columns 24B, permutation 8B, sorted columns
24B, native lexsort scratch reserve 16B, equality/keep masks and temporary boolean
comparisons, duplicate intp indices <=4B, guard/addition gathers and duplicate+1
indices, and one grouped-column scatter gather <=8B. These temporaries have different
lifetimes; even their conservative overlapping live maxima fit the allowance.
No whole-run record keys, global concatenate, list of emitted block arrays or retained
capacity view. Allocator retention and process baseline are outside logical owner
bytes; sampled private/working-set peaks include them and do not prove real peaks.

Certification compares grouped arrays to independent A017 grouping, and prepared
results to A017 and its certified downstream helper (production reference identities
and exact arrays). Neuron order, source/target IDs, counts, anatomical CSR indptr,
indices/data, effective weights, outgoing CSR, signs, signed counts/masks, metadata,
projection/prepared fingerprints, runtime identity and delay grid steps match exactly.
Prepared certification is repeated with B=2,7,65536 and Feather partitions 1,2,3,7,65536.
Merge fixtures cover disjoint, complete/partial overlap, alternating, equal first/last,
equality on either selected-slice endpoint/emission boundary, long equal-pre regions,
pre transitions, empty/one-row/uneven runs, self edges, global-only threshold crossing,
MAX safe sum, overflow fallback, canonical uniqueness, repeated output, seeded source
partition invariance and 2318-run deterministic schedule. Weakrefs cover capacity,
initial inputs and completed stages; they certify reference release, not OS page return.

## Downstream budget evidence and next task

A018R remains A018R-TIME-LIMIT. Known nonmerge time before sign entry is 38.8289515 s.
Sign construction was interrupted after at least 11.7750418 s; its complete duration
is unknown. Effective weights, final CSR/outgoing structures, identity/digest work,
runtime construction and cleanup also lack completed full-scale times. A014 static
analysis identifies an O(C) Python sign list and repeated metadata/hash work; these
are real costs, not zero-time allowances. Existing small downstream exactness tests
are not representative timing evidence. A finite conservative downstream upper
allowance cannot be certified from these records. Budget calculations must retain
38.8289515 s known pre-sign nonmerge work plus >11.7750418 s sign/final-work allowance,
with an unresolved upper endpoint. The remaining deadline headroom is an available
allowance, not a measured estimate of those missing stages.

Exactly one next bounded proposal: **A018U ? Downstream CPU Preparation Completion
Budget Design and Synthetic Certification**. Profile the unchanged post-merge sign,
effective-weight, outgoing/CSR, digest/runtime and cleanup stages on bounded synthetic
scaling fixtures; derive a conservative completion allowance with uncertainty and
check the A018T plus downstream <600-s model. Preserve all scientific identities,
CPU-only/8-GiB/600-s envelope, production defaults and watchdog; no real source,
preparation, advance, Arena, raw download, native dependency or archive change.
Separate user authorization is required. No A018TR execution is authorized or performed.

## Firewall

Full-real preparations/advances, real Arena/behavioral/scientific runs, raw downloads,
Task017 new units, Task017Q and archive writes are all zero. Historical Task016 and
Task017 remain unchanged; Task017 remains NOT_ROBUST. B:/MaleCNS-Archive is untouched.
Scientific graph semantics and biological identities are unchanged. No biological claim.
No promotion, tag, release, version bump, GPU or cap increase.

## Profiling result

A018S profile uses 200000 rows per input, normal uninstrumented phase timers, a
separate AST counter run and cProfile. Disjoint: 400000 Python iterations, 1600000
NumPy scalar loads, 200000 individual key comparisons, zero scientific count int
conversions, branches left/right 200000 each, 1200000 scalar output writes. Allocation
0.0000391 s; loop 0.3267838 s; no compaction. Complete overlap: 200000 iterations,
3200000 scalar loads, 1200000 individual key comparisons, 400000 count conversions,
200000 equal branches, 600000 scalar stores. Allocation 0.0000348 s, loop 0.4250224 s,
compaction 0.0014447 s. Counter int_conversions includes one extra limit conversion.
Each NumPy-index extraction returns a scalar; no hidden float conversions. cProfile
attributes most primitive time to the merge body. Python comparisons, scalar extraction,
branches and stores cannot be separately isolated by cProfile; no invented percentages.
Dominant A018S cost: **P1 Python key-comparison loop**, with measured P2 extraction and
P3 stores coupled to it. P4 compaction and allocation are small here; P5 adds tiny-run
stage/call overhead. A018T remaining cost is **P5** in the many-tiny-run schedule, plus
P6 native grouping/copy/scatter work in large blocks; per-pair comparisons are removed.

Separately instrumented A018T B=16384 400000-row disjoint primitive: wall 0.0058842 s,
25 sorts 0.0003260 s, 150 searches 0.0003505 s, 75 concatenates 0.0005982 s,
28 explicit empty allocations 0.0000653 s. Complete overlap wall 0.0140006 s,
sort 0.0010777 s, search 0.0003990 s, concat 0.0013468 s, explicit allocation
0.0000694 s, exact compaction 0.0012391 s. These instrumentation timings are not
substituted for fresh-process benchmark medians. cProfile self time includes native
ndarray indexing, mask/scatter and ufunc operations not separately exposed as calls;
it is not a measurement of pure Python CPU. Native allocator-internal allocations
are modeled, not claimed to be exhaustively timed. Compaction is measurable but does
not justify retaining oversized owners. All four block profiles are in the JSON.

## Frozen benchmark policy and final measurements

231800 synthetic rows; same A018S construction: many=2318 runs of 100, unique/high/
moderate=2048-row source chunks, uneven=one 115900-row run plus 1159 small runs.
Long-pre uses one pre ID and increasing post IDs. No warmup; fresh sequential process
for every route, block size and repeat; three repeats. No pytest or build ran during
the timing matrix. Existing Windows memory sampler runs at 1 ms; observed peaks are
sampled lower bounds, not full-scale certificates. Timers cover stage scheduling,
primitive work and metrics, with no A018S comparison-accounting wrapper. Independent
A017 oracle tests establish correctness; benchmark digests separately match all routes.
An initial completed matrix was discarded because profiling failed before persistence;
the reported matrix is the complete rerun, persisted per shape. No fastest-run selection.

Selected **B=16384** balances measured times and 2-MiB fixed scratch. Tests also cover
B=2,3,4,7 and operational B=4096,16384,65536,262144. B is absent from scientific identity.

| Shape | A018 median s | A018S median s | A018T median s | A018S/A018T | Runs |
|---|---:|---:|---:|---:|---:|
| many | 3.703944 | 2.234714 | 0.195398 | 11.436708x | 2318 |
| unique | 2.013373 | 1.212585 | 0.042105 | 28.799218x | 114 |
| high | 0.004763 | 0.003351 | 0.006586 | 0.508837x | 114 |
| moderate | 1.741314 | 0.943129 | 0.043510 | 21.676196x | 114 |
| few | 3.493910 | 2.057393 | 0.149072 | 13.801341x | 1160 |
| long_pre | 2.655383 | 1.524693 | 0.028303 | 53.870360x | 114 |

Individual times (seconds), in repeat order:

| Shape | A018 | A018S | A018T B=16384 |
|---|---|---|---|
| many | 3.697731, 3.804839, 3.703944 | 2.191786, 2.234714, 2.237395 | 0.193927, 0.197163, 0.195398 |
| unique | 2.023642, 1.995414, 2.013373 | 1.239020, 1.212585, 1.206262 | 0.041165, 0.042105, 0.043582 |
| high | 0.004987, 0.004763, 0.004637 | 0.003356, 0.003334, 0.003351 | 0.006305, 0.006586, 0.006798 |
| moderate | 1.741314, 1.769743, 1.707327 | 0.943129, 0.948164, 0.933676 | 0.045948, 0.043510, 0.043338 |
| few | 3.488080, 3.537367, 3.493910 | 2.135179, 2.057393, 2.052906 | 0.149072, 0.147995, 0.150430 |
| long_pre | 2.657689, 2.641148, 2.655383 | 1.524693, 1.517320, 1.534550 | 0.026928, 0.029743, 0.028303 |

Block-size sweep medians (seconds):

| Shape | 4096 | 16384 | 65536 | 262144 |
|---|---:|---:|---:|---:|
| many | 0.199335 | 0.195398 | 0.208539 | 0.208179 |
| unique | 0.042366 | 0.042105 | 0.049632 | 0.050673 |
| high | 0.006756 | 0.006586 | 0.006489 | 0.007007 |
| moderate | 0.039692 | 0.043510 | 0.047677 | 0.047109 |
| few | 0.153003 | 0.149072 | 0.164406 | 0.177175 |
| long_pre | 0.039086 | 0.028303 | 0.031433 | 0.033779 |

High overlap regresses by 1.9655x: 3.351 ms -> 6.586 ms (114 runs, only 2260
logical staged input rows). Fixed NumPy calls dominate very short already-compressed
runs. This is a real limitation; no adaptive scalar route is hidden in A018T. Other
five shapes win materially; no large-row overlap catastrophe is observed. Large
complete-overlap primitive timing above separately checks native vector grouping.
Production/default preparation remains unchanged; experimental callers accept the tradeoff.

Many shape: 12 stages, 2317 merges, groups 1159,579,290,145,72,36,18,9,5,2,1,1.
A018 reads 5443600 logical rows, emits 2721800; A018S/A018T consume and emit
2721800 each, no compaction. A018S iterates 2721800 times; A018T 4723 blocks/tail
copies, a 99.826475% iteration reduction. Sorts=2389, searches=14334, bounded concat
calls=7167. Upper scratch=2097152 bytes; max block=16384. Loop counts exclude fixed
three-column loops and native internals; they are not a count of every Python opcode.
Native sort/mask/gather copies add physical passes; logical rows_read is not DRAM
traffic and first_scan_rows is a compatibility counter, not a scalar scan in A018T.
A018S/A018T seconds per million logical rows are 0.821042 / 0.071790 respectively.

Historical A018S authoritative 3.722652 / 2.251169 s and 1.653653x remain intact;
current controlled A018 / A018S / A018T medians are 3.703944 / 2.234714 / 0.195398 s.
Primary speedup=11.436708x; cumulative current-baseline speedup=18.955857x.

| Shape | A018S private | A018T private | A018S working set | A018T working set |
|---|---:|---:|---:|---:|
| many | 733929472 | 732434432 | 116125696 | 113999872 |
| unique | 730034176 | 730918912 | 113336320 | 109694976 |
| high | 717676544 | 717398016 | 101490688 | 101269504 |
| moderate | 724512768 | 724402176 | 108150784 | 108244992 |
| few | 733196288 | 733057024 | 115146752 | 113455104 |
| long_pre | 731238400 | 726175744 | 113012736 | 109625344 |

All per-route/per-size stage, row, compaction, allocation-bound, sort/search and sampled
memory metrics are in the measurement JSON. No blocks are retained for these counters.

## Full-scale model and disposition

At P=151856684,C=25582938,N=2318,B=16384, the tight merge owner/scratch/header bound
is 5493386608 bytes (~5.116 GiB). Active group capacity/compact owner workspace is
<=96C bytes for inputs+capacity plus 24C compaction (120C total), with 2-MiB scratch
added conservatively. This differs from process private bytes. Known A018R P=C,
unique partial rows avoid compaction; payload <=48P plus scratch/headers (~1.146 GiB).
Full preparation structural model remains ~5.37 GiB; the conservative planning
envelope including the historical 1-GiB unproven process allowance and new fixed
scratch is ~6.371953 GiB. **Memory P1 preserved; <=8 GiB proven: No.**

A018R measured merge=549.399792 s. Projections, never real measurements:
- Simple current cumulative speedup model: 28.983115 s.
- Throughput model: 305789355 real logical rows * (0.195398 / 2721800) = 21.952660 s.
- Conservative stress estimate: twice the slower model = 57.966230 s. The 2x factor
  is an explicit operational stress margin, not an empirically proved upper bound.
- Projection disagreement=24.2571% of slower model; extrapolation uncertainty remains.

Stress merge plus known 38.8289515-s nonmerge work gives sign entry ~96.795181 s,
leaving 503.204819 s for the unresolved downstream allowance. Interrupted sign work
already establishes >11.775042 s additional work, not zero. No finite conservative
upper duration for sign/weights/CSR/digests/runtime/cleanup is evidenced; the 503-s
headroom cannot be substituted for such evidence. **600-s completion proven: No.**

**B1 ? BLOCKWISE NUMPY MERGE IMPLEMENTED AND CERTIFIED.**
**R2 ? MERGE IMPROVED, BUT <600-S COMPLETION STILL TOO UNCERTAIN.**
**A18T-B ? BLOCKWISE NUMPY MERGE EXACTLY CERTIFIED; REAL RETRY STILL NOT JUSTIFIED.**
A18S-B remains authoritative. The only proposed next task is A018U as defined above.
No real retry is performed, proposed for execution now, or silently authorized.

## Validation and publication

Final targeted application command collects every test_application module: **863 passed**,
including **A018T 283**, A018S 95, A018 97, A018R 8, A017 79, A016 68, A015 59,
A014 12, A013 17 and A011 8, plus earlier application suites. Existing Feather V1
fixture emits its expected deprecation warning. A014 Job Object contained-tree memory,
time and injected-accounting-failure regressions remain **CERTIFIED_SYNTHETIC**;
no watchdog redesign or real worker run.

Full pytest: **1110 passed, 14 expected CUDA/unenabled-real skips**, one existing
Feather V1 warning, 156.36 s. All stateful/runtime and application regressions pass.
Compileall src/scripts/tests passes. Tracked integrity passes for 9 historical files
and their internal identities. Both working and staged diff checks pass. uv build
produces the 0.3.0 source distribution and wheel successfully. Package version is
unchanged at 0.3.0; active tracked GitHub Actions workflows=0; stash remains empty.
Publication is authorized: commit message **perf: add blockwise NumPy edge merge**,
then git push origin master. Final exact three-way Git identity and clean-state
verification are returned in the final report; no self-referential commit SHA is
embedded in this committed plan.
Commit scope is exactly this plan, compact measurement JSON, synthetic certification
script, experimental blockwise module and A018T test module. No old scientific source,
historical records, raw datasets, workflows or version files are modified.
