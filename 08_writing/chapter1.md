# Chapter 1: Introduction

Chapter objective: define the thesis problem framing, locked research question, objectives, scope boundaries, and contribution positioning for the deterministic single-user playlist pipeline described in the current thesis state.

## 1.1 Problem Context
Music streaming environments expose very large catalogs, while individual users provide partial and noisy preference signals through listening history. This creates an engineering problem: how to produce playlist outputs that are inspectable, controllable, and reproducible under practical data and time constraints, rather than only optimizing predictive performance.

## 1.2 Research Question
This chapter uses the locked research question from the current thesis state:

What design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data?

## 1.3 Research Objectives
The thesis objectives are aligned to the locked scope and implementation posture:

1. Design an automated pipeline that generates playlists from user listening histories.
2. Align cross-platform listening data into an inspectable preference signal using robust metadata handling and semantic enrichment.
3. Construct a deterministic user preference profile based on imported listening data, user-selectable source scope, and manually selected influence tracks.
4. Generate candidate tracks from the active integrated candidate dataset using feature-based filtering.
5. Score candidate tracks using deterministic similarity functions and rule-based adjustments.
6. Assemble playlists using playlist-level rules that ensure diversity, coherence, and ordering.
7. Provide transparent explanations and observability mechanisms for recommendation decisions.
8. Evaluate the system with respect to transparency, controllability, inspectability, and reproducibility.

## 1.4 Scope and Boundaries
In-scope position for this thesis:
- Single-user deterministic playlist generation pipeline.
- Content-based recommendation logic with explicit transparency, controllability, and observability requirements.
- One practical ingestion path and reproducible run logging.
- Active candidate corpus: DS-002 (MSD subset + Last.fm tags), with semantic enrichment for user-side preference extraction.

Out-of-scope position for this thesis:
- Collaborative filtering and deep neural model novelty as core contribution claims.
- Multi-user personalization and large-scale user studies.
- Multi-adapter feature expansion beyond the locked MVP boundary.

## 1.5 Contribution Positioning
The contribution is an engineering and design evidence contribution, not a new model class. Claims are intentionally bounded to implemented artifact behavior, documented run evidence, and explicitly stated limitations.

## 1.6 Chapter Summary
Chapter 1 defines the thesis problem framing and contribution boundary, states the locked research question and objectives, and sets in-scope versus out-of-scope constraints. This establishes the evaluation lens used in later chapters: transparent, controllable, observable, and reproducible system behavior under a constrained MVP context.

