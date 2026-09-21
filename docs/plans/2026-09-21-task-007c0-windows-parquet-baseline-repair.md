# Task 007c0 — Windows Parquet Baseline Repair

## Goal

Resolve the pre-existing Windows PyArrow/pandas parquet-write failure without changing scientific behavior, and establish a clean passing baseline before Task 007c GPU work.

## Scope

- Verify the actual interpreter and dependency versions used by `uv run`.
- Reproduce the exact Task 006 failure and isolate it with a focused parquet matrix.
- Apply the smallest semantically neutral repair supported by the evidence.
- Add focused round-trip regression coverage.
- Run the full baseline checks and commit only Task 007c0 changes.

## Boundaries

- Do not implement GPU code.
- Do not restore or modify the paused Task 008 stash.
- Do not broadly upgrade or downgrade dependencies.
- Do not push or tag.
