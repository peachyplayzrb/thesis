# Tooling Quality Posture (D-Tooling)

Last updated: 2026-04-19

## Scope

This document defines active quality-tooling posture for the implementation surface in `07_implementation/`.

## Static Analysis (D2)

- Tool: `pyright`
- Config authority: `pyrightconfig.json`
- Gate policy: fail on any pyright error in active `src` scope.
- Current mode: `standard` type-checking with explicit project config and output-path exclusions.
- Task surface: `07: Typecheck (pyright)`

Rationale: keep a deterministic, zero-error baseline while preserving bounded rollout risk for strictness escalation.

## Coverage Command (D3)

- Tooling: `pytest` + `pytest-cov`
- Canonical command surface: `scripts/test_coverage.ps1`
- Threshold: `--cov-fail-under 65` (current measured baseline is 69%)
- Outputs:
  - `coverage_src_report_latest.txt`
  - `07_implementation/coverage.xml`
  - `07_implementation/coverage_html/`
- Task surface: `07: Tests + Coverage src`

## Dependency Vulnerability Audit (D6)

- Tool: `pip-audit`
- Canonical command surface: `scripts/dependency_audit.ps1`
- Scope: implementation runtime requirements from `07_implementation/requirements.txt` (not whole-environment package inventory)
- Default mode: advisory (does not fail on findings)
- Optional mode: strict (`-Strict`) to fail when vulnerabilities are reported
- Output: `pip_audit_report_latest.txt`
- Task surface: `07: Dependency Audit (Advisory)`

## Security Static Analysis (D7)

- Tool: `bandit`
- Canonical command surface: `scripts/bandit_src.ps1`
- Default mode: advisory (`--exit-zero`)
- Optional mode: strict (`-Strict`) to enforce non-zero on findings
- Python 3.14 fallback: when Bandit reports AST compatibility failure, the script falls back to `ruff check src --select S` and records this in the report.
- Output: `bandit_src_report_latest.txt`
- Task surface: `07: Bandit src (Advisory)`

## Existing Tooling Alignment

- Lint: Ruff via `scripts/ruff_src.ps1` and `07: Ruff Check src` / `07: Ruff Fix src`.
- Hygiene: Vulture + Radon via `scripts/hygiene_src.ps1`.
- Duplicate-code: Pylint duplicate checker via `scripts/duplicate_src.ps1`.

## Pre-Commit Hooks (D5)

- Tool: `pre-commit`
- Config authority: repository root `.pre-commit-config.yaml`
- Active lightweight hook set:
  - Ruff check on `07_implementation/src`
  - Pyright project typecheck for implementation surface
  - Lightweight pytest gate (`tests/test_wrapper_main.py`)
- Rationale: enforce fast local quality gates before commit without running the full heavyweight validation chain.

## Docstring Coverage (D10 Optional Add-On)

- Tool: `interrogate`
- Canonical command surface: `scripts/docstring_coverage_src.ps1`
- Default mode: advisory (`--fail-under 0`)
- Optional mode: strict (`-Strict`) with configurable threshold (`-FailUnder`)
- Output: `interrogate_src_report_latest.txt`
- Task surface: `07: Docstring Coverage src (Advisory)`

Rationale: keep docstring coverage as an evidence add-on without expanding baseline mandatory quality gates.

## Deferred D-Tooling Items

- D4: Hypothesis tooling stays deferred until scoped property tests are added.
- D9: `xenon` remains deferred; current policy keeps Radon in advisory mode to avoid blocking remediation slices.
