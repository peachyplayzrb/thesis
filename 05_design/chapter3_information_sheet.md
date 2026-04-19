DOCUMENT STATUS: implementation-synchronized Chapter 3 design-control blueprint
LAST SYNCHRONIZED: 2026-04-19 UTC
CONFIDENCE: high for stage ownership and evidence surfaces
ROLE: objective-to-design and design-to-implementation authority bridge
SOURCE: `08_writing/chapter3.md`, `07_implementation/src/*`, `00_admin/thesis_state.md`

# Chapter 3 Information Sheet
System Design and Architecture (Active Baseline)

## 1) Locked Thesis Definitions

### Active Thesis Title
Designing and Evaluating a Transparent and Controllable Playlist Generation Pipeline Using Cross-Source Music Preference Data

### Active Research Question
How can a deterministic playlist generation pipeline be designed and evaluated so that it remains transparent, controllable, and reproducible when user preference data and candidate tracks come from different sources?

## 2) Chapter 3 Role in the Current Repo
Chapter 3 defines intended design properties and evidence contracts. In current posture, those contracts are realized through explicit stage outputs and final contract validation in BL-014.

## 3) Objective-to-Implementation Mapping
1. O1 Uncertainty-aware profiling:
	BL-003 and BL-004 emit confidence, coverage, and seed-trace surfaces.
2. O2 Confidence-aware alignment and candidate shaping:
	BL-003 matching diagnostics and BL-005 candidate decision diagnostics are explicit.
3. O3 Controllable scoring/assembly trade-offs:
	BL-006 and BL-007 expose deterministic controls and metrics.
4. O4 Mechanism-linked explanation/observability:
	BL-008 explanation payloads are sourced from BL-006/BL-007 fields; BL-009 aggregates run-level context.
5. O5 Reproducibility and controllability evaluation:
	BL-010, BL-011, BL-013, BL-014 provide replay, scenario, execution-trace, and integrity evidence.
6. O6 Bounded guidance:
	BL-010/BL-009 include interpretation-boundary surfaces and non-claim framing.

## 4) Active Stage Set (Implemented)
1. BL-003 Alignment
2. BL-004 Profile
3. BL-005 Retrieval
4. BL-006 Scoring
5. BL-007 Playlist
6. BL-008 Transparency
7. BL-009 Observability
8. BL-010 Reproducibility
9. BL-011 Controllability
10. BL-013 Orchestration
11. BL-014 Sanity

Note: BL-012 is intentionally unassigned in the active stage sequence.

## 5) Key Evidence Contracts in Code
1. BL-013 `stage_execution` summary metadata from `orchestration/summary_builder.py`.
2. BL-010 `interpretation_boundaries` from `reproducibility/main.py`.
3. BL-009 `control_registry_snapshot`, `playlist_tradeoff_summary`, and cross-stage summary fields from `observability/main.py`.
4. BL-014 policy-backed gate/advisory outputs from `quality/sanity_checks.py`.

## 6) Known Issues and Residual Risks
1. Influence effects exist but are often weaker/indirect than threshold/weight controls.
2. BL-007 rule ordering remains fixed in code (partial configurability).
3. Full rerun-level counterfactual explanation generation is not implemented.
4. Some control-causality tracing remains bounded rather than exhaustive.

## 7) Contribution Boundary
Deterministic, single-user, inspectable engineering behavior under cross-source uncertainty. No universal claim of recommendation superiority across model families or populations.
