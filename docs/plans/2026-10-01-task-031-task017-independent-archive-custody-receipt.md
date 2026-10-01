# Task 031 — Task 017 independent archive custody receipt

Date: 2026-10-01. Final readback: 2026-10-01T03:43:52Z. Verdict: **COMPLETE**; classification **CUSTODY1 — INDEPENDENT_ARCHIVE_VERIFIED**. Originating repository HEAD and Task 030 authorization commit: `84ca71bae265c6f8f2c94ef1e756f6e3b22fbbb0`. Task 030 was **COMPLETE / A1 — ARCHIVAL_IMPLEMENTATION_READY** and authorized this one archival copy. Package version: `0.3.0`; `v0.3.0` peeled to `a1a6651163840a982799b1fa82c1904e67f84660`.

## Custody pair

Source bundle identity: Task 017P formal recovery point `task017-3168-8328714e-2026-09-29-formal`, identified by the tracked `artifacts/task017/recovery-manifest.json` and Task 030 record. The existing sealed pair was read from the historical external source directory recorded by Task 030. That machine-local source location is not required to retrieve this archive.

| File | Source bytes | Source SHA-256 | Final destination | Destination bytes | Destination SHA-256 |
| --- | ---: | --- | --- | ---: | --- |
| `task017-recovery-bundle.zip` | 3,151,434,246 | `3bea57aec891c8ca90b89229d786e0260d9fcfb0f92d8de8b2b5239f6f1d5170` | `B:\MaleCNS-Archive\task017-recovery-bundle.zip` | 3,151,434,246 | `3bea57aec891c8ca90b89229d786e0260d9fcfb0f92d8de8b2b5239f6f1d5170` |
| `recovery-manifest.json` | 439,274 | `a09661ac697614c05c6bafed88f590a5d00375f2eeeda0a84749ce73eb78edf8` | `B:\MaleCNS-Archive\recovery-manifest.json` | 439,274 | `a09661ac697614c05c6bafed88f590a5d00375f2eeeda0a84749ce73eb78edf8` |

Authorized destination root: `B:\MaleCNS-Archive`. Independence **D1 — DISTINCT_PHYSICAL_STORAGE_VERIFIED**. Windows `subst` reported `B:\` mapped to `D:\B`. Windows partition information placed source `C:\` on physical disk 1 and target `D:\` on physical disk 0. The different physical disk numbers, rather than the drive letters, establish this classification. The archive directory existed and was empty before copying; free space exceeded the pair size. Collision state: **E1 — ABSENT_SAFE_TO_CREATE**.

Copy method: direct byte-preserving file stream copy of the existing ZIP and manifest, without recompression, JSON rewriting, extraction, or checkpoint export. Temporary names were `task017-recovery-bundle.zip.task031.tmp` and `recovery-manifest.json.task031.tmp`, both inside the authorized destination. Both were required absent and created with exclusive create mode. Each temporary file passed SHA-256 and full structural verification before publication. The ZIP was published first, then the manifest, with existence and SHA-256 checked after each rename. Final destination bytes were read again for the complete verification. Existing files overwritten: **No**. Task 031 temporary files remaining: **None**.

Final verification: **PASS**. The manifest parsed and matched the tracked recovery identity. The ZIP opened and contained exactly 3,169 unique expected members: one journal and 3,168 sidecars; no missing, extra, duplicate, or unsafe member names. Every member stream matched its manifest SHA-256. The sidecar digest inventory aggregate matched. The checkpoint fingerprint `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`, complete matrix digest `19c51e79d883915398c2d3d89c3456f3160ba0062cf75abe20e97807979b1028`, journal SHA-256 `878a2b79fa442c539d4f803819e3154b060b4fbb3c6c5a2cb5a6af464503190e`, sidecar inventory SHA-256 `a24561d152e6acb9761c0b306d7a0158d487ce35e114ef02b543647326208553`, and historical execution seal `955b5e19d36e500cdbd148d8c5b4d70d21bf1289` matched tracked records. The matrix digest and execution seal are linked tracked identities, not independently recomputed ZIP members.

Retrieval classification: **R1 — ARCHIVE_READBACK_VERIFIED**. Minimum two-copy custody is satisfied by the original sealed pair and this independent disk copy. This immediate readback is not Task 017Q, a checkpoint import or restore, or cross-machine certification. Task 017Q remains **Q1 / KEEP_DEFERRED**.

Immutability classification: **I3 — LOGICALLY_IMMUTABLE_BY_POLICY**. Storage-enforced immutability and versioning/write protection were not established. Never overwrite either archive file in place; future changes require a new archive object or version. Verify retrieval against the SHA-256 identities above. This receipt does not claim protection against loss of the entire machine or site.

Scientific firewall: scientific simulations **0**; scientific endpoint calculations **0**; checkpoint exports **0**; checkpoint imports **0**; checkpoint restores **0**; Task 017Q executions **0**; MaleCNS raw-data downloads **0**; BANC work **0**; motif calculations **0**. Scientific artifacts, source code, and tests were not changed. No tag, release, or version mutation.
