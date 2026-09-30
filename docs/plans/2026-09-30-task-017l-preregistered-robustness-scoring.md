# Task 017L — Preregistered Read-Only Robustness Scoring

Date: 2026-09-30

## Scope and sealed inputs

Task 017L scored the complete, sealed Task 017 matrix using the committed Task 016 preregistration and the existing Task 010 and Task 011 analysis functions. No simulation was executed, no checkpoint record or sidecar was added, and Task 018 was not started. Task 017Q remains deferred.

| Identity | Value |
| --- | --- |
| Starting local `HEAD` | `955b5e19d36e500cdbd148d8c5b4d70d21bf1289` |
| Starting `origin/master` | `955b5e19d36e500cdbd148d8c5b4d70d21bf1289` |
| Starting live GitHub `master` | `955b5e19d36e500cdbd148d8c5b4d70d21bf1289` |
| Task 016 fingerprint | `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6` |
| Checkpoint fingerprint | `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63` |
| Complete-matrix digest | `19c51e79d883915398c2d3d89c3456f3160ba0062cf75abe20e97807979b1028` |
| Complete-matrix manifest SHA-256 | `73c9e51ae06e7d924f80c75578536c6d1ce2b0cf5e2657041ddcfdf5a2262cd8` |

The committed read-only audit passed at 3,168 / 3,168 records and sidecars, pending 0. Duplicate, missing, orphan, metadata-failure, invalid-result-digest, and technical-invalid counts were all zero. Each of R0 and V1–V7 was 396 / 396. The complete-matrix and latest tracked recovery manifests agree with the audited journal SHA-256 `878a2b79fa442c539d4f803819e3154b060b4fbb3c6c5a2cb5a6af464503190e` and sidecar inventory SHA-256 `a24561d152e6acb9761c0b306d7a0158d487ce35e114ef02b543647326208553`.

## Frozen scoring contract

The committed Task 016 source defines the reference as R0 and the seven non-reference variants as:

| Variant | Frozen change |
| --- | --- |
| V1 | `tau_m = 10 ms` |
| V2 | `tau_m = 30 ms` |
| V3 | `tau_s = 2.5 ms` |
| V4 | synaptic delay `= 1.0 ms` |
| V5 | synaptic weight `= 0.200 mV` |
| V6 | threshold `= -44 mV` |
| V7 | `ConservativeSignPolicy` |

The frozen candidates are `10313`, `10135`, `12752`, `512730`, and `43765`, crossed with LEFT and RIGHT stimulus sides for ten cells. The scored Task 010 effect is `silenced_mean_hz - baseline_mean_hz` at MN9_L. Its direction uses the strict sign, with reference-zero comparisons recording `ZERO` within `1e-12 Hz`. Task 010 effect categories use the unchanged `major >= 20 Hz or 50%`, `moderate >= 5 Hz or 20%`, `small >= 1 Hz or 5%`, and otherwise `negligible` thresholds; percentage change is null for a zero baseline. Category stability permits ordinal distance at most one in `negligible < small < moderate < major`.

For each cell, direction and category stability require at least 6/7 variants. Task 011 mechanism classifications are compared using the Task 016 relation: exact matches score 1; `NETWORK_REDISTRIBUTION_COMPATIBLE`↔`MIXED` and `SHORT_PATH_COMPATIBLE`↔`MIXED` score 0.5; `UNRESOLVED` against a different label scores 0; and a direct short-path/network transition scores 0 and independently prevents compatible stability. Mechanism compatible stability requires a compatibility-score sum of at least 6.0/7 and no direct short-path/network transition. Exact mechanism stability remains separately recorded at 6/7 exact labels. `UNRESOLVED` and `MIXED` outcomes were retained.

For each non-reference variant, global support requires at least 3/4 counterintuitive cells to be network-compatible, no more than 1/4 frozen network-reference cells to switch directly to short-path, and at least 2/3 frozen mixed-reference cells to remain MIXED or become SHORT_PATH_COMPATIBLE. ROBUST requires all seven valid variants, all three stability dimensions at 8/10 or better, and support from all seven variants. PARTIALLY_ROBUST requires all seven valid variants, at least 5/7 supporting variants, and at least 5/10 cells stable in each dimension. With a complete technically valid matrix, all other outcomes are NOT_ROBUST.

## Ten-cell results

Mechanism compatible score retains the Task 016 half-credit partial matches; the mechanism verdict also enforces the direct short-path/network prohibition. Variant-level comparisons and labels for every V1–V7 are in [robustness-scoring.json](../../artifacts/task017/robustness-scoring.json).

| Candidate | Side | R0 effect (Hz) | Direction | Category | Mechanism | Direction stable | Category stable | Mechanism compatible score | Mechanism stable |
| --- | --- | ---: | --- | --- | --- | ---: | ---: | ---: | --- |
| 10313 | LEFT | +9.633333 | POSITIVE | moderate | NETWORK_REDISTRIBUTION_COMPATIBLE | 7/7 | 7/7 | 3.5/7 | No |
| 10313 | RIGHT | +20.366667 | POSITIVE | major | NETWORK_REDISTRIBUTION_COMPATIBLE | 7/7 | 7/7 | 7.0/7 | Yes |
| 10135 | LEFT | +18.400000 | POSITIVE | moderate | NETWORK_REDISTRIBUTION_COMPATIBLE | 7/7 | 7/7 | 7.0/7 | Yes |
| 10135 | RIGHT | +9.666667 | POSITIVE | moderate | MIXED | 5/7 | 7/7 | 4.5/7 | No |
| 12752 | LEFT | -11.333333 | NEGATIVE | moderate | MIXED | 6/7 | 5/7 | 5.0/7 | No |
| 12752 | RIGHT | -1.366667 | NEGATIVE | small | MIXED | 7/7 | 6/7 | 6.0/7 | Yes |
| 512730 | LEFT | -1.533333 | NEGATIVE | small | NETWORK_REDISTRIBUTION_COMPATIBLE | 4/7 | 7/7 | 7.0/7 | Yes |
| 512730 | RIGHT | -0.033333 | NEGATIVE | negligible | UNRESOLVED | 4/7 | 7/7 | 5.0/7 | No |
| 43765 | LEFT | 0.000000 | ZERO | negligible | UNRESOLVED | 6/7 | 7/7 | 6.0/7 | Yes |
| 43765 | RIGHT | 0.000000 | ZERO | negligible | UNRESOLVED | 6/7 | 7/7 | 6.0/7 | Yes |

Stable-cell totals are direction 7/10, category 9/10, and mechanism compatible 6/10.

## Variant global support

| Variant | Counterintuitive network-compatible | Direct network-to-short changes (max 1) | MIXED retained or short (need 2) | Supports |
| --- | ---: | ---: | ---: | --- |
| V1 | 4/4 | 0/4 | 1/3 | No |
| V2 | 4/4 | 0/4 | 1/3 | No |
| V3 | 3/4 | 0/4 | 1/3 | No |
| V4 | 4/4 | 0/4 | 3/3 | Yes |
| V5 | 4/4 | 0/4 | 2/3 | Yes |
| V6 | 4/4 | 0/4 | 2/3 | Yes |
| V7 | 4/4 | 0/4 | 1/3 | No |

Three of seven variants support the frozen global conclusion. Each row satisfies the counterintuitive-cell condition; each has zero direct network-to-short changes; V1, V2, V3, and V7 fail only the mixed-reference retention condition. V4, V5, and V6 meet all three conditions.

## Preregistered global classification and interpretation

**Global classification: `NOT_ROBUST`.** All seven variants are technically valid. Category stability meets 9/10, but direction stability is 7/10 and mechanism compatible stability is 6/10; neither reaches the ROBUST threshold of 8/10. PARTIALLY_ROBUST also fails because only 3/7 variants support the global conclusion, below 5/7, despite category stability meeting 5/10. The complete, technically valid matrix therefore receives the preregistered NOT_ROBUST classification.

Allowed interpretation: within MaleCNS-Sim under the preregistered model variants, the frozen Task 010/011 global conclusion is not robust under the Task 016 criteria. This does not establish biological causality or a biological mechanism. Network-redistribution-compatible evidence is not proof of a biological network-redistribution mechanism; structural short-path compatibility is not direct causal proof. No claim is made about the biological fly brain or models outside the tested variants.

## Deterministic artifact and implementation

The tracked artifact is [artifacts/task017/robustness-scoring.json](../../artifacts/task017/robustness-scoring.json). It records all ten cells, every V1–V7 direction/category/mechanism comparison, global-support evidence, completeness, classification, and a deterministic scoring digest. The scientific digest excludes machine paths and timestamps. Checkpoint records are indexed by their canonical unit keys; analysis iterates the frozen variant/candidate/side order, and the artifact contains no absolute workspace path. Journal order and filesystem location are provenance only and are excluded from the scientific digest.

The read-only scorer requires the sealed manifest hashes and fingerprints, audits every sidecar, refuses missing units, loads sidecars on demand, and uses Task 010/011 analysis functions. It does not invoke the Task 017 execution runner and cannot write checkpoint records or sidecars.

- Deterministic scoring digest: `31c7c8fc6286b6bee53a51946db6667e518ceec696622401bde98c30c7560880`.
- Coverage: 10 / 10 cells and 7 / 7 non-reference variants.
- Simulations executed: 0.
- Task 018 started: No.
- Task 017Q: Deferred.

## Validation and closeout

- `uv run pytest`: 250 passed, 1 established CUDA opt-in skip.
- `uv run python -m compileall src scripts tests`: passed.
- `git diff --check`: passed.
- Post-score committed read-only checkpoint audit: PASS, 3,168 / 3,168, pending 0; all variants 396 / 396; all integrity failure counts zero.
- Production journal SHA-256 before scoring / after scoring: `878a2b79fa442c539d4f803819e3154b060b4fbb3c6c5a2cb5a6af464503190e` / `878a2b79fa442c539d4f803819e3154b060b4fbb3c6c5a2cb5a6af464503190e` (identical).
- Sidecar inventory SHA-256 before scoring / after scoring: `a24561d152e6acb9761c0b306d7a0158d487ce35e114ef02b543647326208553` / `a24561d152e6acb9761c0b306d7a0158d487ce35e114ef02b543647326208553` (identical).
- No simulation was executed. Task 018 was not started. Task 017Q remains deferred. No tag or release was created.

Git commit and push verification are recorded in the final Task 017L closeout message.
