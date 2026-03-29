# Explanation Design

DOCUMENT STATUS: implementation-synchronized explanation design
LAST SYNCHRONIZED: 2026-03-29 UTC
ROLE: BL-008 explanation architecture reference

## 1) Purpose
Define how explanation payloads are generated from scoring and assembly artifacts, and what explanation guarantees/limits are currently implemented.

## 2) Design Goal
Provide deterministic, faithful explanation payloads that are directly derived from BL-006 score components and BL-007 assembly context.

## 3) Implemented Explanation Surface (BL-008)
Stage surface: `src/transparency`.

Inputs:
1. BL-006 scored candidates.
2. BL-007 playlist payload.
3. BL-007 assembly trace/report context.
4. BL-008 explanation runtime controls.

Outputs:
1. `bl008_explanation_payloads.json` (per-track explanations).
2. `bl008_explanation_summary.json` (run metadata and provenance context).

## 4) Per-Track Payload Design
Each playlist track explanation is built from deterministic component contributions.

Core fields include:
1. playlist position and track identity.
2. final score and score rank context.
3. top score contributors.
4. full score breakdown.
5. primary explanation driver.
6. concise `why_selected` rationale text.
7. joined assembly context from BL-007 traces.

## 5) Explanation Runtime Controls
Implemented control knobs include:
1. top contributor limit.
2. near-tie primary-contributor blending behavior.
3. primary-contributor tie delta threshold.

These controls shape explanation presentation while preserving deterministic derivation from scoring outputs.

## 6) Faithfulness Boundaries
Implemented:
1. Explanation values originate from emitted scoring contributions.
2. Assembly context is sourced from BL-007 traces/reports.
3. Payload generation is deterministic for fixed inputs and controls.

Not implemented:
1. Counterfactual what-if explanation generation.
2. Unified per-track control-causality mapping linking user control values to each selection outcome.
3. Dedicated influence-track effect explanation contract.

## 7) Dependency and Compatibility Notes
1. BL-008 assumes BL-006 scored candidate field contracts remain stable.
2. BL-008 assumes BL-007 playlist and trace artifacts are available and schema-compatible.
3. BL-009 consumes BL-008 payload and summary outputs for run-level observability.

## 8) Quality and Evaluation Alignment
Explanation design supports thesis evaluation goals by:
1. exposing score-contribution transparency for selected tracks,
2. preserving deterministic traceability between score computation and explanation payloads,
3. enabling downstream observability aggregation.

## 9) Boundary Statement
This design prioritizes faithful deterministic explanation payloads for thesis inspection. It does not claim full causal explanation of all control effects or user-facing counterfactual guidance.
