id: P-006
citation_key: deldjoo_content-driven_2024
full_reference: Deldjoo, Y., Schedl, M., and Knees, P. (2024) Content-driven music recommendation: Evolution, state of the art, and challenges. Computer Science Review, 51, 100618. doi:10.1016/j.cosrev.2024.100618.
document_status: processed_paper_note
confidence: medium

research_problem:
How content-driven music recommendation has evolved, which content layers are used, and what major open challenges remain.

method_or_system_type:
Survey/review (55 papers) with onion-model categorization of music content and challenge-oriented synthesis.

key_findings:
- Proposes an onion model with layered music content categories (signal, embedded metadata, expert-generated, user-generated, derivative).
- Identifies persistent challenges: diversity/novelty, transparency/explanations, sequence recommendation, scalability/efficiency, cold start, context.
- Highlights transition from pure CF/CB to content-driven hybrid approaches.

limitations:
- Survey-level synthesis, not a direct implementation blueprint for deterministic single-user MVP pipelines.
- Does not provide ISRC-level alignment protocol recommendations.

relevance_to_thesis:
Directly supports candidate-dataset, feature-processing rationale, and playlist/challenge framing for architecture decisions.

supported_architecture_layer:
- Candidate Dataset Layer
- Feature Processing Layer
- Playlist Assembly Layer

theme_mapping:
- music_recommenders
- content_driven_music_recommendation
- playlist_generation
- evaluation_challenges

gap_implications:
Content-driven music recommendation surveys still leave transparency and sequence-quality gaps under-specified; the thesis addresses this by making playlist assembly and feature rationale explicit inside a deterministic pipeline.

design_implications:
- Justify using a fixed content-feature corpus for tractable MVP experiments.
- Explicitly position playlist assembly as distinct from ranking.
- Tie feature choices to content-layer rationale in design chapter.

chapter_use_cases:
- Chapter 2: content-driven music recommendation landscape.
- Chapter 3: dataset/feature layer and candidate strategy rationale.

linked_files:
- 05_design/literature_architecture_mapping.md
- 05_design/requirements_to_design_map.md
- 03_literature/literature_gap_tracker.md
