# Controllability Design

## Purpose

Define how users can intentionally influence playlist outcomes through explicit, bounded, and testable controls.

## Design Goal

Operationalize controllability as measurable cause-effect behavior: changing a control should produce interpretable downstream changes in candidate selection, scoring, or playlist assembly.

## Scope Position

- MVP control model is limited and explicit, not open-ended personalization.
- Controls are deterministic under fixed input and configuration.
- Emphasis is on evaluable influence, not maximizing number of controls.

## Control Surfaces

1. Influence tracks (manual preference steering).
2. Feature-weight parameters (profile-to-candidate similarity emphasis).
3. Candidate filtering thresholds (pool shaping before scoring).
4. Playlist assembly constraints (length, diversity, repetition, ordering limits).

## Control Design Principles

1. Controls must be semantically clear and documented.
2. Controls must be bounded to prevent unstable behavior.
3. Control location in pipeline must be explicit (pre-score, score, post-score).
4. Control values must be persisted in run configuration.
5. Each control should map to at least one measurable output effect.

## Parameter Governance

### Baseline Profile
- Define one default configuration for reproducible baseline runs.

### Variation Strategy
- Use one-factor-at-a-time sensitivity checks for Chapter 4.
- Keep non-target parameters fixed during each test.

### Valid Ranges
- Document allowed range and interpretation for each parameter.
- Reject or clamp invalid values at execution time.

## Control-to-Effect Mapping (Conceptual)

1. `influence_tracks` -> preference profile shift -> candidate ranking differences.
2. `feature_weights` -> similarity composition shift -> score/rank differences.
3. `candidate_thresholds` -> candidate pool size/composition changes.
4. `assembly_rules` -> playlist structure and sequence differences.

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

## Boundary Note

This design demonstrates controllability as an engineering property within single-user deterministic scope. It does not claim universally optimal control UX for all user types.

