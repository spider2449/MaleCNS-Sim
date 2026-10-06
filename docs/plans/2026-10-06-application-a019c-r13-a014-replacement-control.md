# Application A019C-R13: replacement-control adjudication

Authorization: `授權 A019C-R13`. Synthetic-only; no registered payload permission.
Root dynamically verified: D:/spider/working/MaleCNS-Sim.
Starting local HEAD = origin/master = live GitHub master =
`60c900b0c8e5a02ea95efc7340fd190193edf7e9`.

## Plan and inventory

1. Inventory and audit source/history; reproduce only replacement before edits.
2. Document E adjudication before correction; correct only its proven integration.
3. Run corrected replacement, complete A014, bootstrap, harness and fresh CLI in order.
4. Only after these pass, complete deferred admitted validation and manifest.
5. Stop at each specified failure gate; commit/push only on full R13-A.

Initial expanded dirty count 28; staging empty; stash empty; unrelated WIP No.
Exact paths are recorded in the final inventory below. Version 0.3.0; active
tracked workflows 0. All R2-R12 historical outcomes remain unchanged, including
`A19C-R12-A014-REGRESSION-INCOMPLETE`. R12 direct D2 is preserved: exact base
interpreter / -S / fixed script / purpose, 160 MiB allocation, root offender,
MEMORY_LIMIT, exit 1, empty Job, no orphan or retry. No evidence reopens it.

## Historical contract

Source: tests/test_application_a014.py; scripts/investigate_application_a014.py;
tracked A014 plan, process certification lines 101-105 and closure line 129.
Parameters: repeat 0,1 crossed with direct, launcher, child, replacement.
Replacement is spawn-and-parent-exit, not exec or a process identity mutation.
The virtualenv redirector launches a base interpreter running the parent code;
that parent spawns another virtualenv redirector/base-interpreter workload pair,
then sys.exit(0). Both pairs inherit the Job assigned before root resume.
Breakaway disabled; KILL_ON_JOB_CLOSE; inventory persists after parent exit.

| Mode | Root / workload / expected offender | Root exit |
|---|---|---|
| direct | base interpreter / same PID / same PID | 1 |
| launcher | venv redirector / base worker / worker | 1 |
| child | venv redirector / spawned worker / spawned worker | 1 |
| replacement | venv redirector / spawned worker after parent exits / spawned worker | 0 |

Exit 0 certifies the original parent completed the handoff and exited normally
before the contained replacement workload was terminated. The assertion reads
the original Popen root/redirector returncode, not the replacement victim's code,
supervisor Python exit, or pytest result. Classification remains MEMORY_LIMIT.
Original allocation is 167772160 bytes; cap 134217728; sampling 20 ms; timeout
10 s. Cleanup terminates Job with code 1 and requires empty inventory. No retries.

## Single pre-fix reproduction and adjudication

Unmodified repository code, temporary observational pytest plugin:
C:/TEMP/a019c-r13-capture.py. Guarded child entrypoint; activation=1;
absolute firewall PYTHONPATH; audit C:/TEMP/a019c-r13-prefix.jsonl.
Only test_tree_memory_enforcement[0-replacement], -q -x -s, ran: 1 failed.
Parent/supervisor PID 5748; root venv redirector PID 19064; its base worker
PID 18624. Root command was the historical -c spawn/sys.exit(0) string, rewritten
through mandatory guarded_child.py by the existing admission. No denial occurred.
No replacement child existed: Job inventory before cleanup [19064,18624].
Base worker private bytes reached 657444864 during firewall dependency startup;
working set 25030656. Offender 18624; aggregate private bytes 658309120;
MEMORY_LIMIT fired before guard ACTIVE, spawn, workload or allocation.
Allocation actually executed: 0 bytes of the intended bytearray. Audit contains
only supervisor ACTIVE. No payload probes ran; accepted registered reads all 0.
Root poll before cleanup None; TerminateJobObject(...,1) then root returncode 1;
stdout empty, inventory empty, orphans [], one attempt, no retry. The assertion
inspected the correct root; startup termination prevented its intended normal exit.
Individual base-worker exit was not captured with a retained handle; no invented
per-process exit or executable inspection is claimed. Its executable role follows
the established Windows venv redirector topology and source, rather than a live
image-name query. Missing replacement/workload PID is meaningful absence.

**E1 — STALE REPLACEMENT FIXTURE / ACTIVATION INTEGRATION.** Existing mandatory
venv admission accepts the intended topology. Guard startup exceeds the small
synthetic cap before handoff; no production enforcement error is demonstrated.
Tracked historical exit-0 semantics remain explicit, excluding E4. No new
admission is needed, excluding E2. Correction will be test-only handshake startup
integration, analogous to the established direct fixture, preserving real Job,
spawn-and-parent-exit, 160-MiB allocation, root exit 0, child offender, cap and
production supervisor. Guard installation/probes must finish before the fixture
hands the real Job to supervision. No generic executable or shell permission.

This adjudication was written before any fixture correction.

## Correction and corrected evidence

Only tests/test_application_a014.py and this new plan changed in R13.
Production files changed No; admission/firewall files changed No. The fixture
uses the already admitted venv interpreter and mandatory guarded entrypoint,
spawns a guarded synthetic workload, then sys.exit(0). The workload performs
replacement and descendant denied-path probes, signals ready, awaits release,
allocates the exact bytearray, signals allocated and sleeps. A bounded fixture
wait verifies Job membership, distinct workload PID, original root wait()==0,
then releases and verifies allocation before returning the real Job. Exceptions
close that Job; no retry. Historical non-firewall execution remains unchanged.
No new permission for generic executables, shell, alternate scripts/base
executables or wrong direct purpose. E2 R1-R10 are not applicable: no new seam.
The seven existing R12 positive/negative admission tests were rerun and passed.
Existing guarded venv workloads remain admitted as before, never data-privileged;
this is not a new exact-purpose admission claim for general venv Python scripts.

Corrected target command: `.venv/Scripts/python.exe
scripts/a019c_firewall/guarded_child.py -m pytest
tests/test_application_a014.py::test_tree_memory_enforcement[0-replacement]
-q -x --basetemp=C:/TEMP/a019c-r13-corrected-tests`.
Same guard environment; log C:/TEMP/a019c-r13-corrected.jsonl.
Result 1 passed in 1.04 s, pytest exit 0. Supervisor 6920, original root 9944,
original base parent 17764, replacement redirector 19736, workload/base child
13404, probe base child 15756. Parent records handoff child_pid=19736 then exits;
root wait verifies 0. Workload parent_pid=19736; its allocation 167772160 bytes.
Pre-supervision inventory [19736,13404] excludes original parent/root.
Offender 13404; private bytes 837730304, working set 209391616; MEMORY_LIMIT;
root exit 0; Job cleanup verified empty; orphans []; one attempt, no retry.
Payload probes by 13404 and 15756 blocked before read. Allocation occurred, but
the metric includes substantial guard overhead: this proves child offender and
allocation, not that allocation alone caused the threshold crossing.
Replacement/probe individual termination codes were not retained/measured;
root exit and empty live Job inventory are the actual cleanup evidence.

## Complete A014 and mandatory STOP

Command: guarded `-m pytest tests/test_application_a019c_r12_firewall.py
tests/test_application_a014.py -q -x --junitxml=C:/TEMP/a019c-r13-a014.xml
--basetemp=C:/TEMP/a019c-r13-a014-tests`.
Audit C:/TEMP/a019c-r13-a014.jsonl. **16 passed, 1 failed in 4.26 s**, exit 1.
Seven R12 controls, all eight tree-memory cases, and aggregate control PASS.
Replacement repeat 0: root 4200, parent 20036, replacement redirector 13976,
workload/offender 6928, descendant probe 13980; root 0; allocation 167772160.
Replacement repeat 1: root 18500, parent 17996, replacement redirector 19716,
workload/offender 19580, descendant probe 12136; root 0; allocation 167772160.
Both Job cleanup/no-orphan assertions pass; one attempt each; all four payload
probes blocked. Direct controls retain actual allocation/probe evidence twice.
Launcher and child cases pass historical assertions; their workload execution
was not separately established and is not promoted to new activation evidence.

Failure: `tests/test_application_a014.py::test_normal_exit`, expected NORMAL_EXIT,
observed MEMORY_LIMIT. This is a separate control, not the proven replacement
handoff integration defect. No diagnostic rerun, correction or chain-fix after
the mandatory gate. Accounting-failure and preparation-probe tests not reached.
**A19C-R13-A014-REGRESSION-INCOMPLETE**. Certification sufficiency not satisfied.
No bootstrap/harness/CLI/deferred execution, success commit or push.

## Final deterministic manifest

The exact per-node R11 manifest is incorporated without reclassification.
R13 overlays below; other prior PASS results are historical only, not fresh R13
certification. All required remaining S0/S1 nodes remain explicit deferred
NOT RUN; none is silently removed or reclassified S2 to obtain closure.

| Entry | Class | R13 disposition |
|---|---|---|
| R12 exact identity and six negative controls | S0 | 7 PASS |
| A014 direct repeats 0,1 | S1 | PASS, actual guarded allocation |
| A014 launcher/child repeats 0,1 | S1 | Historical assertions PASS; workload activation not independently proved |
| A014 replacement repeats 0,1 | S1 | PASS, handoff/allocation/offender/root 0 proved |
| A014 aggregate control | S1 | PASS |
| A014 normal exit | S1 | FAIL, MEMORY_LIMIT |
| A014 accounting failure | S1 | NOT RUN, fail-fast |
| A014 preparation probe | S0 | NOT RUN, fail-fast |
| Complete bootstrap 39 | S0 | NOT RUN; historical certification not renewed |
| A019C harness 35 | S0 | NOT RUN |
| Fresh contained CLI | S0 | NOT RUN |
| R11 exact admitted A013 nodes | S0/S1 | NOT RUN |
| A011 exact continuity/initial-state nodes and reference LIF/stateful | S0 | NOT RUN |
| Remaining R11 S0/S1 application nodes | S0/S1 | NOT RUN |
| Earlier suites affected by shared R13 helper | S0/S1 | No shared helper changed; no additional rerun |
| compileall | S1 | NOT RUN, gate stopped |
| git diff --check | S1 | PASS, tracked diff only |
| A003 test_selection_uses_stable_a002_digest_and_rejects_extra_fields | S2 | NOT RUN |
| A003 test_validate_and_run_requests_share_exact_spec_identity | S2 | NOT RUN |
| A003 test_result_events_and_backend_export_routes | S2 | NOT RUN |
| A018UJ prohibited data diff | S2 | J2 NOT RUN |
| A018UJ provenance reconstruction | S2 | NOT RUN |
| Default integrity checker | S2 | I2 NOT RUN |
| Unfiltered full pytest | S2 | NOT RUN, synthetic-only authorization; known S2 excluded |
| Build | S1 | B2 NOT RUN, preserved R10 disposition |
| Arena/real execution/tag/release/version mutation | N | NOT EXECUTED |
| Commit/push | N | NOT EXECUTED, success gate not reached |

Final S0/S1 incomplete; S2 explicitly NOT RUN; N outside scope. J2/I2/B2 unchanged.
No `FIREWALL_BOOTSTRAP_CERTIFIED` renewed validity or forward synthetic
certification issued. Historical R11 contract/evidence remains unchanged:
bounded route; production default unchanged; merge block 16384; fallback hard
stop; G1-G6; L3/L4 wrong-layer rejection; Network 1 / Runtime 1 / State 2;
A/B fresh with two warmups + ten measured 20-ms calls each; final 240 ms each;
24 calls, maximum 12 consecutive; no continuous 480 ms, reset, recreation,
B-from-A or coexistence; A released before B. These are not freshly rerun.
Historical schedule: LEFT sugar 42, 100 Hz; RIGHT 0; seed 1555062870;
impulse 68.75 mV; horizon 240 ms; 948 events; generated once; identical windows;
fingerprint 6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a.
Historical exact membrane/synaptic/refractory/pending/output/final-state/time
replay remains unmodified, not freshly certified. Historical timeout wiring
600/30/1500 s, private/working-set caps 8589934592, forced timeout/memory-stop
and containment evidence unchanged, not renewed. R13 A014 uses its distinct
128-MiB cap and validates contained tree cleanup as recorded above.

## Source accounting and final state

accepted_real_connectivity_reads=0
accepted_real_annotation_reads=0
accepted_real_neurotransmitter_reads=0
accepted_real_metadata_reads=0
accepted_real_provenance_reads=0
accepted_real_mapping_reads=0
accepted_other_registered_reads=0
Aggregate accepted registered reads=0. Firewall remains active throughout pytest
discovery and imports. Pre-fix child startup was stopped before ACTIVE and any
workload; no accepted registered content. Deliberate blocked probes: corrected
target 2, full A014 run 8, pre-fix 0, total 10. All before content read.
Permitted executable admissions: existing venv mandatory guarded children and
exact R12 direct base control; no R13 admission extension. Corrected target
involved root, spawned replacement and probe launches; complete A014 repeated
these plus existing admitted controls. Counts above are probe counts, not an
invented exhaustive native process-admission event counter.

Full-real preparations=0; real advances=0; benchmark attempts=0; future A019D
attempt consumed No; GPU No; Arena=0; scientific experiments=0; downloads=0;
archive writes=0. Historical A013 behavior unchanged; Task016 unchanged;
Task017 unchanged / NOT_ROBUST. Production preparation defaults and scientific
semantics unchanged. No tag, release or version mutation. Package 0.3.0;
active tracked workflows 0. HEAD/local/origin/live remain the starting SHA;
worktree dirty, 29 expanded paths; staging/stash empty. No commit/push.
Superseding status is incomplete R13 A014 validation, retaining the complete
R12 and earlier STOP chronology. A019D not eligible or recommended.
Exact next work: separately authorized A014 normal-exit guarded-startup
adjudication and remaining deferred validation; do not start automatically.

## Exact initial dirty paths
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
