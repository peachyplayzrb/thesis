# Chapter 4 Plan (Implementation-to-Evaluation Bridge)

Document status: active planning note
Date: 2026-04-27
Owner: AI + Tim

## 1) Planning Goal
Produce a freeze-ready Chapter 4 that:
- translates Chapter 3 design commitments into concrete implementation realisation,
- shows where objective-linked evidence is produced at each pipeline stage,
- creates clean traceability from Chapter 3 design properties into Chapter 5 evaluation evidence,
- specifies what was implemented without pre-judging evaluation outcomes,
- establishes the evidence surfaces that Chapter 5 will formally assess.

Locked RQ reference:
How can a deterministic playlist generation pipeline be designed and evaluated so that it remains transparent, controllable, and reproducible when user preference data and candidate tracks come from different sources?

## 2) Chapter 4 Role Boundary (Must Respect)

Chapter 4 is implementation architecture and evidence surfaces, not evaluation.
- Include: design intent mapping, pipeline realisation, artefact production, evidence visibility, stage-to-output links.
- Exclude: success/failure judgments, claim that evidence meets quality criteria, performance rankings, comparative superiority statements.

Core wording rule:
- Use language such as "implemented", "emits", "surfaces", "records", "traces", "exposes".
- Avoid language such as "proves", "validates", "demonstrates", "shows quality" unless Chapter 5 evidence is cited.

## 3) Core Implementation Argument (One Sentence)

The pipeline implementation operationalizes the Chapter 3 design commitments through seven sequential stages (alignment, profiling, candidate shaping, scoring, assembly, explanation, and observability) plus two evaluation layers, such that design properties (transparency, controllability, reproducibility) remain visible as concrete evidence artefacts produced at each stage rather than remaining latent in the execution.

## 4) File Status and Version Decision

Two versions currently exist:

**chapter4.md** (742 words)
- Concise summary of stages and evidence artefacts
- High-level continuity mapping from Chapter 3 to Chapter 4
- Best for final condensed submission form

**chapter4_v2.md** (5,062 words)
- Detailed stage-by-stage design-to-implementation bridge
- Includes pipeline diagrams and decision-flow visuals
- Includes detailed evidence artefact specifications
- Stage-specific technology positioning and scope clarification
- Best for comprehensive documentation and handoff clarity

**Decision**: Use chapter4_v2.md as the primary working draft because:
1. It provides the detailed evidence mapping needed for Chapter 5 continuity
2. The stage diagrams and design-intent sections make traceability explicit
3. The detailed artefact specifications ground evaluation criteria
4. Comprehensive content allows selective trimming if word-count constraints require compression

If final word count requires compression, chapters 4-6 can be selectively trimmed after Chapter 5 and 6 are finalised.

## 5) Inputs To Anchor
Primary source inputs for this chapter:
- `08_writing/chapter3.md` (design commitments and architecture)
- `08_writing/chapter4_v2.md` (current detailed draft)
- `00_admin/thesis_state.md` (artefact definition, objectives O1-O6)
- `05_design/architecture.md` (technical architecture reference)
- `07_implementation/src/quality/outputs/` (actual artefact evidence)
- `09_quality_control/claim_evidence_map.md` (evidence-to-claim traceability)
- `00_admin/decision_log.md` (design decision history)

Planning requirement:
Every pipeline stage in Chapter 4 must link to at least one Chapter 3 design commitment (Section 3.x) and must specify the evidence artefacts that Chapter 5 will use to evaluate that commitment.

## 6) Section Blueprint (Aligned To chapter4_v2.md Structure)

### 4.1 Chapter Aim and Scope
- Re-state that Chapter 4 reports implementation realisation, not evaluation outcomes
- Clarify the deterministic single-user scope inherited from Chapter 3
- Position implementation as evidence-instrumented rather than only functionally staged

### 4.2 Design-to-Implementation Bridge
- Map each Chapter 3 design commitment to one implementation stage
- Explain technology positioning (local, inspectable, artefact-based)
- State implementation scope coverage (BL-003 through BL-011)
- Include high-level pipeline overview diagram

### 4.3 BL-003: Cross-Source Alignment and Evidence Intake
- Design intent from Chapter 3 Section 3.6
- Implementation realisation (evidence order, match classification)
- Evidence artefacts produced (bl003_ds001_spotify_summary.json)
- Diagnostics visibility (reason codes, match-rate statistics)

### 4.4 BL-004: Preference Profile Construction
- Design intent from Chapter 3 Section 3.7
- Profile structure realisation (semantic, numeric, attribution, uncertainty)
- Evidence artefacts (bl004_preference_profile.json)
- Uncertainty visibility in profile output

### 4.5 BL-005: Candidate Shaping and Retrieval
- Design intent from Chapter 3 Section 3.8
- Candidate-space definition and filtering logic
- Evidence artefacts (bl005_candidate_diagnostics.json)
- Explicit exclusion pathway tracking

### 4.6 BL-006: Deterministic Scoring
- Design intent from Chapter 3 Section 3.9
- Score component decomposition and active weights
- Evidence artefacts (bl006_score_summary.json)
- Traceability from feature inputs to component scores

### 4.7 BL-007: Playlist Assembly and Constraint Handling
- Design intent from Chapter 3 Section 3.10
- Assembly rules and trade-off logic
- Evidence artefacts (bl007_assembly_report.json)
- Constraint pressure and warning pathway visibility

### 4.8 BL-008: Explanation Fidelity and Mechanism-Linked Rationale
- Design intent from Chapter 3 Section 3.11
- Explanation payload structure and mechanism linking
- Evidence artefacts (bl008_explanation_payloads.json)
- Mapping from ranked outputs to scorer contributors

### 4.9 BL-009: Run-Level Observability and Validity Boundaries
- Design intent from Chapter 3 Section 3.12
- Observability log structure and execution traceability
- Evidence artefacts (bl009_run_observability_log.json)
- Validity-boundary reporting

### 4.10 BL-010 and BL-011: Evaluation Layers
- Reproducibility layer (BL-010): fixed-config replay and deterministic verification
- Controllability layer (BL-011): parameter-variation testing
- Evidence artefacts (reproducibility_report.json, controllability_report.json)

### 4.11 Run-Config Profile and Configuration Authority
- Configuration as methodological instrument
- Persistent run-config structure
- Links to reproducibility and controllability testing

### 4.12 Objective-Linked Tranche Gates
- Three REB-M3 gates linking local stage outputs to objective-level acceptance
- Gate reporting structure (reb_m3_tranche1/2/3_gate_report.json)
- How gates validate design property coverage

### 4.13 Evidence Packaging and Artefact Surface
- Complete inventory of evidence artefacts and their locations
- How local stage outputs feed into evaluation layers
- How tranche gates bind local evidence to thesis-wide design contract

### 4.14 Chapter Summary
- Restate that Chapter 4 establishes the implemented evidence surface
- Clarify that formal evaluation of these artefacts occurs in Chapter 5
- Summarise the design-to-implementation continuity and evidence visibility

## 7) Figure And Table Plan
Minimum visual artifacts (most already in chapter4_v2.md):
- Figure 4.1: Full pipeline sequence overview with config and evaluation-layer relationships
- Figure 4.2: BL-003 alignment decision flow (confident, ambiguous, unmatched, invalid)
- Figure 4.3: BL-004 profile structure (semantic, numeric, attribution, uncertainty layers)
- Figure 4.4: BL-006 score decomposition flow (component-to-composite)
- Figure 4.5: BL-007 assembly constraint interaction diagram
- Figure 4.6: BL-008 explanation payload structure (mechanism linking)

Minimum tables:
- Table 4.1: Chapter 3 design commitment → Chapter 4 implementation stage → Evidence artefact
- Table 4.2: Objective (O1-O6) → Corresponding implementation stages → Chapter 5 evaluation focus
- Table 4.3: Evidence artefact inventory (location, key fields, update frequency)

## 8) Chapter 5 Handoff Mapping (Must Be Explicit)

For each design property and objective, predeclare which Chapter 4 artefacts will be evaluated:

| Objective | Chapter 3 Commitment | Chapter 4 Evidence Surface | Chapter 5 Assessment Focus |
|-----------|---------------------|---------------------------|----------------------------|
| O1: Uncertainty-aware profiling | Section 3.7 | bl004_preference_profile.json + bl003 diagnostics | Uncertainty visibility, attribution clarity |
| O2: Confidence-aware alignment and candidate shaping | Sections 3.6, 3.8 | bl003_ds001_spotify_summary.json + bl005_candidate_diagnostics.json | Alignment confidence reporting, exclusion pathway clarity |
| O3: Controllable trade-offs | Sections 3.9, 3.10 | bl006_score_summary.json + bl007_assembly_report.json + run-config | Parameter sensitivity, constraint interaction |
| O4: Mechanism-linked explanation fidelity | Section 3.11 | bl008_explanation_payloads.json | Score attribution accuracy, contributor identification |
| O5: Reproducibility and controllability readiness | Throughout Chapter 3 | BL-010 and BL-011 outputs + deterministic verification metadata | Replay consistency, parameter-variation signal isolation |
| O6: Bounded-guidance surfaces | Sections 3.12, 3.10 | bl009_run_observability_log.json + BL-007 validity reporting | Boundary condition visibility, execution scope clarity |

## 9) Claim Discipline Rules

- Every claim about what was "implemented" must reference a specific artefact or code location
- Do not pre-judge whether evidence meets quality criteria (that is Chapter 5)
- Distinguish "was implemented" (Chapter 4) from "meets intended quality" (Chapter 5)
- Label limitations in implementation scope (e.g., "single-user scope", "offline track corpus", "local execution model")
- All non-trivial implementation decisions should trace to a decision log entry (D-###) or design document

## 10) Execution Plan (Fast, Practical)

**Step 1: Continuity Hardening (single session)**
- Read Chapter 3 end-to-end
- For each stage in Chapter 4, verify it maps to a Chapter 3 section
- Add explicit cross-references (e.g., "See Chapter 3 Section 3.7 for design intent")
- Check that no design commitment lacks an implementation section

**Step 2: Artefact Ground Truth Pass (single session)**
- Verify that all cited evidence artefact paths exist and contain expected fields
- Spot-check artefact samples to ensure descriptions match actual content
- Update any stale or incorrect path references
- Add actual JSON/CSV field names where specific data fields are discussed

**Step 3: Evidence-to-Evaluation Link Pass (single session)**
- For each artefact, explicitly state which Chapter 5 evaluation criterion will use it
- Add a reference table (Table 4.2 or equivalent) mapping objectives to Chapter 4 evidence
- Ensure no artefact is described without showing its evaluation purpose

**Step 4: Figures/Diagrams Pass (single session)**
- Verify all Mermaid diagrams render correctly
- Check that each figure is referenced and interpreted in adjacent text
- Add captions that explain what the figure shows and why it matters
- Ensure visual hierarchy and labeling are clear

**Step 5: Word-Count and Compression Assessment (single session)**
- Measure current chapter4_v2.md word count against target
- If over target, identify compression candidates (detailed stage sections, redundant explanations)
- Prioritise keeping design-intent explanations and evidence-artefact specifications (these are mandatory)
- Compress technical positioning details and repeated framing language if needed

**Step 6: Final Discipline and Quality Pass (single session)**
- Remove or downgrade any result-like language (e.g., "high quality", "successful", "best")
- Run citation consistency checks (if any)
- Check that all artefact names and paths use consistent naming
- Verify no design jargon is undefined or inconsistent with Chapter 1-3 terminology

## 11) Definition Of Done (Chapter 4 Ready)

- Chapter 4 maps each Chapter 3 design commitment to one implementation stage
- Each stage describes design intent, realisation, and evidence artefacts produced
- All cited evidence artefacts exist and descriptions match actual content
- Figures and tables are present, referenced, and interpreted
- Chapter 5 evaluation focus is explicit for each objective and artefact
- No outcome-overclaiming language remains (no "proves", "validates", "demonstrates quality")
- Continuity to Chapter 5 is clear and evidence-linked
- Chapter 4 is ready for Chapter 5 evaluation evidence review

## 12) Relative Version Comparison

| Aspect | chapter4.md | chapter4_v2.md |
|--------|-----------|----------------|
| Word count | 742 | 5,062 |
| Design-intent mapping | Summary table | Detailed per-stage |
| Diagrams | None | 6+ Mermaid diagrams |
| Stage detail | 1-2 sentences each | 4-6 sentences + artefact specs |
| Evidence artefact specs | Listed | Detailed with JSON field names |
| Technology positioning | Implicit | Explicit with methodology justification |
| Chapter 5 handoff clarity | Implicit | Explicit mapping table |
| Submission form | Condensed, ready | Comprehensive, may need trimming |

**Recommendation**: Use chapter4_v2.md as primary draft. If final word count budget requires compression (target: 8000-12000 words total for all 6 chapters; current total with v2: 15,761), selective trimming of stage-detail sections can occur after Chapter 5 and 6 are finalised and word budgets are clear.

## 13) Lean Blueprint for Thesis-Facing Chapter 4 (Word-Target + Prose Strategy)

This is your actual rewriting guide. It translates the plan into concrete section targets and narrative shapes.

**Overall Chapter 4 target: 3,500–4,000 words** (vs. current chapter4_v2.md 5,062)

### Section Targets and Prose Strategy

| Section | Role | Word Target | Prose Strategy | Key Output |
|---------|------|-------------|-----------------|-----------|
| 4.1 Aim & Scope | Framing | 200–250 | Positioning only; set boundaries clearly; no detail | Clear role statement |
| 4.2 Design-to-Implementation Bridge | Orientation | 300–400 | Explain technology positioning once; introduce the 7 stages; include pipeline diagram (Figure 4.1) | Diagram + clarity on why local/inspectable matters |
| 4.3 BL-003 Alignment | **DETAILED** | 450–550 | Full narrative: design intent → realisation → artefact; include Figure 4.2 (alignment flow); explain why uncertain matches matter | Complete foundation for rest of chapter |
| 4.4 BL-004 Profiling | **DETAILED** | 400–500 | Full narrative; explain profile structure and why attribution/uncertainty visibility matters | Sets profiling precedent |
| 4.5 BL-005 Candidate Shaping | **DETAILED** | 350–450 | Full narrative; emphasise explicit exclusion pathways; concise relative to 4.3–4.4 | Establishes candidate-space control |
| 4.6 BL-006 Scoring | **CORE** | 400–500 | Moderately detailed; design intent → score decomposition; brief on component logic; skip exhaustive parameter list | Component visibility |
| 4.7 BL-007 Assembly | **CORE** | 350–450 | Design intent → rule logic; constraint trade-offs explained; skip detailed config variants; brief figure (Figure 4.5) | Trade-off visibility |
| 4.8 BL-008 Explanation | **CORE** | 300–400 | Mechanism linking is central; design intent → payload structure; concise relative to alignment/profiling | Mechanism fidelity |
| 4.9 BL-009 Observability | **SYNTHESIS** | 250–350 | Run-level integration; validity boundaries; this is summary, not new detail | Execution completeness |
| 4.10 BL-010 & BL-011 Instrumentation | **BRIEF** | 200–250 | **Rename section heading**: "Reproducibility and Controllability Instrumentation" (not "Evaluation Layers"). Very disciplined: what they are, what they emit, why they matter for Chapter 5. No exhaustive detail. | Support for reproducibility claim |
| 4.11 Run-Config Profile | **TRIM HARD** | 100–150 | Mention only if central to your reproducibility argument. If yes: 100 words max on persistent config. If no: omit or move to appendix. | (optional) |
| 4.12 Objective-Linked Tranche Gates | **OPTIONAL/APPENDIX** | 0 or 150 | **Default**: Omit from main chapter. If your supervisor emphasised gates: 150 words max, positioned as internal consistency check (not thesis narrative). Otherwise: appendix or supplementary note. | (optional) |
| 4.13 Evidence Packaging | **CONTINUITY** | 200–250 | Concise inventory and Chapter 5 handoff. Keep table mapping O1–O6 to artefacts. No exhaustive artefact list. | Chapter 5 bridge |
| 4.14 Chapter Summary | **PUNCHY** | 100–150 | One short paragraph: Chapter 4 established the implemented evidence surfaces. Formal evaluation happens in Chapter 5. That's it. | Clean handoff |

**Column notes:**
- **Role**: Whether section builds detail, refines, synthesizes, or bridges
- **Word Target**: Tight range to keep total at 3,500–4,000
- **Prose Strategy**: How to write it so it doesn't sound templated
- **Key Output**: What a reader should take away

### Prose-Variation Rules (Avoid Repetition)

**Sections 4.3–4.5 (Alignment, Profiling, Candidate):**
- **Pattern**: Design intent → implementation realisation → artefact → uncertainty/diagnostics visible
- **Variation tactic**: Emphasise different *why* questions in each
  - 4.3: "Why does alignment matter? Because uncertainty enters here."
  - 4.4: "Why expose the profile? Because influence and attribution must be reviewable."
  - 4.5: "Why explicit exclusion? Because candidate-space decisions must be traceable."

**Sections 4.6–4.8 (Scoring, Assembly, Explanation):**
- **Pattern**: Moderately detailed but briefer than 4.3–4.5 (readers know the pattern now)
- **Variation tactic**: Focus on *mechanism linking* rather than full design narrative
  - 4.6: "Component decomposition ensures rankings stay traceable to named logic."
  - 4.7: "Assembly rules make trade-off pressure visible at the playlist level."
  - 4.8: "Explanation payloads map each selection back to scoring contributors."

**Section 4.9 (Observability):**
- **Tone shift**: Synthesis, not new stage detail
- **Framing**: "The observability layer consolidates evidence across all prior stages, making the full execution record inspectable."

### File Consolidation Decision

- **Archive or delete**: `chapter4.md` (742 words). It is superseded.
- **Primary working file**: `chapter4_v2.md` — rewrite using the lean blueprint above.
- **Expected output**: ~3,500–4,000 words, ready for thesis submission.

---

## 14) Immediate Next Work Package

1. **Review and confirm** the lean blueprint above (section word targets, prose strategy, role assignments)
2. **Make final call on 4.11 (run-config)** and **4.12 (tranche gates)**: Are these central to your thesis narrative, or appendix/omit?
3. **Rewrite chapter4_v2.md** using the lean blueprint as your section guide
4. **Implement prose variation** so 4.3–4.9 don't all sound like the same pattern repeated
5. **Verify artefact paths** in final draft against actual outputs (spot-check 2–3 per stage)
6. **Add tables and figures** (most are already in chapter4_v2.md; ensure they are referenced and captioned)

---

## 15) Progress Update (2026-04-27)

- Completed: planning baseline created aligned to locked RQ and rebuild posture
- Completed: section blueprint synchronised with current chapter4_v2.md structure
- Completed: Chapter 5 handoff expectations made explicit as objective-linked evidence
- Completed: version comparison analysis (chapter4.md vs. chapter4_v2.md) with consolidation recommendation
- Completed: lean blueprint created with section word targets (3,500–4,000 total), prose-variation rules, and strategic trim guidance
- Completed: file consolidation decision (archive chapter4.md; rewrite chapter4_v2.md to lean blueprint)
- **Current status**: Ready to rewrite chapter4_v2.md using lean blueprint guidance. Rewrite should prioritise 4.3–4.8 as the core narrative, compress 4.10–4.14, and vary prose to avoid templated repetition.
