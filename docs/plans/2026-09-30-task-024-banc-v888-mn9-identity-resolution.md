# Task 024 — BANC v888 bilateral MN9 identity resolution

Date: 2026-09-30. Verdict: **STOP**. Readiness: **R6 — BLINDNESS_COMPROMISED**. Identity research stopped before candidate screening or morphology inspection.

## Starting checkpoint and Task 023 authority

Repository root was obtained with `git rev-parse --show-toplevel`. Local HEAD, `origin/master`, and live remote `master` were `652af9314d396f9d5e77ee7eb114bf3608442442`; worktree and stash were empty. Package version was 0.3.0. Published `v0.3.0^{}` peeled to `a1a6651163840a982799b1fa82c1904e67f84660`.

Task 023 records **P2 — MAPPING_NOT_READY**, selection **B — IDENTITY_MAPPING_RESEARCH_REQUIRED**, and recommends release-pinned BANC v888 MN9 identity research using annotations, provenance, and morphology without partner edges or counts. Its `ACCEPTED_CONVERGENT` rule requires, for each side, (1) documented pharyngeal-nerve exit or muscle-9 target and (2) subesophageal soma plus characteristic ventral arbor, comparison against all plausible proboscis motor candidates, and published morphology or independent experimental-atlas corroboration of at least one stream. The rule is precise enough to apply; no `IDENTITY_CONTRACT_UNDERSPECIFIED` stop occurred. Frozen MaleCNS IDs `10331` and `16949` were context only.

## Pinned sources and independent criteria established before the stop

The target is BANC CAVE materialization **v888**, paper snapshot dated 2026-04-17, with paper synapse release **v2** referenced solely for release identification. The BANC project identifies its static Dataverse deposit as DOI `10.7910/DVN/7WTH1N`, its versioned metadata as `compiled_data/banc_888/banc_888_meta.feather`, and morphology as v888 SWC skeletons (`banc_banc_space_swc/{root_id}.swc`) and neuron OBJ meshes. Root IDs are CAVE chunked-graph roots at materialization 888. These are resource descriptions from project documentation, not a completed file-level pin or inspection. The metadata combines CAVE and SeaTable curation with cross-dataset matches; its labels cannot be assumed native or independent by column name alone. Coordinate orientation and laterality conventions were not established before the stop.

FlyBase term `FBbt:00111298` (FB2026_03) identifies adult proboscis muscle-9 motor neuron, also `CB0701` and `E49`. It describes muscle-9/rostrum extension, dorsal subesophageal soma, broad mostly ipsilateral ventral subesophageal arbor, and pharyngeal-nerve exit. For the frozen Task 023 contract, nerve exit or muscle target and soma-plus-arbor are **REQUIRED**; the name/aliases are **SUPPORTING** discovery terms; motor function and laterality alone are **NONSPECIFIC**. Direct muscle target may be **UNAVAILABLE_IN_BANC** if outside the CNS reconstruction. No candidate was tested against these criteria.

## Connectivity-blindness incident and stop

During a public web search for BANC v888 MN9 metadata, the search tool returned an unsolicited result for a third-party `Pronexsteam/brainlab` repository. Its search excerpt stated MN9 response rates for FAFB v783, BANC v888, and MaleCNS v0.9 (`76.7`, `17.8`, and `68.9` Hz respectively), and asserted that BANC has approximately `0.35×` the synapses on the identified cells. A second search returned the same repository and repeated those claims. These are third-party claims, **not verified Task 024 findings**, but they exposed candidate-specific connectivity-related and model-output information. The public BANC pipeline search excerpt also described general dataset-wide synapse products and connectivity-based typing, without exposing candidate partner identities or edges. No partner identities, edge list, BANC synapse table, candidate synapse counts, or Task 018 components were accessed.

The exposure violates Task 024's prospective blindness condition regardless of whether the third-party claims are correct. **CONNECTIVITY_BLIND = NO**. Scientific progression stopped immediately after recognizing the exposure. BANC connectivity queries: **0**. Partner-edge queries: **0**. Synapse-count calculations: **0**. MaleCNS endpoint calculations: **0**. Task 017 and Task 018 reruns: **No**. Task 017Q: **KEEP_DEFERRED**; not executed.

## Unfinished identity gates and decision

Candidate inventory: **0 screened; unknown total plausible candidates**. No candidate root IDs or labels were collected. Annotation provenance classification, morphology criterion matrix, left/right laterality, root verification, root-version semantics, and identity independence classification are **not determined**. No BANC root IDs are frozen. The mapping category is **unassigned because screening stopped**; assigning `NOT_IDENTIFIABLE` would incorrectly imply a completed identity assessment. The Task 023 mapping contract was **not applied to candidates**. Readiness is exactly **R6 — BLINDNESS_COMPROMISED**. Remaining blockers include identity and side evidence, root-version semantics, bilateral completeness/missingness, and comparison-schema harmonization. Preregistration is **not authorized**.

**Exactly one recommended next action:** commission an independent, connectivity-blind researcher to repeat the bounded v888 metadata/provenance/morphology identity audit under the frozen Task 023 contract, without access to this incident's numerical claims or Task 018 outcomes. Do not begin that task here.

## Scientific nonclaims

This record establishes no bilateral MN9 identity, mapping independence, replication, external validation, MaleCNS agreement or disagreement, laterality asymmetry, partner or synaptic-weight conservation, functional or causal mechanism, or behavioral mechanism.

## Stable external references and access audit

- BANC paper: https://doi.org/10.1038/s41586-026-10735-w
- BANC static deposit: https://doi.org/10.7910/DVN/7WTH1N
- BANC pipeline and data-product documentation: https://github.com/htem/bancpipeline
- BANC project repository: https://github.com/htem/BANC-project
- FlyBase adult MN9 term: https://flybase.org/cgi-bin/cvreport.pl?cvterm=FBbt%3A00111298
- Search-result exposure source, not used as identity evidence: https://github.com/Pronexsteam/brainlab

Only public documentation and search excerpts were accessed. No BANC data file, skeleton, mesh, candidate table, connectivity overlay, or live CAVE endpoint was queried. Retrieval date: 2026-09-30.
