# Change Log

Use schema from `00_admin/operating_protocol.md`.

## C-001

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
