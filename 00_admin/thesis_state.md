# Thesis State

## Official Current State

- Current title:
Engineering an Automated, Transparent, and Controllable Playlist Generation Pipeline Using Cross-Source Music Preference Data

- Current research question:
What design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data?

- Current objectives:
1. Design an automated pipeline that generates playlists from user listening histories.
2. Align cross-platform music data with the active candidate dataset strategy using ISRC-first matching with metadata fallback.
3. Construct a deterministic user preference profile based on imported listening data and manually selected influence tracks.
4. Generate candidate tracks from the active integrated candidate dataset using feature-based filtering.
5. Score candidate tracks using deterministic similarity functions and rule-based adjustments.
6. Assemble playlists using playlist-level rules that ensure diversity, coherence, and ordering.
7. Provide transparent explanations and observability mechanisms for recommendation decisions.
8. Evaluate the system with respect to transparency, controllability, inspectability, and reproducibility.

- Current artefact definition:
A deterministic single-user playlist generation pipeline with one practical ingestion path, ISRC-first track alignment, deterministic feature-based scoring, configurable playlist assembly rules, transparent score explanations, and reproducible run logging.

- Current methodology position:
Design Science Research with an iterative literature -> requirements -> design -> implementation -> evaluation flow. Contribution focus is engineering/design evidence for transparent, controllable, and observable recommendation pipelines, not ML model novelty.

- Current system scope:
Locked MVP scope: single-user, content-based, deterministic playlist pipeline with transparency, controllability, and observability as mandatory qualities. Multi-adapter expansion, deep models, and large-scale user studies are out of scope for the core artefact.

- Current evaluation direction:
Evaluation focuses on BSc-feasible artefact testing aligned to module expectations:
• reproducibility (same input/config => same output)
• transparency/inspectability (score contributions and rule adjustments)
• controllability (parameter sensitivity effects on outcomes)
• observability (run logging, diagnostics, and traceable execution context)
• playlist rule compliance and critical evaluation of limitations

- Current data scope:
The active candidate corpus is DS-002 (`MSD subset + Last.fm tags + MusicBrainz mapping`). The BL-019 intersection dataset has been built and verified (9330 tracks, all quality gates pass, determinism confirmed — see `07_implementation/experiment_log.md` EXP-016). Music4All/Music4All-Onion remains a historical baseline and fallback reference. User listening histories are imported from external music platforms and aligned with the active candidate dataset using metadata-first matching (normalized title + artist, duration/release tie-breaks); corpus-side ISRC is not currently assumed.

- Current assumptions:
• recommendation modelling focuses on a single user profile
• deterministic algorithms are used instead of machine learning
• active dataset feature coverage is sufficient for MVP evaluation goals
• one ingestion path is enough to evaluate core design considerations
• manually added influence tracks can improve preference representation

- Current limitations:
• some imported tracks may not match tracks present in the active candidate dataset
• recommendation quality depends on available feature descriptors
• no collaborative filtering or deep recommender baseline is included
• evaluation is limited to BSc-feasible testing and does not include large-scale user studies

## Update Control

- Last updated:
2026-03-21

- Reason for last update:
Mark BL-019 complete: DS-002 intersection dataset built and verified (9330 tracks, quality gates pass, two-run determinism confirmed). Update data scope wording to reflect completed build status and correct Spotify alignment model (metadata-first, not ISRC-first) for the DS-002 corpus.

## Locked Definitions
- Artefact scope lock: `00_admin/Artefact_MVP_definition.md`
- Evaluation plan: `00_admin/evaluation_plan.md`
- Methodology definition: `00_admin/methodology_definition.md`