# Controllability Design

DOCUMENT STATUS: implementation-synchronized controllability design
LAST SYNCHRONIZED: 2026-04-19 UTC
ROLE: controllability architecture aligned to BL-004 through BL-011, BL-013, and BL-014

## 1) Purpose
Define how intentional control changes are represented, executed, measured, and validated.

## 2) Design Goal
Changing a declared control should produce interpretable downstream evidence on the expected stage surfaces, with bounded deterministic claims.

## 3) Architecture Components
1. Control declaration and metadata:
	`run_config/control_registry.py` (`control-registry-v1`).
2. Stage execution and traceability:
	BL-013 orchestration summary (`stage_execution`).
3. Scenario-based controllability evidence:
	BL-011 scenario matrix/report and `interaction_coverage_summary`.
4. Contract validation and evidence integrity:
	BL-014 gate/advisory checks and handshakes.

## 4) Implemented Scenario Model
BL-011 executes baseline + bounded scenarios across profile/retrieval/scoring/playlist layers and emits:
1. Scenario rows (per run/scenario).
2. Matrix summary rows.
3. Interaction coverage summary (single-factor vs interaction coverage).

## 5) Primary Control Families with Strong Evidence
1. Retrieval thresholds and candidate keep criteria (BL-005).
2. Scoring component weights and scoring behavior controls (BL-006).
3. Assembly size/threshold/utility controls (BL-007).

## 6) Evidence Linkage
1. BL-005/BL-007 diagnostics propagate into BL-009 run summaries.
2. BL-010 replay context constrains interpretation of controllability claims.
3. BL-014 checks enforce that stage boundaries and required fields remain valid.

## 7) Known Issues and Limits
1. Some controls are strongly context-dependent and can show weak effect in saturated candidate pools.
2. BL-007 rule order is fixed, limiting controllability to parameter-level adjustments.
3. Influence-related controls are present but can be weaker than threshold/weight controls.
4. Claims remain bounded to deterministic single-user execution conditions.
