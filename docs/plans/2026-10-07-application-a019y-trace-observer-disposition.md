# A019Y trace completeness and observer disposition

Authorization: **授權 A019Y**. Evidence-only review on 2026-10-07.
Root derived by `git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`.
Starting HEAD, origin/master and live GitHub master all equal
`416e9cfdb9cf1406c88f9d1fc44950109aa090ad`. Worktree clean, staging and stash
empty, version 0.3.0, tracked workflows 0. All start gates passed.

Plan: verify committed custody and retained executed text; inventory diagnostics;
review installed 2025.5 documentation and exact capture argv; adjudicate completeness,
observer uncertainty and one possible protocol change; record terminal disposition;
run diff check, commit/push this report only and verify final repository state.

## Terminal disposition

**A019Y-A — GPU PERFORMANCE/PROFILING LINE PAUSED; A019X OBSERVATION LIMITS
NOT WORTH ANOTHER RECAPTURE.** Worker **W2**, completeness **COMP-B**, observer
**OBS-B**, candidate information value **IV-B**. No recapture justified.
Exact next direction: **evidence-only application roadmap decision outside the
current GPU performance line**. No automatic A019Z profiling task.

Preserve **A019X-C — INDETERMINATE**, **A019W-B**, **A019V-C / G4**,
**A019T-A / EQ-B**, **A019S-A**. **FULL-REAL GPU ATTEMPT NOT JUSTIFIED**.
EQ-B backend disposition: **RETAIN-CERTIFIED** within its certified scope.
This is a pause in performance research, not deprecation or universal GPU unsuitability.

## Custody and review boundary

Confirmed eight committed A019X artifacts: result, protocol, machine JSON,
`profile_application_a019x.py`, `analyze_application_a019x.py`, and three tests
(`test_application_a019x.py`, `test_application_a019x_analysis.py`,
`test_application_a019x_cleanup.py`). Reviewed their text/static contracts and
A019W/A019V evidence. None was changed. The machine evidence retains schema,
queries, diagnostic rows, execution argv, timing, identities and raw manifest.

Retained local root:
`C:/Temp/malecns-a019x-8939a1d9de604e38848b2c97fac06417`.
Executed runner independently hashed in this review:
**SHA256 5890f2678a053a079a9c8997f616f80029fa38ed76b0fd87666ce0ee5ffbb00d**.
Its retained filename is `profile_application_a019x-executed.py`.
Retained executed runner/protocol, execution-contract JSON, and both export logs
also match their SHA256 entries in the committed raw manifest.
Static diff against current runner contains only the TerminateProcess declaration
and suspended-root assignment-failure cleanup correction. Capture argv and measured
hot path are unchanged; current runner is **not byte-identical** to executed runner.
The pre-completion protocol is retained as `protocol-executed.md`.
Raw exports/logs and binary trace filenames remain local temporary evidence,
not an archival or independent backup claim. No binary trace/SQLite was opened,
no profiler export was rerun, and no registered payload was inspected.

## Diagnostic inventory and identity

Source: committed `cases[].timeline.diagnostic_problems` in
[a019x-synthetic-gpu-profiling-evidence.json](a019x-synthetic-gpu-profiling-evidence.json),
exported from DIAGNOSTIC_EVENT. The following appendix preserves every warning
row exactly, including numeric source, severity, timestamp type and process identity.
No retained warning explicitly reports dropped/lost CUDA or NVTX records as fact.

Worker identities are S1 PID 13112/globalPid 281694959566848 and S4 PID
14356/globalPid 281715830423552. They are matched by analyzer worker/context/kernel
identity, not guessed from diagnostic wording. Other Python identities are S1
PID 356/globalPid 281480949399552 and S4 PID 18512/globalPid 281785556533248;
these are launcher processes in the retained contained inventories, distinct from
Nsight roots 16668/19880 and CUDA workers. GlobalPid 281474976710656 has no ordinary
worker PID; treat its ETL diagnostic as tool/session-level, exact process unknown.

All CUDA/NVTX warning rows: severity 2/Warning, source 3, timestampType 2.
ETL warning: severity 2/Warning, source 2, timestampType 1.
Numeric source/type IDs are preserved without inventing their semantic names.
Do not sort types 1 and 2 into one chronology or equate them to public NVTX clocks.

| Exact message (other than ETL, reproduced in appendix) | Literal diagnostic claim | Affected evidence |
|---|---|---|
| Not all NVTX events might have been collected. | Possible loss; completeness not guaranteed | NVTX; worker or launcher as identified |
| No NVTX events collected. Does the process use NVTX? | Reported absence in diagnostic scope; scope unresolved | NVTX; not process identity loss |
| Not all CUDA events might have been collected. | Possible loss, not confirmed loss | Worker CUDA APIs/kernel/copy/memset coverage potentially affected; no subclass specified |
| CUDA profiling might have not been started correctly. | Possible collection-start failure | Launcher CUDA; no actual CUDA workload there |
| No CUDA events collected. Does the process use CUDA? | Reported absence | Launcher CUDA; expected without CUDA workload |
| ETL/WPT warning | Auxiliary merged ETL creation failed because tooling unavailable | ETL output; no explicit CUDA/NVTX loss assertion |

Worker disposition **W2 — POSSIBLE RECORD LOSS / COMPLETENESS NOT GUARANTEED**.
The worker's no-NVTX message cannot literally describe the entire final export:
each has a named public range. Its diagnostic scope/cause is unresolved, not
safely benign. The modal CUDA/NVTX warnings are not W1 and cannot be upgraded to
W3 from scheduler counts. Relevant Info rows count CUDA events (S1 23,978),
CUPTI events/buffers (S1 29,454/20), and report stopping; these are different
record populations, not a conservation equation proving loss or completeness.
No affirmative all-used-record-class coverage assurance was found in retained
text or installed documentation.

Launcher disposition: **irrelevant to CUDA-worker record completeness**, narrowly.
These non-CUDA launcher diagnostics neither establish worker loss nor clear its W2.
Process identities are usable for the observed records; no retained warning says
process/thread identity records were lost.

## ETL/WPT and completeness gate

**ETL-A — irrelevant to current CUDA/NVTX completeness question**. Installed
User Guide's Custom ETW Trace and WDDM sections describe per-provider ETL and a
merged ETL containing captured sources for viewing in external tools such as GPUView.
It provides an additional ETW interchange/viewing artifact, not a recovery of
uncollected CUPTI events. Export documentation describes SQLite export from
`.nsys-rep`; retained export argv/metadata explicitly name `.nsys-rep` input and
SQLite output. Analyzer uses NVTX_EVENTS, CUPTI kernel/runtime/driver/memcpy/memset,
context, metadata and diagnostics tables; it reads no ETL. Both exports exited 0.
Lack of WPT does not itself imply CUDA/NVTX loss. Installing WPT has no demonstrated
value for proving completeness of these used classes; no installation recommended.

**COMP-B — NOT PROVEN COMPLETE**. Existing installed tooling and documentation
permit inspecting present records but do not retrospectively certify all used
record classes. Completeness cannot be demonstrated from this retained evidence,
with or without a merged ETL. This is not COMP-C: possible loss is not proven loss.
It is not COMP-D: coverage matters to timeline attribution even though pausing is
now the decision. Named ranges and exactly 200 schedule_ordered launches prove
those records present, not all other operations captured.

## Exact executed features and qualitative cost

Executed workload argv includes `--trace=cuda,nvtx`,
`--capture-range=cudaProfilerApi`, `--capture-range-end=stop`,
`--cuda-memory-usage=false`, `--cuda-trace-all-apis=false`, `--sample=none`,
`--cpuctxsw=none`, `--python-sampling=false`, `--gpu-metrics-devices=none`,
`--gpuctxsw=false`, `--kill=false`, `--force-overwrite=false`.
Profiler start/stop and flushing are outside the public wall timer. Only third
advance is captured; first two are retained warmups. No per-step NVTX instrumentation.

| Feature | Actual status | Expected cost if enabled, qualitative |
|---|---|---|
| Selected CUDA runtime/driver API trace | Enabled; all-API expansion disabled | HIGH potential on dense short-call workload; per-API interception |
| Kernel activity/correlation trace | Enabled, observed | MEDIUM; high aggregate event volume, actual magnitude UNKNOWN |
| Memcpy/memset activity | Enabled, observed | MEDIUM; per-record cost, actual magnitude UNKNOWN |
| NVTX public range | Enabled, one range per case | LOW for sparse explicit annotation |
| Process-tree tracing/identity | Launcher and worker observed | UNKNOWN; no stack sampling implied |
| CUDA buffering/flush | Enabled as part of CUDA collection; interval unspecified (documented default 0) | UNKNOWN; buffer saves may impose cost |
| CPU/Python sampling and CPU/GPU context switches | Explicitly disabled | No enabled cost assigned |
| OS runtime trace, WDDM trace/custom ETW | Not selected by trace=cuda,nvtx | No enabled cost assigned |
| CUDA backtraces/stacks | Not requested; documented default none; sampling disabled | No enabled cost assigned |
| CUDA memory-usage metrics, GPU metrics, all CUDA APIs | Explicitly disabled | No enabled cost assigned |
| CUDA Event completion trace, UM page-fault tracing | Not requested; documented defaults false | No enabled cost assigned |

These labels are qualitative mechanism-based expectations, not measured attribution.
Installed documentation: `C:/Program Files/NVIDIA Corporation/Nsight Systems
2025.5.2/documentation/UserGuide/index.html`, CLI options (lines 675-774),
CUDA Functions Skipped by Default (5853 onward), SQLite examples (4002-4023),
ETL retention (4816, 6619). Installed version provenance is retained in X as
2025.5.2.266 and export schema 3.24.0. No tool executable was invoked in Y.

## Observer analysis and retained conditional evidence

S1 control 344.390400 ms, profile 459.817500 ms, ratio 1.335164: frozen 25%
threshold exceeded. S4 control 863.992800 ms, profile 856.625900 ms, ratio
0.991473: threshold not exceeded. S4 below one is neither negative overhead nor
speedup. Both are single-position observations, not distributions.

**OBS-B — mixed protocol/environment effect**. Per-event interception and buffer
handling plausibly affect short-operation workloads. S1 has 7,098 kernels, 7,097
at most 10 us; S4 has 12,476 kernels, 12,273 at most 10 us. Fixed event cost can
occupy a larger fraction of a small-workload call; S4 has more events but longer
useful device work. Counts alone cannot explain the observed S1 difference.
Sequential fresh processes, different warmup/cache histories and uncontrolled
background load confound the comparison. Exact root cause cannot be identified;
no claim that a specific feature caused 33.5164% distortion. No ratio correction.

| Conditional observation | S1 | S4 |
|---|---:|---:|
| Public NVTX range, ms | 459.825503 | 856.636691 |
| schedule_ordered, ms / public share | 0.389826 / 0.085% | 176.682688 / 20.625% |
| Device activity union, ms / public share | 12.157735 / 2.644% | 224.411461 / 26.197% |
| Host CUDA API union, ms | 200.276734 | 481.565184 |
| GPU idle inside host APIs, ms | 188.137618 | 257.536941 |
| GPU idle outside host APIs, ms | 259.530150 | 374.688289 |
| Conservative idle prefix before next correlated submission, ms / share | 87.858061 / 19.107% | 104.263449 / 12.171% |

All remain **conditional on collection coverage**. Frozen X-A dispatch/pre-submission
50% and X-B device-dominant 80% thresholds remain unchanged; neither reached.
Six workers, 18 advances, no workload retry, S1/S4 EQ-B PASS preserved.
The many-short-operation structure and specific scheduler count are established;
Python dispatch dominance, device dominance and complete coverage are not.
Existing trace does **not** support accepted bottleneck attribution.

## One candidate, same H1 and information value

Only candidate considered: explicitly set **`--cuda-flush-interval=10000`** instead
of the executed unspecified/documented-default-0 interval, deferring periodic
buffer saves beyond each subsecond public range while retaining end-of-collection
flush. Installed option documentation says nonzero intervals on CUDA 11+ can
reduce save overhead by retaining/allocating buffers until the interval expires.
This is a plausible buffering candidate, not a proven correction: retained evidence
does not show a buffer save inside S1's public range, that save overhead caused
its distortion, or that changing this option clears worker warnings. The runtime
version-dependent behavior and actual buffer pressure would remain uncertainties.
No option is changed here. No new installation required by this candidate.

Same H1 remains structurally testable: unchanged production, fixtures, 200-step
advance, capture boundary and CUDA/NVTX categories retain public range, API
correlations, kernel/copy/memset records, scheduler count and conservative
pre-submission analysis. No replacement attribution rule or threshold is proposed.
Removing CUDA APIs or device classes would break those requirements and is not
proposed. Existing unnecessary expensive features are already disabled.

**IV-B — MEDIUM**, not IV-A. Better buffering might improve observation, but does
not offer evidence-backed removal of both blockers or a likely threshold-crossing
architecture target. Conditional shares are well below the frozen dominance
thresholds; this is not proof of H1 rejection. V already records G4 and 80/80
CPU wins, while EQ-B retains correctness value. A cleaner trace would not reopen
V, justify full-real or authorize optimization. No single correction with HIGH
expected decision value is established. Thus no A019Z implementation/recapture
recommendation; stop the diagnostic chain and use the roadmap direction above.

## Validation and zero activity accounting

Documentation/static review only. `git diff --check`: PASS (also repeated on
staged report before commit). No tests or compileall executed; no executable code
changed. Commit this report only, push origin master and verify local/origin/live
identity, clean worktree/staging, empty stash, version 0.3.0 and workflows 0.
Containing commit/final SHA reported externally to avoid self-reference.

Profiler runs=0; recaptures=0; GPU simulation runs=0; CPU simulation runs=0;
synthetic timing runs=0; CUDA/CuPy preflights=0; tool installations=0;
dependency/environment changes=0; full-real preparations=0; real advances=0;
A019D/A019L reruns=0; registered payload reads=0;
Arena/interventions/downloads/archive writes=0; optimizations=0;
tags/releases/version bumps=0. Counters describe performed-command scope,
not independent native telemetry or newly executed firewall certification.

## Exact retained warning rows
| Case | Exact text | globalPid / role | Source | Severity | Timestamp type | Raw timestamp |
|---|---|---|---:|---|---:|---:|
| S1 | Not all NVTX events might have been collected. | 281694959566848 / CUDA worker | 3 | 2 / Warning | 2 | 34768300 |
| S1 | No NVTX events collected. Does the process use NVTX? | 281694959566848 / CUDA worker | 3 | 2 / Warning | 2 | 34773400 |
| S1 | Not all NVTX events might have been collected. | 281480949399552 / Python launcher | 3 | 2 / Warning | 2 | 34774600 |
| S1 | No NVTX events collected. Does the process use NVTX? | 281480949399552 / Python launcher | 3 | 2 / Warning | 2 | 34776200 |
| S1 | Not all CUDA events might have been collected. | 281694959566848 / CUDA worker | 3 | 2 / Warning | 2 | 34779100 |
| S1 | CUDA profiling might have not been started correctly. | 281480949399552 / Python launcher | 3 | 2 / Warning | 2 | 34782500 |
| S1 | No CUDA events collected. Does the process use CUDA? | 281480949399552 / Python launcher | 3 | 2 / Warning | 2 | 34783500 |
| S1 | NVIDIA Nsight Systems requires that Windows Performance Toolkit be installed on the target machine to create a merged ETL file of the trace session. Could not detect Windows Performance Toolkit, therefore the session's merged ETL file was not created. To fix this, please install Windows Performance Toolkit on the target machine. | 281474976710656 / tool/session; process unknown | 2 | 2 / Warning | 1 | 1115151800 |
| S4 | Not all NVTX events might have been collected. | 281715830423552 / CUDA worker | 3 | 2 / Warning | 2 | 51429800 |
| S4 | No NVTX events collected. Does the process use NVTX? | 281715830423552 / CUDA worker | 3 | 2 / Warning | 2 | 51434600 |
| S4 | Not all NVTX events might have been collected. | 281785556533248 / Python launcher | 3 | 2 / Warning | 2 | 51435800 |
| S4 | No NVTX events collected. Does the process use NVTX? | 281785556533248 / Python launcher | 3 | 2 / Warning | 2 | 51437200 |
| S4 | Not all CUDA events might have been collected. | 281715830423552 / CUDA worker | 3 | 2 / Warning | 2 | 51439100 |
| S4 | CUDA profiling might have not been started correctly. | 281785556533248 / Python launcher | 3 | 2 / Warning | 2 | 51441800 |
| S4 | No CUDA events collected. Does the process use CUDA? | 281785556533248 / Python launcher | 3 | 2 / Warning | 2 | 51443000 |
| S4 | NVIDIA Nsight Systems requires that Windows Performance Toolkit be installed on the target machine to create a merged ETL file of the trace session. Could not detect Windows Performance Toolkit, therefore the session's merged ETL file was not created. To fix this, please install Windows Performance Toolkit on the target machine. | 281474976710656 / tool/session; process unknown | 2 | 2 / Warning | 1 | 1498167300 |
