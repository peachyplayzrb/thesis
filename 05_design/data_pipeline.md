# Data Pipeline

DOCUMENT STATUS: implementation-synchronized data pipeline design
LAST SYNCHRONIZED: 2026-03-29 UTC
ROLE: code-grounded data and artifact flow reference

## 1) Purpose
Describe how data moves through BL-003 to BL-009, what each stage consumes and emits, and how data quality/provenance is maintained.

## 2) Primary Data Inputs
1. Candidate corpus input: DS-001 working candidate dataset.
2. User-source inputs: exported listening/history artifacts (top tracks, saved tracks, playlists, recently played).
3. Run-control input: run-config plus optional environment overrides.

## 3) Stage-by-Stage Data Flow

### BL-003 Alignment
Inputs:
- Candidate reference rows (for match targets).
- Source event rows from export artifacts.
- Source-scope and matching controls.

Outputs:
- Seed table CSV with matched candidate enrichment.
- Alignment summary JSON.
- Source-scope manifest JSON.

### BL-004 Profile
Inputs:
- BL-003 seed table and summary/contracts.
- Profile controls (limits, weighting, attribution policy).

Outputs:
- Profile JSON (numeric and semantic signal surfaces).
- Seed trace CSV.
- Profile summary JSON.

### BL-005 Retrieval
Inputs:
- BL-004 profile artifacts.
- Candidate dataset rows.
- Retrieval controls (thresholds, support modes, penalties, language/recency options).

Outputs:
- Filtered candidate CSV.
- Candidate decisions CSV.
- Retrieval diagnostics JSON.

### BL-006 Scoring
Inputs:
- BL-004 profile artifacts.
- BL-005 filtered candidates.
- Scoring controls (weights, thresholds, semantic/numeric behavior).

Outputs:
- Scored candidates CSV.
- Score distribution diagnostics JSON.
- Score summary JSON.

### BL-007 Playlist
Inputs:
- BL-006 scored candidates.
- Assembly controls.

Outputs:
- Playlist JSON.
- Assembly trace CSV.
- Assembly report JSON.

### BL-008 Transparency
Inputs:
- BL-006 scored candidates.
- BL-007 playlist and trace/report context.
- Explanation controls.

Outputs:
- Explanation payloads JSON.
- Explanation summary JSON.

### BL-009 Observability
Inputs:
- Required BL-003 to BL-008 artifact surfaces through registry contracts.

Outputs:
- Run observability log JSON (aggregated diagnostics, provenance, hashes).

## 4) Data Contract and Dependency Notes
1. Stage outputs are consumed as explicit file contracts; BL-009 validates required-path availability.
2. BL-005 decision-surface fields and BL-006 scored-candidate fields function as de facto downstream interfaces.
3. BL-007 assembly outputs provide required context for BL-008 explanations and BL-009 audit aggregation.

## 5) Control and Data Interaction
1. Effective controls shape each stage's transformation and are resolved deterministically from config sources.
2. Control provenance is persisted in stage outputs and/or run-level observability records.
3. BL-007 control behavior is partially configurable: limits/strategies are tunable; rule order remains fixed.

## 6) Data Quality and Validation Strategy
1. Required artifact checks fail fast when critical upstream artifacts are missing.
2. Stage sanitizers enforce value bounds for control payloads.
3. Typed models/dataclasses are used in stage internals for safer transformation boundaries.
4. Hashing and artifact-size metadata provide integrity and reproducibility surfaces.

## 7) Known Pipeline Limits
1. Unmatched-source coverage from alignment remains a known quality boundary.
2. Influence-track effect is weak in current end-to-end behavior.
3. Counterfactual and per-track control-causality explanations are not generated in current outputs.

## 8) Boundary Statement
This pipeline design targets deterministic thesis evaluation (transparency, controllability, reproducibility, observability) and is not a production streaming architecture.
