# Task 006 - Shiu v630 Sugar-to-MN9 Reference Reproduction

Status: implementation and validation complete; ready for Task 006 closure.

This record validates the Task 005 NumPy LIF engine against the original
FlyWire v630 graph used by Shiu et al. It does not map FlyWire v630 IDs to
MaleCNS v1.0 IDs and makes no cross-sex homolog claim.

## 1. Baseline gate

- Branch: `master`
- Task 005 `HEAD`: `1cc860a9b0cd5e7ada4ec0e646184f1160eeff` (`feat: add reference LIF dynamics engine`)
- Worktree before Task 006: clean
- Baseline command: `uv run python -m pytest -q`
- Baseline result: `74 passed in 0.92s`

## 2. Reference provenance

The official companion repository is
[philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model),
resolved on 2026-09-20 as:

```text
main = 91bdd1e7dcf193f3e7ca5a8933497fcef63b7960
```

The raw local artifacts are under the ignored directory
`data/reference/shiu-2024/`. They are not committed. The tracked manifest is
`data/provenance/shiu-2024-v630.json`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `2023_03_23_completeness_630_final.csv` | 3,057,611 | `e6b71e17671a9bdb05f55e4bc6774640a1418cb7a05125e0fc994ad40f9bfdfb` |
| `2023_03_23_connectivity_630_final.parquet` | 86,630,944 | `94db8c650533bc36ffa3223f2e62325d5648b8d6bd31c3a4e1c804628c7557b3` |
| `example.ipynb` | 10,282 | `1737c3043af700504c4791c4bfc02d1856bbeb0d36c469832e4b9399dfddda3a` |
| `model.py` | 11,900 | `fc45837d7122c6ce2a7f3f2f23c515992e4b232aadb919efabb72337fac88e4e` |
| `results/example/sugarR_100Hz.parquet` | 557,849 | `93722ec03c3faa5a85790d77ed16bdd7f1e38a7c847ed0bc3af3dc2e4d0c3d34` |

The quantitative oracle is explicitly `sugarR_100Hz.parquet`. The source
`model.py` default is `r_poi = 150 Hz`, while notebook prose says the default
sugar experiment is 200 Hz; the notebook later explicitly sets 100 Hz for
`sugarR_100Hz`. `sugarR.parquet` was not used as an oracle because its
stimulation provenance is not resolved across that historical discrepancy.

## 3. v630 schema and adapter boundary

The completeness CSV has 127,400 rows. Its unnamed CSV index is the FlyWire
neuron ID, with 127,400 unique values in strict ascending order. The original
Brian index is the row position in this index. The connectivity Parquet has
14,687,178 rows and these columns:

```text
Presynaptic_ID: int64
Postsynaptic_ID: int64
Presynaptic_Index: int64
Postsynaptic_Index: int64
Connectivity: int64
Excitatory: int64
Excitatory x Connectivity: int64
__index_level_0__: int64
```

Both endpoint index columns span 0 through 127,399. The ID/index mapping was
verified on all rows. `Excitatory` contains only `-1` and `+1`, and the stored
`Excitatory x Connectivity` column equals the elementwise product of the two
source columns for all 14,687,178 rows.

The adapter in `src/malecns_sim/data/shiu_v630.py` preserves the completeness
row ordering and uses the original index columns. Its primary projection is:

```text
stored Excitatory x Connectivity * 0.275 mV
```

It does not invoke the MaleCNS Task 004 neurotransmitter resolver. This is a
historical Shiu-v630 signed-connectivity adapter, not a generic connectome
framework and not a MaleCNS biological sign policy.

## 4. Exact reference neuron set

The ordered `neu_sugar` list parsed from the official notebook is exactly 21
IDs:

```text
720575940624963786, 720575940630233916, 720575940637568838,
720575940638202345, 720575940617000768, 720575940630797113,
720575940632889389, 720575940621754367, 720575940621502051,
720575940640649691, 720575940639332736, 720575940616885538,
720575940639198653, 720575940620900446, 720575940617937543,
720575940632425919, 720575940633143833, 720575940612670570,
720575940628853239, 720575940629176663, 720575940611875570
```

All 21 IDs were found in completeness data and mapped to valid original
simulation indices. Their positions, preserving notebook order, are:

```text
65153, 90982, 113421, 114820, 27680, 93880, 102632, 48902,
47685, 119716, 117163, 27293, 116889, 44337, 31392, 100853,
103321, 14231, 84634, 86214, 11916
```

MN9 is the official example ID `720575940660219265`, verified at original
simulation index `127193`.

## 5. Deterministic reference-graph validation

The prepared effective projection fingerprint was:

```text
2d3e07c8de826859bc1a4c4b57c2932fa92eacb426324b36489c1683c778a6e1
```

The graph was prepared once and reused by every trial. Three deterministic
schedules on the original graph were executed successfully:

| Schedule | Runtime | Spikes | Active neurons | Delivered events | Result digest |
|---|---:|---:|---:|---:|---|
| all 21 sugar IDs once at 0 ms, 5 ms | 0.163 s | 26 | 26 | 1,547 | `2c087a4d0a98cad654940a3a7507ca17994c9a895d9c63cf86b0be89b49047b6` |
| first sugar ID at 0, 1, 2 ms, 5 ms | 0.158 s | 1 | 1 | 79 | `fe7e7f7ec4e5c4b70a6d55b94a93ef214e5cc6615101441854ef1b3bbf6987f4` |
| all 21 sugar IDs once at 0 ms, 10 ms | 0.302 s | 32 | 32 | 3,336 | `8d0ff94dcbd58c4c02005317e12a897b88b14875a8f9dc651d046e33ea8ff7dd` |

Repeating the same seeded local trial reproduced the trial-0 digest
`5dd0e37c6ec6f86fa7221ccb87c34f2c6fa022ce3cda76396b2b891a34484b0e`.
These are engine and scheduling checks, not biological validation.

## 6. Official stored 100 Hz result

The read-only result adapter measured `results/example/sugarR_100Hz.parquet`
as 289,073 spike rows from 30 trials (`0..29`), with `t` in seconds from
0.0001 through 0.9999. The declared duration used for rate conversion is one
second. MN9 contributes 2,011 spikes total. Statistics below use population
standard deviation (`ddof=0`).

| Metric | Official reference |
|---|---:|
| MN9 mean firing rate | 67.0333 Hz |
| MN9 SD | 6.5954 Hz |
| MN9 active-trial fraction | 1.0000 |
| Total network spikes, mean | 9,635.7667 |
| Total network spikes, SD | 406.5034 |
| Total network spikes, min..max | 8,781..10,523 |
| Active neurons, mean | 354.3000 |
| Active neurons, SD | 7.8958 |
| Active neurons, min..max | 329..367 |

MN9 trial counts are:

```text
69, 75, 65, 70, 66, 59, 78, 60, 60, 68, 70, 63, 54, 78, 70,
80, 76, 67, 68, 72, 71, 53, 67, 60, 66, 68, 65, 59, 65, 69
```

## 7. MaleCNS-Sim 100 Hz reproduction

The local run used all 21 sugar IDs, 1,000 ms, 30 trials, the Task 005
`PoissonStimulus`, `rate_hz=100`, `weight_factor=250`, and seeds
`600100 + trial`. NumPy-generated Poisson events were not expected to match
Brian2 `PoissonInput` event streams.

| Metric | MaleCNS-Sim | Absolute difference | Relative difference |
|---|---:|---:|---:|
| MN9 mean firing rate | 67.0667 Hz | +0.0333 Hz | +0.0497% |
| MN9 SD | 4.3660 Hz | -2.2293 Hz | -33.8016% |
| MN9 active-trial fraction | 1.0000 | 0.0000 | 0.0000% |
| Total network spikes, mean | 9,763.6667 | +127.9000 | +1.3273% |
| Total network spikes, SD | 313.5157 | -92.9877 | -22.8750% |
| Active neurons, mean | 356.9000 | +2.6000 | +0.7338% |
| Active neurons, SD | 6.3211 | -1.5747 | -19.9429% |

Local MN9 counts were:

```text
61, 64, 63, 68, 62, 65, 73, 65, 71, 72, 75, 64, 64, 71, 64,
67, 65, 70, 74, 61, 71, 75, 67, 66, 61, 61, 68, 71, 63, 70
```

Local sugar input counts were recorded per trial. Their sum was 63,153,
mean 2,105.1, population SD 42.5796, and range 2,005..2,177. Local total
spike counts ranged from 9,126..10,307 and active-neuron counts from 344..376.

The agreement in MN9 mean and active-trial fraction is close, while the lower
local trial-to-trial dispersion and modestly higher network mean are
discrepancies to investigate rather than tune away. No model parameter was
adjusted to improve agreement.

## 8. Sugar-frequency curve

The primary paper describes sugar activation across 10--200 Hz. The bounded
grid used here was 10, 25, 50, 100, 150, and 200 Hz, with 30 trials per
condition and seeds `601000 + frequency * 100 + trial`. The four-worker run
shared one immutable prepared graph.

| Input Hz | MN9 mean Hz | MN9 SD | Active-MN9 fraction | Total spikes mean | Active neurons mean |
|---:|---:|---:|---:|---:|---:|
| 10 | 0.0000 | 0.0000 | 0.0000 | 242.27 | 27.80 |
| 25 | 0.0000 | 0.0000 | 0.0000 | 840.27 | 59.77 |
| 50 | 22.0333 | 6.3429 | 1.0000 | 3,257.77 | 264.67 |
| 100 | 67.4000 | 5.1095 | 1.0000 | 9,708.57 | 356.47 |
| 150 | 82.5667 | 4.2558 | 1.0000 | 13,650.47 | 382.77 |
| 200 | 93.1333 | 5.1944 | 1.0000 | 17,024.33 | 404.27 |

MN9 response therefore changes systematically with input frequency in this
engine reproduction, increasing from silence at 10/25 Hz through 93.13 Hz at
200 Hz. This is a response-shape result, not a claim of exact Brian2
quantitative equality.

## 9. Optional silencing check

One 100 Hz seeded trial used the companion semantics of zeroing all outgoing
synapse weights from one selected neuron. With seed 600100 and sugar ID
`720575940624963786` silenced:

| Condition | MN9 spikes | Total spikes | Active neurons | Result digest |
|---|---:|---:|---:|---|
| Control | 61 | 9,245 | 357 | `5dd0e37c6ec6f86fa7221ccb87c34f2c6fa022ce3cda76396b2b891a34484b0e` |
| Outgoing-silenced | 67 | 9,224 | 350 | `1a42d499d22bda3fc5b1615ae4bb817f2b049b084150f008592d431dd0d539b1` |

This validates the intervention path only; it is not interpreted as a
biological causal result.

## 10. Runtime, memory, and reuse boundary

- First observed v630 load: 0.639 s.
- First observed one-time projection preparation: 7.784 s.
- Serial 100 Hz experiment: 472.06 s for 30 trials, about 15.74 s per trial
  after setup.
- Six-condition frequency sweep: 2,136.84 s wall time with four workers.
- Peak observed Python working set during the four-worker sweep: about 2.14
  GB. This is an observed process working-set sample, not a platform-wide
  memory guarantee.
- Static graph arrays were prepared once per process and passed read-only to
  all trials. Every trial allocated fresh membrane, conductance, refractory,
  and delay-ring state. Offline tests verify equal repeated digests and no
  graph-array mutation.

No persistent binary cache format was introduced.

## 11. Side mapping and scientific limitations

The Nature paper discusses unilateral sugar activation and contralateral versus
ipsilateral MN9. This task did not admit a side-label source or a verified pair
of MN9 identities. The v630 completeness/connectivity files expose IDs and
indices, not hemisphere authority. No hemisphere was inferred from ID order;
the ipsilateral/contralateral comparison is deferred.

The result is an engine reproduction over the original Shiu v630 signed graph.
It is not a MaleCNS v1.0 identity mapping, a statement that the FlyWire MN9
ID is a MaleCNS body ID, a biological validation of the LIF model, or proof of
identical Brian2 scheduling/RNG behavior. Differences remain attributable to
at least RNG stream, event scheduling, and implementation details until
independently isolated.

## 12. Validation and changed files

Offline tests are in `tests/test_task006.py` and cover schema loading, index
mapping, signed-column interpretation, exact neuron parsing, missing-ID
failure, state reset, immutable graph reuse, seeded generation, rate
calculation, reference parquet summarization, comparison metrics, and
provenance boundaries.

Final validation commands/results:

```text
uv run python -m pytest -v       82 passed
uv run python -m compileall src  passed
git diff --check                 passed
```

Changed tracked files:

```text
.gitignore
README.md
data/provenance/shiu-2024-v630.json
docs/plans/2026-09-20-task-006-shiu-v630-sugar-mn9-reproduction.md
src/malecns_sim/analysis/__init__.py
src/malecns_sim/analysis/shiu_v630.py
src/malecns_sim/data/shiu_v630.py
tests/test_task006.py
```

The downloaded reference directory remains ignored. Task 006 scope includes
no push or tag operation.

Recommended next task: Task 007 - MaleCNS v1.0 Sugar/MN9 Homolog Mapping.
