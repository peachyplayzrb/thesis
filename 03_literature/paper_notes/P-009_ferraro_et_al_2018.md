id: P-009
citation_key: ferraro_automatic_2018
full_reference: Ferraro, A., Bogdanov, D., Yoon, J., Kim, K., and Serra, X. (2018) Automatic playlist continuation using a hybrid recommender system combining features from text and audio. Proceedings of the ACM Recommender Systems Challenge 2018, 1-5. doi:10.1145/3267471.3267473.
document_status: processed_paper_note
confidence: medium

research_problem:
How to perform automatic playlist continuation by combining complementary recommendation signals in challenge settings.

method_or_system_type:
Hybrid ranking-fusion system (matrix factorization + co-occurrence model + audio/text signals).

key_findings:
- Combining multiple signal sources improves playlist continuation outcomes in benchmark context.
- Audio and contextual playlist signals are both useful for candidate ranking.
- Practical pipeline design can use modular model components for recommendation assembly.

limitations:
- Challenge-oriented benchmark framing emphasizes performance over transparency.
- Hybrid architecture includes non-MVP complexity and limited direct interpretability.

relevance_to_thesis:
Provides comparative context for why this thesis narrows to deterministic transparent mechanisms while still addressing playlist continuation needs.

supported_architecture_layer:
- Candidate Dataset Layer
- Playlist Assembly Layer
- Configuration and Execution Layer

theme_mapping:
- playlist_generation
- hybrid_baselines
- feature_and_context_signals

design_implications:
- Use as contrast baseline context rather than direct architecture copy.
- Maintain modular execution pipeline design with explicit configuration.

chapter_use_cases:
- Chapter 2: playlist continuation baseline landscape.
- Chapter 3: rationale for deterministic MVP simplification.

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md
