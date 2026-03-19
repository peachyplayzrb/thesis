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
- Strategy update (2026-03-19, D-008 review complete): corpus feasibility review is complete. Keep Music4All-Onion as the active MVP corpus and treat the MSD-based option as fallback only.
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
| BL-004 | P0 | todo | Build deterministic user preference profile generator | Profile artifact for at least one test user |
| BL-005 | P0 | todo | Implement candidate retrieval and feature filtering | Candidate set diagnostics per run |
| BL-006 | P0 | todo | Implement deterministic scoring function with weighted components | Score breakdown table per track |
| BL-007 | P0 | todo | Implement rule-based playlist assembly (diversity, coherence, ordering) | Rule compliance report per run |
| BL-008 | P0 | todo | Add transparency outputs (score contribution + rule adjustment trace) | Human-readable explanation artifact |
| BL-009 | P0 | todo | Add observability logging (config, seed/control params, run metadata) | Reproducible run log schema and examples |
| BL-010 | P0 | todo | Execute reproducibility tests (same input/config => same output) | Test log in `07_implementation/test_notes.md` |
| BL-011 | P0 | todo | Execute controllability tests (parameter sensitivity) | Comparative run matrix |
| BL-012 | P0 | todo | Document limitations and failure modes from test outcomes | `02_foundation/limitations.md` + `08_writing/chapter5.md` notes |
| BL-013 | P1 | todo | Add lightweight CLI or script entrypoint for repeatable runs | Run command documentation |
| BL-014 | P1 | todo | Create automated sanity checks for input schema and deterministic output hashes | Scripted check results |
| BL-015 | P2 | todo | Add second ingestion adapter scaffold (out of core scope) | Backlog-only design note |
| BL-016 | P0 | todo | Create synthetic pre-aligned data assets for core pipeline development | `07_implementation/implementation_notes/test_assets/` — synthetic aligned JSONL + Music4All candidate stub CSV |
| BL-017 | P0 | todo | Build Onion-only canonical dataset layer (track_id join + curated feature schema + data quality checks) | `07_implementation/implementation_notes/data_layer/` outputs: canonical track table, join-coverage report, selected-column manifest |
| BL-018 | P0 | done | Run candidate-corpus feasibility review before further canonical-layer work | `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md` |
| BL-019 | P2 | deferred | Revisit MSD + Last.fm + MusicBrainz corpus engineering as future work | `06_data_and_sources/ds_002_msd_information_sheet.md` + future prototype note if reopened |

## In Progress
- None.

## Done
- `BL-018` completed on 2026-03-19. Recommendation: keep Music4All-Onion as the active MVP corpus and treat the MSD-based option as fallback only.
- Phase A work was previously completed and logged in `experiment_log.md` `EXP-001` and `EXP-002`, then deleted on 2026-03-19 for clean restart.

