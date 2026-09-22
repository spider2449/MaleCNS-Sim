# MaleCNS-Sim Authoritative Research Checkpoint

Date: 2026-09-22

This document consolidates the validated scientific state through completed
Task 011. It is the authoritative research checkpoint for Tasks 004-011.

## 1. Scientific scope and nonclaims

MaleCNS-Sim is an executable connectome simulation and research platform. It
combines the curated MaleCNS v1.0 neuron graph, explicit neurotransmitter sign
policies, and a reproducible reference LIF dynamics engine.

The connectome is not an executable biological brain. A simulation/model
causal effect is not biological causality. Results in this checkpoint are
model-level computational results and do not establish an actual-fly
mechanism, biological necessity, behavioral necessity, receptor-specific
physiology, or model-independent identity.

## 2. Dataset and graph state

The primary curated identity dimension contains exactly 166,700 neurons. The
full curated anatomical graph contains 25,582,938 directed edges and total
anatomical weight 124,177,617, where anatomical weight is synapse count.
The full graph remains the primary substrate.

The `min_synapses=5` graph is sensitivity analysis only. It contains
6,242,118 anatomical edges and total anatomical weight 89,860,280. It is not a
replacement for the full curated graph and was not used to redefine the
scientific endpoint.

For the signed Task 004 Shiu projection, the full graph has 24,904,953
resolved effective edges and 121,444,188 signed anatomical weight; 677,985
edges remain unresolved. The signed projection is a model representation and
does not alter the underlying anatomical graph counts above.

## 3. Neurotransmitter sign policy

The validated policy is the exact Task 004 `Shiu2024SignPolicy`, applied to the
resolved presynaptic identity selected by the Task 004 resolution policy:

| Resolved identity | Effective sign |
| --- | ---: |
| acetylcholine | +1 |
| gaba | -1 |
| glutamate | -1 |
| dopamine | +1 |
| octopamine | +1 |
| serotonin | +1 |
| histamine | unresolved |
| unclear, missing, or unsupported | unresolved |

Neurotransmitter resolution precedence is
`consensus_nt -> predicted_nt -> celltype_predicted_nt -> unresolved`.
An explicit `unclear` value wins its precedence position and remains
unresolved; it does not fall through to a conflicting lower-precedence value.
Unsupported labels and missing rows also remain unresolved.

Unresolved presynaptic signs are excluded from the resolved signed projection;
they are not silently assigned zero, excitation, or inhibition. The unsigned
anatomical graph is preserved. Histamine is unresolved because it is present
in MaleCNS v1.0 but absent from the inspected Shiu transmitter categories.
These are modelling assumptions, not complete receptor-level functional truth.

## 4. Reference LIF engine

The validated reference parameters are:

| Parameter | Value |
| --- | ---: |
| `v_rest` | -52.0 mV |
| `v_reset` | -52.0 mV |
| `v_threshold` | -45.0 mV, strict `v > v_threshold` |
| `tau_membrane` | 20.0 ms |
| `tau_synapse` | 5.0 ms |
| `refractory_period` | 2.2 ms |
| `synaptic_delay` | 1.8 ms |
| synaptic weight per anatomical synapse | 0.275 mV |
| timestep | 0.1 ms |

The engine uses the analytical Brian2-compatible linear update for the two
state variables, not forward Euler. For one interval of length `h`,

```text
E_m = exp(-h / tau_membrane)
E_s = exp(-h / tau_synapse)
g_next = E_s * g
v_next = v_rest + E_m * (v - v_rest) + C * g
C = (E_s - E_m) / (1 - tau_membrane / tau_synapse)
```

The equal-time-constant continuous-limit coefficient is implemented for the
general parameter case. The discrete engine applies direct writes, delayed
conductance writes, the analytical update, strict threshold/reset, and delayed
outgoing scheduling in the validated order. Refractory neurons clamp both
state variables, ignore incoming writes, and cannot threshold. The reference
direct Poisson stimulus gives its directly stimulated targets zero refractory
period, as a narrow stimulus-specific behavior.

Silencing suppresses only outgoing synaptic-event scheduling from the selected
neuron. The neuron can still receive input, update its internal state, and
spike internally. Incoming edges are not removed.

The engine was analytically and deterministically validated against the
inspected Brian2 source behavior. A live Brian2 import was not obtained in the
current Python 3.14 environment, so this checkpoint does not claim a live
Brian2 trace-equivalence result or Brian2 RNG-stream reproduction.

## 5. Published reference reproduction

Task 006 used the official Shiu v630 companion result
`results/example/sugarR_100Hz.parquet` as a read-only quantitative oracle.
Across 30 one-second trials, the official result was:

| Metric | Official Shiu reference | MaleCNS-Sim reproduction |
| --- | ---: | ---: |
| MN9 mean firing rate | 67.0333 Hz | 67.0667 Hz |
| MN9 active-trial fraction | 1.0000 | 1.0000 |
| total network spikes, mean | 9,635.7667 | 9,763.6667 |
| active neurons, mean | 354.3000 | 356.9000 |

The reproduction establishes that the independent, deterministic MaleCNS-Sim
reference engine reproduces the published experiment's MN9 mean response and
response-scale behavior closely under the declared setup. It does not establish
identity between FlyWire v630 and MaleCNS v1.0, exact Brian2 scheduling or RNG
equivalence, biological validity, or an actual-fly mechanism.

## 6. Sugar and MN9 identity

The frozen side-resolved identities are:

| Role | MaleCNS body | Wording constraint |
| --- | ---: | --- |
| MN9_L | 10331 | left readout; side-resolved correspondence |
| MN9_R | 16949 | right readout; side-resolved correspondence |

Task 007b/008a resolved the Shiu reference MN9 readout to the cross-brain
homolog `MN9_R` (body 16949). Body 10331 is retained as the ipsilateral
concurrent readout. `SIDE_RESOLVED` means an annotation-supported anatomical
side/type correspondence. It is not segmentation identity, lineage identity,
or a claim of identical bilateral physiology, and it is not selected from
dynamics.

Sugar populations were frozen before connectivity and firing interpretation:
42 left bodies and 43 right bodies. Because sugar candidates have missing
`somaSide`, the sensory-side definition uses `rootSide`. The root-side
selection establishes the sensory input side; `sugar_right -> MN9_R` is the
primary right condition, while the Shiu-aligned left-sugar reference reads the
contralateral `MN9_R`.

## 7. GPU validation

The CPU NumPy implementation remains the correctness oracle. The validated
optional CUDA backend runs float64; float32 was not used for the scientific
mode. The environment was Python 3.14.0, CuPy 14.2.0, CUDA runtime 12.9
(reported as 12090), local CUDA Toolkit 12.4.99, NVIDIA GeForce RTX 3060 with
12,288 MiB VRAM, driver 581.15, and compute capability 8.6.

CPU/CUDA validation passed synthetic and bounded real-graph checks with exact
canonical spike-event equality and stable digests. The representative Task 011
20 ms trace check also produced equal CPU/CUDA canonical spikes and result
digest `f4bfec70b46d63e5933099b3b8b81cf67d00166f7edba6d80e18c361c94dd5ff`.
The CPU remains the correctness oracle; GPU equivalence is an implementation
validation result, not an independent scientific model.

The prepared-cache and workload measurements were:

| Measurement | Recorded value |
| --- | ---: |
| effective CSR graph | 6,113,545 edges in the `>=5` GPU gate; 24,904,953 edges in the Task 008-011 full cache |
| cache serialization | 2.126 s; 23,973,200 bytes |
| warm cache load | 0.402 s |
| Task 008 full prepared representation | 998,865,328 bytes |
| Task 008 `>=5` prepared representation | 247,209,008 bytes |
| graph-only CUDA allocation | about 74 MiB |
| graph plus one-trial state/delay buffers | about 48 MiB |
| batch-30 state/delay allocation | about 1,209 MiB |
| observed real-workload CUDA memory | about 2,484 MiB |
| batch-30 throughput | 4.13 trials/s |
| 1 trial, 100 ms speedup | 4.41x |
| 1 trial, 1,000 ms speedup | 5.71x |
| 30 trials, 100 ms speedup | 30.54x |

The Task 008-011 full prepared cache fingerprint is
`8064dbec4ecf5ac72a4ab23835e4fcbdc6cdcc5315a1b71f71c135de9eb8cf4d`; its
prepared-graph fingerprint is
`d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495`.

## 8. Task 008 dynamics

The primary full-graph sweep used the 42-body left sugar population, 30
one-second trials per frequency, and 10, 25, 50, 100, 150, and 200 Hz input.
The primary readouts are contralateral MN9_R and ipsilateral MN9_L:

| Input Hz | MN9_R contralateral Hz | MN9_L ipsilateral Hz |
| ---: | ---: | ---: |
| 10 | 0.0 | 1.3 |
| 25 | 0.2 | 26.3333 |
| 50 | 0.8 | 28.8 |
| 100 | 5.9 | 66.5333 |
| 150 | 14.1 | 87.2333 |
| 200 | 20.0 | 97.6667 |

At 100 Hz, the right-sugar mirror condition produced 95.1 Hz in contralateral
MN9_L (10331) and 2.4333 Hz in ipsilateral MN9_R (16949). The left 100 Hz
condition produced 5.9 Hz in contralateral MN9_R and 66.5333 Hz in ipsilateral
MN9_L. These are the recorded mirror results, not a male/female comparison.

The aggregate-input normalization control stimulated the left population at
`100 * 21 / 42 = 50 Hz` per neuron. It produced 1.2 Hz contralateral and
26.9333 Hz ipsilateral activity and is sensitivity analysis only. The
`min_synapses=5` left-sugar, population-faithful 100 Hz sensitivity condition
produced 2.7 Hz contralateral and 68.4333 Hz ipsilateral activity. The full
curated graph remains primary.

Task 008 therefore observed MN9_L dominance in the recorded left/right
conditions, with the exact asymmetry changing by stimulus side and population.
This does not support a simple male/female reversal, and it must not be
reinterpreted as sexual dimorphism or biological causality.

## 9. Task 009 structural results

MN9_L and MN9_R had the following full-graph incoming neighborhoods:

| Measure | MN9_L | MN9_R |
| --- | ---: | ---: |
| total presynaptic neurons / edges | 278 / 278 | 137 / 137 |
| total anatomical weight | 6,012 | 556 |
| resolved-sign anatomical weight | 5,866 | 521 |
| excitatory anatomical weight | 2,956 | 257 |
| inhibitory anatomical weight | 2,910 | 264 |
| unresolved anatomical weight | 146 | 35 |

All four direct sugar-to-MN9 routes were zero: left sugar to MN9_L, left
sugar to MN9_R, right sugar to MN9_L, and right sugar to MN9_R each had zero
direct edges and zero anatomical weight.

The four full-graph two-hop summaries were:

| Route | Intermediates | Paths | Resolved / unresolved | E->E | E->I | Bottleneck | Multiplicative | Signed multiplicative |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| left -> MN9_L | 26 | 145 | 100 / 45 | 65 | 35 | 310 | 3,235 | 2,054 |
| left -> MN9_R | 7 | 54 | 29 / 25 | 17 | 12 | 63 | 263 | 93 |
| right -> MN9_L | 26 | 152 | 88 / 64 | 42 | 46 | 265 | 1,507 | -17 |
| right -> MN9_R | 11 | 94 | 68 / 26 | 47 | 21 | 98 | 685 | 330 |

The seven structural candidates were frozen, in deterministic order, as
`10135, 10313, 12752, 43765, 512730, 514753, 517861`. The Task 009 frozen
candidate fingerprint is
`113b9a767eeb61a56419e7b76e57b785fe26d9bb77e4ad6c9f6e2020be2f6ea9`.

The strongest structural MN9_L signed proxy was body 512730 at 1,904, but a
signed two-hop score is a structural ranking/diagnostic value, not a firing
predictor. Anatomical weight, sign, effective model weight, current activity,
and causal perturbational influence remain distinct quantities. Structural
analysis did not select candidates from dynamics.

## 10. Task 010 causal perturbation

Task 010 preregistered the following fixed thresholds for
`silenced_mean_hz - baseline_mean_hz`: major at least 20 Hz or 50%, moderate
at least 5 Hz or 20%, small at least 1 Hz or 5%, and negligible below both 1 Hz
and 5%. A zero baseline has null percent change and is classified by absolute
change only. These are model-sensitivity labels, not biological necessity
claims.

The 30-trial baseline replay matched the preserved Task 008 trial indices,
seeds, total spike counts, and canonical digests. Key single-candidate effects
were:

| Candidate | LEFT MN9_L change | RIGHT MN9_L change | LEFT MN9_R change | RIGHT MN9_R change |
| ---: | ---: | ---: | ---: | ---: |
| 10135 | +18.400 Hz | +9.667 Hz | +4.000 Hz | +1.800 Hz |
| 10313 | +9.633 Hz | +20.367 Hz | +3.033 Hz | +6.367 Hz |
| 12752 | -11.333 Hz | -1.367 Hz | -4.400 Hz | -2.333 Hz |
| 43765 | 0.000 Hz | 0.000 Hz | 0.000 Hz | 0.000 Hz |
| 512730 | -1.533 Hz | -0.033 Hz | -0.233 Hz | 0.000 Hz |
| 514753 | 0.000 Hz | 0.000 Hz | 0.000 Hz | 0.000 Hz |
| 517861 | -3.100 Hz | +5.600 Hz | 0.000 Hz | +0.567 Hz |

The all-seven intervention increased MN9_L from 66.5333 to 80.0333 Hz for
left sugar and from 95.1 to 106.1333 Hz for right sugar. It also changed
network-wide activity substantially: total spikes increased by 39,033 for left
sugar and 144,920 for right sugar, with corresponding increases in active
neurons and delivered events. Thus the joint result is a broad-network
perturbation, not a selective MN9 mechanism.

The strongest structural candidate, 512730, had only a small left MN9_L effect
(-1.533 Hz) and negligible right MN9_L effect (-0.033 Hz). Candidates 43765
and 514753 were exact nulls under the recorded schedules. The structural
prominence versus model causal influence mismatch is a result, not a reason to
revise the frozen candidate set. The Task 010 result digest is
`20f8d8f6432070625a9ca6a4ddb32b2cc0a68f380102dbd3ee5e35bbcc578e45`.

## 11. Task 011 temporal mechanism audit

Task 011 used only the five frozen cases `10313`, `10135`, `12752`, `512730`,
and `43765`, with fixed trial indices 0, 10, and 20 for both 100 Hz stimulus
sides. The accepted classifications are exactly:

| Candidate | LEFT | RIGHT |
| ---: | --- | --- |
| 10313 | `NETWORK_REDISTRIBUTION_COMPATIBLE` | `NETWORK_REDISTRIBUTION_COMPATIBLE` |
| 10135 | `NETWORK_REDISTRIBUTION_COMPATIBLE` | `MIXED` |
| 12752 | `MIXED` | `MIXED` |
| 512730 | `NETWORK_REDISTRIBUTION_COMPATIBLE` | `UNRESOLVED` |
| 43765 | `UNRESOLVED` | `UNRESOLVED` |

The audit supports the following model-level interpretation:

- A small early divergence can precede broad recurrent expansion.
- 10313 does not support a simple direct-inhibition explanation.
- 10135 RIGHT retains short-path-compatible evidence but also recurrent
  expansion, hence `MIXED`.
- 512730 RIGHT had zero baseline candidate activity, so its classification is
  `UNRESOLVED` rather than evidence of a silent causal route.
- 43765 never spiked or transmitted in either fixed condition.
- Network redistribution is a model-compatible mechanism classification, not
  biological proof.

The Task 011 result digest accepted for this checkpoint is
`fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`.

## 12. Current strongest scientific conclusion

Within the validated MaleCNS-Sim LIF model, anatomical prominence and short-path
structure do not consistently predict perturbational influence on MN9_L. The
strongest counterintuitive perturbation effects examined in Task 011 are
predominantly compatible with recurrent/network redistribution, with short-path
contributions retained in some candidate/stimulus conditions.

This is a model-level conclusion only. It is not a biological causal claim and
does not claim an actual-fly mechanism.

## 13. Reproducibility ledger

### Important task commits

| Task | Commit |
| --- | --- |
| 004 signed connectome policy | `394ba2010fe44d1258302e8c0eced604714b227b` |
| 005 reference LIF engine | `1cc860a9b0cd5e7ada4ec0e646184f1160eeff` |
| 006 Shiu reproduction | `d9b55c378ebdfb651020232fa6d970721168bed7` |
| 007 MN9 mapping/laterality foundation | `390d885b88bc39d1a7a127c87f9c58f179080577`, `3683dc963274efa1c910e224aca4d473f847bb97`, `78d5bd721c04c6d6dd6ad406676e95dd1b138030` |
| 007c GPU backend | `c977108ff42eb6c18aaee0ce626625bacd53a6b6` |
| Windows parquet baseline repair | `3336162c902a40a7bfd86624ef8d08bb4f064015` |
| 008 dynamics comparison | `f22e7c7cf0a7e1d0799321cc3ceb8329099e9e3e` |
| 008a laterality audit | `df48a1f3d6aa519a136e0fddb6b10d08dbf316f6` |
| 009 structural asymmetry | `25286228cf050928fc7534a1603ed388d48d1053` |
| 010 frozen-candidate perturbation | `fe4048726641a99b3cf9ed33aec406d50700f489` |
| 011 temporal mechanism audit | `ae589a9b9726fa2510fff8f32658bc02176f66a3` |

Task 009 frozen candidate fingerprint:
`113b9a767eeb61a56419e7b76e57b785fe26d9bb77e4ad6c9f6e2020be2f6ea9`.

Task 010 result digest:
`20f8d8f6432070625a9ca6a4ddb32b2cc0a68f380102dbd3ee5e35bbcc578e45`.

Task 011 accepted result digest:
`fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`.

The Task 012 expected test baseline is `183 passed, 1 skipped`. The Python
environment is Python 3.14.0 with pytest 9.1.1 under `uv`; the optional GPU
environment is CuPy 14.2.0 with CUDA runtime 12.9 and the RTX 3060 setup
recorded in Section 7. CUDA float64 is validated; float32 is not the scientific
mode.

Derived scientific artifacts under `data/derived/` are ignored by Git and are
kept separate from tracked source and documentation. Task 010 and Task 011
artifacts have their own namespaces; Task 008 was not overwritten. Task 012
does not regenerate, rewrite, or normalize any scientific-result artifact.

## 14. Open scientific questions

These are unresolved questions, not Task 013 proposals:

- What is the biological validity, if any, of the model-level
  network-redistribution mechanisms?
- What biological or anatomical process gives rise to the observed MN9_L
  anatomical asymmetry?
- Does recurrent divergence correspond to experimentally identifiable motifs?
- How robust are these model-level results under independently justified
  alternative neuron and synapse models?

## 15. Project stopping point

Task 011 is the current completed scientific endpoint. Task 012 is a
documentation and reproducibility closure task only. No new perturbation study,
candidate discovery, model change, or scientific hypothesis is authorized by
Task 012. Task 013 must not be started automatically; based on this checkpoint,
no Task 013 is scientifically justified without a separately authorized scope,
pre-registered question, and independent rationale.
