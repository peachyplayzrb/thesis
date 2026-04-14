# Recommendation System Implementation (07_implementation)

Standalone implementation of the BL-003 to BL-014 playlist recommendation pipeline.

Architecture reference:

- CLEAN_ARCHITECTURE.md

This folder is runnable as-is with embedded inputs:

- Embedded candidate dataset: src/data_layer/outputs/ds001_working_candidate_dataset.csv
- Embedded Spotify export bundle: src/ingestion/outputs/spotify_api_export/

No raw Music4All tables are required for the default run path.

## What Actually Runs

Top-level entrypoint:

- main.py

Runtime behavior in main.py:

1. Resolves src as the implementation root.
2. Verifies the embedded DS-001 dataset exists.
3. Resolves run config (default: config/profiles/run_config_ui013_tuning_v1f.json).
4. Calls BL-013 orchestrator at src/orchestration/main.py.
5. Always requests a BL-003 seed refresh via --refresh-seed for wrapper-driven runs.
6. Optionally runs BL-014 sanity checks when --validate-only is set.

Important: --validate-only is additive, not exclusive. It runs BL-013 first, then BL-014.

## Quick Start

```bash
# From 07_implementation/
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

Dependency profile notes:

- `requirements.txt` is intentionally minimal for the active BL-003 to BL-014 runtime path.
- `rapidfuzz` is included for enhanced fuzzy matching; BL-003 has a standard-library fallback when unavailable.
- Spotify export/ingestion utility flows can additionally use `spotipy` (optional install).

Run with explicit config:

```bash
python main.py --run-config config/profiles/run_config_ui013_tuning_v2a_retrieval_tight.json
```

Run with post-pipeline BL-014 validation:

```bash
python main.py --validate-only
```

## Local Web Viewer (Minimal Wrapper)

You can launch a tiny local website and API wrapper to run the pipeline and inspect latest artifacts.

Start server from `07_implementation/`:

```bash
python finalized/web_server.py
```

Open:

```text
http://127.0.0.1:8000
```

Main API routes:

- `GET /api/configs` -> list available run-config profiles from `config/profiles/`
- `GET /api/status` -> latest BL-013 and BL-014 status snapshot
- `GET /api/artifacts` -> key output artifact manifest (exists/size/mtime)
- `GET /api/artifact?name=<artifact_name>` -> safe preview for whitelisted artifacts
- `GET /api/explainer/flow` -> BL-003 to BL-009 stage flow with readiness state
- `GET /api/explainer/stage?stage=<bl_id>` -> per-stage explainer details and metrics
- `GET /api/explainer/explanations?limit=<n>` -> BL-008 explanation-card view for top tracks
- `GET /api/explainer/evidence` -> BL-013/BL-014/BL-009 evidence summary dashboard payload
- `GET /api/explainer/guide` -> guided next-step checklist derived from latest artifact availability
- `GET /api/config-builder/schema` -> complete run-config setting inventory with defaults and per-setting descriptions
- `GET /api/config-builder/profile?name=<config_path>` -> load an existing profile into the config builder
- `POST /api/run` -> execute `main.py` (supports `config_path`, `validate_only`, `continue_on_error`)
- `GET /api/run-stream` -> SSE live stream of wrapper execution

Website panels now include:

- Pipeline Explainer (flow + stage details)
- BL-008 Explanation Viewer (track-level explanation cards)
- Run Evidence Dashboard (BL-013 stage statuses + BL-014 checks + BL-009 evidence context)
- Guided Flow (recommended next action from run and evidence readiness)
- Profile Config Builder (edit/export full run-config surface with inline explanations)

This wrapper is additive and does not modify core runtime logic under `src/`.

Continue past non-fatal stage failures:

```bash
python main.py --continue-on-error
```

## Windows Automation Contract

Use this sequence for deterministic setup and validation on Windows.

```powershell
# From thesis-main/07_implementation
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\preflight_windows.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\check_all.ps1 -SkipSetup
```

Single command path (runs preflight + setup + checks + validate-only):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\check_all.ps1
```

Expected report artifacts after success:

- src/orchestration/outputs/bl013_orchestration_run_latest.json
- src/quality/outputs/bl014_sanity_report.json

## VS Code Task Runner

Use Command Palette -> `Tasks: Run Task` and pick one of:

- `07: Preflight (Windows)`
- `07: Setup Environment`
- `07: CI Guard Phase 6`
- `07: Tests`
- `07: Typecheck (pyright)`
- `07: Validate Only (Wrapper)`
- `07: Full Contract (Preflight + Check-All)`

## Pipeline Stages

- BL-003 Alignment: src/alignment/main.py
- BL-004 Profile: src/profile/main.py
- BL-005 Retrieval: src/retrieval/main.py
- BL-006 Scoring: src/scoring/main.py
- BL-007 Playlist: src/playlist/main.py
- BL-008 Transparency: src/transparency/main.py
- BL-009 Observability: src/observability/main.py
- BL-010 Reproducibility: src/reproducibility/main.py
- BL-011 Controllability: src/controllability/main.py
- BL-014 Quality/Sanity: src/quality/sanity_checks.py

BL-013 orchestration (src/orchestration/main.py) is the stage runner used by the wrapper.

## BL-013 Orchestration Notes

- Default stage order is BL-004 to BL-009.
- BL-003 can be executed before those stages when seed refresh is requested.
- Run summaries are written to src/orchestration/outputs/.
- A latest pointer file is maintained: src/orchestration/outputs/bl013_orchestration_run_latest.json.
- Canonical run config artifacts are emitted under src/run_config/outputs/.

You can run BL-013 directly from src for advanced workflows:

```bash
# From 07_implementation/src
PYTHONPATH=. python orchestration/main.py --run-config ../config/profiles/run_config_ui013_tuning_v1f.json
```

## Validation and Evaluation Commands

BL-014 sanity checks:

```bash
# From 07_implementation/src
PYTHONPATH=. python quality/sanity_checks.py
```

BL-010 reproducibility replay:

```bash
# From 07_implementation/src
PYTHONPATH=. python reproducibility/main.py --replay-count 3
```

BL-011 controllability evaluation:

```bash
# From 07_implementation/src
PYTHONPATH=. python controllability/main.py
```

REB-M3 tranche-1 gate (O1 to O3 evidence surfaces):

```bash
# From 07_implementation/src
PYTHONPATH=. python quality/reb_m3_tranche1_gate.py
```

REB-M3 tranche-2 gate (O4 to O6 evidence surfaces):

```bash
# From 07_implementation/src
PYTHONPATH=. python quality/reb_m3_tranche2_gate.py
```

REB-M3 tranche-3 gate (control-causality hardening surfaces):

```bash
# From 07_implementation/src
PYTHONPATH=. python quality/reb_m3_tranche3_gate.py
```

## Output Artifacts

Core artifacts (under src/*/outputs):

- src/alignment/outputs/bl003_ds001_spotify_seed_table.csv
- src/alignment/outputs/bl003_ds001_spotify_summary.json
- src/profile/outputs/bl004_preference_profile.json
- src/retrieval/outputs/bl005_filtered_candidates.csv
- src/retrieval/outputs/bl005_candidate_decisions.csv
- src/scoring/outputs/bl006_scored_candidates.csv
- src/playlist/outputs/playlist.json
- src/transparency/outputs/bl008_explanation_payloads.json
- src/observability/outputs/bl009_run_observability_log.json

Validation/evaluation artifacts:

- src/reproducibility/outputs/reproducibility_report.json
- src/controllability/outputs/controllability_report.json
- src/quality/outputs/bl014_sanity_report.json

## Configuration

Run config profiles are in config/profiles/.

Current canonical default used by main.py:

- config/profiles/run_config_ui013_tuning_v1f.json

Other profiles include v1 variants, v2 experimental variants, and BL-021 probe profiles.

## Troubleshooting

Missing src directory:

```text
ERROR: Cannot find src directory at ...
```

Fix: run main.py from 07_implementation/.

Missing embedded candidate dataset:

```text
ERROR: Cannot find embedded candidate dataset at .../src/data_layer/outputs/ds001_working_candidate_dataset.csv
```

Fix: ensure the dataset file exists at that path.

Direct BL-013 import errors like ModuleNotFoundError: shared_utils:

Fix: run BL-013 via top-level main.py, or set PYTHONPATH=. when running from src.

PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

This applies only to the current terminal session.

## Test Entry Points

- Standalone smoke script: python test_standalone.py
- Full test suite: pytest tests

## System Requirements

- Python 3.10+
- OS: Windows/macOS/Linux
- Network optional for default embedded-input runs

## License

Provided for academic and research use.

Version: 1.0
Last Updated: March 2026
