# Task 025 — Independent BANC v888 MN9 identity adjudication

Date: 2026-09-30. Verdict: **STOP**. Identity disposition: **NOT_IDENTIFIABLE** from the bounded evidence accessed here. This is a mapping failure, not a frozen bilateral identity.

## Independence, protocol, and start gate

I performed this review independently and did not read Task 018 results, Task 023 full research record, Task 024 history, Task 024A contamination disposition, release result details, or prior MN9 comparison outcome summaries. The sole scientific identity protocol read was `docs/plans/2026-09-30-task-024a-banc-mn9-clean-room-identity-handoff.md` at starting HEAD `7a9c7aee554bbe694e77d09ef6b73b9d8708f5e5`. Local HEAD, `origin/master`, and live `master` matched that commit; worktree and stash were empty.

## Resources accessed and blindness audit

- The named clean-room handoff.
- BANC project GitHub `data/meta/README.md` and `data/meta/banc_888_meta_20260521.parquet` at repository main commit `e31a2e26b9937dca72e5ca1c1960df6454d76114`. Parquet SHA-256: `4dde2e6503e59a79e1e8f46e32687de09e8b595e5bd48f7353829fb713c9761a`. Accessed 2026-09-30. Only selected identity, side, nerve, source, and position columns were read. The file is a bundled metadata snapshot, assembled with SeaTable manual curation priority over GCS and cross-dataset fields according to its README; this does not establish the original evidence for any individual MN9 label.
- Targeted web search for BANC v888 metadata and morphology locations; search snippets described general dataset products, including aggregate dataset size, but exposed no candidate-specific connectivity, partners, counts, ranking, or comparison outcome. A proposed v888 SWC URL for one candidate returned HTTP 404 and no morphology.

No withheld comparison outcome was encountered. No forbidden prior-result material was accessed. BANC connectivity queries: **0**. Partner-edge queries: **0**. Synapse-count calculations: **0**. MaleCNS endpoint calculations: **0**. No connectivity information relevant to a candidate was encountered.

## Candidate inventory and annotation evidence

The selected v888 snapshot contains 35 rows with `cell_class=proboscis_motor_neuron`. All 35 are retained as plausible screening candidates until anatomical comparison. Every row has `cell_type_source=wilson_lab` except the left MN5 row, for which that field is empty. The labels, target terms, and nerve terms below are metadata annotations, not observed anatomy. `L-ML`/`R-ML` mean the corresponding maxillary-labial nerve; `L-P/A`/`R-P/A` mean the corresponding pharyngeal nerve **or** accessory pharyngeal nerve, an unresolved disjunction.

| v888 root ID | Native side label | Cell type | Peripheral target label | Nerve label |
| --- | --- | --- | --- | --- |
| 720575941449780405 | left | MN1 | proboscis_m1_muscle | L-ML |
| 720575941536822514 | left | MN1 | proboscis_m1_muscle | L-ML |
| 720575941484914498 | left | MN2Da | proboscis_m2da_muscle | L-ML |
| 720575941662402360 | left | MN2Db | proboscis_m2db_muscle | L-ML |
| 720575941603110134 | left | MN2V | proboscis_m2v_muscle | L-ML |
| 720575941626721900 | left | MN3L | proboscis_m3l_muscle | L-P/A |
| 720575941604209142 | left | MN3M | proboscis_m3m_muscle | L-P/A |
| 720575941513444089 | left | MN4a | proboscis_m4a_muscle | L-ML |
| 720575941656201177 | left | MN4a | proboscis_m4a_muscle | L-ML |
| 720575941628933433 | left | MN4b | proboscis_m4b_muscle | L-ML |
| 720575941480581856 | left | MN5 | proboscis_m5_muscle | L-P/A |
| 720575941430258647 | left | MN6 | proboscis_m6_muscle | L-ML |
| 720575941589105292 | left | MN7 | proboscis_m7_muscle | L-ML |
| 720575941627279515 | left | MN7 | proboscis_m7_muscle | L-ML |
| 720575941553702042 | left | MN8 | proboscis_m8_muscle | L-ML |
| 720575941410682479 | left | MN9 | proboscis_m9_muscle | L-P/A |
| 720575941623743434 | left | MNx04 | proboscis_muscle | L-P/A |
| 720575941588099140 | right | MN1 | proboscis_m1_muscle | R-ML |
| 720575941588254206 | right | MN1 | proboscis_m1_muscle | R-ML |
| 720575941511829520 | right | MN2Da | proboscis_m2da_muscle | R-ML |
| 720575941462808077 | right | MN2Db | proboscis_m2db_muscle | R-ML |
| 720575941545764232 | right | MN2V | proboscis_m2v_muscle | R-ML |
| 720575941454079539 | right | MN3L | proboscis_m3l_muscle | R-P/A |
| 720575941519595447 | right | MN3L | proboscis_m3l_muscle | R-P/A |
| 720575941652113685 | right | MN3M | proboscis_m3m_muscle | R-P/A |
| 720575941402863216 | right | MN4a | proboscis_m4a_muscle | R-ML |
| 720575941494208128 | right | MN4a | proboscis_m4a_muscle | R-ML |
| 720575941454240169 | right | MN4b | proboscis_m4b_muscle | R-ML |
| 720575941687084527 | right | MN5 | proboscis_m5_muscle | R-P/A |
| 720575941454380013 | right | MN6 | proboscis_m6_muscle | R-ML |
| 720575941558268943 | right | MN7 | proboscis_m7_muscle | R-ML |
| 720575941599758121 | right | MN7 | proboscis_m7_muscle | R-ML |
| 720575941547120161 | right | MN8 | proboscis_m8_muscle | R-ML |
| 720575941623285450 | right | MN9 | proboscis_m9_muscle | R-P/A |
| 720575941603103990 | right | MNx04 | proboscis_muscle | R-P/A |

## Provenance, anatomy, and laterality

The two MN9 rows are `720575941410682479` (left label) and `720575941623285450` (right label). Both have a `proboscis_m9_muscle` target label and a pharyngeal-or-accessory nerve label. The snapshot attributes their cell types to `wilson_lab`, but the exact original annotation, curator route, evidence, and whether the terms were native, transferred, or cross-dataset matched were not established. The bundled snapshot's column priority is insufficient provenance. The unresolved `MNx04` rows and other proboscis motor rows cannot be excluded by label alone.

Criterion-by-criterion assessment for **every inventory row**: muscle-9 target is asserted only for the two MN9 rows and other muscle targets are asserted for named alternatives; no peripheral muscle target was independently observed. Pharyngeal **or accessory** nerve is annotated for MN3L, MN3M, MN5, MN9, and MNx04 on both sides; specific pharyngeal exit was not resolved. Dorsal subesophageal soma, broad mostly ipsilateral ventral subesophageal arbor, and reconstruction continuity were not examined from a verified v888 skeleton or mesh for any row. Thus morphology cannot confirm the two labels or exclude alternatives. No morphology source file, version, coordinate transform, or hash can be pinned.

The metadata has `side` labels for all 35 rows. No documented BANC native midline or rendered soma/nerve exit was obtained to independently verify biological left and right. Native coordinate handedness and any display reflection remain unresolved. The two MN9 side labels are evidence of annotation only, not independently resolved laterality.

## Frozen mapping-contract application

`ACCEPTED_EXPLICIT` fails because annotation authority and independent side/morphology checks are unresolved. `ACCEPTED_CONVERGENT` fails because the two required independent anatomical streams and corroborating atlas or published morphology match were not established. The available evidence does not demonstrate conflicting assignments or two anatomically viable MN9 pairs, so `AMBIGUOUS` is not asserted. Coverage appears possible and the snapshot has proboscis motor rows, so `DATASET_INELIGIBLE` is not established. The bounded identity disposition is **NOT_IDENTIFIABLE**. The handoff explicitly requires stopping when all plausible candidates cannot be compared under the frozen criteria. No bilateral root IDs are frozen.

This disposition is limited to the resources accessed. The `banc_888_id` values are snapshot v888 identifiers, not independently verified live CAVE roots. Split, merge, and cross-version root semantics were not checked. Annotation snapshot date is 2026-05-21; morphology source/version is unresolved. No v888 SWC or OBJ was inspected.

## Recommended next action

Arrange one fresh blinded identity adjudication with access to verified v888 morphology, original annotation provenance, and native side documentation for the complete candidate inventory before any connectivity or external-validation analysis.
