# Unresolved Issues

Last updated: 2026-03-25

## Active

- UI-008 (2026-03-22): Music4All access path is reopened, but final usage terms, provenance details, and local file verification are not fully captured in governance records.
	- impact: DS-001 cannot be promoted from fallback to active corpus until compliance and provenance checks are complete; risk of late rework if restrictions conflict with publication/repo artifacts.
	- current_position:
		- Keep DS-002 as active dataset for BL-020 continuity.
		- Track DS-001 as a re-accessed fallback path pending governance closure.
	- progress_summary:
		1. Provider released dataset download path/credentials on 2026-03-24.
		2. External access blocker is cleared; remaining work is governance and verification.
	- next_action:
		1. Finish local download and record exact received assets (archive names, file sizes, and supplied version labels).
		2. Confirm release/version and checksum identifiers.
		3. Record explicit use/citation/redistribution/retention constraints in `06_data_and_sources/dataset_registry.md`.
		4. Run bounded schema compatibility check before any activation decision.
		5. Escalate unresolved restrictions to supervisor before corpus activation.
	- owner: AI + user
	- status: open

- UI-003 (2026-03-19): Thesis-wide citation verification and literature leverage pass is not yet fully closed in control records.
	- impact: Risk of citation overreach, underused PDF evidence, and missed opportunities to strengthen Chapters 2 to 5 before submission hardening.
	- progress_summary:
		1. Recovery and PDF-audit closure tasks are complete (missing/ambiguous PDF mappings resolved).
		2. Remaining work is synthesis closure: finalize claim-level verification outputs and chapter-targeted hardening recommendations.
	- next_action:
		1. Complete claim-citation matrix expansion for Chapters 3 to 5.
		2. Record verdicts (`supported`, `partially_supported`, `weak_support`, `mismatch`) for unresolved claims.
		3. Produce final chapter-targeted insertion/rewrite/citation-swap notes.
		4. Close package status once synthesis output is logged and cross-referenced.
	- owner: AI + user
	- status: open
	- due_window: 2026-03-19 to 2026-03-29

## Resolved (Recent)

- UI-002 (2026-03-15): Chapter 2 weak-support remediation objective.
	- resolution: Day 2 and Day 3 hardening passes completed; final micro-pass achieved `TOTAL_KEYS_WITH_WEAK=0` for current Chapter 2 audit workflow.
	- key_metrics:
		- baseline: 22 papers with weak claims (24 weak claims)
		- final: 0 papers with weak claims
		- reduction: 100% of baseline weak-claim papers removed in current audited state
	- evidence: `09_quality_control/chapter2_verbatim_audit.md`; `09_quality_control/summarize_ch2_verbatim_audit.py`; `00_admin/timeline.md` (Day 3 closure note).

- UI-007 (2026-03-21): Spotify API ingestion was temporarily blocked by provider-side long cooldown (`HTTP 429`) on `/me`.
	- resolution: Subsequent authenticated export completed successfully (run_id `SPOTIFY-EXPORT-20260321-192533-881299`), generating full BL-002 artifacts and enabling real-data BL-020 execution.
	- evidence: `07_implementation/implementation_notes/ingestion/outputs/spotify_api_export/spotify_export_run_summary.json`; `07_implementation/experiment_log.md` (`EXP-022`); `00_admin/change_log.md` (`C-071`).

## Resolved (Historical)

- UI-006 (2026-03-21): Governance mismatch after DS-002 activation where `thesis_state.md` still stated Music4All/Music4All-Onion as current primary scope.
	- resolution: Synchronized `00_admin/thesis_state.md` to DS-002 active wording and aligned objective/assumption/limitation phrasing.
	- evidence: `00_admin/thesis_state.md` (2026-03-21 update), `00_admin/change_log.md` (`C-042`).

- UI-005 (2026-03-19): Base Music4All was unusable in the local environment; Onion-only workaround was the active interim path.
	- resolution: Superseded by planning decision `D-015`, which activated DS-002 as the BL-019 strategy.
	- evidence: `00_admin/decision_log.md` (`D-015`); `06_data_and_sources/dataset_registry.md` DS-002 status update.

- UI-004 (2026-03-19): Candidate corpus change review between Music4All-Onion and `MSD subset + Last.fm Tag Dataset + MusicBrainz mapping`.
	- resolution: BL-018 feasibility review completed. Result: do not switch corpus; retain MSD-based option as fallback only.
	- evidence: `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md`; `00_admin/decision_log.md` (`D-008`).

- UI-001 (2026-03-15): Parser mismatch between author-year Chapter 2 style and key-based claim extractor.
	- resolution: Extended `09_quality_control/run_ch2_verbatim_audit.py` to map author-year citations to source-index keys and regenerate non-zero claim extraction.
	- evidence: `09_quality_control/run_ch2_verbatim_audit.py`; `09_quality_control/chapter2_verbatim_audit.md`; `00_admin/change_log.md` (`C-009`).
