# Task 007a - Public Lineage and MN9 Candidate Resolution

Status: COMPLETE for the scoped public-evidence attempt, with the valid
scientific completion state `sugar root = UNRESOLVED` and `MN9 = AMBIGUOUS`.
No commit, push, tag, neural dynamics, stimulation, LIF sweep, parameter
tuning, or simulation-based identity choice was performed.

## 1. Gate and starting Task 007 state

The required gate was verified before work began. Task 007 is committed at
`390d885b88bc39d1a7a127c87f9c58f179080577` (`feat: map Shiu reference
neurons to MaleCNS candidates`), `HEAD` equals `origin/master`, and the
working tree was clean.

Task 007 supplied 21 sugar roots plus FlyWire MN9 root
`720575940660219265`. Twenty sugar roots had later `LB3` / sugar-water
annotation overlap; root `720575940620900446` was unresolved. FlyWire MN9 was
`CB0701` / ingestion motor neuron. MaleCNS supplied 87 `LB3` candidates, a
43-body right-side biologically filtered sugar population, and two `CB0701`
candidate bodies: `10331` and `16949`. The Task 007 mapping fingerprint was
`832d8428c458e59cfff7b52fc257a4ba3fd85fdd6f3ebf47f01e02e218f50269`.

## 2. Unresolved v630 sugar root

Queried root: `720575940620900446`.

| evidence layer | dataset/version | result | interpretation |
| --- | --- | --- | --- |
| materialization-specific annotation | FlyWire FAFB, annotation v1.0.0, materialization basis 630 | row present; sensory, gustatory, afferent, MxLbN | valid version-matched v630 annotation evidence |
| later annotation table | FlyWire FAFB, annotation v3.0.0, 783-era basis | row absent | absence only; no deletion, retirement, merge, split, or supersession inferred |
| CAVE root lookup | `flywire_fafb_production`, `fly_v31` | redirected to Google authentication; no JSON payload admitted | live validity not determined |
| CAVE tabular change log | `flywire_fafb_production`, `fly_v31` | redirected to Google authentication; no JSON payload admitted | no public lineage result without credentials |

The CAVE/ChunkedGraph documentation identifies `get_tabular_change_log`,
`get_lineage_graph`, and root-validity methods as the relevant mechanisms.
The exact attempted URLs, timestamp, HTTP category, and no-payload result are
in `data/provenance/task007a-lineage-evidence.json`.

### Lineage result

Final lineage classification: `UNRESOLVED`.

Updated root candidates: none admitted. There is no public one-to-one,
split-descendant, merged-parent, deleted/retired, or superseded-root result.
The v630 root remains valid as a historical reference row, while its later
absence remains separate annotation-table evidence.

### Type cross-check and population impact

No later `LB3` / sugar-water type was found for this root. Type evidence is
therefore not substituted for lineage evidence. The 43-neuron MaleCNS sugar
population did not change: its prior and current fingerprint is
`2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b`.

## 3. Full local MaleCNS metadata comparison

The rows were read from the validated MaleCNS v1.0 annotation and
neurotransmitter Feather files. `null` is a source null, not an inferred
value.

| field | 10331 | 16949 |
| --- | --- | --- |
| bodyId | 10331 | 16949 |
| type | MN9 | MN9 |
| flywireType | CB0701 | CB0701 |
| superclass | cb_motor | cb_motor |
| class | null | null |
| subclass | pm | pm |
| supertype | null | null |
| instance | MN9_L | MN9_R |
| somaSide | L | R |
| rootSide | null | null |
| somaNeuromere | null | null |
| mancType | null | null |
| mancBodyid | null | null |
| entryNerve | null | null |
| exitNerve | PhN | PhN |
| dimorphism | null | null |
| matchingNotes | null | null |
| synonyms | null | null |
| status | Traced | Traced |
| statusLabel | Roughly traced | RT Hard to trace |
| consensus neurotransmitter | acetylcholine | acetylcholine |
| predicted neurotransmitter | unclear, confidence 0.4896524467 | acetylcholine, confidence 0.5731075580 |
| cell-type predicted neurotransmitter | acetylcholine, confidence 0.5386020793 | acetylcholine, confidence 0.5386020793 |
| receptorType | null | null |
| somaLocation | `[55365, 36271, 15889]` | `[41546, 38775, 15447]` |
| tosomaLocation | null | null |
| vfbId | VFB_jrmc20e1 | VFB_jrmc20e2 |
| itoleeHl | putative_primary | putative_primary |
| group | 10331 | 10331 |
| remaining location/lineage fields | assignedOlHex1/2, birthtime, trumanHl, mcnsSerial, serialMotif, fruDsx: null; mancGroup/mancSerial: null | same null fields |

The complete source-shaped records, including every additional Feather field,
are retained in the MN9 provenance JSON.

## 4. Official CB0701 cross-brain evidence

The official [MaleCNS Cell Type Explorer MN9 page](https://github.com/reiserlab/celltype-explorer-drosophila-male-cns/blob/main/types/MN9.html)
labels the male type `MN9`, gives `CB0701` as its FlyWire AKA, and reports two
neurons: one right and one left. It reports acetylcholine at approximately
53.9% confidence. Its page is generated for `male-cns:v1.0`.

The versioned FlyWire annotation evidence labels the reference type
`CB0701`, ingestion motor neuron, isomorphic, right-side, and PhN. This
supports the type-level mapping and makes `16949` anatomically compatible
with the right-side reference. It does not, by itself, prove an individual
cross-sex homolog or eliminate `10331` as a bilateral type counterpart.

The official type evidence is therefore:

- Male type: `MN9`.
- FlyWire type: `CB0701`.
- Male count: left 1, right 1.
- Across-brain relationship: one mapped type with two bilateral MaleCNS bodies.
- Dimorphism: the versioned FlyWire type row says `isomorphic`; the two local
  candidate rows have null `dimorphism` fields.
- Result: type correspondence supported; individual choice unresolved.

## 5. NeuronBridge evidence

The public [NeuronBridge Open Data API](https://link.springer.com/article/10.1186/s12859-024-05732-7)
was queried at `v3_10_0` using its `current.txt`, `config.json`,
`metadata/by_body`, and `metadata/cdsresults` endpoints.

| query | official returned result | direct resolving result |
| --- | --- | --- |
| MaleCNS body 10331 | `male-cns:v0.9:10331`; 1,671 FlyLight results; top result `R51H05`, score `29367.56`; rank field null | no FlyWire/FAFB/MN9-labeled match |
| MaleCNS body 16949 | `male-cns:v0.9:16949`; 2,118 FlyLight results; top result `VT005008`, score `34375.0`; rank field null | no FlyWire/FAFB/MN9-labeled match |
| FlyWire root `720575940660219265` | `flywire_fafb:v783:720575940660219265`; 1,492 FlyLight results | no MaleCNS/MN9-labeled match |

NeuronBridge exposes official aligned SWC resources in JRC2018 unisex space
for both candidates and the FlyWire query. The public result payloads did not
provide a direct candidate-to-reference score or rank. Candidate top scores
are not compared: they are results against different image-query records and
are not an identity threshold. Thus NeuronBridge corroborates that the public
morphology service was attempted but does not resolve the candidate pair.

## 6. Transformed morphology

Official transformed skeleton resources were checked through the NeuronBridge
metadata. No new morphology-matching system was built, no quantitative score
was invented, and no visual claim was made beyond resource availability.
Both candidate skeletons are available in `JRC2018_Unisex_20x_HR`, as is the
FlyWire MN9 skeleton. The available evidence is qualitative/resource-level
only and is insufficient to distinguish the bilateral candidates.

## 7. MANC evidence

Both local candidates have null `mancType` and `mancBodyid`. No independent
MaleCNS-to-MANC crosswalk was present in the validated v1.0 metadata. The
NeuronBridge public metadata separately exposes records in the MANC dataset
with the same numeric IDs, but those records carry unrelated MANC annotations;
numeric equality was not treated as a crosswalk. Independent MANC motor-neuron
support: none found.

## 8. Anatomical evidence

The reference row is right-side, motor, ingestion motor neuron, and PhN.

- `10331`: `MN9_L`, soma side L, `cb_motor`, `pm`, exit nerve PhN. The type
  and nerve are compatible, but the left side contradicts the right-side
  reference.
- `16949`: `MN9_R`, soma side R, `cb_motor`, `pm`, exit nerve PhN. Side and
  nerve are compatible.

Neither row supplies class, supertype, root side, soma neuromere, or entry
nerve. The side evidence points toward `16949`, but no source establishes an
individual cross-sex correspondence strongly enough to exclude `10331`.

## 9. Evidence matrix

| candidate | FlyWire type | across-brain | side | motor superclass | MANC | NeuronBridge | morphology | nerve/soma | dimorphism | contradictory evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10331 | CB0701 match | CB0701 -> MN9 | L | cb_motor | none | FlyLight-only candidate results; no direct target | aligned SWC available, no resolving score | PhN and motor type; side contradictory | isomorphic type evidence; row null | right reference vs MN9_L |
| 16949 | CB0701 match | CB0701 -> MN9 | R | cb_motor | none | FlyLight-only candidate results; no direct target | aligned SWC available, no resolving score | PhN, motor type, and right side compatible | isomorphic type evidence; row null | none |

The matrix is evidence-preserving, not a numeric confidence score. Its
source URLs and normalized values are in
`data/provenance/task007a-mn9-evidence.json`.

## 10. Final statuses

| identity question | final status | selected ID/candidates |
| --- | --- | --- |
| v630 sugar root `720575940620900446` | `UNRESOLVED` | no updated roots admitted |
| MN9 / CB0701 | `AMBIGUOUS` | `10331`, `16949`; selected ID `null` |

The MN9 result is `AMBIGUOUS`, not `EXACT`, because side evidence points to
`16949` but public evidence does not supply individual lineage, a direct
NeuronBridge candidate-to-reference match, a MANC crosswalk, or another
authoritative cross-sex individual correspondence that sufficiently rules out
the other bilateral body.

No exact MaleCNS MN9 ID was selected.

## 11. Determinism

The evidence model canonicalizes IDs, candidate order, evidence-source order,
and unordered evidence collections. Normalization and fingerprinting were
run twice with identical results:

| provenance record | fingerprint |
| --- | --- |
| lineage | `7b07598b48a4df2bb67fd76262800d0162ac6f47d7ab42e8b6642d4ae284ec6b` |
| MN9 | `dd37302ce60946040674f29f6b9b3fb1a5a0cf6edee1756aa122b248ab1c4ea8` |

Combined Task 007a evidence fingerprint:
`4681bbec86391752642ee2f9936e18d763ca77820d7f4dfb3492dd7e11da2d1a`.

No dynamics field is accepted by the evidence model. Ranking-only evidence
cannot produce an exact winner.

## 12. Limitations and explicit nonclaims

- A live CAVE lineage response was unavailable without authentication.
- Later-table absence is not evidence of deletion, retirement, merge, split,
  or supersession.
- NeuronBridge candidate scores are not individual identity scores and no
  threshold was invented.
- Morphology resource availability is not a morphology identity proof.
- The official MN9 bilateral type mapping is not an individual cross-sex
  mapping.
- MANC numeric ID equality was not treated as correspondence.
- No dynamics, connectivity result, spike rate, path length, or simulation
  outcome was used as identity evidence.
- The validated 43-neuron MaleCNS sugar population was not altered.

## 13. Validation and files

Task 007a added:

```text
data/provenance/task007a-lineage-evidence.json
data/provenance/task007a-mn9-evidence.json
docs/plans/2026-09-20-task-007a-public-lineage-and-mn9-resolution.md
src/malecns_sim/analysis/task007a.py
tests/test_task007a.py
```

The final validation commands and working-tree state are reported in the
completion handoff. The next task should be another evidence-resolution task,
not simulation-based candidate selection. Task 008 should not select an MN9
body unless it explicitly accepts the `AMBIGUOUS` status.
