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
- Recommended immediate next work order:
	1. `BL-001` ingestion schema definition.
	2. `BL-002` ingestion parser implementation.
	3. `BL-003` ISRC-first track alignment.
- Evidence-first reminder: for each completed backlog item, write the expected evidence artifact and link it in the matching file listed in the backlog table.

## Items
| ID | Priority | Status | Task | Evidence Output |
| --- | --- | --- | --- | --- |
| BL-001 | P0 | todo | Define ingestion schema for one platform export path | `06_data_and_sources/schema_notes.md` update + sample input/output mapping |
| BL-002 | P0 | todo | Implement ingestion parser and validation checks | Parser module + validation log examples |
| BL-003 | P0 | todo | Implement ISRC-first track alignment with fallback matching | Match report with matched/unmatched counts |
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

## In Progress
- None.

## Done
- None. (Phase A work completed and logged in `experiment_log.md` EXP-001/EXP-002; deleted on 2026-03-19 for clean restart.)

