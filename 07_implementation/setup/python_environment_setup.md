# Python Environment Setup

## Purpose
Set up the thesis repo on a new Windows machine with one command.

## One-Command Bootstrap
Run this from the repository root:

```powershell
.\07_implementation\setup\bootstrap_python_environment.cmd
```

What it does:
- creates `.venv` if it does not already exist
- upgrades `pip` inside `.venv`
- installs pinned packages from `requirements.txt`
- verifies imports for `h5py`, `pypdf`, and `rapidfuzz`

## Expected Result
After the script finishes successfully:
- the repo-local interpreter is `.venv\Scripts\python.exe`
- required packages are installed in `.venv`
- the environment is ready for current implementation and QC scripts

## Manual Fallback
If you want to do the steps manually:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Notes
- `.venv/` is already ignored by git.
- If `python` is not available on PATH, install Python 3.11+ and rerun the bootstrap script.
- Spotify credentials are not part of this bootstrap step. Use the ingestion runbook separately when needed.
- The `.cmd` wrapper is the recommended entrypoint because many Windows machines block direct `.ps1` execution by policy.