DOCUMENT STATUS: rebuilt Chapter 3 design-control blueprint (REB-M2 lock)
CONFIDENCE: medium-high
ROLE: objective-to-design and evidence-contract authority
SOURCE: REB-M1 locked RQ/objectives + confirmed Chapter 2 tensions (2026-04-12)

# Chapter 3 Information Sheet
System Design and Architecture (Rebuild Lock)

## Active Thesis Title
Engineering an Auditable and Controllable Playlist Generation Pipeline Under Cross-Source Preference Uncertainty

## Active Research Question
How can a deterministic playlist generation pipeline be engineered and evaluated so that preference inference, candidate generation, and playlist assembly remain transparent, controllable, and reproducible under cross-source uncertainty and multi-objective playlist trade-offs?

## Chapter 3 Purpose in Rebuild Posture
Chapter 3 translates Chapter 2 contradictions into design requirements, control surfaces, and evidence contracts. It defines what will be built and what must be measurable before implementation restarts. It does not claim implementation success.

## Design Methodology Position
- Design Science Research with a reconstruction flow: Chapter 2 tensions -> objectives -> design requirements -> implementation contracts -> evaluation evidence.
- Deterministic, single-user scope remains explicit and bounded.
- Contribution emphasis is auditable engineering behavior, not model-family novelty.

## Objective-Derived Design Requirements
### O1: Uncertainty-aware preference profiling
- Requirement: profile construction must represent source-specific uncertainty and assumption strength.
- Design response: profile outputs include source coverage, confidence bins, interaction attribution, and explicit uncertainty metadata.

### O2: Confidence-aware alignment and candidate generation
- Requirement: alignment and filtering must expose confidence and exclusion logic.
- Design response: alignment and retrieval surfaces emit traceable confidence signals and exclusion reasons usable in diagnostics.

### O3: Controllable scoring and assembly trade-offs
- Requirement: coherence, diversity, novelty, and ordering trade-offs must be explicit and tunable.
- Design response: deterministic scoring and playlist assembly expose bounded control parameters with clear behavioral intent.

### O4: Mechanism-linked explanations and run observability
- Requirement: explanations must map to actual scoring/assembly mechanisms and be distinguishable from persuasive narrative.
- Design response: explanation payloads are generated from mechanism-level contributions; observability logs capture stage-level control and artifact lineage.

### O5: Reproducibility and controllability evaluation readiness
- Requirement: design must support repeatable reproducibility and controllability testing without hidden defaults.
- Design response: configuration, payload handoff, and run metadata contracts are explicit and versioned.

### O6: Bounded design guidance
- Requirement: outputs must support defensible guidance with clear validity boundaries.
- Design response: design documents define scope limits, known uncertainty boundaries, and failure-reporting expectations.

## Rebuilt Layered Architecture (Control-Centric)
1. Input and Scope Layer: user data scope selection, ingestion provenance, and input assumptions.
2. Alignment and Confidence Layer: cross-source matching, confidence signaling, exclusion traceability.
3. Preference Profiling Layer: deterministic profile construction with inspectable uncertainty diagnostics.
4. Candidate Shaping Layer: confidence-aware filtering and pool-quality diagnostics.
5. Scoring Layer: deterministic scoring with explicit objective-trade-off controls.
6. Playlist Assembly Layer: constrained optimization of diversity/coherence/novelty/ordering under deterministic rules.
7. Explanation Layer: mechanism-linked explanation artifacts and rationale traces.
8. Observability Layer: run-level diagnostics, control snapshots, and artifact hash/index linkage.
9. Evaluation Contract Layer: reproducibility/controllability experiment hooks and reportable metrics.

## Control Surface Contract
- Every exposed control must have: intent, expected directional effect, and observable evidence field.
- Control resolution order must be deterministic and documented.
- Hidden behavior via undeclared defaults is not accepted in active rebuild posture.

## Evidence Contract (Design-Level)
- Reproducibility evidence: repeated-run consistency under fixed inputs/config.
- Controllability evidence: measurable output shift under controlled parameter change.
- Transparency evidence: explanation fields trace to mechanism-level contributions and rule effects.
- Uncertainty evidence: confidence/coverage signals and exclusion diagnostics are emitted for relevant stages.

## Chapter 3 Output Boundaries
- In scope: deterministic single-user architecture, uncertainty signaling, control surfaces, evidence contracts.
- Out of scope: collaborative/deep model novelty, large-scale user studies, claims beyond bounded evidence.

## Diagram Plan (Rebuild)
- Figure 3.1: Objective-to-design traceability map (O1 to O6).
- Figure 3.2: Deterministic pipeline with confidence and control overlays.
- Figure 3.3: Evidence contract flow (controls -> outputs -> evaluation claims).
- Figure 3.4: Uncertainty and exclusion trace path from alignment to explanation.

## Control Rule
Treat this sheet as the active Chapter 3 design authority for REB-M2. Implementation restart decisions must reference these requirements and evidence contracts.
