# Task 017G - Complete Frozen V3 Robustness Variant

## Scope

Continue Task 017 only by completing the frozen `V3_TAU_SYNAPSE_FAST`
variant (`tau_synapse = 2.5 ms`). Preserve the Task 016 specification,
Task 011 digest, candidates, sides, trials, schedules, stimulus definitions,
model topology, classification logic, thresholds, scoring rules, and all
scientific interpretation boundaries. Do not start V4 or Task 018.

## Starting integrity state

- Starting `HEAD`, `origin/master`, and live remote `master`: `5338a4dfb122f743eaf1ec7e8a9387fb9877086d`.
- Worktree clean; stash empty.
- Ledger: `1,188 / 3,168`.
- R0, V1, and V2: `396 / 396` each.
- V3-V7: `0 / 396` each.
- Checkpoint: `1,188` valid referenced units, `1,188` sidecars, no missing or stale sidecars, zero duplicates, zero technical invalids.
- Task 016 fingerprint: `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`.
- Task 011 digest: `fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`.
- Checkpoint fingerprint: `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`.
- Scientific status: `INDETERMINATE`.

The existing journal's final complete record lacked terminal JSONL framing.
Only the terminal newline was repaired; no record or sidecar was regenerated.

## Execution

Use the existing bounded/resumable runner with `--variant V3 --analysis all`.
The execution is capped to V3 and must stop at `396 / 396`. After each
bounded batch, verify monotonic completion, checkpoint identity, referenced
sidecars, duplicate count, technical validity, parameter and fingerprint
identity, CPU/CUDA equivalence, and trace invariance. Do not inspect or score
scientific effects from partial results.

## Completion and validation

The final expected ledger is `1,584 / 3,168`, with V3 at `396 / 396` and V4-V7
untouched. Expected per-analysis totals are:

| Analysis | Completed |
| --- | ---: |
| Task 010 baseline | 240 / 480 |
| Task 010 intervention | 1,200 / 2,400 |
| Task 011 baseline trace | 24 / 48 |
| Task 011 intervention trace | 120 / 240 |

Run `uv run pytest`, `uv run python -m compileall src scripts tests`, and
`git diff --check`. Record timing components only where directly observable.
Commit and push only this plan/report documentation after validation. Do not
tag, release, begin V4, or start Task 018.
