# Mentor Draft 7-Day Sprint (2026-03-23)

Purpose: produce a full, coherent thesis draft in 7 days that reflects the current artefact and is ready for mentor review.

## Outcome Target (Day 7)
- Full draft assembled (Chapters 1 to 5 + references).
- Claims aligned to implemented artefact behavior.
- Core citations mapped and checked against local PDF corpus.
- Clear mentor handoff package with priority feedback questions.

## Daily Operating Rule
- Work in three blocks each day:
  1. writing block (new text)
  2. evidence block (citations and claim checks)
  3. coherence block (cross-chapter consistency)
- End each day by logging updates to:
  - `00_admin/change_log.md`
  - `00_admin/thesis_state.md` (if scope/positioning changed)
  - `09_quality_control/*` artifacts for checks performed

## Day 1 - Scope Lock and Skeleton Alignment
- [x] Confirm implemented-vs-deferred boundaries in `00_admin/thesis_state.md`.
- [x] Ensure unresolved priorities are explicit in `00_admin/unresolved_issues.md`.
- [x] Create or refresh chapter skeleton headings in `08_writing/` drafts.
- [x] Ensure chapter objective statements map to current artefact.

Exit criteria:
- No scope ambiguity remains between artefact and thesis narrative.

## Day 2 - Chapter 1 and Chapter 3 Full Pass
- [ ] Refine Chapter 1 problem/objectives/contribution claims.
- [ ] Refine Chapter 3 methodology/design to match actual implementation choices.
- [ ] Cross-check with:
  - `05_design/architecture.md`
  - `05_design/system_architecture.md`
  - `05_design/requirements_to_design_map.md`

Exit criteria:
- Intro and methodology are implementation-faithful and internally consistent.

## Day 3 - Chapter 2 Literature Hardening Pass
- [ ] Map all major Chapter 2 claims to specific paper-note evidence.
- [ ] Use current audited corpus and notes:
  - `03_literature/paper_notes/`
  - `03_literature/paper_note_pdf_audit_full_2026-03-23.md`
- [ ] Tighten or reword over-claimed statements.
- [ ] Update `09_quality_control/claim_evidence_map.md` where needed.

Exit criteria:
- Each major literature claim has support quality identified (strong/partial/weak).

## Day 4 - Chapter 4 Implementation and Chapter 5 Evaluation
- [ ] Document implementation pipeline stages from actual artifacts in `07_implementation/`.
- [ ] Align Chapter 5 results/evaluation interpretation with available runs and logs.
- [ ] Remove unsupported claims about features not implemented.

Exit criteria:
- Reader can trace from implementation decisions to reported outcomes.

## Day 5 - Thesis-wide Coherence and QC Pass
- [ ] Run chapter-level consistency checks in `09_quality_control/`.
- [ ] Verify terminology consistency (same terms used across chapters).
- [ ] Check all figure/table references resolve and captions are clear.
- [ ] Ensure limitations are explicit and not contradictory.

Exit criteria:
- No major cross-chapter contradictions remain.

## Day 6 - Polish and Mentor-Readability Pass
- [ ] Improve flow, transitions, and chapter openings/closings.
- [ ] Tighten language and remove repetition.
- [ ] Ensure references are clean and consistent with `08_writing/references.bib`.
- [ ] Produce near-final PDF/compiled draft for final review.

Exit criteria:
- Draft reads as one coherent thesis, not stitched sections.

## Day 7 - Mentor Package Finalization
- [ ] Freeze mentor draft version.
- [ ] Write a concise mentor brief with:
  - what changed this week
  - top 5 feedback questions
  - known bounded weaknesses
- [ ] Log handoff in `00_admin/change_log.md` and `00_admin/mentor_feedback_log.md`.

Exit criteria:
- Mentor receives full draft + targeted feedback prompts.

## Guardrails for This Week
- Defer full new website/UI build unless all daily targets are complete early.
- Prefer defendability and evidence traceability over feature expansion.
- Keep all new claims evidence-backed in local corpus.

## Minimum Mentor-Ready Acceptance Checklist
- [ ] Full draft exists for all required chapters.
- [ ] Citation evidence is mapped for core claims.
- [ ] Artefact description matches implemented behavior.
- [ ] Remaining risks are clearly declared as limitations/deferred work.
