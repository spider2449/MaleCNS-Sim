# Task 017H - Frozen V4 Robustness Execution Report

## Result

V4 completed at `396 / 396`. The ledger advanced from `1,584 / 3,168` to
`1,980 / 3,168` (`62.5%` of the frozen matrix). V5-V7 were not started.
Scientific status remains `INDETERMINATE`; causal robustness, mechanism
robustness, and global support remain unscored. No partial scientific results
were interpreted or compared across variants.

## Requested report

1. Starting `HEAD`: `ad152ee37fe298fb2f5a005abd34388532d2225f`.
2. Starting ledger: `1,584 / 3,168`.
3. Ending ledger: `1,980 / 3,168`.
4. V4 completion: `396 / 396`.
5. Variant completion:

   | Variant | Completion |
   | --- | ---: |
   | R0 | 396 / 396 |
   | V1 | 396 / 396 |
   | V2 | 396 / 396 |
   | V3 | 396 / 396 |
   | V4 | 396 / 396 |
   | V5 | 0 / 396 |
   | V6 | 0 / 396 |
   | V7 | 0 / 396 |

6. Per-analysis totals:

   | Analysis | Completion |
   | --- | ---: |
   | Task 010 baseline | 300 / 480 |
   | Task 010 intervention | 1,500 / 2,400 |
   | Task 011 baseline trace | 30 / 48 |
   | Task 011 intervention trace | 150 / 240 |

7. Batches: three bounded V4-only invocations committed `220`, `158`, and `18`
   units. The ledger was audited after each invocation. All three technical
   gates passed. The gates checked CPU/CUDA equivalence, trace invariance, and
   deterministic replay; they did not stop on scientific outputs.
8. Timing (seconds):

   | Invocation | Setup/cache and other | Technical gate | Scientific backend | Checkpoint I/O | Wall |
   | --- | ---: | ---: | ---: | ---: | ---: |
   | 220 units | Not separately isolated | 704.851 | Not separately isolated | 4.603 | 1,814.127 |
   | 158 units | 336.931 | 756.122 | 703.807 | 6.129 | 1,802.988 |
   | 18 units | 385.909 | 711.189 | 118.568 | 3.557 | 1,219.223 |

   For the first invocation, the instrumentation's backend timer also included
   backend calls made inside the technical gate, so a non-overlapping setup
   and scientific-backend split is not available for that invocation. The
   latter two invocations have disjoint component timings. Across all three
   invocations, observed wall time was `4,836.339 s` (`80.606 min`).
9. Scientific-backend throughput from the two fully separated measurements
   (`176` units in `822.375 s`): `0.214014 units/s`, or `770.452 units/hour`.
10. Wall throughput for all V4 units across the three runner invocations:
    `0.081880 units/s`, or `294.768 units/hour`.
11. Duplicate count: `0`.
12. Technical invalid count: `0`.
13. Checkpoint health: healthy; `1,980` valid referenced units and `1,980`
    sidecars, no missing or unreferenced sidecars, and all record fingerprints
    and result digests valid.
14. Checkpoint fingerprint:
    `8328714e2353d380f9e2cee351839c9dd9cb42d4cf93b1721b2a18c39a439f63`.
15. Task 016 fingerprint:
    `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`.
16. Task 011 digest:
    `fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`.
17. Scientific status: `INDETERMINATE`; `1,980 / 3,168` units complete.
    Causal robustness, mechanism robustness, and global support remain
    unscored.
18. Pytest: `214 passed, 1 skipped` (`tests/test_task007c.py`; bounded
    full-graph gate opt-in).
19. Compileall: passed for `src scripts tests`.
20. `git diff --check`: passed.
21. Source-code-change status: no source or scientific-configuration changes.
    Only the Task 017H plan/report are intended for commit; ignored checkpoint
    data and sidecars remain uncommitted.
22. Commit/push status: the Task 017H plan and report were committed and
    pushed to `origin/master` as requested.
23. Local/remote `HEAD` equality: local `HEAD`, `origin/master`, and live
    remote `master` were equal after push.
24. Worktree/stash state: worktree clean; stash empty after push.
25. `READY_TO_CONTINUE_TASK_017`: V4 is complete. V5 requires a separate
    authorization. Task 018 was not started.

## Boundary

No partial scoring or cross-variant scientific comparison was performed.
Checkpoint data under `data/derived` remains ignored and uncommitted.
