# Control Testing Protocol

DOCUMENT STATUS: implementation-synchronized
LAST SYNCHRONIZED: 2026-04-19 UTC
ROLE: repeatable method for control-effect validation under active pipeline contracts

## 1) Purpose
Define how to test whether a declared control produces observable and attributable downstream changes.

## 2) Testing Principle
Use baseline vs treatment comparisons with one bounded control change at a time, fixed inputs, and fixed non-target controls.

## 3) Canonical Test Workflow
1. Baseline run:
	Execute BL-013 with fixed run config and capture all generated artifacts.
2. Treatment run:
	Apply one control delta and rerun BL-013.
3. Control-effect interpretation:
	Use BL-011 scenario evidence where the control family is covered.
4. Contract integrity:
	Run BL-014 and ensure no blocking handshake/gate failure invalidates interpretation.

## 4) Evidence Surfaces by Stage
1. BL-013: `stage_execution`, stage status rows, execution context.
2. BL-005: candidate decision diagnostics and `candidate_shaping_fidelity`.
3. BL-006: score distributions and component contribution surfaces.
4. BL-007: assembly diagnostics and `tradeoff_metrics_summary`.
5. BL-008: explanation fidelity fields (`score_breakdown`, `causal_driver`, `assembly_context`).
6. BL-009: run-level summaries (`control_registry_snapshot`, `playlist_tradeoff_summary`, cross-stage summaries).
7. BL-010: replay verdict (`deterministic_match`) and interpretation bounds.
8. BL-011: scenario matrix and `interaction_coverage_summary`.
9. BL-014: gate/advisory status and contract continuity checks.

## 5) Effect Classification
1. Strong directional effect:
	Expected metrics move in planned direction with stable contract validity.
2. Weak directional effect:
	Change is present but small, noisy, or context-limited.
3. No observable effect:
	No measurable difference on expected surfaces.
4. Invalid comparison:
	Handshake/gate failures or run inconsistency prevent valid interpretation.

## 6) Required Report Fields
1. Control name and previous/new values.
2. Intended directional effect and target surface.
3. Observed changes on each checked surface.
4. BL-014 gate/advisory posture.
5. Bounded claim statement (explicitly non-universal).

## 7) Known Pitfalls
1. Multi-control changes can create false attribution.
2. Missing BL-014 checks can mask invalid evidence.
3. Candidate pool saturation can flatten apparent control effects.
