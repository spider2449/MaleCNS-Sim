# A019C-R5 Windows mandatory-child audit repair

Authorization: `授權 A019C-R5`, exactly one bounded correction. No registered
payload access or real execution authorized. Repository root dynamically derived
with `git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`.

**STOP: A19C-R5-HARNESS-WORKER-COVERAGE-INCOMPLETE.**
FIREWALL_BOOTSTRAP_CERTIFIED was not issued. Broader certification did not resume.

## Inventory and plan

Starting local HEAD, origin/master and live GitHub master all equal
`60c900b0c8e5a02ea95efc7340fd190193edf7e9`. Initial worktree contained 15 actual
untracked files, represented by 13 short-status entries. Staging empty, tracked
diff empty, stash empty. All paths belong to accumulated A019C/R2/R3/R4 WIP;
no unrelated changes. No reset, restore, checkout, clean or stash performed.

Initial paths:

1. docs/plans/2026-10-05-application-a019c-executable-harness-contract-alignment.md
2. docs/plans/2026-10-05-application-a019c-harness-contract.json
3. docs/plans/2026-10-05-application-a019c-r2-guard-first-firewall-recovery.md
4. docs/plans/2026-10-05-application-a019c-synthetic-evidence.json
5. docs/plans/2026-10-06-application-a019c-r3-native-process-firewall-coverage.md
6. docs/plans/2026-10-06-application-a019c-r4-inherited-child-fail-closed.md
7. scripts/a019c_firewall/guarded_child.py
8. scripts/a019c_firewall/sitecustomize.py
9. scripts/a019c_firewall/validation_firewall.py
10. scripts/benchmark_application_a019.py
11. tests/fixtures/application-a019c-preparation-identity.json
12. tests/test_application_a019c.py
13. tests/test_application_a019c_r2_firewall.py
14. tests/test_application_a019c_r3_firewall.py
15. tests/test_application_a019c_r4_firewall.py

Bounded plan: inspect harmless Windows audit values; implement canonical detection;
test serialization first, then mandatory-child responsibility split, then contained
actual worker. Only certify bootstrap after the complete matrix passes; otherwise
stop immediately. The bootstrap failed; subsequent phases remain gated.

Historical records were not edited. A19C-F, A19C-R-D, A19C-R2-C, A19C-R3-D and
A19C-R4-CHILD-FAIL-CLOSED-INCOMPLETE remain historical STOP dispositions.

## Windows evidence and correction

A harmless unguarded Python launch printed 19, with an audit-only observer.
Exact event: `subprocess.Popen`. Event arguments observed:

```python
(None,
 'D:\\spider\\working\\MaleCNS-Sim\\.venv\\Scripts\\python.exe -c print(19) "ordinary quoted argument"',
 None,
 None)
```

Argument types: `(NoneType, str, NoneType, NoneType)`. The command is a serialized
Windows command line, not an argv list. The executable argument is None when
Popen derives it from argv[0]. No shell=True involved. The actual guarded launch
test confirms serialization exactly equals `subprocess.list2cmdline(argv)`.
R4's list/tuple-only assumption is confirmed wrong.

Correction restricted to validation_firewall.py: decode Windows command lines
using CommandLineToArgvW with explicit ctypes signatures and LocalFree; require
exact list2cmdline round-trip equality to fail closed on noncanonical ambiguity.
Compare resolved argv[0] to sys.executable, optional audit executable to that same
path, and argv[1] to the exact approved absolute guarded_child.py. Require a
supported workload position (script, -c, or -m). Entry identity does not inspect
activation. The child retains sole responsibility for activation verification.
No naive whitespace split, broad shell parser or substring approval introduced.
This is the bounded A019 Python launch contract, not a universal OS sandbox.

## Executed bootstrap evidence

Both executions used `.venv/Scripts/python.exe`, activation=1,
PYTHONPATH=scripts/a019c_firewall and a distinct temporary JSONL audit log.
Command tail:

```text
scripts/a019c_firewall/guarded_child.py -m pytest tests/test_application_a019c_r5_firewall.py tests/test_application_a019c_r4_firewall.py -q -x
```

First execution: **18 passed in 2.42 seconds**. Narrow parser cases ran before
process tests. Passed: normal absolute Python path, Python path with spaces,
guard script path with spaces, extra ordinary args, escaped quotes/backslashes,
substring false positives, similar script names, malformed command line,
actual Windows serialization and actual worker bypass rejection.

R4 tests then passed under the correction: active parent and native synthetic
control, all seven source categories, four missing/corrupt activation variants
(normal child and actual worker), positive public/native Feather child and
actual worker startup. Missing activation was allowed through the parent;
the child emitted FIREWALL_REQUIRED_BUT_NOT_ACTIVE and exited 78. A returned
CompletedProcess with that child-generated message establishes child startup.
Workload marker absent; worker guarded-start message absent in negative cases.
Parent did not reject those mandatory launches. Direct actual-worker bypass was
rejected by the audit before process creation using a test-only disabled routing
wrapper, preserving the independent parent audit enforcement proof.

Additional bootstrap tests were authored for a copied mandatory script in a
temporary directory containing spaces and for the actual worker launched through
the unchanged A014 ProcessJob suspended-launch/Job Object path. There is no
separate watchdog worker script: A019 supervisor uses this ProcessJob mechanism.

Final execution: **11 passed, 1 failed in 1.18 seconds**. The actual path-with-spaces
process test passed, preserving escaped ordinary argument content. Valid-activation
contained actual worker started, returned 0 and emitted
A019_WORKER_GUARDED_BEFORE_WORKLOAD. Failure occurred in the test's finally block:

```text
assert job.close() == []
E assert None == []
```

The newly authored test incorrectly assumed a list return from close(). Source
inspection confirms close() verifies empty job inventory internally, closes the
handle and returns None. The call completed, but the test assertion failed.
This is a test API assumption error, not evidence of parent audit rejection,
uncontained execution or accepted real-source access. It still prevents complete
bootstrap certification. STOP honored immediately: no correction/retry after
this failure, no remaining contained-worker activation cases or later tests run.

## Accounting

First execution log: 16 deliberate blocked probes (14 parent category probes,
2 public/native registered-path child probes). Final execution log: zero blocked
source probes; it stopped before the later source-category tests. Total R5
deliberate blocked probes: 16. Each logged before_content_read=true.

Seven accepted counters, each 0 within executed guarded paths:
accepted_real_connectivity_reads, accepted_real_annotation_reads,
accepted_real_neurotransmitter_reads, accepted_real_metadata_reads,
accepted_real_provenance_reads, accepted_real_mapping_reads,
accepted_other_registered_reads. Aggregate 0. No claim of a universal native
acceptance monitor. Complete process-tree coverage remains uncertified.

## Required final report

Values marked NOT RUN refer to R5 certification, not historical evidence. Contract
values below are source/contract requirements only and are not newly certified.

| Item | Result |
|---|---|
| 1 Verdict | STOP; bootstrap incomplete |
| 2 Classification | A19C-R5-HARNESS-WORKER-COVERAGE-INCOMPLETE |
| 3 Starting committed HEAD | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 4 Initial dirty count | 15 actual files, all untracked |
| 5 Initial dirty paths | Full list above |
| 6 Unrelated WIP | No |
| 7 Historical A19C-F preserved | Yes, unchanged |
| 8 Historical A19C-R-D preserved | Yes, unchanged |
| 9 Historical A19C-R2-C preserved | Yes, unchanged |
| 10 Historical A19C-R3-D preserved | Yes, unchanged |
| 11 Historical A19C-R4 stop preserved | Yes, unchanged |
| 12 Windows audit event | subprocess.Popen |
| 13 Windows audit value type | str at args[1] |
| 14 Serialized example | Exact example above |
| 15 R4 argv-list assumption wrong | Yes |
| 16 Detection strategy | CommandLineToArgvW, canonical serialization round trip, exact executable/script positions |
| 17 Naive whitespace split avoided | Yes |
| 18 Spaces tests | PASS; serialized executable/script cases and actual copied-script launch |
| 19 Quoting tests | PASS |
| 20 Substring false-positive rejection | PASS |
| 21 Similar-script rejection | PASS |
| 22 Parent mandatory-child recognition | PASS |
| 23 Missing activation allowed by parent | Yes |
| 24 Missing activation child started | Yes |
| 25 Child rejected itself | Yes; exit 78 and FIREWALL_REQUIRED_BUT_NOT_ACTIVE |
| 26 Negative workload executed | No |
| 27 Positive guarded child | PASS |
| 28 Bypass parent rejection | PASS |
| 29 Parent guarded | Yes |
| 30 Python child guarded | PASS |
| 31 Public PyArrow child guarded | PASS in first execution |
| 32 Native Feather child guarded | PASS in first execution |
| 33 Actual A019 worker guarded | Direct startup PASS; contained positive startup observed, contained certification incomplete |
| 34 Actual worker missing guard fails closed | Direct missing/corrupt activation PASS; contained variants NOT RUN after failure |
| 35 Watchdog worker separately covered | Same actual worker through ProcessJob; complete matrix incomplete |
| 36 PyArrow version | 25.0.1 |
| 37 Native invocation | FeatherReader(source, use_memory_map=False, use_threads=True).read() |
| 38 Synthetic native control | PASS |
| 39 Native registered path blocked | PASS, before constructor/content read |
| 40 Connectivity category | PASS |
| 41 Annotation category | PASS |
| 42 Neurotransmitter category | PASS |
| 43 Metadata category | PASS |
| 44 Provenance category | PASS |
| 45 Mapping category | PASS |
| 46 Other registered category | PASS |
| 47 Deliberate blocked probes | 16 across R5 executions |
| 48 Accepted connectivity reads | 0 |
| 49 Accepted annotation reads | 0 |
| 50 Accepted neurotransmitter reads | 0 |
| 51 Accepted metadata reads | 0 |
| 52 Accepted provenance reads | 0 |
| 53 Accepted mapping reads | 0 |
| 54 Accepted other registered reads | 0 |
| 55 Aggregate accepted reads | 0 |
| 56 FIREWALL_BOOTSTRAP_CERTIFIED | No |
| 57 Broader certification resumed | No |
| 58 Accumulated WIP reconciled | Preserved, not fully certified or reconciled for commit |
| 59 Forward harness | scripts/benchmark_application_a019.py |
| 60 Explicit bounded route | Present in accumulated source; NOT RUN in R5 |
| 61 Production default changed | No |
| 62 Merge block | Contract 16,384; NOT RUN in R5 |
| 63 Fallback hard stop | NOT RUN |
| 64 G1 | NOT RUN |
| 65 G2 | NOT RUN |
| 66 G3 | NOT RUN |
| 67 G4 | NOT RUN |
| 68 G5 | NOT RUN |
| 69 G6 | NOT RUN |
| 70 L3/L4 rejection | NOT RUN |
| 71 PreparedNetwork count | Contract 1; no preparation executed in R5 |
| 72 PreparedRuntime count | Contract 1; none constructed in R5 |
| 73 SimulationState count | Contract 2; none created in R5 |
| 74 State A fresh | NOT RUN |
| 75 State B fresh | NOT RUN |
| 76 Runtime reset | No |
| 77 Runtime recreated | No |
| 78 B derives from A | No; neither executed |
| 79 A structure | Contract 2 warmups + 10 measured, 20 ms each; NOT RUN |
| 80 B structure | Contract 2 warmups + 10 measured, 20 ms each; NOT RUN |
| 81 A final horizon | Contract 240 ms; NOT RUN |
| 82 B final horizon | Contract 240 ms; NOT RUN |
| 83 Total calls | Contract 24; 0 executed in R5 |
| 84 Max consecutive/state | Contract 12; NOT RUN |
| 85 Continuous 480-ms state | No |
| 86 A released before B | NOT RUN |
| 87 A/B coexist | No; neither executed |
| 88 Schedule generation count | Contract 1; 0 in R5 |
| 89 Schedule seed | Contract 1555062870 |
| 90 Schedule horizon | Contract 240 ms |
| 91 Schedule events | Contract 948 |
| 92 Schedule fingerprint | Contract 6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a |
| 93 A/B exact windows | NOT RUN |
| 94 State replay exact | NOT RUN |
| 95 Pending replay exact | NOT RUN |
| 96 Output replay exact | NOT RUN |
| 97 Timing boundaries | Unmodified; NOT RUN |
| 98 Preparation timeout | Source contract 600 s; NOT RUN |
| 99 Advance timeout | Source contract 30 s; NOT RUN |
| 100 Worker timeout | Source contract 1500 s; NOT RUN |
| 101 Private cap | Source contract 8,589,934,592; NOT RUN |
| 102 Working-set cap | Source contract 8,589,934,592; NOT RUN |
| 103 Forced timeout | NOT RUN |
| 104 Forced memory stop | NOT RUN |
| 105 Process containment | Positive actual worker starts through Job Object; complete proof incomplete |
| 106 Cleanup/no orphan | close() completed; new assertion failed (None versus []); not certified |
| 107 No retry | No harness retry performed; synthetic no-retry certification NOT RUN |
| 108 Full pytest | NOT RUN — synthetic-only authorization; known S2 tests excluded |
| 109 S2 exclusions | Four tests listed below; NOT RUN — REAL-DATA DEPENDENT / OUTSIDE AUTHORIZATION |
| 110 Targeted R5 firewall tests | First 10 PASS; final 11 PASS / 1 FAIL, remaining tests stopped |
| 111 Targeted A019C tests | NOT RUN — bootstrap failure |
| 112 Synthetic regressions | NOT RUN — bootstrap failure |
| 113 compileall | NOT RUN — bootstrap failure |
| 114 Tracked integrity | NOT RUN — bootstrap failure; registered provenance reads also outside authorization |
| 115 diff check | NOT RUN — bootstrap failure |
| 116 build | NOT RUN — bootstrap failure |
| 117 Full-real preparations | 0 |
| 118 Real advances | 0 |
| 119 A019D attempt consumed | No |
| 120 GPU used | No |
| 121 Arena runs | 0 |
| 122 Scientific experiments | 0 |
| 123 Downloads | 0 |
| 124 Historical A013 changed | No |
| 125 Scientific semantics changed | No |
| 126 Historical Task016 changed | No |
| 127 Historical Task017 changed | No |
| 128 Task017 classification | NOT_ROBUST preserved |
| 129 Archive writes | 0 |
| 130 Package version | 0.3.0 |
| 131 Active tracked workflows | 0 |
| 132 Final commit SHA | Unchanged 60c900b0c8e5a02ea95efc7340fd190193edf7e9; no new commit |
| 133 Push result | Not attempted |
| 134 Final local HEAD | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 135 Final origin/master | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 136 Final live GitHub master | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 137 Worktree/stash | Dirty intended WIP, 17 actual untracked files after R5 test/plan additions; staging/stash empty |
| 138 Tag/release/version mutation | No |
| 139 Superseding status | R5 stopped; no superseding A019C readiness certification |
| 140 Exact next task | Separately authorized contained-worker bootstrap test correction and completion, then gated A019C synthetic certification |
| 141 A019D recommended | No |

S2 exclusions preserved:

- test_selection_uses_stable_a002_digest_and_rejects_extra_fields
- test_validate_and_run_requests_share_exact_spec_identity
- test_result_events_and_backend_export_routes
- A018UJ test_independent_frozen_artifact_reconstruction_and_provenance

No success or bounded-stop evidence commit; failed new test remains reviewable WIP.
No push, tag or release. No biological interpretation. A019D remains unconsumed.
