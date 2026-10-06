# A019C-R6 contained-worker cleanup correction

Authorization: 授權 A019C-R6. Starting HEAD/local origin/live master:
60c900b0c8e5a02ea95efc7340fd190193edf7e9.
Initial inventory: 17 actual untracked files, 15 status entries; staging, tracked diff,
and stash empty. All accumulated A019C/R2/R3/R4/R5 work; no unrelated WIP.

Plan: confirm ProcessJob API; replace invalid return assertion with worker exit,
retained process-handle exit checks, released job handle and repeated cleanup.
Exercise a live guarded synthetic descendant with the repository Job Object inventory.
Run complete bootstrap with fail-fast; stop immediately on any failure. Only a fully
certified bootstrap permits downstream synthetic validation. Preserve all prior STOPs.

ProcessJob.close() intentionally returns None. It terminates the job, waits for the
worker, verifies empty job inventory, closes the handle, then sets handle=None.
Repeated calls are no-ops. KILL_ON_JOB_CLOSE is set; breakaway is disabled.
Production ProcessJob is unchanged. The invalid R5 assertion was `assert job.close() == []`.

Historical A19C-F, A19C-R-D, A19C-R2-C, A19C-R3-D,
A19C-R4-CHILD-FAIL-CLOSED-INCOMPLETE and
A19C-R5-HARNESS-WORKER-COVERAGE-INCOMPLETE remain unchanged.

Initial paths:
- docs/plans/2026-10-05-application-a019c-executable-harness-contract-alignment.md
- docs/plans/2026-10-05-application-a019c-harness-contract.json
- docs/plans/2026-10-05-application-a019c-r2-guard-first-firewall-recovery.md
- docs/plans/2026-10-05-application-a019c-synthetic-evidence.json
- docs/plans/2026-10-06-application-a019c-r3-native-process-firewall-coverage.md
- docs/plans/2026-10-06-application-a019c-r4-inherited-child-fail-closed.md
- docs/plans/2026-10-06-application-a019c-r5-windows-mandatory-child-audit.md
- scripts/a019c_firewall/guarded_child.py
- scripts/a019c_firewall/sitecustomize.py
- scripts/a019c_firewall/validation_firewall.py
- scripts/benchmark_application_a019.py
- tests/fixtures/application-a019c-preparation-identity.json
- tests/test_application_a019c.py
- tests/test_application_a019c_r2_firewall.py
- tests/test_application_a019c_r3_firewall.py
- tests/test_application_a019c_r4_firewall.py
- tests/test_application_a019c_r5_firewall.py


## R6 execution evidence and STOP

One guarded fail-fast bootstrap invocation ran, using the existing virtualenv
(no dependency installation/download):

```text
.venv/Scripts/python.exe scripts/a019c_firewall/guarded_child.py -m pytest tests/test_application_a019c_r5_firewall.py tests/test_application_a019c_r4_firewall.py tests/test_application_a019c_r3_firewall.py tests/test_application_a019c_r2_firewall.py -q -x
```

Activation=1, PYTHONPATH=scripts/a019c_firewall. Audit log:
C:/TEMP/a019c-r6-bootstrap.jsonl. Result: **14 passed, 1 failed in 1.90 s**.
Classification: **A19C-R6-CONTAINED-WORKER-CLEANUP-INCOMPLETE**.
FIREWALL_BOOTSTRAP_CERTIFIED NOT issued. No downstream validation resumed.

The invalid close-return assertion was removed. Actual contained worker tests
passed for activation=1, missing activation and corrupt activation. Assertions
verify close without exception, handle=None, expected worker exit, signaled
retained process identities and repeated cleanup. ProcessJob itself unchanged.

Parent PID: 16244. Actual worker lifecycle evidence:

| Activation | Worker PID | Initial job inventory | Exit | Handle released | Repeat cleanup |
|---|---|---|---|---|---|
| valid | 16940 | [16940] | 0 | PASS | PASS |
| missing | 15064 | [15064] | 78 | PASS | PASS |
| corrupt | 19624 | [19624] | 78 | PASS | PASS |

These bootstrap workers created no descendants. Valid worker emitted
A019_WORKER_GUARDED_BEFORE_WORKLOAD. Negative workers emitted
FIREWALL_REQUIRED_BUT_NOT_ACTIVE, with no workload marker. Parent permitted
mandatory launches; direct worker bypass test passed before process creation.

The added live-tree cleanup test observed the readiness marker, then failed an
invalid exact-two-member assumption: actual Job Object inventory was
[12480, 16428, 9020, 19772]. The roles of all four members were not established;
no attribution is fabricated. The test failed before retaining their handles.
Its finally block called close successfully, which internally verified empty
job inventory before releasing the job handle. A subsequent read-only
Get-Process scan for all four PIDs returned no processes. This supports no
remaining observed orphan, but does not certify the failed lifecycle test.
No correction or retry followed the failure. A future bounded correction must
use actual job membership rather than a fixed process count, and retain every
observed identity before assertions that can fail.

R5 Windows parsing was unchanged. Its 11 non-contained parser/launch controls
passed; the prior complete 18-test R5/R4 comparison was not completed because
fail-fast stopped before R4. Public/native Feather and category controls were
not reached. Audit log contains zero blocked probes in R6, and only activation
and contained-cleanup records. Historical R5 blocked probes remain 16; these
are not reclassified as current R6 results. Seven accepted read counters remain
zero within the executed guarded paths; no universal OS/native monitor claim.

No harness reconstruction, production default change, science change, real
preparation/advance/benchmark, GPU, Arena, experiment, download or archive write.
No commit/push, tag, release or version mutation. Existing WIP preserved.
Package version 0.3.0; tracked active workflows 0. Final local HEAD,
origin/master and live GitHub master remain the starting SHA. Stash/staging
empty; worktree dirty, now 18 actual untracked files.

## Complete requested final report

NOT RUN below means R6 did not execute/certify it because bootstrap failed.
Contract expectations in the prompt are not substituted for executed evidence.

| # | Item | R6 result |
|---|---|---|
| 1 | Verdict | STOP |
| 2 | Classification | A19C-R6-CONTAINED-WORKER-CLEANUP-INCOMPLETE |
| 3 | Starting HEAD | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 4 | Initial dirty count | 17 actual files; 15 short-status entries |
| 5 | Initial paths | Listed above |
| 6 | Unrelated WIP | No |
| 7 | Prior STOPs preserved | Yes, all six |
| 8 | close return contract | None |
| 9 | R5 bad assertion identified | Yes |
| 10 | Production close changed | No |
| 11 | Replacement assertions | Worker exit, retained identities signaled, handle released, repeated cleanup; live-tree test failed before retaining identities |
| 12 | Contained worker started | Yes |
| 13 | Worker PID | 16940 valid; 15064 missing; 19624 corrupt |
| 14 | Contained children | Actual bootstrap workers: none; live synthetic tree members 12480,16428,9020,19772; individual roles unresolved |
| 15 | close without exception | Yes, all four jobs |
| 16 | Worker exited | Yes |
| 17 | Children exited | Job empty internally; four observed live-tree PIDs absent afterward |
| 18 | Orphan scan | PASS for observed PIDs; overall lifecycle certification incomplete |
| 19 | Repeated cleanup | PASS for three actual-worker cases |
| 20 | Complete R5 Windows suite | NOT RUN to completion; 11 parser/launch controls PASS; earlier R5 18 PASS preserved |
| 21 | Valid guarded child | PASS, actual contained worker |
| 22 | Missing activation reaches child | PASS |
| 23 | Child fails closed | PASS, exit 78 |
| 24 | Negative workload executed | No |
| 25 | Bypass rejected | PASS |
| 26 | Parent guard | PASS within executed cases |
| 27 | Python child guard | PASS within executed actual workers |
| 28 | PyArrow child guard | NOT RUN |
| 29 | Native Feather child guard | NOT RUN |
| 30 | Actual A019 worker guard | PASS startup; source probe not reached |
| 31 | ProcessJob contained worker | Three actual-worker cases PASS; complete cleanup coverage FAIL |
| 32 | Distinct watchdog path | No separate script; same ProcessJob path inspected, full watchdog certification NOT RUN |
| 33 | PyArrow version | Historical 25.0.1; explicit R6 version assertion not reached |
| 34 | Native invocation | Unchanged FeatherReader(source, use_memory_map=False, use_threads=True).read() |
| 35 | Synthetic native control | NOT RUN |
| 36 | Registered native block | NOT RUN |
| 37 | Connectivity coverage | NOT RUN |
| 38 | Annotation coverage | NOT RUN |
| 39 | Neurotransmitter coverage | NOT RUN |
| 40 | Metadata coverage | NOT RUN |
| 41 | Provenance coverage | NOT RUN |
| 42 | Mapping coverage | NOT RUN |
| 43 | Other category coverage | NOT RUN |
| 44 | Deliberate blocked probes | R6: 0; historical R5: 16 preserved |
| 45 | Accepted connectivity reads | 0 |
| 46 | Accepted annotation reads | 0 |
| 47 | Accepted neurotransmitter reads | 0 |
| 48 | Accepted metadata reads | 0 |
| 49 | Accepted provenance reads | 0 |
| 50 | Accepted mapping reads | 0 |
| 51 | Accepted other reads | 0 |
| 52 | Aggregate accepted reads | 0 within executed guarded paths |
| 53 | Bootstrap certified | No |
| 54 | Broader certification resumed | No |
| 55 | Accumulated WIP reconciled | Inventoried and preserved; downstream reconciliation NOT RUN |
| 56 | Forward harness | scripts/benchmark_application_a019.py |
| 57 | Explicit bounded route | NOT certified in R6 |
| 58 | Production default changed | No |
| 59 | Merge block size | Expected 16,384; NOT certified in R6 |
| 60 | Fallback stop | NOT RUN |
| 61 | G1 | NOT RUN |
| 62 | G2 | NOT RUN |
| 63 | G3 | NOT RUN |
| 64 | G4 | NOT RUN |
| 65 | G5 | NOT RUN |
| 66 | G6 | NOT RUN |
| 67 | L3/L4 rejection | NOT RUN |
| 68 | PreparedNetwork count | R6 constructed 0; harness contract NOT RUN |
| 69 | PreparedRuntime count | R6 constructed 0; harness contract NOT RUN |
| 70 | SimulationStates count | R6 constructed 0; harness contract NOT RUN |
| 71 | A fresh | NOT RUN |
| 72 | B fresh | NOT RUN |
| 73 | Runtime reset | No runtime executed |
| 74 | Runtime recreated | No runtime executed |
| 75 | B derives from A | NOT RUN |
| 76 | A structure | NOT RUN |
| 77 | B structure | NOT RUN |
| 78 | A horizon | NOT RUN |
| 79 | B horizon | NOT RUN |
| 80 | Total calls | 0 executed in R6 |
| 81 | Max consecutive/state | NOT RUN |
| 82 | Continuous 480 ms | No trajectory executed |
| 83 | A released before B | NOT RUN |
| 84 | A/B coexist | No states executed |
| 85 | Schedule generation count | 0 in R6 |
| 86 | Schedule seed | NOT RUN |
| 87 | Schedule horizon | NOT RUN |
| 88 | Schedule events | NOT RUN |
| 89 | Schedule fingerprint | NOT RUN |
| 90 | A/B windows identical | NOT RUN |
| 91 | State replay | NOT RUN |
| 92 | Pending replay | NOT RUN |
| 93 | Output replay | NOT RUN |
| 94 | Timing boundaries | NOT RUN |
| 95 | Preparation timeout | NOT RUN |
| 96 | Advance timeout | NOT RUN |
| 97 | Worker timeout | NOT RUN |
| 98 | Private cap | NOT RUN |
| 99 | Working-set cap | NOT RUN |
| 100 | Forced timeout | NOT RUN |
| 101 | Forced memory stop | NOT RUN |
| 102 | Containment | Actual startup PASS; live-tree test FAIL due count assumption |
| 103 | Cleanup/no orphan | Actual worker cases PASS; observed live tree gone; complete test FAIL |
| 104 | No retry | No bootstrap retry; harness forced no-retry NOT RUN |
| 105 | Full pytest | NOT RUN — synthetic-only authorization; known S2 tests excluded |
| 106 | S2 exclusions | Three specified A003 tests; A018UJ provenance reconstruction; integrity source reads outside authorization |
| 107 | R6 tests | 14 PASS, 1 FAIL; fail-fast |
| 108 | Prior firewall regressions | R4/R3/R2 queued but NOT RUN after failure |
| 109 | A019C tests | NOT RUN |
| 110 | Synthetic regressions | NOT RUN |
| 111 | compileall | NOT RUN |
| 112 | Integrity | NOT RUN |
| 113 | diff check | NOT RUN |
| 114 | Build | NOT RUN |
| 115 | Full-real preparations | 0 |
| 116 | Real advances | 0 |
| 117 | A019D attempt consumed | No |
| 118 | GPU used | No |
| 119 | Arena runs | 0 |
| 120 | Scientific experiments | 0 |
| 121 | Downloads | 0 |
| 122 | A013 behavior changed | No |
| 123 | Scientific semantics changed | No |
| 124 | Task016 changed | No |
| 125 | Task017 changed | No |
| 126 | Task017 classification | NOT_ROBUST preserved |
| 127 | Archive writes | 0 |
| 128 | Package version | 0.3.0 |
| 129 | Active tracked workflows | 0 |
| 130 | Final commit | No new commit; 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 131 | Push | Not performed |
| 132 | Local HEAD | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 133 | origin/master | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 134 | Live master | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 135 | Worktree/stash | Dirty, 18 untracked files; staging/stash empty |
| 136 | Tag/release/version mutation | No |
| 137 | Superseding readiness | None; A019C remains uncertified |
| 138 | Exact next task | Separately authorized bounded live-tree cleanup test correction using observed Job Object membership, then complete gated bootstrap |
| 139 | A019D recommended | No; do not execute |

Exact S2 exclusions preserved:
- tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields
- tests/test_application_a003.py::test_validate_and_run_requests_share_exact_spec_identity
- tests/test_application_a003.py::test_result_events_and_backend_export_routes
- tests/test_application_a018uj.py::test_independent_frozen_artifact_reconstruction_and_provenance

Historical STOPs were not edited or rewritten. No success/readiness classification
is issued. No bounded-stop commit was made because bootstrap failed.
