id: P-005
citation_key: schedl_current_2018
full_reference: Schedl, M., Zamani, H., Chen, C.-W., Deldjoo, Y., and Elahi, M. (2018) Current challenges and visions in music recommender systems research. International Journal of Multimedia Information Retrieval, 7(2), 95-116. doi:10.1007/s13735-018-0154-2.
document_status: processed_paper_note
confidence: medium

research_problem:
What major open challenges music recommender system research faces and where future work should focus.

method_or_system_type:
Trends/survey article across academic and industry perspectives.

key_findings:
- Music recommendation must address complex listener needs beyond simple user-item interaction signals.
- Challenges include context, evaluation, sequence/playlist behavior, and richer preference modeling.
- Existing approaches leave substantial under-researched areas in practical music recommendation design.

limitations:
- Survey-level framing; does not provide implementation details for deterministic pipelines.
- Broad challenge framing needs operationalization for a specific thesis artefact.

relevance_to_thesis:
High relevance for positioning architecture decisions in known music-RS challenge space.

supported_architecture_layer:
- Playlist Assembly Layer
- Evaluation and Comparator Framing

theme_mapping:
- music_recommenders
- playlist_generation
- evaluation_challenges
- context_and_preference_complexity

gap_implications:
Strengthens the case that playlist-generation systems require explicit design choices beyond top-N ranking logic.

design_implications:
- Keep dedicated playlist assembly stage separate from candidate ranking.
- Explicitly document which music-RS challenges are in scope vs out of scope.

chapter_use_cases:
- Chapter 2: music domain-specific challenge framing.
- Chapter 3: motivation for layered pipeline with playlist assembly.

linked_files:
- 03_literature/literature_gap_tracker.md
- 05_design/architecture.md
- 05_design/chapter3_information_sheet.md
