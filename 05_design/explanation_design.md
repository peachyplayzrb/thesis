# Explanation Design

DOCUMENT STATUS: implementation-synchronized explanation design
LAST SYNCHRONIZED: 2026-04-19 UTC
ROLE: BL-008 explanation architecture reference

## 1) Purpose
Define how explanation payloads are produced from scoring and assembly artifacts and how fidelity is validated.

## 2) Design Goal
Deliver deterministic, mechanism-linked explanations that are auditable against BL-006 score components and BL-007 assembly decisions.

## 3) Generation Path (Code-Level)
Primary modules:
1. `src/transparency/main.py`
2. `src/transparency/explanation_driver.py`

Primary flow:
1. Load/join scored candidates with playlist and assembly traces.
2. Build score breakdown and contributor ordering.
3. Select causal/narrative drivers.
4. Build human-readable `why_selected` text with mechanism inputs.
5. Emit payload and summary artifacts.

## 4) Required Payload Fields
1. `why_selected`
2. `top_score_contributors`
3. `score_breakdown`
4. `assembly_context`
5. `causal_driver`
6. `narrative_driver`

## 5) Validation and Contract Checks
1. BL-014 validates BL-008 to BL-009 handshake contracts.
2. BL-014 emits explanation-fidelity advisories/gates (policy dependent).
3. BL-009 includes run-level transparency context for downstream interpretation.

## 6) Known Issues and Risks
1. Full rerun-level counterfactual explanation generation is not active.
2. Narrative readability does not guarantee universal user trust/utility.
3. Rejected-path causal explanation coverage remains bounded.

## 7) Interpretation Boundary
Explanation outputs should be interpreted as faithful mechanism traces under deterministic conditions, not universal explanatory sufficiency guarantees.
