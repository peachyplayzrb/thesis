id: P-016
citation_key: flexer_problem_2016
full_reference: The Problem of Limited Inter-rater Agreement in Modelling Music Similarity. Journal of New Music Research (2016). doi:10.1080/09298215.2016.1200631.
document_status: processed_paper_note
confidence: medium

research_problem:
Assess limits of computational music-similarity evaluation due to subjective human agreement.

method_or_system_type:
Empirical analysis of inter-rater agreement limits in music similarity modelling

key_findings:
- Human inter-rater agreement imposes an upper bound on similarity modelling performance.
- Music similarity should be treated as inherently subjective and approximate.
- Evaluation claims should account for agreement ceilings.

limitations:
- Focuses on similarity-modelling limits rather than full recommendation pipelines.

relevance_to_thesis:
Directly informs feature-processing and scoring interpretation limits in thesis evaluation.

supported_architecture_layer:
- Feature Processing Layer
- Deterministic Candidate Scoring Engine

theme_mapping:
- feature_engineering_music
- evaluation_challenges

design_implications:
- Frame score outputs as approximations, not objective ground truth.
- Include limitation discussion tied to subjective similarity.

chapter_use_cases:
- Chapter 2
- Chapter 3 (where relevant)

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md
