# Task 017J - Complete Frozen V6 Robustness Variant

## Scope

Complete only the frozen Task 017 V6 robustness variant (`v_threshold_mV =
-44`). Continue the existing deterministic, append-only checkpoint in bounded
batches. Do not change any scientific inputs, configurations, compatibility
or scoring rules. Do not inspect or compare V6 scientific outcomes, score
robustness, start V7, or start Task 018.

## Preconditions

- Confirm local `HEAD`, `origin/master`, and live remote `master` match the
  authorized starting commit.
- Confirm a clean worktree and empty stash.
- Audit all 2,376 starting units, their metadata fingerprints and result
  digests, and every referenced sidecar. Require zero duplicates, invalid
  technical units, missing sidecars, and unreferenced sidecars.
- Confirm the Task 017 checkpoint fingerprint, Task 016 specification
  fingerprint, and Task 011 result digest against the frozen values in the
  companion report.

## Execution

Use `scripts/run_task017.py --variant V6 --analysis all` with bounded unit
counts and a 30-minute execution budget for each invocation. After each
invocation, audit the complete journal and all sidecars before resuming. Stop
when V6 is 396 / 396. Keep V7 at 0 / 396 and retain scientific status
`INDETERMINATE`.

## Validation and delivery

Run `uv run pytest`, `uv run python -m compileall src scripts tests`, and
`git diff --check`. Record the ledger, technical integrity, fingerprints,
timing, and validation evidence in the companion report. If source code and
scientific configuration remain unchanged, commit only this plan and report,
push, and verify local, tracking, and live remote `master` equality, a clean
worktree, and an empty stash. Do not tag or release.

## Expected completion

The ledger advances from 2,376 / 3,168 to 2,772 / 3,168 (87.5%). R0 through
V6 are each 396 / 396; V7 remains 0 / 396. Expected totals are Task 010
baseline 420 / 480, Task 010 intervention 2,100 / 2,400, Task 011 baseline
trace 42 / 48, and Task 011 intervention trace 210 / 240. No causal or
mechanism robustness scoring is allowed at this partial matrix completion.
