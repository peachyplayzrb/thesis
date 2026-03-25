# Implementation Plan

Last updated: 2026-03-25

## Delivery Strategy
- Follow the locked MVP scope: single-user, deterministic, content-based playlist generation with transparency and controllability.
- Build incrementally from ingestion -> alignment -> scoring -> assembly -> evaluation artifacts.
- Produce evidence artifacts during implementation, not after it.

## Phases

### Phase A: Synthetic data bootstrap and core pipeline development — COMPLETE
- Synthetic pre-aligned data assets (BL-016) were created as a hand-crafted aligned JSONL and candidate stub CSV.
- These assets drove BL-004 through BL-012 while real ingestion was deferred.
- DS-002 candidate corpus (`MSD subset + Last.fm tags`) built and verified via BL-019 (9,330 tracks; quality gates pass; determinism confirmed — EXP-016).

### Phase A-Real: Ingestion and data alignment — COMPLETE
- Real Spotify API export implemented (BL-002): 5,592 unique tracks from top tracks and saved history.
- BL-003 active alignment uses direct DS-001 metadata/identifier mapping for imported Spotify records; ISRC-first matching with fallback metadata logic.
- Source-scope control (BL-021) implemented: canonical run-config `input_scope` contract applied at BL-003 with scope manifest evidence (`bl003_source_scope_manifest.json`).

### Phase B: Deterministic preference and candidate scoring — COMPLETE
- BL-004 ✅: Deterministic preference profile from imported history and optionally influence tracks; outputs `bl004_preference_profile.json`, `bl004_profile_summary.json`, `bl004_seed_trace.csv`.
- BL-005 ✅: Candidate filtering against DS-001 corpus (1,740 kept candidates) with semantic and numeric proximity gating.
- BL-006 ✅: Deterministic multi-component scoring with explicit component weights; outputs `bl006_scored_candidates.csv`, `bl006_score_summary.json`.

### Phase C: Playlist assembly and controllability — COMPLETE
- BL-007 ✅: Rule-based assembly; 10-track playlist with genre diversity and ordering constraints; score range 0.596–0.771.
- BL-010 ✅: Reproducibility validated — identical outputs across three replayed runs.
- BL-011 ✅: Controllability validated — five parameter scenarios with measurable output deltas.
- Canonical run-config system (BL-013, `run_config_utils.py`): single JSON contract drives all stages; all controls configurable without code changes.

### Phase D: Transparency, observability, and evaluation — COMPLETE
- BL-008 ✅: Per-track explanation payloads with component contribution breakdowns and rule-effect traces.
- BL-009 ✅: Versioned observability log (`bl009-observability-v1`) with stage traceability, artifact hashes, execution scope summary, and canonical config artifact pair links.
- BL-013 ✅: Lightweight orchestrator; emits canonical run-intent/run-effective-config artifact pair (`run-intent-v1` / `run-effective-config-v1`) before every run.
- BL-014 ✅: Automated sanity checks; 21/21 checks pass (schema validation, cross-stage hash integrity, count/run-id continuity).
- Semantic control-layer map: `07_implementation/implementation_notes/run_config/semantic_control_map.md` — seven semantic groups map every run-config field to stage, resolver, and output artifacts.

## Definition Of Done (MVP) — ALL MET
- ✅ End-to-end run succeeds on a real user data import path (BL013-ENTRYPOINT-20260325-001946-187550).
- ✅ Deterministic reruns produce identical playlist outputs under fixed configuration (BL-010 reproducibility pass).
- ✅ Explanation and run-log artifacts are generated for each evaluation run.
- ✅ Rule compliance and controllability tests are documented (BL-011, EXP series, TC series).

## Current Execution Posture
- All pipeline stages (BL-003 to BL-009) and evaluation stages (BL-010, BL-011, BL-013, BL-014) are stable and validated.
- Active work is bounded to thesis writing hardening (Chapters 1–5) and citation-package closure (UI-003).
- No scope expansion beyond locked MVP; backlog items remain deferred per `07_implementation/backlog.md`.

## Risks And Controls
- Data mismatch risk: some imported tracks may not match the DS-001 corpus.
	- Control: explicit unmatched reporting in BL-003/BL-004 diagnostics; missing-seed count tracked per run.
- Over-scope risk: Feature creep beyond MVP.
	- Control: backlog priority enforcement (P0 first, P1/P2 deferred).
- Evidence gap risk: claims without traceable outputs.
	- Control: all completed items carry artifact links; BL-009 observability log is the canonical per-run audit record.

