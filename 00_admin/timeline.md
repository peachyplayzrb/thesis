# Thesis Timeline

## Milestones
- M1 (2026-03-13 to 2026-03-20): Planning baseline finalized
	- Populate backlog, implementation plan, and chapter readiness checklist.
	- Confirm evaluation protocol and reproducibility evidence format.
- M2 (2026-03-21 to 2026-04-05): Data ingestion and alignment working
	- Implement one ingestion path for listening history import.
	- Implement ISRC-first alignment with fallback metadata matching.
	- Log unmatched track rate and alignment diagnostics.
- M3 (2026-04-06 to 2026-04-20): Deterministic profile and scoring implemented
	- Build deterministic user profile construction.
	- Implement candidate filtering and deterministic similarity scoring.
	- Add score contribution breakdown outputs.
- M4 (2026-04-21 to 2026-05-05): Playlist assembly and controllability layer complete
	- Implement playlist-level rule checks (diversity, coherence, ordering).
	- Add configurable rule parameters and run-level config capture.
	- Validate deterministic behavior across repeated runs.
- M5 (2026-05-06 to 2026-05-20): Evaluation evidence complete
	- Run reproducibility checks and parameter sensitivity tests.
	- Record transparency/inspectability artifacts and known limitations.
	- Consolidate claim-evidence mapping for report chapters.
- M6 (2026-05-21 to 2026-06-10): Writing and submission hardening
	- Finalize chapter drafts, references, and formatting compliance.
	- Complete final quality-control passes and viva/demo preparation.

## Immediate Work Package (Active)
- WP-CITE-001 (2026-03-19 to 2026-03-24): Thesis-wide citation hardening and literature leverage pass
	- Build claim-citation matrix from Chapter 2 and extend to Chapters 3 to 5 where literature-backed claims are made.
	- Verify each claim against cited PDFs in `10_resources/papers/` and classify support strength.
	- Extract high-value findings, limitations, and trade-off evidence for chapter strengthening.
	- Produce citation replacement recommendations and chapter-targeted hardening notes.

- WP-DRAFT-001 (2026-03-23 to 2026-03-29): 7-day mentor-ready full-draft sprint
	- Execute day-by-day writing/evidence/coherence plan in `00_admin/mentor_draft_7day_sprint_2026-03-23.md`.
	- Prioritize chapter-to-artefact alignment and claim-evidence traceability over new feature expansion.
	- Freeze mentor package on Day 7 with explicit feedback questions and bounded limitations.
	- Day 1 closure note (2026-03-23): scope-lock and skeleton-alignment pass is now audit-backed, including Chapter 1 skeleton completion in `08_writing/chapter1.md`, evidence-bounded hardening edits in `08_writing/chapter2.md`, `08_writing/chapter3.md`, and `08_writing/chapter5.md`, and QC logging in `09_quality_control/chapter_readiness_checks.md`.
	- Day 2 closure note (2026-03-24): evidence-bounded hardening completed on Chapter 2 with 8 targeted wording refinements to address weak-support claims in verbatim audit baseline. Chapters 1 and 3 confirmed aligned to architecture and thesis_state.md. Claim-citation matrix extended with explicit mapping entries (C-CLM-001 through C-CLM-023, extended). UI-002 remains open pending rerun of chapter2_verbatim_audit.md to measure weak_support reduction from hardening edits.
	- Day 3 next actions (2026-03-25): execute targeted literature-to-chapter hardening for Chapters 2 and 3 using extracted paper-note evidence (high-value direct quotes and claims from `10_resources/papers/_extracted_claim_check/`). Rerun chapter2_verbatim_audit.md on current Chapter 2 text to measure weak_support delta. Prioritize closure path for UI-002 if audit still shows elevated weak_support (weak_support > 12).

- WP-WEBINT-001 (2026-03-23 to 2026-03-30): Freeze-and-integrate website execution package
	- Freeze current BL-020 pipeline behavior as the baseline for this package; allow only bug fixes, observability improvements, and integration wiring.
	- Integrate `07_implementation/website/` pages with real run artifacts and deterministic pipeline invocation flow (`import` -> `profile` -> `filter` -> `score` -> `playlist` -> `explain` -> `observe`).
	- Prioritize UI-mediated inspectability: surface run id, stage status, key counts, and artifact links in the website flow.
	- Execute implementation refinement in parallel: stability hardening, clearer error handling around external API steps, and repeatable rerun controls for reproducibility evidence.
	- Keep deferred scope unchanged (`BL-021`, `BL-022`), and avoid adding new adapters or model classes during this package.


## Notes
- Dates are a working baseline for execution control and can be refined against official module deadlines.
- Scope remains locked to the MVP boundary in `00_admin/thesis_state.md` and `00_admin/Artefact_MVP_definition.md`.
