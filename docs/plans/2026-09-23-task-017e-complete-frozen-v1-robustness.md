# Task 017E - Complete Frozen V1 Robustness Variant

## Scope

Resume the existing Task 017 checkpoint and complete only the frozen
`V1_TAU_MEMBRANE_FAST` variant. Preserve the Task 016 specification, Task 011
digest, frozen candidates, stimuli, schedules, trials, thresholds, topology,
technical gates, and scientific interpretation boundary.

## Starting state

- Total ledger: 792 / 3,168.
- R0: 396 / 396.
- V1: 396 / 396.
- V1 remaining: 0.
- V2-V7: 0 / 396 each.
- Duplicates: 0.
- Technical invalids: 0.
- Scientific status: `INDETERMINATE`.

## Execution

- Use bounded atomic batches restricted to V1 and the four frozen analysis kinds.
- After every batch, validate checkpoint identity and sidecars, duplicate count,
  technical invalid count, Task 016 fingerprint, ledger monotonicity, and the
  absence of partial robustness scoring.
- Record setup/gate time, scientific execution time, units/hour, and checkpoint
  I/O timing for each bounded batch where observable.
- Stop at V1 completion. Do not start V2 or Task 018.

## Completion gate

Report the complete V1 ledger, per-analysis totals, checkpoint fingerprint,
duplicates, technical invalids, V1 steady-state throughput, validation results,
and final worktree/stash state. Do not interpret V1 scientific outcomes.
