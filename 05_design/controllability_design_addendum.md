# Controllability Design Addendum

DOCUMENT STATUS: implementation-synchronized addendum
LAST SYNCHRONIZED: 2026-04-19 UTC
ROLE: current findings and practical constraints supplementing `controllability_design.md`

## 1) Purpose
Capture current controllability behavior and document observed practical limits for interpretation.

## 2) Confirmed Implemented Strengths
1. BL-011 bounded scenario execution is active and emits interaction-coverage evidence.
2. BL-013 `stage_execution` gives explicit requested vs executed stage traceability.
3. BL-014 policy-backed checks make control-contract quality visible (advisory/gate surfaces).

## 3) Confirmed Evidence Linkage
1. BL-005 candidate-shaping diagnostics feed into BL-009 run-level summaries.
2. BL-007 tradeoff metrics feed into BL-009 `playlist_tradeoff_summary`.
3. BL-009 carries `control_registry_snapshot` for run-level control authority traceability.

## 4) Practical Issue Analysis
1. Influence controls:
	Observable but commonly weaker than threshold/weight controls in many runs.
2. Context sensitivity:
	Control effect magnitude can vary by candidate pool shape and stage preconditions.
3. Fixed policy order in BL-007:
	Parameter controls are available, but policy ordering is not dynamic.
4. Partial causal coverage:
	Cross-stage rejected-path causality is present but not exhaustive.

## 5) Guidance for Chapter Claims
1. Use BL-011 + BL-013 + BL-014 together for defensible controllability claims.
2. Explicitly label weak-effect results as context-limited rather than control failure.
3. Keep interpretation bounded to deterministic single-user conditions.
