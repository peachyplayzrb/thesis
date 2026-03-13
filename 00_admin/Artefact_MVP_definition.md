# Artefact MVP Definition

## Purpose
Define the minimum viable BSc-level artefact that satisfies university assessment constraints while preserving thesis contribution focus.

## MVP Boundary
Single-user deterministic playlist generation system with transparent scoring and controllable parameters, using one practical ingestion path and one canonical feature corpus.

## Core Functionality (Must Exist)
1. Data ingestion for one selected listening-history source format (single adapter path) plus optional manual seed/influence tracks.
2. Track alignment into candidate corpus using ISRC-first matching with metadata fallback.
3. Deterministic preference profile construction from matched tracks.
4. Deterministic candidate scoring using explicit feature weights and documented adjustment rules.
5. Playlist assembly stage with at least three playlist-level constraints:
- playlist length control
- artist repetition limit
- diversity or ordering control
6. Explanation output that exposes per-track score contributors and rule adjustments.
7. Run logging sufficient for reproducibility:
- input summary
- alignment stats
- scoring configuration
- top-ranked outputs

## Optional Features (Can Be Deferred)
- Multiple external platform adapters.
- Advanced UI with many control widgets.
- Rich visualization dashboard for observability.
- Automated hyperparameter exploration.
- Extended fallback matching heuristics beyond core metadata fallback.

## Explicit Out Of Scope
- Collaborative filtering or deep neural recommendation models.
- Multi-user personalization experiments.
- Large-scale online user study.
- Production-grade deployment/infrastructure concerns.
- Full cross-platform adapter ecosystem.

## Acceptance Criteria For MVP Completion
- End-to-end run executes deterministically under fixed configuration.
- At least one generated playlist can be reproduced exactly from saved configuration.
- Explanation output is traceable to deterministic scoring logic.
- Parameter changes produce observable, documented output differences.
- Testing evidence exists and links back to research question and assessment criteria.
