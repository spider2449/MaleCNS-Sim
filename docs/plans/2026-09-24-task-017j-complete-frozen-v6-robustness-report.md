# Task 017J - Frozen V6 Robustness Execution Report

## Result

V6 completed at `396 / 396`. The checkpoint advanced from `2,376 / 3,168` to
`2,772 / 3,168` (`87.5%`). V7 remains untouched at `0 / 396`. Scientific
status remains `INDETERMINATE`. No V6 scientific outputs were inspected or
compared with R0-V5, and no causal robustness, mechanism robustness,
per-variant global support, or overall classification was scored.

## Integrity and ledger

- Starting `HEAD`: `ff48712b1a17fe3d17de7190e91fc84d5d3148fe`.
- Before execution, local `HEAD`, `origin/master`, and live remote `master`
  matched. The worktree was clean and the stash was empty.
- Starting checkpoint: 2,376 units; all 2,376 unit metadata fingerprints and
  result digests validated; 2,376 referenced and present sidecars; zero
  duplicates, technical invalids, missing sidecars, and unreferenced sidecars.
- Ending checkpoint: 2,772 units; all 2,772 unit metadata fingerprints and
  result digests validated; 2,772 referenced and present sidecars; zero
  duplicates, technical invalids, missing sidecars, and unreferenced sidecars.
- Checkpoint fingerprint remained
  `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`.
- Task 016 fingerprint remained
  `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`.
- Task 011 digest remained
  `fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`.

| Variant | Completion |
| --- | ---: |
| R0 | 396 / 396 |
| V1 | 396 / 396 |
| V2 | 396 / 396 |
| V3 | 396 / 396 |
| V4 | 396 / 396 |
| V5 | 396 / 396 |
| V6 | 396 / 396 |
| V7 | 0 / 396 |

| Analysis | Completion |
| --- | ---: |
| Task 010 baseline | 420 / 480 |
| Task 010 intervention | 2,100 / 2,400 |
| Task 011 baseline trace | 42 / 48 |
| Task 011 intervention trace | 210 / 240 |

## Batches and timing

Two bounded V6-only invocations used `--analysis all` and a 30-minute
execution budget each. The first allowed up to 396 units and delivered 235;
the second allowed the remaining 161 and delivered all 161. A full checkpoint
audit followed each invocation.

| Batch | Units | Runner elapsed (seconds) | Effective throughput (units/hour) |
| --- | ---: | ---: | ---: |
| 1 | 235 | 1,814.532 | 466.236 |
| 2 | 161 | 1,685.757 | 343.822 |
| Combined | 396 | 3,500.289 | 407.281 |

Runner elapsed includes its setup, technical gate, checkpoint work, and unit
execution. Separate setup/gate time, checkpoint I/O time, and backend-only
throughput are not exposed by the bounded runner. Reported throughput is
end-to-end runner throughput. The runner completed both batches with zero
technical-invalid units, no duplicate attempts, and no reported identity,
backend, determinism, or trace consistency failure.

## Validation and closeout

- `uv run pytest`: `214 passed, 1 skipped`; the skipped opt-in full-graph gate
  is `tests/test_task007c.py`.
- `uv run python -m compileall src scripts tests`: passed.
- `git diff --check`: passed.
- Source/scientific configuration change status: none; only this plan and
  report are intended for commit.
- Commit and push: documentation-only commit; final commit and remote
  verification are recorded by the final execution turn.
- Scientific status: `INDETERMINATE`.
- V7 and Task 018 were not started.
- Final state: `READY_TO_CONTINUE_TASK_017`.
