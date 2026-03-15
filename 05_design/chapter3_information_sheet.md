DOCUMENT STATUS: conceptual design guide
CONFIDENCE: medium
ROLE: architecture explanation draft
SOURCE: user-provided Chapter 3 master sheet (2026-03-13)

# Chapter 3 Master Information Sheet
System Design and Architecture

## Thesis Title
Engineering an Automated, Transparent, and Controllable Playlist Generation Pipeline Using Cross-Source Music Preference Data

## Research Question
What design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data?

## Purpose of Chapter 3
Chapter 3 explains how the proposed system is designed and why it is designed that way.
It translates literature insights into a concrete architecture and does not report implementation outcomes or evaluation results.

## Design Methodology
- Design science orientation.
- Iterative flow: literature findings -> engineering requirements -> system architecture -> automated pipeline.
- Focus on interpretability, controllability, observability, and inspectability rather than ML leaderboard performance.

## Literature-Driven Requirement Traceability (Seed)
- Opaque recommendation logic -> inspectable process -> deterministic scoring with score traces.
- Limited user agency -> user influence controls -> influence tracks and adjustable parameters.
- Playlist construction complexity -> playlist-level logic -> dedicated assembly stage.
- Cross-source data mismatch -> robust alignment -> ISRC-first hierarchical matching.
- Reproducibility concerns -> run-level repeatability -> configuration and execution layer.

## Proposed Layered Architecture
1. User Interaction Layer
2. Data Ingestion Layer
3. Track Alignment Layer
4. Preference Modelling Layer
5. Candidate Generation Layer
6. Feature Processing Layer
7. Deterministic Candidate Scoring Engine
8. Playlist Assembly Layer
9. Output and Explanation Layer
10. Observability and Audit Layer
11. Configuration and Execution Layer

## Layer Notes
### User Interaction Layer
- Imports listening history.
- Accepts influence tracks.
- Exposes playlist generation controls.

### Data Ingestion Layer
- Collects saved tracks, playlist tracks, metadata, and ISRC from adapters.

### Track Alignment Layer
- Primary: ISRC match.
- Fallback: artist + title match.
- Unmatched tracks are excluded.

### Preference Modelling Layer
- Builds canonical preference representation from matched history + influence tracks.

### Candidate Generation Layer
- Builds candidate subset before scoring.
- Uses similarity thresholds and metadata filtering.

### Feature Processing Layer
- Feature selection, normalization, missing-value handling, weighting prep.

### Deterministic Scoring Engine
- Computes similarity between profile and candidate vectors.
- Applies explicit rule adjustments.

### Playlist Assembly Layer
- Applies diversity, repetition, length, and ordering rules.

### Output and Explanation Layer
- Exposes track-level similarity contribution, rule adjustments, and ranking rationale.

### Observability and Audit Layer
- Logs import stats, alignment outcomes, candidate pool size, score traces, and playlist rules.

### Configuration and Execution Layer
- Stores feature weights, constraints, filters, and run configuration for reproducibility.

## Artefact Success Criteria
- Same inputs produce same outputs.
- Decision logic is inspectable.
- Explanations are faithful to scoring logic.
- User controls influence results.
- Run behavior is observable through structured diagnostics and logs.
- Runs can be reproduced from saved configuration.

## Assumptions and Limitations
- Single-user focus.
- Content-based design (no collaborative filtering core).
- Some imported tracks will not align.
- Recommendation quality depends on available descriptors.

## Diagram Plan
- Figure 3.1 System architecture overview.
- Figure 3.2 End-to-end data flow.
- Figure 3.3 Cross-source alignment strategy.
- Figure 3.4 Candidate generation and deterministic scoring.
- Figure 3.5 Playlist assembly logic.
- Optional Figure 3.6 Observability and audit logging.

## Control Rule
Treat this sheet as a working architecture hypothesis.
Literature and implementation evidence can refine it.
