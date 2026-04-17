id: P-012
citation_key: lu_recommender_2015
full_reference: Recommender system application developments: A survey. Decision Support Systems (2015). doi:10.1016/j.dss.2015.03.008.
document_status: processed_paper_note
confidence: medium

research_problem:
Synthesize application-domain trends and technical directions in recommender systems.

method_or_system_type:
Survey of recommender system application developments

key_findings:
- Shows broad domain adoption and varied system goals beyond pure prediction.
- Reinforces need to align method choice with application context.
- Highlights practical deployment constraints and evaluation variability.

limitations:
- Not specialized to music recommendation pipelines.
- Limited direct guidance for deterministic transparency mechanisms.

relevance_to_thesis:
Supports design-scoping argument that architecture should match domain constraints and thesis objectives.

supported_architecture_layer:
- Configuration and Execution Layer

theme_mapping:
- recommender_foundations
- evaluation_challenges

gap_implications:
General recommender surveys emphasize domain-dependent trade-offs without showing how transparency goals should dominate method selection in music settings; the thesis addresses that by treating music-domain transparency and controllability as first-order scope constraints.

design_implications:
- Tie architecture decisions to domain-specific objectives rather than generic best-performance claims.

chapter_use_cases:
- Chapter 2
- Chapter 3 (where relevant)

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md
