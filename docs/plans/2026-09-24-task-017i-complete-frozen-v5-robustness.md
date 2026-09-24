# Task 017I - Complete Frozen V5 Robustness Variant

## Scope

Complete only the frozen `V5_WEIGHT_LOW` variant, with an anatomical synapse
weight of `0.200 mV`, using the existing deterministic checkpoint and resume
system. Execute bounded batches through `scripts/run_task017.py` with
`--variant V5 --analysis all`; do not modify Task 016, Task 011, candidates,
stimuli, trials, schedules, scoring rules, or runtime source. Do not inspect or
interpret V5 scientific outcomes, score robustness provisionally, start V6, or
start Task 018.

## Preconditions

- Confirm local `HEAD`, `origin/master`, and live remote `master` all equal
  `621545705d0c21c0163de490ff016aca6ad50f30`.
- Confirm a clean worktree and empty stash.
- Audit exactly `1,980` valid checkpoint units and sidecars; validate unit
  fingerprints and result digests; require zero duplicates, zero technical
  invalids, no missing sidecars, and no unreferenced sidecars.
- Confirm checkpoint fingerprint
  `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`, Task
  016 fingerprint
  `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`, and
  Task 011 digest
  `fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`.

## Execution and closeout

Use bounded resumable invocations with a 30-minute execution budget. Audit all
checkpoint records, result digests, and sidecar references after each completed
invocation. Stop when V5 reaches `396 / 396`, with V6 and V7 untouched. Keep
scientific status `INDETERMINATE` and do not perform scientific scoring or
interpretation.

Run `uv run pytest`, `uv run python -m compileall src scripts tests`, and
`git diff --check`. Record the technical ledger, integrity fingerprints,
timing, and test results in the companion report. If source code remains
unchanged, commit only these two documentation files as
`docs: record Task 017I V5 execution`, push, and verify local, tracking, and
live remote `master` equality, a clean worktree, and empty stash.

## Expected completion

The ledger should advance from `1,980 / 3,168` to `2,376 / 3,168`. R0-V5
should each be `396 / 396`; V6-V7 should remain `0 / 396`. Expected per-analysis
totals are Task 010 baseline `360 / 480`, Task 010 intervention `1,800 / 2,400`,
Task 011 baseline trace `36 / 48`, and Task 011 intervention trace `180 / 240`.
