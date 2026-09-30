# Task 025B ? BANC v888 morphology archive audit

Date: 2026-09-30. Verdict: **COMPLETE** for this bounded file-presence and version-pinning audit. Morphology archive status: **M2 ? ARCHIVAL_OBJECTS_PRESENT_PINNING_INCOMPLETE**. This is an audit record, not a scientific result.

## Starting checkpoint and Task 025A provenance

At entry, local HEAD, `origin/master`, and live GitHub `master` were `0f5bc1b290ec5ab8eb4b9c57dbc05ea9b669db7a`; worktree and stash were empty. Package version: 0.3.0. The v0.3.0 tag peeled to `a1a6651163840a982799b1fa82c1904e67f84660`. [Task 025A](2026-09-30-task-025a-banc-v888-identity-evidence-acquisition.md) has evidence readiness **E6 ? MULTIPLE_EVIDENCE_GAPS_REMAIN** and recommends exactly this bounded v888 archival morphology release-pinning and 35-ID file-presence audit. Its earlier single-object body probe and `_l2.swc` 404 were not treated as coverage evidence here.

## Authoritative archive documentation and naming contract

- The [BANC project data-location index at commit e31a2e26](https://github.com/htem/BANC-project/blob/e31a2e26b9937dca72e5ca1c1960df6454d76114/manuscript/print/banc_data_locations.md) names bucket `lee-lab_brain-and-nerve-cord-fly-connectome`, v888 SWC directory `compiled_data/banc_888/banc_banc_space_swc`, and mesh directory `imported_meshes/banc_meshes`. It describes these as material intended for a Dataverse ZIP, without giving per-object immutable identifiers.
- The [producer export code at commit 5c333c12](https://github.com/htem/bancpipeline/blob/5c333c12f0b9e03873f88cf4e23cad34c0bb49c1/banc/share/banc-export-skeletons.R) uses valid `banc_<ver>` metadata root IDs, copies available skeleton sources as `<root_id>_skeleton.swc`, copies available L2 SWC sources as `<root_id>_l2.swc`, and mirrors the export directory to `compiled_data/banc_<ver>/banc_banc_space_swc/`. Thus `_skeleton.swc` is an explicit producer output and the expected skeleton route for this audit; `_l2.swc` is a separately conditional output, not a required fallback. The code does not establish that the two types are equivalent or that either file's contents match the historical materialization state.
- The [producer README at the same commit](https://github.com/htem/bancpipeline/tree/5c333c12f0b9e03873f88cf4e23cad34c0bb49c1) calls v888 the paper snapshot, describes `banc_swc_skeletons.zip` in the Harvard Dataverse deposit `doi:10.7910/DVN/7WTH1N` as the frozen paper copy, and explicitly describes GCS as mutable. Therefore `banc_888` in a GCS pathname is a release namespace, not by itself an immutability guarantee. Meshes are separate `.obj` products and were not queried.

## Frozen set and metadata-only method

Exactly the 35 v888 root IDs in [Task 025](2026-09-30-task-025-independent-banc-v888-mn9-identity-adjudication.md) were used as equivalent archival lookup keys, in its recorded order. No labels, sides, or identity plausibility were used to choose paths. For each ID, an anonymous GCS JSON object-metadata GET requested exactly `compiled_data/banc_888/banc_banc_space_swc/<id>_skeleton.swc` from the public bucket. This returns metadata JSON, never the SWC body. The `name`, `size`, `generation`, `md5Hash`, `crc32c`, `etag`, and `updated` fields were available for every object. The table records path, HTTP status, byte length, generation, and Base64 MD5. Lengths are technical metadata only. No SWC was downloaded, opened, parsed, or rendered in this task.

| Frozen v888 root ID | Expected object path relative to bucket | Metadata HTTP | Bytes | GCS generation | GCS MD5 (Base64) | Classification |
| --- | --- | ---: | ---: | --- | --- | --- |
| `720575941449780405` | `compiled_data/banc_888/banc_banc_space_swc/720575941449780405_skeleton.swc` | 200 | 1562965 | `1777944381079503` | `1RtBQq+3mL5YHeIspmieoA==` | PRESENT_PINNING_UNCLEAR |
| `720575941536822514` | `compiled_data/banc_888/banc_banc_space_swc/720575941536822514_skeleton.swc` | 200 | 1453132 | `1777944867530938` | `3E0qKL9By08ZyB+r3MKAJQ==` | PRESENT_PINNING_UNCLEAR |
| `720575941484914498` | `compiled_data/banc_888/banc_banc_space_swc/720575941484914498_skeleton.swc` | 200 | 288555 | `1777944561223019` | `vBOYscMkGThZKf6wXB32nw==` | PRESENT_PINNING_UNCLEAR |
| `720575941662402360` | `compiled_data/banc_888/banc_banc_space_swc/720575941662402360_skeleton.swc` | 200 | 846345 | `1777945440037951` | `gNstEQzOhCqU46xj+3cV/A==` | PRESENT_PINNING_UNCLEAR |
| `720575941603110134` | `compiled_data/banc_888/banc_banc_space_swc/720575941603110134_skeleton.swc` | 200 | 569335 | `1777945242592985` | `b2UJWYaBijICfDDdWTdAjg==` | PRESENT_PINNING_UNCLEAR |
| `720575941626721900` | `compiled_data/banc_888/banc_banc_space_swc/720575941626721900_skeleton.swc` | 200 | 767686 | `1777945327878033` | `WXFEiVidoT3sYKs8PTeqaw==` | PRESENT_PINNING_UNCLEAR |
| `720575941604209142` | `compiled_data/banc_888/banc_banc_space_swc/720575941604209142_skeleton.swc` | 200 | 1130967 | `1777945246857712` | `eM42qR8M8ctLNWlSS/3q2Q==` | PRESENT_PINNING_UNCLEAR |
| `720575941513444089` | `compiled_data/banc_888/banc_banc_space_swc/720575941513444089_skeleton.swc` | 200 | 609433 | `1777944718787914` | `bZrFr8rjsMmp7ZqUca9aOw==` | PRESENT_PINNING_UNCLEAR |
| `720575941656201177` | `compiled_data/banc_888/banc_banc_space_swc/720575941656201177_skeleton.swc` | 200 | 322696 | `1777945423204023` | `38UjPK/Bd7uJx+HU5EqMpg==` | PRESENT_PINNING_UNCLEAR |
| `720575941628933433` | `compiled_data/banc_888/banc_banc_space_swc/720575941628933433_skeleton.swc` | 200 | 763674 | `1777945339200548` | `YgyB4pK3HnrihXAJIKIL6w==` | PRESENT_PINNING_UNCLEAR |
| `720575941480581856` | `compiled_data/banc_888/banc_banc_space_swc/720575941480581856_skeleton.swc` | 200 | 653120 | `1777944531451378` | `HTGqv00bEzLbGP5iiohSrw==` | PRESENT_PINNING_UNCLEAR |
| `720575941430258647` | `compiled_data/banc_888/banc_banc_space_swc/720575941430258647_skeleton.swc` | 200 | 25309 | `1777944292027456` | `UM5hYIEIb3+XR/q09N/0HQ==` | PRESENT_PINNING_UNCLEAR |
| `720575941589105292` | `compiled_data/banc_888/banc_banc_space_swc/720575941589105292_skeleton.swc` | 200 | 1371338 | `1777945174084145` | `r9F3zRsSYrAST91MxFgytA==` | PRESENT_PINNING_UNCLEAR |
| `720575941627279515` | `compiled_data/banc_888/banc_banc_space_swc/720575941627279515_skeleton.swc` | 200 | 1194161 | `1777945332072756` | `triDPZ4MCvPZVSjZNhxFoQ==` | PRESENT_PINNING_UNCLEAR |
| `720575941553702042` | `compiled_data/banc_888/banc_banc_space_swc/720575941553702042_skeleton.swc` | 200 | 968553 | `1777944971189412` | `JVW8Cl8E4g2X51axnC5SVQ==` | PRESENT_PINNING_UNCLEAR |
| `720575941410682479` | `compiled_data/banc_888/banc_banc_space_swc/720575941410682479_skeleton.swc` | 200 | 3715295 | `1777944259235353` | `IJiiFMD0P28ps5tO/IK2yQ==` | PRESENT_PINNING_UNCLEAR |
| `720575941623743434` | `compiled_data/banc_888/banc_banc_space_swc/720575941623743434_skeleton.swc` | 200 | 853172 | `1777945313416632` | `lxToVqhBd7w1p8Ec4Mfb6w==` | PRESENT_PINNING_UNCLEAR |
| `720575941588099140` | `compiled_data/banc_888/banc_banc_space_swc/720575941588099140_skeleton.swc` | 200 | 1348845 | `1777945170858855` | `E4FcVMSfVV75rmibmtSL1g==` | PRESENT_PINNING_UNCLEAR |
| `720575941588254206` | `compiled_data/banc_888/banc_banc_space_swc/720575941588254206_skeleton.swc` | 200 | 245973 | `1777945170413331` | `09Kf/gsKcnSe0rV6sne75A==` | PRESENT_PINNING_UNCLEAR |
| `720575941511829520` | `compiled_data/banc_888/banc_banc_space_swc/720575941511829520_skeleton.swc` | 200 | 1132095 | `1777944711222875` | `o/9htp5TLR0we1fIoG+66w==` | PRESENT_PINNING_UNCLEAR |
| `720575941462808077` | `compiled_data/banc_888/banc_banc_space_swc/720575941462808077_skeleton.swc` | 200 | 884391 | `1777944442492319` | `WMAh7BzfiNIAjVvWU6nQrQ==` | PRESENT_PINNING_UNCLEAR |
| `720575941545764232` | `compiled_data/banc_888/banc_banc_space_swc/720575941545764232_skeleton.swc` | 200 | 607265 | `1777944920603053` | `rXM1xtWl+e9HglXMifNgog==` | PRESENT_PINNING_UNCLEAR |
| `720575941454079539` | `compiled_data/banc_888/banc_banc_space_swc/720575941454079539_skeleton.swc` | 200 | 832363 | `1777944403968500` | `T8ycdmk+JicS59mcmHcq2g==` | PRESENT_PINNING_UNCLEAR |
| `720575941519595447` | `compiled_data/banc_888/banc_banc_space_swc/720575941519595447_skeleton.swc` | 200 | 729277 | `1777944762702873` | `LrnPQCD6XZZT88/H+gMqEQ==` | PRESENT_PINNING_UNCLEAR |
| `720575941652113685` | `compiled_data/banc_888/banc_banc_space_swc/720575941652113685_skeleton.swc` | 200 | 1297904 | `1777945406956604` | `G0MPquF4MZsTj+yvNvEO1A==` | PRESENT_PINNING_UNCLEAR |
| `720575941402863216` | `compiled_data/banc_888/banc_banc_space_swc/720575941402863216_skeleton.swc` | 200 | 116148 | `1777944240701986` | `BU9prWU1npX7dWm0Mn3+tQ==` | PRESENT_PINNING_UNCLEAR |
| `720575941494208128` | `compiled_data/banc_888/banc_banc_space_swc/720575941494208128_skeleton.swc` | 200 | 515791 | `1777944608308653` | `Y52PJU+/d25E6e5HtPvduw==` | PRESENT_PINNING_UNCLEAR |
| `720575941454240169` | `compiled_data/banc_888/banc_banc_space_swc/720575941454240169_skeleton.swc` | 200 | 846869 | `1777944404206317` | `DgZt7b52HNUZqLjtB54Quw==` | PRESENT_PINNING_UNCLEAR |
| `720575941687084527` | `compiled_data/banc_888/banc_banc_space_swc/720575941687084527_skeleton.swc` | 200 | 620969 | `1777945470102243` | `Mqm0Erp2DdTs/va44yv7aw==` | PRESENT_PINNING_UNCLEAR |
| `720575941454380013` | `compiled_data/banc_888/banc_banc_space_swc/720575941454380013_skeleton.swc` | 200 | 113633 | `1777944404634231` | `Ed1a7oVoOYElLYf+kQyBGw==` | PRESENT_PINNING_UNCLEAR |
| `720575941558268943` | `compiled_data/banc_888/banc_banc_space_swc/720575941558268943_skeleton.swc` | 200 | 1601615 | `1777945002165815` | `WOPixa/iAAL0zNxIIA+ANg==` | PRESENT_PINNING_UNCLEAR |
| `720575941599758121` | `compiled_data/banc_888/banc_banc_space_swc/720575941599758121_skeleton.swc` | 200 | 1928199 | `1777945235338060` | `W1YihwYJEi/CvRQqfwWcrg==` | PRESENT_PINNING_UNCLEAR |
| `720575941547120161` | `compiled_data/banc_888/banc_banc_space_swc/720575941547120161_skeleton.swc` | 200 | 965809 | `1777944929560662` | `0rC740caZL7q/iGhWUPBzw==` | PRESENT_PINNING_UNCLEAR |
| `720575941623285450` | `compiled_data/banc_888/banc_banc_space_swc/720575941623285450_skeleton.swc` | 200 | 4238867 | `1777945313922762` | `g/IJwDoS2SgmsXURNEpLVw==` | PRESENT_PINNING_UNCLEAR |
| `720575941603103990` | `compiled_data/banc_888/banc_banc_space_swc/720575941603103990_skeleton.swc` | 200 | 1056837 | `1777945243173311` | `7xwWMkIKY8Ig716tYs1H+Q==` | PRESENT_PINNING_UNCLEAR |

Coverage: **PRESENT_PINNED 0; PRESENT_PINNING_UNCLEAR 35; ABSENT 0; UNRESOLVED 0; total 35**. Every listed object exists at the v888-namespaced path as of this audit. Every row has a reproducible current GCS object generation and MD5, but the release linkage and durable future retrieval guarantee remain incomplete; this is why none is classified PRESENT_PINNED. No candidate was excluded scientifically.

## Version-pinning evidence and future retrieval rule

[Google Cloud object metadata documentation](https://cloud.google.com/storage/docs/metadata) states that a generation identifies a specific object version and changes when the same name is rewritten. Its MD5 is a technical checksum (not a morphology or release-equivalence claim). [Google Cloud Object Versioning documentation](https://cloud.google.com/storage/docs/object-versioning) says prior generations are retained on replacement only when Object Versioning is enabled, subject also to lifecycle deletion. Anonymous `storage.buckets.get` for this bucket returned HTTP 401, so **bucket Object Versioning could not be verified**. The producer documents the GCS copy as mutable, and no project convention establishes the GCS v888 prefix as immutable. A generation identifies the bytes observed today but does not alone guarantee they will remain retrievable after replacement or deletion.

The export code maps valid `banc_<ver>` metadata root IDs directly to output filenames; the frozen `banc_888_id` is therefore the appropriate lookup key without latest-root substitution. The metadata audit cannot prove that every live GCS file is byte-identical to the frozen Dataverse paper archive or generated from the exact v888 segmentation state. Later chunked-graph splits or merges do not alter an already stored object by themselves; rerunning or replacing the export could. No current-root or cross-version conversion was used.

Minimum future **technical retrieval pin** for each current GCS object: dataset `BANC v888`; frozen `banc_888_id`; full bucket/object path; recorded GCS generation; and recorded checksum. A future retrieval must request that generation and verify the checksum, then fail closed if unavailable or mismatched. To claim a release-pinned archival object, additionally identify a fixed Dataverse dataset version and the `banc_swc_skeletons.zip` file version/checksum, and establish the member-to-GCS-object correspondence. The public Dataverse dataset API returned HTTP 403 during this audit; no ZIP member manifest, archived-file checksum, or immutable file version was verified. No bodies were downloaded to bridge that gap.

Technical status: **35/35 current GCS paths are accessible by metadata**, so a future metadata-based lookup is feasible now. **35/35 durable retrieval of the same release bytes is not yet established**. Morphology evidence class M is not yet sufficient for future adjudication. The remaining blocker is the unverified link from the mutable current GCS objects to a fixed paper-release archive, plus unverified retention of their GCS generations.

## Disposition and exactly one next action

**M2 ? ARCHIVAL_OBJECTS_PRESENT_PINNING_INCOMPLETE.** Conduct one bounded version-pinning audit of the fixed Harvard Dataverse v888 skeleton ZIP: obtain its published dataset/file version and checksum, inspect only its archive member-name manifest (without extracting or reading SWCs), and verify that all 35 expected member names correspond to the recorded GCS objects by an evidence-backed release mapping. Do not begin that task here.

## Information boundary and scientific nonclaims

Connectivity-blindness declaration: no BANC connectivity, partner-edge, synapse-count, or MaleCNS endpoint data was queried or calculated; no Task 018 outcome details were inspected. Candidate identity decisions: **0**. Morphology interpretations: **0**. Morphology comparisons: **0**. SWC coordinate parsing: **0**. Morphologies rendered: **0**. Morphology bodies downloaded in this task: **0**. BANC connectivity queries: **0**. Partner-edge queries: **0**. Synapse-count calculations: **0**. MaleCNS endpoint calculations: **0**. Task 017Q: **KEEP_DEFERRED**. Neither file presence nor checksum/size establishes biological identity, laterality, reconstruction quality, equivalence of SWC variants, or morphology similarity. Task 025A P and L gaps remain untouched.
