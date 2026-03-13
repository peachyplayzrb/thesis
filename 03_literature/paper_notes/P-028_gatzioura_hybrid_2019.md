id: P-028
citation_key: gatzioura_hybrid_2019
full_reference: A Hybrid Recommender System for Improving Automatic Playlist Continuation. {IEEE (2019). doi:10.1109/TKDE.2019.2952099.
document_status: processed_paper_note
confidence: medium

research_problem:
Improve playlist continuation with semantic and case-based hybrid approach considering coherence/diversity.

method_or_system_type:
Hybrid recommender for automatic playlist continuation

key_findings:
- Playlist continuation benefits from modelling beyond isolated item preference.
- Supports balancing coherence and diversity in playlist generation.
- Addresses semantic-gap concerns with richer representations.

limitations:
- Hybrid complexity and benchmark focus differ from deterministic MVP constraints.

relevance_to_thesis:
Strongly supports playlist assembly requirement and sequence-level mechanism rationale.

supported_architecture_layer:
- Playlist Assembly Layer
- Candidate Dataset Layer

theme_mapping:
- playlist_generation
- music_recommenders

design_implications:
- Retain explicit playlist-assembly stage and diversity/coherence controls in deterministic form.

chapter_use_cases:
- Chapter 2
- Chapter 3 (where relevant)

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md
