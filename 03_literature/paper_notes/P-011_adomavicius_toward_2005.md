id: P-011
citation_key: adomavicius_toward_2005
full_reference: Adomavicius, G. and Tuzhilin, A. (2005) Toward the next generation of recommender systems: a survey of the state-of-the-art and possible extensions. IEEE Transactions on Knowledge and Data Engineering, 17(6), 734-749. doi:10.1109/TKDE.2005.99.
document_status: processed_paper_note
confidence: high

research_problem:
Define core recommender paradigms and limitations of then-current methods.

method_or_system_type:
Foundational survey/taxonomy of recommender systems

key_findings:
- Identifies content-based, collaborative, and hybrid paradigms as core families.
- Highlights recurring issues such as sparsity, cold start, and contextual limitations.
- Proposes extension directions including richer user/item/context modelling.
- Frames recommendation as utility estimation on user-item space and motivates evaluation choices as task dependent.

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

gap_implications:
Foundational recommender taxonomies validate the content-based paradigm but do not resolve transparency-first MVP scoping; the thesis fills that gap by documenting why an interpretable deterministic path is chosen within the broader design space.

design_implications:
- Document paradigm choice explicitly as deliberate scope decision.
- Use limitations as motivation for transparency and controllability focus.
- Keep architecture claims bounded to foundational framing and complement with newer empirical sources for current-state performance trade-offs.

chapter_use_cases:
- Chapter 2
- Chapter 3 (where relevant)

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md

source_recovery_note:
- 2026-03-23: recovered text evidence from user-provided source attachment and Zotero full-text cache export; no longer treated as missing extraction input for citation hardening.
