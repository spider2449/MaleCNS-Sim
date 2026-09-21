# Task 008a - Sugar Sensory Laterality Audit

Status: COMPLETE on 2026-09-21. This audit is metadata-first and does not use
LIF output, connectivity strength, or MN9 firing to assign sensory laterality.
No Task 008 result was overwritten.

## 1. Starting result and preservation

HEAD at audit start and completion is `c977108ff42eb6c18aaee0ce626625bacd53a6b6`.
The completed Task 008 result remains at the ignored path
`data/derived/task008-results.json`. Its exact pre-audit SHA-256 is
`30dc0b57be64a8272a77763bc28d25409b6a6e489e15f87ef91a4ea785a80595` and its
size is 262032 bytes. The preservation manifest records the experiment
fingerprint, population fingerprints and IDs, predicate, CUDA float64 backend,
result digests, and per-condition seed manifests:
`data/provenance/task008a-preserved-task008.json`.

The current Task 008 implementation uses `root_side`/`rootSide`, not
`soma_side`/`somaSide`:

```text
flywireType == LB3
and superclass == cb_sensory
and class == gustatory
and entryNerve == MxLbN
and rootSide == requested anatomical side
```

Therefore the conditional `SOMA_SIDE_DEFINED_EXPLORATORY_RESULT` label is not
applicable: the retained result is a root-side-defined exploratory result, and
the audit tests whether that existing rule is anatomically justified.

## 2. Source pool and deterministic audit table

The source is the local MaleCNS v1.0 annotation Feather file, whose local
provenance is recorded in `data/provenance/male-cns-v1.0.local.json`. There are
87 rows with `flywireType == LB3`. Applying the complete biological filter
before side filtering gives 85 sugar candidates:

```text
flywireType == LB3
superclass == cb_sensory
class == gustatory
entryNerve == MxLbN
```

The two excluded LB3 rows are body IDs `923024` and `957530`; both are
gustatory/cb_sensory rows with `rootSide=R` but have missing `entryNerve`, so
they are not admitted to the sugar pool.

The complete deterministic candidate record table is retained in
`data/provenance/task008a-sugar-candidate-audit.json`. It contains, for every
one of the 85 candidates, body ID, type, instance, flywire type, superclass,
class, subclass, soma side, root side, soma neuromere, entry nerve, receptor
type, matching notes, status, status label, exit nerve, soma/root-location
fields, VFB/type corroboration fields, and the audit fingerprint
`d7d6c74e8ac1c236969ebb941be1a1fa9c7cf1f66e8515f080b864fdcc45e2cd`.

All 85 records are sorted by numeric body ID. No body-ID parity or simulation
output is used.

## 3. Soma/root cross-tabulation

| somaSide | rootSide | count |
| --- | --- | ---: |
| missing | L | 42 |
| missing | R | 43 |

Non-missing mismatches: none.

Missing `somaSide` values: all 85 candidate IDs:

```text
33339, 71254, 72047, 72059, 78240, 85806, 92440, 93290, 101087,
120303, 122806, 125405, 128129, 129171, 130693, 136183, 140015,
140619, 140851, 141663, 142827, 152400, 158537, 159772, 160435,
163597, 166190, 167663, 178321, 178913, 180314, 183061, 183084,
187492, 187776, 190769, 199196, 199308, 201075, 202888, 203234,
204726, 209155, 210344, 215556, 236475, 261048, 261450, 262567,
272263, 312102, 317616, 374701, 512551, 512552, 516216, 516217,
516218, 518542, 531237, 538117, 550065, 557646, 916953, 933317,
942168, 104287023, 147619274, 158893964, 174444965, 213650853,
245892505, 349137284, 388541892, 422510463, 456838775, 475202322,
553738738, 581710868, 766547228, 786482749, 816904261, 884238775,
885642755, 1026733570
```

Missing `rootSide` values: none. Consequently, the direct soma-defined
populations are `L=0`, `R=0`, while the root-defined populations are `L=42`,
`R=43`.

## 4. Annotation semantics and official evidence

The official MaleCNS download page identifies the v1.0 annotation Feather as
the curated neuron-annotation source and directs programmatic users to the
MaleCNS neuPrint dataset:
<https://male-cns.janelia.org/download/>.

The official Berg et al. MaleCNS methods text states that sensory/receptor
neurons can cross the midline and that their side of entry into the neuropil
is annotated as `rootSide`:
<https://iris.cnr.it/retrieve/716dd1ad-7d40-480d-b58d-8b8f75866571/2025.10.09.680999v2.full.pdf>.

The same methods text says that `instance` combines type with `somaSide`, or
with `rootSide` for sensory neurons. This supports treating `somaSide` as a
soma-location/type-instance annotation and `rootSide` as the sensory-root
laterality annotation; it does not support using soma location as the side of
sensory afferent entry.

The resulting semantic conclusions are:

| Field | Supported meaning for this audit |
| --- | --- |
| `somaSide` | Side associated with the soma, when annotated. It is absent for all 85 sugar candidates. The official methods do not define it as sensory afferent entry laterality. |
| `rootSide` | Side of sensory/root entry into neuropil. This is the source-supported field for sensory afferent laterality. |
| `entryNerve` | Nerve by which the neuron enters the CNS. It identifies the pathway, not a left/right code by itself. |

The official evidence is explicit for `rootSide` in sensory neurons but is not
a sugar-specific sentence naming `MxLbN`. That limitation is retained rather
than filled by third-party inference.

## 5. Entry-nerve consistency

All 85 admitted candidates have `entryNerve=MxLbN`: 42 root-L and 43 root-R.
The two excluded LB3 rows lack `entryNerve`. `MxLbN` is a shared nerve label,
not a side-coded label; no L/R inference is made from the string itself.
The root-side split is therefore compatible with a common bilateral
maxillary/labial gustatory afferent pathway, while `entryNerve` alone cannot
choose the hemisphere.

## 6. Type, instance, and pairing corroboration

Root-side type counts are:

| type | L | R |
| --- | ---: | ---: |
| `LB3` | 1 | 0 |
| `LB3a` | 9 | 8 |
| `LB3b` | 5 | 6 |
| `LB3c` | 12 | 10 |
| `LB3d` | 11 | 15 |
| `LB4b` | 4 | 3 |
| missing type | 0 | 1 |

There are 84 explicit instance values with `_L` or `_R`; every suffix agrees
with `rootSide`. Body `104287023` is the one candidate with both type and
instance missing. There are no instance/root suffix contradictions.

The paired type groups present on both sides are `LB3a`, `LB3b`, `LB3c`,
`LB3d`, and `LB4b`, with the unequal counts shown above. `LB3_L` is a
left-side singleton and `104287023` is a right-side untyped/uninstanced
candidate. These asymmetries are retained; no candidates are removed to force
bilateral equality.

Instance/type suffixes are corroboration only. They do not override the
official sensory-root annotation rule.

## 7. Candidate population definitions and set comparison

### A. SomaSide-defined

```text
left  = no candidates
right = no candidates
```

Both populations are empty because `somaSide` is missing for every candidate.

### B. RootSide-defined

```text
left  = the 42 IDs in the `<missing>, L` cross-tab cell
right = the 43 IDs in the `<missing>, R` cross-tab cell
```

The exact sorted ID lists are retained in the audit JSON and in the preserved
Task 008 manifest. The root-defined fingerprints are:

| population | count | fingerprint |
| --- | ---: | --- |
| root-left | 42 | `8b1c625ddf719e5853d409223d88b8c997a1fdcffb298210965b0402efce49c7` |
| root-right | 43 | `2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b` |

### C. Better source-supported rule

`rootSide` is the source-supported sensory-side rule. There is no need for a
morphology classifier or an LIF-based tie-breaker.

The soma/root intersection is empty because the soma-defined sets are empty.
The left symmetric difference is 42 root-only IDs; the right symmetric
difference is 43 root-only IDs. No non-missing side disagreement exists.

## 8. Identity decision

Classification: **VALID_AS_RUN**.

The existing Task 008 population predicate uses `rootSide`, and the official
MaleCNS methods explicitly assign sensory/root entry laterality to `rootSide`.
The decision is independent of dynamics. No candidate is assigned to a wrong
sensory input side under the audited rule, and no population correction is
required.

## 9. Structural diagnostics after identity decision

Only after selecting `rootSide` from annotation semantics, the retained full
prepared graph was inspected structurally. The outgoing population report from
the preserved Task 008 result gives anatomical totals and sign coverage:

| population | resolved edges | unresolved edges | resolved anatomical weight | unresolved anatomical weight | total anatomical weight |
| --- | ---: | ---: | ---: | ---: | ---: |
| root-left, 42 | 2873 | 2 | 14395 | 2 | 14397 |
| root-right, 43 | 3132 | 13 | 17356 | 25 | 17381 |

On the full prepared signed graph, root-left has 459 first-hop targets and
root-right has 458. Both populations reach both MN9 candidates (`10331` and
`16949`) in two hops. The effective-graph first-hop fingerprints are:

```text
root-left  f30751f054423ad0951692f0a7160ba5e9555bee1eb6f2578938ff540d879fa4
root-right 59d187eb341767a35f0c54d0e18bc6b3232b9ff956a8462437ebf28b213c6d6d
```

These are explanatory diagnostics only. They did not influence identity,
population membership, or the VALID_AS_RUN decision.

## 10. Dynamics decision

No new dynamics verification was run. Because the current rule is
`VALID_AS_RUN`, the existing Task 008 CUDA float64 numerical result remains
intact and the observed asymmetry remains a subsequent circuit-analysis
question. No corrected six-frequency sweep or 100 Hz verification run is
required by Task 008a.

## 11. Tests and implementation

Added `src/malecns_sim/analysis/task008a.py` with deterministic source-pool
loading, candidate records, crosstabulation, missing/mismatch detection,
side-population comparison, provenance constants, and a non-circular decision
model. Added `tests/test_task008a.py` covering the requested crosstab,
mismatch, missing values, ordering, population construction, symmetric
difference, provenance, non-circularity, and instance corroboration cases.

The exact requested validation commands are:

```text
uv run python -m compileall src
uv run python -m pytest -v
git diff --check
```

## 12. Limitations

- The official methods establish `rootSide` semantics for sensory/receptor
  entry into neuropil; they do not provide a sugar-specific public definition
  of every `MxLbN` annotation detail.
- `entryNerve` is pathway identity, not a side code.
- `somaSide` and soma-location fields are absent for this candidate pool, so
  morphology was not needed and was not used.
- `LB3` is a MaleCNS/FlyWire type-level mapping boundary, not a claim that
  these 85 bodies are the same 21 FlyWire segments.
- Unequal bilateral counts and the untyped/uninstanced candidate are retained.
- Structural diagnostics use the existing curated/prepared graph and are not
  biological proof of functional influence.

## 13. Completion state

Task 008a is complete as `VALID_AS_RUN`. HEAD remains unchanged. The
`task008-paused-before-gpu-gate` stash remains preserved and was not dropped.
No commit, push, or tag was created.
