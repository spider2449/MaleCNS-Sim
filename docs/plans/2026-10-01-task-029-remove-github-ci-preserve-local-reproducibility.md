# Task 029 — Remove GitHub CI while preserving local reproducibility

## Start and policy

Starting local HEAD, `origin/master`, and live GitHub master were `a6963eda5e61de421effb9fcf81faf4daee0c724`. The worktree and stash were empty. Package version was `0.3.0`; annotated `v0.3.0^{}` was `a1a6651163840a982799b1fa82c1904e67f84660`.

The repository owner decided that MaleCNS-Sim intentionally does not use GitHub CI. Task 029 intentionally removes ongoing GitHub CI. This later policy decision does not alter Task 027 or Task 028 history. Task 028 CI1 — GENERIC_CPU_CI_CERTIFIED remains historically valid: GitHub Actions run `36805240400` completed successfully at certified SHA `a6963eda5e61de421effb9fcf81faf4daee0c724`. Its historical plan and run remain intact.

## Task 028 inventory and change

| Addition | Classification | Task 029 treatment |
| --- | --- | --- |
| `.github/workflows/cpu-reproducibility.yml` | CI_ONLY | Deleted. |
| `scripts/check_tracked_integrity.py` | LOCAL_REPRODUCIBILITY | Preserved unchanged. |
| `tests/test_tracked_integrity.py` | LOCAL_REPRODUCIBILITY | Preserved unchanged, including corrupt-file and re-pinned corruption failures. |
| `README.md` Task 028 text | MIXED | Corrected current GitHub CI claims; retained accurate local commands. |
| Task 028 plan | HISTORICAL_RECORD | Preserved unchanged. |

The checker reads tracked metadata, verifies pinned digests and cross-references, and needs no Actions runner, GPU, raw data, network, simulation, or endpoint calculation. The test copies inputs to a temporary directory and leaves canonical artifacts untouched. The README now states the current no-GitHub-CI policy and lists individual local commands without claiming an integrated gate. No other CI provider or scheduled cloud execution was added. The tracked active GitHub Actions workflow count is zero.

## Local validation and firewall

`uv run pytest`: **256 passed, 1 established opt-in skip**. The integrity regression passed its positive copy check, altered-file hash rejection, and re-pinned cross-reference rejection. `uv run python -m compileall src scripts tests`: PASS. `uv build`: PASS, producing the `0.3.0` sdist and wheel. `uv run python scripts/check_tracked_integrity.py`: **Integrity PASS, 9 tracked files and internal identities**. `git diff --check`: PASS.

Scientific simulations **0**; scientific endpoint calculations **0**; new hypothesis tests **0**; MaleCNS raw-data downloads **0**; Task 017 restore attempts **0**; Task 017Q executions **0**; motif calculations **0**; candidate identity work **0**. No Task 017 or Task 018 rerun and no BANC work. Task 017Q remains **Q1 — KEEP_DEFERRED**. Scientific artifacts remain byte-identical; historical scientific records and Task 026's scientific decision remain unchanged. Package version, tag, and release are unchanged.

## Final repository workflow state

Current repository policy: **NO GITHUB CI**. Local reproducibility commands and offline integrity coverage remain available. Historical Actions runs, including `36805240400`, remain historical evidence; their visibility does not imply an active workflow.
