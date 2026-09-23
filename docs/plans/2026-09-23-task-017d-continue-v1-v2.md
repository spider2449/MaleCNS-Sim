# Task 017D - Continue Frozen Robustness Matrix with V1 and V2

## Scope

Continue the existing Task 017 checkpoint from the completed R0 state. Preserve
the Task 016 specification, Task 011 digest, frozen variants, candidates,
stimuli, schedules, trials, thresholds, scoring rules, and scientific status.
Do not inspect or interpret scientific effects from partial results.

## Phase 0 - Baseline gates

- Verify local `HEAD`, `origin/master`, and the live remote `master` head agree.
- Verify a clean worktree and empty stash before execution.
- Validate the append-only checkpoint identity, all referenced result sidecars,
  unit metadata fingerprints, result digests, and the exact 396-unit R0 ledger.
- Verify zero duplicates and zero technically invalid units.
- Verify the Task 016 fingerprint and Task 011 digest remain unchanged.

## Phase 1 - V1

Execute only the frozen `V1_TAU_MEMBRANE_FAST` variant (`tau_m = 10 ms`) using
bounded resumable invocations. After each invocation, validate monotonic
completion, checkpoint integrity, duplicate count, and technical validity.

## Phase 2 - V2

If V1 completes cleanly, execute only the frozen `V2_TAU_MEMBRANE_SLOW` variant
(`tau_m = 30 ms`) with the same bounded checkpoint and validation rules. Stop
after complete atomic units if the available execution window is insufficient.

## Phase 3 - Timing and validation

Keep startup/cache, technical gates, scientific unit execution, and checkpoint
I/O timing separate where the runner exposes those measurements. Report
steady-state throughput separately from gate-dominated wall time. At delivery,
run `uv run pytest`, `uv run python -m compileall src scripts tests`, and
`git diff --check`.

## Stop and scientific boundary

Fail closed on fingerprint, parameter, schedule/stimulus, duplicate,
checkpoint, CPU/CUDA, trace-invariance, nondeterminism, nonfinite, or overflow
failures. Do not stop for scientific outcomes. Until all 3,168 units pass the
completeness gate, the scientific status remains `INDETERMINATE` and no
robustness or sensitivity scoring is computed. Do not start Task 018.
