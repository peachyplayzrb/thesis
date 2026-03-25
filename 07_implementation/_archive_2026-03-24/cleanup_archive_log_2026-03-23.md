# Ingestion Cleanup Archive Log (2026-03-23)

## Scope
Archive non-active ingestion files into a safekeep folder and keep only active runtime files under:
- `07_implementation/implementation_notes/bl001_bl002_ingestion/`

## Archive Folder
- `07_implementation/implementation_notes/bl001_bl002_ingestion/_safekeep_unused_2026-03-23/`

## Kept In Active Ingestion Folder
- `07_implementation/implementation_notes/bl001_bl002_ingestion/bl001_spotify_input_output_mapping.md`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/ingest_history_parser.py`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/spotify_api_ingestion_runbook.md`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/configs/templates/spotify_env_template.ps1`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/cleanup_archive_log_2026-03-23.md`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_aligned_events.jsonl`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_alignment_report.json`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_lastfm_tag_cache.json`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_export_run_summary.json`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_top_tracks_flat.csv`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_saved_tracks_flat.csv`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_playlist_items_flat.csv`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_token_cache.json`

## Moved To Safekeep Archive
- `07_implementation/implementation_notes/bl001_bl002_ingestion/env`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/__pycache__/export_spotify_max_dataset.cpython-312.pyc`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/__pycache__/`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl003_lastfm_rerun.log`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_aligned_events.pre_partial_backup_20260322-001050.jsonl`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_aligned_events_partial_from_cache.jsonl`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_alignment_report_partial_from_cache.json`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_profile.json`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_top_tracks_by_range.json`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_saved_tracks.json`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_playlists.json`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_playlists_flat.csv`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_playlist_items_flat.jsonl`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_request_log.jsonl`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_rate_limit_block.json`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_resilience_cache.sqlite`

## Archive Path Convention
Files were moved under preserved relative paths, for example:
- From:
  - `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_profile.json`
- To:
  - `07_implementation/implementation_notes/bl001_bl002_ingestion/_safekeep_unused_2026-03-23/07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_profile.json`

## Restore Procedure
Use PowerShell from repository root:

```powershell
$archive = "07_implementation/implementation_notes/bl001_bl002_ingestion/_safekeep_unused_2026-03-23/07_implementation/implementation_notes/bl001_bl002_ingestion"
Copy-Item "$archive\*" "07_implementation/implementation_notes/bl001_bl002_ingestion" -Recurse -Force
```

## Post-Cleanup Validation Plan
- Run exporter smoke test (`--help`) to confirm script is callable.
- Confirm active output files still exist in live paths used by website and BL-003/BL-004.

---

## Cleanup Pass 2 (2026-03-23 — second session)

### Scope
Broader project-wide cleanup requested by user to move all unused/scratch files out of active directories.

### New Archive Locations

**`thesis-main/_scratch_archive_2026-03-23/`** (root-level scratch/temp files):
- `tmp_bl019_mtimes.json`
- `tmp_bl019_processes.json`
- `tmp_bl019_run1.txt`
- `tmp_bl019_run1_utf8.txt`
- `tmp_bl019_status.txt`
- `tmp_bl019_status2.txt`
- `tmp_spotify_run.log`
- `tmp_terminal_probe.txt`
- `bl_align_log.txt`

**`07_implementation/_archive_2026-03-23/`** (implementation-level outdated files):
- `test_resilience_integration.py` — validation test script, export now confirmed working
- `BL020_HANDOFF_AUDIT_2026-03-21.md` — superseded handoff audit from 2026-03-21
- `test_notes.md` — scratch test notes, content preserved in experiment_log.md
- `website_test_data/test_data/` — empty placeholder folder from website directory

**`ingestion/_safekeep_unused_2026-03-23/`** (added to existing safekeep):
- `outputs/export_run.log` — temporary session log produced during background export run

### Active Files Confirmed After Cleanup

**Ingestion package** (`07_implementation/implementation_notes/bl001_bl002_ingestion/`):
- `__init__.py`, `export_spotify_max_dataset.py`, `spotify_artifacts.py`, `spotify_auth.py`, `spotify_client.py`, `spotify_io.py`, `spotify_mapping.py`, `spotify_env_template.ps1`, `ingest_history_parser.py`

**Website** (`07_implementation/website/`):
- `app.js`, `import.html`, `index.html`, `profile_basis.html`, `profile_basis.js`, `style.css`

### Post-Cleanup Validation (Pass 2)
- Python package imports tested: `package imports ok`
- HTTP server started on `127.0.0.1:5500` from `07_implementation/`
- Website `import.html` opened and loads export artifacts correctly
- No errors in any active website or ingestion files
- Change log updated: C-088

## Website Runtime Fix After Cleanup (2026-03-23)
- Issue: local browser test later returned HTTP 404 because multiple temporary Python HTTP servers existed with inconsistent working directories.
- Root cause: manual `http.server` runs depended on shell cwd, so `http://127.0.0.1:5500/` was not stable across sessions.
- Fix applied:
  - Added `07_implementation/index.html` redirect to `website/import.html`
  - Added canonical launcher scripts `07_implementation/setup/start_website.ps1` and `07_implementation/setup/start_website.cmd`
  - Started clean server on port `5501` with explicit `--directory 07_implementation`
- Operational note: direct `.ps1` invocation is blocked by local execution policy on this machine, so the supported startup command is the `.cmd` wrapper or a PowerShell `-ExecutionPolicy Bypass` invocation.
- Stable URLs after fix:
  - `http://127.0.0.1:5501/`
  - `http://127.0.0.1:5501/website/import.html`
- Result: website path resolution no longer depends on terminal cwd.

## Post-Cleanup Runtime Verification (2026-03-23)
- Objective: execute a real end-to-end Spotify export after cleanup archival.
- Result: not completed successfully in this session; exporter execution repeatedly terminated before writing fresh artifacts and before summary regeneration.
- Evidence:
  - Captured runtime log shows paging progress into long-term top tracks and then stops without completion markers.
  - `spotify_export_run_summary.json` remained unchanged at `generated_at_utc=2026-03-21T19:26:20Z`.
  - `spotify_top_tracks_flat.csv`, `spotify_saved_tracks_flat.csv`, and `spotify_playlist_items_flat.csv` retained the same 2026-03-21 modification timestamps.
  - `spotify_request_log.jsonl` is currently missing from live output path (it was archived during cleanup and not regenerated because run did not complete).
- Action required next:
  - Re-run exporter with explicit file logging and no output truncation path, then confirm updated `run_id`, artifact mtimes, and regenerated request log.

## Post-Cleanup Runtime Verification Retry (2026-03-23)
- Objective: rerun full export with deterministic settings and verify artifact freshness after prior incomplete attempts.
- Result: successful end-to-end completion.
- Evidence:
  - New summary `run_id`: `SPOTIFY-EXPORT-20260323-210703-012191`.
  - New summary generation time: `2026-03-23T21:08:36Z`.
  - Refreshed output artifacts and regenerated request log in live path:
    - `spotify_top_tracks_flat.csv`
    - `spotify_saved_tracks_flat.csv`
    - `spotify_playlist_items_flat.csv`
    - `spotify_request_log.jsonl`
  - Counts recorded in summary:
    - `top_tracks_short_term=602`
    - `top_tracks_medium_term=3029`
    - `top_tracks_long_term=5114`
    - `saved_tracks=171`
    - `playlists=4`
    - `playlist_items=31`
    - `api_calls_logged=187`
- Operational note:
  - Prior incomplete attempts were valid diagnostics but are now superseded by this successful verification run.
