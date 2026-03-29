# Controllability Design

DOCUMENT STATUS: implementation-synchronized controllability design
LAST SYNCHRONIZED: 2026-03-29 UTC
ROLE: base control architecture design aligned to BL-003 to BL-009

## Purpose
Define how users can intentionally influence playlist outcomes through explicit, bounded, and testable controls.

## Design Goal
Operationalize controllability as measurable cause-effect behavior: changing a control should produce interpretable downstream changes in candidate selection, scoring, or playlist assembly.

## Scope Position

- MVP control model is limited and explicit, not open-ended personalization.
- Controls are deterministic under fixed input and configuration.
- Emphasis is on evaluable influence, not maximizing number of controls.

## Control Surfaces (Implemented Architecture)

1. BL-003 scope and matching controls:
- Source scope selection and matching behavior controls shape seed construction.

2. BL-004 profile controls:
- Attribution and weighting controls govern profile aggregation behavior.

3. BL-005 retrieval controls:
- Semantic and numeric thresholds shape candidate pool composition.

4. BL-006 scoring controls:
- Component-weight and semantic/numeric strategy controls shape ranking behavior.

5. BL-007 assembly controls:
- Playlist size/threshold/diversity limits and assembly strategy options shape final playlist structure.

6. BL-008 and BL-009 presentation/diagnostic controls:
- Explanation and diagnostic depth controls shape transparency/observability granularity.

## Control Surface Status Summary
1. Working controls:
- Retrieval/scoring thresholds and weights are tunable and measurably affect outputs.
- Input scope and profile control surfaces are active and persisted through run-config-driven flow.

2. Partial controls:
- BL-007 assembly controls are partially configurable.
- Thresholds/limits and strategy knobs are tunable; rule order and some helper heuristics remain fixed.

3. Known weak control:
- Influence-track effect is currently weak and indirect in measured downstream behavior.

## Control Design Principles

1. Controls must be semantically clear and documented.
2. Controls must be bounded to prevent unstable behavior.
3. Control location in pipeline must be explicit (pre-score, score, post-score).
4. Control values must be persisted in run configuration.
5. Each control should map to at least one measurable output effect.

## Runtime Governance

### Baseline Profile
- Define one default configuration for reproducible baseline runs.

### Variation Strategy
- Use one-factor-at-a-time sensitivity checks for Chapter 4.
- Keep non-target parameters fixed during each test.

### Valid Ranges
- Document allowed range and interpretation for each parameter.
- Reject or clamp invalid values at execution time.

### Resolution Order
Controls should be interpreted using deterministic precedence:
1. CLI controls where orchestration supports explicit overrides.
2. Run-config controls.
3. Environment overrides.
4. Stage defaults.
5. Stage-specific sanitization/bounds enforcement.

## Control-to-Effect Mapping (Conceptual)

1. `profile_source_scope` -> ingestion/profile input composition change -> runtime and profile-signal differences.
2. `influence_tracks` -> preference profile shift -> candidate ranking differences.
3. `feature_weights` -> similarity composition shift -> score/rank differences.
4. `candidate_thresholds` -> candidate pool size/composition changes.
5. `assembly_rules` -> playlist structure and sequence differences.

## Current Known Gaps
1. Influence-track control does not consistently produce strong downstream playlist shifts.
2. BL-007 policy ordering is fixed despite expanded tunable control surface.
3. Unified per-track control-causality reporting is not implemented across stage outputs.

## Evaluation Alignment

Controllability evidence in Chapter 4 should verify:

1. Parameter sensitivity: targeted control changes yield non-trivial output changes.
2. Effect interpretability: observed changes align with expected mechanism path.
3. Stability: repeated runs with same config return same outputs.
4. Boundedness: controls do not cause invalid or untraceable states.

## Risks and Mitigations

1. Risk: Too many controls reduce usability.
	- Mitigation: prioritize small high-impact control set in MVP.
2. Risk: Controls exist but effects are weak or opaque.
	- Mitigation: require control-to-effect trace checks per run.
3. Risk: Parameter interactions mask causal interpretation.
	- Mitigation: use controlled variation protocol and log full config.
4. Risk: Overstating control completeness.
	- Mitigation: explicitly separate implemented, partial, and weak control surfaces.

## Boundary Note

This design demonstrates controllability as an engineering property within single-user deterministic scope. It does not claim universally optimal control UX for all user types.
