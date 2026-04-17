# Playlist Generation Pipeline (Standalone Bundle)

This folder is a standalone runnable bundle for the deterministic playlist generation pipeline.

It contains:
- generated runtime `outputs/` folders left empty before first run
- preserved embedded input assets required for the default run path
- requirements.txt
- a single canonical run config profile

## Preserved Embedded Inputs

Some files remain inside `src/*/outputs/` because the active runtime uses them as inputs, not generated review artifacts:
- `src/data_layer/outputs/ds001_working_candidate_dataset.csv`
- `src/data_layer/outputs/ds001_working_candidate_dataset_manifest.json`
- `src/ingestion/outputs/spotify_api_export/`

All other stage output folders are intentionally empty before first run.

## Prerequisites

- Python 3.10+
- PowerShell (Windows)
- A virtual environment is strongly recommended

## Setup

1. Unzip the package.
2. Open the unzipped folder in VS Code.
3. Open a terminal in that folder.

You should now see `main.py`, `requirements.txt`, `config/`, and `src/` at the folder root.

### Windows PowerShell

Copy, paste, and run this full block (change only the path):

```powershell
Set-Location "C:\path\to\mentor_feedback_submission"

if (!(Test-Path ".\.venv\Scripts\python.exe")) {
	py -3.14 -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r ".\requirements.txt"
& ".\.venv\Scripts\python.exe" ".\main.py" --validate-only
```

This block does setup and run in one go. If `.venv` already exists, it reuses it.

```powershell
if (!(Test-Path ".\.venv\Scripts\python.exe")) { py -3.14 -m venv .venv }
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r ".\requirements.txt"
```

Run the pipeline (same terminal, no activation required):

```powershell
& ".\.venv\Scripts\python.exe" ".\main.py" --validate-only
```

Run with Spotify ingestion refresh first (optional):

```powershell
if (!(Test-Path ".\.venv\Scripts\python.exe")) {
    py -3.14 -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r ".\requirements.txt"

$env:PYTHONPATH = (Resolve-Path ".\src").Path
$env:SPOTIFY_CLIENT_ID = "49017c64e9c646ccb6f45137cab3e89f"
$env:SPOTIFY_CLIENT_SECRET = "8f449dbc30cf4f1f91ac96b9a0bf1851"
$env:SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8001/spotify/auth/callback"

& ".\.venv\Scripts\python.exe" ".\src\ingestion\export_spotify_max_dataset.py" --include-top-tracks --include-saved-tracks --include-playlists --include-recently-played
& ".\.venv\Scripts\python.exe" ".\main.py" --validate-only
```

Replace `CLIENT_ID` and `CLIENT_SECRET` with your Spotify app credentials.

### Optional quick check

```powershell
python --version
python -c "import rapidfuzz; print('rapidfuzz ok')"
```

## Run

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

Continue even if a stage reports non-fatal failure:

```bash
python main.py --continue-on-error
```

## Expected Console Output

On a successful run you should see:
- `Starting recommendation system pipeline...`
- `SUCCESS: BL-013 pipeline completed without errors`
- when using `--validate-only`: `SUCCESS: BL-014 validation passed`
- `Pipeline execution complete!`

## Outputs

After a run, generated files will appear under `src/*/outputs/`, including:
- `src/orchestration/outputs/bl013_orchestration_run_latest.json`
- `src/quality/outputs/bl014_sanity_report.json`
- stage-specific BL-003 to BL-009 outputs

These folders start clean before first run and are populated by runtime execution.

## Troubleshooting

- `Run config file not found`:
	- Run from the bundle root where `config/profiles/run_config_ui013_tuning_v1f.json` exists.

- `Cannot find src directory`:
	- Run `python main.py` from the same folder as `main.py`.

- package install issues:
	- Confirm Python 3.10+ and recreate the venv (`python -m venv .venv`).

## Notes

- `rapidfuzz` is included for enhanced fuzzy matching. The code has a standard-library fallback, but this bundle keeps the expected runtime dependency installed.
- `spotipy` is not required for the default embedded-input run path. It is only needed for optional Spotify export utility flows.
