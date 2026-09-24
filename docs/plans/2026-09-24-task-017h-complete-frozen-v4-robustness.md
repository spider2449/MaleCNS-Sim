# Task 017H - Complete Frozen V4 Robustness Variant

## Scope

Continue Task 017 only by completing the frozen `V4_DELAY_SHORT` variant
(`synaptic_delay_ms = 1.0`). Preserve Task 016, Task 011, candidates, sides,
trials, schedules, stimuli, topology, LIF reference defaults, classification
logic, robustness thresholds, and interpretation boundaries. Do not start V5
or Task 018.

## Starting integrity state

- Starting `HEAD`, `origin/master`, and live remote `master`:
  `ad152ee37fe298fb2f5a005abd34388532d2225f`.
- Worktree clean; stash empty.
- Ledger: `1,584 / 3,168`; R0-V3 each `396 / 396`; V4-V7 each `0 / 396`.
- Checkpoint: `1,584` valid referenced units and sidecars, no missing or
  unreferenced sidecars, zero duplicates, zero technical invalids.
- Task 016 fingerprint:
  `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`.
- Task 011 digest:
  `fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`.
- Checkpoint fingerprint:
  `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`.
- Scientific status: `INDETERMINATE`.

## Execution

Use only the existing bounded/resumable runner with `--variant V4 --analysis
all`. Each invocation is capped at 30 minutes. Audit all records, result
digests, checkpoint references, and sidecars after every completed invocation.
Stop after V4 reaches `396 / 396`; do not score or compare scientific
outcomes.

## Expected completion

The target ledger is `1,980 / 3,168`, with R0-V4 at `396 / 396` and V5-V7
untouched. Expected analysis totals are Task 010 baseline `300 / 480`, Task
010 intervention `1,500 / 2,400`, Task 011 baseline trace `30 / 48`, and Task
011 intervention trace `150 / 240`.

Run `uv run pytest`, `uv run python -m compileall src scripts tests`, and
`git diff --check`. Commit and push only the Task 017H plan and report. Do not
tag, release, start Task 018, or begin V5.
