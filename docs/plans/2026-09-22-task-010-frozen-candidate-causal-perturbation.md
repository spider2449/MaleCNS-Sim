# Task 010 - Frozen-Candidate Causal Perturbation of MN9 Asymmetry

Status: IN PROGRESS. This plan is the preregistered Task 010 record. The
candidate set and effect thresholds below are frozen before reading Task 010
perturbation outcomes.

## Scope and hard gates

Task 010 tests dynamics in the validated MaleCNS-Sim LIF model. It starts from
Task 009 commit `2528622` and requires a clean `master` worktree, passing
baseline tests, the prepared Task 008 full graph cache, and an available RTX
3060 CUDA float64 backend. No commit, push, tag, Task 008 overwrite, graph
change, population change, parameter change, sign-policy change, or seed change
is allowed.

The only intervention is suppression of outgoing synaptic transmission from a
frozen candidate neuron. The neuron still receives input, updates its internal
state, and may spike internally. This is the existing Task 005 silencing
semantics: only scheduling of its outgoing synaptic events is suppressed.

## Frozen provenance

The frozen Task 009 candidates are exactly, in this order:

`10135, 10313, 12752, 43765, 512730, 514753, 517861`

The list is read from the committed Task 009 result artifact and checked
against this literal tuple. Task 010 does not derive or revise it from
perturbation results. The readouts remain `MN9_L=10331` and `MN9_R=16949`.
The Task 008a sugar populations remain the existing 42-body left population
and 43-body right population with their recorded fingerprints.

The manifest records body ID, type, instance, side, superclass, class,
neurotransmitter, homolog information when available, and all matching Task
009 structural route metrics. Its deterministic fingerprint is recorded in
the completion section.

## Preregistered thresholds

For a readout, define the signed change as `silenced_mean_hz - baseline_mean_hz`
and the absolute change as its absolute value. For a nonzero baseline, percent
change is `100 * signed_change / abs(baseline_mean_hz)`. If the baseline is
zero, percent change is explicitly `null` and classification uses the absolute
change threshold only.

Classification uses the highest category whose absolute or percent threshold is
met:

| category | absolute change | absolute percent change |
| --- | ---: | ---: |
| major | at least 20 Hz | at least 50% |
| moderate | at least 5 Hz | at least 20% |
| small | at least 1 Hz | at least 5% |
| negligible | below 1 Hz and below 5% |

These labels describe model sensitivity only. They are not biological
necessity claims. The thresholds will not be adjusted after results are seen.

## Execution protocol

1. Record starting HEAD and run `uv run python -m pytest -q`.
2. Build and fingerprint the frozen candidate manifest.
3. Reuse the Task 008 full prepared graph, exact 100 Hz left/right schedules,
   30 trials, 1000 ms duration, `dt=0.1 ms`, Task 005 parameters, and the
   existing Task 008 seed derivation. Baseline replay must match the preserved
   Task 008 trial readouts, total spikes, and canonical spike digests exactly.
   An unexpected mismatch stops Task 010 before interpretation.
4. Run one bounded candidate-silenced CPU/GPU float64 preflight on identical
   schedules and require exact canonical spike-event equality.
5. Run each of the seven candidates independently for left and right sugar.
   Then run the single preregistered all-seven condition for left and right
   sugar. The graph and uploaded CUDA CSR arrays are reused.
6. Calculate raw MN9 rates, rate changes, percent changes, network-wide totals,
   paired trial deltas, and the bounded asymmetry metric
   `(MN9_L - MN9_R) / (MN9_L + MN9_R)`, with a zero denominator represented as
   `null`.
7. Repeat one strong-effect candidate condition, one negligible-effect
   candidate condition when available, and both all-seven conditions with the
   identical schedules. Require identical trial rates, canonical digests, and
   result digests. Repeat selection does not alter the frozen intervention set.
8. Write the Task 010 artifact atomically under its own derived namespace.

Thirty deterministic trials are paired model runs, not biological replicates.
Paired summaries are descriptive; p-values are not the primary conclusion.

## Required outcome record

The completed section will report baseline replay, preflight, all seven
single-candidate outcomes for both stimulation sides, paired summaries,
MN9_L/MN9_R rankings, asymmetry changes, all-seven results, the focused
`512730 / GNG089_L` comparison, homolog interpretation, network-wide side
effects, deterministic repeat evidence, structural-versus-causal comparison,
limitations, changed files, and final Git status.

## Validation commands

```text
uv run python -m compileall src
uv run python -m pytest -v
git diff --check
uv run python scripts/run_task010.py
```

No release or history mutation is part of Task 010.

## Completion record

Results will be appended here only after the preregistered protocol completes.

## Completion record

Status: COMPLETE on 2026-09-22. No commit, push, or tag was made.

### 1. Starting state and gates

- Starting HEAD: `25286228cf050928fc7534a1603ed388d48d1053`.
- Starting branch/worktree: `master`, clean.
- Starting baseline: `uv run python -m pytest -q` -> `165 passed, 1 skipped`.
- Final validation: `uv run python -m compileall src scripts` passed,
  `uv run python -m pytest -v` -> `174 passed, 1 skipped`, and `git diff --check`
  passed.
- CUDA device: NVIDIA GeForce RTX 3060, CUDA runtime 12090.
- Primary backend: CUDA float64, batch 30.
- Prepared graph: 166,700 neurons, 24,904,953 effective edges; cache
  fingerprint `8064dbec4ecf5ac72a4ab23835e4fcbdc6cdcc5315a1b71f71c135de9eb8cf4d`;
  prepared fingerprint
  `d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495`.
- Task 008 populations: left 42-body fingerprint
  `8b1c625ddf719e5853d409223d88b8c997a1fdcffb298210965b0402efce49c7`; right
  43-body fingerprint
  `2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b`.
- Experiment fingerprint:
  `7ebd96522154f09ffa6e913ca0db17c366fe8a1fa7901aa52f28138e10039ef2`.
- Sign policy: `Shiu2024SignPolicy`; `dt=0.1 ms`; duration 1000 ms; frequency
  100 Hz; synaptic weight 0.275 mV; all Task 005 LIF parameters unchanged.

### 2. Frozen candidate manifest

The Task 009 source candidate-list fingerprint was
`113b9a767eeb61a56419e7b76e57b785fe26d9bb77e4ad6c9f6e2020be2f6ea9`. The
Task 010 manifest fingerprint is
`2518ca63e6fc35ed6772518d7a2d1ab17b7ad211e1491cfffa1fe778d89dd5f4`.

| body ID | type / instance | side | superclass | neurotransmitter | homolog | Task 009 signed proxies |
| --- | --- | --- | --- | --- | --- | --- |
| 10135 | DNge031 / DNge031_L | L | descending_neuron | GABA | 10313 / DNge031_R | L->MN9_L -190 |
| 10313 | DNge031 / DNge031_R | R | descending_neuron | GABA | 10135 / DNge031_L | R->MN9_L -108; R->MN9_R -36 |
| 12752 | DNge080 / DNge080_L | L | descending_neuron | acetylcholine | 12364 / DNge080_R | L->MN9_L 101; L->MN9_R 13 |
| 43765 | GNG095 / GNG095_R | R | cb_intrinsic | GABA | 12851 / GNG095_L | R->MN9_L -26; R->MN9_R -55 |
| 512730 | GNG089 / GNG089_L | L | cb_intrinsic | acetylcholine | 556512 / GNG089_R | L->MN9_L 1904 |
| 514753 | GNG568 / GNG568_L | L | cb_intrinsic | acetylcholine | 513411 / GNG568_R | L->MN9_L 144 |
| 517861 | GNG041 / GNG041_R | R | cb_intrinsic | GABA | 43293 / GNG041_L | L->MN9_R -49; R->MN9_R -50 |

No candidate was added, removed, or selected from perturbation outcomes. No
candidate was technically invalid.

### 3. Baseline replay

Both 30-trial replays passed exact trial checks against the preserved Task 008
artifact, including trial index, seed, total network spikes, and canonical
spike-result digest.

| stimulus | MN9_L mean Hz | MN9_R mean Hz | total spikes mean | active neurons mean | delivered events mean | asymmetry |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LEFT sugar | 66.5333 | 5.9000 | 58,227.37 | 3,726.00 | 19,203,465.17 | 0.83709 |
| RIGHT sugar | 95.1000 | 2.4333 | 82,305.57 | 4,878.47 | 27,914,795.03 | 0.95010 |

### 4. Preflight and intervention semantics

The bounded 20 ms, two-trial `512730` silencing preflight passed exact CPU/GPU
canonical spike-event equality. CPU and GPU digests were identical for both
trials:

`1245dd1bb1aab4e65d10090014a8f892741b30a6ef4d4fe126face83d254de92`,
`294dbf0de49a73337912562d157294df5608390aa1851c7cd7929c8211c6b80a`.

The silenced neuron remained eligible to receive input, update its internal
state, and spike internally. Only its outgoing synaptic-event scheduling was
suppressed.

### 5. Single-candidate outcomes

Changes are silenced minus baseline. Percent changes use the signed change over
the absolute baseline mean. The classification is the preregistered category.

| candidate | LEFT MN9_L (Hz, change, %) | LEFT MN9_R (Hz, change, %) | RIGHT MN9_L (Hz, change, %) | RIGHT MN9_R (Hz, change, %) |
| --- | --- | --- | --- | --- |
| 10135 | 84.933, +18.400, +27.66% moderate | 9.900, +4.000, +67.80% moderate | 104.767, +9.667, +10.16% moderate | 4.233, +1.800, +73.97% moderate |
| 10313 | 76.167, +9.633, +14.48% moderate | 8.933, +3.033, +51.41% moderate | 115.467, +20.367, +21.42% major | 8.800, +6.367, +261.64% major |
| 12752 | 55.200, -11.333, -17.03% moderate | 1.500, -4.400, -74.58% moderate | 93.733, -1.367, -1.44% small | 0.100, -2.333, -95.89% moderate |
| 43765 | 66.533, 0.000, 0.00% negligible | 5.900, 0.000, 0.00% negligible | 95.100, 0.000, 0.00% negligible | 2.433, 0.000, 0.00% negligible |
| 512730 | 65.000, -1.533, -2.30% small | 5.667, -0.233, -3.95% negligible | 95.067, -0.033, -0.04% negligible | 2.433, 0.000, 0.00% negligible |
| 514753 | 66.533, 0.000, 0.00% negligible | 5.900, 0.000, 0.00% negligible | 95.100, 0.000, 0.00% negligible | 2.433, 0.000, 0.00% negligible |
| 517861 | 63.433, -3.100, -4.66% small | 5.900, 0.000, 0.00% negligible | 100.700, +5.600, +5.89% moderate | 3.000, +0.567, +23.29% small |

### 6. Paired-trial summaries

The following are paired intervention-minus-baseline spike-count deltas per
trial. Ranges and standard deviations are in spike counts; rate deltas are
equivalent to Hz because each trial is 1000 ms.

| candidate / stimulus | MN9_L mean / median / range / SD | MN9_R mean / median / range / SD | total network mean / median / range / SD |
| --- | --- | --- | --- |
| 10135 / LEFT | +18.4 / +20 / 0..35 / 9.55 | +4.0 / +5 / -5..11 / 3.33 | +93,679 / +10,534 / -20,663..684,942 / 213,985 |
| 10135 / RIGHT | +9.67 / +11 / -10..31 / 9.33 | +1.8 / +2 / -1..7 / 2.04 | +39,905 / +284 / -498,112..671,149 / 191,215 |
| 10313 / LEFT | +9.63 / +8.5 / -10..30 / 10.29 | +3.03 / +3 / -5..9 / 3.44 | +26,280 / +4,664 / -26,539..668,542 / 121,886 |
| 10313 / RIGHT | +20.37 / +20.5 / -4..38 / 9.93 | +6.37 / +6.5 / -2..14 / 3.65 | +67,784 / +9,003 / -491,084..677,787 / 236,093 |
| 12752 / LEFT | -11.33 / -10.5 / -28..7 / 8.05 | -4.4 / -4 / -9..-1 / 1.91 | +5,335 / -6,769 / -48,495..488,122 / 92,047 |
| 12752 / RIGHT | -1.37 / -3 / -24..24 / 12.69 | -2.33 / -2 / -7..0 / 1.61 | +11,880 / -9,707 / -507,583..604,969 / 179,345 |
| 43765 / LEFT | 0 / 0 / 0..0 / 0 | 0 / 0 / 0..0 / 0 | 0 / 0 / 0..0 / 0 |
| 43765 / RIGHT | 0 / 0 / 0..0 / 0 | 0 / 0 / 0..0 / 0 | 0 / 0 / 0..0 / 0 |
| 512730 / LEFT | -1.53 / -2.5 / -35..21 / 11.54 | -0.23 / 0 / -4..4 / 2.37 | +39,630 / -890 / -35,133..675,636 / 169,124 |
| 512730 / RIGHT | -0.03 / 0 / -13..12 / 4.01 | 0 / 0 / -1..2 / 0.46 | +708 / 0 / -2,441..23,011 / 4,263 |
| 514753 / LEFT | 0 / 0 / 0..0 / 0 | 0 / 0 / 0..0 / 0 | 0 / 0 / 0..0 / 0 |
| 514753 / RIGHT | 0 / 0 / 0..0 / 0 | 0 / 0 / 0..0 / 0 | 0 / 0 / 0..0 / 0 |
| 517861 / LEFT | -3.1 / -3 / -30..19 / 10.36 | 0 / 0 / -8..6 / 3.15 | +35,568 / -291 / -26,654..580,669 / 146,247 |
| 517861 / RIGHT | +5.6 / +4.5 / -12..27 / 10.16 | +0.57 / +0.5 / -5..5 / 2.61 | +66,160 / -190 / -498,277..684,846 / 246,184 |

These are paired deterministic model trials, not biological replicates. The
large total-network ranges show why network-wide collapse or amplification
must be considered alongside MN9 rates.

### 7. Rankings and asymmetry

By largest absolute MN9_L change among the two stimulus conditions, the ranking
was `10313` (+20.367 Hz, RIGHT), `10135` (+18.400 Hz, LEFT), `12752`
(-11.333 Hz, LEFT), `517861` (+5.600 Hz, RIGHT), `512730` (-1.533 Hz, LEFT),
then `43765` and `514753` (zero). By largest absolute MN9_R change, the ranking
was `10313` (+6.367 Hz, RIGHT), `12752` (-4.400 Hz, LEFT), `10135` (+4.000 Hz,
LEFT), `517861` (+0.567 Hz, RIGHT), `512730` (-0.233 Hz, LEFT), then `43765`
and `514753` (zero).

The bounded asymmetry metric was `(MN9_L - MN9_R) / (MN9_L + MN9_R)`:

| intervention | LEFT baseline -> silenced | RIGHT baseline -> silenced |
| --- | --- | --- |
| 10135 | 0.83709 -> 0.79121 | 0.95010 -> 0.92232 |
| 10313 | 0.83709 -> 0.79005 | 0.95010 -> 0.85837 |
| 12752 | 0.83709 -> 0.94709 | 0.95010 -> 0.99787 |
| 43765 | 0.83709 -> 0.83709 | 0.95010 -> 0.95010 |
| 512730 | 0.83709 -> 0.83962 | 0.95010 -> 0.95009 |
| 514753 | 0.83709 -> 0.83709 | 0.95010 -> 0.95010 |
| 517861 | 0.83709 -> 0.82981 | 0.95010 -> 0.94214 |
| all seven | 0.83709 -> 0.86776 | 0.95010 -> 0.97764 |

### 8. All-seven joint perturbation

The joint intervention did not collapse the network or remove MN9_L dominance.
For LEFT sugar, MN9_L changed from 66.5333 to 80.0333 Hz (+13.5 Hz,
moderate), MN9_R changed from 5.9 to 5.6667 Hz (-0.2333 Hz, negligible), and
asymmetry increased from 0.83709 to 0.86776. For RIGHT sugar, MN9_L changed
from 95.1 to 106.1333 Hz (+11.0333 Hz, moderate), MN9_R changed from 2.4333
to 1.2 Hz (-1.2333 Hz, major by the percent threshold), and asymmetry
increased from 0.95010 to 0.97764.

Network-wide means also increased: total spikes by 39,033 for LEFT and
144,920 for RIGHT; active neurons by 209.53 and 1,284.60 respectively; and
delivered events by 11,570,750 and 47,444,532 respectively. These global side
effects are substantial and prevent treating the joint result as a selective
MN9 mechanism.

### 9. `512730 / GNG089_L` focused interpretation

`512730` was the strongest Task 009 signed structural proxy at 1,904, with 26
left-sugar contributors and a 105 bottleneck proxy. Its causal effect was
small for LEFT MN9_L (-1.533 Hz, -2.30%) and negligible for RIGHT MN9_L
(-0.033 Hz, -0.04%). It therefore did not translate structural prominence
into a large single-candidate MN9 response effect under this protocol.
This is a useful structural-versus-dynamics discrepancy, not evidence that
the structural metric is invalid.

### 10. Homolog comparison

Homologs were recorded but not silenced. The results are compatible with the
Task 009 observation that bilateral homologs have different sugar input and
MN9 output wiring. In particular, `10135/10313` and `GNG095` `43765` show
different stimulation-side effects despite homolog annotation, while
`512730/556512` was not treated as an automatically paired intervention.
No new intervention candidate was introduced.

### 11. Repeatability and preservation

The repeated `10135 / LEFT` condition, repeated `43765 / LEFT` condition, and
both all-seven conditions each reproduced all 30 trial rates, total spike
counts, and canonical result digests exactly. The Task 010 artifact is
separate from `data/derived/task008-results.json`; the Task 008 artifact was
not overwritten. Task 010 result digest:

`20f8d8f6432070625a9ca6a4ddb32b2cc0a68f380102dbd3ee5e35bbcc578e45`.

### 12. Interpretation and nonclaims

Within the validated MaleCNS-Sim LIF model, silencing `10313` changed the
RIGHT-sugar MN9_L response by +20.367 Hz and the MN9_R response by +6.367 Hz;
silencing `10135` changed the LEFT-sugar MN9_L response by +18.4 Hz. Those are
model-sensitivity findings under the specified sugar stimulus. The strongest
structural candidate `512730` had only a small or negligible MN9 effect, and
`43765`/`514753` were exact nulls in this implementation and schedule.

These results do not establish biological necessity, behavioral necessity,
experimentally proven synaptic mechanism, or an actual fly causal effect.
Thirty deterministic trials are not biological replicates. Large network-wide
side effects, model-policy neurotransmitter signs, homolog/type uncertainty,
and the finite candidate set limit mechanistic interpretation.

### 13. Files and Git status

Tracked working-tree files added or changed for Task 010:

- `docs/plans/2026-09-22-task-010-frozen-candidate-causal-perturbation.md`
- `src/malecns_sim/analysis/task010.py`
- `tests/test_task010.py`
- `scripts/run_task010.py`

Ignored derived artifact:

- `data/derived/task010-results.json`

Git remains on `master` at starting HEAD with only the four Task 010 files
above untracked; no commit, push, or tag was performed.

### 14. Recommended next task

Stop after Task 010. If a follow-up is authorized, first define a separate
task for mechanism diagnostics or broader preregistered perturbation design;
do not revise the Task 010 candidate set or thresholds retrospectively.
