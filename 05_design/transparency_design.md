# Transparency Design

## Purpose

Define how the playlist pipeline exposes decision logic in a faithful, inspectable, and thesis-defensible way.

## Design Goal

Ensure recommendation outputs can be traced to explicit feature inputs, scoring contributions, and rule adjustments, rather than explained only through post-hoc narrative.

## Scope Position

- Single-user deterministic pipeline.
- Transparency-by-design, not interface-only explanation.
- Focus on mechanism visibility within MVP constraints, not universal explanation usability claims.

## Transparency Requirements

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
- Per-track explanation object includes:
  - selected feature contributors,
  - component values,
  - rule adjustments,
  - final rank position.
- Explanations are derived from run artifacts, not regenerated heuristically afterward.

### Assembly Transparency
- Playlist-level rules are logged with pass/fail or applied-adjustment outcomes.
- Final ordering rationale records major rule impacts where relevant.

## Data Structures (Conceptual)

1. `candidate_score_trace`
	- `track_id`
	- `base_similarity`
	- `feature_contributions`
	- `rule_adjustments`
	- `final_score`
2. `playlist_rule_trace`
	- `rule_name`
	- `rule_input`
	- `rule_outcome`
	- `affected_tracks`
3. `explanation_payload`
	- `track_id`
	- `why_selected`
	- `top_contributors`
	- `applied_rules`

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

## Boundary Note

This design supports transparency and inspectability claims for a deterministic MVP. It does not claim that explanation style is optimal for all user populations.

