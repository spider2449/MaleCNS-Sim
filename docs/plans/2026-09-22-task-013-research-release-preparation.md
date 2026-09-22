# Task 013 - MaleCNS-Sim Research Release Preparation

## Scope

Prepare the validated MaleCNS-Sim research checkpoint for a reproducible
release without changing scientific results, model behavior, candidate
definitions, or interpretation. Task 011 remains the current scientific
endpoint and Task 012 remains the documentation/reproducibility closure.

No new experiment, result regeneration, tag, or published release is in
scope.

## Validation record

Completed before commit:

- `uv run pytest`: `183 passed, 1 skipped` in 6.13 s.
- `uv run python -m compileall src scripts tests`: PASS.
- `git diff --check`: PASS.
- Task 011 digest: exact accepted digest retained.
- Scientific source, tests, provenance, and derived-result paths: no diff.

## Required starting state

- Authoritative starting HEAD:
  `4fa0d2d9f977ca0f307b0490345b466b8c9fee91`
- Local branch and expected remote branch: `master` / `origin/master`
- Worktree clean and stash list empty
- Accepted Task 011 digest:
  `fbe9b0a7f138fdbdea7a0a8cf22e8493596a9299dd9b9f6c3537c48f550dece4`
- Expected validation baseline: `183 passed, 1 skipped`

## Deliverables

- `docs/MALECNS_RELEASE_GATE.md`
- This Task 013 plan
- Release-facing README and metadata corrections only where required for
  reproducibility or truthful release description

## Release-facing audit

Review the README, project metadata, dependency groups, checkpoint document,
validated-analysis scripts, test and compileall instructions, ignored raw and
derived-data policy, license/provenance metadata, and existing version state.
Keep the full curated graph primary and preserve all scientific claim
boundaries from the authoritative checkpoint.

## Reproducibility record

Document CPU-only and optional CUDA/CuPy installation, validation commands,
raw-data verification, prepared-cache creation/loading, and the exact scripts
and prerequisites for Tasks 006 and 008-011. Do not claim a single-command
reproduction where the repository does not provide one.

## Version decision

The repository has an explicit project version `0.1.0`, with no tags or prior
release history establishing another convention. The additive validated
research checkpoint is prepared as version `0.2.0`; only normal project
metadata and its lockfile entry are updated.

## Validation and history boundary

Run:

```text
uv run pytest
uv run python -m compileall src scripts tests
git diff --check
```

Verify the Task 011 digest, scientific source/result state, complete reviewed
diff, clean worktree, empty stash, local/remote equality, and live remote HEAD.
Commit only reviewed Task 013 release-preparation files, push `master`, and
stop. Do not tag, create a release, or start Task 014.
