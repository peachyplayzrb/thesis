# Thesis Timeline

Last updated: 2026-03-25

## Milestones
- M1 (2026-03-13 to 2026-03-20): Planning baseline finalized [completed]
	- Populate backlog, implementation plan, and chapter readiness checklist.
	- Confirm evaluation protocol and reproducibility evidence format.
- M2 (2026-03-21 to 2026-04-05): Data ingestion and DS-001 alignment baseline [in progress]
	- Implement one ingestion path for listening history import.
	- Implement DS-001 metadata/identifier alignment path for imported listening history.
	- Implement source-scope actuation and persist effective scope in run outputs.
	- Log alignment diagnostics, coverage, and traceability artifacts.
- M3 (2026-04-06 to 2026-04-20): Deterministic profile and scoring implemented [planned]
	- Build deterministic user profile construction.
	- Implement candidate filtering and deterministic similarity scoring.
	- Add score contribution breakdown outputs.
- M4 (2026-04-21 to 2026-05-05): Playlist assembly and controllability layer complete [planned]
	- Implement playlist-level rule checks (diversity, coherence, ordering).
	- Add configurable rule parameters and run-level config capture.
	- Validate deterministic behavior across repeated runs.
- M5 (2026-05-06 to 2026-05-20): Evaluation evidence complete [planned]
	- Run reproducibility checks and parameter sensitivity tests.
	- Record transparency/inspectability artifacts and known limitations.
	- Consolidate claim-evidence mapping for report chapters.
- M6 (2026-05-21 to 2026-06-10): Writing and submission hardening [planned]
	- Finalize chapter drafts, references, and formatting compliance.
	- Complete final quality-control passes and viva/demo preparation.

## Active Work Packages
- WP-CITE-001 (2026-03-19 to 2026-03-29): Thesis-wide citation hardening and literature leverage pass [in progress]
	- Build claim-citation matrix from Chapter 2 and extend to Chapters 3 to 5 where literature-backed claims are made.
	- Verify each claim against cited PDFs in `10_resources/papers/` and classify support strength.
	- Extract high-value findings, limitations, and trade-off evidence for chapter strengthening.
	- Produce citation replacement recommendations and chapter-targeted hardening notes.
	- Current status note (2026-03-25): UI-003 remains open; package window extended for synthesis closeout and chapter-targeted insertion pass.

- WP-DRAFT-001 (2026-03-23 to 2026-03-29): 7-day mentor-ready full-draft sprint [in progress]
	- Execute day-by-day writing/evidence/coherence plan in `00_admin/mentor_draft_7day_sprint_2026-03-23.md`.
	- Prioritize chapter-to-artefact alignment and claim-evidence traceability over new feature expansion.
	- Freeze mentor package on Day 7 with explicit feedback questions and bounded limitations.
	- Day 1 closure note (2026-03-23): scope-lock and skeleton-alignment pass is now audit-backed, including Chapter 1 skeleton completion in `08_writing/chapter1.md`, evidence-bounded hardening edits in `08_writing/chapter2.md`, `08_writing/chapter3.md`, and `08_writing/chapter5.md`, and QC logging in `09_quality_control/chapter_readiness_checks.md`.
	- Day 2 closure note (2026-03-24): evidence-bounded hardening completed on Chapter 2 with targeted wording refinements; Chapters 1 and 3 confirmed aligned to architecture and thesis state.
	- Day 3 closure note (2026-03-24): systematic hardening completed and UI-002 remediation objective closed for current audit workflow (`TOTAL_KEYS_WITH_WEAK=0`).
	- Day 4 active note (2026-03-25): implementation/results chapter alignment and evaluation narrative tightening are the current execution focus.

- WP-WEBINT-001 (2026-03-23 to 2026-03-30): Freeze-and-integrate website execution package [in progress]
	- Freeze current BL-020 pipeline behavior as the baseline for this package; allow only bug fixes, observability improvements, and integration wiring.
	- Integrate `07_implementation/website/` pages with real run artifacts and deterministic pipeline invocation flow (`import` -> `profile` -> `filter` -> `score` -> `playlist` -> `explain` -> `observe`).
	- Prioritize UI-mediated inspectability: surface run id, stage status, key counts, and artifact links in the website flow.
	- Execute implementation refinement in parallel: stability hardening, clearer error handling around external API steps, and repeatable rerun controls for reproducibility evidence.
	- Keep deferred scope unchanged (`BL-022`), and avoid adding new adapters or model classes during this package.

## Recently Closed
- UI-002 closure recorded (2026-03-24): Chapter 2 weak-claim remediation objective completed for current audit workflow.
- BL-021 source-scope contract closure recorded (2026-03-24): source-scope behavior promoted from deferred design to implemented baseline.

## Notes
- Dates are a working baseline for execution control and can be refined against official module deadlines.
- Scope remains locked to the MVP boundary in `00_admin/thesis_state.md` and `00_admin/Artefact_MVP_definition.md`.
- Operational source of truth for open blockers remains `00_admin/unresolved_issues.md`.
- Sprint execution truth remains `00_admin/mentor_draft_7day_sprint_2026-03-23.md`.
