id: P-053
citation_key: betello_reproducible_2025
full_reference: A Reproducible Analysis of Sequential Recommender Systems. IEEE Access (2025). doi:10.1109/ACCESS.2024.3522049.
document_status: processed_paper_note
source_index_status: screened_keep
confidence: high

research_problem:
Assess reproducibility in sequential recommender systems by standardizing preprocessing and implementation choices.

method_or_system_type:
Recommender reproducibility analysis and framework-backed comparative study

key_findings:
- Experimental configuration can strongly change conclusions about model performance.
- Standardized preprocessing and implementation reduce misleading comparisons.
- Reproducible setup is necessary for credible progress claims in recommender research.

limitations:
- Sequential-recommender context is not identical to deterministic content-based thesis pipeline.

relevance_to_thesis:
Strengthens reproducibility/accountability arguments and supports explicit configuration capture in evaluation.

supported_architecture_layer:
- Observability and Audit Layer
- Configuration and Execution Layer

theme_mapping:
- reproducibility_in_recommenders
- evaluation_challenges

gap_implications:
Further reduces reproducibility evidence risk and supports audit-grade evaluation reporting.

design_implications:
- Record preprocessing choices and parameter settings in run artifacts.
- Report configuration sensitivity impacts explicitly.

chapter_use_cases:
- Chapter 2
- Chapter 4
- Chapter 5

linked_files:
- 09_quality_control/claim_evidence_map.md
- 09_quality_control/citation_checks.md
