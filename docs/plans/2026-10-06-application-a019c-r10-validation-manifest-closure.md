# Application A019C-R10: validation manifest closure and build-backend adjudication

Authorization: `授權 A019C-R10`. Root dynamically derived with
`git rev-parse --show-toplevel`: `D:/spider/working/MaleCNS-Sim`.

## Plan

1. Preserve the accumulated inventory and verify local/origin/live identities.
2. Confirm certified bootstrap before any synthetic test discovery/import.
3. Adjudicate the exact A018UJ diff and integrity payload boundaries.
4. Diagnose isolated backend startup while retaining fail-closed behavior.
5. Run targeted harness, fresh contained CLI and admitted broader regressions.
6. Stop on a remaining validation failure; preserve history and record evidence.
7. Commit/push only after every required success gate passes.

## Verdict and starting inventory

**A19C-R10-OTHER-VALIDATION-BLOCKER. Forward certification withheld.**
J2, I2 and B2 are resolved. The broader synthetic-safe A018UR timeout regression
failed under the active firewall; no historical failure was relabeled PASS.
No commit/push, reset, restore, clean, stash, tag, release or version change.

Starting local HEAD, origin/master and live GitHub master all matched
`60c900b0c8e5a02ea95efc7340fd190193edf7e9`.
Initial short-status count: 19 entries because one directory was collapsed.
Expanded inventory: **21 untracked files**, no tracked changes, staging empty,
stash empty. All are scoped accumulated A019C work; unrelated WIP: No.
The expanded initial paths follow; R10 adds only this report.

## Historical chronology

Preserved unchanged: A19C-F; A19C-R-D; A19C-R2-C; A19C-R3-D;
A19C-R4-CHILD-FAIL-CLOSED-INCOMPLETE;
A19C-R5-HARNESS-WORKER-COVERAGE-INCOMPLETE;
A19C-R6-CONTAINED-WORKER-CLEANUP-INCOMPLETE;
A19C-R7-FIREWALL-METHOD-INVALID; A19C-R8-B; A19C-R9-B.
R9's tooling-policy stop and unknown build cause remain historical facts;
this report supplies new R10 adjudication, not an edited R9 outcome.

## Bootstrap preservation

Activation: `MALECNS_A019C_R2_FIREWALL=1`; absolute
`PYTHONPATH=D:/spider/working/MaleCNS-Sim/scripts/a019c_firewall`.
Correct audit variable: `MALECNS_A019C_R2_LOG`.

Command:
`.venv/Scripts/python.exe scripts/a019c_firewall/guarded_child.py -m pytest tests/test_application_a019c_r5_firewall.py tests/test_application_a019c_r4_firewall.py tests/test_application_a019c_r3_firewall.py tests/test_application_a019c_r2_firewall.py -q -x`.

First pre-validation bootstrap: **39 passed in 5.27 s**. Its environment mistakenly
used the unused `MALECNS_A019C_R2_AUDIT_LOG` name, so that run supplies test evidence
but no audit-file evidence. Corrected audit-only rerun, unchanged suite:
**39 passed in 5.23 s**; `C:/TEMP/a019c-r10-bootstrap.jsonl`.
Parent, valid/missing/corrupt activation, bypass rejection, serialized Windows
commands, public/native Feather, seven source categories, 4-/6-process trees,
repeated cleanup and no-orphan assertions PASS. Two live-tree cleanup records.
**FIREWALL_BOOTSTRAP_CERTIFIED remains valid.** No bootstrap source edits.

## A018UJ adjudication: J2

Target: `tests/test_application_a018uj.py::test_no_real_execution_and_scientific_default_unchanged`.
Its purpose is to verify identity observation does not prepare/advance or mutate
projection bytes, retain the reference configuration identity, forbid execution
entrypoints, and assert historical immutability of source, data and packaging.
The exact final regression includes:
`git diff d6fdb16e078bfca524214b9d1855ece3f8e9a7d7 -- src data pyproject.toml`.
This can read registered data from working-tree or Git-object content; native Git
is outside Python payload interception. It was NOT executed in R10.

**J2: S2 — NOT RUN — requires prohibited data diff outside synthetic authorization.**
Historical test unchanged; no replacement added; no narrower assertion is claimed
to preserve its data-immutability coverage. Broad Git allowance: No. No shell Git
bypass. The targeted A019C and synthetic preparation regressions independently
cover forward identity/default wiring, without claiming unchanged real data.
Historical PASS evidence for the exact excluded test was not re-established in
R10; R8 has a firewall-policy failure, not PASS. Historical results remain intact.

## Integrity adjudication: I2

Checker purpose: nine frozen evidence hashes and their Task008/017/018 linked
identity/custody checks. Four prohibited inputs are:

- `data/provenance/male-cns-v1.0.json`
- `data/provenance/shiu-2024-v630.json`
- `data/provenance/task008a-preserved-task008.json`
- `data/derived/task008-results.json`

`uv run python scripts/check_tracked_integrity.py`:
**I2 — NOT RUN — requires registered scientific provenance/data outside A019C-R10 authorization.**
No partial mode introduced. All nine hashes and linked checks are **NOT CHECKED**,
not PASS. Historical integrity evidence is not recertified by source inspection.

## Build exit-78 audit: B2

Backend: `setuptools.build_meta`; build requirement `setuptools>=68`.
uv 0.11.8 selected cached setuptools 84.0.0 under `uv build --offline -v`.
A temporary diagnostic `sitecustomize.py` under
`C:/Temp/a019c-r10-build-diagnostic` invokes the unchanged firewall install and
records the startup exception before retaining `os._exit(78)`.
No guard disabling, arbitrary-child permission or repository bootstrap change.

Exact executable returning 78:
`D:/spider/uv_cache_dir/builds-v0/.tmpN65Pwr/Scripts/python.exe`.
It inherited activation `'1'`, the diagnostic path, and the real firewall path.
Its isolated site-packages contain build requirements, not project runtime
requirements. Stack: diagnostic sitecustomize -> validation_firewall.install
line 138 -> `import pyarrow` -> **ModuleNotFoundError: No module named 'pyarrow'**.
The Python open audit and subprocess interception are installed before that
import, but ACTIVE/logged completion and Arrow reader interception are not.
Startup exits 78 before any backend hook executes. The uv label mentions
build_sdist; debug identifies the pending get_requires_for_build_sdist hook.
Missing activation, environment sanitization, mandatory-child rejection and an
ordinary setuptools/backend error are not the observed cause.

Evidence: `C:/TEMP/a019c-r10-build-startup.txt`; no completed activation record
in the build guard log. Offline mode: no downloads.
Packaging configuration selects `src` packages and static assets; it does not
require registered scientific payload. This is source inspection, not a successful
build or a proof of ordinary-build health.

**B2 — NOT RUN — build isolation cannot be certified under the synthetic-only firewall without broadening the validation boundary.**
The diagnostic reproduced fail-closed startup; final build gate excluded, not
PASS. The existing guard requires pyarrow unavailable in the isolated backend.
Admitting backend execution/dependencies/child policy would require a new certified
build-tooling boundary, unnecessary for this task's limited claim. No actual
product/build defect is established; B3 is unsupported. No B1 payload-access
permission exists. No unguarded repository build was attempted.

## Fresh harness and CLI

Targeted command: guarded `-m pytest tests/test_application_a019c.py -q -x`.
**35 passed in 7.31 s**; `C:/TEMP/a019c-r10-harness.xml`.
Fresh CLI: guarded `scripts/benchmark_application_a019.py --synthetic --output C:/TEMP/a019c-r10-forward-evidence.json`; **exit 0**, classification A19C-A.
This execution result is not the withheld overall R10 certification.

CLI evidence: bounded route A015/A016/A017/A018/A018T/A018U/A018UJ explicit;
merge block 16384; fallback null; G1-G6 true; one preparation/network/runtime;
two fresh states; A released before B; no coexistence; 24 calls, max 12/state;
each 2 warmups + 10 measured, 20 ms/call, final 240 ms. No runtime reset or
recreation; B does not derive from A; no continuous 480-ms trajectory.
Exact membrane/synaptic/refractory/pending/delayed/output/final-state/time replay;
no approximation. Timing boundaries retained.
Schedule generated once; LEFT sugar, 42 stimulated neurons, RIGHT unstimulated;
LEFT 100 Hz, RIGHT 0; seed 1555062870; impulse 68.75 mV; horizon 240 ms;
948 events; fingerprint
`6be96fd6d35b9910540ed10e08f38c3e0c3bcb4e5e7171ea7698cf6afcb6de9a`;
identical A/B windows. Harness tests verify L3/L4 rejection and fallback hard stop.
Preparation/advance/worker limits 600/30/1500 s; private and working-set caps
8589934592 each. Forced timeout/memory stops, process containment, live-tree
cleanup, no observed orphan and no retry PASS in targeted tests/bootstrap.
Fresh CLI watchdog: one launch, Windows Job Object, empty orphan list.

## Broader validation blocker

Explicit selected files and per-test classes appear in the manifest below.
Invocation used guarded pytest, `-q -x`, five exact S2 exclusions, and explicit
deferments for unadmitted historical Git/Node/legacy launcher tooling. A011
selection was only exact continuity and initial-state identity; no Arena test ran.

**23 passed, 1 failed, 27 deselected in 2.66 s.**
Failing node:
`tests/test_application_a018ur.py::test_supervisor_time_failure_cleans_without_retry`.
Expected `A018UR-TIME-LIMIT`; actual `A018UR-PREPARATION-ERROR`.
The test sets PREPARATION_CAP=0.15 s and expects prepare_start from its synthetic
child. Saved result has events=[], attempts=0, exit_code=1, orphans=[].
Source initializes the preparation-error classification and starts a startup
clock before receiving prepare_start; crossing the cap before that event keeps
PREPARATION-ERROR. Active firewall startup is additional child work before that
event. The precise child-startup timing/error was not separately diagnosed;
no stronger root cause or independent historical test defect is claimed.
No retry, cap adjustment, test rewrite, historical harness edit or conversion
of this failed S0 entry to an exclusion. Stop is authoritative.
Saved evidence:
`C:/TEMP/pytest-of-spider.tp/pytest-383/test_supervisor_time_failure_c0/result.json`;
JUnit `C:/TEMP/a019c-r10-broader.xml`.
A019A 4 PASS; A018UJ admitted subset 11 PASS; A018UI admitted subset 2 PASS;
A018UR 6 PASS + 1 FAIL. Remaining selected suites NOT RUN after fail-fast stop.
R10 integration suite NOT RUN/not created. compileall NOT RUN after stop.
Integrity/build exclusions above. git diff --check PASS (tracked diff empty).

## Manifest and sufficiency

The deterministic manifest below classifies every test function in the bounded
candidate files, plus bootstrap/harness, without collecting unfiltered pytest.
Parameter-instance outcomes are in JUnit. A function marked PASS passed every
instance executed; NOT RUN functions are never PASS. Source-only historical
Git tests, Node tests and legacy launcher tests are **S1 deferred**, not S2 and
not silently called irrelevant. Their execution policy is not certified.
Arena functions are N for this forward-harness scope and remain forbidden.
The three known A003 tests and both A018UJ prohibited tests are S2.

For each S2 test, historical PASS evidence is **not re-established in R10**;
prior documents/results remain unchanged. A003 payload-backed catalog/spec/export
and A018UJ real-artifact provenance/data-immutability checks do not establish the
forward executable synthetic wiring. Their exclusion alone would not prevent the
limited forward claim: targeted route/G1-G6/two-state/replay/watchdog/no-retry and
bootstrap tests provide direct synthetic evidence. This is not recertification of
real identities, data immutability or historical science.
However overall sufficiency is **NOT SATISFIED**: a permitted S0 regression failed
and broader S0/S1 validation remains incomplete. Final classification inventory
is recorded; a successful closed validation manifest is not achieved.
Full pytest: **NOT RUN — synthetic-only authorization; known S2 real-data tests excluded**.

## Source access accounting and execution firewall

Accepted registered reads: connectivity=0, annotation=0, neurotransmitter=0,
metadata=0, provenance=0, mapping=0, other=0; aggregate=0.
Guarded executions block registered opens; no native Git/Node validation child
was admitted. Safe source/metadata inspection is separate from payload access.
Bootstrap audit: 34 blocked events: connectivity 8, annotation 4,
neurotransmitter 4, metadata 4, provenance 5, mapping 4, other 5;
33 registered-path probes + one synthetic deny-root sentinel. Validation audit:
8 active records, no blocked payload events. First bootstrap is unlogged; its
probe count is not added to the audited total. Exact task-wide blocked total
therefore not asserted; **34 logged deliberate blocked probes**, plus the
unlogged first bootstrap's expected probes. No accepted payload reads.
Permitted tooling operations: metadata Git inventory/identities/ls-remote,
source reads, guarded pytest/CLI, offline fail-closed startup diagnostic and
tracked whitespace check. No scientific payload tooling permission granted.

Full-real preparations=0; real advances=0; real benchmark attempts=0;
future A019D attempt unconsumed; GPU No; Arena executions 0; scientific
experiments 0; downloads 0; archive writes 0. Historical A013 behavior unchanged;
production default unchanged; scientific semantics unchanged; no tracked source
modifications. Historical Task016/Task017 unchanged; Task017 NOT_ROBUST retained
as historical disposition, not re-scored. No biological interpretation.
Package version 0.3.0; active tracked workflows 0.

## Readiness and final custody

Superseding readiness: bootstrap certified; J2/I2/B2 adjudicated;
A019C-FORWARD-HARNESS-SYNTHETICALLY-CERTIFIED **not issued**.
A019D not recommended or executed. Next bounded task: adjudicate the A018UR
synthetic supervisor startup-timeout regression under mandatory child activation,
and finish the explicitly deferred validation manifest without weakening payload
blocking or rewriting historical outcomes.
No commit/push. Local/origin/live final identity remains the starting SHA.
Final worktree: 22 scoped untracked files; staging empty; stash empty.
No tag/release/version mutation. All accumulated WIP preserved.

## Exact expanded initial paths

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

## Deterministic per-test manifest

| Exact node base (all parameter instances) | Class | R10 outcome | Reason |
|---|---|---|---|
| `tests/test_application_a019c_r5_firewall.py::test_canonical_serialization` | S0 | PASS | 4 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r5_firewall.py::test_false_positive_rejected` | S0 | PASS | 3 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r5_firewall.py::test_malformed_rejected` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r5_firewall.py::test_actual_windows_audit_serialization` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r5_firewall.py::test_actual_worker_bypass_rejected` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r5_firewall.py::test_script_path_with_spaces` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r5_firewall.py::test_contained_actual_worker_startup` | S0 | PASS | 3 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r5_firewall.py::test_live_contained_descendant_cleanup` | S0 | PASS | 2 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r4_firewall.py::test_parent_native_control_and_categories` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r4_firewall.py::test_required_child_rejects_before_workload` | S0 | PASS | 4 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r4_firewall.py::test_normal_public_native_child` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r4_firewall.py::test_actual_worker_startup` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r4_firewall.py::test_inherited_activation_removed_parent_rejects` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r3_firewall.py::test_01_valid_native_synthetic_control` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r3_firewall.py::test_02_native_registered_source_denied_before_constructor` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r3_firewall.py::test_03_python_child_native_guard` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r3_firewall.py::test_04_missing_inherited_guard_fails_closed` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r2_firewall.py::test_blocked_before_content` | S0 | PASS | 7 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r2_firewall.py::test_generated_and_temp_and_source_allowed` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r2_firewall.py::test_subprocess_guard` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r2_firewall.py::test_child_cannot_drop_guard` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c_r2_firewall.py::test_native_reader_denies_synthetic_sentinel` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_full_structure_route_lifetime_replay_and_defaults` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_each_gate_stops_before_runtime_one_preparation` | S0 | PASS | 7 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_cross_layer_rejected` | S0 | PASS | 2 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_fallback_hard_stop` | S0 | PASS | 2 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_induced_failure_no_retry` | S0 | PASS | 6 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_exact_resource_limits` | S0 | PASS | 5 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_contained_tree_forced_stops_no_orphan` | S0 | PASS | 4 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_synthetic_cli_contained_success` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_synthetic_source_guard_before_access` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_timing_structure_and_historical_default` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_completed_preparation_deadline_before_runtime` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_completed_call_deadline_no_retry` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_watchdog_instrumentation_failure_terminates_tree` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_contract_schema_matches_success_evidence` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019c.py::test_watchdog_child_memory_stop_aggregate_and_cleanup` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019a.py::test_frozen_two_state_contract` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019a.py::test_historical_schedule_from_tracked_metadata_only` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019a.py::test_b_starts_fresh_after_a_released_using_same_runtime_and_graph` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a019a.py::test_a019a_checks_have_no_real_execution_and_preserve_defaults` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a018uj.py::test_independent_frozen_artifact_reconstruction_and_provenance` | S2 | NOT RUN | git show reads data/derived/task008-results.json; historical PASS not re-established; exclusion does not alone prevent forward synthetic claim |
| `tests/test_application_a018uj.py::test_each_mandatory_layer_mismatch_fails` | S0 | PASS | 7 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a018uj.py::test_correct_tuple_and_cross_layer_rejection` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a018uj.py::test_ambiguous_legacy_fields_rejected` | S0 | PASS | 3 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a018uj.py::test_no_real_execution_and_scientific_default_unchanged` | S2 | NOT RUN | J2: exact historical diff includes data; historical PASS not re-established; exclusion does not alone prevent forward synthetic claim |
| `tests/test_application_a018ui.py::test_historical_identity_layer_reconstruction` | S1 | NOT RUN | Historical Git/Node/legacy launcher operation not admitted; deferred, not PASS |
| `tests/test_application_a018ui.py::test_historical_current_components_exact` | S1 | NOT RUN | Historical Git/Node/legacy launcher operation not admitted; deferred, not PASS |
| `tests/test_application_a018ui.py::test_metadata_and_diagnostic_bytes` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a018ui.py::test_effective_digest_field_order` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a018ui.py::test_historical_preparation_and_committed_fingerprints` | S1 | NOT RUN | Historical Git/Node/legacy launcher operation not admitted; deferred, not PASS |
| `tests/test_application_a018ui.py::test_production_default_and_frozen_expectation_unchanged` | S1 | NOT RUN | Historical Git/Node/legacy launcher operation not admitted; deferred, not PASS |
| `tests/test_application_a018ur.py::test_success_exact_identity_no_advance_default_restored` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a018ur.py::test_identity_mismatch_stops_and_cleans` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a018ur.py::test_failure_cleanup_and_fallback_prevented` | S0 | PASS | 3 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a018ur.py::test_exact_frozen_constants_and_no_execution_entrypoints` | S0 | PASS | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a018ur.py::test_supervisor_time_failure_cleans_without_retry` | S0 | FAIL | 1 executed parameter instance(s); JUnit evidence |
| `tests/test_application_a018ur.py::test_supervisor_success_boundary_handshake` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018u.py::test_instrumented_oracle_exact` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018u.py::test_missing_metadata_and_policy_contract` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018u.py::test_large_safe_exact` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018u.py::test_large_integer_identity` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018u.py::test_default_has_no_probe` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018u.py::test_synthetic_bounds` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018t.py::test_exact_oracle_ownership_release` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018t.py::test_prepared_scientific_oracle` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018t.py::test_compaction_releases_capacity` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018t.py::test_many_small_schedule_determinism` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018t.py::test_partition_and_stage_release` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018t.py::test_overflow_reference_fallback` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018t.py::test_production_default` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018t.py::test_closed_boundaries` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018t.py::test_large_ids_and_invalid_block` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018t.py::test_equal_key_on_either_slice_endpoint` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018t.py::test_seeded_partition_block_invariance` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018s.py::test_exact_oracle_ownership_release` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018s.py::test_prepared_scientific_oracle` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018s.py::test_compaction_releases_capacity` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018s.py::test_many_small_schedule_determinism` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018s.py::test_partition_and_stage_release` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018s.py::test_overflow_reference_fallback` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018s.py::test_production_default` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018.py::test_runs_exact_deterministic_and_lifetime` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018.py::test_downstream_partition_exact` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018.py::test_overflow_rejection` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018.py::test_completed_stage_inputs_reclaimable` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018.py::test_overflow_loader_fallback` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018.py::test_schedule_partition_invariance` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018.py::test_fan_in_composition_invariance` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a018.py::test_production_default` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a017.py::test_exact_downstream` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a017.py::test_integer_domain_and_merge` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a017.py::test_lifetime_bounds_and_no_partial_threshold` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a017.py::test_invalid_excluded_upstream` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a017.py::test_scale_exact` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a017.py::test_production_dispatch_unchanged` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a017.py::test_overflow_oracle_fallback` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a017.py::test_high_cardinality_exact` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a016.py::test_boundaries_exact` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a016.py::test_invalid_boundary` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a016.py::test_reader_projection_admission_lifetime` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a016.py::test_v1_rejected` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a016.py::test_scale_exact` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a016.py::test_masks_released_numeric_ownership` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a016.py::test_noninteger_schema_rejected` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a015.py::test_exact_adversarial` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a015.py::test_high_exclusion_scale` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a015.py::test_membership_exact` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a015.py::test_authoritative_membership_and_no_identity_collapse` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a015.py::test_invalid_excluded_rows_rejected` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a014.py::test_tree_memory_enforcement` | S1 | NOT RUN | Historical Git/Node/legacy launcher operation not admitted; deferred, not PASS |
| `tests/test_application_a014.py::test_aggregate_limit_without_individual_offender` | S1 | NOT RUN | Historical Git/Node/legacy launcher operation not admitted; deferred, not PASS |
| `tests/test_application_a014.py::test_normal_exit` | S1 | NOT RUN | Historical Git/Node/legacy launcher operation not admitted; deferred, not PASS |
| `tests/test_application_a014.py::test_accounting_failure_stops_tree` | S1 | NOT RUN | Historical Git/Node/legacy launcher operation not admitted; deferred, not PASS |
| `tests/test_application_a014.py::test_instrumentation_opt_in_and_exact_identity` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_limits_and_cpu_only` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_one_preparation` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_watchdog_stops` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_percentiles_and_warmup_exclusion` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_schedule_is_complete_grid_slices_and_reused` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_two_fresh_states_exact_twenty_four_advances_and_replay` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_mismatch_fails_at_first_component` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_canonical_digest_exact_and_endian_stable` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_pending_guard` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_no_download_arena_gpu_or_import_execution` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_refuse_existing_output` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_watchdog_binds_worker_not_launcher` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a013.py::test_native_watchdog_can_terminate_actual_redirected_python` | S1 | NOT RUN | Historical Git/Node/legacy launcher operation not admitted; deferred, not PASS |
| `tests/test_application_a011.py::test_exact_continuity` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a011.py::test_initial_state_and_identity` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a011.py::test_clocks_controls_reset_replay` | N | NOT RUN | Arena-specific execution outside this authorization |
| `tests/test_application_a011.py::test_encoder_decoder_bounds_and_invalid_contracts` | N | NOT RUN | Arena-specific execution outside this authorization |
| `tests/test_application_a011.py::test_synthetic_visible_response_and_intervention` | N | NOT RUN | Arena-specific execution outside this authorization |
| `tests/test_application_a011.py::test_render_speed_cannot_change_backend` | N | NOT RUN | Arena-specific execution outside this authorization |
| `tests/test_application_a011.py::test_http_ui_assets_and_commands` | N | NOT RUN | Arena-specific execution outside this authorization |
| `tests/test_application_a008.py::test_reproducibility_contracts_and_packaged_assets` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a008.py::test_application_docs_are_portable_and_do_not_embed_session_urls` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007c.py::test_synthetic_production_api_and_assets` | S1 | NOT RUN | Historical Git/Node/legacy launcher operation not admitted; deferred, not PASS |
| `tests/test_application_a007c.py::test_authoritative_backend_firewall_and_packaging` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_spec_serialization_identity_and_no_verdict` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_invalid_variant_allowlist` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_cross_variant_event_schedule` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_full_sweep_and_retention_stress` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_exact_reuse_and_mixed_provenance` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_cancel_preserves_completed_evidence` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_stop_on_failure` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_mixed_child_reuse_after_cancellation` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_parent_byte_bound_preserves_earlier_evidence` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_identity_and_graph_mismatch_rejected` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_session_host_origin_and_synthetic_api` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_cpu_startup_cuda_lazy` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_schedule_gap_stops_before_execution` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_all_children_reused_without_execution` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_cancel_before_first_child` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_child_capacity_and_parent_limits` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007b.py::test_strict_request_contract` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_exact_variant_contract` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_reference_and_weight_coupling` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_allowlisted_sign_policy` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_invalid_preparation` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_nonfinite_parameters` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_reject_unbounded_client_input` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_true_preparation_and_execution` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_ordinary_reference_bytes_and_known_certified_identities` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_same_variant_pairing` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_cross_variant_rejected` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_sixteen_children_survive_recent_eviction` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_parent_byte_limit_and_snapshot` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_no_historical_runner_dependency` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_cuda_receives_equivalent_configuration` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_variant_cuda_unavailable_is_explicit` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_closed_session_cannot_admit_parent` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_frozen_preset_digest` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_parent_child_capacity` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a007a.py::test_derived_input_must_remain_finite` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a006r.py::test_visible_run_transitions` | S1 | NOT RUN | Historical Git/Node/legacy launcher operation not admitted; deferred, not PASS |
| `tests/test_application_a006.py::test_pair_metrics_digest_and_zero_baseline` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a006.py::test_nonzero_deltas_and_deterministic_identity` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a006.py::test_mismatch_rejected` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a006.py::test_schedule_and_incomplete_rejected` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a006.py::test_union_playback_and_recorded_zero` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a006.py::test_comparison_api_session_and_backend_export` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a005.py::test_post_update_spike_time_grid` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a005.py::test_sparse_payload_identity_digest_and_no_fabricated_events` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a005.py::test_deterministic_raster_order` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a005.py::test_payload_rejects_nonfinite_trace_and_size_cap` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a005.py::test_playback_endpoint_session_and_completion_gate` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a004.py::test_long_identity_layout_has_shared_wrap_rule` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a004.py::test_view_determinism_identity_and_cap` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a004.py::test_target_and_combined_context` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a004.py::test_rejects_unbounded_or_unknown_filter` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a004.py::test_subgraph_route_bounds_session_failure_and_pending` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a003.py::test_loopback_catalog_security_and_ui` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a003.py::test_previous_process_token_is_rejected` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a003.py::test_history_limit_is_fixed` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields` | S2 | NOT RUN | DatasetCatalog.local reads registered catalog payload; historical PASS not re-established; exclusion does not alone prevent forward synthetic claim |
| `tests/test_application_a003.py::test_validate_and_run_requests_share_exact_spec_identity` | S2 | NOT RUN | DatasetCatalog.local reads registered catalog payload; historical PASS not re-established; exclusion does not alone prevent forward synthetic claim |
| `tests/test_application_a003.py::test_manager_retains_safe_failure` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a003.py::test_manager_evicts_oldest_completed_job` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a003.py::test_result_events_and_backend_export_routes` | S2 | NOT RUN | DatasetCatalog.local reads registered catalog payload; historical PASS not re-established; exclusion does not alone prevent forward synthetic claim |
| `tests/test_application_a002.py::test_spec_validation_and_canonical_identity` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a002.py::test_final_grid_step_spike_is_valid` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a002.py::test_spike_outside_engine_grid_is_rejected` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a002.py::test_nonfinite_spike_step_is_rejected` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a002.py::test_equal_timestep_spikes_have_deterministic_neuron_order` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a002.py::test_invalid_top_level` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a002.py::test_invalid_stimulus_and_finite_values` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a002.py::test_state_events_and_no_fake_progress` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a002.py::test_comparison_spikes_and_robustness_contract` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a002.py::test_optional_git_provenance` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a002.py::test_cpu_only_import_and_cuda_unavailable` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_application_a002.py::test_non_scientific_synthetic_engine_integration` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_reference_parameters_are_explicit_and_grid_is_exact` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_linear_update_matches_analytical_solution` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_resting_neuron_and_synaptic_decay` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_positive_and_negative_direct_impulses_have_expected_polarity` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_threshold_reset_and_g_reset` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_refractory_blocks_input_until_strictly_after_2_2_ms` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_incoming_event_during_refractory_is_ignored_and_poisson_targets_can_opt_out` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_exact_delay_and_signed_sparse_propagation` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_self_edge_and_two_neuron_inhibitory_edge_are_supported` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_multiple_and_simultaneous_events_sum_deterministically` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_unresolved_edges_are_excluded_and_anatomy_is_unchanged` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_explicit_stimulus_is_sorted_reproducible_and_validates_ids_and_grid` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_seeded_poisson_is_reproducible_and_uses_reference_scaling` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_silencing_disables_outgoing_only` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_fingerprints_and_result_digest_are_deterministic_and_identity_sensitive` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_effective_weight_preserves_anatomical_count_boundary` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_effective_inhibitory_weight_uses_presynaptic_sign` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_two_neuron_chain_keeps_spike_output_compact` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_simulation_reports_identity_metadata` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_parameter_identity_changes_simulation_configuration` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_duration_must_be_on_the_discrete_clock` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_duplicate_schedule_times_are_additive` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_poisson_rejects_more_than_one_expected_event_per_step` | S0 | NOT RUN | Stopped at A018UR failure |
| `tests/test_task005.py::test_trace_requires_an_explicit_small_subset` | S0 | NOT RUN | Stopped at A018UR failure |

## Command manifest

| Exact command or tooling operation | Class | R10 outcome | Reason |
|---|---|---|---|
| Guarded fresh CLI described above | S0 | PASS | Fresh contained synthetic output A19C-A |
| R10 integration tests | S0 | NOT RUN | No suite added before validation stop |
| Guarded `python -m compileall src scripts tests` | S1 | NOT RUN | Validation stop |
| `git diff --check` | S1 | PASS | Tracked diff empty; does not validate untracked content |
| Metadata Git inventory, staging, stash, HEAD/origin/live identity | S1 | PASS | Metadata only |
| Safe source/configuration inspection | S1 | PASS | No registered payload inspected |
| `uv build --offline -v` startup diagnostic | S1 | PASS as diagnostic only | Exact missing-pyarrow startup cause established; build did not PASS |
| `uv build` final build gate | S1 | NOT RUN | B2: build isolation cannot be certified under synthetic-only firewall without broadening boundary |
| `uv run python scripts/check_tracked_integrity.py` | S2 | NOT RUN / NOT CHECKED | I2: requires registered scientific provenance/data; historical PASS not recertified; no forward synthetic claim coverage required |
| Unfiltered full pytest | S2 | NOT RUN | Synthetic-only authorization; known S2 real-data tests excluded; historical PASS not recertified |
| Full-real preparation, real advance/benchmark, GPU, Arena, scientific experiment, download, archive writes | N | NOT EXECUTED | Explicitly unauthorized; future real attempt unconsumed |
| Tag/release/version bump | N | NOT EXECUTED | Not authorized |
| Commit/push | N | NOT EXECUTED | Success prerequisite not met |

Candidate selections and deferments are explicit; no deferred S1 item is converted to PASS or S2. The failed A018UR test remains S0/FAIL. Manifest classifications are deterministic, but required execution closure is incomplete.

## Historical PASS evidence for exclusions

Safe inspection of existing plan text establishes that historical PASS records
exist (these are records, not fresh R10 execution):

- The three A003 S2 tests: A003R targeted A002/A003 26 passed and full 282 passed,
  1 skipped, recorded in `docs/plans/2026-10-01-application-a003-local-visual-workbench.md`.
- Both A018UJ S2 tests: dedicated A018UJ 13 passed and full 1222 passed,
  14 skipped, recorded in `docs/plans/2026-10-05-application-a018uj-identity-evidence-adjudication.md`.
- Default integrity checker: the A018UJ plan records nine frozen files/internal
  identities PASS; R10 still marks every entry NOT CHECKED.
- Historical full pytest and build PASS are likewise recorded there; R10 full
  pytest remains NOT RUN and build remains B2 NOT RUN.

The manifest phrase "historical PASS not re-established" means no fresh R10
recertification; historical PASS evidence exists as specified here. R8/R9 stops
remain unchanged. None of these historical records substitutes for R10 closure.
