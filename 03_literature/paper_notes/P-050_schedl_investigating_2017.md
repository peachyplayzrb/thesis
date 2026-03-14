id: P-050
citation_key: schedl_investigating_2017
full_reference: Investigating country-specific music preferences and music recommendation algorithms with the LFM-1b dataset. International Journal of Multimedia Information Retrieval (2017). doi:10.1007/s13735-017-0118-y.
document_status: processed_paper_note
confidence: medium

research_problem:
Analyze large-scale listening behavior and country-specific music preference patterns, with recommendation baseline implications.

method_or_system_type:
Music recommender dataset analysis and baseline recommendation study

key_findings:
- Large-scale listening logs reveal substantial preference heterogeneity across user groups and countries.
- Dataset-level baselines are useful for reproducible comparison and future method evaluation.
- Preference distribution analysis supports nuanced evaluation beyond single global metrics.

limitations:
- Uses LFM-1b rather than Music4All.
- Focus is analysis/baseline context, not deterministic playlist-pipeline architecture.

relevance_to_thesis:
Supports external benchmark and heterogeneity framing in music recommendation evaluation discussion.

supported_architecture_layer:
- Evaluation and Comparator Framing
- Preference Modeling Layer

theme_mapping:
- music_recommenders
- benchmarking_and_protocol_rigor

gap_implications:
Adds third-party music-recommendation dataset evidence for evaluation framing and user-preference diversity discussions.

design_implications:
- Keep evaluation reporting explicit about dataset assumptions and user heterogeneity.
- Avoid overgeneralizing from single cohort behavior.

chapter_use_cases:
- Chapter 2
- Chapter 5

linked_files:
- 03_literature/literature_gap_tracker.md
- 09_quality_control/citation_checks.md
