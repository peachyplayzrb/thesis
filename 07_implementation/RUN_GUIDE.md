# Run Guide

Last updated: 2026-03-27

## Purpose
This is the canonical run and troubleshooting guide for the active deterministic implementation.

This document supersedes command duplication in:
- 07_implementation/implementation_notes/SETUP.md
- 07_implementation/implementation_notes/bl013_entrypoint/bl013_run_command.md

## Scope
- Implementation root: 07_implementation/implementation_notes
- Canonical baseline reference: 07_implementation/ACTIVE_BASELINE.md

## Environment
- OS: Windows (PowerShell)
- Python environment: thesis-main/.venv
- Supported execution contexts:
  - Outer workspace root: .../thesis-main (3)/thesis-main
  - Inner repo root: .../thesis-main (3)/thesis-main/thesis-main

## Dependency Install
From outer workspace root:

```powershell
& "thesis-main/.venv/Scripts/python.exe" -m pip install -r thesis-main/requirements.txt
```

## BL-013 Orchestration Commands
Default full-chain run from outer workspace root:

```powershell
& "thesis-main/.venv/Scripts/python.exe" "thesis-main/07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py" --refresh-seed --run-config "thesis-main/07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json"
```

Equivalent from inner repo root:

```powershell
& ".venv/Scripts/python.exe" "07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py" --refresh-seed --run-config "07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json"
```

Default command without explicit arguments:

```powershell
python 07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py
```

Run selected ordered stages:

```powershell
python 07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py --stages BL-004 BL-005 BL-006
```

Continue after stage failure:

```powershell
python 07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py --continue-on-error
```

## Verification Commands
Sanity check:

```powershell
& "thesis-main/.venv/Scripts/python.exe" "thesis-main/07_implementation/implementation_notes/bl014_quality/run_bl014_sanity_checks.py"
```

Inner-root sanity equivalent:

```powershell
& ".venv/Scripts/python.exe" "07_implementation/implementation_notes/bl014_quality/run_bl014_sanity_checks.py"
```

Quality suite:

```powershell
& "thesis-main/.venv/Scripts/python.exe" "thesis-main/07_implementation/implementation_notes/bl014_quality/run_bl014_quality_suite.py"
```

Inner-root quality equivalent:

```powershell
& ".venv/Scripts/python.exe" "07_implementation/implementation_notes/bl014_quality/run_bl014_quality_suite.py" --mode active
```

## Troubleshooting
BL-013 fails before stage execution:
- Confirm current working directory matches one of the supported contexts.
- Confirm virtual environment Python path is valid.
- Confirm run-config path is repository-relative to your current context.

BL-013 fails due to seed freshness or config mismatch:
- Re-run with --refresh-seed and explicit --run-config.
- Verify the run_config_ui013_tuning_v1f.json path resolves from the current root.

BL-014 fails after a run:
- Inspect BL-013 summary and BL-014 report under stage outputs.
- Re-run BL-013 and BL-014 with unchanged inputs and config to isolate transient filesystem/path issues.

Determinism concern:
- Run BL-013 twice with unchanged code, data, and config.
- Compare stable_artifact_hashes from BL-013 run summaries.

## Canonical Outputs to Keep
- BL-007 playlist JSON
- BL-008 explanation payloads
- BL-009 observability log and index
- BL-014 sanity and quality reports

## Related References
- Baseline authority: 07_implementation/ACTIVE_BASELINE.md
- Backlog control board: 07_implementation/backlog.md
- Submission manifest: 07_implementation/implementation_notes/SUBMISSION_MANIFEST.md
