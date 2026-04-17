id: P-003
citation_key: tintarev_evaluating_2012
full_reference: Tintarev, N. and Masthoff, J. (2012) Evaluating the effectiveness of explanations for recommender systems. User Modeling and User-Adapted Interaction, 22(4-5), 399-439. doi:10.1007/s11257-011-9117-5.
document_status: processed_paper_note
confidence: high

research_problem:
How to evaluate recommender explanations rigorously when explanation aims can conflict.

method_or_system_type:
Methodological review plus empirical studies in recommendation domains.

key_findings:
- Explanation aims can conflict; evaluation must declare which aim is measured.
- Personalizing explanations can increase satisfaction while reducing decision effectiveness in some cases.
- Evaluation design must account for under/overestimation effects and domain dependencies.
- Distinguishes perceived vs post-consumption effectiveness and highlights metric-selection risks for explanation studies.

limitations:
- Experiments are not in music-specific recommendation settings.
- Does not prescribe a complete pipeline architecture.

relevance_to_thesis:
High relevance for defining balanced evaluation of transparency, controllability, and user outcomes.

supported_architecture_layer:
- Output and Explanation Layer
- Evaluation and Comparator Framing

theme_mapping:
- explainable_recommenders
- evaluation_of_explainable_systems
- user_satisfaction_vs_effectiveness_tradeoff

gap_implications:
Challenges simplistic assumption that more explanation detail always improves user decisions.

design_implications:
- Include both utility/effectiveness and satisfaction-style measures.
- Treat explanation personalization as a parameter requiring careful calibration.
- Include opt-out and rating-distribution checks when interpreting explanation-effect outcomes.

chapter_use_cases:
- Chapter 2: methodological caution for explanation evaluation.
- Chapter 5: interpretation of evaluation trade-offs.

linked_files:
- 03_literature/literature_gap_tracker.md
- 09_quality_control/claim_evidence_map.md
- 09_quality_control/chapter_readiness_checks.md

source_recovery_note:
- 2026-03-23: recovered text evidence from user-provided source attachment and Zotero full-text cache export; no longer treated as missing extraction input for citation hardening.
