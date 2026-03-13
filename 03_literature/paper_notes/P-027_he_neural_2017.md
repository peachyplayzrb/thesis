id: P-027
citation_key: he_neural_2017
full_reference: Neural Collaborative Filtering. Proceedings of the 26th International Conference on World Wide Web (2017). doi:10.1145/3038912.3052569.
document_status: processed_paper_note
confidence: medium

research_problem:
Use neural architectures to model non-linear user-item interactions for recommendation.

method_or_system_type:
Neural collaborative filtering model

key_findings:
- Neural CF can improve modelling power over linear MF assumptions.
- Requires training and latent representations with reduced interpretability.
- Introduces higher modelling complexity and optimization dependency.

limitations:
- Outside deterministic transparent MVP scope; not music-specific.

relevance_to_thesis:
Functions as out-of-scope comparator to justify deterministic and interpretable architecture boundaries.

supported_architecture_layer:
- Configuration and Execution Layer

theme_mapping:
- recommender_foundations
- evaluation_challenges

design_implications:
- Use for boundary justification: interpretable deterministic system chosen over neural opacity for thesis goals.

chapter_use_cases:
- Chapter 2
- Chapter 3 (where relevant)

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md
