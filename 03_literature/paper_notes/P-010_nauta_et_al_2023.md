id: P-010
citation_key: nauta_anecdotal_2023
full_reference: Nauta, M., Trienes, J., Pathak, S., Nguyen, E., Peters, M., Schmitt, Y., Schlotterer, J., Van Keulen, M., and Seifert, C. (2023) From Anecdotal Evidence to Quantitative Evaluation Methods: A Systematic Review on Evaluating Explainable AI. ACM Computing Surveys, 55(13s), 1-42. doi:10.1145/3583558.
document_status: processed_paper_note
confidence: medium

research_problem:
How explainable AI systems are evaluated and which quantitative evaluation methods are used beyond anecdotal evidence.

method_or_system_type:
Systematic review of XAI evaluation practice and metrics taxonomy.

key_findings:
- Many XAI studies rely on anecdotal evaluation; quantitative methods are needed for robust validation.
- Multi-property evaluation framing is required rather than single binary explainability judgement.
- Offers structured metric perspective useful for reproducible evaluation design.

limitations:
- Not recommender-specific; transfer to music recommender context requires adaptation.
- Does not prescribe recommender logging schema directly.

relevance_to_thesis:
Strengthens observability/audit and configuration-execution evaluation design by supporting quantified explanation assessment.

supported_architecture_layer:
- Observability and Audit Layer
- Configuration and Execution Layer
- Output and Explanation Layer

theme_mapping:
- evaluation_of_explainable_systems
- quantitative_xai_evaluation
- reproducibility_of_explanation_assessment

design_implications:
- Avoid anecdotal-only explanation claims; include explicit quantitative checks where feasible.
- Record evaluation configuration and outputs to enable comparison and replay.

chapter_use_cases:
- Chapter 2: explainability evaluation methodology.
- Chapter 5: quantitative interpretation of transparency results.

linked_files:
- 00_admin/evaluation_plan.md
- 05_design/literature_architecture_mapping.md
- 09_quality_control/claim_evidence_map.md
