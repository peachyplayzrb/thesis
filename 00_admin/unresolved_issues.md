# Unresolved Issues

Last updated: 2026-04-12

## Active
None.


Active-set sync note (2026-03-25 18:25 UTC): Open items are UI-003 (citation package closure) and UI-013 (pipeline optimization and evidence-hygiene closure).
Active-set sync note (2026-03-25 22:55 UTC): Open items remain UI-003 (citation package closure) and UI-013 (pipeline optimization and evidence-hygiene closure); UI-013 control-surface uplift is implemented, optimization tuning closure is pending.
Active-set sync note (2026-03-25 23:00 UTC): Open items remain UI-003 and UI-013; UI-013 BL-008 explanation-dominance criterion is now passing under the v1b profile, with remaining closure work centered on BL-010/BL-011 path-semantics normalization and final evidence packaging.
Active-set sync note (2026-03-25 23:10 UTC): Open items remain UI-003 and UI-013; UI-013 path-semantics normalization for BL-010/BL-011 is now implemented and revalidated (`BL010-REPRO-20260325-231041`, `BL011-CTRL-20260325-231130`, freshness `BL-FRESHNESS-20260325-231159`), leaving final evidence packaging as the remaining closure step.
Active-set sync note (2026-03-26 UTC): Open items remain UI-003 and UI-013. Implementation hardening pass completed (C-176/C-177): artifact-load validation hardened across BL-003/BL-008/BL-009/BL-010/BL-011/DS-001 with fail-fast helpers and schema guards; BL-006 scoring engine empty lead-genre false match fixed. BL-010/BL-011/BL-014 all pass on updated baseline. UI-013 remaining work is final evidence packaging and BL-005/BL-006 tuning sweep closure.
Active-set sync note (2026-03-26 17:56 UTC): Open items remain UI-003 and UI-013. BL-006 contribution semantics are now corrected and BL-007 to BL-009 lineage has been refreshed (`BL006-SCORE-20260326-175531-101302`, `BL007-ASSEMBLE-20260326-175552-183434`, `BL008-EXPLAIN-20260326-175552-995824`, `BL009-OBSERVE-20260326-175553-758828`, `BL014-SANITY-20260326-175554-065408`). This fixes a real transparency/evidence bug, but BL-008 diversity evidence must be regenerated under the corrected weighted-contribution contract before UI-013 can be closed.
Active-set sync note (2026-03-26 18:06 UTC): Open items now reduce to UI-003 only. UI-013 is closed after refreshed v1b acceptance evidence on the corrected BL-006 weighted-contribution contract passed all thresholds (`BL013-ENTRYPOINT-20260326-180047-134553`, `BL014-SANITY-20260326-180057-357905`; BL-008 dominance `0.3`, BL-005 kept `54402`, BL-003 match rate `0.1595`).
Active-set sync note (2026-03-26 21:03 UTC): Open active item remains UI-003 (citation package closure). Pipeline is now stable on the v1f baseline (`run_config_ui013_tuning_v1f.json`): danceability, energy, and valence are active end-to-end in BL-005 and BL-006; BL-013 restore `BL013-ENTRYPOINT-20260326-210305-914179` and BL-014 sanity pass (`22/22`). BL-010 reproducibility pass (`BL010-REPRO-20260326-205834`); BL-011 controllability pass (`BL011-CTRL-20260326-205932`). Active freshness suite at `6/8` — non-blocking evidence-alignment caveat documented in CODEBASE_ISSUES_CURRENT.md. Planned next steps: freshness re-alignment, UI-003 citation closure, chapter alignment to v1f counts, and evaluation evidence packaging for Chapter 5.
Active-set sync note (2026-03-26 21:27 UTC): Freshness re-alignment is complete. BL-010 pass (`BL010-REPRO-20260326-212523`), BL-011 pass (`BL011-CTRL-20260326-212611`), BL-013 restore pass (`BL013-ENTRYPOINT-20260326-212711-234744`), BL-014 sanity pass (`BL014-SANITY-20260326-212725-976781`), and active freshness suite pass (`BL-FRESHNESS-SUITE-20260326-212726`, `7/7`). Open active issue remains UI-003 only.
Active-set sync note (2026-03-26 22:30 UTC): Evidence audit completed for the canonical v1f baseline (EXP-048 / C-182). All 10 playlist track titles resolved from `ds001_working_candidate_dataset.csv`. BL-010/BL-011 config-snapshot divergence documented: BL-010 uses 70,680 candidates (pinned snapshot), BL-011 uses 33,096 (pinned snapshot), canonical v1f uses 46,776; both evaluation passes remain valid on their respective pinned states. Key chapter-alignment numbers confirmed: 46,776 filtered candidates, 10 scoring components, 22/22 sanity checks, 7/7 freshness, 1064 seeds, ~84% alignment miss rate. Dissertation claims by strength packaged. Open active issue remains UI-003 only.
Active-set sync note (2026-03-27 01:22 UTC): v1f evidence refresh and document-consistency pass completed. BL-013 pass (`BL013-ENTRYPOINT-20260327-012149-023331`), BL-014 sanity pass (`BL014-SANITY-20260327-011939-797165`, `22/22`), BL-010 pass (`BL010-REPRO-20260327-011941`), BL-011 pass (`BL011-CTRL-20260327-012056`), and active freshness suite pass (`BL-FRESHNESS-SUITE-20260327-012201`, `19/19`). Chapter 4 EP matrix rows are now populated and abstract draft is in place. Open active issue remains UI-003 only.
Active-set sync note (2026-03-27 03:05 UTC): UI-003 closure package is now complete at control-record level. Chapters 3 to 5 claim-verdict matrix and chapter-targeted hardening notes are logged in `09_quality_control/ui003_claim_verdicts_ch3_ch5.md` and `09_quality_control/ui003_chapter_hardening_notes_ch3_ch5.md`. No active unresolved issues remain.
Active-set sync note (2026-03-29 UTC): Confirmed no active unresolved issues. Architecture migration wave (BL-003 typed boundaries + stage-shell, BL-004 through BL-007 OO migration + controllable-logic uplift) is complete and logged. Documentation sync C-219 is complete. 00_admin full synchronization wave C-220 is in progress. Only remaining active scope is physical submission packaging.
Active-set sync note (2026-03-30 UTC): Aggressive root archival wave accepted and executed (D-044/C-222). No new unresolved blocker opened by this operation; active runtime posture remains `07_implementation/main.py` with archived root wrappers/config surfaces retained in deep archive.
Active-set sync note (2026-04-09 UTC): Confirmed no active unresolved issues after the pyright/full-contract closure wave. The active `07_implementation` runtime path revalidated clean with pytest `361/361`, pyright `0 errors, 0 warnings, 0 informations`, BL-013 pass `BL013-ENTRYPOINT-20260409-180340-350614`, and BL-014 pass `BL014-SANITY-20260409-180356-824725` (`28/28`).
Active-set sync note (2026-04-09 runtime-root governance): Confirmed no active blocker. Workflow authority is now explicitly anchored to `07_implementation/`; `_scratch/` (including `_scratch/final_artefact_bundle/`) is reference-only and should not be treated as active runtime control surface.
Active-set sync note (2026-04-10 zero-trust audit closeout): Confirmed no new unresolved blocker from the Chapter 2 zero-trust reference audit cycle; all citations extracted from the frozen Chapter 2 baseline received manual verdicts, and no citation remained unverifiable.

## Resolved (Recent)

- UI-014 (2026-04-12): Architecture rebuild RQ/objective derivation blocker.
	- resolution: Closed. RQ and objective set were derived from confirmed Chapter 2 tensions, scope and artefact definition were locked for rebuild posture, and governance/foundation mirrors were synchronized.
	- evidence:
		1. `00_admin/decision_log.md` (`D-053`, `D-054`).
		2. `00_admin/change_log.md` (`C-283`).
		3. `00_admin/thesis_state.md`, `02_foundation/current_title_and_rq.md`, `02_foundation/objectives.md`, `02_foundation/contribution_statement.md`, `02_foundation/assumptions.md`, `02_foundation/limitations.md`, `00_admin/timeline.md`.

- UI-003 (2026-03-19): Thesis-wide citation verification and literature leverage synthesis closure.
	- resolution: Closed at control-record level. Claim-citation matrix expansion for Chapters 3 to 5 is complete, verdict labels were recorded (`supported`, `partially_supported`, `weak_support`, `mismatch`), and chapter-targeted hardening notes were documented for remaining weak/mismatch text locations.
	- evidence:
		1. `09_quality_control/ui003_claim_verdicts_ch3_ch5.md` (claim-level verdict matrix).
		2. `09_quality_control/ui003_chapter_hardening_notes_ch3_ch5.md` (chapter-targeted rewrite/citation-swap notes).
		3. Cross-reference consistency maintained with `09_quality_control/claim_evidence_map.md` and `09_quality_control/citation_checks.md`.

- UI-013 (2026-03-25): Pipeline optimization and evidence-hygiene package closure on the active BL baseline.
	- resolution: Closed. The controlled tuning sweep, BL-010/BL-011 path-semantics normalization, BL-006 transparency-contract correction, and refreshed v1b acceptance evidence now all align on one corrected active baseline.
	- evidence:
		1. Canonical implementation reporting baseline is now `07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json` per D-033 (superseding the baseline-selection aspect of D-032). `run_config_ui013_tuning_v2a_retrieval_tight.json` remains experimental.
		2. Controlled sweep across `v1`, `v1a`, `v1b`, `v1c` remains logged in `_scratch/ui013_tuning_sweep_results.json`.
		3. BL-010 / BL-011 path-semantics normalization and freshness evidence remains passing from 2026-03-25.
		4. BL-006 transparency-contract correction completed on 2026-03-26 (`C-178`, `EXP-046`).
		5. Refreshed v1b acceptance pass on corrected semantics succeeded (`BL013-ENTRYPOINT-20260326-180047-134553`, `BL014-SANITY-20260326-180057-357905`).
		6. Acceptance metrics now satisfy all UI-013 thresholds on the corrected baseline: `bl003_match_rate=0.1595`, `bl005_kept_candidates=54402`, `bl006_numeric_minus_semantic=-0.068775`, `bl008_top_label_dominance_share=0.3`.
		7. Refreshed BL-008 top-contributor distribution is `{Lead genre match:3, Tag overlap:3, Tempo (BPM):3, Genre overlap:1}` in `_scratch/ui013_v1b_bl008_focus_result.json`.

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
