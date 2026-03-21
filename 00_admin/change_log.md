# Change Log

Use schema from `00_admin/operating_protocol.md`.

## C-001
- date: 2026-03-12
- proposed_by: AI + user
- status: accepted
- change_summary: Initial repository and thesis environment setup; folder structure created, Git repository initialized on inner thesis-main folder, working branch `setup/initial-work` created, and AI operating protocol established.
- reason: Foundational setup required before any thesis work could be tracked or executed.
- evidence_basis: Repo memory note in `/memories/repo/setup.md`; initial commit history.
- affected_components: All top-level thesis folders; `00_admin/operating_protocol.md`
- impact_assessment: High-positive. Established the traceable environment all subsequent work depends on.
- approval_record: Implicitly approved by project initiation on 2026-03-12.

## C-006
- date: 2026-03-15
- proposed_by: AI + user
- status: accepted
- change_summary: Create `08_writing/chapter2_draft_v9.md` from the prior Chapter 2 wording and retain `08_writing/chapter2_draft_v10.md` as the humanized variant.
- reason: User requested archival of the older draft text in a separate v9 file while keeping the revised human-style v10 draft.
- evidence_basis: User-provided full Chapter 2 old-version text in chat and the existing edited state of `08_writing/chapter2_draft_v10.md`.
- affected_components: `08_writing/chapter2_draft_v9.md`, `08_writing/chapter2_draft_v10.md`, `00_admin/change_log.md`
- impact_assessment: Medium-positive. Preserves draft lineage and improves traceability between old and revised chapter variants.
- approval_record: Requested and confirmed by user in chat on 2026-03-15.

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
- affected_components: `07_implementation/implementation_notes/ingestion/ingest_history_parser.py`, `07_implementation/implementation_notes/alignment/align_tracks.py`, `07_implementation/implementation_notes/run_outputs/` (8 output files), `07_implementation/implementation_notes/test_assets/sample_listening_history.csv`, `07_implementation/implementation_notes/test_assets/sample_music4all_candidates.csv`, `07_implementation/backlog.md`, `07_implementation/test_notes.md`
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
- evidence_basis: `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md`; `07_implementation/experiment_log.md` EXP-DA-001; `06_data_and_sources/dataset_registry.md`; `00_admin/decision_log.md` D-008.
- affected_components: `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/unresolved_issues.md`, `06_data_and_sources/dataset_registry.md`, `07_implementation/backlog.md`, `07_implementation/implementation_plan.md`, `07_implementation/experiment_log.md`, `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md`
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
- evidence_basis: Current working-tree audit; `00_admin/decision_log.md` (`D-008`, `D-009`); `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md`; `.gitignore` dataset exclusion rule.
- affected_components: `.gitignore`, `00_admin/change_log.md`, `00_admin/decision_log.md`, `00_admin/unresolved_issues.md`, `06_data_and_sources/dataset_registry.md`, `06_data_and_sources/ds_002_msd_information_sheet.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/implementation_plan.md`, `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md`
- impact_assessment: High-positive. Preserves an auditable session snapshot without polluting the repository with large local dataset binaries.
- approval_record: Requested by user in chat on 2026-03-19.

## C-021
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Complete BL-009 observability logging for the bootstrap pipeline by implementing a deterministic run-level audit builder, generating the canonical observability artifacts, and synchronizing the implementation and governance records.
- reason: User requested that BL-009 be planned, implemented, and fully logged end to end.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-011`); `07_implementation/test_notes.md` (`TC-OBS-001`); generated artifacts `07_implementation/implementation_notes/observability/outputs/bl009_run_observability_log.json` and `07_implementation/implementation_notes/observability/outputs/bl009_run_index.csv`; backlog completion note for `BL-009`.
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `06_data_and_sources/schema_notes.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/observability/build_bl009_observability_log.py`, `07_implementation/implementation_notes/observability/outputs/bl009_run_observability_log.json`, `07_implementation/implementation_notes/observability/outputs/bl009_run_index.csv`
- impact_assessment: High-positive. Closes the observability evidence gap for the locked MVP, makes the bootstrap run chain auditable across BL-017 to BL-008, and prepares the ground for BL-010 reproducibility testing.
- approval_record: Requested by user in chat on 2026-03-21.

## C-022
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Complete BL-010 reproducibility testing by implementing a three-replay bootstrap runner, adding stable replay fingerprints for timestamped downstream artifacts, hardening BL-004 to BL-009 run-id precision, generating archived replay evidence, and synchronizing project governance records.
- reason: User requested that BL-010 be planned, implemented, and fully logged end to end.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-012`); `07_implementation/test_notes.md` (`TC-REPRO-001`); generated artifacts `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_config_snapshot.json`, `bl010_reproducibility_report.json`, `bl010_reproducibility_run_matrix.csv`, and archived replay directories `replay_01/` to `replay_03/`.
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/profile/build_bl004_preference_profile.py`, `07_implementation/implementation_notes/retrieval/build_bl005_candidate_filter.py`, `07_implementation/implementation_notes/scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/playlist/build_bl007_playlist.py`, `07_implementation/implementation_notes/transparency/build_bl008_explanation_payloads.py`, `07_implementation/implementation_notes/observability/build_bl009_observability_log.py`, `07_implementation/implementation_notes/reproducibility/run_bl010_reproducibility_check.py`, `07_implementation/implementation_notes/reproducibility/outputs/`
- impact_assessment: High-positive. Provides the locked MVP reproducibility evidence, removes rapid-replay run-id collisions, and establishes a reusable baseline for BL-011 controllability testing.
- approval_record: Requested by user in chat on 2026-03-21.

## C-023
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Retrospectively synchronize governance records for BL-004 by logging the completed deterministic preference-profile stage and its evidence artifacts in the change log.
- reason: A logging audit found that BL-004 had experiment and test evidence but no explicit `C-###` entry, which violates the implementation logging rule that every completed backlog item must have change-log coverage.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-006`); `07_implementation/test_notes.md` (`TC-PROFILE-001`); generated artifacts `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`, `bl004_profile_summary.json`, and `bl004_seed_trace.csv`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/profile/build_bl004_preference_profile.py`, `07_implementation/implementation_notes/profile/outputs/`
- impact_assessment: Medium-positive. Restores protocol-compliant governance traceability for the first core bootstrap pipeline stage without changing the underlying implementation outputs.
- approval_record: Logged during user-requested full logging audit on 2026-03-21.

## C-024
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Retrospectively synchronize governance records for BL-005 by logging the completed candidate-retrieval and filtering stage and its evidence artifacts in the change log.
- reason: A logging audit found that BL-005 had experiment and test evidence but no explicit `C-###` entry, which violates the implementation logging rule that every completed backlog item must have change-log coverage.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-007`); `07_implementation/test_notes.md` (`TC-CAND-001`); generated artifacts `07_implementation/implementation_notes/retrieval/outputs/bl005_filtered_candidates.csv`, `bl005_candidate_decisions.csv`, and `bl005_candidate_diagnostics.json`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/retrieval/build_bl005_candidate_filter.py`, `07_implementation/implementation_notes/retrieval/outputs/`
- impact_assessment: Medium-positive. Restores protocol-compliant governance traceability for the retrieval/filtering stage and makes the BL-005 evidence chain complete.
- approval_record: Logged during user-requested full logging audit on 2026-03-21.

## C-025
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Retrospectively synchronize governance records for BL-006 by logging the completed deterministic scoring stage and its evidence artifacts in the change log.
- reason: A logging audit found that BL-006 had experiment and test evidence but no explicit `C-###` entry, which violates the implementation logging rule that every completed backlog item must have change-log coverage.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-008`); `07_implementation/test_notes.md` (`TC-SCORE-001`); generated artifacts `07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv` and `bl006_score_summary.json`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/scoring/build_bl006_scored_candidates.py`, `07_implementation/implementation_notes/scoring/outputs/`
- impact_assessment: Medium-positive. Restores protocol-compliant governance traceability for the ranking stage and tightens the Chapter 4 evidence chain.
- approval_record: Logged during user-requested full logging audit on 2026-03-21.

## C-026
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Retrospectively synchronize governance records for BL-007 by logging the completed rule-based playlist-assembly stage and its evidence artifacts in the change log.
- reason: A logging audit found that BL-007 had experiment and test evidence but no explicit `C-###` entry, which violates the implementation logging rule that every completed backlog item must have change-log coverage.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-009`); `07_implementation/test_notes.md` (`TC-PLAYLIST-001`); generated artifacts `07_implementation/implementation_notes/playlist/outputs/bl007_playlist.json`, `bl007_assembly_trace.csv`, and `bl007_assembly_report.json`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/playlist/build_bl007_playlist.py`, `07_implementation/implementation_notes/playlist/outputs/`
- impact_assessment: Medium-positive. Restores protocol-compliant governance traceability for the assembly stage and completes the audit trail from ranking to playlist output.
- approval_record: Logged during user-requested full logging audit on 2026-03-21.

## C-027
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Retrospectively synchronize governance records for BL-008 by logging the completed transparency-output stage and its evidence artifacts in the change log.
- reason: A logging audit found that BL-008 had experiment and test evidence but no explicit `C-###` entry, which violates the implementation logging rule that every completed backlog item must have change-log coverage.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-010`); `07_implementation/test_notes.md` (`TC-EXPLAIN-001`); generated artifacts `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_payloads.json` and `bl008_explanation_summary.json`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/transparency/build_bl008_explanation_payloads.py`, `07_implementation/implementation_notes/transparency/outputs/`
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
- evidence_basis: `00_admin/evaluation_plan.md` (`EP-CTRL-001`, `EP-CTRL-002`, `EP-CTRL-003`); `05_design/controllability_design.md`; `07_implementation/experiment_log.md` (`EXP-013` planned state); `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_config_snapshot.json`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/implementation_notes/controllability/`
- impact_assessment: Medium-positive. Establishes a protocol-compliant start state for BL-011 and ties the next evaluation step directly to the verified BL-010 baseline.
- approval_record: Requested by user in chat on 2026-03-21.

## C-031
- date: 2026-03-21
- proposed_by: user + AI
- status: accepted
- change_summary: Complete BL-011 controllability testing by implementing a dedicated OFAT scenario runner, generating archived baseline and variant outputs, fixing one volatile-hash normalization defect in the repeat check, and synchronizing the implementation and governance records.
- reason: User requested that BL-011 be planned, implemented, and fully logged end to end.
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-013`); `07_implementation/test_notes.md` (`TC-005`, `TC-006`, `TC-007`); generated artifacts `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_config_snapshot.json`, `bl011_controllability_report.json`, `bl011_controllability_run_matrix.csv`, and archived scenario directories under `07_implementation/implementation_notes/controllability/outputs/scenarios/`.
- affected_components: `00_admin/change_log.md`, `00_admin/decision_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/controllability/run_bl011_controllability_check.py`, `07_implementation/implementation_notes/controllability/outputs/`
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
- evidence_basis: `07_implementation/experiment_log.md` (`EXP-015`); `07_implementation/test_notes.md` (`TC-CLI-001`); orchestration artifacts under `07_implementation/implementation_notes/entrypoint/`.
- affected_components: `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py`, `07_implementation/implementation_notes/entrypoint/bl013_run_command.md`, `07_implementation/implementation_notes/entrypoint/outputs/`
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
- evidence_basis: `07_implementation/experiment_log.md` (EXP-016, status pass); `07_implementation/test_notes.md` (TC-DATASET-001, status pass); `07_implementation/implementation_notes/data_layer/outputs/bl019_ds002_integrated_candidate_dataset.csv` (SHA256 `b9c729a2...`); `07_implementation/implementation_notes/data_layer/outputs/bl019_ds002_integration_report.json` (9330 rows, elapsed 26.984 s, all quality gates pass); two-run hash match confirmed.
- affected_components: `00_admin/change_log.md`, `00_admin/thesis_state.md`, `06_data_and_sources/dataset_registry.md`, `07_implementation/backlog.md`, `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`
- impact_assessment: High-positive. DS-002 candidate corpus is now a verified, reproducible artefact ready for downstream ingestion and alignment stages.
- approval_record: Requested by user in chat on 2026-03-21.