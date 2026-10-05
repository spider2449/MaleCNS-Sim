# Application A018S ? bounded CPU staged-merge optimization

## Authorization and gate

Explicit authorization: ?? A018S. Root derived with git rev-parse --show-toplevel:
D:/spider/working/MaleCNS-Sim. Before mutation local HEAD, origin/master and live
GitHub master matched f9995c51604f0683b471afda63687665502e858b. Clean worktree,
empty stash, package 0.3.0, zero tracked Actions workflows. No AGENTS.md file was
found in the checkout; the supplied instructions govern this plan and English code.

A018R-TIME-LIMIT is preserved: one historical attempt, zero completions/advances,
600.0037853 s stop in sign construction; merge 549.399792 s in 12 stages;
source 1.732872 s, endpoint membership 7.713078 s, local grouping 3.737166 s,
downstream projection/CSR 7.778817 s. Peak aggregate private 5464100864 bytes,
working set 4421849088 bytes; 8-GiB cap not hit, no fallback. Expected real digest
ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f remains
an expectation, never an A018S measurement. No real source was opened in A018S.

## Baseline audit and measured cause

The unchanged A018 module remains the performance baseline. Adjacent source-order
binary groups use a first Python cursor scan to count/check, an exact allocation,
and a second cursor scan to compare/check/write. Each cursor iteration repeatedly
indexes NumPy int64 scalars and compares two int64 keys lexicographically. Equality
converts two counts to transient Python integers for checked addition. No retained
per-edge object exists. Both scans repeat all cursor comparisons and equality work.
Tail rows also pass through Python, although exhausted-side comparisons are skipped.
Stage bookkeeping releases input slots immediately, carries odd runs without copying,
and records scalar schedules only. No repeated traversal beyond these stages exists.

Pre-implementation 400000-input-row primitive profile: disjoint count/check
0.2105592 s, write 0.3020389 s, allocation 0.0000855 s; complete overlap
0.3895163 s, 0.4239988 s, allocation 0.0000576 s. Each scan performs 200000
live-key comparisons; disjoint emits 400000 rows, overlap 200000. Allocation is
not the dominant measured cost. The write-minus-count difference includes output
stores and branches; it does not isolate native memory bandwidth. Equality is
materially slower per emitted pair. Primary bottleneck **T1 ? Python per-row
scanning**; T2 (duplicate scan) and T3 (repeated stages) contribute. No unsupported
claim that comparison alone, NumPy scalar access alone, or allocator cost dominates.
Repeated profile and per-merge wall/counter evidence are in the compact JSON report.

## Operation-count model

Let N be run count, P initial rows, A_g active input rows and O_g emitted rows.
For source-order binary merging, stages=ceil(log2 N), merge groups=N-1, with odd
carries neither read nor written. Baseline first reads=sum A_g, second reads=sum A_g,
writes=sum O_g; row touches=2 sum A_g + sum O_g. A surviving globally unique row
at depth d is read 2d times and written d times. Overlap reduces subsequent rows,
never permits early thresholding. These are logical triple-row visits, not the
number of individual scalar loads or physical DRAM transactions.

For 2318 equal-size unique runs: 12 stages, 2317 groups, group counts
1159,579,290,145,72,36,18,9,5,2,1,1; sum A_g=27218 times one run's row size.
Thus mean depth=27218/2318, not exactly 12 because carries skip stages. The physical
A016 source shape is 2318, but A018R actually admitted 2313 nonempty runs. Its
measured baseline reads=611578710, first=second=305789355, writes=305789355,
touches=917368065. No synthetic compression is substituted for those counters.

## At most three candidates

A. Single-pass upper-bound two-way output: selected. Removes one Python scan,
retains exact keys/counts and the existing schedule. Capacity A_g; compact if O_g<A_g.
B. Native higher fan-in: evaluated analytically and rejected within this task.
K=2/4/8/16 imply 12/6/4/3 outer stages at 2318 runs. Conventional Python heap
would create transient tuple/int objects each emitted row plus O(K) heap records;
this is rejected for T1 and the explicit no-edge-object constraint. Numeric heap
would require a Python O(log K) loop per output or broader native work. Binary
composition inside larger groups preserves the same inner row traversals and does
not provide a true speedup. No k-way CPU measurement or implementation is claimed.
C. Bounded group concatenate/sort using existing NumPy grouping: rejected for
full-scale worst-case memory. A group's input can reach 2C; inherited 128A grouping
coexistence plus unmerged inputs can exceed 8 GiB at P=151856684,C=25582938.
A blockwise numeric search/scatter design might avoid this but requires separate
workspace/lifetime analysis and is not stacked into A018S. No new compiled dependency.

For true K-way inputs A<=KC, outputs O<=C; whole-stage input rows<=P. Exact-output
payload would be 24(P+C), upper capacity 24(P+KC), plus native workspace and possible
compact copy 24C. K=4/8/16 upper capacities increasingly threaten P1; they are not
selected. Reads/writes are sum A_g/sum O_g per scan, compression-dependent; unique
balanced trees approach P ceil(logK N). Determinism requires fixed source groups
and canonical ties. K=2 is the only timed implemented fan-in. Higher-fan-in timings
are unavailable, not inferred from composing binary tests. Size-aware scheduling
is not selected: deterministic size/ordinal ordering would be possible but changes
overflow discovery ordering and needs a separate audit. No multiprocessing/threading.

## One implementation, exactness and ownership

**O1 ? ONE BOUNDED EXACT OPTIMIZATION JUSTIFIED AND IMPLEMENTED.** New experimental
single_pass_integer_merge module leaves A018 and A017 oracles intact. The new loader
must be selected explicitly; production and A018R harness dispatch remain unchanged.
The single cursor scan is the unchanged comparison/addition logic with immediate
writes into three owned int64 arrays of capacity len(left)+len(right). No key packing:
contracts admit endpoints up to INT64_MAX, so two uint32 fields are unsafe. Two int64
keys remain. No new per-edge object, heap, permutation, concatenate, or sort.

Unique output returns those exact owners directly. Any unused capacity triggers
three exact-sized copy allocations (operational compaction threshold zero). During
copy both old capacity and all exact outputs are counted; no sliced view escapes.
Compaction is unconditional for waste, avoiding cumulative retained slack. Output
scientific dtype stays int64; scientific equality/order/threshold are unchanged.
For nonnegative admitted safe totals every intermediate sum is <=final safe sum,
so this unchanged source-order schedule and one checked scan are exact. Overflow
raises OverflowError before returning any output; unchanged A017 exceptional reference
fallback preserves modular reference behavior. No saturation or widening. Threshold
remains solely after complete global aggregation.

Let U=unmerged outside active group, A=active rows, D=completed next-stage rows,
O=logical output. No-overlap peak=24(U+A+D+A). Compact peak conservatively=
24(U+A+D+A+O); U+A+D<=P, A<=P, O<=A. Generic bound=72P+8192+2048(N+1).
With certified global cardinality C: A<=2C,O<=C, hence tight bound=
24(P+3C)+8192+2048(N+1). This includes all old-stage owners, completed next-stage
owners, capacity backing owners, all compact copies, ndarray/list/tuple headers,
scalar schedule records and cursors. No row-sized index/permutation workspace.
Observer callbacks must retain no strong aliases. Inputs and old stage containers
release at the same boundaries as A018; weakrefs prove reclaimability, not OS page
return. Compaction weakrefs prove capacity owners die after return. No retained history.

Full-scale worst structural merge model at P=151856684,C=25582938 is about 5.11 GiB
plus bounded headers; active compact group <=120C bytes (~2.859 GiB). At the known
A018R P=C and globally unique partial keys, compaction is absent and peak merge
payload<=48P (~1.144 GiB), but worst structural planning is retained. Downstream
model remains ~5.37 GiB plus unproven process overhead; planning ~6.37 GiB with
explicit 1-GiB allowance, below unchanged 8-GiB cap. **P1 preserved; <=8 GiB proven:
No.** No full preparation memory certificate; observed small synthetic allocator
increases are reported, not concealed. Watchdog remains necessary.

## Synthetic certification and decision

Fixtures cover all twenty requested adversarial shapes, exact oracle counts,
canonical ordering, empty/one/odd runs, MAX endpoints, safe MAX sum, overflow fallback,
threshold crossing/miss, self edges, mixed overlap, deterministic output/schedule,
source partitions and binary composition with fan-in group boundaries 2/4/8/16.
That last test is semantic composition invariance, not a k-way performance claim.
Prepared synthetic results compare against the unchanged A017 scientific oracle,
including neuron order, topology, CSR indptr/indices/data, weights, signs, delays,
projection/prepared/runtime identities. No stateful real advance or real data test.
Baseline A018 remains independently regression-tested.

Benchmark: five shapes, 231800 logical synthetic rows, three repeats, fresh process
per route/repeat. Many-small has exactly 2318 runs of 100 unique rows; uneven has
one 115900-row run plus 1159 small runs. Other fixtures use 2048-row chunks; high
cardinality 10, moderate 10000, unique compression 1.0x. Windows process private/WS
sampled at 1 ms. Peaks are sampled lower bounds and include interpreter/generation
allocator retention. Numeric comparison-count wrapper runs identically on both
routes and adds O(log output_rows) boundary accounting per call; raw timers include
that overhead. No arrays retained in counters. Final matrix runs without concurrent
pytest; earlier exploratory matrix is replaced. Row-touch totals include compaction
reads and writes, so high overlap can reduce CPU without reducing logical touches.

### Final isolated measurements

Times are median seconds; peaks are maxima over three repeats, in bytes.

| Shape | Runs | Stages/calls | Baseline s | Optimized s | Speedup | Baseline reads/writes | Optimized reads/writes | Touches before/after | s per million reads before/after | Private before/after | WS before/after |
|---|---:|---|---:|---:|---:|---|---|---|---|---|---|
| high | 114 | 7/113 | 0.006087 | 0.003947 | 1.5422x | 4520/1130 | 2260/1130 | 5650/5650 | 1.3466/1.7464 | 717672448/717742080 | 101101568/101220352 |
| moderate | 114 | 7/113 | 1.699785 | 0.939071 | 1.8101x | 1925952/741176 | 962976/741176 | 2667128/2264152 | 0.8826/0.9752 | 724451328/724484096 | 108027904/108105728 |
| unique | 114 | 7/113 | 2.016392 | 1.222577 | 1.6493x | 3230656/1615328 | 1615328/1615328 | 4845984/3230656 | 0.6241/0.7569 | 729653248/730595328 | 112295936/113184768 |
| many | 2318 | 12/2317 | 3.722652 | 2.251169 | 1.6537x | 5443600/2721800 | 2721800/2721800 | 8165400/5443600 | 0.6839/0.8271 | 734052352/732573696 | 116559872/115871744 |
| few | 1160 | 11/1159 | 3.502337 | 2.071149 | 1.6910x | 5038800/2519400 | 2519400/2519400 | 7558200/5038800 | 0.6951/0.8221 | 733855744/733872128 | 115232768/115200000 |

Compaction adds read/write pairs per emitted row only on overlapping merge calls; raw JSON reports these separately. First/second scan counts baseline are half its reads each; optimized first equals its reads and second is zero. Native compaction is counted separately. Key comparison and equality-event counts are exact logical cursor events (two scans baseline, one optimized). Both routes have identical schedules and triple digests. Seconds per million total touches can be computed from the recorded wall time and touch total; these are not physical memory-throughput measurements.

### Fixed fan-in analytical unique-case model

For 2318 runs of 100 unique rows, modeled native single-scan K-way scheduling:

| K | Stages | Groups | Row reads | Row writes | Max active inputs | Exact output | Numeric cursor workspace | CPU |
|---|---:|---:|---:|---:|---|---|---|---|
| 2 | 12 | 2317 | 2721800 | 2721800 | <=24 min(P,2C) bytes | <=24C bytes | O(2) plus unimplemented native work | measured above |
| 4 | 6 | 774 | 1388000 | 1388000 | <=24 min(P,4C) bytes | <=24C bytes | O(4) plus unimplemented native work | not measured; rejected design |
| 8 | 4 | 333 | 927200 | 927200 | <=24 min(P,8C) bytes | <=24C bytes | O(8) plus unimplemented native work | not measured; rejected design |
| 16 | 3 | 155 | 694000 | 694000 | <=24 min(P,16C) bytes | <=24C bytes | O(16) plus unimplemented native work | not measured; rejected design |

### Projections and exact next task

Selected real-shape unique benchmark speedup 1.653653x gives simple real merge projection **332.234034 s** (549.399792/speedup). Independently, unchanged source-order schedule on the recorded real unique partials would read 305789355 rows once; synthetic optimized throughput gives **252.914794 s**. This second model uses A018R row counters and its 12-stage structure, not real execution. Difference is about 24% relative to the simple estimate; classify **material extrapolation uncertainty**. Full-size cache behavior, instrumentation, row distribution and OS load are not proven by these reduced fixtures. High-duplication throughput does not apply to the real unique-key shape.

Using the slower simple estimate plus A018R known 38.8289515 s before sign construction outside merge gives projected sign entry ~371.063 s, leaving ~228.937 s of the unchanged 600-s budget. This is an allowance, not a measurement of remaining work. Sign construction was interrupted; effective graph, outgoing CSR, digest/identity and runtime construction have no completed A018R timings. Unmeasured downstream work and extrapolation uncertainty prevent a strong time certificate. **600-s real completion proven: No.**

**T2 ? OPTIMIZATION IMPROVES MERGE BUT 600-S COMPLETION REMAINS TOO UNCERTAIN.**

**A18S-B ? EXACT CPU MERGE OPTIMIZATION CERTIFIED; REAL RETRY STILL NOT JUSTIFIED.**

Exactly one next bounded proposal: **A018T ? Bounded Blockwise NumPy Two-Key Merge Design and Synthetic Certification**. Analyze and, only if defensible, certify one sequential blockwise search/scatter algorithm using two int64 keys, no new native dependency, no global unbounded concatenate, checked sums, unchanged threshold and identity, explicit transient/owner bound compatible with P1, the independent A017 oracle, and 2318-run synthetic evidence. Address remaining T1 and projection uncertainty; no real source/preparation/retry or advance. Separate authorization required. No A018SR execution or retry proposal is justified by this T2 decision.

## Firewall

A018S full-real preparations=0, completed=0, advances=0, Arena=0, behavioral=0, scientific experiments=0, raw downloads=0, Task017 new units=0, Task017Q=0, archive writes=0, BANC=0. Historical Task016 unchanged; Task017 unchanged / NOT_ROBUST; B:/MaleCNS-Archive unchanged. No biological claim. No GPU, policy change, tag, release or version mutation. Existing synthetic stateful tests are authorized regressions. Production default unchanged.

## Validation and publication

Targeted A018S 95 passed; unchanged A018 97 passed (192 combined). Selected prior
regressions 251 passed: A017 79, A016 68, A015 59, A014 12, A013 17, A011 8,
A018R 8. Full pytest: 827 passed, 14 expected CUDA/unenabled real skips, one existing
Feather V1 deprecation warning, 115.41 s. All 580 application cases pass; available
stateful/runtime regressions pass. Watchdog contained-tree regressions remain
CERTIFIED_SYNTHETIC (no redesign, no full-real worker).

After the full suite, the conservative compaction header metric was corrected from
9 to 12 ndarray headers; fixed allowance and algorithms unchanged. Targeted A018S
was rerun on final code. Derived throughput fields were added to the report; raw
benchmark timings are unchanged. Compileall src/scripts/tests, tracked integrity
(9 files/internal identities), git diff --check, and uv build pass. Package 0.3.0;
zero tracked workflows, no version/tag/release mutation. Only the five A018S files
are staged. Commit message: perf: optimize bounded edge merge. Push and three-way
final identity verification are required and reported in the final response.
