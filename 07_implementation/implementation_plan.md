# Implementation Plan

## Delivery Strategy
- Follow the locked MVP scope: single-user, deterministic, content-based playlist generation with transparency and controllability.
- Build incrementally from ingestion -> alignment -> scoring -> assembly -> evaluation artifacts.
- Produce evidence artifacts during implementation, not after it.

## Phases
1. Phase A: Synthetic data bootstrap and core pipeline development
- Create synthetic pre-aligned data assets (BL-016): a hand-crafted aligned JSONL and a candidate stub CSV that match the schemas defined in `06_data_and_sources/schema_notes.md`.
- Use these assets to drive BL-004 through BL-012 without real ingestion.
- Real ingestion and alignment (BL-001, BL-002, BL-003) are deferred to Phase A-Real (see below).
- BL-019 planning addendum (2026-03-21): implement the DS-002 candidate-corpus workflow (`MSD subset + Last.fm tags`; optional MusicBrainz metadata) with deterministic joins, manifest output, and quality-gate checks before downstream reruns.
- Rationale: unblocks core pipeline implementation immediately; see decision_log.md D-005.
- Corpus note (2026-03-21 update): use DS-002 as the active real-data corpus strategy for BL-019 planning and implementation. Keep prior Onion artifacts as historical baseline evidence only.

1a. Phase A-Real: Ingestion and data alignment (deferred)
- Define and validate one real ingestion path (BL-001, BL-002).
- Implement ISRC-first matching and fallback metadata logic (BL-003).
- Output alignment diagnostics and unmatched-track reporting.
- Resume after the core pipeline (Phases B–D) is proven end-to-end on synthetic data.

2. Phase B: Deterministic preference and candidate scoring
- Construct deterministic preference profile from imported history and influence tracks.
- Filter candidate tracks from the DS-002 integrated corpus feature space.
- Compute deterministic similarity scores with explicit component weights.

3. Phase C: Playlist assembly and controllability controls
- Assemble playlists using explicit rules for diversity, coherence, and ordering.
- Expose key parameters for controllability experiments.
- Ensure deterministic outputs for identical input/configuration.

4. Phase D: Transparency, observability, and evaluation
- Generate per-track explanation outputs (component contributions and adjustments).
- Capture run logs: config, inputs, outputs, and diagnostics.
- Execute reproducibility and parameter-sensitivity tests.

## Definition Of Done (MVP)
- End-to-end run succeeds on at least one real user data import path.
- Deterministic reruns produce identical playlist outputs under fixed configuration.
- Explanation and run-log artifacts are generated for each evaluation run.
- Rule compliance and controllability tests are documented in implementation and quality-control notes.

## Risks And Controls
- Data mismatch risk: Track alignment may fail for part of imported data.
	- Control: explicit unmatched reporting and fallback matching path.
- Corpus volatility risk: the canonical candidate dataset may change while implementation is in progress.
	- Control: lock BL-019 to DS-002 source contracts (`MSD subset`, `Last.fm tags`; optional MusicBrainz metadata) and record manifest hashes for each refresh run.
- Over-scope risk: Feature creep beyond MVP.
	- Control: backlog priority enforcement (P0 first, P1/P2 deferred).
- Evidence gap risk: claims without traceable outputs.
	- Control: require artifact links for each completed backlog item.

