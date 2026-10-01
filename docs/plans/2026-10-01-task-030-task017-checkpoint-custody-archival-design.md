# Task 030 — Task 017 checkpoint custody and archival design gate

Date: 2026-10-01. Verdict: **COMPLETE**. Classification: **A1 — ARCHIVAL_IMPLEMENTATION_READY**. Engineering design only; Task 017Q remains **Q1 — KEEP_DEFERRED**.

## Starting gate and identity

Local HEAD, `origin/master`, and live GitHub `master` were `2dd54ceb94c5603009c5761336caddca09746709`; worktree and stash were empty. Package version was `0.3.0`; `v0.3.0` peeled to `a1a6651163840a982799b1fa82c1904e67f84660`. No GitHub Actions workflows are tracked; repository policy is **NO GITHUB CI**, as Task 029 disposition P1 records. Task 026 is `NO_V0_4_SCIENTIFIC_QUESTION_CURRENTLY_READY`; Task 017 is `NOT_ROBUST`.

Tracked Task 017 recovery and complete-matrix manifests, the Task 017K completion record, and the research checkpoint agree on these identities:

| Identity | Verified value |
| --- | --- |
| Task 016 preregistration fingerprint | `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6` |
| Task 017 checkpoint fingerprint | `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63` |
| Complete matrix digest | `19c51e79d883915398c2d3d89c3456f3160ba0062cf75abe20e97807979b1028` |
| Journal SHA-256 | `878a2b79fa442c539d4f803819e3154b060b4fbb3c6c5a2cb5a6af464503190e` |
| Sidecar inventory SHA-256 | `a24561d152e6acb9761c0b306d7a0158d487ce35e114ef02b543647326208553` |
| Execution seal commit | `955b5e19d36e500cdbd148d8c5b4d70d21bf1289` |
| Tracked ZIP SHA-256 | `3bea57aec891c8ca90b89229d786e0260d9fcfb0f92d8de8b2b5239f6f1d5170` |
| Tracked export manifest SHA-256 | `a09661ac697614c05c6bafed88f590a5d00375f2eeeda0a84749ce73eb78edf8` |

The seal commit is historical provenance, not the export's `source_git_head` (`405ba38212487b1e6699cd61045893ad5eb27d38`). The latter identifies the commit at export. The matrix digest is a separate tracked identity, not a ZIP member checksum.

## Existing recovery machinery and local state

`scripts/export_task017_checkpoint.py DESTINATION` calls `write_recovery_bundle`. It audits the local checkpoint and writes a deterministic, uncompressed ZIP with sorted sidecar names, fixed timestamps and permissions, repository-relative names, and a JSON recovery manifest. Export rejects an existing ZIP or manifest and writes the ZIP via a `.tmp` file followed by `os.replace`; the manifest is written separately. Thus the pair is not atomically published as a unit. A failed export removes its temporary ZIP and manifest, but a pre-existing temporary file is not an explicit admission check. A future custody task should copy the *existing sealed pair*, not run export.

`scripts/import_task017_checkpoint.py BUNDLE_DIRECTORY` calls `restore_recovery_bundle`. It checks the ZIP digest, schema, tracked recovery-point match, Task 016/checkpoint fingerprints, exact archive member set and duplicates, safe relative member paths, journal and per-sidecar SHA-256, sidecar aggregate, and a full staged checkpoint audit including counts and pending keys. It rejects incompatible or partial destinations and stale import staging; an already identical destination is accepted read only. It stages under the destination parent, installs sidecars, then atomically places the journal as the final marker. On exceptions it removes newly installed files and staging. This is a two-step install with rollback, not a transactional filesystem operation or power-loss guarantee. Zero pending units are verifiable. Synthetic tests exercise corruption, missing/orphan/duplicate files, mismatch, interruption, and destination refusal. Task 030 performs no import.

Current state is **C1 — AUTHORITATIVE_BUNDLE_PRESENT**. Exactly one complete sealed export candidate was found at the historical external directory `C:\Temp\Task017-3168-8328714e-2026-09-29-formal`: `task017-recovery-bundle.zip` is 3,151,434,246 bytes and hashes to the tracked ZIP digest; `recovery-manifest.json` is 439,274 bytes and hashes to the tracked manifest digest. The live derived checkpoint journal is 6,464,975 bytes with the tracked journal digest; its sidecar directory contains 3,168 files totaling 3,144,088,441 bytes. The external pair, not the live derived state alone, is the archival source. These paths describe local discovery only and are not archive identities or required recovery paths. Timestamps were not used to decide authority. No scientific result content was inspected.

## Custody specification and archive choice

Preserve both export files byte for byte, including the exact ZIP and exact manifest. The immutable identity is their tracked SHA-256 pair, with ZIP SHA-256 serving as the whole-bundle digest. The manifest supplies schema/tool version, source commit, Task 016 and Task 017 fingerprints, journal digest, per-sidecar digests and inventory aggregate, complete unit ledger, and provenance. The execution seal and complete matrix digest remain linked through tracked records. A custody receipt should record creation time in UTC, storage location and independent-copy identifier, hashes and byte sizes of both files, repository commit used for verification, and the recovery instructions, without changing either sealed file. It must not embed an absolute source-machine path as a dependency or inspect scientific outcomes. Verification after transfer must hash both files against tracked identities, parse the manifest, and verify the ZIP inventory and member bytes. No Git history mutation is needed to recover.

| Form | Assessment |
| --- | --- |
| Existing Task 017P ZIP plus manifest | **Preferred.** Deterministic, Windows-readable ZIP_STORED; fixed metadata; stable checksum; exact inventory and byte verification available. About 3.15 GB, so destination must support files above 4 GB margin and transfer should verify bytes. Existing importer checks extraction safety. No new parser or format. |
| New deterministic ZIP | Feasible on Windows and large files with Zip64, but repeats the existing format and creates a new digest and identity. No needed metadata is absent from Task 017P. |
| Deterministic TAR | Stream-friendly for large files, but Windows tooling and path/link extraction rules add complexity; a new digest would need pinning. |
| Directory plus manifest | Simple direct per-file checks; 3,168 separate files increase partial-copy and filename-normalization exposure. Whole-directory identity requires a new canonicalization rule. |
| Compressed TAR | Reduces possible storage bytes but adds compressor determinism/version and extraction-safety concerns, CPU cost, and a new digest. |

No new archive format is justified. The existing ZIP stores content without relying on source timestamps, permissions, or absolute paths. Future copy must refuse an occupied destination unless its two files already match exactly; it must write temporary names, verify source and destination hashes, and publish the pair only after verification. The Task 017P exporter does not itself create an immutable off-machine custody copy.

## Storage classes and two-copy rule

| Class | Durability, access, and limits |
| --- | --- |
| Local second copy | Fast retrieval and no credentials, but same host failure and often same disk; mutable and not independent if same disk. |
| External drive | Independent of source disk when disconnected and stored separately; portable, but physical loss, filesystem file-size limits, and manual integrity checks matter. |
| NAS | Separate machine/storage may be independent with snapshots and checksum support; network and credentials can block retrieval; same-site hazards remain. |
| Object storage | Strong remote retrieval and optional versioning/immutability/checksum features; credentials, costs, provider policy, and private exposure controls need an owner. |
| GitHub release asset | Convenient repository-linked retrieval, but size/policy and public exposure/repository coupling make it unsuitable as a default for unpublished scientific state. |
| Personal cloud storage | Easy transfer; mutation/sync conflicts, credentials, size limits, and provider checksum semantics vary. |
| Institutional archive | Potential long-term governance, stable retrieval and access policy; ingest rules, approval, size limits, and credentials vary. |

Recommend **at least two custody copies**: the primary sealed export/working source and one independently retrievable secondary copy. Same disk is not independent; another disk in the same machine survives one disk failure but not machine loss; an external disk kept separately, separate machine, or private remote object storage qualifies for a minimum independent copy after hash verification. Prefer an external drive stored separately or private versioned object storage/institutional archive where available. No provider selected, no upload authorized. A second independent medium/site may improve durability, but this gate defines a minimum of two copies. The current C: export and D: live checkpoint do not establish durable cross-machine retrieval.

## Retrieval check and failure model

A future custody retrieval check reads the copied pair, compares their sizes and SHA-256 to the tracked recovery point, parses the manifest and checks schema/identities, enumerates ZIP members without extraction, rejects duplicate, unsafe, missing, or extra names, hashes the journal and every sidecar stream, and recomputes the sidecar inventory digest. It records a dated verification receipt. This checks transferred bytes and inventory only. It is **not Task 017Q** and claims no cross-machine restore, runnable checkpoint, simulation continuity, GPU portability, or scientific reproducibility.

| Failure | Task 017P control and remaining gap |
| --- | --- |
| Accidental deletion, source disk failure, lost credentials | Hashing cannot recover lost access; independent custody and access continuity are needed. |
| Silent corruption, truncation, provider mutation | Tracked ZIP and manifest digests detect changed bytes when retrieved; no automatic monitoring or repair. |
| Partial or stale copy, wrong bundle | Exact two-file tracked hashes and recovery-point comparison reject it; operator must verify after transfer. |
| Filename/path normalization, unsafe paths | Member allowlist, relative path checks and exact inventory detect archive-level changes; storage path and Unicode/case behavior require retrieval checking on target platform. |
| Duplicate or missing sidecars | Archive inventory and staged audit reject them; no scientific run needed. |
| Manifest/archive mismatch | ZIP digest, member inventory and per-file hashes reject it against tracked manifest. |
| Interrupted custody copy | Existing exporter/importer controls do not govern an external copy operation; future task needs temporary names, refusal of overwrite, cleanup and final hash verification. |

SHA-256 here detects accidental change against trusted tracked pins; it is not a guarantee against compromise of all pins and copies. The existing manifest has no archive creation timestamp field; the future custody receipt must supply a custody timestamp without altering sealed bytes.

## Disposition and next action

**A1 — ARCHIVAL_IMPLEMENTATION_READY.** The authoritative source pair is identified and matches the tracked hashes; existing identities, representation, and read-only verification procedure are sufficient; no scientific execution or unresolved overwrite behavior is required. **Exactly one next task:** create and verify one immutable archival copy of the existing Task 017P sealed ZIP and manifest, with a custody receipt. The operator must explicitly select the destination before any write outside the repository. Task 030 creates no copy.

Scientific simulations **0**; endpoint calculations **0**; checkpoint restores **0**; imports **0**; exports **0**; archive writes **0**; external uploads **0**; Task 017Q executions **0**; MaleCNS raw-data downloads **0**. Task 017 and Task 018 were not rerun; BANC and motifs were not inspected. Scientific artifacts, source and tests were not changed. No tag, release, or version mutation.
