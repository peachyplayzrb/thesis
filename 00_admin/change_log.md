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

## C-008
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