# Architecture

DOCUMENT STATUS: working design
CONFIDENCE: medium
ROLE: design candidate
SOURCE: `05_design/chapter3_information_sheet.md` + `10_resources/previous_drafts/old_literature_review.md`

## Evidence vs Interpretation
Evidence inputs:
- Chapter 3 master information sheet (conceptual architecture draft).
- Legacy literature review extraction and bibliography.

Interpretation outputs:
- Layer/component extraction and dependency view.
- Risks, refinements, and literature-justification checklist.

## 1) Extracted System Layers and Components
1. User Interaction: source selection, import actions, influence track input, parameter controls.
2. Data Ingestion: platform adapters, metadata extraction, history capture.
3. Track Alignment: ISRC-first matcher, metadata fallback matcher, unmatched handling.
4. Preference Modelling: profile builder from matched tracks plus influence tracks.
5. Candidate Generation: candidate pool retrieval, thresholding/filtering strategy.
6. Feature Processing: feature selection, normalization, missing-value handling, weight prep.
7. Deterministic Scoring: similarity function and explicit adjustment rules.
8. Playlist Assembly: diversity/repetition/length/order constraints.
9. Output and Explanation: per-track explanation artifacts.
10. Observability and Audit: stage-level logs and traces.
11. Configuration and Execution: run profiles, reproducibility controls.

## 2) Assumptions Made By Current Architecture
- Deterministic scoring can provide useful recommendation quality for the thesis scope.
- Cross-source alignment quality is sufficient with ISRC + metadata fallback.
- Music4All feature coverage is adequate for preference modelling and scoring.
- Single-user scope is acceptable for thesis contribution claims.
- Explanations derived from deterministic scoring will be understandable and useful.

## 3) Design Elements Requiring Literature Justification
- Why deterministic similarity scoring is preferred for transparency goals.
- Why ISRC-first hierarchical matching is valid and what failure rates are acceptable.
- Why selected feature set supports user-perceived relevance and controllability.
- Why chosen playlist assembly constraints improve coherence/diversity.
- Why observability logs chosen are sufficient for inspectability and reproducibility.
- Why evaluation criteria prioritize transparency/controllability over ranking accuracy.

## 4) Elements Likely Requiring Refinement
- Alignment policy for remasters/live versions/metadata conflicts.
- Candidate generation method (threshold strategy may over-prune or over-expand).
- Rule interactions in scoring and assembly (risk of unstable behavior across parameter sets).
- Explanation format granularity (too technical vs too shallow).
- Config profile schema for reproducibility and run comparison.

## 5) Architecture Risks and Weaknesses
- Data loss risk: unmatched imported tracks can bias preference profile.
- Semantic gap risk: feature similarity may not reflect perceived playlist fit.
- Control overload risk: too many user parameters may reduce usability.
- Rule brittleness risk: hard constraints may produce repetitive or rigid playlists.
- Traceability debt risk: partial logging can break explanation faithfulness.

## 6) Working-Hypothesis Constraint
This architecture is a design hypothesis, not final system truth.
Conflicts between literature evidence, implementation evidence, and current design must be logged before architectural lock-in.

