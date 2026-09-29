# Task 017 V7 Filtered Checkpoint Audit

## Objective

Determine whether the existing 260 V7 Task 010 records match the committed filtered pending selection and bounded runner semantics. Preserve all checkpoint and result files during the audit.

## Audit steps

1. Verify the committed selector, runner append sequence, merge ordering, and relevant tests.
2. Reconstruct the 210-unit Task 010 batch and the 50-unit resume using unit keys only.
3. Audit V7 set membership, missing keys, journal order, checkpoint integrity, and delivery-ledger provenance.
4. If every gate passes, promote the 3,032-unit checkpoint state and create an external certified backup before further execution.
5. Run the requested test, compile, and diff checks without running scientific units.

## Constraints

Do not execute scientific units, alter or truncate the checkpoint, score results, pull, or start Task 018. Keep scientific status `INDETERMINATE`.

## Audit result — 2026-09-29

**Verdict: `VALID_FILTERED_EXECUTION_CHECKPOINT`.** The checkpoint remains scientifically `INDETERMINATE`.

### Selector and journal semantics

`pending_task017_unit_keys` builds the completed token set from checkpoint records, filters the preregistered expected matrix by selected variant and analysis, removes completed keys, and retains canonical order (`variant_id -> stimulus_side -> analysis_kind -> trial_index -> candidate_id`) within that filtered sequence. It does not require selected keys to form a prefix of the unfiltered global matrix. `Task017Checkpoint.put` appends in execution-call order and rejects duplicate keys; `records()` sorts by the canonical key tuple for consumers. Therefore a bounded filtered run may append valid Task 010 keys while canonical Task 011 predecessors remain pending. `test_task017_checkpoint_merge_order_is_independent` and `test_task017_bounded_budget_and_canonical_pending_resume` cover these behaviors.

### Reconstructed V7 batches

- Batch A selected 210 keys and matched the first 210 physical V7 journal entries exactly: LEFT baseline 30, LEFT intervention 150, RIGHT baseline 30.
- Batch B selected the next 50 keys and matched V7 journal entries 210–259 exactly. The final key is V7 `task010_intervention`, RIGHT, trial 9, candidate `512730`.
- The frozen Task 011 candidate order used by the runner is `10313`, `10135`, `12752`, `512730`, `43765`; the intervention execution loop sorts it to `10135`, `10313`, `12752`, `43765`, `512730` for trial batches.

### Set, merge, and integrity results

- V7 expected keys: 396. Observed keys: 260 unique; all belong to the expected set.
- The deterministic filtered selector returns exactly 136 pending V7 keys. Observed and pending sets are disjoint and their union is the full expected V7 set. The exact keys are recorded in `data/derived/task017-authoritative-execution-state.json` and the external backup manifest.
- Canonical `records()` serialization was identical when records were inserted in forward and reverse journal order. No dedicated standalone merge function exists; `records()` is the committed canonical merge operation covered by the order-independence test.
- Integrity: 3,032 journal units and 3,032 sidecars; 0 duplicate units, 0 orphan sidecars, 0 metadata fingerprint failures, 0 result digest failures, and 0 technical invalids. Task 016 fingerprint: `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`. Task 017 checkpoint fingerprint: `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`.

### Delivery provenance and backup

The delivery ledger arithmetic reconciles: `2,982 - 2,772 = 210`; the final invocation added 50 to reach 3,032. Its recorded selected analyses are `all`, so the report supports the unit counts and resulting keys but does not prove the final CLI used `--analysis task010`. The reconstructed filtered selection produces those same next 50 keys. No further command provenance is inferred.

The authoritative execution ledger is 3,032 / 3,168: R0–V6 each 396 / 396; V7 260 / 396; 136 V7 keys remain. Scientific status remains `INDETERMINATE`. No scientific units were executed and no scoring was performed.

A certified out-of-checkout export was created on C: at `C:\Users\spider.tp\Documents\MaleCNS-Sim-Backups\Task017-3032-8328714e-2026-09-29`. It contains the journal and all 3,032 sidecars; source and copy SHA-256 hashes match for all 3,033 files. Journal SHA-256: `d085103d4c2a0b2d68930670158912294472c09565a9479ac3290665a2138d00`. Backup manifest SHA-256: `3ed31e2de4ed4ca9ca147f0f2bf71b1706b7b6e754b21c92ca70d8d556b8463b`.

Validation: `uv run pytest` — 214 passed, 1 skipped; `uv run python -m compileall src scripts tests` — passed; `git diff --check` — passed. No scientific simulations, checkpoint edits, pulls, scoring, or Task 018 work were performed.
