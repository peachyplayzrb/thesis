# Observability Design

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

## Run Log Schema (Conceptual)

### 1. `run_metadata`
- `run_id`
- `timestamp`
- `dataset_version`
- `pipeline_version`

### 2. `run_config`
- all user-set and default parameter values
- control settings and bounds

### 3. `ingestion_alignment_diagnostics`
- imported row counts
- valid/invalid counts
- matched by ISRC count
- matched by fallback count
- unmatched count and representative reasons

### 4. `scoring_traces`
- candidate set size
- per-candidate score components
- applied rule adjustments

### 5. `assembly_diagnostics`
- selected tracks
- rule checks and violations
- ordering and constraint outcomes

### 6. `output_artifacts`
- final playlist
- explanation payloads
- summary metrics used in evaluation

## Diagnostic Coverage by Stage

1. Ingestion: schema validity and source record summary.
2. Alignment: match-path and unmatched visibility.
3. Profile construction: profile input coverage summary.
4. Candidate generation: pool size and filtering reasons.
5. Scoring: contribution-level traceability.
6. Assembly: constraint and ordering behavior.

## Reproducibility Link

Observability design must support deterministic replay checks:

1. Same input + same config => same output.
2. Differences across runs must be explainable from recorded config/data/version changes.

## Evaluation Alignment

Observability evidence in Chapter 4 should verify:

1. Trace completeness against required schema.
2. Diagnostic usefulness for explaining outcomes.
3. Replayability support from stored run records.

## Risks and Mitigations

1. Risk: Missing stage logs break audit chain.
	- Mitigation: required-field validation before run finalization.
2. Risk: Excessive log detail harms readability.
	- Mitigation: keep layered logs (summary plus deep trace).
3. Risk: Inconsistent identifiers across artifacts.
	- Mitigation: enforce run_id and track_id linkage rules.

## Boundary Note

This observability design supports thesis-level inspectability and reproducibility claims for a deterministic MVP. It does not attempt full production monitoring or real-time operations analytics.

