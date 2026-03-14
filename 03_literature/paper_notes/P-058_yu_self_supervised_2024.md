id: P-058
citation_key: yu_self_supervised_2024
full_reference: Self-Supervised Learning for Recommender Systems: A Survey. IEEE Transactions on Knowledge and Data Engineering (2024). doi:10.1109/TKDE.2023.3282907.
document_status: processed_paper_note
confidence: high

research_problem:
Survey self-supervised learning approaches for recommender systems and summarize method families, strengths, and challenges.

method_or_system_type:
Survey of self-supervised recommender methods

key_findings:
- Self-supervised methods are influential in modern recommender performance pipelines.
- Method complexity and infrastructure requirements are non-trivial.
- Deployment and interpretation concerns remain important despite performance gains.

limitations:
- Not focused on transparent deterministic architecture design.
- Primarily used as comparator-context evidence for scope positioning.

relevance_to_thesis:
Strengthens the rationale for explicitly framing deep/self-supervised methods as comparator context rather than MVP implementation requirement.

supported_architecture_layer:
- Comparator Framing Layer

theme_mapping:
- multimodal_and_hybrid_tradeoff
- comparator_design

gap_implications:
Reinforces challenge-side evidence against overclaiming deterministic universal superiority.

design_implications:
- Keep deterministic design rationale tied to inspectability/reproducibility goals.
- Explicitly acknowledge high-performing SSL alternatives in literature comparison.

chapter_use_cases:
- Chapter 2
- Chapter 5

linked_files:
- 09_quality_control/claim_evidence_map.md
- 09_quality_control/citation_checks.md
- 03_literature/literature_gap_tracker.md
