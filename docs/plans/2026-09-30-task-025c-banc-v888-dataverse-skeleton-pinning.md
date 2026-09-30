# Task 025C — BANC v888 Dataverse skeleton archive pinning

Date: 2026-09-30. Verdict: **COMPLETE**. Pinning classification: **D2 — ARCHIVE_FIXED_BUT_GCS_CORRESPONDENCE_UNPROVEN**. Morphology archive prerequisite for future evidence acquisition: **M1 — ARCHIVAL_COVERAGE_PINNED**, provided the pinned Dataverse archive is used directly. This makes no MN9 identity decision.

## Starting checkpoint and Task 025B provenance

Repository root was derived with `git rev-parse --show-toplevel`. Local HEAD, `origin/master`, and live GitHub `master` were `e159ceb2e029aa8bf0ef0bb84c545d2ae99ad634`; the worktree and stash were empty. Package version was 0.3.0 and `v0.3.0^{}` was `a1a6651163840a982799b1fa82c1904e67f84660`. [Task 025B](2026-09-30-task-025b-banc-v888-morphology-archive-audit.md) recorded **M2 — ARCHIVAL_OBJECTS_PRESENT_PINNING_INCOMPLETE**, with PRESENT_PINNED 0, PRESENT_PINNING_UNCLEAR 35, ABSENT 0, UNRESOLVED 0. Its sole next action was this bounded Dataverse v888 ZIP metadata and member-name pinning audit. Its 35 GCS generations, MD5s, CRC32Cs, ETags, update times, and byte lengths remain the existing GCS evidence; none of those objects was downloaded here.

## Authoritative dataset and archive identity

The [BANC producer README](https://github.com/htem/bancpipeline/tree/5c333c12f0b9e03873f88cf4e23cad34c0bb49c1) identifies the Harvard Dataverse deposit `doi:10.7910/DVN/7WTH1N` and `banc_swc_skeletons.zip` as the frozen paper copy for v888, while describing GCS as mutable. The [producer export code](https://github.com/htem/bancpipeline/blob/5c333c12f0b9e03873f88cf4e23cad34c0bb49c1/banc/share/banc-export-skeletons.R) defines the `<root_id>_skeleton.swc` naming contract. [Harvard Dataverse's exact version 3.0 API record](https://dataverse.harvard.edu/api/datasets/:persistentId/versions/3.0?persistentId=doi:10.7910/DVN/7WTH1N) provides the following primary metadata:

| Field | Recorded value |
| --- | --- |
| Installation | Harvard Dataverse, `dataverse.harvard.edu` |
| Dataset title | Publication version: Distributed control circuits across a brain-and-cord connectome |
| Dataset PID | `doi:10.7910/DVN/7WTH1N` |
| Dataset version | **3.0**, state `RELEASED` |
| Dataset first publication date | 2026-05-27 |
| Exact version release time | 2026-07-01T12:45:04Z |
| Authors/depositor | 100 authors in citation metadata, led by Bates, Alexander S.; depositor Bates, Alexander Shakeel; deposit date 2026-04-29 |
| Archive location/filename | `skeletons/banc_swc_skeletons.zip` |
| File ID/PID | Dataverse file ID **13952186**; file PID empty/unassigned in this record |
| Archive byte length | **16,583,469,842** |
| Archive checksum | **MD5 `7e73e3ca52fdbd4c67d112fbc267948c`** (Dataverse metadata) |
| File access | `restricted=false`; public file download succeeded with a range GET |

The [file metadata endpoint](https://dataverse.harvard.edu/api/files/13952186) independently exposes file identity and metadata. The archive description explicitly says that it contains v888 print-materialization and v626 preprint-materialization root IDs, that v888 is the paper version of record, and that the single ZIP was packaged from the source GCS directory. This establishes intended export provenance and explains why archive-wide names alone must be filtered by the frozen v888 IDs. It does not establish equality with the **current** GCS object generations.

## Access-method audit

Task 025B's dataset API HTTP 403 was not reproduced: anonymous `GET /api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/7WTH1N` returned HTTP 200, as did `GET /api/datasets/:persistentId/versions/3.0?...`, metadata export `GET /api/datasets/export?exporter=dataverse_json&persistentId=...`, and file metadata `GET /api/files/13952186`. The dataset landing page and DOI resolution reached Harvard Dataverse but returned HTTP 202 with an empty body in this environment. The cause of the earlier 403 is **undetermined**. A plain Python `HEAD` and range GET without a browser user agent returned 403; an anonymous browser-user-agent range GET through `GET /api/access/datafile/13952186` redirected to a temporary signed public S3 URL and returned HTTP 206. This is a legitimate public download mechanism, with no credentials or access-control bypass. The signed URL is temporary and is not the archival pin. No full ZIP download occurred.

## Published-version semantics and retrieval rule

[Dataverse dataset-version documentation](https://guides.dataverse.org/en/6.7/user/dataset-management.html#dataset-versions) says edits to a published dataset create a draft; publishing that draft creates another numbered version. Its [replace-file documentation](https://guides.dataverse.org/en/6.7/user/dataset-management.html#replace-files) says replacement creates a new draft and previous file versions remain accessible through version history. Thus a normal replacement does not mutate the already released 3.0 file association. Dataverse administrators may have exceptional powers, and deaccession or service availability can affect future access; this is an archival version pin, not an absolute permanence guarantee. The [Native API version specifiers](https://guides.dataverse.org/en/latest/api/native-api.html#dataset-version-specifiers) distinguish explicit `3.0` from `:latest`, `:latest-published`, and `:draft`; the dataset DOI alone does not select an immutable version. File IDs identify files, while a replacement can receive a different file identity; a file PID was not assigned here. The checksum is recorded in the exact version's file metadata. We did **not** hash all 16.58 GB, so the archive MD5 was **not independently verified**; the HTTP byte range and ZIP central-directory structure were checked against the recorded byte length.

Minimum archive pin: **dataset DOI `doi:10.7910/DVN/7WTH1N` + exact released dataset version `3.0` + file ID `13952186` + `skeletons/banc_swc_skeletons.zip` + byte length `16583469842` + Dataverse MD5 `7e73e3ca52fdbd4c67d112fbc267948c`**. Future use must query dataset version `3.0`, confirm that file ID/name/length/checksum still match, download that file, and verify its MD5 before using a member. Never substitute an unqualified DOI landing page or a `latest` selector. A member name identifies coverage, not the member's bytes.

## ZIP member-name inspection and 35-ID results

The public file endpoint supported HTTP range GET. The final 65,557 bytes gave the ZIP end record and ZIP64 locator. The ZIP64 end record specified central-directory offset **16,563,620,346** and length **19,849,398**. One HTTP 206 range fetched exactly bytes `16563620346-16583469743` (19,849,398 bytes). Only ZIP central-directory records were parsed, yielding 185,280 unique member names, of which 101,387 ended `_skeleton.swc`. No compressed member data, SWC body, coordinate, or morphology content was requested. The full ZIP was **not downloaded**, no SWC was extracted, and the Dataverse archive checksum was not independently recalculated.

| Frozen v888 ID | Exact archive member | Result |
| --- | --- | --- |
| `720575941449780405` | `720575941449780405_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941536822514` | `720575941536822514_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941484914498` | `720575941484914498_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941662402360` | `720575941662402360_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941603110134` | `720575941603110134_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941626721900` | `720575941626721900_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941604209142` | `720575941604209142_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941513444089` | `720575941513444089_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941656201177` | `720575941656201177_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941628933433` | `720575941628933433_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941480581856` | `720575941480581856_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941430258647` | `720575941430258647_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941589105292` | `720575941589105292_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941627279515` | `720575941627279515_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941553702042` | `720575941553702042_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941410682479` | `720575941410682479_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941623743434` | `720575941623743434_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941588099140` | `720575941588099140_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941588254206` | `720575941588254206_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941511829520` | `720575941511829520_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941462808077` | `720575941462808077_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941545764232` | `720575941545764232_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941454079539` | `720575941454079539_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941519595447` | `720575941519595447_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941652113685` | `720575941652113685_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941402863216` | `720575941402863216_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941494208128` | `720575941494208128_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941454240169` | `720575941454240169_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941687084527` | `720575941687084527_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941454380013` | `720575941454380013_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941558268943` | `720575941558268943_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941599758121` | `720575941599758121_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941547120161` | `720575941547120161_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941623285450` | `720575941623285450_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |
| `720575941603103990` | `720575941603103990_skeleton.swc` | ARCHIVE_MEMBER_PRESENT |

Totals: **ARCHIVE_MEMBER_PRESENT 35; ARCHIVE_MEMBER_ABSENT 0; ARCHIVE_MEMBER_AMBIGUOUS 0; UNRESOLVED 0; total 35**. Each listed name occurred exactly once.

## Correspondence, consequence, limitations, and next action

The producer documentation and Dataverse description connect this ZIP to the intended BANC v888 paper export and its source GCS directory. The archived members cover all 35 frozen IDs. However, no member bytes were compared with Task 025B's **current** GCS generations; filename equality and the producer's packaging statement cannot prove byte identity after mutable GCS updates. **GCS/Dataverse byte identity: No.** It is **not required** for future morphology acquisition if that work uses the exact pinned Dataverse archive directly and verifies the downloaded archive's MD5. It remains required for any claim that a particular current GCS object equals an archived member. Consequently D2, rather than D1, applies; M1 applies to the direct-archive route, resolving the archival prerequisite for that route. No morphology interpretation or identity adjudication follows from M1.

**Exactly one recommended next action:** BANC v888 wilson_lab Annotation Provenance Audit, to determine whether relevant labels are native, transferred, mixed, or otherwise derived. That research was not begun here.

Connectivity-blind declaration: candidate identity decisions **0**; morphology interpretations **0**; morphology comparisons **0**; SWC parsing **0**; coordinate parsing **0**; morphology rendering **0**; BANC connectivity queries **0**; partner-edge queries **0**; synapse-count calculations **0**; MaleCNS endpoint calculations **0**. No Task 018 outcome was inspected. Task 017Q remains **KEEP_DEFERRED**. Archive names and checksums do not establish biological identity, laterality, reconstruction quality, or similarity.
