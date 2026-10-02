# Application A007C - Robustness evidence UI

## Start gate and boundary

Repository root derived by git rev-parse --show-toplevel. Local HEAD, origin/master and live GitHub master: f5a0be8ba7236b78dfa5a8e55a880c544e7311e4. Worktree clean; stash empty; package 0.3.0; zero active tracked workflows. Required A6-COMPARISON-CERTIFIED, A006S-LOCAL-SERVER-RELIABILITY-CERTIFIED, A007A-VARIANT-CONTRACT-CERTIFIED and A007B-ORCHESTRATION-CERTIFIED verified in current documentation. v0.3.0 peels to a1a6651163840a982799b1fa82c1904e67f84660.

## Information architecture

Dedicated Robustness section in the existing workbench, before the shared A006 comparison. Existing setup, execution, A004 viewport, A005 playback and A006 pairing controls remain available. Retained sweep selector and explicit creation, cancel, release and backend export controls precede the matrix, signed delta chart and wrapping variant inspector. Selected variant evidence uses the shared comparison presentation below.

Matrix columns: Variant, Exact change, Baseline, Intervention, delta spikes, Relative, Status, Provenance. Backend order is preserved, normally R0,V1,V2,V3,V4,V5,V6,V7. Exact labels read backend overrides, never a frontend variant definition table. V5 displays 0.200 mV synaptic weight, backend schedule amplitude 50 mV and the configured factor 250 rule. Before schedule evidence is available, direct input is explicitly unavailable. V7 displays the backend ConservativeSignPolicy identity.

Primary chart metric: target spike-count absolute delta, in spikes. Coordinates scale backend deltas only; no frontend scientific delta calculation, hashing, classification or aggregate verdict. Zero axis is visible; negative/positive signed numbers and different bar positions accompany colors; zero has a mark. Missing/failed evidence has an unavailable label and no zero bar. Matrix numeric values remain accessible independently of the chart.

NO_AGGREGATE_RULE displays "No aggregate robustness verdict requested." ZERO_BASELINE relative delta remains unavailable; absolute delta remains displayed. Role-level REUSED/EXECUTED provenance is retained. PENDING, intermediate running states, COMPLETE, REUSED, FAILED and CANCELLED are text. Partial parents retain earlier completed evidence; later PENDING variants show not executed. Active status displays backend current variant/role/phase, completed/total counts and backend elapsed seconds; no percentage or ETA.

## Identity-safe switching

EvidenceSelection owns an explicit generation and robustness_id/variant_id/expected comparison ID. Parent switching increments a separate generation, clears matrix/chart/inspector and invalidates older parent updates. Latest parent-update generation rejects out-of-order polling. Variant switching calls clearComparison before any request: animation stops, cursor resets, maps clear, old dual raster/viewport presentation is hidden. Before presentation, generation ownership, shared comparison generation, variant digest, comparison ID/digest, role run/result identities and graph fingerprints are checked. Stale successes and errors are discarded. Shared A006 requests also guard their comparison generation.

Tests deliberately finish R0 and V3 requests after V5, including V3's comparison/playback/subgraph requests. They verify exact row/chart ID selection, playback reset, stale spike-map clearing and parent switching. Native A006 presenter is reused for authoritative metrics, shared cursor/time axis, aligned row order, raster, schematic positions, playback controls and spike-window overlays. Step controls are added to the existing shared controls. No edge propagation animation.

Inspector includes robustness/preset/result identities, variant digest/definition/overrides, role run/spec/result/graph/schedule fingerprints, role provenance/reuse lookup, comparison identity/result digest, realized event schedule evidence, status/errors and warnings. Existing identity-value wrapping is retained. Wording: "Event identities/times matched across variants; prescribed amplitude follows variant configuration." It does not claim identical amplitudes.

## Explicit actions and security

Creation requires a validated baseline, an explicit Start Robustness Sweep click and confirmation explaining eight variants, up to sixteen scientific child runs, serial execution, exact verified reuse and no aggregate rule. Initial load performs GET requests only. No real production Start is used in certification. Cancel explains cooperative boundaries and that an opaque simulation may finish first. Release is disabled for active parents and requires confirmation that this session's retained robustness evidence is removed. Export downloads the protected backend /export response with a short robustness ID in the filename. No client-authored export record.

Session token, Origin/Host checks, bounded IDs, fixed preset/variant allowlists and path protections are unchanged. The sole server change adds the static robustness.js asset to the existing allowlist. No token text/logging in UI; no internal paths.

## Synthetic review launcher

Command: uv run python scripts/review_application_a007c.py

The script announces SYNTHETIC REVIEW DATA / No MaleCNS scientific result and prints a session URL. It builds temporary four-neuron Feather fixtures and explicitly injected synthetic adapter/catalog, then creates parents through the production protected HTTP API. It never calls DatasetCatalog.local or reads real dataset files. Normal malecns-workbench does not import the review launcher or receive a synthetic toggle.

Complete eight-variant parent: positive, negative and zero absolute deltas, ZERO_BASELINE, R0 REUSED and other EXECUTED roles. A temporary R0 source parent is deliberately released after exact reuse so the production two-parent retention bound permits a separate eight-row PARTIAL parent. PARTIAL fixture has completed R0-V3, bounded V4 FAILED and V5-V7 not executed. Mixed provenance and CANCELLED states additionally covered by focused frontend tests and existing backend tests. Browser label is tied to explicit review catalog metadata and matching synthetic manifest identity.

## Performance and manual acceptance

A007C synthetic UI measurement instrumentation covers parent/panel load, matrix, chart, selected comparison/playback/viewport request load, playback indexing, comparison inspector update, initial dual raster/viewport render and total switch. DOM test harness timings are synthetic measurements without a browser layout engine; they are not browser performance or MaleCNS execution performance. Browser timings and visual/Console acceptance are pending because computer-use inventory reports no available browsers.

Manual review must verify the user's thirty-item checklist: synthetic label, readable exact matrix definitions and V5/V7 semantics, statuses/provenance, signed chart and zero axis, unavailable relative baseline, no aggregate verdict, row/chart selection, all eight comparisons/rasters/viewports, no stale graph/spikes, playback, inspector/hash wrapping, precise schedule wording, partial/failure, export, responsive layout, no edge propagation and no unexplained Console errors. Do not click production Start.

Current classification: A7-ROBUSTNESS-VIEW-CERTIFIED. Manual visual acceptance: PASS. On 2026-10-02 the user explicitly reported "A007C UI 測試 OK" for the exact current implementation, including all listed UI contracts, responsive behavior and browser Console acceptance. Closure changes documentation only; accepted application behavior is frozen. Commit/push is authorized after final validation; no tag/release/version bump.

## Scientific firewall

Real MaleCNS robustness parents and scientific child runs 0. Task017 units 0; Task017Q 0; raw-data downloads 0; checkpoint export/import/restore 0/0/0; archive writes 0; BANC 0. Historical Task016 and Task017 unchanged; Task017 remains NOT_ROBUST. B archive untouched. Synthetic observations have no biological interpretation. No new biological claim.

## Validation

Pending final results; see appended validation record.

## Automated validation record

- Targeted A007C: 2 pytest tests with production HTTP fixture and extensive Node DOM contract assertions; PASS. Node is required for the focused frontend harness.
- Targeted A007B: 22 passed. Targeted A007A: 52 passed. A002-A006/A006R: 59 passed. Session regressions: 4 passed. Combined targeted run: 139 passed in 48.19 seconds.
- Full pytest: 395 passed, 1 opt-in real-data test skipped; existing CuPy CUDA-path warning only. Final broad run after all code and test changes: 54.99 seconds.
- compileall: PASS. Tracked integrity: PASS, nine pinned files/internal identities. git diff --check: PASS. uv build: PASS, sdist and wheel 0.3.0, robustness.js included.
- Normal uv run malecns-workbench startup: PASS, authenticated empty parent list, protected robustness routes and no scientific execution.
- Fresh wheel installed in isolated Python 3.12 environment without CuPy: PASS; package imports from installed site-packages; normal installed entry point starts, protected robustness endpoints reject missing session and authenticated initial parent list is empty. Production static assets return 200 and contain the A007C controls/selection guard. Copied review launcher runs independently of repository/tests from the installed wheel and creates the complete synthetic eight-variant parent plus partial fixture through production API.
- DOM synthetic measurements, representative run: panel load/render 1.0 ms; matrix 0.4 ms; chart 0.4 ms; R0 comparison/playback/viewport mock requests each round to 0.0 ms; indexing 0.0 ms; variant inspector 0.1 ms; pair presentation 0.1 ms; raster/viewport mock-canvas render 0.8 ms; total R0 switch 1.3 ms. These measure Node DOM/mock-canvas work with retained backend fixture values; no browser/network/render performance inference. The production page exposes per-component browser timing when manually opened. Browser measurements remain pending.
- Computer-use browser inventory: empty. Manual visual acceptance and DevTools Console check: NOT PERFORMED. No automatic claim of certification.
- Launcher corrections during development: required Origin header added rather than bypassing protection; production two-parent bound handled by explicit temporary source release; cleanup uses LocalServer.server_close (RunManager has no close); smoke command uses normal default available port because its launcher parser does not forward --port. No prior tests/security contracts weakened.
- Current local/origin/live master remain the starting commit. Worktree deliberately contains only the eleven A007C files; stash empty; workflows zero. No commit/push, tag/release/version bump.

Exact next recommended application task: Application Task A008 - application documentation and reproducibility certification, including installed-package operating instructions and evidence-view limitations. Do not start it automatically.

Final follow-up: shared A006 measurement text preserved with the extracted presenter timings; A007C/A006/A006R 22 passed in 7.96 seconds. The final full run including backend-authoritative metric assertions, frontend export routing and late A006 failure protection passed 395 tests, one opt-in real-data skip and the existing CUDA-path warning. Final compileall, integrity, diff check, build and installed CPU-only review smoke passed. Browser visual/Console acceptance and actual browser performance remain pending. Classification A7-AUTOMATED-READY-MANUAL-PENDING; publication withheld.


## A007C authorized closure - 2026-10-02

Manual acceptance PASS supersedes the historical pending-acceptance records above. Final classification A7-ROBUSTNESS-VIEW-CERTIFIED closes A7-CONTRACT-GAP through the certified A007A and A007B prerequisites plus A007C. Acceptance covers R0-V7, V5 0.200 mV/50 mV/factor 250, V7 ConservativeSignPolicy, ZERO_BASELINE, signed backend spike-count deltas, identity-safe switching and stale-response rejection, comparison/playback/raster/schematic viewport, inspector/schedule wording, partial/failure/cancel/release/export, explicit production start confirmation, synthetic labeling, responsive layout and Console checks. Synthetic review values remain non-scientific. NO_AGGREGATE_RULE remains; no frontend scientific delta calculation or aggregate robustness verdict. No biological robustness, causality, mechanism or necessity claim. Historical Task017 remains separately NOT_ROBUST.

Start identity f5a0be8ba7236b78dfa5a8e55a880c544e7311e4; only the existing eleven A007C files are authorized for commit. Real MaleCNS robustness runs 0; real scientific child runs 0; Task017 units 0; Task017Q executions 0; downloads 0; checkpoint export/import/restore 0/0/0; archive writes 0; BANC 0. Historical Task016/Task017 and B:\MaleCNS-Archive unchanged. Final validation results follow below.

### Closure validation results

- Targeted A007C: 2 passed (7.23 s); A007B: 22 passed (19.33 s); A007A: 52 passed (7.25 s); A002-A006 including A006R: 59 passed (16.46 s).
- Full pytest: 395 passed, 1 opt-in real-data test skipped, 1 existing CUDA-path warning (55.02 s). No opt-in scientific execution enabled.
- compileall: PASS; tracked integrity: PASS (nine pinned files/internal identities); git diff --check: PASS; uv build: PASS (sdist and wheel, version 0.3.0).
- Normal uv run malecns-workbench: PASS on an OS-selected available port; empty runs/robustness lists, protected GET/POST, static assets, no automatic robustness execution.
- Fresh wheel: isolated Python 3.12 environment, installed site-packages import, CuPy absent; normal installed entry point, A007C assets, protected GET/POST and empty production run/parent lists PASS. Copied synthetic review launcher independent of repository/tests: COMPLETE eight-variant and PARTIAL fixtures, synthetic label, V5 50 mV and null aggregate result PASS.
- Initial external smoke probe with an unread unauthorized POST body encountered a Windows connection reset; corrected the probe to send an empty unauthorized POST. No application change. Both normal and installed-wheel protection checks then passed.
- Accepted source, static assets, review launcher and tests match the pre-closure SHA-256 snapshot byte-for-byte. Historical tracked files are outside the eleven-file commit scope and pinned integrity passes. Archive/checkpoint/download/BANC operations were not invoked.
- Publication authorized as feat: add robustness evidence view; final commit/local/origin/live identities are reported after push. No tag, release, version or workflow mutation.
