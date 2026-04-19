# Transparency Specifications

DOCUMENT STATUS: implementation-synchronized specification
LAST SYNCHRONIZED: 2026-04-19 UTC
ROLE: stage-level transparency contract summary for active implementation

## 1) Purpose
Define transparency-relevant outputs required at each stage for auditability and chapter-facing evidence continuity.

## 2) Stage-Level Transparency Contracts

### BL-004 Profile
Required outputs:
1. Profile summary and uncertainty-related diagnostics.
2. Seed trace carrying confidence-bearing context.

### BL-005 Retrieval
Required outputs:
1. Candidate decision rows (keep/reject reasoning surface).
2. `candidate_shaping_fidelity` diagnostics.

### BL-006 Scoring
Required outputs:
1. Component-level score diagnostics.
2. Structured scored candidate fields consumed downstream.

### BL-007 Assembly
Required outputs:
1. Assembly trace rows and report diagnostics.
2. `tradeoff_metrics_summary` in assembly report.

### BL-008 Transparency
Required per-track fields:
1. `why_selected`
2. `top_score_contributors`
3. `score_breakdown`
4. `assembly_context`
5. `causal_driver`
6. `narrative_driver`

### BL-009 Observability
Required run-level fields:
1. `control_registry_snapshot`
2. `playlist_tradeoff_summary`
3. `cross_stage_influence_attribution_summary`
4. `validity_boundaries.reproducibility_interpretation`

### BL-010 Reproducibility
Required bounded-claim field:
1. `interpretation_boundaries`

### BL-013 Orchestration
Required execution-trace field:
1. `stage_execution`

### BL-014 Sanity
Required integrity checks:
1. BL-008 to BL-009 handshake checks.
2. Explanation-fidelity advisories/gates.
3. Policy-backed transparency/control-causality gate surfaces.

## 3) Policy Convention
Where implemented, contract severity is policy-normalized:
1. `allow`
2. `warn`
3. `strict`

## 4) Known Transparency Issues
1. Counterfactual rerun explanation outputs are not fully active.
2. Rejected-path causal completeness is partial.
3. Explanation fidelity does not imply universal user trust outcomes.
