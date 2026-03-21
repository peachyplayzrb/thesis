# Backlog

## Priority Legend
- P0: Must complete for locked MVP and assessment evidence.
- P1: Strongly recommended quality improvement.
- P2: Optional stretch item if time permits.

## Handoff Snapshot (2026-03-15)
- Collaboration repo: `https://github.com/TimothySpiteri/thesis` (private).
- Primary branch: `main`.
- Latest synced commit at handoff prep: `4d422b0516cb2d6d866ee4cd8470a0715397f992`.
- Locked operating constraints: keep title/RQ/scope/methodology aligned with `00_admin/thesis_state.md` and use change proposals for protected changes.
- Current implementation status: clean restart as of 2026-03-19. All items reset to todo.
- Strategy update (2026-03-19, D-005): start with synthetic pre-aligned data. BL-001, BL-002, BL-003 deferred until after the core pipeline is proven end-to-end. See decision_log.md D-005.
- Strategy update (2026-03-21, D-015): activate the DS-002 corpus strategy (`MSD subset + Last.fm tags + MusicBrainz mapping`) as the current BL-019 implementation path.
- Recommended immediate next work order:
	1. `BL-017` build the Onion-only canonical dataset layer.
	2. `BL-016` create synthetic pre-aligned data assets.
	3. `BL-004` deterministic preference profile generator.
	4. `BL-005` candidate retrieval and feature filtering.
	5. `BL-006` deterministic scoring function.
	6. `BL-007` rule-based playlist assembly.
	7. `BL-008` transparency outputs.
	8. `BL-009` observability logging.
	9. `BL-010` reproducibility tests.
	10. `BL-011` controllability tests.
	11. `BL-012` document limitations.
	12. `BL-001`, `BL-002`, `BL-003` real ingestion + alignment (deferred, resume after core pipeline is stable).
- Evidence-first reminder: for each completed backlog item, write the expected evidence artifact and link it in the matching file listed in the backlog table.

## Items
| ID | Priority | Status | Task | Evidence Output |
| --- | --- | --- | --- | --- |
| BL-001 | P0 | deferred | Define ingestion schema for one platform export path | `06_data_and_sources/schema_notes.md` update + sample input/output mapping |
| BL-002 | P0 | deferred | Implement ingestion parser and validation checks | Parser module + validation log examples |
| BL-003 | P0 | deferred | Implement ISRC-first track alignment with fallback matching | Match report with matched/unmatched counts |
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
| BL-014 | P1 | todo | Create automated sanity checks for input schema and deterministic output hashes | Scripted check results |
| BL-015 | P2 | todo | Add second ingestion adapter scaffold (out of core scope) | Backlog-only design note |
| BL-016 | P0 | done | Create synthetic pre-aligned data assets for core pipeline development | `07_implementation/implementation_notes/test_assets/` — synthetic aligned JSONL + Music4All candidate stub CSV |
| BL-017 | P0 | done | Build Onion-only canonical dataset layer (track_id join + curated feature schema + data quality checks) | `07_implementation/implementation_notes/data_layer/` outputs: canonical track table, join-coverage report, selected-column manifest |
| BL-018 | P0 | done | Run candidate-corpus feasibility review before further canonical-layer work | `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md` |
| BL-019 | P0 | done | Build DS-002 integrated candidate dataset (`MSD subset + Last.fm tags + MusicBrainz mapping`) with deterministic joins and quality gates | `07_implementation/experiment_log.md` (`EXP-016`) + `07_implementation/test_notes.md` (`TC-DATASET-001`) + dataset outputs under `07_implementation/implementation_notes/data_layer/outputs/` |

## In Progress
- (nothing currently in progress)

## Done
- `BL-019` completed on 2026-03-21. DS-002 intersection dataset built (9330 tracks, all quality gates pass, determinism confirmed across two runs). Artifacts at `07_implementation/implementation_notes/data_layer/outputs/`. Evidence in `EXP-016` and `TC-DATASET-001`.
- `BL-013` completed on 2026-03-21. Lightweight pipeline entrypoint implemented at `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py` with run command documentation in `07_implementation/implementation_notes/entrypoint/bl013_run_command.md`; execution evidence and repeatability checks recorded in `07_implementation/experiment_log.md` (`EXP-015`) and `07_implementation/test_notes.md` (`TC-CLI-001`).
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

