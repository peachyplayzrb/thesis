# Thesis State

Last updated: 2026-03-25 22:57 UTC (tuning sweep complete; v1b profile selected)

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
1. Close `UI-003` thesis-wide citation package: complete claim-citation hardening synthesis for Chapters 2 to 5 and finalize chapter-targeted improvement notes.
2. Continue mentor sprint execution at Day 4 to Day 7 from `00_admin/mentor_draft_7day_sprint_2026-03-23.md`.
3. Keep website integration under bounded hardening only (`WP-WEBINT-001`): bug fixes, observability clarity, and orchestration reliability without scope expansion.
4. Keep M3/M4 execution status synchronized with implementation reality and package evidence for M5 evaluation consolidation.

Priority status checkpoint (2026-03-26 18:06 UTC): Tier-1 pipeline remediation remains complete. UI-013 is now closed on the active baseline: the v1b profile remains the active configuration per decision D-032, refreshed acceptance evidence passed on corrected BL-006 weighted semantics (`bl003_match_rate=0.1595`, `bl005_kept_candidates=54402`, `bl006_numeric_minus_semantic=-0.068775`, `bl008_top_label_dominance_share=0.3`, BL-014 pass), and the primary remaining submission-hardening dependency is UI-003 citation closure.

Priority status checkpoint (2026-03-26 21:03 UTC): Pipeline is now on the v1f baseline (`run_config_ui013_tuning_v1f.json`), completing the intended 10-component scoring surface by activating danceability, energy, and valence end-to-end in BL-005 and BL-006. BL-013 restore `BL013-ENTRYPOINT-20260326-210305-914179` pass; BL-014 sanity pass `22/22`; BL-010 reproducibility pass; BL-011 controllability pass. The active freshness suite fails at `6/8` due to a non-blocking post-restore evidence-alignment mismatch (documented). Implementation scope is closed on v1f. Planned next actions: (1) freshness re-alignment, (2) UI-003 citation closure — the primary remaining submission-hardening dependency, (3) chapter alignment to v1f counts, (4) evaluation evidence packaging.

Priority status checkpoint (2026-03-26 21:27 UTC): Freshness re-alignment is complete on the active v1f baseline. BL-010 pass (`BL010-REPRO-20260326-212523`), BL-011 pass (`BL011-CTRL-20260326-212611`), BL-013 restore pass (`BL013-ENTRYPOINT-20260326-212711-234744`), BL-014 sanity pass (`BL014-SANITY-20260326-212725-976781`), and active freshness suite pass (`BL-FRESHNESS-SUITE-20260326-212726`, `7/7`). The primary remaining submission-hardening dependency is unchanged: UI-003 citation closure.

Priority status checkpoint (2026-03-26 22:30 UTC): Evidence audit completed for the canonical v1f baseline. All 10 playlist track titles resolved from `ds001_working_candidate_dataset.csv`: (1) Elton John — Candle in the Wind (1973, score 0.7269, pool rank 1), (2) Bruce Hornsby — The Way It Is (1986, score 0.7229, pool rank 2), (3) The Cars — Drive (1984, score 0.4672, pool rank 3,910), (4) Fernando Milagros — Otra Vida (2017, pool rank 3,911), (5) Maria Mena — Sorry (2004, pool rank 3,912), (6) Supertramp — It's Raining Again (1982, pool rank 4,089), (7) Loverboy — Turn Me Loose (1980, pool rank 5,808), (8) Billy Joel — I Go to Extremes (1989, pool rank 5,910), (9) U2 — Book of Your Heart (2017, pool rank 6,638), (10) Bruce Hornsby — The Valley Road (1988, pool rank 6,776). Rank cliff confirmed at position 3 (pool rank 3,910) due to genre-diversity forcing. Bruce Hornsby appears at positions 2 and 10 (no `max_per_artist` rule configured — known limitation). BL-010/BL-011 config-snapshot divergence documented: BL-010 internal replays use 70,680 candidates, BL-011 baseline uses 33,096, canonical v1f uses 46,776 — divergence caused by pinned config snapshots captured before v1f was finalised; `deterministic_match` and `all_variant_shifts_observable` claims remain valid against their respective pinned states. Dissertation claim strengths packaged for Chapter 4/5 use: strongly supported (determinism, explanation transparency, controllability directionality, observability completeness); moderately supported (diversity enforcement, 84% alignment-miss rate as documented limitation); weakly supported (universal applicability, qualitative playlist judgements). Remaining open dependency unchanged: UI-003 citation closure. Logs updated: C-182 / EXP-048.

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
- **Quality Automation** (BL-014 ✅): Automated sanity checks green on v1f baseline. Latest run (`BL014-SANITY-20260326-215800-844786`) passed 22/22 checks. Active freshness suite (`BL-FRESHNESS-SUITE-20260326-215801`) passed 7/7.
- **Reproducibility** (BL-010 ✅): Latest pass `BL010-REPRO-20260326-215557` (`deterministic_match=true`, 3 replays). Note: BL-010 internal config snapshot uses 70,680 candidates (pinned before v1f finalisation); reproducibility property holds on that pinned state.
- **Controllability** (BL-011 ✅): Latest pass `BL011-CTRL-20260326-215213` (`all_variant_shifts_observable=true`, 5 scenarios). Note: BL-011 internal config snapshot uses 33,096 candidates (pinned before v1f finalisation); controllability property holds on that pinned state.
- **Post-Migration Stabilization** (2026-03-26 ✅): BL-ordered folder migration is runtime-stable. Latest v1f orchestration pass: `BL013-ENTRYPOINT-20260326-215741-269303`.
- **Tier-1 Hardening Closure** (2026-03-25 ✅): CRI-004, CRI-002, HIGH-003, HIGH-004, and CRI-003 are implemented, validated, and logged in `00_admin/tier1_hardening_execution_log_2026-03-25.md`.
- **Current Execution Focus** (2026-03-26 22:30 UTC): v1f baseline fully operational. Primary remaining work: UI-003 citation closure, chapter text alignment to v1f counts (46,776 candidates, 10 components, 22/22 checks), and Chapter 4/5 evidence packaging.
- **Active Risk (Governance)**: Citation-package closure (UI-003) remains the sole submission-hardening dependency.
- **Implementation Quality Status**: Pipeline closed on the active v1f baseline (`run_config_ui013_tuning_v1f.json`). BL-014 passes 22/22. All 10 scoring components active. BL-010 determinism and BL-011 controllability confirmed on their respective pinned states. No open implementation closure risks.

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
2026-03-26 22:30 UTC

- Reason for last update:
(1) Added priority status checkpoint for evidence audit session (EXP-048 / C-182): resolved all 10 playlist track titles, documented BL-010/BL-011 config-snapshot candidate-count divergence, and packaged dissertation claims by strength. (2) Updated BL-020 implementation state section to reflect v1f canonical numbers (46,776 candidates, 10-component scoring, 22/22 checks, resolved playlist). (3) Updated BL-021 and Artefact Refinement Cycle as-of dates.

## Locked Definitions
- Artefact scope lock: `00_admin/Artefact_MVP_definition.md`
- Evaluation plan: `00_admin/evaluation_plan.md`
- Methodology definition: `00_admin/methodology_definition.md`