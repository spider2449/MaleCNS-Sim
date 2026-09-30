# Task 025D — BANC v888 `wilson_lab` annotation provenance audit

Date: 2026-09-30. Verdict: **COMPLETE** (bounded audit). Provenance: **P3 — PROVENANCE_UNRESOLVED**. P sufficient for future identity adjudication: **NO**. Independence: **I5 — INDEPENDENCE_UNRESOLVED**. Task 025 remains **STOP / NOT_IDENTIFIABLE**; no BANC MN9 side is frozen.

## Starting checkpoint and Task 025C

Repository root was derived with `git rev-parse --show-toplevel`. Starting local HEAD, `origin/master`, and live GitHub `master` all equaled `d25e3d6b6c14093a593b2445267cccbb94483c52`; worktree and stash were empty. Package version was `0.3.0`; `v0.3.0^{}` was `a1a6651163840a982799b1fa82c1904e67f84660`. [Task 025C](2026-09-30-task-025c-banc-v888-dataverse-skeleton-pinning.md) classified the archive **D2 — ARCHIVE_FIXED_BUT_GCS_CORRESPONDENCE_UNPROVEN**, established **M1** for future direct use of its pinned Dataverse archive, and specified exactly this audit as its sole next action.

## Sources and frozen identities

Retrieved 2026-09-30. The [BANC-project repository](https://github.com/htem/BANC-project/tree/e31a2e26b9937dca72e5ca1c1960df6454d76114), pinned at `e31a2e26b9937dca72e5ca1c1960df6454d76114`, contains `data/meta/banc_888_meta_20260521.parquet`, its [snapshot README](https://github.com/htem/BANC-project/blob/e31a2e26b9937dca72e5ca1c1960df6454d76114/data/meta/README.md), and `R/startup/banc-meta-live.R`. The frozen parquet has 188,508 rows; this is the snapshot examined here. The [producer repository](https://github.com/htem/bancpipeline/tree/5c333c12f0b9e03873f88cf4e23cad34c0bb49c1), pinned at `5c333c12f0b9e03873f88cf4e23cad34c0bb49c1`, contains curation update scripts and [taxonomy documentation](https://github.com/htem/bancpipeline/blob/5c333c12f0b9e03873f88cf4e23cad34c0bb49c1/annotations/annotations.md). The [BANC metadata deposit description](https://github.com/htem/BANC-project/blob/e31a2e26b9937dca72e5ca1c1960df6454d76114/manuscript/print/dataverse/documentation/banc_888_meta.md) identifies the separate 79-column paper feather and DOI `10.7910/DVN/7WTH1N`; it is useful documentation but is **not** the examined 165-column parquet. The [final paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC13518251/) describes BANC v888 annotation and cross-dataset matching generally. None supplies a versioned, row-level `wilson_lab` source table for these 35 rows. No source neuron ID, crosswalk release, or source-file checksum could be pinned.

## Relevant fields and merge path

All listed fields in the examined parquet are string-like annotation values unless noted; empty/null means no value recorded, not biological absence. The paper feather documentation describes many semantic roles, but its schema is not identical to this parquet. The table therefore distinguishes documented meaning from observed snapshot use.

| Field | Documented/observed meaning | Provenance and limits |
|---|---|---|
| `root_id` | BANC v888 neuron key; string | Snapshot join key, not a type assertion. |
| `cell_type` | Most specific hierarchy term; string | SeaTable/manual-curation precedence over GCS and franken metadata. A term may be inherited from another dataset; source is not encoded in the term. |
| `cell_type_source`, `cell_type_source_text` | Source marker/text; string | `wilson_lab` appears in both for 34/35 rows. Public documentation does not define a row-level method, curator, date, or evidence for this marker. One row has blank/null values. |
| `super_class`, `cell_class`, `cell_sub_class` | Hierarchical classifications; string | `motor` and `proboscis_motor_neuron` select the frozen inventory. The merged table can combine sources by column. |
| `side` | Laterality; string | Both MN9-labeled rows have left/right values. The paper-feather documentation says its side is computed from soma anchor; the live snapshot loader also coalesces SeaTable side before GCS side. Which route supplied each frozen row is unrecorded. |
| `nerve` | Entry/exit nerve; string | Left/right pharyngeal-or-accessory-pharyngeal values appear; origin and disjunction are unresolved. |
| `flow`, `cell_function`, `cell_function_detailed` | Flow and functional classification; string | Both rows record motor-related terms. These are annotations, not functional proof. |
| `peripheral_target_type` | Annotated peripheral target; string | Both rows record `proboscis_m9_muscle`; no morphology was examined here. |
| `fafb_cell_type`, `fafb_alignment_cell_type`, `manc_cell_type`, `malecns_cell_type`, `hemibrain_cell_type`, `fanc_cell_type` | Separate cross-dataset label columns; string | Their presence cannot establish how `cell_type=MN9` was assigned. Match confidence/IDs were not resolved as a `wilson_lab` crosswalk. |

The [snapshot README](https://github.com/htem/BANC-project/blob/e31a2e26b9937dca72e5ca1c1960df6454d76114/data/meta/README.md) states that `R/startup/banc-meta-live.R` merges live SeaTable manual curation, GCS segmentation properties, and frankenbrain matches, with SeaTable > GCS > franken priority for manual-curation columns and GCS priority for `proofread`, then writes the dated parquet. That establishes the **merge path**, not the original `wilson_lab` assignment. The producer's curation scripts show that metadata may be updated from cell-info rows, cell-type joins, and matching; no examined source ties either MN9 root to one of those operations. Thus the traceable chain is: **unlocated original annotation → unresolved SeaTable/GCS/franken ingress → documented coalescing in `banc-meta-live.R` → `banc_888_meta_20260521.parquet`**. The archive paper feather follows a related producer path but cannot substitute for this row-level chain.

## Assignment method, dataset, and crosswalk

`wilson_lab` is a **source attribution string**, plausibly naming the Wilson laboratory; it is not a documented assignment protocol. Original assignment method: **P_UNKNOWN**. Native manual, transferred manual, morphology matched, algorithmic, and hybrid routes remain possible. The general BANC paper and pipeline discuss curation and cross-dataset matching, but do not identify which route produced these specific labels. Source connectome/dataset and release: **unresolved**. Source neuron IDs, mapping mechanism, one-to-one status, independent bilateral side assignment, confidence/ambiguity, and whether a mapping predates v888: **unresolved**. The frozen snapshot date establishes latest presence, not the first annotation date. No transfer is asserted or rejected.

## MN9-labeled rows and complete inventory context

| BANC v888 root | Exact `cell_type` | Marker | Other recorded annotations | Earliest traceable row and chain |
|---|---|---|---|---|
| `720575941410682479` | `MN9` | `cell_type_source=wilson_lab`; `cell_type_source_text=wilson_lab` | `side=left`; left pharyngeal or accessory pharyngeal nerve; `peripheral_target_type=proboscis_m9_muscle` | Examined 2026-05-21 parquet; original assignment, author, note, confidence, source ID, and side derivation unresolved. Same incomplete merge chain above. |
| `720575941623285450` | `MN9` | `cell_type_source=wilson_lab`; `cell_type_source_text=wilson_lab` | `side=right`; right pharyngeal or accessory pharyngeal nerve; `peripheral_target_type=proboscis_m9_muscle` | Examined 2026-05-21 parquet; original assignment, author, note, confidence, source ID, and side derivation unresolved. Same incomplete merge chain above. |

The two rows have the same **observed marker and pipeline**, but their original assignment mechanisms cannot be shown to be identical. Side provenance is not shown to be coupled to the MN9 annotation. Across all **35** frozen `cell_class=proboscis_motor_neuron` rows, `cell_type_source` is `wilson_lab` for **34** and blank for **1**; `cell_type_source_text` is `wilson_lab` for 34 and null for 1. This is a mixed **recorded-source state**, not proof of two original assignment methods. The same uncertainty applies to the 34 marked candidates; none is ranked or excluded.

## Independence, sufficiency, and next action

**I5 — INDEPENDENCE_UNRESOLVED.** The label's original evidence and any crosswalk to external IDs are unavailable, so its independence from a future reference identity cannot be assessed. If future work establishes transferred labeling, that alone would **not** prevent independent corroboration from newly examined BANC morphology; no such corroboration is claimed here. Answer to whether transferred labeling prevents independent morphology corroboration: **NO, conditional on transfer being established and morphology independently assessed**.

**P3 — PROVENANCE_UNRESOLVED; P sufficient = NO.** The critical original assignment origin/method and row-level ingress cannot be established. This is more than a noncritical version gap. The exact missing link is the versioned source annotation record or audit trail behind the `wilson_lab` cell types, including the two root IDs and evidence/method notes.

**Exactly one recommended next action:** obtain and pin the authoritative Wilson-lab/BANC SeaTable or CAVE annotation export plus revision/audit history for these `wilson_lab` rows, then trace the two MN9 labels' originating records and assignment method. Do not begin laterality research.

## Firewall and scientific nonclaims

Connectivity-blind audit: BANC connectivity queries **0**; partner-edge queries **0**; synapse-count calculations **0**; MaleCNS endpoint calculations **0**; Task 018 numerical results and external-validation outcomes **not inspected**. Connectivity/outcome contamination: **No**. Candidate identity decisions **0**; candidate ranking **0**; morphology interpretations **0**; morphology comparisons **0**; SWC parsing **0**; coordinate analysis **0**. Task 017Q remains **KEEP_DEFERRED**.

This audit establishes no BANC MN9 identity, bilateral identity correctness, anatomical or functional equivalence, synaptic conservation, connectivity or Task 018 replication, biological asymmetry, or causal mechanism. Both labeled roots remain candidates only; the frozen 35-candidate inventory and Task 025 STOP/NOT_IDENTIFIABLE state remain intact.
