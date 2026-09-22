# Task 009 - MN9 Left/Right Structural Asymmetry Analysis

Status: COMPLETE on 2026-09-21. This task is structural-connectome analysis only. It
does not run LIF dynamics, perturbations, stimulation, sign changes, weight
tuning, or candidate selection from firing results.

## Scope and baseline gate

Task 009 requires the committed Task 008 and Task 008a work, branch `master`,
and a clean worktree. The starting HEAD is recorded in the completion section
after analysis. The paused Task 008 stash is not used or modified.

The required baseline command is:

```text
uv run python -m pytest -q
```

## Validated identities frozen before graph analysis

Task 008a establishes `VALID_AS_RUN`, with `rootSide` as the source-supported
sensory-side field. The exact existing Task 008 populations remain frozen:

| population | count | fingerprint |
| --- | ---: | --- |
| left sugar | 42 | `8b1c625ddf719e5853d409223d88b8c997a1fdcffb298210965b0402efce49c7` |
| right sugar | 43 | `2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b` |

The readout IDs are frozen as `MN9_L=10331` and `MN9_R=16949`. These are the
Task 007b side-resolved laterality/type correspondences; the analysis does not
promote them to segmentation identity or identical physiology.

## Method

The primary graph is the full curated neuron-level graph. All measurements are
computed independently on:

1. the unsigned anatomical graph, where edge weights are synapse counts; and
2. the Task 004 Shiu-compatible signed graph, where a presynaptic sign is a
   model-policy assignment and unresolved signs remain unresolved.

The analysis uses sparse NumPy grouping and joins. It does not materialize an
individual Python object for every two-hop path. For each intermediate it
retains contributing sugar-edge groups, target-edge groups, sign products, and
transparent structural aggregates.

The two-hop diagnostics are explicitly proxies, not current, firing
probability, or causal effect:

- path count;
- bottleneck sum of `min(w1, w2)` over structural edge pairs;
- anatomical multiplicative sum `w1*w2`; and
- signed multiplicative sum `sign1*sign2*w1*w2` for resolved-sign pairs.

The `min_synapses=5` graph is a later sensitivity analysis. Full graph results
remain primary. No dynamics dependency is permitted in the Task 009 analysis
module or offline tests.

## Planned result sections

The final record will report the Task 008 observation and Task 008a validation,
population/readout fingerprints, direct sugar-to-MN9 measurements, complete
MN9 incoming neighborhoods, first-hop partitions, all four exact two-hop
routes, E/I route composition, independent top-intermediate rankings,
annotation-supported homolog pairs, source-normalized controls, threshold
sensitivity, official dimorphism metadata, structural interpretation and
nonclaims, and a frozen small Task 010 candidate list. The analysis and its
fingerprints will be run twice and must match exactly.

## 1. Task 008 observation and Task 008a validation

Task 008 measured the following 100 Hz means:

| input | MN9_L | MN9_R |
| --- | ---: | ---: |
| left sugar | 66.53 Hz | 5.90 Hz |
| right sugar | 95.10 Hz | 2.43 Hz |

Task 008a independently validated the source populations as `VALID_AS_RUN`:
the side field is `rootSide`, with 42 left and 43 right sugar bodies. No LIF
result was used in Task 009 to select a population, readout, or explanation.

## 2. Baseline, frozen populations, and readouts

The starting branch was `master`, the worktree was clean, and Tasks 008 and
008a were committed. Starting HEAD was:

```text
df48a1f3d6aa519a136e0fddb6b10d08dbf316f6
```

Baseline:

```text
uv run python -m pytest -q
155 passed, 1 skipped in 5.85s
```

The exact frozen populations were not altered:

| population | count | fingerprint |
| --- | ---: | --- |
| left sugar | 42 | `8b1c625ddf719e5853d409223d88b8c997a1fdcffb298210965b0402efce49c7` |
| right sugar | 43 | `2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b` |

Readouts were frozen as `MN9_L=10331` and `MN9_R=16949`. These remain
side-resolved laterality/type correspondences, not segmentation identity or a
claim of identical bilateral physiology.

## 3. Graph representations and direct connectivity

The primary graph is the full curated neuron graph. Anatomical weights are
synapse counts. Signed metrics use the Task 004 `Shiu2024SignPolicy`; signs
are assigned by presynaptic neuron, and unresolved signs are retained in
unsigned totals but excluded from resolved signed sums. The `min_synapses=5`
graph is sensitivity-only.

All four direct routes were empty:

| route | direct edges | anatomical weight | signed positive | signed negative | contributing sugar bodies |
| --- | ---: | ---: | ---: | ---: | ---: |
| left sugar -> MN9_L | 0 | 0 | 0 | 0 | 0 |
| left sugar -> MN9_R | 0 | 0 | 0 | 0 | 0 |
| right sugar -> MN9_L | 0 | 0 | 0 | 0 | 0 |
| right sugar -> MN9_R | 0 | 0 | 0 | 0 | 0 |

This reconfirms Task 007's no-direct-edge result against the frozen Task 008a
populations.

## 4. MN9 incoming neighborhoods

The complete incoming neighborhoods show a large bilateral anatomical
embedding difference, while each readout has both excitatory and inhibitory
inputs under the Task 004 policy:

| measure | MN9_L | MN9_R |
| --- | ---: | ---: |
| total presynaptic neurons | 278 | 137 |
| total input edges | 278 | 137 |
| total anatomical weight | 6,012 | 556 |
| resolved-sign presynaptic neurons | 249 | 126 |
| resolved-sign anatomical weight | 5,866 | 521 |
| excitatory presynaptic neurons | 126 | 70 |
| inhibitory presynaptic neurons | 123 | 56 |
| excitatory anatomical weight | 2,956 | 257 |
| inhibitory anatomical weight | 2,910 | 264 |
| unresolved presynaptic neurons | 29 | 11 |
| unresolved anatomical weight | 146 | 35 |

Normalized by total anatomical input weight, MN9_L is 49.17% excitatory,
48.40% inhibitory, and 2.43% unresolved. MN9_R is 46.22% excitatory,
47.48% inhibitory, and 6.29% unresolved. Thus MN9_R does not have stronger
absolute inhibition; it has much weaker absolute excitation and inhibition,
with a slightly more inhibitory resolved balance after unresolved input is
excluded.

Neurotransmitter composition by incoming edge count and anatomical weight was:

| transmitter | MN9_L count / weight | MN9_R count / weight |
| --- | ---: | ---: |
| acetylcholine | 126 / 2,956 | 70 / 257 |
| GABA | 90 / 2,713 | 48 / 247 |
| glutamate | 33 / 197 | 8 / 17 |
| histamine | 2 / 10 | 1 / 1 |
| unresolved | 27 / 136 | 10 / 34 |

The highest-weight MN9_L input types were `DNge062`, `GNG015`, `GNG120`,
`GNG117`, and `GNG095`. For MN9_R they were `GNG095`, `DNge062`, `GNG130`,
`GNG015`, and `GNG234`.

## 5. First-hop sugar targets

On the full anatomical graph, both sugar populations had 459 unique first-hop
targets. They shared 223 targets, with 236 left-only and 236 right-only
targets. The side-specific edge and weight partition was:

| target partition | left edges / weight | right edges / weight |
| --- | ---: | ---: |
| shared | 1,939 / 11,472 | 2,128 / 13,830 |
| left-only | 936 / 2,925 | 0 / 0 |
| right-only | 0 / 0 | 1,017 / 3,551 |
| total | 2,875 / 14,397 | 3,145 / 17,381 |

All observed first-hop negative signed weight was zero. Resolved positive
weight was 14,395 for left and 17,356 for right; unresolved weight was 2 and
25 respectively. The resolved-target counts were 459 for left and 458 for
right (one right anatomical target is supported only by unresolved-sign
edges). Shared target count alone is therefore not treated as functional
equivalence.

## 6. Exact two-hop decomposition and structural proxies

Each two-hop route was aggregated by intermediate without materializing one
Python object per path. The full-graph results are:

| route | intermediates | paths | resolved / unresolved | positive / negative | E->E | E->I | I->E | I->I | bottleneck | multiplicative | signed multiplicative |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| left -> MN9_L | 26 | 145 | 100 / 45 | 65 / 35 | 65 | 35 | 0 | 0 | 310 | 3,235 | 2,054 |
| left -> MN9_R | 7 | 54 | 29 / 25 | 17 / 12 | 17 | 12 | 0 | 0 | 63 | 263 | 93 |
| right -> MN9_L | 26 | 152 | 88 / 64 | 42 / 46 | 42 | 46 | 0 | 0 | 265 | 1,507 | -17 |
| right -> MN9_R | 11 | 94 | 68 / 26 | 47 / 21 | 47 | 21 | 0 | 0 | 98 | 685 | 330 |

The three proxy columns are purely structural ranking/diagnostic values:
`min(w1,w2)` summed over paths, `w1*w2` summed over paths, and the signed
product for resolved-sign paths. They are not current, firing probability,
or causal effect. The E/I table shows that resolved sugar-edge signs are
effectively excitatory; inhibition enters through E->I second edges. There
were no resolved I->E or I->I two-hop paths in these four routes.

## 7. Top intermediates and metadata

Rankings were kept independent rather than collapsed into an opaque score. The
following are the top five IDs for each metric; the JSON report retains body
ID, type, instance, side, superclass, class, neurotransmitter, and dimorphism
metadata for every listed intermediate.

| route | sugar input weight | MN9 outgoing weight | bottleneck | absolute signed proxy |
| --- | --- | --- | --- | --- |
| left -> MN9_L | 512730, 12230, 43293, 12808, 10135 | 12752, 10673, 32102, 514753, 556717 | 512730, 12230, 12808, 10135, 514753 | 512730, 10135, 514753, 12752, 556717 |
| right -> MN9_L | 12808, 43293, 10557, 12230, 15450 | 12364, 10673, 43765, 32102, 530560 | 12808, 12230, 10557, 15450, 10313 | 10313, 12364, 15450, 43293, 11582 |
| left -> MN9_R | 12230, 517861, 12807, 12422, 521748 | 12752, 10673, 12422, 12230, 12807 | 12230, 12422, 517861, 12807, 521748 | 12422, 517861, 12807, 12752, 10673 |
| right -> MN9_R | 556512, 12230, 517861, 10313, 12807 | 43765, 10673, 12364, 512751, 10313 | 556512, 12230, 517861, 10313, 12807 | 556512, 43765, 517861, 10313, 12807 |

The strongest single signed structural support for MN9_L is the left
`GNG089_L` body `512730` (signed proxy 1,904), followed by `DNge031_L`
`10135` (-190), `GNG568_L` `514753` (144), `DNge080_L` `12752` (101), and
`GNG538_L` `556717` (99). The strongest MN9_R signed routes include
`GNG089_R` `556512` (+418) and inhibitory `GNG095_R` `43765` (-55),
`GNG041_R` `517861` (-50), and `DNge031_R` `10313` (-36).

## 8. Homolog-pair comparison

Homologs were not fabricated. The analysis retained 30 pairs only when the
annotation supplied the same type, superclass, class, and a unique `_L`/`_R`
instance suffix pair. It recorded left-sugar input to the left member,
right-sugar input to the right member, both members' weights to each MN9, and
the observed sign sets.

Examples show why bilateral pairing does not imply equal routing. `GNG089`
(`512730`/`556512`) receives left/right sugar weights 272/418 but sends 7/0
anatomical weight to MN9_L and 0/1 to MN9_R. `GNG095`
(`12851`/`43765`) sends 351/26 to MN9_L and 4/55 to MN9_R, with both paired
outputs inhibitory. `DNge080` (`12752`/`12364`) is comparatively similar:
101/96 to MN9_L and 13/9 to MN9_R, both excitatory. These are within-male
left/right structural differences, not evidence of male/female dimorphism.

## 9. Source-side normalization

Task 008a measured 2,873 resolved outgoing edges and 14,397 anatomical weight
for left sugar, versus 3,132 resolved edges and 17,381 anatomical weight for
right sugar. The full structural run retains the corresponding total edge
counts of 2,875 and 3,145 including unresolved edges.

The source-normalized controls were:

| route | bottleneck / sugar body | multiplicative / sugar body | signed / sugar body | signed / sugar outgoing weight |
| --- | ---: | ---: | ---: | ---: |
| left -> MN9_L | 7.381 | 77.024 | 48.905 | 0.142669 |
| left -> MN9_R | 1.500 | 6.262 | 2.214 | 0.006460 |
| right -> MN9_L | 6.163 | 35.047 | -0.395 | -0.000978 |
| right -> MN9_R | 2.279 | 15.930 | 7.674 | 0.018986 |

The right source has more outgoing anatomical material, so source size alone
cannot explain MN9_L dominance. Even after source normalization, left sugar
routes to MN9_L remain much stronger than right sugar routes to MN9_L.

## 10. `min_synapses=5` sensitivity

The threshold sensitivity preserved the qualitative target asymmetry:

| target | total incoming weight (full / >=5) | excitatory weight (full / >=5) | inhibitory weight (full / >=5) | presynaptic count (full / >=5) |
| --- | ---: | ---: | ---: | ---: |
| MN9_L | 6,012 / 5,699 | 2,956 / 2,805 | 2,910 / 2,792 | 278 / 93 |
| MN9_R | 556 / 386 | 257 / 161 | 264 / 203 | 137 / 27 |

Thresholded route results were:

| route | intermediates | paths | bottleneck | multiplicative | signed |
| --- | ---: | ---: | ---: | ---: | ---: |
| left -> MN9_L | 5 | 21 | 127 | 2,113 | 1,668 |
| left -> MN9_R | 0 | 0 | 0 | 0 | 0 |
| right -> MN9_L | 2 | 12 | 60 | 470 | 0 |
| right -> MN9_R | 0 | 0 | 0 | 0 | 0 |

The full graph remains primary. The threshold graph reduces weak two-hop
routes, but retains a much stronger left-sugar -> MN9_L path structure than
right-sugar -> MN9_L. The strongest threshold identities for left -> MN9_L
were `512730`, `10135`, `12230`, `12808`, and `556717`; right -> MN9_L
retained `12808` and `12230`.

## 11. Dimorphism metadata

The official MaleCNS annotation `dimorphism` field was inspected for all
important intermediates. Every important local row was null and therefore
classified `unresolved`; none was classified `isomorphic`, `dimorphic`, or
`male-specific` from that field. Existing official FlyWire type evidence marks
the sugar LB3 and MN9 CB0701 types as isomorphic, but that type-level result
does not classify the within-male intermediate asymmetry as sexual dimorphism.

## 12. Structural interpretation and competing explanations

The best-supported structural explanation is a combination of B and C, with a
contribution from A but not enough to account for the result alone:

1. MN9_L has approximately 10.8 times MN9_R's total incoming anatomical
   weight, and substantially more excitatory and inhibitory input in absolute
   terms.
2. Left sugar has fewer source neurons and less outgoing anatomical weight,
   yet its two-hop route to MN9_L has signed proxy 2,054 versus -17 for the
   right-sugar route. This is downstream routing, not source-population size.
3. The left -> MN9_L route has 145 paths and 26 intermediates, versus 152 and
   26 for right -> MN9_L, so path count alone is not the explanation. Weight
   concentration and signs are important: `GNG089_L` contributes signed proxy
   1,904.
4. D is present as route sign composition: left -> MN9_L is 65 E->E and 35
   E->I, while right -> MN9_L is 42 E->E and 46 E->I. MN9_R is not exposed to
   stronger absolute inhibition overall; its absolute excitatory and
   inhibitory incoming weights are both much smaller.
5. E is a descriptive possibility at the bilateral cell level because paired
   homologs can have different weights and target routing, but local
   dimorphism metadata does not support a sexual-dimorphism claim.
6. F is supported: a small number of high-weight intermediates, especially
   `512730`, dominate transparent independent rankings. This is a structural
   concentration hypothesis, not a causal claim.

No single two-hop proxy is a firing prediction, and no proxy was selected by
or calibrated to the Task 008 firing rates.

## 13. Frozen Task 010 candidate list

Before any perturbation simulation, the following seven bodies were frozen by
structural rules only: the top five absolute signed-proxy intermediates for
MN9_L across both source sides, unioned with the top five negative signed
proxy intermediates on MN9_R routes, with deterministic ID ordering and
duplicates removed:

| body ID | structural reason | signed proxy values |
| ---: | --- | --- |
| 10135 | top absolute signed support for MN9_L | left->L -190 |
| 10313 | MN9_L support and negative MN9_R route | right->L -108; right->R -36 |
| 12752 | top absolute signed support for MN9_L | left->L 101; left->R 13 |
| 43765 | negative MN9_R route | right->L -26; right->R -55 |
| 512730 | top absolute signed support for MN9_L | left->L 1,904 |
| 514753 | top absolute signed support for MN9_L | left->L 144 |
| 517861 | negative MN9_R route | left->R -49; right->R -50 |

No candidate was silenced, stimulated, or selected using a dynamics result.

## 14. Determinism and fingerprints

All IDs and rankings use explicit numeric ID tie breakers. The final run
performed the analysis twice on the same immutable loaded representations and
required identical repeat fingerprints:

| fingerprint | value |
| --- | --- |
| analysis configuration | `2eff9e8a0336861ee723560a4db3d77c0ede57f717497b338b604227bb033373` |
| frozen sugar populations | `2ad1dd72506f0a8e137077078850d9cbd9da34d118b6f45537a5a4aba837d4e4` |
| MN9 readouts | `7deb18ff1028a49d5c19fce462b106f95e2d38bbc472798bfebdf68ca618aa26` |
| two-hop aggregate table | `ff9fd2073370c1be15b9b94fd8f2c1442ea3da8a5bf18934c002968df117a073` |
| frozen Task 010 list | `113b9a767eeb61a56419e7b76e57b785fe26d9bb77e4ad6c9f6e2020be2f6ea9` |
| full graph unsigned | `fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4` |
| full graph signed | `861f07218122e122383d8465b30e65f5eb1d5b11a474b767a6312b3115ecaf25` |
| >=5 graph unsigned | `661a07e346541da75e81fa0eac487102af496fcfc9f6bdc743c9ca957b4f4a74` |
| >=5 graph signed | `0367327291c21f6154c4d4253a7673acd11b045fa43114d4a611b0a12ce1c85d` |

Repeat status was `identical=true`. The repeated full-report fingerprint was
`11d2f408fd70d56ae7c7d6e45b19c6ca8efb9db13b6305d3b1a609d5665fa3e8` and the
repeated threshold-report fingerprint was
`3bbc6bb26a705f93e0bc4c469804a3b09c851ddde3cc83e6cd0bfc592bc4204b`.

## 15. Limitations and nonclaims

- Structural proxies are not current, firing probability, causal effect, or a
  substitute for a nonlinear LIF experiment.
- Anatomical synapse count, Task 004 sign, and effective signed model weight
  remain distinct. Unresolved signs are not silently assigned.
- A two-hop route does not establish that an intermediate drives MN9 in a
  dynamical experiment.
- Type/instance pairing is an annotation-supported representation only; it is
  not a cross-sex lineage or segmentation identity claim.
- Within-male left/right asymmetry is not sexual dimorphism. The local
  dimorphism metadata for important intermediates was unresolved.
- The Task 010 list is frozen for a later causal experiment and must not be
  expanded or reordered from post-perturbation results.

## 16. Implementation and validation

Added:

- `src/malecns_sim/analysis/task009.py` for sparse/vectorized unsigned and
  signed structural analysis, deterministic rankings, homolog comparisons,
  source normalization, threshold sensitivity, metadata classification, and
  candidate freezing;
- `tests/test_task009.py` with 10 offline tests covering incoming
  decomposition, first-hop partitions, two-hop aggregation, sign classes,
  all three proxies, ranking ties, homolog representation, normalization,
  threshold sensitivity, candidate freezing, and absence of dynamics imports;
- `scripts/run_task009.py` for the real-data run and ignored JSON artifact;
- this plan/report.

Validation completed:

```text
uv run python -m compileall src scripts       PASS
uv run python -m pytest -q                    165 passed, 1 skipped
uv run python -m pytest -v                    PASS (same 165 passed, 1 skipped)
git diff --check                              PASS
```

The full suite includes the 10 new Task 009 tests. The one skip remains the
pre-existing bounded CUDA real-graph gate. No commit, push, or tag was made.
The paused Task 008 stash was not used or modified.
