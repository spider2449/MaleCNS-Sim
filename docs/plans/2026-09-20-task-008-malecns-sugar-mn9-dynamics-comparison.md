# Task 008 - MaleCNS Sugar-to-MN9 Dynamics Comparison

Status: COMPLETE on 2026-09-21. This record is intentionally uncommitted for
review; Task 008 implementation and measured validation are complete.

## 1. Task 007b identity boundary

The Shiu-aligned reference input is anatomical left sugar GRNs and the
contralateral anatomical right MN9. Task 007b independently resolved the
FlyWire CB0701 reference `720575940660219265` to the side-resolved MaleCNS
cross-brain homolog `16949 = MN9_R`. `10331 = MN9_L` is retained as the
ipsilateral concurrent readout. This is `SIDE_RESOLVED`, not segmentation
identity, and neither identity is selected from dynamics.

## 2. Laterality gate

The existing Task 007 predicate is applied twice with only anatomical side
changed:

```text
flywireType == LB3
and superclass == cb_sensory
and class == gustatory
and entryNerve == MxLbN
and rootSide == requested anatomical side
```

The side field is `rootSide` because the sugar candidates have missing
`somaSide`. The measured left population is established before connectivity
or firing results are considered. `sugar_right -> MN9_R` is forbidden as the
primary condition.

## 3. Frozen populations

Measured identities are recorded below after the full-data run. The existing
right population and its Task 007 fingerprint must remain unchanged.

| population | count | fingerprint |
| --- | ---: | --- |
| `sugar_left` | 42 | `8b1c625ddf719e5853d409223d88b8c997a1fdcffb298210965b0402efce49c7` |
| `sugar_right` | 43 | `2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b` |

## 4. Population reports

The final report includes body IDs, type/flywireType, soma/root side,
superclass/class, receptor/nerve/neuromere/dimorphism metadata, Task 004
resolved and unresolved NT counts, signed outgoing-edge coverage, excluded
outgoing edges, and anatomical outgoing weight. No population is downsampled.

## 5. Population size versus Shiu

Shiu v630 stimulated 21 GRNs. MaleCNS population-faithful trials stimulate
every defensibly mapped candidate on that side at the requested per-neuron
rate. The optional normalized control uses `rate * 21 / N` and is interpreted
only as aggregate-input sensitivity, not as the biologically preferred
condition.

## 6. Simulation configuration

The primary substrate is the Task 003 full curated neuron graph and the sign
policy is the Task 004 `Shiu2024SignPolicy`. Task 005 reference parameters are
used unchanged: `v_rest=-52 mV`, `v_reset=-52 mV`, `threshold=-45 mV`,
`tau_membrane=20 ms`, `tau_synapse=5 ms`, `refractory=2.2 ms`,
`delay=1.8 ms`, `weight=0.275 mV * signed anatomical count`, and `dt=0.1 ms`.

## 7. Unresolved signs

Unresolved presynaptic signs remain excluded from the prepared projection.
Externally stimulated candidates still receive direct Poisson input, but their
unresolved outgoing edges do not acquire a sign. Reports distinguish resolved
and excluded outgoing edge counts and weights.

## 8. Preparation and reuse

Static loading, Task 003 projection, Task 004 resolution/sign projection, and
Task 005 effective projection occur once per graph/policy configuration.
Each trial creates fresh membrane, conductance, refractory, delayed-event,
and stimulus state while reusing the immutable prepared projection. Preparation
time, memory, graph loading, trial timing, and delivered synaptic events are
recorded separately.

## 9. Primary sweep

`sugar_left` is stimulated at 10, 25, 50, 100, 150, and 200 Hz for 30
one-second trials per frequency. Each trial records both MN9 readouts, total
spikes, active neurons, input events, queued/delivered synaptic events, and a
result digest.

## 10. Primary contra/ipsi results

Measured with CUDA float64, the full curated graph, the persisted prepared
cache, 30 trials per frequency, and 1000 ms per trial:

| frequency Hz | MN9_R contralateral Hz | MN9_L ipsilateral Hz |
| ---: | ---: | ---: |
| 10 | 0.0 | 1.3 |
| 25 | 0.2 | 26.3333 |
| 50 | 0.8 | 28.8 |
| 100 | 5.9 | 66.5333 |
| 150 | 14.1 | 87.2333 |
| 200 | 20.0 | 97.6667 |

The primary experiment fingerprint is
`7ebd96522154f09ffa6e913ca0db17c366fe8a1fa7901aa52f28138e10039ef2`.

## 11. Task 006 comparison

The fixed reference curve is 0, 0, 22.03, 67.4, 82.57, and 93.13 Hz at the
six frequencies. Descriptive differences, rank association, and normalized
curve shape are reported without parameter optimization. The measured
Spearman association is 1.0. Measured primary-minus-reference differences are
0.0, 0.2, -21.23, -61.50, -68.47, and -73.13 Hz.

## 12. Mirror result

The mirror condition uses `sugar_right` at 100 Hz for 30 trials and reads
`10331 = MN9_L` contralaterally and `16949 = MN9_R` ipsilaterally. The measured
means are 95.1 Hz contralateral and 2.4333 Hz ipsilateral.

## 13. Aggregate-input-normalized result

The primary left population is also run with per-neuron rate `100 * 21 / N`
(`N=42`, therefore 50 Hz), for 30 trials. The measured means are 1.2 Hz
contralateral and 26.9333 Hz ipsilateral. This is a sensitivity control only.

## 14. `min_synapses=5` sensitivity

The full graph remains primary. One left-sugar, population-faithful, 100 Hz,
30-trial condition was run on the Task 003 `min_synapses=5` graph. The
measured means are 2.7 Hz contralateral and 68.4333 Hz ipsilateral as a
structural-threshold sensitivity analysis.

## 15. Runtime and memory

The full graph contains 166700 neurons and 24904953 effective edges. Its
prepared representation uses 998865328 bytes and took 282.80 seconds to
load and prepare. The `min_synapses=5` graph contains 6113545 effective edges,
uses 247209008 bytes, and took 267.51 seconds to load and prepare. The
primary sweep took 541.21 seconds; repeat, mirror, normalized, and threshold
conditions took 90.08, 90.60, 91.26, and 85.19 seconds respectively.

Prepared caches are retained at `data/derived/task008/full-prepared-graph.npz`
and `data/derived/task008/min-synapses-5-prepared-graph.npz`.

## 16. Deterministic fingerprints

The implementation fingerprints both populations, the experiment definition,
prepared graph, primary sweep, mirror condition, normalized condition, and
threshold sensitivity. Seeds hash experiment identity, side, frequency, trial
index, graph fingerprint, and sign-policy fingerprint. The 30-trial 100 Hz
repeat has identical canonical result digest, MN9 trial rates, total spike
counts, and all 30 trial digests.

## 17. Hypothesis evaluation

The preregistered qualitative hypotheses are: increasing unilateral sugar
frequency generally increases contralateral MN9 activity, and contralateral
MN9 activity exceeds ipsilateral activity. The outcome is reported as both,
one, or neither; disagreement is a biological/data result unless engineering
checks fail.

## 18. Scientific limitations and nonclaims

`16949` is a side-resolved cross-brain homolog, not segmentation identity.
MaleCNS candidates are homologous population candidates, not the 21 FlyWire
segments. Male/female connectivity and annotation can differ. Absolute rate
agreement is not expected. Poisson input is a model intervention,
neurotransmitter sign is a model policy, and synaptic count times 0.275 mV is
a Shiu model assumption. No behavior or proboscis extension is simulated.
Disagreement is not tuned away.

## 19. Validation and nonclaims

`uv run python -m compileall src scripts` passed. `uv run python -m pytest -v`
passed with 148 tests passed and 1 expected CUDA real-graph test skipped.
`git diff --check` passed. The bounded 2-trial, 20 ms CPU/GPU preflight used
identical pre-generated schedules and passed exact canonical spike-event
equality. No commit, push, or tag is part of Task 008; the named Task 008
stash remains preserved for review.
