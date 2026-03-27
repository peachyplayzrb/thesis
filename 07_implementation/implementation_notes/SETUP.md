# Setup And Run Guide (Submission)

Last updated: 2026-03-27

## Scope
This guide is for running the active deterministic implementation in `07_implementation/implementation_notes`.

## Environment
- OS: Windows (PowerShell examples below)
- Python: use the workspace virtual environment at `thesis-main/.venv`
- Two execution contexts are supported:
	- Outer workspace root: `.../thesis-main (3)/thesis-main`
	- Inner repo root: `.../thesis-main (3)/thesis-main/thesis-main`
- Install dependencies from outer workspace root:

```powershell
& "thesis-main/.venv/Scripts/python.exe" -m pip install -r thesis-main/requirements.txt
```

## Active Orchestration Command
Run from outer workspace root (`thesis-main (3)/thesis-main`):

```powershell
& "thesis-main/.venv/Scripts/python.exe" "thesis-main/07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py" --refresh-seed --run-config "thesis-main/07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json"
```

Equivalent command from inner repo root (`thesis-main (3)/thesis-main/thesis-main`):

```powershell
& ".venv/Scripts/python.exe" "07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py" --refresh-seed --run-config "07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json"
```

## Quality Verification
Run sanity checks after orchestration:

```powershell
& "thesis-main/.venv/Scripts/python.exe" "thesis-main/07_implementation/implementation_notes/bl014_quality/run_bl014_sanity_checks.py"
```

Inner repo root equivalent:

```powershell
& ".venv/Scripts/python.exe" "07_implementation/implementation_notes/bl014_quality/run_bl014_sanity_checks.py"
```

Optional quality suite:

```powershell
& "thesis-main/.venv/Scripts/python.exe" "thesis-main/07_implementation/implementation_notes/bl014_quality/run_bl014_quality_suite.py"
```

Inner repo root equivalent:

```powershell
& ".venv/Scripts/python.exe" "07_implementation/implementation_notes/bl014_quality/run_bl014_quality_suite.py" --mode active
```

## Canonical Outputs To Keep
- BL-007 playlist JSON
- BL-008 explanation payloads
- BL-009 observability log/index
- BL-014 sanity/quality reports

Intermediate artifacts are retained in stage `outputs/` folders for auditability and reproducibility.
