# Chapter 3

## 3.1 Design Methodology
- Methodological stance: Design Science Research.
- Workflow used: literature synthesis -> requirements -> architecture/design -> implementation -> evaluation.
- Scope control: architecture treated as working hypothesis constrained by MVP feasibility.

## 3.2 Literature-Driven Design Requirements
- Inspectable recommendation logic (transparency-by-design).
- User influence over recommendation behavior (controllability).
- Playlist-level quality constraints beyond item ranking.
- Reproducibility and auditability of recommendation runs.
- Practical BSc-level delivery constraints from university requirements.

## 3.3 Overall System Architecture
- Layered pipeline overview.
- End-to-end data flow from user input to generated playlist and explanation outputs.
- MVP conformance note: single ingestion path, deterministic core, no multi-model complexity.

## 3.4 Data Ingestion and Alignment
- Data ingestion boundary: one practical source format + manual seed input.
- Alignment method: ISRC-first matching with metadata fallback.
- Failure handling: unmatched-track exclusions and reporting.

## 3.5 Preference Modelling and Candidate Generation
- User preference profile construction from matched track features and influence tracks.
- Candidate dataset strategy using canonical corpus and filtered candidate subset.
- Feature-processing steps for comparability and scoring readiness.

## 3.6 Deterministic Scoring and Playlist Assembly
- Deterministic candidate scoring function and explicit rule adjustments.
- Playlist assembly constraints: length, repetition limits, diversity/ordering rules.
- Rationale for deterministic approach in relation to transparency and reproducibility goals.

## 3.7 Transparency and Explanation Mechanisms
- Explanation outputs tied directly to score contributions and adjustment rules.
- Distinction between faithful mechanism-linked explanations and post-hoc rationalization.
- Expected contribution to user understanding and system inspectability.

## 3.8 Observability and Reproducibility
- Run logging model: input summary, alignment stats, scoring config, output artifacts.
- Replay strategy for deterministic verification.
- Link to evaluation criteria for traceability and reproducibility.

## 3.9 Configuration and Execution Control
- Configuration profile structure and execution controls.
- Parameter sensitivity testing support.
- Scope note on non-goals (no large-scale benchmark or production deployment complexity).

