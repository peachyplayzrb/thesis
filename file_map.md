# File Map

## Purpose
This file tracks files touched during active cleanup and repo-organization work so the current location, role, and status of each file stays easy to audit.

## Update Rule
After each future task segment, append or update entries here for any file that was created, edited, moved, archived, restored, or explicitly reviewed for placement.

For every tracked file, record four things:
- where it is now
- whether it is active, reviewed, moved, or archived
- what it does
- why it was kept, moved, or archived

## Status Labels
- `active`: file is in its intended working location.
- `archived`: file was moved out of the active surface but retained.
- `reviewed`: file was checked and intentionally left where it is.
- `moved`: file changed location and remains active.

## Active Repo Files Touched

| File | Status | Current Location | What It Does | Notes |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | active | repo root | Defines agent/session workflow rules for how work in the thesis repo should start, close, and stay within approved scope. | Updated to include cleanup hygiene guidance for keeping root canonical. |
| `.gitignore` | active | repo root | Tells git which local caches, generated outputs, probe files, credentials, and temporary artifacts should stay untracked. | Updated comment text and added ignore rules for cleanup-operation artifacts and archive staging. |
| `.gitattributes` | reviewed | repo root | Defines repo-wide git attributes, especially LFS handling for large datasets and binary-like source files. | Reviewed only; still the correct location for repo-wide LFS and binary handling rules. |
| `requirements.txt` | reviewed | repo root | Declares the Python packages needed to run the repo's scripts and pipeline utilities. | Reviewed against actual imports; already up to date, so no edit was needed. |
| `07_implementation/scripts/run_pipeline_test.py` | moved | `07_implementation/scripts/` | Runs a lightweight BL-013 pipeline smoke test to confirm the main orchestration entrypoint is still callable. | Moved from repo root to a clearer implementation-scripts location and updated path resolution. |
| `07_implementation/backlog.md` | active | `07_implementation/` | Canonical implementation-control board for active scope and evidence state. | Updated 2026-03-27 alignment notes to keep v1f canonical and v2a experimental. |
| `07_implementation/implementation_notes/SETUP.md` | active | `07_implementation/implementation_notes/` | Canonical run/setup guide for orchestration and quality checks. | Updated command examples for both outer workspace root and inner repo root execution contexts. |
| `07_implementation/implementation_notes/CODEBASE_ISSUES_CURRENT.md` | active | `07_implementation/implementation_notes/` | Current implementation snapshot and issue/status register. | Added explicit alignment lock note and marked v1d run snapshot section as historical/superseded. |
| `07_implementation/implementation_notes/CODEBASE_ISSUES_HISTORICAL.md` | active | `07_implementation/implementation_notes/` | Historical implementation snapshots retained for traceability and comparison. | Added to externalize superseded v1d snapshot details from the current-state sheet. |
| `07_implementation/experiment_log.md` | active | `07_implementation/` | Canonical run-by-run implementation evidence ledger used for thesis traceability. | Added EXP-049 documenting the 2026-03-27 v2a experimental evidence wave and pass metrics while keeping v1f canonical. |
| `07_implementation/implementation_notes/bl000_run_config/configs/profiles/CONFIG_LIFECYCLE.md` | active | `07_implementation/implementation_notes/bl000_run_config/configs/profiles/` | Lifecycle index for all run-config profile files (canonical, experimental, historical-retained). | Added to keep v1a-v1e retained but explicitly classified under D-033 policy posture. |
| `07_implementation/implementation_notes/bl000_run_config/outputs/RUN_CONFIG_RETENTION_POLICY.md` | active | `07_implementation/implementation_notes/bl000_run_config/outputs/` | Documents retention and archival policy for timestamped run-config output artifacts. | Added policy-only guidance in this pass; no artifact deletions performed. |
| `07_implementation/implementation_notes/bl013_entrypoint/outputs/BL013_RUN_MANIFEST.md` | active | `07_implementation/implementation_notes/bl013_entrypoint/outputs/` | Run-wave index mapping dense BL-013 run outputs to date/config/purpose groups. | 2026-03-27 cleanup: dated JSON run logs pruned from 117 to 10 most recent (20260327-series); manifest and `bl013_orchestration_run_latest.json` retained. |
| `07_implementation/implementation_notes/bl000_run_config/docs/bl000_run_config_state_log_2026-03-25.md` | active | `07_implementation/implementation_notes/bl000_run_config/docs/` | Stage-level state log for BL-000 run-config contract and evidence. | Added 2026-03-27 alignment lock update classifying v1f active and v2a experimental. |
| `00_admin/bl010_bl011_baseline_pinning_manifest.md` | active | `00_admin/` | Documents intentional BL-010/BL-011 pinned-snapshot divergence and reproducibility context. | Added to formalize historical pinning rationale while keeping v1f canonical reporting posture. |
| `00_admin/change_log.md` | active | `00_admin/` | Canonical C-series governance log for tracked implementation changes. | Updated maintenance snapshot and added C-185 entry for this docs/governance alignment implementation pass. |
| `00_admin/decision_log.md` | active | `00_admin/` | Canonical D-series governance log for implementation decisions. | Updated maintenance snapshot and added D-034 retention-policy decision after D-033 baseline lock. |
| `00_admin/unresolved_issues.md` | active | `00_admin/` | Tracks active and resolved issue posture for implementation governance. | Updated resolved UI-013 evidence wording to align with D-033 (v1f canonical, v2a experimental). |
| `08_writing/chapter4.md` | active | `08_writing/` | Chapter 4 implementation/evaluation evidence narrative and test matrix. | Updated Table 4.3 EP rows from `pending` to evidence-backed pass records using current v1f artifacts. |
| `08_writing/chapter5.md` | active | `08_writing/` | Chapter 5 interpretation and limitations narrative. | Reworded stale bootstrap references to current v1f evidence posture and explicit BL-010/BL-011 snapshot caveat. |
| `08_writing/abstract.md` | active | `08_writing/` | Thesis abstract summarizing RQ, method, results, and scoped contribution. | Replaced empty stub with current evidence-aligned abstract text. |
| `00_admin/thesis_state.md` | active | `00_admin/` | Canonical thesis execution-state register. | Updated top timestamp and added 2026-03-27 checkpoint with refreshed v1f run IDs. |
| `07_implementation/backlog.md` | active | `07_implementation/` | Canonical implementation-control board for active scope and evidence state. | Updated latest integrated evidence chain and final-state references to 2026-03-27 v1f run IDs. |

## Archived Workspace-Level Files Touched

These files are outside the inner git repo root but were touched during the cleanup pass and are now retained in the workspace archive staging area.

| Original Role | Status | Current Location | What It Does | Notes |
| --- | --- | --- | --- | --- |
| BL-006 quick reference | archived | `../_archive_cleanup_staging_2026-03-26/_cleanup_admin/BL006_QUICK_REFERENCE.md` | Summarizes BL-006 scoring structure, function flow, data flow, and refactor targets for quick human reference. | Reference document moved out of the active root surface. |
| BL-006 structure analysis | archived | `../_archive_cleanup_staging_2026-03-26/_cleanup_admin/BL006_STRUCTURE_ANALYSIS.md` | Provides a deeper structural breakdown of the BL-006 script, including blocks, dependencies, extraction targets, and scoring model details. | Analysis document moved out of the active root surface. |
| Cleanup delete manifest | archived | `../_archive_cleanup_staging_2026-03-26/_cleanup_admin/cleanup_delete_manifest_2026-03-26.txt` | Lists the files that were originally identified as safe cleanup candidates before switching from delete to move. | One-off cleanup planning artifact. |
| Cleanup keep manifest | archived | `../_archive_cleanup_staging_2026-03-26/_cleanup_admin/cleanup_keep_manifest_2026-03-26.txt` | Lists files and folders explicitly protected from cleanup moves or deletion. | One-off cleanup planning artifact. |
| Cleanup move manifest | archived | `../_archive_cleanup_staging_2026-03-26/_cleanup_admin/cleanup_move_manifest_2026-03-26.txt` | Maps each moved file from its original path to the archive staging location. | Manifest used to move disposable files into staging. |
| Cleanup move execution report | archived | `../_archive_cleanup_staging_2026-03-26/_cleanup_admin/cleanup_move_execution_report_2026-03-26.txt` | Records the actual results of the cleanup move operation, including moved, missing, and failed items. | Records what was moved during the cleanup pass. |
| Cleanup validation report | archived | `../_archive_cleanup_staging_2026-03-26/_cleanup_admin/cleanup_validation_report_2026-03-26.txt` | Records post-move checks confirming cleanup targets were gone and protected paths remained intact. | Records post-move validation results. |
| Restore script | archived | `../_archive_cleanup_staging_2026-03-26/_cleanup_admin/restore_from_cleanup_staging_2026-03-26.ps1` | Reverses the cleanup move manifest by moving archived items back to their original locations. | Rollback utility kept for safety, not needed in active root. |
| Restore dry-run report | archived | `../_archive_cleanup_staging_2026-03-26/_cleanup_admin/restore_from_cleanup_staging_2026-03-26_dryrun_report.txt` | Captures the simulated restore results without changing any files. | Validation output for rollback simulation. |

## Archived Cleanup Payload Area

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `../_archive_cleanup_staging_2026-03-26/` | archived | Serves as the top-level holding area for files removed from the active workspace during cleanup. | Workspace-level staging area for moved scratch files and cleanup artifacts. |
| `../_archive_cleanup_staging_2026-03-26/_scratch/` | archived | Holds the outer-root scratch scripts, logs, JSON probes, text probes, and pycache content that were moved out of the active surface. | Contains moved outer-root scratch and temp files. |
| `../_archive_cleanup_staging_2026-03-26/_cleanup_admin/` | archived | Holds cleanup manifests, validation reports, rollback tooling, and archived root-level reference documents. | Contains cleanup manifests, reports, rollback script, and archived reference docs. |

## Reviewed Repo Archive Directories

All prior scattered archive folders were consolidated into a single deep archive in the 2026-03-27 cleanup pass.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `_deep_archive_march2026/` | archived | Single consolidated archive holding all six March 2026 implementation/cleanup archive folders. | Created 2026-03-27 by merging `_archive_implementation_2026-03-26_pre_refactor/`, `_archive_run_outputs_2026-03-26_cleanup/`, `07_implementation/_archive_2026-03-23/`, `07_implementation/_archive_2026-03-24/`, `07_implementation/_archive_2026-03-25/`, and `07_implementation/implementation_notes/_archive_cleanup_2026-03-26/` into one location. |
| `00_admin/archives/` | archived | Holds dated admin bloat files moved out of the 00_admin root (sprint plans, email drafts, hardening logs, etc.) | Created 2026-03-27; contains C_080_day_3_hardening.txt, current_implementation_information_sheet_2026-03-25.md, mentor_draft_7day_sprint_2026-03-23.md, music4all_access_email_draft_2026-03-21.md, remediation_backlog_2026-03-25.md, tier1_hardening_execution_log_2026-03-25.md. |
| `_deep_archive_march2026/IMPLEMENTATION_STATE_2026-03-24.md` | archived | Historical implementation-state snapshot moved out of active implementation surface. | Archived on 2026-03-27 during document-consistency cleanup; superseded by `07_implementation/implementation_notes/CODEBASE_ISSUES_CURRENT.md`. |
| `_deep_archive_march2026/implementation_plan.md` | archived | Historical implementation-plan snapshot retained for traceability. | Archived on 2026-03-27 during document-consistency cleanup; active implementation posture now tracked in `07_implementation/backlog.md`. |

These files are inside the inner repo scratch area. They are not core runtime files, but they do represent a meaningful UI013 tuning experiment rather than disposable junk.

| File | Status | Current Location | What It Does | Notes |
| --- | --- | --- | --- | --- |
| `_scratch/run_ui013_sweep.ps1` | reviewed | `_scratch/` | Runs a multi-config UI013 tuning sweep by executing BL-013 and BL-014 across several run-config profiles and collecting comparison metrics. | Scratch but meaningful; keep if the tuning study may be repeated. |
| `_scratch/ui013_tuning_sweep_results.json` | reviewed | `_scratch/` | Stores the sweep results across the `v1`, `v1a`, `v1b`, and `v1c` tuning configurations, including candidate counts, contribution balance, dominance share, and pass/fail status. | Generated experiment output; archive if the study is complete. |
| `_scratch/ui013_v1b_bl008_focus_result.json` | reviewed | `_scratch/` | Stores a focused summary for the `v1b` configuration, especially around BL-008 explanation-balance outcomes and overall sanity status. | Generated experiment summary; archive if the study is complete. |

## Reviewed Repo Infrastructure Directories

These directories support repo operation and collaboration, but they serve different roles.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `.github/` | reviewed | Holds repo-level Copilot customization and reusable prompt files that standardize collaborator workflow, session governance, and recurring analysis tasks. | Canonical repo tooling/config; should remain in the repo. |
| `.github/copilot-instructions.md` | reviewed | Defines how Copilot should behave in this repo, including session-start checks, logging strictness, and session-close governance. | Active collaborator-instructions file; keep in place. |
| `.github/prompts/` | reviewed | Holds reusable prompt templates for recurring thesis tasks such as claim verification, paper analysis, consistency checks, and session startup. | Canonical prompt library for collaborator workflows. |
| `.venv/` | reviewed | Stores the local Python virtual environment, including the interpreter and installed packages used to run repo scripts on this machine. | Local environment state, not canonical source; keep locally but do not treat as archival repo content. |

## Reviewed Governance Directory

The `00_admin/` folder is the thesis governance and execution-control hub. It is mostly canonical and should remain in the repo root structure.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `00_admin/` | reviewed | Holds the governance layer for the thesis: current state, scope, decisions, changes, risks, evaluation direction, mentor interaction, and operating rules. | Canonical control hub; should remain active and central. |
| `00_admin/README.md` | reviewed | Explains the purpose of the admin folder, recommended read order, key files, and hygiene rules. | Canonical orientation file for the control hub. |
| `00_admin/operating_protocol.md` | reviewed | Defines naming rules, logging schemas, update authority, definition-of-done rules, archive protocol, and session logging requirements. | Canonical workflow policy file. |
| `00_admin/thesis_state.md` | reviewed | Stores the current official thesis title, research question, scope, objectives, evaluation direction, implementation state, and current priorities. | Canonical current-state file; should remain active. |
| `00_admin/change_log.md` | reviewed | Records C-series changes across the repo and thesis workflow. | Canonical governance log. |
| `00_admin/decision_log.md` | reviewed | Records D-series design and implementation decisions. | Canonical governance log. |
| `00_admin/unresolved_issues.md` | reviewed | Tracks active blockers, risks, and open issues. | Canonical governance file. |
| `00_admin/evaluation_plan.md` | reviewed | Defines the evaluation contract and evidence expectations for the thesis artefact. | Canonical evaluation-control file. |
| `00_admin/methodology_definition.md` | reviewed | Defines the methodology position and its implications for the project. | Canonical methodology-control file. |
| `00_admin/timeline.md` | reviewed | Tracks milestones and work-package timing. | Canonical planning file. |
| `00_admin/mentor_question_log.md` | reviewed | Tracks MQ-series mentor questions and their status. | Canonical mentor-governance file. |
| `00_admin/mentor_feedback_log.md` | reviewed | Tracks MF-series mentor feedback and follow-up actions. | Canonical mentor-governance file. |
| `00_admin/thesis_scope_lock.md` | reviewed | Explicitly defines what is in scope and out of scope for the thesis artefact. | Canonical scope-control file. |
| `00_admin/Artefact_MVP_definition.md` | reviewed | Defines the minimum artefact contract for the thesis system. | Canonical artefact-definition file. |
| `00_admin/templates/` | reviewed | Holds reusable templates for changes, decisions, mentor questions, and architecture/paper notes. | Canonical support tooling for governance work. |

## Reviewed Dated Admin Records

These files are still useful, but they are more like dated planning notes, execution logs, or reference drafts than always-active control files.

| File | Status | Current Location | What It Does | Notes |
| --- | --- | --- | --- | --- |
| `00_admin/current_implementation_information_sheet_2026-03-25.md` | reviewed | `00_admin/` | Snapshot information sheet describing implementation status at a specific date. | Useful historical reference; not a primary control file. |
| `00_admin/remediation_backlog_2026-03-25.md` | reviewed | `00_admin/` | Dated remediation planning document for a specific hardening/remediation cycle. | Historical working document; archive candidate later if clutter becomes a problem. |
| `00_admin/tier1_hardening_execution_log_2026-03-25.md` | reviewed | `00_admin/` | Execution log for Tier-1 hardening work and its closure evidence. | Historical execution evidence; reasonable to keep in admin unless an admin archive is introduced. |
| `00_admin/mentor_draft_7day_sprint_2026-03-23.md` | reviewed | `00_admin/` | Time-bounded mentor sprint plan/draft for a specific date window. | Dated planning artifact; archive candidate later. |
| `00_admin/C_080_day_3_hardening.txt` | reviewed | `00_admin/` | Plain-text hardening note tied to a specific change/hardening effort. | Lower-structure dated admin artifact; strongest archive candidate among current admin files. |
| `00_admin/music4all_access_email_draft_2026-03-21.md` | reviewed | `00_admin/` | Draft external communication related to Music4All access. | One-off communication draft; clear archive candidate if no longer needed. |

## Reviewed Implementation Directory

The `07_implementation/` folder is the active implementation hub. It contains both canonical live implementation assets and dated implementation-history material.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `07_implementation/` | reviewed | Holds the active implementation plan, backlog, experiment evidence, website integration work, runtime setup, scripts, and the main stage-by-stage implementation tree. | Canonical implementation hub; should remain active. |
| `07_implementation/implementation_notes/` | reviewed | Contains the BL-stage implementation modules, configs, outputs, and detailed implementation artifacts that power the actual pipeline. | Core runtime implementation area; canonical. |
| `07_implementation/backlog.md` | reviewed | Tracks BL-series implementation items, their priorities, statuses, evidence outputs, and current execution posture. | Canonical implementation-control file. |
| `07_implementation/experiment_log.md` | reviewed | Records EXP-series implementation and evaluation runs with inputs, outputs, metrics, and traceability. | Canonical implementation evidence log. |
| `07_implementation/implementation_plan.md` | reviewed | Historical implementation-planning document for a prior execution cycle. | Archived to `_deep_archive_march2026/implementation_plan.md`; active posture now tracked in `07_implementation/backlog.md`. |
| `07_implementation/website.md` | reviewed | Tracks the website plan, architecture, user flows, API contract, and integration roadmap for BL-023. | Canonical plan file for website integration work. |
| `07_implementation/website/` | reviewed | Contains the actual website frontend assets and routes used for the UI integration layer. | Active implementation area for BL-023. |
| `07_implementation/setup/` | reviewed | Contains runtime/setup support such as the website API server and environment bootstrap logic. | Canonical setup/runtime support area. |
| `07_implementation/scripts/` | reviewed | Holds helper scripts that support implementation operations, including the relocated smoke test entrypoint. | Correct location for operational helper scripts. |
| `07_implementation/test_notes.md` | reviewed | Records test-oriented notes and test-case references for implementation validation. | Canonical implementation QA/support file. |
| `07_implementation/SPOTIFY_INTEGRATION.md` | reviewed | Documents Spotify integration details and related implementation context. | Canonical implementation reference doc. |

## Reviewed Dated Implementation Records

These files and folders are still useful, but they are either dated state snapshots or already archived implementation history rather than current live control files.

| File Or Path | Status | Current Location | What It Does | Notes |
| --- | --- | --- | --- | --- |
| `07_implementation/IMPLEMENTATION_STATE_2026-03-24.md` | reviewed | `_deep_archive_march2026/` | Dated implementation-state snapshot for a specific point in time. | Historical reference; archived out of the live implementation root. |
| `07_implementation/_archive_2026-03-23/` | reviewed | `07_implementation/` | Dated archive directory containing older implementation materials retained for rollback and history. | Already correctly archived in place. |
| `07_implementation/_archive_2026-03-24/` | reviewed | `07_implementation/` | Dated archive directory containing older implementation materials retained for rollback and history. | Already correctly archived in place. |
| `07_implementation/_archive_2026-03-25/` | reviewed | `07_implementation/` | Dated archive directory containing older implementation materials retained for rollback and history. | Already correctly archived in place. |

## Reviewed Writing Directory

The `08_writing/` folder is the active thesis-writing surface. It combines live chapter drafts, chapter-planning notes, reference-management files, and final-document assembly artifacts.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `08_writing/` | reviewed | Holds the active thesis draft chapters, writing plans, bibliography files, master merged draft, and final document assembly artifacts. | Canonical writing hub; should remain active. |
| `08_writing/abstract.md` | reviewed | Stores the thesis abstract text for the final report. | Active abstract draft is now populated and aligned to the current evidence posture. |
| `08_writing/chapter1.md` | reviewed | Holds the Chapter 1 introduction draft covering problem framing, research question, objectives, and scope. | Canonical live chapter draft. |
| `08_writing/chapter2.md` | reviewed | Holds the Chapter 2 literature and design-rationale draft. | Canonical live chapter draft, with planning support from `chapter2_plan.md`. |
| `08_writing/chapter3.md` | reviewed | Holds the Chapter 3 design and architecture draft. | Canonical live chapter draft, with planning support from `chapter3_plan.md`. |
| `08_writing/chapter4.md` | reviewed | Holds the Chapter 4 implementation and evaluation draft. | Canonical live chapter draft. |
| `08_writing/chapter5.md` | reviewed | Holds the Chapter 5 conclusion/final discussion draft. | Canonical live chapter draft. |
| `08_writing/chapter2_plan.md` | reviewed | Stores the active plan for Chapter 2 structure, evidence closure, and freeze criteria. | Active planning note that supports the live Chapter 2 draft. |
| `08_writing/chapter3_plan.md` | reviewed | Stores the active plan for Chapter 3 structure, traceability, and chapter-role boundaries. | Active planning note that supports the live Chapter 3 draft. |
| `08_writing/references.bib` | reviewed | Stores the main bibliography database used to manage formal thesis citations. | Canonical citation source file. |
| `08_writing/references_working.md` | reviewed | Provides a lightweight working-notes surface for citation/reference handling outside the main bibliography database. | Support file for citation work; currently mostly empty. |
| `08_writing/thesis_master_draft_merged.md` | reviewed | Assembles the thesis into one continuous merged markdown draft with front matter and chapter content combined. | Likely the main consolidated markdown deliverable before final Word packaging. |
| `08_writing/thesis_document_template_aligned.md` | reviewed | Provides a thesis draft aligned to the university document template and required front-matter structure. | Canonical packaging aid for final submission formatting. |
| `08_writing/Thesis.docx` | reviewed | Stores the Word-format thesis document for final formatting and submission. | Final-delivery artifact rather than source-of-truth prose, but still an active writing output. |

## Reviewed Writing Version Records

These files and folders look like writing-history snapshots, alternate drafts, or temporary variants rather than the primary live writing surface.

| File Or Path | Status | Current Location | What It Does | Notes |
| --- | --- | --- | --- | --- |
| `08_writing/_versions/` | reviewed | `08_writing/` | Holds older chapter and draft snapshots such as `chapter2_draft_v9.md`, `chapter2_draft_v10.md`, `chapter2_draft_v11.md`, and other temporary/final-draft variants. | Writing-history area; good candidate to keep as-is or later rationalize if naming becomes confusing. |
| `08_writing/chapter3_v2.md` | reviewed | `08_writing/` | Preserves an alternate Chapter 3 draft revision alongside the main `chapter3.md`. | Draft snapshot rather than the clearest primary chapter file. |
| `08_writing/chapter2_v2.md` | reviewed | `08_writing/_versions/` | Represents an older Chapter 2 draft iteration retained as version history. | Version-history material rather than current canonical draft content. |
| `08_writing/chapter2_v3.md` | reviewed | `08_writing/_versions/` | Represents an older Chapter 2 draft iteration retained as version history. | Version-history material rather than current canonical draft content. |
| `08_writing/chapter2_v4.md` | reviewed | `08_writing/_versions/` | Represents an older Chapter 2 draft iteration retained as version history. | Version-history material rather than current canonical draft content. |

## Reviewed Data And Sources Directory

The `06_data_and_sources/` folder is the canonical data-governance and dataset-staging hub. It mixes source-of-truth dataset documentation with heavyweight local raw-data assets used by the implementation pipeline.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `06_data_and_sources/` | reviewed | Holds dataset registry records, provenance controls, schema definitions, source-adapter notes, and staged local source files for the thesis corpora. | Canonical data-governance hub; should remain active. |
| `06_data_and_sources/dataset_registry.md` | reviewed | Tracks the registered datasets, their roles, provenance state, access conditions, and active-versus-fallback status. | Canonical corpus-of-record and provenance-control file. |
| `06_data_and_sources/provenance_rules.md` | reviewed | Defines the evidence, licensing, and integrity conditions required before external data can become thesis-active. | Canonical compliance-control file for dataset usage. |
| `06_data_and_sources/schema_notes.md` | reviewed | Defines the expected ingestion, alignment, bootstrap, and profile artifact schemas used by the pipeline. | Canonical data-contract reference for implementation stages. |
| `06_data_and_sources/source_adapter_notes.md` | reviewed | Records how external dataset sources were contacted, interpreted, and locally placed for thesis use. | Canonical source-acquisition note for Music4All handling. |
| `06_data_and_sources/ds_001_music4all_information_sheet.md` | reviewed | Documents the DS-001 Music4All base dataset, including acquisition route, inventory, key fields, and intended pipeline role. | Canonical dataset information sheet for the active Music4All base corpus. |
| `06_data_and_sources/ds_001_prepared_working_schema.md` | reviewed | Defines the prepared DS-001 working table derived from raw Music4All files for runtime candidate scoring and alignment. | Canonical preparation spec bridging raw data into runtime assets. |
| `06_data_and_sources/ds_002_msd_information_sheet.md` | reviewed | Documents the constructed DS-002 fallback dataset based on MSD plus Last.fm and MusicBrainz-linked metadata. | Canonical fallback-corpus information sheet. |

## Reviewed Local Dataset Payloads

These items are local corpus payloads, archives, and indices. They are operationally important, but they are not lightweight documentation files and should be treated as machine-local data assets.

| File Or Path | Status | Current Location | What It Does | Notes |
| --- | --- | --- | --- | --- |
| `06_data_and_sources/music4all_raw/` | reviewed | `06_data_and_sources/` | Holds the provider-delivered raw Music4All export before or alongside extraction. | Correct staging area for raw DS-001 source data; excluded from normal source editing workflows. |
| `06_data_and_sources/music4all_raw/music4all/music4all/` | reviewed | `06_data_and_sources/music4all_raw/` | Contains the extracted base Music4All corpus files such as `id_information.csv`, `id_metadata.csv`, `id_tags.csv`, `id_genres.csv`, `id_lang.csv`, `listening_history.csv`, plus `audios/` and `lyrics/`. | Active local DS-001 payload surface used to derive prepared runtime datasets. |
| `06_data_and_sources/track_metadata.db` | reviewed | `06_data_and_sources/` | Stores a local metadata database used for dataset inspection or intermediate lookup work. | Local data asset rather than governance documentation. |
| `06_data_and_sources/unique_artists.txt` | reviewed | `06_data_and_sources/` | Stores a large text index of unique artist records from the MSD-related corpus assets. | Large dataset-support text asset; keep as local reference data. |
| `06_data_and_sources/unique_tracks.txt` | reviewed | `06_data_and_sources/` | Stores a large text index of unique track records from the MSD-related corpus assets. | Large dataset-support text asset; too large for normal editor sync, so treat as machine-local reference data. |
| `06_data_and_sources/lastfm_subset.zip` | reviewed | `06_data_and_sources/` | Stores a compressed Last.fm subset archive used to construct or validate the fallback DS-002 corpus. | Raw source archive; retain as local reproducibility input. |
| `06_data_and_sources/millionsongsubset.tar.gz` | reviewed | `06_data_and_sources/` | Stores the compressed Million Song Dataset subset archive. | Raw source archive for DS-002 construction. |
| `06_data_and_sources/MSongsDB-master.zip` | reviewed | `06_data_and_sources/` | Stores the MSD support-code/database archive associated with Million Song Dataset processing. | Local support archive for dataset handling rather than a thesis narrative file. |

## Reviewed Quality Control Directory

The `09_quality_control/` folder is the canonical thesis QA and evidence-discipline hub. It holds the recurring checks that keep chapters, claims, citations, and implementation evidence aligned to the locked thesis scope.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `09_quality_control/` | reviewed | Holds thesis-quality control logs, readiness checks, claim-to-evidence mappings, citation-risk tracking, audit schedules, and remediation support artifacts. | Canonical QA/control hub; should remain active. |
| `09_quality_control/chapter_readiness_checks.md` | reviewed | Tracks readiness status across thesis chapters and submission-wide checks, including open blockers and progress notes. | Canonical chapter-readiness checklist. |
| `09_quality_control/citation_checks.md` | reviewed | Tracks chapter citation integrity, evidence-risk levels, freeze gates, and bounded limitations for literature claims. | Canonical citation-risk and freeze-control file. |
| `09_quality_control/claim_evidence_map.md` | reviewed | Maps major thesis claims to specific sources, confidence levels, and chapter usage. | Canonical claim-traceability file. |
| `09_quality_control/rq_alignment_checks.md` | reviewed | Records recurring checks that the title, RQ, scope, and chapter language remain synchronized with the locked thesis state. | Canonical research-question alignment log. |
| `09_quality_control/audit_schedule.md` | reviewed | Defines the recurring cadence for literature, consistency, chapter-readiness, and cleanup audits. | Canonical QA cadence note. |
| `09_quality_control/consistency_audit.md` | reviewed | Serves as the thesis-consistency audit record for cross-artifact alignment checks. | Currently sparse, but still the correct canonical location for that audit stream. |
| `09_quality_control/duplication_watch.md` | reviewed | Serves as the log for tracking duplicated arguments or redundant writing across thesis chapters and notes. | Currently sparse, but still the correct canonical location for duplication checks. |

## Reviewed Quality Control Audit Records

These items are still useful, but they are more like dated audit outputs, focused remediation packs, or tooling support than the core recurring QA control files.

| File Or Path | Status | Current Location | What It Does | Notes |
| --- | --- | --- | --- | --- |
| `09_quality_control/pipeline_audit_comprehensive_2026-03-25.md` | reviewed | `09_quality_control/` | Records a dated, deep audit of the implementation pipeline with critical and high-priority findings across BL stages. | High-value audit snapshot; historical but still important for hardening evidence. |
| `09_quality_control/verbatim_audits/` | reviewed | `09_quality_control/` | Holds Chapter 2 verbatim-audit reports plus helper scripts for generating and summarizing those audits. | Focused audit-output and tooling area rather than a primary control log. |
| `09_quality_control/verbatim_audits/run_ch2_verbatim_audit.py` | reviewed | `09_quality_control/verbatim_audits/` | Runs the automated Chapter 2 verbatim-support audit against local PDFs and writing files. | Operational QA helper script; not a narrative control file. |
| `09_quality_control/verbatim_audits/summarize_ch2_verbatim_audit.py` | reviewed | `09_quality_control/verbatim_audits/` | Summarizes the raw Chapter 2 verbatim-audit results into a more digestible output. | QA helper script paired with the verbatim audit workflow. |
| `09_quality_control/weak_claims/` | reviewed | `09_quality_control/` | Holds analysis, prioritization, quick-reference guidance, and remediation plans for weakly supported Chapter 2 claims. | Targeted remediation package rather than a general recurring control surface. |
| `09_quality_control/weak_claims/weak_claims_EXECUTIVE_SUMMARY.md` | reviewed | `09_quality_control/weak_claims/` | Summarizes the highest-impact weak claims, their risks, and the recommended remediation order. | Useful remediation summary; not the primary thesis QA ledger. |

## Reviewed Requirements Directory

The `01_requirements/` folder is the canonical assessment-requirements hub. It combines locally curated requirement summaries with the raw university source pack used to derive those summaries.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `01_requirements/` | reviewed | Holds requirement interpretations, assessment constraints, submission rules, formatting expectations, and the source university-document pack behind those rules. | Canonical assessment-requirements hub; should remain active. |
| `01_requirements/submission_requirements.md` | reviewed | Summarizes required submission channels, milestone pattern, final outputs, and open confirmation points for the project. | Canonical local summary of submission obligations. |
| `01_requirements/marking_criteria.md` | reviewed | Summarizes the module assessment structure, component criteria, proposal gate expectations, and related marking risks. | Canonical local summary of marking expectations. |
| `01_requirements/formatting_rules.md` | reviewed | Summarizes report-structure, word-count, referencing, and presentation expectations for the final thesis report. | Canonical local formatting summary. |
| `01_requirements/university_rules.md` | reviewed | Consolidates the ingested university source set into a ranked binding/advisory rule summary for the thesis. | Canonical synthesis file translating source documents into practical requirement guidance. |
| `01_requirements/ambiguity_flags.md` | reviewed | Tracks unresolved or high-risk interpretation issues in the university requirements, such as viva semantics and current-year validity. | Canonical ambiguity/risk log for assessment-rule interpretation. |

## Reviewed University Requirement Sources

These items are the raw institutional source materials and templates that back the local requirement summaries. They are authoritative evidence inputs, but not all of them are active working notes.

| File Or Path | Status | Current Location | What It Does | Notes |
| --- | --- | --- | --- | --- |
| `01_requirements/university_documents/` | reviewed | `01_requirements/` | Holds the raw university handbooks, marking sheets, briefs, templates, guidance PDFs, sample report materials, and lecture-support files used to derive the local requirement summaries. | Source-evidence pack for assessment rules. |
| `01_requirements/university_documents/Projects HandBook Version 4.6.docx` | reviewed | `01_requirements/university_documents/` | Provides the module handbook and milestone/assessment framing used as a primary source for requirement extraction. | High-priority binding source document. |
| `01_requirements/university_documents/Project Marking sheet (1).docx` | reviewed | `01_requirements/university_documents/` | Provides the main project and artefact marking rubric. | High-priority binding source document. |
| `01_requirements/university_documents/Professionalism Assessment Brief.docx` | reviewed | `01_requirements/university_documents/` | Provides the brief for the professionalism component of the module. | High-priority binding source document. |
| `01_requirements/university_documents/Professionalism Marking sheet.docx` | reviewed | `01_requirements/university_documents/` | Provides the marking rubric for the professionalism component. | High-priority binding source document. |
| `01_requirements/university_documents/Project Proposal Report Marking grid (1).docx` | reviewed | `01_requirements/university_documents/` | Provides the pass/fail gate criteria for the project proposal stage. | High-priority binding source document. |
| `01_requirements/university_documents/Project Cover Page.docx` | reviewed | `01_requirements/university_documents/` | Provides the required project cover/declaration template. | Active submission template rather than a narrative working file. |
| `01_requirements/university_documents/Logbook.docx` | reviewed | `01_requirements/university_documents/` | Provides the template for project-management evidence and supervision tracking. | Active submission-support template. |
| `01_requirements/university_documents/LS134-Harvard-Quick-Guide-2018.pdf` | reviewed | `01_requirements/university_documents/` | Provides Harvard referencing guidance used as an advisory citation-format source. | Advisory but operationally important. |
| `01_requirements/university_documents/LS015-Guide-to-Writing-a-Literature-Review.pdf` | reviewed | `01_requirements/university_documents/` | Provides literature-review writing guidance used as advisory support. | Advisory guidance source. |
| `01_requirements/university_documents/Sample Project Final Report v1 (3).pdf` | reviewed | `01_requirements/university_documents/` | Provides a sample final report for structure and presentation comparison. | Example material, not a binding rule source. |
| `01_requirements/university_documents/Sample Project Final Report v1 (3).md` | reviewed | `01_requirements/university_documents/` | Provides a text/markdown form of the sample final report material for easier local inspection. | Working copy of example material rather than an authoritative rule file. |
| `01_requirements/university_documents/~$mple Project Final Report v1 (3).pdf` | reviewed | `01_requirements/university_documents/` | Appears to be a transient Office lock/temp artifact associated with the sample report file. | Generated temp artifact, not meaningful canonical content. |

## Reviewed Foundation Directory

The `02_foundation/` folder is the canonical thesis-definition layer. It captures the locked title/RQ, problem framing, objectives, terminology, assumptions, contribution boundary, and validity limits that the rest of the repo should stay aligned to.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `02_foundation/` | reviewed | Holds the core thesis-definition files that fix the problem framing, objectives, scope language, assumptions, contribution boundary, and key terminology. | Canonical foundation layer; should remain active. |
| `02_foundation/current_title_and_rq.md` | reviewed | Stores the current official thesis title and research question wording with an explicit alignment note to the locked thesis state. | Canonical title/RQ reference file. |
| `02_foundation/problem_statement.md` | reviewed | States the thesis problem framing, engineering challenge, bounded MVP scope, and the rationale for the thesis artefact. | Canonical problem-definition file. |
| `02_foundation/objectives.md` | reviewed | Defines the primary objective and the specific thesis objectives that guide design, implementation, and evaluation. | Canonical objective-definition file. |
| `02_foundation/assumptions.md` | reviewed | Lists the foundational assumptions behind the deterministic, single-user, artefact-focused thesis approach. | Canonical assumptions register. |
| `02_foundation/limitations.md` | reviewed | Defines the validity limits and observed failure modes that bound how thesis claims should be interpreted. | Canonical limitations and validity-boundary file. |
| `02_foundation/contribution_statement.md` | reviewed | States the bounded contribution claim of the thesis as engineering/design evidence rather than model-superiority evidence. | Canonical contribution-scope statement. |
| `02_foundation/terminology.md` | reviewed | Defines the core pipeline, data, and status terms used consistently across the thesis and implementation materials. | Canonical terminology-control file. |

## Reviewed Literature Directory

The `03_literature/` folder is the canonical literature-processing hub. It combines active trackers for coverage and gaps with the paper-note inventory and higher-level synthesis outputs used to support chapter writing and QC traceability.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `03_literature/` | reviewed | Holds literature trackers, paper-note inventory, synthesis outputs, theme notes, reading coordination files, and PDF-audit artifacts. | Canonical literature-processing hub; should remain active. |
| `03_literature/literature_gap_tracker.md` | reviewed | Stores the active research-gap statement, its support/challenge evidence, and the design implications drawn from the literature. | Canonical gap-positioning file. |
| `03_literature/coverage_tracker.md` | reviewed | Records literature processing progress, recovered-source handling, and cross-links into updated paper notes and extracted claim-check artifacts. | Canonical literature coverage/progress tracker. |
| `03_literature/reading_queue.md` | reviewed | Serves as the queue surface for pending or planned literature processing work. | Currently sparse, but still the correct coordination file for future reading intake. |
| `03_literature/source_index.csv` | reviewed | Provides the indexed source registry that ties citation keys, papers, and literature-processing workflows together. | Canonical machine-readable literature index. |
| `03_literature/theme_support_all_resources.md` | reviewed | Summarizes theme-to-paper support counts across the processed source set. | Canonical thematic coverage summary. |

## Reviewed Literature Note Inventories

These folders are active and useful, but they function more as inventories of notes and synthesis outputs than as single control files.

| File Or Path | Status | Current Location | What It Does | Notes |
| --- | --- | --- | --- | --- |
| `03_literature/paper_notes/` | reviewed | `03_literature/` | Holds the per-paper note files for the processed literature set, currently spanning `P-001` through `P-065`. | Core literature evidence inventory; active and high value. |
| `03_literature/thematic_notes/` | reviewed | `03_literature/` | Holds theme-scoping notes such as `potential_themes.md` that help organize literature into recurring topic buckets. | Lightweight thematic working area; active but relatively small. |
| `03_literature/synthesis_notes/` | reviewed | `03_literature/` | Holds higher-level synthesis artifacts such as architecture-theme mappings and cross-paper support summaries. | Active literature synthesis layer bridging notes into thesis design/write-up. |

## Reviewed Literature Audit Records

These items are mainly audit outputs or audit-support artifacts around literature-note fidelity rather than the core literature notes themselves.

| File Or Path | Status | Current Location | What It Does | Notes |
| --- | --- | --- | --- | --- |
| `03_literature/pdf_audits/` | reviewed | `03_literature/` | Holds dated audits of paper-note versus PDF fidelity plus resolution checklists. | Audit-history area for literature-note validation. |
| `03_literature/pdf_audits/paper_note_pdf_audit_full_2026-03-23.md` | reviewed | `03_literature/pdf_audits/` | Records a dated full audit of paper-note fidelity against source PDFs. | Historical but useful audit evidence. |
| `03_literature/pdf_audits/paper_pdf_resolution_checklist_2026-03-23.md` | reviewed | `03_literature/pdf_audits/` | Tracks PDF resolution/verification actions for the literature set. | Operational audit checklist rather than an active synthesis file. |

## Reviewed Research Discovery Directory

The `04_research_discovery/` folder is the canonical evidence-acquisition and search-governance layer. It tracks what literature searches were run, what gaps still need targeted evidence, and which papers are candidates for future ingestion.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `04_research_discovery/` | reviewed | Holds literature-search planning, search execution logs, follow-up priorities, and candidate-paper staging notes. | Canonical search-governance hub; should remain active. |
| `04_research_discovery/paper_search_log.md` | reviewed | Records executed search batches, their results, ingestion decisions, and linked literature gaps. | Canonical search execution log. |
| `04_research_discovery/search_followups.md` | reviewed | Tracks the prioritized follow-up evidence acquisition plan and query pack for unresolved literature gaps. | Canonical follow-up plan for search-driven gap closure. |
| `04_research_discovery/candidate_papers.md` | reviewed | Serves as the staging surface for candidate papers identified during search before full ingestion decisions are made. | Currently sparse, but still the correct place for candidate-paper triage notes. |
| `04_research_discovery/consensus_queries.md` | reviewed | Serves as the shared query surface for recurring or agreed search strings used during literature discovery. | Currently sparse, but still the correct place for search-query standardization. |

## Reviewed Design Directory

The `05_design/` folder is the canonical literature-to-architecture translation layer. It captures the proposed system design, the Chapter 3 design scaffold, and the mechanism-specific design notes for transparency, controllability, observability, and explanation.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `05_design/` | reviewed | Holds architecture drafts, design traceability maps, Chapter 3 design scaffolding, and focused mechanism-design notes for the thesis artefact. | Canonical design layer; should remain active. |
| `05_design/chapter3_information_sheet.md` | reviewed | Provides the master Chapter 3 design sheet that defines the layered architecture, design methodology, assumptions, diagram plan, and success criteria. | Canonical design master sheet. |
| `05_design/architecture.md` | reviewed | Extracts and critiques the current system architecture as a working design hypothesis, including risks and required literature justification. | High-value architecture working document. |
| `05_design/system_architecture.md` | reviewed | States the compact layered system architecture and end-to-end flow as a provisional design hypothesis. | Canonical concise architecture summary. |
| `05_design/requirements_to_design_map.md` | reviewed | Maps literature issues and thesis requirements to concrete mechanisms and Chapter 3 handoff targets. | Canonical design traceability bridge. |
| `05_design/literature_architecture_mapping.md` | reviewed | Maps each architecture layer to its literature basis, support strength, and remaining justification gaps. | Canonical architecture-justification map. |
| `05_design/controllability_design.md` | reviewed | Defines the bounded control surfaces, parameter governance, and controllability evaluation expectations for the pipeline. | Canonical controllability design brief. |
| `05_design/observability_design.md` | reviewed | Defines the run-level logging, diagnostics, and replay-support requirements needed for auditability and reproducibility. | Canonical observability design brief. |
| `05_design/transparency_design.md` | reviewed | Defines how scoring logic, rule effects, and uncertainty boundaries should be exposed faithfully through artifacts. | Canonical transparency-by-design brief. |
| `05_design/explanation_design.md` | reviewed | Serves as the focused design surface for recommendation explanation behavior and explanation artifact structure. | Currently sparse, but still the correct dedicated location for explanation-specific design. |
| `05_design/data_pipeline.md` | reviewed | Serves as the focused design surface for end-to-end data-pipeline structure and stage flow. | Currently sparse, but still the correct dedicated location for data-pipeline design. |

## Reviewed Resources Directory

The `10_resources/` folder is the canonical supporting-resource library. It holds literature PDFs, dataset bundles, dataset documentation copies, previous draft carryovers, extracted text artifacts, and example/legacy materials that support the active thesis workflow without being the primary control surface.

| Path | Status | What It Does | Notes |
| --- | --- | --- | --- |
| `10_resources/` | reviewed | Holds supporting papers, dataset bundles, extracted text assets, previous draft materials, dataset documentation copies, and legacy/example artifacts. | Canonical supporting-resource hub; should remain active. |
| `10_resources/ingestion_rules.md` | reviewed | Defines how legacy materials and design-source documents should be ingested, interpreted, and cross-checked before reuse. | Canonical resource-ingestion governance note. |
| `10_resources/papers/` | reviewed | Stores the local paper library used for literature processing, including PDFs, extracted text, claim-check artifacts, and staged bundle subfolders. | Active reference library backing `03_literature/` and QC workflows. |
| `10_resources/papers/_extracted/` | reviewed | Stores extracted text or derived artifacts from the local paper library. | Support area for literature processing rather than direct source-of-truth notes. |
| `10_resources/papers/_extracted_claim_check/` | reviewed | Stores extracted text assets specifically prepared for claim-verification and audit workflows. | Operational support area for QC/citation checking. |
| `10_resources/papers/nw/` | reviewed | Holds a staged paper bundle plus bundle bibliography (`nw.bib`) for one local literature-ingestion batch. | Resource-bundle staging area rather than thesis-control documentation. |
| `10_resources/papers/rp/` | reviewed | Holds a staged paper bundle plus bundle bibliography (`rp.bib`) for another local literature-ingestion batch. | Resource-bundle staging area rather than thesis-control documentation. |
| `10_resources/datasets/` | reviewed | Stores raw or packaged external dataset assets such as MSD and Music4All/Onion bundles used for corpus construction and validation. | Canonical local dataset-resource library. |
| `10_resources/dataset_docs/` | reviewed | Stores copied vendor/source documentation related to datasets, such as Music4All reference slides. | Canonical supporting documentation area for datasets. |
| `10_resources/dataset_docs/music4all/` | reviewed | Holds Music4All-specific documentation copies such as `music4all_slide.pdf`. | Narrow dataset-doc sublibrary; active reference material. |
| `10_resources/previous_drafts/` | reviewed | Stores older thesis writing and literature-review materials retained as historical drafting inputs. | Historical support area; useful, but not current canonical writing. |
| `10_resources/previous_drafts/old_literature_review.md` | reviewed | Preserves the old literature review as a legacy extraction source that can inform paper-note creation and gap checks. | Historical input only; should not be treated as authoritative evidence by itself. |
| `10_resources/old_script` | reviewed | Stores a legacy standalone Spotify/Flask job-runner script used for earlier data collection or experimentation. | Legacy utility artifact, not part of the current canonical implementation surface. |
| `10_resources/Sample.pdf` | reviewed | Stores a sample/reference PDF artifact in the resource library. | Example/reference material rather than a current control or runtime file. |

## Proposed Second-Pass Cleanup Candidates

This section is a conservative proposal only. Nothing below has been moved yet. The goal is to identify files that are no longer part of the active control surface and could be moved into a dated archive location in a second cleanup pass.

| Candidate | Recommended Action | Why It Is A Candidate | Safety Level | Notes |
| --- | --- | --- | --- | --- |
| `01_requirements/university_documents/~$mple Project Final Report v1 (3).pdf` | remove or archive | Appears to be a transient Office lock/temp file rather than meaningful thesis content. | high | Strongest cleanup candidate in the repo tree. |
| `00_admin/C_080_day_3_hardening.txt` | archive | Plain-text dated hardening note with lower structure than the main admin logs. | high | Good fit for a future `00_admin/_archive_admin_YYYY-MM-DD/` folder. |
| `00_admin/music4all_access_email_draft_2026-03-21.md` | archive | One-off communication draft, not an ongoing governance control file. | high | Retain for traceability, but move out of the active admin surface. |
| `00_admin/mentor_draft_7day_sprint_2026-03-23.md` | archive | Time-bounded mentor sprint draft rather than an enduring control file. | high | Safe once no active sprint work depends on it. |
| `00_admin/remediation_backlog_2026-03-25.md` | archive later | Dated remediation planning file tied to a specific hardening cycle. | medium | Keep active until the current remediation cycle is clearly closed. |
| `00_admin/current_implementation_information_sheet_2026-03-25.md` | archive later | Dated implementation snapshot rather than the live thesis state source. | medium | Archive when its content is no longer being referenced directly. |
| `_scratch/ui013_tuning_sweep_results.json` | archive if study complete | Generated experiment output from a scratch tuning sweep rather than core runtime state. | medium | Keep only if further UI013 tuning iterations are expected. |
| `_scratch/ui013_v1b_bl008_focus_result.json` | archive if study complete | Generated focused experiment summary inside repo scratch space. | medium | Archive with the sweep result if the study is closed. |
| `08_writing/chapter3_v2.md` | archive after writing freeze | Alternate draft revision rather than the primary chapter file. | medium | Only move after confirming `chapter3.md` is the accepted canonical draft. |
| `08_writing/_versions/` | archive later or rationalize | Writing-history area is useful but clutters the active writing surface once chapters are frozen. | medium | Better archived as a whole than selectively pruning individual draft files. |
| `09_quality_control/pipeline_audit_comprehensive_2026-03-25.md` | archive later | High-value dated audit snapshot, but not a recurring control file. | low-medium | Keep visible until hardening findings are fully acted on. |
| `09_quality_control/verbatim_audits/` | archive after Chapter 2 closure | Focused audit-output/tooling area for Chapter 2 hardening, not an enduring top-level control surface. | low-medium | Keep active if verbatim audit reruns are still expected. |
| `09_quality_control/weak_claims/` | archive after Chapter 2 closure | Remediation package for a specific hardening phase rather than a permanent QA control layer. | low-medium | Keep active while Chapter 2 evidence hardening remains live. |
| `10_resources/previous_drafts/` | keep in place or archive later | Already separated into a historical-support area, so it is low urgency. | low | Not cluttering the active root much because it already sits under resources. |
| `10_resources/old_script` | archive | Legacy standalone script not part of the active implementation surface. | medium | Good candidate for a dated legacy-tools archive under resources. |
| `10_resources/Sample.pdf` | archive later | Example/reference file rather than active thesis or runtime content. | low | Low urgency because it already lives in the resources library. |

## Proposed Second-Pass Archive Policy

- Prefer moving historical-but-meaningful files into a dated in-repo archive folder rather than deleting them.
- Strong candidate archive zones are `00_admin/_archive_admin_2026-03-26/`, `08_writing/_archive_writing_2026-03-26/`, `09_quality_control/_archive_qc_2026-03-26/`, and `10_resources/_archive_legacy_2026-03-26/`.
- Treat raw datasets, active chapter drafts, current governance logs, and current implementation/runtime files as protected.
- Only archive scratch experiment outputs after confirming the related study is actually complete.

## Handoff Findings Snapshot

This note is a concise handoff summary for the next chat so the current repo-organization findings do not need to be reconstructed from scratch.

- The top-level thesis structure from `00_admin/` through `10_resources/` has now been reviewed and mapped.
- The active canonical control surfaces are: governance (`00_admin/`), requirements (`01_requirements/`), foundation (`02_foundation/`), literature processing (`03_literature/`), research discovery (`04_research_discovery/`), design (`05_design/`), data and sources (`06_data_and_sources/`), implementation (`07_implementation/`), writing (`08_writing/`), quality control (`09_quality_control/`), and resources (`10_resources/`).
- Previously completed cleanup work already moved outer-root scratch/path-scan clutter and cleanup admin artifacts into `../_archive_cleanup_staging_2026-03-26/`.
- No new files were moved in the second-pass planning stage; only archive candidates were identified and documented.
- Highest-confidence second-pass cleanup candidates are: the Office temp file in `01_requirements/university_documents/`, the dated plain-text/admin draft items in `00_admin/`, and selected legacy/example materials under `10_resources/`.
- Medium-confidence candidates depend on user confirmation about whether related work is complete: scratch UI013 experiment outputs, `08_writing/chapter3_v2.md`, and the broader `08_writing/_versions/` area.
- Lower-priority items should stay visible until hardening work is clearly complete: `09_quality_control/verbatim_audits/`, `09_quality_control/weak_claims/`, and `09_quality_control/pipeline_audit_comprehensive_2026-03-25.md`.
- Recommended next cleanup action is a conservative Phase 1 move of only the `high` safety items into dated in-repo archive folders.
- If a future chat continues cleanup execution, use this file as the source of truth before moving anything.

## Current Root Shape

### Repo root: `thesis-main/`
- Canonical directories remain under `00_admin/` through `10_resources/`.
- Root-level control files remain: `AGENTS.md`, `.gitignore`, `.gitattributes`, `requirements.txt`.
- Active smoke test script now lives under `07_implementation/scripts/`.
- Dated archive directories remain in place for implementation snapshots and historical run-output retention.
- `_scratch/` currently contains retained UI013 tuning experiment artifacts rather than throwaway temp files.
- `.github/` is canonical collaborator tooling.
- `.venv/` is local runtime environment state.
- `00_admin/` is the canonical governance and control hub, with a mix of always-active control files and some dated admin records.
- `01_requirements/` is the canonical assessment-requirements hub, combining curated rule summaries with the raw university source pack.
- `02_foundation/` is the canonical thesis-definition layer for the locked title/RQ, objectives, assumptions, terminology, contribution, and limitations.
- `03_literature/` is the canonical literature-processing hub for paper notes, gap tracking, thematic synthesis, and literature-audit support.
- `04_research_discovery/` is the canonical literature-search governance layer for query planning, search logs, and evidence-acquisition follow-ups.
- `05_design/` is the canonical literature-to-architecture layer for system design, design traceability, and mechanism-specific design briefs.
- `06_data_and_sources/` is the canonical data-governance and dataset-staging hub, combining source documentation with large local corpus assets.
- `07_implementation/` is the canonical implementation hub, with active runtime material plus dated implementation snapshots.
- `08_writing/` is the canonical thesis-writing hub, with active chapter drafts and a separate version-history layer.
- `09_quality_control/` is the canonical QA hub for citation discipline, claim traceability, RQ alignment, and dated audit evidence.
- `10_resources/` is the canonical supporting-resource library for papers, dataset bundles, extracted reference assets, and legacy/example materials.

### Workspace root: outer project folder
- Active top-level folders now consist only of `thesis-main/`.
- `_archive_cleanup_staging_2026-03-26/` was moved to the parent folder (`thesis-main (3)/`) during the 2026-03-27 cleanup pass — it is outside the workspace.
- The partial `07_implementation/` orphan folder (workspace root level, 4 files) was deleted after confirming the canonical versions inside `thesis-main/` were newer.
- `thesis-main/` contains the complete active project.
