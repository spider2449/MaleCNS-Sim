# Task 002 - MaleCNS v1.0 Real-Data Validation and Provenance

## Status

COMPLETE after the 2026-09-20 real-data execution. No commit, push, tag, or
remote modification was performed.

## Baseline and scope

- Repository: `F:\coding\otherPrj\MaleCNS-Sim`
- Branch: `master`
- Baseline: `28989667fdc7d62f79f5cbc86770708bde23a44f`
- Baseline verification: exact `HEAD`, clean worktree, 27 tracked files, and
  the baseline 14-test suite passed before changes.
- Scope: the three official v1.0 flat-connectome Feather files only. No
  synapse-level or EM files were downloaded.

The official connectivity file is documented as a segment-to-segment full
connection graph. The normalized large-file path therefore preserves exact
integer segment IDs; it does not claim that every segment endpoint is a
biological neuron or assign an excitatory/inhibitory sign.

## Official source and provenance

Source organization: HHMI Janelia / FlyEM
Dataset page: <https://male-cns.janelia.org/download/>
Bulk-data base: `gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/`
Adapter/schema version: `malecns-v1-feather-explicit-mapping-v2`

| File | Exact source URL | Bytes | SHA-256 | Validated UTC |
| --- | --- | ---: | --- | --- |
| `body-annotations-male-cns-v1.0-minconf-0.5.feather` | `https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather` | 14,483,314 | `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2` | `2026-09-20T05:44:22+00:00` |
| `body-neurotransmitters-male-cns-v1.0.feather` | `https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-neurotransmitters-male-cns-v1.0.feather` | 43,282,834 | `95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621` | `2026-09-20T05:44:27+00:00` |
| `connectome-weights-male-cns-v1.0-minconf-0.5.feather` | `https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/connectome-weights-male-cns-v1.0-minconf-0.5.feather` | 1,051,241,946 | `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1` | `2026-09-20T05:45:48+00:00` |

The tracked provenance manifest is `data/provenance/male-cns-v1.0.json`.

## Phase 1 - annotations

Arrow schema:

```text
assignedOlHex1: double
assignedOlHex2: double
bodyId: int64
flywireType: string
group: double
instance: string
somaSide: string
statusLabel: dictionary<values=string, indices=int8, ordered=1>
superclass: string
type: string
vfbId: string
hemibrainType: string
itoleeHl: string
supertype: string
birthtime: string
mancBodyid: double
mancGroup: double
mancType: string
subclass: string
synonyms: string
class: string
rootSide: string
somaNeuromere: string
trumanHl: string
dimorphism: string
matchingNotes: string
entryNerve: string
mancSerial: double
mcnsSerial: double
serialMotif: string
fruDsx: string
exitNerve: string
receptorType: string
somaLocation: list<item: int64>
tosomaLocation: list<item: int64>
status: string
```

Measured statistics: 211,577 rows; 211,577 unique `bodyId` values; 0 null
IDs; 0 duplicate ID values; ID range 10,001 through 1,571,825,087. Every
non-ID field was schema-inspected. Usable non-null counts were: `flywireType`
143,156, `group` 147,514, `instance` 161,506, `somaSide` 150,726,
`statusLabel` 210,690, `superclass` 166,700, `type` 164,506, `vfbId`
166,686, `hemibrainType` 32,919, `itoleeHl` 37,754, `supertype` 34,096,
`birthtime` 7,904, `mancBodyid` 18,715, `mancGroup` 14,554, `mancType`
22,744, `subclass` 21,930, `synonyms` 3,955, `class` 26,513, `rootSide`
17,939, `somaNeuromere` 21,820, `trumanHl` 19,753, `dimorphism` 2,368,
`matchingNotes` 3,425, `entryNerve` 11,835, `mancSerial` 5,422,
`mcnsSerial` 3,945, `serialMotif` 902, `fruDsx` 5,012, `exitNerve` 1,005,
`receptorType` 752, `somaLocation` 141,781, `tosomaLocation` 995, and
`status` 206,105.

Measured mapping: `bodyId` -> integer ID, `type` -> cell type, `somaSide`,
`superclass`, and `status` -> preserved metadata. No classification was
inferred from free text.

## Phase 2 - neurotransmitters

Arrow schema:

```text
body: int64
cell_type: string
total_nt_predictions: int32
predicted_nt_confidence: double
predicted_nt: string
ground_truth: string
celltype_total_nt_predictions: int32
celltype_predicted_nt: string
celltype_predicted_nt_confidence: double
consensus_nt: string
```

Measured statistics: 1,835,518 rows; 1,835,518 unique `body` values; 0 null
IDs; 0 duplicate ID values; ID range 10,001 through 1,571,862,184. Prediction
fields were `predicted_nt`, `celltype_predicted_nt`, and `consensus_nt`; each
had 1,835,518 non-null values and 8 distinct values. Confidence fields were
`predicted_nt_confidence` with 1,834,661 non-null values and 857 missing, and
`celltype_predicted_nt_confidence` with 164,445 non-null values and 1,671,073
missing. `ground_truth` had 85,484 non-null values and 1,750,034 missing.
`cell_type` was non-null in 164,446 rows. The annotation/neurotransmitter ID
overlap was 187,016; 24,561 annotation IDs had no neurotransmitter row and
1,648,502 neurotransmitter IDs had no annotation row.

The adapter preserves source prediction labels and confidence metadata. It
does not assign excitatory or inhibitory biological sign.

## Phase 3 - aggregated connectivity

Arrow schema:

```text
body_pre: int64
body_post: int64
weight: int64
```

Measured statistics: 151,856,684 raw rows; source column `body_pre` with
1,834,661 unique IDs; target column `body_post` with 87,576,984 unique IDs;
union of endpoint IDs 88,384,522; 123 self-edge rows; 0 duplicate
source-target pairs; minimum weight 1; maximum weight 2,591; total connection
weight 311,833,243. Source IDs ranged from 10,001 through 1,571,862,184;
target IDs ranged from 10,001 through 1,571,863,634.

## Phase 4 - normalization and mapping

The explicit official mapping is:

```text
annotation_body_id = bodyId
edge_source_id = body_pre
edge_target_id = body_post
edge_weight = weight
annotation_cell_type = type
annotation_side = somaSide
annotation_class = superclass
annotation_status = status
neurotransmitter_body_id = body
prediction = consensus_nt, predicted_nt, celltype_predicted_nt
probability = predicted_nt_confidence, celltype_predicted_nt_confidence
```

The compact normalized representation used exact NumPy `int64` arrays for
88,404,403 node IDs, 151,856,684 source IDs, target IDs, and weights. It
deterministically orders IDs and source-target pairs, aggregates duplicate
pairs, preserves self-edges, and retains 211,577 normalized annotation
records. 187,016 annotated records received source neurotransmitter metadata.
No float conversion occurred.

## Phase 5 - CSR builds

CSR memory values are calculated sums of the `data`, `indices`, and `indptr`
array `nbytes`; they exclude Python and allocator overhead.

| Graph | Nodes / CSR shape | Edges / nnz | Index / indptr / data dtype | Total weight | CSR bytes | Build seconds |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| full | 88,404,403 / (88,404,403, 88,404,403) | 151,856,684 | int32 / int32 / float64 | 311,833,243 | 2,175,897,824 | 60.2125 first, 59.5952 rebuild |
| `min_synapses=5` | 88,404,403 / (88,404,403, 88,404,403) | 7,622,864 | int32 / int32 / float64 | 97,991,093 | 445,091,984 | 3.0190 first, 2.8411 rebuild |

The filtered graph had 1,445,249 participating endpoint IDs, 40 self-edges,
and 30,854 annotation IDs absent from filtered connectivity.

## Phase 6 - determinism

Fingerprints hash ordered numeric IDs plus CSR `indptr`, `indices`, and `data`
arrays with explicit length framing; no pickle or object serialization was
used.

| Graph | First fingerprint | Rebuild fingerprint | Equal |
| --- | --- | --- | --- |
| full | `7390a5fda49f95f8f0f8cebbc5f063631cd4558525e3ee8ca6e49c689d2e1c7b` | same | yes |
| `min_synapses=5` | `21ca5440c3e12aceaa223814e432cb7d2cbd12121fca20eda338c0fa50f592e5` | same | yes |

Measured fingerprint times were 2.1853 s and 2.1825 s for the full graph,
and 0.8467 s and 0.8906 s for the filtered graph.

## Phase 7 - graph propagation smoke test

This is the existing non-biological deterministic graph propagation primitive,
not neural activity. The deterministic starting ID was 10,001.

| Graph | Outgoing edges | Non-zero output targets | Aggregate activation | Output digest | Runtime seconds |
| --- | ---: | ---: | ---: | --- | ---: |
| full | 2,859 | 2,859 | 4,491.0 | `f8f0cdc03107af127d0bcd848afffd29ce895a27b3f4a57f6b19634318940d7d` | 20.5064 |
| `min_synapses=5` | 85 | 85 | 862.0 | `4ef73b44649f5b2b9ad754099b0f9150149697101453c93ed83b1c276fac93c1` | 17.6934 |

After graph rebuild/reload, both full and filtered propagation outputs were
identical. Full reload runtimes were 20.7369 s and 20.7963 s; filtered reload
runtimes were 17.6795 s and 17.8426 s. The corresponding digests were
identical to the first run.

## Phase 8 - benchmark environment and timings

Measured environment:

```text
Windows 11 IoT Enterprise LTSC 10.0.26100 build 26100
uv 0.12.17
Python 3.12.13
NumPy 2.5.3
pandas 3.0.6
SciPy 1.18.1
PyArrow 25.0.1
pytest 9.1.1
```

Direct Feather read timings from a fresh process were: annotations 0.017693
s, neurotransmitters 0.038802 s, and connectivity 1.597308 s. The complete
adapter normalization path, including source reads, exact-ID validation,
metadata mapping, duplicate check, and deterministic edge ordering, measured
196.4045 s. A second adapter reload measured 189.5001 s.

## Validation results

- Baseline suite: 14 passed before changes.
- Final suite: 15 passed.
- `uv run python -m compileall src`: PASS.
- CLI help, Feather inspection, and manifest verification: PASS.
- `git diff --check`: PASS.
- Repository hygiene: raw Feather files remain under ignored `data/raw/`; no
  raw data, virtual environment, cache, or generated large graph artifact is
  tracked.

## Defect and fix

The original row-wise adapter materialized every large connectivity row as
Python dictionaries and could not safely scale to the measured 151,856,684
rows and 88,404,403 node IDs. The narrow fix adds a compact exact-integer
normalized representation and CSR/fingerprint/propagation support for it;
the existing small-table object representation remains unchanged. A summary
truthiness bug exposed by NumPy node IDs was fixed, and regression coverage
was added for large integer IDs, duplicate aggregation, self-edges, and
prediction metadata.

## Explicit nonclaims and limitations

- This validates data identity, schemas, normalization, sparse graph
  construction, deterministic propagation, and measured provenance only.
- The propagation result is not neural firing or biological activity.
- Connection weights are source graph weights, not validated functional
  synaptic efficacies.
- No excitatory/inhibitory sign was assigned from neurotransmitter labels.
- The graph is segment-scale according to the official connectivity file; no
  claim is made that every endpoint is a separately annotated biological
  neuron.
- The raw files are local and intentionally untracked.

## Recommended next task

Task 003 may define the next authorized research scope. Do not infer neural
dynamics, biological sign, embodiment, or behavioral validation from this
Task 002 result.
