id: P-033
citation_key: bellogin_improving_2021
full_reference: Improving accountability in recommender systems research through reproducibility. User Modeling and User-Adapted Interaction (2021). doi:10.1007/s11257-021-09302-x.
document_status: processed_paper_note
confidence: high

research_problem:
Position reproducibility as a mechanism for accountability and transparency in recommender-systems research.

method_or_system_type:
Methodological paper on reproducibility-accountability linkage in recommender systems

key_findings:
- Reproducibility practices contribute directly to accountability and trustworthiness.
- Transparent reporting standards are necessary for meaningful comparison and validation.
- Engineering workflows should expose assumptions and evaluation conditions.

limitations:
- Methodological focus; limited implementation-level logging schema detail.

relevance_to_thesis:
Directly supports thesis observability and auditability rationale for inspectable recommendation pipelines.

supported_architecture_layer:
- Observability and Audit Layer
- Configuration and Execution Layer

theme_mapping:
- reproducibility_in_recommenders
- accountability

gap_implications:
Further narrows the residual observability gap at the methodological level, while leaving some instrumentation specifics open.

design_implications:
- Record assumptions, configuration, and evaluation protocol per run.
- Link outputs and explanations to reproducible run identifiers.

chapter_use_cases:
- Chapter 2
- Chapter 5

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md