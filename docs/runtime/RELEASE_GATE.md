# Application/runtime candidate release gate

Status: **0.4.0 CANDIDATE WIP; ARTIFACT VALIDATION NOT RUN; PUBLICATION NOT AUTHORIZED**.
This gate concerns the 0.4.0 engineering candidate. Package version is
0.4.0. It complements the [historical scientific gate](../MALECNS_RELEASE_GATE.md)
without rewriting scientific results or certifying protected payload integrity.

## Frozen scope

Stable CPU factory/opaque state/detached output, legacy compatibility and packaged
workbench; optional experimental GPU and engineered synthetic Arena. The
[consumer guide](USER_GUIDE.md) and [candidate notes](../releases/0.4.0-preparation.md)
define claims and exclusions. Task026 remains
NO_V0_4_SCIENTIFIC_QUESTION_CURRENTLY_READY. No routine real-data preparation,
benchmark, GPU timing, scientific endpoint rerun or archive recovery.

## Required future evidence

| Gate | Acceptance requirement | Current disposition |
| --- | --- | --- |
| Candidate identity | Exact local/origin/live source SHA; complete dirty/staged/WIP inventory; frozen ordinary input/lock hashes | A024 preparation committed at c32919d4f0228310401abce17d09d3d68cb76deb; final validation candidate not yet frozen |
| Guarded validation | Approved task-wide guard before discovery/import; fresh sparse execution tree, environment, plugin/child/cache custody; preserve exact H/I/N and terminal exclusions | A023 historical PASS only; fresh candidate run NOT RUN |
| Changed validation inputs | Explicitly review additions and taxonomy; keep numerical oracles and all exclusions, never silently broaden grants | New example checks require admission; NOT RUN |
| Integrity split | I0 unprotected content; I2 bounded consistency; report I1 separately | Fresh checks NOT RUN; I1 NOT RUN — REGISTERED-PAYLOAD-REQUIRED |
| Build custody | Approved protected-root-free ordinary source tree; fresh wheel and sdist; source/lock/build-tool identities, logs, hashes and inventories | NOT RUN |
| Installed CPU artifact | Fresh outside-checkout environment with declared dependencies; actual wheel import location, runtime exports and absent CuPy | NOT RUN |
| Consumer examples | Run both guide CPU examples from installed artifact; retain assertions/output; independent continuity oracle for API regressions | Static review only |
| CLI/static assets | Installed malecns-sim and malecns-workbench help/startup, automatic-port authenticated API/static asset smoke without data | NOT RUN |
| Artifact exclusions | Inspect wheel/sdist contents; no raw inputs/caches/secrets/unrelated research WIP; document which guides/examples ship | NOT RUN |
| GPU optionality | CPU import/install without GPU; extra metadata/locked closure checked separately; no mandatory device execution | Static metadata review only |
| GPU claim | Fresh device certification only with separate explicit authority; fake-device/structural tests do not certify hardware | Experimental; historical EQ-B only |
| Version transition | Explicit authority to set version and synchronize metadata/lock/notes; freeze and validate resulting bytes | Authorized in A025; metadata/lock/notes updated to 0.4.0; executable validation NOT RUN |
| Publication | Exact tested artifact/source identity, final diff/scope/cleanup report, explicit tag/release/publication authority | NOT AUTHORIZED |

A023 counted H=1503, I=12, N=41 (1556 collected, 1544 passed, 12 NOT RUN).
The eleven protected prerequisites and one absent external baseline are explicit
terminal exclusions. They do not become passing tests when omitted. Keep original
H/I identities; review any new validation checks as N. Any source/metadata/version
change after freeze invalidates affected certification and requires a fresh
candidate, not relabeling the old evidence.

## Bounded validation route

The 2026-10-08 A024 documentation reconciliation was delivered separately at
80f57f97eb0429d6d9845766a78e0bc41cd524ca. The subsequent A025 version overlay
requires its own candidate-specific evidence; A023 implementation validation
does not certify different source or artifact bytes. Preserve the incoming A025 stopped-work
files separately; their presence grants no authority to resume execution.

The user has authorized A025 candidate execution under the
[0.4.0 candidate plan](../plans/2026-10-08-application-a025-v040-release-candidate.md).
Protection/custody certification remains a prerequisite. Review the A023 provisioner/freezer/
runner as ordinary text, adapt their approved frozen inputs to the actual candidate
and example/artifact checks, and certify the route before discovery or build.
Do not treat a bare checkout pytest or build as a zero-payload certification route.
Use the existing H/I/N/taxonomy/final evidence under docs/manifests as historical
authority; they are not commands to import unchanged and certify different bytes.

Freeze after development checks, then use one fresh final environment/process tree
with plugin census, exact child authority, before/after ordinary hashes and cleanup
accounting. Build only from explicitly approved ordinary inputs; install the actual
wheel outside the checkout with runtime dependencies. Record Python, OS, package
versions, command lines, source/lock/artifact hashes, import locations, entry points,
assets and complete results. CPU guide execution is synthetic simulation and must
be named in that authorization. Device preflight/example execution is separate.

If a failure requires repair, return to development, invalidate the candidate and
report the failure. Never patch a frozen run, weaken the firewall, compute protected
hashes to fill I1, or reuse an old wheel as current evidence. No retry of any consumed
historical real benchmark is authorized by this route.

Release-safe I0/I2 acceptance alone cannot satisfy a policy requiring full I1.
The release decision must explicitly retain/adjudicate that boundary; missing
protected integrity is a blocker under any full-integrity requirement. Similarly,
Python >=3.12 metadata is not evidence of every Python/platform combination.
A008's installed wheel and A023's provisioning wheel are historical evidence only;
A009 blind new-user acceptance remains uncertified.


## A025 native Windows candidate route

The task-local controller freezes finite ordinary inputs at the A024 baseline
and executes them in a unique Windows AppContainer and kill-on-close Job.
Independent controls require actual GPU availability, native protected-root
read denials, raw-device/write denials, immutable tools, and complete cleanup.
Temporary profile-only namespace/ancestor metadata, read-only NUL, fixed Node
and suspended Nsight executable rights are removed afterward. The synthetic
symlink broker admits only bounded temporary fixture links and reads no target
contents; it preserves the original test and native symlink audit.

Clean environments receive the complete original locked wheel closure with
whole-artifact SHA-256 verification. Frozen offline uv sync reconciles the GPU/dev
environment before the actual candidate wheel is installed. A separate build
environment creates wheel and sdist from a protected-root-free copy. The complete
original collection must produce 1544 passed, zero skips/failures and 12 original
taxonomy exclusions: 11 registered-payload-required nodes and one unavailable
external starting-SHA replay. Original B3/terminal/taxonomy requirements remain.

The installed GPU guide runs only the four-neuron synthetic example. A separate
fresh CPU environment installs the actual wheel with runtime dependencies,
checks both archive metadata/inventories, executable CPU guide blocks, legacy
continuity, CLI entry points, authenticated HTTP routes and static assets.
The signature-reference fence is not executable; it is identified explicitly.
The [A025 result](../plans/2026-10-08-application-a025-release-candidate-result.md)
records the tested source/tool/artifact identities and all subgate results.
Final result records are written after execution and excluded from their own
candidate hash map to avoid circular identity. I1 remains NOT RUN; no publication,
new full-real attempt, GPU speedup or biological claim follows from RC acceptance.
