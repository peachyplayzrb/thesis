# Chapter 4: Implementation and Evaluation

## 4.1 Chapter Aim and Scope
This chapter reports how the designed artefact is implemented and how it is evaluated under the locked MVP scope. The chapter does not claim state-of-the-art recommendation accuracy. Instead, it evaluates whether the system delivers deterministic behavior, transparent and inspectable recommendation logic, practical controllability, and playlist-rule compliance under BSc-feasible conditions.

Scope boundaries remain consistent with `00_admin/thesis_state.md`: single-user pipeline, one practical ingestion path, deterministic scoring core, and no deep-model baseline benchmarking.

## 4.2 Evaluation Criteria and Success Conditions
Evaluation follows `00_admin/evaluation_plan.md` and uses five criteria.

Table 4.1 defines the evaluation criteria, operational checks, and minimum success conditions used in this chapter.

| Criterion | Operational check | Minimum success condition |
| --- | --- | --- |
| Reproducibility | Replay identical input and configuration across multiple runs | Identical ranked output and playlist output for repeated runs |
| Traceability | Inspect score-contribution and rule-adjustment outputs per recommended track | Every recommended track has readable mechanism-linked explanation fields |
| Controllability | Change one parameter at a time and observe output differences | Output changes are interpretable and directionally consistent with control intent |
| Constraint compliance | Verify playlist-level rules (for example length, repetition, ordering/diversity) | Generated playlists satisfy configured rule set or produce explicit violation logs |
| Testing quality | Document method, setup, outputs, and critical interpretation | Reproducible test notes with failures/limitations explicitly discussed |

## 4.3 Chapter 3 to Chapter 4 Continuity Mapping
To prevent design-evaluation drift, each Chapter 3 commitment is tied to a Chapter 4 evaluation check.

Table 4.2 provides the design-to-evaluation continuity mapping used to keep Chapter 4 evidence aligned with Chapter 3 commitments.

| Chapter 3 design commitment | Chapter 4 evaluation check | Evidence artifact |
| --- | --- | --- |
| Objective-aligned deterministic architecture under MVP constraints (Sections 3.1 to 3.3) | Verify implemented pipeline stages and scope boundary compliance | Implementation summary + scope-conformance checklist |
| Explicit user control and parameterized execution (Sections 3.2, 3.8) | One-factor-at-a-time sensitivity tests | Parameter sweep table and output delta summary |
| Distinct playlist assembly stage with rule constraints (Section 3.6) | Rule-compliance checks per generated playlist | Constraint pass/fail table with violation diagnostics |
| Explicit feature/metric-based deterministic scoring (Sections 3.5, 3.6) | Explanation-fidelity checks against raw score components | Track-level score breakdown snapshots |
| Staged alignment with unmatched reporting (Section 3.4) | Alignment diagnostics and unmatched-rate reporting | Matching summary (ISRC hits, fallback hits, unmatched count/rate) |
| Run-level observability and replayability (Section 3.7) | Deterministic replay tests with run logs | Re-run comparison logs and config snapshots |

This mapping provides the direct handoff from design rationale to evaluable system behavior.

## 4.4 Implementation Overview (Report Structure)
Implementation reporting should be organized by pipeline stage to preserve inspectability.

1. Ingestion and input normalization.
2. ISRC-first alignment and metadata fallback logic.
3. Preference-profile construction from matched history and influence tracks.
4. Candidate filtering and feature preparation.
5. Deterministic scoring with rule adjustments.
6. Playlist assembly and post-assembly validation.
7. Explanation rendering and run-level logging.

For each stage, report:
- implemented behavior,
- key configuration controls,
- known limitations,
- and which evaluation criterion the stage primarily supports.

## 4.5 Evaluation Procedure
The evaluation procedure uses a staged protocol to keep results interpretable.

1. Baseline reproducibility run:
- fix input history, influence tracks, and configuration;
- execute repeated runs;
- compare ranked candidates and final playlists for identity.

2. Alignment-quality diagnostics:
- record ISRC matches, metadata fallback matches, and unmatched tracks;
- analyze whether unmatched items are bounded and transparently reported.

3. Explanation-fidelity validation:
- select sample recommendations from baseline runs;
- verify explanation values against deterministic score components and rule adjustments.

4. Controllability sensitivity tests:
- vary one control parameter at a time (for example feature weights or diversity controls);
- record rank/playlist deltas and assess directional interpretability.

5. Constraint-compliance verification:
- check playlist outputs against configured rules;
- log any violations with likely causes.

## 4.6 Evidence Packaging
Evaluation evidence should be stored in reproducible, cross-referenced artifacts.

- Primary logs and notes: `07_implementation/test_notes.md`, `07_implementation/experiment_log.md`
- Supporting summaries: reproducibility tables, sensitivity tables, and rule-compliance tables in this chapter
- Quality-control linkage: update `09_quality_control/claim_evidence_map.md` and `09_quality_control/chapter_readiness_checks.md` after final result integration

## 4.7 Limits and Interpretation Discipline
Results in this chapter should be interpreted as design-evidence for a scoped deterministic pipeline, not as universal recommender superiority claims. Any weak or mixed outcomes (for example high unmatched rate or unstable sensitivity behavior) should be explicitly documented and carried into Chapter 5 limitations.

## 4.8 Chapter Summary
Chapter 4 operationalizes the Chapter 3 design into a transparent evaluation workflow centered on reproducibility, inspectability, controllability, and playlist-rule compliance. This preserves continuity with Chapter 2 literature consequences and prepares evidence-grounded interpretation for Chapter 5.

