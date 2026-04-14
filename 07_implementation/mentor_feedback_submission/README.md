# Mentor Feedback Submission Bundle

This folder is a clean mentor-review bundle for the playlist generation artefact.

It contains:
- a cleaned copy of `src/`
- no `__pycache__` folders
- generated runtime `outputs/` folders left empty
- preserved embedded input assets required for the default run path
- a minimal `requirements.txt`
- a single canonical run config profile

## Preserved Embedded Inputs

Some files remain inside `src/*/outputs/` because the active runtime uses them as inputs, not generated review artifacts:
- `src/data_layer/outputs/ds001_working_candidate_dataset.csv`
- `src/data_layer/outputs/ds001_working_candidate_dataset_manifest.json`
- `src/ingestion/outputs/spotify_api_export/`

All other stage output folders are intentionally empty before first run.

## Prerequisites

- Python 3.10+
- A virtual environment is recommended

## Setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run The Program

Default run:

```bash
python main.py
```

Run with validation:

```bash
python main.py --validate-only
```

Run with explicit config:

```bash
python main.py --run-config config/profiles/run_config_ui013_tuning_v1f.json
```

## Outputs

After a run, generated files will appear under `src/*/outputs/`, including:
- `src/orchestration/outputs/bl013_orchestration_run_latest.json`
- `src/quality/outputs/bl014_sanity_report.json`
- stage-specific BL-003 to BL-009 outputs

## Notes

- `rapidfuzz` is included for enhanced fuzzy matching. The code has a standard-library fallback, but this bundle keeps the expected runtime dependency installed.
- `spotipy` is not required for the default embedded-input run path. It is only needed for optional Spotify export utility flows.
