# Application A019C-R8: obsolete child-guard regression correction

Authorization: `授權 A019C-R8`. One bounded regression correction, followed by
bootstrap-gated synthetic certification. Repository root was derived with
`git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`.
Starting local HEAD, origin/master and live GitHub master all matched
`60c900b0c8e5a02ea95efc7340fd190193edf7e9`.
Version 0.3.0; zero tracked active workflows; staging and stash empty.

## Plan and initial inventory

1. Inventory and preserve accumulated WIP; reject unrelated changes.
2. Correct only the obsolete R2 test to the mandatory-child responsibility split.
3. Run the complete accumulated bootstrap fail-fast under the startup firewall.
4. Only after bootstrap PASS, run the synthetic harness and explicit validation.
5. Preserve failures and withhold success, commit/push and A019D readiness unless
   every required stage passes.

Initial inventory: exactly 19 untracked files, no tracked modifications, no
unrelated paths. The directory-collapsed short status had 17 entries; the full
file inventory below is authoritative. No reset, restore, checkout, clean or
stash operation was performed.

```text
docs/plans/2026-10-05-application-a019c-executable-harness-contract-alignment.md
docs/plans/2026-10-05-application-a019c-harness-contract.json
docs/plans/2026-10-05-application-a019c-r2-guard-first-firewall-recovery.md
docs/plans/2026-10-05-application-a019c-synthetic-evidence.json
docs/plans/2026-10-06-application-a019c-r3-native-process-firewall-coverage.md
docs/plans/2026-10-06-application-a019c-r4-inherited-child-fail-closed.md
docs/plans/2026-10-06-application-a019c-r5-windows-mandatory-child-audit.md
docs/plans/2026-10-06-application-a019c-r6-contained-worker-cleanup.md
docs/plans/2026-10-06-application-a019c-r7-live-process-tree-cleanup.md
scripts/a019c_firewall/guarded_child.py
scripts/a019c_firewall/sitecustomize.py
scripts/a019c_firewall/validation_firewall.py
scripts/benchmark_application_a019.py
tests/fixtures/application-a019c-preparation-identity.json
tests/test_application_a019c.py
tests/test_application_a019c_r2_firewall.py
tests/test_application_a019c_r3_firewall.py
tests/test_application_a019c_r4_firewall.py
tests/test_application_a019c_r5_firewall.py
```

## Correction and preserved chronology

R7 ended with 37 passed, 1 failed. Its exact remaining failure was
`tests/test_application_a019c_r2_firewall.py::test_child_cannot_drop_guard`.
The old test asserted `pytest.raises(guard.SourceAccessDenied)` around
`subprocess.run([sys.executable, "-c", "pass"], env={})`. It originated in R2,
before the R5 responsibility split, and expected parent rejection.

The replacement passes the exact mandatory guarded entrypoint explicitly,
removes activation with `env={}`, and supplies a harmless marker-writing
workload. A CompletedProcess with exit 78 and
`FIREWALL_REQUIRED_BUT_NOT_ACTIVE` establishes parent permission, child startup
and child rejection. The absent marker proves that workload did not execute.
The test retains its original name and regression intent.

Production behavior was not changed. No firewall implementation, child bootstrap,
Windows parser, ProcessJob.close, native Feather interception or taxonomy was
edited in R8. R3/R4 neighboring inherited-activation-removal tests remain valid:
they exercise rejection before automatic wrapping, rather than explicitly
passing a legitimate mandatory child. The separate R5 actual-worker bypass test
disables automatic wrapping and proves parent rejection at the audit boundary.
R4/R5 retain corrupt activation and valid activation controls independently.

Preserved historical dispositions, without rewriting any STOP as PASS:
`A19C-F`, `A19C-R-D`, `A19C-R2-C`, `A19C-R3-D`,
`A19C-R4-CHILD-FAIL-CLOSED-INCOMPLETE`,
`A19C-R5-HARNESS-WORKER-COVERAGE-INCOMPLETE`,
`A19C-R6-CONTAINED-WORKER-CLEANUP-INCOMPLETE`,
`A19C-R7-FIREWALL-METHOD-INVALID`.

## Complete bootstrap

Every Python validation invocation set activation to 1, absolute
`PYTHONPATH=<root>/scripts/a019c_firewall`, and a distinct task audit log.
The bootstrap parent ran through `guarded_child.py`, which installs the guard
before pytest discovery/imports. No registered payload was inspected to set up
the task. Git metadata and source/WIP inspection preceded Python execution.

```text
.venv/Scripts/python.exe scripts/a019c_firewall/guarded_child.py -m pytest
  tests/test_application_a019c_r5_firewall.py
  tests/test_application_a019c_r4_firewall.py
  tests/test_application_a019c_r3_firewall.py
  tests/test_application_a019c_r2_firewall.py -q -x
39 passed in 5.28 s
```

**FIREWALL_BOOTSTRAP_CERTIFIED** was issued only after this full PASS and audit
inspection. All P1-P16 requirements passed: parent guard; valid, missing and
corrupt mandatory child activation; independent bypass rejection; Python,
public PyArrow/Feather and native Feather child coverage; actual A019 worker;
Job-contained worker; both live trees; all retained identities terminated;
no observed orphan; repeat cleanup; seven-category coverage. No unexplained
process-tree gap was observed in the tested trees.

Windows controls passed for serialized commands, executable/script paths with
spaces, quoting, similar-script rejection, substring false positives and
mandatory entrypoint recognition. PyArrow was 25.0.1. Native control and blocked
probes used `FeatherReader(source, use_memory_map=False, use_threads=True).read()`.
The R2 historical synthetic-sentinel test retains its original shorter native
invocation; complete exact-signature controls are supplied by R3/R4.

Live-tree evidence, bootstrap parent PID 7748:

| Case | Worker | Pre-cleanup Job-owned PIDs | Post-cleanup | Repeated cleanup | Orphan |
|---|---|---|---|---|---|
| A | 18836 | 1012, 8596, 8976, 18836 | All retained identities exited; none live | PASS | None observed |
| B | 18808 | 4828, 8440, 13008, 18808, 18872, 19396 | All retained identities exited; none live | PASS | None observed |

These are observed counts (4 and 6), not fixed-count requirements.
The tests retain process handles to avoid confusing PID reuse with survival.
All worker/child role and launched-child membership assertions passed.

Bootstrap audit: `C:/TEMP/a019c-r8-bootstrap.jsonl`.
Blocked events: connectivity 8, annotation 4, neurotransmitter 4, metadata 4,
provenance 5, mapping 4, other 5: 34 total. One other-category event is the
generated synthetic sentinel with a temporary deny root; 33 events probe
registered paths. All were rejected before content read. Later integrity
validation added one registered-provenance rejection, giving 35 deliberate
blocked probes overall, of which 34 targeted registered paths.
Accepted connectivity, annotation, neurotransmitter, metadata, provenance,
mapping and other registered reads are each 0; aggregate 0.
These R8 zeros do not replace the historical violation accounting.

## Resumed synthetic certification and validation failure

Only after the bootstrap success gate, the existing accumulated harness was
used without rebuilding or changing implementation:

```text
.venv/Scripts/python.exe scripts/a019c_firewall/guarded_child.py -m pytest
  tests/test_application_a019c.py -q -x
35 passed in 7.39 s

.venv/Scripts/python.exe scripts/a019c_firewall/guarded_child.py
  scripts/benchmark_application_a019.py --synthetic
  --output C:/TEMP/a019c-r8-forward-evidence.json
exit 0; evidence classification A19C-A
```

The fresh CLI evidence is distinct from the historical synthetic evidence and
does not overwrite it. It records explicit bounded-route opt-in,
`A015/A016/A017/A018/A018T/A018U/A018UJ`, block size 16384, no fallback,
G1-G6 true, one prepared network, one runtime, two states, 24 completed calls,
240 ms per state, exact replay, A released before B, no coexisting states,
and one 948-event schedule with the required fingerprint. The targeted suite
also passed both fallback stops, cross-layer rejection, timing brackets,
forced preparation/advance/worker timeouts, memory stops, process containment,
cleanup, no observed orphan and no retry. Production defaults and A013 remain
unchanged. CLI watchdog: one launch, 161 samples, no observed orphan.

The explicit broader manifest selected A019A, A018UJ, A018UI, A018UR, A018U,
A018T, A018S, A018, A017, A016, A015, A014, A013, A011, reference-LIF
(`test_task005.py`), A008, A007C/B/A, A006R/A006, A005, A004, A003 and A002.
All execution remained under the firewall. The run used `-q -x` and explicitly
deselected the three named A003 S2 tests and A018UJ provenance reconstruction.
No unfiltered full pytest was run.

Result: **15 passed, 1 failed, 4 deselected in 2.02 s**. A019A passed all four
tests; A018UJ passed eleven selected cases before its last selected test failed:

`tests/test_application_a018uj.py::test_no_real_execution_and_scientific_default_unchanged`

The failing statement launches `git diff` through Python subprocess. The
unchanged validation firewall rejects it with
`SourceAccessDenied: unsupported A019 child executable`. No Git child workload
started. This is a post-bootstrap validation integration failure, not a
missing-activation regression or accepted registered-source access. The later
manifest entries were not executed after this fail-fast stop. They are not
claimed PASS. No firewall exception, unrelated test edit, or retry was added.
An equivalent shell-side Git metadata diff was empty, but is not substituted
for a passing pytest result.

Independent post-bootstrap checks:

| Check | Result |
|---|---|
| `uv run --offline python -m compileall src scripts tests` | PASS |
| `uv run --offline python scripts/check_tracked_integrity.py` | FAIL CLOSED: registered provenance blocked before read; exit 1 |
| `git diff --check` | PASS; no tracked diff; final untracked R8 changes also checked separately |
| `uv build --offline` | FAIL CLOSED: setuptools source-distribution backend exited 78; no successful build claim |

Offline mode prevented downloads. The build startup failure was not repaired or
retried; its detailed underlying startup exception is not established by the
captured output. No build PASS is inferred from prior runs.

S2 exclusions:

- `test_selection_uses_stable_a002_digest_and_rejects_extra_fields`
- `test_validate_and_run_requests_share_exact_spec_identity`
- `test_result_events_and_backend_export_routes`
- `test_independent_frozen_artifact_reconstruction_and_provenance`

**NOT RUN — REAL-DATA DEPENDENT / OUTSIDE AUTHORIZATION** applies to those S2
tests. Full pytest: **NOT RUN — synthetic-only authorization; known S2 tests excluded**.
The integrity command was attempted under the guard and denied; it did not
successfully read the prohibited manifest.

## Final disposition and complete requested checklist

**A19C-R8-B — FIREWALL BOOTSTRAP CERTIFIED; A019C HARNESS SYNTHETIC CERTIFICATION FAILED.**
The harness-specific 35 tests and fresh CLI succeeded, but the complete required
certification remains failed at Stage 3. This classification does not claim
that the forward synthetic replay itself failed. Stage 1 PASS, Stage 2 targeted
PASS, Stage 3 FAIL. `A019C-FORWARD-HARNESS-SYNTHETICALLY-CERTIFIED` is withheld.
No commit or push was made; all accumulated WIP is preserved. A019D is not
recommended and its future real attempt remains unconsumed. The next bounded
work is validation/firewall integration adjudication for non-Python metadata
children, isolated build bootstrap, and the prohibited integrity inputs;
it requires separate scope and must preserve the zero-real-source boundary.

In the checklist, NR means not executed after the fail-fast broader validation
failure, not a PASS. PASS evidence is scoped to this R8 execution.

| # | Requested field | Result |
|---|---|---|
| 1 | Verdict | Bootstrap PASS; complete certification FAIL |
| 2 | R8 classification | A19C-R8-B |
| 3 | Starting HEAD | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 4 | Initial dirty count | 19 files |
| 5 | Initial dirty paths | Full inventory above |
| 6 | Unrelated WIP | No |
| 7 | Historical STOPs preserved | Yes, all eight |
| 8 | Obsolete test path | tests/test_application_a019c_r2_firewall.py |
| 9 | Obsolete test name | test_child_cannot_drop_guard |
| 10 | Old behavior | Parent rejection for missing activation |
| 11 | New behavior | Legitimate entrypoint permitted; child rejects before workload |
| 12 | Test corrected | Yes |
| 13 | Production behavior changed | No |
| 14 | Valid guarded child | PASS |
| 15 | Missing activation parent permits | Yes |
| 16 | Missing activation child starts | Yes |
| 17 | Missing activation child fails closed | Yes, exit 78 and deterministic error |
| 18 | Missing activation workload executed | No |
| 19 | Corrupt activation parent permits | Yes |
| 20 | Corrupt activation child fails closed | Yes, exit 78 |
| 21 | Corrupt activation workload executed | No |
| 22 | Bypass parent rejection | PASS |
| 23 | Bypass workload executed | No |
| 24 | Windows parser | PASS |
| 25 | Paths with spaces | PASS |
| 26 | Quoting | PASS |
| 27 | Substring false positives | Rejected; PASS |
| 28 | Similar scripts | Rejected; PASS |
| 29 | Observed 4-process cleanup | PASS |
| 30 | Observed 6-process cleanup | PASS |
| 31 | All observed pre-cleanup PIDs gone | Yes; retained identities exited |
| 32 | Observed orphan | None |
| 33 | Repeated cleanup | PASS |
| 34 | Parent guard | PASS |
| 35 | Python child guard | PASS |
| 36 | PyArrow child guard | PASS |
| 37 | Native Feather child guard | PASS |
| 38 | Actual A019 worker guard | PASS |
| 39 | Job-contained worker | PASS |
| 40 | PyArrow version | 25.0.1 |
| 41 | Native invocation | FeatherReader(source, use_memory_map=False, use_threads=True).read() |
| 42 | Synthetic native control | PASS |
| 43 | Registered native path blocked before read | Yes |
| 44 | Connectivity coverage | PASS |
| 45 | Annotation coverage | PASS |
| 46 | Neurotransmitter coverage | PASS |
| 47 | Metadata coverage | PASS |
| 48 | Provenance coverage | PASS |
| 49 | Mapping coverage | PASS |
| 50 | Other registered coverage | PASS |
| 51 | Deliberate blocked probes | 35 total: 34 registered-path probes, 1 synthetic deny-root sentinel |
| 52 | Accepted connectivity reads | 0 |
| 53 | Accepted annotation reads | 0 |
| 54 | Accepted neurotransmitter reads | 0 |
| 55 | Accepted metadata reads | 0 |
| 56 | Accepted provenance reads | 0 |
| 57 | Accepted mapping reads | 0 |
| 58 | Accepted other registered reads | 0 |
| 59 | Aggregate accepted reads | 0 |
| 60 | FIREWALL_BOOTSTRAP_CERTIFIED | Yes |
| 61 | Broader certification resumed | Yes, only after bootstrap PASS |
| 62 | Accumulated WIP reconciled | Preserved and reused; closure incomplete |
| 63 | Harness path | scripts/benchmark_application_a019.py |
| 64 | Explicit bounded route | Yes; A015/A016/A017/A018/A018T/A018U/A018UJ |
| 65 | Production default changed | No |
| 66 | Merge block size | 16384 |
| 67 | Fallback hard stop | PASS, negative and overflow controls |
| 68 | G1 | PASS |
| 69 | G2 | PASS |
| 70 | G3 | PASS |
| 71 | G4 | PASS |
| 72 | G5 | PASS |
| 73 | G6 | PASS |
| 74 | L3/L4 rejection | PASS, both directions |
| 75 | PreparedNetwork count | 1 per successful forward run |
| 76 | PreparedRuntime count | 1 per successful forward run |
| 77 | SimulationState count | 2 per successful forward run |
| 78 | A fresh | Yes |
| 79 | B fresh | Yes |
| 80 | Runtime reset | No |
| 81 | Runtime recreation | No |
| 82 | B derives from A | No |
| 83 | A structure | 2 warmups + 10 measured; 20 ms/call |
| 84 | B structure | 2 warmups + 10 measured; 20 ms/call |
| 85 | A final horizon | 240 ms |
| 86 | B final horizon | 240 ms |
| 87 | Total calls | 24 per successful forward run |
| 88 | Maximum consecutive/state | 12 |
| 89 | Continuous 480-ms state | No |
| 90 | A released before B | Yes |
| 91 | A/B coexist | No |
| 92 | Schedule generation count | 1 per successful forward run |
| 93 | Schedule seed | 1555062870 |
| 94 | Schedule horizon | 240 ms |
| 95 | Schedule event count | 948 |
| 96 | Schedule fingerprint | 6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a |
| 97 | A/B windows identical | Yes |
| 98 | State replay exact | Yes; membrane, synaptic, refractory, final state/time |
| 99 | Pending replay exact | Yes; pending and delayed-event counts |
| 100 | Output replay exact | Yes |
| 101 | Timing boundaries preserved | PASS |
| 102 | Preparation timeout wired | 600 s; PASS |
| 103 | Advance timeout wired | 30 s; PASS |
| 104 | Worker timeout wired | 1500 s; PASS |
| 105 | Private cap wired | 8589934592 bytes; PASS |
| 106 | Working-set cap wired | 8589934592 bytes; PASS |
| 107 | Forced timeout | PASS |
| 108 | Forced memory stop | PASS |
| 109 | Process containment | PASS |
| 110 | Complete live-tree cleanup | PASS for both observed bootstrap trees and targeted watchdog cases |
| 111 | No observed orphan | PASS |
| 112 | No retry | PASS |
| 113 | Full pytest | NOT RUN — synthetic-only authorization; known S2 tests excluded |
| 114 | S2 exclusions | Three A003 tests and A018UJ provenance reconstruction, named above |
| 115 | Targeted R8 test | PASS within 39-test bootstrap |
| 116 | Accumulated firewall regressions | 39 PASS, R2-R7 coverage in R2/R3/R4/R5 files |
| 117 | Targeted A019C | 35 PASS; fresh CLI exit 0 |
| 118 | Synthetic-safe regressions | 15 PASS, 1 FAIL, 4 deselected; later sets NR |
| 119 | compileall | PASS |
| 120 | Tracked integrity | FAIL CLOSED before registered provenance read |
| 121 | Diff check | PASS |
| 122 | Build | FAIL; isolated backend exit 78 under activation |
| 123 | Full-real preparations | 0 |
| 124 | Real advances | 0 |
| 125 | Future A019D attempt consumed | No |
| 126 | GPU used | No |
| 127 | Arena runs | 0; later A011 tests were never reached |
| 128 | Scientific experiments | 0 |
| 129 | Downloads | 0; uv commands offline |
| 130 | Historical A013 behavior changed | No |
| 131 | Scientific semantics changed | No |
| 132 | Historical Task016 changed | No |
| 133 | Historical Task017 changed | No |
| 134 | Historical Task017 classification | NOT_ROBUST |
| 135 | Archive writes | 0 |
| 136 | Package version | 0.3.0 |
| 137 | Active tracked workflows | 0 |
| 138 | Final commit SHA | No new commit; starting SHA retained |
| 139 | Push result | Not attempted; A19C-R8-A not reached |
| 140 | Final local HEAD | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 141 | Final origin/master | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 142 | Final live master | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 143 | Worktree/stash | Dirty: 20 scoped untracked files; staging empty; stash empty |
| 144 | Tag/release/version mutation | No |
| 145 | Superseding A019C status | Bootstrap certified; full synthetic certification incomplete |
| 146 | Exact next task | Separately scoped validation/firewall integration adjudication; no automatic execution |
| 147 | A019D recommended | No |

All non-test mutation in R8 is this documentation file. The only test mutation
is the obsolete R2 regression. No previous chronology was erased. No biological
interpretation is made.
