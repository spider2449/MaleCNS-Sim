# Application A019C-R12: A014 direct-executable admission adjudication

Authorization: `授權 A019C-R12`. Synthetic-only. Root derived with
`git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`.

## Plan and stop gates

1. Inventory accumulated WIP and local/origin/live identities.
2. Audit the A014 source and historical direct/launcher distinction.
3. Reproduce only `[0-direct]` under the current certified firewall.
4. Adjudicate D1-D5 and make only the narrow authorized correction.
5. Rerun the direct target, then the complete A014 admitted set; stop on failure.
6. Only after A014 PASS, run bootstrap, harness, CLI and deferred validation.
7. Record evidence; commit/push only on A19C-R12-A.

## Starting inventory

Local HEAD = origin/master = live GitHub master =
`60c900b0c8e5a02ea95efc7340fd190193edf7e9`.
Expanded dirty paths: **24**. Short status collapses the firewall directory.
Staging empty; stash empty; unrelated WIP **No**. Package 0.3.0;
active tracked `.github/workflows` files 0. No reset, restore, checkout,
clean, stash or discard.

Exact initial paths:

```text
tests/test_application_a018ur.py
docs/plans/2026-10-05-application-a019c-executable-harness-contract-alignment.md
docs/plans/2026-10-05-application-a019c-harness-contract.json
docs/plans/2026-10-05-application-a019c-r2-guard-first-firewall-recovery.md
docs/plans/2026-10-05-application-a019c-synthetic-evidence.json
docs/plans/2026-10-06-application-a019c-r10-validation-manifest-closure.md
docs/plans/2026-10-06-application-a019c-r11-supervisor-startup-timeout.md
docs/plans/2026-10-06-application-a019c-r3-native-process-firewall-coverage.md
docs/plans/2026-10-06-application-a019c-r4-inherited-child-fail-closed.md
docs/plans/2026-10-06-application-a019c-r5-windows-mandatory-child-audit.md
docs/plans/2026-10-06-application-a019c-r6-contained-worker-cleanup.md
docs/plans/2026-10-06-application-a019c-r7-live-process-tree-cleanup.md
docs/plans/2026-10-06-application-a019c-r8-obsolete-child-guard-regression.md
docs/plans/2026-10-06-application-a019c-r9-validation-firewall-integration.md
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

All earlier chronology and STOP classifications remain unchanged, including
`A19C-R11-DEFERRED-VALIDATION-BLOCKER`. R11 C1 timeout correction remains in
the accumulated WIP. R10 J2/I2/B2 are not reopened.

## Static contract and historical intent

Exact target:
`tests/test_application_a014.py::test_tree_memory_enforcement[0-direct]`.
Parameterization: repeat=0,1 crossed with direct, launcher, child, replacement.
Historical source: `git show e195c7c:tests/test_application_a014.py`.
Historical plan: `docs/plans/2026-10-05-application-a014-preparation-memory-investigation.md`,
process containment and synthetic control discussion (lines 101-103).

The direct case deliberately uses `sys._base_executable`, unlike launcher mode's
`sys.executable`. The historical plan explicitly lists direct base interpreter,
actual Windows virtualenv launcher -> worker, parent -> child, and parent exits
after spawn, twice each. Direct execution is an independent control of process
tree memory enforcement without the virtualenv redirector. It needs the base
interpreter identity, not arbitrary Python code or a child-activation bypass.
Its workload is only a 160-MiB bytearray, PID print and eight-second sleep.
It has no repository/data-source dependency. It must be in the same Job Object.

Launch: `supervise_synthetic` -> real `ProcessJob` -> suspended Popen -> assign
Job Object -> resume. Breakaway disabled, KILL_ON_JOB_CLOSE enabled. Inventory
and memory accounting are Job Object based. Supervisor samples aggregate private
bytes and working set at 20 ms, cap=128 MiB, timeout=10 seconds, terminates the
tree and waits for empty inventory. Expected MEMORY_LIMIT, offenders nonempty,
orphans=[], exit=1 for direct/launcher/child and exit=0 for replacement. The
non-direct cases additionally require an offender different from the launcher
and small launcher private bytes where present. There is no retry loop.

## Single pre-fix reproduction

Environment for every R12 pytest command:
`MALECNS_A019C_R2_FIREWALL=1`, absolute `PYTHONPATH=scripts/a019c_firewall`,
separate `MALECNS_A019C_R2_LOG` paths under `C:/TEMP`.

Command:
`.venv/Scripts/python.exe scripts/a019c_firewall/guarded_child.py -m pytest tests/test_application_a014.py::test_tree_memory_enforcement[0-direct] -q -x --basetemp=C:/TEMP/a019c-r12-prefix-tests`.
Exit 1: 1 failed in 0.14 s. Audit: `C:/TEMP/a019c-r12-prefix.jsonl`.
Requested executable: `D:/uv/cpython-3.14-windows-x86_64-none/python.exe`.
Requested argv: base executable, `-c`, fixed allocate/PID/sleep string.
Parent decision: `SourceAccessDenied('unsupported A019 child executable')`
in `validation_firewall.guarded_command`, before Popen launches a process.
Parent ACTIVE recorded; child did not start; workload/allocation did not start.
ProcessJob exception closes its newly created job handle. No child/orphan/retry.
All accepted registered-source counters zero.

## Adjudication and correction

**D2 — LEGITIMATE BOUNDED SYNTHETIC EXECUTABLE CONTROL.** Source and history
explicitly require the independent direct-base-interpreter topology. Pre-fix
rejection precedes memory execution, so this is not D3. D1 would erase the
documented direct-versus-redirector distinction if changed to the usual launcher.
D4 would exclude a material synthetic memory control without justification.

Exact admission is the complete four-element argv:

```text
<resolved sys._base_executable>
-S
<absolute scripts/a019c_firewall/a014_direct_control.py>
a014-tree-memory-control-v1
```

Parent wrapper and native Popen audit both check this identity. An explicit
executable override must resolve to the same base executable. No extra argument,
arbitrary code, shell, alternate executable, PATH lookup, or generic base-Python
admission is added. Existing virtualenv guarded-child policy remains unchanged.
Admission requires activation=1. The fixed script checks purpose and activation,
loads the existing local venv dependencies and explicitly installs the guard
before any workload or probe. `-S` prevents ignored sitecustomize failures;
explicit installation fails closed. The script sets descendant `sys.executable`
to the established venv interpreter. Descendants use mandatory guarded_child.
Execution admission grants no data permission.

R12 files changed: validation-only `scripts/a019c_firewall/validation_firewall.py`;
new validation fixture `scripts/a019c_firewall/a014_direct_control.py`;
`tests/test_application_a014.py`; new admission controls
`tests/test_application_a019c_r12_firewall.py`; this plan. **Production files
changed: No.** Existing A013/A014 production helpers and scientific semantics
unchanged. Non-firewall historical direct launch remains unchanged.

Intermediate admitted target passed in 0.17 s, but its audit had no child ACTIVE
or allocation record. This was rejected as workload evidence: startup can exceed
the small cap before workload activation. It is not counted as certification.
The fixture now waits for guarded readiness, releases the child, then waits for
the exact 167,772,160-byte allocation marker before returning the same real
contained ProcessJob to the unchanged supervisor. Ten-second fixture handshake
failure closes the job; it does not change the memory cap/classification/timeout.
The direct assertion additionally requires launcher PID among offenders.

Corrected target: **1 passed in 0.71 s**, exit 0.
Command identical except basetemp `C:/TEMP/a019c-r12-corrected-tests` and audit
`C:/TEMP/a019c-r12-corrected.jsonl`. Parent PID 9512; direct PID 19172; descendant
probe PID 12296. ACTIVE recorded for all three. Both registered-path probes
blocked before content read. Direct ready and allocated(167772160) records
present. MEMORY_LIMIT, direct PID offender, exit=1, empty job inventory/orphans=[]
assertions PASS. Exactly one job/workload attempt; no retry. This proves actual
allocation and memory enforcement, not launch rejection or guard startup pressure.
Cleanup evidence is ProcessJob's empty inventory plus waited root process exit;
no separate retained-handle certification is claimed in R12.

## Complete A014 run and mandatory STOP

Command:
`.venv/Scripts/python.exe scripts/a019c_firewall/guarded_child.py -m pytest tests/test_application_a019c_r12_firewall.py tests/test_application_a014.py -q -x --junitxml=C:/TEMP/a019c-r12-a014.xml --basetemp=C:/TEMP/a019c-r12-a014-tests`.
Audit: `C:/TEMP/a019c-r12-a014.jsonl`.
Result: **10 passed, 1 failed in 1.27 s**, exit 1.

All seven R12 admission controls PASS: exact authorized identity accepted;
unrecognized purpose, alternate executable, shell wrapper, arbitrary `-c`, extra
argument rejected; shell=True rejected. Corrected direct case also passes in
this run with direct PID 16840 and descendant 1556 ACTIVE, two blocked probes,
ready and exact allocation recorded. Cleanup/no-orphan/no-retry assertions PASS.

New failure:
`tests/test_application_a014.py::test_tree_memory_enforcement[0-replacement]`:
MEMORY_LIMIT/offenders/orphans assertions reached, but exit_code was **1**,
historical required value **0**. No post-failure correction or retry. This does
not establish a production regression or a cause for the replacement mismatch.
Launcher/child cases passed existing assertions but their workload activation
was not separately proved in R12; startup pressure is not certified as workload
evidence for those cases. A014 complete subset therefore is **NOT PASS**.

**STOP: A19C-R12-A014-REGRESSION-INCOMPLETE.** No subsequent validation executed.

## Final deterministic validation manifest

The exact per-node R11 manifest is preserved in its original plan. It is
incorporated here without changing classifications or historical outcomes.
R12 execution overlays only the entries below; every other node retains its
R11 outcome as historical evidence, not a fresh R12 PASS. Deferred NOT RUN
entries remain NOT RUN. No required S0/S1 entry is silently excluded.

| Entry | Class | R12 outcome |
|---|---|---|
| R12 exact identity control | S0 | PASS |
| R12 five alternative argv controls | S0 | PASS, all five |
| R12 shell=True control | S0 | PASS |
| A014 `[0-direct]` | S1 | PASS, actual allocation proved |
| A014 `[0-launcher]`, `[0-child]` | S1 | Assertions PASS; workload proof not established |
| A014 `[0-replacement]` | S1 | FAIL, exit 1 != 0 |
| A014 repeat=1 four cases | S1 | NOT RUN, fail-fast |
| A014 aggregate/normal/accounting/probe tests | S1/S0 as R11 | NOT RUN, fail-fast |
| Bootstrap complete 39-test suite | S0 | NOT RUN; R11 39 PASS historical |
| A019C 35-test harness | S0 | NOT RUN; R11 35 PASS historical |
| Fresh contained CLI | S0 | NOT RUN; R11 PASS historical |
| A013 admitted subset | S0/S1 | NOT RUN |
| Stateful/A011 continuity and initial-state | S0 | NOT RUN |
| Application admitted regressions and historical Git/Node S1 | S0/S1 | NOT RUN |
| Earlier already-passing suites | S0/S1 | NOT RERUN; no shared production helper change |
| compileall (`uv run python -m compileall src scripts tests`) | S1 | NOT RUN, A014 stop |
| git diff --check | S1 | PASS; covers tracked diff only |
| Three known A003 payload-backed tests | S2 | NOT RUN |
| A018UJ data-diff (J2) and provenance reconstruction | S2 | NOT RUN |
| Default tracked integrity (I2) | S2 | NOT RUN |
| Unfiltered full pytest | S2 | NOT RUN, synthetic-only authorization |
| Build (B2) | S1 | NOT RUN, preserved R10 disposition |
| Arena-specific A011 cases | N | NOT RUN |
| Commit/push/tag/release/version mutation | N | NOT EXECUTED |

Final S0 and S1 closure incomplete; S2 explicitly NOT RUN. Certification
sufficiency **NOT SATISFIED**. Bootstrap's established R11 certification is
preserved historically, but the modified admission policy has **not** received
the required complete bootstrap regression; renewed validity is not claimed.

## Source accounting and preserved forward contract

Accepted counters: connectivity=0, annotation=0, neurotransmitter=0, metadata=0,
provenance=0, mapping=0, other registered=0; aggregate **0**.
R12 audit logs: prefix active=1; intermediate target active=1;
corrected active=3, blocked=2, ready=1, allocated=1;
complete run active=3, blocked=2, ready=1, allocated=1.
Total deliberate blocked probes **4**, all before content read. Tooling allowed:
Git metadata/source history, named source/plan inspection, guarded selected
pytest, temporary audit/JUnit/handshake writes, source/plan editing and diff check.
No accepted data reads or data permission changes.

Forward contract source/evidence files untouched; not freshly recertified after
the stop. R11 established: bounded route; production default unchanged; G1-G6
PASS; L3/L4 reject; one PreparedNetwork, one PreparedRuntime, two fresh states;
each two warmups and ten measured 20-ms calls, final 240 ms; total 24, maximum
12 consecutive. No continuous 480-ms trajectory, runtime reset/recreation,
B-from-A derivation or A/B coexistence; A released before B. Schedule once:
LEFT 42 sugar neurons at 100 Hz, RIGHT 0 Hz, seed 1555062870, impulse 68.75 mV,
horizon 240 ms, events 948, fingerprint
`6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a`.
Exact A/B windows, membrane/synaptic/refractory/pending/output/final-state replay
historically PASS. Resource wiring 600/30/1500 seconds and private/working-set
caps 8,589,934,592 bytes each unchanged. Historical forced timeout/memory,
containment/live-tree/no-orphan/no-retry evidence preserved, not R12 recertified.

Full-real preparations=0; real advances=0; real benchmark attempts=0;
future A019D attempt consumed No; GPU No; Arena=0; scientific experiments=0;
downloads=0; archive writes=0. Historical A013 behavior unchanged; Task016
unchanged; Task017 unchanged / NOT_ROBUST. Scientific semantics unchanged.

## Final repository state and next task

No success commit/push. Final local/origin/live remain
`60c900b0c8e5a02ea95efc7340fd190193edf7e9`. Staging and stash empty;
worktree dirty **28 expanded paths**, all scoped: initial 24 plus this plan,
modified A014 test, direct-control script, R12 controls. No unrelated paths.
Package 0.3.0; active tracked workflows 0; no tag/release/version mutation.
All prior records untouched. Final tracked diff check PASS.

Final classification: **A19C-R12-A014-REGRESSION-INCOMPLETE**.
No A19C-R12-A or A019C-FORWARD-HARNESS-SYNTHETICALLY-CERTIFIED issued.
Next task: separately authorized A014 replacement-control exit/topology
adjudication, including guarded workload-start proof for remaining modes,
then complete the deferred validation gates. A019D **not eligible or recommended**.
