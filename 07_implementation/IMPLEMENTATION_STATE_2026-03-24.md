# Implementation State — 2026-03-24

Comprehensive reference for the current active implementation. Everything described here
reflects the actual executed and evidenced state of the pipeline as of 2026-03-24.

---

## 1. Pipeline Architecture

```
BL-001 (schema def)
BL-002 (Spotify API export)   →  spotify_api_export/ outputs
BL-003 (DS-001 seed build)    →  alignment/outputs/
BL-004 (preference profile)   →  profile/outputs/
BL-005 (candidate filter)     →  retrieval/outputs/
BL-006 (scoring)              →  scoring/outputs/
BL-007 (playlist assembly)    →  playlist/outputs/
BL-008 (transparency)         →  transparency/outputs/
BL-009 (observability)        →  observability/outputs/
```

Orchestrator: `BL-013` runs BL-004 through BL-009 in order, with optional `--refresh-seed`
to pre-run BL-003 before any stages.

Evaluation layer:
- `BL-010` — reproducibility (3-replay determinism check)
- `BL-011` — controllability (5-scenario parameter sensitivity)
- `BL-014` — sanity checks (21-rule cross-stage artifact audit)

Website layer:
- `setup/website_api_server.py` — Flask API server for pipeline + Spotify ingestion
- `website/` — multi-page frontend

Run-config layer:
- `run_config/run_config_utils.py` — config loading, deep-merge, validation
- `run_config/run_config_template_v1.json` — canonical schema v1 template

---

## 2. Active Dataset — DS-001 (Music4All / Music4All-Onion)

| Property | Value |
|---|---|
| Source | Music4All-Onion (accessed 2026-03-24) |
| Script | `implementation_notes/bl000_data_layer/build_ds001_working_dataset.py` |
| Output | `data_layer/outputs/ds001_working_candidate_dataset.csv` |
| Manifest | `data_layer/outputs/ds001_working_candidate_dataset_manifest.json` |
| Track count | 109,269 |
| Size | ~23.2 MB |
| SHA-256 | `296331CA6390D2C111AA336C7EB154B69EC7060604312ac8a274f545b68a04ef` |
| Generated | 2026-03-24T15:18:06Z |

Source tables joined (inner on `id`):
- `id_information.csv` — track ID, Spotify ID, title, artist
- `id_metadata.csv` — tempo, key, mode, duration, year
- `id_tags.csv` — Last.fm tag descriptors
- `id_genres.csv` — genre labels
- `id_lang.csv` (left join) — language tags

Raw source files are in `06_data_and_sources/music4all_raw/`.

---

## 3. Stage-by-Stage Reference

### BL-001 — Ingestion Schema Definition
- **Script**: `implementation_notes/bl001_bl002_ingestion/ingest_history_parser.py`
- **Module files**: `spotify_auth.py`, `spotify_client.py`, `spotify_resilience.py`, `spotify_artifacts.py`, `spotify_mapping.py`, `spotify_io.py`
- **Purpose**: Defines the canonical listening-event schema and CSV ingestion parser for offline-format history files
- **Status**: Complete. Used as reference schema and in Spotify export normalization
- **State log**: `implementation_notes/bl001_bl002_ingestion/bl001_state_log_2026-03-24.md`

### BL-002 — Spotify API Export
- **Script**: `implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`
- **Output dir**: `implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/`
- **Latest run ID**: `SPOTIFY-EXPORT-20260324-210031-788770`
- **Key stats** (latest export, 2026-03-24T21:01Z):

| Source | Count |
|---|---|
| Top tracks — long term | 5,114 |
| Top tracks — medium term | 3,029 |
| Top tracks — short term | 602 |
| Saved tracks | 171 |
| Playlists | 4 |
| Playlist items | 31 |
| Recently played | 50 |

- **Key files**:
  - `spotify_top_tracks_flat.csv` — 3.2 MB, all time ranges flattened
  - `spotify_saved_tracks.json` — 522 KB
  - `spotify_recently_played.json` — 146 KB
  - `spotify_resilience_cache.sqlite` — 18 MB (SQLite 24h TTL API cache)
  - `spotify_export_run_summary.json` — run metadata + counts
- **Ingestion features**: OAuth PKCE flow, pagination for all endpoints, SQLite resilience cache with 24h TTL, fail-fast on extreme Retry-After windows, full request log
- **Status**: Complete — real data available
- **State log**: `implementation_notes/bl001_bl002_ingestion/bl002_state_log_2026-03-24.md`
- **Runbook**: `implementation_notes/bl001_bl002_ingestion/spotify_api_ingestion_runbook.md`

### BL-003 — DS-001 Spotify Seed Builder
- **Script**: `implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`
- **Output dir**: `implementation_notes/bl003_alignment/outputs/`
- **Purpose**: Joins exported Spotify tracks against DS-001 candidate corpus using two alignment strategies (Spotify ID exact match, then normalized title+artist metadata match). Filters by `input_scope` from run-config to control which source types are used. Emits a source-scope manifest.
- **Latest run** (via BL-013 refresh-seed, 2026-03-24T22:13Z):

| Metric | Value |
|---|---|
| Input events (after scope filter) | 637 |
| Matched by Spotify ID | 160 |
| Matched by metadata | 64 |
| Unmatched | 413 |
| Seed table rows | 221 |

- **Outputs**:
  - `bl003_ds001_spotify_seed_table.csv` — 57 KB, seed event rows
  - `bl003_ds001_spotify_matched_events.jsonl` — 180 KB, full matched events
  - `bl003_ds001_spotify_trace.csv` — 118 KB, per-event alignment trace
  - `bl003_ds001_spotify_unmatched.csv` — 75 KB, unmatched events
  - `bl003_ds001_spotify_summary.json` — run metadata + counts
  - `bl003_source_scope_manifest.json` — active scope flags and filter stats
- **Input scope control** (`input_scope` from run-config):
  - `include_top_tracks` + `top_time_ranges` — which time ranges to include
  - `include_saved_tracks` + `saved_tracks_limit`
  - `include_playlists` + `playlists_limit` + `playlist_items_per_playlist_limit`
  - `include_recently_played` + `recently_played_limit`
- **Status**: Complete. DS-001 path active; BL-021 scope actuation confirmed via EXP-042
- **State log**: `implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md`

### BL-004 — Preference Profile
- **Script**: `implementation_notes/bl004_profile/build_bl004_preference_profile.py`
- **Output dir**: `implementation_notes/bl004_profile/outputs/`
- **Purpose**: Builds a weighted preference profile from BL-003 seed events. Derives lead genres, genre distribution, tag distribution, and audio-feature centers. Persists effective input scope and run-config provenance.
- **Latest run ID**: `BL004-PROFILE-20260324-221335-715210`
- **Key outputs** (current):

| Metric | Value |
|---|---|
| Matched seed count | 221 |
| Total effective weight | 594.5 |
| Dominant lead genre | classic rock (weight 215.4) |
| Config source | run_config |

- **Outputs**:
  - `bl004_preference_profile.json` — profile vectors (tags, genres, audio feature centers)
  - `bl004_profile_summary.json` — top genres, config provenance, input_scope
  - `bl004_seed_trace.csv` — 36 KB, per-seed weight trace
- **Run-config controls**: `user_id`, `top_tag_limit`, `top_genre_limit`, `top_lead_genre_limit`, `influence_track_boost`, `recency_decay_rate`
- **Status**: Complete
- **State log**: `implementation_notes/bl004_profile/bl004_state_log_2026-03-24.md`

### BL-005 — Candidate Filter
- **Script**: `implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`
- **Output dir**: `implementation_notes/bl005_retrieval/outputs/`
- **Purpose**: Filters DS-001 109,269 candidates down to a candidate pool. Keep rule: `not seed AND (semantic_score >= 2 OR (semantic_score >= 1 AND numeric_pass_count >= 1))`. Uses profile lead genres, tag sets, and audio feature proximity.
- **Latest run ID**: `BL005-FILTER-20260324-220924-588977`
- **Key stats**:

| Metric | Value |
|---|---|
| Total candidates | 109,269 |
| Filtered candidates (kept) | 56,700 |
| Retention rate | ~51.9% |

- **Outputs**:
  - `bl005_filtered_candidates.csv` — 12.9 MB, kept candidates
  - `bl005_candidate_decisions.csv` — 17.7 MB, full decision audit trail
  - `bl005_candidate_diagnostics.json` — run metadata + filter stats
- **Numeric thresholds** (from run-config): tempo ±20, key ±2, mode ±0.5, duration_ms ±45000
- **Status**: Complete
- **State log**: `implementation_notes/bl005_retrieval/bl005_state_log_2026-03-24.md`

### BL-006 — Candidate Scoring
- **Script**: `implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`
- **Output dir**: `implementation_notes/bl006_scoring/outputs/`
- **Purpose**: Scores all 56,700 filtered candidates against the preference profile using weighted component similarity. Active weight set is post-retune (numeric-leading in top-100).
- **Latest run ID**: `BL006-SCORE-20260324-220927-040002`
- **Active component weights**:

| Component | Weight |
|---|---|
| tempo | 0.20 |
| duration_ms | 0.13 |
| key | 0.13 |
| mode | 0.09 |
| lead_genre | 0.17 |
| genre_overlap | 0.12 |
| tag_overlap | 0.16 |

- **Score statistics**:

| Stat | Value |
|---|---|
| Candidates scored | 56,700 |
| Max score | 0.818 |
| Min score | 0.004 |
| Mean score | 0.241 |
| Median score | 0.228 |

- **Component balance (top-100)** — numeric mean 0.385 > semantic mean 0.293 (numeric-leading after retune)
- **Outputs**:
  - `bl006_scored_candidates.csv` — 8.4 MB, all scored candidates ranked
  - `bl006_score_summary.json` — stats, component balance diagnostics, top-10
- **Status**: Complete. Post-retune baseline locked
- **State log**: `implementation_notes/bl006_scoring/bl006_state_log_2026-03-24.md`
- **Quality snapshot**: `implementation_notes/bl006_scoring/bl006_top50_quality_snapshot_2026-03-24.md`

### BL-007 — Playlist Assembly
- **Script**: `implementation_notes/bl007_playlist/build_bl007_playlist.py`
- **Output dir**: `implementation_notes/bl007_playlist/outputs/`
- **Purpose**: Assembles a 10-track playlist from scored candidates using deterministic rule-based selection: score threshold (0.35), genre diversity cap (max 4 per genre), consecutive genre cap (max 2), target size (10).
- **Latest run ID**: `BL007-ASSEMBLE-20260324-220929-541533`
- **Key stats**:

| Metric | Value |
|---|---|
| Candidates evaluated | 56,700 |
| Playlist length | 10 |
| Score range | 0.780 – 0.818 |
| Genre cap hits (R2) | 5 |

- **Outputs**:
  - `bl007_playlist.json` — 10-track playlist with positions, scores, genres
  - `bl007_assembly_trace.csv` — 3.8 MB, full per-candidate rule trace
  - `bl007_assembly_report.json` — counts, rule hits, genre mix
- **Run-config controls**: `target_size`, `min_score_threshold`, `max_per_genre`, `max_consecutive`
- **Status**: Complete
- **State log**: `implementation_notes/bl007_playlist/bl007_state_log_2026-03-24.md`

### BL-008 — Transparency Explanations
- **Script**: `implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`
- **Output dir**: `implementation_notes/bl008_transparency/outputs/`
- **Purpose**: Generates per-track explanation payloads for each playlist track. Each payload includes a natural-language `why_selected` sentence and a score breakdown showing each component's contribution. Derives component list dynamically from BL-006 active weights (no hardcoded components).
- **Latest run ID**: `BL008-EXPLAIN-20260324-195641-957331`
- **Outputs**:
  - `bl008_explanation_payloads.json` — 25 KB, 10 explanation objects
  - `bl008_explanation_summary.json` — metadata, top-contributor distribution
- **Status**: Complete
- **State log**: `implementation_notes/bl008_transparency/bl008_state_log_2026-03-24.md`

### BL-009 — Observability Log
- **Script**: `implementation_notes/bl009_observability/build_bl009_observability_log.py`
- **Output dir**: `implementation_notes/bl009_observability/outputs/`
- **Purpose**: Captures comprehensive run-level observability: stage run IDs, artifact hashes, configuration snapshots, counts, and provenance. Persists effective input_scope and run-config details. Produces canonical JSON log and flat CSV index.
- **Latest run ID**: `BL009-OBSERVE-20260324-220931-086881`
- **Recorded upstream run IDs**:
  - BL-006: `BL006-SCORE-20260324-220927-040002`
  - BL-007: `BL007-ASSEMBLE-20260324-220929-541533`
  - BL-008: `BL008-EXPLAIN-20260324-195641-957331`
- **Outputs**:
  - `bl009_run_observability_log.json` — 24 KB, full run log
  - `bl009_run_index.csv` — single-row run summary for fast lookup
- **Status**: Complete
- **State log**: `implementation_notes/bl009_observability/bl009_state_log_2026-03-24.md`

### BL-010 — Reproducibility Check
- **Script**: `implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`
- **Output dir**: `implementation_notes/bl010_reproducibility/outputs/`
- **Purpose**: Verifies deterministic reproducibility by running BL-004 through BL-009 three times against fixed inputs and comparing stable content fingerprints. Report covers per-stage and per-artifact determinism.
- **Latest run ID**: `BL010-REPRO-20260324-200214`
- **Result**: `deterministic_match=true`, `first_mismatch_artifact=null`, all 3 replays pass
- **Run time**: 31.9 seconds (3 full end-to-end replays)
- **Note**: Uses synthetic bootstrap assets (`bl016_*`) as fixed inputs, not real DS-001 data — this is by design to ensure reproducibility is measured against a stable, version-controlled input set
- **Outputs**:
  - `bl010_reproducibility_report.json` — 35 KB, per-artifact fingerprint comparison
  - `bl010_reproducibility_run_matrix.csv` — per-stage pass/fail matrix
  - `bl010_reproducibility_config_snapshot.json` — fixed input hashes
- **Status**: Complete. Determinism confirmed on current baseline
- **State log**: `implementation_notes/bl010_reproducibility/bl010_state_log_2026-03-24.md`

### BL-011 — Controllability Check
- **Script**: `implementation_notes/bl011_controllability/run_bl011_controllability_check.py`
- **Output dir**: `implementation_notes/bl011_controllability/outputs/`
- **Purpose**: Verifies behavioral sensitivity to control-surface changes by running 5 pre-defined scenarios (baseline, no_influence_tracks, valence_weight_up, stricter_thresholds, looser_thresholds) and comparing candidate pool, ranking, and playlist outcomes.
- **Latest run**: 2026-03-21T19:08Z (run from within controllability runner)
- **Scenarios**:
  - `baseline` — standard BL-010 config
  - `no_influence_tracks` — influence boost disabled
  - `valence_weight_up` — increased valence/tag weight
  - `stricter_thresholds` — tighter numeric proximity thresholds
  - `looser_thresholds` — wider numeric proximity thresholds
- **Outputs**:
  - `bl011_controllability_report.json` — 46 KB, scenario comparison
  - `bl011_controllability_run_matrix.csv` — 5-row per-scenario results
  - `bl011_controllability_config_snapshot.json` — 17 KB, scenario effective configs
  - `scenarios/` — per-scenario pipeline artifacts (BL-004 through BL-007 outputs)
- **Status**: Complete. Non-zero behavioral deltas confirmed across all scenarios
- **State log**: covered by backlog BL-011 done entry

### BL-013 — Pipeline Orchestrator
- **Script**: `implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`
- **Output dir**: `implementation_notes/bl013_entrypoint/outputs/`
- **Purpose**: Thin Python orchestrator that invokes BL-004 through BL-009 in order. Supports optional stage subset selection and structured JSON run summary. Supports `--refresh-seed` flag to pre-run BL-003 before selected stages.
- **Latest run ID**: `BL013-ENTRYPOINT-20260324-221334-097740`
- **Latest run result**: `overall_status=pass`, 2 stages (BL-003 + BL-004), 0 failures
- **Usage** (from `bl013_run_command.md`):
  ```
  # Full pipeline:
  python run_bl013_pipeline_entrypoint.py --stages BL-004 BL-005 BL-006 BL-007 BL-008 BL-009

  # Full pipeline with scope-aware seed refresh:
  python run_bl013_pipeline_entrypoint.py --refresh-seed --stages BL-004 BL-005 BL-006 BL-007 BL-008 BL-009 --run-config path/to/config.json
  ```
- **Run-config transport**: sets `BL_RUN_CONFIG_PATH` env var before each stage subprocess
- **Outputs**:
  - `bl013_orchestration_run_latest.json` — symlink-style latest alias
  - `bl013_orchestration_run_{RUN_ID}.json` — per-run results
- **Status**: Complete
- **Docs**: `implementation_notes/bl013_entrypoint/bl013_run_command.md`

### BL-014 — Sanity Checks
- **Script**: `implementation_notes/bl014_quality/run_bl014_sanity_checks.py`
- **Output dir**: `implementation_notes/bl014_quality/outputs/`
- **Purpose**: Automated post-run artifact audit. 21 checks across: schema validation, cross-stage artifact hash continuity, count consistency, run-id format, and required-field presence.
- **Last run**: 2026-03-22T03:45Z (against BL-020 DS-002 baseline; still valid for artifact structure)
- **Result**: 21/21 checks passed
- **Outputs**:
  - `bl014_sanity_report.json` — check results
  - `bl014_sanity_run_matrix.csv` — check summary
  - `bl014_sanity_config_snapshot.json` — config at time of checks
- **Status**: Complete

### BL-016 — Synthetic Test Assets (Bootstrap Mode)
- **Purpose**: Generated pre-aligned synthetic data for early bootstrap pipeline testing before real DS-001 data was available
- **Status**: Complete/frozen. **Moved to `_archive_2026-03-24/test_assets/` on 2026-03-24 cleanup.**
  BL-010 reproducibility evidence already captured (deterministic_match=true, 3 replays pass, report on disk).
  Restore from archive if BL-010 needs to be re-run.
- **Archived assets**:
  - `bl016_synthetic_aligned_events.jsonl` — 36 synthetic events
  - `bl016_candidate_stub.csv` — 100-track synthetic candidate table
  - `bl016_asset_manifest.json` — asset hashes
  - `sample_listening_history.csv` — CSV test fixture

---

## 4. Run-Config System (BL-021)

**Schema version**: `run-config-v1`  
**Transport**: `BL_RUN_CONFIG_PATH` environment variable  
**Merge strategy**: run-config deepmerges over stage defaults; unknown keys rejected  
**Utility module**: `implementation_notes/bl000_run_config/run_config_utils.py`  
**Template**: `implementation_notes/bl000_run_config/run_config_template_v1.json`

### Resolved controls per stage:
- **BL-003**: `input_scope` (source selection + limits)
- **BL-004**: `user_id`, `top_tag_limit`, `top_genre_limit`, `top_lead_genre_limit`, `influence_track_boost`, `recency_decay_rate`; also receives `input_scope` for provenance recording
- **BL-005**: `top_lead_genre_limit`, `numeric_thresholds`
- **BL-006**: `base_component_weights`, `numeric_thresholds`
- **BL-007**: `target_size`, `min_score_threshold`, `max_per_genre`, `max_consecutive`
- **BL-008**: derives from BL-006 active weights (no additional controls)
- **BL-009**: `log_level`; also receives `input_scope` for provenance recording

### input_scope controls (BL-021):
```json
{
  "input_scope": {
    "source_family": "spotify_api_export",
    "include_top_tracks": true,
    "top_time_ranges": ["short_term", "medium_term", "long_term"],
    "include_saved_tracks": true,
    "saved_tracks_limit": null,
    "include_playlists": true,
    "playlists_limit": null,
    "playlist_items_per_playlist_limit": null,
    "include_recently_played": true,
    "recently_played_limit": null
  }
}
```

### Evidence artifacts (BL-021 A/B probes):
Located in `implementation_notes/bl000_run_config/probe_comparison_outputs/`
- `bl021_probe_comparison_actuated_summary.json` — non-zero deltas confirming behavioral control
- `bl003_source_scope_manifest_probeA_actuated.json` — scope manifest from actuated run
- Profile + observability snapshots for probe A (baseline) and A-actuated (scope-filtered)

---

## 5. Website Layer

### Backend — `setup/website_api_server.py` (55 KB)
Flask development server providing:

| Endpoint group | Endpoints |
|---|---|
| Spotify ingestion | `POST /api/spotify/export/start`, `GET /api/spotify/export/status`, `POST /api/spotify/export/cancel` |
| Pipeline | `GET /api/pipeline/stages`, `POST /api/pipeline/run`, `GET /api/pipeline/status/{id}`, `GET /api/pipeline/result/{id}` |
| Profile | `GET /api/profile`, `POST /api/profile/clear`, `GET /api/profile/basis` |
| Results | `GET /api/results/latest`, `GET /api/results/history`, `GET /api/results/run/{id}` |
| Evidence | `GET /api/evidence/bundle`, `GET /api/evidence/export` |
| Observability | `GET /api/health`, `GET /api/runtime/config`, `POST /api/runtime/config/validate` |

### Frontend pages (in `website/`):

| File | Purpose |
|---|---|
| `index.html` | Landing page / navigation hub |
| `import.html` | Spotify import control-room UI |
| `profile_basis.html` | Profile source configuration |
| `run.html` | Pipeline run controls + stage selection |
| `results.html` | Playlist results + explanation viewer |
| `history.html` | Run history browser |
| `stage_bl004.html` – `stage_bl009.html` | Per-stage parameter tuning pages |

### Frontend JS modules:

| File | Purpose |
|---|---|
| `app.js` | Spotify ingestion state machine + import flow |
| `profile_basis.js` | Source selection UI + profile summary |
| `run.js` | Pipeline orchestration UI |
| `results.js` | Playlist + explanation rendering |
| `history.js` | History table rendering |
| `stage_page.js` | Shared stage parameter control logic |
| `style.css` | Global design system (dark control-room theme) |

### Startup:
```powershell
# From thesis-main root:
powershell -ExecutionPolicy Bypass -File "07_implementation/setup/start_website.ps1"
# Opens browser to http://127.0.0.1:5501
```

Smoke test: `07_implementation/setup/smoke_website_api.ps1`

---

## 6. Key Evidence Artifacts

| Experiment | Description | Location |
|---|---|---|
| EXP-022 | BL-003 Last.fm enrichment (DS-002 path, 5,361 tags, ~101 min) | experiment_log.md |
| EXP-026 | BL-005 filter pass on DS-002 (1,740 kept) | experiment_log.md |
| EXP-027 | BL-006 scoring on DS-002 (semantic-only mode) | experiment_log.md |
| EXP-028 | BL-007 assembly (10-track, classic rock dominant) | experiment_log.md |
| EXP-031 | BL-014 sanity checks 21/21 pass | experiment_log.md |
| EXP-035 | BL-006 retune closure (numeric-leading top-100) | experiment_log.md |
| EXP-036 | BL-007 refresh against retune baseline | experiment_log.md |
| EXP-037 | BL-008 transparency refresh | experiment_log.md |
| EXP-038 | BL-009 observability refresh | experiment_log.md |
| EXP-039 | BL-010 reproducibility on current baseline (3-replay pass) | experiment_log.md |
| EXP-040 | BL-021 scope persistence probe | experiment_log.md |
| EXP-041 | BL-021 A/B zero-delta (before actuation) | experiment_log.md |
| EXP-042 | BL-021 A/B non-zero delta (after actuation, confirmed) | experiment_log.md |

Key test notes: TC-BL021-R2-001 through TC-BL021-R2-003 in `test_notes.md`.

---

## 7. Active File Manifest

### Root-level governance files
```
backlog.md                   — implementation task status (BL-001 to BL-022)
experiment_log.md            — all experiment records (EXP-001 to EXP-042+)
test_notes.md                — all test cases (TC-*)
implementation_plan.md       — stage-level technical plan
artefact_refinement_spec.md  — locked artefact scope and refinement spec
website.md                   — website blueprint + execution log
SPOTIFY_INTEGRATION.md       — Spotify integration reference
IMPLEMENTATION_STATE_2026-03-24.md  — this file
```

### Setup and startup
```
setup/website_api_server.py        — Flask backend (55 KB, ACTIVE)
setup/start_website.ps1            — one-command startup script
setup/start_website.cmd            — CMD wrapper
setup/bootstrap_python_environment.ps1  — venv setup script
setup/bootstrap_python_environment.cmd  — CMD wrapper
setup/python_environment_setup.md  — setup docs
setup/smoke_website_api.ps1        — API smoke test
```

### Data layer
```
implementation_notes/bl000_data_layer/build_ds001_working_dataset.py          — DS-001 builder (ACTIVE)
implementation_notes/bl000_data_layer/outputs/ds001_working_candidate_dataset.csv       — 23.2 MB (ACTIVE)
implementation_notes/bl000_data_layer/outputs/ds001_working_candidate_dataset_manifest.json  — (ACTIVE)
```

### Ingestion (BL-001, BL-002)
```
implementation_notes/bl001_bl002_ingestion/ingest_history_parser.py       — BL-001 CSV parser
implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py  — BL-002 API exporter
implementation_notes/bl001_bl002_ingestion/spotify_auth.py                — OAuth module
implementation_notes/bl001_bl002_ingestion/spotify_client.py              — API client module
implementation_notes/bl001_bl002_ingestion/spotify_resilience.py          — cache + rate-limit module
implementation_notes/bl001_bl002_ingestion/spotify_artifacts.py           — artifact serialization
implementation_notes/bl001_bl002_ingestion/spotify_mapping.py             — field mapping
implementation_notes/bl001_bl002_ingestion/spotify_io.py                  — file I/O helpers
implementation_notes/bl001_bl002_ingestion/spotify_env_template.ps1       — env var template
implementation_notes/bl001_bl002_ingestion/spotify_schema_reference.md    — schema reference
implementation_notes/bl001_bl002_ingestion/spotify_api_ingestion_runbook.md  — runbook
implementation_notes/bl001_bl002_ingestion/bl001_state_log_2026-03-24.md
implementation_notes/bl001_bl002_ingestion/bl002_state_log_2026-03-24.md
implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/    — current export artifacts
```

### Alignment (BL-003)
```
implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py  — active (ACTIVE)
implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md
implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_seed_table.csv
implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_matched_events.jsonl
implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_trace.csv
implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_unmatched.csv
implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_summary.json
implementation_notes/bl003_alignment/outputs/bl003_source_scope_manifest.json
```

### Profile / Retrieval / Scoring / Playlist / Transparency / Observability (BL-004..009)
```
implementation_notes/bl004_profile/build_bl004_preference_profile.py
implementation_notes/bl004_profile/bl004_state_log_2026-03-24.md
implementation_notes/bl004_profile/outputs/bl004_preference_profile.json
implementation_notes/bl004_profile/outputs/bl004_profile_summary.json
implementation_notes/bl004_profile/outputs/bl004_seed_trace.csv

implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py
implementation_notes/bl005_retrieval/bl005_state_log_2026-03-24.md
implementation_notes/bl005_retrieval/outputs/bl005_filtered_candidates.csv
implementation_notes/bl005_retrieval/outputs/bl005_candidate_decisions.csv
implementation_notes/bl005_retrieval/outputs/bl005_candidate_diagnostics.json

implementation_notes/bl006_scoring/build_bl006_scored_candidates.py
implementation_notes/bl006_scoring/bl006_state_log_2026-03-24.md
implementation_notes/bl006_scoring/bl006_top50_quality_snapshot_2026-03-24.md
implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv
implementation_notes/bl006_scoring/outputs/bl006_score_summary.json

implementation_notes/bl007_playlist/build_bl007_playlist.py
implementation_notes/bl007_playlist/bl007_state_log_2026-03-24.md
implementation_notes/bl007_playlist/outputs/bl007_playlist.json
implementation_notes/bl007_playlist/outputs/bl007_assembly_trace.csv
implementation_notes/bl007_playlist/outputs/bl007_assembly_report.json

implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py
implementation_notes/bl008_transparency/bl008_state_log_2026-03-24.md
implementation_notes/bl008_transparency/outputs/bl008_explanation_payloads.json
implementation_notes/bl008_transparency/outputs/bl008_explanation_summary.json

implementation_notes/bl009_observability/build_bl009_observability_log.py
implementation_notes/bl009_observability/bl009_state_log_2026-03-24.md
implementation_notes/bl009_observability/outputs/bl009_run_observability_log.json
implementation_notes/bl009_observability/outputs/bl009_run_index.csv
```

### Evaluation stages (BL-010, BL-011, BL-014)
```
implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py
implementation_notes/bl010_reproducibility/bl010_state_log_2026-03-24.md
implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_report.json
implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_run_matrix.csv
implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_config_snapshot.json

implementation_notes/bl011_controllability/run_bl011_controllability_check.py
implementation_notes/bl011_controllability/bl011_state_log_2026-03-24.md
implementation_notes/bl011_controllability/outputs/bl011_controllability_report.json
implementation_notes/bl011_controllability/outputs/bl011_controllability_run_matrix.csv
implementation_notes/bl011_controllability/outputs/bl011_controllability_config_snapshot.json
implementation_notes/bl011_controllability/outputs/scenarios/  — 5 scenario sub-folders

implementation_notes/bl014_quality/run_bl014_sanity_checks.py
implementation_notes/bl014_quality/outputs/bl014_sanity_report.json
implementation_notes/bl014_quality/outputs/bl014_sanity_run_matrix.csv
implementation_notes/bl014_quality/outputs/bl014_sanity_config_snapshot.json
```

### Bootstrap test assets (BL-016)
```
[ARCHIVED] implementation_notes/test_assets/ → _archive_2026-03-24/test_assets/
```


### Run config (BL-021)
```
implementation_notes/bl000_run_config/run_config_utils.py
implementation_notes/bl000_run_config/run_config_template_v1.json
implementation_notes/bl000_run_config/run_config_bl021_probe_v1.json
implementation_notes/bl000_run_config/run_config_bl021_probe_v2.json
implementation_notes/bl000_run_config/probe_comparison_outputs/          — BL-021 evidence artifacts
```

### Pipeline entrypoint (BL-013)
```
implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py
implementation_notes/bl013_entrypoint/bl013_run_command.md
implementation_notes/bl013_entrypoint/outputs/bl013_orchestration_run_latest.json
implementation_notes/bl013_entrypoint/outputs/bl013_orchestration_run_BL013-ENTRYPOINT-20260324-*.json
```

### Website frontend
```
website/index.html
website/import.html
website/profile_basis.html
website/run.html
website/results.html
website/history.html
website/stage_bl004.html  website/stage_bl005.html  website/stage_bl006.html
website/stage_bl007.html  website/stage_bl008.html  website/stage_bl009.html
website/app.js
website/profile_basis.js
website/run.js
website/results.js
website/history.js
website/stage_page.js
website/style.css
```

---

## 8. What Was Archived (see `_archive_2026-03-24/`)

The following categories of files were moved to `_archive_2026-03-24/`:

- **DS-002 pipeline scripts** — `bl003_align_spotify_api_to_ds002.py`, `build_bl003_partial_from_cache.py`, `build_bl019_ds002_dataset.py`
- **DS-002 dataset outputs** — `bl019_ds002_*` files, 5.5 MB
- **Raw Onion canonical layer** — `onion_canonical_track_table.csv` (73 MB), coverage report, manifest (superseded by `build_ds001_working_dataset.py`)
- **BL-020 DS-002 era alignment outputs** — `bl020_aligned_events.jsonl` (~5.6 MB), `bl020_alignment_report.json`, `bl020_lastfm_tag_cache.json` (~5.1 MB)
- **Old BL-013 runs from 2026-03-21** — 2 run JSON files
- **BL-010 replay data** — `replay_01/`, `replay_02/`, `replay_03/` (each ~55 MB of stage outputs)
- **Pre-retune scoring snapshot** — `bl006_scored_candidates_pre_retune.csv` (8.6 MB), `bl006_score_summary_pre_retune.json`
- **Temp planning docs** — `bl006_bl010_clean_commit_plan_2026-03-24.md`, `bl006_bl010_freeze_checklist_2026-03-24.md`, `candidate_corpus_feasibility_review_2026-03-19.md`, `full_dataset_acquisition_checklist_2026-03-21.md`, `ds001_spotify_join_plan.md`
- **Old BL-002 healthcheck run** — `_bl002_healthcheck_2026-03-24/`
- **Stale ingestion archive** — `_safekeep_unused_2026-03-23/` (re-archived)
- **Stale misc** — `import_data_page_plan.md`, `cleanup_archive_log_2026-03-23.md`, `bl001_spotify_input_output_mapping.md`, root-level `index.html`
- **Bootstrap test assets (BL-016)** — `implementation_notes/test_assets/` (moved 2026-03-24)
- **Bootstrap test run outputs** — `implementation_notes/run_outputs/` (tc001_* test run artifacts)

Total approximated archive size: **~360 MB**

Active file count after cleanup: **191 files** (implementation_notes + setup + website)  
Archived in `_archive_2026-03-24/`: **101 files**

---

## 9. Current Backlog Status Summary

| ID | Name | Status |
|---|---|---|
| BL-001 | Ingestion schema | done |
| BL-002 | Spotify API export | done |
| BL-003 | DS-001 seed build | done |
| BL-004 | Preference profile | done |
| BL-005 | Candidate filter | done |
| BL-006 | Scoring | done |
| BL-007 | Playlist assembly | done |
| BL-008 | Transparency explanations | done |
| BL-009 | Observability | done |
| BL-010 | Reproducibility check | done |
| BL-011 | Controllability check | done |
| BL-013 | Pipeline orchestrator | done |
| BL-014 | Sanity checks | done |
| BL-016 | Synthetic test assets | done |
| BL-017 | Onion canonical dataset layer | done |
| BL-019 | DS-002 dataset build | done |
| BL-020 | Real-data end-to-end run | done |
| BL-021 | Source-scope contract | done |
| BL-022 | Corpus-path switching | deferred |

Full details: `backlog.md`

---

## 10. 2026-03-25 Baseline Refresh

Latest validated baseline (post-alignment):

- BL-010 reproducibility
  - run_id: `BL010-REPRO-20260324-234322`
  - status: pass (`deterministic_match=true`)
  - fixed_input_source: `active_pipeline_outputs`
- BL-011 controllability
  - run_id: `BL011-CTRL-20260324-235114`
  - status: pass
  - all scenario checks (repeat consistency, observable shift, expected direction): true
- BL-013 orchestrator
  - run_id: `BL013-ENTRYPOINT-20260324-235248-642823`
  - status: pass
  - BL-004 through BL-009: all pass

Operational note:
- BL-009, BL-010, and BL-011 are now aligned with the active BL-004..BL-009 path and no longer hard-depend on archived BL-016/BL-017 assets.

