# Task 017K - Complete Frozen V7 Robustness Variant

## Scope

Complete only frozen Task 017 variant V7 (`ConservativeSignPolicy`) from the
verified 2,772 / 3,168 checkpoint to 3,168 / 3,168. Do not change scientific
inputs or rules, inspect outcomes for robustness, score, or start Task 018.

## Integrity gate

Before execution, verify the specified starting commit and remotes, clean
worktree, empty stash, checkpoint journal and all unit sidecars, unit and
result digests, Task 016 fingerprint, and Task 011 digest. Do not initialize,
regenerate, replace, or repair the checkpoint. If the checkpoint cannot be
verified, stop before running the execution command and record the blocker.

## Execution and closure

If integrity passes, execute V7 with the existing deterministic bounded runner
in atomic batches, auditing the complete journal and sidecars after every
batch. Preserve the preregistered inputs and report exact per-analysis and
per-variant totals. Audit the full matrix before any future scoring; this task
does not apply scoring rules. On complete technical validity, create the
deterministic complete-matrix manifest and digest for Task 017L.

Run `uv run pytest`,
`uv run python -m compileall src scripts tests`, and `git diff --check`.
Record results in the companion report. Commit documentation only if no source
or scientific configuration changed, then push and verify final repository
state. Do not tag or release.
