# Task 017P — Portable Scientific Execution State

## Scope

This is an engineering and reproducibility change. It does not alter Task 016
or Task 017 scientific specifications, execute units, score robustness, or start
Task 018.

## Incident and reproducibility layers

The source repository moved to a new machine, but its ignored Task 017 journal
and result sidecars did not move with the source. This exposed three separate
requirements:

- **Source reproducibility:** Git records the code, specification, dependency
  metadata, and recovery-point description.
- **Environment reproducibility:** project metadata installs the CUDA Python
  runtime components and development/test tools from a clean environment.
- **Execution-state portability:** an audited bundle carries the journal and
  every referenced result sidecar and can be restored into another checkout.

The mutable journal and its binary sidecars remain outside normal Git because
they are large, append-only derived execution results. The tracked recovery
manifest identifies a certified external recovery point without becoming a
second mutable checkpoint or storing a machine-local backup path.

## Audit and recovery commands

Install the supported environment and preflight the GPU first:

```powershell
uv sync --extra gpu --group dev
uv run --extra gpu --group dev python scripts/check_gpu.py
```

Audit a local checkpoint without changing it:

```powershell
uv run --extra gpu --group dev python scripts/audit_task017_checkpoint.py
```

Export to a new directory outside the checkout. The directory contains a
deterministic ZIP with the journal and sidecars plus `recovery-manifest.json`.
The manifest includes the bundle SHA-256, journal digest, per-sidecar digest
inventory and aggregate, specification/checkpoint fingerprints, completion
counts, pending keys, source Git HEAD, and environment metadata.

```powershell
uv run --extra gpu --group dev python scripts/export_task017_checkpoint.py C:\path\outside\checkout\task017-recovery
```

Restore into a checkout with no local checkpoint:

```powershell
uv run --extra gpu --group dev python scripts/import_task017_checkpoint.py C:\path\to\task017-recovery
uv run --extra gpu --group dev python scripts/audit_task017_checkpoint.py
```

Import verifies the bundle checksum, manifest schema, Task 016 and checkpoint
fingerprints, journal and sidecar digests, record/sidecar consistency, unit
matrix membership, completion counts, and exact pending keys. It extracts to a
temporary staging directory and performs a full audit there. Only then does it
install the sidecar directory and atomically place the journal as the final
commit marker. A failed import removes its staging area and any newly installed
sidecar directory; it does not replace an existing destination. An existing
incompatible or partial checkpoint is rejected rather than merged.

Absolute checkout and backup paths are used only to access files. They are not
included in checkpoint, unit, schedule, result, source, resume, or bundle
scientific identity. The archive contains repository-relative names only.

## Fresh-machine recovery sequence

1. Clone or pull the repository.
2. Install from committed project metadata with `uv sync --extra gpu --group dev`.
3. Run `uv run --extra gpu --group dev python scripts/check_gpu.py` and require `GPU_READY`.
4. Obtain the recovery bundle named by the tracked recovery manifest.
5. Verify/import it with `scripts/import_task017_checkpoint.py`.
6. Run `scripts/audit_task017_checkpoint.py` and check the exact pending set.
7. Resume only when the operator has separately authorized scientific execution.

If the tracked recovery manifest describes an incomplete Task 017 recovery
point but the local derived checkpoint is absent, the system/operator must not
silently initialize a replacement checkpoint.

## Certified recovery point

The recovery manifest is tracked at
`artifacts/task017/recovery-manifest.json`. It identifies the latest certified
external bundle by filename and cryptographic digests, and records the frozen
Task 016 and checkpoint fingerprints and exact ledger. It contains no absolute
backup path. The recorded bundle is the formal export created for this task,
not only the earlier manual export.

The certified scientific state is 3,032 / 3,168 complete: R0–V6 are each
396 / 396, V7 is 260 / 396, and 136 V7 units remain. Scientific status remains
`INDETERMINATE`. The Task 016 fingerprint is
`2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`; the
checkpoint fingerprint is
`8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`.

The earlier certified external backup manifest SHA-256 is
`3ed31e2de4ed4ca9ca147f0f2bf71b1706b7b6e754b21c92ca70d8d556b8463b`.
The formal export created `task017-recovery-bundle.zip` with SHA-256
`056e2a0593fa8e67d34b251e4143fb2f25b885452ff456b732c4526605fab19a`. Its
recovery manifest SHA-256 is
`e3e4c547925b1af5861023810760cf1c08b668a6f4621dfc72bc72a125707e1a`. The
bundle is stored outside the checkout in
`Task017-3032-8328714e-2026-09-29-formal`.
The tracked manifest points to this formal bundle and records the prior manual
backup manifest digest for provenance.

## Certification evidence

The live checkpoint audit passed with 3,032 records and sidecars; duplicates,
missing sidecars, orphans, metadata/result digest failures, and technical
invalids were all zero. The journal digest remains
`d085103d4c2a0b2d68930670158912294472c09565a9479ac3290665a2138d00` and the
sidecar inventory aggregate is
`af3998392e0dff502875c9998ad4d75903a7b65a41e4508b104dc0a3275d26cd`.

Synthetic tests cover deterministic export, root-independent checkpoint and
unit identities, export/import equivalence, exact pending keys, corruption,
missing/orphan/duplicate sidecars or units, wrong specification/checkpoint
fingerprints, incompatible destinations, partial staging, and interrupted
imports. The Task 017 checkpoint/export/import and relevant Task 007c CUDA test
selection passed; the bounded full-graph Task 007c gate remains opt-in under
the established project policy. The GPU preflight returned `GPU_READY` on a
GeForce RTX 3060 using CuPy 14.2.0, float64 arithmetic, and NVRTC compilation
of both the preflight and MaleCNS-Sim schedule kernels.

The formal bundle imported into a separate temporary repository root and the
restored checkpoint passed the new audit. Source and restored states matched
exactly for all 3,032 canonical records, every sidecar SHA-256, both scientific
fingerprints, and the full ordered pending-key tuple (136 units). Restored
counts were R0–V6 396 / 396 each, V7 260 / 396, and 136 pending; duplicate,
missing, orphan, digest-invalid, and technical-invalid counts were all zero.
The temporary certification copy remains in the named `C:\Temp` Task 017P
folder because automatic safety review rejected the recursive cleanup command.
No production checkpoint file was targeted for cleanup.

The separate clean environment was created solely from the project lock and
`uv sync --extra gpu --group dev`; no package was installed outside project
metadata. It provided pytest, CuPy 14.2.0, CUDA runtime/NVRTC 12.9 components,
and reported `GPU_READY`. Targeted Task 017/export/import and Task 007c tests
passed 58 with the established full-graph gate skipped. The complete suite
passed 227 with that same single opt-in skip; `compileall` passed.

The final production audit after source and dependency work still reported
3,032 / 3,168, V7 260 / 396, and 136 pending. Its journal digest and sidecar
inventory aggregate match the pre-edit audit, both scientific fingerprints
match, and all duplicate, missing, orphan, invalid-digest, and technical-invalid
counts are zero. The new importer also reverified the bundle against the
tracked recovery-point manifest and audited the restored alternate root.

No Task 017 scientific unit was executed, no scientific result changed, no
robustness score was computed, and Task 018 was not started.
