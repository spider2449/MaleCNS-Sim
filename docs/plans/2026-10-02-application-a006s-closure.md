# Application Task A006S closure

Starting HEAD: `1a451afc70a4841a03c5687a2635c40fc6dde98f`.

## Plan

Verify the accepted worktree and Git identities, record manual acceptance, run the required local validation, commit the exact accepted implementation with this documentation, push master, and verify final identities and clean state. Do not change application behavior or start A007.

## Final acceptance and classification

Manual startup acceptance: **PASS**. The user explicitly reported `A006S UI 測試 OK` for the exact current worktree.

**A006S-LOCAL-SERVER-RELIABILITY-CERTIFIED**.
A006 remains **A6-COMPARISON-CERTIFIED**. A007 remains **NOT STARTED**.

ROOT CAUSE CONFIRMED: default fixed-port stale-listener / session ownership mismatch.
The existing fragment/sessionStorage token handling was not the remaining root cause.

Normal `uv run malecns-workbench` requests port 0, allowing the operating system to select an available loopback port, and prints the actual authenticated URL. Explicit `--port N` remains supported. Address reuse is disabled; Windows `SO_EXCLUSIVEADDRUSE` is applied before binding. An occupied fixed port fails clearly with exit status 1 rather than sharing a listener.

Each process has an independent non-secret server instance ID, port and secret session token. The instance ID is operational metadata, not authentication or scientific identity. Fragment/sessionStorage handling remains in place, including same-tab refresh, replacement fragments and blocked-storage fallback. Host validation, Origin validation, protected API authentication and mutating Origin requirements are preserved.

Manual acceptance certifies successful printed-URL opening, no stale session failure, authenticated same-tab refresh, second-server independence, no unexplained browser console errors, and clean Ctrl+C shutdown. Shutdown prints `MaleCNS workbench stopped.` and normal Ctrl+C produces no traceback. Server closure runs in `finally`.

Earlier recovery documents retain their historical observations and pending handoffs; this closure supersedes those pending statuses.

## Scientific boundary and next task

No scientific execution. Scientific runs = 0; Task017 units = 0; Task017Q executions = 0; raw-data downloads = 0; archive writes = 0. Historical scientific artifacts and `B:\MaleCNS-Archive` remain unchanged. Validation uses mocks and synthetic test fixtures, not scientific experiment runs. Active tracked GitHub Actions workflows = 0.

Package version remains `0.3.0`; `v0.3.0` peels to `a1a6651163840a982799b1fa82c1904e67f84660`. No tag, release or version mutation.

Exact next authorized task: **Application Task A007 — Robustness Evidence View & Sweep Orchestration**. It is not started by this closure.

## Closure validation

Targeted local-server/session tests: 12 passed. Targeted A003-A006/A006R tests: 40 passed. Full pytest: 319 passed, 1 skipped (opt-in real graph gate), 1 existing CUDA-path warning. compileall: PASS. Tracked integrity: PASS (9 tracked files and internal identities). git diff --check: PASS. uv build: PASS (sdist and wheel, version 0.3.0).

Accepted server, frontend and test SHA-256 hashes were unchanged during closure. No tracked artifacts/data differences; the B: archive recursive path, length, modification-time and attribute inventory was unchanged. Stash empty; no tracked GitHub Actions workflows. No scientific runs, raw-data downloads or archive writes were performed.

Commit message: `fix: make local workbench startup reliable`. The exact commit and post-push Git identities are recorded in the final closure report.
