# Thesis State

Last updated: 2026-03-29 UTC (Phase 5-6 modularization and docs sync complete)

## Official Current State

- Current title:
Engineering an Automated, Transparent, and Controllable Playlist Generation Pipeline Using Cross-Source Music Preference Data

- Current research question:
What design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data?

- Current objectives:
1. Design an automated pipeline that generates playlists from user listening histories.
2. Align cross-platform listening data into an inspectable preference signal using robust metadata and identifier handling.
3. Construct a deterministic user preference profile based on imported listening data, user-selectable source scope, and manually selected influence tracks.
4. Generate candidate tracks from the active integrated candidate dataset using feature-based filtering.
5. Score candidate tracks using deterministic similarity functions and rule-based adjustments.
6. Assemble playlists using playlist-level rules that ensure diversity, coherence, and ordering.
7. Provide transparent explanations and observability mechanisms for recommendation decisions.
8. Evaluate the system with respect to transparency, controllability, inspectability, and reproducibility.

- Current artefact definition:
A deterministic single-user playlist generation pipeline with one practical ingestion path, deterministic preference extraction from imported history using metadata/identifier handling, deterministic feature-based scoring on a fixed candidate corpus, configurable playlist assembly rules, transparent score explanations, reproducible run logging, and implemented source-scope control via canonical run-config (`input_scope`) with recorded effective scope in BL-004 and BL-009 outputs.

- Current methodology position:
Design Science Research with an iterative literature -> requirements -> design -> implementation -> evaluation flow. Contribution focus is engineering/design evidence for transparent, controllable, and observable recommendation pipelines, not ML model novelty.

- Current system scope:
Locked MVP scope: single-user, content-based, deterministic playlist pipeline with transparency, controllability, and observability as mandatory qualities. Multi-adapter expansion, deep models, and large-scale user studies are out of scope for the core artefact.

- Current evaluation direction:
Evaluation focuses on BSc-feasible artefact testing aligned to module expectations:
• reproducibility (same input/config => same output)
• transparency/inspectability (score contributions and rule adjustments)
• controllability (parameter sensitivity effects on outcomes)
• observability (run logging, diagnostics, and traceable execution context)
• playlist rule compliance and critical evaluation of limitations

- Current data scope:
The active execution corpus is DS-001 (Music4All base path). DS-002 (`MSD subset + Last.fm tags`) remains a validated fallback reference, including the BL-019 intersection build evidence (9330 tracks, quality gates pass, determinism confirmed — see `07_implementation/experiment_log.md` EXP-016). Real Spotify history is available via BL-002 API export. Spotify Web API audio-feature endpoints remain deprecated, so user-side preference extraction relies on DS-001-aligned metadata and available corpus-side features, with no active Last.fm dependency.

- Current assumptions:
• recommendation modelling focuses on a single user profile
• deterministic algorithms are used instead of machine learning
• active dataset feature coverage is sufficient for candidate-side scoring and controllability tests
• one ingestion path is enough to evaluate core design considerations
• manually added influence tracks can improve preference representation

- Current limitations:
• some imported tracks may not match tracks present in the active candidate dataset
• recommendation quality depends on available feature descriptors
• user-side tempo/key/loudness are not obtainable from Spotify API due to endpoint deprecation
• no collaborative filtering or deep recommender baseline is included
• evaluation is limited to BSc-feasible testing and does not include large-scale user studies

### BL-021 Source-Scope Completion Update (2026-03-24)
- Canonical run-config source-scope contract is implemented and validated.
- BL-003 now applies `input_scope` filtering and emits `bl003_source_scope_manifest.json`.
- BL-004 and BL-009 persist effective source-scope plus run-config provenance.
- A/B probes confirm behavioral controllability with non-zero profile deltas after actuation (`EXP-042`, `TC-BL021-R2-003`).
- BL-013 now supports optional one-command seed refresh (`--refresh-seed`) to align orchestration with scope changes.

## Latest Open Priorities (Execution Snapshot)
All primary in-repo implementation and QC tasks are complete as of 2026-03-28. Only remaining open item is physical submission packaging — see `09_quality_control/chapter_readiness_checks.md` for the single open gate (`[ ] Formatting and submission constraints are met`).

Priority status checkpoint (2026-03-26 18:06 UTC): Historical checkpoint retained for audit continuity. The original v1b active-baseline wording in this checkpoint is superseded by D-033 and later checkpoints that lock v1f as canonical. Metric snapshot remains useful as transitional evidence (`bl003_match_rate=0.1595`, `bl005_kept_candidates=54402`, `bl006_numeric_minus_semantic=-0.068775`, `bl008_top_label_dominance_share=0.3`, BL-014 pass).

Priority status checkpoint (2026-03-26 21:03 UTC): Pipeline is now on the v1f baseline (`run_config_ui013_tuning_v1f.json`), completing the intended 10-component scoring surface by activating danceability, energy, and valence end-to-end in BL-005 and BL-006. BL-013 restore `BL013-ENTRYPOINT-20260326-210305-914179` pass; BL-014 sanity pass `22/22`; BL-010 reproducibility pass; BL-011 controllability pass. The active freshness suite fails at `6/8` due to a non-blocking post-restore evidence-alignment mismatch (documented). Implementation scope is closed on v1f. Planned next actions: (1) freshness re-alignment, (2) UI-003 citation closure — the primary remaining submission-hardening dependency, (3) chapter alignment to v1f counts, (4) evaluation evidence packaging.

Priority status checkpoint (2026-03-26 21:27 UTC): Freshness re-alignment is complete on the active v1f baseline. BL-010 pass (`BL010-REPRO-20260326-212523`), BL-011 pass (`BL011-CTRL-20260326-212611`), BL-013 restore pass (`BL013-ENTRYPOINT-20260326-212711-234744`), BL-014 sanity pass (`BL014-SANITY-20260326-212725-976781`), and active freshness suite pass (`BL-FRESHNESS-SUITE-20260326-212726`, `7/7`). The primary remaining submission-hardening dependency is unchanged: UI-003 citation closure.

Priority status checkpoint (2026-03-26 22:30 UTC): Evidence audit completed for the canonical v1f baseline. All 10 playlist track titles resolved from `ds001_working_candidate_dataset.csv`: (1) Elton John — Candle in the Wind (1973, score 0.7269, pool rank 1), (2) Bruce Hornsby — The Way It Is (1986, score 0.7229, pool rank 2), (3) The Cars — Drive (1984, score 0.4672, pool rank 3,910), (4) Fernando Milagros — Otra Vida (2017, pool rank 3,911), (5) Maria Mena — Sorry (2004, pool rank 3,912), (6) Supertramp — It's Raining Again (1982, pool rank 4,089), (7) Loverboy — Turn Me Loose (1980, pool rank 5,808), (8) Billy Joel — I Go to Extremes (1989, pool rank 5,910), (9) U2 — Book of Your Heart (2017, pool rank 6,638), (10) Bruce Hornsby — The Valley Road (1988, pool rank 6,776). Rank cliff confirmed at position 3 (pool rank 3,910) due to genre-diversity forcing. Bruce Hornsby appears at positions 2 and 10 (no `max_per_artist` rule configured — known limitation). BL-010/BL-011 config-snapshot divergence documented: BL-010 internal replays use 70,680 candidates, BL-011 baseline uses 33,096, canonical v1f uses 46,776 — divergence caused by pinned config snapshots captured before v1f was finalised; `deterministic_match` and `all_variant_shifts_observable` claims remain valid against their respective pinned states. Dissertation claim strengths packaged for Chapter 4/5 use: strongly supported (determinism, explanation transparency, controllability directionality, observability completeness); moderately supported (diversity enforcement, 84% alignment-miss rate as documented limitation); weakly supported (universal applicability, qualitative playlist judgements). Remaining open dependency unchanged: UI-003 citation closure. Logs updated: C-182 / EXP-048.

Priority status checkpoint (2026-03-27 01:22 UTC): Historical checkpoint retained for audit continuity. Later same-day canonical evening wave supersedes these IDs for active reporting; use `07_implementation/ACTIVE_BASELINE.md` as authority.

Priority status checkpoint (2026-03-27 03:05 UTC): UI-003 citation package is closed at control-record level. Chapter 3 to 5 claim-verdict matrix and chapter-targeted hardening notes are now logged in `09_quality_control/ui003_claim_verdicts_ch3_ch5.md` and `09_quality_control/ui003_chapter_hardening_notes_ch3_ch5.md`.

Priority status checkpoint (2026-03-27 16:54 UTC): Additional same-day run wave is now recorded as non-canonical evidence context (not baseline replacement). Latest observed chain: BL-009 `BL009-OBSERVE-20260327-165412-004409` with upstream BL-004 `BL004-PROFILE-20260327-165357-389471`, BL-005 `BL005-FILTER-20260327-165358-293711`, BL-006 `BL006-SCORE-20260327-165402-861535`, BL-007 `BL007-ASSEMBLE-20260327-165409-663614`, BL-008 `BL008-EXPLAIN-20260327-165410-986323`; BL-005 kept candidates `70680`; BL-008 top-contributor distribution `{Lead genre match:4, Tag overlap:3, Danceability:2, Tempo (BPM):1}`. Canonical reporting baseline remains v1f.

Priority status checkpoint (2026-03-27 18:49 UTC): BL-023 website integration hardening now includes a FastAPI-based local server, typed POST validation, localhost-only CORS, preserved `{"error": ...}` API compatibility, and automated regression coverage (`07_implementation/setup/test_website_api_server.py`) in addition to the live smoke script. External behavior remains stable on the 7-stage pipeline surface; canonical reporting baseline remains v1f.

Priority status checkpoint (2026-03-28 03:41 UTC): Admin-first synchronization pass completed before chapter implementation edits. `07_implementation/ACTIVE_BASELINE.md` is confirmed as canonical evidence authority with no run-ID changes in this checkpoint; `00_admin/Artefact_MVP_definition.md`, `09_quality_control/chapter_readiness_checks.md`, and `00_admin/timeline.md` were synchronized to this baseline posture. Next execution step remains chapter hardening with strict run-linked references.

Priority status checkpoint (2026-03-28 03:46 UTC): Chapter hardening execution is now in progress with first-pass implementation applied. `08_writing/chapter3.md` alignment-limitation metrics were synchronized to canonical baseline wording (`match_rate=0.1595`, threshold posture aligned to v1f controls), and `08_writing/chapter4.md` Sections 4.8 to 4.10 were populated with run-linked reproducibility/controllability/rule-compliance/explanation-fidelity results. Chapter 4 readiness gate for rule-compliance/failure-case write-through is now closed in `09_quality_control/chapter_readiness_checks.md`.

Priority status checkpoint (2026-03-28 04:18 UTC): Handoff synchronization pass completed before branch push. Repository content swap requested by user is now in place (`07_implementation` carries the implementation package runtime surface; `final_artefact` holds prior baseline-content snapshot), stale nested verification output folders and stale pytest cache were removed, and admin control files were updated to log this transition state explicitly.

Priority status checkpoint (2026-03-28 05:11 UTC): Active-root alignment closure completed. Repository config now treats `07_implementation/src` as the canonical implementation source for type-checking and tests; `final_artefact-old` is explicitly marked legacy/reference-only to reduce accidental operator drift.

Priority status checkpoint (2026-03-28 closing pass): All in-repo QC and implementation tasks are complete. Code hygiene refactor closed (C-197): `safe_int` centralized in `shared_utils/parsing.py`, duplicate helpers removed from 3 modules, 181/181 tests pass, pyright clean on all edited files. Canonical run IDs synchronized across backlog, manifest, thesis_state, and chapter evidence tables (C-198). UI-003 verdict matrix fully closed: `supported=18`, `mismatch=0`, `weak_support=0` in `09_quality_control/ui003_claim_verdicts_ch3_ch5.md`. Chapter 2 verbatim audit gate closed: Ru et al. wording hardened to task-specific multi-label genre classification scope; rerun confirmed `total_claim_checks=40`, `weak_support=0` in `09_quality_control/chapter2_verbatim_audit.md` (C-199). All chapter readiness gates marked complete in `09_quality_control/chapter_readiness_checks.md`. Only remaining action is external submission packaging (Canvas deadline, cover/declaration template, Turnitin package assembly).

Priority status checkpoint (2026-03-29 00:05 UTC): Ingestion runtime-policy alignment and implementation cleanup completed. BL-002 policy now explicitly treats token-cache persistence and endpoint caching as disabled runtime behavior for live exports, with OAuth-per-run and item-first track-only playlist-item flattening captured in governance (`D-040`, `C-201`). `07_implementation` cleanup pass removed generated artifacts and duplicate profile-tree drift, retained canonical profile location, and stabilized stage subprocess imports via `PYTHONPATH` propagation in `07_implementation/main.py` (`C-202`).

Priority status checkpoint (2026-03-29 06:00 UTC): Phase 1-4 controllability & transparency governance layer complete. Implemented 14-file persistent governance framework establishing controllability and transparency as first-class thesis-core design priorities: Phase 1 signal files (4), Phase 2 design & governance (5 + D-041/D-042/D-043 decisions), Phase 3 operational procedures (4 + Section 17 update), Phase 4 verification (comprehensive consistency/discoverability checks). Key deliverables: `.controllability-transparency.instructions.md` (workspace root), `GOVERNANCE.md` (3-question gate for feature development), `CONTROL_SURFACE_REGISTRY.md` (3 working + 2 weak controls documented), `TRANSPARENCY_SPEC.md` (5 gaps identified), `CONTROL_TESTING_PROTOCOL.md` (4 measurement methods), `TRANSPARENCY_AUDIT_CHECKLIST.md` (A1-A4 design, B1-B5 validation), `SIGNAL_FILES_MAINTENANCE.md` (weekly/quarterly procedures), `PHASE_4_VERIFICATION_COMPLETE.md` (full verification passed). All files cross-referenced consistently (C1 check ✓), no contradictions (C2-C3 ✓), known gaps documented and gated (C4 ✓). Git commit 0a0c3c0, change log entry C-203. Every agent now sees thesis priority immediately on workspace entry. Control testing and transparency auditing are systematic. Governance gate prevents weak features. Next: Phase 3+ code implementation using documented procedures (D-042: influence track redesign, D-043: control traceability).

Priority status checkpoint (2026-03-29 modularization pass): Phase 5 and Phase 6 implementation cleanup is complete. BL-013 orchestration control resolution now consistently honors CLI > run-config > defaults and `orchestration/main.py` is reduced to a thin entrypoint over focused CLI, stage-runner, seed-freshness, and summary helpers. BL-011 controllability is split into dedicated profile, retrieval, scoring, playlist, pathing, and runtime-control modules, and BL-003 matching/reporting is split into focused text, indexing, matching, writing, validation, and summary helpers while preserving compatibility wrappers at the legacy import surfaces. Touched files were revalidated with pyright (`0 errors`). Remaining work remains external submission packaging rather than in-repo implementation changes.

## Current Implementation Status

### BL-020 Implementation State (as of 2026-03-26)
- **Ingestion**: Schema locked (BL-001 ✅), parser + Web API exporter implemented (BL-002 ✅), real Spotify API export completed (5,592 unique tracks from top + saved history)
- **Candidate Dataset**: DS-001 is the active execution corpus. DS-002 remains built and verified (BL-019 ✅, 9,330 tracks) as a validated fallback reference.
- **Alignment** (BL-003 ✅): Active alignment now uses direct DS-001 metadata/identifier mapping for imported Spotify records. Historical Last.fm enrichment artifacts from earlier BL-020 runs are retained as legacy evidence only and are not part of the active path.
- **Preference Profiling** (BL-004 ✅): Active profile generation uses DS-001-aligned seeds with deterministic trace outputs (`bl004_preference_profile.json`, `bl004_profile_summary.json`, `bl004_seed_trace.csv`).
- **Candidate Filtering** (BL-005 ✅): Deterministic filtering executed against the active DS-001 corpus on v1f config; 46,776 candidates retained from 109,269 total (seeds excluded). DS-002 filtering results remain archived as fallback-reference evidence.
- **Candidate Scoring** (BL-006 ✅): Deterministic 10-component hybrid scoring active on v1f: numeric (tempo, duration_ms, key, mode, danceability, energy, valence) + semantic (lead_genre, genre_overlap, tag_overlap). All components active with no rebalance fallback on v1f run.
- **Playlist Assembly** (BL-007 ✅): Rule-based playlist assembly completed on canonical v1f run (`BL007-ASSEMBLE-20260326-215757-053177`). Final 10-track playlist resolved: (1) Elton John — Candle in the Wind, (2) Bruce Hornsby — The Way It Is, (3) The Cars — Drive, (4) Fernando Milagros — Otra Vida, (5) Maria Mena — Sorry, (6) Supertramp — It's Raining Again, (7) Loverboy — Turn Me Loose, (8) Billy Joel — I Go to Extremes, (9) U2 — Book of Your Heart, (10) Bruce Hornsby — The Valley Road. Score range: 0.4476–0.7269. Rank cliff at position 3 (pool rank 3,910). Evidence in EXP-048.
- **Transparency Explanations** (BL-008 ✅): Transparency explanation payload generation remains active with mechanism-linked score breakdowns and rule-effect traces for playlist outputs.
- **Observability** (BL-009 ✅): Canonical run-level observability completed on 2026-03-22. Output: `bl009_run_observability_log.json` and `bl009_run_index.csv` with stage traceability, configuration snapshots, diagnostics, and artifact hashes. Evidence in EXP-030/TC-BL020-009.
- **Pipeline Completion**: BL-020 is fully complete (BL-003 through BL-009 executed, logged, and test-documented).
- **Quality Automation** (BL-014 ✅): Automated sanity checks are green on v1f baseline. Active canonical sanity/freshness runs are `BL014-SANITY-20260327-201731-408637` (22/22) and `BL-FRESHNESS-SUITE-20260327-201942` (19/19). Earlier 2026-03-26 IDs are retained as historical checkpoints only.
- **Reproducibility** (BL-010 ✅): Active canonical pass is `BL010-REPRO-20260327-201949` (`deterministic_match=true`, 3 replays). Note: BL-010 internal config snapshot uses 70,680 candidates (pinned before v1f finalisation); reproducibility property holds on that pinned state.
- **Controllability** (BL-011 ✅): Active canonical pass is `BL011-CTRL-20260327-202057` (`all_variant_shifts_observable=true`, 5 scenarios). Note: BL-011 internal config snapshot uses 33,096 candidates (pinned before v1f finalisation); controllability property holds on that pinned state.
- **Post-Migration Stabilization** (2026-03-26 ✅): BL-ordered folder migration is runtime-stable. Active canonical v1f orchestration reference is `BL013-ENTRYPOINT-20260327-201712-508978`.
- **Tier-1 Hardening Closure** (2026-03-25 ✅): CRI-004, CRI-002, HIGH-003, HIGH-004, and CRI-003 are implemented, validated, and logged in `00_admin/tier1_hardening_execution_log_2026-03-25.md`.
- **Current Execution Focus** (2026-03-27 03:05 UTC): v1f baseline fully operational. Primary remaining work: chapter table completion and wording hardening at the known weak/mismatch locations documented in the UI-003 closure package.
- **Current Execution Focus** (2026-03-27 16:54 UTC): v1f baseline remains the canonical reporting baseline; active work continues on BL-023 bounded website integration hardening and chapter evidence-packaging follow-through.
- **Current Execution Focus** (2026-03-27 18:49 UTC): server-layer hardening for BL-023 is now in place and regression-backed; remaining website work is bounded to modular cleanup, observability/result-surface polish, and reliability fixes only.
- **Current Execution Focus** (2026-03-28 UTC): final_artefact clean-code pass complete (C-192). Dead `sha256_direct` removed, `sha256_of_values` canonical in `shared_utils/hashing.py`, BL-009 observability resolver migrated to `resolve_stage_controls` factory, parity tests added. 171/171 tests pass. G2 deferred per D-039. No outstanding code-quality blockers for submission.
- **Current Execution Focus** (2026-03-28 closing pass): All in-repo QC gates closed (C-197/C-198/C-199). Code hygiene refactor applied and validated: `safe_int` centralized, duplicate helpers removed from 3 modules, 181/181 tests pass, pyright clean. UI-003 verdict matrix `mismatch=0`, `weak_support=0`. Chapter 2 verbatim audit `weak_support=0` (`total_claim_checks=40`). All chapter readiness gates complete. No open implementation or QC blockers for submission.
- **Active Risk (Governance)**: No active unresolved governance blocker; residual risk is execution discipline for chapter hardening completion.
- **Implementation Quality Status**: Pipeline closed on the active v1f baseline (`run_config_ui013_tuning_v1f.json`). BL-014 passes 22/22. All 10 scoring components active. BL-010 determinism and BL-011 controllability confirmed on their respective pinned states. No open implementation closure risks.
- **Implementation Modularity Status** (2026-03-29): Orchestration, controllability, and alignment runtime surfaces are now split into focused helper modules with thin compatibility entrypoints/wrappers retained at `main.py`, `pipeline_runner.py`, `scenarios.py`, `matching.py`, and `reporting.py`. Current risk is low and limited to normal maintenance drift rather than monolithic-script fragility.

### BL-021 Source-Scope Control State (as of 2026-03-26)
- Source-scope contract is baseline behavior (no longer deferred): implemented, validated, and traceable in run artifacts.
- BL-003 applies `input_scope` filtering and emits `bl003_source_scope_manifest.json`.
- BL-004 and BL-009 persist effective source-scope plus run-config provenance.
- BL-013 supports optional one-command seed refresh (`--refresh-seed`) for scope-sensitive reruns.

### Artefact Refinement Cycle State (as of 2026-03-26) — ALL COMPLETE
- R1 ✅: Every BL-013 run emits `run_intent_<timestamp>.json` (schema `run-intent-v1`) and `run_effective_config_<timestamp>.json` (schema `run-effective-config-v1`) as a deterministic pair before any stage executes. Both are linked from BL-009 with SHA256 verification. Validated in BL013-ENTRYPOINT-20260325-001946-187550.
- R2 ✅: Semantic control-layer map produced at `07_implementation/implementation_notes/bl000_run_config/semantic_control_map.md`. Seven semantic groups (Input Composition, Profile Construction, Retrieval Filtering, Scoring, Playlist Assembly, Transparency, Observability) map every run-config field to consuming stage, resolver function, and output artifacts.
- R3 ✅: BL-009 observability log promoted to versioned schema (`BL009_OBSERVABILITY_SCHEMA_VERSION = "bl009-observability-v1"`). `execution_scope_summary` top-level block added with source family, interaction types, seed count, influence participation flag, and canonical artifact pair availability. Validated in BL013-ENTRYPOINT-20260325-001552-538292.

### Detailed Audit
See: `07_implementation/BL020_HANDOFF_AUDIT_2026-03-21.md` for comprehensive pre-implementation checklist and artifact inventory.

## Update Control

- Last updated:
2026-03-29 (Phase 5-6 modularization + docs sync pass)

- Reason for last update:
(1) Phase 5 BL-013 orchestration cleanup completed: control resolution was externalized and `orchestration/main.py` reduced to a thin entrypoint over focused helper modules while preserving behavior.
(2) Phase 6 modularization completed across BL-011 and BL-003 support code: controllability scenario execution is split into dedicated stage/path/runtime-control modules and alignment matching/reporting is split into focused helper modules with compatibility wrappers retained.
(3) Admin/runtime docs were synchronized to the modularized layout and touched files were revalidated with pyright; canonical baseline and chapter/QC closure posture remain unchanged, so the only remaining task is external submission packaging.

## Locked Definitions
- Artefact scope lock: `00_admin/Artefact_MVP_definition.md`
- Evaluation plan: `00_admin/evaluation_plan.md`
- Methodology definition: `00_admin/methodology_definition.md`
