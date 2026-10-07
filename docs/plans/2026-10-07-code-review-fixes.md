# Code review fixes

Date: 2026-10-07.

Fix the RunManager completion race by releasing its active flag only in final
cleanup. Fix the validation plugin census by distinguishing module, class and
instance registrations. Add deterministic regression tests for interleaved run
admission and legitimate/foreign plugin representations.

Run only targeted development tests with the protected-payload firewall active
before collection. Do not execute scientific workloads or final certification.
Preserve existing WIP, frozen manifests and historical certification results.

## Development result

Both fixes are implemented. Ten new regression cases plus the two existing
mocked RunManager failure/retention tests passed (12 passed). The actual pytest
builtin census is covered, including the LegacyTmpdirPlugin defining module.
The protected-payload firewall was active before pytest import and collection;
plugin autoload and pytest cache writes were disabled. No scientific engine
was executed. Git diff whitespace validation passed.

DEVELOPMENT TEST — NOT FINAL CERTIFICATION. Frozen candidate manifests were
not updated and no longer describe the repaired candidate. Any future Phase C
requires updated identities and a new frozen candidate in a fresh environment.
Historical G16 and certification dispositions remain unchanged. No commit or
push was performed.
