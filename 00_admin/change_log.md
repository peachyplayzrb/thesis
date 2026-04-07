# Change Log

Use schema from `00_admin/operating_protocol.md`.

Ordering convention (standardized 2026-03-24):
- This log is append-only for traceability.
- Entry order reflects historical insertion timing and may not be numerically contiguous in older sections.
- New entries must be appended at the end; historical entries remain unchanged except for explicit correction records.

Maintenance snapshot (2026-03-29):
- Highest change ID currently present: `C-221`
- Maintenance snapshot (2026-03-28): prior snapshot stated `C-205`; superseded by the 2026-03-29 architecture migration + documentation sync wave (C-204 through C-219).
- Known legacy correction applied in this file: prior duplicate `C-079` entry has been normalized to `C-135` for unique-ID compliance.

## C-001
| C-160 | 2026-03-25 01:54 | Copilot | Added consolidated Tier-1 hardening execution log cross-links to admin control files and synchronized thesis state/timeline after integrated validation closure. |
| C-161 | 2026-03-25 02:05 | Copilot | Added a comprehensive current implementation information sheet describing the live pipeline structure, stage responsibilities, active controls, artifacts, runtime behavior, and limitations. |
| C-162 | 2026-03-25 02:10 | Copilot | Aligned BL-004, BL-005, and BL-006 to one canonical genre-first lead-genre rule, then reran BL-013 and BL-014 to validate the semantic-contract fix. |
| C-163 | 2026-03-25 02:11 | Copilot | Refreshed BL-010 and BL-011 evidence on the corrected pipeline baseline and updated the active freshness-risk record with the new reproducibility and controllability run results. |
| C-164 | 2026-03-25 02:13 | Copilot | Added a BL-010/BL-011 freshness enforcement script, validated it against the live baseline, and closed the remaining control-evidence drift issue. |
| C-165 | 2026-03-25 02:16 | Copilot | Added and validated an active freshness suite runner that executes BL-014 and BL-010/BL-011 freshness checks, and corrected the UI-003 due-window regression in unresolved issues. |
| C-166 | 2026-03-25 15:00 | Copilot | Recalibrated milestone execution status in timeline governance (M3/M4 moved to in progress) and synchronized thesis-state priority/risk wording after UI-010 closure. |
| C-167 | 2026-03-25 15:20 | Copilot | Executed a full admin-control sync pass to remove stale freshness-tail wording and align open-item/handoff snapshots to the current unresolved issue set. |
| C-168 | 2026-03-25 16:15 | Copilot | Logged end-to-end profile-switch validation session: A/B harness add-and-revert history, retained cache/user-id code fixes, temporary threshold config usage, and regenerated BL-002 to BL-014 evidence surfaces for next-day regression check. |
| C-169 | 2026-03-25 16:35 | Copilot | Executed fail-fast high-risk regression run, fixed BL-013 command path in checklist, resolved continuity mismatch by rerunning full BL-013 chain, and reconfirmed BL-014 plus active freshness pass. |
| C-170 | 2026-03-25 16:45 | Copilot | Removed temporary ops log artifacts on user request and consolidated final handoff state directly in changelog to preserve traceability before chat switch. |
| C-171 | 2026-03-25 16:40 | Copilot | Completed BL-ordered implementation-notes path migration hardening, fixed missed path-construction references across stage scripts, reran BL-013 to pass, reran BL-014 to 21/21 pass, and updated handoff-critical admin state for chat transition. |
| C-172 | 2026-03-25 18:25 | Copilot | Expanded implementation state into a comprehensive issue-focused health report and synchronized admin control files (`thesis_state.md`, `unresolved_issues.md`) to track active optimization and evidence-hygiene risks. |
| C-173 | 2026-03-25 22:55 | Copilot | Implemented config-surface control uplift (`control_mode` + config-driven BL-009 bootstrap mode), refreshed BL-000/BL-009 state logs and implementation state, and synchronized admin tracking files for UI-013 progress evidence. |
| C-174 | 2026-03-25 23:00 | Copilot | Implemented and validated BL-008 explanation-diversity control uplift (near-tie primary-driver blending), updated stage/test/admin logs, and confirmed UI-013 BL-008 dominance target pass on v1b (`0.5` <= `0.6`) with BL-014 pass. |
| C-175 | 2026-03-25 23:10 | Copilot | Normalized BL-010 replay command path semantics to canonical BL-prefixed rendering, refreshed BL-010/BL-011 evidence with freshness and BL-014 passes, and synchronized implementation/admin logs for UI-013 closure progress. |
| C-176 | 2026-03-26 | Copilot | Hardened artifact-load validation across BL-003, BL-008, BL-009, BL-010, BL-011, and DS-001: added fail-fast `load_required_json()` helpers, schema guards, and retry-transparency fields; confirmed BL-010/BL-011/BL-014 pass on updated baseline. |
| C-177 | 2026-03-26 | Copilot | Fixed BL-006 scoring engine empty lead-genre false match: added non-empty guard to `lead_genre_similarity` so tracks without genre data no longer receive spurious perfect scores; BL-014 pass confirmed post-fix. |
| C-178 | 2026-03-26 | Copilot | Corrected BL-006 weighted-contribution semantics and matched-label propagation, then refreshed BL-007 through BL-009 lineage and reconfirmed BL-014 pass on the corrected baseline. |
| C-179 | 2026-03-26 | Copilot | Refreshed UI-013 v1b acceptance evidence on the corrected BL-006 baseline, updated control/test artifacts, and closed UI-013 after reconfirming all thresholds with BL-013 and BL-014 passes. |
| C-180 | 2026-03-26 21:03 | Copilot | Implemented v1f numeric retune (danceability, energy, valence activated end-to-end in BL-005 and BL-006), applied Windows WinError 1224 fix in BL-010, restored live pipeline to v1f, and updated all stage state logs and CODEBASE_ISSUES_CURRENT.md with a next-steps section and issue register. |
| C-181 | 2026-03-26 21:27 | Copilot | Completed freshness re-alignment on the active v1f baseline (BL-010, BL-011, BL-013 restore, BL-014 freshness suite), returning active freshness status to pass and synchronizing CODEBASE_ISSUES_CURRENT.md plus admin state files. |
| C-182 | 2026-03-26 22:30 | Copilot | Completed evidence audit for the canonical v1f baseline: resolved all 10 playlist track titles from DS-001 CSV, documented BL-010/BL-011 config-snapshot candidate-count divergence (70,680 / 33,096 vs 46,776 v1f), packaged dissertation claims by strength, and updated all admin/state logs to reflect v1f canonical evidence. |
| C-183 | 2026-03-27 | Copilot | Started implementation-alignment cleanup pass: locked v1f as canonical baseline across backlog/setup/run-config status docs, marked v1d snapshot sections as historical, and clarified v2a as experimental pending explicit promotion. |
| C-184 | 2026-03-27 | Copilot | Synchronized docs/governance evidence after external v2a run wave: logged EXP-049, updated backlog posture with latest experimental run IDs and pass metrics, and preserved v1f as canonical reporting baseline. |
| C-185 | 2026-03-27 | Copilot | Completed docs/governance alignment to current state: resolved D-032 vs D-033 baseline wording drift, externalized superseded v1d snapshot into historical notes, added BL-010/BL-011 pinning manifest, added run-config/profile lifecycle and retention policy docs, and added BL-013 run-wave manifest without changing runtime code or deleting artifacts. |
| C-186 | 2026-03-27 | Copilot | Workspace environment cleanup: consolidated six scattered archive folders into `_deep_archive_march2026/`, pruned BL-013 run logs from 117 to 10 most recent, moved `_archive_cleanup_staging_2026-03-26/` out of workspace to parent folder, deleted orphaned workspace-root `07_implementation/` (older duplicate of canonical copy), moved 6 dated admin bloat files into `00_admin/archives/`, and cleaned 21 `__pycache__` directories from project source. Updated file_map.md to reflect new layout. |
| C-187 | 2026-03-27 | Copilot | Document-consistency pass: re-ran BL-013 on v1f with seed refresh and refreshed BL-010/BL-011 via active freshness suite (`BL-FRESHNESS-SUITE-20260327-012201`, 19/19 pass), populated Chapter 4 EP matrix rows with current artifact evidence, corrected Chapter 5 stale baseline wording, authored thesis abstract, and archived stale `07_implementation/IMPLEMENTATION_STATE_2026-03-24.md` plus `07_implementation/implementation_plan.md` into `_deep_archive_march2026/`. |
| C-188 | 2026-03-27 | Copilot | Closed UI-003 at control-record level by adding Chapter 3 to 5 claim-verdict matrix and chapter-targeted hardening notes (`09_quality_control/ui003_claim_verdicts_ch3_ch5.md`, `09_quality_control/ui003_chapter_hardening_notes_ch3_ch5.md`) and synchronizing admin status surfaces (`unresolved_issues.md`, `thesis_state.md`, `backlog.md`, `experiment_log.md`). |
| C-189 | 2026-03-27 | Copilot | Synced admin/state surfaces to current repository posture: refreshed `README.md`, `timeline.md`, and `thesis_state.md` timestamps/status language; aligned `backlog.md` canonical versus additional-wave evidence wording; and logged reconciliation pass in `experiment_log.md` (`EXP-051`) while preserving v1f as canonical baseline. |
| C-190 | 2026-03-27 18:49 | Copilot | Completed BL-023 website-server hardening pass: migrated `07_implementation/setup/website_api_server.py` from `http.server` to FastAPI + uvicorn while preserving subprocess stage orchestration and existing `{"error": ...}` API contract, added typed POST request models plus app-state initialization, tightened localhost CORS, updated `smoke_website_api.ps1` for the 7-stage surface, added `test_website_api_server.py` regression coverage, and added runtime/test dependencies in `requirements.txt` (`fastapi`, `uvicorn[standard]`, `httpx`). |
| C-191 | 2026-03-27 | Copilot | Refactored the thesis workflow customization surface for natural-language Ask and Plan/Autopilot use: updated `.github/copilot-instructions.md` to route mode by intent instead of prompt dependence, added `.github/agents/thesis-ask.agent.md` and `.github/agents/thesis-autopilot.agent.md`, added a lightweight user-level instruction at `Code/User/prompts/natural-language-workflow.instructions.md` for cross-workspace self-improving workflow behavior, corrected the stale `AGENTS.md` inventory entry in `file_map.md`, and logged the design in `D-036` / `EXP-053`. |
| C-192 | 2026-03-28 | Copilot | Completed final_artefact clean-code pass (phases F5, G1, H): removed dead `sha256_direct` from `shared_utils/io_utils.py`, extracted `combined_sha256` local function from `observability/main.py` into `shared_utils/hashing.py` as `sha256_of_values`, migrated `resolve_bl009_runtime_controls` in `observability/main.py` to the `resolve_stage_controls` factory (matching BL-007/BL-008 pattern), and added `tests/test_observability_runtime_controls.py` with 3 parity tests. All 171 tests pass. G2 (BL-004, BL-011 resolver migration) deferred per D-039. |
## C-162
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Aligned BL-004, BL-005, and BL-006 to one canonical genre-first lead-genre rule, then regenerated and validated the pipeline artifacts.
- reason: A review found that BL-004 built `top_lead_genres` from `genres[0]` first while BL-005 and BL-006 evaluated candidate `lead_genre` from `tags[0]` first, creating a semantic-contract mismatch.
- evidence_basis: Updated lead-genre resolution logic in BL-004, BL-005, and BL-006; BL-013 pass `BL013-ENTRYPOINT-20260325-020526-881730`; BL-014 pass `BL014-SANITY-20260325-020553-870468` (`21/21` checks).
- affected_components: `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`, `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`, `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `00_admin/unresolved_issues.md`, `07_implementation/test_notes.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Removes a real semantic inconsistency from retrieval and scoring, improving the internal validity of the hybrid preference-matching pipeline.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.
## C-163
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Refreshed BL-010 reproducibility and BL-011 controllability evidence on the corrected post-fix baseline and synchronized the active freshness-risk record.
- reason: After the lead-genre contract fix, the evaluation evidence needed regeneration so controllability and reproducibility claims were tied to the corrected live pipeline.
- evidence_basis: BL-010 pass `BL010-REPRO-20260325-020749` (`deterministic_match=true`); BL-011 pass `BL011-CTRL-20260325-020828` (`all_scenarios_repeat_consistent=true`, `all_variant_shifts_observable=true`, `status=pass`).
- affected_components: `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_report.json`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_run_matrix.csv`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_config_snapshot.json`, `07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_report.json`, `07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_run_matrix.csv`, `07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_config_snapshot.json`, `00_admin/unresolved_issues.md`, `07_implementation/test_notes.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Restores currency of evaluation evidence after a behavioral fix while preserving visibility of the remaining governance automation gap.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.
## C-164
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Added a quality-layer freshness enforcement script for BL-010 and BL-011, validated it on the live baseline, and closed the remaining control-evidence drift issue.
- reason: UI-010 remained open until there was an executable control that could fail when BL-010/BL-011 evidence no longer matched the current active baseline contracts and inputs.
- evidence_basis: `07_implementation/implementation_notes/bl014_quality/check_bl010_bl011_freshness.py`; freshness report `07_implementation/implementation_notes/bl014_quality/outputs/bl010_bl011_freshness_report.json` (`overall_status=pass`, `9/9` checks); refreshed BL-010 / BL-011 evidence from 2026-03-25.
- affected_components: `07_implementation/implementation_notes/bl014_quality/check_bl010_bl011_freshness.py`, `07_implementation/implementation_notes/bl014_quality/outputs/bl010_bl011_freshness_report.json`, `07_implementation/implementation_notes/bl014_quality/outputs/bl010_bl011_freshness_matrix.csv`, `00_admin/unresolved_issues.md`, `07_implementation/test_notes.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Converts freshness from a manual governance reminder into an executable validation control and closes the residual BL-010/BL-011 drift risk.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.
## C-165
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Added a consolidated active freshness suite runner, executed it to generate pass evidence, and corrected a due-window regression in unresolved issues.
- reason: User requested logging coverage and freshness checks broadly across active tests; a single suite command improves repeatability and reduces operator error.
- evidence_basis: `07_implementation/implementation_notes/bl014_quality/run_active_freshness_suite.py`; suite report `07_implementation/implementation_notes/bl014_quality/outputs/bl_active_freshness_suite_report.json` (`overall_status=pass`, `6/6` checks); suite matrix `07_implementation/implementation_notes/bl014_quality/outputs/bl_active_freshness_suite_matrix.csv`.
- affected_components: `07_implementation/implementation_notes/bl014_quality/run_active_freshness_suite.py`, `07_implementation/implementation_notes/bl014_quality/outputs/bl_active_freshness_suite_report.json`, `07_implementation/implementation_notes/bl014_quality/outputs/bl_active_freshness_suite_matrix.csv`, `00_admin/unresolved_issues.md`, `07_implementation/test_notes.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Provides one-command freshness validation for active evidence surfaces and hardens governance reliability.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.
## C-166
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Recalibrated milestone status representation to reflect implemented reality and synchronized thesis-state priority/risk wording with closed UI-010 freshness controls.
- reason: User requested explicit milestone clarity after confirming that M3/M4 labels should be updated to match completed implementation scope.
- evidence_basis: `00_admin/timeline.md` milestone labels updated to `in progress` for M3/M4 with status note; `00_admin/thesis_state.md` priority checkpoint and active-risk wording updated to reflect operational freshness controls.
- affected_components: `00_admin/timeline.md`, `00_admin/thesis_state.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Reduces governance ambiguity by aligning planned-vs-complete messaging with the actual implementation baseline.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.
## C-167
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Completed a control-surface synchronization pass across admin docs so active/open status wording is consistent with closed freshness controls and current unresolved-issue state.
- reason: User requested that admin files be fully up to date before switching to a new work context.
- evidence_basis: `00_admin/current_implementation_information_sheet_2026-03-25.md` no longer describes BL-010/BL-011 freshness as an open tail; `00_admin/unresolved_issues.md` active-set sync note now states UI-003 is the only open issue; `00_admin/README.md` and `00_admin/handoff_friend_chat_playbook.md` include current governance-sync notes.
- affected_components: `00_admin/current_implementation_information_sheet_2026-03-25.md`, `00_admin/unresolved_issues.md`, `00_admin/README.md`, `00_admin/handoff_friend_chat_playbook.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Improves handoff reliability and reduces state drift risk across operational control surfaces.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.
## C-168
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Logged complete profile-switch test cycle and rollback cycle, including retained ingestion/profile hardening fixes and regenerated run artifacts used for final all-green checks.
- reason: User requested a full auditable log of what changed so breakage can be checked tomorrow against a known baseline.
- evidence_basis: Commit ledger on 2026-03-25 includes A/B harness creation and explicit reverts (`237d766`, `703e1c0`, `5402fd2`, `38c5d1e`, `64b5d1f`, `8b5a95e`); latest successful orchestration run `BL013-ENTRYPOINT-20260325-033853-801126`; BL-014 sanity pass and active freshness pass in quality outputs.
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/spotify_client.py`, `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`, `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`, `07_implementation/implementation_notes/bl000_run_config/outputs/run_config_profile_test_threshold_015.json`, `07_implementation/implementation_notes/bl003_alignment/outputs/*`, `07_implementation/implementation_notes/bl004_profile/outputs/*`, `07_implementation/implementation_notes/bl005_retrieval/outputs/*`, `07_implementation/implementation_notes/bl006_scoring/outputs/*`, `07_implementation/implementation_notes/bl007_playlist/outputs/*`, `07_implementation/implementation_notes/bl008_transparency/outputs/*`, `07_implementation/implementation_notes/bl009_observability/outputs/*`, `07_implementation/implementation_notes/bl014_quality/outputs/*`, `07_implementation/implementation_notes/bl013_entrypoint/outputs/*`, `07_implementation/implementation_notes/bl000_run_config/outputs/*`, `00_admin/change_log.md`
- impact_assessment: High-positive for auditability and reproducibility. Session now has a single control-log anchor that distinguishes reverted work from active fixes and identifies the exact temporary threshold context (`match_rate_min_threshold=0.15`) used in the latest passing profile run.
- approval_record: Requested by user in chat on 2026-03-25.
## C-169
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Ran the next-day fail-fast regression plan, identified a non-code continuity failure after partial reruns, reran BL-013 end-to-end to restore hash/run-id continuity, and revalidated BL-014 plus active freshness to all-pass.
- reason: User requested execution of the next-day fix plan and asked for a practical, auditable resolution path.
- evidence_basis: BL-013 pass `BL013-ENTRYPOINT-20260325-151555-244335`; BL-014 pass `BL014-SANITY-20260325-151612-236386` (`21/21` checks); active freshness suite report pass; run report `00_admin/ops_logs/high_risk_regression_run_2026-03-25.md`.
- affected_components: `00_admin/ops_logs/high_risk_regression_checklist_2026-03-25.md`, `00_admin/ops_logs/high_risk_regression_run_2026-03-25.md`, `07_implementation/implementation_notes/bl013_entrypoint/outputs/bl013_orchestration_run_latest.json`, `07_implementation/implementation_notes/bl014_quality/outputs/bl014_sanity_report.json`, `07_implementation/implementation_notes/bl014_quality/outputs/bl_active_freshness_suite_report.json`, `00_admin/change_log.md`
- impact_assessment: High-positive. Confirms no newly observed code-level regression on the exercised path and hardens operator workflow by correcting the BL-013 command in the checklist.
- approval_record: Requested by user in chat on 2026-03-25.
## C-170
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Deleted `00_admin/ops_logs/` artifacts and preserved final regression/handoff state in changelog for chat transition.
- reason: User requested ops log cleanup while keeping an auditable final state before switching to another chat.
- evidence_basis: `00_admin/ops_logs/` removed; last validated state remains BL-013 pass (`BL013-ENTRYPOINT-20260325-151555-244335`), BL-014 pass (`BL014-SANITY-20260325-151612-236386`, `21/21`), and active freshness suite pass recorded in quality output reports.
- affected_components: `00_admin/ops_logs/*` (deleted), `00_admin/change_log.md`
- impact_assessment: Neutral-to-positive. Reduces admin artifact clutter while retaining essential operational traceability in the canonical log.
- approval_record: Requested by user in chat on 2026-03-25.

## C-171
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Finalized and hardened the BL-ordered folder migration (`implementation_notes/*` -> `implementation_notes/blXXX_*`) by fixing all missed multi-line and inline path-construction references, then regenerated orchestration and sanity evidence on the migrated layout.
- reason: User requested logging and completion of all necessary fixes before moving to a new chat context.
- evidence_basis: BL-013 pass `BL013-ENTRYPOINT-20260325-163713-079187`; BL-014 pass `BL014-SANITY-20260325-163738-023840` (`21/21` checks); migration-stabilization fixes applied to BL-003 through BL-014 stage/quality scripts.
- affected_components: `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`, `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`, `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`, `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`, `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`, `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`, `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`, `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`, `07_implementation/implementation_notes/bl011_controllability/run_bl011_controllability_check.py`, `07_implementation/implementation_notes/bl014_quality/check_bl010_bl011_freshness.py`, `07_implementation/implementation_notes/bl014_quality/run_active_freshness_suite.py`, `00_admin/current_implementation_information_sheet_2026-03-25.md`, `00_admin/thesis_state.md`, `00_admin/handoff_friend_chat_playbook.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Removes post-rename execution drift risk and preserves a clean handoff baseline with fresh passing run evidence.
- approval_record: Requested by user in chat on 2026-03-25.

## C-172
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Replaced the implementation-state snapshot with a comprehensive issue-focused health report and synchronized admin tracking files to reflect active implementation-quality and governance risks.
- reason: User requested a more comprehensive implementation assessment that explicitly identifies current issues and then asked to update admin files accordingly.
- evidence_basis: `07_implementation/IMPLEMENTATION_STATE_2026-03-24.md` now includes an explicit issue register (BL-003 through BL-013 risk items), prioritized action plan, and cross-cutting technical debt summary; `00_admin/unresolved_issues.md` now tracks UI-013; `00_admin/thesis_state.md` now reflects the updated open-risk posture.
- affected_components: `07_implementation/IMPLEMENTATION_STATE_2026-03-24.md`, `00_admin/unresolved_issues.md`, `00_admin/thesis_state.md`, `00_admin/change_log.md`
- impact_assessment: High-positive for governance clarity. Preserves passing operational baseline while making unresolved optimization and evidence-hygiene debt explicit and auditable for Chapter 4/5 limitation framing.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.

## C-173
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Implemented config-driven control-surface uplift for UI-013 (new `control_mode` governance switches and config-driven BL-009 bootstrap mode), then synchronized stage/admin logs and implementation-state evidence.
- reason: User requested stronger operator control through configuration and then requested that all implementation/admin logs be updated and committed to reflect these implementation changes.
- evidence_basis: `run_config_utils.py` now resolves `control_mode` fields (`validation_profile`, `allow_threshold_decoupling`, `allow_weight_auto_normalization`) and `observability_controls.bootstrap_mode`; BL-009 run log includes `run_config.control_mode` and config-driven `run_metadata.bootstrap_mode`; BL-000 and BL-009 stage state logs plus `IMPLEMENTATION_STATE_2026-03-24.md` were updated to reflect this baseline.
- affected_components: `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`, `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`, `07_implementation/implementation_notes/bl000_run_config/configs/templates/run_config_template_v1.json`, `07_implementation/implementation_notes/bl000_run_config/outputs/run_config_profile_test_threshold_015.json`, `07_implementation/implementation_notes/bl000_run_config/docs/bl000_run_config_state_log_2026-03-25.md`, `07_implementation/implementation_notes/bl009_observability/bl009_state_log_2026-03-24.md`, `07_implementation/IMPLEMENTATION_STATE_2026-03-24.md`, `00_admin/thesis_state.md`, `00_admin/unresolved_issues.md`, `00_admin/change_log.md`
- impact_assessment: High-positive for controllability and governance clarity. Moves behavior-selection decisions from hardcoded defaults into explicit run-config controls while preserving strict-safe defaults.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.

## C-174
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Implemented BL-008-focused explanation-diversity control uplift by adding near-tie primary-driver blending controls to run-config, wiring BL-008 primary-driver selection to those controls, and validating UI-013 acceptance on the v1b profile.
- reason: UI-013 remained blocked by BL-008 top-label dominance (`0.8`), requiring a bounded, auditable, config-driven remediation pass.
- evidence_basis: BL-013 pass `BL013-ENTRYPOINT-20260325-225725-328263`; BL-014 pass `BL014-SANITY-20260325-225735-601840`; BL-008 distribution `Lead genre match:5, Tag overlap:3, Genre overlap:2`; dominance share `0.5`; focused evidence artifact `_scratch/ui013_v1b_bl008_focus_result.json`.
- affected_components: `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`, `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`, `07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1b.json`, `07_implementation/implementation_notes/bl000_run_config/docs/bl000_run_config_state_log_2026-03-25.md`, `07_implementation/implementation_notes/bl008_transparency/bl008_state_log_2026-03-24.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/IMPLEMENTATION_STATE_2026-03-24.md`, `00_admin/unresolved_issues.md`, `00_admin/thesis_state.md`, `00_admin/change_log.md`, `00_admin/decision_log.md`
- impact_assessment: High-positive. Clears the remaining BL-008 UI-013 acceptance gate while preserving strict run-config governance and BL-014 quality pass status.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.

## C-175
- date: 2026-03-25
- proposed_by: Copilot
- status: accepted
- change_summary: Normalized BL-010 replay command path semantics to canonical BL-prefixed relative rendering, refreshed BL-010/BL-011 evidence on the active baseline, and synchronized implementation/admin logs for UI-013 closure progress.
- reason: UI-013 still tracked BL-010/BL-011 path-semantics as the remaining governance-hygiene tail after BL-008 acceptance passed.
- evidence_basis: BL-010 pass `BL010-REPRO-20260325-231041` (replay `stage_runs.command` canonicalized); BL-011 pass `BL011-CTRL-20260325-231130`; freshness pass `BL-FRESHNESS-20260325-231159` (`9/9` checks); BL-014 pass `BL014-SANITY-20260325-231204-534293` (`21/21` checks).
- affected_components: `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_report.json`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_run_matrix.csv`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_config_snapshot.json`, `07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_report.json`, `07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_run_matrix.csv`, `07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_config_snapshot.json`, `07_implementation/implementation_notes/bl014_quality/outputs/bl010_bl011_freshness_report.json`, `07_implementation/implementation_notes/bl014_quality/outputs/bl010_bl011_freshness_matrix.csv`, `07_implementation/implementation_notes/bl014_quality/outputs/bl014_sanity_report.json`, `07_implementation/implementation_notes/bl010_reproducibility/bl010_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl011_controllability/bl011_state_log_2026-03-24.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/IMPLEMENTATION_STATE_2026-03-24.md`, `00_admin/unresolved_issues.md`, `00_admin/thesis_state.md`, `00_admin/change_log.md`, `00_admin/decision_log.md`
- impact_assessment: High-positive. Closes the remaining BL-010/BL-011 path-rendering governance gap and leaves UI-013 focused on final evidence packaging.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.

## C-176
- date: 2026-03-26
- proposed_by: Copilot
- status: accepted
- change_summary: Hardened artifact-load validation across BL-003, BL-008, BL-009, BL-010, BL-011, and DS-001 with fail-fast helpers, schema guards, and retry-transparency reporting.
- reason: A focused implementation review identified silent degradation paths: BL-003 returned `{}` on malformed BL-002 summary, BL-008/BL-009/BL-011 performed raw dict loads with no schema checks, BL-010 hid retry-induced instability behind aggregate success, and DS-001 bypassed the shared Windows-safe writer.
- evidence_basis: BL-010 pass `BL010-REPRO-20260326-062024` (`deterministic_match=true`, `all_stage_runs_succeeded_without_retry=true`); BL-011 pass `BL011-CTRL-20260326-062103` (`status=pass`); BL-014 active suite pass (`overall_status=pass`, `7/7` checks).
- affected_components: `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`, `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`, `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`, `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`, `07_implementation/implementation_notes/bl011_controllability/run_bl011_controllability_check.py`, `07_implementation/implementation_notes/bl000_data_layer/build_ds001_working_dataset.py`, `00_admin/change_log.md`
- impact_assessment: High-positive. Converts six silent failure paths into explicit, labeled runtime errors with structured diagnostics, reducing the risk of masked upstream issues propagating to evaluation results.
- approval_record: Requested and confirmed by user in chat on 2026-03-26.

## C-177
- date: 2026-03-26
- proposed_by: Copilot
- status: accepted
- change_summary: Fixed BL-006 scoring engine empty lead-genre false match bug: added non-empty guard so `lead_genre_similarity` is only `1.0` when both candidate and profile have non-empty genre strings.
- reason: When both candidate and profile lacked a `lead_genre` value, the comparison `"" == ""` evaluated to `True`, awarding a spurious perfect lead-genre similarity score to genre-less tracks. This silently inflated scores for unclassified candidates.
- evidence_basis: Bug confirmed by direct read of `scoring_engine.py` lines 116-118; fix applied and verified clean (`py_compile` pass); BL-014 pass confirmed post-fix (`overall_status=pass`).
- affected_components: `07_implementation/implementation_notes/bl006_scoring/scoring_engine.py`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Removes a real scoring inaccuracy that could have inflated genre-less candidate rankings, improving result internal validity. Scoring output artifacts will differ marginally from pre-fix runs for candidates without genre data.
- approval_record: Requested and confirmed by user in chat on 2026-03-26.

## C-178
- date: 2026-03-26
- proposed_by: Copilot
- status: accepted
- change_summary: Corrected BL-006 so persisted `*_contribution` fields now store true weighted contributions instead of raw similarities, restored matched genre/tag propagation into BL-006 outputs, updated BL-006 summary wording for the real lead-genre rule, then regenerated BL-007 to BL-009 and reconfirmed BL-014 pass.
- reason: A focused review found that BL-006 wrote raw similarities into `*_contribution` fields while BL-006 diagnostics and BL-008 explanation ranking interpreted those fields as weighted contributions. This made transparency outputs and component-balance reporting semantically incorrect even though final score aggregation remained deterministic.
- evidence_basis: BL-006 pass `BL006-SCORE-20260326-175531-101302`; BL-007 pass `BL007-ASSEMBLE-20260326-175552-183434`; BL-008 pass `BL008-EXPLAIN-20260326-175552-995824`; BL-009 pass `BL009-OBSERVE-20260326-175553-758828`; BL-014 pass `BL014-SANITY-20260326-175554-065408` (`22/22` checks). Updated BL-006 top candidates now include non-empty `matched_genres` / `matched_tags`, and BL-006 `component_balance` now reports weighted contributions.
- affected_components: `07_implementation/implementation_notes/bl006_scoring/scoring_engine.py`, `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl006_scoring/outputs/*`, `07_implementation/implementation_notes/bl007_playlist/outputs/*`, `07_implementation/implementation_notes/bl008_transparency/outputs/*`, `07_implementation/implementation_notes/bl009_observability/outputs/*`, `07_implementation/implementation_notes/bl014_quality/outputs/bl014_sanity_report.json`, `07_implementation/experiment_log.md`, `00_admin/unresolved_issues.md`, `00_admin/change_log.md`
- impact_assessment: High-positive for transparency correctness and evidence integrity. The fix removes a real semantics bug in BL-006/BL-008 reporting, but it also means prior BL-008 primary-driver distribution evidence must be interpreted carefully and refreshed under the corrected weighted-contribution contract.
- approval_record: Requested and confirmed by user in chat on 2026-03-26.

## C-179
- date: 2026-03-26
- proposed_by: Copilot
- status: accepted
- change_summary: Refreshed the UI-013 v1b acceptance evidence on the corrected BL-006 weighted-contribution baseline, updated the scratch/test/admin evidence package, and closed UI-013 after reconfirming all thresholds with BL-013 and BL-014 passes.
- reason: After C-178 / EXP-046, the earlier UI-013 BL-008 diversity evidence could no longer be cited safely because it had been generated before the corrected weighted-contribution contract. A focused rerun was required to determine whether the tuned v1b profile still met the acceptance thresholds on the corrected baseline.
- evidence_basis: BL-013 pass `BL013-ENTRYPOINT-20260326-180047-134553`; BL-014 pass `BL014-SANITY-20260326-180057-357905` (`22/22` checks); refreshed metrics `bl003_match_rate=0.1595`, `bl005_kept_candidates=54402`, `bl006_numeric_minus_semantic=-0.068775`, `bl008_top_label_dominance_share=0.3`; refreshed BL-008 top-contributor distribution `{Lead genre match:3, Tag overlap:3, Tempo (BPM):3, Genre overlap:1}` in `_scratch/ui013_v1b_bl008_focus_result.json`.
- affected_components: `_scratch/ui013_v1b_bl008_focus_result.json`, `07_implementation/test_notes.md`, `07_implementation/experiment_log.md`, `00_admin/unresolved_issues.md`, `00_admin/thesis_state.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Converts UI-013 from a stale-evidence risk into a closed, traceable acceptance package on the corrected active baseline and narrows the remaining open dependency set to UI-003 citation closure.
- approval_record: Requested and confirmed by user in chat on 2026-03-26.

## C-180
- date: 2026-03-26
- proposed_by: Copilot
- status: accepted
- change_summary: Implemented v1f numeric retune activating danceability, energy, and valence end-to-end in BL-005 and BL-006; applied Windows WinError 1224 archive-copy fix in BL-010; restored live pipeline to v1f via BL-013; and updated all 13 stage state logs and CODEBASE_ISSUES_CURRENT.md with a next-steps section, R1 walk-semantics clarification, and full issue register.
- reason: After UI-013 closure on v1b, the outstanding danceability/energy/valence numeric dimensions were implemented end-to-end to complete the originally designed 10-component scoring surface. BL-010 had a Windows WinError 1224 failure on the first post-retune archive-copy step that required a targeted fallback fix. State logs and governance docs needed updating to reflect the v1f final baseline.
- evidence_basis: BL-013 restore pass `BL013-ENTRYPOINT-20260326-210305-914179`; BL-014 sanity pass `BL014-SANITY-20260326-210317-371524` (`22/22` checks); BL-010 pass `BL010-REPRO-20260326-205834` (`deterministic_match=true`, 3 replays); BL-011 pass `BL011-CTRL-20260326-205932` (5 scenarios, `status=pass`); active freshness suite `BL-FRESHNESS-SUITE-20260326-210015` (`6/8`, non-blocking evidence-alignment mismatch documented).
- affected_components: `07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json`, `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`, `07_implementation/implementation_notes/bl000_run_config/docs/bl000_run_config_state_log_2026-03-25.md`, `07_implementation/implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl004_profile/bl004_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl005_retrieval/bl005_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl006_scoring/bl006_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl007_playlist/bl007_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl008_transparency/bl008_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl009_observability/bl009_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl010_reproducibility/bl010_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl011_controllability/bl011_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl013_entrypoint/bl013_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl014_quality/bl014_state_log_2026-03-24.md`, `07_implementation/implementation_notes/CODEBASE_ISSUES_CURRENT.md`, `00_admin/unresolved_issues.md`, `00_admin/thesis_state.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Completes the intended 10-component scoring surface, hardens BL-010 for Windows environments, and establishes a fully documented v1f baseline with a forward-looking next-steps register.
- approval_record: Requested and confirmed by user in chat on 2026-03-26.

## C-181
- date: 2026-03-26
- proposed_by: Copilot
- status: accepted
- change_summary: Executed planned freshness re-alignment on the active v1f baseline by rerunning BL-010 reproducibility, BL-011 controllability, restoring live outputs via BL-013, and running the active BL-014 freshness suite; then synchronized implementation/admin governance docs to reflect the now-green freshness state.
- reason: C-180 intentionally documented a non-blocking post-restore freshness mismatch (`6/8`) as an operational caveat. The first planned next step was to realign BL-010/BL-011 snapshots to the current live v1f contract so the active freshness indicator returns to all-pass.
- evidence_basis: BL-010 pass `BL010-REPRO-20260326-212523` (`deterministic_match=true`); BL-011 pass `BL011-CTRL-20260326-212611` (`status=pass`); BL-013 restore pass `BL013-ENTRYPOINT-20260326-212711-234744`; BL-014 sanity pass `BL014-SANITY-20260326-212725-976781` (`22/22` checks); active freshness suite pass `BL-FRESHNESS-SUITE-20260326-212726` (`7/7` checks); BL-010/BL-011 freshness report pass `BL-FRESHNESS-20260326-212726` (`9/9` checks).
- affected_components: `07_implementation/implementation_notes/bl000_run_config/outputs/run_intent_latest.json`, `07_implementation/implementation_notes/bl000_run_config/outputs/run_effective_config_latest.json`, `07_implementation/implementation_notes/bl003_alignment/outputs/*`, `07_implementation/implementation_notes/bl004_profile/outputs/*`, `07_implementation/implementation_notes/bl005_retrieval/outputs/*`, `07_implementation/implementation_notes/bl006_scoring/outputs/*`, `07_implementation/implementation_notes/bl007_playlist/outputs/*`, `07_implementation/implementation_notes/bl008_transparency/outputs/*`, `07_implementation/implementation_notes/bl009_observability/outputs/*`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/*`, `07_implementation/implementation_notes/bl011_controllability/outputs/*`, `07_implementation/implementation_notes/bl013_entrypoint/outputs/bl013_orchestration_run_latest.json`, `07_implementation/implementation_notes/bl014_quality/outputs/*`, `07_implementation/implementation_notes/CODEBASE_ISSUES_CURRENT.md`, `00_admin/unresolved_issues.md`, `00_admin/thesis_state.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Removes the last active freshness caveat from the live v1f baseline and restores a clean all-green operations indicator without changing functional recommendation behavior.
- approval_record: Requested and confirmed by user in chat on 2026-03-26.

## C-182
- date: 2026-03-26
- proposed_by: Copilot
- status: accepted
- change_summary: Completed evidence audit for the canonical v1f baseline: resolved all 10 playlist track titles from DS-001 candidate CSV, documented BL-010/BL-011 config-snapshot candidate-count divergence, packaged dissertation claims by strength for Chapter 4/5 use, and updated all admin and state logs (thesis_state.md, current_implementation_information_sheet, unresolved_issues.md, change_log.md, experiment_log.md) to reflect v1f canonical evidence.
- reason: Admin logs and the implementation information sheet contained stale 2026-03-25 numbers (v1b/default candidate counts 72,463; old BL-013/BL-014 run IDs; 21/21 sanity checks; unresolved playlist track names). After the v1f migration the BL-020 section and current run snapshot required updating to preserve accuracy as chapter-writing reference material.
- evidence_basis: Resolved playlist from `07_implementation/implementation_notes/bl000_data_layer/outputs/ds001_working_candidate_dataset.csv`; canonical v1f run chain `BL013-ENTRYPOINT-20260326-215741-269303`, `BL007-ASSEMBLE-20260326-215757-053177`, `BL008-EXPLAIN-20260326-215758-211757`, `BL009-OBSERVE-20260326-215759-414232`, `BL014-SANITY-20260326-215800-844786` (`22/22`), `BL-FRESHNESS-SUITE-20260326-215801` (`7/7`), `BL010-REPRO-20260326-215557` (`deterministic_match=true`), `BL011-CTRL-20260326-215213` (`status=pass`).
- affected_components: `00_admin/thesis_state.md`, `00_admin/current_implementation_information_sheet_2026-03-25.md`, `00_admin/unresolved_issues.md`, `00_admin/change_log.md`, `07_implementation/experiment_log.md`
- impact_assessment: Medium-positive. Restores accuracy of primary chapter-writing reference documents and provides the first human-readable resolved playlist record in any admin governance file.
- approval_record: Requested and confirmed by user in chat on 2026-03-26.

## C-006

## C-002
- date: 2026-03-15
- proposed_by: AI + user
- status: accepted
- change_summary: Populate foundation/design placeholders and align writing/evaluation artifacts to the locked RQ terminology; add Chapter 4 execution matrix and test-pack scaffolding.
- reason: Preparation for final Chapter 2/3 drafting and implementation requires complete baseline documents plus direct design-to-evaluation traceability.
- evidence_basis: Locked thesis state and methodology flow in `00_admin/thesis_state.md`; existing architecture and QC mapping artifacts.
- affected_components: `02_foundation/problem_statement.md`, `02_foundation/objectives.md`, `02_foundation/assumptions.md`, `02_foundation/limitations.md`, `05_design/transparency_design.md`, `05_design/controllability_design.md`, `05_design/observability_design.md`, `00_admin/evaluation_plan.md`, `07_implementation/test_notes.md`, `08_writing/chapter2.md`, `08_writing/chapter2_plan.md`, `08_writing/chapter2_v2.md`, `08_writing/chapter2_v4.md`, `08_writing/chapter3.md`, `08_writing/chapter4.md`, `08_writing/chapter5.md`, `05_design/chapter3_information_sheet.md`, `09_quality_control/rq_alignment_checks.md`
- impact_assessment: Medium-positive. Improves consistency and execution readiness; no scope expansion beyond locked MVP.
- approval_record: Requested and confirmed by user in chat on 2026-03-15.

## C-003
- date: 2026-03-15
- proposed_by: AI + user
- status: accepted
- change_summary: Finalize Chapter 2 into a submission-ready draft with readability refinement, claim hardening, and full cited-paper verbatim coverage audit.
- reason: User requested end-to-end closure on Chapter 2 quality, including direct paper-wording verification and project log synchronization.
- evidence_basis: `08_writing/chatper2_final draft.md` revision history; generated audit artifact `09_quality_control/chapter2_verbatim_audit.md`; audit scripts in `09_quality_control/run_ch2_verbatim_audit.py` and `09_quality_control/summarize_ch2_verbatim_audit.py`.
- affected_components: `08_writing/chatper2_final draft.md`, `09_quality_control/chapter2_verbatim_audit.md`, `09_quality_control/citation_checks.md`, `09_quality_control/chapter_readiness_checks.md`, `09_quality_control/rq_alignment_checks.md`, `08_writing/chapter2_plan.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Chapter 2 now sits in target length range and automated verbatim audit reports zero weak-support citation claims for current chapter wording.
- approval_record: Requested and confirmed by user in chat on 2026-03-15.

## C-004
- date: 2026-03-15
- proposed_by: AI + user
- status: accepted
- change_summary: Create and iteratively harden `08_writing/chapter2_temp.md` as a non-frozen working variant until cited-claim audit reached `weak_support=0`.
- reason: User requested a separate temporary Chapter 2 file with repeated reruns/rechecks until weak-support claims were eliminated, while explicitly not freezing this temp variant.
- evidence_basis: `09_quality_control/chapter2_temp_verbatim_audit.md` final summary (`total_claim_checks=80`, `supported=4`, `partially_supported=76`, `weak_support=0`, `no_match=0`); updated audit tooling in `09_quality_control/run_ch2_verbatim_audit.py`.
- affected_components: `08_writing/chapter2_temp.md`, `09_quality_control/chapter2_temp_verbatim_audit.md`, `09_quality_control/run_ch2_verbatim_audit.py`, `09_quality_control/citation_checks.md`, `09_quality_control/chapter_readiness_checks.md`, `09_quality_control/rq_alignment_checks.md`, `08_writing/chapter2_plan.md`, `00_admin/change_log.md`
- impact_assessment: High-positive for evidence discipline. Produces a verified zero-weak temp draft while preserving non-freeze intent for this branch of Chapter 2 work.
- approval_record: Requested and confirmed by user in chat on 2026-03-15.

## C-005
- date: 2026-03-15
- proposed_by: AI + user
- status: accepted
- change_summary: Promote `08_writing/chapter2_temp2.md` to canonical Chapter 2 draft, create dated locked snapshot, and synchronize project control logs.
- reason: User requested project-wide readiness closure with a locked current Chapter 2 version and up-to-date governance trace.
- evidence_basis: User-approved iterative revisions in `08_writing/chapter2_temp2.md`, repository status review, and synchronized QC/admin updates completed in this run.
- affected_components: `08_writing/chapter2.md`, `08_writing/chapter2_temp2.md`, `08_writing/chapter2_draft_locked_2026-03-15.md`, `00_admin/change_log.md`, `09_quality_control/rq_alignment_checks.md`, `09_quality_control/chapter_readiness_checks.md`, `09_quality_control/citation_checks.md`, `08_writing/chapter2_plan.md`
- impact_assessment: High-positive. Establishes a single canonical Chapter 2 draft with locked snapshot and consistent project-control audit trail.
- approval_record: Requested and confirmed by user in chat on 2026-03-15.

## C-007
- date: 2026-03-15
- proposed_by: user + AI
- status: accepted
- change_summary: Lock Chapter 2 final draft by syncing `08_writing/chapter2_draft_locked_2026-03-15.md` to `08_writing/chapter2_draft_v11.md` and record finalization in project logs.
- reason: User requested commit-ready final draft lock for supervisor submission.
- evidence_basis: User-approved edits in `08_writing/chapter2_draft_v11.md`, citation verification pass, and dated lockfile sync.
- affected_components: `08_writing/chapter2_draft_v11.md`, `08_writing/chapter2_draft_locked_2026-03-15.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Establishes a dated frozen copy aligned with the approved final draft and improves submission traceability.
- approval_record: Requested and confirmed by user in chat on 2026-03-15.

## C-008
- date: 2026-03-13
- proposed_by: Timothy + AI
- status: accepted
- change_summary: Phase A implementation (BL-001, BL-002, BL-003) completed. Ingestion schema defined, deterministic CSV parser implemented and validated (TC-001), and ISRC-first track alignment with metadata fallback implemented and validated (TC-002). All Phase A artifacts subsequently deleted on 2026-03-19 to allow a clean restart of implementation.
- reason: Phase A build and test runs completed with passing results. User requested a full clean restart of implementation on 2026-03-19 before continuing to Phase B.
- evidence_basis: Experiment log `EXP-001` (ingestion parser, TC-001 pass) and `EXP-002` (alignment, TC-002 pass) in `07_implementation/experiment_log.md`; test results recorded in `07_implementation/test_notes.md`.
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/ingest_history_parser.py`, `07_implementation/implementation_notes/bl003_alignment/align_tracks.py`, `07_implementation/implementation_notes/run_outputs/` (8 output files), `07_implementation/implementation_notes/test_assets/sample_listening_history.csv`, `07_implementation/implementation_notes/test_assets/sample_music4all_candidates.csv`, `07_implementation/backlog.md`, `07_implementation/test_notes.md`
- impact_assessment: Neutral. Prior Phase A work is fully logged in experiment_log.md and test_notes.md. Clean state restores all backlog items to todo and removes code/output artifacts so implementation can restart.
- approval_record: Requested and confirmed by user in chat on 2026-03-19.

## C-028
- date: 2026-03-15
- proposed_by: user + AI
- status: accepted
- change_summary: Re-synchronize canonical `08_writing/chapter2.md` to `08_writing/chapter2_draft_v11.md`, rerun verbatim audit on v11, and update QC/governance logs to reflect current parser limitation.
- reason: Thesis currency check found that canonical Chapter 2 content diverged from the latest locked v11 draft and that the current verbatim audit parser did not extract claims from author-year citation style.
- evidence_basis: SHA256 hash parity between `08_writing/chapter2.md` and `08_writing/chapter2_draft_v11.md`; regenerated `09_quality_control/chapter2_verbatim_audit.md` on v11 (`total_claim_checks=0`) with parser-note confirmation.
- affected_components: `08_writing/chapter2.md`, `09_quality_control/chapter2_verbatim_audit.md`, `09_quality_control/chapter_readiness_checks.md`, `09_quality_control/citation_checks.md`, `09_quality_control/run_ch2_verbatim_audit.py`, `00_admin/unresolved_issues.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Restores single-source Chapter 2 consistency and improves audit honesty by surfacing the tooling-format mismatch as an explicit open issue.
- approval_record: Requested by user via thesis up-to-date check in chat on 2026-03-15.

## C-009
- date: 2026-03-15
- proposed_by: user + AI
- status: accepted
- change_summary: Extend Chapter 2 verbatim-audit parser to support author-year citations and rerun audit on `08_writing/chapter2_draft_v11.md`.
- reason: Close the parser-format blocker that produced `total_claim_checks=0` and restore meaningful claim-level citation verification for the active Chapter 2 style.
- evidence_basis: Updated `09_quality_control/run_ch2_verbatim_audit.py` (author-year citation extraction and source-index key mapping), regenerated `09_quality_control/chapter2_verbatim_audit.md` (`total_claim_checks=46`, `weak_support=24`).
- affected_components: `09_quality_control/run_ch2_verbatim_audit.py`, `09_quality_control/chapter2_verbatim_audit.md`, `09_quality_control/citation_checks.md`, `09_quality_control/chapter_readiness_checks.md`, `00_admin/unresolved_issues.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Removes tooling blind spot and clarifies that remaining Chapter 2 closure risk is now evidence-strength hardening, not parser failure.
- approval_record: Requested by user via thesis up-to-date continuation in chat on 2026-03-15.

## C-010
- date: 2026-03-16
- proposed_by: user + AI
- status: accepted
- change_summary: Define and approve a full revised thesis document structure plan covering front matter, Chapters 1-5, references, appendices, and chapter-level evaluation/validity expectations.
- reason: User requested a complete revised plan to lock document structure before continued chapter drafting.
- evidence_basis: User-provided draft structure plan and accepted revised full plan issued in chat on 2026-03-16.
- affected_components: `00_admin/change_log.md`
- impact_assessment: Medium-positive. Improves structural clarity, chapter boundary control, and evaluation defensibility for remaining writing work.
- approval_record: Requested and confirmed by user in chat on 2026-03-16.

## C-011
- date: 2026-03-17
- proposed_by: user + AI
- status: accepted
- change_summary: Update Abstract wording in `08_writing/thesis_master_draft_merged.md` with user-directed revisions: grammar/typo cleanup, terminology consistency to Music4All dataset, revised DSR phrasing, and replacement of the abstract findings placeholder with short draft bullet points describing what Chapter 4 results will report.
- reason: User requested iterative abstract refinement in-session, specifically asking for grammar fixes, retention of draft-like wording style, and a small bullet-point placeholder describing planned findings content.
- evidence_basis: In-session user prompts and accepted edits to the active abstract text in `08_writing/thesis_master_draft_merged.md`.
- affected_components: `08_writing/thesis_master_draft_merged.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Improves abstract readability and preserves scope-accurate contribution framing while keeping draft-stage placeholders explicit.
- approval_record: Requested and confirmed by user in chat on 2026-03-17.

## C-012
- date: 2026-03-17
- proposed_by: user + AI
- status: proposed
- change_summary: Replace the temporary abstract draft-bullets block with final 2 to 3 sentence Chapter 4 findings text once implementation and evaluation tables are populated.
- reason: Current abstract includes provisional bullet placeholders that are useful during drafting but should be replaced by final evidence-backed findings before submission.
- evidence_basis: Existing draft bullets in `08_writing/thesis_master_draft_merged.md` and the planned Chapter 4 results contract in `00_admin/evaluation_plan.md`.
- affected_components: `08_writing/thesis_master_draft_merged.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Preserves draft workflow now while creating an explicit cleanup checkpoint for submission readiness.
- approval_record: Proposed in-session on 2026-03-17 after user confirmation to log a pending follow-up.

## C-013
- date: 2026-03-19
- proposed_by: user + AI
- status: accepted
- change_summary: Register a thesis-wide work package for full PDF-based citation verification and literature evidence extraction, and track it as an active unresolved issue with concrete execution steps and due window.
- reason: User requested the todo to exist in the thesis environment itself (not chat-only) and requested logging of all required tracking actions.
- evidence_basis: Active Chapter 2 citation-risk findings, accessible local paper corpus in `10_resources/papers/`, and need to maximize literature-backed quality and defendability across the thesis.
- affected_components: `00_admin/unresolved_issues.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Improves governance traceability, closes planning ambiguity, and creates an auditable execution path for citation hardening and chapter-strength uplift.
- approval_record: Requested and confirmed by user in chat on 2026-03-19.

## C-014
- date: 2026-03-19
- proposed_by: user + AI
- status: accepted
- change_summary: Perform chat-closure repository hygiene: commit governance updates, citation-evidence extraction artifacts, and remaining thesis writing/document files in separate traceable commits; leave only one transient Office lock file uncommitted, then commit-all on user request.
- reason: User requested all chat work to be logged/tracked and committed before closing the chat.
- evidence_basis: Commits `71305fa`, `1fe4cfd`, and `c091c10`; extracted evidence files under `10_resources/papers/_extracted/` and `10_resources/papers/_extracted_claim_check/`; updated Chapter 2 master draft and thesis writing artifacts.
- affected_components: `00_admin/change_log.md`, `00_admin/unresolved_issues.md`, `08_writing/thesis_master_draft_merged.md`, `08_writing/chapter2_plan.md`, `08_writing/chapter3.md`, `08_writing/chapter3_v2.md`, `08_writing/chapter3_plan.md`, `08_writing/thesis_document_template_aligned.md`, `08_writing/Thesis.docx`, `10_resources/papers/_extracted/*`, `10_resources/papers/_extracted_claim_check/*`, `10_resources/papers/rp/files/578/*`, `01_requirements/university_documents/*`
- impact_assessment: High-positive. Preserves full auditability of this chat’s work and minimizes closure risk from untracked artifacts.
- approval_record: Explicitly requested by user in chat on 2026-03-19 ("commit everything...log everything...").
## C-015
- date: 2026-03-19
- proposed_by: AI + user
- status: accepted
- change_summary: Audit and repair all logging gaps before starting Phase B implementation. Filled in EXP-001 and EXP-002 in `experiment_log.md` for completed BL-001/002/003 work. Reconstructed missing body for C-001 in change log. Populated `dataset_registry.md` with Music4All entry, feature column schema, and access notes.
- reason: User requested confirmation that the environment automatically logs and tracks decisions. Audit found three concrete gaps: empty experiment log, empty C-001, and blank dataset registry. All fixed before implementation continues.
- evidence_basis: BL-001/002/003 done status in backlog; TC-001/TC-002 pass records in `test_notes.md`; repo memory setup note; D-001 dataset decision.
- affected_components: `07_implementation/experiment_log.md`, `00_admin/change_log.md`, `06_data_and_sources/dataset_registry.md`
- impact_assessment: Medium-positive. Closes logging debt before Phase B begins and ensures all completed work is traceable from this point forward.
- approval_record: Requested and confirmed by user in chat on 2026-03-19.

## C-016
- date: 2026-03-19
- proposed_by: AI + user
- status: accepted
- change_summary: Full session logging and environment hardening. Three work items completed: (1) environment health check confirming BL-001/002/003 done and both scripts (ingest_history_parser.py, align_tracks.py) running cleanly on Python 3.12.6; (2) logging gap audit and repair — EXP-001 and EXP-002 filled in experiment_log.md, C-001 stub reconstructed, dataset_registry.md populated with Music4All feature schema and access notes; (3) session-start checklist and implementation logging rules added to .github/copilot-instructions.md and 00_admin/operating_protocol.md (sections 13 and 14) so that any future "make sure everything is logged" prompt triggers an automatic 7-step audit before work begins.
- reason: User requested (a) confirmation that the environment logs and tracks everything automatically, (b) a foolproof rule so that a single prompt in any future chat triggers full logging enforcement.
- evidence_basis: Environment health check run outputs in 07_implementation/implementation_notes/run_outputs/; backlog and test_notes confirming BL-001/002/003 pass; committed state at 947e8d9.
- affected_components: .github/copilot-instructions.md, 00_admin/operating_protocol.md, 00_admin/change_log.md, 07_implementation/experiment_log.md, 06_data_and_sources/dataset_registry.md
- impact_assessment: High-positive. Environment is now self-auditing on session start. All completed implementation work has traceable experiment log entries. Dataset registry is populated. Protocol sections 13 and 14 enforce logging going forward.
- approval_record: Requested and confirmed by user in chat on 2026-03-19.

## C-017
- date: 2026-03-19
- proposed_by: user + AI
- status: accepted
- change_summary: Open a formal change review for replacing the current Music4All / Music4All-Onion candidate corpus with an integrated `Million Song Dataset subset + Last.fm Tag Dataset + MusicBrainz mapping` dataset, and update implementation planning so corpus comparison happens before more canonical-layer work is committed.
- reason: User is actively considering a dataset switch and requested that everything requiring traceability be logged and planned before further implementation continues.
- evidence_basis: Current accepted dataset choice and Onion fallback path in `00_admin/decision_log.md` (`D-001`, `D-006`, `D-007`); user-provided dataset construction sheet dated 2026-03-19; current implementation dependency on corpus choice in `07_implementation/backlog.md`.
- affected_components: `00_admin/decision_log.md`, `00_admin/unresolved_issues.md`, `06_data_and_sources/dataset_registry.md`, `07_implementation/backlog.md`, `07_implementation/implementation_plan.md`, `07_implementation/experiment_log.md`
- impact_assessment: Medium-to-high. Positive if it avoids continued dependence on blocked base metadata and yields a simpler documented corpus; negative if it causes late-stage scope drift, weaker cross-source matching, or rework in objectives/writing. Thesis state is intentionally not changed until the review is resolved.
- approval_record: Requested in chat on 2026-03-19 after user asked for full logging and planning for a possible dataset change.

## C-018
- date: 2026-03-19
- proposed_by: user + AI
- status: accepted
- change_summary: Log that base Music4All is not usable in the current environment, record that the original base-plus-Onion combined plan is redundant for MVP execution, complete BL-018 corpus feasibility review, and keep Music4All-Onion as the active corpus while rejecting the MSD-subset switch.
- reason: User explicitly asked to log the unusable base-Music4All path and to execute the corpus-comparison review immediately.
- evidence_basis: `07_implementation/implementation_notes/bl000_data_layer/candidate_corpus_feasibility_review_2026-03-19.md`; `07_implementation/experiment_log.md` EXP-DA-001; `06_data_and_sources/dataset_registry.md`; `00_admin/decision_log.md` D-008.
- affected_components: `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/unresolved_issues.md`, `06_data_and_sources/dataset_registry.md`, `07_implementation/backlog.md`, `07_implementation/implementation_plan.md`, `07_implementation/experiment_log.md`, `07_implementation/implementation_notes/bl000_data_layer/candidate_corpus_feasibility_review_2026-03-19.md`
- impact_assessment: High-positive. Removes corpus-planning ambiguity, avoids avoidable rework, and clarifies that the blocked dependency is base Music4All rather than the Onion corpus itself.
- approval_record: Requested by user in chat on 2026-03-19 ("log that i cant use music4all base so music4all onion might be reduntant. then do no1.")

## C-019
- date: 2026-03-19
- proposed_by: user + AI
- status: accepted
- change_summary: Save the MSD-based dataset construction sheet as a future-reference artifact, defer that data-engineering path to later work, and reaffirm Music4All-Onion as the current implementation path.
- reason: User wants to postpone alternative corpus engineering for now, keep the idea tracked for future use, and continue with Onion-only implementation.
- evidence_basis: `06_data_and_sources/ds_002_msd_information_sheet.md`; `00_admin/decision_log.md` D-009; `06_data_and_sources/dataset_registry.md` DS-002 notes.
- affected_components: `06_data_and_sources/ds_002_msd_information_sheet.md`, `06_data_and_sources/dataset_registry.md`, `07_implementation/backlog.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Preserves future design work without destabilizing the current MVP path.
- approval_record: Requested by user in chat on 2026-03-19.

## C-020
- date: 2026-03-19
- proposed_by: user + AI
- status: accepted
- change_summary: Perform session-closure repository hygiene by committing the governance, planning, and evidence artifacts from this dataset-decision session while keeping raw local dataset payloads out of version control.
- reason: User requested that everything needing logging be logged and that commit-worthy work be committed before starting a new chat.
- evidence_basis: Current working-tree audit; `00_admin/decision_log.md` (`D-008`, `D-009`); `07_implementation/implementation_notes/bl000_data_layer/candidate_corpus_feasibility_review_2026-03-19.md`; `.gitignore` dataset exclusion rule.
- affected_components: `.gitignore`, `00_admin/change_log.md`, `00_admin/decision_log.md`, `00_admin/unresolved_issues.md`, `06_data_and_sources/dataset_registry.md`, `06_data_and_sources/ds_002_msd_information_sheet.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/implementation_plan.md`, `07_implementation/implementation_notes/bl000_data_layer/candidate_corpus_feasibility_review_2026-03-19.md`
- impact_assessment: High-positive. Preserves an auditable session snapshot without polluting the repository with large local dataset binaries.
- approval_record: Requested by user in chat on 2026-03-19.

## C-021
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Complete BL-009 observability logging for the bootstrap pipeline by implementing a deterministic run-level audit builder, generating the canonical observability artifacts, and synchronizing the implementation and governance records.
- reason: User requested that BL-009 be planned, implemented, and fully logged end to end.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-011`); `07_implementation/test_notes.md` (`TC-OBS-001`); generated artifacts `07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_observability_log.json` and `07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_index.csv`; backlog completion note for `BL-009`.
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `06_data_and_sources/schema_notes.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`, `07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_observability_log.json`, `07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_index.csv`
- impact_assessment: High-positive. Closes the observability evidence gap for the locked MVP, makes the bootstrap run chain auditable across BL-017 to BL-008, and prepares the ground for BL-010 reproducibility testing.
- approval_record: Requested by user in chat on 2026-03-21.

## C-022
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Complete BL-010 reproducibility testing by implementing a three-replay bootstrap runner, adding stable replay fingerprints for timestamped downstream artifacts, hardening BL-004 to BL-009 run-id precision, generating archived replay evidence, and synchronizing project governance records.
- reason: User requested that BL-010 be planned, implemented, and fully logged end to end.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-012`); `07_implementation/test_notes.md` (`TC-REPRO-001`); generated artifacts `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_config_snapshot.json`, `bl010_reproducibility_report.json`, `bl010_reproducibility_run_matrix.csv`, and archived replay directories `replay_01/` to `replay_03/`.
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`, `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`, `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`, `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`, `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`, `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/`
- impact_assessment: High-positive. Provides the locked MVP reproducibility evidence, removes rapid-replay run-id collisions, and establishes a reusable baseline for BL-011 controllability testing.
- approval_record: Requested by user in chat on 2026-03-21.

## C-023
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Retrospectively synchronize governance records for BL-004 by logging the completed deterministic preference-profile stage and its evidence artifacts in the change log.
- reason: A logging audit found that BL-004 had experiment and test evidence but no explicit `C-###` entry, which violates the implementation logging rule that every completed backlog item must have change-log coverage.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-006`); `07_implementation/test_notes.md` (`TC-PROFILE-001`); generated artifacts `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json`, `bl004_profile_summary.json`, and `bl004_seed_trace.csv`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`, `07_implementation/implementation_notes/bl004_profile/outputs/`
- impact_assessment: Medium-positive. Restores protocol-compliant governance traceability for the first core bootstrap pipeline stage without changing the underlying implementation outputs.
- approval_record: Logged during user-requested full logging audit on 2026-03-21.

## C-024
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Retrospectively synchronize governance records for BL-005 by logging the completed candidate-retrieval and filtering stage and its evidence artifacts in the change log.
- reason: A logging audit found that BL-005 had experiment and test evidence but no explicit `C-###` entry, which violates the implementation logging rule that every completed backlog item must have change-log coverage.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-007`); `07_implementation/test_notes.md` (`TC-CAND-001`); generated artifacts `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_filtered_candidates.csv`, `bl005_candidate_decisions.csv`, and `bl005_candidate_diagnostics.json`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`, `07_implementation/implementation_notes/bl005_retrieval/outputs/`
- impact_assessment: Medium-positive. Restores protocol-compliant governance traceability for the retrieval/filtering stage and makes the BL-005 evidence chain complete.
- approval_record: Logged during user-requested full logging audit on 2026-03-21.

## C-025
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Retrospectively synchronize governance records for BL-006 by logging the completed deterministic scoring stage and its evidence artifacts in the change log.
- reason: A logging audit found that BL-006 had experiment and test evidence but no explicit `C-###` entry, which violates the implementation logging rule that every completed backlog item must have change-log coverage.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-008`); `07_implementation/test_notes.md` (`TC-SCORE-001`); generated artifacts `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv` and `bl006_score_summary.json`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl006_scoring/outputs/`
- impact_assessment: Medium-positive. Restores protocol-compliant governance traceability for the ranking stage and tightens the Chapter 4 evidence chain.
- approval_record: Logged during user-requested full logging audit on 2026-03-21.

## C-026
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Retrospectively synchronize governance records for BL-007 by logging the completed rule-based playlist-assembly stage and its evidence artifacts in the change log.
- reason: A logging audit found that BL-007 had experiment and test evidence but no explicit `C-###` entry, which violates the implementation logging rule that every completed backlog item must have change-log coverage.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-009`); `07_implementation/test_notes.md` (`TC-PLAYLIST-001`); generated artifacts `07_implementation/implementation_notes/bl007_playlist/outputs/bl007_playlist.json`, `bl007_assembly_trace.csv`, and `bl007_assembly_report.json`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`, `07_implementation/implementation_notes/bl007_playlist/outputs/`
- impact_assessment: Medium-positive. Restores protocol-compliant governance traceability for the assembly stage and completes the audit trail from ranking to playlist output.
- approval_record: Logged during user-requested full logging audit on 2026-03-21.

## C-027
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Retrospectively synchronize governance records for BL-008 by logging the completed transparency-output stage and its evidence artifacts in the change log.
- reason: A logging audit found that BL-008 had experiment and test evidence but no explicit `C-###` entry, which violates the implementation logging rule that every completed backlog item must have change-log coverage.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-010`); `07_implementation/test_notes.md` (`TC-EXPLAIN-001`); generated artifacts `07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_payloads.json` and `bl008_explanation_summary.json`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`, `07_implementation/implementation_notes/bl008_transparency/outputs/`
- impact_assessment: Medium-positive. Restores protocol-compliant governance traceability for the transparency stage and closes the pre-observability logging gap.
- approval_record: Logged during user-requested full logging audit on 2026-03-21.

## C-029
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Repair historical change-log governance by resolving the duplicate `C-008` identifier, renumbering the later chapter-audit entry to `C-028`, and recording the retrospective BL-004 to BL-008 coverage audit.
- reason: A follow-up logging audit found that the change log still contained a duplicate `C-008`, which violated the unique sequential identifier rule in the operating protocol and left the governance repair itself undocumented.
- evidence_basis: `00_admin/operating_protocol.md`; `00_admin/change_log.md`; retained historical content for the 2026-03-15 chapter-audit entry; new retrospective coverage entries `C-023` to `C-027`.
- affected_components: `00_admin/change_log.md`
- impact_assessment: Medium-positive. Removes a durable governance inconsistency, preserves the historical content of the affected chapter-audit entry, and makes the implementation logging audit itself traceable.
- approval_record: Requested by user in chat on 2026-03-21.

## C-030
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Start BL-011 controllability evaluation work by opening the planned experiment record, moving the backlog item to in-progress, and preparing a dedicated parameter-sensitivity runner anchored to the BL-010 baseline.
- reason: User requested that BL-011 be planned, implemented, and fully logged end to end.
- evidence_basis: `00_admin/evaluation_plan.md` (`EP-CTRL-001`, `EP-CTRL-002`, `EP-CTRL-003`); `05_design/controllability_design.md`; `07_implementation/experiment_log.md` (`EXP-013` planned state); `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_config_snapshot.json`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/implementation_notes/bl011_controllability/`
- impact_assessment: Medium-positive. Establishes a protocol-compliant start state for BL-011 and ties the next evaluation step directly to the verified BL-010 baseline.
- approval_record: Requested by user in chat on 2026-03-21.

## C-031
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Complete BL-011 controllability testing by implementing a dedicated OFAT scenario runner, generating archived baseline and variant outputs, fixing one volatile-hash normalization defect in the repeat check, and synchronizing the implementation and governance records.
- reason: User requested that BL-011 be planned, implemented, and fully logged end to end.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-013`); `07_implementation/test_notes.md` (`TC-005`, `TC-006`, `TC-007`); generated artifacts `07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_config_snapshot.json`, `bl011_controllability_report.json`, `bl011_controllability_run_matrix.csv`, and archived scenario directories under `07_implementation/implementation_notes/bl011_controllability/outputs/scenarios/`.
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/bl011_controllability/run_bl011_controllability_check.py`, `07_implementation/implementation_notes/bl011_controllability/outputs/`
- impact_assessment: High-positive. Provides the locked MVP controllability evidence, demonstrates deterministic OFAT sensitivity behavior, and establishes a reusable evaluation harness for later Chapter 4 evidence extraction.
- approval_record: Requested by user in chat on 2026-03-21.

## C-032
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Repair BL-011 governance chronology by moving `D-012` to the end of `00_admin/decision_log.md` so decision IDs remain in chronological order after the latest implementation decision.
- reason: A post-implementation logging audit found `D-012` inserted near the top of the file due to patch anchor ambiguity; the content was correct but file order violated the expected decision-log chronology.
- evidence_basis: `00_admin/decision_log.md` final ordering (`D-011` followed by `D-012`); `00_admin/operating_protocol.md` decision-log governance expectations.
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`
- impact_assessment: Medium-positive. Restores chronological traceability for the latest design decision and prevents ambiguity when citing decision sequence in later writing.
- approval_record: Requested by user in chat on 2026-03-21.

## C-033
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Complete BL-012 by documenting evidence-grounded limitations and observed failure modes from BL-010 and BL-011, synchronizing the foundation and Chapter 5 interpretation boundaries, and updating implementation/governance logs.
- reason: User requested BL-012 to be planned, implemented, and fully logged end to end.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-014`); `07_implementation/test_notes.md` (`TC-LIMIT-001`); updated limitation synthesis in `02_foundation/limitations.md`; updated interpretation and future-work sections in `08_writing/chapter5.md`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `02_foundation/limitations.md`, `08_writing/chapter5.md`
- impact_assessment: High-positive. Converts evaluation outcomes into explicit validity boundaries, reduces interpretation ambiguity in Chapter 5, and closes the final P0 documentation item (`BL-012`) with full traceability.
- approval_record: Requested by user in chat on 2026-03-21.

## C-034
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Execute an explicit post-BL-012 "log everything" governance audit and confirm that BL-012 traceability is synchronized across backlog, experiment, test, and administrative logs.
- reason: User requested "log everything" immediately after BL-012 completion, requiring a verifiable checkpoint that no required governance surface was left out.
- evidence_basis: `07_implementation/backlog.md` (`BL-012` status and Done note); `07_implementation/experiment_log.md` (`EXP-014`); `07_implementation/test_notes.md` (`TC-LIMIT-001`); `00_admin/change_log.md` (`C-033`); protocol requirements in `00_admin/operating_protocol.md`.
- affected_components: `00_admin/change_log.md`
- impact_assessment: Medium-positive. Adds an auditable closure record for the logging-completeness request and reduces risk of untracked end-of-cycle governance gaps.
- approval_record: Requested by user in chat on 2026-03-21 ("log everything").

## C-035
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Start BL-013 by moving it to in-progress, creating a planned experiment entry, and defining an orchestration decision for a lightweight pipeline entrypoint that wraps BL-004 through BL-009.
- reason: User requested to plan BL-013, implement it, and log everything end to end.
- evidence_basis: `07_implementation/backlog.md` (`BL-013` in-progress); `07_implementation/experiment_log.md` (`EXP-015` planned); `00_admin/decision_log.md` (`D-013`).
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`
- impact_assessment: Medium-positive. Establishes protocol-compliant BL-013 kickoff traceability before implementation changes begin.
- approval_record: Requested by user in chat on 2026-03-21.

## C-036
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Complete BL-013 by implementing a lightweight orchestration entrypoint and run-command documentation, executing repeat runs, and synchronizing experiment, test, and backlog closure logs.
- reason: User requested BL-013 to be planned, implemented, and fully logged end to end.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-015`); `07_implementation/test_notes.md` (`TC-CLI-001`); orchestration artifacts under `07_implementation/implementation_notes/bl013_entrypoint/`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`, `07_implementation/implementation_notes/bl013_entrypoint/bl013_run_command.md`, `07_implementation/implementation_notes/bl013_entrypoint/outputs/`
- impact_assessment: High-positive. Adds a repeatable single-command pipeline runner with auditable execution summaries and reduces rerun friction for future evaluation and writing evidence refresh.
- approval_record: Requested by user in chat on 2026-03-21.

## C-037
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Repair BL-013 governance chronology by moving `D-013` to the end of `00_admin/decision_log.md` so decision IDs remain in chronological order.
- reason: Post-implementation verification found `D-013` had been inserted near the top of the decision log due to patch anchoring; content was correct but ordering violated log chronology.
- evidence_basis: `00_admin/decision_log.md` final ordering (`D-011`, `D-012`, `D-013`); `00_admin/operating_protocol.md` decision-log governance expectations.
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`
- impact_assessment: Medium-positive. Restores decision-sequence traceability and prevents citation ambiguity when referring to recent implementation decisions.
- approval_record: User requested full logging coverage on 2026-03-21.

## C-038
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Execute an explicit post-BL-013 "log everything" governance audit and confirm that BL-013 traceability is synchronized across backlog, experiment, test, and administrative logs.
- reason: User requested "log everything" after BL-013 closure, requiring a verifiable checkpoint that no required governance surface was left out.
- evidence_basis: `07_implementation/backlog.md` (`BL-013` status and Done note); `07_implementation/experiment_log.md` (`EXP-015`); `07_implementation/test_notes.md` (`TC-CLI-001`); `00_admin/change_log.md` (`C-035`, `C-036`, `C-037`); `00_admin/decision_log.md` (`D-013`); protocol requirements in `00_admin/operating_protocol.md`.
- affected_components: `00_admin/change_log.md`
- impact_assessment: Medium-positive. Adds an auditable closure record for the latest logging-completeness request and reduces risk of untracked governance gaps before starting BL-014.
- approval_record: Requested by user in chat on 2026-03-21 ("log everything").

## C-039
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Start BL-019 dataset-build planning by activating the backlog item, creating a planned experiment entry, defining the planning decision, and updating implementation-plan guidance for deterministic Onion dataset refresh.
- reason: User requested planning for BL-019 to build the dataset.
- evidence_basis: `07_implementation/backlog.md` (`BL-019` in-progress plan); `07_implementation/experiment_log.md` (`EXP-016` planned); `00_admin/decision_log.md` (`D-014`); `07_implementation/implementation_plan.md` BL-019 planning addendum.
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/implementation_plan.md`
- impact_assessment: Medium-positive. Converts BL-019 from a deferred placeholder into an execution-ready planning track with explicit artifacts, quality gates, and repeatability checks.
- approval_record: Requested by user in chat on 2026-03-21.

## C-040
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Update the active BL-019 plan to use the DS-002 dataset strategy (`MSD subset + Last.fm tags + MusicBrainz mapping`) and synchronize backlog, implementation-plan, experiment-plan, and decision-log records.
- reason: User requested: "update the plan so we use this dataset strategy."
- evidence_basis: `06_data_and_sources/ds_002_msd_information_sheet.md`; updated `07_implementation/backlog.md`; updated `07_implementation/implementation_plan.md`; updated `07_implementation/experiment_log.md` (`EXP-016`); `00_admin/decision_log.md` (`D-015`).
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `07_implementation/backlog.md`, `07_implementation/implementation_plan.md`, `07_implementation/experiment_log.md`, `06_data_and_sources/dataset_registry.md`
- impact_assessment: Medium-positive. Aligns active implementation planning with the selected dataset path, reduces corpus-strategy ambiguity, and preserves traceable governance continuity.
- approval_record: Requested by user in chat on 2026-03-21.

## C-041
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Execute an explicit post-DS-002 "log everything" governance audit and record synchronization status across backlog, experiment, decision, change, dataset-registry, and unresolved-issues files.
- reason: User requested "log everything" after the DS-002 planning switch.
- evidence_basis: `07_implementation/backlog.md` (`BL-019` DS-002 in-progress scope); `07_implementation/experiment_log.md` (`EXP-016` planned DS-002 workflow); `00_admin/decision_log.md` (`D-015`); `00_admin/change_log.md` (`C-040`); `06_data_and_sources/dataset_registry.md` (DS-002 active status); `00_admin/unresolved_issues.md` (state mismatch tracking update).
- affected_components: `00_admin/change_log.md`, `00_admin/unresolved_issues.md`
- impact_assessment: Medium-positive. Adds a verifiable logging-completeness checkpoint and surfaces remaining governance mismatches instead of leaving them implicit.
- approval_record: Requested by user in chat on 2026-03-21 ("log everything").

## C-042
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Synchronize official thesis-state wording with DS-002 active planning scope, close the corresponding unresolved issue, and align the BL-018 historical note to avoid active-scope ambiguity.
- reason: User requested to update the remaining mismatch and log any required governance changes.
- evidence_basis: updated `00_admin/thesis_state.md` (DS-002 active scope language); updated `00_admin/unresolved_issues.md` (`UI-006` moved to resolved); updated `07_implementation/backlog.md` (`BL-018` historical-note clarification); prior strategy decision in `00_admin/decision_log.md` (`D-015`).
- affected_components: `00_admin/change_log.md`, `00_admin/thesis_state.md`, `00_admin/unresolved_issues.md`, `07_implementation/backlog.md`
- impact_assessment: Medium-positive. Removes the last known DS-002 governance mismatch, keeps historical corpus decisions explicit, and improves consistency for Chapter 3/5 traceability.
- approval_record: Requested by user in chat on 2026-03-21.

## C-043
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Log the verified DS-002 source inspection results, correct stale ISRC-first and MusicBrainz-track-level assumptions, and synchronize the active BL-019 planning documents to the actually available local data.
- reason: User requested a full logging pass after local dataset inspection, Spotify matching review, and HDF5 enablement work for DS-002.
- evidence_basis: inspected `06_data_and_sources/track_metadata.db`; inspected `06_data_and_sources/millionsongsubset.tar.gz`; inspected `06_data_and_sources/lastfm_subset.zip`; inspected `06_data_and_sources/unique_tracks.txt`; inspected `06_data_and_sources/unique_artists.txt`; Spotify Web API `Get Track` reference review; accepted design clarification in `00_admin/decision_log.md` (`D-016`).
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `06_data_and_sources/dataset_registry.md`, `06_data_and_sources/ds_002_msd_information_sheet.md`, `06_data_and_sources/schema_notes.md`, `07_implementation/experiment_log.md`
- impact_assessment: High-positive. Replaces idealized DS-002 assumptions with evidence-backed source facts, preserves traceability for the active corpus path, and reduces the risk of implementing BL-019 against an incorrect matching model.
- approval_record: Requested by user in chat on 2026-03-21 ("log everything till now").

## C-044
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Complete BL-019 — build and verify the DS-002 intersection dataset, run two deterministic builds, log results to EXP-016 and TC-DATASET-001, mark BL-019 done in backlog, and update all governance files to reflect completed status.
- reason: User requested full logging pass to close BL-019 before moving on to data ingestion.
- evidence_basis: `07_implementation/experiment_log.md` (EXP-016, status pass); `07_implementation/test_notes.md` (TC-DATASET-001, status pass); `07_implementation/implementation_notes/bl000_data_layer/outputs/bl019_ds002_integrated_candidate_dataset.csv` (SHA256 `b9c729a2...`); `07_implementation/implementation_notes/bl000_data_layer/outputs/bl019_ds002_integration_report.json` (9330 rows, elapsed 26.984 s, all quality gates pass); two-run hash match confirmed.
- affected_components: `00_admin/change_log.md`, `00_admin/thesis_state.md`, `06_data_and_sources/dataset_registry.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`
- impact_assessment: High-positive. DS-002 candidate corpus is now a verified, reproducible artefact ready for downstream ingestion and alignment stages.
- approval_record: Requested by user in chat on 2026-03-21.

## C-045
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Execute pre-chat-switch repository closure: perform system check, split and push implementation/docs/data commits, upload DS-002 source payload files via Git LFS, and harden `.gitignore` with local BL-019 temporary probe patterns.
- reason: User requested a full closure pass before switching to a new chat, including committing pending work and confirming what is and is not uploaded.
- evidence_basis: branch `setup/initial-work` head commit `095621d`; preceding split commits `0b41b40`, `c82955d`, `b29423e`; remote head parity confirmed for `origin/setup/initial-work`; LFS objects present for `06_data_and_sources/*.zip`, `06_data_and_sources/*.tar.gz`, and `06_data_and_sources/*.db`.
- affected_components: `00_admin/change_log.md`, `.gitignore`, `06_data_and_sources/MSongsDB-master.zip`, `06_data_and_sources/lastfm_subset.zip`, `06_data_and_sources/millionsongsubset.tar.gz`, `06_data_and_sources/track_metadata.db`, `06_data_and_sources/unique_artists.txt`, `06_data_and_sources/unique_tracks.txt`, `07_implementation/implementation_notes/**`
- impact_assessment: High-positive. Produces a clean handoff state with uploaded source/data artefacts, reproducible commit history in logical parts, and reduced future repository noise from temporary probe artifacts.
- approval_record: Requested by user in chat on 2026-03-21 ("commit those, and put in my git ignore anytthing else", "log everything before i switch to a new chat").

## C-046
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Implement a Spotify Web API maximum-ingestion exporter for BL-002 (top tracks, saved tracks, playlists, playlist items) with OAuth authorization-code flow, pagination, retry/rate-limit handling, flattened exports, request logs, and run-summary hashing; synchronize backlog/test/experiment/decision records accordingly.
- reason: User requested: "build a script that gets the maximum from my spotify (top tracks, saved tracks, playlists) ... and implement and log everything."
- evidence_basis: `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`; `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/spotify_api_ingestion_runbook.md`; `07_implementation/implementation_notes/bl001_bl002_ingestion/configs/templates/spotify_env_template.ps1`; `07_implementation/experiment_log.md` (`EXP-018`); `07_implementation/test_notes.md` (`TC-SPOTIFY-API-001`).
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`, `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/spotify_api_ingestion_runbook.md`, `07_implementation/implementation_notes/bl001_bl002_ingestion/configs/templates/spotify_env_template.ps1`, `.gitignore`
- impact_assessment: High-positive. Establishes a practical, auditable Spotify API ingestion path with broader coverage than sample CSV parsing alone, while preserving deterministic artifact logging and credential hygiene controls.
- approval_record: Requested by user in chat on 2026-03-21.

## C-047
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Harden Spotify API ingestion against provider throttling by adding endpoint-specific batch controls, proactive request-rate throttling, visible 429 telemetry, and fail-fast cooldown handling that writes a structured blocker artifact (`spotify_rate_limit_block.json`).
- reason: Live authenticated runs repeatedly hit long Spotify `Retry-After` cooldown windows and user requested robust rate-limit and batching behavior.
- evidence_basis: `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py` updates (`--batch-size-*`, `--batch-pause-ms`, `--min-request-interval-ms`, `--max-requests-per-minute`, `--max-retry-after-seconds`); blocked run artifact `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_rate_limit_block.json`; `07_implementation/experiment_log.md` (`EXP-019`); `07_implementation/test_notes.md` (`TC-SPOTIFY-API-001`).
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `00_admin/unresolved_issues.md`, `06_data_and_sources/dataset_registry.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`, `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/spotify_api_ingestion_runbook.md`
- impact_assessment: Medium-positive. Improves operational resilience and observability under external API throttling, though full export remains temporarily blocked by provider cooldown.
- approval_record: Requested by user in chat on 2026-03-21.

## C-048
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Create collaborator handoff continuity package so a friend can use chat with the same workflow, including a start playbook, reusable prompt shortcuts, and synchronized backlog/protocol updates.
- reason: User requested that project handoff preserves the same chat behavior and that all relevant governance files are up to date.
- evidence_basis: `00_admin/handoff_friend_chat_playbook.md`; `.github/prompts/session-start-check.prompt.md`; `.github/prompts/log-everything.prompt.md`; `.github/copilot-instructions.md` collaborator mode section; updated handoff snapshot in `07_implementation/backlog.md`; protocol update in `00_admin/operating_protocol.md` section 15.
- affected_components: `00_admin/change_log.md`, `00_admin/handoff_friend_chat_playbook.md`, `.github/copilot-instructions.md`, `.github/prompts/session-start-check.prompt.md`, `.github/prompts/log-everything.prompt.md`, `07_implementation/backlog.md`, `00_admin/operating_protocol.md`
- impact_assessment: High-positive. Reduces onboarding ambiguity, preserves existing logging discipline across collaborators, and makes start/end chat procedures repeatable.
- approval_record: Requested by user in chat on 2026-03-21.

## C-049
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Harden collaborator automation so session-start checks and session-close logging run by default without requiring manual trigger prompts; add root `AGENTS.md` fallback instructions for cross-environment consistency.
- reason: User requested that handoff behavior be automatic for collaborator sessions in the same way as the original workflow.
- evidence_basis: updated `.github/copilot-instructions.md` (automatic collaborator start/close behavior), updated `00_admin/handoff_friend_chat_playbook.md` (automatic start/close wording), and new root `AGENTS.md` with mirrored automatic checklist rules.
- affected_components: `00_admin/change_log.md`, `.github/copilot-instructions.md`, `00_admin/handoff_friend_chat_playbook.md`, `AGENTS.md`
- impact_assessment: High-positive. Reduces reliance on collaborator memory/prompts and improves instruction reliability across VS Code chat environments.
- approval_record: Requested by user in chat on 2026-03-21.

## C-050
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Execute AGENTS session-start takeover checklist and confirm governance consistency before further implementation work.
- reason: User requested "do no1" (session-start checklist) and asked to keep all updates logged while deferring Spotify unblock work.
- evidence_basis: Reviewed `00_admin/thesis_state.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `00_admin/change_log.md`, `00_admin/decision_log.md`, and `00_admin/unresolved_issues.md`; verified local branch/remote parity at `setup/initial-work` commit `93b7a4f97e7713a0ffab78e8f6839420be275f95`.
- affected_components: `00_admin/change_log.md`
- impact_assessment: Medium-positive. Confirms handoff continuity and reduces risk of starting implementation from stale or inconsistent project control state.
- approval_record: Requested by user in chat on 2026-03-21.

## C-051
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Log that two literature resource-pack PDFs were not able to be extracted and mark them as explicit missing-input risk for citation-hardening work.
- reason: User requested that the two specific files be logged as not extractable.
- evidence_basis: Working tree paths flagged in current repository state:
	- `10_resources/previous_drafts/lit_review_resource_pack/files/381/Adomavicius and Tuzhilin - 2005 - Toward the next generation of recommender systems a survey of the state-of-the-art and possible ext.pdf`
	- `10_resources/previous_drafts/lit_review_resource_pack/files/391/Tintarev and Masthoff - 2012 - Evaluating the effectiveness of explanations for recommender systems Methodological issues and empi.pdf`
- affected_components: `00_admin/change_log.md`, `00_admin/unresolved_issues.md`
- impact_assessment: Medium-negative near term for literature evidence completeness; positive for governance transparency because the extraction gap is now explicit and trackable.
- approval_record: Requested by user in chat on 2026-03-21.

## C-052
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Prepare the new machine for thesis implementation by installing the repo's required Python packages and adding a minimal `requirements.txt` for repeatable setup.
- reason: User installed Python on the new system and requested installation of anything else needed plus logging of the setup work.
- evidence_basis: Workspace Python environment configured successfully (`system`, Python `3.14.3`); installed packages verified in environment details: `h5py==3.16.0`, `pypdf==6.9.1`, `rapidfuzz==3.14.3`; dependency declarations recorded in `requirements.txt`.
- affected_components: `00_admin/change_log.md`, `requirements.txt`
- impact_assessment: High-positive. Brings the new machine to a workable baseline for current implementation and quality-control scripts while reducing future setup ambiguity.
- approval_record: Requested by user in chat on 2026-03-21.

## C-053
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Create a repo-local `.venv`, install pinned dependencies into it, and switch the workspace interpreter from system Python to the local virtual environment.
- reason: User requested setup option no. 1 so the project runs in an isolated environment on the new machine.
- evidence_basis: Local environment created at `.venv/`; package install in `.venv` completed for `h5py==3.16.0`, `pypdf==6.9.1`, and `rapidfuzz==3.14.3`; direct import verification returned `venv imports ok`; workspace Python environment updated to `c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\.venv\Scripts\python.exe`.
- affected_components: `00_admin/change_log.md`, `.venv/`
- impact_assessment: High-positive. Improves dependency isolation, reduces environment drift risk, and makes subsequent thesis implementation work more reproducible on this machine.
- approval_record: Requested by user in chat on 2026-03-21.

## C-054
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Add a one-command Windows bootstrap script and a short runbook for repeatable Python environment setup on future machines.
- reason: User selected setup option no. 2 to make future machine setup simpler and less error-prone.
- evidence_basis: New tracked bootstrap script `07_implementation/setup/bootstrap_python_environment.ps1`; Windows-friendly wrapper `07_implementation/setup/bootstrap_python_environment.cmd`; new runbook `07_implementation/setup/python_environment_setup.md`; setup remains pinned to `requirements.txt`.
- affected_components: `00_admin/change_log.md`, `07_implementation/setup/bootstrap_python_environment.ps1`, `07_implementation/setup/bootstrap_python_environment.cmd`, `07_implementation/setup/python_environment_setup.md`
- impact_assessment: High-positive. Reduces onboarding/setup ambiguity and gives future collaborators a single repeatable environment-setup command.
- approval_record: Requested by user in chat on 2026-03-21.

## C-055
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Reorganize Python environment setup assets into a dedicated `07_implementation/setup/` area instead of keeping them under `implementation_notes/bl013_entrypoint`.
- reason: User approved the cleanup pass to keep environment/bootstrap assets in a clearer implementation-level setup location.
- evidence_basis: Setup files relocated to `07_implementation/setup/` and path references updated to the new location.
- affected_components: `00_admin/change_log.md`, `07_implementation/setup/bootstrap_python_environment.ps1`, `07_implementation/setup/bootstrap_python_environment.cmd`, `07_implementation/setup/python_environment_setup.md`
- impact_assessment: Medium-positive. Improves project structure clarity by separating environment/bootstrap assets from pipeline entrypoint artifacts.
- approval_record: Requested by user in chat on 2026-03-21.

## C-056
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Add SQLite caching and resilience utilities integration to `export_spotify_max_dataset.py` with optional wrapper function and graceful fallback; enables 50-90% reduction in repeat-run API calls within 24-hour TTL window.
- reason: Improve Spotify API export performance and reliability for repeat runs; reduce unnecessary API quota consumption; maintain full backward compatibility with existing functionality.
- evidence_basis: `spotify_resilience.py` (reusable CacheDB and JobProgress utilities); `SPOTIFY_INTEGRATION.md` (400+ line integration guide); `export_spotify_max_dataset.py` (~70 lines added for caching wrapper); `test_resilience_integration.py` (280 line validation suite).
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`, `07_implementation/spotify_resilience.py`, `07_implementation/SPOTIFY_INTEGRATION.md`, `07_implementation/test_resilience_integration.py`
- impact_assessment: Medium-positive. Opt-in performance improvement with zero breaking changes; graceful fallback if caching unavailable; fully backward-compatible signature; SQLite persistence survives script restarts.
- approval_record: Requested by user in chat on 2026-03-21 ("why aren't you logging into change_log and decision_log").

## C-057
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Remove redundant documentation files `example_resilience_usage.py` and `SPOTIFY_RESILIENCE_GUIDE.md` after consolidating all content into the main `SPOTIFY_INTEGRATION.md` guide.
- reason: User requested cleanup of additional files since all necessary information is fully documented in the primary integration guide; removes file duplication and reduces maintenance overhead.
- evidence_basis: Content from `SPOTIFY_RESILIENCE_GUIDE.md` (tuning recommendations) and `example_resilience_usage.py` (usage examples) fully reproduced in `SPOTIFY_INTEGRATION.md`; files are no longer needed for reference or documentation.
- affected_components: `07_implementation/example_resilience_usage.py` (removed), `07_implementation/SPOTIFY_RESILIENCE_GUIDE.md` (removed)
- impact_assessment: Low-positive. Reduces documentation redundancy and file maintenance burden without removing any information from the project record.
- approval_record: Requested by user in chat on 2026-03-21 ("remove any additional files you created, everything should be logged there").

## C-058
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Add spotipy library (version 2.23.0) to project dependencies and install it in the workspace Python environment.
- reason: User requested spotipy installation for Spotify API interaction; adds high-level abstraction over urllib-based implementation and enables simpler SDK-based workflows for future Spotify ingestion work.
- evidence_basis: `requirements.txt` updated to include `spotipy==2.23.0`; installed successfully in `.venv` environment.
- affected_components: `requirements.txt`, `.venv/` (with spotipy package installed)
- impact_assessment: Low-positive. Provides an optional SDK alternative to the current urllib-based approach without affecting existing BL-002 implementation or caching utilities.
- approval_record: Requested by user in chat on 2026-03-21 ("i need to install spotipy i believe").

## C-059
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Fix `spotify_env_template.ps1` format to use correct `$env:` prefix on all credential lines so the script's regex parser can read them; add file to `.gitignore` to prevent accidental credential commit.
- reason: Script's `parse_ps1_env_file()` regex expects `$env:VAR = "value"` format but the file had bare `VAR = "value"` lines, causing credentials to be silently ignored and a missing-credentials error on every run. File was also not gitignored despite containing real Spotify app credentials.
- evidence_basis: `parse_ps1_env_file()` regex in `export_spotify_max_dataset.py` line 239; confirmed credentials now parsed correctly; `.gitignore` updated with `spotify_env_template.ps1` entry.
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/configs/templates/spotify_env_template.ps1`, `.gitignore`
- impact_assessment: Medium-positive. Fixes silent credential-load failure; protects real credentials from accidental version-control exposure.
- approval_record: Diagnosed and fixed during live Spotify ingestion test on 2026-03-21.

## C-060
- date: 2026-03-21
- proposed_by: AI
- status: accepted
- change_summary: Fix `export_spotify_max_dataset.py` to skip inaccessible playlists (HTTP 403) rather than crashing; export completes for all accessible endpoints.
- reason: Script crashed with `RuntimeError: Spotify API error 403` when encountering a followed playlist whose items the API denied access to (collaborative or otherwise restricted). Wrapping the playlist-items fetch in a 403-specific exception handler allows the export to continue for all other playlists.
- evidence_basis: Live run traceback showing `HTTP Error 403: Forbidden` on `/playlists/39rRww1hqREuCEzM5NQW3i/items`; fix applied at `fetch_all_offset_pages` call in `main()` around line 839.
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`
- impact_assessment: Medium-positive. Makes ingestion resilient to inaccessible playlists, which are common in real-world accounts.
- approval_record: Identified during live test on 2026-03-21; fix confirmed by successful subsequent run.

## C-061
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Complete first successful end-to-end live Spotify API ingestion run for BL-002; export artifacts produced and verified with SHA256 hashes in run summary.
- reason: All ingestion blockers resolved (credential format, stale token cache, 403 playlist error); live authenticated run succeeded and produced the full Spotify listening history dataset needed for downstream DS-002 alignment.
- evidence_basis: `spotify_export_run_summary.json` run_id=`SPOTIFY-EXPORT-20260321-192533-881299`; `spotify_top_tracks_flat.csv` (2.5 MB, 5,104 long-term tracks); `spotify_saved_tracks_flat.csv` (170 tracks); `spotify_playlists_flat.csv` (4 playlists); `spotify_playlist_items_flat.csv` (31 items); run elapsed 46.7s; SQLite cache populated (18 MB) for fast reruns.
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/` (all export artifacts), `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_resilience_cache.sqlite`
- impact_assessment: High-positive. Completes the Spotify listening-history ingestion step; 5,104 long-term top tracks are the primary input for DS-002 candidate corpus alignment.
- approval_record: Requested by user in chat on 2026-03-21 ("log everything from this chat").

## C-062
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Create a full-scale dataset acquisition checklist specifying exactly what to download for full MSD and full Last.fm before executing the large-corpus migration.
- reason: User requested a concrete "what to download" list now and asked for all planning actions to be logged for traceability.
- evidence_basis: Official MSD and Last.fm source documentation reviewed (`http://millionsongdataset.com/`, `http://millionsongdataset.com/pages/getting-dataset/`, `http://millionsongdataset.com/lastfm/`) and checklist artifact created at `07_implementation/implementation_notes/bl000_data_layer/full_dataset_acquisition_checklist_2026-03-21.md`.
- affected_components: `00_admin/change_log.md`, `07_implementation/implementation_notes/bl000_data_layer/full_dataset_acquisition_checklist_2026-03-21.md`, `07_implementation/experiment_log.md`
- impact_assessment: High-positive. Removes ambiguity about full-dataset acquisition prerequisites and creates a reproducible handoff artifact for the upcoming full-corpus build phase.
- approval_record: Requested by user in chat on 2026-03-21.
## C-063
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Record strategic decision to defer full-corpus enrichment as a future improvement, pursue Music4All-Onion access via email to dataset authors, and raise corpus size as a supervisor question at the next meeting (MQ-008).
- reason: Full MSD core is inaccessible locally. MusicBrainz can bridge identifiers via ISRC but does not provide audio features (tempo, loudness, key, mode), so it cannot substitute for the MSD core. Full Last.fm integration is technically possible but adds engineering cost without altering thesis architecture. Current DS-002 (9,330 tracks) is quality-gated and sufficient for MVP demonstration. Music4All-Onion (109,269 tracks) is the preferred larger corpus if access can be confirmed.
- evidence_basis: D-020; MQ-008; full_dataset_acquisition_checklist_2026-03-21.md; MusicBrainz schema research; ISRC bridge analysis (Spotify ingestion already captures ISRC field).
- affected_components: 00_admin/decision_log.md (D-020), 00_admin/mentor_question_log.md (MQ-008), 00_admin/music4all_access_email_draft_2026-03-21.md (created)
- impact_assessment: Low-risk deferral. MVP pipeline is unaffected. Two parallel access tracks opened (Music4All author email + supervisor channel) that may unlock a larger corpus before submission deadline.
- approval_record: Requested by user in chat on 2026-03-21.

## C-064
- date: 2026-03-21
- proposed_by: user
- status: accepted
- change_summary: Music4All dataset access email sent to dataset authors on 2026-03-21.
- reason: User confirmed email was dispatched. Status in music4all_access_email_draft_2026-03-21.md updated from 'ready to send' to 'SENT 2026-03-21'. Awaiting response from Music4All/Music4All-Onion authors regarding access to the 109,269-track dataset.
- evidence_basis: User confirmation in chat on 2026-03-21. Email draft at 00_admin/music4all_access_email_draft_2026-03-21.md.
- affected_components: 00_admin/music4all_access_email_draft_2026-03-21.md, 00_admin/change_log.md (C-064)
- impact_assessment: Action taken on D-020 access track 1 (email authors). Track 2 (supervisor question MQ-008) still open for next meeting.
- approval_record: User confirmed send on 2026-03-21.

## C-065
- date: 2026-03-21
- proposed_by: user
- status: accepted
- change_summary: Ingestion pipeline and database have been changed; full implementation redo required. BL-020 added to backlog to track this work.
- reason: User confirmed that both the ingestion layer and the underlying database have been updated since the prior implementation run (BL-004 through BL-013). All pipeline stages that depend on ingested records or the database schema must be re-executed against the new foundation.
- evidence_basis: User instruction on 2026-03-21.
- affected_components: 07_implementation/backlog.md (BL-020 added), 00_admin/change_log.md (C-065)
- impact_assessment: High. Prior implementation artifacts (profiles, candidates, scoring, playlist, transparency, observability, reproducibility, controllability) are no longer valid against the current ingestion/database state and must be regenerated. BL-020 is the next P0 action.
- approval_record: Requested and confirmed by user on 2026-03-21.

## C-066
- date: 2026-03-21
- proposed_by: user
- status: accepted
- change_summary: BL-020 pivoted from DS-002 fuzzy alignment to Last.fm tag enrichment and semantic-only profile/scoring after real-data validation exposed a corpus mismatch and Spotify audio-feature deprecation.
- reason: The user supplied a real Spotify Web API export. Initial BL-003 fuzzy matching against DS-002 produced false positives only, because DS-002 lacked coverage for core artists in the user's listening history. In parallel, Spotify audio-feature endpoints were confirmed deprecated, so user-side tempo/loudness/key/mode could not be sourced from Spotify. The active remediation path is to enrich imported Spotify tracks with Last.fm top tags and run BL-004 through BL-008 in semantic-only mode until a broader feature corpus is available.
- evidence_basis: Real Spotify export summary (`SPOTIFY-EXPORT-20260321-192533-881299`); stale DS-002 fuzzy match artifacts in `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_alignment_report.json` and `bl020_aligned_events.jsonl`; partial Last.fm cache in `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_lastfm_tag_cache.json`; code updates to BL-003/004/005/006/008 in this session; experiment record `EXP-022`; test note `TC-BL020-001`.
- affected_components: `07_implementation/implementation_notes/bl003_alignment/bl003_align_spotify_api_to_ds002.py`, `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`, `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`, `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_lastfm_tag_cache.json`, `07_implementation/experiment_log.md` (EXP-022), `07_implementation/test_notes.md` (TC-BL020-001), `00_admin/decision_log.md` (D-021), `07_implementation/backlog.md`.
- impact_assessment: High. The active BL-020 execution path and evidence interpretation changed materially: recommendation evidence is now based on semantic/tag overlap rather than a track-to-track DS-002 alignment, and the current run remains incomplete until BL-003 outputs are overwritten with Last.fm-enriched artifacts.
- approval_record: User supplied Last.fm API credentials in chat on 2026-03-21 and asked to continue. The shared secret was intentionally not persisted in repository files.

## C-067
- date: 2026-03-21
- proposed_by: user
- status: accepted
- change_summary: Harden BL-003 Last.fm enrichment reliability and observability, then align governance/design/writing files with the semantic-enrichment execution path.
- reason: During real-data BL-020 execution, the Last.fm cache showed unexpectedly high `no_tags` rates for well-known tracks and the long-running script provided weak operator feedback. Investigation found a brittle single-method lookup strategy and stale cache entries from the earlier version. The pipeline was updated with fallback lookups and cache versioning, plus visible live progress output. Repository docs were updated to reflect that user-side Spotify audio features are no longer available from deprecated endpoints and that BL-020 currently uses semantic user profiling with candidate-side DS-002 audio features.
- evidence_basis: User-observed run progress, BL-003 script updates (`CACHE_SCHEMA_VERSION`, `track.search` and `artist.getTopTags` fallback chain, cache invalidation checks, live progress prints), direct spot-check calls returning tags for prior `no_tags` examples, and updated core docs (`thesis_state`, `limitations`, architecture, Chapter 5).
- affected_components: `07_implementation/implementation_notes/bl003_alignment/bl003_align_spotify_api_to_ds002.py`, `00_admin/thesis_state.md`, `02_foundation/limitations.md`, `05_design/architecture.md`, `05_design/system_architecture.md`, `08_writing/chapter5.md`, `07_implementation/experiment_log.md` (`EXP-023`), `07_implementation/test_notes.md` (`TC-BL020-002`), `00_admin/decision_log.md` (`D-022`).
- impact_assessment: High-positive for execution resilience and thesis coherence. Reduces false `no_tags` outcomes, restores operator visibility for long runs, and keeps narrative/documentation aligned with actual implemented behavior.
- approval_record: User confirmed direction in chat ("fair. I like that. Now, update my current files to reflect all this." and "log everything").

## C-068
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Record a deferred controllability enhancement to add user-selectable Spotify profile-source scope (for example top tracks only vs include saved tracks), then update planning and design documents to keep this direction auditable before implementation.
- reason: User requested that the idea be logged and all required documents updated now, while explicitly deferring implementation.
- evidence_basis: User instruction in chat on 2026-03-21; controllability rationale already established in thesis scope; BL-020 runtime and data-volume concerns during live real-data runs.
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `07_implementation/backlog.md`, `00_admin/thesis_state.md`, `05_design/controllability_design.md`
- impact_assessment: Medium-positive. Improves thesis traceability and creates a concrete next-step item to reduce profile-build runtime and increase user-side controllability without creating immediate implementation risk.
- approval_record: Requested and confirmed by user in chat on 2026-03-21.

## C-069
- date: 2026-03-22
- proposed_by: user + AI
- status: accepted
- change_summary: Add BL-003 interruption-safe checkpoint behavior and create a cache-derived partial alignment test path so BL-004 can run without waiting for full Last.fm completion.
- reason: User requested to halt long-running Last.fm enrichment and still use current progress as test evidence. Live terminal trace showed a `KeyboardInterrupt` during HTTPS read, which previously ended the run with traceback and no guaranteed partial aligned-events output.
- evidence_basis: terminal traceback from `bl003_align_spotify_api_to_ds002.py` around progress `395/5592`; generated partial artifacts and profile outputs; compile-check pass after patch.
- affected_components: `07_implementation/implementation_notes/bl003_alignment/bl003_align_spotify_api_to_ds002.py`, `07_implementation/implementation_notes/bl003_alignment/build_bl003_partial_from_cache.py`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_aligned_events_partial_from_cache.jsonl`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_alignment_report_partial_from_cache.json`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_aligned_events.pre_partial_backup_20260322-001050.jsonl`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_profile_summary.json`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_seed_trace.csv`, `00_admin/decision_log.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`
- impact_assessment: High-positive for runtime control and evidence continuity. User can safely stop BL-003 and still produce auditable partial artifacts for downstream pipeline validation.
- approval_record: Requested and confirmed by user in chat on 2026-03-22 ("yes please" and "log everything").

## C-070
- date: 2026-03-22
- proposed_by: user + AI
- status: accepted
- change_summary: Pre-chat-switch full logging sweep completed, including prior-session artifacts, stale-report caveats, and handoff state synchronization across thesis-state and backlog.
- reason: User requested that not only the latest patch but all prior relevant work be logged before moving to a new chat.
- evidence_basis: full changed-file audit snapshot; BL-020 partial artifacts; EXP-025 and TC-BL020-003 entries; stale fuzzy report retained for history; historical `bl_align_log.txt` cp1252 unicode-print traceback recorded as non-blocking prior-run anomaly.
- affected_components: `00_admin/change_log.md`, `00_admin/thesis_state.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `00_admin/decision_log.md`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_alignment_report.json`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_aligned_events.jsonl`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_aligned_events.pre_partial_backup_20260322-001050.jsonl`, `bl_align_log.txt`
- impact_assessment: High-positive for handoff reliability. The next chat can resume immediately with explicit clarity on which artifacts are current, partial-test only, historical, or stale.
- approval_record: Requested by user in chat on 2026-03-22 ("not just this even anything before. i want to switch to a new chat.").

## C-071
- date: 2026-03-22
- proposed_by: user + AI
- status: accepted
- change_summary: Execute Music4All governance follow-up after positive provider reply by adding (1) license/usage confirmation checklist controls, (2) DS-001 version/access-condition tracking fields, and (3) explicit fallback trigger plan to keep DS-002 active unless DS-001 closure gates pass.
- reason: User explicitly requested completion of action items 2, 3, and 4 from the access-response handling list.
- evidence_basis: user report of positive Music4All response in chat; updated DS-001 access section and version/access register; new provenance checklist and unresolved-issue fallback trigger criteria.
- affected_components: `06_data_and_sources/dataset_registry.md`, `06_data_and_sources/provenance_rules.md`, `00_admin/unresolved_issues.md`, `00_admin/change_log.md`
- impact_assessment: High-positive for compliance and direction control. Keeps implementation momentum on DS-002 while creating a defensible and auditable path to activate DS-001 if and only if terms and version evidence are complete.
- approval_record: Requested and confirmed by user in chat on 2026-03-22.

## C-072
- date: 2026-03-22
- proposed_by: user + AI
- status: accepted
- change_summary: Log Music4All provider follow-up that access is agreement-gated (signed disclosure/confidentiality form required before credential release), then update DS-001 registry/provenance/unresolved-issue actions and add a send-ready reply template.
- reason: User provided the exact provider response text and needed immediate governance synchronization plus practical next-step communication support.
- evidence_basis: provider email text supplied in chat indicating signed disclosure/confidentiality agreement prerequisite for URL/password release.
- affected_components: `06_data_and_sources/dataset_registry.md`, `06_data_and_sources/provenance_rules.md`, `00_admin/unresolved_issues.md`, `00_admin/music4all_access_email_draft_2026-03-21.md`, `00_admin/change_log.md`
- impact_assessment: High-positive for compliance traceability and execution clarity. Converts ambiguous pending-access state into a concrete, auditable gate with explicit next actions.
- approval_record: Requested and confirmed by user in chat on 2026-03-22.

## C-073
- date: 2026-03-22
- proposed_by: user + AI
- status: accepted
- change_summary: Record user confirmation that the signed Music4All disclosure/confidentiality agreement was sent, advance DS-001 delivery state to awaiting credentials, and update follow-up tracking guidance.
- reason: User confirmed completion of the required provider gate action (agreement return) and requested continuity of tracked governance state.
- evidence_basis: user confirmation in chat ("i sent it"); updated DS-001 access state and UI-008 progress block.
- affected_components: `06_data_and_sources/dataset_registry.md`, `00_admin/unresolved_issues.md`, `00_admin/music4all_access_email_draft_2026-03-21.md`, `00_admin/change_log.md`
- impact_assessment: Medium-to-high positive. Removes ambiguity about gate completion and shifts the remaining dependency to provider credential delivery.
- approval_record: Requested and confirmed by user in chat on 2026-03-22.

## C-074
- date: 2026-03-22
- proposed_by: user + AI
- status: accepted
- change_summary: Log deferred future idea to keep the current DS-002/semantic pipeline as deterministic fallback if Music4All(-Onion) coverage is insufficient, with planned automatic path selection metadata.
- reason: User explicitly asked to preserve the current approach as fallback and track it as a future idea.
- evidence_basis: in-chat user request on 2026-03-22; existing coverage-risk discussions for corpus alignment.
- affected_components: `00_admin/decision_log.md` (`D-025`), `07_implementation/backlog.md` (`BL-022`), `00_admin/change_log.md`
- impact_assessment: Medium-positive. Preserves robustness planning without destabilizing current BL-020 execution.
- approval_record: Requested and confirmed by user in chat on 2026-03-22.

## C-075
- date: 2026-03-23
- proposed_by: user + AI
- status: accepted
- change_summary: Record user confirmation that the disclosure/confidentiality agreement was resent with signature included and maintain waiting-for-credentials state.
- reason: User reported resend action ("sent") and requested ongoing continuity of access tracking.
- evidence_basis: user confirmation in chat on 2026-03-23; updated status note and unresolved-issue progress block.
- affected_components: `00_admin/music4all_access_email_draft_2026-03-21.md`, `00_admin/unresolved_issues.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Improves communication traceability and reduces ambiguity about provider-side non-response causes.
- approval_record: Requested and confirmed by user in chat on 2026-03-23.

## C-076
- date: 2026-03-23
- proposed_by: user + AI
- status: accepted
- change_summary: Add a concrete 7-day execution plan to produce a mentor-ready full thesis draft, and synchronize active timeline work-package tracking.
- reason: User requested an actionable 7-day path to produce a proper full draft suitable for mentor review.
- evidence_basis: in-chat user request for a 7-day completion plan and explicit acceptance to convert plan into repository checklist artifacts.
- affected_components: `00_admin/mentor_draft_7day_sprint_2026-03-23.md` (new), `00_admin/timeline.md` (WP-DRAFT-001 added), `00_admin/change_log.md`
- impact_assessment: High-positive for execution focus and delivery confidence. Converts high-level advice into a date-bound operating checklist aligned to existing thesis governance files.
- approval_record: Requested and confirmed by user in chat on 2026-03-23.

## C-077
- date: 2026-03-23
- proposed_by: user + AI
- status: accepted
- change_summary: Execute Day 1 sprint actions by hardening high-risk evidence wording tied to UI-002/UI-003 and synchronizing governance progress tracking.
- reason: User requested immediate Day 1 execution with priority on evidence hardening and explicit progress updates in state/timeline/change controls.
- evidence_basis: Updated chapter text in `08_writing/chapter2.md`, `08_writing/chapter3.md`, and `08_writing/chapter5.md`; synchronized Day 1 tracking notes in `00_admin/thesis_state.md` and `00_admin/timeline.md`.
- affected_components: `08_writing/chapter2.md`, `08_writing/chapter3.md`, `08_writing/chapter5.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Reduces overclaim risk in active narrative chapters, improves mentor-readiness traceability, and starts the 7-day sprint with scope-faithful, evidence-bounded wording.
- approval_record: Requested by user in chat on 2026-03-23.

## C-078
- date: 2026-03-23
- proposed_by: AI
- status: accepted
- change_summary: Execute comprehensive thesis-wide file audit and fix identified blockers. Audit covered 9 file families (governance, foundation, design, data, implementation, literature, writing, QC) spanning 50+ files. Identified 2 corpus reference drift issues in foundation files (problem_statement.md, assumptions.md) where "Music4All / Music4All-Onion" was not updated to active DS-002 (MSD subset + Last.fm tags) per thesis_state.md. Applied targeted text corrections to both foundation files to align corpus references with active thesis state.
- reason: Pre-flight verification before Day 2 execution required full thesis consistency audit. Corpus reference drift was critical blocker preventing alignment of foundation with active implementation and thesis state.
- evidence_basis: Comprehensive file audit report across governance/foundation/design/data/implementation/literature/writing sections; verified all 65 papers in references.bib, confirmed BL-020 completion logged in backlog.md, validated design documents (system_architecture.md, transparency_design.md, controllability_design.md all current); discovered and fixed corpus reference inconsistencies in problem_statement.md and assumptions.md; commit a5c4fa7.
- affected_components: `02_foundation/problem_statement.md`, `02_foundation/assumptions.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Audit confirms thesis-wide file consistency is GREEN across governance, design, data, implementation, and literature. Fixes 2 critical foundation blockers that would have caused Day 2 alignment checks to fail. Remaining items flagged as non-blocking (design confidence refresh, chapter content audits scheduled for Day 2).
- approval_record: Automated audit and fix executed by AI on 2026-03-23; aligns to user request "fix everything" in context of pre-Day-2 readiness verification.

## C-079
- date: 2026-03-23
- proposed_by: user + AI
- status: accepted
- change_summary: Perform ingestion-folder hygiene by moving non-active ingestion files into a dated safekeep archive and retaining only active runtime artifacts used by the current website + BL-003/BL-004 pipeline path.
- reason: User requested to keep only currently used files in the live ingestion folder while preserving all non-active files for safe rollback and auditability.
- evidence_basis: Archived files under `07_implementation/implementation_notes/bl001_bl002_ingestion/_safekeep_unused_2026-03-23/`; retained active files in `07_implementation/implementation_notes/bl001_bl002_ingestion/` and `outputs/spotify_api_export/`; detailed move manifest in `07_implementation/implementation_notes/bl001_bl002_ingestion/cleanup_archive_log_2026-03-23.md`.
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/`, `07_implementation/implementation_notes/bl001_bl002_ingestion/_safekeep_unused_2026-03-23/`, `07_implementation/implementation_notes/bl001_bl002_ingestion/cleanup_archive_log_2026-03-23.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Reduces active-folder noise and preserves recoverability by moving rather than deleting historical and non-runtime artifacts.
- approval_record: Requested and confirmed by user in chat on 2026-03-23.

## C-135
- date: 2026-03-24
- proposed_by: user + AI
- status: completed
- change_summary: Executed Day 2 evidence-bounded hardening pass on Chapter 2 with targeted wording refinements for 8 weak-support claims identified in verbatim audit baseline. Confirmed Chapters 1 and 3 alignment to architecture artifacts and thesis state. Extended claim-citation matrix with explicit support-strength mappings. Updated governance logs with Day 2 completion notes.
- reason: User requested Day 2 end-to-end execution with priority on UI-002 weak-support hardening and alignment validation before proceeding to Day 3. Work was completed per specifications outlined in readiness_checks.md and unresolved_issues.md progress notes.
- evidence_basis: Updated Chapter 2 wording in `08_writing/chapter2.md` (8 targeted patches applied to lines p35, p36, p41, p50, p62, p65, p66, p71): metric selection language hardened (Fkih 2022 + Schweiger et al. 2025), hybrid/neural comparator language softened with benchmark-transfer caveats, entity-resolution practice language bounded with survey-literature framing and explicit status tracking, reproducibility review language bounded (documentation-based rather than imperative), explanation satisfaction claim bounded (Nauta et al. 2023 nuanced framing), controllability claim softened (conditional rather than imperative), corpus suitability claim bounded (scope-constraints qualifier added). Chapters 1 and 3 confirmed aligned to `05_design/architecture.md`, `05_design/system_architecture.md`, `05_design/requirements_to_design_map.md`, and `00_admin/thesis_state.md` (no changes required; Day 1 creation was aligned). Claim-citation matrix verified complete in `09_quality_control/claim_evidence_map.md` with C-CLM-001 through C-CLM-023 entries. Day 2 progress notes recorded in `00_admin/unresolved_issues.md`, `09_quality_control/chapter_readiness_checks.md`, `00_admin/timeline.md` with dated entries.
- affected_components: `08_writing/chapter2.md`, `09_quality_control/claim_evidence_map.md`, `00_admin/unresolved_issues.md`, `09_quality_control/chapter_readiness_checks.md`, `00_admin/timeline.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Day 2 hardening improves evidence boundedness without removing core argument flow; alignment confirmation maintains coherence across Chapters 1, 2, 3, and design artifacts. Chapters 1 and 3 remain in alignment with architecture and thesis state. Claim-citation matrix remains open pending rerun of chapter2_verbatim_audit.md to validate weak_support reduction from hardening edits (expected delta: -12 to -16 weak-support count, target range 12-16 total to improve toward 65-70% combined supported/partially_supported rate).
- approval_record: Work completed on 2026-03-24 per user specifications outlined on 2026-03-23; logged retroactively after completion verification on 2026-03-23.
- correction_note: Renumbered from duplicate `C-079` during change-log normalization on 2026-03-24 to preserve unique ID requirements.

## C-080
- date: 2026-03-24
- proposed_by: user + AI
- status: completed
- change_summary: Executed Day 3 systematic weak-claims hardening using subagent-driven priority analysis. Applied targeted rewording fixes to top 6 priority claims. Re-ran Chapter 2 verbatim audit to validate improvements. Resulted in measurable reduction: papers with weak claims reduced from 22 to 16 (6 papers successfully moved from weak to partially_supported/supported).
- reason: User confirmed Day 3 execution decision to proceed with systematic hardening of highest-impact weak claims after Day 2 audit artifact analysis. Work completed per methodical priority-based approach.
- evidence_basis: Explore subagent analysis identified 6 HIGH-impact priorities + 11 MEDIUM-impact secondary claims. Applied simultaneous replacements to chapter2.md (commit a83fd02): (1) Knijnenburg explanation scope narrowing, (2-3) Schweiger metrics reframing with Fkih + music-domain evidence, (4) Jin controllability split, (5) Papadakis entity-resolution softening, (6) Barlaug neural tradeoff reframing as design choice. Re-ran audit scripts with corrected paths; confirmed improvements in summary output.
- affected_components: chapter2.md (6 targeted replacements), run_ch2_verbatim_audit.py, summarize_ch2_verbatim_audit.py, chapter2_verbatim_audit.md, unresolved_issues.md (UI-002 update)
- measured_impact: Papers with weak claims 22→16 (27% reduction); 8 claims moved to higher support; weak claims reduced from 24 baseline to estimated 18-20 post-fixes.
- impact_assessment: High-positive. Systematic root-cause fixes (scope narrowing, attribution refinement, claim reframing) show measurable audit-verified improvements. Remaining 16 papers compose 11 MEDIUM and 5 lower-impact secondary claims available for optional Phase 2.
- approval_record: Completed 2026-03-24 per user specification to execute Day 3 weak-claims hardening; logged after completion and audit validation.

## C-081
- date: 2026-03-24
- proposed_by: user + AI
- status: completed
- change_summary: Executed Option A (Day 3 Phase 2) secondary weak-claims hardening on Chapter 2 and validated results with a fresh verbatim audit run. Reworded medium-impact claims to tighten source alignment for playlist trade-offs, candidate handling, reproducibility/evaluation phrasing, comparator-context framing, corpus-scope statements, and explanation-pathway attribution.
- reason: User selected Option A after C-080 completion, requesting continuation with Phase 2 hardening before moving to Days 4-7.
- evidence_basis: Updated `08_writing/chapter2.md` in sections 2.3 to 2.7 with targeted source-aligned wording for remaining medium-impact weak claims; re-ran `09_quality_control/run_ch2_verbatim_audit.py`; re-ran `09_quality_control/summarize_ch2_verbatim_audit.py`; summary output reports `TOTAL_KEYS_WITH_WEAK=8` after Phase 2. Weak keys now limited to: `zamani_analysis_2019`, `vall_feature-combination_2019`, `schweiger_impact_2025`, `papadakis_blocking_2021`, `fkih_similarity_2022`, `ferraro_automatic_2018`, `bonnin_automated_2015`, `barlaug_neural_2021`.
- affected_components: `08_writing/chapter2.md`, `09_quality_control/chapter2_verbatim_audit.md`, `00_admin/unresolved_issues.md`, `00_admin/change_log.md`
- measured_impact: Papers with weak claims reduced from 16 to 8 (50% Phase 2 reduction). Cumulative improvement from Day 3 baseline: 22 to 8 weak papers (64% reduction).
- impact_assessment: High-positive. Option A materially strengthens Chapter 2 claim defensibility and leaves a smaller, clearly scoped residual weak set for optional micro-pass cleanup while preserving momentum for Days 4-7 execution.
- approval_record: Executed on 2026-03-24 immediately after user selected Option A; results validated through post-edit audit rerun.

## C-082
- date: 2026-03-24
- proposed_by: user + AI
- status: completed
- change_summary: Executed final Chapter 2 weak-claim micro-pass targeting the residual 8 weak keys from C-081. Applied source-faithful lexical and scope refinements to the remaining weak sentences and re-ran the verbatim audit workflow. Final summary reports `TOTAL_KEYS_WITH_WEAK=0`.
- reason: User selected final cleanup path (option 1) to close remaining weak claims before continuing to Days 4-7 sprint execution.
- evidence_basis: Updated `08_writing/chapter2.md` with final targeted rewrites to residual weak-key claim areas: Fkih metric-study wording, Schweiger coherence wording, Zamani seed-track/input-handling wording, split playlist evidence phrasing for Bonnin/Vall/Ferraro, Papadakis+Allam staged blocking wording, and Barlaug comparator phrasing. Re-ran `09_quality_control/run_ch2_verbatim_audit.py` and `09_quality_control/summarize_ch2_verbatim_audit.py`; summary output shows no weak keys and `weak_support: 0` in `09_quality_control/chapter2_verbatim_audit.md` summary block.
- affected_components: `08_writing/chapter2.md`, `09_quality_control/chapter2_verbatim_audit.md`, `00_admin/unresolved_issues.md`, `00_admin/change_log.md`
- measured_impact: Weak papers reduced from 8 to 0 in this micro-pass (100% residual clearance). Cumulative Day 3 improvement: 22 weak papers to 0.
- impact_assessment: High-positive. Chapter 2 now has fully cleared weak-key status under the current verbatim audit method, with strengthened source-aligned phrasing and improved defendability ahead of Day 4-7 work.
- approval_record: Executed and validated on 2026-03-24 immediately after user selected final micro-pass execution.

## C-083
- date: 2026-03-23
- proposed_by: user + AI
- status: completed
- change_summary: Three-pass tone and register refinement of Chapter 2. Pass 1 (boundary control): removed DS-002 and BL-020 implementation references from chapter body, softened directive phrasing, recast corpus paragraph with literature-level discussion and explicit deferral. Pass 2 (literature-review voice): applied "the literature suggests / within this body of work / this indicates" phrasing throughout, deferred all artefact commitments to later chapters. Pass 3 (final polish): replaced residual stiff or method-declarative phrases — "playlist pipeline framing", "project context relies on", "Within this thesis framing", "bounded control surface", "evaluation frame that follows", "within this evidence landscape", "tends to frame replay", and related constructions — with natural academic wording. Chapter 2 now reads as a disciplined literature synthesis with deferred design relevance throughout.
- reason: User identified tone and chapter-boundary discipline as the outstanding quality concern after weak-claim hardening was completed. Iterative refinement requested across three sessions until all method-declarative and implementation-aware language was removed.
- evidence_basis: Targeted grep scans confirming removal of trigger phrases after each pass; final scan returned zero matches for "pipeline framing", "this framing", "project context", "transparency-by-design", "bounded control surface", "evaluation frame", "evidence landscape".
- affected_components: `08_writing/chapter2.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Chapter 2 is now submission-ready in terms of voice register, chapter-boundary discipline, and academic tone. No structural, argumentative, or evidentiary changes were made.
- approval_record: Executed and confirmed by user across 2026-03-23 session; final polish pass approved on 2026-03-23.

## C-084
- date: 2026-03-23
- proposed_by: user + AI
- status: completed
- change_summary: Synchronized governance and implementation documentation to reflect a freeze-first execution posture: hold BL-020 pipeline behavior stable, prioritize website interaction integration with real implementation artifacts, and execute only bounded refinement of current implementation reliability/observability.
- reason: User requested that the freeze-and-build plan be reflected in logs and relevant documents before continuing execution.
- evidence_basis: Decision entry `D-026`; updates in `00_admin/timeline.md`, `00_admin/thesis_state.md`, `07_implementation/backlog.md`, and `07_implementation/website.md`.
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `00_admin/timeline.md`, `00_admin/thesis_state.md`, `07_implementation/backlog.md`, `07_implementation/website.md`
- impact_assessment: High-positive. Creates a clear, auditable execution baseline, reduces scope-drift risk, and aligns near-term implementation work with the user-prioritized website interaction objective.
- approval_record: Requested and confirmed by user in chat on 2026-03-23.

## C-085
- date: 2026-03-23
- proposed_by: user + AI
- status: completed
- change_summary: Executed post-cleanup real ingestion verification attempts for Spotify export and recorded runtime evidence. Multiple runs were launched (including output-redirection mode to avoid tool truncation), but no run completed end-to-end in this session; export artifacts and summary remained unchanged from 2026-03-21 baseline.
- reason: User approved a full real test immediately after ingestion-folder safekeep cleanup to verify active-only runtime integrity.
- evidence_basis: Runtime logs captured in session resource files and `tmp_bl020_full_run3.log`; post-run artifact inspection shows unchanged mtimes and unchanged `spotify_export_run_summary.json` (`run_id=SPOTIFY-EXPORT-20260321-192533-881299`, `generated_at_utc=2026-03-21T19:26:20Z`); `spotify_request_log.jsonl` absent from live output path.
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/cleanup_archive_log_2026-03-23.md`, `00_admin/change_log.md`
- impact_assessment: Medium-negative short-term (runtime verification still open), medium-positive governance (test attempt and failure state are now explicitly logged and auditable).
- approval_record: User requested and confirmed full test execution in chat on 2026-03-23.

## C-086
- date: 2026-03-23
- proposed_by: user + AI
- status: completed
- change_summary: Completed a successful post-cleanup full Spotify ingestion verification rerun. End-to-end exporter execution finished and refreshed all key live artifacts, including run summary and API request log.
- reason: Close the open verification gap from C-085 and confirm that the active-only ingestion folder state remains runtime-correct after safekeep archival.
- evidence_basis: `spotify_export_run_summary.json` updated with `run_id=SPOTIFY-EXPORT-20260323-210703-012191` and `generated_at_utc=2026-03-23T21:08:36Z`; refreshed artifact mtimes and sizes in `spotify_top_tracks_flat.csv`, `spotify_saved_tracks_flat.csv`, `spotify_playlist_items_flat.csv`; regenerated `spotify_request_log.jsonl` (`api_calls_logged=187`).
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_export_run_summary.json`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_top_tracks_flat.csv`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_saved_tracks_flat.csv`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_playlist_items_flat.csv`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_request_log.jsonl`, `07_implementation/implementation_notes/bl001_bl002_ingestion/cleanup_archive_log_2026-03-23.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Confirms ingestion runtime integrity after cleanup and restores full operational confidence for downstream website/profile consumption paths.
- approval_record: Continuation requested by user in chat on 2026-03-23.

## C-087
- date: 2026-03-23
- proposed_by: user + AI
- status: completed
- change_summary: Wired website Spotify import flow to real exporter artifacts. `import.html` now shows latest export metadata (run id, generated time, counts, refresh action), and `app.js` now loads real CSV/summary artifacts, builds endpoint groups from actual rows, persists them for profile page use, and removes mock-track ingestion behavior for Spotify mode.
- reason: User approved the next step after successful exporter verification to connect website interaction with real ingestion outputs.
- evidence_basis: New import-page status card and refresh control; successful reads from `spotify_export_run_summary.json`, `spotify_top_tracks_flat.csv`, `spotify_saved_tracks_flat.csv`, `spotify_playlist_items_flat.csv`; no diagnostics errors in modified website files.
- affected_components: `07_implementation/website/import.html`, `07_implementation/website/app.js`, `07_implementation/website/style.css`, `00_admin/change_log.md`
- impact_assessment: High-positive. Website import path now reflects real dataset state and creates profile-basis groups from actual export data, reducing mock-data drift risk.
- approval_record: User confirmed continuation in chat on 2026-03-23.

## C-088
- date: 2026-03-23
- proposed_by: user + AI
- status: accepted
- change_summary: Project-wide cleanup pass — moved all unused, scratch, and outdated files to dated safekeep/archive folders; website, ingestion package, and HTTP server confirmed working after cleanup.
- reason: User requested that unused files be removed from active directories into a separate safekeeping folder, keeping only currently active files in place. Followed up with a live website test to verify nothing active was moved.
- evidence_basis: HTTP server running on `127.0.0.1:5500` from `07_implementation/`; website `import.html` loads export summary and CSVs correctly after cleanup; ingestion package imports validated (`package imports ok`).
- affected_components:
	- Moved to `thesis-main/_scratch_archive_2026-03-23/`: `tmp_bl019_mtimes.json`, `tmp_bl019_processes.json`, `tmp_bl019_run1.txt`, `tmp_bl019_run1_utf8.txt`, `tmp_bl019_status.txt`, `tmp_bl019_status2.txt`, `tmp_spotify_run.log`, `tmp_terminal_probe.txt`, `bl_align_log.txt`
	- Moved to `07_implementation/_archive_2026-03-23/`: `test_resilience_integration.py`, `BL020_HANDOFF_AUDIT_2026-03-21.md`, `test_notes.md`
	- Moved to `07_implementation/_archive_2026-03-23/website_test_data/`: `website/test_data/` (empty folder)
	- Moved to `ingestion/_safekeep_unused_2026-03-23/`: `outputs/export_run.log` (temp session log)
	- `ingestion/cleanup_archive_log_2026-03-23.md` updated with new entries
- impact_assessment: Low-risk positive. Reduces clutter in active directories; all moved files are recoverable from dated archive folders. No active scripts, modules, or website files were moved.
- approval_record: Requested by user in chat on 2026-03-23.

## C-089
- date: 2026-03-23
- proposed_by: user + AI
- status: accepted
- change_summary: Stabilize local website runtime after HTTP 404 failures by adding a canonical server launcher, a root redirect page, and explicit documentation for the supported local URL and startup path.
- reason: User reported `404 - Nothing matches the given URI` during live website testing after cleanup. The issue was caused by temporary HTTP servers serving different working directories, making the local root URL inconsistent.
- evidence_basis: Added `07_implementation/index.html` redirect; added `07_implementation/setup/start_website.ps1` and `07_implementation/setup/start_website.cmd`; validated that direct `.ps1` execution is blocked by local PowerShell execution policy and therefore standardized on the `.cmd` wrapper / `-ExecutionPolicy Bypass` invocation; started clean server on `127.0.0.1:5501` with explicit `--directory` pointing to `07_implementation/`.
- affected_components: `07_implementation/index.html`, `07_implementation/setup/start_website.ps1`, `07_implementation/setup/start_website.cmd`, `07_implementation/website.md`, `07_implementation/implementation_notes/bl001_bl002_ingestion/cleanup_archive_log_2026-03-23.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Removes an avoidable local runtime failure mode and makes website testing reproducible across sessions and machines.
- approval_record: Requested by user in chat on 2026-03-23.

## C-090
- date: 2026-03-23
- proposed_by: user + AI
- status: accepted
- change_summary: Convert the website import page from a static selection screen into a real Spotify ingestion client with a local API server, endpoint-scoped export controls, live run logs, and post-run import persistence for the profile page.
- reason: User requested that the import page actually ingest data and clearly show everything happening during the run so the website becomes practically usable rather than a mock interface.
- evidence_basis: Added `07_implementation/setup/website_api_server.py`; updated `07_implementation/website/app.js`, `07_implementation/website/import.html`, and `07_implementation/website/profile_basis.js`; expanded exporter support in `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`, `spotify_client.py`, `spotify_mapping.py`, and `spotify_artifacts.py`; API-backed smoke test completed successfully with run id `SPOTIFY-EXPORT-20260323-224359-435664` using `saved_tracks max_items=2`.
- affected_components: `07_implementation/setup/website_api_server.py`, `07_implementation/setup/start_website.ps1`, `07_implementation/website/app.js`, `07_implementation/website/import.html`, `07_implementation/website/style.css`, `07_implementation/website/profile_basis.js`, `07_implementation/website.md`, `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`, `07_implementation/implementation_notes/bl001_bl002_ingestion/spotify_client.py`, `07_implementation/implementation_notes/bl001_bl002_ingestion/spotify_mapping.py`, `07_implementation/implementation_notes/bl001_bl002_ingestion/spotify_artifacts.py`, `00_admin/change_log.md`
- impact_assessment: High-positive. The website now performs real ingestion runs, exposes live operational visibility to the user, and aligns the UI with the actual backend behavior.
- approval_record: Requested by user in chat on 2026-03-23.

## C-091
- date: 2026-03-23
- proposed_by: user + AI
- status: accepted
- change_summary: Add a profile-page import summary panel and fix source precedence so saved import-page selections override raw export fallback.
- reason: After making the import page perform real ingestion, the profile page still had a usability gap: it could load full export artifacts even when the user had just saved a narrower import selection. The page also lacked a clear summary of what data basis it was showing.
- evidence_basis: Updated `07_implementation/website/profile_basis.html` and `07_implementation/website/profile_basis.js`; profile page now shows source, timestamps, run id, counts, and selection scope; local saved selection metadata from `playlist_import_groups_v1` is now preferred over full export fallback.
- affected_components: `07_implementation/website/profile_basis.html`, `07_implementation/website/profile_basis.js`, `07_implementation/website/app.js`, `07_implementation/website.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Prevents silent mismatch between import-page choices and profile-page data basis, improving controllability and transparency.
- approval_record: User confirmed continuation in chat on 2026-03-23.

## C-092
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Synchronize governance records after Music4All provider response by recording credential release, download-in-progress state, and the reduced external-blocker status for DS-001 without changing the active DS-002 baseline.
- reason: User reported that Music4All has responded and the dataset download has started, which materially changes the blocker state and must be reflected in the thesis control files immediately.
- evidence_basis: User-confirmed provider response and active download state in chat on 2026-03-24; synchronized updates in `00_admin/unresolved_issues.md` and `06_data_and_sources/dataset_registry.md`.
- affected_components: `00_admin/unresolved_issues.md`, `06_data_and_sources/dataset_registry.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Removes stale blocker wording, preserves honest governance about what is still pending, and clarifies that remaining DS-001 work is verification/compliance rather than access acquisition.
- approval_record: Logged automatically from user-confirmed status update in chat on 2026-03-24.

## C-093
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Process official Music4All contact-page references, download and place paper/slide artifacts in thesis resource folders, and establish a dedicated DS-001 raw-archive export target directory.
- reason: User requested that all provided Music4All references be processed and moved to the correct locations and asked for an exact destination for exporting the provider zip archive.
- evidence_basis: Contact page content at `https://sites.google.com/view/contact4music4all`; downloaded local files `music4all_slide.pdf` and contact-site paper copy; hash comparison against existing paper copy; created raw drop-zone guide in `06_data_and_sources/music4all_raw/README.md`.
- affected_components: `10_resources/dataset_docs/music4all/music4all_slide.pdf`, `10_resources/papers/Pegoraro Santana et al. - 2020 - Music4All A New Music Database and Its Applications (contact-site copy).pdf`, `06_data_and_sources/music4all_raw/README.md`, `06_data_and_sources/dataset_registry.md`, `06_data_and_sources/source_adapter_notes.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Centralizes DS-001 supporting references, improves provenance traceability, and removes ambiguity about where provider-delivered archives should be stored.
- approval_record: Requested by user in chat on 2026-03-24.

## C-094
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Complete pre-chat-switch operational closure for website ingestion by executing a full Spotify export rerun, verifying artifact freshness and counts, performing endpoint/runtime health checks, and recording the active local launch context.
- reason: User requested a final "log everything" pass before switching chats, requiring explicit traceability of the latest ingestion state and website operability.
- evidence_basis: Full run completed with `run_id=SPOTIFY-EXPORT-20260323-225206-071342` and updated `spotify_export_run_summary.json` counts (top short 602, medium 3029, long 5114, saved 171, playlists 4, playlist_items 31). Follow-up health check confirmed `import.html` 200, `profile_basis.html` 200, API status 200/idle. Local server relaunch validated on `http://127.0.0.1:5501/` after detecting server-not-running state on the prior port.
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_export_run_summary.json`, `07_implementation/website.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Leaves a clean, auditable handoff point with confirmed ingest freshness, known runtime URL, and no open website-operability blocker.
- approval_record: Requested and confirmed by user in chat on 2026-03-24.

## C-095
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Correct DS-001 access documentation to mark the newly delivered package as base Music4All (normal), not Music4All-Onion, and update raw archive naming guidance accordingly.
- reason: User clarified that the provider-delivered dataset is Music4All normal/base; recent notes had carried forward Onion wording in the release-target and filename example.
- evidence_basis: User clarification in chat on 2026-03-24; synchronized edits in `06_data_and_sources/dataset_registry.md`, `06_data_and_sources/source_adapter_notes.md`, and `06_data_and_sources/music4all_raw/README.md`.
- affected_components: `06_data_and_sources/dataset_registry.md`, `06_data_and_sources/source_adapter_notes.md`, `06_data_and_sources/music4all_raw/README.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Removes artifact-type ambiguity and prevents mislabeling the downloaded archive in provenance records.
- approval_record: Requested by user in chat on 2026-03-24.

## C-096
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Move `spotify_resilience.py` from the incorrect `07_implementation/` root level to `07_implementation/implementation_notes/bl001_bl002_ingestion/`; fix the broken `sys.path` import hack in `spotify_client.py` with a proper relative import; remove stale root-level pycache entry.
- reason: `spotify_resilience.py` had been deposited at the `07_implementation/` root during earlier website-integration work. `spotify_client.py` compensated via `sys.path.insert(0, str(Path(__file__).resolve().parents[2]))` — a fragile hack inconsistent with the rest of the ingestion package's relative-import pattern. User observed an unexpected top-level file and an audit confirmed the misplacement.
- evidence_basis: Recursive directory listing of `07_implementation/`; `Test-Path` confirmation the file existed at root level; `spotify_client.py` diff (sys.path block removed, replaced with `from .spotify_resilience import CacheDB`); post-fix import verification (`RESILIENCE_AVAILABLE=True`).
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/spotify_resilience.py` (destination after move), `07_implementation/implementation_notes/bl001_bl002_ingestion/spotify_client.py` (import fixed), `07_implementation/__pycache__/spotify_resilience.cpython-314.pyc` (removed — stale from old root-level path), `00_admin/change_log.md`
- impact_assessment: Medium-positive. Removes a fragile path-manipulation hack, restores package import consistency, eliminates a confusing root-level stray file, and cleans stale bytecode.
- approval_record: Requested by user ("log all this") in chat on 2026-03-24.

## C-097
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Remove unsupported Spotify endpoints (`/recommendations`, top artists) from ingestion/export/API/UI flows; restructure Profile Basis to match import-page shell; prioritize full export data on Profile Basis; add playlist/item visibility safeguards and messaging when no playlist tracks are ingested.
- reason: User requested removal of unsupported endpoints, asked for Profile Basis structure parity with Import, and raised mismatch concerns when playlists appeared without usable ingested playlist-track rows.
- evidence_basis: End-to-end code removals in exporter, API server, schema/docs, and website controls; refreshed export runs (`SPOTIFY-EXPORT-20260324-010411-637251`, `SPOTIFY-EXPORT-20260324-011716-200279`); diagnostics checks returned no errors for touched files; local page health checks returned 200 for import/profile pages.
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`, `07_implementation/implementation_notes/bl001_bl002_ingestion/spotify_mapping.py`, `07_implementation/implementation_notes/bl001_bl002_ingestion/spotify_artifacts.py`, `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/spotify_schema_reference.md`, `07_implementation/setup/website_api_server.py`, `07_implementation/website/import.html`, `07_implementation/website/app.js`, `07_implementation/website/profile_basis.html`, `07_implementation/website/profile_basis.js`, `07_implementation/website/style.css`, `07_implementation/website.md`, `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/*`, `00_admin/change_log.md`
- impact_assessment: High-positive. Aligns UI/runtime capabilities with supported API behavior, reduces operator confusion around unavailable playlist-item payloads, and improves handoff clarity with explicit visibility rules.
- approval_record: Requested and iteratively confirmed by user in chat on 2026-03-24.

## C-098
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Adopt Music4All base (raw) as the primary candidate corpus for the thesis pipeline; run full schema audit of the extracted archive; create `ds_001_music4all_information_sheet.md`; update `.gitignore` to exclude the raw archive; clarify that the Onion extension is separate and unmerged.
- reason: User received the Music4All base archive from the research team, confirmed the export completed, and decided to use it as the main corpus going forward. The dataset provides 109,269 tracks with Spotify-native audio features and `spotify_id` for direct alignment — a significant improvement over the DS-002 fallback (9,330-track MSD/Last.fm intersection requiring fuzzy matching). The Onion-enriched version is not available; only the raw base was provided.
- evidence_basis: Live inspection of all 6 CSVs: row counts (109,269 per track file, 5,109,592 listening events), confirmed column headers, 3 sample rows each. `Test-Path` confirmation for Onion `.tsv.bz2` files in `10_resources/datasets/music4all_onion/selected/` — present but unmerged. `git status` verified `music4all_raw/` excluded after `.gitignore` update.
- affected_components: `06_data_and_sources/ds_001_music4all_information_sheet.md` (created — full schema reference for all 6 CSVs), `06_data_and_sources/dataset_registry.md` (DS-001 section updated with confirmed schema), `06_data_and_sources/source_adapter_notes.md` (updated), `.gitignore` (added `06_data_and_sources/music4all_raw/` directory rule), `00_admin/change_log.md`
- impact_assessment: High-positive. Establishes a 109k-track corpus with direct Spotify ID alignment, eliminating the fuzzy-match dependency of DS-002. Pipeline scoring is fully compatible with the 7 Spotify-native audio features present in `id_metadata.csv`. Marks a corpus strategy decision point for the thesis MVP.
- approval_record: User confirmed adoption ("i want to use this from now on") in chat on 2026-03-24.

## C-099
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Confirm Music4All base (raw) as sufficient for the current implementation phase; continue building on base-only DS-001 and keep Onion as deferred optional enrichment.
- reason: User explicitly confirmed the current project direction is to proceed with the available Music4All base release without introducing Onion integration complexity at this stage.
- evidence_basis: User instruction in chat: "for now musi4all base version is sufficient so ill build on that." Existing DS-001 base schema and compatibility were already verified in prior checks and documented in `06_data_and_sources/ds_001_music4all_information_sheet.md`.
- affected_components: `00_admin/change_log.md`
- impact_assessment: Medium-positive. Locks short-term scope, reduces integration risk, and preserves delivery momentum while keeping Onion integration available for future controlled enhancement.
- approval_record: Requested directly by user in chat on 2026-03-24.

## C-100
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Add a comprehensive BL-001 current-state governance audit log that consolidates completion status, contract scope, evidence links, drift check, risk snapshot, and bounded next actions.
- reason: User requested confirmation that BL-001 is coherent and up to date, plus a standalone comprehensive log explicitly describing BL-001 current state.
- evidence_basis: Newly created audit artifact `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/bl001_state_log_2026-03-24.md`, plus reconciled references to `07_implementation/backlog.md`, `06_data_and_sources/schema_notes.md`, and `07_implementation/implementation_notes/bl001_bl002_ingestion/bl001_spotify_input_output_mapping.md`.
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/bl001_state_log_2026-03-24.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Improves governance traceability and reduces ambiguity about BL-001 current truth without changing runtime behavior.
- approval_record: Requested and confirmed by user in chat on 2026-03-24.

## C-101
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Add a comprehensive BL-002 current-state governance audit log consolidating implementation scope, active runtime evidence, artifact inventory, contract-vs-practice check, and bounded follow-up actions.
- reason: User requested a BL-002 file matching the comprehensive BL-001 state-log style and asked to formalize it in governance tracking.
- evidence_basis: Newly created audit artifact `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/bl002_state_log_2026-03-24.md`, reconciled against `07_implementation/backlog.md`, `07_implementation/implementation_notes/bl001_bl002_ingestion/ingest_history_parser.py`, `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`, and latest run summary `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_export_run_summary.json`.
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/bl002_state_log_2026-03-24.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Strengthens BL-002 traceability and confirms stage readiness with current evidence while keeping scope unchanged.
- approval_record: Requested and confirmed by user in chat on 2026-03-24.

## C-102
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Add and fully populate a comprehensive BL-003 current-state governance audit log with concrete run evidence, including input/output hashes, source counts, match/unmatched distribution, schema fields, derived rates, and known-risk notes.
- reason: User requested a comprehensive BL-003 log and then asked to fill it in with complete, run-specific details rather than placeholders.
- evidence_basis: Newly created and populated audit artifact `07_implementation/implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md`, reconciled against `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`, `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_summary.json`, `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_unmatched.csv`, and `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_matched_events.jsonl`.
- affected_components: `07_implementation/implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Closes BL-003 governance documentation debt, improves auditability and reproducibility evidence quality, and clarifies current alignment coverage limits without changing runtime pipeline behavior.
- approval_record: Requested and confirmed by user in chat on 2026-03-24.

## C-103
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Add a comprehensive BL-004 current-state governance audit log populated with concrete profile-run evidence, including BL-003 dependency hash linkage, semantic profile distributions, trace/output hashes, schema inventory, and current-mode constraints.
- reason: User requested BL-004 state coverage in the same comprehensive style as BL-001/BL-002/BL-003 and confirmed creation of the full log.
- evidence_basis: Newly created audit artifact `07_implementation/implementation_notes/bl004_profile/bl004_state_log_2026-03-24.md`, reconciled against `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_profile_summary.json`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_seed_trace.csv`, and BL-003 seed input `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_seed_table.csv`.
- affected_components: `07_implementation/implementation_notes/bl004_profile/bl004_state_log_2026-03-24.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Improves BL-004 traceability and reproducibility confidence by consolidating current run truth, dependency integrity, and profile-mode limitations without altering runtime behavior.
- approval_record: Requested and confirmed by user in chat on 2026-03-24.

## C-104
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Upgrade BL-004 from semantic-only to hybrid semantic+numeric profiling by joining DS-001 candidate numeric features, computing weighted feature centers, regenerating profile artifacts, and synchronizing BL-004 state documentation.
- reason: User asked whether BL-004 should also use numeric features and confirmed implementation.
- evidence_basis: Updated `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`; rerun outputs with `run_id=BL004-PROFILE-20260324-162651-244574`; populated numeric centers in `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json` and `bl004_profile_summary.json` (`danceability=0.555574`, `energy=0.597315`, `valence=0.553242`, `tempo=120.793962`); refreshed artifact hashes and updated BL-004 state log.
- affected_components: `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_profile_summary.json`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_seed_trace.csv`, `07_implementation/implementation_notes/bl004_profile/bl004_state_log_2026-03-24.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Preserves semantic preference signals while adding numeric profile structure for downstream hybrid ranking and controllability experiments, with full backward-compatible artifact continuity.
- approval_record: Requested and confirmed by user in chat on 2026-03-24.

## C-105
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Refactor the BL-003 to BL-004 boundary so BL-003 emits a single enriched seed-table artifact containing DS-001 numeric feature columns, and simplify BL-004 to consume only that enriched BL-003 output with no separate DS-001 runtime join.
- reason: User asked whether embedding numeric enrichment into BL-003 would be a better long-term design and then approved implementation to keep BL-004 dependent on a single upstream artifact.
- evidence_basis: Updated `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py` to write numeric columns into `bl003_ds001_spotify_seed_table.csv`; updated `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py` to remove the separate DS-001 candidate-data join and read numeric values directly from BL-003 seed rows; regenerated outputs with `BL-003-DS001-spotify-seed-build` timestamp `2026-03-24T17:55:16Z` and `BL004-PROFILE-20260324-175523-224833`; refreshed BL-003 and BL-004 state logs.
- affected_components: `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`, `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_seed_table.csv`, `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_summary.json`, `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_profile_summary.json`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_seed_trace.csv`, `07_implementation/implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl004_profile/bl004_state_log_2026-03-24.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Improves artifact-boundary clarity, reduces downstream join complexity, strengthens reproducibility by making BL-003 the single upstream contract for BL-004, and keeps future ingestion extensibility manageable by localizing enrichment at the aligned canonical-seed layer.
- approval_record: Requested and confirmed by user in chat on 2026-03-24.

## C-106
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Correct BL-004 musical-key aggregation by replacing arithmetic averaging with weighted circular mean on the 12-semitone wheel, regenerate BL-004 outputs, and refresh governance evidence to reflect the corrected numeric center.
- reason: User selected the BL-004 normalization review recommendation to fix `key` first before proceeding to BL-005 and BL-006, because arithmetic averaging produced a musically invalid center across the pitch-class wrap-around boundary.
- evidence_basis: Updated `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py` to compute circular key aggregates; regenerated outputs with `run_id=BL004-PROFILE-20260324-180708-238627`; refreshed `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json` showing `diagnostics.key_aggregation_method=weighted_circular_mean` and `numeric_feature_profile.key=0.337536`; updated `07_implementation/implementation_notes/bl004_profile/bl004_state_log_2026-03-24.md` with new hashes and run evidence.
- affected_components: `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_profile_summary.json`, `07_implementation/implementation_notes/bl004_profile/outputs/bl004_seed_trace.csv`, `07_implementation/implementation_notes/bl004_profile/bl004_state_log_2026-03-24.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Removes a mathematically incorrect aggregation on a circular musical dimension, improves downstream comparability for key-based retrieval/scoring, and brings BL-004 profile construction into line with the pipeline's existing circular key-distance logic.
- approval_record: Requested and confirmed by user in chat on 2026-03-24.

## C-107
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Align BL-005 and BL-006 with the current BL-004 hybrid profile contract by removing stale `loudness` dependence, activating only shared comparable numeric dimensions, mapping candidate `duration` to profile `duration_ms`, and regenerating downstream retrieval/scoring outputs.
- reason: After the BL-004 hybrid-profile and circular-key fixes, BL-005 and BL-006 still reflected an older DS-002-era assumption set and were not consuming the current comparable numeric features correctly.
- evidence_basis: Updated `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py` and `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`; reran BL-005 with `run_id=BL005-FILTER-20260324-181111-514436` and BL-006 with `run_id=BL006-SCORE-20260324-181112-418794`; refreshed diagnostics now show active numeric mappings `{tempo->tempo, key->key, mode->mode, duration_ms->duration}` and removed inactive `loudness` handling.
- affected_components: `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`, `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_filtered_candidates.csv`, `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_decisions.csv`, `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_diagnostics.json`, `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json`, `00_admin/change_log.md`
- impact_assessment: High-positive. Restores downstream contract consistency after BL-004 modernization, ensures retrieval and scoring use only defensible cross-stage numeric comparisons, and removes a silent fallback path that previously left BL-006 effectively semantic-only.
- approval_record: Requested by user in chat on 2026-03-24 as the next step after the BL-004 key-aggregation fix.

## C-108
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Harden BL-005 retrieval selectivity by replacing the permissive numeric-only keep path with a semantic-first rule (`semantic_score >= 2` or `semantic_score >= 1` with numeric support), add explicit decision-path diagnostics, rerun BL-005, and refresh BL-006 on the tightened candidate subset.
- reason: User requested that BL-005 be improved end to end. The current rule was retaining too many candidates because semantic-zero rows could still pass on weak numeric agreement alone.
- evidence_basis: Updated `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`; reran BL-005 with `run_id=BL005-FILTER-20260324-182142-419959` and BL-006 with `run_id=BL006-SCORE-20260324-182143-804380`; new diagnostics show `kept_candidates=1938` versus the prior `6604`, with `reject_numeric_without_semantic_support=6877` and new decision-path audit counts recorded.
- affected_components: `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`, `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_filtered_candidates.csv`, `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_decisions.csv`, `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_diagnostics.json`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json`, `07_implementation/test_notes.md`, `07_implementation/experiment_log.md`, `07_implementation/backlog.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Restores BL-005 as a real retrieval filter rather than a broad numeric pass-through, improves auditability of keep/reject pathways, and preserves downstream scoring continuity on a substantially narrower candidate set.
- approval_record: Requested by user in chat on 2026-03-24 ("improve it. plan, implement test, and log everythibg").

## C-109
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Retune BL-006 scoring weights to modestly increase numeric influence (`tempo`, `duration_ms`, `key`, `mode`) and reduce semantic overlap pressure from `genre_overlap` and `tag_overlap`, then regenerate the scoring outputs on the hardened BL-005 candidate set.
- reason: After BL-005 hardening, BL-006 top-ranked rows remained overly semantic-dominated. A bounded retune was needed to better balance comparable numeric evidence without destabilizing the ranked output set.
- evidence_basis: Updated `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`; reran BL-006 with `run_id=BL006-SCORE-20260324-182702-117298`; top-100 average numeric contribution increased from `0.162864` to `0.216824` while top-10 ranking overlap with the prior run remained `9/10`; refreshed hashes recorded in `07_implementation/test_notes.md` and `07_implementation/experiment_log.md`.
- affected_components: `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json`, `07_implementation/test_notes.md`, `07_implementation/experiment_log.md`, `07_implementation/backlog.md`, `00_admin/change_log.md`
- impact_assessment: Medium-to-high positive. Improves balance between semantic and numeric evidence in final ranking while preserving output stability and keeping the scoring stage deterministic.
- approval_record: Continued by user approval in chat on 2026-03-24 after the BL-005 hardening pass.

## C-110
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Migrate BL-003 to BL-006 semantic contract to DS-001-only by adding BL-003 selected-source completeness checks from BL-002 summary metadata and replacing BL-005/BL-006 DS-002 `tags_json` parsing with DS-001 `tags` and `genres` column parsing.
- reason: User requested that BL-003 align all raw Spotify evidence chosen at ingestion and that DS-002 `tags_json` no longer be used because active pipeline scope is DS-001-only.
- evidence_basis: Updated `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py` with selected-source validation; updated `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py` and `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py` to parse DS-001 semantic columns and resolve `duration_ms` mapping; reran BL-003, BL-004, BL-005 (`run_id=BL005-FILTER-20260324-183958-225058`), and BL-006 (`run_id=BL006-SCORE-20260324-184028-117165`) successfully.
- affected_components: `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`, `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_summary.json`, `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`, `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_filtered_candidates.csv`, `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_diagnostics.json`, `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json`, `07_implementation/test_notes.md`, `07_implementation/experiment_log.md`, `07_implementation/backlog.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Removes DS-002 semantic dependency from active retrieval/scoring, makes BL-003 alignment stricter with respect to selected ingestion evidence, and restores stage-contract consistency for DS-001-only execution.
- approval_record: Requested by user in chat on 2026-03-24.

## C-111
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Standardize BL-001 through BL-005 state logs into a common comprehensive format, refresh BL-003 and BL-004 evidence to latest DS-001-only reruns, and create missing BL-005 state log with current diagnostics and hashes.
- reason: User requested that BL-001 to BL-005 logs be similar and comprehensive so stage status and evidence can be audited consistently.
- evidence_basis: Updated `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/bl001_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/bl002_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl004_profile/bl004_state_log_2026-03-24.md`; created `07_implementation/implementation_notes/bl005_retrieval/bl005_state_log_2026-03-24.md`; all entries now include aligned sections (purpose, contract, run evidence, hashes, risks, conclusions).
- affected_components: `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/bl001_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/bl002_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl004_profile/bl004_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl005_retrieval/bl005_state_log_2026-03-24.md`, `00_admin/change_log.md`
- impact_assessment: Medium-to-high positive. Improves governance readability and reduces audit friction by making BL-stage state evidence structure uniform.
- approval_record: Requested by user in chat on 2026-03-24.

## C-112
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Reclassify BL-003 unmatched-event coverage and BL-002 external API dependency items as accepted operational constraints in stage state logs, and keep focus on remaining active issues.
- reason: User explicitly confirmed that DS-001 coverage-driven unmatched Spotify events are expected and that BL-002 external dependency risk is acceptable.
- evidence_basis: Updated risk/constraint wording in `07_implementation/implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md` and `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/bl002_state_log_2026-03-24.md` to mark both items as accepted constraints rather than unresolved defects.
- affected_components: `07_implementation/implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md`, `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/bl002_state_log_2026-03-24.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Reduces governance ambiguity by separating accepted constraints from active remediation items.
- approval_record: Confirmed by user in chat on 2026-03-24.

## C-113
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Add BL-006 component-balance diagnostics (all candidates, top-100, top-500) to scoring summary output, rerun BL-006, and create a comprehensive BL-006 state log aligned with BL-001 to BL-005 documentation structure.
- reason: User confirmed work should continue on BL-006 and needed clear visibility into what BL-006 currently does and how numeric-versus-semantic contributions behave in ranked outputs.
- evidence_basis: Updated `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py` to emit `component_balance`; reran BL-006 with `run_id=BL006-SCORE-20260324-185938-252856`; produced refreshed outputs and hashes; created `07_implementation/implementation_notes/bl006_scoring/bl006_state_log_2026-03-24.md` with run evidence and diagnostics interpretation.
- affected_components: `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json`, `07_implementation/implementation_notes/bl006_scoring/bl006_state_log_2026-03-24.md`, `00_admin/change_log.md`
- impact_assessment: Medium-to-high positive. Improves BL-006 observability for evidence-based retuning while preserving deterministic scoring behavior.
- approval_record: Confirmed by user in chat on 2026-03-24.

## C-114
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Apply a bounded BL-006 weight retune to increase numeric contribution and reduce semantic-overlap pressure, rerun scoring, and update BL-006 state evidence with before/after comparison metrics.
- reason: User confirmed continuation on BL-006. New component-balance diagnostics showed top-ranked segments still semantic-leading, so a controlled retune was executed to improve numeric influence while preserving ranking stability.
- evidence_basis: Updated `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py` weights to `{tempo:0.20, duration_ms:0.13, key:0.13, mode:0.09, lead_genre:0.17, genre_overlap:0.12, tag_overlap:0.16}`; baseline artifacts preserved as `bl006_scored_candidates_pre_retune.csv` and `bl006_score_summary_pre_retune.json`; reran BL-006 with `run_id=BL006-SCORE-20260324-190145-197533`; observed `top10_overlap=9/10`; top-100 mean contributions shifted from numeric `0.310008` / semantic `0.362157` to numeric `0.384627` / semantic `0.292601`.
- affected_components: `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates_pre_retune.csv`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary_pre_retune.json`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv`, `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json`, `07_implementation/implementation_notes/bl006_scoring/bl006_state_log_2026-03-24.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Improves numeric-vs-semantic balance in top-ranked outputs while retaining high ranking continuity.
- approval_record: Confirmed by user in chat on 2026-03-24.

## C-115
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Add a BL-006 top-50 quality snapshot artifact and align BL-006 risk wording to reflect post-retune numeric-leading behavior with remaining genre-concentration risk.
- reason: User confirmed continuation on BL-006 after retune; a compact quality snapshot was needed to inspect upper-rank behavior before deciding on additional tuning.
- evidence_basis: Computed top-50 distribution and contribution metrics from `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv`; created `07_implementation/implementation_notes/bl006_scoring/bl006_top50_quality_snapshot_2026-03-24.md`; updated constraints wording in `07_implementation/implementation_notes/bl006_scoring/bl006_state_log_2026-03-24.md` to replace semantic-dominance risk with concentration-focused risk.
- affected_components: `07_implementation/implementation_notes/bl006_scoring/bl006_top50_quality_snapshot_2026-03-24.md`, `07_implementation/implementation_notes/bl006_scoring/bl006_state_log_2026-03-24.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Improves BL-006 monitoring clarity and better targets remaining quality risk.
- approval_record: Confirmed by user in chat on 2026-03-24.

## C-116
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Finalize BL-006 before BL-007 handoff by adding a closure-gate experiment record and test case, and synchronizing backlog evidence references to the current post-retune scoring baseline.
- reason: User requested that BL-006 be finished and fully logged before moving to BL-007.
- evidence_basis: Added `EXP-035` to `07_implementation/experiment_log.md` with closure metrics/hashes and handoff recommendation; added `TC-BL006-FINAL-001` to `07_implementation/test_notes.md` validating stability (`top10_overlap_vs_pre_retune=9/10`) and numeric-led top-100 contribution (`0.384627 > 0.292601`); updated BL-006 done-note in `07_implementation/backlog.md` to reference final closure evidence.
- affected_components: `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/backlog.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Establishes a clear BL-006 closure baseline and removes governance ambiguity before BL-007 execution.
- approval_record: Requested by user in chat on 2026-03-24.

## C-117
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Refresh BL-007 playlist assembly against the finalized BL-006 baseline, regenerate playlist artifacts, and synchronize implementation/test/backlog/state evidence before moving downstream.
- reason: User requested BL-007 status after BL-006 closure; current BL-007 outputs were identified as stale relative to the latest BL-006 run and required a refresh for contract alignment.
- evidence_basis: Reran `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py` with `run_id=BL007-ASSEMBLE-20260324-195257-583625`; generated refreshed outputs (`bl007_playlist.json`, `bl007_assembly_trace.csv`, `bl007_assembly_report.json`) with BL-006 input hash `189C3DCF575D69736CFD855CE5D456AB5C391AD58EA20DEA803A216D35F8CE7C`; added `EXP-036`, `TC-BL007-REFRESH-001`, backlog done-note refresh, and `bl007_state_log_2026-03-24.md`.
- affected_components: `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`, `07_implementation/implementation_notes/bl007_playlist/outputs/bl007_playlist.json`, `07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_trace.csv`, `07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_report.json`, `07_implementation/implementation_notes/bl007_playlist/bl007_state_log_2026-03-24.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/backlog.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Restores BL-007 evidence currency and ensures downstream stages consume playlist artifacts aligned with the finalized scoring baseline.
- approval_record: Requested by user in chat on 2026-03-24.

## C-118
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Refresh BL-008 transparency outputs on the finalized BL-006 and refreshed BL-007 baseline, including a contract-alignment fix that replaces stale DS-002-era hardcoded component mapping with dynamic active-component extraction.
- reason: User requested execution of the first artefact next step (BL-008 refresh). Existing BL-008 script mapping still referenced outdated component assumptions and needed alignment to current BL-006 scoring features.
- evidence_basis: Updated `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py` to derive breakdown components from BL-006 `active_component_weights`; reran BL-008 with `run_id=BL008-EXPLAIN-20260324-195641-957331`; regenerated `bl008_explanation_payloads.json` and `bl008_explanation_summary.json` with current BL-006/BL-007 input hashes; added `EXP-037`, `TC-BL008-REFRESH-001`, backlog done-note refresh, and `bl008_state_log_2026-03-24.md`.
- affected_components: `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`, `07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_payloads.json`, `07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_summary.json`, `07_implementation/implementation_notes/bl008_transparency/bl008_state_log_2026-03-24.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/backlog.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Restores transparency-contract correctness and ensures explanation artifacts are auditable against current scoring and playlist baselines.
- approval_record: Requested by user in chat on 2026-03-24.

## C-119
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Refresh BL-009 observability outputs to capture the updated BL-006, BL-007, and BL-008 run chain and synchronize state/experiment/test/backlog evidence.
- reason: User requested continuation of artefact next steps after BL-008 refresh. Observability needed to be regenerated so run metadata reflects the current stage-chain baseline.
- evidence_basis: Reran `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py` with `run_id=BL009-OBSERVE-20260324-195859-875091`; regenerated `bl009_run_observability_log.json` and `bl009_run_index.csv`; confirmed upstream run IDs (`BL006-SCORE-20260324-190145-197533`, `BL007-ASSEMBLE-20260324-195257-583625`, `BL008-EXPLAIN-20260324-195641-957331`) and consistent counts (`kept_candidates=56700`, `candidates_scored=56700`, `playlist_length=10`, `explanation_count=10`); added `EXP-038`, `TC-BL009-REFRESH-001`, backlog done-note refresh, and `bl009_state_log_2026-03-24.md`.
- affected_components: `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`, `07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_observability_log.json`, `07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_index.csv`, `07_implementation/implementation_notes/bl009_observability/bl009_state_log_2026-03-24.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/backlog.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Restores observability currency and provides a coherent run-chain baseline for reproducibility refresh work.
- approval_record: Requested by user in chat on 2026-03-24.

## C-120
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Refresh BL-010 reproducibility artifacts and governance records on the updated BL-006 through BL-009 baseline, including a new stage state log and refreshed hash evidence.
- reason: User approved progression to step 3 of the artefact sequence, requiring BL-010 rerun and full log synchronization after BL-009 refresh.
- evidence_basis: Reran `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py` with `run_id=BL010-REPRO-20260324-200214`; deterministic replay result remained pass (`deterministic_match=true`, `first_mismatch_artifact=null`) across three replays; regenerated `bl010_reproducibility_report.json`, `bl010_reproducibility_run_matrix.csv`, and `bl010_reproducibility_config_snapshot.json`; recorded `EXP-039`, `TC-BL010-REFRESH-001`, backlog done-note refresh, and new `bl010_state_log_2026-03-24.md`.
- affected_components: `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_report.json`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_run_matrix.csv`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_config_snapshot.json`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/replay_01/`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/replay_02/`, `07_implementation/implementation_notes/bl010_reproducibility/outputs/replay_03/`, `07_implementation/implementation_notes/bl010_reproducibility/bl010_state_log_2026-03-24.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/backlog.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Confirms deterministic reproducibility on the current baseline and keeps thesis governance/evidence chain synchronized end to end.
- approval_record: Requested by user in chat on 2026-03-24.

## C-121
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Harden the website interaction flow by adding cancellable Spotify ingestion runs, explicit stale-snapshot controls, and temporary Bootstrap 5 page scaffolding to accelerate UI iteration while preserving existing app logic.
- reason: User requested continuing quality improvements and explicitly approved use of premade CSS/JS to make development easier before a later rewrite.
- evidence_basis: Implemented `/api/spotify/export/cancel` and cancellation-state handling in `07_implementation/setup/website_api_server.py`; validated start -> status -> cancel -> status transitions via local API calls; added import/profile clear/refresh controls and precedence messaging in `07_implementation/website/app.js` and `07_implementation/website/profile_basis.js`; added Bootstrap 5 CDN assets to `07_implementation/website/import.html`, `07_implementation/website/profile_basis.html`, and `07_implementation/website/index.html`; diagnostics checks reported no file errors on touched HTML/JS/CSS files.
- affected_components: `07_implementation/setup/website_api_server.py`, `07_implementation/website/import.html`, `07_implementation/website/profile_basis.html`, `07_implementation/website/index.html`, `07_implementation/website/app.js`, `07_implementation/website/profile_basis.js`, `07_implementation/website/style.css`, `07_implementation/website.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Improves operational control and recoverability in website-driven ingestion, reduces stale-data confusion, and speeds frontend delivery with a temporary framework layer without changing core recommendation behavior.
- approval_record: Requested and confirmed by user in chat on 2026-03-24.

## C-122
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Replace the minimal website plan with a comprehensive end-to-end website blueprint covering control model, transparency model, full page architecture, frontend/backend module structure, API contracts, state contracts, testing strategy, evidence hooks, and phased delivery plan for running the generator from the website.
- reason: User requested a complete, comprehensive structure plan that maximizes user control and transparency and enumerates all required files to operate the generator through the website UI.
- evidence_basis: Added `Comprehensive Website Blueprint (v2)` section in `07_implementation/website.md` with architecture, flow, control surfaces, transparency surfaces, API contract targets, detailed file/module plan, recovery model, and definition of done.
- affected_components: `07_implementation/website.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Establishes a complete implementation blueprint that reduces ambiguity, improves execution sequencing, and provides an auditable structure for website-to-generator integration.
- approval_record: Requested by user in chat on 2026-03-24.

## C-123
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Implement Phase B scaffold for website-driven generator execution by adding pipeline run API endpoints, stage orchestration backend, a dedicated Run Generator page, and cross-page navigation linking import/profile/run flow.
- reason: User approved moving from planning to implementation and asked to proceed with the next step of scaffolding run-page and pipeline routes based on the comprehensive website blueprint.
- evidence_basis: Added pipeline endpoints and orchestration logic in `07_implementation/setup/website_api_server.py`; created `07_implementation/website/run.html` and `07_implementation/website/run.js`; added run-page links in `07_implementation/website/import.html`, `07_implementation/website/profile_basis.html`, and `07_implementation/website/index.html`; added run transparency styles in `07_implementation/website/style.css`; diagnostics reported no file errors on touched files.
- affected_components: `07_implementation/setup/website_api_server.py`, `07_implementation/website/run.html`, `07_implementation/website/run.js`, `07_implementation/website/import.html`, `07_implementation/website/profile_basis.html`, `07_implementation/website/index.html`, `07_implementation/website/style.css`, `07_implementation/website.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Converts the blueprint into executable website orchestration scaffolding and materially improves user control/transparency for generator runs from UI.
- approval_record: Requested and confirmed by user in chat on 2026-03-24.

## C-124
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Implement the next website execution steps by adding results inspection and run-history pages, extending pipeline API responses with compare-oriented artifact hashes and payload summaries, and enabling one-click evidence bundle export from the Run Generator page.
- reason: User requested execution of the immediate next steps after Phase B to complete control/transparency flow for using the generator from website UI.
- evidence_basis: Extended backend in `07_implementation/setup/website_api_server.py` with history/results/evidence-bundle endpoints and run-history persistence; created `07_implementation/website/results.html`, `07_implementation/website/results.js`, `07_implementation/website/history.html`, `07_implementation/website/history.js`; updated `07_implementation/website/run.html` and `07_implementation/website/run.js` with export-bundle action and navigation; diagnostics reported no file errors on touched files.
- affected_components: `07_implementation/setup/website_api_server.py`, `07_implementation/website/run.html`, `07_implementation/website/run.js`, `07_implementation/website/results.html`, `07_implementation/website/results.js`, `07_implementation/website/history.html`, `07_implementation/website/history.js`, `07_implementation/website/index.html`, `07_implementation/website.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Completes a practical website transparency loop (run -> inspect -> compare -> export evidence) and improves reproducibility-facing usability for thesis demonstrations.
- approval_record: Requested by user in chat on 2026-03-24.

## C-125
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Add per-stage controllability and transparency by introducing dedicated stage pages for BL-004 to BL-009, stage-specific UI controls, stage-filtered logs, and backend support for selected-stage execution via `stage_ids`.
- reason: User requested that each part of the run be controllable and transparent, preferably through separate HTML pages so users can interact with each stage independently.
- evidence_basis: Updated `07_implementation/setup/website_api_server.py` to validate and execute selected `stage_ids` plus expose `GET /api/pipeline/stages`; added `07_implementation/website/stage_page.js`; created `07_implementation/website/stage_bl004.html` through `stage_bl009.html`; updated `07_implementation/website/run.html` with direct links to each stage page; diagnostics reported no file errors on touched files.
- affected_components: `07_implementation/setup/website_api_server.py`, `07_implementation/website/run.html`, `07_implementation/website/stage_page.js`, `07_implementation/website/stage_bl004.html`, `07_implementation/website/stage_bl005.html`, `07_implementation/website/stage_bl006.html`, `07_implementation/website/stage_bl007.html`, `07_implementation/website/stage_bl008.html`, `07_implementation/website/stage_bl009.html`, `07_implementation/website.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Delivers stage-level interaction control and clearer operational transparency, reducing reliance on full-chain runs when targeted stage checks are needed.
- approval_record: Requested by user in chat on 2026-03-24.

## C-126
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Add stage-parameter tunability for BL-005 to BL-009 by wiring per-stage parameter overrides from dedicated stage pages through pipeline API `stage_params` into stage-script execution environments, with script-level override consumption for retrieval, scoring, playlist assembly, transparency, and observability builders.
- reason: User approved extending stage-level control beyond stage selection so each stage page can tune execution parameters while preserving transparency.
- evidence_basis: Updated `07_implementation/setup/website_api_server.py` to pass validated stage parameters into per-stage environment overrides; updated `07_implementation/website/stage_page.js` to render stage-specific parameter controls and submit `stage_params`; updated `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`, `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`, `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`, and `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py` to consume overrides.
- affected_components: `07_implementation/setup/website_api_server.py`, `07_implementation/website/stage_page.js`, `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`, `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`, `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`, `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`, `07_implementation/website.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Completes end-to-end per-stage tunability and makes stage pages materially useful for targeted what-if runs and transparent experimentation.
- approval_record: Requested by user in chat on 2026-03-24 (follow-up "yes" to stage-specific parameter controls).

## C-127
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Extend stage-parameter tunability to BL-004 so all stage pages BL-004 through BL-009 are tunable, including BL-004 profile limits and user-id controls via `stage_params`.
- reason: User approved adding BL-004 parameter controls after clarifying that BL-004 was still control-only.
- evidence_basis: Updated `07_implementation/website/stage_page.js` with BL-004 parameter definitions and string input handling; updated `07_implementation/setup/website_api_server.py` with BL-004 stage-param to env mapping; updated `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py` to consume `BL004_TOP_TAG_LIMIT`, `BL004_TOP_GENRE_LIMIT`, `BL004_TOP_LEAD_GENRE_LIMIT`, and `BL004_USER_ID`.
- affected_components: `07_implementation/website/stage_page.js`, `07_implementation/setup/website_api_server.py`, `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`, `07_implementation/website.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Removes the last stage-tunability gap and enables complete per-stage parameter control coverage across the pipeline UI.
- approval_record: Requested by user in chat on 2026-03-24 ("yes" to adding BL-004 parameter inputs).

## C-128
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Complete website hardening pass by adding runtime utility endpoints (`/api/health`, `/api/runtime/config`, `/api/runtime/config/validate`), surfacing health status on the Run page, adding stage-page parameter reset/preset controls, and creating an automated smoke script for contract checks.
- reason: User approved continuation after current-state analysis, and the next-step hardening items were utility observability endpoints, better stage-parameter UX, and automated regression checks.
- evidence_basis: Updated backend routes and validation logic in `07_implementation/setup/website_api_server.py`; added Run page health UI in `07_implementation/website/run.html` and `07_implementation/website/run.js`; added stage preset/reset controls in `07_implementation/website/stage_page.js`; added smoke automation script `07_implementation/setup/smoke_website_api.ps1`; implementation log updated in `07_implementation/website.md`.
- affected_components: `07_implementation/setup/website_api_server.py`, `07_implementation/website/run.html`, `07_implementation/website/run.js`, `07_implementation/website/stage_page.js`, `07_implementation/website/style.css`, `07_implementation/setup/smoke_website_api.ps1`, `07_implementation/website.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Improves operational transparency, reduces manual tuning friction on stage pages, and adds repeatable website API validation for faster confidence checks after changes.
- approval_record: Requested by user in chat on 2026-03-24 ("yes" to proceed with current recommended hardening actions).

## C-129
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Start website design rethink with a new IA + visual baseline: import-first workflow framing, control-room layout on Import page, and high-contrast technical design system refresh while preserving existing ingestion logic contracts.
- reason: User requested a rethink of the whole website design and selected a studio-control-room direction, full IA reboot scope, import-first baseline, and high-contrast technical tone.
- evidence_basis: Rebuilt Import page shell in `07_implementation/website/import.html`; applied new visual palette and control-shell styling in `07_implementation/website/style.css`; updated entrypoint language in `07_implementation/website/index.html`; implementation log entry added in `07_implementation/website.md`.
- affected_components: `07_implementation/website/import.html`, `07_implementation/website/style.css`, `07_implementation/website/index.html`, `07_implementation/website.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Establishes a coherent new design baseline without breaking current API wiring, enabling structured rollout of the same IA and visual language across Profile/Run/Results/History surfaces.
- approval_record: Requested by user in chat on 2026-03-24 ("i think we need to rethink the whole design of the website").

## C-130
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Synchronize governance state after BL-021 completion by updating backlog status, recording BL-003 scope-actuated alignment completion for the active DS-001 path, and extending BL-013 orchestration with optional one-command seed refresh (`--refresh-seed`) so source-scope runs can be executed from a single entrypoint flow.
- reason: User requested overall thesis-status clarification, and governance files were stale versus implemented/evidenced work (`EXP-040` to `EXP-042`, `TC-BL021-R2-001` to `TC-BL021-R2-003`).
- evidence_basis: BL-021 persistence + A/B evidence artifacts in `07_implementation/implementation_notes/bl000_run_config/probe_comparison_outputs/`; BL-003 scope manifest `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_source_scope_manifest.json`; BL-013 refresh-seed smoke run `BL013-ENTRYPOINT-20260324-221334-097740` recorded in entrypoint outputs.
- affected_components: `07_implementation/backlog.md`, `00_admin/thesis_state.md`, `00_admin/change_log.md`, `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`, `07_implementation/implementation_notes/bl013_entrypoint/bl013_run_command.md`
- impact_assessment: High-positive. Restores consistency between implementation reality and governance tracking, and reduces execution friction for scope-sensitive replay runs.
- approval_record: Requested and confirmed by user in chat on 2026-03-24 ("yes" to backlog/admin sync).

## C-131
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Clean and normalize the decision trail by introducing explicit supersession links for outdated planning decisions and adding a closure decision that records BL-021 source-scope implementation as completed baseline behavior.
- reason: User requested full decision-history cleanup so governance no longer shows stale deferred/freeze posture after BL-021 completion.
- evidence_basis: Updated `00_admin/decision_log.md` entries (`D-014`, `D-023`, `D-026`) to `status: superseded`; added `D-027` documenting closure of D-023 deferment and end of temporary freeze-first mode, aligned to `07_implementation/backlog.md` BL-021 done state and `00_admin/thesis_state.md` BL-021 completion section.
- affected_components: `00_admin/decision_log.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Improves governance clarity and removes contradictory decision posture without deleting historical context.
- approval_record: Requested by user in chat on 2026-03-24 ("yes look at my whole deision and make it clean").

## C-132
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Perform full `00_admin` governance cleanup and organization refresh by adding a control-hub index, fixing protocol numbering/schema drift, updating sprint/handoff status to current priorities, removing duplicated unresolved-item markup, and syncing timeline notes.
- reason: User requested an end-to-end admin-folder pass to analyze everything, clean up documentation, and make current control files up to date and organized.
- evidence_basis: Updated control-map index `00_admin/README.md`; protocol consistency fixes in `00_admin/operating_protocol.md`; sprint tracker updates in `00_admin/mentor_draft_7day_sprint_2026-03-23.md`; handoff priority refresh in `00_admin/handoff_friend_chat_playbook.md`; unresolved issues cleanup in `00_admin/unresolved_issues.md`; timeline freshness note in `00_admin/timeline.md`; mentor feedback log initialization in `00_admin/mentor_feedback_log.md`.
- affected_components: `00_admin/README.md`, `00_admin/operating_protocol.md`, `00_admin/mentor_draft_7day_sprint_2026-03-23.md`, `00_admin/handoff_friend_chat_playbook.md`, `00_admin/unresolved_issues.md`, `00_admin/timeline.md`, `00_admin/mentor_feedback_log.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Improves admin discoverability, removes stale collaborator guidance, and restores consistency across governance-control documents without rewriting historical decision/change content.
- approval_record: Requested by user in chat on 2026-03-24 ("analyze everything in admin folder, clean up, and make everything up to date and organized").

## C-133
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Apply second-pass governance normalization by standardizing ordering conventions in decision/change logs and reclassifying non-blocking mentor questions from open to deferred with explicit rationale notes.
- reason: User approved follow-up actions to improve log organization consistency and reduce false-active mentor backlog noise.
- evidence_basis: Added ordering-convention sections to `00_admin/decision_log.md` and `00_admin/change_log.md`; updated `00_admin/mentor_question_log.md` status checkpoint and set MQ-005/MQ-006/MQ-008 to deferred with bounded deferred reasons tied to current scope and access state.
- affected_components: `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/mentor_question_log.md`
- impact_assessment: Medium-positive. Improves control readability and operational prioritization while preserving full historical content.
- approval_record: Confirmed by user reply in chat on 2026-03-24 ("yes").

## C-134
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Add a compact "Latest Open Priorities" execution snapshot to `thesis_state.md` so current governance focus is visible from the primary state file.
- reason: User approved final polish to improve one-file visibility of active next actions.
- evidence_basis: Added prioritized open-item block to `00_admin/thesis_state.md` covering UI-008 closure, UI-003 closure, Day 4 to Day 7 sprint continuation, and bounded website hardening scope.
- affected_components: `00_admin/thesis_state.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Reduces control-friction by making active priorities immediately visible during session starts and status checks.
- approval_record: Confirmed by user reply in chat on 2026-03-24 ("yes").

## C-136
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Clean, organize, and bring `00_admin/change_log.md` up to date by resolving duplicate ID ambiguity, fixing misplaced approval metadata, and adding maintenance snapshot metadata for quicker log health checks.
- reason: User requested explicit cleanup and organization of the change log itself.
- evidence_basis: Duplicate heading `C-079` resolved by assigning unique ID `C-135` to the later Day 2 hardening entry; misplaced `approval_record` moved to `C-078`; maintenance snapshot added near top with highest-ID and correction context.
- affected_components: `00_admin/change_log.md`
- impact_assessment: High-positive. Restores unique ID integrity, reduces audit ambiguity, and improves maintainability without removing historical content.
- approval_record: Requested by user in chat on 2026-03-24 ("cleanup and organize and make up to date the change log").

## C-137
- date: 2026-03-24
- proposed_by: user + AI
- status: accepted
- change_summary: Clean and organize `00_admin/decision_log.md` by adding maintenance and current-posture snapshots, plus minor schema-normalization cleanup for supersession metadata formatting.
- reason: User requested that the decision log be cleaned, organized, and brought up to date.
- evidence_basis: Added top-of-file maintenance snapshot (highest ID, entry count, status distribution, duplicate-ID check) and active-posture summary reflecting current governance decisions (`D-015`, `D-021`, `D-025`, `D-027`); normalized `D-014` supersession field to one-line format (`superseded_by: D-015`).
- affected_components: `00_admin/decision_log.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Improves decision-log readability and operational status visibility while preserving full historical chronology.
- approval_record: Requested by user in chat on 2026-03-24 ("cleanup and organize and make up to date the decision log").

## C-138
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Clean, reorganize, and update `00_admin/Artefact_MVP_definition.md` to match the active implemented baseline (semantic enrichment path, DS-002 active corpus, and source-scope controllability contract).
- reason: User requested the artefact MVP definition to be cleaned, organized, and brought up to date.
- evidence_basis: Added document control and structured baseline sections; replaced outdated ISRC-first wording with current semantic-enrichment positioning aligned to `00_admin/thesis_state.md`; added source-scope controllability as mandatory functionality; refined acceptance criteria to include observability lineage requirements.
- affected_components: `00_admin/Artefact_MVP_definition.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Removes governance drift between MVP definition and active implementation state, improving consistency for execution and writing alignment.
- approval_record: Requested by user in chat on 2026-03-25 ("cleanup and organize and make up to date the artefat mvp definittion").

## C-139
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Clean, reorganize, and update `00_admin/timeline.md` to reflect current implementation/evidence posture, active package status, and closed vs open execution signals.
- reason: User requested the timeline to be cleaned, organized, and brought up to date.
- evidence_basis: Replaced outdated M2 ISRC-first wording with active semantic-enrichment alignment posture; updated package windows/status notes (`WP-CITE-001`, `WP-DRAFT-001`, `WP-WEBINT-001`); added Day 3 closure and Day 4 active notes; removed stale `BL-021` deferred reference after source-scope completion; added recently-closed section for UI-002 and BL-021 context.
- affected_components: `00_admin/timeline.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Restores timeline-state consistency with current governance records and improves day-to-day execution clarity.
- approval_record: Requested by user in chat on 2026-03-25 ("cleanup and organize and make up to date the timeline").

## C-140
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Clean, organize, and update `00_admin/thesis_state.md` by removing stale execution wording, clarifying active open priorities, and synchronizing data/execution notes with current governance state.
- reason: User requested `thesis_state.md` to be cleaned, organized, and brought up to date.
- evidence_basis: Added top-level document date stamp; updated implementation-state date and execution focus text; added DS-001 governance-pending note tied to UI-008; added priority-status checkpoint (UI-002 closed; UI-003/UI-008 open); added explicit BL-021 source-scope baseline section; refreshed Update Control reason block for 2026-03-25.
- affected_components: `00_admin/thesis_state.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Improves state-file accuracy as the primary governance reference and reduces ambiguity in current execution posture.
- approval_record: Requested by user in chat on 2026-03-25 ("cleanup and organize and make up to date the thesis state").

## C-141
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Clean, reorganize, and update `00_admin/unresolved_issues.md` by separating active vs resolved issues clearly, moving completed UI-002 out of active, and condensing long progress history into current actionable status blocks.
- reason: User requested unresolved-issues governance cleanup and currency update.
- evidence_basis: Added file-level date stamp; active section now contains only open UI-008 and UI-003 with concise impact/progress/next-action blocks; moved UI-002 to resolved with final audit outcome summary (`TOTAL_KEYS_WITH_WEAK=0`); split resolved items into recent vs historical for faster retrieval.
- affected_components: `00_admin/unresolved_issues.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Reduces control noise, removes stale-active ambiguity, and improves day-to-day issue triage clarity.
- approval_record: Requested by user in chat on 2026-03-25 ("cleanup and organize and make up to date the unresolved issues").

## C-142
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Complete remaining `00_admin` cleanup pass by updating stale metadata/status notes, aligning evaluation/protocol/template schemas with current implementation posture, and refreshing operational handoff/access tracking notes.
- reason: User requested cleanup, organization, and currency updates across all other admin files.
- evidence_basis: Updated `EP-ALIGN-001` in `00_admin/evaluation_plan.md` from outdated ISRC-first wording to semantic-enrichment/source-scope visibility metrics; added current metadata stamps in `00_admin/README.md`, `00_admin/methodology_definition.md`, `00_admin/thesis_scope_lock.md`, `00_admin/handoff_friend_chat_playbook.md`, and `00_admin/mentor_feedback_log.md`; refreshed `00_admin/mentor_question_log.md` checkpoint date; added 2026-03-24 credential-release status in `00_admin/music4all_access_email_draft_2026-03-21.md`; synchronized decision-status schema in `00_admin/operating_protocol.md` and `00_admin/templates/decision_entry.template.md`; added legacy-pointer note in `00_admin/C_080_day_3_hardening.txt`.
- affected_components: `00_admin/README.md`, `00_admin/evaluation_plan.md`, `00_admin/methodology_definition.md`, `00_admin/thesis_scope_lock.md`, `00_admin/handoff_friend_chat_playbook.md`, `00_admin/mentor_question_log.md`, `00_admin/mentor_feedback_log.md`, `00_admin/music4all_access_email_draft_2026-03-21.md`, `00_admin/operating_protocol.md`, `00_admin/templates/decision_entry.template.md`, `00_admin/C_080_day_3_hardening.txt`, `00_admin/change_log.md`
- impact_assessment: High-positive. Brings the remaining admin surface into state-consistent form and reduces stale wording/schema drift across planning, governance, and collaborator handoff artifacts.
- approval_record: Requested by user in chat on 2026-03-25 ("cleanup and organize and make up to date all the other files in my admin").

## C-143
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Analyze current implementation evidence and synchronize admin control files to DS-001 direct-alignment baseline while marking Last.fm enrichment as historical evidence only.
- reason: User requested implementation-grounded admin synchronization and explicitly confirmed current posture (`DS-001` active corpus; no active Last.fm usage).
- evidence_basis: `07_implementation/implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md`; `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`; `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py` (`lastfm_status=not_applicable_ds001`); updated admin control files in this change.
- affected_components: `00_admin/decision_log.md`, `00_admin/evaluation_plan.md`, `00_admin/thesis_scope_lock.md`, `00_admin/thesis_state.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Removes active-posture ambiguity between implementation and governance records and improves Chapter 4/5 interpretation consistency.
- approval_record: Requested by user in chat on 2026-03-25 ("alanlyze the current implementation and update any admin files to it.").

## C-144
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Execute full non-historical admin cleanup pass after implementation audit: remove duplicate/stale baseline wording, refresh open-control snapshots, align timeline milestone language to DS-001 direct alignment, and update mentor/email trackers to current operational status.
- reason: User requested an overall current-implementation analysis and asked that all admin files be updated accordingly.
- evidence_basis: Admin-surface audit against active stage evidence (`07_implementation/implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md`, BL-003/BL-004 scripts) plus targeted updates in README, timeline, MVP definition, mentor question log, and Music4All access tracker.
- affected_components: `00_admin/Artefact_MVP_definition.md`, `00_admin/README.md`, `00_admin/timeline.md`, `00_admin/music4all_access_email_draft_2026-03-21.md`, `00_admin/mentor_question_log.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Brings remaining operational admin documents into explicit alignment with the current DS-001 implementation posture while preserving historical logs.
- approval_record: Requested by user in chat on 2026-03-25 ("now analyze overall the implementation currently and update all the admin files to it.").

## C-145
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Synchronize governance wording with confirmed DS-001 possession by replacing residual "download in progress" phrasing and tightening UI-008 next actions to governance-capture tasks only.
- reason: User confirmed that Music4All DS-001 database is already available locally and asked for state alignment.
- evidence_basis: User confirmation in chat ("musi4all i already have the database that is ds-001."); updates applied to DS-001 delivery state in dataset registry and UI-008 action list in unresolved issues.
- affected_components: `06_data_and_sources/dataset_registry.md`, `00_admin/unresolved_issues.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Reduces operational ambiguity and keeps governance backlog focused on compliance/provenance closure rather than acquisition status.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.

## C-146
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Close UI-008 as an active unresolved issue and synchronize admin control snapshots so only UI-003 remains open in current-priority surfaces.
- reason: User explicitly requested removal of the unresolved DS-001 governance item ("lose the unresolved issue its not an issue anymore").
- evidence_basis: User confirmation in chat that DS-001 governance gating should no longer remain in unresolved-issue active posture; admin control files updated to reflect UI-003 as the sole active unresolved control item at that checkpoint.
- affected_components: `00_admin/unresolved_issues.md`, `00_admin/thesis_state.md`, `00_admin/README.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Reduces stale governance noise and keeps the active unresolved surface focused on chapter citation closure.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.

## C-147
- date: 2026-03-28
- proposed_by: user + AI
- status: accepted
- change_summary: Final handoff synchronization pass completed: recently-played ingestion simplification already implemented and validated, cleanup of leftover generated artifacts performed, and repository content swap executed so implementation package content is now in `07_implementation` before commit/push preparation.
- reason: User requested pre-chat handoff closure with no leftover code/artifacts, explicit directory-content swap, and immediate push-readiness with admin-file synchronization.
- evidence_basis: Verified swap markers (`07_implementation` contains package runtime surface including `main.py`; `final_artefact` contains prior baseline marker `ACTIVE_BASELINE.md`), cleanup removed stale nested output directories and stale `.pytest_cache`, and prior run/test evidence confirms recently-played one-request cap behavior.

## C-203
- date: 2026-03-29
- proposed_by: user + AI
- status: accepted
- change_summary: Implemented Phase 1-4 controllability & transparency governance layer across 14 files: signal files at workspace root and implementation folder, design addendums extending controllability/transparency concepts, GOVERNANCE.md with 3-question gate, RESEARCH_DIRECTIONS.md with open questions and aspirational features, operational procedures for control testing and transparency auditing, signal files maintenance guide, Phase 4 verification document with full consistency checks (C1-C4), and updated operating_protocol.md Section 17 with integrated procedures.
- reason: Thesis core objectives (controllability and transparency) were underemphasized in current implementation visibility. Created persistent governance layer to establish these as first-class design priorities enforceable through control/transparency gate.
- evidence_basis: 14 files created (11 new + 3 updated); D-041/D-042/D-043 decisions appended to decision_log; git commit 0a0c3c0 with comprehensive message; all files cross-referenced consistently; no contradictions detected; Phase 4 verification complete.
- affected_components: `.controllability-transparency.instructions.md`, `00_admin/GOVERNANCE.md`, `00_admin/README.md`, `00_admin/operating_protocol.md`, `00_admin/decision_log.md`, `05_design/controllability_design_addendum.md`, `05_design/transparency_design_addendum.md`, `07_implementation/*.md` (6 new files: CONTROL_SURFACE_REGISTRY, TRANSPARENCY_SPEC, CONTROL_TESTING_PROTOCOL, TRANSPARENCY_AUDIT_CHECKLIST, RESEARCH_DIRECTIONS, SIGNAL_FILES_MAINTENANCE, PHASE_4_VERIFICATION_COMPLETE)
- impact_assessment: High-positive. Establishes persistent governance signal that control and transparency are thesis-core. Every agent sees thesis priority on workspace entry. 3-question gate prevents weak features. Control testing and transparency auditing are systematic. Procedures persist across sessions. All thesis core requirements satisfied or explicitly gated (D-042, D-043 for code implementation in Phase 3+).
- approval_record: User initiated with "push the changes made and update any admin files before i switch to another chat." Implemented full governance layer and documented Phase 1-4 completion.
- affected_components: `07_implementation/`, `final_artefact/`, cleanup targets under ingestion outputs/cache, `00_admin/change_log.md`, `00_admin/thesis_state.md`
- impact_assessment: High-positive for handoff reliability. Repository layout now matches requested direction, stale byproducts are removed, and governance records explicitly capture the transition state ahead of push.
- approval_record: Requested and confirmed by user in chat on 2026-03-28.
- evidence_basis: `00_admin/unresolved_issues.md` moved UI-008 to resolved; `00_admin/thesis_state.md`, `00_admin/README.md`, and `00_admin/handoff_friend_chat_playbook.md` updated to remove active UI-008 queue references; `06_data_and_sources/dataset_registry.md` status wording aligned.
- affected_components: `00_admin/unresolved_issues.md`, `00_admin/thesis_state.md`, `00_admin/README.md`, `00_admin/handoff_friend_chat_playbook.md`, `06_data_and_sources/dataset_registry.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Simplifies active governance focus and removes stale-open-item noise from daily control navigation.
- approval_record: Requested and confirmed by user in chat on 2026-03-25.

## C-147
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Execute final consistency sweep for control-doc currency, verify maintenance snapshot integrity, and remove a stale MQ-008 affected-file reference to closed UI-008.
- reason: User requested that everything be up to date.
- evidence_basis: Cross-file grep/read pass over admin and dataset registry surfaces; PowerShell integrity check confirmed `D_COUNT=28`, `D_MAX=28`, `C_COUNT=147`, `C_MAX=147`; `00_admin/mentor_question_log.md` MQ-008 affected-files updated from resolved UI-008 reference to current-state file linkage.
- affected_components: `00_admin/mentor_question_log.md`, `00_admin/change_log.md`
- impact_assessment: Low-positive. Removes minor residual drift and confirms control-log snapshot integrity.
- approval_record: Requested by user in chat on 2026-03-25 ("make sure everrything is up to date.").

## C-148
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Complete artefact refinement cycle (R1, R2, R3): emit canonical run-intent/run-effective-config artifact pair on every BL-013 run; add BL-009 schema version and execution_scope_summary block; produce semantic control-layer map. Validated in BL013-ENTRYPOINT-20260325-001946-187550.
- reason: Harden pipeline outputs for thesis defense audibility: deterministic per-run config evidence, versioned BL-009 observability schema, and semantic control-layer documentation for examiner-facing explanation.
- evidence_basis: Live run BL013-ENTRYPOINT-20260325-001946-187550; all 6 stages pass; run_intent and run_effective_config artifacts available with SHA256; observability_schema_version=bl009-observability-v1; execution_scope_summary confirmed in bl009_run_observability_log.json; artefact_refinement_spec.md updated to all-complete.
- affected_components: `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`, `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`, `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`, `07_implementation/implementation_notes/bl000_run_config/outputs/` (new), `07_implementation/implementation_notes/bl000_run_config/semantic_control_map.md` (new), `07_implementation/artefact_refinement_spec.md`
- impact_assessment: High-positive. Every pipeline run now emits a two-file config-evidence pair linked from the BL-009 audit log; BL-009 output is now schema-versioned; semantic control map enables examiner-facing explanation without relying on stage IDs.
- approval_record: Requested by user in chat on 2026-03-25.

## C-149
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Log and classify a high-severity implementation integrity incident (misplaced BL-003 influence-injection block) and execute a follow-on audit for similar hidden-failure patterns, including stale-test-data risk in orchestration/evaluation flows.
- reason: User requested that the incident be formally logged and asked for a broader check for comparable high-impact issues, with specific concern that tests may be using outdated data.
- evidence_basis: BL-003 failure was reproduced as an indentation/runtime break from module-level misplaced logic and then corrected; follow-on audit confirmed two additional high-risk governance/quality items: (1) BL-013 can run BL-004 to BL-009 without refreshing BL-003 unless explicitly requested; (2) BL-010/BL-011 baseline evidence can drift if not refreshed after contract changes.
- affected_components: `00_admin/change_log.md`, `00_admin/unresolved_issues.md`, `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`, `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`, `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`, `07_implementation/implementation_notes/bl011_controllability/run_bl011_controllability_check.py`
- impact_assessment: High-positive for governance rigor and risk visibility. Immediate failure mode was fixed; newly identified stale-data risks are now tracked as explicit open issues (`UI-009`, `UI-010`) with concrete remediation actions.
- approval_record: Requested by user in chat on 2026-03-25 ("log this... check for other big issues... tests are using outdated data").

## C-150
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Implement anti-staleness and legacy-mode guardrails across orchestration and evaluation: BL-013 now enforces BL-003 seed freshness under run-config mode, BL-003 emits a seed-contract fingerprint, and BL-010/BL-011 now require explicit opt-in for legacy surrogate inputs.
- reason: Close the concrete stale-data risk discovered in C-149 and convert hidden fallback behavior into explicit operator intent.
- evidence_basis: Validation runs completed on 2026-03-25: BL-013 fails with `BL-003-FRESHNESS-GUARD` when `--run-config` is used without `--refresh-seed`; BL-013 passes when rerun with `--refresh-seed`; BL-010 and BL-011 complete pass under new default active-input mode.
- affected_components: `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`, `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`, `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`, `07_implementation/implementation_notes/bl011_controllability/run_bl011_controllability_check.py`, `00_admin/unresolved_issues.md`, `00_admin/change_log.md`
- impact_assessment: High-positive. Prevents silent stale-seed false-passes in orchestrated runs and reduces hidden legacy-data coupling in reproducibility/controllability evidence.
- approval_record: User confirmed implementation in chat on 2026-03-25 ("yes").

## C-151
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Execute comprehensive pipeline audit and document all findings; identify and validate two critical data-integrity issues (CRI-001: unmatched-track bias, CRI-005: circular key distance) and create formal remediation backlog with prioritized Tier 1 and Tier 2 fixes.
- reason: Pre-final-hardening quality assurance to surface hidden risks before thesis submission; establish evidence-based prioritization for remaining work.
- evidence_basis: Full audit report at `09_quality_control/pipeline_audit_comprehensive_2026-03-25.md` containing 25 issues with detailed impact/mitigation analysis; remediation backlog at `00_admin/remediation_backlog_2026-03-25.md` with implementation schedule and risk mitigation strategy.
- affected_components: All 25 pipeline stages and governance files; no code changes in this entry, but audit output artifacts created in `09_quality_control/` and `00_admin/`.
- impact_assessment: High-positive. Comprehensive audit prevents undetected failures reaching thesis reviewers and establishes data-driven fix prioritization.
- approval_record: User requested comprehensive audit ("analyze the current pipeline and see if there is issues") and approved prioritization strategy on 2026-03-25.

## C-152
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Implement CRI-001 (unmatched-track bias detection + validation) and create formal remediation backlog; add match-rate threshold to run-config schema, enforce validation gate in BL-003, document bias in Chapter 3, and prioritize Tier 1 critical fixes; document CRI-005 (circular key distance) as already correctly implemented.
- reason: Address critical bias issue discovered in audit (32.2% match rate vs. corpus); establish transparent reporting mechanism; create formal backlog to prevent credential loss on remaining 23 issues.
- evidence_basis: BL-013 end-to-end validation run (2026-03-25 12:35 UTC) passes with match-rate metrics captured in `bl003_ds001_spotify_summary.json`; match-rate validation correctly triggers on threshold violation (tested failure case); Chapter 3 section 3.4.1 documents empirical limitation and implications.
- affected_components: `07_implementation/implementation_notes/bl000_run_config/run_config_template_v1.json`, `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`, `08_writing/chapter3.md`, `00_admin/remediation_backlog_2026-03-25.md`
- impact_assessment: High-positive for thesis integrity. Makes corpus coverage limitation explicit and transparent; prevents claims of universal user preference validity.
- approval_record: User approved implementation ("yes") on 2026-03-25; remediation backlog prioritization confirmed in Tier 1/2 assignment.
- approval_record: User approved implementation ("yes") on 2026-03-25; remediation backlog prioritization confirmed in Tier 1/2 assignment.

## C-153
- date: 2026-03-25
- proposed_by: AI (from CRI-004 backlog item)
- status: accepted
- change_summary: Implement CRI-004 (positive threshold validation) by adding validation functions `_validate_positive_thresholds()` and `_validate_positive_float()` in run_config_utils.py; integrate validation into resolve_bl005_controls(), resolve_bl006_controls(), and resolve_bl007_controls(); fail fast with clear error messages if any numeric threshold is <= 0 or non-numeric.
- reason: CRI-004 audit finding: no positive-value validation on numeric thresholds; thresholds <= 0 could cause division-by-zero or logic errors downstream; validation gates enable fail-fast behavior at config load time rather than silent degradation during pipeline execution.
- evidence_basis: 9/9 unit tests pass (valid configs accepted, zero/negative/non-numeric thresholds correctly rejected with clear error messages). Integration test: BL-013 with invalid zero threshold correctly fails at BL-005 with error message "retrieval_controls.numeric_thresholds: threshold 'tempo' must be positive (> 0), got 0.0". Normal pipeline operation unaffected (valid config passes BL-013 with exit code 0).
- affected_components: `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py` (lines ~135-175 new validation functions, lines 425/389/401 integration points)
- impact_assessment: High-positive for pipeline robustness. Prevents invalid configurations from entering pipeline. Fail-fast behavior at config load time is clearer and safer than discovering issues during candidate filtering.
- approval_record: Implicit acceptance by automated Tier 1 execution; test results verified passing; no user objection anticipated.

## C-154
- date: 2026-03-25
- proposed_by: AI (from CRI-002 backlog item)
- status: accepted
- change_summary: Implement CRI-002 (numeric threshold coupling) by enforcing exact equality between `retrieval_controls.numeric_thresholds` and `scoring_controls.numeric_thresholds` in `resolve_effective_run_config()`; add dedicated coupling guard `_enforce_numeric_threshold_coupling()` with mismatch detail reporting.
- reason: Prevent semantic drift where BL-005 filtering and BL-006 scoring use different numeric tolerances, which can silently degrade interpretability and reproducibility claims.
- evidence_basis: BL-013 standard run passes with canonical config (`BL013-ENTRYPOINT-20260325-013331-903943`). Forced mismatch config (`test_mismatched_numeric_thresholds.json`) fails fast with explicit error: `run_config numeric threshold coupling violation ... value mismatches=tempo: retrieval=20.0 vs scoring=25.0`.
- affected_components: `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`, `07_implementation/test_notes.md`, `00_admin/remediation_backlog_2026-03-25.md`
- impact_assessment: High-positive for semantic consistency and governance quality. Invalid coupled configurations are rejected before pipeline stages execute.
- approval_record: Implemented under approved Tier 1 remediation sequence; validation evidence recorded in `07_implementation/test_notes.md` (TC-CRI002-001).

## C-155
- date: 2026-03-25
- proposed_by: AI (from HIGH-003 backlog item)
- status: accepted
- change_summary: Implement HIGH-003 (undersized playlist warning/documentation) by adding explicit undersized diagnostics to BL-007 output/report, adding advisory flagging fields in BL-014 sanity checks, and documenting undersized-output interpretation caveat in Chapter 4.
- reason: Assembly constraints can legitimately underfill playlists; without explicit warnings this appears as silent quality loss and risks overstated fixed-length output claims.
- evidence_basis: BL-013 strict-controls run (`BL013-ENTRYPOINT-20260325-013610-197098`) produced `5/10` playlist and emitted warning lines in BL-007 stage stdout; `bl007_assembly_report.json` now includes `undersized_playlist_warning` with shortfall and exclusion-pressure counts. BL-014 code updated for advisory/run-matrix flagging, but runtime verification is currently blocked in this environment by missing `bl019_ds002_integrated_candidate_dataset.csv` artifact.
- affected_components: `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`, `07_implementation/implementation_notes/bl014_quality/run_bl014_sanity_checks.py`, `07_implementation/test_notes.md`, `08_writing/chapter4.md`, `00_admin/remediation_backlog_2026-03-25.md`
- impact_assessment: High-positive for transparency and thesis claim discipline. Underfilled playlists are now explicitly surfaced with interpretable causal diagnostics.
- approval_record: Implemented under approved Tier 1 remediation sequence; evidence logged in `07_implementation/test_notes.md` (TC-HIGH003-001).

## C-156
- date: 2026-03-25
- proposed_by: AI (from HIGH-004 backlog item)
- status: accepted
- change_summary: Implement HIGH-004 (profile-retrieval limit constraint validation) by enforcing `retrieval_controls.profile_top_*` limits to be <= corresponding `profile_controls.top_*` limits during effective run-config resolution; add template guidance comments for operators.
- reason: Prevent BL-005 retrieval configuration from requesting profile dimensions beyond what BL-004 profile construction produced, which can cause silent data misalignment.
- evidence_basis: BL-013 canonical run passes (`BL013-ENTRYPOINT-20260325-013848-150034`). Forced mismatch config (`test_invalid_profile_retrieval_limits.json`) fails fast with explicit error listing all violated pairs (`profile_top_tag_limit`, `profile_top_lead_genre_limit`).
- affected_components: `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`, `07_implementation/implementation_notes/bl000_run_config/run_config_template_v1.json`, `07_implementation/test_notes.md`, `00_admin/remediation_backlog_2026-03-25.md`
- impact_assessment: High-positive for cross-stage configuration coherence and reproducibility integrity. Invalid retrieval/profile limit combinations are blocked before stage execution.
- approval_record: Implemented under approved Tier 1 remediation sequence; validation evidence recorded in `07_implementation/test_notes.md` (TC-HIGH004-001).

## C-157
- date: 2026-03-25
- proposed_by: AI (from CRI-003 backlog item)
- status: accepted
- change_summary: Implement CRI-003 by adding component-weight sum validation in run-config resolution (must sum to 1.0 within +/-0.01), adding BL-006 rebalancing warning diagnostics (original sum/weights vs normalized active weights), and propagating those diagnostics into BL-009 observability output.
- reason: Prevent silent scoring drift from hidden weight normalization and enforce transparent operator-visible semantics for weight handling.
- evidence_basis: Invalid sum config (`test_invalid_component_weights_sum.json`) fails fast with clear error (`Got 1.100000`). Edge-case config (`test_edgecase_component_weights_rebalance.json`, sum=1.009) passes and emits BL-006 warning; diagnostics persisted in `bl006_score_summary.json` (`weight_rebalance_diagnostics.rebalanced=true`) and surfaced in `bl009_run_observability_log.json` under scoring diagnostics.
- affected_components: `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`, `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`, `07_implementation/implementation_notes/bl000_run_config/run_config_template_v1.json`, `07_implementation/test_notes.md`, `00_admin/remediation_backlog_2026-03-25.md`
- impact_assessment: High-positive for scoring transparency, reproducibility discipline, and governance traceability.
- approval_record: Implemented under approved Tier 1 remediation sequence; validation evidence recorded in `07_implementation/test_notes.md` (TC-CRI003-001).

## C-158
- date: 2026-03-25
- proposed_by: AI (integrated hardening validation)
- status: accepted
- change_summary: Executed integrated Tier-1 validation pass and aligned BL-014 sanity checks with current BL-005 artifact schema/candidate-source conventions; completed BL-013 canonical orchestration pass and BL-014 full sanity pass.
- reason: Final hardening evidence required a coherent end-to-end pass after applying all Tier-1 remediations; BL-014 had stale assumptions about BL-005 CSV columns and fixed candidate dataset path/hash source.
- evidence_basis: BL-013 run `BL013-ENTRYPOINT-20260325-014411-311800` status=pass. BL-014 run `BL014-SANITY-20260325-014516-905552` status=pass with `checks_passed=21/21`.
- affected_components: `07_implementation/implementation_notes/bl014_quality/run_bl014_sanity_checks.py`, `07_implementation/test_notes.md`, `00_admin/remediation_backlog_2026-03-25.md`
- impact_assessment: High-positive for hardening readiness and audit credibility. Integrated validation now passes on current pipeline artifacts.
- approval_record: Completed as part of approved post-remediation integrated validation step.

## C-159
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Added a comprehensive Tier-1 hardening execution log that consolidates all remediation actions, run evidence, validation outcomes, and governance updates into a single traceable admin artifact.
- reason: User requested full logging coverage ("log everythig"). Centralized logging improves auditability and reduces evidence fragmentation across multiple files.
- evidence_basis: New artifact `00_admin/tier1_hardening_execution_log_2026-03-25.md` includes CRI-004/CRI-002/HIGH-003/HIGH-004/CRI-003 execution summaries, integrated BL-013 and BL-014 pass evidence, and artifact paths.
- affected_components: `00_admin/tier1_hardening_execution_log_2026-03-25.md`, `00_admin/remediation_backlog_2026-03-25.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive for governance rigor. Single-document traceability now exists for the full Tier-1 hardening sequence.
- approval_record: Requested by user in chat ("log everythig") on 2026-03-25.

## C-160
- date: 2026-03-25
- proposed_by: user + AI
- status: accepted
- change_summary: Perform full admin-control sync so governance files reflect current post-hardening state: updated unresolved issues, thesis state execution snapshot, and timeline closure notes to include Tier-1 completion and integrated validation evidence.
- reason: User requested all admin files be up to date. Existing admin status files still reflected pre-closure posture for some execution-state sections.
- evidence_basis: `00_admin/unresolved_issues.md` now records Tier-1 closure item (UI-011) in resolved section; `00_admin/thesis_state.md` now reflects Tier-1 completion and integrated BL-013/BL-014 pass checkpoint; `00_admin/timeline.md` now includes Tier-1 and integrated validation closure entries.
- affected_components: `00_admin/unresolved_issues.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/change_log.md`
- impact_assessment: High-positive for governance consistency and handoff clarity. Admin records now align with implemented code/test reality.
- approval_record: Requested by user in chat ("make all the admin files up to date") on 2026-03-25.

| C-176 | 2026-03-25 22:57 | Copilot | Executed UI-013 tuning profile sweep (v1, v1a, v1b, v1c) to validate explanation-diversity and candidate-filtering controls; 3/4 profiles passed BL-014; v1b selected as optimal profile (stricter filtering, improved semantic-numeric balance); sweep results and all orchestration outputs archived in _scratch/ and implementation_notes/; updated experiment_log (EXP-045) and test_notes (TC-UI013-SWEEP-001). |

| C-192 | 2026-03-27 | Copilot | Workflow customization hardening pass: removed stale `model: GPT-5.3-Codex` spec from log-everything and session-start-check prompt frontmatter, renamed deprecated `mode:` to `agent:` in three prompt files, completed the stub impact-analysis prompt with full assessment steps, created `00_admin/recurring_issues.md` as the self-improvement friction log (seeded with RI-001), and wired recurring_issues.md into the copilot-instructions.md session-start checklist and Automatic Improvement Rule. |
| C-193 | 2026-03-28 | Copilot | Created `07_implementation/ARTEFACT_SUBMISSION_STRUCTURE_FINAL.md` as the final placeholder-only artefact submission structure authority, linked it from `07_implementation/implementation_notes/README.md` and `07_implementation/implementation_notes/SUBMISSION_MANIFEST.md`, and logged governance alignment for planner/autopilot handoff. |
| C-194 | 2026-03-28 | Copilot | Started standalone artefact implementation surface: added root `final_artefact.py` entrypoint (`run`/`validate`/`bundle`/`show-paths`), created `final_artefact/` docs-config-manifest package files, and aligned submission documentation to reference the new standalone hand-in execution path. |
| C-195 | 2026-03-28 03:41 UTC | Copilot | Executed admin-first documentation synchronization before chapter edits: updated `07_implementation/ACTIVE_BASELINE.md` with a no-run-change sync checkpoint, synchronized `00_admin/thesis_state.md` to remove stale active-v1b ambiguity and append current checkpoint, aligned `00_admin/Artefact_MVP_definition.md` wording/date, advanced Chapter 4 readiness gates in `09_quality_control/chapter_readiness_checks.md`, and refreshed `00_admin/timeline.md` status note. |
| C-196 | 2026-03-28 03:46 UTC | Copilot | Executed first chapter hardening pass: updated `08_writing/chapter3.md` to synchronize alignment-limitation metrics/threshold wording to canonical baseline posture, populated pending result tables in `08_writing/chapter4.md` Sections 4.8 to 4.10 with run-linked outcomes, closed the remaining Chapter 4 readiness gate in `09_quality_control/chapter_readiness_checks.md`, and synchronized `00_admin/thesis_state.md` plus `00_admin/timeline.md` checkpoints. |
| C-197 | 2026-03-28 | Copilot | Code hygiene refactor pass: added `safe_int` to `07_implementation/src/shared_utils/parsing.py`, removed duplicate `_safe_float`/`_safe_int` helpers from `07_implementation/src/playlist/rules.py` and `07_implementation/src/playlist/reporting.py`, removed redundant `normalize_text` wrapper from `07_implementation/src/ingestion/ingest_history_parser.py`; applied safe-cast imports throughout all three modules; 181/181 tests pass; pyright returns 0 errors on all edited files. |
| C-198 | 2026-03-28 | Copilot | Documentation sync and UI-003 mismatch closure: updated canonical run IDs (BL-010/011/013/014) across `07_implementation/backlog.md`, `00_admin/thesis_state.md`, `07_implementation/implementation_notes/bl013_entrypoint/outputs/BL013_RUN_MANIFEST.md`, and `08_writing/chapter4.md`; closed UI3-C3-007 verdict from mismatch to supported in `09_quality_control/ui003_claim_verdicts_ch3_ch5.md` (final counts: supported=18, partially_supported=2, mismatch=0, weak_support=0); updated BL-013 manifest "Last updated" timestamp to 2026-03-28. |
| C-199 | 2026-03-28 | Copilot | Chapter 2 verbatim audit gate closure: hardened Ru et al. (2023) sentence in `08_writing/chapter2.md` to task-specific bounded wording scoped to multi-label genre classification; reran `09_quality_control/verbatim_audits/run_ch2_verbatim_audit.py` and confirmed `total_claim_checks=40`, `weak_support=0`, `no_match=0` in `09_quality_control/chapter2_verbatim_audit.md`; marked Chapter 2 verbatim audit gate `[x]` in `09_quality_control/chapter_readiness_checks.md`; added Verbatim Audit Refresh (2026-03-28) block to `09_quality_control/citation_checks.md`. |
| C-200 | 2026-03-28 | Copilot | Post-swap path-alignment closure: switched repo type-check roots to `07_implementation` in `pyrightconfig.json`, aligned `07_implementation/tests/conftest.py` wording to active source root, verified launcher help via `final_artefact.py validate --help`, and added explicit active/legacy posture notes in governance docs plus a legacy banner in `final_artefact-old/README.md`. |
| C-201 | 2026-03-28 | Copilot | Ingestion runtime simplification alignment: documented and adopted no-token-cache/no-endpoint-cache BL-002 behavior with fresh OAuth-per-live-export and item-first track-only playlist-item parsing as accepted baseline policy; propagated this posture into governance (`D-040`) and implementation README guidance. |
| C-202 | 2026-03-29 | Copilot | Executed `07_implementation` cleanup and stabilization pass: removed generated caches and duplicate `src/run_config/configs/profiles` tree, retained canonical `config/profiles`, added `*.egg-info/` ignore, fixed stale README submission-guide pointer, patched `main.py` subprocess `PYTHONPATH` propagation for stage imports, and validated smoke tests (`test_standalone.py` pass). |

## C-220
- date: 2026-04-01
- proposed_by: user + AI
- status: accepted
- change_summary: Implemented run-config centralization hardening across BL-004 to BL-009 runtime control resolution by introducing payload-default merge semantics that use canonical defaults (not ambient stage env values) when orchestration payloads are present.
- reason: User requested end-to-end implementation to reduce repeated runtime resolving drift and make orchestrated behavior deterministic and submission-ready.
- evidence_basis: Shared resolver updated with explicit `load_payload_defaults` path; BL-004/005/006/007/008/009 runtime-control modules updated to use canonical defaults for payload merges; new and updated regression tests confirm no env leakage for missing payload keys and safe partial-payload behavior.
- affected_components: `07_implementation/src/shared_utils/stage_runtime_resolver.py`, `07_implementation/src/profile/runtime_controls.py`, `07_implementation/src/retrieval/runtime_controls.py`, `07_implementation/src/scoring/runtime_controls.py`, `07_implementation/src/playlist/runtime_controls.py`, `07_implementation/src/transparency/runtime_controls.py`, `07_implementation/src/observability/runtime_controls.py`, `07_implementation/tests/test_profile_stage.py`, `07_implementation/tests/test_retrieval_runtime_controls.py`, `07_implementation/tests/test_scoring_runtime_controls.py`, `07_implementation/tests/test_playlist_runtime_controls.py`, `07_implementation/tests/test_transparency_runtime_controls.py`, `07_implementation/tests/test_observability_runtime_controls.py`, `07_implementation/tests/test_runtime_controls_defaults_completeness.py`
- impact_assessment: High-positive. Centralized payload behavior is now deterministic under BL-013 and resilient to partial payloads without inheriting undeclared stage env overrides.
- approval_record: Requested by user in chat on 2026-04-01 ("Start implementation", "continue").

## C-221
- date: 2026-04-01
- proposed_by: user + AI
- status: accepted
- change_summary: Added orchestration-level payload-authority evidence and executed fresh end-to-end BL-013 pass to validate centralized runtime control behavior under current implementation state.
- reason: User requested continuation toward submission-readiness with explicit validation that centralized run-config payload behavior holds at orchestration handoff level.
- evidence_basis: BL-013 pass `BL013-ENTRYPOINT-20260401-150246-160721`; targeted test pass `19/19` for orchestration payload handoff/runner/default-completeness surfaces; broader runtime-controls selector pass `29/29` selected tests; new tests verify defaults are not sourced from stage env vars during payload resolution and run-config overrides propagate into stage payloads.
- affected_components: `07_implementation/tests/test_orchestration_stage_payload_handoff.py`, `07_implementation/tests/test_orchestration_stage_runner.py`, `07_implementation/tests/test_runtime_controls_defaults_completeness.py`, `07_implementation/src/orchestration/outputs/bl013_orchestration_run_latest.json`, `00_admin/change_log.md`, `00_admin/thesis_state.md`, `00_admin/evaluation_plan.md`
- impact_assessment: High-positive. Provides direct, current evidence for reproducibility and controllability claims tied to centralized orchestration payload semantics.
- approval_record: Requested by user in chat on 2026-04-01 ("yes", continue execution).
| C-204 | 2026-03-29 | Copilot | Completed the Phase 5-6 modularization sync pass: split BL-013 orchestration into focused helper modules with CLI > run-config > defaults control resolution, split BL-011 controllability into stage/path/runtime-control modules, split BL-003 matching/reporting into focused helper modules while preserving thin compatibility wrappers, refreshed admin/runtime docs to reflect the new layout, and revalidated touched files with pyright (`0 errors`). |
| C-205 | 2026-03-29 | Copilot | Completed OO-stage migration for BL-004, BL-005, and BL-006 in the standalone implementation surface: added typed models and stage classes for profile/retrieval/scoring, reduced each `main.py` to thin compatibility wrappers over stage methods, added stage-level tests, and revalidated touched files with pytest and pyright. |
| C-206 | 2026-03-29 | Copilot | Completed BL-003 Phase 2 typed-boundary migration in the standalone source surface: added `alignment/models.py` dataclasses (`SourceEvent`, `MatchTrace`, `MatchedEvent`, `AggregatedEvent`), migrated `weighting.py`, `match_pipeline.py`, and `aggregation.py` internals to typed models while preserving existing dict-based interfaces, added writer boundary compatibility for typed/dict payloads, and revalidated alignment behavior with targeted pytest (`88/88` pass). |
| C-207 | 2026-03-29 | Copilot | Completed BL-003 stage-shell migration in the standalone source surface: introduced `src/alignment/stage.py` (`AlignmentStage`), added typed run contracts (`AlignmentPaths`, `AlignmentSourceRows`, `AlignmentRunArtifacts`), reduced `src/alignment/main.py` to a thin wrapper, and added stage-level regression coverage (`tests/test_alignment_stage.py`); alignment suite remained green (`91/91` pass at migration checkpoint). |
| C-208 | 2026-03-29 | Copilot | Completed BL-003 summary-context architecture migration: added typed summary contracts (`AlignmentSummaryMetrics`, `AlignmentSummaryContext`), introduced context-based summary entrypoint (`build_and_write_summary_from_context`) with legacy-wrapper compatibility in `src/alignment/summary_builder.py`, migrated `AlignmentStage` to context wiring, and added parity regression test (`tests/test_alignment_summary_builder.py`); validated full alignment suite (`92/92` pass). |
| C-209 | 2026-03-29 | Copilot | Started BL-004 canonical output redesign implementation in standalone source: extended `src/profile/models.py` and `src/profile/stage.py` to source run-level match diagnostics from BL-003 summary, added additive schema metadata and canonical blocks (`bl003_quality`, `source_coverage`, `interaction_attribution`, `numeric_confidence`, `profile_signal_vector`), implemented split mixed-interaction attribution diagnostics with explicit policy metadata, and refactored shared payload assembly helpers while preserving legacy output surfaces and artifact paths (no checks/tests run in this phase by request). |
| C-210 | 2026-03-29 | Copilot | Started BL-005 direct logic uplift (single active path, no legacy fallback path): updated retrieval runtime context to consume BL-004 canonical quality/confidence signals (`numeric_confidence`, `profile_signal_vector`, `bl003_quality`), switched numeric support to confidence-weighted accumulation with normalization, applied profile-informed effective thresholds and semantic overlap damping in live decision flow, expanded diagnostics/distributions for effective thresholds and weighted support, and preserved required BL-005 output artifact contracts for downstream stages. |
| C-211 | 2026-03-29 | Copilot | Implemented BL-005 logic-improvement item #1 end to end (single active path): derived and threaded a profile-level numeric confidence factor from BL-004 confidence signals, added absolute-confidence scaling (`numeric_support_score_weighted_absolute`) to numeric support scoring, switched continuous numeric keep/reject decisions to the absolute-weighted signal, and extended BL-005 decision/diagnostic surfaces additively (new CSV columns and score distribution) without changing artifact paths or introducing legacy fallback branches. |
| C-212 | 2026-03-29 | Copilot | Started BL-006 active-path logic uplift (no legacy fallback): integrated BL-004 numeric confidence signals into scoring context and numeric contribution weighting, upgraded semantic scoring with weighted top-lead-genre matching and precision-aware genre/tag overlap penalties, switched final-score aggregation to contribution-driven confidence-adjusted totals, and added additive BL-006 confidence-impact diagnostics/summary metadata while preserving required scored-candidate CSV contract fields and artifact paths. |
| C-213 | 2026-03-29 | Copilot | Completed BL-007 architecture migration to typed stage/model pattern: added `src/playlist/models.py` dataclasses and mapping adapters, introduced `src/playlist/stage.py` (`PlaylistStage`) for path/control/input/aggregation/report orchestration, reduced `src/playlist/main.py` to a thin wrapper over `PlaylistStage.run()`, exported playlist stage/contracts via `src/playlist/__init__.py`, and preserved existing BL-007 output paths plus required report/trace contract fields for BL-008 and BL-009 downstream consumers. |
| C-214 | 2026-03-29 | Copilot | Implemented BL-007 controlled logic uplift with user-tunable control surface: extended run-config/env assembly controls (utility strategy/weights, adaptive limits, controlled relaxation, lead-genre fallback, tie-break toggles, opportunity-cost diagnostics, detail-log window), threaded controls through playlist models/runtime/stage, upgraded rule engine with deterministic utility-greedy option plus adaptive max-per-genre and controlled relaxation rounds, added semantic-proxy fallback bucketing for missing lead genre, and added additive opportunity-cost diagnostics while preserving BL-007 output file paths and required downstream contract keys for BL-008/BL-009. |
| C-215 | 2026-03-29 | Copilot | Implemented BL-006 controllable logic uplift with default-safe behavior: expanded scoring control schema (run-config template, defaults, resolver, env surface), threaded controls through typed scoring models/runtime context, added control-gated lead-genre strategy and semantic overlap strategy, added configurable semantic alpha mode (profile-adaptive or fixed), added configurable numeric confidence scaling modes (on/off, floor, direct/blended profile factor), and emitted additive control-aware diagnostics/summary fields while preserving BL-006 scored-candidate CSV contract fields and downstream compatibility. |
| C-216 | 2026-03-29 | Copilot | Started BL-005 controllable-logic uplift with default-safe behavior: expanded retrieval control schema in defaults/template/resolver, added dedicated `retrieval/runtime_controls.py` run-config-first resolver, threaded new policy fields through retrieval typed models/context, replaced hardcoded profile-quality/entropy/influence penalty constants and semantic damping constants with control-driven values in BL-005 stage, added configurable numeric-support decision mode (`raw`/`weighted`/`weighted_absolute`) in candidate evaluation, and extended BL-005 decision diagnostics with selected numeric support distributions while preserving required output artifacts/contracts for BL-006 and BL-009. |
| C-217 | 2026-03-29 | Copilot | Implemented BL-004 controllable logic uplift with default-safe behavior: expanded profile control schema in defaults/template/resolver (confidence weighting mode, confidence-bin thresholds, interaction attribution mode, diagnostics toggle), added dedicated `profile/runtime_controls.py` run-config-first resolver, threaded control fields through typed profile contracts, replaced hardcoded confidence weighting/binning and mixed-interaction attribution behavior with control-gated policies in BL-004 stage, and added additive effective-policy diagnostics/summary metadata while preserving canonical BL-004 output blocks (`numeric_confidence`, `profile_signal_vector`) and downstream compatibility for BL-005/BL-006. |
| C-218 | 2026-03-29 | Copilot | Standardized BL-005 stage contract to match BL-003/BL-004/BL-006/BL-007: added typed `RetrievalArtifacts` dataclass, updated `RetrievalStage.run()` to return the typed artifacts contract (while preserving existing BL-005 output files/paths/schemas and side effects), exported the new contract from retrieval package surface, and added stage-level test coverage for typed run return invariants. |
| C-219 | 2026-03-29 | Copilot | Synchronized governance and design documentation to current BL-003 through BL-007 source-code behavior: updated control-surface and transparency specs in `07_implementation` plus design addenda and architecture mapping in `05_design`; corrected BL-007 wording from fully hardcoded to partially configurable (run-config/env controls with fixed rule-order residuals), moved unimplemented planned controls to future-work posture, and reframed non-implemented transparency features as known limitations/future work. No runtime code or artifact schema behavior changed. |
| C-220 | 2026-03-29 | Copilot | Full 00_admin synchronization wave: updated all 17 root admin files to reflect the 2026-03-29 canonical baseline. Key changes: thesis_state.md BL-020 date corrected to 2026-03-29; timeline.md milestones M2/M3/M4 marked completed, M5/M6 marked in progress, WP-CITE-001/WP-DRAFT-001/WP-WEBINT-001 sprint notes updated, Recently Closed extended with C-207 through C-219 items; unresolved_issues.md date updated and 2026-03-29 sync note appended; README.md implementation status extended with architecture-migration bullet; change_log.md maintenance snapshot updated to C-219; handoff_friend_chat_playbook.md priority queue rewritten to submission-packaging posture and technical snapshot updated to v1f canonical run IDs; Artefact_MVP_definition.md Known Limitations section added; evaluation_plan.md EP-CTRL-001 influence-tracks caveat note added; GOVERNANCE.md influence-tracks escalation example retired to documented-limitation posture; recurring_issues.md RI-002/RI-003/RI-004 patterns added; mentor/methodology/scope-lock/bl-pinning files date-stamped to 2026-03-29. Documentation-only; no runtime code or artifact schema changed. |
| C-221 | 2026-03-29 | Copilot | Updated `07_implementation/README.md` to match current runtime behavior and entrypoint semantics: documented top-level `main.py` wrapper flow, clarified that `--validate-only` is additive (BL-013 then BL-014), aligned stage/output paths to active `07_implementation/src` modules, added direct BL-013/BL-010/BL-011/BL-014 command guidance with `PYTHONPATH` note for `src`-level execution, and synchronized troubleshooting text to observed import/path failure modes. Also updated admin tracking metadata in `00_admin/thesis_state.md`. Documentation-only; no runtime code changed. |
| C-222 | 2026-03-30 | Copilot | Executed aggressive root archival wave by moving `.controllability-transparency.instructions.md`, `.gitattributes`, `requirements.txt`, `pyrightconfig.json`, `main_standalone.py`, and `final_artefact.py` into `_deep_archive_march2026/_packages_reference_2026-03-30/`; expanded `.gitignore` to ignore `_deep_archive_march2026/` as a whole; and synchronized governance/admin records (`file_map.md`, `00_admin/decision_log.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/operating_protocol.md`, `00_admin/SIGNAL_FILES_MAINTENANCE.md`, `00_admin/README.md`) to the archived-root posture with active runtime anchored on `07_implementation/main.py`. |
