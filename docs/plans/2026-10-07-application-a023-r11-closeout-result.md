# A023-R11-CLOSEOUT result

Date: 2026-10-07.

**A023-A — PUBLIC RUNTIME API IMPLEMENTED AND ZERO-PAYLOAD RELEASE-SAFE VALIDATION PASSED; RELEASE PREPARATION MAY CONTINUE.**

**G16 = PASS** under the current user-authorized release-safe acceptance boundary.

The stable CPU resumable runtime API is implemented and validated. GPU remains experimental. Closed-loop remains engineered/application-only. No new scientific-v0.4 claim is made.

This is post-run documentation outside the frozen candidate. It does not replace the frozen inputs or rewrite any historical result. Final commit SHA and post-push three-way readback are reported in the delivery response because a commit cannot contain its own identity.

## Identity and scope

- Starting authoritative local/origin/live SHA: `c5ad89377575592665344f6420126b16c29b4339`.
- Frozen manifest SHA256: `b8f0dfd2f37ce34035a0d220b4408caf3124be582c8f42fb70c498740744203e`.
- Frozen ordinary inputs: 440.
- Final environment: `C:/TEMP/malecns-a023r11-final-23b63938ad7347a6b5d8691c07792eae`.
- Python: `3.14.0 (main, Nov 19 2025, 22:43:52) [MSC v.1944 64 bit (AMD64)]`; pytest 9.1.1.
- Exact locked project/runtime/dev/GPU distributions: 25; no lock/dependency/version edit.
- Fresh exact-base sparse tree, candidate overlay, Python/uv environment, process, TEMP/TMP/cache, disabled plugin autoload, accepted builtin census, contained children and cleanup.
- No data/artifacts root in the execution or independent wheel-build tree. Local wheel supplies genuine metadata; release packaging certification is deferred.

## Development evidence

**DEVELOPMENT TEST — NOT FINAL CERTIFICATION.**

This closeout ran 87 tests: test_application_a011.py, test_application_a007b.py, test_application_a023.py, test_application_a023r11_controls.py and test_code_review_fixes.py. All passed; one CUDA-path warning. Command: `.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider` followed by those five paths, with guard activation before import and plugin autoload disabled.

A new guarded development collection ran `scripts/a023r11_development.py --collect-only -q -p no:cacheprovider`. It established exactly 1556 nodes. No development failures or source/test fixes occurred in this closeout. Prior documented fixes and failures remain historical development evidence.

A011: terminal Z3-RUN. Exact Node executable/argv/read grants resolve command composition without global protection bypass. Original HTTP/backend/JS regression assertions remain; the historical JS production path is still executed. Negative authority controls reject alternate arguments, startup injection, executable, shell, cwd and close-fds deviations. Both development and fresh final checks passed.

A007B: terminal Z3-RUN. Ownership, deterministic export, orchestration and retention correctness assertions passed. Incidental timing values are not benchmark or performance evidence.

Retained development changes include the RunManager completion/admission race correction, class/instance-aware builtin plugin census, startup allowance with explicit synthetic prepare_start assertion, exact native child PYTHONPATH, pre-assertion Task017 Git mock, literal browser-session JS extraction, and genuine locked metadata/GPU provisioning. Runtime API semantics were not redesigned; underlying equations, fixtures/tolerances and production defaults were not changed.

## Frozen taxonomy, identities and final results

| Item | Final result |
| --- | --- |
| H | 1503 exact historical identities retained |
| I | 12 exact historical infrastructure identities retained |
| N | 41 exact identities, listed below |
| H union I union N / collected | 1556 exact identities |
| H taxonomy | Z0=1467; Z1=11; Z2=0; Z3=25 |
| Z3 terminal states | 24 Z3-RUN; 1 Z3-NOT-RUN; 0 Z3-BLOCKED |
| Executed / PASS / FAIL / skip | 1544 / 1544 / 0 / 0 |
| NOT RUN | 12: 11 protected-content prerequisites; 1 absent external baseline |
| I0 | PASS — UNPROTECTED CONTENT ONLY |
| I1 | NOT RUN — REGISTERED-PAYLOAD-REQUIRED |
| I2 | PASS — BOUNDED MANIFEST CONSISTENCY |
| Final classification | ZERO-PAYLOAD RELEASE-SAFE VALIDATION PASS |

The exact collected identities are in a023-validation-final-collection.txt and the frozen manifest; the exact executed identities and per-node reports are in a023-closeout-final-evidence.json. Collection-file SHA256: `29ef2a566fb77754369719a17c1cfda71f24c61a7b5f594a2f58c4e77255a22e`.

One intended suite ran. Controller command: `.venv/Scripts/python.exe -B scripts/a023r11_prepare.py`.

Frozen child command: `<fresh execution>/.venv/Scripts/python.exe -B <fresh execution>/scripts/a023_release_validation.py <fresh run root>`.

Exact pytest arguments: `tests -q -s --tb=short -c <fresh execution>/pyproject.toml -o cache_dir=<fresh run root>/pytest-cache -o log_file=<fresh run root>/evidence/pytest.log --basetemp=<fresh run root>/temp/pytest`, with the single frozen Collection observer. No source/test repair or retry occurred during Phase C.

Accepted protected payload opens during Phase C: **0**. Parent accounting: `{"accepted_protected_checks": 0, "denied_protected_checks": 63}`; firewall blocked events: 75. Expected negative controls are included. Counters cover the fresh guarded process tree and wrapped readers, not an independent native-read census or development/history zero-payload claim. Registered content is absent from the fresh tree; exact Node read grants and unchanged fail-closed Python/Arrow protection remain active.

Before/after frozen identities matched; independent checkout/execution readback also matched all ordinary inputs. No protected hashes were computed. Job accounting: `{"active": 0, "total": 106, "terminated": 0}`. No active contained descendants remained; Job closed. Both runner and pytest exit=0.

## Current gate reconfirmation

| Gate | Evidence scope | Result |
| --- | --- | --- |
| G1 | Stable import and exact exports | PASS |
| G2 | PreparedNetwork remains internal | PASS |
| G3 | Factory-only opaque facades | PASS |
| G4 | Fresh independent states and exact-owner rejection | PASS |
| G5 | In-place advance with detached result | PASS |
| G6 | Preflight validation before mutation | PASS |
| G7 | Ordinary execution/output failure poisoning; no rollback | PASS |
| G8 | Positive grid-aligned duration and canonical time; no 20 ms cap | PASS |
| G9 | Chunk-relative explicit events, duplicates and endpoints | PASS |
| G10 | Internal packing retained | PASS |
| G11 | Immutable detached tuple result | PASS |
| G12 | Stable public error categories | PASS |
| G13 | Experimental GPU facade and lifecycle | PASS |
| G14 | Additive legacy compatibility | PASS |
| G15 | Independent engine continuity/refractory/delay regressions | PASS |
| G16 | Current authorized exact release-safe suite, split integrity and fresh environment | PASS |

G1-G14 are reconfirmed by current facade/source/export review and fresh A023 assertions, including real bounded GPU correctness. G15 is reconfirmed by the fresh retained engine regression modules and continuity oracles. G16 uses the actual current authorized release-safe contract; it is not inferred solely from earlier G1-G15. This is not full pytest PASS, unconditional full-integrity PASS, release packaging certification or release readiness.

## Explicit NOT RUN identities

- `tests/test_application_a003.py::test_result_events_and_backend_export_routes` — NOT RUN — REGISTERED-PAYLOAD-REQUIRED; Registered catalog identities require protected content
- `tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields` — NOT RUN — REGISTERED-PAYLOAD-REQUIRED; Registered catalog identities require protected content
- `tests/test_application_a003.py::test_validate_and_run_requests_share_exact_spec_identity` — NOT RUN — REGISTERED-PAYLOAD-REQUIRED; Registered catalog identities require protected content
- `tests/test_application_a018uj.py::test_independent_frozen_artifact_reconstruction_and_provenance` — NOT RUN — REGISTERED-PAYLOAD-REQUIRED; Historical protected Git blob read
- `tests/test_application_a018uj.py::test_no_real_execution_and_scientific_default_unchanged` — NOT RUN — REGISTERED-PAYLOAD-REQUIRED; Historical Git diff includes protected data; synthetic defaults remain covered by A018UI and A023
- `tests/test_application_a019h.py::test_starting_commit_exact_replay` — Z3-NOT-RUN; Optional external starting-SHA module absent; no external source admitted; independent historical replay remains covered by pinned A018UI fixtures and A023 continuity
- `tests/test_task006.py::test_reference_provenance_manifest_is_pinned` — NOT RUN — REGISTERED-PAYLOAD-REQUIRED; Registered Shiu provenance required
- `tests/test_task007.py::test_exact_id_reference_is_preserved_as_canonical_strings` — NOT RUN — REGISTERED-PAYLOAD-REQUIRED; Default loader opens registered FlyWire mapping evidence
- `tests/test_task007b.py::test_production_task007_readout_uses_only_the_resolved_mn9_body` — NOT RUN — REGISTERED-PAYLOAD-REQUIRED; Registered Feather inputs required
- `tests/test_task007c.py::test_cuda_bounded_real_graph_equivalence` — NOT RUN — REGISTERED-PAYLOAD-REQUIRED; Registered full graph required
- `tests/test_task008a.py::test_task008_result_preservation_manifest_is_explicit` — NOT RUN — REGISTERED-PAYLOAD-REQUIRED; Registered protected provenance required
- `tests/test_tracked_integrity.py::test_tracked_integrity_accepts_copy_and_rejects_corrupt_metadata` — NOT RUN — REGISTERED-PAYLOAD-REQUIRED; Copies and hashes protected registered evidence

## Exact final N

- `tests/test_application_a023r11_controls.py::test_a011_activation_cannot_bypass_child_protection[close_fds]`
- `tests/test_application_a023r11_controls.py::test_a011_activation_cannot_bypass_child_protection[cwd]`
- `tests/test_application_a023r11_controls.py::test_a011_activation_cannot_bypass_child_protection[environment]`
- `tests/test_application_a023r11_controls.py::test_a011_activation_cannot_bypass_child_protection[executable]`
- `tests/test_application_a023r11_controls.py::test_a011_activation_cannot_bypass_child_protection[shell]`
- `tests/test_application_a023r11_controls.py::test_a011_exact_authority_and_composition`
- `tests/test_application_a023r11_controls.py::test_a011_protected_fixture_denied_before_open`
- `tests/test_application_a023r11_controls.py::test_browser_session_exact_authority`
- `tests/test_application_a023r11_controls.py::test_browser_session_historical_assertions_unchanged`
- `tests/test_application_a023r11_controls.py::test_complete_readiness_is_pass_capable`
- `tests/test_application_a023r11_controls.py::test_native_child_environment_composes_exact_authority`
- `tests/test_application_a023r11_controls.py::test_readiness_denies_incomplete_or_changed_contract[I1]`
- `tests/test_application_a023r11_controls.py::test_readiness_denies_incomplete_or_changed_contract[Z2]`
- `tests/test_application_a023r11_controls.py::test_readiness_denies_incomplete_or_changed_contract[base]`
- `tests/test_application_a023r11_controls.py::test_readiness_denies_incomplete_or_changed_contract[blocked]`
- `tests/test_application_a023r11_controls.py::test_readiness_denies_incomplete_or_changed_contract[collection]`
- `tests/test_application_a023r11_controls.py::test_readiness_denies_incomplete_or_changed_contract[duplicate]`
- `tests/test_application_a023r11_controls.py::test_readiness_denies_incomplete_or_changed_contract[missing]`
- `tests/test_application_a023r11_controls.py::test_readiness_denies_incomplete_or_changed_contract[mutable]`
- `tests/test_application_a023r11_controls.py::test_readiness_denies_incomplete_or_changed_contract[taxonomy]`
- `tests/test_code_review_environment.py::test_dependency_census_rejects_incomplete_or_changed_environment[duplicate]`
- `tests/test_code_review_environment.py::test_dependency_census_rejects_incomplete_or_changed_environment[extra]`
- `tests/test_code_review_environment.py::test_dependency_census_rejects_incomplete_or_changed_environment[gpu]`
- `tests/test_code_review_environment.py::test_dependency_census_rejects_incomplete_or_changed_environment[project]`
- `tests/test_code_review_environment.py::test_dependency_census_rejects_incomplete_or_changed_environment[version]`
- `tests/test_code_review_environment.py::test_frozen_packaging_inputs_are_required`
- `tests/test_code_review_environment.py::test_genuine_project_metadata_and_gpu_prerequisites`
- `tests/test_code_review_environment.py::test_gpu_closure_is_complete_and_does_not_mutate_lock`
- `tests/test_code_review_environment.py::test_late_extra_expansion_and_cycles`
- `tests/test_code_review_environment.py::test_provisioning_rejects_materialized_protected_root[artifacts]`
- `tests/test_code_review_environment.py::test_provisioning_rejects_materialized_protected_root[data]`
- `tests/test_code_review_fixes.py::test_actual_builtin_plugin_census`
- `tests/test_code_review_fixes.py::test_completion_cannot_clear_a_new_run[application_error]`
- `tests/test_code_review_fixes.py::test_completion_cannot_clear_a_new_run[success]`
- `tests/test_code_review_fixes.py::test_completion_cannot_clear_a_new_run[unexpected_error]`
- `tests/test_code_review_fixes.py::test_plugin_census_uses_defining_module[False-class]`
- `tests/test_code_review_fixes.py::test_plugin_census_uses_defining_module[False-instance]`
- `tests/test_code_review_fixes.py::test_plugin_census_uses_defining_module[False-module]`
- `tests/test_code_review_fixes.py::test_plugin_census_uses_defining_module[True-class]`
- `tests/test_code_review_fixes.py::test_plugin_census_uses_defining_module[True-instance]`
- `tests/test_code_review_fixes.py::test_plugin_census_uses_defining_module[True-module]`

## Complete A023 changed-file inventory

Historical eleven-path WIP is retained within this expanded legitimate closeout inventory. Later R11 adapters, manifests, code-review/environment fixes and post-run evidence are additional A023 work. The unrelated incoming `docs/references/deep-research-report.md` is preserved and excluded from the candidate overlay and commit.

- `docs/manifests/a023-before-closeout-frozen-candidate.json`
- `docs/manifests/a023-before-environment-recovery-frozen-candidate.json`
- `docs/manifests/a023-closeout-final-evidence.json`
- `docs/manifests/a023-validation-baseline-h.txt`
- `docs/manifests/a023-validation-final-collection.txt`
- `docs/manifests/a023-validation-infrastructure-i.txt`
- `docs/manifests/a023-validation-new-n.txt`
- `docs/manifests/a023-zero-payload-taxonomy.json`
- `docs/manifests/a023r11-before-code-review-frozen-candidate.json`
- `docs/manifests/a023r11-frozen-candidate.json`
- `docs/plans/2026-10-07-application-a023-public-runtime-implementation.md`
- `docs/plans/2026-10-07-application-a023-r11-closeout-result.md`
- `docs/plans/2026-10-07-application-a023-r11-closeout.md`
- `docs/plans/2026-10-07-application-a023r-zero-payload-validation-recovery.md`
- `docs/plans/2026-10-07-application-a023r10c2-local-repro.md`
- `docs/plans/2026-10-07-application-a023r11-release-safe-validation.md`
- `docs/plans/2026-10-07-code-review-environment-recovery-result.md`
- `docs/plans/2026-10-07-code-review-environment-recovery.md`
- `docs/plans/2026-10-07-code-review-fixes.md`
- `docs/plans/2026-10-07-code-review-phase-c-result.md`
- `docs/plans/2026-10-07-code-review-phase-c.md`
- `scripts/a019c_firewall/a007c_node.py`
- `scripts/a019c_firewall/a011_node.cjs`
- `scripts/a019c_firewall/a011_node.py`
- `scripts/a019c_firewall/session_node.cjs`
- `scripts/a019c_firewall/session_node.py`
- `scripts/a023_fail_closed_inspect.py`
- `scripts/a023_local_repro.py`
- `scripts/a023_release_validation.py`
- `scripts/a023_validation_environment.py`
- `scripts/a023r11_development.py`
- `scripts/a023r11_freeze.py`
- `scripts/a023r11_prepare.py`
- `scripts/profile_application_a019x.py`
- `src/malecns_sim/application/server.py`
- `src/malecns_sim/experimental/__init__.py`
- `src/malecns_sim/experimental/gpu.py`
- `src/malecns_sim/runtime.py`
- `tests/js/workbench_session.cjs`
- `tests/test_a023_fail_closed_inspect.py`
- `tests/test_application_a011.py`
- `tests/test_application_a018r.py`
- `tests/test_application_a023.py`
- `tests/test_application_a023r11_controls.py`
- `tests/test_code_review_environment.py`
- `tests/test_code_review_fixes.py`
- `tests/test_task017.py`
- `tests/test_workbench_session.py`

## Evidence identities

- `environment.json`: `7ad2397cde6c0109f90387d6b1b34f38b796c8e8be83b2816fae5331f93d6915`.
- `final-validation.json`: `ffef0722d1505ac05a0b823f8f30fc1974c3c2f5e5fec871f13adfa3c4f77ae6`.
- `suite-output.txt`: `4219ca65d2bd1d50c876c1f9a19fe87a765802cf3f2821a13cfe2abe381b3eb3`.
- `firewall.jsonl`: `9efac2baf7c6d8d665b26a88eeaba9d8b20a24e90a9dda1b054a70fd91b76f71`.

## Historical and scientific boundaries

A023-B and all prior STOP/contract violations, R6 premature execution, PE3-UNRESOLVED, R10/R10R/R10B/R10B2/R10B3, R10C custody and R11 inspection incidents remain historical. The previous failed and successful final reports are not reused as this run. R6 27 passed remains PREMATURE OBSERVATION — NOT ACCEPTANCE EVIDENCE.

No new scientific claim, protected-content simulation, benchmark, profiler, CPU/GPU performance optimization or performance conclusion. Task026 remains NO_V0_4_SCIENTIFIC_QUESTION_CURRENTLY_READY. Historical CPU latency/realtime conclusions remain unchanged. Public runtime additions implement A022; this closeout made no product/runtime source edits.

## Commit, custody and next task

Commit/push is authorized only after this A023-A determination. Final changed/staged inventory and git diff --check must pass before the coherent closure commit; post-push local HEAD, origin/master and live GitHub master must agree. The final delivery supplies those SHAs and push result. Staging/stash were empty at entry; no reset, stash or discard was used. Existing worktrees remain preserved. The unrelated research document remains untracked after commit.

Version remains 0.3.0. No version bump, tag, GitHub Release or publication. The local metadata wheel is validation provisioning only.

Exact next task: **A024 — bounded v0.4 application/runtime release preparation: public docs, examples, package/export review, changelog/release notes, stable/experimental boundary, reproducibility instructions, and release gate.** A024 is not started.
