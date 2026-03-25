# Current Implementation Information Sheet — 2026-03-25

## Purpose
This document explains what the current implementation actually does, how the pipeline is structured, what each implemented part is responsible for, which artifacts it produces, and what the latest validated runtime behavior looks like.

It is not a conceptual architecture note. It is an implementation-state sheet aligned to the live code and current output artifacts.

## One-Sentence Summary
The current system is a deterministic single-user playlist generation pipeline that takes Spotify listening-history exports, aligns them to the active DS-001 candidate corpus, builds a hybrid semantic-plus-feature preference profile, retrieves and scores candidates, assembles a rule-constrained playlist, generates explanations, and writes structured observability artifacts.

## Current Execution Posture
- Active candidate corpus: DS-001 working candidate dataset
- Active orchestration entrypoint: BL-013
- Active sanity-check harness: BL-014
- Recommendation logic type: deterministic, content-based, hybrid semantic + numeric-feature scoring
- Current canonical validation status:
  - BL-013 pass: `BL013-ENTRYPOINT-20260325-163713-079187`
  - BL-014 pass: `BL014-SANITY-20260325-163738-023840` (`21/21` checks)

## High-Level Flow
1. Spotify export data is collected and normalized.
2. Imported listening events are aligned to tracks present in DS-001.
3. A preference profile is built from aligned listening history and optional influence tracks.
4. Candidate tracks are filtered using semantic evidence and numeric support rules.
5. Remaining candidates are scored using a weighted hybrid similarity function.
6. A final playlist is assembled using explicit playlist rules.
7. Explanations are generated for each playlist track.
8. Observability and audit artifacts are written.
9. Sanity checks validate schema, count continuity, and hash linkage across outputs.

## Core Control Layer

### Canonical Run Configuration
The active implementation uses a canonical run-config resolved through:
- `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`

This control layer normalizes and validates:
- input scope
- influence-track settings
- profile limits
- retrieval thresholds
- scoring thresholds and component weights
- assembly rules
- transparency limits
- observability settings

### Important Runtime Guardrails
The following guardrails are active in the current implementation:
- Positive threshold validation
- Retrieval/scoring numeric-threshold coupling
- Profile/retrieval limit compatibility checks
- Component-weight sum validation with rebalance diagnostics
- BL-003 seed freshness guard in BL-013
- BL-003 match-rate validation gate
- BL-007 undersized-playlist diagnostics

## Implemented Parts

### BL-001 — Ingestion Schema Layer
Status: baseline/locked support layer

Role:
- Defines the expected structure for imported listening-history data.
- Supports reproducible ingestion expectations upstream of BL-002.

What it means in practice:
- BL-001 is not the main runtime workhorse in the current orchestration path, but the implementation assumes a stable schema contract for downstream processing.

### BL-002 — Spotify Export / Ingestion Layer
Status: implemented and used as the live input path

Role:
- Collects Spotify user-history data from the available export path.
- Produces flat export artifacts consumed by BL-003.

Inputs:
- Spotify top tracks
- saved tracks
- playlist items
- recently played history

Outputs feed into:
- BL-003 alignment

Operational note:
- Current active path assumes Spotify metadata is available, but user-side audio-feature endpoints are deprecated, so candidate-side corpus features remain the numeric comparison source.

### BL-003 — Alignment / Seed Construction
Script:
- `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`

Role:
- Align imported Spotify events to DS-001 candidate rows.
- Produce the seed table used to build the preference profile.
- Record full traceability for matched and unmatched events.

What it does:
- Applies input-scope filtering from run-config.
- Aligns by Spotify/metadata matching logic.
- Aggregates matched events into DS-001-aligned seed rows.
- Emits unmatched-event diagnostics.
- Emits source-scope manifest and seed contract metadata.
- Enforces minimum match-rate threshold.

Key outputs:
- `bl003_ds001_spotify_seed_table.csv`
- `bl003_ds001_spotify_trace.csv`
- `bl003_ds001_spotify_unmatched.csv`
- `bl003_ds001_spotify_summary.json`
- `bl003_source_scope_manifest.json`

Current observed behavior:
- Input events: 12083
- Matched events: 1886
- Seed table rows: 1058
- Match-rate validation: `15.61%` vs threshold `15.0%` -> pass

Why it matters:
- BL-003 defines the evidence actually available to the downstream profile.
- It is the main point where corpus coverage limitations become visible.

### BL-004 — Preference Profile Construction
Script:
- `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`

Role:
- Convert aligned seeds into a deterministic user preference profile.

What it builds:
- semantic profile:
  - top tags
  - top genres
  - top lead genres
- numeric feature profile:
  - candidate-comparable numeric centers such as tempo, key, mode, duration, and other DS-001-side values

Important characteristic:
- The profile is hybrid, not semantic-only.
- It contains semantic preference structure and numeric centers derived from aligned candidate-side data.

Key outputs:
- `bl004_preference_profile.json`
- `bl004_profile_summary.json`
- `bl004_seed_trace.csv`

Current observed behavior:
- Matched seeds used: 1058

Why it matters:
- BL-004 is the canonical user-preference representation consumed by retrieval and scoring.

### BL-005 — Candidate Retrieval / Filtering
Script:
- `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`

Role:
- Filter the full candidate dataset into a smaller, defensible candidate pool before scoring.

What it does:
- Excludes seed tracks from retrieval output.
- Computes semantic evidence from overlap with profile lead genres, genres, and tags.
- Computes numeric pass counts where candidate-side numeric features align with profile numeric centers.
- Applies a semantic-first keep rule.

Current keep logic:
- keep strong semantic matches directly
- keep weaker semantic matches only if numeric support is present
- reject numeric-only candidates without semantic evidence

This means:
- retrieval is semantic-first
- retrieval is not numeric-only
- retrieval is not purely semantic if numeric features are available

Key outputs:
- `bl005_filtered_candidates.csv`
- `bl005_candidate_decisions.csv`
- `bl005_candidate_diagnostics.json`

Current observed behavior:
- Kept candidates: 72463
- Rejected non-seed candidates: 35748

Why it matters:
- BL-005 is the first stage that constrains what can ever appear in the final playlist.

### BL-006 — Candidate Scoring
Script:
- `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`

Role:
- Score retrieved candidates with a deterministic hybrid similarity function.

Scoring components:
- Numeric components:
  - tempo
  - duration_ms
  - key
  - mode
- Semantic components:
  - lead_genre
  - genre_overlap
  - tag_overlap

Important characteristic:
- BL-006 is hybrid semantic + numeric scoring.
- It is not a semantic-only scorer in the current canonical run.

What it does:
- Activates numeric components only when profile and candidate values are comparable.
- Drops inactive numeric components if needed.
- Re-normalizes active component weights when required.
- Emits explicit diagnostics when rebalancing occurs.

Current canonical run behavior:
- Candidates scored: 72463
- Mean score: 0.245727
- Max score: 0.787428
- Weight rebalance flag in latest canonical run: false

Key outputs:
- `bl006_scored_candidates.csv`
- `bl006_score_summary.json`

Why it matters:
- BL-006 defines the final rank order used by playlist assembly.

### BL-007 — Playlist Assembly
Script:
- `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`

Role:
- Convert ranked candidates into a final playlist using explicit rule-based assembly.

Rules applied:
- R1: minimum score threshold
- R2: max per genre
- R3: max consecutive same-genre run
- R4: target-length cap

What it does:
- Traverses ranked candidates greedily.
- Admits or excludes each candidate according to assembly rules.
- Writes a complete assembly trace.
- Emits undersized-playlist diagnostics if the playlist cannot reach target size.

Key outputs:
- `bl007_playlist.json`
- `bl007_assembly_trace.csv`
- `bl007_assembly_report.json`

Current observed behavior:
- Playlist length: 10/10
- Undersized warning: false in the latest canonical run

Why it matters:
- BL-007 is where ranking becomes an actual playlist and where diversity constraints become operational.

### BL-008 — Transparency / Explanation Generation
Script:
- `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`

Role:
- Generate human-readable and machine-readable explanations for every track in the final playlist.

What each explanation contains:
- playlist position
- score rank
- final score
- top score contributors
- full score breakdown
- assembly context
- concise why-selected text

Key outputs:
- `bl008_explanation_payloads.json`
- `bl008_explanation_summary.json`

Current observed behavior:
- Explanation payloads generated: 10

Why it matters:
- BL-008 is the main transparency surface for interpreting why a track appears in the playlist.

### BL-009 — Observability / Audit Logging
Script:
- `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`

Role:
- Consolidate the entire run into a structured audit log.

What it records:
- run metadata
- execution scope summary
- resolved run-config context
- stage diagnostics across BL-004 to BL-008
- exclusion diagnostics
- output artifact references and hashes
- propagated warning surfaces such as weight rebalance diagnostics

Key outputs:
- `bl009_run_observability_log.json`
- `bl009_run_index.csv`

Why it matters:
- BL-009 is the single most useful artifact for understanding what happened in one run without opening every stage output individually.

### BL-010 — Reproducibility Evaluation Harness
Status: implemented evaluation harness

Role:
- Re-run the deterministic pipeline pathway multiple times and compare outputs.

Important current posture:
- defaults to active pipeline outputs
- legacy surrogate inputs require explicit opt-in

Why it matters:
- BL-010 provides formal evidence for reproducibility claims.

### BL-011 — Controllability Evaluation Harness
Status: implemented evaluation harness

Role:
- Run controlled parameter changes and compare behavior across scenarios.

Important current posture:
- defaults to active pipeline outputs
- legacy surrogate inputs require explicit opt-in
- influence-track scenario wording is now dataset-agnostic

Why it matters:
- BL-011 provides formal evidence for controllability claims.

### BL-013 — End-to-End Orchestration
Script:
- `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`

Role:
- Run the active implementation end to end from BL-003 refresh through BL-009.

What it does:
- validates stage order
- optionally refreshes BL-003 seeds
- emits canonical run-intent and run-effective-config artifacts
- enforces BL-003 seed freshness when run-config is used
- runs BL-004 to BL-009 in order
- records orchestration summary and stable artifact hashes

Why it matters:
- BL-013 is the practical entrypoint for seeing the current implementation behave as one system.

### BL-014 — Sanity Check Harness
Script:
- `07_implementation/implementation_notes/bl014_quality/run_bl014_sanity_checks.py`

Role:
- Validate that the outputs from BL-004 to BL-009 are structurally coherent.

What it checks:
- required artifact presence
- schema shape
- cross-stage hash linkage
- count continuity
- run-id continuity
- advisory conditions such as undersized playlists

Current observed behavior:
- Latest run passed `21/21` checks

Why it matters:
- BL-014 is the quickest way to confirm that the pipeline outputs are internally consistent after code or config changes.

## Current Recommendation Logic: What the System Is Actually Using

### Short Answer
The current implementation does not build recommendations on semantics alone.

### More Precise Answer
- BL-004 builds a hybrid preference profile.
- BL-005 retrieval is semantic-first with numeric support.
- BL-006 scoring is hybrid semantic + numeric.
- In the latest canonical run, numeric components were active and no scoring rebalance fallback was needed.

Therefore, the live system is best described as:
- deterministic
- content-based
- hybrid semantic-plus-feature recommendation pipeline

## Current Run Snapshot (Canonical)
- BL-013 run ID: `BL013-ENTRYPOINT-20260325-151555-244335`
- overall status: pass
- elapsed: 15.123 seconds

Stage snapshot:
- BL-003 match rate: `15.61%` (`pass` against `15.0%` minimum)
- BL-004 seeds used: `1058`
- BL-005 kept candidates: `72463`
- BL-006 scored candidates: `72463`
- BL-007 final playlist: `10/10`
- BL-008 explanations: `10`
- BL-009 weight rebalance diagnostics: `false` in the latest canonical run

## Main Strengths of the Current Implementation
- Deterministic stage structure
- Strong traceability through JSON/CSV artifacts
- Canonical run-config control layer
- Explicit validation guardrails for stale or incoherent configurations
- Human-readable explanation payloads
- Run-level observability and sanity checking

## Main Current Limitations
- BL-003 alignment coverage is incomplete, so the profile is built from a subset of imported listening history.
- The system is single-user and content-based only.
- Numeric user-side Spotify audio features are not directly available from the current Spotify API path, so numeric comparisons rely on corpus-side candidate features and aligned DS-001 values.
- Recommendation quality remains bounded by the available descriptors and DS-001 coverage.
- BL-003 alignment coverage remains a practical quality boundary, but BL-010/BL-011 freshness controls are now implemented and passing in active quality checks.

## Best Files to Read If You Want to Understand the System Quickly
- BL-013 orchestration summary:
  - `07_implementation/implementation_notes/bl013_entrypoint/outputs/bl013_orchestration_run_latest.json`
- BL-003 alignment summary:
  - `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_summary.json`
- BL-004 profile summary:
  - `07_implementation/implementation_notes/bl004_profile/outputs/bl004_profile_summary.json`
- BL-005 retrieval diagnostics:
  - `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_diagnostics.json`
- BL-006 score summary:
  - `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json`
- BL-007 assembly report:
  - `07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_report.json`
- BL-008 explanation summary:
  - `07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_summary.json`
- BL-009 observability log:
  - `07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_observability_log.json`
- BL-014 sanity report:
  - `07_implementation/implementation_notes/bl014_quality/outputs/bl014_sanity_report.json`

## Final Interpretation
The current implementation is not just a conceptual prototype. It is an operational deterministic pipeline with explicit configuration control, evidence-producing stage outputs, and integrated validation. Its main trade-off is not lack of implementation depth; it is the bounded quality and coverage of the available aligned user-history signal.