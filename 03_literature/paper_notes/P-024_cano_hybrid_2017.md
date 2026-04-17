id: P-024
citation_key: cano_hybrid_2017
full_reference: Hybrid recommender systems: A systematic literature review. {IDA (2017). doi:10.3233/IDA-163209.
document_status: processed_paper_note
confidence: medium

research_problem:
Analyze hybridization methods, addressed problems, and evaluation practices.

method_or_system_type:
Systematic literature review of hybrid recommender systems

key_findings:
- Hybrid methods often target cold-start and sparsity.
- Most studies remain accuracy-centric with limited user-oriented evaluation.
- Complexity and context adaptation remain open challenges.

limitations:
- Not specific to music deterministic transparency-by-design systems.

relevance_to_thesis:
Provides comparative baseline context and justifies MVP complexity control.

supported_architecture_layer:
- Candidate Dataset Layer
- Configuration and Execution Layer

theme_mapping:
- recommender_foundations
- candidate_dataset_and_filtering

gap_implications:
Hybrid music recommenders often prioritize performance gains without equally strong user-facing justification for added complexity; the thesis addresses this by defending a simpler deterministic MVP on transparency and auditability grounds.

design_implications:
- Use as contrast to justify not adopting hybrid complexity in MVP core.

chapter_use_cases:
- Chapter 2
- Chapter 3 (where relevant)

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md
