# Backlog

Last updated: 2026-03-25

## Priority Legend
- P0: Must complete for locked MVP and assessment evidence.
- P1: Strongly recommended quality improvement.
- P2: Optional stretch item if time permits.

## Current Execution Posture (2026-03-25)
- All P0 items and all previously active P1 items (BL-021 and the artefact refinement cycle) are complete.
- BL-013 and BL-009 have been significantly enhanced: canonical run-intent/run-effective-config artifact pair on every run; BL-009 schema versioned at `bl009-observability-v1` with `execution_scope_summary` block. Validated in `BL013-ENTRYPOINT-20260325-001946-187550`.
- Semantic control-layer map published at `07_implementation/implementation_notes/run_config/semantic_control_map.md`.
- Active work: BL-023 (website-to-pipeline integration) and thesis writing/citation hardening (UI-003).
- BL-024 and BL-022 remain deferred; BL-015 is out of scope.

## Items

| ID | Priority | Status | Task | Evidence Output |
| --- | --- | --- | --- | --- |
| BL-001 | P0 | done | Define ingestion schema for one platform export path | `06_data_and_sources/schema_notes.md` Spotify mapping section + `07_implementation/implementation_notes/ingestion/bl001_spotify_input_output_mapping.md` |
| BL-002 | P0 | done | Implement ingestion parser and validation checks | `07_implementation/implementation_notes/ingestion/ingest_history_parser.py` + `07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py` |
| BL-003 | P0 | done | Implement ISRC-first track alignment with fallback matching against DS-001 | BL-003 alignment outputs; `bl003_source_scope_manifest.json`; evidence in EXP-034, EXP-042, TC-BL003-005-DS001-ONLY-001 |
| BL-004 | P0 | done | Build deterministic user preference profile generator | `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`, `bl004_profile_summary.json`, `bl004_seed_trace.csv` |
| BL-005 | P0 | done | Implement candidate retrieval and feature filtering | `07_implementation/implementation_notes/retrieval/outputs/bl005_filtered_candidates.csv`, `bl005_candidate_decisions.csv`, `bl005_candidate_diagnostics.json`; 1,740 kept candidates from 9,330; EXP-032 |
| BL-006 | P0 | done | Implement deterministic scoring function with weighted components | `07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv`, `bl006_score_summary.json`; retuned 2026-03-24 (EXP-033, EXP-035, TC-BL006-FINAL-001) |
| BL-007 | P0 | done | Implement rule-based playlist assembly (diversity, coherence, ordering) | `07_implementation/implementation_notes/playlist/outputs/bl007_playlist.json` (10 tracks), `bl007_assembly_trace.csv`, `bl007_assembly_report.json`; score range 0.596–0.771 |
| BL-008 | P0 | done | Add transparency outputs (score contribution and rule adjustment trace) | `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_payloads.json`, `bl008_explanation_summary.json` |
| BL-009 | P0 | done | Add observability logging; schema-versioned at `bl009-observability-v1` with `execution_scope_summary` and canonical config artifact pair links | `07_implementation/implementation_notes/observability/outputs/bl009_run_observability_log.json`, `bl009_run_index.csv`; validated in BL013-ENTRYPOINT-20260325-001946-187550 |
| BL-010 | P0 | done | Execute reproducibility tests (same input/config => same output) | `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_report.json`; `deterministic_match=true` across three replays; run BL010-REPRO-20260324-234322 |
| BL-011 | P0 | done | Execute controllability tests (parameter sensitivity) | `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_report.json`, `bl011_controllability_run_matrix.csv`; five scenarios; run BL011-CTRL-20260324-235114 |
| BL-012 | P0 | done | Document limitations and failure modes from test outcomes | `02_foundation/limitations.md` + `08_writing/chapter5.md` Sections 5.4 and 5.5 |
| BL-013 | P1 | done | Lightweight orchestrator with repeatable run controls; emits canonical run-intent/run-effective-config artifact pair per run | `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py`; `run_config/outputs/run_intent_*.json` and `run_effective_config_*.json`; validated in BL013-ENTRYPOINT-20260325-001946-187550 |
| BL-014 | P1 | done | Automated sanity checks for input schema and deterministic output hashes | `07_implementation/implementation_notes/sanity/run_bl014_sanity_checks.py`; 21/21 checks pass; EXP-031, TC-BL014-001 |
| BL-015 | P2 | todo | Add second ingestion adapter scaffold (out of core scope) | Backlog-only design note |
| BL-016 | P0 | done | Create synthetic pre-aligned data assets for core pipeline development | `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`, `bl016_candidate_stub.csv`, `bl016_asset_manifest.json` |
| BL-017 | P0 | done | Build Music4All-Onion canonical dataset layer with join and quality checks | `07_implementation/implementation_notes/data_layer/outputs/` — canonical track table, join-coverage report, selected-column manifest |
| BL-018 | P0 | done | Candidate-corpus feasibility review | `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md`; superseded by D-015 (DS-002 activated) |
| BL-019 | P0 | done | Build DS-002 integrated candidate dataset (MSD subset + Last.fm tags) with deterministic joins and quality gates | `07_implementation/implementation_notes/data_layer/outputs/`; 9,330 tracks; all quality gates pass; EXP-016, TC-DATASET-001 |
| BL-020 | P0 | done | Full pipeline redo against updated ingestion schema and DS-001 corpus; BL-004 through BL-013 stages regenerated | All stage outputs under `07_implementation/implementation_notes/`; EXP-022 to EXP-030; TC-BL020-001 to TC-BL020-009 |
| BL-021 | P1 | done | Add user-selectable source-scope control and persist effective scope in run metadata | Run-config `input_scope` contract wired; `bl003_source_scope_manifest.json`; A/B controllability evidence EXP-040 to EXP-042, TC-BL021-R2-001 to TC-BL021-R2-003 |
| BL-022 | P1 | todo | Add deterministic corpus fallback policy (Music4All-first, DS-002 fallback on low coverage) | Fallback policy spec + per-run path-selection metadata + A/B report |
| BL-023 | P1 | doing | Integrate website flow with deterministic pipeline outputs and run orchestration | UI run trace (run id + stage status), artifact linkage, implementation notes in `07_implementation/website.md` |
| BL-024 | P1 | todo | Bounded implementation hardening (error handling, observability clarity, rerun controls) without changing core recommendation logic | Hardening diff summary + updated diagnostics examples + stability test notes |

## Active

### BL-023 — Website-to-Pipeline Integration
Status: in progress since 2026-03-23.
Scope: wire `07_implementation/website/` import controls, run trigger/orchestration, stage status and diagnostics render, and output/explanation display to real pipeline artifacts.
Server: `07_implementation/setup/website_api_server.py`; stage parameters passed via env vars (BL004–BL009 env var contract documented in repo memory).
Plan: `07_implementation/website.md`.
Next: complete stage-status display and output render; smoke-test full UI flow against live BL-013 orchestrated run.

## Deferred

- **BL-024** (P1): bounded implementation hardening — activate after BL-023 reaches stable state.
- **BL-022** (P1): deterministic corpus fallback — deferred per D-025; activate after BL-020 stabilization window closes.
- **BL-015** (P2): second ingestion adapter scaffold — out of core scope; not planned for current submission.

## Done

All P0 items and active P1 items (BL-021, BL-013 artefact refinement, BL-009 schema promotion) are complete. Final evidence for each item is recorded in the Items table above. Full experiment and test-case evidence in `07_implementation/experiment_log.md` and `07_implementation/test_notes.md`.

Key final-state references:
- Latest full-chain orchestrated run: `BL013-ENTRYPOINT-20260325-001946-187550` (6/6 stages pass)
- Reproducibility: `BL010-REPRO-20260324-234322` (deterministic_match=true)
- Controllability: `BL011-CTRL-20260324-235114` (all checks true, five scenarios)
- Semantic control-layer map: `07_implementation/implementation_notes/run_config/semantic_control_map.md`
- Governance: change IDs C-065 through C-148 in `00_admin/change_log.md`
- Collaboration repo: `https://github.com/TimothySpiteri/thesis` (private).
- Primary working branch: `setup/initial-work`.
- Current local head at handoff prep: `93f6369624a55f33d544737aaea9c9f5b3152eb5`.
- Locked operating constraints: keep title/RQ/scope/methodology aligned with `00_admin/thesis_state.md` and use change proposals for protected changes.
- Current implementation status: BL-020 full pipeline rerun and BL-014 sanity automation are complete with evidence logged. Active implementation priority is freeze-and-integrate website execution with bounded hardening.
- Strategy update (2026-03-19, D-005): start with synthetic pre-aligned data. BL-001, BL-002, BL-003 deferred until after the core pipeline is proven end-to-end. See decision_log.md D-005.
- Strategy update (2026-03-21, D-015): activate the DS-002 corpus strategy (`MSD subset + Last.fm tags`) as the current BL-019 implementation path; MusicBrainz fields are optional metadata and currently unused.
- Ingestion update (2026-03-21): BL-001 schema is now locked to Spotify Extended Streaming History CSV as the selected single-adapter MVP path.
- Ingestion update (2026-03-21): BL-002 parser is implemented and a Spotify Web API max-export ingestion script now collects top tracks, saved tracks, playlists, and playlist items with OAuth + pagination.
- Environment update (2026-03-21): repo-local Python setup is now standardized via `requirements.txt` and one-command bootstrap under `07_implementation/setup/`.
- Implementation redo (2026-03-21, C-065): ingestion pipeline and database have changed; full pipeline redo required. BL-020 is now the top P0 item.
- Pre-BL-020 audit (2026-03-21): comprehensive readiness audit completed and logged in `BL020_HANDOFF_AUDIT_2026-03-21.md`. All pipeline scaffolds ready; real ingestion data is the sole blocker.
- Execution update (2026-03-23): freeze current BL-020 baseline and prioritize website interaction integration + bounded implementation refinement; avoid scope expansion into deferred items.
- Recommended immediate next work order:
	1. `BL-023` website-to-pipeline integration as the current practical execution item.
	   - Scope: wire `07_implementation/website/` flow to real artifacts and deterministic stage orchestration.
	   - Sequence: import controls → run trigger/orchestration → stage status + diagnostics render → output and explanation display.
	2. `BL-024` bounded implementation refinement under freeze.
	   - Scope: reliability fixes, observability clarity, API error handling, and reproducibility-oriented rerun controls.
	3. Maintain writing evidence hardening for `UI-002` and `UI-003` in parallel.
	4. Keep deferred items (`BL-021`, `BL-022`) unchanged until freeze package closes.
- Evidence-first reminder: for each completed backlog item, write the expected evidence artifact and link it in the matching file listed in the backlog table.

## Items
| ID | Priority | Status | Task | Evidence Output |
| --- | --- | --- | --- | --- |
| BL-001 | P0 | done | Define ingestion schema for one platform export path | `06_data_and_sources/schema_notes.md` Spotify mapping section + `07_implementation/implementation_notes/ingestion/bl001_spotify_input_output_mapping.md` |
| BL-002 | P0 | done | Implement ingestion parser and validation checks | `07_implementation/implementation_notes/ingestion/ingest_history_parser.py` + `07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py` + run outputs/logs |
| BL-003 | P0 | done | Implement ISRC-first track alignment with fallback matching | Match report with matched/unmatched counts |
| BL-004 | P0 | done | Build deterministic user preference profile generator | Profile artifact for at least one test user |
| BL-005 | P0 | done | Implement candidate retrieval and feature filtering | Candidate set diagnostics per run |
| BL-006 | P0 | done | Implement deterministic scoring function with weighted components | Score breakdown table per track |
| BL-007 | P0 | done | Implement rule-based playlist assembly (diversity, coherence, ordering) | Rule compliance report per run |
| BL-008 | P0 | done | Add transparency outputs (score contribution + rule adjustment trace) | Human-readable explanation artifact |
| BL-009 | P0 | done | Add observability logging (config, seed/control params, run metadata) | Reproducible run log schema and examples |
| BL-010 | P0 | done | Execute reproducibility tests (same input/config => same output) | Test log in `07_implementation/test_notes.md` |
| BL-011 | P0 | done | Execute controllability tests (parameter sensitivity) | Comparative run matrix |
| BL-012 | P0 | done | Document limitations and failure modes from test outcomes | `02_foundation/limitations.md` + `08_writing/chapter5.md` notes |
| BL-013 | P1 | done | Add lightweight CLI or script entrypoint for repeatable runs | Run command documentation |
| BL-014 | P1 | done | Create automated sanity checks for input schema and deterministic output hashes | Scripted check results |
| BL-015 | P2 | todo | Add second ingestion adapter scaffold (out of core scope) | Backlog-only design note |
| BL-016 | P0 | done | Create synthetic pre-aligned data assets for core pipeline development | `07_implementation/implementation_notes/test_assets/` — synthetic aligned JSONL + Music4All candidate stub CSV |
| BL-017 | P0 | done | Build Onion-only canonical dataset layer (track_id join + curated feature schema + data quality checks) | `07_implementation/implementation_notes/data_layer/` outputs: canonical track table, join-coverage report, selected-column manifest |
| BL-018 | P0 | done | Run candidate-corpus feasibility review before further canonical-layer work | `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md` |
| BL-019 | P0 | done | Build DS-002 integrated candidate dataset (`MSD subset + Last.fm tags`; optional MusicBrainz metadata) with deterministic joins and quality gates | `07_implementation/experiment_log.md` (`EXP-016`) + `07_implementation/test_notes.md` (`TC-DATASET-001`) + dataset outputs under `07_implementation/implementation_notes/data_layer/outputs/` |
| BL-020 | P0 | done | Redo full pipeline implementation against updated ingestion schema and database (C-065) — re-run BL-004 through BL-013 stages and regenerate all artifacts | Updated run outputs, profile, candidate, scoring, playlist, transparency, observability, reproducibility and controllability artifacts under `07_implementation/implementation_notes/` + `07_implementation/experiment_log.md` (`EXP-022`) + `07_implementation/test_notes.md` (`TC-BL020-001`) |
| BL-021 | P1 | done | Add user-selectable Spotify profile-source scope control (top tracks/saved tracks/playlist tracks + per-source limits) and persist selected scope in run metadata | Config/UI spec + source-selection manifest in run outputs + controllability test showing runtime/profile-effect deltas |
| BL-022 | P1 | todo | Add deterministic corpus fallback policy: try Music4All(-Onion) alignment first, then auto-fallback to current DS-002 semantic path when coverage thresholds are not met | Fallback policy spec + per-run path-selection metadata + A/B alignment coverage report |
| BL-023 | P1 | doing | Integrate website flow with current deterministic pipeline outputs and run orchestration under freeze scope | UI run trace (run id + stage status), artifact linkage screen captures, and implementation notes in `07_implementation/website.md` |
| BL-024 | P1 | todo | Refine current implementation for interaction reliability (error handling, observability clarity, bounded rerun control) without changing core recommendation logic | Hardening diff summary + updated diagnostics examples + stability test notes |

## In Progress
- `BL-023` started on 2026-03-23 as the freeze-package integration item. Direction: keep BL-020 behavior stable, wire website interaction flow to real run artifacts/stage execution, and prioritize inspectable run diagnostics in the UI.
- `BL-021` was previously deferred by D-023 during freeze packaging, then activated and completed on 2026-03-24 through runyes-config contract wiring, BL-003 scope actuation, and A/B controllability evidence (`EXP-040`, `EXP-041`, `EXP-042`; `TC-BL021-R2-001`, `TC-BL021-R2-002`, `TC-BL021-R2-003`).
- `BL-022` has been accepted as a deferred P1 idea (D-025): define deterministic dataset-path fallback switching (Music4All-first when available, DS-002 fallback on low coverage) after BL-020 stabilization.

### Handoff Note (2026-03-22)
- Treat `07_implementation/implementation_notes/ingestion/outputs/bl020_alignment_report.json` as historical fuzzy-alignment evidence (stale for current BL-003 strategy).
- Current active `bl020_aligned_events.jsonl` was intentionally swapped to partial cache-derived content for test execution and can be restored from `bl020_aligned_events.pre_partial_backup_20260322-001050.jsonl`.
- Historical terminal artifact `bl_align_log.txt` records a prior cp1252 Unicode print failure (`UnicodeEncodeError` on arrow character) from an older script revision; this is non-blocking for the current patched workflow.

## Done
- `BL-021` completed on 2026-03-24. Canonical run-config source-scope contract is now wired end-to-end and behaviorally actuated: BL-004 and BL-009 persist effective `input_scope`, BL-003 applies source-scope filtering and emits `bl003_source_scope_manifest.json`, and A/B evidence confirms non-zero profile deltas. Evidence in `07_implementation/experiment_log.md` (`EXP-040` to `EXP-042`) and `07_implementation/test_notes.md` (`TC-BL021-R2-001` to `TC-BL021-R2-003`).
- `BL-003` completed on 2026-03-24 for the active DS-001 path. ISRC-first plus metadata fallback alignment is operational with strict selected-source checks, canonical DS-001 seed outputs, and source-scope-aware filtering integrated into `build_bl003_ds001_spotify_seed_table.py`; evidence in `EXP-034`, `EXP-042`, and `TC-BL003-005-DS001-ONLY-001`.
- `BL-020` completed on 2026-03-22. Full rerun pipeline executed end-to-end on real Spotify export + Last.fm semantic enrichment path with BL-003 through BL-009 artifacts generated and validated. Evidence in `07_implementation/experiment_log.md` (`EXP-022` through `EXP-030`) and `07_implementation/test_notes.md` (`TC-BL020-001` through `TC-BL020-009`).
- `BL-014` completed on 2026-03-22. Automated sanity checks implemented and executed (`21/21` checks passed) with evidence in `07_implementation/experiment_log.md` (`EXP-031`) and `07_implementation/test_notes.md` (`TC-BL014-001`).
- `BL-002` completed on 2026-03-21. Deterministic parser implemented and validated on Spotify-style sample export (`rows_total=7`, `rows_valid=4`, `rows_invalid=3`) with artifacts in `07_implementation/implementation_notes/run_outputs/`; Spotify Web API max-export ingestion script added at `07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py` with runbook `07_implementation/implementation_notes/ingestion/spotify_api_ingestion_runbook.md`.
- `BL-001` completed on 2026-03-21. Ingestion schema path locked to Spotify Extended Streaming History CSV with explicit raw-to-normalized field mapping and sample input/output mapping artifacts in `06_data_and_sources/schema_notes.md` and `07_implementation/implementation_notes/ingestion/bl001_spotify_input_output_mapping.md`.
- `BL-019` completed on 2026-03-21. DS-002 intersection dataset built (9330 tracks, all quality gates pass, determinism confirmed across two runs). Artifacts at `07_implementation/implementation_notes/data_layer/outputs/`. Evidence in `EXP-016` and `TC-DATASET-001`.
- `BL-013` completed on 2026-03-21. Lightweight pipeline entrypoint implemented at `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py` with run command documentation in `07_implementation/implementation_notes/entrypoint/bl013_run_command.md`; execution evidence and repeatability checks recorded in `07_implementation/experiment_log.md` (`EXP-015`) and `07_implementation/test_notes.md` (`TC-CLI-001`).
- `BL-013` refreshed on 2026-03-24 as the current baseline orchestrator run. Latest full-chain confirmation `BL013-ENTRYPOINT-20260324-235248-642823` passed (`overall_status=pass`) with all stages BL-004 through BL-009 successful; evidence in `07_implementation/implementation_notes/entrypoint/outputs/bl013_orchestration_run_latest.json` and `07_implementation/implementation_notes/entrypoint/bl013_state_log_2026-03-24.md`.
- `BL-012` completed on 2026-03-21. Limitation and failure-mode synthesis documented in `02_foundation/limitations.md` and integrated into `08_writing/chapter5.md` (Sections 5.4 and 5.5), with implementation evidence logged in `07_implementation/experiment_log.md` (`EXP-014`) and `07_implementation/test_notes.md` (`TC-LIMIT-001`).
- `BL-011` completed on 2026-03-21. Controllability artifacts generated at `07_implementation/implementation_notes/controllability/outputs/` (`bl011_controllability_config_snapshot.json`, `bl011_controllability_report.json`, `bl011_controllability_run_matrix.csv`, archived scenario directories `baseline/`, `no_influence_tracks/`, `valence_weight_up/`, `stricter_thresholds/`, `looser_thresholds/`).
- `BL-011` refreshed and aligned on 2026-03-24 for active pipeline mode. Latest run `BL011-CTRL-20260324-235114` passed with all checks true (`all_scenarios_repeat_consistent=true`, `all_variant_shifts_observable=true`, `all_variant_directions_met=true`); evidence in `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_report.json`, `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_run_matrix.csv`, `07_implementation/implementation_notes/controllability/bl011_state_log_2026-03-24.md`, and `07_implementation/experiment_log.md` (`EXP-043`).
- `BL-010` completed on 2026-03-21. Reproducibility artifacts generated at `07_implementation/implementation_notes/reproducibility/outputs/` (`bl010_reproducibility_config_snapshot.json`, `bl010_reproducibility_report.json`, `bl010_reproducibility_run_matrix.csv`, archived replay directories `replay_01/` to `replay_03/`).
- `BL-010` refreshed and aligned on 2026-03-24 for active pipeline mode. Latest run `BL010-REPRO-20260324-234322` passed deterministic replay checks (`deterministic_match=true`, `fixed_input_source=active_pipeline_outputs`) with evidence in `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_report.json` and stage record at `07_implementation/implementation_notes/reproducibility/bl010_state_log_2026-03-24.md`.
- `BL-009` completed on 2026-03-21. Observability artifacts generated at `07_implementation/implementation_notes/observability/outputs/` (`bl009_run_observability_log.json`, `bl009_run_index.csv`).
- `BL-009` refreshed on 2026-03-24 to align with current BL-006 -> BL-008 run chain. Current run `BL009-OBSERVE-20260324-195859-875091` captures refreshed upstream run IDs and hashes; evidence in `07_implementation/experiment_log.md` (`EXP-038`) and `07_implementation/test_notes.md` (`TC-BL009-REFRESH-001`), with state record at `07_implementation/implementation_notes/observability/bl009_state_log_2026-03-24.md`.
- `BL-008` completed on 2026-03-19. Transparency artifacts generated at `07_implementation/implementation_notes/transparency/outputs/` (`bl008_explanation_payloads.json`, `bl008_explanation_summary.json`).
- `BL-008` refreshed on 2026-03-24 against finalized BL-006 and refreshed BL-007 baselines. Transparency script mapping was updated to dynamic active-component extraction; evidence in `07_implementation/experiment_log.md` (`EXP-037`) and `07_implementation/test_notes.md` (`TC-BL008-REFRESH-001`), with state record at `07_implementation/implementation_notes/transparency/bl008_state_log_2026-03-24.md`.
- `BL-007` completed on 2026-03-19. Playlist assembly artifacts generated at `07_implementation/implementation_notes/playlist/outputs/` (`bl007_playlist.json`, `bl007_assembly_trace.csv`, `bl007_assembly_report.json`).
- `BL-007` refreshed on 2026-03-24 against finalized BL-006 baseline. Current run `BL007-ASSEMBLE-20260324-195257-583625` regenerated playlist artifacts and aligned input hash to BL-006 closure output; evidence in `07_implementation/experiment_log.md` (`EXP-036`) and `07_implementation/test_notes.md` (`TC-BL007-REFRESH-001`) with state record at `07_implementation/implementation_notes/playlist/bl007_state_log_2026-03-24.md`.
- `BL-006` completed on 2026-03-19. Deterministic scoring artifacts generated at `07_implementation/implementation_notes/scoring/outputs/` (`bl006_scored_candidates.csv`, `bl006_score_summary.json`).
- `BL-006` retuned on 2026-03-24. Component weights were rebalanced to increase numeric influence and reduce semantic overlap pressure; latest evidence in `07_implementation/experiment_log.md` (`EXP-033`) and `07_implementation/test_notes.md` (`TC-BL006-RETUNE-001`).
- `BL-006` finalized on 2026-03-24 for BL-007 handoff. Closure gate checks passed (`top10_overlap_vs_pre_retune=9/10`, top-100 numeric-led contribution), with evidence in `07_implementation/experiment_log.md` (`EXP-035`) and `07_implementation/test_notes.md` (`TC-BL006-FINAL-001`), plus stage evidence in `07_implementation/implementation_notes/scoring/bl006_state_log_2026-03-24.md` and `07_implementation/implementation_notes/scoring/bl006_top50_quality_snapshot_2026-03-24.md`.
- `BL-005` completed on 2026-03-19. Candidate filtering artifacts generated at `07_implementation/implementation_notes/retrieval/outputs/` (`bl005_filtered_candidates.csv`, `bl005_candidate_decisions.csv`, `bl005_candidate_diagnostics.json`).
- `BL-005` hardened on 2026-03-24. Retrieval keep rule tightened to reject weak numeric-only matches; latest run kept `1,938 / 9,330` candidates (`20.77%`) instead of `6,604 / 9,330`, with evidence in `07_implementation/experiment_log.md` (`EXP-032`) and `07_implementation/test_notes.md` (`TC-BL005-HARDEN-001`).
- DS-001 contract migration on 2026-03-24. BL-003 now validates selected-source completeness against BL-002 export summary, and BL-005/BL-006 semantic matching now uses DS-001 `tags`/`genres` columns (`EXP-034`, `TC-BL003-005-DS001-ONLY-001`).
- `BL-004` completed on 2026-03-19. Deterministic profile artifacts generated at `07_implementation/implementation_notes/profile/outputs/` (`bl004_preference_profile.json`, `bl004_profile_summary.json`, `bl004_seed_trace.csv`).
- `BL-016` completed on 2026-03-19. Synthetic pre-aligned assets generated at `07_implementation/implementation_notes/test_assets/` (`bl016_synthetic_aligned_events.jsonl`, `bl016_candidate_stub.csv`, `bl016_asset_manifest.json`).
- `BL-017` completed on 2026-03-19. Uncapped Onion canonical-layer outputs generated at `07_implementation/implementation_notes/data_layer/outputs/` (`onion_canonical_track_table.csv`, `onion_join_coverage_report.json`, `onion_selected_column_manifest.json`).
- `BL-018` completed on 2026-03-19. Historical recommendation at that time was to keep Music4All-Onion as active and treat the MSD-based option as fallback; this was later superseded for active BL-019 planning by decision `D-015` on 2026-03-21.
- Phase A work was previously completed and logged in `experiment_log.md` `EXP-001` and `EXP-002`, then deleted on 2026-03-19 for clean restart.

 