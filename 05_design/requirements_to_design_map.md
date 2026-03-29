# Requirements To Design Map

DOCUMENT STATUS: implementation-synchronized traceability map
LAST SYNCHRONIZED: 2026-03-29 UTC
CONFIDENCE: high for design-to-implementation mapping, medium for literature-strength grading
ROLE: requirement-to-design-to-implementation bridge

## 1) Requirement to Mechanism Traceability

| Requirement Theme | Design Requirement | Implemented Mechanism | Primary Stage Surface | Status |
| --- | --- | --- | --- | --- |
| Transparency | Recommendation process must be inspectable | Deterministic scoring plus per-track explanation payloads | BL-006 and BL-008 | Implemented (partial causal depth) |
| Controllability | Users can influence recommendation behavior through bounded controls | Run-config/env control surfaces across retrieval, scoring, and assembly | BL-005, BL-006, BL-007 | Implemented (partial in effect strength) |
| Playlist quality beyond ranking | Playlist-level constraints and sequencing needed | Rule-based assembly with threshold and diversity constraints | BL-007 | Implemented |
| Cross-source alignment reliability | Source events must map into candidate corpus | Alignment pipeline with source-scope and matching strategies | BL-003 | Implemented (known unmatched-rate boundary) |
| Reproducibility/observability | Runs must be replayable and auditable | Config provenance, stage diagnostics, artifact hashing, observability log | BL-009 (+ BL-010/BL-011 evaluation layers) | Implemented |

## 2) BL Stage Coverage Map

| BL Stage | Design Role | Key Requirement Contribution |
| --- | --- | --- |
| BL-003 Alignment | Source normalization and seed construction | Data reliability and inspectable matching lineage |
| BL-004 Profile | Preference signal aggregation | Interpretable profile representation |
| BL-005 Retrieval | Candidate filtering | Controlled pool shaping and rejection traceability |
| BL-006 Scoring | Deterministic relevance scoring | Faithful contribution-level decision basis |
| BL-007 Playlist | Constraint-based assembly | Playlist-level quality constraints |
| BL-008 Transparency | Explanation payload generation | Human-readable, score-grounded justification |
| BL-009 Observability | Run-level audit aggregation | End-to-end traceability and reproducibility evidence |

## 3) Requirement Fulfillment Posture
1. Transparency: implemented with score-grounded explanations; limited by missing counterfactual and full control-causality surfaces.
2. Controllability: implemented via stage controls; influence-track effect remains weak in current behavior.
3. Reproducibility: implemented via deterministic pipeline behavior and run-level provenance/hashing.
4. Observability: implemented via BL-009 aggregated diagnostics and required artifact contracts.
5. Playlist quality controls: implemented through BL-007 constraints with partial control-policy tunability.

## 4) Design Assumptions Still in Force
1. Deterministic recommendation behavior is preferred for inspectability and reproducibility goals.
2. Single-user scope is sufficient for thesis artefact evaluation goals.
3. Candidate-side features and metadata are sufficient for controllability/transparency evaluation in scope.

## 5) Known Requirement Gaps
1. Control-causality requirement is only partially satisfied (no unified per-track causal contract).
2. Influence-track controllability requirement is partially satisfied (weak measured effect).
3. Counterfactual explanation requirement is not implemented.

## 6) Evidence and Governance Linkage
Implementation-consistency references:
1. Architecture baseline: `05_design/architecture.md`.
2. Control posture source: `07_implementation/CONTROL_SURFACE_REGISTRY.md`.
3. Transparency posture source: `07_implementation/TRANSPARENCY_SPEC.md`.

This map should be updated whenever stage ownership or required artifact contracts change.
