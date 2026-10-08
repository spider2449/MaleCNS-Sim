# Git preservation of remaining workspace files

Date: 2026-10-08.
Authorization: the user requested handling the remaining Git files after the
flight coupling commit 80d7b2e42c88119ad8fc1b74fd2de20ebe748fef.

## Scope

Commit the eight previously preserved untracked files without changing their
contents: the A025 stopped-development evidence, A025 validation plan, v0.4.0
publication record, deep research report, and four A025 development scripts.
The historical exclusion of the research report from artifact candidates stays
in force; preserving it in Git does not admit it into an artifact/build contract.
This new Git-only authorization does not resume A025 or repeat publication.

## Checks and limits

The evidence JSON parsed and retains A025-CONTRACT-VIOLATION. All four scripts
passed AST parsing under the existing source firewall without being executed.
Check the staged diff and whitespace before committing, then verify final status.
No source data, artifact build, tests of A025 execution routes, dependency
installation, GPU workload, tag, or release operation is part of this task.
The research report is preserved as incoming notes; its scientific claims and
embedded conversation citations were not revalidated for this Git-only commit.
No prior worktree, stash, historical evidence, or release identity is rewritten.
