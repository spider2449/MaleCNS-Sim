# A006S graceful console shutdown

Scope: shutdown UX only; preserve existing uncommitted A006S work. Catch KeyboardInterrupt around serve_forever, print a concise stopped message, and always call server_close. No startup, token, port, security, run-manager, or scientific contract changes. No commit or push.

Validation plan: a mocked serve_forever raises KeyboardInterrupt without signal infrastructure; assert normal return, cleanup, stopped output, and empty stderr. Run targeted server/session tests, full pytest, compileall, tracked integrity, diff check, and build. Return to manual startup acceptance. No scientific runs.

Validation completed: targeted local-server/session tests 12 passed; full pytest 319 passed, 1 skipped, 1 existing CUDA-path warning. compileall, tracked integrity (9 files), git diff --check, and uv build passed. Mocked interruption returned normally, called server_close once, printed the stopped message, and emitted no stderr. Real scientific runs: 0. No commit or push. Manual startup acceptance remains pending.

## Final closure reference

Manual startup acceptance PASS; A006S-LOCAL-SERVER-RELIABILITY-CERTIFIED. See [A006S closure](2026-10-02-application-a006s-closure.md) for the final correction and acceptance. Earlier observations above remain historical.
