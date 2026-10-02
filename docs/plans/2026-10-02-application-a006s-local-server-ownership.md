# A006S local startup and session ownership correction

Starting HEAD: `1a451afc70a4841a03c5687a2635c40fc6dde98f`.
A006 remains `A6-COMPARISON-CERTIFIED`; A007 is not started. No commit, tag, release, or version bump.

## Plan and scope

Reproduce ephemeral-port authentication and compare the old 8765 listener. Preserve historical recovery records and existing uncommitted recovery work. Default to port 0, enforce exclusive Windows ownership before bind, expose non-secret process identity, improve session diagnostics, test security/bootstrap, validate distribution, and leave a normal-command server for manual acceptance. No scientific execution.

## Correction evidence

ROOT CAUSE CONFIRMED: fixed-port stale-listener/session ownership collision.

The phase-1 command was `uv run malecns-workbench --port 0`. Its printed URL was `http://127.0.0.1:59032/#token=TUoU8C9APoa3Y9mB-4iTALORxUPdpzd_C4kbgLMiL-M`; PID 10896 started 2026-10-02 10:06:11 Asia/Taipei. With that exact token, /, /api/status, /api/runs and /compare.js returned 200. The existing 8765 listener, PID 18336, started 2026-10-01 16:47:55, returned 403 for that token and 404 for /compare.js. This establishes different ownership and stale Python routes; it does not require a simulation.

The earlier fragment/sessionStorage handling was valid. The remaining user-visible failure concerned server/listener ownership. The historical `2026-10-02-local-session-refresh.md` and `2026-10-02-local-server-recovery.md` remain unchanged. Their bind-only observation never proved exclusivity. Port 8765 was unreliable in this Windows environment; ephemeral allocation avoids that collision. A prior process token is intentionally rejected by another process.

## Implementation

Normal invocation uses port 0 and prints the actual bound port, independent instance ID, and token URL. Windows SO_EXCLUSIVEADDRUSE is applied before bind where supported; address reuse is disabled across platforms. An occupied explicit 8765 now exits 1 with WinError 10048 and a clear startup message. Existing listeners are never killed automatically. On platforms without the Windows option, normal exclusive bind with address reuse disabled is used; only Windows was live-tested here.

/api/status exposes server_instance_id, never the token. Authentication remains 403 for missing or rejected tokens. Session errors include the non-secret current instance and distinguish missing/rejected credentials. IDs remain operational only and never enter scientific identity. Host, Origin, loopback, protected route and mutating Origin enforcement are preserved.

## Validation

Focused session and A003-A006/A006R tests: 43 passed. Full pytest: 318 passed, 1 skipped (opt-in real graph gate), 1 existing CUDA-path warning. compileall, tracked integrity (9 files), diff whitespace check, and uv build passed. Tests use mocks/synthetic fixtures, not real MaleCNS runs.

The new wheel was installed in a fresh temporary virtual environment, with CuPy absent. Its installed malecns-workbench entry point selected port 59249 automatically (PID 13112, start 10:08:35, instance d814e4e37ed2); /, /api/status and exact-token /api/runs returned 200. Package import came from that environment's site-packages.

Normal workspace invocation selected 59255, PID 15324, start 10:08:45, instance dc5d2e118e3d. All three required requests returned 200. The actual frontend token bootstrap was evaluated with browser-object mocks in Node and used to authenticate this live server; initial fragment and same-tab stored-token refresh both returned 200. Regression tests cover replacement, hashchange, blocked storage, and refresh. Native browser rendering/console acceptance remains for the user.

A second normal invocation selected 59264 with instance 42c03cab5620 and a distinct token. Both servers authenticated independently after startup. The primary workspace server is left running for handoff.

## Scientific firewall and handoff

Real MaleCNS runs 0; Task017 units 0; Task017Q 0; raw-data downloads 0; archive writes 0. Historical scientific artifacts and B:\MaleCNS-Archive unchanged by this work. No scientific identity or result changes. Existing recovery edits retained. No commit.

A006S-READY-FOR-USER-STARTUP-TEST. Run `uv run malecns-workbench`, open its exact printed URL, check initial open and refresh, start another normal server and confirm the first remains usable, and inspect the browser console. No Run is required.

## Final closure reference

Manual startup acceptance PASS; A006S-LOCAL-SERVER-RELIABILITY-CERTIFIED. See [A006S closure](2026-10-02-application-a006s-closure.md) for the final correction and acceptance. Earlier observations above remain historical.
