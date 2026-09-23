# Task 017G - Frozen V3 Robustness Execution Report

## Result

V3 completed successfully. The Task 017 ledger advanced from `1,188 / 3,168`
to `1,584 / 3,168`. V3 is complete at `396 / 396`; V4-V7 were not started.
Scientific status remains `INDETERMINATE`; no partial robustness, mechanism,
causal, or global-support scoring was performed.

## Requested report

1. Starting `HEAD`: `5338a4dfb122f743eaf1ec7e8a9387fb9877086d`.
2. Starting ledger: `1,188 / 3,168`.
3. Ending ledger: `1,584 / 3,168`.
4. V3 completion: `396 / 396`.
5. Variant completion:

   | Variant | Completion |
   | --- | ---: |
   | R0 | 396 / 396 |
   | V1 | 396 / 396 |
   | V2 | 396 / 396 |
   | V3 | 396 / 396 |
   | V4 | 0 / 396 |
   | V5 | 0 / 396 |
   | V6 | 0 / 396 |
   | V7 | 0 / 396 |

6. Per-analysis totals:

   | Analysis | Completion |
   | --- | ---: |
   | Task 010 baseline | 240 / 480 |
   | Task 010 intervention | 1,200 / 2,400 |
   | Task 011 baseline trace | 24 / 48 |
   | Task 011 intervention trace | 120 / 240 |

7. Batches executed: two bounded V3-only invocations, committing `368` units
   and then `28` units. No V4-V7 work was selected.
8. Timing:

   | Component | First invocation |
   | --- | ---: |
   | Setup/cache | 355.781 s |
   | Technical gate | 144.943 s |
   | Scientific backend | 1,299.709 s |
   | Checkpoint I/O | 4.830 s |
   | Total wall | 1,807.502 s |

   The 28-unit continuation reported `656.339 s` total wall time. Its internal
   component timings were not exposed separately by the command-line runner;
   no unmeasured allocation is claimed. Aggregate wall time for all 396 V3
   units was `2,463.841 s`.

9. Measured scientific-backend throughput: `0.283140 units/s`,
   `1,019.305 units/hour` during the instrumented 368-unit invocation.
10. Wall throughput: first invocation `0.203596 units/s`,
    `732.945 units/hour`; continuation `0.042661 units/s`,
    `153.579 units/hour`; aggregate `0.160725 units/s`,
    `578.609 units/hour`.
11. Duplicate count: `0`.
12. Technical invalid count: `0`.
13. Checkpoint health: healthy; `1,584` valid referenced units and `1,584`
    sidecars, exact reference matching, no missing or stale sidecars, and all
    result digests and metadata fingerprints valid.
14. Checkpoint fingerprint:
    `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`.
15. Task 016 fingerprint:
    `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`.
16. Task 011 digest:
    `fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`.
17. Scientific status: `INDETERMINATE`; the matrix is incomplete at 50%.
18. Pytest: `214 passed, 1 skipped` (`tests/test_task007c.py` real-gate skip).
19. Compileall: passed for `src scripts tests`.
20. Git diff check: passed.
21. Source-code-change status: no source or scientific configuration change.
    Only this Task 017G plan/report is repository work; ignored checkpoint
    data and sidecars remain uncommitted.
22. Commit/push status: pending final documentation commit and push.
23. Local/remote HEAD equality before documentation: local, `origin/master`,
    and live remote `master` were equal at the starting HEAD. Final equality
    will be verified after push.
24. Worktree/stash state before documentation: clean worktree and empty stash.
    Final state will be verified after push.
25. `READY_TO_CONTINUE_TASK_017`: V3 is complete and the remaining frozen
    matrix is technically ready for a separately authorized continuation.

## Boundary

No V4 execution was started. Task 018 was not started. No scientific effects,
silence, saturation, null effects, reversed effects, or mechanism evidence were
interpreted.
