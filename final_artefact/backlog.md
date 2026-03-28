# Backlog

Last updated: 2026-03-27 16:54 UTC

## Priority Legend
- P0: Must complete for locked MVP and assessment evidence.
- P1: Strongly recommended quality improvement.
- P2: Optional stretch item if time permits.

## Current Execution Posture (2026-03-27)
- Core implementation scope is complete on the active v1f baseline.
- Active profile baseline: `run_config_ui013_tuning_v1f.json`.
- Canonical baseline authority and full evidence chains:
  - `07_implementation/ACTIVE_BASELINE.md`
- Latest integrated evidence chain remains green.
- Latest experimental v2a evidence wave remains green (non-canonical).
- Latest same-day website/server environment-mode wave remains logged as non-canonical.
- Current active work is bounded to:
  - BL-023 website-to-pipeline integration
  - chapter hardening follow-through from the closed UI-003 package
- BL-022, BL-024, and BL-025 remain deferred.
- BL-015 remains out of core scope.

## Items

| ID | Priority | Status | Task | Current Evidence Output |
| --- | --- | --- | --- | --- |
| BL-001 | P0 | done | Define ingestion schema for one platform export path | `06_data_and_sources/schema_notes.md` + BL-001/BL-002 docs under `07_implementation/implementation_notes/bl001_bl002_ingestion/` |
| BL-002 | P0 | done | Implement ingestion parser and validation checks | `07_implementation/implementation_notes/bl001_bl002_ingestion/ingest_history_parser.py`, `export_spotify_max_dataset.py`, runbook, and Spotify export outputs |
| BL-003 | P0 | done | Implement DS-001 alignment with metadata/identifier fallback and source-scope actuation | `bl003_ds001_spotify_seed_table.csv`, `bl003_ds001_spotify_summary.json`, `bl003_source_scope_manifest.json`; latest active seed rows `1064` |
| BL-004 | P0 | done | Build deterministic user preference profile generator | `bl004_preference_profile.json`, `bl004_profile_summary.json`, `bl004_seed_trace.csv` |
| BL-005 | P0 | done | Implement candidate retrieval and feature filtering | `bl005_filtered_candidates.csv`, `bl005_candidate_decisions.csv`, `bl005_candidate_diagnostics.json`; latest kept candidates `46776` |
| BL-006 | P0 | done | Implement deterministic scoring function with weighted components | `bl006_scored_candidates.csv`, `bl006_score_summary.json`; active component count `10` on v1f |
| BL-007 | P0 | done | Implement rule-based playlist assembly (diversity, coherence, ordering) | `bl007_playlist.json`, `bl007_assembly_trace.csv`, `bl007_assembly_report.json`; latest playlist `10/10` |
| BL-008 | P0 | done | Add transparency outputs (score contribution and rule adjustment trace) | `bl008_explanation_payloads.json`, `bl008_explanation_summary.json`; canonical v1f top-contributor mix remains documented, with additional same-day non-canonical wave showing `4/3/2/1` across lead genre/tag overlap/danceability/tempo |
| BL-009 | P0 | done | Add observability logging with canonical config-artifact linkage | `bl009_run_observability_log.json`, `bl009_run_index.csv`; schema `bl009-observability-v1` |
| BL-010 | P0 | done | Execute reproducibility tests (same input/config => same output) | `bl010_reproducibility_report.json`; latest canonical v1f run `BL010-REPRO-20260327-201949`, `deterministic_match=true` |
| BL-011 | P0 | done | Execute controllability tests (parameter sensitivity) | `bl011_controllability_report.json`, `bl011_controllability_run_matrix.csv`; latest canonical v1f run `BL011-CTRL-20260327-202057`, five scenarios |
| BL-012 | P0 | done | Document limitations and failure modes from test outcomes | `02_foundation/limitations.md` + `08_writing/chapter5.md` |
| BL-013 | P1 | done | Lightweight orchestrator with repeatable run controls and canonical config artifacts | `run_bl013_pipeline_entrypoint.py`, `run_intent_*.json`, `run_effective_config_*.json`; latest canonical integrated run `BL013-ENTRYPOINT-20260327-201712-508978` |
| BL-014 | P1 | done | Automated sanity and freshness checks for active outputs | `run_bl014_sanity_checks.py`, `run_active_freshness_suite.py`, `check_bl010_bl011_freshness.py`; latest canonical sanity/freshness `22/22` and `19/19` on `BL014-SANITY-20260327-201731-408637` / `BL-FRESHNESS-SUITE-20260327-201942` |
| BL-015 | P2 | todo | Add second ingestion adapter scaffold (out of core scope) | Backlog-only design note |
| BL-016 | P0 | done | Create synthetic pre-aligned data assets for core pipeline development | `07_implementation/implementation_notes/test_assets/` |
| BL-017 | P0 | done | Build active DS-001 working dataset layer with quality checks | `07_implementation/implementation_notes/bl000_data_layer/outputs/` |
| BL-018 | P0 | done | Candidate-corpus feasibility review | `07_implementation/implementation_notes/bl000_data_layer/candidate_corpus_feasibility_review_2026-03-19.md` |
| BL-019 | P0 | done | Build DS-002 integrated candidate dataset fallback reference | `07_implementation/implementation_notes/bl000_data_layer/outputs/`; validated fallback corpus (`9330` tracks) |
| BL-020 | P0 | done | Full pipeline redo against updated ingestion schema and DS-001 corpus | Current stage outputs under `07_implementation/implementation_notes/`; active implementation baseline is now stabilized on v1f |
| BL-021 | P1 | done | Add user-selectable source-scope control and persist effective scope in run metadata | Run-config `input_scope`, `bl003_source_scope_manifest.json`, controllability evidence |
| BL-022 | P1 | todo | Add deterministic corpus fallback policy (DS-001 first, DS-002 fallback on low coverage) | Fallback policy spec + path-selection metadata + A/B report |
| BL-023 | P1 | doing | Integrate website flow with deterministic pipeline outputs and run orchestration | `07_implementation/website.md`, website/server flow, UI run trace and artifact linkage |
| BL-024 | P1 | todo | Bounded implementation hardening (error handling, observability clarity, rerun controls) without changing core recommendation logic | Hardening diff summary + updated diagnostics examples + stability notes |
| BL-025 | P1 | todo | Add user-selectable BL-005 retrieval decision policy mode via run-config (planning approved, runtime deferred) | Policy-mode field spec + validation plan |

## Active

### BL-023 — Website-to-Pipeline Integration
Status: in progress since 2026-03-23.

Scope:
- Wire `07_implementation/website/` controls to real pipeline execution.
- Trigger or surface BL-013 orchestration from the website flow.
- Render stage status, diagnostics, playlist outputs, and explanations from live artifacts.

Current boundary:
- Keep work bounded to integration, reliability, and observability clarity.
- Do not expand recommendation scope or reopen closed pipeline items.

Related current non-implementation dependency:
- No active unresolved governance dependency outside the code backlog.

## Deferred

- BL-024 (P1): bounded hardening after BL-023 stabilizes.
- BL-022 (P1): deterministic dataset fallback policy.
- BL-025 (P1): BL-005 retrieval policy modes.
- BL-015 (P2): second ingestion adapter scaffold.

## Done

All P0 implementation items are complete. Previously active P1 implementation items for BL-013, BL-014, and BL-021 are also complete.

Key final-state references:
- Latest full-chain orchestrated run: `BL013-ENTRYPOINT-20260327-201712-508978`
- Reproducibility: `BL010-REPRO-20260327-201949`
- Controllability: `BL011-CTRL-20260327-202057`
- Sanity: `BL014-SANITY-20260327-201731-408637`
- Active freshness suite: `BL-FRESHNESS-SUITE-20260327-201942`
- Latest experimental (v2a) run wave: `BL013-ENTRYPOINT-20260327-002121-545346` + `BL010-REPRO-20260327-001916` + `BL011-CTRL-20260327-002019` + `BL014-SANITY-20260327-002035-164549` + `BL-FRESHNESS-SUITE-20260327-002136`
- Semantic control-layer map: `07_implementation/implementation_notes/bl000_run_config/docs/semantic_control_map.md`
- Current implementation summary: `_deep_archive_march2026/IMPLEMENTATION_STATE_2026-03-24.md` (historical snapshot)

## Notes

- Active reporting should use the v1f baseline, not earlier v1b/v1d snapshots.
- `run_config_ui013_tuning_v2a_retrieval_tight.json` is experimental and is not the canonical reporting baseline.
- DS-001 is the active execution corpus; DS-002 remains a validated fallback reference, not the live path.
- Use run-specific artifacts as canonical evidence; use `*_latest` artifacts as convenience pointers only.
