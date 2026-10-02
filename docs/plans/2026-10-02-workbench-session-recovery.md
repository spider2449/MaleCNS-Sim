# Workbench session recovery

Fix session recovery when an existing browser document receives a new token fragment. Preserve server authentication and origin checks. Retain the fragment when session storage is unavailable. Add an explicit CLI browser-opening option to avoid manual URL transfer. Validate browser session regressions and existing server authentication tests. Do not commit or push.

## Final closure reference

Manual startup acceptance PASS; A006S-LOCAL-SERVER-RELIABILITY-CERTIFIED. See [A006S closure](2026-10-02-application-a006s-closure.md) for the final correction and acceptance. Earlier observations above remain historical.
