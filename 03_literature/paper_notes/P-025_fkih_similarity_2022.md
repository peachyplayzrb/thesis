id: P-025
citation_key: fkih_similarity_2022
full_reference: Similarity measures for Collaborative Filtering-based Recommender Systems: Review and experimental comparison. Journal of King Saud University - Computer and Information Sciences (2022). doi:10.1016/j.jksuci.2021.09.014.
document_status: processed_paper_note
confidence: medium

research_problem:
Compare similarity metrics and their impact in collaborative filtering performance.

method_or_system_type:
Review and experimental comparison of similarity measures in CF

key_findings:
- Similarity measure choice significantly changes recommender performance.
- Metric selection is context-sensitive and empirically consequential.
- Provides comparative evidence across standard datasets.

limitations:
- CF-focused; direct transfer to content-only music scoring requires caution.

relevance_to_thesis:
Supports transparent justification of similarity-function choice and sensitivity analysis.

supported_architecture_layer:
- Deterministic Candidate Scoring Engine
- Configuration and Execution Layer

theme_mapping:
- similarity_measures
- evaluation_challenges

design_implications:
- Justify scoring metric selection and include parameter/metric sensitivity checks.

chapter_use_cases:
- Chapter 2
- Chapter 3 (where relevant)

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md
