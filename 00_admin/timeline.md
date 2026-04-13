# Thesis Timeline

Last updated: 2026-04-13

## REBUILD PHASE (active from 2026-04-12)

Full architecture rebuild initiated (D-052). Chapter 2 is the only confirmed component. All milestones and work packages below are now pre-rebuild legacy reference unless explicitly re-opened in this rebuild phase.

- REB-M1 (2026-04-12 onwards): Re-derive RQ and objectives from Chapter 2 gaps and themes [completed]
	- Identify unresolved contradictions in Chapter 2 (transparency/accuracy, explanation fidelity, candidate-generation primacy, cross-source alignment, multi-objective quality)
	- Re-derive the research question and objectives that address those gaps in a DSR/engineering-evidence framing
	- Confirm scope and artefact definition before any implementation restarts
	- Status update (2026-04-12): completed via D-053 and D-054 with synchronized foundation/admin updates (C-283).

- REB-M2 (2026-04-12 onwards): Rebuild Chapter 3 (design) anchored in Chapter 2 conclusions [completed]
	- Convert the six active objectives into explicit design requirements and traceability links.
	- Define the active control/evidence surface needed to test uncertainty handling, controllability, and reproducibility claims.
	- Produce a bounded Chapter 3 rebuild outline before any implementation restart decisions.
	- Status update (2026-04-12): completed via objective-anchored Chapter 3 design lock and requirements-map rebuild (D-055, C-284).
- REB-M3 (2026-04-12 onwards): Rebuild implementation and evaluation to match re-grounded design [completed]
	- Apply artefact-definition switch from checkpoint wording to implementation-entry control/evidence contract.
	- Rebuild implementation surfaces only where O1 to O6 traceability and evidence contracts can be preserved.
	- Gate each implementation tranche on reproducibility, controllability, transparency-fidelity, and uncertainty-visibility checks.
	- Status update (2026-04-12): kickoff accepted via D-056 and synchronized in C-285.
	- Status update (2026-04-12): tranche-1 executable O1 to O3 gate implemented at `07_implementation/src/quality/reb_m3_tranche1_gate.py` and documented for execution (D-057, C-286).
	- Status update (2026-04-12): tranche-2 executable O4 to O6 gate implemented at `07_implementation/src/quality/reb_m3_tranche2_gate.py` and documented for execution (D-058, C-287).
	- Status update (2026-04-12): tranche-3 control-causality/validity-boundary gate is now passing (`REB-M3-TRANCHE3-GATE-20260412-140805-553785`, `9/9`) after BL-009 schema correction that restores top-level `validity_boundaries` contract alignment (D-062, C-291).
	- Status update (2026-04-12): follow-up regression hardening is complete for BL-009 section validation; `ensure_required_sections` now requires top-level `validity_boundaries` and dedicated tests pass, with full validation chain still green (`338/338`, `BL013-ENTRYPOINT-20260412-141352-373476`, `BL014-SANITY-20260412-141423-183313`, tranche-3 `REB-M3-TRANCHE3-GATE-20260412-141431-157169`) (D-063, C-292).
	- Closure update (2026-04-12): REB-M3 implementation/evidence rebuild is complete; tranche gates, wrapper validation, and regression hardening are green, and remaining work has moved to chapter proofing and submission packaging (D-066, C-296).
	- Post-closure enhancement update (2026-04-12): item-4 influence-policy implementation wave is now active and passing validation with additive BL-007 policy controls plus BL-009 per-track influence diagnostics (`342/342`, pyright clean, `BL013-ENTRYPOINT-20260412-150114-734913`, `BL014-SANITY-20260412-150146-906654`) (D-067, C-297).
	- Post-closure enhancement update (2026-04-12): BL-003 now accepts `user_csv` as a 5th advisory source with album-aware fuzzy scoring. A live sample `user_csv_flat.csv` using alias-exercising headers was validated end-to-end; wrapper pass `BL013-ENTRYPOINT-20260412-211514-304085` and sanity pass `BL014-SANITY-20260412-211538-292523` (`28/28`) both succeeded, and BL-003/BL-009 outputs recorded `user_csv=10` rows selected under advisory policy (D-078, C-310, C-311).
	- Post-closure enhancement update (2026-04-12): BL-003 fuzzy fallback is now configurable in wave 1 without changing exact-match precedence. New controls cover secondary-artist retry, relaxed second pass, explicit album-scoring control, and additive fuzzy diagnostics; targeted pytest (`97/97`), full pytest (`411/411`), and wrapper validate-only pass (`BL013-ENTRYPOINT-20260412-213836-591492`, `BL014-SANITY-20260412-213859-249947`, `28/28`) are green (D-079, C-312).
	- Post-closure enhancement update (2026-04-13): Phase A diagnostics-first fallback hardening is implemented additively across BL-003 and BL-004. BL-003 now emits runtime-scope parse diagnostics and resolution-path metadata, while BL-004 now emits explicit fallback counters for confidence/default/synthetic paths. Validation is green on targeted tests (`38/38`) and wrapper validate-only (`BL013-ENTRYPOINT-20260413-001017-614914`, `BL014-SANITY-20260413-001042-070086`, `28/28`) (D-081, C-314).
	- Post-closure enhancement update (2026-04-13): BL-004 strict validation policy controls are now available per fallback family (`allow|warn|strict`) for confidence, interaction-type, and synthetic-data fallback paths, with default warn-compatible behavior and strict-mode fail-fast enforcement. Validation remains green on focused tests (`41/41`) and wrapper validate-only (`BL013-ENTRYPOINT-20260413-001816-449005`, `BL014-SANITY-20260413-001850-553405`, `28/28`) (D-082, C-315).
	- Post-closure enhancement update (2026-04-13): BL-004 attribution and numeric-integrity hardening now separates malformed vs true no-signal paths and supports optional fail-fast thresholds for numeric drift (`numeric_malformed_row_threshold`, `no_numeric_signal_row_threshold`). New diagnostics include malformed confidence/count/weight and numeric-feature counters. Validation remains green on focused tests (`43/43`) and wrapper validate-only (`BL013-ENTRYPOINT-20260413-002608-855860`, `BL014-SANITY-20260413-002636-061270`, `28/28`) (D-083, C-316).
	- Post-closure enhancement update (2026-04-13): BL-004 cross-BL contract handshake enforcement is now active with policy-controlled (`allow|warn|strict`) validation of BL-003 prerequisite fields (`runtime_scope_diagnostics` in summary inputs and `match_confidence_score` in seed schema). Handshake warnings are surfaced additively in BL-004 diagnostics and can fail fast under strict policy. Validation remains green on focused tests (`43/43`) and wrapper validate-only (`BL013-ENTRYPOINT-20260413-003304-652082`, `BL014-SANITY-20260413-003326-987801`, `28/28`) (D-084, C-317).
	- Post-closure enhancement update (2026-04-13): BL-004 handshake strict-negative coverage is now explicit in test surfaces. New tests validate warn-path warning emission and strict-path fail-fast for missing handshake-required BL-003 fields, and run-config profile controls now assert handshake policy fallback/normalization. Validation remains green on focused tests (`47/47`) and wrapper validate-only (`BL013-ENTRYPOINT-20260413-003752-142736`, `BL014-SANITY-20260413-003814-485246`, `28/28`) (D-085, C-318).
	- Post-closure enhancement update (2026-04-13): BL-014 now enforces wrapper-level BL-003↔BL-004 handshake continuity via new sanity check `schema_bl003_bl004_handshake_contract` (BL-003 summary inputs + structural seed fields + BL-004 diagnostics policy metadata). Validation remains green on targeted pytest (`56/56`) and wrapper validate-only (`BL013-ENTRYPOINT-20260413-004155-782240`, `BL014-SANITY-20260413-004220-078507`, `29/29`) (D-086, C-319).
	- Post-closure enhancement update (2026-04-13): BL-014 Slice 15 advisory hardening is complete. BL-014 now emits `advisory_bl005_handshake_warning_volume` when BL-005 handshake validation is warn-mode with elevated violation volume beyond threshold, while preserving pass/fail check contracts and wrapper compatibility. Validation remains green on focused tests (`14/14`) and wrapper validate-only (`BL013-ENTRYPOINT-20260413-104436-925545`, `BL014-SANITY-20260413-104503-647428`, `30/30`) (D-091, C-324).
	- Post-closure enhancement update (2026-04-13): BL-005 Slice 16 parity closure is complete. Retrieval handshake validation now includes seed-trace confidence row-quality checks (missing/non-numeric/out-of-range) under existing policy semantics (`allow|warn|strict`), and BL-014 now has symmetric main-level negative-fixture evidence for `schema_bl004_bl005_handshake_contract` failure behavior. Validation remains green on targeted tests (`20/20`) and wrapper validate-only (`BL013-ENTRYPOINT-20260413-105724-234842`, `BL014-SANITY-20260413-105751-328487`, `30/30`) (D-092, C-325).
	- Post-closure enhancement update (2026-04-13): BL-005 Slice 17 runtime-control diagnostics parity is complete. Retrieval runtime controls now emit explicit payload-parse and normalization/coercion diagnostics, and BL-005 diagnostics payloads now persist runtime-control resolution metadata plus validation warnings for audit visibility without changing filter behavior. Validation remains green on focused tests (`9/9`) and wrapper validate-only (`BL013-ENTRYPOINT-20260413-111111-723084`, `BL014-SANITY-20260413-111136-703270`, `30/30`) (D-093, C-326).
	- Post-closure enhancement update (2026-04-13): BL-005 Slice 18 advisory visibility is complete. BL-014 now emits `advisory_bl005_control_resolution_fallback_volume` for elevated BL-005 runtime-control normalization volume and records the advisory threshold in config snapshot metadata; validation remains green on focused tests (`27/27`) and wrapper validate-only (`BL013-ENTRYPOINT-20260413-111934-887225`, `BL014-SANITY-20260413-111957-022045`, `30/30`) (D-094, C-327).
	- Post-closure enhancement update (2026-04-13): BL-014 negative-fixture evidence for the handshake gate is now implemented. A temp-artifact integration test proves `quality.sanity_checks.main()` fails specifically on `schema_bl003_bl004_handshake_contract` when BL-003 handshake inputs are stripped, while normal wrapper validation remains green (`57/57`; `BL013-ENTRYPOINT-20260413-004657-028023`, `BL014-SANITY-20260413-004719-088476`, `29/29`) (D-087, C-320).
	- Post-closure enhancement update (2026-04-13): BL-004 handshake controls now include row-quality confidence checks and strict synthetic-weight reconstruction fail-fast behavior, and BL-003 summary outputs now emit unmatched-reason histogram/classification for clearer coverage-vs-input interpretation. Validation remains green on focused pytest (`25/25`) and wrapper validate-only (`BL013-ENTRYPOINT-20260413-011824-759642`, `BL014-SANITY-20260413-011850-557804`, `29/29`) (D-088, C-321).
	- Post-closure enhancement update (2026-04-13): BL-003/BL-004 semantic-alignment clarity slice is complete. BL-004 now emits additive diagnostics basis metadata and BL-003 event-level companion counters to prevent row/event granularity ambiguity, and BL-004 profile/summary payloads now carry `bl003_config_source` for provenance continuity. Validation remains green on focused pytest (`24/24`), touched-file pyright clean (`0 errors` on edited profile files), and wrapper validate-only (`BL013-ENTRYPOINT-20260413-014731-291681`, `BL014-SANITY-20260413-014753-532309`, `29/29`) (D-089, C-322).
	- Post-closure enhancement update (2026-04-13): BL-005 Slice 14 handshake hardening is complete. Retrieval now enforces policy-gated BL-004 handshake validation (`allow|warn|strict`) with additive diagnostics, run-config/runtime now expose `bl004_bl005_handshake_validation_policy`, and BL-014 now enforces wrapper continuity via `schema_bl004_bl005_handshake_contract`. Validation remains green on focused pytest (`48/48`), touched-file pyright (`0 errors`), and wrapper validate-only (`BL013-ENTRYPOINT-20260413-103628-028213`, `BL014-SANITY-20260413-103658-484887`, `30/30`) (D-090, C-323).
- REB-M4 (2026-04-12 onwards): Rebuild Chapter 4/5 from re-evidenced implementation and evaluation [completed]
	- Replace pre-rebuild Chapter 4/5 framing with objective-linked implementation, evaluation, and discussion structure.
	- Anchor chapter claims to active `07_implementation/src` evidence artifacts and REB-M3 tranche gates.
	- Keep all Chapter 5 interpretation bounded to explicit uncertainty, control, and validity-boundary evidence.
	- Status update (2026-04-12): kickoff accepted via D-064; `08_writing/chapter4.md` and `08_writing/chapter5.md` were rebuilt to the active O1 to O6 evidence contract using current tranche-gate and validation artifacts (C-294).
	- Status update (2026-04-12): quality-control mirrors were synchronized to the rebuild posture via updated readiness, RQ-alignment, claim-evidence, and claim-verdict surfaces (`09_quality_control/chapter_readiness_checks.md`, `09_quality_control/rq_alignment_checks.md`, `09_quality_control/claim_evidence_map.md`, `09_quality_control/ui003_claim_verdicts_ch3_ch5.md`) under D-065 / C-295.
	- Closure update (2026-04-12): Chapter 4/5 citation-density hardening is complete, chapter-facing interpretation now carries explicit literature anchors, and the remaining open work is outside REB-M4 (submission proofing/packaging) rather than rebuild alignment (D-066, C-296).

---

## Legacy Milestones (pre-rebuild — frozen 2026-04-12)


- M1 (2026-03-13 to 2026-03-20): Planning baseline finalized [completed]
	- Populate backlog, implementation plan, and chapter readiness checklist.
	- Confirm evaluation protocol and reproducibility evidence format.
- M2 (2026-03-21 to 2026-04-05): Data ingestion and DS-001 alignment baseline [completed]
	- Implement one ingestion path for listening history import.
	- Implement DS-001 metadata/identifier alignment path for imported listening history.
	- Implement source-scope actuation and persist effective scope in run outputs.
	- Log alignment diagnostics, coverage, and traceability artifacts.
- M3 (2026-04-06 to 2026-04-20): Deterministic profile and scoring implemented [completed]
	- Build deterministic user profile construction.
	- Implement candidate filtering and deterministic similarity scoring.
	- Add score contribution breakdown outputs.
- M4 (2026-04-21 to 2026-05-05): Playlist assembly and controllability layer complete [completed]
	- Implement playlist-level rule checks (diversity, coherence, ordering).
	- Add configurable rule parameters and run-level config capture.
	- Validate deterministic behavior across repeated runs.
	- Status note (2026-03-25): BL-004 through BL-009 implementation is complete and validated; remaining scope in M3/M4 is evidence packaging and chapter-facing synthesis alignment.
- M5 (2026-05-06 to 2026-05-20): Evaluation evidence complete [in progress]
	- Run reproducibility checks and parameter sensitivity tests.
	- Record transparency/inspectability artifacts and known limitations.
	- Consolidate claim-evidence mapping for report chapters.
- M6 (2026-05-21 to 2026-06-10): Writing and submission hardening [in progress]
	- Finalize chapter drafts, references, and formatting compliance.
	- Complete final quality-control passes and viva/demo preparation.
	- Status note (2026-04-12): Chapter 2 mentor-ready draft sent for supervisor review; awaiting feedback under `MQ-009`.

## Active Work Packages
- WP-CITE-001 (2026-03-19 to 2026-03-29): Thesis-wide citation hardening and literature leverage pass [completed]
	- Build claim-citation matrix from Chapter 2 and extend to Chapters 3 to 5 where literature-backed claims are made.
	- Verify each claim against cited PDFs in `10_resources/papers/` and classify support strength.
	- Extract high-value findings, limitations, and trade-off evidence for chapter strengthening.
	- Produce citation replacement recommendations and chapter-targeted hardening notes.
	- Current status note (2026-03-27): UI-003 control-record closure is complete; remaining work is chapter-level hardening follow-through and insertion-quality checks.
	- Closure note (2026-03-29): WP-CITE-001 follow-through is complete. All chapter hardening actions recorded in `09_quality_control/ui003_chapter_hardening_notes_ch3_ch5.md` are applied or explicitly deferred with rationale. This work package is closed.

- WP-DRAFT-001 (2026-03-23 to 2026-03-29): 7-day mentor-ready full-draft sprint [completed]
	- Execute day-by-day writing/evidence/coherence plan in `00_admin/mentor_draft_7day_sprint_2026-03-23.md`.
	- Prioritize chapter-to-artefact alignment and claim-evidence traceability over new feature expansion.
	- Freeze mentor package on Day 7 with explicit feedback questions and bounded limitations.
	- Day 1 closure note (2026-03-23): scope-lock and skeleton-alignment pass is now audit-backed, including Chapter 1 skeleton completion in `08_writing/chapter1.md`, evidence-bounded hardening edits in `08_writing/chapter2.md`, `08_writing/chapter3.md`, and `08_writing/chapter5.md`, and QC logging in `09_quality_control/chapter_readiness_checks.md`.
	- Day 2 closure note (2026-03-24): evidence-bounded hardening completed on Chapter 2 with targeted wording refinements; Chapters 1 and 3 confirmed aligned to architecture and thesis state.
	- Day 3 closure note (2026-03-24): systematic hardening completed and UI-002 remediation objective closed for current audit workflow (`TOTAL_KEYS_WITH_WEAK=0`).
	- Day 4 active note (2026-03-25): implementation/results chapter alignment and evaluation narrative tightening are the current execution focus.
	- Day 5 status note (2026-03-28 03:41 UTC): admin-first synchronization completed across baseline authority, thesis state, MVP definition, and chapter readiness gates before chapter text hardening proceeds.
	- Day 5 execution note (2026-03-28 03:46 UTC): chapter hardening pass started and applied to Chapter 3 and Chapter 4, including stale metric correction and population of previously pending implementation/evaluation result tables.
	- Day 6 closure note (2026-03-29): architecture migration wave completed (BL-003 typed boundaries, BL-003 stage-shell, BL-004/BL-005/BL-006/BL-007 OO-stage migration, BL-004 through BL-007 controllable-logic uplift). Documentation sync wave closed (C-219). All chapters remain aligned to v1f canonical baseline.
	- Day 7 note (2026-03-29): 00_admin full synchronization wave now in progress (C-220). Remaining active work is physical submission packaging (Canvas deadline, cover/declaration template, Turnitin package).

- WP-WEBINT-001 (2026-03-23 to 2026-03-30): Freeze-and-integrate website execution package [completed]
	- Freeze current BL-020 pipeline behavior as the baseline for this package; allow only bug fixes, observability improvements, and integration wiring.
	- Integrate `07_implementation/website/` pages with real run artifacts and deterministic pipeline invocation flow (`import` -> `profile` -> `filter` -> `score` -> `playlist` -> `explain` -> `observe`).
	- Prioritize UI-mediated inspectability: surface run id, stage status, key counts, and artifact links in the website flow.
	- Execute implementation refinement in parallel: stability hardening, clearer error handling around external API steps, and repeatable rerun controls for reproducibility evidence.
	- Keep deferred scope unchanged (`BL-022`), and avoid adding new adapters or model classes during this package.
	- Current status note (2026-03-29): workflow shell and results-clarity implementation pass remains complete, FastAPI server hardening plus automated API regression coverage remain in place, and the bounded modular cleanup pass is now closed across BL-013 orchestration, BL-011 controllability, and BL-003 alignment support code. This work package is complete; remaining open scope is physical submission packaging only.

## Recently Closed
- UI-002 closure recorded (2026-03-24): Chapter 2 weak-claim remediation objective completed for current audit workflow.
- BL-021 source-scope contract closure recorded (2026-03-24): source-scope behavior promoted from deferred design to implemented baseline.
- Tier-1 remediation package closure recorded (2026-03-25): CRI-004, CRI-002, HIGH-003, HIGH-004, and CRI-003 all completed with governance logging and test evidence.
- Integrated validation closure recorded (2026-03-25): BL-013 canonical orchestration passed and BL-014 sanity checks passed (`21/21`) after hardening updates.
- Lead-genre contract closure recorded (2026-03-25): UI-012 closed after aligning BL-004, BL-005, and BL-006 to one canonical genre-first lead-genre rule, followed by BL-013/BL-014 validation pass.
- Evaluation-freshness closure recorded (2026-03-25): UI-010 closed after BL-010/BL-011 evidence refresh and implementation of executable freshness controls (`check_bl010_bl011_freshness.py` and `run_active_freshness_suite.py`).
- Milestone-state recalibration recorded (2026-03-25): M3 and M4 moved from planned to in progress to reflect completed BL-004 through BL-009 implementation and active evidence-synthesis work.
- UI-003 control-record closure recorded (2026-03-27): Chapter 3 to 5 claim-verdict matrix and chapter-targeted hardening notes are logged and active unresolved governance issues are now empty.
- Phase 5-6 modularization closure recorded (2026-03-29): orchestration, controllability, and alignment runtime helpers were split into focused modules with stable compatibility entrypoints retained and touched files revalidated with pyright.
- BL-003 typed-boundary closure recorded (2026-03-29): Phase 2 alignment migration completed with typed internal data models (`SourceEvent`, `MatchTrace`, `MatchedEvent`, `AggregatedEvent`) wired through weighting, matching, aggregation, and writer boundaries while preserving existing output/interface contracts; targeted alignment tests pass (`88/88`).
- BL-003 stage-shell migration recorded (2026-03-29): `AlignmentStage` introduced with typed run contracts (`AlignmentPaths`, `AlignmentSourceRows`, `AlignmentRunArtifacts`); `main.py` reduced to thin wrapper; alignment suite green (`91/91+`).
- BL-003 summary-context migration recorded (2026-03-29): typed `AlignmentSummaryMetrics` and `AlignmentSummaryContext` introduced; `build_and_write_summary_from_context` entrypoint consolidated with legacy-wrapper compatibility; alignment suite green (`92/92`).
- BL-004 through BL-007 OO-stage migration recorded (2026-03-29): each stage now has explicit typed models/stage class and thin compatibility `main.py` wrappers; BL-004 canonical output redesign adds `bl003_quality`, `source_coverage`, `interaction_attribution`, `numeric_confidence`, and `profile_signal_vector` blocks.
- BL-004 through BL-007 controllable-logic uplift recorded (2026-03-29): run-config/env control schemas expanded, runtime-control resolvers added, hardcoded behavior replaced with control-driven policy, and control-action diagnostic fields added additively across each stage (C-215 through C-217).
- BL-005 retrieval typed-artifacts contract recorded (2026-03-29): `RetrievalArtifacts` dataclass standardized the `RetrievalStage.run()` return contract to match BL-003/BL-004/BL-006/BL-007 (C-218).
- Documentation sync wave recorded (2026-03-29): governance and design docs synchronized to BL-003 through BL-007 source-code behavior; BL-007 wording corrected to partially configurable (C-219).
- 00_admin full synchronization wave recorded (2026-03-29): all admin files synchronized to current canonical baseline (C-220).
- Aggressive root archival wave recorded (2026-03-30): moved `.controllability-transparency.instructions.md`, `.gitattributes`, `requirements.txt`, `pyrightconfig.json`, `main_standalone.py`, and `final_artefact.py` into `_deep_archive_march2026/_packages_reference_2026-03-30/`, expanded `.gitignore` to ignore deep archive, and synchronized admin logs/state (D-044, C-222).
- Pyright/full-contract closure recorded (2026-04-09): the active `07_implementation` runtime path is back to full green after the April typing-remediation wave; pytest passed (`361/361`), pyright returned `0 errors, 0 warnings, 0 informations`, BL-013 passed (`BL013-ENTRYPOINT-20260409-180340-350614`), and BL-014 passed (`BL014-SANITY-20260409-180356-824725`, `28/28`).
- Runtime-root governance sync recorded (2026-04-09): instruction and admin control surfaces now explicitly enforce `07_implementation/` as the only active runtime/workflow surface and classify `_scratch/` as reference-only unless user-requested for historical inspection (D-048, C-229).
- Config-first final artefact wrapper slice recorded (2026-04-09): added the new active `07_implementation/final_artefact/` package with explicit artefact config, generated run-config bridging to the validated `src` pipeline, focused wrapper tests, and a BL-013 fix for seed-refresh payload resolution outside the visible stage order. Validation: focused pytest `15/15`, wrapper validate pass (`BL013-ENTRYPOINT-20260409-184945-119248`, `BL014-SANITY-20260409-184955-724616`), and full contract pass after changes (`366/366`, pyright `0 errors`, BL-013 `BL013-ENTRYPOINT-20260409-185031-056745`, BL-014 `BL014-SANITY-20260409-185043-887580`) (D-049, C-230).

## Notes
- Dates are a working baseline for execution control and can be refined against official module deadlines.
- Scope remains locked to the MVP boundary defined in `00_admin/thesis_state.md`.
- Operational source of truth for open blockers remains `00_admin/unresolved_issues.md`.
- Sprint execution truth remains `00_admin/mentor_draft_7day_sprint_2026-03-23.md`.
