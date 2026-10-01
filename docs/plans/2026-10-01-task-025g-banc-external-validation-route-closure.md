# Task 025G — BANC confirmatory external-validation route closure

Date: 2026-10-01. Verdict: **COMPLETE**. Classification: **BANC_CONFIRMATORY_ROUTE_CLOSED**. Reason and exact route disposition: **IDENTITY_NOT_PROSPECTIVELY_RESOLVABLE**.

## Authority and scope

The starting local HEAD, `origin/master`, and live GitHub master were `04270914d78aebc0fa578a20ec56d1226872c0b4`; worktree and stash were empty. Package version was `0.3.0`, and `v0.3.0` peeled to `a1a6651163840a982799b1fa82c1904e67f84660`. [Task 025F](2026-10-01-task-025f-discovery-only-label-morphology-confirmation-gate.md) was **COMPLETE**, with decision **F6 — MULTIPLE_METHOD_BLOCKERS**. It froze required but unobservable direct muscle 9 innervation, insufficient uniqueness of the remaining CNS pattern, zero confirmatory weight for existing labels, unresolved P3 provenance, the need for a fresh adjudicator for any future label-blind route, and exactly one next action: this closure. This record disposes of the current route only; it does not revise Task 025F or any prior scientific result.

Under the prospectively frozen identity standard and currently pinned BANC v888 CNS morphology, MN9 identity cannot be established with sufficient label-independent evidence for confirmatory external validation. This does not find the BANC MN9 labels wrong, reject either candidate as MN9, find the BANC morphology incorrect, rule out future identification of MN9 in BANC, or limit BANC's use for other questions.

## Preserved negative-evidence chain

| Task | Preserved disposition |
| --- | --- |
| 023 | BANC was the preferred candidate dataset, but bilateral MN9 mapping was not ready. MANC and FANC were `DATASET_INELIGIBLE`; the FAFB/FlyWire lead was `NOT_IDENTIFIABLE` and was not selected for execution. |
| 024 | **STOP / R6**: blindness was compromised before candidate screening. |
| 024A | Contamination disposition and clean-room handoff. |
| 025 | Independent adjudication: **NOT_IDENTIFIABLE**. |
| 025A | **E6 — multiple evidence gaps**. |
| 025B | Current GCS morphology objects available for **35/35** frozen candidates; archive pinning incomplete. |
| 025C | Immutable Dataverse 3.0 archive covers all **35/35**; **D2**; **M1** applies when the Dataverse archive is used directly. |
| 025D | **P3 — annotation provenance unresolved**. |
| 025E | **S4 — SeaTable source identified but historical records inaccessible**; P3 remains; provenance search intentionally terminated. |
| 025F | **F6 — multiple method blockers**; label-independent confirmation protocol not feasible with authorized evidence. |

These historical classifications remain unchanged.

## What failed

**Data availability:** This is not the primary final blocker. All 35 frozen candidates have morphology members in the immutable Dataverse 3.0 skeleton archive.

**Annotation provenance:** P3 remains unresolved. `wilson_lab` is source attribution only. Existing `cell_type=MN9` labels and their source markers are discovery-only and carry **ZERO confirmatory weight**.

**Identity criteria:** This is the primary final blocker. The prospective acceptance rule required **R1 direct muscle 9 innervation, R2 pharyngeal nerve exit, R3 dorsal SEZ soma, R4 ventral SEZ arbor, and S1 predominantly ipsilateral arbor**, all to MATCH. R1 cannot be observed in the pinned CNS morphology. The remaining observable CNS pattern is insufficiently unique. No candidate can satisfy the frozen confirmatory rule using the authorized evidence. No replacement criterion or relaxed threshold is adopted.

**Blinding:** Any future label-blind route would require a fresh adjudicator because the prior adjudicator was exposed to labels and root IDs. This is secondary to the insufficient evidence route.

## What was not tested

Task 025F inspected no candidate morphology. Task 025G likewise opens, parses, and renders no candidate morphology and scores no candidate. No candidate was accepted or rejected as MN9; no biological LEFT/RIGHT BANC identity or bilateral pair was frozen. No BANC connectivity was queried, no BANC Task 018 endpoint was calculated, and no cross-dataset anatomical-asymmetry comparison occurred. Thus there is **no external-validation result for the Task 018 endpoint**. The endpoint was never validly reached; this closure is neither a replication failure nor a failure to reproduce Task 018.

Roots `720575941410682479` and `720575941623285450` remain **DISCOVERY-ONLY MN9-LABELED CANDIDATES**. Neither is confirmed MN9, rejected MN9, or a validated member of a bilateral pair. Historical metadata descriptions do not freeze biological LEFT/RIGHT identity.

## Reopening and research status

Reopening this route requires materially **new independent evidence**, followed by a **new prospective protocol before examining the new candidate evidence**. Possible triggers are authoritative recovery of the original Wilson-lab annotation provenance sufficient for an independent identity chain; a release-pinned BANC-compatible dataset with muscle/target evidence sufficient to observe R1; independently validated anatomy supporting another prospectively defensible MN9-specific criterion; or an authoritative identity crosswalk with independently documented confirmatory provenance. Current MN9 labels, morphology that merely “looks right,” a relaxed threshold, or a convincing post-hoc candidate comparison are not reopening triggers.

The BANC confirmatory route is **CLOSED — IDENTITY_NOT_PROSPECTIVELY_RESOLVABLE**. MANC and FANC remain **DATASET_INELIGIBLE** under Task 023. The FAFB/FlyWire lead remains **NOT_IDENTIFIABLE** under Task 023 and was not selected for execution. No dataset is reassessed or selected here.

Task 018A remains the confirmatory anatomical decomposition in the frozen MaleCNS graph. Its full-graph primary classification `SHARED_PARTNER_DIFFERENCE_LARGEST` and threshold-5 sensitivity classification `LEFT_ONLY_INPUT_LARGEST` are unchanged. Task 025G neither strengthens nor weakens its numerical result; independent external-dataset validation remains absent. Task 017 remains **NOT_ROBUST**, and Task 017Q remains **KEEP_DEFERRED** without execution.

For v0.4, the specific BANC route investigated by Tasks 023–025F is closed. No replacement confirmatory dataset or new scientific hypothesis is authorized. Network motifs, another connectome, candidate-specific morphology, and Task 018 sensitivity observations are not promoted into a confirmatory question. A future direction requires a separate result-blind roadmap gate.

**Exactly one recommended next action:** v0.4 Post-BANC Research Roadmap Decision Gate. That gate may decide whether an independently motivated research direction is sufficiently defined to continue; it is not performed here. There is no ranking, replacement dataset, or new preregistration.

## Scientific accounting

| Activity | Count |
| --- | ---: |
| Candidate morphology files opened / parsed / rendered | 0 / 0 / 0 |
| Candidate morphology scores / identity decisions / rankings | 0 / 0 / 0 |
| Laterality adjudications | 0 |
| BANC connectivity queries / partner-edge queries / synapse-count calculations | 0 / 0 / 0 |
| BANC Task 018 endpoint calculations / MaleCNS endpoint recalculations | 0 / 0 |
| Scientific executions | 0 |

No Task 017 or Task 018 rerun and no Task 017Q execution occurred. No source, test, or scientific artifact changes; no tag, release, or version mutation.
