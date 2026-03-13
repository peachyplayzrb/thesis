# Thesis State

## Official Current State

- Current title:
Engineering an Automated, Transparent, and Controllable Playlist Generation Pipeline Using Cross-Source Music Preference Data

- Current research question:
What are the design considerations for engineering an automated, transparent, and controllable playlist generation pipeline using cross-source music preference data?

- Current objectives:
1. Design an automated pipeline that generates playlists from user listening histories.
2. Align cross-platform music data with the Music4All dataset using ISRC-based track matching.
3. Construct a deterministic user preference profile based on imported listening data and manually selected influence tracks.
4. Generate candidate tracks from the Music4All dataset using feature-based filtering.
5. Score candidate tracks using deterministic similarity functions and rule-based adjustments.
6. Assemble playlists using playlist-level rules that ensure diversity, coherence, and ordering.
7. Provide transparent explanations and observability mechanisms for recommendation decisions.
8. Evaluate the system with respect to transparency, controllability, inspectability, and reproducibility.

- Current artefact definition:
A deterministic single-user playlist generation pipeline with one practical ingestion path, ISRC-first track alignment, deterministic feature-based scoring, configurable playlist assembly rules, transparent score explanations, and reproducible run logging.

- Current methodology position:
Design Science Research with an iterative literature -> requirements -> design -> implementation -> evaluation flow. Contribution focus is engineering/design evidence for transparent and controllable recommendation pipelines, not ML model novelty.

- Current system scope:
Locked MVP scope: single-user, content-based, deterministic playlist pipeline with transparency and controllability as mandatory qualities. Multi-adapter expansion, deep models, and large-scale user studies are out of scope for the core artefact.

- Current evaluation direction:
Evaluation focuses on BSc-feasible artefact testing aligned to module expectations:
• reproducibility (same input/config => same output)
• transparency/inspectability (score contributions and rule adjustments)
• controllability (parameter sensitivity effects on outcomes)
• playlist rule compliance and critical evaluation of limitations

- Current data scope:
The system uses the Music4All / Music4All-Onion dataset as the primary candidate track corpus. User listening histories are imported from external music platforms and aligned with the dataset using ISRC identifiers and metadata matching.

- Current assumptions:
• recommendation modelling focuses on a single user profile
• deterministic algorithms are used instead of machine learning
• Music4All feature coverage is sufficient for MVP evaluation goals
• one ingestion path is enough to evaluate core design considerations
• manually added influence tracks can improve preference representation

- Current limitations:
• some imported tracks may not match tracks present in the Music4All dataset
• recommendation quality depends on available feature descriptors
• no collaborative filtering or deep recommender baseline is included
• evaluation is limited to BSc-feasible testing and does not include large-scale user studies

## Update Control

- Last updated:
2026-03-13

- Reason for last update:
Scope stabilization pass after university requirement ingestion: locked MVP artefact boundary, evaluation strategy, and methodology flow for assessment-feasible delivery.

## Locked Definitions
- Artefact scope lock: `00_admin/Artefact_MVP_definition.md`
- Evaluation plan: `00_admin/evaluation_plan.md`
- Methodology definition: `00_admin/methodology_definition.md`