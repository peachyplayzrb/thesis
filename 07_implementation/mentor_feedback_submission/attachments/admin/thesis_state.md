# Thesis State

Last updated: 2026-04-20 UTC (C-584 / D-289. Chapter 3 candidate-shaping rationale now replaces the unsupported `Steck et al., 2021` inline citation with the curated explanation-evaluation authority `Tintarev and Masthoff, 2012`, yielding bibliography-supported citation form `Tintarev and Masthoff, 2007, 2012` without changing design substance, locked scope, or implementation/runtime behavior. Chapter 1 scope wording remains refreshed with explicit Music4All citation authority (`Pegoraro Santana et al., 2020`). Governance ID-integrity normalization remains complete across both ledgers (`C-580`, `C-581`, `D-289`). Quality posture remains green from the prior cleanup tranche: Ruff pass, duplicate advisory clean, dependency advisory clean with one explicit ignore, and full tests 638/638 with one expected warning. Next: external submission/package confirmations.)

> Full historical audit trail (priority checkpoints, post-closure enhancement logs) is in `00_admin/thesis_state_ARCHIVE_20260416.md` and `00_admin/change_log.md`.

---

## Current Posture

**Rebuild phase:** All four rebuild milestones (REB-M1 through REB-M4) are complete as of 2026-04-12.

**Chapter status:**

| Chapter | Status | Change anchor |
|---------|--------|---------------|
| Chapter 1 — Introduction | **Final** (user-edited and locked; citation wording refreshed) | C-583, 2026-04-20 |
| Chapter 2 — Literature Review | **Final** (mentor-hardened, citations verified, formatting locked) | C-403, 2026-04-16 |
| Chapter 3 — Design | Canonical active draft now includes explicit option-space and selected-design rationale coverage in `08_writing/chapter3.md`; `chapter3_v3.md` retained as comparison history | D-132, D-133, D-134, D-136, D-137, D-138, D-139, D-140, D-143, D-149; C-418, C-419, C-437 |
| Chapter 4 — Implementation | Rebuild-era draft with explicit Chapter 3 continuity hardening (`08_writing/chapter4.md`) | D-064, D-125, D-141 |
| Chapter 5 — Evaluation | Rebuild-era draft with explicit continuity to Chapter 3 option-space selection rationale (`08_writing/chapter5.md`) | D-125, D-150; C-390, C-438 |
| Chapter 6 — Discussion | Rebuild-era draft with explicit continuity to Chapter 3 option-space selection rationale (`08_writing/chapter6.md`) | D-125, D-150; C-390, C-438 |

**Implementation status:** All pipeline stages (BL-003 to    BL-009) are green. Latest validated tranche state for the active follow-up wave: full contract rerun completed on 2026-04-18 with `620/620` tests, `pyright 0`, BL-013 `BL013-ENTRYPOINT-20260418-035540-208118`, and BL-014 `BL014-SANITY-20260418-035641-651065` (`36/36`). Follow-on operability hardening added BL-013 deterministic verification mode, fixed optional-stage status accounting, aligned BL-010 replay validation to current artifact names, restored BL-004 to BL-005 confidence continuity by preserving `match_confidence_score` in `bl004_seed_trace.csv`, removed duplicate BL-003 execution during refresh-seed orchestration, and adds explicit requested-versus-executed stage-flow metadata in BL-013 summary artifacts via `stage_execution`. Latest deterministic verification repeatability pair is BL-013 `BL013-ENTRYPOINT-20260418-040101-368238` and BL-013 `BL013-ENTRYPOINT-20260418-040456-884132`, with BL-010 runs `BL010-REPRO-20260418-040141` and `BL010-REPRO-20260418-040530` (`deterministic_match=True` both runs, stage_execution coherent in both summaries). Duplicate-code governance now has dedicated automation via `07_implementation/scripts/duplicate_src.ps1` and task surfaces `07: Duplicate Check src (Advisory|Strict)`, and duplicate-reduction refactoring has progressed through shared validation-policy helpers, shared REB gate helpers across all three tranche gates, a centralized BL-005 filtered-field handshake contract, shared BL-005/BL-006 runtime-control bookkeeping helpers, shared BL-009/BL-010 control-context helpers, canonical BL-007 playlist config serialization via `playlist.models`, centralized BL-013 completion emission via `orchestration.summary_builder`, and shared BL-011 snapshot-construction plus constants authority reuse in quality/run-config surfaces; advisory duplicate findings are now reduced to 0 (C-501 / D-210). Post-dedup static typing hardening then updated the shared BL-011 helper interface to `Mapping`/`Path`-typed parameters, restoring Pyright zero-regression status after C-501 (C-502 / D-211). Complexity-reduction updates are active: BL-011 retrieval/scoring stage executors were helper-extracted to reduce hotspot complexity from E-grade to D-grade (C-503 / D-212), BL-013 orchestration entrypoint flow was helper-extracted in-module to remove the prior elevated `main` hotspot while preserving behavior/contracts (C-504 / D-213), BL-007 `assemble_bucketed` was refactored via candidate-level helper extraction to reduce complexity from `E (33)` to `D (24)` (C-505 / D-214), BL-007 run-config resolution was helper-extracted in `resolve_bl007_controls` so the prior hotspot is decomposed into helper-level `C` functions (C-506 / D-215), BL-014 explanation-fidelity checks were decomposed into payload-level helper logic (C-507 / D-216), retrieval context parsing in `retrieval.models.context_from_mapping` was decomposed into focused coercion helpers (C-508 / D-217), scoring context parsing in `scoring.models.context_from_mapping` was decomposed into focused mapping/coercion helpers (C-509 / D-218), scoring controls parsing in `scoring.models.controls_from_mapping` was decomposed via shared coercion helpers with reduced hygiene complexity (`D (25)` to `C (15)`) (C-510 / D-219), scoring component-score assembly in `scoring_engine.compute_component_scores` was decomposed into focused helpers with the prior hotspot removed from hygiene listings (C-511 / D-220), shared fuzzy candidate selection in `shared_utils.text_matching.fuzzy_find_candidate` was decomposed into focused helper flow with hygiene reduction from `D (28)` to `C (15)` (C-512 / D-221), BL-014 active-suite orchestration in `quality.suite.run_active_mode` was decomposed into focused helper flow with hygiene reduction from `D (25)` to `C (14)` (C-513 / D-222), run-config schema coercion in `run_config.schema.coerce_field` was decomposed into focused per-type coercion helpers with the prior hotspot removed from hygiene listings (C-514 / D-223), run-config effective resolution in `run_config.run_config_utils.resolve_effective_run_config` was decomposed into focused section-level resolvers with the prior hotspot removed from hygiene C-or-higher listings (C-515 / D-224), BL-005 runtime-context assembly in `retrieval.stage.RetrievalStage.build_runtime_context` was decomposed into focused helpers for semantic profile, numeric confidence, signal metrics, threshold adjustment, and recency/language derivation with the prior hotspot removed from hygiene C-or-higher listings (C-516 / D-225), BL-004 to BL-005 handshake validation in `retrieval.input_validation.validate_bl004_bl005_handshake` was decomposed into focused helpers for profile-key checks, seed-trace schema inspection, numeric-threshold compatibility inspection, and violation assembly with the prior hotspot removed from hygiene C-or-higher listings (C-517 / D-226), BL-005 candidate evaluation in `retrieval.candidate_evaluator.evaluate_bl005_candidates` was decomposed into focused helpers for runtime-context resolution, semantic extraction/scoring, language-recency gating, numeric-support scoring, and decision-row assembly with the prior hotspot removed from hygiene C-or-higher listings while validation remains green (C-518 / D-227), BL-009 observability context preparation in `observability.main._prepare_observability_context` was decomposed into focused helpers for input loading, contract validation, BL-003 context extraction, handshake preparation, version/hash assembly, and retrieval/assembly sampling with the prior hotspot removed from hygiene listings while validation remains green (C-519 / D-228), BL-013 seed freshness validation in `orchestration.seed_freshness` was decomposed into focused helpers for control-shape normalization, observed-source validation, and contract payload checks with prior D-grade hotspots removed and `_build_behavior_controls` now reporting `C (12)` while validation remains green (C-520 / D-229), BL-011 controllability profile staging in `controllability.stage_profile.execute_profile_stage` was decomposed into focused helpers for selection/validation, accumulation, row construction, and payload/hash assembly with the prior hotspot removed from D-grade hygiene listings while validation remains green (C-521 / D-230), BL-011 controllability scoring staging in `controllability.stage_scoring.execute_scoring_stage` was decomposed into focused helpers for numeric similarity computation, semantic overlap contribution assembly, row payload construction, summary projection, and scored-field projection with the prior hotspot removed from D-grade hygiene listings while validation remains green (C-522 / D-231), BL-011 controllability retrieval staging in `controllability.stage_retrieval.execute_retrieval_stage` was decomposed into focused helpers for semantic-input extraction, semantic-match evaluation, rule-hit/count bookkeeping, decision-row assembly, and diagnostics assembly with the prior hotspot removed from D-grade hygiene listings while validation remains green (C-523 / D-232), BL-011 controllability orchestration in `controllability.main.main` was decomposed into focused helpers for run-input preparation, scenario execution, baseline-comparison attachment, matrix/report assembly, and no-op control diagnostics extraction with controllability-main removed from D-grade hygiene listings while validation remains green (C-524 / D-233), ingestion track-field mapping in `ingestion.spotify_mapping.extract_track_fields` was decomposed into focused helpers for dict coercion, artist projection, and duration projection with the prior D-grade hotspot removed while validation remains green (C-525 / D-234), and ingestion export retrieval in `ingestion.export_spotify_max_dataset._fetch_all_data` was decomposed into focused helpers for top-track retrieval, playlist dedup/retrieval, playlist-item batch retrieval, and recently-played retrieval with the prior D-grade hotspot removed while validation remains green (C-526 / D-235), and BL-007 tradeoff-metrics assembly in `playlist.reporting.build_tradeoff_metrics_summary` was decomposed into focused helpers for genre extraction/analysis, entropy metrics computation, transition metrics extraction, ranking metrics extraction, top-100 exclusion statistics computation, and three summary-dict builders with the prior D-grade hotspot (D 28) removed while validation remains green (C-527 / D-236), and BL-014 explanation-fidelity validation in `quality.sanity_checks._bl008_explanation_payload_warnings` was decomposed into focused helpers for score breakdown extraction, contribution share bounds checking, negative margin detection, primary/causal driver consistency checking, score-band phrase validation, and assembly context key validation with the prior D-grade hotspot (D 30, highest-ranked D-grade) removed while validation remains green (C-528 / D-237), and BL-014 `quality.sanity_checks.main` F(67) was decomposed into 8 focused helpers (`_load_sanity_data`, `_build_artifact_paths`, `_run_schema_and_handshake_checks`, `_resolve_gates_and_advisories`, `_run_hash_integrity_checks`, `_run_continuity_and_count_checks`, `_gate_status`, `_build_matrix_row`) plus `bl008_explanation_fidelity_warnings` E(32) and `bl008_bl009_handshake_contract_ok` D(21) cleared via `_bl008_bl09_check_logic` extraction; BL-007 `playlist.rules.assemble_bucketed` D(24) was cleared by extracting the inner candidate iteration loop into `_run_candidate_loop` with `relaxation_active` pre-computation; hygiene report now shows zero D/E/F-grade entries across all `src/` modules — the complexity-reduction campaign (C-523 through C-529) is complete (C-529 / D-238). UNDO-O added `build_interpretation_boundaries()` to BL-010 (`reproducibility/main.py`), emitting a `reproducibility-interpretation-v1` structured block (`verdict_basis`, `consistency_domain`, `non_claims`) as `interpretation_boundaries` in the BL-010 report; added `build_reproducibility_interpretation()` to BL-009 (`observability/main.py`), emitting a parallel structured block as `reproducibility_interpretation` inside `validity_boundaries`; hardened chapter 5 and chapter 6 reproducibility limit statements to explicitly name artifact-level framing and environmental invariance non-claims; then refreshed Chapter 4/5 and quality-control references to current 2026-04-18 validation authorities and stage-flow traceability evidence (C-469, C-470, C-487 / D-181, D-196). UNDO-B, UNDO-C, and UNDO-D remain closed. The Chapter 3 weak-spot follow-up set (`UNDO-J` through `UNDO-O`) is now fully implementation-hardened and chapter-facing evidence references are synchronized to the current validated baseline.

**Next work:** UNDO-J through UNDO-O implementation hardening, chapter-readiness/full-contract sync, and professionalism companion expansion are complete. Next: reduce measured Chapter 1 to 6 word-count risk in compiled package form, then complete template/format-specific packaging (institutional cover/declaration and any required template/visual conversions), and close external Canvas/Turnitin/viva confirmations.

---

## Locked Definitions

These definitions are locked under rebuild posture and must not be changed without a `D-###` decision entry.

### Title
Designing and Evaluating a Transparent and Controllable Playlist Generation Pipeline Using Cross-Source Music Preference Data

### Research Question
How can a deterministic playlist generation pipeline be designed and evaluated so that it remains transparent, controllable, and reproducible when user preference data and candidate tracks come from different sources?

### Objectives
1. Design a preference profiling approach from user listening history across different data sources.
2. Implement cross-source alignment and candidate filtering with explicit uncertainty handling.
3. Implement deterministic scoring and playlist assembly with controls for coherence, diversity, novelty, and ordering.
4. Produce explanation and logging outputs that show how pipeline decisions were made.
5. Evaluate how well the pipeline reproduces results and how playlist quality changes when settings are adjusted.
6. Identify the limits of the results and the conditions under which the conclusions apply.

### Artefact Definition
A deterministic, single-user playlist generation artefact rebuilt under explicit objective-to-control-to-evidence contracts, where cross-source uncertainty signaling, confidence-aware alignment/candidate shaping, controllable scoring/assembly trade-offs, mechanism-linked explanations, and run-level reproducibility/controllability evidence are mandatory outputs rather than optional diagnostics.

### Methodology
Design Science Research with a literature-grounded reconstruction flow from confirmed Chapter 2 gaps to RQ and objectives, then to design, implementation, and evaluation. Contribution focus is engineering evidence quality and traceability, not model-family novelty.

### Scope
Single-user deterministic scope. The thesis contribution is bounded to auditable engineering behavior under cross-source uncertainty. Collaborative filtering, deep model novelty, and large-scale user studies are out of scope.

---

## Rebuild Milestones

All milestones completed 2026-04-12 unless noted.

| Milestone | Outcome | Decision anchor |
|-----------|---------|-----------------|
| REB-M1 — Re-derive RQ and objectives | RQ and objectives derived from Chapter 2 tensions and locked | D-053, D-054 |
| REB-M2 — Lock Chapter 3 design authority | Chapter 3 design blueprint and O1–O6 evidence-contract map established | D-055 |
| REB-M3 — Rebuild implementation | Tranche gates (T1–T3) passing; 30+ post-closure hardening slices complete; full validation green | D-056 to D-105 |
| REB-M4 — Rebuild Chapter 4/5 | Chapter 4 and 5 rebuilt on O1–O6 contracts; citation-density hardening and chapter 4/5/6 split complete | D-064, D-125 |

**Key REB-M3 artefacts:**
- Tranche gates: `07_implementation/src/quality/reb_m3_tranche{1,2,3}_gate.py`
- Design blueprint: `05_design/chapter3_information_sheet.md`
- Evidence-contract map: `05_design/requirements_to_design_map.md`

---

## Implementation Status (summary)

| Area | Status | Notes |
|------|--------|-------|
| BL-003 alignment | Green | DS-001 active corpus; `user_csv` 5th advisory source; configurable fuzzy fallback |
| BL-004 profiling | Green | Policy-gated fallback controls; row-quality handshake; BL-003 handshake enforcement |
| BL-005 retrieval | Green | Policy-gated BL-004 handshake; runtime-control diagnostics parity |
| BL-006 scoring | Green | 10-component hybrid scoring (v1f); policy-gated BL-005 handshake |
| BL-007 assembly | Green | Influence-policy modes; utility-decay; opportunity-cost controls; BL-006 handshake |
| BL-008 explanation | Green | Explanation-fidelity fields; provenance de-dup; assembly-context enrichment; BL-007 handshake |
| BL-009 observability | Green | BL-008 handshake; `validity_boundaries` top-level contract |
| BL-010 reproducibility | Green | `deterministic_match=true`, 3 replays (v1f pinned snapshot) |
| BL-011 controllability | Green | `all_variant_shifts_observable=true`, 5 scenarios (v1f pinned snapshot) |
| BL-013 orchestration | Green | Config-first wrapper; seed-refresh support |
| BL-014 sanity checks | Green | 36/36 checks; full inter-stage handshake continuity |
| Mentor bundle | Validated | `BL014-SANITY-20260414-121945-312010`, 36/36 |

Active dataset: DS-001 (Music4All). Active config profile: `run_config_ui013_tuning_v1f.json`.

---

## Governance Quickref

| Item | Current value |
|------|--------------|
| Highest change ID | C-584 |
| Highest decision ID | D-289 |
| Active unresolved issues | Active mentor-feedback remediation backlog now tracked as `UNDO-R` in `00_admin/unresolved_issues.md` (A-H implementation checklist complete). Submission blockers remain tracked in `09_quality_control/submission_readiness_status.md` and `01_requirements/ambiguity_flags.md` |
| Admin log files | `change_log.md`, `decision_log.md`, `unresolved_issues.md`, `timeline.md` |
| Foundation files | `02_foundation/current_title_and_rq.md`, `objectives.md`, `contribution_statement.md`, `problem_statement.md` |
| Historical state (pre-cleanup) | `00_admin/thesis_state_ARCHIVE_20260416.md` |

---

## Pre-Rebuild Legacy Note

A full architecture rebuild was initiated on 2026-04-12 (D-052). All pre-rebuild title, RQ, objectives, and methodology wording is superseded by the locked definitions above. The pre-rebuild state is preserved in `00_admin/thesis_state_ARCHIVE_20260416.md` for audit continuity.
