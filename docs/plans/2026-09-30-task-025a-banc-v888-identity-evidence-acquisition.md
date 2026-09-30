# Task 025A — BANC v888 MN9 identity evidence acquisition

Date: 2026-09-30. Verdict: **COMPLETE** for the bounded evidence audit. Evidence readiness: **E6 — MULTIPLE_EVIDENCE_GAPS_REMAIN**. This record makes no MN9 identity decision.

## Start gate and historical boundary

Starting local HEAD, `origin/master`, and live GitHub master were `7a9c7aee554bbe694e77d09ef6b73b9d8708f5e5`. The only untracked file was the Task 025 record; the stash was empty. Package version was 0.3.0 and the v0.3.0 tag peeled to `a1a6651163840a982799b1fa82c1904e67f84660`. The Task 025 record remains unchanged: **STOP**, **NOT_IDENTIFIABLE**, `BANC_MN9_L` and `BANC_MN9_R` not frozen. Its complete 35-candidate inventory remains intact. Its two MN9-labeled IDs are candidates only.

## Morphology access and bounded test

The [BANC project data-location index](https://github.com/htem/BANC-project/blob/main/manuscript/print/banc_data_locations.md) names `gs://lee-lab_brain-and-nerve-cord-fly-connectome/compiled_data/banc_888/banc_banc_space_swc` for v888 SWCs and `imported_meshes/banc_meshes` for meshes. The [producer pipeline](https://github.com/htem/bancpipeline) describes a public, unauthenticated GCS bucket, per-root skeleton files, and a static Harvard Dataverse paper deposit. The GCS copy is described as mutable; the Dataverse copy is the archival route. Skeletons are pipeline products, not a demonstrated live CAVE generation call. The exact relationship between the snapshot's `banc_888_id` and every stored filename has not been verified.

One quarantined candidate, `720575941410682479`, was used solely as an access probe. `GET https://storage.googleapis.com/lee-lab_brain-and-nerve-cord-fly-connectome/compiled_data/banc_888/banc_banc_space_swc/720575941410682479_l2.swc` returned 404. The corresponding `_skeleton.swc` returned HTTP 200, SWC text, 3,715,295 bytes, SHA-256 `e60fb7663d40a7591fde55da23c9208d14d0fc9f6540c5c624114940c6b1356e`. The returned SWC has coordinate fields; their biological orientation was not interpreted. No morphology features were read, scored, or compared. The tested URL is v888-namespaced and uses the snapshot ID directly, avoiding a latest-root resolution call, but the mutable bucket does not by itself provide an immutable file-version guarantee. No authentication was needed. The earlier 404 established only that its particular URL failed.

The route is technically parameterized by root ID, but existence and release-pinned access were not checked for the other 34 candidates. Coverage: **0 confirmed accessible, 0 confirmed unavailable, 35 unresolved** for the full inventory as a release-pinned package. The single probe proves access for one current GCS object only and is deliberately excluded from the coverage count.

## Annotation provenance

The [snapshot README](https://github.com/htem/BANC-project/blob/main/data/meta/README.md) says `banc_888_meta_20260521.parquet` is a bundled snapshot assembled from live SeaTable manual curations, GCS segmentation properties, and cross-dataset matches, with SeaTable priority for cell types. The [BANC data-location index](https://github.com/htem/BANC-project/blob/main/manuscript/print/banc_data_locations.md) also identifies v888 community `cell_info` and core-team `codex_annotations` tables. The [producer pipeline](https://github.com/htem/bancpipeline) documents both manual review and automated alignment workflows in general. None of these sources traces the particular `wilson_lab` MN9 labels to an original curator, source row, method, date, confidence note, independently assigned side, or exact-neuron identity claim. The `wilson_lab` field alone does not establish those facts. Classification: **PROVENANCE_UNRESOLVED**; native/transferred/mixed status **unresolved**. The snapshot date is known, not the annotation date.

## Laterality and coordinates

The [BANC dataset documentation](https://github.com/sjcabs/fly_connectome_data_tutorial/blob/main/data/dataset_documentation/banc_data.md) describes BANC-space coordinates, voxel/nanometre position variants, v888 root identifiers, and `side` metadata. The [bancr client documentation](https://github.com/natverse/bancr) describes `L` and `R` side values and BANC nanometre coordinates, and notes that mirror operations use a symmetric template because native BANC space is asymmetric. These sources do not establish a sufficiently explicit native left/right axis sign, midline, source-image/display reflection, nerve-side rule, or independent check of the relevant metadata side labels. Classification: **LATERALITY_PARTIALLY_DOCUMENTED**. Candidate-level side adjudication was not attempted.

## Root and version semantics

The [BANC dataset documentation](https://github.com/sjcabs/fly_connectome_data_tutorial/blob/main/data/dataset_documentation/banc_data.md) calls `banc_888_id` the root ID at CAVE materialization 888 and lists `root_626`, `root_850`, and `root_888` cross-version columns plus a supervoxel ID for current-root resolution. The [producer pipeline](https://github.com/htem/bancpipeline) identifies v888 as the paper snapshot and distinguishes the mutable GCS mirror from the static Dataverse deposit. Safe future retrieval rule: use the exact `banc_888_id` from the frozen snapshot against an explicitly v888-namespaced file or pinned Dataverse release; record the object hash; never substitute `get_latest_roots`, current CAVE roots, or an unverified cross-version mapping. This is a proposed safety rule, not a complete proof of split/merge or timestamp semantics for all 35 IDs. Classification: **VERSION_PINNING_PARTIAL**.

## Readiness and next action

M sufficient: **No** (one mutable-bucket access probe; all-candidate archival coverage unverified). P sufficient: **No**. L sufficient: **No**. V sufficient: **No**. Therefore E6. No adjudicator manifest was created. The single recommended next action is a bounded **v888 morphology release-pinning and 35-ID file-presence audit** against the archival Dataverse deposit, recording immutable archive identity and per-ID presence without opening or comparing candidate morphologies. This is prerequisite to a reproducible complete inventory; annotation and laterality gaps remain for later work. Do not start candidate adjudication.

## Scientific firewall and accounting

Scientific executions: 0. Candidate identity decisions: 0. Candidate morphology comparisons: 0. BANC connectivity queries: 0. Partner-edge queries: 0. Synapse-count calculations: 0. MaleCNS endpoint calculations: 0. Task 017 rerun: No. Task 018 rerun: No. Task 017Q execution: No; disposition **KEEP_DEFERRED**. No connectivity outcome was accessed or encountered. No source, test, or scientific artifact was changed. No tag, release, or version mutation was made.
