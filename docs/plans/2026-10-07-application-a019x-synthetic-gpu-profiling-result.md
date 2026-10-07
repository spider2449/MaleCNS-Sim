# A019X bounded synthetic GPU profiling result

**A019X-C: INDETERMINATE.** The six-worker, 18-advance diagnostic completed
without a workload retry. S1/S4 numerical comparisons pass EQ-B and each trace
contains 200 ordered scheduler launches. Collection-completeness warnings and
S1's material observer effect prevent accepting H1 as the dominant cause or
rejecting it in favor of device execution. Preserve A019W-B, A019V-C/G4,
T-A/EQ-B and S-A. **Full-real remains NOT JUSTIFIED.**

Authorization: the user's instruction to continue after the explicit A019X
synthetic-only authorization question. Followed the
[prepared protocol](2026-10-07-application-a019x-synthetic-gpu-profiling-protocol.md).
Baseline local/origin/live master:
`95f53df6703ac4aa03a66ff763c5a0427ebde2b2`. Initial dirty scope was only the
earlier protocol. All scientific source, V harness and general firewall pins
pass. Version 0.3.0; workflows zero. No production or UI changes.

## Completion, correctness, and lifecycle

Fixed order: S1 CPU/GPU/TRACE, then S4 CPU/GPU/TRACE. Each gets one runtime,
one fresh state and three consecutive 20-ms advances. The first two are retained
warmups; the third is the sole observed 40-60-ms chunk. Exactly six CPU and
twelve GPU calls, two CUDA capture ranges. This is a 60-ms diagnostic per fresh
state, not the historical 240-ms A/B replay or a new performance distribution.

Reused V's generated fixtures and full schedules unchanged. S1 consumed 5/5/5
events; S4 consumed 77/96/74. Full schedules remain 60/948 events at 240 ms,
with both full and consumed-window identities in the
[machine evidence](a019x-synthetic-gpu-profiling-evidence.json). S4 remains
127,400 nodes and 14,687,178 edges, not A019L's real projection.

Four GPU roles each compare initial state and three boundaries against their
case's CPU reference: **16 boundary comparisons PASS**, zero observed floating
error and zero discrete mismatches across state and result fields. Finite floats,
exact shape/dtype/timestep/deadline/pending/order/count rules and frozen
`rtol=atol=2e-13` retained. Snapshots and comparisons outside public timing and
capture. Stable state/graph pointers; no graph reload or extra hot-path barrier.

All six workers exit 0; exports exit 0. Windows Job assignment precedes root
resume, with no breakaway enabled; cleanup verifies empty Job inventory, releases
owned handles and supports repeated close. No orphan observed in the contained
inventory. Batch wall time **53.540757 s**, including sequential workers/exports.
499 workload samples: contained private peak **2,997,886,976 B**, working-set
peak **1,367,076,864 B**. These are sampled process-tree aggregates, not true
within-call native peaks. All frozen time/host caps respected.

## Public wall timing and observer effects

Milliseconds; single observations, not means or a new CPU/GPU speed comparison.
Warmups are retained in machine evidence, including GPU control first-use calls
of 5.768539 s on S1 and 5.651278 s on S4. Existing caches were retained.

| Case | GPU control, chunk 2 | Profiled, chunk 2 | Profiled/control | 25% observer flag |
|---|---:|---:|---:|---|
| S1 | 344.390400 | 459.817500 | 1.335164 | YES |
| S4 | 863.992800 | 856.625900 | 0.991473 | NO |

The S1 difference exceeds the frozen material-distortion threshold. S4's ratio
below one is a single-position observation, not negative profiler overhead or
a speedup. Warmup histories and sequential fresh-process execution differ;
background load was not controlled. No concurrent test/compile workload was
introduced during the batch. Do not correct trace timings by subtracting these
ratios or substitute them for V's historical distributions.

## Conditional timeline observations

SQLite export schema 3.24.0, Nsight Systems 2025.5.2.266. Exactly one named public
NVTX range per case. Worker PID/context/stream and host launch correlations are
recorded. S1 PID 13112, S4 PID 14356; context 1, stream 13 in both independent
captures. Exactly **200 `schedule_ordered` launches per case**, all correlated
to the range's launching thread. Source-level operation estimates are not used
as measured counts.

The following is descriptive accounting of the records present, conditional on
collection coverage. CUDA/NVTX warnings prevent claiming complete coverage.
Intervals are clipped to the public range and merged before computing duration;
host/device percentages overlap and are not added.

| Observation | S1 | S4 |
|---|---:|---:|
| Public NVTX range | 459.825503 ms | 856.636691 ms |
| Kernel records | 7,098 | 12,476 |
| Kernels at most 10 microseconds | 7,097 | 12,273 |
| Ordered scheduler total | 0.389826 ms (0.085%) | 176.682688 ms (20.625%) |
| Device activity union, kernels/copies/memsets | 12.157735 ms (2.644%) | 224.411461 ms (26.197%) |
| Host CUDA API interval union | 200.276734 ms | 481.565184 ms |
| GPU-idle intervals inside host APIs | 188.137618 ms | 257.536941 ms |
| GPU-idle intervals outside host APIs | 259.530150 ms | 374.688289 ms |
| Conservative idle prefix before next correlated submission | 87.858061 ms (19.107%) | 104.263449 ms (12.171%) |
| Memcpy records / total bytes | 2,225 / 9,080 | 2,463 / 15,048 |
| Memset records | 410 | 468 |

All operation-gap correlations needed by the conservative calculation are
present. It attributes only an idle prefix before the next operation's first
correlated host API starts. Already submitted work and the post-device tail are
left unclassified, avoiding false Python attribution of device/driver queue
gaps. Unobserved device records could still affect this conditional calculation.

S4's ordered kernel is a substantial part of observed device work, but its
20.625% public-range share does not demonstrate device-dominant execution.
The device union does not reach the frozen 80% X-B threshold. Conversely,
conservative pre-submission idle prefixes do not reach X-A's 50% threshold.
The many-short-operation premise is supported by measured counts, while H1's
causal dominance remains unresolved.

Host API totals include S4's 2,463 `cudaMemcpyAsync` calls (381.406171 ms
summed API duration), 12,076 `cuLaunchKernel` calls (73.624173 ms), and 2,331
`cudaStreamSynchronize` calls (16.727996 ms). S1 has 2,225 memcpy and 2,215
stream-synchronization calls. These counts are consistent with recurring
compaction/readback work in the inspected CuPy path; that association is an
inference, not per-Python-function attribution. A tiny transferred-byte total
does not eliminate per-call transfer/driver waiting. CUDA API duration can
include queued-device waits, driver work and profiler intervention; it is not
Python execution time. CPU scheduling/stacks were excluded by protocol.

## Collection completeness and frozen disposition

Both reports contain warnings that not all CUDA/NVTX events might have been
collected, including the actual CUDA worker's serialized process identity.
Other warnings refer to the Python launcher, which has no CUDA workload. Both
also report that a merged ETL was not created because Windows Performance
Toolkit was not detected. This does not prove CUDA loss or require an install;
the exact diagnostics and their severity/source/timestamp types are retained.

The named public ranges and expected scheduler counts are present despite
messages about absent NVTX events. These facts do not establish completeness of
every other operation. Diagnostic timestamp types differ, so their chronology
must not be inferred by sorting the raw numbers as one clock. No silent dismissal
of warnings, installation, alternate profiler, or recapture was performed.

The conservative completeness gate fails. Independently, S1 exceeds the observer
threshold, and the conditional measured shares fall between X-A and X-B.
**X-C is required**, not an optimization finding or a universal GPU verdict.

Exactly one next task: **A019Y — evidence-only disposition of trace-completeness
warnings and observer effects**, deciding whether the GPU performance line
should close or whether one separately authorized observation-protocol
correction has sufficient value. It may inspect existing reports/tool
documentation only. No recapture, tooling installation, optimization or
full-real attempt is automatically authorized or started.

## Harness history and final verification

Preparation failures/corrections are preserved in the protocol: a malformed
JUnit option, inherited interactive Python override, incompatible control CLI
switch combination before target launch, and missing stderr forwarding from an
expected failing worker. Each stopped control batch has its own retained output.
Final pre-workload native controls all pass, including a live guarded descendant,
timeout and missing activation. No CPU/GPU workload was repeated after a change.

Post-run source review found a cold cleanup-path defect: if Job assignment
failed, a newly created suspended root could remain outside the Job. The runner
now explicitly terminates that root before releasing handles. A dedicated test
uses real CreateProcessW with injected assignment rejection, verifies the root
was never resumed and has exited, and executes no profiler/workload. The exact
executed runner is retained byte-for-byte with its frozen SHA256
`5890f2678a053a079a9c8997f616f80029fa38ed76b0fd87666ce0ee5ffbb00d`.
The delivered correction changes only that failure cleanup; no scientific
source, measured hot path or captured trace is changed. Current runner is not
claimed byte-identical to the executed runner. The executed protocol is also
retained before its completion status/result link update.

Validation: inherited firewall bootstrap **28 PASS**; final launch/accounting/
real suspended-root cleanup tests **32 PASS**; native controls **4 PASS**.
Guarded compileall of the two new scripts and three tests: **PASS**. Final
tracked/new-file diff checks and exact eight-file scope inventory: **PASS**.
No full pytest or extra
GPU/CPU simulation regression is needed because production is unchanged and
all captured advances are already checked against their CPU oracle.

Raw reports, exports, snapshots, logs, schema/query records and SHA256 manifest:
`C:/Temp/malecns-a019x-8939a1d9de604e38848b2c97fac06417`.
This is retained local temporary evidence, not an archival custody claim.
Nsight also used its own transient `C:/Temp/nsys-report-*.qdstrm` locations;
the output-directory cap does not bound those native spill files. No historical
artifact/archive was written, and no binary report is committed to Git.

Scope: two new scripts, three tests, the protocol, this report and machine
evidence. Full-real preparations/advances, A019D/A019L reruns, registered payload
reads, Arena/intervention runs, downloads, archive writes and production edits
all zero under guarded-scope/performed-command accounting, not independent
native-byte telemetry. Denied probes are retained as controls. No real-time,
full-real performance, Python-only dominance, biological, or native VRAM peak
claim. No release/tag/version bump, commit or push.
