# Task 017K-R5: Complete V7 and Seal the Technical Matrix

Date: 2026-09-29

## Scope and outcome

This execution completed only the 136 remaining preregistered V7 units from the certified Task 017 checkpoint. The full technical matrix is complete at 3,168 / 3,168 and remains scientifically unscored (`INDETERMINATE`). Task016 definitions and fingerprints, source-gate authorization, variants, schedules, stimuli, readouts, and scientific parameters were not changed.

Starting authoritative Git HEAD: `405ba38212487b1e6699cd61045893ad5eb27d38` (`master`). The frozen Task017 STARTING_HEAD remains `b32c116b704cf94bcfd9d9e601eddfdd70271a2f`. The working tree was clean, the stash list was empty, and local HEAD, fetched `origin/master`, and live GitHub `master` all matched the starting HEAD.

## Certified starting checkpoint

The read-only audit passed at 3,032 / 3,168 records and sidecars, with 136 pending. R0–V6 were each 396 / 396; V7 was 260 / 396. The pending-set digest was `79b5c8e67b3d5af7abd3f48a8562b8e1e0178333105b7b67e75df6f3dcee40d1`. All pending keys were selected by the committed deterministic selector, belonged to V7, were disjoint from completed keys, and completed plus pending keys equaled the exact 3,168-key matrix. V7 retained `ConservativeSignPolicy` and the frozen parameter configuration.

Starting analysis totals were Task010 baseline 480 / 480, Task010 intervention 2,300 / 2,400, Task011 baseline trace 42 / 48, and Task011 intervention trace 210 / 240. Duplicate, missing, orphan, digest-invalid, and technical-invalid counts were zero. The Task016 fingerprint was `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`; the checkpoint fingerprint was `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`. The starting journal SHA-256 was `d085103d4c2a0b2d68930670158912294472c09565a9479ac3290665a2138d00`; the starting sidecar aggregate was `af3998392e0dff502875c9998ad4d75903a7b65a41e4508b104dc0a3275d26cd`.

## Gates and execution

The source-gate identity test passed. Task017 CUDA per-trial silencing equivalence and Task010 CPU/GPU silencing equivalence passed. GPU preflight reported `GPU_READY` on the NVIDIA GeForce RTX 3060 with CuPy 14.2.0 and NVRTC kernel compilation. The established opt-in Task007c full-graph CUDA test remained skipped because `MALECNS_TASK007C_REAL=1` was not set.

Production commands:

```powershell
uv run --extra gpu --group dev python scripts/run_task017.py --variant V7 --max-units 136
uv run --extra gpu --group dev python scripts/run_task017.py --variant V7 --max-units 61
```

The first bounded invocation delivered 75 units in 1,805.559 seconds and returned with 61 pending. A complete checkpoint audit passed at 3,107 / 3,168 with zero invalid units, after which the exact remaining count was resumed. The second invocation delivered the remaining 61 units in 1,873.717 seconds. Total runner wall time was 3,679.276 seconds. The delivery report exposes combined elapsed time; it does not separate setup/gate, backend, and checkpoint-I/O timings.

## Complete technical audit

The final read-only audit passed at 3,168 / 3,168, pending 0. Each variant was 396 / 396: R0, V1, V2, V3, V4, V5, V6, and V7. Analysis totals were Task010 baseline 480 / 480, Task010 intervention 2,400 / 2,400, Task011 baseline trace 48 / 48, and Task011 intervention trace 240 / 240.

Duplicate units: 0. Duplicate sidecar references: 0. Missing sidecars: 0. Orphan sidecars: 0. Metadata failures: 0. Result digest failures: 0. Technical invalids: 0. Task016 and checkpoint fingerprints remain unchanged at the values above.

Final journal SHA-256: `878a2b79fa442c539d4f803819e3154b060b4fbb3c6c5a2cb5a6af464503190e`.

Final sidecar inventory aggregate: `a24561d152e6acb9761c0b306d7a0158d487ce35e114ef02b543647326208553`.

Canonical completed-key digest: `47d160d985b46acd6a079c04906f60f99a929422a0b9cbe64f303223bc83af32`.

Complete technical matrix digest: `19c51e79d883915398c2d3d89c3456f3160ba0062cf75abe20e97807979b1028`.

The digest covers canonical ordered technical rows containing each key, unit fingerprint, result digest, artifact reference, sidecar SHA-256, and technical-validity field. It does not encode scientific interpretations.

## Manifests and recovery export

The complete technical matrix manifest is [complete-matrix-manifest.json](../../artifacts/task017/complete-matrix-manifest.json), SHA-256 `73c9e51ae06e7d924f80c75578536c6d1ce2b0cf5e2657041ddcfdf5a2262cd8`.

The formal Task017P exporter audited the live checkpoint before packaging this new external bundle:

- Bundle: `C:\Temp\Task017-3168-8328714e-2026-09-29-formal\task017-recovery-bundle.zip`
- Bundle SHA-256: `3bea57aec891c8ca90b89229d786e0260d9fcfb0f92d8de8b2b5239f6f1d5170`
- Recovery manifest: `C:\Temp\Task017-3168-8328714e-2026-09-29-formal\recovery-manifest.json`
- Recovery manifest SHA-256: `a09661ac697614c05c6bafed88f590a5d00375f2eeeda0a84749ce73eb78edf8`

The tracked [recovery-manifest.json](../../artifacts/task017/recovery-manifest.json) now identifies 3,168 / 3,168, pending 0, R0–V7 at 396 each, and the new formal bundle. It preserves the Task016 and checkpoint fingerprints and contains no machine-local bundle path. Its file SHA-256 is `f65261013717d7cc7739cdfbdd4c6e4c002f0b22bc4edbba50ac1952d0810208`. The historical 3,032-unit bundle was not modified or deleted.

## Restore certification and cleanup

The new 3,168-unit bundle was imported and audited under the separate repo-root location `C:\Temp\MaleCNS-Sim-Task017K-R5-restore-2026-09-29`. The restored copy matched the live checkpoint exactly for completion count, pending count, Task016 fingerprint, checkpoint fingerprint, canonical key set, journal SHA-256, sidecar aggregate, and all 3,168 individual sidecar digests. No simulations were run from the restored copy.

Automatic cleanup of the certified temporary copy was rejected by safety policy. The copy remains untouched at `C:\Temp\MaleCNS-Sim-Task017K-R5-restore-2026-09-29`; status: `TEMP_CERT_COPY_CLEANUP_PENDING`. This does not affect scientific completion or portability certification.

## Validation and claim boundaries

- `uv run pytest`: 242 passed, 1 established opt-in skip.
- `uv run python -m compileall src scripts tests`: passed.
- `uv run --extra gpu --group dev python scripts/check_gpu.py`: `GPU_READY`.
- `git diff --check`: passed.
- Final live checkpoint audit: 3,168 / 3,168, pending 0.

NO ROBUSTNESS SCORING WAS PERFORMED. The scientific matrix is complete but remains unscored and `INDETERMINATE`. Task018 was NOT started. Task017Q remains deferred. No tag or release was created.
