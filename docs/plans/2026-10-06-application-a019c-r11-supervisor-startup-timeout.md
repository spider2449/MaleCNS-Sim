# Application A019C-R11: supervisor startup-timeout adjudication

Authorization: `授權 A019C-R11`. Synthetic-only; no registered payload access,
real preparation/advance/benchmark, GPU, Arena, experiment, download or archive write.
Root derived by `git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`.

## Plan

1. Inventory accumulated WIP and verify committed identities.
2. Audit historical supervisor, fixture and mandatory child activation statically.
3. Reproduce only the failing synthetic test under the existing firewall.
4. Adjudicate and correct the fixture narrowly; preserve production semantics.
5. Run A018UR, bootstrap, A019C and fresh synthetic CLI gates.
6. Resume the R10 S0/S1 manifest, stopping on its first failure.
7. Record the closed or blocked manifest; commit/push only if certification succeeds.

## Inventory and history

Starting local HEAD, origin/master and live GitHub master:
`60c900b0c8e5a02ea95efc7340fd190193edf7e9`.
Initial inventory: 22 expanded untracked files, 20 short-status entries because
the firewall directory is collapsed. Staging and stash empty. No unrelated WIP.
The exact expanded inventory is R10's 21 initial paths plus its own report:
`docs/plans/2026-10-06-application-a019c-r10-validation-manifest-closure.md`.
No tracked file was initially dirty. No reset/restore/clean/stash/discard.
Package version 0.3.0; active tracked workflows 0.

Historical records remain unchanged: A19C-F, A19C-R-D, A19C-R2-C, A19C-R3-D,
A19C-R4-CHILD-FAIL-CLOSED-INCOMPLETE, A19C-R5-HARNESS-WORKER-COVERAGE-INCOMPLETE,
A19C-R6-CONTAINED-WORKER-CLEANUP-INCOMPLETE, A19C-R7-FIREWALL-METHOD-INVALID,
A19C-R8-B, A19C-R9-B, A19C-R10-OTHER-VALIDATION-BLOCKER.

## Static contract and historical intent

Exact failing node:
`tests/test_application_a018ur.py::test_supervisor_time_failure_cleans_without_retry`.
Historical source at `0fee2dfdddbfaac37bb5970ab6b73c3fbcc686e4` confirms the
fixture sets PREPARATION_CAP=0.15, launches Python `-c`, emits prepare_start with
the worker perf-counter timestamp, sleeps five seconds, and asserts TIME-LIMIT,
attempts=0 and orphans=[]. Its purpose is preparation timeout after entry,
contained cleanup and no retry; not a guard-bootstrap performance requirement.

Production `scripts/certify_application_a018ur.py::supervise` constructs a real
ProcessJob, starts its reader, initializes PREPARATION-ERROR and starts a startup
clock. Receiving prepare_start sets preparation_start and phase_start from
started_ns. Expiry maps to TIME-LIMIT only when preparation_start exists;
otherwise PREPARATION-ERROR. Exceptions also map to PREPARATION-ERROR;
invalid_output does likewise. prepare_only maps genuine exceptions separately.
prepare_start is required for this interrupted preparation-timeout branch.
Worker prepare_only emits it before preparation. No production contract changed.

The firewall's Popen wrapper converts the fixture argv to the exact mandatory
`scripts/a019c_firewall/guarded_child.py -c` entrypoint. Parent argv audit admits
that path, and child verifies activation=1 and ACTIVE before exec. sitecustomize
installs guard including Arrow imports first. Missing/corrupt activation remains
child-side fail-closed; bypass remains parent-rejected.

## Pre-fix reproduction

Environment: MALECNS_A019C_R2_FIREWALL=1; absolute firewall PYTHONPATH;
MALECNS_A019C_R2_LOG=C:/TEMP/a019c-r11-prefix.jsonl.
Command: `.venv/Scripts/python.exe scripts/a019c_firewall/guarded_child.py -m pytest tests/test_application_a018ur.py::test_supervisor_time_failure_cleans_without_retry -q -x --basetemp=C:/TEMP/a019c-r11-prefix-tests`.
Exit 1; 1 failed in 1.34 s. Saved result: PREPARATION-ERROR, events=[], attempts=0,
orphans=[], terminated child exit 1. Contained child PID 15812 exists in samples.
Activation inherited and valid in parent; no child ACTIVE completion record before
termination. No prepare_start, success or result event; no startup exception or
invalid_output recorded. The first observed failure is startup-clock expiry,
not missing activation. Guard completion in that killed child is not claimed.
Execution stopped for analysis before correction.

## Adjudication and exact correction

**C1 — TEST/HARNESS ACTIVATION INTEGRATION STALE.** The old 150-ms fixture startup
assumption includes new mandatory guard initialization before its intended
preparation boundary. Valid activation is inherited automatically, but it cannot
finish in the fixture's pre-event window. This is not a production classification
defect or evidence that historical TIME-LIMIT is obsolete.

Only `tests/test_application_a018ur.py` changed. The timeout fixture wraps the
existing real ProcessJob constructor with a synthetic ready/release handshake.
The child asserts ACTIVE when firewall activation is present, writes a temporary
ready marker, and waits for release before emitting prepare_start and sleeping.
The fixture waits at most ten seconds for readiness, closes the job on readiness
failure, then returns the same contained job to the unchanged supervisor.
The readiness limit is fixture orchestration, not a production resource limit.
The 0.15-second injected preparation cap and five-second stall are unchanged.
No mandatory activation bypass, allowlist change, guard disablement or production
edit. No fake event or classification is inserted. Assertions additionally require
exact events=[prepare_start], interrupted duration >=0.15 and terminated exit.

## Targeted gates

Corrected single node: 1 passed in 1.47 s, exit 0.
Audit C:/TEMP/a019c-r11-target.jsonl records ACTIVE for parent and child PID 4924.
Post-fix sequence: legitimate contained child -> active guard -> fixture ready
-> workload release -> prepare_start -> stall -> TIME-LIMIT -> job cleanup.
No success/result event; no orphan; attempts=0. TIME-LIMIT and PREPARATION-ERROR
semantics unchanged. Real ProcessJob cleanup remains in use.

Full A018UR suite: **8 passed in 2.30 s**. Includes genuine invalid-input
PREPARATION-ERROR, timeout, cleanup/no-retry and successful boundary handshake.
Bootstrap: **39 passed in 5.28 s**. Valid activation, missing/corrupt activation,
bypass rejection and live contained cleanup controls PASS. Certification remains
FIREWALL_BOOTSTRAP_CERTIFIED; no bootstrap source changes.
A019C harness: **35 passed in 7.42 s**.
Fresh guarded CLI: `scripts/benchmark_application_a019.py --synthetic --output C:/TEMP/a019c-r11-forward-evidence.json`, exit 0, A19C-A.
JUnit files: C:/TEMP/a019c-r11-a018ur.xml, a019c-r11-bootstrap.xml,
a019c-r11-harness.xml. Separate audit logs use the corresponding names.

## Frozen forward contract retained

Harness path scripts/benchmark_application_a019.py; explicit bounded route;
production default unchanged; merge block 16,384; fallback hard stop;
G1-G6 and L3/L4 rejection PASS in 35-test suite. One PreparedNetwork, one
PreparedRuntime, two fresh SimulationStates. Each state: two warmups plus ten
measured calls at 20 ms, final 240 ms. Total 24, max consecutive 12/state.
No runtime reset/recreation, B derivation from A, continuous 480-ms trajectory
or A/B coexistence. A released before B. Exact state/pending/output replay;
timing boundaries retained.
Schedule once: LEFT sugar, 42 neurons, 100 Hz; RIGHT unstimulated, 0 Hz;
seed 1555062870; impulse 68.75 mV; horizon 240 ms; events 948;
fingerprint `6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a`.
A/B windows identical. Preparation/advance/worker timeouts 600/30/1500 s;
private and working-set caps each 8,589,934,592. Forced timeout, memory-stop,
containment, live-tree cleanup, no-orphan and no-retry controls PASS.

## Preserved exclusions and execution boundary

J2 A018UJ data-diff test NOT RUN; I2 integrity NOT RUN; B2 build NOT RUN.
No contrary R11 evidence reopens them. Both A018UJ S2 tests, three known A003
payload-backed tests, default integrity checker and unfiltered pytest remain
NOT RUN. Historical PASS evidence and all R10 dispositions remain unchanged.
Full pytest: NOT RUN — synthetic-only authorization; known S2 real-data tests excluded.
Real preparations/advances/benchmarks=0; future A019D attempt unconsumed;
GPU No; Arena/experiments/downloads/archive writes=0. Historical A013 behavior,
scientific semantics, Task016 and Task017 unchanged; Task017 NOT_ROBUST.
No biological interpretation. No tag, release or version mutation.

## Deferred validation stop and final verdict

**A19C-R11-DEFERRED-VALIDATION-BLOCKER.** C1 correction resolved; overall forward
certification withheld. A019C-FORWARD-HARNESS-SYNTHETICALLY-CERTIFIED not issued.
Certification sufficiency NOT SATISFIED. No commit/push; all WIP retained.

Exact resumed command: guarded pytest separately, sequentially, `-q -x`, explicit
files tests/test_application_a018u.py, a018t.py, a018s.py, a018.py, a017.py,
a016.py, a015.py, a014.py, a013.py (each with test_application_ prefix).
Each writes C:/TEMP/a019c-r11-<suite>.xml. Environment remains activated with
absolute firewall PYTHONPATH and log C:/TEMP/a019c-r11-deferred.jsonl.
PowerShell exits immediately when a suite exits nonzero; final command exit 1.

| Suite | R11 outcome |
|---|---|
| A018U | 80 passed, 34.32 s |
| A018T | 283 passed, 45.71 s |
| A018S | 95 passed, 15.53 s |
| A018 | 97 passed, 15.38 s |
| A017 | 79 passed, 24.70 s |
| A016 | 68 passed, 19.36 s; one Feather V1 deprecation warning |
| A015 | 59 passed, 5.00 s |
| A014 | 1 failed, 0.17 s; remaining instances NOT RUN |
| A013 | NOT RUN after fail-fast |
| A011/reference LIF | NOT RUN after fail-fast |
| Application synthetic-safe suites | NOT RUN after fail-fast |
| Remaining historical Git/Node S1 controls | NOT RUN; not excluded or PASS |
| compileall | NOT RUN after fail-fast |
| git diff --check | PASS |

Exact new blocker:
`tests/test_application_a014.py::test_tree_memory_enforcement[0-direct]`.
Fixture direct mode uses sys._base_executable:
`D:/uv/cpython-3.14-windows-x86_64-none/python.exe`, while the admitted executable
is the current virtual-environment sys.executable. ProcessJob -> Popen ->
validation_firewall.guarded_command raises
`SourceAccessDenied('unsupported A019 child executable')` at line 62.
Parent rejection occurs before Popen launches this allocation workload; no
unsupported child is admitted. No allowlist broadening, cap change, retry,
new A014 correction or conversion of this failed S1 test to S2.
This does not invalidate bootstrap certification or the targeted A018UR result.

All seven accepted registered-source counters remain zero: connectivity,
annotation, neurotransmitter, metadata, provenance, mapping and other; aggregate 0.
R11 audit logs: prefix ACTIVE=1; target=2; A018UR=3; bootstrap=12; harness=5;
CLI=2; deferred=8. Only bootstrap has blocked records: 34 (33 registered-path
probes plus one synthetic deny-root sentinel). These are deliberate blocked
probes, not accepted reads. Permitted tooling: metadata Git inventory/identities,
source/history reads limited to named source files, guarded selected pytest,
guarded contained synthetic CLI, audit/JUnit/generated result inspection,
plan writing and git diff --check. No data diff, integrity, build or downloads.

Final local/origin/live identity remains the starting SHA. Staging/stash empty;
worktree dirty: 24 expanded paths (22 accumulated + modified A018UR test + R11
plan). No unrelated paths. Historical files untouched. Production files changed:
none. Test changes: only the timeout fixture and its additional assertions.
Final commit SHA: no new commit. Push: NOT RUN, success prerequisite unmet.
Package 0.3.0; active tracked workflows 0; no tag/release/version mutation.

Superseding readiness: A018UR timeout adjudicated and targeted gates PASS;
bootstrap certified; deferred validation incomplete. A019D eligibility No;
A019D is neither recommended nor executed. Exact next bounded task: adjudicate
the A014 direct-executable synthetic validation admission blocker and complete
the remaining R10 S0/S1 manifest under a separately authorized scope.

## R11 per-test manifest

Unexecuted parameter instances remain NOT RUN. R10 PASS is historical evidence only.

| Exact node base | Class | R11 outcome |
|---|---|---|
| `tests/test_application_a019c_r5_firewall.py::test_canonical_serialization` | S0 | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_false_positive_rejected` | S0 | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_malformed_rejected` | S0 | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_actual_windows_audit_serialization` | S0 | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_actual_worker_bypass_rejected` | S0 | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_script_path_with_spaces` | S0 | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_contained_actual_worker_startup` | S0 | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_live_contained_descendant_cleanup` | S0 | PASS |
| `tests/test_application_a019c_r4_firewall.py::test_parent_native_control_and_categories` | S0 | PASS |
| `tests/test_application_a019c_r4_firewall.py::test_required_child_rejects_before_workload` | S0 | PASS |
| `tests/test_application_a019c_r4_firewall.py::test_normal_public_native_child` | S0 | PASS |
| `tests/test_application_a019c_r4_firewall.py::test_actual_worker_startup` | S0 | PASS |
| `tests/test_application_a019c_r4_firewall.py::test_inherited_activation_removed_parent_rejects` | S0 | PASS |
| `tests/test_application_a019c_r3_firewall.py::test_01_valid_native_synthetic_control` | S0 | PASS |
| `tests/test_application_a019c_r3_firewall.py::test_02_native_registered_source_denied_before_constructor` | S0 | PASS |
| `tests/test_application_a019c_r3_firewall.py::test_03_python_child_native_guard` | S0 | PASS |
| `tests/test_application_a019c_r3_firewall.py::test_04_missing_inherited_guard_fails_closed` | S0 | PASS |
| `tests/test_application_a019c_r2_firewall.py::test_blocked_before_content` | S0 | PASS |
| `tests/test_application_a019c_r2_firewall.py::test_generated_and_temp_and_source_allowed` | S0 | PASS |
| `tests/test_application_a019c_r2_firewall.py::test_subprocess_guard` | S0 | PASS |
| `tests/test_application_a019c_r2_firewall.py::test_child_cannot_drop_guard` | S0 | PASS |
| `tests/test_application_a019c_r2_firewall.py::test_native_reader_denies_synthetic_sentinel` | S0 | PASS |
| `tests/test_application_a019c.py::test_full_structure_route_lifetime_replay_and_defaults` | S0 | PASS |
| `tests/test_application_a019c.py::test_each_gate_stops_before_runtime_one_preparation` | S0 | PASS |
| `tests/test_application_a019c.py::test_cross_layer_rejected` | S0 | PASS |
| `tests/test_application_a019c.py::test_fallback_hard_stop` | S0 | PASS |
| `tests/test_application_a019c.py::test_induced_failure_no_retry` | S0 | PASS |
| `tests/test_application_a019c.py::test_exact_resource_limits` | S0 | PASS |
| `tests/test_application_a019c.py::test_contained_tree_forced_stops_no_orphan` | S0 | PASS |
| `tests/test_application_a019c.py::test_synthetic_cli_contained_success` | S0 | PASS |
| `tests/test_application_a019c.py::test_synthetic_source_guard_before_access` | S0 | PASS |
| `tests/test_application_a019c.py::test_timing_structure_and_historical_default` | S0 | PASS |
| `tests/test_application_a019c.py::test_completed_preparation_deadline_before_runtime` | S0 | PASS |
| `tests/test_application_a019c.py::test_completed_call_deadline_no_retry` | S0 | PASS |
| `tests/test_application_a019c.py::test_watchdog_instrumentation_failure_terminates_tree` | S0 | PASS |
| `tests/test_application_a019c.py::test_contract_schema_matches_success_evidence` | S0 | PASS |
| `tests/test_application_a019c.py::test_watchdog_child_memory_stop_aggregate_and_cleanup` | S0 | PASS |
| `tests/test_application_a019a.py::test_frozen_two_state_contract` | S0 | NOT RERUN; R10 PASS preserved |
| `tests/test_application_a019a.py::test_historical_schedule_from_tracked_metadata_only` | S0 | NOT RERUN; R10 PASS preserved |
| `tests/test_application_a019a.py::test_b_starts_fresh_after_a_released_using_same_runtime_and_graph` | S0 | NOT RERUN; R10 PASS preserved |
| `tests/test_application_a019a.py::test_a019a_checks_have_no_real_execution_and_preserve_defaults` | S0 | NOT RERUN; R10 PASS preserved |
| `tests/test_application_a018uj.py::test_independent_frozen_artifact_reconstruction_and_provenance` | S2 | NOT RUN |
| `tests/test_application_a018uj.py::test_each_mandatory_layer_mismatch_fails` | S0 | NOT RERUN; R10 PASS preserved |
| `tests/test_application_a018uj.py::test_correct_tuple_and_cross_layer_rejection` | S0 | NOT RERUN; R10 PASS preserved |
| `tests/test_application_a018uj.py::test_ambiguous_legacy_fields_rejected` | S0 | NOT RERUN; R10 PASS preserved |
| `tests/test_application_a018uj.py::test_no_real_execution_and_scientific_default_unchanged` | S2 | NOT RUN |
| `tests/test_application_a018ui.py::test_historical_identity_layer_reconstruction` | S1 | NOT RUN |
| `tests/test_application_a018ui.py::test_historical_current_components_exact` | S1 | NOT RUN |
| `tests/test_application_a018ui.py::test_metadata_and_diagnostic_bytes` | S0 | NOT RERUN; R10 PASS preserved |
| `tests/test_application_a018ui.py::test_effective_digest_field_order` | S0 | NOT RERUN; R10 PASS preserved |
| `tests/test_application_a018ui.py::test_historical_preparation_and_committed_fingerprints` | S1 | NOT RUN |
| `tests/test_application_a018ui.py::test_production_default_and_frozen_expectation_unchanged` | S1 | NOT RUN |
| `tests/test_application_a018ur.py::test_success_exact_identity_no_advance_default_restored` | S0 | PASS |
| `tests/test_application_a018ur.py::test_identity_mismatch_stops_and_cleans` | S0 | PASS |
| `tests/test_application_a018ur.py::test_failure_cleanup_and_fallback_prevented` | S0 | PASS |
| `tests/test_application_a018ur.py::test_exact_frozen_constants_and_no_execution_entrypoints` | S0 | PASS |
| `tests/test_application_a018ur.py::test_supervisor_time_failure_cleans_without_retry` | S0 | PASS |
| `tests/test_application_a018ur.py::test_supervisor_success_boundary_handshake` | S0 | PASS |
| `tests/test_application_a018u.py::test_instrumented_oracle_exact` | S0 | PASS |
| `tests/test_application_a018u.py::test_missing_metadata_and_policy_contract` | S0 | PASS |
| `tests/test_application_a018u.py::test_large_safe_exact` | S0 | PASS |
| `tests/test_application_a018u.py::test_large_integer_identity` | S0 | PASS |
| `tests/test_application_a018u.py::test_default_has_no_probe` | S0 | PASS |
| `tests/test_application_a018u.py::test_synthetic_bounds` | S0 | PASS |
| `tests/test_application_a018t.py::test_exact_oracle_ownership_release` | S0 | PASS |
| `tests/test_application_a018t.py::test_prepared_scientific_oracle` | S0 | PASS |
| `tests/test_application_a018t.py::test_compaction_releases_capacity` | S0 | PASS |
| `tests/test_application_a018t.py::test_many_small_schedule_determinism` | S0 | PASS |
| `tests/test_application_a018t.py::test_partition_and_stage_release` | S0 | PASS |
| `tests/test_application_a018t.py::test_overflow_reference_fallback` | S0 | PASS |
| `tests/test_application_a018t.py::test_production_default` | S0 | PASS |
| `tests/test_application_a018t.py::test_closed_boundaries` | S0 | PASS |
| `tests/test_application_a018t.py::test_large_ids_and_invalid_block` | S0 | PASS |
| `tests/test_application_a018t.py::test_equal_key_on_either_slice_endpoint` | S0 | PASS |
| `tests/test_application_a018t.py::test_seeded_partition_block_invariance` | S0 | PASS |
| `tests/test_application_a018s.py::test_exact_oracle_ownership_release` | S0 | PASS |
| `tests/test_application_a018s.py::test_prepared_scientific_oracle` | S0 | PASS |
| `tests/test_application_a018s.py::test_compaction_releases_capacity` | S0 | PASS |
| `tests/test_application_a018s.py::test_many_small_schedule_determinism` | S0 | PASS |
| `tests/test_application_a018s.py::test_partition_and_stage_release` | S0 | PASS |
| `tests/test_application_a018s.py::test_overflow_reference_fallback` | S0 | PASS |
| `tests/test_application_a018s.py::test_production_default` | S0 | PASS |
| `tests/test_application_a018.py::test_runs_exact_deterministic_and_lifetime` | S0 | PASS |
| `tests/test_application_a018.py::test_downstream_partition_exact` | S0 | PASS |
| `tests/test_application_a018.py::test_overflow_rejection` | S0 | PASS |
| `tests/test_application_a018.py::test_completed_stage_inputs_reclaimable` | S0 | PASS |
| `tests/test_application_a018.py::test_overflow_loader_fallback` | S0 | PASS |
| `tests/test_application_a018.py::test_schedule_partition_invariance` | S0 | PASS |
| `tests/test_application_a018.py::test_fan_in_composition_invariance` | S0 | PASS |
| `tests/test_application_a018.py::test_production_default` | S0 | PASS |
| `tests/test_application_a017.py::test_exact_downstream` | S0 | PASS |
| `tests/test_application_a017.py::test_integer_domain_and_merge` | S0 | PASS |
| `tests/test_application_a017.py::test_lifetime_bounds_and_no_partial_threshold` | S0 | PASS |
| `tests/test_application_a017.py::test_invalid_excluded_upstream` | S0 | PASS |
| `tests/test_application_a017.py::test_scale_exact` | S0 | PASS |
| `tests/test_application_a017.py::test_production_dispatch_unchanged` | S0 | PASS |
| `tests/test_application_a017.py::test_overflow_oracle_fallback` | S0 | PASS |
| `tests/test_application_a017.py::test_high_cardinality_exact` | S0 | PASS |
| `tests/test_application_a016.py::test_boundaries_exact` | S0 | PASS |
| `tests/test_application_a016.py::test_invalid_boundary` | S0 | PASS |
| `tests/test_application_a016.py::test_reader_projection_admission_lifetime` | S0 | PASS |
| `tests/test_application_a016.py::test_v1_rejected` | S0 | PASS |
| `tests/test_application_a016.py::test_scale_exact` | S0 | PASS |
| `tests/test_application_a016.py::test_masks_released_numeric_ownership` | S0 | PASS |
| `tests/test_application_a016.py::test_noninteger_schema_rejected` | S0 | PASS |
| `tests/test_application_a015.py::test_exact_adversarial` | S0 | PASS |
| `tests/test_application_a015.py::test_high_exclusion_scale` | S0 | PASS |
| `tests/test_application_a015.py::test_membership_exact` | S0 | PASS |
| `tests/test_application_a015.py::test_authoritative_membership_and_no_identity_collapse` | S0 | PASS |
| `tests/test_application_a015.py::test_invalid_excluded_rows_rejected` | S0 | PASS |
| `tests/test_application_a014.py::test_tree_memory_enforcement` | S1 | FAIL |
| `tests/test_application_a014.py::test_aggregate_limit_without_individual_offender` | S1 | NOT RUN |
| `tests/test_application_a014.py::test_normal_exit` | S1 | NOT RUN |
| `tests/test_application_a014.py::test_accounting_failure_stops_tree` | S1 | NOT RUN |
| `tests/test_application_a014.py::test_instrumentation_opt_in_and_exact_identity` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_limits_and_cpu_only` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_one_preparation` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_watchdog_stops` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_percentiles_and_warmup_exclusion` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_schedule_is_complete_grid_slices_and_reused` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_two_fresh_states_exact_twenty_four_advances_and_replay` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_mismatch_fails_at_first_component` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_canonical_digest_exact_and_endian_stable` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_pending_guard` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_no_download_arena_gpu_or_import_execution` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_refuse_existing_output` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_watchdog_binds_worker_not_launcher` | S0 | NOT RUN |
| `tests/test_application_a013.py::test_native_watchdog_can_terminate_actual_redirected_python` | S1 | NOT RUN |
| `tests/test_application_a011.py::test_exact_continuity` | S0 | NOT RUN |
| `tests/test_application_a011.py::test_initial_state_and_identity` | S0 | NOT RUN |
| `tests/test_application_a008.py::test_reproducibility_contracts_and_packaged_assets` | S0 | NOT RUN |
| `tests/test_application_a008.py::test_application_docs_are_portable_and_do_not_embed_session_urls` | S0 | NOT RUN |
| `tests/test_application_a007c.py::test_synthetic_production_api_and_assets` | S1 | NOT RUN |
| `tests/test_application_a007c.py::test_authoritative_backend_firewall_and_packaging` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_spec_serialization_identity_and_no_verdict` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_invalid_variant_allowlist` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_cross_variant_event_schedule` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_full_sweep_and_retention_stress` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_exact_reuse_and_mixed_provenance` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_cancel_preserves_completed_evidence` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_stop_on_failure` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_mixed_child_reuse_after_cancellation` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_parent_byte_bound_preserves_earlier_evidence` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_identity_and_graph_mismatch_rejected` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_session_host_origin_and_synthetic_api` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_cpu_startup_cuda_lazy` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_schedule_gap_stops_before_execution` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_all_children_reused_without_execution` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_cancel_before_first_child` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_child_capacity_and_parent_limits` | S0 | NOT RUN |
| `tests/test_application_a007b.py::test_strict_request_contract` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_exact_variant_contract` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_reference_and_weight_coupling` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_allowlisted_sign_policy` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_invalid_preparation` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_nonfinite_parameters` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_reject_unbounded_client_input` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_true_preparation_and_execution` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_ordinary_reference_bytes_and_known_certified_identities` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_same_variant_pairing` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_cross_variant_rejected` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_sixteen_children_survive_recent_eviction` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_parent_byte_limit_and_snapshot` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_no_historical_runner_dependency` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_cuda_receives_equivalent_configuration` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_variant_cuda_unavailable_is_explicit` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_closed_session_cannot_admit_parent` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_frozen_preset_digest` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_parent_child_capacity` | S0 | NOT RUN |
| `tests/test_application_a007a.py::test_derived_input_must_remain_finite` | S0 | NOT RUN |
| `tests/test_application_a006r.py::test_visible_run_transitions` | S1 | NOT RUN |
| `tests/test_application_a006.py::test_pair_metrics_digest_and_zero_baseline` | S0 | NOT RUN |
| `tests/test_application_a006.py::test_nonzero_deltas_and_deterministic_identity` | S0 | NOT RUN |
| `tests/test_application_a006.py::test_mismatch_rejected` | S0 | NOT RUN |
| `tests/test_application_a006.py::test_schedule_and_incomplete_rejected` | S0 | NOT RUN |
| `tests/test_application_a006.py::test_union_playback_and_recorded_zero` | S0 | NOT RUN |
| `tests/test_application_a006.py::test_comparison_api_session_and_backend_export` | S0 | NOT RUN |
| `tests/test_application_a005.py::test_post_update_spike_time_grid` | S0 | NOT RUN |
| `tests/test_application_a005.py::test_sparse_payload_identity_digest_and_no_fabricated_events` | S0 | NOT RUN |
| `tests/test_application_a005.py::test_deterministic_raster_order` | S0 | NOT RUN |
| `tests/test_application_a005.py::test_payload_rejects_nonfinite_trace_and_size_cap` | S0 | NOT RUN |
| `tests/test_application_a005.py::test_playback_endpoint_session_and_completion_gate` | S0 | NOT RUN |
| `tests/test_application_a004.py::test_long_identity_layout_has_shared_wrap_rule` | S0 | NOT RUN |
| `tests/test_application_a004.py::test_view_determinism_identity_and_cap` | S0 | NOT RUN |
| `tests/test_application_a004.py::test_target_and_combined_context` | S0 | NOT RUN |
| `tests/test_application_a004.py::test_rejects_unbounded_or_unknown_filter` | S0 | NOT RUN |
| `tests/test_application_a004.py::test_subgraph_route_bounds_session_failure_and_pending` | S0 | NOT RUN |
| `tests/test_application_a003.py::test_loopback_catalog_security_and_ui` | S0 | NOT RUN |
| `tests/test_application_a003.py::test_previous_process_token_is_rejected` | S0 | NOT RUN |
| `tests/test_application_a003.py::test_history_limit_is_fixed` | S0 | NOT RUN |
| `tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields` | S2 | NOT RUN |
| `tests/test_application_a003.py::test_validate_and_run_requests_share_exact_spec_identity` | S2 | NOT RUN |
| `tests/test_application_a003.py::test_manager_retains_safe_failure` | S0 | NOT RUN |
| `tests/test_application_a003.py::test_manager_evicts_oldest_completed_job` | S0 | NOT RUN |
| `tests/test_application_a003.py::test_result_events_and_backend_export_routes` | S2 | NOT RUN |
| `tests/test_application_a002.py::test_spec_validation_and_canonical_identity` | S0 | NOT RUN |
| `tests/test_application_a002.py::test_final_grid_step_spike_is_valid` | S0 | NOT RUN |
| `tests/test_application_a002.py::test_spike_outside_engine_grid_is_rejected` | S0 | NOT RUN |
| `tests/test_application_a002.py::test_nonfinite_spike_step_is_rejected` | S0 | NOT RUN |
| `tests/test_application_a002.py::test_equal_timestep_spikes_have_deterministic_neuron_order` | S0 | NOT RUN |
| `tests/test_application_a002.py::test_invalid_top_level` | S0 | NOT RUN |
| `tests/test_application_a002.py::test_invalid_stimulus_and_finite_values` | S0 | NOT RUN |
| `tests/test_application_a002.py::test_state_events_and_no_fake_progress` | S0 | NOT RUN |
| `tests/test_application_a002.py::test_comparison_spikes_and_robustness_contract` | S0 | NOT RUN |
| `tests/test_application_a002.py::test_optional_git_provenance` | S0 | NOT RUN |
| `tests/test_application_a002.py::test_cpu_only_import_and_cuda_unavailable` | S0 | NOT RUN |
| `tests/test_application_a002.py::test_non_scientific_synthetic_engine_integration` | S0 | NOT RUN |
| `tests/test_task005.py::test_reference_parameters_are_explicit_and_grid_is_exact` | S0 | NOT RUN |
| `tests/test_task005.py::test_linear_update_matches_analytical_solution` | S0 | NOT RUN |
| `tests/test_task005.py::test_resting_neuron_and_synaptic_decay` | S0 | NOT RUN |
| `tests/test_task005.py::test_positive_and_negative_direct_impulses_have_expected_polarity` | S0 | NOT RUN |
| `tests/test_task005.py::test_threshold_reset_and_g_reset` | S0 | NOT RUN |
| `tests/test_task005.py::test_refractory_blocks_input_until_strictly_after_2_2_ms` | S0 | NOT RUN |
| `tests/test_task005.py::test_incoming_event_during_refractory_is_ignored_and_poisson_targets_can_opt_out` | S0 | NOT RUN |
| `tests/test_task005.py::test_exact_delay_and_signed_sparse_propagation` | S0 | NOT RUN |
| `tests/test_task005.py::test_self_edge_and_two_neuron_inhibitory_edge_are_supported` | S0 | NOT RUN |
| `tests/test_task005.py::test_multiple_and_simultaneous_events_sum_deterministically` | S0 | NOT RUN |
| `tests/test_task005.py::test_unresolved_edges_are_excluded_and_anatomy_is_unchanged` | S0 | NOT RUN |
| `tests/test_task005.py::test_explicit_stimulus_is_sorted_reproducible_and_validates_ids_and_grid` | S0 | NOT RUN |
| `tests/test_task005.py::test_seeded_poisson_is_reproducible_and_uses_reference_scaling` | S0 | NOT RUN |
| `tests/test_task005.py::test_silencing_disables_outgoing_only` | S0 | NOT RUN |
| `tests/test_task005.py::test_fingerprints_and_result_digest_are_deterministic_and_identity_sensitive` | S0 | NOT RUN |
| `tests/test_task005.py::test_effective_weight_preserves_anatomical_count_boundary` | S0 | NOT RUN |
| `tests/test_task005.py::test_effective_inhibitory_weight_uses_presynaptic_sign` | S0 | NOT RUN |
| `tests/test_task005.py::test_two_neuron_chain_keeps_spike_output_compact` | S0 | NOT RUN |
| `tests/test_task005.py::test_simulation_reports_identity_metadata` | S0 | NOT RUN |
| `tests/test_task005.py::test_parameter_identity_changes_simulation_configuration` | S0 | NOT RUN |
| `tests/test_task005.py::test_duration_must_be_on_the_discrete_clock` | S0 | NOT RUN |
| `tests/test_task005.py::test_duplicate_schedule_times_are_additive` | S0 | NOT RUN |
| `tests/test_task005.py::test_poisson_rejects_more_than_one_expected_event_per_step` | S0 | NOT RUN |
| `tests/test_task005.py::test_trace_requires_an_explicit_small_subset` | S0 | NOT RUN |

## Exact initial dirty paths

```text
docs/plans/2026-10-05-application-a019c-executable-harness-contract-alignment.md
docs/plans/2026-10-05-application-a019c-harness-contract.json
docs/plans/2026-10-05-application-a019c-r2-guard-first-firewall-recovery.md
docs/plans/2026-10-05-application-a019c-synthetic-evidence.json
docs/plans/2026-10-06-application-a019c-r10-validation-manifest-closure.md
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
