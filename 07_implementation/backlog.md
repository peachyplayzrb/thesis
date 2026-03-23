# Backlog

## Priority Legend
- P0: Must complete for locked MVP and assessment evidence.
- P1: Strongly recommended quality improvement.
- P2: Optional stretch item if time permits.

## Handoff Snapshot (2026-03-21)
- Collaboration repo: `https://github.com/TimothySpiteri/thesis` (private).
- Primary working branch: `setup/initial-work`.
- Current local head at handoff prep: `93f6369624a55f33d544737aaea9c9f5b3152eb5`.
- Locked operating constraints: keep title/RQ/scope/methodology aligned with `00_admin/thesis_state.md` and use change proposals for protected changes.
- Current implementation status: all P0 items through `BL-020` and `BL-014` are done. Next practical work remains writing/citation hardening (`UI-002`, `UI-003`) and dataset-access governance closure (`UI-008`).
- Strategy update (2026-03-19, D-005): start with synthetic pre-aligned data. BL-001, BL-002, BL-003 deferred until after the core pipeline is proven end-to-end. See decision_log.md D-005.
- Strategy update (2026-03-21, D-015): activate the DS-002 corpus strategy (`MSD subset + Last.fm tags`) as the current BL-019 implementation path; MusicBrainz fields are optional metadata and currently unused.
- Ingestion update (2026-03-21): BL-001 schema is now locked to Spotify Extended Streaming History CSV as the selected single-adapter MVP path.
- Ingestion update (2026-03-21): BL-002 parser is implemented and a Spotify Web API max-export ingestion script now collects top tracks, saved tracks, playlists, and playlist items with OAuth + pagination.
- Environment update (2026-03-21): repo-local Python setup is now standardized via `requirements.txt` and one-command bootstrap under `07_implementation/setup/`.
- Implementation redo (2026-03-21, C-065): ingestion pipeline and database have changed; full pipeline redo required. BL-020 is now the top P0 item.
- Pre-BL-020 audit (2026-03-21): comprehensive readiness audit completed and logged in `BL020_HANDOFF_AUDIT_2026-03-21.md`. Historical note only; BL-020 is now complete.
- Recommended immediate next work order:
	1. Maintain writing evidence hardening for `UI-002` and `UI-003` in parallel.
	2. Progress UI-008 Music4All credential/terms closure while keeping DS-002 active unless activation gates pass.
	3. Optionally rerun BL-002 Spotify export to refresh snapshot data (not a blocker; one successful run already exists).
- Evidence-first reminder: for each completed backlog item, write the expected evidence artifact and link it in the matching file listed in the backlog table.

## Items
| ID | Priority | Status | Task | Evidence Output |
| --- | --- | --- | --- | --- |
| BL-001 | P0 | done | Define ingestion schema for one platform export path | `06_data_and_sources/schema_notes.md` Spotify mapping section + `07_implementation/implementation_notes/ingestion/bl001_spotify_input_output_mapping.md` |
| BL-002 | P0 | done | Implement ingestion parser and validation checks | `07_implementation/implementation_notes/ingestion/ingest_history_parser.py` + `07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py` + run outputs/logs |
| BL-003 | P0 | done | Implement Last.fm tag enrichment on real Spotify data with fallback lookup chain | `07_implementation/implementation_notes/ingestion/outputs/bl020_alignment_report.json` + `bl020_aligned_events.jsonl` + `bl020_lastfm_tag_cache.json` (2026-03-22 real-data run) |
| BL-004 | P0 | done | Build deterministic user preference profile generator | Profile artifact for at least one test user |
| BL-005 | P0 | done | Implement candidate retrieval and feature filtering | `07_implementation/implementation_notes/retrieval/outputs/bl005_filtered_candidates.csv` (1,740 filtered candidates) + diagnostics (2026-03-22 real-data run) |
| BL-006 | P0 | done | Implement deterministic scoring function with weighted components | Score breakdown table per track |
| BL-007 | P0 | done | Implement rule-based playlist assembly (diversity, coherence, ordering) | Rule compliance report per run |
| BL-008 | P0 | done | Add transparency outputs (score contribution + rule adjustment trace) | Human-readable explanation artifact |
| BL-009 | P0 | done | Add observability logging (config, seed/control params, run metadata) | Reproducible run log schema and examples |
| BL-010 | P0 | done | Execute reproducibility tests (same input/config => same output) | Test log in `07_implementation/test_notes.md` |
| BL-011 | P0 | done | Execute controllability tests (parameter sensitivity) | Comparative run matrix |
| BL-012 | P0 | done | Document limitations and failure modes from test outcomes | `02_foundation/limitations.md` + `08_writing/chapter5.md` notes |
| BL-013 | P1 | done | Add lightweight CLI or script entrypoint for repeatable runs | Run command documentation |
| BL-014 | P1 | done | Create automated sanity checks for input schema and deterministic output hashes | `07_implementation/implementation_notes/quality/run_bl014_sanity_checks.py` + outputs under `07_implementation/implementation_notes/quality/outputs/` |
| BL-015 | P2 | todo | Add second ingestion adapter scaffold (out of core scope) | Backlog-only design note |
| BL-016 | P0 | done | Create synthetic pre-aligned data assets for core pipeline development | `07_implementation/implementation_notes/test_assets/` — synthetic aligned JSONL + Music4All candidate stub CSV |
| BL-017 | P0 | done | Build Onion-only canonical dataset layer (track_id join + curated feature schema + data quality checks) | `07_implementation/implementation_notes/data_layer/` outputs: canonical track table, join-coverage report, selected-column manifest |
| BL-018 | P0 | done | Run candidate-corpus feasibility review before further canonical-layer work | `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md` |
| BL-019 | P0 | done | Build DS-002 integrated candidate dataset (`MSD subset + Last.fm tags`; optional MusicBrainz metadata) with deterministic joins and quality gates | `07_implementation/experiment_log.md` (`EXP-016`) + `07_implementation/test_notes.md` (`TC-DATASET-001`) + dataset outputs under `07_implementation/implementation_notes/data_layer/outputs/` |
| BL-020 | P0 | done | Redo full pipeline implementation against updated ingestion schema and database (C-065) — re-run BL-004 through BL-013 stages and regenerate all artifacts | **Completed (2026-03-22)**: BL-003 enriched 5,592 tracks (95.87% coverage). BL-004 semantic-only profile. BL-005 filtered 1,740 (18.62%). BL-006 ranked mean 0.214. BL-007 assembled 10-track playlist. BL-008 generated 10 explanations. BL-009 audit log complete. Evidence: EXP-022–030. **STATUS: FULLY COMPLETE.** |
| BL-021 | P1 | todo | Add user-selectable Spotify profile-source scope control (top tracks/saved tracks/playlist tracks + per-source limits) and persist selected scope in run metadata | Config/UI spec + source-selection manifest in run outputs + controllability test showing runtime/profile-effect deltas |
| BL-022 | P1 | todo | Add deterministic corpus fallback policy: try Music4All(-Onion) alignment first, then auto-fallback to current DS-002 semantic path when coverage thresholds are not met | Fallback policy spec + per-run path-selection metadata + A/B alignment coverage report |

## Completed
- `BL-020` — **FULLY COMPLETE (2026-03-22)**. Pipeline: BL-003 enrichment (5,592 tracks) → BL-004 profiling (semantic-only) → BL-005 filtering (1,740) → BL-006 scoring (ranked 0.77–0.01) → BL-007 playlist (10 tracks) → BL-008 transparency (10 explanations) → BL-009 observability (full audit log). All stages deterministic, fully auditable, submission-ready. Final observability log documents all stages with upstream run IDs, configuration snapshots, stage diag nostics, and artifact hashes.
- `BL-021` has been accepted as a deferred P1 design item (D-023): do not implement yet; keep current BL-020 stabilization as the active execution priority.
- `BL-022` has been accepted as a deferred P1 idea (D-025): define deterministic dataset-path fallback switching (Music4All-first when available, DS-002 fallback on low coverage) after BL-020 stabilization.

### Handoff Note (2026-03-22)
- Treat `07_implementation/implementation_notes/ingestion/outputs/bl020_alignment_report.json` as historical fuzzy-alignment evidence (stale for current BL-003 strategy).
- Current active `bl020_aligned_events.jsonl` was intentionally swapped to partial cache-derived content for test execution and can be restored from `bl020_aligned_events.pre_partial_backup_20260322-001050.jsonl`.
- Historical terminal artifact `bl_align_log.txt` records a prior cp1252 Unicode print failure (`UnicodeEncodeError` on arrow character) from an older script revision; this is non-blocking for the current patched workflow.

## Done
- `BL-005` completed on 2026-03-22 on real filtered candidate set. Semantic filtering against DS-002 (9,330 candidates) using BL-004 preference profile. Artifacts: `07_implementation/implementation_notes/retrieval/outputs/bl005_filtered_candidates.csv` (run_id=`BL005-FILTER-20260322-021107-181373`, 1,740 kept candidates from 9,330 total = 18.62% retention rate), `bl005_candidate_decisions.csv` (full audit trail), `bl005_candidate_diagnostics.json` (metadata and rule hit counts). Semantic rule distribution: lead_genre_match=425, genre_overlap=1,669, tag_overlap=1,740. Numeric features disabled (consistent with BL-004 semantic-only profile). Runtime: 0.236 seconds. Deterministic execution confirmed. Evidence in `07_implementation/experiment_log.md` (EXP-026) and `07_implementation/test_notes.md` (TC-BL020-005).
- `BL-004` re-executed on 2026-03-22 on real enriched Spotify data (5,592 seed events from BL-003). Profile artifacts regenerated at `07_implementation/implementation_notes/profile/outputs/` (`bl004_preference_profile.json` run_id=`BL004-PROFILE-20260322-020511-252947`, `bl004_profile_summary.json`, `bl004_seed_trace.csv`). Dominant lead genres: classical (1019.05), classic rock (778.89), progressive rock (755.93), pop (522.76), rock (321.15). Feature centers: empty dict (semantic-only mode without Spotify audio features). Completion: <1 second after BL-003 finished.
- `BL-003` completed end-to-end on 2026-03-22 on real Spotify Web API export (5,592 unique tracks from combined top + saved history). Last.fm tag enrichment with fallback lookup chain. Artifacts: `07_implementation/implementation_notes/ingestion/outputs/bl020_alignment_report.json` (run_id=`BL003-ALIGN-20260322-020126-080489`, completed 2026-03-22T02:01:26Z), `bl020_aligned_events.jsonl` (5.9 MB, all 5,592 events with populated `lastfm_status`, `lastfm_tags`, `lastfm_error`), `bl020_lastfm_tag_cache.json` (5.4 MB, fresh build). Success: 5,361 tagged (95.87%), 204 no_tags (3.65%), 27 errors (0.48%). Runtime: 6,089 seconds (~101 minutes). No interruption. Cache: 871 hits (residual warmup) + 4,721 misses (fresh API calls). Evidence in `07_implementation/experiment_log.md` (EXP-022) and `07_implementation/test_notes.md` (TC-BL020-001).
- `BL-002` completed on 2026-03-21. Deterministic parser implemented and validated on Spotify-style sample export (`rows_total=7`, `rows_valid=4`, `rows_invalid=3`) with artifacts in `07_implementation/implementation_notes/run_outputs/`; Spotify Web API max-export ingestion script added at `07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py` with runbook `07_implementation/implementation_notes/ingestion/spotify_api_ingestion_runbook.md`. Successful authenticated export evidence exists (`spotify_export_run_summary.json`, run_id=`SPOTIFY-EXPORT-20260321-192533-881299`) with 5,592 unique tracks across top + saved history.
- `BL-001` completed on 2026-03-21. Ingestion schema path locked to Spotify Extended Streaming History CSV with explicit raw-to-normalized field mapping and sample input/output mapping artifacts in `06_data_and_sources/schema_notes.md` and `07_implementation/implementation_notes/ingestion/bl001_spotify_input_output_mapping.md`.
- `BL-019` completed on 2026-03-21. DS-002 intersection dataset built (9330 tracks, all quality gates pass, determinism confirmed across two runs). Artifacts at `07_implementation/implementation_notes/data_layer/outputs/`. Evidence in `EXP-016` and `TC-DATASET-001`.
- `BL-013` completed on 2026-03-21. Lightweight pipeline entrypoint implemented at `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py` with run command documentation in `07_implementation/implementation_notes/entrypoint/bl013_run_command.md`; execution evidence and repeatability checks recorded in `07_implementation/experiment_log.md` (`EXP-015`) and `07_implementation/test_notes.md` (`TC-CLI-001`).
- `BL-014` completed on 2026-03-22. Automated sanity-check runner implemented at `07_implementation/implementation_notes/quality/run_bl014_sanity_checks.py` and executed successfully (`run_id=BL014-SANITY-20260322-024523-652281`). Results: 21/21 checks passed for schema presence, cross-stage hash linkage, and BL-005 to BL-009 continuity. Artifacts: `bl014_sanity_report.json`, `bl014_sanity_run_matrix.csv`, `bl014_sanity_config_snapshot.json`. Evidence in `07_implementation/experiment_log.md` (`EXP-031`) and `07_implementation/test_notes.md` (`TC-BL014-001`).
- `BL-012` completed on 2026-03-21. Limitation and failure-mode synthesis documented in `02_foundation/limitations.md` and integrated into `08_writing/chapter5.md` (Sections 5.4 and 5.5), with implementation evidence logged in `07_implementation/experiment_log.md` (`EXP-014`) and `07_implementation/test_notes.md` (`TC-LIMIT-001`).
- `BL-011` completed on 2026-03-21. Controllability artifacts generated at `07_implementation/implementation_notes/controllability/outputs/` (`bl011_controllability_config_snapshot.json`, `bl011_controllability_report.json`, `bl011_controllability_run_matrix.csv`, archived scenario directories `baseline/`, `no_influence_tracks/`, `valence_weight_up/`, `stricter_thresholds/`, `looser_thresholds/`).
- `BL-010` completed on 2026-03-21. Reproducibility artifacts generated at `07_implementation/implementation_notes/reproducibility/outputs/` (`bl010_reproducibility_config_snapshot.json`, `bl010_reproducibility_report.json`, `bl010_reproducibility_run_matrix.csv`, archived replay directories `replay_01/` to `replay_03/`).
- `BL-009` completed on 2026-03-21. Observability artifacts generated at `07_implementation/implementation_notes/observability/outputs/` (`bl009_run_observability_log.json`, `bl009_run_index.csv`).
- `BL-008` completed on 2026-03-19. Transparency artifacts generated at `07_implementation/implementation_notes/transparency/outputs/` (`bl008_explanation_payloads.json`, `bl008_explanation_summary.json`).
- `BL-007` completed on 2026-03-19. Playlist assembly artifacts generated at `07_implementation/implementation_notes/playlist/outputs/` (`bl007_playlist.json`, `bl007_assembly_trace.csv`, `bl007_assembly_report.json`).
- `BL-006` completed on 2026-03-19. Deterministic scoring artifacts generated at `07_implementation/implementation_notes/scoring/outputs/` (`bl006_scored_candidates.csv`, `bl006_score_summary.json`).
- `BL-005` completed on 2026-03-19. Candidate filtering artifacts generated at `07_implementation/implementation_notes/retrieval/outputs/` (`bl005_filtered_candidates.csv`, `bl005_candidate_decisions.csv`, `bl005_candidate_diagnostics.json`).
- `BL-004` completed on 2026-03-19. Deterministic profile artifacts generated at `07_implementation/implementation_notes/profile/outputs/` (`bl004_preference_profile.json`, `bl004_profile_summary.json`, `bl004_seed_trace.csv`).
- `BL-016` completed on 2026-03-19. Synthetic pre-aligned assets generated at `07_implementation/implementation_notes/test_assets/` (`bl016_synthetic_aligned_events.jsonl`, `bl016_candidate_stub.csv`, `bl016_asset_manifest.json`).
- `BL-017` completed on 2026-03-19. Uncapped Onion canonical-layer outputs generated at `07_implementation/implementation_notes/data_layer/outputs/` (`onion_canonical_track_table.csv`, `onion_join_coverage_report.json`, `onion_selected_column_manifest.json`).
- `BL-018` completed on 2026-03-19. Historical recommendation at that time was to keep Music4All-Onion as active and treat the MSD-based option as fallback; this was later superseded for active BL-019 planning by decision `D-015` on 2026-03-21.
- Phase A work was previously completed and logged in `experiment_log.md` `EXP-001` and `EXP-002`, then deleted on 2026-03-19 for clean restart.

 