# A019C-R15: A013 guarded-entrypoint adjudication

Authorization: `授權 A019C-R15`; synthetic-only. Root derived using
`git rev-parse --show-toplevel`. Starting local/origin/live master:
`60c900b0c8e5a02ea95efc7340fd190193edf7e9`. Initial expanded dirty paths: 30;
staging/stash empty; unrelated WIP No; version 0.3.0; active workflows 0.
Exact initial inventory is the R14 final inventory (30 paths), preserved unchanged.

Plan: inventory; static historical audit; single pre-fix reproduction; adjudicate
before correction; corrected target; complete A013; bootstrap; harness and fresh
CLI; remaining admitted manifest; compileall and diff check. Stop on first new
failure. Commit/push accumulated coherent WIP only after complete R15-A.
All previous STOP records remain unchanged, including
`A19C-R14-DEFERRED-VALIDATION-BLOCKER`. R14 F1/6/19/39/35/CLI PASS and A013
16 PASS + 1 FAIL remain historical evidence, not reclassified outcomes.

## Historical contract and adjudication before correction

Exact node: `tests/test_application_a013.py::test_native_watchdog_can_terminate_actual_redirected_python`.
Introduction `4e2e10c` and tracked A013 report's instrumentation-correction section
define termination of the actual redirected Python print/sleep worker following
the real benchmark's launcher-PID monitoring defect. This differs from A014's
tree aggregate memory controls. No automatic cap/timeout trigger is exercised:
the test binds WindowsMemory to a consumed self-reported PID, snapshots nonzero
working set, directly calls native TerminateProcess(exit 1), waits at most 5 s,
and closes the native handle, with finally termination if needed. One launch;
no retry. Workload sleeps 10 s. No Job Object in this historical fixture.

Historical argv: `[sys.executable, '-u', '-c',
'import os,time; print(os.getpid(),flush=True); time.sleep(10)']`.
Executable is the repository virtualenv redirector; actual worker is its base
interpreter. stdout is PIPE, text=True; stderr/environment otherwise inherited.
The parent consumes exactly one PID line before binding the monitor.
The tracked code explicitly flushes that line. No other output is consumed.
Tracked source/report records no independent rationale for `-u`, no standard-flag
coverage requirement, and no evidence that this option itself defines the control.
It supplies unbuffered launch behavior; preserve that behavior rather than guess
it away. Removing it alone would retain the explicitly flushed PID synchronization,
but is not the selected correction. No buffering/timing weakening is needed.

Current guarded_command inserts CHILD_ENTRY before all payload tokens.
mandatory_child requires exact resolved sys.executable, exact CHILD_ENTRY position,
then -c/-m or a non-option script. The transformed argv's third token is -u,
so parent subprocess audit rejects `child lacks mandatory firewall entrypoint`
before Windows CreateProcess. Neither child guard nor workload starts; native
watchdog is not armed. Normal guarded -c and R14 print controls lack that option;
R13 additionally has replacement handoff topology; R12 uses a distinct exact base
-S/purpose contract. Those topology differences are not a simple flag difference.

Single unmodified reproduction: guarded pytest -q -x with observational plugin
`C:/TEMP/a019c_r15_capture.py`; 1 FAIL, exit 1; audit
`C:/TEMP/a019c-r15-prefix.jsonl`. Raw and parsed argv and parent activation recorded.
No child PID exists; readiness/output, termination and cleanup are not claimed
as successful watchdog execution. Parent guard ACTIVE; activation=1.

**G1 — STALE A013 FIXTURE / ARGV INTEGRATION.** Preserve actual redirector,
unbuffered IO, explicit PID flush, workload, monitor, kill, cleanup and no retry.
Correction only in this fixture: set PYTHONUNBUFFERED=1 in a copied child environment
and use the existing -c form. This is not G4 removal of unbuffered semantics,
G2 admission broadening, or G3 production defect. Add observations/assertions
for active child guard, actual base image, workload start, native kill and exit.
Production/shared admission changes: No. Generic flags allowed: No.
G2 U1-U10 are not applicable; existing policy remains unchanged. Full A014 rerun
is not mandatory because neither shared admission nor A014 fixture changes.

J2/I2/B2 remain NOT RUN; unfiltered full pytest NOT RUN; all S2 remain NOT RUN.
No full-real preparation/advance/benchmark, GPU, Arena, experiment, download,
archive write, Task016/017 or historical scientific behavior change authorized.

## Execution results

All Python gates used `.venv/Scripts/python.exe scripts/a019c_firewall/guarded_child.py`,
activation=1, absolute firewall PYTHONPATH, distinct audit files, `-q -x`, unique
basetemp and JUnit paths. No discovery/import ran without the task-wide guard.

| Gate | R15 result |
|---|---|
| Single pre-fix target | 1 FAIL, 1.19 s, exit 1; parent-side rejection |
| Corrected single target | 1 PASS, 1.42 s |
| Complete admitted A013 | 17 PASS, 1.59 s; no remaining failure |
| Affected A014 | Not required/not rerun; no shared admission change; R14 19 PASS retained as historical |
| Complete bootstrap R5/R4/R3/R2 | 39 PASS, 5.41 s; FIREWALL_BOOTSTRAP_CERTIFIED renewed |
| A019C harness | 35 PASS, 7.60 s |
| Fresh contained CLI | exit 0, A19C-A; C:/TEMP/a019c-r15-forward-evidence.json |
| Stateful/A011/reference LIF | 27 PASS, 1.37 s |
| Application manifest selection | 2 PASS, 1 FAIL, 6.05 s; fail-fast |
| compileall | NOT RUN after mandatory STOP |
| Final git diff --check | NOT RUN after mandatory STOP |

Prefix parent PID 13084, executable
`D:\spider\working\MaleCNS-Sim\.venv\Scripts\python.exe`, base executable
`D:\uv\cpython-3.14-windows-x86_64-none\python.exe`.
Exact raw/transformed/parsed argv is logged in C:/TEMP/a019c-r15-prefix.jsonl;
transformed form is that executable + absolute guarded_child.py + -u + -c +
the exact historical code above. Rejection is token position/option, not executable
identity, parser ambiguity, -c, activation or payload. Parent ACTIVE/activation 1;
no launcher/worker PID, no child guard, no workload/readiness, no watchdog arming.

Corrected single: parent 3436, venv launcher 540, actual worker 17892.
Windows QueryFullProcessImageNameW reports
`D:\uv\cpython-3.14.0-windows-x86_64-none\python.exe`, which resolves equal to
sys._base_executable (the unversioned alias). Child ACTIVE -> workload-start with
PYTHONUNBUFFERED=1 -> explicitly flushed PID consumed -> native handle/snapshot
-> watchdog armed -> TerminateProcess -> worker exit 1 and launcher exit 1.
Native GetExitCodeProcess verifies the retained worker handle has exited; monitor
handle and stdout close in finally. No retry, one launch; no descendant spawn.
Complete A013 independently repeats this execution: parent 18280, launcher 19312,
worker 8156, both exits 1. Post-run metadata CIM scan found none of recorded task
PIDs alive and no Python command containing the R15 task markers. This is scoped
observed no-orphan evidence, not a global process enumeration certification.

Only R15 code change: tests/test_application_a013.py fixture. Production benchmark,
production accounting, preparation default, scientific semantics and shared guard
are unchanged. New assertions record actual base image and exact native/launcher
exit. Unbuffered startup setting is local to this child environment. -u remains
rejected by the unchanged grammar; arbitrary Python options/order/executables and
shells are not admitted. G2-specific alternative-script/purpose/duplicate/reorder
controls are N/A; bootstrap retains executable/shell/activation/payload/descendant
negative controls. Child/descendant registered probes block before content read.

Stateful command selects only A011::test_exact_continuity,
A011::test_initial_state_and_identity and tests/test_task005.py; no Arena cases.
Application selection is the exact R10 S0/S1 node list for A008 through A002,
saved C:/TEMP/a019c-r15-application-nodes.txt. A008's two tests PASS. Next node
`tests/test_application_a007c.py::test_synthetic_production_api_and_assets` FAILS
at line 51: `["node", tests/js/application_a007c.cjs, temporary synthetic
evidence.json, src/malecns_sim/application/static]`.
guarded_command raises `SourceAccessDenied('unsupported A019 child executable')`
before Popen/Node launch. Python synthetic HTTP assertions ran; Node asset
assertions did not. Teardown completed. This S1 remains FAIL, not S2/N/PASS.
No separate Node admission correction or retry was attempted. Remaining selected
application and historical Git/Node S1 entries remain NOT RUN.

**A19C-R15-DEFERRED-VALIDATION-BLOCKER.** A013 G1 adjudicated and passing, but
complete S0/S1 closure is not achieved. Forward certification withheld;
A019C-FORWARD-HARNESS-SYNTHETICALLY-CERTIFIED not issued. Certification
sufficiency NOT SATISFIED. No success commit/push. All previous chronology intact.
Exact next bounded work: separately authorized A007C Node synthetic-validation
admission adjudication and remaining manifest completion. A019D not eligible,
not recommended and not executed.

## Forward contract freshly verified, without overall certification

CLI A19C-A: explicit A015/A016/A017/A018/A018T/A018U/A018UJ bounded route;
merge block 16,384; fallback null; G1-G6 true. Harness asserts hard fallback stop
and L3/L4 wrong-layer rejection. Production default unchanged. Counts: one
PreparedNetwork, one PreparedRuntime, two fresh SimulationStates; A released
before B, no coexistence, no B derivation from A, no runtime reset/recreation.
Each state has two warmups and ten measured 20-ms advances, final 240 ms.
24 calls, max consecutive 12/state; no continuous 480-ms trajectory.
Exact membrane/synaptic/refractory/pending/delayed/output/final state/time replay.

Schedule generated once: LEFT sugar 42 neurons, 100 Hz; RIGHT 0 Hz;
seed 1555062870; impulse 68.75 mV; horizon 240 ms; 948 events;
fingerprint 6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a.
A/B windows identical. Limits 600/30/1500 s (prepare/advance/worker), private and
working-set caps each 8,589,934,592. Forced timeout/memory-stop, containment,
live-tree cleanup, no orphan/no retry PASS in harness/bootstrap. CLI one launch,
Windows Job Object, orphans []; 170 samples. Sampled private peak 736075776,
working set 115675136; no claim of continuous peaks or full-real feasibility.
CLI source_access_started=true means synthetic route entry only:
synthetic_source_accesses=1, full_real_source_accesses=0, attempt_count=0.

## Accounting, exclusions and final custody

All seven accepted counters are 0: accepted_real_connectivity_reads,
accepted_real_annotation_reads, accepted_real_neurotransmitter_reads,
accepted_real_metadata_reads, accepted_real_provenance_reads,
accepted_real_mapping_reads, accepted_other_registered_reads. Aggregate 0.
This is fail-closed task-wide guarded execution accounting, not independent
native accepted-byte telemetry. R15 audit files contain 26 ACTIVE, 34 blocked,
two live_tree_cleanup and three contained_cleanup records. Bootstrap only has
blocked records: 33 registered-path probes plus one corrupt-policy sentinel.
Categories: connectivity 8, annotation 4, neurotransmitter 4, metadata 4,
provenance 5, mapping 4, other 5 (including the sentinel). Deliberate blocked
registered probes=33; policy probe=1; no accepted read is inferred from a block.
Permitted A013 form: exact current venv + guarded_child.py + -c fixture, copied
environment with PYTHONUNBUFFERED=1. Executed twice (target and full suite);
historical -u form rejected once, no retry within either semantic execution.

J2 prohibited data diff, A018UJ provenance reconstruction and I2 default integrity
remain S2 NOT RUN. B2 build remains NOT RUN. Three known A003 payload-backed
nodes remain S2 NOT RUN. Unfiltered full pytest NOT RUN: synthetic-only
authorization, known S2 real-data tests excluded. No exclusion is called PASS.
All S2 historical evidence remains preserved, not freshly recertified.

Execution firewall: full-real preparations 0; real advances 0; real benchmark
attempts 0; A019D attempt consumed No; GPU No; Arena/scientific experiments/
downloads/archive writes 0. Historical A013 scientific behavior unchanged;
Task016 unchanged; Task017 unchanged / NOT_ROBUST. No tag/release/version mutation.

Final local/origin/live master still 60c900b0c8e5a02ea95efc7340fd190193edf7e9.
No new commit; push NOT RUN. Final expanded dirty paths 32: initial 30 plus
modified A013 test and this R15 plan. Staging/stash empty; unrelated WIP No.
Version 0.3.0; active tracked workflows 0. No reset/clean/restore/stash/discard.
R15 changed no earlier recovery record. Final diff gate intentionally NOT RUN.

Audit/JUnit/result artifacts under C:/TEMP are local validation evidence and may
not persist on another machine; this tracked-candidate report records material
results and boundary limitations. Final per-node manifest follows.

## Exact initial inventory

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
?? docs/plans/2026-10-06-application-a019c-r14-a014-normal-exit.md
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

## Final per-node manifest

S0/S1 closure INCOMPLETE; S2 NOT RUN; N unchanged. Fresh R15 results override only current status. R10/R11/R14 outcomes remain historical.

| Node | Class | Final status | Evidence |
|---|---|---|---|
| `tests/test_application_a019c_r5_firewall.py::test_canonical_serialization` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r5_firewall.py::test_false_positive_rejected` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r5_firewall.py::test_malformed_rejected` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r5_firewall.py::test_actual_windows_audit_serialization` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r5_firewall.py::test_actual_worker_bypass_rejected` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r5_firewall.py::test_script_path_with_spaces` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r5_firewall.py::test_contained_actual_worker_startup` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r5_firewall.py::test_live_contained_descendant_cleanup` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r4_firewall.py::test_parent_native_control_and_categories` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r4_firewall.py::test_required_child_rejects_before_workload` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r4_firewall.py::test_normal_public_native_child` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r4_firewall.py::test_actual_worker_startup` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r4_firewall.py::test_inherited_activation_removed_parent_rejects` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r3_firewall.py::test_01_valid_native_synthetic_control` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r3_firewall.py::test_02_native_registered_source_denied_before_constructor` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r3_firewall.py::test_03_python_child_native_guard` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r3_firewall.py::test_04_missing_inherited_guard_fails_closed` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r2_firewall.py::test_blocked_before_content` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r2_firewall.py::test_generated_and_temp_and_source_allowed` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r2_firewall.py::test_subprocess_guard` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r2_firewall.py::test_child_cannot_drop_guard` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c_r2_firewall.py::test_native_reader_denies_synthetic_sentinel` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_full_structure_route_lifetime_replay_and_defaults` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_each_gate_stops_before_runtime_one_preparation` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_cross_layer_rejected` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_fallback_hard_stop` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_induced_failure_no_retry` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_exact_resource_limits` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_contained_tree_forced_stops_no_orphan` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_synthetic_cli_contained_success` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_synthetic_source_guard_before_access` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_timing_structure_and_historical_default` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_completed_preparation_deadline_before_runtime` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_completed_call_deadline_no_retry` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_watchdog_instrumentation_failure_terminates_tree` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_contract_schema_matches_success_evidence` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019c.py::test_watchdog_child_memory_stop_aggregate_and_cleanup` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a019a.py::test_frozen_two_state_contract` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a019a.py::test_historical_schedule_from_tracked_metadata_only` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a019a.py::test_b_starts_fresh_after_a_released_using_same_runtime_and_graph` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a019a.py::test_a019a_checks_have_no_real_execution_and_preserve_defaults` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a018uj.py::test_independent_frozen_artifact_reconstruction_and_provenance` | S2 | NOT RUN | Prohibited registered payload validation; historical PASS not recertified |
| `tests/test_application_a018uj.py::test_each_mandatory_layer_mismatch_fails` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a018uj.py::test_correct_tuple_and_cross_layer_rejection` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a018uj.py::test_ambiguous_legacy_fields_rejected` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a018uj.py::test_no_real_execution_and_scientific_default_unchanged` | S2 | NOT RUN | Prohibited registered payload validation; historical PASS not recertified |
| `tests/test_application_a018ui.py::test_historical_identity_layer_reconstruction` | S1 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a018ui.py::test_historical_current_components_exact` | S1 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a018ui.py::test_metadata_and_diagnostic_bytes` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a018ui.py::test_effective_digest_field_order` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a018ui.py::test_historical_preparation_and_committed_fingerprints` | S1 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a018ui.py::test_production_default_and_frozen_expectation_unchanged` | S1 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a018ur.py::test_success_exact_identity_no_advance_default_restored` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a018ur.py::test_identity_mismatch_stops_and_cleans` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a018ur.py::test_failure_cleanup_and_fallback_prevented` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a018ur.py::test_exact_frozen_constants_and_no_execution_entrypoints` | S0 | PASS (historical R10) | Preserved earlier selected results; no fresh R15 rerun |
| `tests/test_application_a018ur.py::test_supervisor_time_failure_cleans_without_retry` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a018ur.py::test_supervisor_success_boundary_handshake` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a018u.py::test_instrumented_oracle_exact` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018u.py::test_missing_metadata_and_policy_contract` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018u.py::test_large_safe_exact` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018u.py::test_large_integer_identity` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018u.py::test_default_has_no_probe` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018u.py::test_synthetic_bounds` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018t.py::test_exact_oracle_ownership_release` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018t.py::test_prepared_scientific_oracle` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018t.py::test_compaction_releases_capacity` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018t.py::test_many_small_schedule_determinism` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018t.py::test_partition_and_stage_release` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018t.py::test_overflow_reference_fallback` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018t.py::test_production_default` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018t.py::test_closed_boundaries` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018t.py::test_large_ids_and_invalid_block` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018t.py::test_equal_key_on_either_slice_endpoint` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018t.py::test_seeded_partition_block_invariance` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018s.py::test_exact_oracle_ownership_release` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018s.py::test_prepared_scientific_oracle` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018s.py::test_compaction_releases_capacity` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018s.py::test_many_small_schedule_determinism` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018s.py::test_partition_and_stage_release` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018s.py::test_overflow_reference_fallback` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018s.py::test_production_default` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018.py::test_runs_exact_deterministic_and_lifetime` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018.py::test_downstream_partition_exact` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018.py::test_overflow_rejection` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018.py::test_completed_stage_inputs_reclaimable` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018.py::test_overflow_loader_fallback` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018.py::test_schedule_partition_invariance` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018.py::test_fan_in_composition_invariance` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a018.py::test_production_default` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a017.py::test_exact_downstream` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a017.py::test_integer_domain_and_merge` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a017.py::test_lifetime_bounds_and_no_partial_threshold` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a017.py::test_invalid_excluded_upstream` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a017.py::test_scale_exact` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a017.py::test_production_dispatch_unchanged` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a017.py::test_overflow_oracle_fallback` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a017.py::test_high_cardinality_exact` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a016.py::test_boundaries_exact` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a016.py::test_invalid_boundary` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a016.py::test_reader_projection_admission_lifetime` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a016.py::test_v1_rejected` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a016.py::test_scale_exact` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a016.py::test_masks_released_numeric_ownership` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a016.py::test_noninteger_schema_rejected` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a015.py::test_exact_adversarial` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a015.py::test_high_exclusion_scale` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a015.py::test_membership_exact` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a015.py::test_authoritative_membership_and_no_identity_collapse` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a015.py::test_invalid_excluded_rows_rejected` | S0 | PASS (historical R11) | Preserved earlier deferred-gate results; no fresh R15 rerun |
| `tests/test_application_a014.py::test_tree_memory_enforcement` | S1 | PASS (historical R14) | 19 controls; not rerun, no shared changes |
| `tests/test_application_a014.py::test_aggregate_limit_without_individual_offender` | S1 | PASS (historical R14) | 19 controls; not rerun, no shared changes |
| `tests/test_application_a014.py::test_normal_exit` | S1 | PASS (historical R14) | 19 controls; not rerun, no shared changes |
| `tests/test_application_a014.py::test_accounting_failure_stops_tree` | S1 | PASS (historical R14) | 19 controls; not rerun, no shared changes |
| `tests/test_application_a014.py::test_instrumentation_opt_in_and_exact_identity` | S0 | PASS (historical R14) | 19 controls; not rerun, no shared changes |
| `tests/test_application_a013.py::test_limits_and_cpu_only` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a013.py::test_one_preparation` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a013.py::test_watchdog_stops` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a013.py::test_percentiles_and_warmup_exclusion` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a013.py::test_schedule_is_complete_grid_slices_and_reused` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a013.py::test_two_fresh_states_exact_twenty_four_advances_and_replay` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a013.py::test_mismatch_fails_at_first_component` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a013.py::test_canonical_digest_exact_and_endian_stable` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a013.py::test_pending_guard` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a013.py::test_no_download_arena_gpu_or_import_execution` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a013.py::test_refuse_existing_output` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a013.py::test_watchdog_binds_worker_not_launcher` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a013.py::test_native_watchdog_can_terminate_actual_redirected_python` | S1 | PASS | Fresh R15 JUnit |
| `tests/test_application_a011.py::test_exact_continuity` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a011.py::test_initial_state_and_identity` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a011.py::test_clocks_controls_reset_replay` | N | NOT RUN | Arena-specific scope excluded |
| `tests/test_application_a011.py::test_encoder_decoder_bounds_and_invalid_contracts` | N | NOT RUN | Arena-specific scope excluded |
| `tests/test_application_a011.py::test_synthetic_visible_response_and_intervention` | N | NOT RUN | Arena-specific scope excluded |
| `tests/test_application_a011.py::test_render_speed_cannot_change_backend` | N | NOT RUN | Arena-specific scope excluded |
| `tests/test_application_a011.py::test_http_ui_assets_and_commands` | N | NOT RUN | Arena-specific scope excluded |
| `tests/test_application_a008.py::test_reproducibility_contracts_and_packaged_assets` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a008.py::test_application_docs_are_portable_and_do_not_embed_session_urls` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_application_a007c.py::test_synthetic_production_api_and_assets` | S1 | FAIL | Fresh R15 JUnit |
| `tests/test_application_a007c.py::test_authoritative_backend_firewall_and_packaging` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_spec_serialization_identity_and_no_verdict` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_invalid_variant_allowlist` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_cross_variant_event_schedule` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_full_sweep_and_retention_stress` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_exact_reuse_and_mixed_provenance` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_cancel_preserves_completed_evidence` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_stop_on_failure` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_mixed_child_reuse_after_cancellation` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_parent_byte_bound_preserves_earlier_evidence` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_identity_and_graph_mismatch_rejected` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_session_host_origin_and_synthetic_api` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_cpu_startup_cuda_lazy` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_schedule_gap_stops_before_execution` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_all_children_reused_without_execution` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_cancel_before_first_child` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_child_capacity_and_parent_limits` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007b.py::test_strict_request_contract` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_exact_variant_contract` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_reference_and_weight_coupling` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_allowlisted_sign_policy` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_invalid_preparation` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_nonfinite_parameters` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_reject_unbounded_client_input` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_true_preparation_and_execution` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_ordinary_reference_bytes_and_known_certified_identities` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_same_variant_pairing` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_cross_variant_rejected` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_sixteen_children_survive_recent_eviction` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_parent_byte_limit_and_snapshot` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_no_historical_runner_dependency` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_cuda_receives_equivalent_configuration` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_variant_cuda_unavailable_is_explicit` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_closed_session_cannot_admit_parent` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_frozen_preset_digest` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_parent_child_capacity` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a007a.py::test_derived_input_must_remain_finite` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a006r.py::test_visible_run_transitions` | S1 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a006.py::test_pair_metrics_digest_and_zero_baseline` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a006.py::test_nonzero_deltas_and_deterministic_identity` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a006.py::test_mismatch_rejected` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a006.py::test_schedule_and_incomplete_rejected` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a006.py::test_union_playback_and_recorded_zero` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a006.py::test_comparison_api_session_and_backend_export` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a005.py::test_post_update_spike_time_grid` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a005.py::test_sparse_payload_identity_digest_and_no_fabricated_events` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a005.py::test_deterministic_raster_order` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a005.py::test_payload_rejects_nonfinite_trace_and_size_cap` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a005.py::test_playback_endpoint_session_and_completion_gate` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a004.py::test_long_identity_layout_has_shared_wrap_rule` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a004.py::test_view_determinism_identity_and_cap` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a004.py::test_target_and_combined_context` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a004.py::test_rejects_unbounded_or_unknown_filter` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a004.py::test_subgraph_route_bounds_session_failure_and_pending` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a003.py::test_loopback_catalog_security_and_ui` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a003.py::test_previous_process_token_is_rejected` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a003.py::test_history_limit_is_fixed` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields` | S2 | NOT RUN | Prohibited registered payload validation; historical PASS not recertified |
| `tests/test_application_a003.py::test_validate_and_run_requests_share_exact_spec_identity` | S2 | NOT RUN | Prohibited registered payload validation; historical PASS not recertified |
| `tests/test_application_a003.py::test_manager_retains_safe_failure` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a003.py::test_manager_evicts_oldest_completed_job` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a003.py::test_result_events_and_backend_export_routes` | S2 | NOT RUN | Prohibited registered payload validation; historical PASS not recertified |
| `tests/test_application_a002.py::test_spec_validation_and_canonical_identity` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a002.py::test_final_grid_step_spike_is_valid` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a002.py::test_spike_outside_engine_grid_is_rejected` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a002.py::test_nonfinite_spike_step_is_rejected` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a002.py::test_equal_timestep_spikes_have_deterministic_neuron_order` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a002.py::test_invalid_top_level` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a002.py::test_invalid_stimulus_and_finite_values` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a002.py::test_state_events_and_no_fake_progress` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a002.py::test_comparison_spikes_and_robustness_contract` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a002.py::test_optional_git_provenance` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a002.py::test_cpu_only_import_and_cuda_unavailable` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_application_a002.py::test_non_scientific_synthetic_engine_integration` | S0 | NOT RUN | Remaining validation deferred; historical records preserved |
| `tests/test_task005.py::test_reference_parameters_are_explicit_and_grid_is_exact` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_linear_update_matches_analytical_solution` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_resting_neuron_and_synaptic_decay` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_positive_and_negative_direct_impulses_have_expected_polarity` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_threshold_reset_and_g_reset` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_refractory_blocks_input_until_strictly_after_2_2_ms` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_incoming_event_during_refractory_is_ignored_and_poisson_targets_can_opt_out` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_exact_delay_and_signed_sparse_propagation` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_self_edge_and_two_neuron_inhibitory_edge_are_supported` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_multiple_and_simultaneous_events_sum_deterministically` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_unresolved_edges_are_excluded_and_anatomy_is_unchanged` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_explicit_stimulus_is_sorted_reproducible_and_validates_ids_and_grid` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_seeded_poisson_is_reproducible_and_uses_reference_scaling` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_silencing_disables_outgoing_only` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_fingerprints_and_result_digest_are_deterministic_and_identity_sensitive` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_effective_weight_preserves_anatomical_count_boundary` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_effective_inhibitory_weight_uses_presynaptic_sign` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_two_neuron_chain_keeps_spike_output_compact` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_simulation_reports_identity_metadata` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_parameter_identity_changes_simulation_configuration` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_duration_must_be_on_the_discrete_clock` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_duplicate_schedule_times_are_additive` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_poisson_rejects_more_than_one_expected_event_per_step` | S0 | PASS | Fresh R15 JUnit |
| `tests/test_task005.py::test_trace_requires_an_explicit_small_subset` | S0 | PASS | Fresh R15 JUnit |

Additional final tooling entries: bootstrap S1 39 PASS; A019C S0/S1 35 PASS; fresh CLI S1 PASS; compileall S1 NOT RUN after STOP; final diff check S1 NOT RUN after STOP; metadata/source inspection S1 PASS; full pytest S2 NOT RUN; default integrity S2 I2 NOT RUN; build B2 NOT RUN; J2 S2 NOT RUN. Historical Git/Node S1 entries remain required and incomplete, not reclassified.
