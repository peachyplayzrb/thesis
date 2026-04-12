# Requirements To Design Map

DOCUMENT STATUS: REB-M2 objective-anchored design traceability map
LAST SYNCHRONIZED: 2026-04-12 UTC
CONFIDENCE: medium-high for objective-to-design mapping, medium for implementation readiness boundaries
ROLE: requirement-to-design and design-to-evidence bridge

## 1) Objective to Design Requirement Traceability

| Objective | Design Requirement | Design Mechanism Class | Required Evidence Contract | Status |
| --- | --- | --- | --- | --- |
| O1 Uncertainty-aware profiling | Profile assumptions and source reliability must be inspectable | Profile confidence metadata, source coverage, interaction attribution | Profile uncertainty/coverage outputs and diagnostics are emitted | Design locked |
| O2 Confidence-aware alignment and candidate generation | Alignment confidence and exclusion logic must be explicit | Confidence-aware matching and retrieval exclusion tracing | Alignment/retrieval artifacts include confidence and exclusion reason fields | Design locked |
| O3 Controllable trade-offs in scoring and assembly | Coherence/diversity/novelty/ordering trade-offs must be tunable and bounded | Deterministic control surfaces in scoring and playlist assembly | Parameter-change experiments show directional output shifts | Design locked |
| O4 Mechanism-linked explanations and observability | Explanations must correspond to actual mechanism behavior | Contribution-grounded explanation payloads plus run observability logs | Explanation fields and observability logs map back to mechanism-level inputs | Design locked |
| O5 Reproducibility and controllability evaluation | Runs must be replayable and control-actuation effects measurable | Explicit config/payload contracts and run provenance | Reproducibility and controllability checks runnable from declared artifacts | Design locked |
| O6 Bounded design guidance | Claims must state validity limits and uncertainty boundaries | Scope/assumption/limitation-aware reporting contract | Results include bounded claims and explicit failure/limit reporting | Design locked |

## 2) Requirement to Stage Responsibility Map

| Stage Surface | Primary Design Responsibility | Linked Objectives |
| --- | --- | --- |
| BL-003 Alignment | Cross-source matching confidence and exclusion traceability | O2, O5 |
| BL-004 Profile | Uncertainty-aware profile construction and inspectable assumptions | O1, O4 |
| BL-005 Retrieval | Confidence-aware candidate shaping and rejection diagnostics | O2, O3 |
| BL-006 Scoring | Deterministic trade-off weighting and contribution traceability | O3, O4 |
| BL-007 Playlist | Deterministic assembly controls for quality trade-offs | O3, O5 |
| BL-008 Transparency | Mechanism-linked explanation payload emission | O4, O6 |
| BL-009 Observability | Run-level provenance, diagnostics, and contract traceability | O4, O5, O6 |

## 3) Design-to-Evaluation Contract Map

| Evaluation Theme | Required Design Instrumentation | Pass Condition Type |
| --- | --- | --- |
| Reproducibility | Deterministic control resolution, run config capture, artifact lineage | Same input/config yields stable outputs within declared contract |
| Controllability | Explicit control knobs with directional-effect diagnostics | Planned parameter deltas produce observable and attributable output shifts |
| Transparency fidelity | Contribution-level and rule-level mechanism traces | Explanation claims can be traced to generated mechanism fields |
| Uncertainty visibility | Confidence and exclusion diagnostics at alignment/profile/retrieval surfaces | Uncertainty is represented explicitly, not inferred post hoc |
| Bounded guidance quality | Scope and failure-boundary reporting contract | Claims include where results hold and where evidence is limited |

## 4) Active Assumptions (Rebuild)
1. Deterministic single-user scope remains the valid boundary for this thesis artefact.
2. Cross-source uncertainty handling is addressed through explicit confidence and exclusion signaling rather than probabilistic model-family expansion.
3. Evidence quality depends on explicit control/evidence contracts, not only on output quality metrics.

## 5) Known Open Risks for REB-M3 Transition
1. Control-causality can drift if control intent/effect/diagnostic linkage is not kept one-to-one.
2. Explanation fidelity can drift if explanation fields are decoupled from scoring/assembly mechanisms.
3. Artefact scope can drift if implementation introduces undeclared defaults or out-of-scope adaptation logic.

## 6) Governance Linkage
1. Design authority: `05_design/chapter3_information_sheet.md`.
2. Rebuild posture authority: `00_admin/thesis_state.md` and `00_admin/timeline.md`.
3. Decision and change anchors for this lock: `00_admin/decision_log.md` and `00_admin/change_log.md`.

Update this map whenever objective wording, stage ownership, or evaluation evidence contracts change.
