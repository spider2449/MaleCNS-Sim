# Task 025E — Wilson-lab/BANC annotation source and revision recovery

Date: 2026-09-30. Verdict: **COMPLETE** (bounded negative provenance recovery). Source state: **S4 — SOURCE_IDENTIFIED_BUT_INACCESSIBLE**. Provenance: **P3 — PROVENANCE_UNRESOLVED**. Independence: **I5 — INDEPENDENCE_UNRESOLVED**. P sufficient: **NO**.

## Starting checkpoint

The repository root was obtained with `git rev-parse --show-toplevel`. Local HEAD, `origin/master`, and live GitHub master were `b1a3d0289602ff74c1d34a00553927b3554c6c92`. Worktree and stash were empty. Package version was `0.3.0`; peeled `v0.3.0` was `a1a6651163840a982799b1fa82c1904e67f84660`. [Task 025D](2026-09-30-task-025d-banc-v888-wilson-lab-annotation-provenance.md) reported P3, P sufficient NO, and exactly one action: recover the authoritative Wilson-lab/BANC export and revisions, then trace the two MN9 labels.

## Reconstructed provenance DAG

```
UNKNOWN original Wilson-lab assignment records/method/revisions
    -> UNKNOWN route into BANC SeaTable `banc_meta` and/or GCS metadata
    -> SeaTable `banc_meta` (base `banc_meta`, table `banc_meta`)
       and GCS segmentation-properties metadata
    -> BANC-project `R/startup/banc-meta-live.R` coalescing
    -> `data/meta/banc_888_meta_20260521.parquet`
```

The pinned [snapshot loader](https://github.com/htem/BANC-project/blob/e31a2e26b9937dca72e5ca1c1960df6454d76114/R/startup/banc-meta-live.R) calls `banctable_query()`, reads GCS metadata, joins by `supervoxel_id`, prioritizes SeaTable `cell_type` where present, and writes dated parquet. Its offline fallback is `data/meta/bc_orig_cache.feather`; the code does not establish that this cache supplied the frozen snapshot. Nor does it select the `cell_type_source` marker's per-row ingress. The public [bancr table documentation](https://natverse.org/bancr/reference/banctable_query.html) identifies SeaTable URL `https://cloud.seatable.io/`, workspace `57832`, base/table `banc_meta`/`banc_meta`, default SQL `SELECT * FROM banc_meta`, and credential variable `BANCTABLE_TOKEN`. Table ID, a dated SeaTable export filename, and export revision/checksum are **UNKNOWN**.

## Bounded authoritative search and Git history

Examined the pinned [BANC-project](https://github.com/htem/BANC-project/tree/e31a2e26b9937dca72e5ca1c1960df6454d76114) snapshot/README/loader, the pinned [bancpipeline](https://github.com/htem/bancpipeline/tree/5c333c12f0b9e03873f88cf4e23cad34c0bb49c1) curation scripts and annotations documentation, public [bancr](https://natverse.org/bancr/reference/banctable_query.html) access documentation, repository branches/tags and histories, and the Task 025D cited [Dataverse documentation](https://github.com/htem/BANC-project/blob/e31a2e26b9937dca72e5ca1c1960df6454d76114/manuscript/print/dataverse/documentation/banc_888_meta.md). The Dataverse paper feather is a related output, not a versioned original annotation table. Public project/pipeline documentation and bounded searches of maintainer GitHub material and paper/supplement locations yielded no row-level original export or revision log. No unrelated analysis was used.

History-aware checks included `git log --all -S'wilson_lab'`, path history for `data/meta/bc_orig_cache.feather` and candidate annotation files, `git ls-tree -r`, and `git show` of relevant committed scripts. The producer's `wilson_lab` curation references enter its public history in commit `58e349be3fcb126c49e967a0120ca3a9e6640645`; this pins **code only**, not source records. A tracked `annotations/cell_info_annotations.xlsx` has blob `96904d0a1a2e0a2e4abc72f038b9129d9070a2b2`; its name and history identify a cell-info artifact, not the authoritative `wilson_lab`/SeaTable export. It was not treated as the sought source. No public historical file was established as a deleted or renamed export of the 34 rows. The specific upstream `wilson_lab` original may be external, but the route is undocumented; this audit does not assert it was never tracked anywhere.

SeaTable is a documented external component. Public documentation says the draft SeaTable source is restricted to the BANC production team and requires `BANCTABLE_TOKEN`; no access control was bypassed. The public dated parquet is recoverable, but an exact 2026-05-21 SeaTable table state and row revision history were **not** recovered. Revision availability, archival policy, and anonymous historical access for this base are undocumented in the examined sources. **S4** applies to the identified SeaTable source; it does not claim historical source loss (**S6**).

## Two-row record and method trace

| Candidate root | Originating record | Earliest observed MN9 | Author/source | Revisions and event relation | Traceability |
|---|---|---|---|---|---|
| `720575941410682479` (LEFT as recorded in merged row) | Not recovered; merged row only | Dated 2026-05-21 parquet; assignment date unknown | Merged marker `wilson_lab`; assigning curator unknown | Previous label, timestamp, reason, subsequent edits, independent side changes, and coordinated event unknown | **T3 — MERGED_ROW_ONLY** |
| `720575941623285450` (RIGHT as recorded in merged row) | Not recovered; merged row only | Dated 2026-05-21 parquet; assignment date unknown | Merged marker `wilson_lab`; assigning curator unknown | Previous label, timestamp, reason, subsequent edits, independent side changes, and coordinated event unknown | **T3 — MERGED_ROW_ONLY** |

Both merged rows contain `cell_type=MN9` and `cell_type_source=wilson_lab`. No original source neuron/dataset IDs, mapping method, confidence, ambiguity note, assignment comment, author, or revision ID were recovered. Source dataset/version if transferred: **UNKNOWN**. Explicit source neuron IDs: **none recovered**. Overall and per-row assignment method: **A6 — METHOD_UNRESOLVED**. The marker is attribution, not a documented method. No conclusion that the rows were assigned together is supported.

## Broader source coverage and decision

The frozen inventory contains 34 `wilson_lab` markers among 35 candidates. No authoritative upstream row export was recovered for comparison. Upstream coverage among the 34: **matched 0 / missing 0 / conflicting 0 / unresolved 34**. “Missing” would require a recovered source table demonstrably omitting a row; that evidence is absent. The 35th merged row has a blank source marker and is outside this coverage count.

**P3** remains because the original records, method, revision sequence, and row-level ingress remain unresolved. **I5** remains because independence from a reference identity cannot be assessed. The public snapshot proves candidate labels were present by its date; it does not independently confirm identity. Critical gaps are the historical SeaTable/export row state, original assignment records, method/evidence, revisions, source IDs if transferred, and marker propagation into the GCS/SeaTable merge. The bounded search terminates after the named public repository histories, releases/branches, project data and Dataverse documentation, public client documentation, and directly relevant maintainer/paper sources; further recovery requires authorized historical table access or a curator-supplied export.

**Exactly one recommended next action:** decision gate to assess whether independent morphology corroboration can proceed under a prospectively frozen rule that treats the MN9 labels as discovery-only, non-confirmatory candidate hints. Do not adopt that rule or start the audit here.

## Firewall and nonclaims

Candidate identity decisions **0**; candidate ranking **0**; morphology interpretation/comparison **0**; SWC parsing **0**; coordinate analysis **0**; laterality adjudication **0**. BANC connectivity queries **0**; partner-edge queries **0**; synapse-count calculations **0**; MaleCNS endpoint calculations **0**. Task 018 outcome details were not inspected. Connectivity/outcome contamination: **No**. Task 017Q: **KEEP_DEFERRED**.

No biological identity, side correctness, transfer, independent corroboration, equivalence, or functional claim is made. Both MN9-labeled roots remain candidates only. Package stays `0.3.0`; no source, test, or scientific artifact change is part of this task.
