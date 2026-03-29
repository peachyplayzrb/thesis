# Observability Design

DOCUMENT STATUS: implementation-synchronized observability design
LAST SYNCHRONIZED: 2026-03-29 UTC
ROLE: BL-009 run-level audit architecture reference

## Purpose
Define the run-level visibility required to audit, replay, and diagnose pipeline behavior under thesis evaluation constraints.

## Design Goal
Make each execution traceable from input and configuration through alignment, scoring, assembly, and final outputs.

## Scope Position

- Observability is artefact-level execution visibility, not production SRE telemetry.
- Logging scope is optimized for transparency, controllability, and reproducibility evaluation.
- MVP favors structured, deterministic run records over high-volume monitoring.

## Observability Requirements

1. Every run has a unique run identifier.
2. Input summary and configuration snapshot are persisted.
3. Stage-level diagnostics are captured for all major pipeline stages.
4. Score and rule traces are linkable to final playlist outputs.
5. Failures and exclusions are recorded with explicit reasons.

## Run Log Schema (Implemented)

### 1. `run_metadata`
- `run_id`
- `generated_at_utc`
- `dataset_version`
- `pipeline_version`
- stage lineage and provenance fields

### 2. `run_config`
- effective control surfaces and config-source metadata
- run-config provenance artifacts where available

### 3. `ingestion_alignment_diagnostics`
- imported row counts
- valid/invalid counts
- matched by ISRC count
- matched by fallback count
- unmatched count and representative reasons

### 4. `stage_diagnostics`
- BL-003 through BL-008 diagnostics aggregated into one run log surface
- stage-level counts, summary metrics, and key diagnostic blocks

### 5. `exclusion_diagnostics`
- BL-005 and BL-007 exclusion samples with reason categories
- capped diagnostic sampling for readability

### 6. `output_artifacts`
- primary outputs, trace outputs, supporting outputs
- artifact hash and size metadata for integrity checks

## Diagnostic Coverage by Stage

1. Ingestion: schema validity and source record summary.
2. Alignment: match-path and unmatched visibility.
3. Profile construction: profile input coverage summary.
4. Candidate generation: pool size and filtering reasons.
5. Scoring: contribution-level traceability.
6. Assembly: constraint and ordering behavior.
7. Transparency: explanation payload lineage.
8. Observability: run-chain consistency and artifact integrity.

## Reproducibility Link

Observability design must support deterministic replay checks:

1. Same input + same config => same output.
2. Differences across runs must be explainable from recorded config/data/version changes.
3. Artifact-level hash surfaces must support evidence integrity checks.

## Evaluation Alignment

Observability evidence in Chapter 4 should verify:

1. Trace completeness against required schema.
2. Diagnostic usefulness for explaining outcomes.
3. Replayability support from stored run records.
4. Cross-stage provenance continuity through required artifact contracts.

## Risks and Mitigations

1. Risk: Missing stage logs break audit chain.
	- Mitigation: required-field validation before run finalization.
2. Risk: Excessive log detail harms readability.
	- Mitigation: keep layered logs (summary plus deep trace).
3. Risk: Inconsistent identifiers across artifacts.
	- Mitigation: enforce run_id and track_id linkage rules.
4. Risk: Overstating transparency from observability data.
	- Mitigation: keep control-causality and counterfactual limits explicit.

## Known Limits in Current Implementation
1. Observability aggregates diagnostics but does not provide full per-track control-causality attribution.
2. Counterfactual what-if analysis is not emitted by BL-009.
3. Exclusion details are sampled rather than exhaustively embedded in top-level summaries.

## Boundary Note

This observability design supports thesis-level inspectability and reproducibility claims for a deterministic MVP. It does not attempt full production monitoring or real-time operations analytics.
