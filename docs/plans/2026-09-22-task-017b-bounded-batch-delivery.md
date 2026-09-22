# Task 017B - Bounded Batch Delivery for the Preregistered Robustness Matrix

Status: IMPLEMENTATION AND DELIVERY PLAN.

## Scope

Add resumable, deterministic, bounded local delivery controls to the already
frozen Task 017 runner. Preserve the Task 016 specification, the eight literal
variants, candidates, schedules, trials, identities, thresholds, topology,
sign policies, and scientific interpretation boundary.

## Execution plan

1. Recheck the authoritative Git state, Task 011 digest, Task 016 fingerprint,
   and required Task 016/017/017R reports.
2. Define one canonical expected-unit ordering and expose variant, analysis,
   maximum-unit, and maximum-runtime selection controls.
3. Ensure each scientific unit is durably written before the next unit starts;
   stop only between units and reuse prior units only after exact fingerprint
   verification.
4. Add tests for bounded resume/merge equivalence, incomplete-tail recovery,
   identity mismatches, duplicate rejection, and stale sidecars.
5. Run the bounded durability suite and repository validation, then execute one
   deliberately small real Task 017 checkpoint batch without inspecting effects.
6. Report only technical progress and completeness evidence; keep the
   scientific status INDETERMINATE and do not begin Task 018.

## Delivery boundary

Only execution infrastructure, tests, and this plan are in scope. Derived
checkpoint/result data remains uncommitted unless repository policy explicitly
requires it. No variants, scientific parameters, schedules, trials, scoring
rules, or conclusions are changed.
