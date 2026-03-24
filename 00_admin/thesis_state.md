# Thesis State

Last updated: 2026-03-25

## Official Current State

- Current title:
Engineering an Automated, Transparent, and Controllable Playlist Generation Pipeline Using Cross-Source Music Preference Data

- Current research question:
What design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data?

- Current objectives:
1. Design an automated pipeline that generates playlists from user listening histories.
2. Align cross-platform listening data into an inspectable preference signal using robust metadata handling and semantic enrichment.
3. Construct a deterministic user preference profile based on imported listening data, user-selectable source scope, and manually selected influence tracks.
4. Generate candidate tracks from the active integrated candidate dataset using feature-based filtering.
5. Score candidate tracks using deterministic similarity functions and rule-based adjustments.
6. Assemble playlists using playlist-level rules that ensure diversity, coherence, and ordering.
7. Provide transparent explanations and observability mechanisms for recommendation decisions.
8. Evaluate the system with respect to transparency, controllability, inspectability, and reproducibility.

- Current artefact definition:
A deterministic single-user playlist generation pipeline with one practical ingestion path, semantic preference extraction from imported history, deterministic feature-based scoring on a fixed candidate corpus, configurable playlist assembly rules, transparent score explanations, reproducible run logging, and implemented source-scope control via canonical run-config (`input_scope`) with recorded effective scope in BL-004 and BL-009 outputs.

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
The active candidate corpus is DS-002 (`MSD subset + Last.fm tags`). The BL-019 intersection dataset has been built and verified (9330 tracks, all quality gates pass, determinism confirmed — see `07_implementation/experiment_log.md` EXP-016). Music4All/Music4All-Onion remains a historical baseline and fallback reference. Real Spotify history is now available via BL-002 API export. For BL-020, user-side preference extraction is executed as semantic enrichment (Last.fm top tags on imported Spotify tracks) because Spotify Web API audio-feature endpoints are deprecated. Candidate-side audio features (`tempo`, `loudness`, `key`, `mode`) remain sourced from DS-002. MusicBrainz-related fields exist in the dataset as optional metadata but are not currently used in the active pipeline.

DS-001 (Music4All access-reopened path) remains governance-pending and is not active until provenance, terms, and compatibility checks are fully recorded (tracked in UI-008).

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
1. Close `UI-008` governance completion: finalize DS-001 provenance, version, terms, and checksum capture before any activation decision.
2. Close `UI-003` thesis-wide citation package: complete claim-citation hardening synthesis for Chapters 2 to 5 and finalize chapter-targeted improvement notes.
3. Continue mentor sprint execution at Day 4 to Day 7 from `00_admin/mentor_draft_7day_sprint_2026-03-23.md`.
4. Keep website integration under bounded hardening only (`WP-WEBINT-001`): bug fixes, observability clarity, and orchestration reliability without scope expansion.

Priority status checkpoint (2026-03-25): UI-002 is closed for current Chapter 2 audit workflow; UI-003 and UI-008 remain the two governance-critical open items.

## Current Implementation Status

### BL-020 Implementation State (as of 2026-03-25)
- **Ingestion**: Schema locked (BL-001 ✅), parser + Web API exporter implemented (BL-002 ✅), real Spotify API export completed (5,592 unique tracks from top + saved history)
- **Candidate Dataset**: DS-002 built and verified (BL-019 ✅) — 9,330 tracks ready for pipeline
- **Alignment** (BL-003 ✅): Last.fm tag enrichment completed end-to-end on 2026-03-22. Outputs: `bl020_aligned_events.jsonl` (5,592 events, 5.9 MB), `bl020_alignment_report.json`, `bl020_lastfm_tag_cache.json` (5.4 MB). Coverage: 5,361 successfully tagged (95.87%), 204 no_tags (3.65%), 27 errors (0.48%). Runtime: ~101 minutes. Evidence in EXP-022/TC-BL020-001.
- **Preference Profiling** (BL-004 ✅): Profile generation completed on 2026-03-22 from enriched events. Output: `bl004_preference_profile.json`, `bl004_profile_summary.json`, `bl004_seed_trace.csv`. Dominant lead genres: classical, classic rock, progressive rock, pop, rock. Feature centers: empty dict (semantic-only mode). Evidence in EXP-023/TC-BL020-002.
- **Candidate Filtering** (BL-005 ✅): Semantic filtering completed on 2026-03-22 against 9,330 DS-002 candidates using BL-004 profile. Output: `bl005_filtered_candidates.csv` (1,740 kept, 18.62% retention), full decision audit trail, deterministic diagnostics. Evidence in EXP-026/TC-BL020-005.
- **Candidate Scoring** (BL-006 ✅): Semantic-weighted similarity scoring completed on 2026-03-22 against 1,740 filtered candidates using BL-004 profile. Output: `bl006_scored_candidates.csv` (ranked 0.77–0.01, mean 0.214, median 0.183), `bl006_score_summary.json` (diagnostics, top 10). Weights re-normalized for semantic-only mode (lead_genre 36.4%, genre_overlap 30.9%, tag_overlap 32.7%). Evidence in EXP-027/TC-BL020-006.
- **Playlist Assembly** (BL-007 ✅): Rule-based playlist assembly completed on 2026-03-22 from 1,740 scored candidates. Output: `bl007_playlist.json` (10-track final playlist), `bl007_assembly_trace.csv` (audit trail for all 1,740 candidates), `bl007_assembly_report.json` (rule hits and genre distribution). Genre mix: classic rock (4), pop (3), progressive rock (2), rock (1). Score range: 0.596–0.771. Evidence in EXP-028/TC-BL020-007.
- **Transparency Explanations** (BL-008 ✅): Transparency explanation payload generation completed on 2026-03-22 for all 10 playlist tracks. Output: `bl008_explanation_payloads.json` (10 explanations with why_selected sentences and score breakdowns), `bl008_explanation_summary.json` (metadata and top contributor distribution). Top contributors: lead genre match (6 tracks), tag overlap (3 tracks), genre overlap (1 track). All component weights correctly represented (semantic-only mode). Evidence in EXP-029/TC-BL020-008.
- **Observability** (BL-009 ✅): Canonical run-level observability completed on 2026-03-22. Output: `bl009_run_observability_log.json` and `bl009_run_index.csv` with stage traceability, configuration snapshots, diagnostics, and artifact hashes. Evidence in EXP-030/TC-BL020-009.
- **Pipeline Completion**: BL-020 is fully complete (BL-003 through BL-009 executed, logged, and test-documented).
- **Quality Automation** (BL-014 ✅): Automated sanity checks completed on 2026-03-22 via `run_bl014_sanity_checks.py`. Result: 21/21 checks passed across schema validation, cross-stage hash integrity, and count/run-id continuity for BL-004 through BL-009 artifacts. Evidence in EXP-031/TC-BL014-001.
- **Current Execution Focus** (2026-03-25): keep deterministic recommendation behavior stable while continuing bounded website integration and thesis-writing hardening in parallel; avoid scope expansion beyond active work packages and deferred-item boundaries.
- **Active Risk**: External API reliability (Last.fm) is explicitly tracked in run reports; all observable transient errors logged

### BL-021 Source-Scope Control State (as of 2026-03-25)
- Source-scope contract is baseline behavior (no longer deferred): implemented, validated, and traceable in run artifacts.
- BL-003 applies `input_scope` filtering and emits `bl003_source_scope_manifest.json`.
- BL-004 and BL-009 persist effective source-scope plus run-config provenance.
- BL-013 supports optional one-command seed refresh (`--refresh-seed`) for scope-sensitive reruns.

### Detailed Audit
See: `07_implementation/BL020_HANDOFF_AUDIT_2026-03-21.md` for comprehensive pre-implementation checklist and artifact inventory.

## Update Control

- Last updated:
2026-03-25

- Reason for last update:
(1) Align execution posture wording with supersession state (freeze-first mode treated as historical context, not active strategy). (2) Add explicit DS-001 governance-pending note to prevent corpus-activation ambiguity while UI-008 remains open. (3) Add priority-status checkpoint clarifying UI-002 closure and current critical open items (UI-003, UI-008). (4) Synchronize BL-021 source-scope status placement and implementation-state date with current control docs.

## Locked Definitions
- Artefact scope lock: `00_admin/Artefact_MVP_definition.md`
- Evaluation plan: `00_admin/evaluation_plan.md`
- Methodology definition: `00_admin/methodology_definition.md`