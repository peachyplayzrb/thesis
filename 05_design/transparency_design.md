# Transparency Design

DOCUMENT STATUS: implementation-synchronized transparency design
LAST SYNCHRONIZED: 2026-03-29 UTC
ROLE: base transparency architecture aligned to BL-008 and BL-009 behavior

## Purpose
Define how the playlist pipeline exposes decision logic in a faithful, inspectable, and thesis-defensible way.

## Design Goal
Ensure recommendation outputs can be traced to explicit feature inputs, scoring contributions, and rule adjustments, rather than explained only through post-hoc narrative.

## Scope Position

- Single-user deterministic pipeline.
- Transparency-by-design, not interface-only explanation.
- Focus on mechanism visibility within MVP constraints, not universal explanation usability claims.

## Transparency Requirements (Implemented Expectations)

1. Explanations must be generated from actual scoring and assembly artifacts.
2. Each recommended track must expose core score contributors.
3. Rule-based adjustments (for example diversity/order effects) must be visible.
4. Intermediate outputs must be retained enough to support audit and debugging.
5. Uncertainty boundaries (for example unmatched tracks) must be explicitly surfaced.

## Mechanism Design

### Score Decomposition
- Represent final score as an additive or otherwise decomposable structure.
- Store component-level values per candidate (base similarity, weight effects, rule deltas).

### Explanation Artifacts
- BL-008 explanation payloads include per-track contributor surfaces, score breakdown fields, and concise `why_selected` rationale.
- Explanations are derived from BL-006 score outputs and BL-007 assembly context, not generated heuristically after the fact.

### Assembly Transparency
- BL-007 trace/report surfaces provide rule outcomes and exclusion categories used by BL-008 and BL-009.
- BL-009 aggregates assembly diagnostics into run-level observability context.

## Implemented Transparency Surfaces

### BL-008 Explanation Layer
1. Per-track explanation payloads with:
- playlist position and track identity,
- final score and contributor ranking,
- score breakdown,
- primary explanation driver,
- assembly context linkage.

2. Explanation summary with run metadata and provenance context.

### BL-009 Observability Layer
1. Run-level diagnostics aggregation across BL-003 to BL-008.
2. Config provenance and stage-level diagnostic surfaces.
3. Artifact hashing and integrity metadata.

## Dependency Notes
1. BL-008 depends on BL-006 scored-candidate field contracts and BL-007 assembly artifacts.
2. BL-009 depends on required artifact surfaces from BL-003 through BL-008.
3. Transparency and observability are coupled through artifact lineage, not inline recomputation.

## Known Limitations (Current Implementation)
1. Unified per-track control-causality blocks are not emitted.
2. Counterfactual what-if explanations are not emitted.
3. Influence-track effect attribution is not surfaced as a dedicated explanation contract.
4. BL-005 threshold-attribution explanations are partial rather than fully causal.

## Future Work (Optional, Out of Current Scope)
1. Add explicit control-causality contracts at track and stage levels.
2. Add counterfactual explanation surfaces for major control families.
3. Add stronger influence-effect attribution contracts when effect strength is measurably stable.

## Evaluation Alignment

Transparency evidence in Chapter 4 should verify:

1. Explanation fidelity: explanation values match scoring artifacts.
2. Trace completeness: required score/rule fields are present for tested runs.
3. Debuggability: recommendation anomalies can be diagnosed from stored traces.

## Risks and Mitigations

1. Risk: Explanation drift from mechanism.
	- Mitigation: build explanations directly from score-trace objects.
2. Risk: Overly technical explanations for users.
	- Mitigation: keep dual-layer output (structured trace plus readable summary).
3. Risk: Partial logging undermines auditability.
	- Mitigation: enforce required trace schema per run.
4. Risk: Overstating transparency coverage.
	- Mitigation: keep known limitations explicit in design and evaluation claims.

## Boundary Note

This design supports transparency and inspectability claims for a deterministic MVP. It does not claim that explanation style is optimal for all user populations.
