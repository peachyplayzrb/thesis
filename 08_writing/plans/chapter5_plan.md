# Chapter 5 Plan (Evidence-to-Evaluation Bridge)

Document status: active planning note
Date: 2026-04-27
Owner: AI + Tim

## 1) Planning Goal
Produce a freeze-ready Chapter 5 that:
- presents evidence from Chapter 4 implementation against locked objectives O1–O6,
- evaluates reproducibility and controllability through explicit acceptance criteria,
- avoids overclaiming beyond the bounded single-user deterministic scope,
- creates a clean handoff into Chapter 6 discussion and limitations.

Locked RQ reference:
How can a deterministic playlist generation pipeline be designed and evaluated so that it remains transparent, controllable, and reproducible when user preference data and candidate tracks come from different sources?

## 2) Chapter 5 Role Boundary (Must Respect)
Chapter 5 is evaluation and evidence assessment, not broad model-family comparison.
- Include: objective-linked acceptance checks, reproducibility verification, controllability parameter-sensitivity analysis, explanation fidelity validation, bounded-scope evidence.
- Exclude: benchmark comparisons to neural/collaborative systems, claims beyond single-user deterministic scope, broad generalization beyond cross-source playlist constraints.

Core wording rule:
- Use language such as "evidence indicates", "criterion met", "criterion partially met", and "criterion not met" in objective sections.
- Reserve language such as "the pipeline satisfies" for the synthesis section only, after all criteria checks are presented.
- Avoid language such as "outperforms", "proves superiority", "best approach" unless directly comparing to pre-implementation baseline.
- Qualify all findings with explicit scope bounds (single-user, offline corpus, deterministic only).

## 3) Core Evaluation Argument (One Sentence)
Chapter 5 assesses the implemented pipeline against six objectives using artefact evidence produced in Chapter 4 and reports findings against pre-specified acceptance criteria.

## 3A) Pre-Specified Acceptance Criteria (Lock Before Drafting)
These criteria are draft-locked planning anchors and must be finalized before narrative drafting begins.

Locked constants (must be written into Chapter 5 methodology before evidence interpretation):
- O1 missingness threshold X: 0.20 (20% missingness).
- O5 reproducibility replay count N: 3 independent fixed-config replays.
- O4 structural-fidelity sample: 30 tracks total (10 selected, 10 rejected, 10 boundary-ranked by score percentile).
- O4 percentile tolerance: absolute difference <= 1.0 percentile point versus BL-006 source value.
- O5 controllability measurable-delta rule: each tested parameter variation must produce a downstream delta meeting at least one minimum magnitude threshold: candidate-set size change >= 1.0% of baseline (or >= 3 tracks, whichever is larger), score-distribution shift >= 0.01 in at least one tracked summary statistic, or final playlist composition change >= 1 track.

- O1 (Uncertainty-aware profiling): `bl004_preference_profile.json` contains uncertainty markers for all features with missingness > X (0.20), attribution tracking is populated for all influence-track inputs, and confidence-stratified records remain distinguishable from confident records.
- O2 (Confidence-aware alignment and candidate shaping): BL-003 match rate exceeds the 15% minimum threshold; unmatched records include explicit reason categories; BL-005 exclusions are separated across threshold, metadata, and influence pathways.
- O3 (Controllable trade-offs): BL-006 exposes decomposed component scores and active weight vectors for all scored candidates; BL-007 records rule activations and relaxation events with explicit reason codes and non-empty diagnostics fields when triggered.
- O4 (Mechanism-linked explanation fidelity): BL-008 payloads contain required fields (`score_percentile`, `score_band`, component attribution, rule effects, confidence marker) for all selected tracks; structural cross-check on the fixed 30-track sample yields zero critical mismatches and no more than 2 minor mismatches.
- O5 (Reproducibility and controllability): BL-010 reports identical output hashes across N=3 independent fixed-config replays; BL-011 reports per-variation deltas that meet at least one locked minimum magnitude threshold from the O5 measurable-delta rule.
- O6 (Bounded-guidance surfaces): BL-009 contains at least one explicit non-claim statement and at least one populated validity-boundary field; BL-007 must satisfy one auditable case: (a) if relaxation occurred, at least one relaxation event is recorded with a non-empty reason code and diagnostics context, or (b) if no relaxation occurred, BL-007 explicitly reports zero relaxation events and confirms constraints were satisfied without relaxation.

O6 audit clarification (no-relaxation case):
- Verify BL-007 contains explicit no-relaxation evidence (`relaxation_records` present and empty, or equivalent schema-level no-relaxation indicator).
- Verify BL-007 includes positive confirmation that constraints were satisfied without relaxation (not only absence of events).
- Verify BL-009 corroborates the same no-relaxation state in run-level validity/boundary reporting.

O4 mismatch taxonomy:
- Critical mismatch: missing required explanation field, wrong primary contributor attribution, or rule-effect contradiction against BL-007 assembly record.
- Minor mismatch: percentile tolerance breach only (difference > 1.0 percentile point) with contributor and rule-effect alignment still intact.

Lock rule:
- Do not rewrite these criteria after results extraction unless a mismatch is found between criterion wording and implemented artefact contracts; any criterion change must be documented as a traceability correction.
- Criteria are frozen before evidence extraction; any post-freeze change requires explicit governance traceability (change-log + decision-log note).

## 4) Inputs To Anchor
Primary source inputs for this chapter:
- `08_writing/chapter4.md` (implementation evidence surfaces)
- `05_design/chapter3_information_sheet.md` (design commitments)
- `05_design/requirements_to_design_map.md` (objective-to-evidence mapping)
- `07_implementation/src/quality/outputs/reb_m3_tranche*.json` (objective-gate evidence)
- `07_implementation/src/*/outputs/bl*.json` (stage-level artefacts BL-003 through BL-009)
- `07_implementation/src/reproducibility/outputs/reproducibility_report.json` (BL-010 results)
- `07_implementation/src/controllability/outputs/controllability_report.json` (BL-011 results)
- `00_admin/thesis_state.md` (locked objectives and scope)

Planning requirement:
Every evaluation finding should trace backward to a Chapter 4 evidence artifact and forward to a Chapter 6 limitation or discussion point.

## 5) Section Blueprint (Writing Skeleton)
1. Evaluation methodology and objective-linked acceptance criteria
   - Re-state the DSR evaluation frame and bounded scope inherited from Chapter 3 (single-user, offline corpus, deterministic execution).
   - Define "satisfied" for each of O1–O6 using the pre-specified criteria table before presenting findings.
   - Declare method-by-objective assessment types in advance:
     - field-population and schema-presence checks (O1, O2, O6),
     - decomposition and rule-effect inspection (O3),
     - structural cross-check between explanation payloads and scoring/assembly artifacts (O4),
     - hash consistency and replay comparison (O5 reproducibility),
     - controlled-delta interpretation (O5 controllability).
   - Establish evidence-versus-interpretation discipline for each objective section so conclusion language is derived from criteria outcomes, not assumed up front.
   - Target section length guidance: 400-500 words to avoid under-specifying evaluation method.

2. O5 Evidence: Reproducibility and Controllability (credibility-first ordering)
   - Present BL-010 deterministic replay results (same input/config -> same outputs).
   - Present BL-011 controlled-variation results (parameter changes cascade predictably).
   - Use this section to establish objective-assessment rigor before the more interpretation-sensitive objectives.

3. O1 Evidence: Uncertainty-Aware Profiling
   - Present BL-004 profile-structure evidence and BL-003 confidence markers.
   - Show how uncertainty is visible in attribute statistics and attribution tracking.

4. O2 Evidence: Confidence-Aware Alignment and Candidate Shaping
   - Present BL-003 match-rate diagnostics and cross-source identifier coverage.
   - Show BL-005 exclusion pathways and candidate-space visibility.

5. O3 Evidence: Controllable Trade-offs
   - Present BL-006 score decomposition and component weights.
   - Show BL-007 assembly rule effects and constraint relaxation records.

6. O4 Evidence: Mechanism-Linked Explanation Fidelity
   - Present BL-008 explanation payloads with score attribution and contributor mapping.
   - Show fidelity validation results from BL-014 explanation checks.
   - Explicitly bound this section to structural fidelity only (mechanism-alignment of explanation content), not perceived usefulness, user trust, or UX outcomes.

7. O6 Evidence: Bounded-Guidance Surfaces
   - Present BL-009 run-observability records with validity boundaries and non-claims.
   - Show BL-007 explicit constraint-violation reporting.

8. Objective-gate synthesis and acceptance summary
   - Summarize criterion outcomes for each O1–O6.
   - Identify any partially satisfied objectives and state their scope implications.
   - Characterize what the collective evidence indicates about the thesis contribution within its stated bounds.

9. Evaluation boundaries, non-claims, and Chapter 6 handoff
   - Explicitly state scope limits (single-user, offline, deterministic).
   - Identify what the evidence does not address (long-term user satisfaction, real-time performance, hybrid comparisons).
    - Point forward to discussion of implications, limitations, and future work.

## 6) Figure And Table Plan
Minimum visual artifacts:
- Figure 5.1: Evidence artifact inventory map (BL stage -> produced artefact -> mapped objective -> chapter section reference).
- Figure 5.2: Objective assessment-status matrix using a three-state legend (`Satisfied`, `Partially satisfied`, `Not satisfied`) with one row per objective and one column per acceptance criterion family.

Figure specification notes:
- Figure 5.2 is a categorical matrix, not a percentage chart.
- Figure 5.2 fixed column families are: Contract Presence, Diagnostic Completeness, Determinism and Delta Evidence, Boundary Clarity.
- Status assignment must be criterion-based and trace back to Table 5.1/5.2 evidence rows.
- Any `Partially satisfied` or `Not satisfied` cell must be accompanied by a short boundary note and Chapter 6 forward pointer.

Minimum tables:
- Table 5.1: O1–O6 objective descriptions with acceptance criteria (what does "satisfied" mean).
- Table 5.2: Evidence-to-objective mapping with artifact reference (BL-003 → O2, BL-004 → O1, etc.).
- Table 5.3: Reproducibility and controllability test results (deterministic replay pass rates, parameter-variation signal clarity).

## 7) Traceability To Chapter 6 (Must Be Explicit)
For each objective evaluation outcome, identify the discussion implication:
- O1 satisfaction → discuss implications for uncertainty communication to users.
- O2 satisfaction → discuss cross-source reliability limits and alignment confidence thresholds.
- O3 satisfaction → discuss controllability user interface and parameter transparency.
- O4 satisfaction → discuss explanation effectiveness and fidelity gaps.
- O5 fully satisfied (BL-010 pass + BL-011 all tested scenarios meeting locked delta thresholds) → discuss reproducibility guarantees, controllability confidence, and bounded determinism conditions.
- O5 partially satisfied (BL-010 pass + BL-011 only subset of scenarios meeting locked delta thresholds) → discuss reproducibility guarantees with explicit controllability coverage limits, unconfirmed interaction ranges, and bounded claims.
- O6 satisfaction → discuss scope limits and non-applicability conditions.

## 8) Claim Discipline Rules
- Scope all findings explicitly (single-user playlist generation, offline corpus, deterministic execution).
- Present evidence strength honestly (what the artifacts show vs. infer).
- Avoid generalizing beyond the bounded scope (no claims about large-scale deployment, real-time performance, collaborative scenarios).
- Label open questions and evidence gaps for Chapter 6 discussion.
- Keep comparator context (neural/hybrid methods exist but are out of scope for this thesis).

O4-specific methodological boundary:
- Evaluate explanation fidelity as structural mechanism alignment only (payload-to-scoring/assembly consistency).
- Do not claim perceived usefulness, user trust, or explanatory persuasiveness from artefact-level checks.
- Route perceived-usefulness limitations explicitly to Chapter 6.

## 9) Execution Plan (Fast, Practical)
Step 1: Objective acceptance criteria lock (single focused session)
- Run synchronization pre-check before criteria validation:
   - Confirm Chapter 4 evidence references used for extraction are current and consistent.
   - Confirm Chapter 3 design commitments and requirements-to-design mappings are unchanged.
   - Confirm BL-003 to BL-011 artifact paths exist and are readable from active surfaces.
   - Record checkpoint timestamp and active artifact authorities before interpreting results.
- Mandatory pre-condition: refresh BL-011 before extraction and drafting.
   - If BL-011 is older than the latest BL-006/BL-007 authority set, run BL-011 again first.
   - Record BL-011 run timestamp and config authority used for evaluation extraction.
- Validate and finalize the pre-specified O1–O6 criteria and locked constants before interpreting evidence.
- Freeze criteria set and record any required wording correction as a traceability update before extraction starts.
- Confirm criteria align with Chapter 3 design and Chapter 4 implementation artefact contracts.

Step 2: Evidence mapping pass (single session)
- Populate Table 5.2 with BL-stage → objective → artifact references.
- Confirm all six objectives have at least one evidence artifact.

Step 3: Evaluation results synthesis (1–2 focused sessions)
- Extract key results from BL-010 and BL-011 outputs.
- Summarize objective-gate results from tranche gates.
- Organize findings in chapter order: O5, O1, O2, O3, O4, O6.
- Apply explicit O5 decision gate immediately after BL-011 extraction:
   - PASS: all tested BL-011 scenarios meet at least one locked minimum-delta threshold.
   - PARTIAL: after one mandatory rerun attempt, only a subset of tested scenarios meets thresholds; document residual gap and bounded implication.
   - FAIL: no tested scenarios meet thresholds; escalate as evaluation blocker and do not proceed to drafting without explicit decision traceability.

Step 4: Traceability pass (single session)
- Verify each evaluation finding traces backward to Chapter 4 evidence artifact.
- Add forward links to Chapter 6 discussion implications.

Step 5: Scope and boundary pass (single session)
- Add explicit scope statements to each section.
- Clarify non-claims and out-of-scope items.

Step 6: Figures/tables insertion (single session)
- Insert and caption required figures/tables.
- Ensure each is referenced and interpreted in text.

Step 7: Final discipline pass (single session)
- Remove overclaiming language.
- Confirm all findings are evidence-grounded.
- Run citation/consistency checks and update quality-control logs.

## 10) Definition Of Done (Chapter 5 Ready)
- Chapter 5 is methodologically consistent with DSR and bounded scope.
- All six objectives have explicit acceptance criteria and evidence.
- All thresholds, sample rules, and tolerance constants are explicitly present in-plan before drafting.
- Evaluation findings are traceable to Chapter 4 implementation and Chapter 3 design.
- Reproducibility and controllability evidence is presented with numerical results.
- Scope and non-claims are explicit and unambiguous.
- Handoff to Chapter 6 is clear and discussion-focused.
- No outcome-overclaiming language remains.
- Required figures/tables are present, referenced, and interpreted.

## 11) Immediate Next Work Package
- Baseline chapter file: continue from `08_writing/chapter5.md` as primary draft.
- Validate locked criteria against implemented artefact contracts and freeze before extraction starts; begin with BL-010/BL-011 extraction for O5.
- Populate Table 5.1 and Table 5.2 with locked definitions and artifact references.
- Extract and summarize key numerical results from BL-010/BL-011 outputs.
- Draft scope-and-boundaries section with explicit non-claims.

## 12) Progress Update (2026-04-27)
- Completed: dedicated Chapter 5 planning baseline created and aligned to locked RQ and objectives O1–O6.
- Completed: chapter role boundary made explicit (evaluation, not broad model comparison).
- Completed: pre-specified acceptance criteria and locked constants written into Section 3A; O4 mismatch taxonomy defined; Figure 5.2 column families specified.
- Completed: handoff to Chapter 6 expectations identified (implications, limitations, future work).
- Current status: criteria-locked and freeze-governed; ready to execute O5-first evidence extraction, objective synthesis, and artefact insertion on the Chapter 5 draft.
