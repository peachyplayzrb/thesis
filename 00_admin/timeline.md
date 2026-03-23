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

## Notes
- Dates are a working baseline for execution control and can be refined against official module deadlines.
- Scope remains locked to the MVP boundary in `00_admin/thesis_state.md` and `00_admin/Artefact_MVP_definition.md`.
