# A007 robustness evidence view: contract audit

Date: 2026-10-02. Verdict: **A7-CONTRACT-GAP**. Classification: Application infrastructure audit; implementation and certification incomplete.

## Start gate

The repository root was derived using `git rev-parse --show-toplevel`. Local HEAD, origin/master, and live GitHub master were `c02501e114b487a4c41926a4a04a950e06ce8b7c`. Worktree and stash were empty. Package version was 0.3.0, v0.3.0 peeled to `a1a6651163840a982799b1fa82c1904e67f84660`, and tracked active workflows numbered zero. A3, A4, A5, A6, and A006S certification records were present. Task017 remains NOT_ROBUST; Task017Q remains Q1 / KEEP_DEFERRED.

## Phase 1 findings and contract gap

`application/models.py` already provides canonical finite JSON, strict experiment decoding, deterministic run identities, numeric comparisons, and a generic `RobustnessRequest`. Its variant representation accepts numeric LIF overrides and seeds, but cannot express a sign-policy override. Its result placeholder carries variant ID, spec digest, count and warnings rather than paired run evidence.

Direct, non-simulation contract probes produced INVALID_SPEC for all three of: ModelSpec with weight 0.200, SignPolicySpec with ConservativeSignPolicy, and RobustnessVariant with a sign-policy override. ModelSpec explicitly restricts projection weight to 0.275; SignPolicySpec restricts signing to the reference policy. `service.EngineAdapter.prepare(files, backend)` does not receive model or sign configuration. ProductionEngine delegates to Task008 prepare_network, which hard-codes reference signing and default effective weight. run_experiment explicitly rejects non-none robustness requests.

The lower-level reusable primitives already support the required operations: `SignedAnatomicalConnectome.from_projection`, `EffectiveSignedProjection.from_signed_connectome(..., synaptic_weight_mV=...)`, LIFParameters, simulate_lif, and the CUDA graph upload/simulation primitives. A thin sweep adapter over the current application contracts is insufficient. A generic application-owned configurable preparation seam and validated model/sign contract must precede execution. Do not bypass validation, masquerade as reference configuration, or use Task017's runner as the application backend.

`comparisons.verify_pair` is reusable unchanged for same-variant comparisons: exact model/sign, schedules, dataset, target, seed, backend, timing, observables, engine and graph controls remain appropriate. In particular, its unsigned projection identity can remain constant across this family; signed/effective graph fingerprints legitimately change for V5/V7 across variants, but must match within each pair. No scientific pairing rule should be weakened.

RunManager's HISTORY_LIMIT is eight runs. An eight-variant baseline/intervention sweep needs up to sixteen retained sub-runs, with graphs and playback references. Parent-owned retention is necessary: changing only the display would leave early rows unavailable. The global active-run reservation must cover the entire parent sweep, including finalization, rather than permit unrelated jobs between child runs. Cancellation must be explicitly connected to the existing run_experiment trial-boundary callback; the current HTTP shell has no cancellation route.

Task017 orchestration includes its frozen checkpoint, cache, journal/sidecar, historical Git gates, CUDA execution and scoring responsibilities. None becomes the production UI backend. Task017 scoring and Task016 thresholds remain historical only. No Task017 runner, scorer or restore was invoked for this audit.

## Verified family and proposed preset

Definitions were checked against Task016's preregistration table and Task017.VARIANT_CONFIGURATIONS. The following application IDs are proposed mappings, not deployed preset contracts:

| ID | Historical ID | Exact override from R0 |
| --- | --- | --- |
| R0 | R0_REFERENCE_TASK005 | None |
| V1 | V1_TAU_MEMBRANE_FAST | tau_membrane_ms = 10 ms |
| V2 | V2_TAU_MEMBRANE_SLOW | tau_membrane_ms = 30 ms |
| V3 | V3_TAU_SYNAPSE_FAST | tau_synapse_ms = 2.5 ms |
| V4 | V4_DELAY_SHORT | synaptic_delay_ms = 1.0 ms |
| V5 | V5_WEIGHT_LOW | synaptic_weight_per_anatomical_synapse_mV = 0.200 mV |
| V6 | V6_THRESHOLD_HIGHER | v_threshold_mV = -44 mV |
| V7 | V7_CONSERVATIVE_SIGNS | sign policy = ConservativeSignPolicy |

R0: rest/reset -52 mV, threshold -45 mV, membrane time constant 20 ms, synapse time constant 5 ms, refractory period 2.2 ms, delay 1.8 ms, anatomical weight 0.275 mV, Shiu2024SignPolicy, reference neurotransmitter resolution. The family retains the direct-input factor 250. Thus V5 also changes input amplitude from 68.75 to 50 mV. This is part of the verified weight axis, not accidental stimulus drift.

Proposed preset name: `application-historical-variation-family-v1`. The eventual preset identity must include a domain-separated digest of canonical ordered definitions, full reference parameters, units, signing/resolution policies, input-weight semantics, and source provenance at the starting commit. No stable preset digest was implemented or certified here.

## Required versioned design

Proposed schema: `application-robustness-v1`, not yet implemented. RobustnessSpec must bind the source comparison template, preset identity, requested ordered variant definitions, explicit paired seed policy, pairing policy and aggregate rule. The robustness ID must be a domain-separated canonical digest without timestamps. Exact per-variant derived experiment specs must bind their own model and sign configuration.

Each result row must contain its variant definition/digest, exact spec identities, dataset/model/sign identities, seed, realized schedules, both run IDs/result digests, comparison ID, unsigned and signed/effective graph fingerprints, backend-authored numeric values, warnings, status, and per-role REUSED/EXECUTED provenance. Result integrity must include missing/failed rows and export provenance; elapsed time belongs to execution metadata rather than deterministic scientific identity.

Across variants compare normalized complete specs against the reference template, allowing only that row's declared axis. Compare actual input event times separately from weighted stimulus fingerprints: ExplicitStimulus.fingerprint includes weight_mV, so V5 legitimately has a different full fingerprint. Within each variant require the same complete fingerprint using A006 verification. Across variants require equal event-time schedules and only the declared V5 amplitude difference. Graph differences must be derived from the declared sign/weight axis, not accepted arbitrarily.

Reuse requires exact executed spec, dataset, model/sign, seed, schedule, graph, backend and engine identities plus verified result integrity and retained graph/playback evidence. Similar settings are insufficient. Reuse must never bypass the same-variant pairing checks. No reuse mechanism was implemented in this audit.

The parent job must execute one scientific run at a time, retain all child evidence, publish terminal completion only after verified export, and report current variant index/ID, completed/total variants, real phase, elapsed wall time and baseline/intervention role. Do not fabricate within-run percentage or synthetic-derived real-run ETA. Preserve completed rows on later failure or cooperative cancellation. Parent states: COMPLETE, PARTIAL, FAILED, CANCELLED; row states: PENDING, RUNNING, COMPLETE, FAILED, CANCELLED, REUSED.

The intended matrix is Variant / exact change / baseline count / intervention count / signed delta / relative delta / status, with comparison IDs, warnings and provenance inspectable. A backend-authored signed delta chart summarizes model output only. ZERO_BASELINE remains a null relative delta with an explicit warning. Failed/missing rows remain selectable for inspection, with unavailable playback clearly marked.

Default aggregate rule must be serialized as NO_AGGREGATE_RULE. Display: "No aggregate robustness verdict requested." No historical >=6/7 rule is inherited. Any future optional rule must be explicitly versioned, backend-computed and forbidden from producing a verdict for an incomplete sweep. JavaScript only displays backend-authored values and classifications.

Selecting a completed row must reuse A006 comparison, dual raster, synchronized playback and schematic viewport. Clear all prior graph/playback identities, selection, comparison and inspector state before asynchronous loads; reject late responses from previous selections. Verify loaded run/result/comparison/graph/playback bindings before display. Variants are separate simulations, never time points; no propagation animation.

Export must be backend-authored and include spec, result, preset/definitions, identities, numeric values, failures, aggregation policy, provenance and integrity digest. Extend existing session/Host/Origin protections to all robustness routes and package any new static assets. No robustness routes or assets were added here. The optional historical Task017 panel is omitted.

## Certification and limits

Synthetic R0-V7 sweep certification was not performed: the application contract cannot yet represent all eight members faithfully. No A007 matrix, chart, switching benchmarks, export or manual acceptance is claimed. A later implementation must cover all 30 requested test categories, the six bounded performance measurements, fresh-wheel CPU-only startup/security/asset smoke, and user visual acceptance before commit/push. Existing-suite validation is recorded below; it is not A007 certification.

Real new MaleCNS robustness runs: 0. Task017 units: 0. Task017Q executions: 0. Raw-data downloads: 0. Checkpoint export/import/restore: 0/0/0. Archive writes: 0. BANC: 0. New biological hypotheses: 0. Historical scientific artifacts and B archive were not changed. Task016 and Task017 were not modified. No biological robustness, confidence, probability or mechanism claim is made.

No real full sweep is required or justified by this audit. Next recommended application task: **A007A — application-owned configurable preparation and variant identity contract**, retaining reference behavior and A006 pairing, with synthetic V5/V7 integration and parent-owned retention, before completing the A007 view. This recommendation does not authorize any historical execution or a real sweep.

No commit, push, tag, release or version bump.

## Validation results

- Direct contract probes: three expected INVALID_SPEC rejections (V5 model, V7 sign, V7 generic override); no simulation executed.
- Targeted existing application regression: 51 passed (A002/A004/A005/A006/A006R). No dedicated A007 implementation tests exist; the requested 30-category A007 certification remains unperformed.
- `uv run pytest`: 319 passed, one explicitly gated real-data test skipped, 24.69 seconds. One existing CuPy CUDA-path warning. Historical test fixtures do not execute historical Task017 units.
- `uv run python -m compileall src scripts tests`: passed.
- `uv run python scripts/check_tracked_integrity.py`: PASS, nine pinned tracked files and internal identities.
- `git diff --check`: passed.
- `uv build`: source distribution and wheel built, version 0.3.0.
- Fresh-wheel smoke: wheel installed into a new temporary virtual environment without CuPy; the installed malecns-workbench entry point started on an automatically available loopback port; root loaded; all six existing static assets were packaged; missing-token run API returned 403 and authenticated empty history returned 200. A007 robustness route returned 404, consistent with the gap. No synthetic robustness view or robustness API protection is certified. An initial attempt used an environment containing CuPy and was discarded as CPU-only evidence.
- A007 result construction, matrix payload, row/chart preparation, playback switching and viewport switching timings: not measured because those features were not implemented. Existing test duration is not a scientific execution ETA.
- User manual visual acceptance: not requested or obtained; there is no A007 view to accept.
- Final scope: only this plan and application ARCHITECTURE.md; no source/tests/static assets changed.


## A007A backend prerequisite resolution

The original audit outcome remains A7-CONTRACT-GAP. [A007A configurable preparation and variant contract](2026-10-02-application-a007a-configurable-preparation-variant-contract.md) resolves the backend preparation, variant identity, pairing and result-retention prerequisite. The A007 matrix, orchestration, evidence API and UI remain future work. Historical identities and this audit outcome are preserved.
