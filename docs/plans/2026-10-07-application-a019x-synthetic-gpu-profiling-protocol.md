# A019X bounded synthetic GPU profiling protocol

Status: **COMPLETED; A019X-C, INDETERMINATE.** See the
[completed diagnostic report](2026-10-07-application-a019x-synthetic-gpu-profiling-result.md).
The user's subsequent
instruction to continue, after the explicit bounded synthetic authorization
question, authorizes implementing and executing this protocol. The original
preparation and its zero-execution accounting below describe the earlier phase.
The pre-execution protocol is retained byte-for-byte with the raw evidence.

The latest completed task is
[A019W](2026-10-07-application-a019w-gpu-performance-disposition.md).
W selects exactly one next task, A019X, and explicitly says it is a recommendation
that is not automatically started or execution-authorized there. This preparation
originally left workload execution pending explicit bounded synthetic authority.
That authority is now supplied by the follow-up instruction. No full-real
attempt, optimization, or automatic follow-up is authorized here.

## Verified starting state

Repository: `D:/spider/working/MaleCNS-Sim`, origin
`https://github.com/spider2449/MaleCNS-Sim.git`, branch `master`.
Local HEAD, origin/master, and live remote master were all
`95f53df6703ac4aa03a66ff763c5a0427ebde2b2` before mutation.
Worktree and staging were clean; stash empty; version 0.3.0;
tracked workflow count zero. An existing detached worktree at
`.kilo/worktrees/clarity-mare`, revision `60fb1ee`, was observed and left alone.

Preserve W-B, V-C/G4, T-A/EQ-B and S-A within their certified scopes.
S4 is the requested-count synthetic fixture, not the A019L full-real projection.
Nothing in this protocol changes the full-real disposition: **NOT JUSTIFIED**.

## Single diagnostic question

GPU-H1: Does repeated per-timestep Python/CuPy dispatch, short-operation launch
cost, and compaction-related waiting make a substantial contribution to the
synchronized 200-step public GPU advance?

Use an unchanged production advance. Observe the host/device timeline, CUDA API
durations, launch correlations, kernel durations/counts, and transfers. Ordered
propagation is measured only as a competing explanation. This is not a search
for optimizations or a replacement CPU/GPU performance matrix.

## Profiler readiness established without workload execution

The installed Windows CLI is:

`C:/Program Files/NVIDIA Corporation/Nsight Systems 2025.5.2/target-windows-x64/nsys.exe`

`--version` returned `2025.5.2.266-255236693005v0`.
`profile --help` and `export --help` returned successfully. No capture, CUDA
preflight, device query, Python import, test discovery, or synthetic advance was
performed. Executable presence and help output do not certify injection,
Python 3.14 sampling, CUDA trace completeness, or contained-worker compatibility.

The installed help supports CUDA/NVTX tracing, `cudaProfilerApi` capture range,
`--capture-range-end=stop`, `--kill=false`, SQLite export, and disabling CPU
sampling/context-switch collection. Use the installed version's syntax as
authority; the current online guide may describe a newer release.
The [NVIDIA User Guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html)
explains capture-range controls and tracing overhead. In particular, tracing
every CUDA API can materially distort short-call workloads. Full API tracing,
hardware metrics, CUDA memory tracing, and Python sampling are excluded from
the initial protocol. Missing Python-stack attribution must remain uncertainty.

## Frozen workload proposal

Reuse `fixture`, `schedule`, `pack`, `capture`, and `compare_arrays` from
`scripts/benchmark_application_a019v.py` without invoking its worker/supervisor,
writing its TARGET, or modifying its committed evidence.

| Case | Nodes | Edges | Projection SHA256 |
|---|---:|---:|---|
| S1 | 128 | 1,024 | `356f66641e82475ac9682f722d11d9aac28e700786c4307d2cbdbe61e2fac132` |
| S4 | 127,400 | 14,687,178 | `aa03c559d83a266375c149142620f48cf024204abde0dcd2dd17affdc56ee39f` |

S1 uses V's 60-event full schedule, S4 its 948-event full schedule. Generate the
same 240-ms schedule, but consume only its first three 20-ms windows. Retain the
full-schedule and consumed-window identities separately. Keep dt=0.1 ms,
amplitude=68.75 mV, source refractory exemption, no silencing, no selected
traces, and the original graph/weight construction. Do not choose a quieter
window or an alternative topology after observing a trace.

Fixed order: S1 CPU correctness reference, S1 GPU unprofiled control, S1 GPU
profiled observation, then the same three roles for S4. Each role gets one
runtime and one fresh state. Calls 0 and 1 are retained warmups; call 2 covers
40-60 ms and is the sole observed advance. Capture only call 2 in the profiled
role. Run sequentially; release the state/runtime before the next role.

Budget: six workload workers, three calls each, **18 total advances**: six CPU
correctness calls and twelve GPU calls. Exactly two capture ranges, one per
case. These are fresh 60-ms diagnostic trajectories, not the historical two
240-ms A/B trajectories and not a new replay/timing-distribution certification.
No adaptive warmups, repetitions, rejected outlier replacement, or automatic
rerun. A failed attempt is recorded and stops the batch.

## Public boundary and correctness

Pack events before the observed T5 boundary. Use monotonic wall timing around
the unchanged `runtime.advance(..., duration_ms=20, stimulus=...)`, including
production output materialization and synchronization. Put a single NVTX public
call range around that boundary; profiler start/stop and trace flushing are
outside the wall timer. No per-step instrumentation, tracing monkeypatch,
additional hot-path barrier, or CUDA-event-only attribution.

Compare initial state and all three chunk boundaries against the CPU reference
outside timers/capture. Preserve exact shapes, dtypes, timestep, refractory
deadlines, pending counts, canonical spike order/multiplicity, all result
fields, finite floats, and `rtol=atol=2e-13`. Keep safe optional-field JSON
encoding and `np.load(..., allow_pickle=False)`. Record stable state/graph
pointers and cleanup. Any mismatch is a correctness stop, not profiling data
that justifies architecture research.

The unprofiled and profiled wall times supply a descriptive observer-effect
ratio only. One observation per case cannot establish a stable overhead
correction. Retain raw values and flag absolute deviation above 25% as material
distortion. Do not subtract an estimated overhead from the timeline or compare
these samples as a replacement for V's historical distributions.

## Process-tree gate before any import or execution

The existing guard's `mandatory_child` admits fixed guarded Python entrypoints
and named controls; `guarded_command` rejects a non-Python executable. An
ordinary guarded `ProcessJob([nsys, ...])` is therefore incompatible. Do not
disable the firewall, run the workload unguarded, or broaden admission to
arbitrary native programs to work around this restriction.

The execution preparation must provide a task-local, exact native-profiler
launch contract and containment supervisor, with the profiler launching the
absolute `.venv/Scripts/python.exe`, then the absolute existing
`scripts/a019c_firewall/guarded_child.py`, then the A019X worker. Freeze and check
all executable paths, argument positions, cwd, environment, and output paths.
Reject shell execution, alternate executables/scripts, arbitrary profiler
arguments, and missing guard activation. Do not change production source or
the general firewall admission rules.

Install the inherited guard before discovery/imports. Establish bootstrap and
negative controls, then certify that the root profiler and its target/descendants
are assigned to a Windows Job before workload execution and cannot escape it.
Exercise worker failure, timeout, environment removal, and cleanup using
non-GPU synthetic controls first. Retain the Job inventory through normal
shutdown and verify it is empty. Profiler injection compatibility and cleanup
are mandatory gates; executable help output is insufficient. If this cannot
be demonstrated within the frozen contract, report an infrastructure stop
without executing GPU workloads or repairing the guard during a run.

Proposed profiler options, to be pinned by the exact launch contract before use:

```text
profile --trace=cuda,nvtx --sample=none --cpuctxsw=none
--python-sampling=false --gpu-metrics-devices=none --gpuctxsw=false
--cuda-memory-usage=false --cuda-trace-all-apis=false
--capture-range=cudaProfilerApi --capture-range-end=stop --kill=false
--force-overwrite=false --output=<new task-local absolute path>
<absolute Python> <absolute guarded_child.py> <absolute A019X worker> <fixed role>
```

Construction/import per worker: 180 s. Each public advance: 30 s. Each profiled
worker including report finalization: 300 s. Entire workload batch: 900 s.
Contained private-byte and working-set sums: each 8 GiB, sampled at 0.1 s.
Watchdog failure, cap breach, or inventory ambiguity stops the batch. Export
timeout: 180 s per report; generated task output cap: 2 GiB. Output caps are
sampled watchdog bounds, not an OS-enforced guarantee against brief overshoot.
Do not kill unrelated profiler/device users or install/update tooling.

## Analysis and decision rules

Retain the public-call range, target PID/thread/context/stream identities,
CUDA API/kernel/memcpy records and their correlations. Require exactly 200
`schedule_ordered` launches for the observed 200-step call. Missing launches,
dropped records, absent range/stream correlation, or trace errors make the
diagnostic indeterminate. Export schema is discovered from the newly generated
SQLite only; record schema/tool versions and queries, not assumed column names.

Compute clipped interval unions within the public range: GPU kernel activity,
GPU transfer activity, API calls on the launching host thread, and GPU-idle
gaps. Report ordered-kernel duration separately and short-kernel duration/count
distribution (fixed short threshold: 10 microseconds). Device and host intervals
overlap; never add their percentages or treat summed API time as critical-path
time. Distinguish tail synchronization from launch starvation, and final
readback from per-step compaction-related waits.

Trace-correlated GPU-idle gaps without queued preceding work support a
host-submission limitation. They do not by themselves identify Python/CuPy as
the cause: scheduling, profiler intervention, and driver work remain alternatives
when CPU scheduling/stacks are unavailable. Likewise, long API intervals are
not proof of Python time. Report this limitation explicitly.

- **X-A: H1 supported within this observation.** Repeated host-limited gaps and
  short-operation trains explain at least half of the observed critical-path
  interval on S4, with S1 providing consistent corroboration, complete trace,
  passing correctness, and no material observer-effect flag. Report the actual
  attribution evidence and residual uncertainty. The next step can only be an
  evidence-only architecture feasibility decision; no assumed speedup.
- **X-B: H1 not supported as the major explanation.** A complete usable S4
  trace attributes at least 80% of the public interval to device activity,
  and correlated host-submission gaps are at most 10%. Recommend pausing this
  architecture-investment line; do not pivot into optimizing the competing
  kernel within X.
- **X-C: indeterminate.** Intermediate shares, mixed cases, unclassified idle
  time, missing attribution, material observer effects, or failed gates. Do not
  force a binary conclusion or silently expand collection. Name one bounded
  next decision based on the recorded limitation.

These are frozen diagnostic decision thresholds, not biological rules,
statistical significance tests, or certified performance predictions.

## Evidence, boundaries, and delivery

Future execution outputs: a new A019X harness/control test set, an A019X result
section or linked report, and `docs/plans/a019x-synthetic-gpu-profiling-evidence.json`.
Retain raw profiler reports, SQLite exports, guard/supervisor logs and SHA256
manifest in a fresh task-local temporary output directory; record its exact
path. Do not commit binary traces, overwrite V evidence, inspect registered
payloads, or write historical artifacts/archives. No commit/push is performed
by this preparation; publication must follow the execution task's authorized
closure scope.

Source SHA256 pins from this preparation:

| Source | SHA256 |
|---|---|
| `src/malecns_sim/dynamics/cuda.py` | `793b4859ff11355611c788f222d82334b6da023b82504348e115996a9b5b8ddc` |
| `src/malecns_sim/dynamics/lif.py` | `c8b2f10b37ecaecce14830b6b027e79e9474bf0f3a7c79b15b7115cb923b8d8e` |
| `src/malecns_sim/dynamics/stimulus.py` | `8a3d14f6d7f76cf4399fe94076b0f6f4d9adde63579bd3d303da30f6a3f5f94d` |
| `scripts/benchmark_application_a019v.py` | `f96513c2f315bdc7af3a132e799c199e02406bebe2b87da37bf18e5addec4294` |
| `scripts/a019c_firewall/validation_firewall.py` | `170e203635d0fcf3b2af9a860dfa049c3c8e24fd43829c023a7bb5c3dd5643af` |

Recheck pins, identity and dirty scope before implementation and before capture.
An unexpected source/fixture change is a stop requiring a revised protocol.
Preserve full-real, GPU-generalization, real-time and biological nonclaims.
No kernel fusion, stream/block changes, graph replay, tolerance relaxation,
precision change, source-data use, Arena/intervention, download, release, tag,
version bump, or automatic next task.

Preparation accounting: GPU/CPU advances=0; captures=0; CUDA/CuPy
preflights=0; full-real preparations=0; registered payload inspections=0;
production/harness/guard edits=0. These are performed-command-scope records,
not newly instrumented native telemetry or new firewall certification.

Preparation validation: `git diff --check` PASS; explicit new-file check with
`git diff --no-index --check -- /dev/null <this document>` PASS. Final inventory
contains only this new untracked plan; tracked and staged diffs are empty;
stash empty; local/origin identity remains the starting SHA. No
Python/test/compileall execution is needed or performed for this document.
Execution authority and integration certification were pending at preparation.

## Execution preparation record

The sole initial dirty file was this earlier plan. Starting HEAD and live remote
remain `95f53df6703ac4aa03a66ff763c5a0427ebde2b2`; all five source pins pass.
Inherited firewall bootstrap: 28 PASS. The first pytest invocation was rejected
because PowerShell split the JUnit option; no tests ran in that invocation.

Task-local `scripts/profile_application_a019x.py` uses an exact, validated
CreateProcessW contract, assigns the suspended native root to a no-breakaway
Windows Job before resuming it, and reuses the existing inventory/memory methods.
General firewall source/admission and production code remain unchanged.
Interactive Python override variables are removed from the child environment;
missing guard activation is allowed only for the harmless negative control.
The first contract-test run exposed the inherited interactive override; explicit
child-environment sanitization corrected it. Final contract controls: 26 PASS.

Pre-workload native preparation used fresh directories for each stopped control
batch. First: CLI rejected `capture-range=none` combined with `capture-range-end`
before target launch. Second: normal worker passed; the expected failing worker
exited 1 and cleaned up, but its stderr did not appear in the native log, so the
observation-based control failed. Third: explicit expected-error marker plus
nonzero exit establishes failure; all four native controls pass: normal exit 0,
expected failure exit 1, timeout with retained live worker/descendant identities,
and missing activation exit 78 before workload. Job inventory is empty and all
owned handles released after each control, including repeated close.

These were harness/bootstrap corrections before any CPU/GPU fixture advance.
Each stopped preparation batch is retained; no failed scientific/profiled
workload has been retried. The workload batch is still limited to six workers,
18 advances and two CUDA capture ranges, with no automatic retry.

Retained preparation directories:

- `C:/Temp/malecns-a019x-5714e6a570794d8582e1c0ee4f9f8d03`
- `C:/Temp/malecns-a019x-fb7c641316404e749a21a9d0e574d25e`
- `C:/Temp/malecns-a019x-8939a1d9de604e38848b2c97fac06417`

The last directory is the admitted workload output root. Before its batch,
freeze a manifest of harness/production/profiler hashes and exact launch argv.
Control captures use NVTX only with no CUDA capture range; their CLI omits
CUDA-only and capture-range-end switches. The two workload captures retain
the protocol's CUDA/NVTX and cudaProfilerApi options unchanged.
