# Independent BANC v888 MN9 identity adjudication: clean-room handoff

Date: 2026-09-30. This protocol contains only identity rules frozen in Task 023 before candidate screening. Its sole purpose is to decide whether adult proboscis MN9 can be identified bilaterally in BANC CAVE materialization **v888**. Do not calculate or inspect a connectivity or comparison endpoint.

## Sources and information boundary

Use release-pinned BANC v888 native annotation and morphology, the BANC paper and project documentation, and preexisting anatomical literature: FlyBase adult proboscis MN9 term **FBbt:00111298** (including its cited primary morphology sources). The BANC static deposit is DOI `10.7910/DVN/7WTH1N`; versioned metadata is described at `compiled_data/banc_888/banc_888_meta.feather`, and v888 morphology as SWC skeletons and neuron OBJ meshes. These are source locations, not verified file-level pins. Record exact files, versions, retrieval dates, schemas and hashes used. Verify whether each annotation is native, curated, imported or a cross-dataset match; a column name alone does not establish independence.

Do not receive or inspect Task 018 results or decomposition, Task 024 exposure details, partner identities or edges, synapse tables or counts, connectivity rankings, response values, connectivity-derived candidate hints, or any expected external comparison outcome. Do not use BANC connectivity to discover or classify candidates. If any such information is encountered, stop and document the exposure without incorporating it into the identity decision.

## Frozen anatomical identity criteria

Adult proboscis muscle-9 motor neuron has a muscle-9 target associated with rostrum extension, a dorsal subesophageal soma, a broad mostly ipsilateral ventral subesophageal arbor, and pharyngeal-nerve exit. Muscle-9 target or pharyngeal-nerve exit, together with the soma and arbor evidence, are required for the convergent rule below. A muscle target may be unavailable within a CNS reconstruction. The names MN9, CB0701 and E49 are supporting discovery terms, not independent proof. Motor function and laterality alone are nonspecific. Do not conflate an adult proboscis MN9 with a larval body-wall muscle-9 neuron.

## Candidate enumeration and evidence assessment

Enumerate **all plausible proboscis motor candidates** from permitted v888 annotations and anatomy before assigning a mapping category. Report every plausible candidate, including rejected and unresolved ones, with its release-pinned root ID in the adjudicator's returned report. Do not preselect a pair by connectivity or by agreement with another dataset's endpoint.

For each candidate, trace the annotation's original source, curator or transfer route, release and evidence. Examine permitted v888 soma, arbor and nerve-exit morphology, including reconstruction gaps or uncertain trajectories. Compare each criterion against all plausible candidates and record a criterion-by-criterion evidence matrix, source citations, contradictions and missing observations. A transferred label alone needs provenance review and independent corroboration from BANC morphology. A registered or mirrored template may help morphology matching only with the transform and handedness recorded.

## Laterality

Use dataset-native biological `side`/`somaSide` annotation first, verified against the release's documented midline and a rendered soma or nerve exit. Resolve coordinates in BANC native space before registration. Do not infer biological side solely from a reflected display. If the native label and anatomical side conflict, classify as **AMBIGUOUS** until source documentation resolves it. Never swap left and right to improve agreement with an external result.

## Frozen mapping categories and thresholds

- **ACCEPTED_EXPLICIT:** a release-pinned authoritative native annotation names adult MN9/CB0701 on exactly one complete candidate per biological side, with dataset-native side evidence and no contradictory morphology. A transferred label alone requires source/provenance review.
- **ACCEPTED_CONVERGENT:** absent explicit labels, two independent anatomical evidence streams must converge uniquely for *each* side: (1) documented pharyngeal-nerve exit or muscle-9 target and (2) subesophageal soma plus characteristic ventral arbor, compared against all plausible proboscis motor candidates; a published morphology match or independent experimental atlas must corroborate at least one stream. A matching name, connectivity similarity, or a single bilateral-looking pair is insufficient.
- **AMBIGUOUS:** multiple viable candidates or conflicting sources.
- **NOT_IDENTIFIABLE:** target anatomy is potentially covered but available evidence cannot establish the pair.
- **DATASET_INELIGIBLE:** coverage or data structure excludes the target or required identity assessment.

Do not relax these thresholds. A missing side, unresolved side conflict, incomplete candidate comparison or uncertain annotation provenance cannot be silently promoted to acceptance. Report why evidence is unavailable rather than substituting a connectivity clue.

## Root-ID freeze and version semantics

Only after applying the frozen criteria, report the selected left and right v888 CAVE chunked-graph root IDs, or explicitly report that no defensible bilateral pair can be frozen. Verify each root against materialization v888 and document any root changes, splits, merges or mapping ambiguity across versions. Pin the annotation and morphology release, source file or endpoint identifiers, access date, checksums where available, and coordinate/side conventions. Do not silently mix roots, annotations or morphology from different materializations.

## Required returned report

Include adjudicator identity and independence declaration; dataset/materialization and exact source versions; complete plausible-candidate inventory; annotation provenance for each; criterion-by-criterion anatomical matrix and citations; reconstruction limitations; independently resolved side evidence; classification and rationale per side and for the bilateral pair; frozen root IDs only if accepted; version semantics and source hashes; ambiguities and stop conditions. State explicitly that no connectivity, partner-edge, synapse-count, comparison endpoint or Task 018 result was accessed. Return the identity decision before seeing any future comparison endpoint.

## Independence and stop conditions

The adjudicator must not have participated in Task 018 endpoint interpretation in a way that exposed the relevant outcome, unless otherwise demonstrably blinded to it; must not have seen the prior researcher's contaminated excerpt; and may be told only that connectivity information was exposed to the prior researcher. Use this protocol alone for the identity decision. Stop on outcome/connectivity exposure, inability to establish independence, unresolvable version or side semantics, or inability to compare all plausible candidates under the frozen criteria. Report a mapping failure or ambiguity rather than filling gaps by inference. If no genuinely independent adjudicator is available, the confirmatory external-validation route must be reconsidered.
