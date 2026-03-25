# Unresolved Issues

Last updated: 2026-03-25 22:55 UTC

## Active

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


- UI-013 (2026-03-25): Pipeline optimization and evidence-hygiene package is not yet closed on the active BL baseline.
	- impact: If left unresolved, final thesis claims remain operationally valid but weaker on precision/coverage quality, explanation richness, and evidence readability.
	- progress_summary:
		1. Comprehensive implementation issue register was consolidated in `07_implementation/IMPLEMENTATION_STATE_2026-03-24.md`.
		2. Runtime and assurance stages are passing, but optimization debt remains visible in BL-003/BL-005/BL-006/BL-008 and governance-hygiene drift remains in BL-010/BL-011 path semantics.
		3. Config-surface control uplift implemented: run-config now exposes explicit `control_mode` governance switches (`validation_profile`, `allow_threshold_decoupling`, `allow_weight_auto_normalization`) and BL-009 observability `bootstrap_mode` is now config-driven instead of hardcoded.
	- next_action:
		1. Define target thresholds for BL-003 match-rate and BL-005 kept-candidate volume under one canonical tuning config.
		2. Run one controlled tuning sweep for BL-005/BL-006 weight and gate settings with BL-009 diagnostic comparison.
		3. Normalize BL-010/BL-011 report path semantics to BL-prefixed canonical rendering.
		4. Log closure evidence and map unresolved items to Chapter 4 limitation language if deferred.
	- owner: AI + user
	- status: open
	- due_window: 2026-03-25 to 2026-03-31

Active-set sync note (2026-03-25 18:25 UTC): Open items are UI-003 (citation package closure) and UI-013 (pipeline optimization and evidence-hygiene closure).
Active-set sync note (2026-03-25 22:55 UTC): Open items remain UI-003 (citation package closure) and UI-013 (pipeline optimization and evidence-hygiene closure); UI-013 control-surface uplift is implemented, optimization tuning closure is pending.

## Resolved (Recent)

- UI-010 (2026-03-25): Control-evaluation artifacts risk drift from current live data baselines.
	- resolution: Closed. BL-010 and BL-011 evidence was regenerated after the lead-genre fix, freshness expectations were recorded in test notes, and a dedicated quality check now fails when BL-010/BL-011 evidence no longer matches the current active baseline contracts.
	- evidence:
		1. `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py` defaults to active pipeline outputs unless legacy mode is explicitly enabled.
		2. `07_implementation/implementation_notes/bl011_controllability/run_bl011_controllability_check.py` defaults to active pipeline outputs unless legacy mode is explicitly enabled.
		3. BL-010 reproducibility refresh passed (`BL010-REPRO-20260325-020749`, `deterministic_match=true`, `fixed_input_source=active_pipeline_outputs`).
		4. BL-011 controllability refresh passed (`BL011-CTRL-20260325-020828`, `all_scenarios_repeat_consistent=true`, `all_variant_shifts_observable=true`, `status=pass`).
		5. `07_implementation/implementation_notes/bl014_quality/check_bl010_bl011_freshness.py` passed on 2026-03-25 (`BL-FRESHNESS-20260325-021237`, `9/9` checks).
		6. `07_implementation/implementation_notes/bl014_quality/run_active_freshness_suite.py` passed on 2026-03-25 (`BL-FRESHNESS-SUITE-20260325-021510`, `6/6` checks), consolidating active freshness checks for BL-013, BL-014, and BL-010/BL-011.

- UI-012 (2026-03-25): Lead-genre semantic contract was inconsistent across BL-004, BL-005, and BL-006.
	- resolution: Closed. BL-004, BL-005, and BL-006 now use one canonical lead-genre rule: prefer the first `genres` label and only fall back to the first `tags` label when no genre is present.
	- evidence:
		1. `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py` now resolves lead genre with the canonical genre-first rule.
		2. `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py` now uses the same genre-first rule for `lead_genre_match`.
		3. `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py` now uses the same genre-first rule for `lead_genre_similarity`.
		4. BL-013 canonical rerun passed (`BL013-ENTRYPOINT-20260325-020526-881730`).
		5. BL-014 sanity suite passed (`BL014-SANITY-20260325-020553-870468`, `21/21` checks).

- UI-011 (2026-03-25): Tier-1 pipeline remediation package closure tracking item.
	- resolution: Closed. All Tier-1 remediation items (CRI-004, CRI-002, HIGH-003, HIGH-004, CRI-003) are implemented with integrated validation evidence complete.
	- evidence:
		1. BL-013 integrated canonical run passed (`BL013-ENTRYPOINT-20260325-014411-311800`).
		2. BL-014 sanity suite passed (`BL014-SANITY-20260325-014516-905552`, `21/21` checks).
		3. Consolidated execution record logged in `00_admin/tier1_hardening_execution_log_2026-03-25.md`.

- UI-009 (2026-03-25): BL-013 stale-seed false-pass risk under run-config execution.
	- resolution: Implemented a BL-003 freshness guard in BL-013. When `--run-config` is supplied without `--refresh-seed`, BL-013 now fails fast on seed-contract mismatch and instructs the operator to refresh BL-003.
	- evidence:
		1. `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py` includes `BL-003-FRESHNESS-GUARD` preflight validation.
		2. `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py` now emits `inputs.seed_contract` + contract hash for comparison.
		3. Validation run on 2026-03-25: fail without refresh, pass with `--refresh-seed`.

- UI-008 (2026-03-22): Music4All governance-closure tracking item.
	- resolution: Closed by current-state confirmation that DS-001 is already received and operational for active runs; unresolved-issue status removed per user directive.
	- evidence: user confirmation in chat on 2026-03-25; `06_data_and_sources/dataset_registry.md` DS-001 delivery state; `00_admin/thesis_state.md` active DS-001 posture.

- UI-002 (2026-03-15): Chapter 2 weak-support remediation objective.
	- resolution: Day 2 and Day 3 hardening passes completed; final micro-pass achieved `TOTAL_KEYS_WITH_WEAK=0` for current Chapter 2 audit workflow.
	- key_metrics:
		- baseline: 22 papers with weak claims (24 weak claims)
		- final: 0 papers with weak claims
		- reduction: 100% of baseline weak-claim papers removed in current audited state
	- evidence: `09_quality_control/chapter2_verbatim_audit.md`; `09_quality_control/summarize_ch2_verbatim_audit.py`; `00_admin/timeline.md` (Day 3 closure note).

- UI-007 (2026-03-21): Spotify API ingestion was temporarily blocked by provider-side long cooldown (`HTTP 429`) on `/me`.
	- resolution: Subsequent authenticated export completed successfully (run_id `SPOTIFY-EXPORT-20260321-192533-881299`), generating full BL-002 artifacts and enabling real-data BL-020 execution.
	- evidence: `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_export_run_summary.json`; `07_implementation/experiment_log.md` (`EXP-022`); `00_admin/change_log.md` (`C-071`).

## Resolved (Historical)

- UI-006 (2026-03-21): Governance mismatch after DS-002 activation where `thesis_state.md` still stated Music4All/Music4All-Onion as current primary scope.
	- resolution: Synchronized `00_admin/thesis_state.md` to DS-002 active wording and aligned objective/assumption/limitation phrasing.
	- evidence: `00_admin/thesis_state.md` (2026-03-21 update), `00_admin/change_log.md` (`C-042`).

- UI-005 (2026-03-19): Base Music4All was unusable in the local environment; Onion-only workaround was the active interim path.
	- resolution: Superseded by planning decision `D-015`, which activated DS-002 as the BL-019 strategy.
	- evidence: `00_admin/decision_log.md` (`D-015`); `06_data_and_sources/dataset_registry.md` DS-002 status update.

- UI-004 (2026-03-19): Candidate corpus change review between Music4All-Onion and `MSD subset + Last.fm Tag Dataset + MusicBrainz mapping`.
	- resolution: BL-018 feasibility review completed. Result: do not switch corpus; retain MSD-based option as fallback only.
	- evidence: `07_implementation/implementation_notes/bl000_data_layer/candidate_corpus_feasibility_review_2026-03-19.md`; `00_admin/decision_log.md` (`D-008`).

- UI-001 (2026-03-15): Parser mismatch between author-year Chapter 2 style and key-based claim extractor.
	- resolution: Extended `09_quality_control/run_ch2_verbatim_audit.py` to map author-year citations to source-index keys and regenerate non-zero claim extraction.
	- evidence: `09_quality_control/run_ch2_verbatim_audit.py`; `09_quality_control/chapter2_verbatim_audit.md`; `00_admin/change_log.md` (`C-009`).
