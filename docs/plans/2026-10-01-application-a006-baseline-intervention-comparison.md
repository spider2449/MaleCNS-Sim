# Application Task A006 — Baseline vs Intervention Comparison

Date: 2026-10-01. Starting HEAD, origin/master, and live GitHub master: `1cb452de0322f54b003cee6cf6dcfb7e1b138007`. Start gate passed: clean worktree and empty stash, package `0.3.0`, zero tracked GitHub Actions workflows, and `v0.3.0` peeled to `a1a6651163840a982799b1fa82c1904e67f84660`. A003, A004, and A005 were certified. Task017 remains `NOT_ROBUST`; Task017Q remains `Q1 — KEEP_DEFERRED`.

## Intervention audit

The A002/A003 picker supports `none` or one `outgoing_silence` body: 16949 for LEFT sugar, 10331 for RIGHT sugar. The engine receives `silenced_neuron_ids` at simulation time, preserves the prepared topology and weights, and excludes a firing silenced source from outgoing event scheduling. Incoming events, internal state, and recorded spikes remain. The base and prepared graph fingerprints therefore remain the same for a controlled pair; the effective event scheduling differs.

## Pairing and result contract

`application-comparison-v1` uses deterministic run IDs, target ID, and metric-set ID for comparison identity. The result stores both run/spec/result identities, dataset and schedule fingerprints, base and prepared graph fingerprints, backend and intervention state, pairing evidence, target metrics, playback grid and engine spike digests, graph semantics, warnings, and an authoritative digest. Timestamps are excluded from comparison identity.

The backend requires exact equality of dataset/manifest, stimulus population and settings, duration, dt, seed policy and realized seed, realized stimulus schedule fingerprint, model and sign policy, target, backend, observables, robustness request, trial count, result schema, engine version, base graph, and prepared graph. The baseline must have no intervention; the intervention must be one corresponding-MN9 outgoing silence. Running, failed, missing, mismatched, and non-paired results are rejected. The browser cannot confer eligibility. `ZERO_BASELINE` means relative delta is null, including when both counts are zero.

The paired-run API inherits controlled picker fields from the completed baseline. The first certification intervention is the existing corresponding-MN9 outgoing silence. It is plumbing certification, not biological candidate selection. No scientific mechanism or causal verdict is produced.

## Playback and display

Both authoritative A005 sparse playback payloads are bound to the comparison identities. Synchronized mode requires the same duration and dt. A single cursor and display speed drive separate baseline/intervention rasters on identical x scales and union body-ID row order. Viewport schematic coordinates are determined once from union body IDs, so shared neurons stay fixed. Each run's displayed nodes and counts remain explicit; absent union members appear muted. Structural edges remain drawn; outgoing edges of the silenced source are marked as scheduling-suppressed. Selected-neuron histories show zero recorded spikes distinctly from a neuron absent from the current display filter. Derived window highlights and counts do not enter the result digest. Display filter ≠ biological pathway; schematic positions are not anatomical.

## Certification and nonclaims

The known A005 baseline identity may be reused only if loaded safely in the current server session. Current run history is in memory, so a fresh server cannot import that prior run through the bounded API. One A006 baseline was executed. Its deterministic run/spec/result/graph identities exactly matched the known A005 baseline. A certification-script polling race observed the `COMPLETED` event before RunManager finished its atomic result export, so the immediate paired-run request was rejected. No intervention was started at that point. The complete temporary baseline JSON was recovered with `read_result`, which verifies its authoritative and manifest digests, and its exact known identities were checked. RunManager was corrected to publish terminal state only after export is complete. This recovered completed baseline is used for the one allowed intervention run; there is no baseline rerun. This is an integrity-checked certification recovery, not a general cross-session import API.

The result is a model-output comparison only. It cannot establish biological causality, necessity, inhibition, or pathway control. Task017 units: 0. Task017Q executions: 0. Raw-data downloads: 0. Archive writes: 0. Historical scientific artifacts and B: archive remain outside A006 scope.

## Real A006 certification measurement

Exactly two real runs were executed: one baseline (304.605 s) and one outgoing-silence intervention (299.416 s). The completed baseline file was recovered from the interrupted atomic-export temporary file with SHA-256 `fdbd8b1c39e05b0aae473d744ff160bdbd491856eb0c2b8307bfd622dee5a472`; the intervention result file SHA-256 is `d4fe3be527e1ce572a7e1dae500208a1d47a082c29943bd63c89d125c8b5ad7a`.

| Identity or metric | Baseline | Intervention |
|---|---|---|
| Job ID | `f642a037359f4b0e876f408d0d7bde79` | `c48182cd136b4db28208ab203b644da1` |
| Run ID | `4827ec1ebd407566b4254d80f59eaceecc01f9364d903f54a4843683a88920ce` | `da1796f753e24bf656b8698389f0c6614693e521f4fd4805e81d11f04149e9b6` |
| Spec digest | `5d5e5d95d38b457d0fcc20d7351d3d79e95fc9321b5fb252697763fbdedb9d38` | `6bbc6aa1433fd363d8fd8edd3de3401a92a4435be39fe4ac3e97a9d3590a9787` |
| Result digest | `e91b47199c295efe1c0937751cea78200c1e4845d02b3c5ad79d92eb2fbccce7` | `d52ea0513cccf4d15546cb2e3b13e42e977d0226db361cc2c66ae91c9110042e` |
| Base graph | `fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4` | same |
| Prepared graph | `ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f` | same |
| Realized schedule | `3e3ddb63ad75a568227a857b2e0ae432bfc12b894c43e5e63ccf9285a6b93b32` | same |
| Target spikes; rate | 0; 0 Hz | 0; 0 Hz |

Pairing status: `PAIRED`. Absolute spike-count and firing-rate deltas: 0. Relative deltas: null, reason `ZERO_BASELINE`. Comparison ID: `7b1e54b66a02155227dab891795c7651b115a81170ed3bb37df83a0add7a09a8`. Comparison result digest: `91d9acccf01edade2961218d9f78f2b165071a08d5dd4b00a09db16f70d9d055`. The intervention is `outgoing_silence` of body 16949 on CPU. This zero result is accepted as plumbing certification and is not a biological finding.

A006 certification measurement on these verified result objects: eligibility check 33.5 ms; comparison construction 34.1 ms; comparison payload 4,301 bytes; dual backend playback construction 25.2 ms and 188,888 bytes; dual raster event indexing 1.33 ms for 1,136 neurons with recorded spikes. In the live registered review session, the combined/cap-80 baseline and intervention viewport extractions took 0.798 s and 0.791 s; the union contained 80 rows, the dual comparison playback payload was 387,707 bytes, and the protected endpoint returned it in 0.162 s. The backend export exactly matched the created comparison result. Browser responsiveness remains for manual review.

Manual visual acceptance is pending because no browser control surface was available to Codex. Classification: `A6-AUTOMATED-READY-MANUAL-PENDING`. The remaining application gap is a durable, integrity-checked run registry for safe cross-session baseline reuse. The local manual review process registered these two exact integrity-checked files for inspection without executing another simulation; it does not add a public arbitrary-path API. No A006 commit or push is authorized until the user accepts the visual checklist.

## Manual acceptance and closure — 2026-10-02

Classification: `A6-COMPARISON-CERTIFIED`. The user reported A006R manual acceptance PASS for the exact A006/A006R worktree and explicitly authorized closure, commit, and push. This supersedes the earlier manual-pending status and commit/push restriction. Acceptance includes the already-present local-session token persistence/refresh behavior in `app.js`, `2026-10-02-local-session-refresh.md`, and `2026-10-02-local-server-recovery.md`, classified as Application Layer usability and local-session recovery support.

Pre-closure inspection found only A006/A006R files and those authorized ancillary items. The `app.js` diff contains only accepted local-session refresh and A006/A006R UI work. Historical scientific artifacts are unchanged. No code, CSS, or JavaScript behavior changes are made during closure. No new MaleCNS simulation, A007 work, historical evidence change, tag, release, or version bump is authorized or performed.

Final closure validation: targeted A006/A006R tests 20 passed; full `uv run pytest` 315 passed and 1 existing opt-in full-graph skip, with one CUDA-path environment warning. `uv run python -m compileall src scripts tests`, `uv run python scripts/check_tracked_integrity.py` (9 frozen tracked files and internal identities), `git diff --check`, and `uv build` all passed. Package version remains `0.3.0`. The final scope inspection still found exactly the 14 authorized files, an empty stash, and zero tracked GitHub Actions workflows.
