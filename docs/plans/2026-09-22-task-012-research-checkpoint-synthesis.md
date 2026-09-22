# Task 012 - Research Checkpoint Synthesis and Reproducibility Closure

## Scope

Create the authoritative research-state checkpoint for validated Tasks 004-011.
This task is documentation and reproducibility closure only. It does not change
the model, LIF parameters, neurotransmitter/sign policy, sugar populations,
MN9 identity, candidate set, or derived scientific-result artifacts. It does
not run a new perturbation study or start Task 013.

## Required preflight

- Confirm HEAD is `ae589a9b9726fa2510fff8f32658bc02176f66a3`.
- Confirm the local branch and expected remote branch tip match the supplied
  authoritative HEAD.
- Confirm a clean worktree and an empty stash list.
- Inspect the existing Task 004-011 plans and record only already validated
  values.

## Deliverables

- `docs/MALECNS_RESEARCH_CHECKPOINT.md`
- This plan file, as the required Task 012 execution record.

The checkpoint will state the scientific scope and nonclaims, graph and sign
state, reference LIF engine, Shiu reproduction, sugar/MN9 identity, GPU gate,
Tasks 008-011 results, reproducibility ledger, open questions, and the Task 011
stopping point.

## Validation and closure

Run the requested validation without regenerating any scientific-result
artifact:

```text
uv run pytest
uv run python -m compileall src scripts tests
git diff --check
```

Confirm the Task 011 digest remains
`fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`, no
parameter/candidate/model-policy files changed, and no result artifact changed.
Inspect the diff, commit only the documentation files with
`docs: consolidate MaleCNS research checkpoint`, push the current remote
branch, and verify local HEAD equals the remote branch HEAD. Do not create a
tag.
