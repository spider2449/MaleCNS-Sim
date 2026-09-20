# Task 004 - Neurotransmitter Sign Policy & Signed Connectome

## Status

COMPLETE for the local MaleCNS v1.0 validation on 2026-09-20. Changes are
left uncommitted for review as requested. No neural dynamics are implemented.

Task 003 was verified before work began:

| Check | Result |
| --- | --- |
| Branch | `master` |
| HEAD | `f635189b8a73862f58ebb66965099c62c0816ab1` (`feat: add curated MaleCNS neuron connectome`) |
| Working tree | clean at start |
| Baseline | `uv run python -m pytest -q`: 21 passed |

## Scientific references and inspected source

The primary simulation reference was Shiu et al., “A Drosophila computational
brain model reveals sensorimotor processing”, Nature 634, 210-219 (2024),
DOI [10.1038/s41586-024-07763-9](https://doi.org/10.1038/s41586-024-07763-9).
The peer-reviewed article's Methods section was inspected, as was the official
companion repository [`philshiu/Drosophila_brain_model`](https://github.com/philshiu/Drosophila_brain_model).

The paper describes GABAergic and glutamatergic neurons as inhibitory and
dopaminergic, octopaminergic, and serotonergic neurons as excitatory. Its
exclusive inhibitory/excitatory whole-neuron treatment makes acetylcholine the
remaining excitatory category in the aggregate mapping used here. The official
code assigns one signed value to each presynaptic connection through its
`Excitatory x Connectivity` input and multiplies that value by the model's
synaptic scale. It does not provide a MaleCNS policy and does not contain a
histamine category matching this MaleCNS v1.0 table.

This task therefore implements an explicitly named aggregate-label analogue,
not an assertion that MaleCNS and FlyWire predictions are equivalent.

## MaleCNS v1.0 source evidence

The inspected neurotransmitter Feather schema is:

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

Task 004 joins these rows to the Task 003 curated identity predicate:
`superclass` is a non-empty string. The raw 1.8M-row neurotransmitter table is
not used as the primary simulation coverage denominator.

### Curated label distribution

The curated denominator is 166,700 neurons. There are 166,522 matching NT
rows and 178 curated IDs without an NT row. Counts below are measured locally.

| Source field | Counts by value |
| --- | --- |
| `consensus_nt` | acetylcholine 103,720; dopamine 392; gaba 22,069; glutamate 29,302; histamine 7,891; octopamine 101; serotonin 48; unclear 2,999; missing 178 |
| `predicted_nt` | acetylcholine 94,947; dopamine 4,443; gaba 20,231; glutamate 28,058; histamine 2,126; octopamine 101; serotonin 465; unclear 16,151; missing 178 |
| `celltype_predicted_nt` | acetylcholine 98,512; dopamine 4,448; gaba 21,483; glutamate 29,016; histamine 7,969; octopamine 87; serotonin 386; unclear 4,621; missing 178 |
| `ground_truth` | acetylcholine 52,779; dopamine 380; gaba 13,150; glutamate 14,397; histamine 4,683; octopamine 51; serotonin 44; missing 81,216 |

The prediction fields disagree on 21,714 curated neurons when comparing the
non-null values as a set. Confidence measurements are preserved, not used as
an unrequested probabilistic sign model:

| Confidence field | Present / missing | Min | 5th percentile | Median | 95th percentile | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `predicted_nt_confidence` | 165,665 / 1,035 | 0.1868583282 | 0.6451507951 | 0.9361791459 | 0.9747326673 | 0.9753679521 |
| `celltype_predicted_nt_confidence` | 164,445 / 2,255 | 0.1956920074 | 0.6099678093 | 0.9387226265 | 0.9688992177 | 0.9753679521 |

Ground-truth metadata is available for 85,484 curated neurons.

## Resolution policy

`NeurotransmitterEvidence` is source metadata only. It retains all three
prediction fields, both confidence fields, `ground_truth`, and source
`superclass`. `NeurotransmitterResolutionPolicy` is configurable and records
the winning source field, raw label, canonical identity, and selected
confidence.

The default policy identity is
`MaleCNSV1ConsensusThenPredictedThenCelltype`, with this exact precedence:

```text
consensus_nt -> predicted_nt -> celltype_predicted_nt -> unresolved
```

Fallback occurs only when a higher-precedence field is absent or blank. An
explicit `unclear` label wins its precedence position but resolves to the
explicit unresolved state; it does not silently fall through to a conflicting
lower-precedence prediction. Unsupported labels also remain unresolved.

For the measured curated set, the resolver selected `consensus_nt` for
166,522 neurons and had no source field for 178. It resolved 163,523 supported
identities and left 3,177 unresolved: 2,999 explicit `unclear` labels and 178
missing NT rows.

## Sign policies

Signs are model assumptions, not adapter fields. `NeurotransmitterSignPolicy`
returns `+1`, `-1`, `0`, or unresolved (`None`). The current policies do not
assign `0`; the representation supports it for a future explicit neutral or
modulatory policy.

| Resolved identity | `Shiu2024SignPolicy` | `ConservativeSignPolicy` |
| --- | ---: | ---: |
| acetylcholine | +1 | +1 |
| gaba | -1 | -1 |
| glutamate | -1 | unresolved |
| dopamine | +1 | unresolved |
| octopamine | +1 | unresolved |
| serotonin | +1 | unresolved |
| histamine | unresolved: absent from the Shiu source category | unresolved |
| unclear / missing / unsupported | unresolved | unresolved |

The Shiu-compatible policy follows the paper's aggregate treatment as closely
as the MaleCNS data permits. It is not a claim that a MaleCNS consensus label
is the same object as Shiu's FlyWire per-synapse prediction and majority rule.
In particular, histamine is deliberately unresolved because it is present in
MaleCNS v1.0 but not in the inspected Shiu transmitter categories. The
conservative policy refuses the additional glutamate and monoamine assumptions.

## Signed anatomical representation

The existing unsigned projection remains unchanged:

```text
anatomical_weight = synapse_count
```

`SignedAnatomicalConnectome` separately stores ordered per-neuron resolution
records, per-neuron sign results, per-edge presynaptic signs, and derived signed
counts. The derived value is:

```text
signed_count = presynaptic_sign * anatomical_weight
```

An unresolved presynaptic sign does not become zero: its edge has an explicit
unresolved mask and no signed count. Self-edges use the same presynaptic sign
rule as every other edge. No future functional weight is represented.

## Local coverage results

Both rows below use the 166,700-neuron curated identity dimension. “Unresolved
neurons” means sign-unassigned neurons; unresolved NT count is 3,177 under the
resolution policy. “Signed weight fraction” is assigned anatomical weight over
all anatomical weight. No policy assigned neutral edges in this validation.

| Graph / policy | Sign-assigned neurons | Unresolved neurons | Signed edges | Unresolved edges | Signed weight / total | Fraction | Excitatory edges / weight | Inhibitory edges / weight |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full / Shiu | 155,632 | 11,068 | 24,904,953 | 677,985 | 121,444,188 / 124,177,617 | 0.9779877480 | 15,180,678 / 74,674,954 | 9,724,275 / 46,769,234 |
| full / conservative | 125,789 | 40,911 | 19,670,694 | 5,912,244 | 99,208,816 / 124,177,617 | 0.7989267180 | 14,745,137 / 73,491,164 | 4,925,557 / 25,717,652 |
| `>=5` / Shiu | 155,632 | 11,068 | 6,113,545 | 128,573 | 88,022,553 / 89,860,280 | 0.9795490622 | 3,827,619 / 54,423,300 | 2,285,926 / 33,599,253 |
| `>=5` / conservative | 125,789 | 40,911 | 5,027,863 | 1,214,255 | 73,011,399 / 89,860,280 | 0.8124991264 | 3,777,780 / 53,848,657 | 1,250,083 / 19,162,742 |

Unresolved anatomical weight is, respectively, 2,733,429; 24,968,801;
1,837,727; and 16,848,881 for the four rows above. The unsigned graph
dimensions remain Task 003's 25,582,938 full edges and 6,242,118 `>=5` edges.

Actual source superclass values were retained. Among the largest source groups,
`ol_intrinsic`, `cb_intrinsic`, `vnc_intrinsic`, `visual_projection`,
`vnc_sensory`, `cb_sensory`, `ascending_neuron`, and `descending_neuron` have
substantial signed coverage under the Shiu policy. `ol_sensory` is an important
exception: all 6,098 curated `ol_sensory` neurons resolve to histamine, so none
receives a sign under either current policy and all of their outgoing edges
remain unresolved. `vnc_motor` also remains substantially unresolved because
389 of its 708 curated neurons have consensus `unclear`.

Selected superclass weight coverage is shown below as signed anatomical weight
over total anatomical weight for that source superclass. These are the actual
MaleCNS labels, not reconstructed sensory/motor categories.

| Superclass (curated neurons) | Full / Shiu | Full / conservative | `>=5` / Shiu | `>=5` / conservative |
| --- | ---: | ---: | ---: | ---: |
| `ol_intrinsic` (89,403) | 43,937,243 / 43,984,759 | 34,570,468 / 43,984,759 | 28,767,287 / 28,782,628 | 23,242,536 / 28,782,628 |
| `cb_intrinsic` (32,164) | 38,053,549 / 39,150,032 | 29,959,087 / 39,150,032 | 28,602,203 / 29,333,289 | 22,695,403 / 29,333,289 |
| `vnc_intrinsic` (13,161) | 15,412,984 / 15,592,981 | 13,185,691 / 15,592,981 | 12,520,344 / 12,599,082 | 10,694,437 / 12,599,082 |
| `visual_projection` (9,201) | 7,214,935 / 7,354,973 | 6,301,033 / 7,354,973 | 5,021,981 / 5,097,895 | 4,425,444 / 5,097,895 |
| `vnc_sensory` (6,370) | 3,140,872 / 3,300,704 | 3,121,198 / 3,300,704 | 2,328,478 / 2,447,941 | 2,311,524 / 2,447,941 |
| `ol_sensory` (6,098) | 0 / 651,362 | 0 / 651,362 | 0 / 573,925 | 0 / 573,925 |

## Fingerprints

The existing unsigned graph fingerprint is retained. Signed fingerprints add
the unsigned identity, resolution policy identity, sign policy identity,
ordered source evidence and resolution provenance, and ordered sign arrays.
Rebuilding the signed graphs twice produced equal fingerprints; policy identity
changes the fingerprint.

| Graph / policy | Existing unsigned fingerprint | Signed fingerprint |
| --- | --- | --- |
| full / Shiu | `fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4` | `861f07218122e122383d8465b30e65f5eb1d5b11a474b767a6312b3115ecaf25` |
| full / conservative | `fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4` | `327fc0a88ae23cbf2c34cacea3e9a827f27ba27c21083b6c612ca55bfb373671` |
| `>=5` / Shiu | `661a07e346541da75e81fa0eac487102af496fcfc9f6bdc743c9ca957b4f4a74` | `0367327291c21f6154c4d4253a7673acd11b045fa43114d4a611b0a12ce1c85d` |
| `>=5` / conservative | `661a07e346541da75e81fa0eac487102af496fcfc9f6bdc743c9ca957b4f4a74` | `1b4d81c2b01db572f9cf56e133f9065a6ad7bf400fb06ab566ca07246017f9bc` |

## Tests and validation

- `uv run python -m pytest -q`: 50 passed.
- `uv run python -m compileall src`: pass.
- Synthetic tests cover resolution precedence, unresolved and conflicting
  fields, confidence retention, all supported labels, both policies, unresolved
  signs, presynaptic sign application, self-edges, derived counts, unsigned
  preservation, ordering, deterministic fingerprints, and policy identity.
- The local real-data analysis was run twice in fresh Python processes. The
  measured distributions, graph coverage, and fingerprints above were equal
  between runs.
- `git diff --check`: pass.

## Scientific limitations and explicit nonclaims

- A predicted neurotransmitter is not perfect ground truth.
- Neurotransmitter identity does not universally determine functional sign.
- Co-transmission may exist.
- Receptor identity is not represented by this connectome.
- Gap junctions are not represented.
- Neuropeptide and other modulatory effects are not represented.
- Signed synapse count is a model assumption, not measured postsynaptic
  current or a future functional synaptic weight.
- The Shiu-compatible mapping does not claim MaleCNS/FlyWire data equivalence.
- This task adds no membrane voltage, spikes, refractory state, time steps,
  delays, alpha synapses, Poisson inputs, LIF parameters, Brian2, or GPU
  kernels.

## Files changed

- `src/malecns_sim/data/neurotransmitter.py`
- `src/malecns_sim/sign.py`
- `src/malecns_sim/graph/signed.py`
- `src/malecns_sim/data/__init__.py`
- `src/malecns_sim/graph/__init__.py`
- `src/malecns_sim/__init__.py`
- `tests/test_task004.py`
- `README.md`
- this plan file

## Recommended next task

Task 005 - Reference Leaky Integrate-and-Fire Engine. It must consume this
signed anatomical layer explicitly and receive separate authorization for all
neural-dynamics assumptions.
