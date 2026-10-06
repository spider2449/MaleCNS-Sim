# A019C-R7 live process-tree cleanup

Authorization: 授權 A019C-R7. Root dynamically derived by git rev-parse.
Starting local HEAD = origin/master = live master = 60c900b0c8e5a02ea95efc7340fd190193edf7e9.
Initial inventory: 18 untracked files, staging/tracked diff/stash empty; no unrelated WIP.
Version 0.3.0; active tracked workflows 0.

Plan: correct only the fixed live-tree cardinality assertion; retain all observed
process identities before assertions, record workload roles and parent IDs with
synthetic readiness markers, exercise one and two descendants, then run one
fail-fast bootstrap. Stop immediately on any bootstrap failure. Only complete
bootstrap certification permits synthetic harness and explicitly safe validation.
Production ProcessJob.close(), parsing, source taxonomy and semantics unchanged.

R6: 14 passed, 1 failed; expected 2, observed 4: [12480,16428,9020,19772].
All four were absent afterward, but the failed test did not certify cleanup.
Historical A19C-F, A19C-R-D, A19C-R2-C, A19C-R3-D,
A19C-R4-CHILD-FAIL-CLOSED-INCOMPLETE,
A19C-R5-HARNESS-WORKER-COVERAGE-INCOMPLETE and
A19C-R6-CONTAINED-WORKER-CLEANUP-INCOMPLETE remain unchanged.

Initial paths:
- docs/plans/2026-10-05-application-a019c-executable-harness-contract-alignment.md
- docs/plans/2026-10-05-application-a019c-harness-contract.json
- docs/plans/2026-10-05-application-a019c-r2-guard-first-firewall-recovery.md
- docs/plans/2026-10-05-application-a019c-synthetic-evidence.json
- docs/plans/2026-10-06-application-a019c-r3-native-process-firewall-coverage.md
- docs/plans/2026-10-06-application-a019c-r4-inherited-child-fail-closed.md
- docs/plans/2026-10-06-application-a019c-r5-windows-mandatory-child-audit.md
- docs/plans/2026-10-06-application-a019c-r6-contained-worker-cleanup.md
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

## R7 execution evidence and mandatory STOP

One bootstrap run (activation=1; PYTHONPATH=scripts/a019c_firewall), no retry:

```text
.venv/Scripts/python.exe scripts/a019c_firewall/guarded_child.py -m pytest tests/test_application_a019c_r5_firewall.py tests/test_application_a019c_r4_firewall.py tests/test_application_a019c_r3_firewall.py tests/test_application_a019c_r2_firewall.py -q -x
37 passed, 1 failed in 5.34 s
```

Audit: C:/TEMP/a019c-r7-bootstrap.jsonl. Parent PID 17708.
Failure: R2 test_child_cannot_drop_guard expected parent SourceAccessDenied.
Actual mandatory child started, printed FIREWALL_REQUIRED_BUT_NOT_ACTIVE and
rejected before its harmless pass workload. This obsolete parent-rejection
expectation contradicts the retained R4/R5 mandatory-child pass-through contract.
No assertion correction/retry follows this failure. Classification:
**A19C-R7-FIREWALL-METHOD-INVALID**. Bootstrap certification NOT issued.

Replacement invariant: capture pre_cleanup_pids=set(job.pids()); retain every
identity before assertions; worker in set; len(set)>=1; all expected workload
and launched-child roles in set; child parent PIDs in set; final pre-close
inventory equals captured set. Close must succeed, all retained identities must
be signaled, all observed PIDs must be absent or represent terminated processes,
worker exited, handle=None, repeated close safe. No surviving observed orphan.
No process-count equality is used. Repeated close checks do not launch workers.

| Case | Job launcher | Complete pre-cleanup set | Workload role / parent | Launched children | Child workload / parent | Post-cleanup |
|---|---|---|---|---|---|---|
| A, one descendant | 18708 | {18708,18972,19180,19672}, count 4 | 18972 / 18708 | 19672 | 19180 / 19672 | Every retained identity terminated; no live observed PID; no orphan; repeat PASS |
| B, two descendants | 1756 | {1756,1808,7192,9092,12156,18768}, count 6 | 7192 / 1756 | 18768,1808 | 12156 / 18768; 9092 / 1808 | Every retained identity terminated; no live observed PID; no orphan; repeat PASS |

Readiness sampling saw counts 1,2,3,4 in A and 1,2,4,6 in B. Runtime execution
and launch PIDs differ, consistent with Windows virtualenv launcher indirection;
markers establish these parent relationships without guessing image names.
Readiness completes before final inventory capture; workload creates no more
children afterward. Final inventory equality verifies no uncaptured Job member
at the last pre-cleanup observation. Production close verifies empty Job before
releasing its handle. This is observed-tree evidence, not a universal OS monitor.

Contained actual-worker cases: valid PID 5872 exit 0; missing PID 18256 exit 78;
corrupt PID 14860 exit 78. Each singleton inventory retained, exited, repeated
close safe and no orphan. Valid startup marker present; negative workload marker
absent. R5 parser/launch controls all passed. R4 all passed. R3 all passed.
R2 nine passed, then obsolete assertion failed; final native sentinel not reached.
PyArrow 25.0.1 assertion passed; native synthetic and registered parent/child
probes passed. Seven source categories each blocked through Python/public/native
representative routes as exercised. Log contains 33 deliberate blocked registered
source probes, all before content read. Accepted counters below remain zero.
No real payload inspection, scientific execution or downstream validation occurred.

## Complete requested final report

NR means NOT RUN in R7 after bootstrap failure; expected contract values are
not substituted for current certification. Results below refer to this run.

| Requested items | Result |
|---|---|
| 1 Verdict | STOP |
| 2 Classification | A19C-R7-FIREWALL-METHOD-INVALID |
| 3 Starting committed HEAD | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 4 Initial dirty count | 18 actual untracked files; 16 short-status entries |
| 5 Initial dirty paths | Complete list above |
| 6 Unrelated WIP | No |
| 7 Historical STOPs preserved | All seven unchanged |
| 8 R6 defect reconstructed | Yes, old len(before)==2 assertion and R6 evidence |
| 9 Previous expected count | 2 |
| 10 Actual R6 count | 4 |
| 11 Exact invariant | Complete captured set, worker/role membership, all retained identities terminated, no live observed PID/orphan, released Job handle, safe repeat; detailed above |
| 12 Exact cardinality removed | Yes |
| 13 Worker/root observed in Job | Yes, both cases |
| 14 Expected child roles | Yes, one and two descendant workloads plus launch intermediaries |
| 15 Pre-cleanup sets | A {18708,18972,19180,19672}; B {1756,1808,7192,9092,12156,18768} |
| 16 Counts | A 4; B 6 |
| 17 Ancestry | Marker PID/parent and launched-child relationships captured above |
| 18 Cleanup executed | Yes |
| 19 close return | None, ignored; production unchanged |
| 20 All pre-cleanup PIDs absent afterward | All retained identities terminated; none alive in post-close PID probes |
| 21 Any orphan | No observed orphan |
| 22 Repeat cleanup | PASS |
| 23 Dynamic case | PASS, counts 4 and 6; startup counts also varied |
| 24 R5 Windows parser | PASS |
| 25 Valid activation | PASS |
| 26 Missing activation reaches child | Yes |
| 27 Missing activation fail closed | PASS, exit 78 |
| 28 Corrupt activation fail closed | PASS, exit 78 |
| 29 Negative workload executed | No |
| 30 Bypass rejected | PASS |
| 31 Parent guarded | PASS for executed Python boundaries |
| 32 Python child guarded | PASS |
| 33 PyArrow child guarded | PASS |
| 34 Native Feather child guarded | PASS |
| 35 Actual A019 worker guarded | PASS startup; source probe not added to worker |
| 36 Contained worker guarded | PASS |
| 37 PyArrow version | 25.0.1, executed assertion |
| 38 Native invocation | FeatherReader(source, use_memory_map=False, use_threads=True).read() |
| 39 Native synthetic control | PASS |
| 40 Registered native path blocked before read | PASS |
| 41 Connectivity | PASS exercised category boundaries |
| 42 Annotation | PASS exercised category boundaries |
| 43 Neurotransmitter | PASS exercised category boundaries |
| 44 Metadata | PASS exercised category boundaries |
| 45 Provenance | PASS exercised category boundaries |
| 46 Mapping | PASS exercised category boundaries |
| 47 Other registered | PASS exercised category boundaries |
| 48 Deliberate blocked probes | 33 current registered-source probes |
| 49 Accepted connectivity reads | 0 |
| 50 Accepted annotation reads | 0 |
| 51 Accepted neurotransmitter reads | 0 |
| 52 Accepted metadata reads | 0 |
| 53 Accepted provenance reads | 0 |
| 54 Accepted mapping reads | 0 |
| 55 Accepted other reads | 0 |
| 56 Aggregate accepted reads | 0 in executed guarded scope; no universal OS interception claim |
| 57 FIREWALL_BOOTSTRAP_CERTIFIED | No |
| 58 Broader certification resumed | No |
| 59 Accumulated WIP reconciled | Inventoried/preserved; downstream certification NR |
| 60 Forward harness | scripts/benchmark_application_a019.py |
| 61 Bounded route | NR |
| 62 Production default changed | No |
| 63 Merge block | Expected 16384; NR |
| 64 Fallback hard stop | NR |
| 65 G1 | NR |
| 66 G2 | NR |
| 67 G3 | NR |
| 68 G4 | NR |
| 69 G5 | NR |
| 70 G6 | NR |
| 71 L3/L4 rejection | NR |
| 72 PreparedNetwork count | 0 executed in R7; harness NR |
| 73 PreparedRuntime count | 0 executed in R7; harness NR |
| 74 SimulationState count | 0 executed in R7; harness NR |
| 75 A fresh | NR |
| 76 B fresh | NR |
| 77 Runtime reset | No runtime executed |
| 78 Runtime recreated | No runtime executed |
| 79 B derives from A | NR |
| 80 A structure | NR |
| 81 B structure | NR |
| 82 A final horizon | NR |
| 83 B final horizon | NR |
| 84 Total calls | 0 in R7 |
| 85 Max consecutive/state | NR |
| 86 Continuous 480 ms | No trajectory executed |
| 87 A released before B | NR |
| 88 A/B coexist | No states executed |
| 89 Schedule generations | 0 in R7 |
| 90 Seed | NR |
| 91 Horizon | NR |
| 92 Event count | NR |
| 93 Fingerprint | NR |
| 94 A/B identical windows | NR |
| 95 State replay | NR |
| 96 Pending replay | NR |
| 97 Output replay | NR |
| 98 Timing boundaries | NR |
| 99 Preparation timeout | NR |
| 100 Advance timeout | NR |
| 101 Worker timeout | NR |
| 102 Private cap | NR |
| 103 Working-set cap | NR |
| 104 Forced timeout | NR |
| 105 Forced memory stop | NR |
| 106 Containment | PASS bootstrap; harness watchdog NR |
| 107 Complete live-tree cleanup | PASS both bootstrap cases |
| 108 No orphan | PASS observed bootstrap trees |
| 109 No retry | Bootstrap not retried; harness no-retry NR |
| 110 Full pytest | NOT RUN — synthetic-only authorization; known S2 tests excluded |
| 111 S2 exclusions | Exact list below |
| 112 Targeted R7 tests | Both live-tree cases PASS |
| 113 Prior firewall regressions | R5/R4/R3 PASS; R2 nine PASS, one FAIL, final test not reached |
| 114 Targeted A019C | NR |
| 115 Synthetic-safe regressions | A019A/A018UJ/UI/UR/U/T/S/A018/A017/A016/A015/A014/A013/A011/reference-LIF/application all NR |
| 116 compileall | NR, bootstrap failure |
| 117 Integrity | NR, bootstrap failure; also checker reads registered data, prohibited by source-access boundary |
| 118 diff check | NR, bootstrap failure |
| 119 build | NR, bootstrap failure |
| 120 Full-real preparations | 0 |
| 121 Real advances | 0 |
| 122 Future A019D consumed | No |
| 123 GPU used | No |
| 124 Arena | 0 |
| 125 Scientific experiments | 0 |
| 126 Downloads | 0; existing virtualenv used |
| 127 A013 behavior changed | No |
| 128 Scientific semantics changed | No |
| 129 Task016 changed | No |
| 130 Task017 changed | No |
| 131 Task017 classification | NOT_ROBUST preserved |
| 132 Archive writes | 0 |
| 133 Package version | 0.3.0 |
| 134 Active tracked workflows | 0 |
| 135 Final commit | No new commit; 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 136 Push | Not performed |
| 137 Final local HEAD | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 138 Final origin/master | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 139 Final live master | 60c900b0c8e5a02ea95efc7340fd190193edf7e9, verified after failure |
| 140 Worktree/stash | Dirty, 19 intended untracked files; staging/tracked diff/stash empty |
| 141 Tag/release/version mutation | No |
| 142 Superseding A019C status | None; remains uncertified, all historical STOPs preserved |
| 143 Exact next task | Separately authorized bounded correction of obsolete R2 parent-rejection assertion to mandatory-child fail-closed contract, then complete gated bootstrap |
| 144 A019D recommended | No; do not execute |

Exact S2 exclusions preserved, not run:
- tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields
- tests/test_application_a003.py::test_validate_and_run_requests_share_exact_spec_identity
- tests/test_application_a003.py::test_result_events_and_backend_export_routes
- tests/test_application_a018uj.py::test_independent_frozen_artifact_reconstruction_and_provenance

No success token emitted. No biological interpretation. No stop-evidence commit
because the mandatory bootstrap remains failed. Only the accumulated R5 test file
and this new R7 plan were changed in R7; all other WIP preserved.
