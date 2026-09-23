# Task 017F - Complete Frozen V2 Robustness Variant

## Scope

Resume the existing Task 017 checkpoint and execute only the frozen
`V2_TAU_MEMBRANE_SLOW` variant with `tau_m = 30 ms`. Preserve the Task 016
specification, Task 011 digest, frozen candidates, stimuli, schedules, trials,
thresholds, topology, technical gates, checkpoint identity, and the scientific
interpretation boundary.

## Starting state

- Total ledger: 792 / 3,168.
- R0: 396 / 396.
- V1: 396 / 396.
- V2: 0 / 396.
- Duplicates: 0.
- Technical invalids: 0.
- Scientific status: `INDETERMINATE`.

## Execution

- Use bounded atomic invocations restricted to V2 and all four frozen analysis
  kinds.
- Do not use R0 or V1 scientific outputs to alter V2 execution.
- Retain and report technical invalids according to Task 016.
- Measure technical gate/setup time, scientific backend time, checkpoint I/O,
  and wall-clock throughput separately where observable.
- Validate checkpoint identity, sidecars, duplicate count, technical validity,
  Task 016 fingerprint, and ledger monotonicity after each batch.

## Completion gate

- Stop only after V2 reaches 396 / 396, or report the bounded stopping point if
  execution is externally interrupted.
- Run `uv run pytest`, `uv run python -m compileall src scripts tests`, and
  `git diff --check` after completion.
- Report technical ledger state only; scientific status remains `INDETERMINATE`.
- Do not start V3 or Task 018.
