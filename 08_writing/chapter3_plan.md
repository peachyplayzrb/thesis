# Chapter 3 Plan (Design-To-Implementation Bridge)

Document status: active planning note  
Date: 2026-03-15  
Owner: AI + Tim

## 1) Planning Goal
Produce a freeze-ready Chapter 3 that:
- translates Chapter 2 conclusions into concrete architecture decisions,
- keeps design claims methodologically disciplined (design hypothesis, not validated outcome),
- creates a clean handoff into Chapter 4 implementation and evaluation evidence.

Locked RQ reference:
What design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data?

## 2) Chapter 3 Role Boundary (Must Respect)
Chapter 3 is design and methodology, not results.
- Include: rationale, architecture, pipeline stages, controls, logging strategy, traceability.
- Exclude: empirical claims about final performance, success rates, or validated superiority.

Core wording rule:
- Use language such as "designed to", "intended to", "proposed".
- Avoid language such as "proved", "demonstrated", "outperformed" unless Chapter 4 evidence is cited.

## 3) Core Design Argument (One Sentence)
A deterministic, layered, and auditable playlist-generation pipeline is the most defensible architecture under this thesis scope because it operationalizes transparency, controllability, and observability as explicit engineering mechanisms.

## 4) Inputs To Anchor
Primary source inputs for this chapter:
- `05_design/chapter3_information_sheet.md`
- `08_writing/chapter2.md`
- `00_admin/decision_log.md`
- `00_admin/methodology_definition.md`
- `00_admin/thesis_state.md`
- `00_admin/Artefact_MVP_definition.md`
- `00_admin/evaluation_plan.md`

Planning requirement:
Every major Chapter 3 commitment should trace backward to Chapter 2 and forward to a Chapter 4 evidence artifact.

## 5) Section Blueprint (Writing Skeleton)
1. Methodological position and chapter role
- Re-state DSR flow and chapter purpose.
- Clarify design-hypothesis status.

2. Literature-derived design requirements
- Convert literature themes into requirement groups:
  inspectability, controllability, playlist constraints, alignment reliability, reproducibility.

3. Architecture overview
- Present layered deterministic pipeline and stage responsibilities.
- Add a simple end-to-end flow statement.

4. Input boundary, ingestion, and cross-source alignment
- Define ingestion scope and normalization assumptions.
- Specify ISRC-first plus metadata fallback and unmatched-track handling.

5. Preference profile and candidate preparation
- Describe profile construction and influence-track integration.
- Define candidate narrowing and explicit preprocessing choices.

6. Deterministic scoring design
- Specify metric/weight parameterization and score decomposition.
- Keep claims goal-aligned (inspectability/replayability rationale).

7. Playlist assembly design
- Separate assembly from ranking.
- Define explicit rules: length, repetition limits, diversity/ordering constraints.

8. Explanation, observability, and reproducibility controls
- Require mechanism-linked explanations and run-level artifacts.
- Define minimum run log contents.

9. Configuration and execution model
- Define saved configuration profile and controlled-variation protocol.
- Link directly to Chapter 4 testability.

10. Design traceability and chapter handoff
- Summarize commitments and map them to implementation/evaluation checks.

## 6) Figure And Table Plan
Minimum visual artifacts:
- Figure 3.1: Layered architecture overview.
- Figure 3.2: End-to-end pipeline flow.
- Figure 3.3: Alignment decision flow (ISRC-first fallback logic).
- Figure 3.4: Scoring plus assembly interaction.

Minimum tables:
- Table 3.1: Chapter 2 design consequence -> Chapter 3 design commitment mapping.
- Table 3.2: Requirement -> Architecture mechanism -> Planned Chapter 4 evidence artifact.

## 7) Chapter 4 Handoff Mapping (Must Be Explicit)
For each quality attribute, predeclare how it will be tested:
- Transparency: score contribution traces and explanation fidelity checks.
- Controllability: controlled parameter variation runs.
- Observability: log completeness and diagnostic visibility checks.
- Reproducibility: same-input same-config replay consistency checks.
- Rule compliance: playlist-rule adherence and violation reporting.

## 8) Claim Discipline Rules
- Keep deterministic design justified as objective-aligned, not universally superior.
- Acknowledge comparator context (hybrid/neural) without strawman framing.
- Label assumptions and known limitations in design language.
- Ensure all non-trivial claims remain citation-backed and traceable.

## 9) Execution Plan (Fast, Practical)
Step 1: Structure lock (single focused session)
- Confirm final section order and remove overlap across sections.
- Keep one clear purpose per section.

Step 2: Traceability pass (single session)
- Verify each section ends with a concrete design consequence.
- Ensure consequence is implementable and testable.

Step 3: Handoff hardening (single session)
- Add explicit links from Chapter 3 mechanisms to Chapter 4 evidence types.
- Confirm no design commitment lacks an evaluation path.

Step 4: Figures/tables pass (single session)
- Insert and caption required figures/tables.
- Ensure each figure/table is referenced and interpreted in text.

Step 5: Final discipline pass (single session)
- Remove result-like wording.
- Run citation/consistency checks and update quality-control logs.

## 10) Definition Of Done (Chapter 3 Ready)
- Chapter 3 is methodologically consistent with DSR and locked scope.
- Architecture stages are concrete enough to implement directly.
- Design commitments are traceable to literature and decision logs.
- Handoff to Chapter 4 is explicit and test-oriented.
- No outcome-overclaiming language remains.
- Required figures/tables are present, referenced, and interpreted.

## 11) Immediate Next Work Package
- Baseline chapter file: continue from `08_writing/chapter3_v2.md` as primary draft.
- Add Table 3.2 (requirement -> mechanism -> evidence artifact).
- Draft Figure 3.3 alignment flow and Figure 3.4 scoring-assembly interaction.
- Run chapter-level wording pass for design-only claim discipline.

## 12) Progress Update (2026-03-15)
- Completed: dedicated Chapter 3 planning baseline created and aligned to locked RQ.
- Completed: section blueprint synchronized with current Chapter 3 structure and architecture sheet.
- Completed: Chapter 4 handoff expectations made explicit as testable quality attributes.
- Current status: ready to execute writing hardening and visual artifact insertion pass on the Chapter 3 draft.
