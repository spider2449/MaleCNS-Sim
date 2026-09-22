# Task 017R - Recover Preregistered v0.3 Robustness Execution

Status: TECHNICAL RECOVERY IMPLEMENTED. The complete Task 017 scientific matrix
was not executed by Task 017R. The current scientific classification remains
`INDETERMINATE` and no sensitivity or invariance claim is made. Final execution
state: `BLOCKED_EXECUTION_BUDGET`.

## Phase 0 - preserved failed execution

- Authoritative starting HEAD: `77f0c1110df766d93198275845e29749e53c9d04`.
- Historical report preserved at
  `docs/plans/2026-09-22-task-017-execute-v0.3-mechanism-robustness.md`.
- Historical report SHA-256:
  `0CC1B4D53B007C21A2FD10F8377C4FA1C048612E6067009CCE967A7AE0C3F97E`.
- Incomplete result digest preserved as
  `cf1f2fe16e3b7a895a89d2515f60762aa41ef22eb55f4bb99695f6f2716d67ea`.
- Task 011 digest: `fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`.
- Task 016 specification fingerprint:
  `2ecfe9ffca858a404b755a2bd4f34c88ed509718bee7f296e8fdcc5eb909e1d6`.

The historical report and incomplete derived JSON were not deleted or
reinterpreted.

## Phase 1 - measured budget diagnosis

Timing-only probes did not inspect scientific effects, rates, classifications,
or partial numerical outputs.

| Component | Measured time |
| --- | ---: |
| Prepared cache load | 1.529822 s |
| CUDA graph preparation/upload | 3.778136 s |
| Task 008 identity load | 3.018132 s |
| Frozen schedule construction, both sides and 30 trials | 0.976405 s |
| CUDA full untraced batch of 30 | 89.247537 s |
| V1 CUDA full untraced batch of 30 | 94.260090 s |
| CUDA traced batch of 3 | 27.681141 s |
| CPU 20 ms traced gate | 1.482484 s |
| Bounded real-graph CPU/CUDA technical gate (10 ms, including setup/replay) | 263.36 s |
| Host prepared graph memory | 998,865,328 bytes |

The failed run therefore exhausted its 30-minute wall-clock budget because the
current Task 017 runner executed the full graph at approximately 0.336
untraced trials/s and approximately 0.108 traced trials/s, while the prior
estimate assumed 4.13 trials/s. The runner also rebuilt schedules per variant,
uploaded a graph per variant, repeated full validation replays per variant,
and had no persisted unit boundary. This is an orchestration and measured
throughput mismatch, not a scientific stopping result.

The timing-only V1 probe measured approximately 0.318 full untraced trials/s,
so the representative alternative did not materially improve the budget.

A six-trial independent-mask CUDA probe was technically valid but slower:
21.472256 s untraced and 28.874065 s traced. The capability remains available
for deterministic independent batching, while the matrix runner uses
candidate/side batches for better throughput and checkpoint granularity.

## Phase 2 - implementation audit

Reviewed Task 017 files:

- `src/malecns_sim/dynamics/lif.py`
- `src/malecns_sim/dynamics/cuda.py`
- `src/malecns_sim/analysis/task017.py`
- `scripts/run_task017.py`
- `tests/test_task017.py`
- the preserved historical Task 017 report above

The active-CPU silencing implementation remains valid: default reference
execution is unchanged, while silenced neurons retain input and state updates
and only outgoing event scheduling is suppressed. Synthetic CPU replay and
trace invariance pass. The seven variants, candidates, schedules, thresholds,
compatibility rules, topology, sugar populations, and MN9 identities remain
literal and unchanged.

## Phases 3-6 - checkpoint and stage design

Task 017R adds an append-only JSONL checkpoint journal with compressed NPZ
result sidecars. Each scientific unit is keyed by:

`variant_id, candidate_id, stimulus_side, trial_index, analysis_kind`

The unit record stores effective model parameters, graph/cache/sign
fingerprints, candidate and stimulus identity, trial seed, schedule fingerprint,
duration, timestep, input weight, silencing semantics, and trace schema.
Reuse requires exact checkpoint identity and unit fingerprint matches. Missing
artifacts, mismatches, duplicate records, and duplicate execution attempts
fail closed. Canonical result records are merged by deterministic key order,
independent of execution order.

The four persisted analysis kinds are the Task 010 baseline and intervention
and the Task 011 baseline-trace and intervention-trace units. The exact ledger
contains 3,168 expected units, with completed, missing, duplicate, invalid
technical, per-variant, and per-analysis counts.

Stage A executes and persists raw backend-neutral results. Stage B requires the
exact 3,168-unit complete and technically valid ledger. Stage C is unreachable
unless that gate passes; an incomplete or invalid matrix remains
`INDETERMINATE` and its scientific cells remain explicitly unassessed.

The runner now reuses an identity-matched CUDA graph for variants with the
same effective graph and reweights frozen schedules without regenerating event
times or seeds. Candidate/side batches remain the performance path, while
checkpoint writes retain individual trial recovery boundaries.

Technical micro-validation used synthetic fixtures and did not inspect MN9
effects.

## Phase 7-8 - recovery estimate

The measured current workload implies approximately 8,568 seconds (142.8
minutes) for the 2,880 Task 010-style trials and approximately 2,657 seconds
(44.3 minutes) for the 288 trace trials, or approximately 11,225 seconds
(187.1 minutes) before CPU validation, checkpoint I/O, and repeated immutable
setup. The exact current throughput estimate is therefore not compatible with
the preregistered 30-minute budget. VRAM was not increased or used
concurrently; the measured prepared host graph was 998,865,328 bytes and the
existing CUDA memory plan remains sequential. A later complete execution must
resume from the checkpoint and must re-estimate after any further
orchestration-only optimization.

The bounded real-graph technical gate alone took 263.36 s. Repeating that
measured lower-duration gate for eight variants would already add about 35.1
minutes; the preregistered 1000 ms CPU full-graph checks are not cheaper by
assumption and were not extrapolated from scientific outputs.

Task 017R does not execute the complete matrix and does not alter the
preregistration to fit the measured budget.

## Phase 9-10 - validation

- `uv run pytest`: 193 passed, 1 skipped.
- Bounded real-graph CPU/CUDA technical gate: `1 passed in 263.36s`.
- `uv run python -m compileall src scripts tests`: passed.
- `git diff --check`: passed.
- Task 011 digest unchanged: confirmed above.
- Task 016 fingerprint unchanged: confirmed above.

No partial scientific interpretation occurred. No Task 018 work started.

## Delivery boundary

The recovery implementation was committed as
`bcd16d5406ce507ac6804a56b484c28f9ade3135` with message
`feat: make robustness matrix execution resumable` and pushed to `origin/master`.
At that verification point, local HEAD, tracking `origin/master`, and live
remote `origin/master` all equaled that commit. The worktree was clean, the
stash was empty, no tag pointed at the commit, and no release or Task 018 work
occurred. No derived JSON checkpoint or robustness result was committed under
the existing `data/derived` policy.
