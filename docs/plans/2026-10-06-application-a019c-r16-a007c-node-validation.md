# A019C-R16: A007C Node synthetic-validation admission

Authorization: `授權 A019C-R16`. Synthetic-only; no real payload authorization.
Root derived by `git rev-parse --show-toplevel`: D:/spider/working/MaleCNS-Sim.
Starting local HEAD/origin/master/live master:
`60c900b0c8e5a02ea95efc7340fd190193edf7e9`.
Initial expanded inventory: 32 paths, all accumulated A019C recovery scope;
unrelated WIP No; staging/stash empty. Version 0.3.0; active tracked workflows 0.

Plan: inventory, static tracked historical audit, single pre-fix reproduction,
adjudicate H1-H5, narrow correction and negative controls, corrected single case,
complete admitted application selection, shared admission controls/bootstrap,
harness/fresh CLI, affected stateful controls, compileall/diff check and final
manifest. Stop at a new application blocker; success alone permits commit/push.

Previous chronology and classifications remain unchanged, including
`A19C-R15-DEFERRED-VALIDATION-BLOCKER`. R10 J2/I2/B2, R11 C1, R12 D2, R13 E1,
R14 F1 and R15 G1 are not reopened. Historical STOP records are not renamed PASS.

## Historical boundary and rejection

Exact failing case:
`tests/test_application_a007c.py::test_synthetic_production_api_and_assets`.
Tracked introduction: `257355c feat: add robustness evidence view`.
Reference: docs/plans/2026-10-02-application-a007c-robustness-ui.md, particularly
Identity-safe switching and Final automated validation. The report explicitly
states Node is required for the focused frontend harness.

Node executes tests/js/application_a007c.cjs, loading production compare.js and
robustness.js into a VM with DOM/mock-canvas objects. It proves backend-authored
values are rendered unchanged (including deliberately inconsistent delta values),
ZERO_BASELINE and NO_AGGREGATE_RULE, row/chart selection, comparison/playback/
subgraph routing, stale asynchronous successes/errors, resets and parent switching.
It checks actual JavaScript Promise, VM and module semantics, not merely JSON
serialization. Python substitution would lose the independent JS-consumer boundary.
The mocked frontend performs no real scientific execution. Inputs are generated
synthetic HTTP evidence and source assets; no registered scientific payload needed.

Historical exact argv:
`["node", ROOT/tests/js/application_a007c.cjs, TEMP/evidence.json, ROOT/src/malecns_sim/application/static]`.
No flags, npm/npx, inline JS or shell. PATH resolves to
`C:/Program Files/nodejs/node.exe`; file metadata version 24.13.0.
cwd is repository root, environment inherited, stdout/stderr PIPE, text=True.
Expected exit 0 and `A007C DOM/API contract checks PASS; out-of-order variant and parent switching PASS`,
followed by synthetic measurement text. subprocess.run waits and closes pipes;
the review fixture shuts down/closes the HTTP server and its temporary directory.
Historical launcher had no timeout.

guarded_command compares Path(command[0]).resolve() with sys.executable.resolve().
For the bare token `node`, the former is ROOT/node, not PATH resolution. It raises
`SourceAccessDenied('unsupported A019 child executable')` before original Popen.
The same failure applies to an absolute Node executable under the old Python-only
grammar. There is no Windows command serialization/parse ambiguity: audit_argv
of the canonical serialization preserves the four supplied tokens. The later
mandatory_child subprocess audit and Windows CreateProcess are never reached.
No child identity, activation or JS assertion failure occurred.

Single unmodified reproduction: guarded pytest -q -x, JUnit
C:/TEMP/a019c-r16-prefix.xml; **1 FAIL**, 5.49 s, exit 1.
Parent PID 17672, active=1, audit C:/TEMP/a019c-r16-prefix.jsonl.
Exact data path C:/TEMP/a019c-r16-prefix/test_synthetic_production_api_0/evidence.json.
Node PID none; descendants none; child activation not reached; script/workload
start false. Synthetic HTTP assertions executed and fixture teardown completed.
No Node workload cleanup PASS is inferred from pre-launch rejection.

## Adjudication and correction

**H2 — NARROW NODE SYNTHETIC-VALIDATION ADMISSION GAP.** Tracked intent requires
the independent JS runtime. H1 routing through Python cannot activate a Node
runtime guard; H3 has no pre-fix started workload; H4 contradicts tracked intent.
A distinct validation-tool contract is appropriate, unlike Python mandatory
entrypoint, R12 direct base-Python -S control, R13 replacement topology,
R14 normal exit and R15 redirected-Python unbuffered control.

Production files changed No. A007C fixture changed Yes. Shared validation-only
admission changed Yes. Historical CJS and production JS are unchanged.
New fixed helper scripts/a019c_firewall/a007c_node.py constructs exactly:

```text
C:\Program Files\nodejs\node.exe
--permission
--allow-fs-read=<absolute scripts/a019c_firewall/a007c_node.cjs>
--allow-fs-read=<absolute tests/js/application_a007c.cjs>
--allow-fs-read=<canonical temporary evidence.json>
--allow-fs-read=<absolute static/compare.js>
--allow-fs-read=<absolute static/robustness.js>
<absolute scripts/a019c_firewall/a007c_node.cjs>
a007c-synthetic-dom-contract-v1
<canonical temporary evidence.json>
<absolute src/malecns_sim/application/static>
```

All eleven argv tokens and order match exactly. Input must be a canonical existing
file named evidence.json under tempfile.gettempdir(), pass registered-source check;
all admitted source paths must resolve to themselves. Test runs set TEMP/TMP=C:/TEMP.
cwd must equal ROOT, activation=1, ACTIVE true, close_fds=True, no executable
override or shell. Child environment strips NODE_* and OPENSSL_CONF; admission
rejects their presence. Fixture adds timeout=30 s. Wrapper checks permission state,
blocks a direct registered-path fs read and descendant creation, prints start/PID
markers, then requires the unchanged historical CJS with its original argv shape.
Writes, workers, addons, WASI and child creation are not granted.

Runtime documentation checked against installed version:
https://nodejs.org/download/release/v24.13.0/docs/api/permissions.html.
Permissions restrict trusted code; they are not a malicious-code sandbox or native
byte telemetry. Exact reviewed scripts/assets only are admitted. No directory or
wildcard read grant; arbitrary Node, JS, -e/--eval, loaders, flags or shells remain
rejected. Existing Python mandatory activation is preserved in source but shared
regression certification is pending following the application STOP below.

## Controls and corrected execution

tests/test_application_a019c_r16_firewall.py::test_exact_node_grammar_and_negative_controls
PASS. N1 exact command recognized both list and canonical Windows serialization;
authorized runtime executes in the A007C case. N2 alternate executable, N3 alternate
script, N4 wrong purpose, N5 shell, N6 -e/--eval, N7 extra flag, N8 traversal spelling
rejected before launch. Alternate --require and NODE_OPTIONS injection also rejected.
Parent registered evidence path rejected before read. N9 wrapper's registered-path
read returns ERR_ACCESS_DENIED before content read. N10 descendant registered-path
probe denied at spawnSync before descendant creation; no claim of a launched
descendant doing a read. N11 normal subprocess exit/pipe cleanup PASS; N12 scoped
post-run CIM scan has no A007C task command or recorded Node PID alive.

Corrected single A007C plus admission controls: **2 PASS**, 5.84 s, exit 0.
Parent PID 19384, Node PID 18268. stdout contains direct/descendant probe blocks,
guard ACTIVE, script-start and workload-start, followed by historical contract PASS.
One Node launch; no retry. No descendant created. JUnit
C:/TEMP/a019c-r16-single.xml; audit C:/TEMP/a019c-r16-single.jsonl.

Complete application selection uses the exact R15/R10 admitted node list,
C:/TEMP/a019c-r15-application-nodes.txt, -q -x, unique basetemp and JUnit.
Result **78 PASS, 1 FAIL**, 21.92 s, exit 1. Parent PID 9400; A007C passes again.
Next distinct blocker:
`tests/test_application_a006r.py::test_visible_run_transitions`, line 84,
`[C:/Program Files/nodejs/node.EXE, '-e', <tracked inline DOM/run-status JS>, STATIC]`.
It raises the same unsupported-executable exception before launch. This is a
separate inline JS contract, not admitted by A007C's exact grammar. It is not an
application assertion regression. Fail-fast STOP; no A006R correction or retry.
JUnit C:/TEMP/a019c-r16-application.xml; audit C:/TEMP/a019c-r16-application.jsonl.

## Final disposition and remaining gates

**A19C-R16-APPLICATION-VALIDATION-BLOCKER.** A007C H2 target and negative controls
pass, but complete manifest closure fails at distinct A006R admission.
Superseding overall A019C status: synthetic certification withheld; manifest
incomplete. Certification sufficiency NOT SATISFIED. No success commit/push.
A019D not eligible, not recommended, not executed.
Exact next bounded task: separately authorize A006R inline Node synthetic-validation
contract adjudication and remaining manifest completion, including shared regression.

After mandatory STOP: affected A014/A013 controls, complete bootstrap, A019C harness,
fresh contained CLI, affected Stateful/A011, compileall and final git diff --check
NOT RUN. R15 historical results remain 19 A014, 17 A013, 39 bootstrap, 35 harness,
CLI A19C-A/exit 0 and 27 Stateful/A011/reference LIF PASS. Because shared admission
changed, R15 bootstrap and stateful evidence do not certify current R16 code.
FIREWALL_BOOTSTRAP_CERTIFIED historical record preserved; current renewal pending.

J2 prohibited data diff, I2 integrity and B2 build remain NOT RUN, not PASS.
Full pytest NOT RUN: synthetic-only authorization; known S2 real-data tests excluded.
S0/S1 required closure INCOMPLETE. S2 explicit NOT RUN. N unchanged/outside scope.
No unresolved S0/S1 converted to S2 or N. Per-node manifest follows, retaining R15
historical evidence while recording only actual fresh R16 execution.

Accepted registered-source reads all 0: connectivity, annotation, neurotransmitter,
metadata, provenance, mapping, other; aggregate 0. Accepted-read accounting uses
fail-closed guarded execution/source-access accounting and is not independent native
byte telemetry. R16 deliberate probes: one parent registered-path block and two
Node direct registered-path blocks (single/application), two descendant-creation
blocks (no descendant starts). Permitted Node application operations: two exact
bounded launches, generated JSON plus exact JS assets only. No accepted payload read.

Forward contract below is **historical R15 evidence only**, not fresh R16 certification:
explicit bounded route PASS; production default unchanged; merge block 16,384;
hard fallback stop PASS; G1-G6 and L3/L4 PASS. One PreparedNetwork, one PreparedRuntime,
two fresh SimulationStates, A released before B, no coexistence or B deriving from A,
no runtime reset/recreation. Each state 2 warmups + 10 measured x20 ms, final 240 ms;
24 calls, maximum consecutive 12/state; no continuous 480-ms trajectory.
Schedule generated once: LEFT sugar 42 neurons at 100 Hz, RIGHT 0; seed 1555062870;
impulse 68.75 mV, horizon 240 ms, 948 events; fingerprint
6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a.
Exact windows/membrane/synaptic/refractory/pending/delayed/output/final-state/time
replay PASS. Timeouts 600/30/1500 s; both caps 8,589,934,592 bytes.
Forced timeout/memory stop, containment/live-tree cleanup/no orphan/no retry PASS
historically; no new claims about R16 shared-helper certification.

Execution firewall: full-real preparations 0; real advances 0; real benchmarks 0;
A019D attempt consumed No; GPU No; Arena/experiments/downloads/archive writes 0.
Historical A013 scientific behavior unchanged; Task016 unchanged; Task017 unchanged /
NOT_ROBUST. Production preparation default and scientific semantics unchanged.

Final local/origin/live SHA remains starting SHA. Commit/push NOT RUN; no new SHA.
Final worktree dirty; staging/stash empty; version 0.3.0; workflows 0.
No tag/release/version mutation or reset/restore/clean/stash. Only metadata custody
checks and this report/manifest were completed after STOP. Earlier records unchanged.
Local C:/TEMP evidence is not guaranteed to persist on another machine.

## Exact initial inventory (32 paths)

```text
 M tests/test_application_a013.py
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
?? docs/plans/2026-10-06-application-a019c-r15-a013-u-guarded-entrypoint.md
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

## Deterministic final per-node manifest

R15 evidence remains historical. NOT RUN below means no fresh R16 execution; mandatory renewal is unresolved. Parameterized JUnit results are summarized under their manifest function.

| Node | Class | R16 result | Historical R15 status |
|---|---|---|---|
| `tests/test_application_a019c_r5_firewall.py::test_canonical_serialization` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_false_positive_rejected` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_malformed_rejected` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_actual_windows_audit_serialization` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_actual_worker_bypass_rejected` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_script_path_with_spaces` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_contained_actual_worker_startup` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r5_firewall.py::test_live_contained_descendant_cleanup` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r4_firewall.py::test_parent_native_control_and_categories` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r4_firewall.py::test_required_child_rejects_before_workload` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r4_firewall.py::test_normal_public_native_child` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r4_firewall.py::test_actual_worker_startup` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r4_firewall.py::test_inherited_activation_removed_parent_rejects` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r3_firewall.py::test_01_valid_native_synthetic_control` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r3_firewall.py::test_02_native_registered_source_denied_before_constructor` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r3_firewall.py::test_03_python_child_native_guard` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r3_firewall.py::test_04_missing_inherited_guard_fails_closed` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r2_firewall.py::test_blocked_before_content` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r2_firewall.py::test_generated_and_temp_and_source_allowed` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r2_firewall.py::test_subprocess_guard` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r2_firewall.py::test_child_cannot_drop_guard` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r2_firewall.py::test_native_reader_denies_synthetic_sentinel` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_full_structure_route_lifetime_replay_and_defaults` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_each_gate_stops_before_runtime_one_preparation` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_cross_layer_rejected` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_fallback_hard_stop` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_induced_failure_no_retry` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_exact_resource_limits` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_contained_tree_forced_stops_no_orphan` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_synthetic_cli_contained_success` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_synthetic_source_guard_before_access` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_timing_structure_and_historical_default` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_completed_preparation_deadline_before_runtime` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_completed_call_deadline_no_retry` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_watchdog_instrumentation_failure_terminates_tree` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_contract_schema_matches_success_evidence` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c.py::test_watchdog_child_memory_stop_aggregate_and_cleanup` | S0 | NOT RUN | PASS |
| `tests/test_application_a019a.py::test_frozen_two_state_contract` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a019a.py::test_historical_schedule_from_tracked_metadata_only` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a019a.py::test_b_starts_fresh_after_a_released_using_same_runtime_and_graph` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a019a.py::test_a019a_checks_have_no_real_execution_and_preserve_defaults` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a018uj.py::test_independent_frozen_artifact_reconstruction_and_provenance` | S2 | NOT RUN | NOT RUN |
| `tests/test_application_a018uj.py::test_each_mandatory_layer_mismatch_fails` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a018uj.py::test_correct_tuple_and_cross_layer_rejection` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a018uj.py::test_ambiguous_legacy_fields_rejected` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a018uj.py::test_no_real_execution_and_scientific_default_unchanged` | S2 | NOT RUN | NOT RUN |
| `tests/test_application_a018ui.py::test_historical_identity_layer_reconstruction` | S1 | NOT RUN | NOT RUN |
| `tests/test_application_a018ui.py::test_historical_current_components_exact` | S1 | NOT RUN | NOT RUN |
| `tests/test_application_a018ui.py::test_metadata_and_diagnostic_bytes` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a018ui.py::test_effective_digest_field_order` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a018ui.py::test_historical_preparation_and_committed_fingerprints` | S1 | NOT RUN | NOT RUN |
| `tests/test_application_a018ui.py::test_production_default_and_frozen_expectation_unchanged` | S1 | NOT RUN | NOT RUN |
| `tests/test_application_a018ur.py::test_success_exact_identity_no_advance_default_restored` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a018ur.py::test_identity_mismatch_stops_and_cleans` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a018ur.py::test_failure_cleanup_and_fallback_prevented` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a018ur.py::test_exact_frozen_constants_and_no_execution_entrypoints` | S0 | NOT RUN | PASS (historical R10) |
| `tests/test_application_a018ur.py::test_supervisor_time_failure_cleans_without_retry` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a018ur.py::test_supervisor_success_boundary_handshake` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a018u.py::test_instrumented_oracle_exact` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018u.py::test_missing_metadata_and_policy_contract` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018u.py::test_large_safe_exact` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018u.py::test_large_integer_identity` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018u.py::test_default_has_no_probe` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018u.py::test_synthetic_bounds` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018t.py::test_exact_oracle_ownership_release` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018t.py::test_prepared_scientific_oracle` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018t.py::test_compaction_releases_capacity` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018t.py::test_many_small_schedule_determinism` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018t.py::test_partition_and_stage_release` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018t.py::test_overflow_reference_fallback` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018t.py::test_production_default` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018t.py::test_closed_boundaries` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018t.py::test_large_ids_and_invalid_block` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018t.py::test_equal_key_on_either_slice_endpoint` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018t.py::test_seeded_partition_block_invariance` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018s.py::test_exact_oracle_ownership_release` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018s.py::test_prepared_scientific_oracle` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018s.py::test_compaction_releases_capacity` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018s.py::test_many_small_schedule_determinism` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018s.py::test_partition_and_stage_release` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018s.py::test_overflow_reference_fallback` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018s.py::test_production_default` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018.py::test_runs_exact_deterministic_and_lifetime` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018.py::test_downstream_partition_exact` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018.py::test_overflow_rejection` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018.py::test_completed_stage_inputs_reclaimable` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018.py::test_overflow_loader_fallback` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018.py::test_schedule_partition_invariance` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018.py::test_fan_in_composition_invariance` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a018.py::test_production_default` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a017.py::test_exact_downstream` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a017.py::test_integer_domain_and_merge` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a017.py::test_lifetime_bounds_and_no_partial_threshold` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a017.py::test_invalid_excluded_upstream` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a017.py::test_scale_exact` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a017.py::test_production_dispatch_unchanged` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a017.py::test_overflow_oracle_fallback` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a017.py::test_high_cardinality_exact` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a016.py::test_boundaries_exact` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a016.py::test_invalid_boundary` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a016.py::test_reader_projection_admission_lifetime` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a016.py::test_v1_rejected` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a016.py::test_scale_exact` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a016.py::test_masks_released_numeric_ownership` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a016.py::test_noninteger_schema_rejected` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a015.py::test_exact_adversarial` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a015.py::test_high_exclusion_scale` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a015.py::test_membership_exact` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a015.py::test_authoritative_membership_and_no_identity_collapse` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a015.py::test_invalid_excluded_rows_rejected` | S0 | NOT RUN | PASS (historical R11) |
| `tests/test_application_a014.py::test_tree_memory_enforcement` | S1 | NOT RUN | PASS (historical R14) |
| `tests/test_application_a014.py::test_aggregate_limit_without_individual_offender` | S1 | NOT RUN | PASS (historical R14) |
| `tests/test_application_a014.py::test_normal_exit` | S1 | NOT RUN | PASS (historical R14) |
| `tests/test_application_a014.py::test_accounting_failure_stops_tree` | S1 | NOT RUN | PASS (historical R14) |
| `tests/test_application_a014.py::test_instrumentation_opt_in_and_exact_identity` | S0 | NOT RUN | PASS (historical R14) |
| `tests/test_application_a013.py::test_limits_and_cpu_only` | S0 | NOT RUN | PASS |
| `tests/test_application_a013.py::test_one_preparation` | S0 | NOT RUN | PASS |
| `tests/test_application_a013.py::test_watchdog_stops` | S0 | NOT RUN | PASS |
| `tests/test_application_a013.py::test_percentiles_and_warmup_exclusion` | S0 | NOT RUN | PASS |
| `tests/test_application_a013.py::test_schedule_is_complete_grid_slices_and_reused` | S0 | NOT RUN | PASS |
| `tests/test_application_a013.py::test_two_fresh_states_exact_twenty_four_advances_and_replay` | S0 | NOT RUN | PASS |
| `tests/test_application_a013.py::test_mismatch_fails_at_first_component` | S0 | NOT RUN | PASS |
| `tests/test_application_a013.py::test_canonical_digest_exact_and_endian_stable` | S0 | NOT RUN | PASS |
| `tests/test_application_a013.py::test_pending_guard` | S0 | NOT RUN | PASS |
| `tests/test_application_a013.py::test_no_download_arena_gpu_or_import_execution` | S0 | NOT RUN | PASS |
| `tests/test_application_a013.py::test_refuse_existing_output` | S0 | NOT RUN | PASS |
| `tests/test_application_a013.py::test_watchdog_binds_worker_not_launcher` | S0 | NOT RUN | PASS |
| `tests/test_application_a013.py::test_native_watchdog_can_terminate_actual_redirected_python` | S1 | NOT RUN | PASS |
| `tests/test_application_a011.py::test_exact_continuity` | S0 | NOT RUN | PASS |
| `tests/test_application_a011.py::test_initial_state_and_identity` | S0 | NOT RUN | PASS |
| `tests/test_application_a011.py::test_clocks_controls_reset_replay` | N | NOT RUN | NOT RUN |
| `tests/test_application_a011.py::test_encoder_decoder_bounds_and_invalid_contracts` | N | NOT RUN | NOT RUN |
| `tests/test_application_a011.py::test_synthetic_visible_response_and_intervention` | N | NOT RUN | NOT RUN |
| `tests/test_application_a011.py::test_render_speed_cannot_change_backend` | N | NOT RUN | NOT RUN |
| `tests/test_application_a011.py::test_http_ui_assets_and_commands` | N | NOT RUN | NOT RUN |
| `tests/test_application_a008.py::test_reproducibility_contracts_and_packaged_assets` | S0 | PASS | PASS |
| `tests/test_application_a008.py::test_application_docs_are_portable_and_do_not_embed_session_urls` | S0 | PASS | PASS |
| `tests/test_application_a007c.py::test_synthetic_production_api_and_assets` | S1 | PASS | FAIL |
| `tests/test_application_a007c.py::test_authoritative_backend_firewall_and_packaging` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_spec_serialization_identity_and_no_verdict` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_invalid_variant_allowlist` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_cross_variant_event_schedule` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_full_sweep_and_retention_stress` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_exact_reuse_and_mixed_provenance` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_cancel_preserves_completed_evidence` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_stop_on_failure` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_mixed_child_reuse_after_cancellation` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_parent_byte_bound_preserves_earlier_evidence` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_identity_and_graph_mismatch_rejected` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_session_host_origin_and_synthetic_api` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_cpu_startup_cuda_lazy` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_schedule_gap_stops_before_execution` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_all_children_reused_without_execution` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_cancel_before_first_child` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_child_capacity_and_parent_limits` | S0 | PASS | NOT RUN |
| `tests/test_application_a007b.py::test_strict_request_contract` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_exact_variant_contract` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_reference_and_weight_coupling` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_allowlisted_sign_policy` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_invalid_preparation` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_nonfinite_parameters` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_reject_unbounded_client_input` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_true_preparation_and_execution` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_ordinary_reference_bytes_and_known_certified_identities` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_same_variant_pairing` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_cross_variant_rejected` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_sixteen_children_survive_recent_eviction` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_parent_byte_limit_and_snapshot` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_no_historical_runner_dependency` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_cuda_receives_equivalent_configuration` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_variant_cuda_unavailable_is_explicit` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_closed_session_cannot_admit_parent` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_frozen_preset_digest` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_parent_child_capacity` | S0 | PASS | NOT RUN |
| `tests/test_application_a007a.py::test_derived_input_must_remain_finite` | S0 | PASS | NOT RUN |
| `tests/test_application_a006r.py::test_visible_run_transitions` | S1 | FAIL | NOT RUN |
| `tests/test_application_a006.py::test_pair_metrics_digest_and_zero_baseline` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a006.py::test_nonzero_deltas_and_deterministic_identity` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a006.py::test_mismatch_rejected` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a006.py::test_schedule_and_incomplete_rejected` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a006.py::test_union_playback_and_recorded_zero` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a006.py::test_comparison_api_session_and_backend_export` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a005.py::test_post_update_spike_time_grid` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a005.py::test_sparse_payload_identity_digest_and_no_fabricated_events` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a005.py::test_deterministic_raster_order` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a005.py::test_payload_rejects_nonfinite_trace_and_size_cap` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a005.py::test_playback_endpoint_session_and_completion_gate` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a004.py::test_long_identity_layout_has_shared_wrap_rule` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a004.py::test_view_determinism_identity_and_cap` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a004.py::test_target_and_combined_context` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a004.py::test_rejects_unbounded_or_unknown_filter` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a004.py::test_subgraph_route_bounds_session_failure_and_pending` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a003.py::test_loopback_catalog_security_and_ui` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a003.py::test_previous_process_token_is_rejected` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a003.py::test_history_limit_is_fixed` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields` | S2 | NOT RUN | NOT RUN |
| `tests/test_application_a003.py::test_validate_and_run_requests_share_exact_spec_identity` | S2 | NOT RUN | NOT RUN |
| `tests/test_application_a003.py::test_manager_retains_safe_failure` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a003.py::test_manager_evicts_oldest_completed_job` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a003.py::test_result_events_and_backend_export_routes` | S2 | NOT RUN | NOT RUN |
| `tests/test_application_a002.py::test_spec_validation_and_canonical_identity` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a002.py::test_final_grid_step_spike_is_valid` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a002.py::test_spike_outside_engine_grid_is_rejected` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a002.py::test_nonfinite_spike_step_is_rejected` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a002.py::test_equal_timestep_spikes_have_deterministic_neuron_order` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a002.py::test_invalid_top_level` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a002.py::test_invalid_stimulus_and_finite_values` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a002.py::test_state_events_and_no_fake_progress` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a002.py::test_comparison_spikes_and_robustness_contract` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a002.py::test_optional_git_provenance` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a002.py::test_cpu_only_import_and_cuda_unavailable` | S0 | NOT RUN | NOT RUN |
| `tests/test_application_a002.py::test_non_scientific_synthetic_engine_integration` | S0 | NOT RUN | NOT RUN |
| `tests/test_task005.py::test_reference_parameters_are_explicit_and_grid_is_exact` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_linear_update_matches_analytical_solution` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_resting_neuron_and_synaptic_decay` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_positive_and_negative_direct_impulses_have_expected_polarity` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_threshold_reset_and_g_reset` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_refractory_blocks_input_until_strictly_after_2_2_ms` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_incoming_event_during_refractory_is_ignored_and_poisson_targets_can_opt_out` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_exact_delay_and_signed_sparse_propagation` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_self_edge_and_two_neuron_inhibitory_edge_are_supported` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_multiple_and_simultaneous_events_sum_deterministically` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_unresolved_edges_are_excluded_and_anatomy_is_unchanged` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_explicit_stimulus_is_sorted_reproducible_and_validates_ids_and_grid` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_seeded_poisson_is_reproducible_and_uses_reference_scaling` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_silencing_disables_outgoing_only` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_fingerprints_and_result_digest_are_deterministic_and_identity_sensitive` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_effective_weight_preserves_anatomical_count_boundary` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_effective_inhibitory_weight_uses_presynaptic_sign` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_two_neuron_chain_keeps_spike_output_compact` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_simulation_reports_identity_metadata` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_parameter_identity_changes_simulation_configuration` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_duration_must_be_on_the_discrete_clock` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_duplicate_schedule_times_are_additive` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_poisson_rejects_more_than_one_expected_event_per_step` | S0 | NOT RUN | PASS |
| `tests/test_task005.py::test_trace_requires_an_explicit_small_subset` | S0 | NOT RUN | PASS |
| `tests/test_application_a019c_r16_firewall.py::test_exact_node_grammar_and_negative_controls` | S1 | PASS | N/A new R16 control |

Command nodes: compileall S1 NOT RUN; diff check S1 NOT RUN after STOP; metadata inventory/identity S1 PASS; safe source inspection S1 PASS; fresh CLI S0 NOT RUN; integrity S2 I2 NOT RUN; full pytest S2 NOT RUN; build S1 B2 NOT RUN. Full-real/GPU/Arena/science/download/archive and tag/release/version mutation N NOT EXECUTED. Commit/push N NOT EXECUTED because success prerequisite failed.
