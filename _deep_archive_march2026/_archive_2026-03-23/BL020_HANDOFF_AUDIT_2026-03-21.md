# BL-020 Implementation Redo: Pre-Work Audit
**Date: 2026-03-21**  
**Status: Ready for handoff to implementation phase**

---

## Executive Summary

The workspace has **ingestion schema locked**, **canonical dataset ready** (DS-002, 9,330 tracks), and **all pipeline scaffold code in place**. However, **no real user data has been ingested yet**, and all current pipeline artifacts are stale (built from synthetic test data). 

**BL-020 is ready to start once you have a real ingestion output to feed into the profile builder.**

---

## 1. INGESTION LAYER — READY FOR DATA COLLECTION

### BL-001: Schema (✅ LOCKED)
- **Path**: Spotify Extended Streaming History CSV
- **Schema**: 10 normalized fields
  - `event_id | track_name | artist_name | album_name | isrc | played_at | ms_played | source_platform | ingest_run_id | row_quality_flag`
- **Quality flags**: Detects missing ISRC, invalid timestamp, negative ms_played
- **Documentation**: 
  - Mapping details in `06_data_and_sources/schema_notes.md`
  - Input/output mapping: `07_implementation/implementation_notes/bl001_bl002_ingestion/bl001_spotify_input_output_mapping.md`

### BL-002: Ingestion Scripts (✅ IMPLEMENTED)
Two paths available:

#### CSV Parser
- **Script**: `07_implementation/implementation_notes/bl001_bl002_ingestion/ingest_history_parser.py`
- **Function**: Deterministic parser for Spotify CSV export
- **Tested**: Yes (sample output shows rows_total=7, rows_valid=4, rows_invalid=3)
- **Output format**: Normalized JSONL or CSV with quality flags

#### Web API Exporter
- **Script**: `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`
- **Function**: Collects from Spotify API — top tracks, saved tracks, playlists, playlist items
- **Auth**: OAuth2 + pagination support
- **Runbook**: `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/spotify_api_ingestion_runbook.md`
- **Status**: Ready to run (requires OAuth token + cooldown window per UI-007)
- **Test outputs**: Available in `ingestion/outputs/spotify_api_export/`

### ⚠️ BLOCKING ISSUE
**No real user listening history has been processed yet.** 
- CSV parser is ready but needs input file
- Spotify API exporter is coded but needs user authorization restart
- **Decision D-020** tracks Music4All dataset access (email sent 2026-03-21, awaiting response)

---

## 2. CANONICAL DATASET — READY FOR PIPELINE CONSUMPTION

### BL-019: DS-002 Integrated Dataset (✅ COMPLETED 2026-03-21)

**Location**: `07_implementation/implementation_notes/bl000_data_layer/outputs/`

#### Main Artifact
- **File**: `bl019_ds002_integrated_candidate_dataset.csv`
- **Records**: 9,330 tracks
- **Schema**: `track_id | year | duration | tempo | loudness | key | mode | lastfm_tags | musicbrainz_mbid`
- **Quality**: All entries have valid numeric features (no nulls in core fields)

#### Join Coverage
```
Metadata coverage: 100% (MSD base)
Last.fm tags coverage: 100%
MusicBrainz mapping coverage: 93.6%
```
(from `bl019_ds002_integration_report.json`)

#### Supporting Files
- `bl019_ds002_dataset_manifest.json` — Schema description and provenance
- `bl019_ds002_quality_checks.csv` — All QA gates pass ✅

### Decision Context
- **Decision D-015** (2026-03-21): Activated **DS-002 (MSD subset)** as the active candidate corpus
- **Superseded**: `onion_canonical_track_table.csv` from BL-017 (Onion-only strategy)
- **Reasoning**: Feasibility review (`candidate_corpus_feasibility_review_2026-03-19.md`) recommended Onion, but D-015 prioritized MSD subset for deterministic, reproducible candidate set with broader feature coverage

---

## 3. PIPELINE SCAFFOLD & STALE ARTIFACTS

### Code Status
All pipeline components have implemented scripts **and test outputs exist** (but are obsolete).

| Component | Script File | Folder | Last Evidence |
| --- | --- | --- | --- |
| **Profile** (BL-004) | `build_bl004_preference_profile.py` | `profile/outputs/` | Synthetic user data; outputs in `bl004_preference_profile.json` |
| **Retrieval** (BL-005) | `build_bl005_candidate_filter.py` | `retrieval/outputs/` | Filtered against old dataset; outputs: `bl005_filtered_candidates.csv`, `bl005_candidate_decisions.csv` |
| **Scoring** (BL-006) | `build_bl006_scored_candidates.py` | `scoring/outputs/` | Scored old candidates; outputs: `bl006_scored_candidates.csv`, `bl006_score_summary.json` |
| **Playlist** (BL-007) | `build_bl007_playlist.py` | `playlist/outputs/` | Assembled from stale scores; outputs: `bl007_playlist.json`, `bl007_assembly_trace.csv`, `bl007_assembly_report.json` |
| **Transparency** (BL-008) | `build_bl008_explanation_payloads.py` | `transparency/outputs/` | Stale explanation artifacts: `bl008_explanation_payloads.json`, `bl008_explanation_summary.json` |
| **Observability** (BL-009) | `build_bl009_observability_log.py` | `observability/outputs/` | Stale run log: `bl009_run_observability_log.json`, `bl009_run_index.csv` |
| **Reproducibility** (BL-010) | `run_bl010_reproducibility_check.py` | `reproducibility/outputs/` | Stale test matrix: runs stored in dated scenario dirs |
| **Controllability** (BL-011) | `run_bl011_controllability_check.py` | `controllability/outputs/` | Stale test scenarios: `baseline/`, `no_influence_tracks/`, `valence_weight_up/`, etc. |

### Pipeline Entrypoint
- **Script**: `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`
- **Documentation**: `07_implementation/implementation_notes/bl013_entrypoint/bl013_run_command.md`
- **Status**: ✅ Ready to run (will invoke the full BL-004 → BL-013 chain)

### ⚠️ ARTIFACT INVALIDATION NOTICE
**All outputs in `implementation_notes/*/outputs/` folders are STALE and based on synthetic/test data or old ingestion.**

When you run BL-020, you will:
1. **Delete or archive** stale output folders
2. **Re-run** all components with:
   - Real ingestion events (from BL-001 or BL-002)
   - New canonical dataset: [bl019_ds002_integrated_candidate_dataset.csv](../implementation_notes/bl000_data_layer/outputs/bl019_ds002_integrated_candidate_dataset.csv)
3. **Regenerate** all artifacts (profile, candidates, scores, playlist, explanations, logs, test matrices)

---

## 4. ENVIRONMENT & DEPENDENCIES

### Python Setup
- **Version**: 3.11+ required
- **Bootstrap**: `.\07_implementation\setup\bootstrap_python_environment.cmd` (one command)
  - Creates `.venv` in workspace directory
  - Installs all packages from `requirements.txt`
  
### Pinned Packages
```
h5py==3.16.0            (MSD HDF5 access)
pypdf==6.9.1            (PDF ingestion support)
rapidfuzz==3.14.3       (fuzzy matching for alignment)
spotipy==2.23.0         (Spotify API client)
```

### Documentation
- `07_implementation/setup/python_environment_setup.md` — Bootstrap instructions + manual fallback

### Current Status
✅ Environment bootstrapped and ready. Package versions pinned and deterministic.

---

## 5. RECENT DECISIONS & CHANGE LOG ENTRIES

### Decisions (Decision Log)
- **D-005** (2026-03-19): Start with synthetic pre-aligned data; defer real alignment (BL-003) until core pipeline proven → unblocked Phase B
- **D-015** (2026-03-21): Activate DS-002 (MSD subset) as current candidate corpus → replaced Onion-only strategy
- **D-020** (2026-03-21): Music4All dataset access track — email sent to authors (awaiting response)

### Change Log Entries
- **C-065** (2026-03-21): Ingestion pipeline and database changed; full implementation redo required → **BL-020 P0**
- **BL-001 completion** (2026-03-21): Spotify CSV schema locked; mapping docs created
- **BL-002 completion** (2026-03-21): Parser + Web API exporter scripts implemented
- **BL-019 completion** (2026-03-21): DS-002 dataset (9,330 tracks) built, tested, and verified

---

## 6. BL-020 KICKOFF CHECKLIST

### Before Starting Implementation
- [ ] Real ingestion data acquired (either Spotify CSV or Music4All dataset access)
- [ ] Ingestion parser run against real data → produces valid event output
- [ ] Events loaded into memory/staging for profile builder consumption
- [ ] New canonical dataset confirmed available: `bl019_ds002_integrated_candidate_dataset.csv`

### During BL-020 Execution
- [ ] **Step 1**: Archive or delete all stale `/outputs/` folders in `implementation_notes/*/`
- [ ] **Step 2**: Run BL-004 (profile builder) against real ingestion events
- [ ] **Step 3**: Run BL-005 through BL-013 in sequence using the entrypoint script
- [ ] **Step 4**: Verify all new outputs exist and are dated 2026-03-21 or later
- [ ] **Step 5**: Document run outcomes in `experiment_log.md` (new EXP entry)
- [ ] **Step 6**: Update `test_notes.md` with any failures or deviations
- [ ] **Step 7**: Record completion of BL-020 in backlog.md

### Parallel Work (Optional)
- Monitor Music4All dataset access (D-020 track 1) — if granted, can pivot to BL-003 (real track alignment) sooner
- Prepare BL-014 (automated sanity checks) to run immediately after BL-020 completes

---

## 7. KEY FILES & REFERENCE LINKS

| Topic | File | Purpose |
| --- | --- | --- |
| **Schema** | `06_data_and_sources/schema_notes.md` | Ingestion schema definition |
| **Ingestion I/O** | `07_implementation/implementation_notes/bl001_bl002_ingestion/bl001_spotify_input_output_mapping.md` | Field mapping reference |
| **CSV Parser** | `07_implementation/implementation_notes/bl001_bl002_ingestion/ingest_history_parser.py` | Ready to use |
| **Web API Exporter** | `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py` + runbook | Requires OAuth restart |
| **Candidate Dataset** | `07_implementation/implementation_notes/bl000_data_layer/outputs/bl019_ds002_integrated_candidate_dataset.csv` | Feed to profile builder |
| **Feasibility Review** | `07_implementation/implementation_notes/bl000_data_layer/candidate_corpus_feasibility_review_2026-03-19.md` | Context for DC-D-015 decision |
| **Pipeline Entrypoint** | `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py` | Run full BL-004→BL-013 chain |
| **Run Command Docs** | `07_implementation/implementation_notes/bl013_entrypoint/bl013_run_command.md` | How to invoke the pipeline |
| **Backlog** | `07_implementation/backlog.md` | Master task tracker |
| **Change Log** | `00_admin/change_log.md` | All recorded changes (latest: C-065) |
| **Decision Log** | `00_admin/decision_log.md` | All decisions (latest: D-020) |

---

## 8. NEXT STEPS (For Implementation Chat)

When you switch to a new chat session for BL-020 execution:

1. **Reference this audit**: Link back to this file for context on what's ready and what's stale
2. **Clarify ingestion input**: Ask user for the actual user listening history data
3. **Run BL-004 first**: Profile builder is the pipeline entry point
4. **Follow the entrypoint script**: Use `run_bl013_pipeline_entrypoint.py` to chain all steps
5. **Log all outcomes**: Update `experiment_log.md` and `test_notes.md` as you go
6. **Mark BL-020 done** in backlog once all artifacts are regenerated and tested

---

**Audit prepared by**: AI (GitHub Copilot)  
**Date**: 2026-03-21  
**Status**: ✅ Ready for handoff — all prerequisites mapped, no blockers except real ingestion data
