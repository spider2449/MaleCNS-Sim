# Task 017I - Frozen V5 Robustness Execution Report

## Result

V5 completed at `396 / 396`. The ledger advanced from `1,980 / 3,168` to
`2,376 / 3,168`. V6 and V7 remain untouched at `0 / 396`. Scientific status
remains `INDETERMINATE`; no V5 scientific outcomes were inspected or
interpreted, and no provisional robustness scoring was performed.

## Integrity and ledger

- Starting `HEAD`: `621545705d0c21c0163de490ff016aca6ad50f30`.
- Before execution, local `HEAD`, `origin/master`, and live remote `master`
  matched. The worktree was clean and the stash was empty.
- Starting checkpoint: `1,980 / 3,168` valid units and sidecars; zero
  duplicates and zero technical invalids.
- Ending checkpoint: `2,376 / 3,168` valid units and sidecars; all unit
  fingerprints and result digests validated; zero missing or unreferenced
  sidecars; zero duplicates; zero technical invalids.
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
| V6 | 0 / 396 |
| V7 | 0 / 396 |

| Analysis | Completion |
| --- | ---: |
| Task 010 baseline | 360 / 480 |
| Task 010 intervention | 1,800 / 2,400 |
| Task 011 baseline trace | 36 / 48 |
| Task 011 intervention trace | 180 / 240 |

## Batches and timing

Two bounded V5-only resumable invocations completed `260` and `136` units.
Each used `--analysis all`; the first allowed up to `396` units and the second
up to the `136` remaining units. Each invocation used a 30-minute execution
budget and was followed by a full checkpoint audit.

| Batch | Units | Runner elapsed (seconds) | Effective throughput (units/hour) |
| --- | ---: | ---: | ---: |
| 1 | 260 | 1,812.748 | 516.343 |
| 2 | 136 | 1,509.726 | 324.297 |
| Combined | 396 | 3,322.474 | 429.078 |

Runner elapsed totals `55.375` minutes. The bounded delivery payload exposes
end-to-end invocation elapsed time, but does not expose a separate scientific
backend timer; backend-only throughput is therefore unavailable. The reported
throughput is end-to-end unit delivery throughput and includes runner setup,
technical gates, checkpoint work, and unit execution.

## Verification and closeout

- `uv run pytest`: `214 passed, 1 skipped`; the skipped opt-in full-graph gate
  is `tests/test_task007c.py`.
- `uv run python -m compileall src scripts tests`: passed.
- `git diff --check`: passed.
- Source-code change status: no source or scientific-configuration changes;
  only this plan and report are intended for commit.
- Commit and push: the plan and report were committed and pushed with message
  `docs: record Task 017I V5 execution`; final repository identity is verified
  after push.
- Scientific status: `INDETERMINATE`.
- Task 018 was not started; V6 was not started.
- Final state: `READY_TO_CONTINUE_TASK_017`.
