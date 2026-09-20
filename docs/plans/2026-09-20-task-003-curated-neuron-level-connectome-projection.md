# Task 003 - Curated Neuron-Level Connectome Projection & Validation

## Status

COMPLETE after the 2026-09-20 v1.0 local execution. This task does not
implement neural dynamics or neurotransmitter sign semantics.

## Scope and source semantics

Task 002 validated the official v1.0 flat-connectome weights as a
segment-to-segment table. Its 151,856,684 rows contain 88,404,403 segment IDs,
not the curated neuron graph used for publication-level neuron counts. The
MaleCNS download page describes the annotations as curated neuron annotations
and the weights file as segment-to-segment connection strengths:

- <https://male-cns.janelia.org/download/>
- <https://doi.org/10.1016/j.cell.2026.08.015>
- <https://github.com/flyconnectome/2025malecns/blob/main/supplemental_data/quantify-neuron-connections.ipynb>

The raw segment graph remains distinct from the curated neuron graph. No raw
Feather file or derived graph artifact was added to Git.

## Official neuron-selection rule

The Cell paper's annotation semantics state that a body is a neuron when it
has a `superclass`; bodies without one are fragments. Task 003 implements that
boundary as the exact predicate:

```text
retain annotation row iff superclass is a non-empty string
```

The rule preserves all retained body IDs as sorted NumPy `int64` values. It
does not infer neuron identity from `type`, `class`, `status`, free text, or
connectivity. Missing or empty `superclass` is the only exclusion reason.
`status` is audited but is not an inclusion predicate: missing status is
retained when superclass is present, and `Glia` is not independently removed.
In this release all 11,864 `Glia` status records also lack superclass, so none
is retained by the superclass rule. The 94 non-empty `*_tbc` superclass values
are retained; this is required to reproduce the v1.0 full publication graph.

The current supplemental notebook is explicitly pinned to `VERSION = 'v0.9'`
and uses the older predicate `sc and 'tbc' not in sc`. Its printed v0.9
results are 25,563,426 edges between 166,391 graph-participating neurons and,
after `weight >= 5`, 6,237,402 edges between 165,752 neurons. Applying that
historical `not tbc` predicate to the local v1.0 files gives 25,574,615 edges
between 166,400 participating neurons and 6,240,402 edges between 165,768
neurons. It is therefore documented as a version/convention cross-check, not
used as the v1.0 selection rule.

The notebook counts only endpoints appearing in the filtered edge table. The
Task 003 curated identity set retains isolated annotated neurons so the CSR
dimension is scientifically explicit; the report separately gives
graph-participating and isolated counts.

## Annotation selection measurements

| Quantity | Measured value |
| --- | ---: |
| Annotation records | 211,577 |
| Curated IDs with non-empty `superclass` | 166,700 |
| Excluded IDs with missing/empty `superclass` | 44,877 |
| Missing `status` values | 5,472 |
| `status == Glia` records | 11,864 |
| Retained `status == Glia` records | 0 |
| Retained `*_tbc` superclass records | 94 |

## Projection and validation

The projection retains a raw edge only when both `body_pre` and `body_post`
are in the curated ID set. It then sorts and aggregates duplicate pairs with
exact integer weights, preserving self-edges. Thresholding is applied to this
projected neuron-level graph, never to the 88-million-node segment graph.

### Full curated graph

| Quantity | Measured value |
| --- | ---: |
| Raw segment edge rows | 151,856,684 |
| Endpoint rows retained | 25,582,938 |
| Endpoint rows excluded | 126,273,746 |
| Duplicate pairs after projection | 0 |
| Curated identity IDs | 166,700 |
| Retained source neurons | 165,480 |
| Retained target neurons | 166,330 |
| Graph-participating neurons | 166,483 |
| Isolated curated neurons | 217 |
| Self-edges | 101 |
| Total retained synaptic weight | 124,177,617 |
| Minimum / maximum edge weight | 1 / 2,591 |

The full edge count and participating-neuron count exactly reproduce the Cell
reference of 25,582,938 directed edges between 166,483 neurons. The 217
isolated curated IDs reconcile the 166,700 curated identity set with the
166,483-node connected graph.

### `min_synapses = 5` curated graph

| Quantity | Measured value |
| --- | ---: |
| Retained edges | 6,242,118 |
| Threshold-excluded projected edges | 19,340,820 |
| Graph-participating neurons | 165,836 |
| Isolated curated neurons | 864 |
| Self-edges | 33 |
| Total retained synaptic weight | 89,860,280 |
| Minimum / maximum edge weight | 5 / 2,591 |

The supplied reference is approximate at about 6.24 million edges and 165,536
neurons. The local v1.0 result is 300 neurons higher than that approximate
node figure while remaining in the same 6.24-million-edge scale. The older
v0.9 notebook output and its v1.0 `not tbc` adaptation also differ, so this
task does not force the approximate reference to match. The exact remaining
difference may reflect release and counting-version conventions; the local
predicate, threshold (`>= 5`), isolated-node treatment, self-edge treatment,
and measured counts are retained as the reproducible v1.0 result.

## CSR representation

The existing graph boundary continues to use `float64` CSR data because the
Task 001/002 propagation API is float-valued. Raw and projected synapse counts
remain exact `int64` arrays until CSR construction; changing CSR data dtype is
outside this task because it would change the established downstream numeric
boundary without a demonstrated need.

| Graph | Shape | NNZ | Index / indptr / data | CSR bytes | First / rebuild build seconds |
| --- | --- | ---: | --- | ---: | ---: |
| Curated full | `(166700, 166700)` | 25,582,938 | `int32 / int32 / float64` | 307,662,060 | 2.3567 / 2.3715 |
| Curated `>=5` | `(166700, 166700)` | 6,242,118 | `int32 / int32 / float64` | 75,572,220 | 0.5806 / 0.5883 |

For comparison, Task 002's raw segment CSR measurements were 2,175,897,824
bytes and 60.2125 / 59.5952 seconds for the full graph, and 445,091,984
bytes and 3.0190 / 2.8411 seconds for `min_synapses=5`. The curated graph is
the intended future simulation substrate; these measurements are engineering
comparisons, not biological performance claims.

## Deterministic fingerprints

The fingerprints include ordered curated IDs, CSR `indptr`, `indices`, and
`data` bytes. Rebuilding each graph twice produced identical fingerprints:

| Graph | Fingerprint | Rebuild equal |
| --- | --- | --- |
| Curated full | `fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4` | yes |
| Curated `>=5` | `661a07e346541da75e81fa0eac487102af496fcfc9f6bdc743c9ca957b4f4a74` | yes |

## Non-biological propagation smoke test

The existing scalar propagation primitive was run from deterministic body ID
`10001`. It is a graph test, not neural activity and not a neurotransmitter
or sign model.

| Graph | Non-zero targets | Aggregate activation | Output digest | Rebuild equal |
| --- | ---: | ---: | --- | --- |
| Curated full | 313 | 1,186.0 | `ec7cf8adda175aba5241c007a1e4c6a5b14f0729de562930d688a8ebb60ada27` | yes |
| Curated `>=5` | 64 | 735.0 | `803b0fa0b803bcf8721c6b95833d6097703d1293bea275ae75f0eac32874d3a3` | yes |

## Implementation and tests

The narrow implementation adds:

- `select_publication_neuron_ids`, with explicit exclusion and status audit
  counts;
- `project_numeric_connectome`, with exact integer endpoint filtering and
  duplicate-pair aggregation;
- `threshold_curated_projection`, which applies the threshold after projection;
- a curated projection model and CSR construction path; and
- offline synthetic regression coverage for selection, missing values,
  excluded records, large IDs, endpoint filtering, self-edges, duplicates,
  deterministic ordering, isolated neurons, threshold order, fingerprints,
  and propagation.

Validation completed:

- Task 002 baseline: 15 tests passed before Task 003 changes;
- Task 003 final suite: 21 tests passed;
- `uv run python -m compileall src`: PASS;
- CLI help, real annotation Feather inspection, and three-file manifest
  verification: PASS;
- real v1.0 projection, CSR rebuild, fingerprint, and propagation checks:
  PASS;
- `git diff --check`: PASS.

No neuPrint token or network-dependent test was used. The official download
files and supplemental notebook were sufficient for this boundary.

## Known limitations and nonclaims

- The raw table is segment-level; the curated projection is an annotation and
  endpoint-membership boundary, not a new synapse reconstruction.
- The 217 isolated curated identities remain in the matrix dimension even
  though the publication graph count reports participating endpoints.
- The threshold reference supplied for the paper is approximate and does not
  provide a fully pinned v1.0 notebook convention; the exact local result is
  recorded rather than altered to fit it.
- Connection weights are source synapse counts, not validated functional
  efficacies.
- No excitatory/inhibitory sign, neurotransmitter semantics, neural dynamics,
  learning, embodiment, GPU path, or behavior claim is made.

## Recommended next task

Task 004 may define the next authorized research scope. Any neural-dynamics
work must preserve the raw segment graph / curated neuron graph boundary and
must obtain separate authority for transmitter sign and biological dynamics.
