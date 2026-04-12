# Artefact MVP Definition

Last updated: 2026-03-28

## Purpose
Define the minimum viable BSc-level artefact that satisfies university assessment constraints while preserving thesis contribution focus.

## Locked MVP Boundary (Current)
Single-user deterministic playlist generation pipeline with transparent scoring, controllable execution, and run-level observability. Scope is constrained to one practical ingestion path and one active candidate corpus strategy.

## Current Baseline (As Implemented)
- Ingestion path: Spotify listening-history import (BL-002) with optional manual influence tracks.
- User-side alignment approach: deterministic metadata/identifier alignment against DS-001 records (BL-003 active path).
- Candidate corpus: DS-001 (Music4All base) as active operational corpus.
- Source-scope controllability: implemented via canonical run-config `input_scope`, with effective scope persisted in BL-004 and BL-009 outputs.
- Pipeline stages: BL-003 through BL-009 complete with deterministic artifacts and BL-014 sanity checks in place.

## Core Functionality (Must Exist)
1. Data ingestion for one selected listening-history source format (single adapter path) plus optional manual seed/influence tracks.
2. Deterministic preference-signal construction from imported history via bounded metadata/identifier handling.
3. Deterministic preference profile construction from enriched inputs with auditable seed trace outputs.
4. Deterministic candidate filtering and scoring with explicit feature/semantic weights and documented adjustment rules.
5. Playlist assembly stage with at least three playlist-level constraints:
- playlist length control
- artist repetition control (when configured)
- diversity or ordering control
6. Explanation output that exposes per-track score contributors and rule adjustments.
7. Source-scope actuation controls that can change profile inputs in a traceable way.
8. Run logging sufficient for reproducibility and observability:
- input summary
- alignment/enrichment stats
- scoring configuration
- top-ranked outputs
- stage diagnostics and artifact provenance

## Optional Features (Can Be Deferred)
- Multiple external platform adapters.
- Advanced UI with many control widgets.
- Rich visualization dashboard for observability.
- Automated hyperparameter exploration.

## Known Limitations (Implementation-Bounded)
- Alignment miss-rate (~84%): most imported listening-history tracks do not find a match in DS-001 due to metadata/identifier coverage gaps; this is documented and accepted per `02_foundation/limitations.md`.
- Influence tracks have weak measured effect: BL-011 controllability testing shows zero directional shift in final playlist composition from adding/removing influence tracks via the current pre-profile injection path; direct assembly-layer integration is out of scope for the locked MVP.
- No unified per-track control-causality tracing: the `DECISION_FIELDS` contract captures scored metadata, but no field explicitly links each playlist position to the specific control parameter that produced it.
- No counterfactual explanation outputs: BL-008 explains actual score contributors but does not generate what-if alternative explanations.
- BL-007 partially configurable: thresholds and utility strategies are tunable via run-config, but rule order (R1 hard limits → R2 genre diversity → R3 utility-greedy → R4 relaxation) is fixed in code.
- No `max_per_artist` rule is configured in the canonical v1f baseline; Bruce Hornsby therefore appears twice in the canonical output (positions 2 and 10) — a known accepted limitation.
- User-side tempo/key/loudness unavailable: Spotify Web API audio-feature endpoints are deprecated, so numeric profile signals for those dimensions are absent.
- Extended fallback matching heuristics beyond the active DS-001 alignment path.

## Explicit Out Of Scope
- Collaborative filtering or deep neural recommendation models.
- Multi-user personalization experiments.
- Large-scale online user study.
- Production-grade deployment/infrastructure concerns.
- Full cross-platform adapter ecosystem.

## Acceptance Criteria for MVP Completion
- End-to-end run executes deterministically under fixed configuration.
- At least one generated playlist can be reproduced exactly from saved configuration.
- Explanation output is traceable to deterministic scoring logic.
- Parameter changes produce observable, documented output differences.
- Run-level observability outputs capture configuration, stage transitions, and artifact lineage.
- Testing evidence exists and links back to research question and assessment criteria.

## Drift Guardrails
- Do not change title, research question, or methodology from this file; those are controlled in `00_admin/thesis_state.md` and require explicit governance updates.
- Keep MVP wording synchronized with active baseline decisions in `00_admin/decision_log.md` and implementation state in `00_admin/thesis_state.md`.
