id: P-061
citation_key: bonnin_automated_2015
full_reference: Bonnin, G., and Jannach, D. (2015) Automated Generation of Music Playlists: Survey and Experiments. ACM Computing Surveys, 47(2), 1-35. doi:10.1145/2652481.
document_status: processed_paper_note
source_index_status: screened_keep
confidence: high

research_problem:
Synthesize automated music playlist generation methods and evaluate representative approaches under a comparative experimental setup.

method_or_system_type:
Survey and comparative evaluation study

key_findings:
- Playlist-generation approaches differ substantially in data assumptions and optimization targets.
- Evaluation designs for playlists require more than item-accuracy metrics alone.
- Popularity effects can dominate outcomes unless explicitly controlled and interpreted.

limitations:
- Predates newer deep and multimodal recommendation paradigms.
- General playlist-generation framing does not directly resolve deterministic-control-specific claims.

relevance_to_thesis:
High-value support for Chapter 2 playlist-evaluation framing and for bounded interpretation of metric outcomes.

supported_architecture_layer:
- Playlist Assembly Layer
- Evaluation and Comparator Framing

theme_mapping:
- playlist_generation
- evaluation_protocol_rigor
- popularity_bias

gap_implications:
Strengthens playlist-evaluation-method evidence and reduces dependence on challenge-only sources.

design_implications:
- Keep playlist-level checks explicit (not only ranking-level checks).
- Include popularity-awareness in interpretation of playlist outcomes.

chapter_use_cases:
- Chapter 2
- Chapter 5

linked_files:
- 03_literature/literature_gap_tracker.md
- 09_quality_control/claim_evidence_map.md
- 09_quality_control/citation_checks.md
