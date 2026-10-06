# A019C-R14 normal-exit adjudication

Authorization: `授權 A019C-R14`; synthetic-only. Starting local/origin/live
HEAD: `60c900b0c8e5a02ea95efc7340fd190193edf7e9`. Initial expanded dirty
count 29; staging/stash empty; unrelated WIP No. Version 0.3.0; tracked
active workflows zero. Prior records, including R13 STOP, remain unchanged.

Plan: inventory; static historical audit; one unmodified reproduction;
adjudicate before correction; corrected target; focused controls; complete
A014; bootstrap; harness/CLI; deferred validation. Stop at each failure gate.
Commit/push only on complete R14-A.

## Historical contract and comparison

Tracked introduction e195c7c and A014 plan lines 97-105 establish absolute
aggregate current private bytes OR working set, not delta or lifetime peak.
ProcessJob launches suspended, assigns Job before resume, includes descendants,
then supervise_synthetic samples every 20 ms immediately after construction.
Startup is included. Default normal-control cap is 268435456 bytes (256 MiB),
timeout 10 seconds. Original body prints normal and exits; no material allocation,
no baseline exclusion/readiness/grace. Expected NORMAL_EXIT, root exit 0, empty
Job. Source establishes ordinary low-memory startup purpose; no historical
numeric rationale for exactly 256 MiB is recorded. Do not invent one.

| Control | Topology | Cap | Allocation | Offender/result/root exit |
|---|---|---:|---:|---|
| Normal | venv redirector/base worker | 256 MiB | print only | none/NORMAL_EXIT/0 |
| Direct | exact base -S fixed guarded control | 128 MiB | 160 MiB | root/MEMORY_LIMIT/1 |
| Launcher | venv redirector/base worker | 128 MiB | 160 MiB | worker/MEMORY_LIMIT/1 |
| Child | parent/spawned venv worker | 128 MiB | 160 MiB | descendant/MEMORY_LIMIT/1 |
| Replacement | parent exits after spawn | 128 MiB | 160 MiB | replacement/MEMORY_LIMIT/0 |
| Aggregate | parent and child | 128 MiB | 60 MiB each | tree/MEMORY_LIMIT |
| Accounting error | live sleeping worker | 256 MiB | none | WATCHDOG_FAILURE |

No explicit genuine process-error classification test exists here. The runner
does not classify nonzero child exit as a separate process-error status.

## Single unmodified reproduction

Guarded pytest observational plugin C:/TEMP/a019c-r14-capture.py; output
C:/TEMP/a019c-r14-prefix-output.txt; audit C:/TEMP/a019c-r14-prefix.jsonl.
Only test_normal_exit: 1 failed in 0.24 s. Supervisor 7868 ACTIVE; root 17128
venv redirector; base worker 7360 (role from source topology; image path was
not independently queried). First aggregate private 303104, then 8118272,
10227712, 12488704, 15163392, 17367040, finally 661643264 bytes.
Offender 7360 private 660779008; root private 864256; aggregate working set
32743424. Cap 268435456. Final sample is the first observed crossing;
continuous peak/precise crossing time unavailable. Worker peak commit at that
sample equals 660779008. Guard child ACTIVE absent, output empty, no ready,
workload-start or normal marker. Startup dependency import precedes workload.
No normal allocation executed. Before guard-install entry memory not directly
observable; first launch sample above is not claimed as a guard boundary.
Root poll None before cleanup, exit 1 after termination; Job empty; orphans [];
one attempt/no retry. Accepted registered reads zero; blocked probes zero.

The event is real under absolute accounting, caused by startup interference
with the historical low-memory print control, not a false production sample.

## Adjudication before correction

**F1 — STALE NORMAL-EXIT FIXTURE / STARTUP INTEGRATION.** No production defect
or obsolete expected result is demonstrated. Mandatory firewall imports Arrow
and its NumPy dependency; installed NumPy config identifies scipy-openblas
0.3.34.106.0, MAX_THREADS=24. No OPENBLAS/OMP/MKL thread environment bound
is present. The large startup jump is consistent with native dependency thread
initialization; attribution to OpenBLAS specifically is a hypothesis to test,
not yet a proven allocation trace.

Narrow proposed correction: bound only this print fixture's child OpenBLAS
thread count to one, and add guard/readiness/workload/completion observations.
The print workload needs no BLAS concurrency. Preserve the 256-MiB cap, immediate
absolute accounting, all samples, actual workload, and mandatory guard. No
production or admission change. If this fails, record the failure without
numeric inflation or independent fixes.

## Corrected evidence and mandatory deferred STOP

The first corrected observational run passed (root 17088, base worker 14796),
with sampled aggregate private peak 29581312 and working-set peak 43823104.
The final completion-marker fixture then passed alone in 0.41 s: root 19916,
base worker 11200; ACTIVE -> normal_ready -> normal_workload_start ->
normal_completed; completion file contains normal; root exit 0; sampled private
peak 29413376, working-set peak 43614208; no offenders; Job empty; no retry.
Readiness/workload instantaneous memory was not measured: markers occur between
samples. No exact phase byte values or continuous peak are invented.
OPENBLAS_NUM_THREADS=1 is scoped by monkeypatch to this fixture's spawned child;
all negative controls retain their own environment/caps and production sampling.
The single-variable comparison supports native startup pool interference; it is
not a full native allocation attribution. No numeric cap changed.

Commands use mandatory guarded_child.py -m pytest, activation=1, absolute
scripts/a019c_firewall PYTHONPATH, separate C:/TEMP/a019c-r14-*.jsonl audit logs,
-q -x and unique bounded basetemp directories. The final target's completion
file assertion prevents a PASS from skipping the workload.

| Gate | R14 result |
|---|---|
| Final corrected normal target | 1 PASS, 0.41 s |
| Focused normal/direct/replacement/child/aggregate/accounting-error | 6 PASS, 2.36 s |
| Complete A014 plus R12 admission controls | 19 PASS, 5.48 s (12 A014 + 7 admission) |
| Bootstrap R2/R3/R4/R5 | 39 PASS, 5.27 s; FIREWALL_BOOTSTRAP_CERTIFIED renewed |
| A019C harness | 35 PASS, 7.36 s |
| Fresh contained CLI | exit 0, A19C-A; C:/TEMP/a019c-r14-forward-evidence.json |
| A013 | 16 PASS, 1 FAIL, 1.43 s |
| Stateful/A011/reference LIF | NOT RUN after mandatory STOP |
| Remaining application regressions | NOT RUN after mandatory STOP |
| compileall | NOT RUN after mandatory STOP |
| git diff --check | NOT RUN as deferred gate after mandatory STOP |

A013 failing node:
`tests/test_application_a013.py::test_native_watchdog_can_terminate_actual_redirected_python`.
Its argv is venv Python -u -c print-PID/sleep. Existing guarded_command inserts
mandatory script ahead of -u; mandatory_child rejects that option position before
Popen can execute a child: SourceAccessDenied, child lacks mandatory firewall
entrypoint. No workload or termination occurred for this node. Do not broaden
admission or fix the independent integration issue in R14. This failure is not
an A014 memory/accounting regression and does not invalidate bootstrap PASS.

**A19C-R14-DEFERRED-VALIDATION-BLOCKER**. No R14-A; no forward certification;
no success commit/push. A019D not eligible or recommended. Prior STOP records
remain historical STOP records; this record supersedes current recovery status
only, without rewriting any prior outcome.

## Final manifest and source accounting

The exact per-node R11/R10 manifests remain incorporated, with this R14 overlay.
No deferred item is reclassified to obtain closure. R11 historical PASS for
A018U/T/S, A018, A017/16/15 remains historical, not fresh R14 execution.
Required S0/S1 closure is incomplete; all remaining admitted nodes NOT RUN.
S2 remains explicitly NOT RUN: three A003 payload tests (selection identity,
validate/run identity, result export); A018UJ data-diff (J2), A018UJ provenance
reconstruction; default integrity (I2); unfiltered pytest; build (B2).
N: Arena-specific A011 cases, real execution/GPU/download/archive/release work.
Full pytest NOT RUN — synthetic-only authorization; known S2 real-data tests excluded.

Accepted connectivity/annotation/neurotransmitter/metadata/provenance/mapping/
other registered reads: each 0, aggregate 0. Audit uses fail-closed pre-read
blocking rather than independent native accepted-byte telemetry. Bootstrap
contains 34 blocked records (33 registered-path probes and one corrupt policy
entrypoint probe); focused controls 4 blocked registered probes; A014 8 blocked
registered probes: 45 deliberate registered-path blocks total, plus one policy
probe. No blocked record is an accepted read. Permitted executed synthetic
controls: normal, direct exact purpose, launcher, child, replacement, aggregate,
watchdog accounting failure, bootstrap and contained harness controls. The A013
-u executable control was rejected before execution.

## Complete requested final report

| # | Field | Result |
|---:|---|---|
| 1 | Verdict | A19C-R14-DEFERRED-VALIDATION-BLOCKER |
| 2 | Starting HEAD | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 3 | Initial dirty count/paths | 29; exact inventory below |
| 4 | Unrelated WIP | No |
| 5 | Prior outcomes preserved | Yes; R13 STOP unchanged |
| 6 | Exact normal test | tests/test_application_a014.py::test_normal_exit |
| 7 | Historical purpose | Low-memory print process exits normally under absolute accounting |
| 8 | Historical cap | 268435456 bytes |
| 9 | Why that cap | Ordinary startup allowance implied by fixture; exact numeric rationale undocumented |
| 10 | Memory metric | Current aggregate private bytes OR working set; offenders per PID |
| 11 | Accounting boundary | Immediately after real ProcessJob construction/resume |
| 12 | Startup included | Yes, before and after correction |
| 13 | Root/topology | Failed 17128/base 7360; final target 19916/base 11200 |
| 14 | Guard state | Supervisor ACTIVE; failed child never ACTIVE; corrected child ACTIVE |
| 15 | Readiness | Absent pre-fix; corrected normal_ready after ACTIVE |
| 16 | Workload start | Absent pre-fix; corrected normal_workload_start |
| 17 | Normal exit point | Absent pre-fix; corrected completion marker/file, root exit 0 |
| 18 | Before guard/readiness memory | Boundary unobservable; first pre-fix tree sample 303104 private bytes |
| 19 | Memory at readiness | Not measured at exact marker |
| 20 | Memory at workload start | Not measured at exact marker |
| 21 | Sampled peak private | Failed tree 661643264; final corrected tree 29413376 |
| 22 | Configured cap | 268435456 unchanged |
| 23 | Offender | Failed 7360; corrected none |
| 24 | Limit before workload | Yes in failed reproduction |
| 25 | Material normal allocation | No; print-only |
| 26 | Cause | Guard dependency startup crossed absolute cap before print; native thread bound removes interference |
| 27 | Adjudication | F1 |
| 28 | Evidence | Historical source + single failure timeline + single-variable corrected run + positive/negative controls |
| 29 | Production code changed | No in R14 |
| 30 | Fixture/helper changed | Only test_normal_exit in tests/test_application_a014.py |
| 31 | Numeric cap changed | No |
| 32 | Old/new cap | 268435456 / 268435456 |
| 33 | Numeric derivation | N/A; one BLAS thread because print has no parallel BLAS workload |
| 34 | Corrected workload started | Yes, marker + print + completion file |
| 35 | Corrected result | NORMAL_EXIT |
| 36 | False offender absent | Yes |
| 37 | Cleanup | PASS, empty Job |
| 38 | No orphan | PASS |
| 39 | No retry | PASS, one attempt |
| 40 | Direct control | MEMORY_LIMIT PASS, actual 160-MiB allocation |
| 41 | Replacement | MEMORY_LIMIT PASS, actual allocation/handoff/root 0 |
| 42 | Descendant/tree | Historical child and aggregate assertions PASS; child allocation activation not independently newly proved |
| 43 | Genuine error distinction | No separate process-error test; injected WATCHDOG_FAILURE PASS; harness genuine preparation-error controls PASS |
| 44 | Complete A014 | 12 A014 + 7 admission = 19 PASS |
| 45 | Remaining A014 failures | None |
| 46 | Bootstrap | 39 PASS |
| 47 | Bootstrap certification renewed | Yes |
| 48 | A019C harness | 35 PASS |
| 49 | Fresh CLI | exit 0, A19C-A |
| 50 | A013 | 16 PASS, 1 FAIL (native -u control denied) |
| 51 | Stateful/A011 | NOT RUN after STOP |
| 52 | Application regressions | Remaining NOT RUN after STOP |
| 53 | compileall | NOT RUN after STOP |
| 54 | diff check | NOT RUN after STOP |
| 55 | J2 | Preserved, NOT RUN |
| 56 | I2 | Preserved, NOT RUN |
| 57 | B2 | Preserved, NOT RUN |
| 58 | Full pytest | NOT RUN, synthetic-only authorization; S2 excluded |
| 59 | Final S0 | Incomplete; named PASS gates above; remaining NOT RUN |
| 60 | Final S1 | A014 PASS; A013 native control FAIL; remaining NOT RUN |
| 61 | Final S2 | All NOT RUN, explicit exclusions above |
| 62 | Certification sufficiency | NOT SATISFIED |
| 63 | Accepted connectivity | 0 |
| 64 | Accepted annotation | 0 |
| 65 | Accepted neurotransmitter | 0 |
| 66 | Accepted metadata | 0 |
| 67 | Accepted provenance | 0 |
| 68 | Accepted mapping | 0 |
| 69 | Accepted other registered | 0 |
| 70 | Aggregate accepted | 0 |
| 71 | Bounded route | PASS; merge block 16384; fallback hard-stop PASS |
| 72 | Production default changed | No |
| 73 | G1-G6 | PASS |
| 74 | L3/L4 wrong-layer rejection | PASS |
| 75 | PreparedNetwork | 1 per forward run |
| 76 | PreparedRuntime | 1 per forward run |
| 77 | SimulationState | 2 per forward run |
| 78 | A/B fresh | Yes |
| 79 | Runtime reset/recreated | No |
| 80 | A/B calls | Each 2 warmup + 10 measured; 20 ms/call; final 240 ms |
| 81 | Total/max consecutive | 24 / 12 |
| 82 | Continuous 480-ms trajectory | No |
| 83 | Lifetime | A released before B; no coexistence; B not derived from A |
| 84 | Schedule generation | Once per forward run |
| 85 | Seed/horizon/events | 1555062870 / 240 ms / 948; LEFT sugar 42 at 100 Hz, RIGHT 0, impulse 68.75 mV |
| 86 | Fingerprint | 6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a |
| 87 | Exact replay | PASS: windows, membrane, synaptic, refractory, pending/delayed, output, final state/time |
| 88 | Resources | PASS; preparation 600 s, advance 30 s, worker 1500 s; private/WS 8589934592 each |
| 89 | Forced timeout/memory | PASS in harness |
| 90 | Containment/live-tree/no-orphan/no-retry | PASS in bootstrap/harness; failing A013 node not executed |
| 91 | Full-real preparations | 0 |
| 92 | Real advances | 0 |
| 93 | A019D attempt consumed | No; real benchmarks 0 |
| 94 | GPU/Arena/science/download/archive | No / 0 / 0 / 0 / 0 |
| 95 | Historical A013 behavior changed | No |
| 96 | Task016 changed | No |
| 97 | Task017 | Unchanged / NOT_ROBUST |
| 98 | Version | 0.3.0 |
| 99 | Active tracked workflows | 0 |
| 100 | Final commit | No new commit; HEAD 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 101 | Push | NOT RUN, success prerequisite not met |
| 102 | Final local/origin/live | All 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 103 | Worktree/staging/stash | DIRTY, 30 scoped paths / empty / empty |
| 104 | Tag/release/version mutation | No |
| 105 | Superseding current status | R14 deferred-validation STOP; prior STOP chronology preserved |
| 106 | Exact next work | Separately authorized A013 native-watchdog -u guarded-entrypoint adjudication and deferred validation completion |
| 107 | A019D recommended | No; A019D gate closed |

## Initial exact scoped inventory

```text
 M tests/test_application_a014.py
 M tests/test_application_a018ur.py
?? docs/plans/2026-10-05-application-a019c-executable-harness-contract-alignment.md
?? docs/plans/2026-10-05-application-a019c-harness-contract.json
?? docs/plans/2026-10-05-application-a019c-r2-guard-first-firewall-recovery.md
?? docs/plans/2026-10-05-application-a019c-synthetic-evidence.json
?? docs/plans/2026-10-06-application-a019c-r10-validation-manifest-closure.md
?? docs/plans/2026-10-06-application-a019c-r11-supervisor-startup-timeout.md
?? docs/plans/2026-10-06-application-a019c-r12-a014-direct-executable.md
?? docs/plans/2026-10-06-application-a019c-r13-a014-replacement-control.md
?? docs/plans/2026-10-06-application-a019c-r3-native-process-firewall-coverage.md
?? docs/plans/2026-10-06-application-a019c-r4-inherited-child-fail-closed.md
?? docs/plans/2026-10-06-application-a019c-r5-windows-mandatory-child-audit.md
?? docs/plans/2026-10-06-application-a019c-r6-contained-worker-cleanup.md
?? docs/plans/2026-10-06-application-a019c-r7-live-process-tree-cleanup.md
?? docs/plans/2026-10-06-application-a019c-r8-obsolete-child-guard-regression.md
?? docs/plans/2026-10-06-application-a019c-r9-validation-firewall-integration.md
?? scripts/a019c_firewall/a014_direct_control.py
?? scripts/a019c_firewall/guarded_child.py
?? scripts/a019c_firewall/sitecustomize.py
?? scripts/a019c_firewall/validation_firewall.py
?? scripts/benchmark_application_a019.py
?? tests/fixtures/application-a019c-preparation-identity.json
?? tests/test_application_a019c.py
?? tests/test_application_a019c_r12_firewall.py
?? tests/test_application_a019c_r2_firewall.py
?? tests/test_application_a019c_r3_firewall.py
?? tests/test_application_a019c_r4_firewall.py
?? tests/test_application_a019c_r5_firewall.py
```
