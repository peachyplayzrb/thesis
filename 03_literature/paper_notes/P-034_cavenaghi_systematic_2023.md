id: P-034
citation_key: cavenaghi_systematic_2023
full_reference: A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems. ACM Transactions on Recommender Systems (2023). doi:10.1145/3596519.
document_status: processed_paper_note
confidence: high

research_problem:
Systematically investigate reproducibility barriers in reinforcement-learning recommender systems.

method_or_system_type:
Systematic reproducibility study focused on RL recommendation research

key_findings:
- Reproducibility issues persist due to incomplete reporting and high experimental sensitivity.
- Clear protocol, hyperparameter, and environment reporting are critical.
- The reproducibility problem is significant enough to affect claim reliability.

limitations:
- RL-focused context may not transfer fully to deterministic non-RL recommenders.

relevance_to_thesis:
Strengthens observability and configuration-control justification by providing recommender-specific reproducibility evidence.

supported_architecture_layer:
- Observability and Audit Layer
- Configuration and Execution Layer

theme_mapping:
- reproducibility_in_recommenders
- evaluation_challenges

gap_implications:
Provides strong recommender-domain support for auditable execution and trace logging requirements.

design_implications:
- Capture run environment and parameterization explicitly for each experiment.
- Treat reproducibility diagnostics as part of evaluation outputs.

chapter_use_cases:
- Chapter 2
- Chapter 5

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md