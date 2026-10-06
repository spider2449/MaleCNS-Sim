# A019C-R17 A006R inline Node adjudication

Authorization: ?? A019C-R17. Starting HEAD/local/origin/live: `60c900b0c8e5a02ea95efc7340fd190193edf7e9`.

Plan: inventory; static audit; one pre-fix test; exact-script correction; single test; full admitted application set; Node controls; bootstrap; harness and fresh CLI; affected Python controls; compileall/diff; manifest; conditional commit/push.

I1 selected. Historical source is transport, not a text identity contract. Node VM/Promise/DOM semantics are required. The fixed fixture preserves the entire source after a two-line argv adapter: inline argv[1] STATIC becomes script argv[2] STATIC before historical code runs. Same production run-status.js, style.css and app.js, synthetic job/evidence and assertions. No real input.

Historical inline SHA256: `68120c63c86df3941d938565589f08425119d43b63a2db855756ba27da5c682e`. Exact source retained below.

```javascript

const fs = require('fs'), vm = require('vm'), assert = require('assert');
const elements = new Map();
function $(id) {
 if (!elements.has(id)) elements.set(id,{textContent:'',hidden:true,disabled:false,value:'',dataset:{},classList:{toggle(){}},selectedOptions:[]});
 return elements.get(id);
}
let now = 100000;
const context = vm.createContext({$, Date, setInterval(){}, validSelection:{}, activeJob:null, api:async()=>({runs:[]}), error(){}, loadRunHistory:async()=>{}});
vm.runInContext(fs.readFileSync(process.argv[1]+'/run-status.js','utf8'),context);
function run(code){return vm.runInContext(code,context);}
run('acceptRun({job_id:"b4c124cd1234",spec_digest:"digest"},"none")');
assert.equal($('run').disabled,true); assert.match($('run').textContent,/Running/);
assert.match($('run-heading').textContent,/ACTIVE.*BASELINE/);
assert.match($('run-job').textContent,/b4c124cd/);
assert.equal($('compare-create-intervention').disabled,true);
for(const [state,label] of Object.entries({VALIDATING:'Validating experiment',LOADING_DATA:'Loading dataset',PREPARING_NETWORK:'Preparing simulation network',RUNNING:'Running simulation',FINALIZING:'Finalizing result'})){
 run(`executingRun.state=${JSON.stringify(state)}; renderRunStatus()`);
 assert.match($('run-phase').textContent,new RegExp(label));
 assert.equal($('execution-overlay').hidden,false);
 assert(!/\d+%/.test($('run-status').textContent+$('run-phase').textContent));
}
run('executingRun.startedAt=1000; executingRun.state="RUNNING"');
assert.equal(run('runPresentation(executingRun,278000).elapsed'),'04:37');
run('activeJob="previous123"; renderRunStatus()');
assert.match($('previous-result').textContent,/Viewing previous result.*previous/);
assert.match($('execution-overlay').textContent,/Job b4c124cd.*Viewing previous result/);
run('executingRun.mode="outgoing_silence"; renderRunStatus()');
assert.match($('compare-active').textContent,/INTERVENTION running/);
run('executingRun.trialText="Completed trials 1 / 2"; renderRunStatus()');
assert.equal($('run-summary').textContent,'Completed trials 1 / 2');
for(const [state,label] of Object.entries({COMPLETED:'Run completed',FAILED:'Run failed',CANCELLED:'Run cancelled'})){
 run(`executingRun.state=${JSON.stringify(state)}; executingRun.endedAt=278000; renderRunStatus()`);
 assert.equal($('run').disabled,false);assert.equal($('run-status').hidden,false);
 assert.match($('run-phase').textContent,new RegExp(label));
 assert.equal($('execution-overlay').hidden,true);
 assert.equal(run('runPresentation(executingRun,999999).elapsed'),'04:37');
}
run('executingRun.state="FAILED"; executingRun.error={code:"SIMULATION_FAILED",message:"local run failed"}; renderRunStatus()');
assert.equal($('run-summary').textContent,'SIMULATION_FAILED: local run failed');
assert.match($('active-identity').textContent,/A002 run identity: pending.*?/);
run('executingRun=null;submittingRun=true;updateRunControls()');assert.equal($('run').disabled,true);
assert.equal($('run').textContent,'Submitting...');
const css=fs.readFileSync(process.argv[1]+'/style.css','utf8');
assert.match(css,/@media\(prefers-reduced-motion:reduce\).*animation:none/);
assert.match(css,/#run-status\{position:sticky/);
const app=fs.readFileSync(process.argv[1]+'/app.js','utf8');
assert.match(app,/if\(!validSelection\|\|runBusy\(\)\)return/);
assert.match(app,/acceptRun\(response,validSelection.mode\);watch/);
assert.match(app,/ACTIVE - /);
(async()=>{
 run('executingRun=null;submittingRun=false;activeJob=null');
 let resolveRequest, requests=0;
 context.api=()=>{requests++;return new Promise(resolve=>{resolveRequest=resolve;});};
 context.error=()=>{};context.watch=()=>{};
 let click;
 $('run').addEventListener=(event,handler)=>{click=handler;};
 const handler=app.split('\n').find(line=>line.startsWith('$("run").addEventListener'));
 run(handler);
 const request=click(); assert.equal($('run').disabled,true);
 await click();assert.equal(requests,1);
 resolveRequest({job_id:'accepted123',spec_digest:'accepted-digest'});await request;
 assert.match($('run-heading').textContent,/ACTIVE/);assert.match($('run-job').textContent,/accepted/);
 const backend={job_id:'accepted123',state:'PREPARING_NETWORK',run_id:'real-identity',spec_digest:'accepted-digest',spec:{intervention:{kind:'none'}}};
 context.api=async(path)=>path==='/api/runs'?{runs:[backend]}:path.endsWith('/events')?{events:[{timestamp:'2026-10-02T00:00:00Z',payload:{}},{payload:{completed_trials:1,total_trials:2}}]}:backend;
 await run('pollRunStatus()');
 assert.match($('run-phase').textContent,/Preparing simulation network/);
 assert.match($('active-identity').textContent,/real-identity/);
 assert.equal($('run-summary').textContent,'Completed trials 1 / 2');
 backend.state='CANCELLED';await run('pollRunStatus()');
 assert.equal($('run').disabled,false);assert.match($('run-phase').textContent,/Run cancelled/);
})().catch(e=>{console.error(e);process.exitCode=1;});

```

Pre-fix argv: `[C:\Program Files\nodejs\node.EXE, -e, SOURCE_ABOVE, D:\spider\working\MaleCNS-Sim\src\malecns_sim\application\static]`. Node 24.13.0. cwd repository root; inherited environment with mandatory activation, absolute firewall PYTHONPATH, TEMP/TMP=C:/TEMP and audit log C:/TEMP/a019c-r17-prefix.jsonl. Expected stdout/stderr empty and exit 0; subprocess waits/closes pipes, no descendants expected. Result 1 FAIL: guarded_command unsupported A019 child executable before Popen/CreateProcess; Node/JS did not start. This is not an application behavior failure.

Correction: fixture-only source transport plus exact A006R validation-only admission using the R16 architecture, distinct purpose. No production files changed. Generic Node/eval/shell/alternate forms remain denied. Historical R10-R16 records retained; J2/I2/B2 NOT RUN. Results pending.

## Exact initial inventory: 37 scoped paths

```text
 M tests/test_application_a007c.py
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
?? docs/plans/2026-10-06-application-a019c-r16-a007c-node-validation.md
?? docs/plans/2026-10-06-application-a019c-r3-native-process-firewall-coverage.md
?? docs/plans/2026-10-06-application-a019c-r4-inherited-child-fail-closed.md
?? docs/plans/2026-10-06-application-a019c-r5-windows-mandatory-child-audit.md
?? docs/plans/2026-10-06-application-a019c-r6-contained-worker-cleanup.md
?? docs/plans/2026-10-06-application-a019c-r7-live-process-tree-cleanup.md
?? docs/plans/2026-10-06-application-a019c-r8-obsolete-child-guard-regression.md
?? docs/plans/2026-10-06-application-a019c-r9-validation-firewall-integration.md
?? scripts/a019c_firewall/a007c_node.cjs
?? scripts/a019c_firewall/a007c_node.py
?? scripts/a019c_firewall/a014_direct_control.py
?? scripts/a019c_firewall/guarded_child.py
?? scripts/a019c_firewall/sitecustomize.py
?? scripts/a019c_firewall/validation_firewall.py
?? scripts/benchmark_application_a019.py
?? tests/fixtures/application-a019c-preparation-identity.json
?? tests/test_application_a019c.py
?? tests/test_application_a019c_r12_firewall.py
?? tests/test_application_a019c_r16_firewall.py
?? tests/test_application_a019c_r2_firewall.py
?? tests/test_application_a019c_r3_firewall.py
?? tests/test_application_a019c_r4_firewall.py
?? tests/test_application_a019c_r5_firewall.py
```

Unrelated WIP No; initial tracked diff 4 files, 197 insertions, 9 deletions. Staging/stash empty. R16 H2, its exact A007C controls and all historical STOP outcomes retained.

## Actual results and mandatory STOP

Corrected A006R single: 1 PASS, exit 0, 0.16 s. Parent PID 17512, Node PID 8640; guard/script/workload markers present, historical assertions completed. Direct payload read blocked before content; descendant probe blocked before creation. Normal exit and pipes closed; scoped CIM scan found no Node PID 8640 or A006R/A007C task processes. No orphan observed.

Complete application S0/S1: **131 PASS, 1 FAIL**, 23.95 s, exit 1. A006R and A007C PASS. Distinct blocker: `tests/test_application_a002.py::test_optional_git_provenance`, assertion `_git_provenance()["git_commit"]` returned None. Static explanation: service.py invokes bare git subprocess forms; guard rejects non-admitted executable and service catches OSError, returning None. This is static evidence, not a separately instrumented Git invocation. No correction/retry made.

**A19C-R17-APPLICATION-VALIDATION-BLOCKER**. All dependent gates STOP. A007C exact execution passed in application selection; full Node negative-control regression NOT RUN. New equivalence/control tests written before the application failure arrived, but NOT RUN. Generic Node/arbitrary JS/eval/shell/alternate executable/script/purpose remain excluded by exact source grammar; fresh negative-control certification pending.

Bootstrap 39, harness 35, fresh CLI, affected A013/A014/Stateful/A011 controls, compileall and final diff check: NOT RUN after STOP. Historical R15 39/35/CLI/27 PASS preserved but not current recertification: shared admission dispatcher changed, so Python forms require renewed controls. FIREWALL_BOOTSTRAP_CERTIFIED historical only.

J2 prohibited data diff, I2 integrity, B2 build: NOT RUN, preserved. Full pytest: NOT RUN ? synthetic-only authorization; known S2 real-data tests excluded.

## Exact admitted runtime argv

```json
[
  {
    "kind": "trusted_node_admitted",
    "pid": 17512,
    "argv": [
      "C:\\Program Files\\nodejs\\node.exe",
      "--permission",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\scripts\\a019c_firewall\\a006r_node.cjs",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\tests\\js\\application_a006r.cjs",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\src\\malecns_sim\\application\\static\\run-status.js",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\src\\malecns_sim\\application\\static\\style.css",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\src\\malecns_sim\\application\\static\\app.js",
      "D:\\spider\\working\\MaleCNS-Sim\\scripts\\a019c_firewall\\a006r_node.cjs",
      "a006r-visible-run-contract-v1",
      "D:\\spider\\working\\MaleCNS-Sim\\src\\malecns_sim\\application\\static"
    ],
    "cwd": "D:\\spider\\working\\MaleCNS-Sim"
  },
  {
    "kind": "trusted_node_admitted",
    "pid": 13868,
    "argv": [
      "C:\\Program Files\\nodejs\\node.exe",
      "--permission",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\scripts\\a019c_firewall\\a007c_node.cjs",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\tests\\js\\application_a007c.cjs",
      "--allow-fs-read=C:\\TEMP\\a019c-r17-application\\test_synthetic_production_api_0\\evidence.json",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\src\\malecns_sim\\application\\static\\compare.js",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\src\\malecns_sim\\application\\static\\robustness.js",
      "D:\\spider\\working\\MaleCNS-Sim\\scripts\\a019c_firewall\\a007c_node.cjs",
      "a007c-synthetic-dom-contract-v1",
      "C:\\TEMP\\a019c-r17-application\\test_synthetic_production_api_0\\evidence.json",
      "D:\\spider\\working\\MaleCNS-Sim\\src\\malecns_sim\\application\\static"
    ],
    "cwd": "D:\\spider\\working\\MaleCNS-Sim"
  },
  {
    "kind": "trusted_node_admitted",
    "pid": 13868,
    "argv": [
      "C:\\Program Files\\nodejs\\node.exe",
      "--permission",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\scripts\\a019c_firewall\\a006r_node.cjs",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\tests\\js\\application_a006r.cjs",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\src\\malecns_sim\\application\\static\\run-status.js",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\src\\malecns_sim\\application\\static\\style.css",
      "--allow-fs-read=D:\\spider\\working\\MaleCNS-Sim\\src\\malecns_sim\\application\\static\\app.js",
      "D:\\spider\\working\\MaleCNS-Sim\\scripts\\a019c_firewall\\a006r_node.cjs",
      "a006r-visible-run-contract-v1",
      "D:\\spider\\working\\MaleCNS-Sim\\src\\malecns_sim\\application\\static"
    ],
    "cwd": "D:\\spider\\working\\MaleCNS-Sim"
  }
]
```

Runtime Node 24.13.0 from R16 installed-runtime record; no Node version subprocess admitted in R17. Environment sanitized by the unchanged R16 helper: NODE_* and OPENSSL_CONF removed; mandatory activation retained; exact ROOT cwd, close_fds=True, timeout 30 s. No shell. Permissions grant individual fixed scripts/assets only. A006R purpose a006r-visible-run-contract-v1, A007C purpose a007c-synthetic-dom-contract-v1.

## Final per-node manifest

No unclassified nodes; validation closure remains incomplete because required nodes FAIL or NOT RUN. Parameterized cases aggregate by function. Historical results remain in R16/R15 records.

| Node | Class | R17 result |
|---|---|---|
| `tests/test_application_a019c_r5_firewall.py::test_canonical_serialization` | S0 | NOT RUN |
| `tests/test_application_a019c_r5_firewall.py::test_false_positive_rejected` | S0 | NOT RUN |
| `tests/test_application_a019c_r5_firewall.py::test_malformed_rejected` | S0 | NOT RUN |
| `tests/test_application_a019c_r5_firewall.py::test_actual_windows_audit_serialization` | S0 | NOT RUN |
| `tests/test_application_a019c_r5_firewall.py::test_actual_worker_bypass_rejected` | S0 | NOT RUN |
| `tests/test_application_a019c_r5_firewall.py::test_script_path_with_spaces` | S0 | NOT RUN |
| `tests/test_application_a019c_r5_firewall.py::test_contained_actual_worker_startup` | S0 | NOT RUN |
| `tests/test_application_a019c_r5_firewall.py::test_live_contained_descendant_cleanup` | S0 | NOT RUN |
| `tests/test_application_a019c_r4_firewall.py::test_parent_native_control_and_categories` | S0 | NOT RUN |
| `tests/test_application_a019c_r4_firewall.py::test_required_child_rejects_before_workload` | S0 | NOT RUN |
| `tests/test_application_a019c_r4_firewall.py::test_normal_public_native_child` | S0 | NOT RUN |
| `tests/test_application_a019c_r4_firewall.py::test_actual_worker_startup` | S0 | NOT RUN |
| `tests/test_application_a019c_r4_firewall.py::test_inherited_activation_removed_parent_rejects` | S0 | NOT RUN |
| `tests/test_application_a019c_r3_firewall.py::test_01_valid_native_synthetic_control` | S0 | NOT RUN |
| `tests/test_application_a019c_r3_firewall.py::test_02_native_registered_source_denied_before_constructor` | S0 | NOT RUN |
| `tests/test_application_a019c_r3_firewall.py::test_03_python_child_native_guard` | S0 | NOT RUN |
| `tests/test_application_a019c_r3_firewall.py::test_04_missing_inherited_guard_fails_closed` | S0 | NOT RUN |
| `tests/test_application_a019c_r2_firewall.py::test_blocked_before_content` | S0 | NOT RUN |
| `tests/test_application_a019c_r2_firewall.py::test_generated_and_temp_and_source_allowed` | S0 | NOT RUN |
| `tests/test_application_a019c_r2_firewall.py::test_subprocess_guard` | S0 | NOT RUN |
| `tests/test_application_a019c_r2_firewall.py::test_child_cannot_drop_guard` | S0 | NOT RUN |
| `tests/test_application_a019c_r2_firewall.py::test_native_reader_denies_synthetic_sentinel` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_full_structure_route_lifetime_replay_and_defaults` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_each_gate_stops_before_runtime_one_preparation` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_cross_layer_rejected` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_fallback_hard_stop` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_induced_failure_no_retry` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_exact_resource_limits` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_contained_tree_forced_stops_no_orphan` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_synthetic_cli_contained_success` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_synthetic_source_guard_before_access` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_timing_structure_and_historical_default` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_completed_preparation_deadline_before_runtime` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_completed_call_deadline_no_retry` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_watchdog_instrumentation_failure_terminates_tree` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_contract_schema_matches_success_evidence` | S0 | NOT RUN |
| `tests/test_application_a019c.py::test_watchdog_child_memory_stop_aggregate_and_cleanup` | S0 | NOT RUN |
| `tests/test_application_a019a.py::test_frozen_two_state_contract` | S0 | NOT RUN |
| `tests/test_application_a019a.py::test_historical_schedule_from_tracked_metadata_only` | S0 | NOT RUN |
| `tests/test_application_a019a.py::test_b_starts_fresh_after_a_released_using_same_runtime_and_graph` | S0 | NOT RUN |
| `tests/test_application_a019a.py::test_a019a_checks_have_no_real_execution_and_preserve_defaults` | S0 | NOT RUN |
| `tests/test_application_a018uj.py::test_independent_frozen_artifact_reconstruction_and_provenance` | S2 | NOT RUN |
| `tests/test_application_a018uj.py::test_each_mandatory_layer_mismatch_fails` | S0 | NOT RUN |
| `tests/test_application_a018uj.py::test_correct_tuple_and_cross_layer_rejection` | S0 | NOT RUN |
| `tests/test_application_a018uj.py::test_ambiguous_legacy_fields_rejected` | S0 | NOT RUN |
| `tests/test_application_a018uj.py::test_no_real_execution_and_scientific_default_unchanged` | S2 | NOT RUN |
| `tests/test_application_a018ui.py::test_historical_identity_layer_reconstruction` | S1 | NOT RUN |
| `tests/test_application_a018ui.py::test_historical_current_components_exact` | S1 | NOT RUN |
| `tests/test_application_a018ui.py::test_metadata_and_diagnostic_bytes` | S0 | NOT RUN |
| `tests/test_application_a018ui.py::test_effective_digest_field_order` | S0 | NOT RUN |
| `tests/test_application_a018ui.py::test_historical_preparation_and_committed_fingerprints` | S1 | NOT RUN |
| `tests/test_application_a018ui.py::test_production_default_and_frozen_expectation_unchanged` | S1 | NOT RUN |
| `tests/test_application_a018ur.py::test_success_exact_identity_no_advance_default_restored` | S0 | NOT RUN |
| `tests/test_application_a018ur.py::test_identity_mismatch_stops_and_cleans` | S0 | NOT RUN |
| `tests/test_application_a018ur.py::test_failure_cleanup_and_fallback_prevented` | S0 | NOT RUN |
| `tests/test_application_a018ur.py::test_exact_frozen_constants_and_no_execution_entrypoints` | S0 | NOT RUN |
| `tests/test_application_a018ur.py::test_supervisor_time_failure_cleans_without_retry` | S0 | NOT RUN |
| `tests/test_application_a018ur.py::test_supervisor_success_boundary_handshake` | S0 | NOT RUN |
| `tests/test_application_a018u.py::test_instrumented_oracle_exact` | S0 | NOT RUN |
| `tests/test_application_a018u.py::test_missing_metadata_and_policy_contract` | S0 | NOT RUN |
| `tests/test_application_a018u.py::test_large_safe_exact` | S0 | NOT RUN |
| `tests/test_application_a018u.py::test_large_integer_identity` | S0 | NOT RUN |
| `tests/test_application_a018u.py::test_default_has_no_probe` | S0 | NOT RUN |
| `tests/test_application_a018u.py::test_synthetic_bounds` | S0 | NOT RUN |
| `tests/test_application_a018t.py::test_exact_oracle_ownership_release` | S0 | NOT RUN |
| `tests/test_application_a018t.py::test_prepared_scientific_oracle` | S0 | NOT RUN |
| `tests/test_application_a018t.py::test_compaction_releases_capacity` | S0 | NOT RUN |
| `tests/test_application_a018t.py::test_many_small_schedule_determinism` | S0 | NOT RUN |
| `tests/test_application_a018t.py::test_partition_and_stage_release` | S0 | NOT RUN |
| `tests/test_application_a018t.py::test_overflow_reference_fallback` | S0 | NOT RUN |
| `tests/test_application_a018t.py::test_production_default` | S0 | NOT RUN |
| `tests/test_application_a018t.py::test_closed_boundaries` | S0 | NOT RUN |
| `tests/test_application_a018t.py::test_large_ids_and_invalid_block` | S0 | NOT RUN |
| `tests/test_application_a018t.py::test_equal_key_on_either_slice_endpoint` | S0 | NOT RUN |
| `tests/test_application_a018t.py::test_seeded_partition_block_invariance` | S0 | NOT RUN |
| `tests/test_application_a018s.py::test_exact_oracle_ownership_release` | S0 | NOT RUN |
| `tests/test_application_a018s.py::test_prepared_scientific_oracle` | S0 | NOT RUN |
| `tests/test_application_a018s.py::test_compaction_releases_capacity` | S0 | NOT RUN |
| `tests/test_application_a018s.py::test_many_small_schedule_determinism` | S0 | NOT RUN |
| `tests/test_application_a018s.py::test_partition_and_stage_release` | S0 | NOT RUN |
| `tests/test_application_a018s.py::test_overflow_reference_fallback` | S0 | NOT RUN |
| `tests/test_application_a018s.py::test_production_default` | S0 | NOT RUN |
| `tests/test_application_a018.py::test_runs_exact_deterministic_and_lifetime` | S0 | NOT RUN |
| `tests/test_application_a018.py::test_downstream_partition_exact` | S0 | NOT RUN |
| `tests/test_application_a018.py::test_overflow_rejection` | S0 | NOT RUN |
| `tests/test_application_a018.py::test_completed_stage_inputs_reclaimable` | S0 | NOT RUN |
| `tests/test_application_a018.py::test_overflow_loader_fallback` | S0 | NOT RUN |
| `tests/test_application_a018.py::test_schedule_partition_invariance` | S0 | NOT RUN |
| `tests/test_application_a018.py::test_fan_in_composition_invariance` | S0 | NOT RUN |
| `tests/test_application_a018.py::test_production_default` | S0 | NOT RUN |
| `tests/test_application_a017.py::test_exact_downstream` | S0 | NOT RUN |
| `tests/test_application_a017.py::test_integer_domain_and_merge` | S0 | NOT RUN |
| `tests/test_application_a017.py::test_lifetime_bounds_and_no_partial_threshold` | S0 | NOT RUN |
| `tests/test_application_a017.py::test_invalid_excluded_upstream` | S0 | NOT RUN |
| `tests/test_application_a017.py::test_scale_exact` | S0 | NOT RUN |
| `tests/test_application_a017.py::test_production_dispatch_unchanged` | S0 | NOT RUN |
| `tests/test_application_a017.py::test_overflow_oracle_fallback` | S0 | NOT RUN |
| `tests/test_application_a017.py::test_high_cardinality_exact` | S0 | NOT RUN |
| `tests/test_application_a016.py::test_boundaries_exact` | S0 | NOT RUN |
| `tests/test_application_a016.py::test_invalid_boundary` | S0 | NOT RUN |
| `tests/test_application_a016.py::test_reader_projection_admission_lifetime` | S0 | NOT RUN |
| `tests/test_application_a016.py::test_v1_rejected` | S0 | NOT RUN |
| `tests/test_application_a016.py::test_scale_exact` | S0 | NOT RUN |
| `tests/test_application_a016.py::test_masks_released_numeric_ownership` | S0 | NOT RUN |
| `tests/test_application_a016.py::test_noninteger_schema_rejected` | S0 | NOT RUN |
| `tests/test_application_a015.py::test_exact_adversarial` | S0 | NOT RUN |
| `tests/test_application_a015.py::test_high_exclusion_scale` | S0 | NOT RUN |
| `tests/test_application_a015.py::test_membership_exact` | S0 | NOT RUN |
| `tests/test_application_a015.py::test_authoritative_membership_and_no_identity_collapse` | S0 | NOT RUN |
| `tests/test_application_a015.py::test_invalid_excluded_rows_rejected` | S0 | NOT RUN |
| `tests/test_application_a014.py::test_tree_memory_enforcement` | S1 | NOT RUN |
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
| `tests/test_application_a011.py::test_clocks_controls_reset_replay` | N | NOT RUN |
| `tests/test_application_a011.py::test_encoder_decoder_bounds_and_invalid_contracts` | N | NOT RUN |
| `tests/test_application_a011.py::test_synthetic_visible_response_and_intervention` | N | NOT RUN |
| `tests/test_application_a011.py::test_render_speed_cannot_change_backend` | N | NOT RUN |
| `tests/test_application_a011.py::test_http_ui_assets_and_commands` | N | NOT RUN |
| `tests/test_application_a008.py::test_reproducibility_contracts_and_packaged_assets` | S0 | PASS |
| `tests/test_application_a008.py::test_application_docs_are_portable_and_do_not_embed_session_urls` | S0 | PASS |
| `tests/test_application_a007c.py::test_synthetic_production_api_and_assets` | S1 | PASS |
| `tests/test_application_a007c.py::test_authoritative_backend_firewall_and_packaging` | S0 | PASS |
| `tests/test_application_a007b.py::test_spec_serialization_identity_and_no_verdict` | S0 | PASS |
| `tests/test_application_a007b.py::test_invalid_variant_allowlist` | S0 | PASS |
| `tests/test_application_a007b.py::test_cross_variant_event_schedule` | S0 | PASS |
| `tests/test_application_a007b.py::test_full_sweep_and_retention_stress` | S0 | PASS |
| `tests/test_application_a007b.py::test_exact_reuse_and_mixed_provenance` | S0 | PASS |
| `tests/test_application_a007b.py::test_cancel_preserves_completed_evidence` | S0 | PASS |
| `tests/test_application_a007b.py::test_stop_on_failure` | S0 | PASS |
| `tests/test_application_a007b.py::test_mixed_child_reuse_after_cancellation` | S0 | PASS |
| `tests/test_application_a007b.py::test_parent_byte_bound_preserves_earlier_evidence` | S0 | PASS |
| `tests/test_application_a007b.py::test_identity_and_graph_mismatch_rejected` | S0 | PASS |
| `tests/test_application_a007b.py::test_session_host_origin_and_synthetic_api` | S0 | PASS |
| `tests/test_application_a007b.py::test_cpu_startup_cuda_lazy` | S0 | PASS |
| `tests/test_application_a007b.py::test_schedule_gap_stops_before_execution` | S0 | PASS |
| `tests/test_application_a007b.py::test_all_children_reused_without_execution` | S0 | PASS |
| `tests/test_application_a007b.py::test_cancel_before_first_child` | S0 | PASS |
| `tests/test_application_a007b.py::test_child_capacity_and_parent_limits` | S0 | PASS |
| `tests/test_application_a007b.py::test_strict_request_contract` | S0 | PASS |
| `tests/test_application_a007a.py::test_exact_variant_contract` | S0 | PASS |
| `tests/test_application_a007a.py::test_reference_and_weight_coupling` | S0 | PASS |
| `tests/test_application_a007a.py::test_allowlisted_sign_policy` | S0 | PASS |
| `tests/test_application_a007a.py::test_invalid_preparation` | S0 | PASS |
| `tests/test_application_a007a.py::test_nonfinite_parameters` | S0 | PASS |
| `tests/test_application_a007a.py::test_reject_unbounded_client_input` | S0 | PASS |
| `tests/test_application_a007a.py::test_true_preparation_and_execution` | S0 | PASS |
| `tests/test_application_a007a.py::test_ordinary_reference_bytes_and_known_certified_identities` | S0 | PASS |
| `tests/test_application_a007a.py::test_same_variant_pairing` | S0 | PASS |
| `tests/test_application_a007a.py::test_cross_variant_rejected` | S0 | PASS |
| `tests/test_application_a007a.py::test_sixteen_children_survive_recent_eviction` | S0 | PASS |
| `tests/test_application_a007a.py::test_parent_byte_limit_and_snapshot` | S0 | PASS |
| `tests/test_application_a007a.py::test_no_historical_runner_dependency` | S0 | PASS |
| `tests/test_application_a007a.py::test_cuda_receives_equivalent_configuration` | S0 | PASS |
| `tests/test_application_a007a.py::test_variant_cuda_unavailable_is_explicit` | S0 | PASS |
| `tests/test_application_a007a.py::test_closed_session_cannot_admit_parent` | S0 | PASS |
| `tests/test_application_a007a.py::test_frozen_preset_digest` | S0 | PASS |
| `tests/test_application_a007a.py::test_parent_child_capacity` | S0 | PASS |
| `tests/test_application_a007a.py::test_derived_input_must_remain_finite` | S0 | PASS |
| `tests/test_application_a006r.py::test_visible_run_transitions` | S1 | PASS |
| `tests/test_application_a006.py::test_pair_metrics_digest_and_zero_baseline` | S0 | PASS |
| `tests/test_application_a006.py::test_nonzero_deltas_and_deterministic_identity` | S0 | PASS |
| `tests/test_application_a006.py::test_mismatch_rejected` | S0 | PASS |
| `tests/test_application_a006.py::test_schedule_and_incomplete_rejected` | S0 | PASS |
| `tests/test_application_a006.py::test_union_playback_and_recorded_zero` | S0 | PASS |
| `tests/test_application_a006.py::test_comparison_api_session_and_backend_export` | S0 | PASS |
| `tests/test_application_a005.py::test_post_update_spike_time_grid` | S0 | PASS |
| `tests/test_application_a005.py::test_sparse_payload_identity_digest_and_no_fabricated_events` | S0 | PASS |
| `tests/test_application_a005.py::test_deterministic_raster_order` | S0 | PASS |
| `tests/test_application_a005.py::test_payload_rejects_nonfinite_trace_and_size_cap` | S0 | PASS |
| `tests/test_application_a005.py::test_playback_endpoint_session_and_completion_gate` | S0 | PASS |
| `tests/test_application_a004.py::test_long_identity_layout_has_shared_wrap_rule` | S0 | PASS |
| `tests/test_application_a004.py::test_view_determinism_identity_and_cap` | S0 | PASS |
| `tests/test_application_a004.py::test_target_and_combined_context` | S0 | PASS |
| `tests/test_application_a004.py::test_rejects_unbounded_or_unknown_filter` | S0 | PASS |
| `tests/test_application_a004.py::test_subgraph_route_bounds_session_failure_and_pending` | S0 | PASS |
| `tests/test_application_a003.py::test_loopback_catalog_security_and_ui` | S0 | PASS |
| `tests/test_application_a003.py::test_previous_process_token_is_rejected` | S0 | PASS |
| `tests/test_application_a003.py::test_history_limit_is_fixed` | S0 | PASS |
| `tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields` | S2 | NOT RUN |
| `tests/test_application_a003.py::test_validate_and_run_requests_share_exact_spec_identity` | S2 | NOT RUN |
| `tests/test_application_a003.py::test_manager_retains_safe_failure` | S0 | PASS |
| `tests/test_application_a003.py::test_manager_evicts_oldest_completed_job` | S0 | PASS |
| `tests/test_application_a003.py::test_result_events_and_backend_export_routes` | S2 | NOT RUN |
| `tests/test_application_a002.py::test_spec_validation_and_canonical_identity` | S0 | PASS |
| `tests/test_application_a002.py::test_final_grid_step_spike_is_valid` | S0 | PASS |
| `tests/test_application_a002.py::test_spike_outside_engine_grid_is_rejected` | S0 | PASS |
| `tests/test_application_a002.py::test_nonfinite_spike_step_is_rejected` | S0 | PASS |
| `tests/test_application_a002.py::test_equal_timestep_spikes_have_deterministic_neuron_order` | S0 | PASS |
| `tests/test_application_a002.py::test_invalid_top_level` | S0 | PASS |
| `tests/test_application_a002.py::test_invalid_stimulus_and_finite_values` | S0 | PASS |
| `tests/test_application_a002.py::test_state_events_and_no_fake_progress` | S0 | PASS |
| `tests/test_application_a002.py::test_comparison_spikes_and_robustness_contract` | S0 | PASS |
| `tests/test_application_a002.py::test_optional_git_provenance` | S0 | FAIL |
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
| `tests/test_application_a019c_r16_firewall.py::test_exact_node_grammar_and_negative_controls` | S1 | NOT RUN |
| `tests/test_application_a019c_r17_firewall.py::test_historical_inline_equivalence` | S1 | NOT RUN after STOP |
| `tests/test_application_a019c_r17_firewall.py::test_a006r_exact_node_controls` | S1 | NOT RUN after STOP |

Command nodes: metadata identity/inventory S1 PASS; static source audit S1 PASS; compileall S1 NOT RUN; diff check S1 NOT RUN; fresh CLI S1 NOT RUN; integrity S2 I2 NOT RUN; data diff S2 J2 NOT RUN; full pytest S2 NOT RUN; build S1 B2 NOT RUN (frozen disposition). Full-real/GPU/Arena/science/download/archive/tag/release/version mutations N NOT EXECUTED. Conditional commit/push N NOT EXECUTED because certification failed.

S0/S1 INCOMPLETE; S2 explicit NOT RUN; N not applicable/not executed. Manifest classification complete; success validation manifest incomplete. Certification sufficiency FAIL.

## Access accounting and preserved forward contract

accepted_real_connectivity_reads = 0

accepted_real_annotation_reads = 0

accepted_real_neurotransmitter_reads = 0

accepted_real_metadata_reads = 0

accepted_real_provenance_reads = 0

accepted_real_mapping_reads = 0

accepted_other_registered_reads = 0

Aggregate accepted reads = 0. Accepted-read accounting is based on fail-closed guarded execution and source-access accounting, not independent native byte telemetry. Deliberate blocked probes: A006R direct/descendant 2 each (single plus application), A007C direct/descendant 1 each (application). Descendants denied before creation. Permitted Node forms: 2 A006R exact launches and 1 A007C exact launch. No registered read accepted.

Forward contract **historical R15 only, no fresh R17 recertification**: explicit bounded route PASS; production default unchanged; merge block 16,384; hard fallback stop PASS; G1-G6 PASS; L3/L4 rejection PASS; PreparedNetwork 1, PreparedRuntime 1, SimulationStates 2. A/B fresh and independent; A released before B, no coexistence, no B derivation from A, no runtime reset/recreation. Each 2 warmups + 10 measured x20 ms, final 240 ms; total 24, maximum consecutive 12; no continuous 480-ms trajectory. LEFT sugar 42, LEFT 100 Hz, RIGHT 0, seed 1555062870, impulse 68.75 mV, horizon 240 ms, events 948; fingerprint 6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a; exact replay PASS historically. Timeouts preparation/advance/worker 600/30/1500 s, private/working-set caps each 8,589,934,592. Forced timeout/memory/containment/cleanup/no-orphan/no-retry PASS historically. Resource wiring historical PASS; current renewal pending.

Full-real preparations 0; real advances 0; A019D attempt consumed No; GPU/Arena/science/download/archive none/0. A013 scientific behavior, Task016 and Task017/NOT_ROBUST unchanged. No production or scientific semantic change.

## Final custody and next gate

No success commit or push; final local/origin/live remain 60c900b0c8e5a02ea95efc7340fd190193edf7e9. Worktree DIRTY (43 scoped paths), staging/stash empty, version 0.3.0, active tracked workflows 0. No tag/release/version mutation, reset/restore/clean/stash. Superseding A019C status: certification withheld; mandatory application blocker unresolved. A019D not eligible/recommended/executed. Exact next bounded task: separately authorized A002 optional-Git-provenance guarded-validation contract adjudication and remaining manifest completion. No new task started.

## Requested 100-field final report

| # | Field | Result |
|---|---|---|
| 1 | Verdict | A19C-R17-APPLICATION-VALIDATION-BLOCKER |
| 2 | Starting HEAD | 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 3 | Initial dirty inventory | 37 paths; exact list above |
| 4 | Unrelated WIP | No |
| 5 | Historical outcomes | Preserved |
| 6 | A006R failing test | tests/test_application_a006r.py::test_visible_run_transitions |
| 7 | Historical purpose | Visible acceptance/phases/terminals/identities/duplicate submission/previous result/elapsed/errors/reduced motion |
| 8 | Why Node | Production JavaScript VM, DOM mock, Promise and event-handler semantics |
| 9 | Node required | Yes |
| 10 | Inline -e required | No |
| 11 | Pre-fix executable | C:\Program Files\nodejs\node.EXE |
| 12 | Pre-fix argv | Executable, -e, exact source above, STATIC |
| 13 | Inline digest | 68120c63c86df3941d938565589f08425119d43b63a2db855756ba27da5c682e |
| 14 | cwd/environment | ROOT; inherited environment with mandatory bootstrap and TEMP/TMP C:/TEMP; corrected child sanitized |
| 15 | Rejection layer | guarded_command before original Popen/CreateProcess |
| 16 | Pre-fix Node started | No |
| 17 | Pre-fix JS started | No |
| 18 | I adjudication | I1 |
| 19 | Evidence | Historical tracked source/plan, unchanged source suffix/digest, corrected actual runtime PASS |
| 20 | Production changed | No |
| 21 | Fixture changed | Yes |
| 22 | Shared admission changed | Yes; distinct exact-script dispatcher |
| 23 | Correction | Fixed fixture and exact permission wrapper; historical argv adapter |
| 24 | Fixed script | tests/js/application_a006r.cjs |
| 25 | Equivalence | Byte-for-byte historical source preserved with argv adapter; actual assertions PASS |
| 26 | I2 grammar | N/A |
| 27 | Generic Node allowed | No |
| 28 | Arbitrary JS allowed | No |
| 29 | Generic node -e allowed | No |
| 30 | Shell allowed | No |
| 31 | Alternate script allowed | No |
| 32 | Alternate executable allowed | No |
| 33 | Wrong purpose allowed | No |
| 34 | Node payload probe | Blocked before content |
| 35 | Descendant payload probe | Blocked before descendant creation |
| 36 | Corrected Node launched | Yes; single PID 8640 |
| 37 | Corrected JS ran | Yes |
| 38 | Historical assertions | PASS |
| 39 | Exit/result | PASS; exit 0 |
| 40 | Cleanup/no orphan | PASS observed; normal exit, pipes closed, scoped CIM empty |
| 41 | Complete application | 131 PASS, 1 FAIL; fail-fast |
| 42 | Remaining application failures | A002 test_optional_git_provenance; later nodes NOT RUN |
| 43 | A007C regression | Exact workload PASS in application; full control renewal NOT RUN |
| 44 | Node control suite | NOT RUN after STOP; new tests written but unexecuted |
| 45 | Bootstrap | NOT RUN after STOP; historical R15 39 PASS |
| 46 | FIREWALL_BOOTSTRAP_CERTIFIED | Historical preserved; current renewal pending |
| 47 | A019C harness | NOT RUN after STOP; historical R15 35 PASS |
| 48 | Fresh CLI | NOT RUN after STOP; historical R15 A19C-A/exit 0 |
| 49 | Stateful/A011 | Historical R15 27 PASS; affected Python renewal required/pending |
| 50 | compileall | NOT RUN after STOP |
| 51 | diff check | NOT RUN after STOP |
| 52 | J2 | Preserved NOT RUN |
| 53 | I2 integrity | Preserved NOT RUN |
| 54 | B2 | Preserved NOT RUN |
| 55 | Full pytest | NOT RUN ? synthetic-only authorization; known S2 real-data tests excluded |
| 56 | S0 | Incomplete |
| 57 | S1 | Incomplete |
| 58 | S2 | Explicit NOT RUN |
| 59 | N | Not applicable/not executed |
| 60 | Manifest complete | All nodes classified; validation closure incomplete |
| 61 | Certification sufficiency | FAIL |
| 62 | Connectivity reads | 0 |
| 63 | Annotation reads | 0 |
| 64 | Neurotransmitter reads | 0 |
| 65 | Metadata reads | 0 |
| 66 | Provenance reads | 0 |
| 67 | Mapping reads | 0 |
| 68 | Other registered reads | 0 |
| 69 | Aggregate accepted reads | 0 |
| 70 | Qualifier | Recorded: guarded accounting, not independent native byte telemetry |
| 71 | Permitted Node forms | Exact A006R and unchanged exact A007C; 2 and 1 launches respectively |
| 72 | Bounded route | Historical PASS; no fresh recertification |
| 73 | Production default changed | No |
| 74 | G1-G6 | Historical PASS; renewal pending |
| 75 | L3/L4 | Historical PASS; renewal pending |
| 76 | Network/runtime/state counts | Historical 1/1/2 |
| 77 | A/B freshness | Historical fresh/independent; A released before B, no coexistence |
| 78 | Calls/horizons | Historical each 2 warmups +10 measured x20 ms =240 ms; total24/max12 |
| 79 | Continuous 480 ms | No historically; no R17 advance |
| 80 | Schedule | Historical seed1555062870/horizon240/events948; fingerprint above |
| 81 | Exact replay | Historical PASS; renewal pending |
| 82 | Resource wiring | Historical PASS; renewal pending |
| 83 | Forced resource/cleanup controls | Historical PASS; renewal pending |
| 84 | Full-real preparations | 0 |
| 85 | Real advances | 0 |
| 86 | A019D attempt consumed | No |
| 87 | GPU/Arena/science/download/archive | None/0 |
| 88 | A013 behavior | Unchanged |
| 89 | Task016 | Unchanged |
| 90 | Task017 | Unchanged / NOT_ROBUST |
| 91 | Package version | 0.3.0 |
| 92 | Active workflows | 0 |
| 93 | Final commit SHA | No new commit; starting SHA remains |
| 94 | Push | NOT RUN |
| 95 | Final local/origin/live | All 60c900b0c8e5a02ea95efc7340fd190193edf7e9 |
| 96 | Worktree/staging/stash | DIRTY 43 scoped paths / empty / empty |
| 97 | Tag/release/version mutation | No |
| 98 | Superseding A019C | Certification withheld; manifest unresolved |
| 99 | Exact next task | Separately authorized A002 optional-Git-provenance contract adjudication and manifest completion |
| 100 | A019D recommended | No |
