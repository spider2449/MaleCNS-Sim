# Task 017K-R4 — Source-Gate Reauthorization

Date: 2026-09-29

## Scope and blocker

The Task 017 runner compares every changed path from the frozen `STARTING_HEAD`
with the historical delivery-path and execution-document rules. The certified
Task 017P state is authoritative at `4f90e82adbff8709b389ba2f1748f110dcebb519`,
but its portability and environment files are outside both historical rules.
The gate therefore reports source drift even though that exact state was
already certified. `STARTING_HEAD` remains
`b32c116b704cf94bcfd9d9e601eddfdd70271a2f`; moving it would change the
checkpoint identity and would no longer refer to the original frozen source.

Broadening `TASK017_DELIVERY_PATHS` to include dependency files, tools, or whole
directories would accept future edits by path alone. That would silently
reauthorize dependency and portability changes that have not been certified.

## Git-derived Task 017P delta

The comparison from `b32c116b704cf94bcfd9d9e601eddfdd70271a2f` through
`4f90e82adbff8709b389ba2f1748f110dcebb519` classified all 29 changed paths:

- **A — existing delivery paths (3):** `scripts/run_task017.py`,
  `src/malecns_sim/analysis/task017.py`, `tests/test_task017.py`.
- **B — existing execution documentation (15):**
  `docs/plans/2026-09-22-task-017b-bounded-batch-delivery.md`;
  `docs/plans/2026-09-23-task-017c-incremental-v0.3-robustness-matrix.md`;
  `docs/plans/2026-09-23-task-017d-continue-v1-v2.md`;
  `docs/plans/2026-09-23-task-017e-complete-frozen-v1-robustness.md`;
  `docs/plans/2026-09-23-task-017f-complete-frozen-v2-robustness.md`;
  `docs/plans/2026-09-23-task-017g-complete-frozen-v3-robustness.md` and
  `docs/plans/2026-09-23-task-017g-complete-frozen-v3-robustness-report.md`;
  the corresponding `2026-09-24-task-017h-*`, `2026-09-24-task-017i-*`, and
  `2026-09-24-task-017j-*` complete-frozen and report files; and
  `docs/plans/2026-09-25-task-017k-complete-frozen-v7-robustness.md` plus its
  `-report.md` file.
- **C — exact certified Task 017P infrastructure/documentation (11):**

| Path | Git blob at certified base |
| --- | --- |
| `artifacts/task017/recovery-manifest.json` | `88a48e98b79cd4bdc779f273283240bccbf6a20a` |
| `docs/plans/2026-09-29-task-017p-portable-scientific-execution-state.md` | `4ba8ac8973f141a0f3d2815e246a293430c63348` |
| `docs/plans/2026-09-29-task-017v7-filtered-checkpoint-audit.md` | `d180c77c53741314254793b03cd66d54738115f4` |
| `pyproject.toml` | `210f7034f5b7180bd5598ad932484aa0daf5e741` |
| `scripts/audit_task017_checkpoint.py` | `4962756e8878d9128e7f8cf619a7352c7b522c73` |
| `scripts/check_gpu.py` | `590b55ffaf6280efcd57ac5ecc9fcc4e4ff407cb` |
| `scripts/export_task017_checkpoint.py` | `041f43aa8a05c6ef1802a9ad95c1dc5cce797a9b` |
| `scripts/import_task017_checkpoint.py` | `45511eb8c50a9362de4009f1228b14565b6f312a` |
| `src/malecns_sim/analysis/task017_portability.py` | `b8d7265cd7a24315faeff42ab88857a40b4c7a87` |
| `tests/test_task017_portability.py` | `341200e6e8db7da94345389106027a6d415bfb56` |
| `uv.lock` | `f5b74337c96149007aa1f2e89ae6fa5ec162e76d` |

There were no category-D paths.

## Gate repair

The gate retains `STARTING_HEAD`, the delivery-path set, and the bounded
execution-document regex. It adds the certified base
`4f90e82adbff8709b389ba2f1748f110dcebb519` and an explicit path-to-Git-blob
map for the 11 category-C files. A changed path passes only if its historical
rule allows it, or it is in that map and both its blob at the certified base
and its blob at the current committed `HEAD` equal the recorded object ID.
Unknown paths, new files, and any later edit to a certified file fail closed.
The path normalization continues to reject absolute paths and traversal.

Tests cover the full certified delta with the historical files/docs, every
certified infrastructure path with a changed current blob, unexpected files,
absolute/traversal inputs, established delivery/docs behavior, and a later
matching execution-document closure. Frozen checkpoint identity assertions
cover `STARTING_HEAD`, Task 016 fingerprint, all variants, candidates, trial
indices, expected count, and `V020_SOURCE`.

## Validation and state boundary

The initial committed read-only production audit passed: 3,032 / 3,168 units,
V7 260 / 396, pending 136; Task 016 fingerprint
`2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`; checkpoint
fingerprint `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`;
journal SHA-256
`d085103d4c2a0b2d68930670158912294472c09565a9479ac3290665a2138d00`; and
sidecar aggregate
`af3998392e0dff502875c9998ad4d75903a7b65a41e4508b104dc0a3275d26cd`. Final
engineering validation and post-commit zero-unit gate evidence will be
recorded below before completion.

No Task 017 scientific unit was executed. No robustness scoring was performed.
Task 018 was not started, and Task 017Q remains deferred.

### Engineering validation

- `uv run pytest`: 242 passed, 1 established opt-in full-graph test skipped.
- `uv run python -m compileall src scripts tests`: passed.
- `git diff --check`: passed.
- `uv run python scripts/check_gpu.py`: `GPU_READY` (GeForce RTX 3060,
  CuPy 14.2.0, NVRTC kernels compiled).
- Post-validation `scripts/audit_task017_checkpoint.py`: PASS at 3,032 / 3,168;
  V7 260 / 396; pending 136; duplicate, missing, orphan, digest-invalid,
  and technical-invalid counts all zero.
- Task 016 fingerprint remains
  `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`.
  Checkpoint fingerprint remains
  `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`.
- Journal SHA-256 remains
  `d085103d4c2a0b2d68930670158912294472c09565a9479ac3290665a2138d00`;
  sidecar aggregate remains
  `af3998392e0dff502875c9998ad4d75903a7b65a41e4508b104dc0a3275d26cd`.
