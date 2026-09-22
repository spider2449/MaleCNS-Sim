# Task 011 - Temporal Mechanism Audit of Counterintuitive MN9 Perturbations

Status: IN PROGRESS. This is the preregistered Task 011 analysis record. It
uses only the frozen Task 010 interventions and fixed trial indices `0`, `10`,
and `20` for both 100 Hz sugar stimulus sides.

## Scope and hard gates

The mechanism question is whether counterintuitive MN9_L increases after
silencing are most compatible with a short signed path, recurrent/network
redistribution, a mixed mechanism, or unresolved evidence. No new neuron,
stimulus, sign, graph threshold, MN9 identity, LIF parameter, or intervention
is introduced. The five frozen cases are `10313`, `10135`, `12752`, `512730`,
and `43765`.

The preserved `task008-paused-before-gpu-gate` stash is inspected before any
Task 011 mutation. It may be dropped only if all useful changes are already
represented or superseded by committed Tasks 008-010; it is never applied.

## Fixed execution

Task 008 deterministic schedule construction is reused unchanged. Baseline and
each single-candidate outgoing-silencing execution use identical schedules at
trial indices `0`, `10`, and `20`, 1000 ms duration, 0.1 ms timestep, 100 Hz
input, the Task 005 LIF parameters, and the cached Task 008 full signed graph.
Sparse traces record canonical spike events, per-timestep delivered-event
signatures, selected v/g traces, and candidate/first-hop summaries without a
dense all-neuron state matrix.

## Preregistered compatibility rules

`SHORT_PATH_COMPATIBLE` requires an annotation-supported signed path of at
most two hops, a changing immediate target before MN9 divergence, timing
compatible with 1.8 ms per hop, signed effect compatibility, and no broad
network divergence required before MN9 divergence. `NETWORK_REDISTRIBUTION_
COMPATIBLE` is supported by broad divergence before MN9 response, absence of an
explanatory short signed route, multiple recurrent branches, or substantial
network activity change before MN9 response. If both sets of evidence apply,
the result is `MIXED`; if neither is supported, it is `UNRESOLVED`.

These are model-level compatibility labels, not biological mechanism or
necessity claims.

## Required result sections

The completion record will include candidate structural metadata, baseline
activity exposure, first-divergence timing, propagation windows, first-hop
target changes, 10313/10135/12752 comparisons, structural-vs-causal and null
controls, CPU/CUDA trace validation, deterministic replay, classifications,
limitations, fingerprints, changed files, and final Git state.

## Validation

```text
uv run python -m compileall src
uv run python -m pytest -v
git diff --check
git status --short
git diff --stat
```

No commit, push, or tag is part of Task 011.

## Completion record

Status: COMPLETE on 2026-09-22. No commit, push, or tag was made.

### 1. Preregistered question and gates

The question was whether the Task 010 counterintuitive MN9_L increases after
silencing are compatible with a signed short path, recurrent/network
redistribution, a mixed mechanism, or unresolved evidence. Only the frozen
Task 010 cases `10313`, `10135`, `12752`, `512730`, and `43765` were used.
The starting HEAD was `fe4048726641a99b3cf9ed33aec406d50700f489`, the supplied
Task 010 digest was
`20f8d8f6432070625a9ca6a4ddb32b2cc0a68f380102dbd3ee5e35bbcc578e45`, and the
starting baseline was `174 passed, 1 skipped`.

The stale `task008-paused-before-gpu-gate` stash contained only the earlier
active-LIF/export changes already represented or superseded by committed Tasks
008-010. It was classified `SAFE_TO_DROP` and only that exact stash was
dropped. It was not applied. The worktree was clean before Task 011 mutations.

### 2. Frozen trials, stimuli, and trace schema

Task 008 schedule generation was reused unchanged for LEFT sugar 100 Hz and
RIGHT sugar 100 Hz. The fixed trial indices were exactly `0`, `10`, and `20`
for baseline and every single-candidate silencing. The full cached graph was
166,700 neurons and used the existing Task 004 `Shiu2024SignPolicy`, Task 005
parameters, `dt=0.1 ms`, 1.8 ms synaptic delay, and 1000 ms duration.

The cache fingerprint was
`8064dbec4ecf5ac72a4ab23835e4fcbdc6cdcc5315a1b71f71c135de9eb8cf4d`; the
prepared graph fingerprint was
`d773107682fdc4280e91ac5aa88c8bd2a3a913ee80c85b5e7fc12d7d47ba6495`; and the
effective graph fingerprint was
`ed1cfbbdd6841a87a82ca3b0416536d57fea4a647581dc7cb8e0b9ebf1608a2f`.

The sparse trace schema records canonical spike output, per-timestep delivered
event counts, signed and absolute delivered weight sums, delivered target
counts, delivered target-index checksums, and selected v/g traces for the five
cases plus both MN9 readouts. It never allocates a dense all-neuron state
matrix. Diagnostic floating summaries are fingerprinted at the declared
`1e-10` trace tolerance; exact event counts and target checksums remain
unrounded.

### 3. Candidate structural metadata and baseline activity

Outgoing weights below are anatomical-weight equivalents under the signed
projection. `+/-` are Task 004 effective signs; the route counts are known
direct or two-hop routes in the frozen graph.

| candidate | NT/sign | targets | total | positive | negative | direct MN9_L/R | shortest L/R; two-hop L/R |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 10135 | GABA / negative | 537 | 5,079 | 0 | 5,079 | yes/no | 1/2; 108/56 |
| 10313 | GABA / negative | 547 | 4,586 | 0 | 4,586 | yes/yes | 1/1; 116/74 |
| 12752 | acetylcholine / positive | 421 | 4,754 | 4,754 | 0 | yes/yes | 1/1; 98/62 |
| 512730 | acetylcholine / positive | 254 | 1,937 | 1,937 | 0 | yes/no | 1/2; 94/33 |
| 43765 | GABA / negative | 168 | 2,523 | 0 | 2,523 | yes/yes | 1/1; 57/52 |

Baseline exposure over the three fixed trials was:

| candidate | LEFT spikes/rate; outgoing events; active targets | RIGHT spikes/rate; outgoing events; active targets |
| --- | --- | --- |
| 10135 | 329 / 109.67 Hz; 176,673; 537 | 142 / 47.33 Hz; 76,254; 537 |
| 10313 | 144 / 48.00 Hz; 78,768; 547 | 365 / 121.67 Hz; 199,655; 547 |
| 12752 | 103 / 34.33 Hz; 43,363; 421 | 123 / 41.00 Hz; 51,783; 421 |
| 512730 | 18 / 6.00 Hz; 4,572; 254 | 0 / 0.00 Hz; 0; 0 |
| 43765 | 0 / 0.00 Hz; 0; 0 | 0 / 0.00 Hz; 0; 0 |

Thus the structural prominence of 512730 does not imply exposure under RIGHT
stimulus, and 43765 is an inactive exact-null control in both conditions.

### 4. Divergence timing and propagation

The following ranges are across trials 0, 10, and 20, in ms, in the order
delivery difference, downstream spike difference, MN9_L state difference, and
MN9_L spike-train difference:

| case | delivery | downstream | MN9_L state | MN9_L spikes | peak divergent neurons |
| --- | --- | --- | --- | --- | --- |
| 10135 / LEFT | 12.7-18.5 | 14.2-20.2 | 12.8-18.6 | 22.0-33.7 | 28-48 |
| 10135 / RIGHT | 31.1-38.4 | 31.4-38.8 | 31.2-41.4 | 34.5-43.0 | 37-58 |
| 10313 / LEFT | 34.6-56.8 | 34.9-57.1 | 34.7-56.9 | 44.2-69.7 | 34-46 |
| 10313 / RIGHT | 13.5-14.4 | 14.3-16.5 | 13.6-14.5 | 18.6-21.6 | 36-47 |
| 12752 / LEFT | 33.3-41.3 | 33.6-41.6 | 35.5-41.4 | 37.2-47.5 | 25-36 |
| 12752 / RIGHT | 27.1-35.6 | 27.4-35.7 | 27.2-35.7 | 28.0-37.0 | 46-143 |
| 512730 / LEFT | 11.9-14.3 | 13.2-15.5 | 12.0-14.4 | 31.3-35.5 | 23-41 |
| 512730 / RIGHT | null | null | null | null | 0 |
| 43765 / either | null | null | null | null | 0 |

The full eight-window propagation profiles are in the derived artifact. They
show small early divergence followed by thousands of divergent neurons and
divergent spike events in the 20-50 ms and later windows for active cases. For
example, 10313 / RIGHT has mean divergent events `26.7`, `74.7`, `385.3`,
`2,325.0`, `6,114.3`, `20,515.7`, `33,134.0`, and `63,826.0` across the
successive windows; mean divergent neurons are `14.0`, `39.3`, `202.0`,
`959.7`, `2,894.7`, `4,039.3`, `2,974.7`, and `2,694.0`. MN9_L delta spikes
are not required to precede the broad later expansion.

### 5. First-hop targets and mechanism classifications

The immediate target sets are pre-existing graph targets only. Changed-target
unions across the three trials were 10135 LEFT/RIGHT `247/242`, 10313
`237/248`, 12752 `224/247`, 512730 `116/0`, and 43765 `0/0`, against target
counts `537`, `547`, `421`, `254`, and `168`, respectively. First-hop changes
were compared before MN9 divergence; later changes were not used to claim a
short path.

| case | classification |
| --- | --- |
| 10313 / LEFT | NETWORK_REDISTRIBUTION_COMPATIBLE |
| 10313 / RIGHT | NETWORK_REDISTRIBUTION_COMPATIBLE |
| 10135 / LEFT | NETWORK_REDISTRIBUTION_COMPATIBLE |
| 10135 / RIGHT | MIXED |
| 12752 / LEFT | MIXED |
| 12752 / RIGHT | MIXED |
| 512730 / LEFT | NETWORK_REDISTRIBUTION_COMPATIBLE |
| 512730 / RIGHT | UNRESOLVED |
| 43765 / LEFT | UNRESOLVED |
| 43765 / RIGHT | UNRESOLVED |

The mixed labels mean that at least one fixed trial supplied short-path
compatibility evidence while the case also supplied network evidence. They do
not establish a biological mechanism.

### 6. 10313 focus

10313 is GABA/negative under Task 004 and has direct graph edges to both MN9
readouts, but its signed direct/two-hop path summary is mixed rather than a
single uniform sign. Under RIGHT sugar, its first delivery difference occurred
at 13.5-14.4 ms, downstream spike divergence at 14.3-16.5 ms, MN9_L state
divergence at 13.6-14.5 ms, and MN9_L spike-train divergence at 18.6-21.6 ms.
The immediate target spikes did not change before the MN9 state difference, so
the short-path test failed its ordering requirement. The later propagation
expanded to thousands of divergent neurons. The result is therefore
`NETWORK_REDISTRIBUTION_COMPATIBLE`, not “direct inhibitor of MN9_L”.

Under LEFT sugar, the corresponding ranges were 34.6-56.8, 34.9-57.1,
34.7-56.9, and 44.2-69.7 ms, with the same conservative classification.
The Task 010 RIGHT effect of +20.37 Hz remains a model-level counterintuitive
silencing response; this audit supports downstream/recurrent redistribution,
not a direct biological inhibition claim.

### 7. 10135 comparison

10135 is also GABA/negative and directly reaches MN9_L in the frozen graph.
LEFT first delivery, downstream, MN9_L state, and MN9_L spike divergence were
12.7-18.5, 14.2-20.2, 12.8-18.6, and 22.0-33.7 ms; this is classified
`NETWORK_REDISTRIBUTION_COMPATIBLE` because the immediate-target ordering did
not support a short path before MN9. RIGHT ranges were 31.1-38.4, 31.4-38.8,
31.2-41.4, and 34.5-43.0 ms. Two trials had an immediate target change before
MN9 and delay/sign-compatible timing, but the same trials also had recurrent
branch and broad-network evidence, producing `MIXED`. Bilateral equivalence
is therefore not supported.

### 8. 12752 opposite-direction comparison

12752 is acetylcholine/positive and directly reaches both MN9 readouts. The
Task 010 LEFT MN9_L effect was -11.33 Hz, opposite to the 10313/10135
silencing increases. Its Task 011 propagation begins at 33.3-41.3 ms LEFT and
27.1-35.6 ms RIGHT, with MN9_L spike divergence at 37.2-47.5 and 28.0-37.0
ms. One RIGHT trial and two LEFT trials passed the short-path compatibility
inputs, but all those cases also had network evidence; both sides are
`MIXED`. This is a temporal comparison, not proof that the positive candidate
is biologically excitatory or necessary.

### 9. Structural-vs-causal discordance and null control

512730/GNG089_L has the largest Task 009 signed structural proxy among the
Task 010 candidates, but only 18 baseline spikes across the three LEFT trials
and none under RIGHT. It generated 4,572 outgoing events LEFT and zero RIGHT.
LEFT had delivery divergence at 11.9-14.3 ms and later changed 116 immediate
target spike trains, but the first-hop ordering did not explain MN9 before its
state divergence; the classification is network redistribution-compatible.
RIGHT has no temporal divergence and is unresolved. This supports activity
exposure/redundancy as possible explanations without choosing among them.

43765/GNG095_R produced zero baseline spikes, zero outgoing activity, zero
changed first-hop targets, and exact-null traces for both stimulus sides. The
null is therefore most consistent with an inactive candidate under these fixed
trials, not with cancellation evidence. The analysis does not claim that other
conditions would also be null.

### 10. CPU/CUDA validation and replay

The representative 20 ms trial used LEFT trial-0 schedule, silenced `10313`,
and the same selected trace identities. CPU and CUDA float64 had equal
canonical spikes and result digest
`f4bfec70b46d63e5933099b3b8b81cf67d00166f7edba6d80e18c361c94dd5ff`, equal
sparse delivery semantics, tight v/g agreement, and unchanged spikes when
trace collection was disabled. The complete fixed matrix was executed twice;
the raw artifact hash and embedded result digest matched on the second run.

Final Task 011 result digest:
`fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`.

### 11. Limitations and nonclaims

These labels are compatibility statements within the MaleCNS-Sim LIF model.
They do not prove a direct biological mechanism, causal necessity in vivo,
receptor-specific physiology, behavioral effect, or model-independent identity.
The short-path test uses annotation-supported frozen graph routes and the
Task 004 signed policy; mixed signed routes remain ambiguous. The network
thresholds and trace tolerances were fixed in code before interpreting these
results. Only three deterministic trials per side were analyzed, and no new
perturbation or target selection was performed.

### 12. Files, validation, and Git state

Tracked files changed for Task 011:

- `docs/plans/2026-09-22-task-011-temporal-mechanism-audit.md`
- `src/malecns_sim/analysis/__init__.py`
- `src/malecns_sim/analysis/task011.py`
- `src/malecns_sim/dynamics/__init__.py`
- `src/malecns_sim/dynamics/cuda.py`
- `src/malecns_sim/dynamics/lif.py`
- `scripts/run_task011.py`
- `tests/test_task011.py`

Ignored derived artifact:

- `data/derived/task011-results.json`

The final requested validation is `uv run python -m compileall src`,
`uv run python -m pytest -v`, `git diff --check`, `git status --short`, and
`git diff --stat`. No commit, push, or tag is part of this task.

### 13. Recommended next task

Stop after Task 011. Any follow-up should separately preregister broader
mechanistic diagnostics or perturbations; do not revise the frozen Task 010 or
Task 011 cases retrospectively.
