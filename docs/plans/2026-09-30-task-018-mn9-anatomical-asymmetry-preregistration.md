# Task 018 — MN9 Anatomical-Asymmetry Preregistration

Date: 2026-09-30. Status: FROZEN DESIGN; execution awaits separate authorization.

**TASK 018 EXECUTION NOT AUTHORIZED BY THIS COMMIT.** This document fixes a
future read-only structural analysis. It reports no new Task 018 measurement.

## Provenance and independence

Task 007b resolved MaleCNS body 10331 as `MN9_L` and 16949 as `MN9_R` at
`SIDE_RESOLVED`, before connectivity analysis. Task 009 then documented full
curated-graph incoming anatomical weights of 6,012 and 556, respectively, and
278 versus 137 presynaptic neurons. Task 015, committed as `1113c0c` on
2026-09-22, explicitly asked what anatomical organization accounts for this
approximately 10.8-fold gap. It proposed presynaptic composition and other
descriptive decompositions without selecting a final metric. Task 017L scoring
was committed later as `51519db` on 2026-09-30. Task 017N Decision B authorizes
prospective design of this independent question. The prior Task 009 values
motivate the question; future Task 018 values are not inspected in this design.
Task 017 is sealed as `NOT_ROBUST`; Task 017Q remains `DEFERRED`.

## Scientific question and claim boundary

**Primary question:** In the frozen MaleCNS v1.0 full curated anatomical graph,
how does the established greater incoming synapse-count weight of `MN9_L`
decompose into (i) weight differences from presynaptic neurons connected to
both MN9 neurons and (ii) weight from presynaptic neurons connected to just
one MN9 neuron?

This is an exact, descriptive accounting of graph edges, not a test of a
biological cause, firing, functional strength, sex difference, or Task 017
robustness. There is no directional hypothesis for which component dominates.
No secondary confirmatory question is registered. An optional, explicitly
nonclassifying threshold sensitivity is specified below.

## Frozen inputs and graph construction

- Dataset: the three MaleCNS v1.0 Feather files in
  `data/provenance/male-cns-v1.0.json`, with its recorded SHA-256 values:
  annotations `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`,
  neurotransmitters `95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621`,
  and weights `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1`.
  The neurotransmitter file is identity-verified with the release but its
  values are not used by the primary analysis.
- Use `official_v1_mapping()`, `load_male_cns_v1_numeric()`,
  `select_publication_neuron_ids()`, and `project_numeric_connectome()` under
  adapter schema `malecns-v1-feather-explicit-mapping-v2`. The primary graph is
  the complete 166,700-node curated neuron projection, without a synapse-count
  threshold, sign projection, or LIF representation. Require its established
  25,582,938 directed edges and 124,177,617 total synapses before analysis.
- `body_pre` is source, `body_post` is target, and positive integer `weight`
  is an anatomical synapse count. Retain only edges whose source and target
  belong to the curated set. The existing projection sums duplicate source,
  target rows as integer counts and sorts pairs deterministically. Do not
  reinterpret counts as physiological efficacy. Include autapses if present;
  the established projection has no autapse exclusion.
- Require both MN9 IDs in the curated node set. Their `type=MN9`,
  `instance=MN9_L/MN9_R`, and `somaSide=L/R` must agree with Task 007b's
  annotation evidence. These annotations validate readout identity only.
  `rootSide` is not used for the motor-neuron identities. For context, the
  frozen sugar sensory predicate is `flywireType=LB3`, `class=gustatory`,
  `superclass=cb_sensory`, `entryNerve=MxLbN`, with `rootSide` yielding
  42 LEFT and 43 RIGHT bodies. Sugar membership is not used in the primary
  endpoint. Missing source-side or neurotransmitter metadata never excludes
  an edge; presynaptic side, neuropil, transmitter, and sugar annotations do
  not enter the primary endpoint. Missing or contradictory MN9 identity fields
  stop the run. Other curated neurons need no side assignment.
- The unit of analysis is one frozen bilateral MN9 pair in one connectome
  release. Each directed, aggregated source-to-MN9 edge contributes once.
  An MN9 with no incoming edges has weight zero and an empty partner set.

## Primary endpoint: exact presynaptic partner partition

For `s` in `{L,R}`, let `w_s(p)` be the nonnegative integer synapse count on
the aggregated directed edge from curated presynaptic body `p` to `MN9_s`, or
zero if that edge is absent. Define `P_s={p:w_s(p)>0}`, `C=P_L∩P_R`,
`U_L=P_L\P_R`, and `U_R=P_R\P_L`. Order all sets by ascending numeric body ID.
No partner-side matching or inferred homology is applied: shared means the
**same curated body ID** projects to both MN9 targets.

```text
W_L = sum over p in P_L of w_L(p)
W_R = sum over p in P_R of w_R(p)
D = W_L - W_R
D_shared = sum over p in C of (w_L(p) - w_R(p))
D_left_only = sum over p in U_L of w_L(p)
D_right_only = -sum over p in U_R of w_R(p)
D = D_shared + D_left_only + D_right_only
```

Report these integer values, `|P_L|`, `|P_R|`, `|C|`, `|U_L|`, and `|U_R|`.
For `D>0`, report signed contribution fractions `D_i/D` without clipping;
negative fractions represent offsets and fractions must sum exactly to 1
apart from decimal rendering. For `D=0`, fractions are `null` with reason
`zero_gap`; for `D<0`, fractions are `null` with reason `reversed_gap`.
The primary comparison uses the signed left-minus-right gap; absolute values
are used solely to identify the component of largest magnitude. There is no
normalization by number of partners, no statistical resampling, and no
minimum-effect threshold. Exact integers govern decisions; displayed decimal
fractions have no decision role.

## Decision rule, reference population, and multiplicity

First verify the exact partition identity, set disjointness/completeness,
input hashes, graph identity, and MN9 annotation identity. A failed check
produces `INDETERMINATE` with an error reason and no valid scientific result.
For a valid graph:

- `D<=0`: `NO_LEFT_INCOMING_WEIGHT_EXCESS_IN_THIS_GRAPH`.
- `D>0`: find the maximum of `|D_shared|`, `|D_left_only|`, and
  `|D_right_only|`. If exactly one component attains it, classify as
  `SHARED_PARTNER_DIFFERENCE_LARGEST`, `LEFT_ONLY_INPUT_LARGEST`, or
  `RIGHT_ONLY_OFFSET_LARGEST`, respectively. If two or three tie exactly,
  classify `TIED_LARGEST_COMPONENTS` and list every tied component.

These labels identify the largest *magnitude* in an exact accounting; they
do not assert that one component explains a biological mechanism or that its
magnitude is statistically unusual. In the positive-gap branch, the right-only
term is nonpositive and can only offset the gap. Report all three signed
components even when one is largest. No external reference/null population is
used: the single selected bilateral pair and this deterministic connectome
provide no defensible sampling distribution, independent homologous-pair
registry, or side/class-matched null. No p-value, bootstrap interval, rank,
or significance claim is permitted. The three terms are one exact identity,
not three separately tested endpoints; no voting or multiplicity correction
is applicable.

## Fixed sensitivity analysis

Recompute the identical partition and reporting fields on the existing
`threshold_curated_projection(..., min_synapses=5)` graph, where the threshold
is applied **after** duplicate-pair aggregation. Require the established
6,242,118 edges and 89,860,280 synapses. Label every output
`SENSITIVITY_MIN_SYNAPSES_5`. This sensitivity cannot change the primary
classification, even if its largest component differs. No Task 017 V1–V7
model variant is used.

## Exploratory analyses not part of the confirmatory Task 018 result

Potential presynaptic soma-side/neuropil distributions, transmitter or
Task 004 sign composition, sugar-linked path depth, source-neuron homology,
top-contributor concentration, and relationships to dynamics require separate
fixed annotation, missingness, ontology, or causal designs. They are omitted
from the confirmatory endpoint. Task 017-derived 512730 direction stability,
10313 and 10135 side differences, 12752 LEFT instability, and the V4/V5/V6
versus V1/V2/V3/V7 pattern are quarantined here. None selected an MN9 body,
graph, metric, threshold, anatomical region, direction, exclusion, or success
rule above. Any later output from these ideas is hypothesis-generating, cannot
alter the Task 018 primary classification or retroactively become a
preregistered finding, and needs another independent prospective study for
confirmation.

## Future execution architecture and integrity

The separately authorized execution should read the three raw Feather files
and the tracked manifest, verify file hashes before loading, construct both
existing graph projections, validate the expected graph and MN9 identities,
compute the primary result, then compute sensitivity. CPU integer/NumPy
operations suffice. GPU, Task 017 checkpoint/sidecars, Task 017 scoring,
stimulation, and LIF simulation are unnecessary and must not be inputs.
There is no random seed because there is no sampling.

Proposed ignored outputs are `data/derived/task018-results.json` and
`data/derived/task018-report.md`. The JSON should use schema identifier
`malecns-sim-task018-anatomical-asymmetry-v1`, record the preregistration
SHA-256 and Git commit, raw-file and manifest SHA-256 values, adapter schema,
source commit, graph counts and canonical unsigned-graph fingerprints for both
projections, MN9 IDs and checked annotation fields, exact partner counts and
signed partition terms, fractions/null reasons, primary classification,
sensitivity result, execution timestamp, software versions, and a result
digest. Use SHA-256 of canonical UTF-8 JSON (sorted keys, compact separators,
no NaN) over a payload excluding its own digest, as in the repository's
existing canonical-result convention. Produce a candidate in a temporary
path and atomically publish both final outputs only after all validations
pass. On failure, keep an explicit incomplete/error record outside final
result paths; never emit a completed classification from partial data. A
future implementation must check repeated deterministic runs agree exactly.
Stop on raw hash, annotation identity, projection count, integer, digest,
partition, or output-atomicity failure. Scientifically surprising valid
values do not stop the analysis or justify changing this specification.

## Frozen-document fingerprint and authorization

The Task 018 preregistration fingerprint is the SHA-256 of the exact committed
UTF-8 bytes of this Markdown file, including its line endings. Reproduce with
`git show <preregistration-commit>:docs/plans/2026-09-30-task-018-mn9-anatomical-asymmetry-preregistration.md`
as the byte stream into SHA-256, or hash the file in a clean checkout of that
commit. The fingerprint value is recorded in the commit/report, not inside
this file, avoiding circular identity. This content-hash convention is
reproducible from committed content; Task 016's canonical-JSON specification
fingerprint applies to its separate executable specification and is not
silently reused for this Markdown-only design.

All scientific choices needed for this narrow descriptive analysis are fixed
here. The next eligible, separately authorized task is **Task 018A — MN9
Anatomical-Asymmetry Execution**. This commit itself authorizes no Task 018A,
Task 018R, Task 017 simulation, scoring, tag, or release.
