id: P-011
citation_key: adomavicius_toward_2005
full_reference: Toward the next generation of recommender systems: a survey of the state-of-the-art and possible extensions. {IEEE (2005). doi:10.1109/TKDE.2005.99.
document_status: processed_paper_note
confidence: medium

research_problem:
Define core recommender paradigms and limitations of then-current methods.

method_or_system_type:
Foundational survey/taxonomy of recommender systems

key_findings:
- Identifies content-based, collaborative, and hybrid paradigms as core families.
- Highlights recurring issues such as sparsity, cold start, and contextual limitations.
- Proposes extension directions including richer user/item/context modelling.

limitations:
- General-domain survey, not music-specific.
- Predates modern explainability and deep recommender pipelines.

relevance_to_thesis:
Provides foundational framing for why deterministic content-based architecture is a valid design choice and where limitations should be acknowledged.

supported_architecture_layer:
- Candidate Dataset Layer
- Configuration and Execution Layer

theme_mapping:
- recommender_foundations
- candidate_dataset_and_filtering

design_implications:
- Document paradigm choice explicitly as deliberate scope decision.
- Use limitations as motivation for transparency and controllability focus.

chapter_use_cases:
- Chapter 2
- Chapter 3 (where relevant)

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md
