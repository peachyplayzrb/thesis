# Final Artefact Standalone Runner

Legacy status: This folder is retained as an archived legacy snapshot. The active implementation root is `07_implementation`, and current standalone launcher flow is controlled from repository root via `final_artefact.py`.

This folder defines the standalone hand-in surface for the thesis artefact.

## Entry Program
- `../final_artefact.py`

## Quick Run (from thesis-main root)
```powershell
& ".venv/Scripts/python.exe" "final_artefact.py" run --refresh-seed
```

## Run + Validation
```powershell
& ".venv/Scripts/python.exe" "final_artefact.py" run --refresh-seed --validate-only
```

## Validation Only
```powershell
& ".venv/Scripts/python.exe" "final_artefact.py" validate
```

## Portable Bundle Build
```powershell
& ".venv/Scripts/python.exe" "final_artefact.py" bundle --destination "_scratch"
```

This creates `_scratch/final_artefact_bundle/` with runtime code, launcher, and a bundle manifest.

## Config
Default profile is configured in `config/default_config.json`.

## Notes
- This entrypoint is submission-facing and does not alter BL stage logic.
- Baseline authority remains `07_implementation/ACTIVE_BASELINE.md`.
