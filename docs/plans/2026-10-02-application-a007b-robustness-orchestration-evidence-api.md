# A007B robustness orchestration and evidence API

Date: 2026-10-02. Starting HEAD: 637a2236374da27c67489b1c56292a55b7159384.

Start gate passed: local/origin/live master equal the expected commit; clean worktree, empty stash, version 0.3.0, zero tracked workflows, unchanged v0.3.0 target and all three required certifications.

## Implementation plan

1. Add strict application-robustness-v1 spec/result and domain-separated identity using certified A007A definitions.
2. Reserve whole-sweep execution ownership; execute ordered baseline/intervention pairs serially. Check actual event schedules across variants and preserve A006 full stimulus equality within pairs.
3. Extend certified parent retention with byte-accounted immutable graph/evidence snapshots. Reconstruct playback and A006 comparison from retained results.
4. Implement exact reuse with explicit rejection/execution provenance, stop-on-failure, cooperative cancellation and real phase events.
5. Add session-protected bounded APIs and deterministic backend export without an aggregate verdict.
6. Certify synthetic full/reuse sweeps, eviction stress, limits, protection and measurements; run all requested validation and wheel smoke.
7. Document evidence and remaining UI work; commit/push only if all certification requirements pass.

Scientific firewall: real MaleCNS runs, Task017 units, Task017Q, downloads, checkpoint operations and archive writes remain zero. Historical files and B archive are outside mutation scope.

## Implemented contract and lifecycle

Schema: application-robustness-v1. Identity domain: malecns-application-robustness-v1. Preset remains application-historical-variation-family-v1, digest 34de3189f0630c159fabe140892362ec65228487984224ef880702eb3fd8f139. Certified A007A definitions are imported, never redefined. Spec serialization is strict and deterministic, binding base ExperimentSpec, target, intervention, ordered requested IDs, seeds, preset and pairing/reuse/schedule/failure/aggregate policies. Unsupported presets, override fields, aggregates or policies reject admission; operational timing does not enter identity.

Parent states: CREATED, VALIDATING, RUNNING, FINALIZING, COMPLETE, PARTIAL, FAILED, CANCELLED. Variant states: PENDING, BASELINE_RUNNING, BASELINE_COMPLETE, INTERVENTION_RUNNING, COMPARING, COMPLETE, FAILED, CANCELLED, REUSED. REUSED means both roles reused. Mixed roles are explicit baseline/intervention EXECUTED or REUSED, with original job/run identities, result/spec/variant/graph/schedule digests and reuse lookup/rejection evidence. No state is inferred from Recent Runs.

Whole-sweep RunManager ownership prevents ordinary-run interleaving. Exactly one child simulation executes at a time; default order R0,V1,V2,V3,V4,V5,V6,V7, baseline then intervention. STOP_ON_VARIANT_FAILURE preserves earlier completed evidence, marks the failing variant FAILED and leaves later variants PENDING; parent is PARTIAL when earlier variants completed, otherwise FAILED. Failed child result snapshots are retained when available and within capacity. Cancellation checks occur before children, between baseline/intervention, between variants and before final completion. Opaque simulations finish; completed evidence is retained before cancellation is recognized. Parent becomes CANCELLED, preserving completed variants and individual completed children. No true mid-simulation cancellation or restart recovery is claimed.

Progress events expose actual service phase transitions, variant/role and completed/total counts; no percentage or ETA. The eight-pair workflow fits the 256-event bound. Elapsed seconds remain operational snapshot metadata.

## Schedule and reuse evidence

Every child's actual explicit schedule is generated and cross-checked before any execution. Event-time evidence binds neuron IDs, times and multiplicity, refractory-free IDs, seed, dt and duration, under malecns-application-input-event-schedule-v1. It excludes only the prescribed amplitude variation: V5 uses 50 mV; all other variants use 68.75 mV. Amplitude-inclusive full fingerprints and event counts remain per-variant evidence. Execution identity and service engine-result checks verify these full fingerprints. A006 verifies full realized-schedule equality within every pair. Equal seeds alone are never treated as proof. An injected schedule mismatch stops before any child execution with A007B-SCHEDULE-CONTRACT-GAP evidence.

The synthetic certification event-time fingerprint across R0-V7 is 220a44e5541f78ae659df083338f716d9b86b6c8d676db2de7b36ee01f955735. This is a fixture identity, not a MaleCNS result.

Exact reuse searches retained children of session-owned sweep parents. Registered dataset source hashes, manifest and mapping are checked even for reuse. Full VariantExperimentSpec digest, exact expected current-package RunIdentity, compatible verified result schema, complete status, realized full schedule and immutable graph identity/integrity must match. This binds dataset, target, intervention, backend, seed and exact preparation configuration. Approximate candidates are recorded with rejection reasons before fallback execution. EXECUTE_ONLY is an explicitly bound alternative. Reused evidence is copied into the destination parent, so later source release does not break retrieval. No arbitrary filesystem lookup or UI-field approximation exists.

## Retention and evidence API

The certified ParentResultStore now byte-accounts immutable graph/evidence envelopes alongside child results. Limits: two parents per session, sixteen children per parent, 64,000,000 encoded bytes per parent. Fixed 512,000-byte metadata reservation permits terminal failure/cancellation publication when child evidence fills capacity. Admission fails explicitly; required evidence is never silently evicted. Release is explicit and terminal-only. Session shutdown closes admission, requests cancellation and releases retained data. Session-local ownership is independent of eight-entry Recent Runs; it is not disk persistence.

One canonical combined/160-node, at-most-1,200-edge graph view is retained per child, with extraction timing/size metadata omitted and an integrity envelope. Arbitrary cap/mode snapshots are outside this bounded implementation. Run/spec/graph identities are checked on retrieval. Pair graph payload contains both views plus shared/union node IDs. Playback is reconstructed through A005/A006 from immutable verified results and graph identity; no large playback blobs are duplicated. The existing comparison-playback bound is 34,000,000 bytes. A006 comparisons are stored per variant, then rebuilt/checked on retrieval, retaining spike counts/rates, absolute/relative deltas, ZERO_BASELINE, identities and authoritative digest.

Routes follow existing protections:

- POST /api/robustness: exactly selection, preset_id, variant_ids, reuse_policy, aggregate_rule; selection uses existing catalog allowlists.
- GET /api/robustness and /api/robustness/{id}: list/status/spec/result/progress.
- GET /api/robustness/{id}/events and /export.
- GET /api/robustness/{id}/variants/{variant}: status, provenance and comparison/evidence identities.
- GET /api/robustness/{id}/variants/{variant}/comparison, /playback and /subgraph.
- Playback/subgraph accept only optional role=baseline|intervention, supporting a completed baseline whose pair failed/cancelled. Default returns paired evidence.
- POST /api/robustness/{id}/cancel and /release: empty object body.

Session token and existing Host/Origin checks apply to every route. Requests remain bounded at 2,048 bytes, parent IDs at exact hexadecimal lookup, variants/presets at certified allowlists. Path inputs and free-form overrides are absent/rejected. CPU startup imports no CuPy/CUDA module; existing GPU dispatch remains lazy and optional.

Export schema: application-robustness-export-v1. Digest domain: malecns-application-robustness-v1-export. Export includes complete RobustnessSpec/Result, ordered definitions/statuses, role provenance, numeric comparisons, identities/digests, errors/cancellation, warnings and aggregate rule/result. Export excludes operational progress/elapsed metadata and deterministically serializes a retained evidence snapshot. New executions can have different invocation IDs/export bytes; identity never binds timestamps. NO_AGGREGATE_RULE always produces aggregate_result=null, with no robustness verdict. Historical Task016 thresholds and Task017 scoring remain unchanged and unused.

## Synthetic certification

The full synthetic/test-engine R0-V7 sweep executes sixteen children using actual A007A resolution, preparation, explicit input generation and LIF dispatch. For this arithmetic fixture only, the test adapter replaces target observations with known counts: R0=0/0, V1=1/2, V2-V7=1/1. These deliberate test-engine counts certify ZERO_BASELINE, nonzero delta and same-value behavior, without biological meaning or a claim that those counts are LIF model conclusions. Every pair passes the real A006 backend comparison; all eight variants end COMPLETE. A separate HTTP full sweep uses unmodified synthetic LIF outputs.

Full reuse case: sixteen initial children, then reversed variant order with all sixteen children REUSED and zero additional scientific executions. Releasing the source parent leaves all comparison/playback/graph evidence available. A smaller reuse case executes four initial children, then reuses four and executes two new V2 children. Seed mismatch executes two new children with explicit EXACT_SPEC_MISMATCH rejection evidence. A cancelled-baseline case proves mixed baseline=REUSED/intervention=EXECUTED provenance.

Stress: twenty-four unrelated ordinary RunManager admissions through its actual create/eviction path (with test execution seam, no extra scientific runs) leave Recent Runs at eight while parent retains all sixteen children. All eight comparisons, playbacks and graph contexts are retrievable afterward. Capacity failures, partial failure, cancellation before the first child/between children/between variants, completed evidence survival, graph identity corruption and session/Host/Origin checks pass.

## A007B synthetic certification measurements

Latest measured bounded fixture run; these are not real MaleCNS sweep timings or ETA:

| Operation | Measurement |
| --- | --- |
| Full 16-child sweep | 3.025441 seconds |
| Parent result construction | 0.003511 seconds |
| Retained encoded bytes, including metadata reserve | 654,057 bytes |
| Per-variant comparison retrieval | 0.008580-0.009251 seconds |
| Playback reconstruction/retrieval | 0.015209-0.016299 seconds |
| Subgraph/shared-union retrieval | 0.011180-0.012035 seconds |
| Export construction | 0.002944 seconds |
| Export payload excluding its final digest field | 73,220 bytes |

Measurements are emitted by test_full_sweep_and_retention_stress; operational timings are not identity dimensions.

## Coverage and validation

All requested categories are exercised by focused A007B tests plus unchanged A007A/A002-A006 regressions:

- Deterministic spec/identity/preset/order, unsupported aggregate, integrity and strict allowlists: spec_serialization_identity_and_no_verdict, invalid_variant_allowlist, strict_request_contract.
- Parent/child ownership, serial ordering, role preparation, real progress and sixteen-child full sweep: full_sweep_and_retention_stress; A007A same_variant_pairing/cross_variant_rejected.
- Within-pair full schedule and cross-variant actual event evidence: cross_variant_event_schedule, schedule_gap_stops_before_execution; A006 DIFFERENT_SCHEDULE regression.
- Exact/approximate/mixed/all-child reuse and explicit provenance: exact_reuse_and_mixed_provenance, mixed_child_reuse_after_cancellation, all_children_reused_without_execution.
- Failure/cancellation survival and capacity limits: stop_on_failure, cancel_preserves_completed_evidence, cancel_before_first_child, parent_byte_bound_preserves_earlier_evidence, child_capacity_and_parent_limits; unchanged A007A full sixteen-child rejection/byte-bound tests.
- History eviction, all retained evidence, deterministic export/digest, no aggregate verdict: full_sweep_and_retention_stress.
- Identity/session/Host/Origin/path/override protection: identity_and_graph_mismatch_rejected, session_host_origin_and_synthetic_api, strict_request_contract.
- CPU startup and lazy CUDA: cpu_startup_cuda_lazy; unchanged A007A CUDA dispatch/unavailable tests.

Results:

- Targeted A007B: 22 passed, 18.95 seconds.
- Targeted A007A: 52 passed, 6.92 seconds.
- Targeted A002-A006/A006R: 59 passed, 15.95 seconds; local-session regressions: four passed, 2.58 seconds.
- Full uv run pytest: 393 passed, one opt-in real-data test skipped, one existing CUDA-path warning, 49.07 seconds.
- compileall, tracked integrity (nine pinned files/internal identities), diff check and build: PASS.
- Fresh CPU-only wheel: installed in an isolated temporary environment without CuPy; installed-source identity verified. Installed entry-point startup on an available port, root loading, protected robustness routes and authenticated empty parent list: PASS. Installed-wheel A007B/A007A/A006/A006R: 94 passed, 18.70 seconds, including full synthetic HTTP API without CuPy.
- Normal uv run malecns-workbench: available-port startup and robustness session protection PASS; no real simulation.

Harness corrections: one regression command named a nonexistent local-session test file; it was corrected to test_workbench_session.py. The first normal-launch smoke cleanup terminated uv while a Windows launcher descendant held its output pipe; the identified smoke-owned process tree was stopped, and the harness now stops its own launcher tree before closing the pipe. Existing user listeners were untouched. No production security checks or prior tests were weakened.

## Classification and remaining work

Verdict: A007B-ORCHESTRATION-CERTIFIED. Classification: backend/API prerequisite infrastructure, synthetic certification only. A007 overall remains A7-CONTRACT-GAP. No manual visual acceptance is required for this backend task.

Real MaleCNS simulations 0; Task017 units 0; Task017Q 0; raw-data downloads 0; checkpoint export/import/restore 0/0/0; archive writes 0; BANC 0. Historical Task016 and Task017 unchanged; Task017 remains NOT_ROBUST. B archive unchanged. Version 0.3.0; v0.3.0 peeled target a1a6651163840a982799b1fa82c1904e67f84660; tracked active workflows zero. No tag/release/version bump.

Final scope: eight files, comprising three application documents, three application modules, one focused test module and one launcher smoke script. Authorized publication: feat: add robustness sweep orchestration, then push origin master and verify exact local/origin/live identity plus clean worktree/empty stash.

Exact next recommended task: Application Task A007C — robustness matrix/chart UI and identity-safe variant evidence switching, using this backend API, followed by synthetic/manual UI acceptance. Do not start it automatically.
