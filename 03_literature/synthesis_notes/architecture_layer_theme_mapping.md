# Architecture Layer To Literature Theme Mapping

DOCUMENT STATUS: working synthesis note
CONFIDENCE: medium
ROLE: mapping draft
SOURCE: chapter 3 sheet + legacy literature review

## Layer -> Potential Themes
1. User Interaction Layer -> `controllability`, `scrutability`, `explainable_interfaces`
2. Data Ingestion Layer -> `cross_source_preference_data`, `data_provenance`, `adapter_reliability`
3. Track Alignment Layer -> `entity_resolution`, `cross_platform_track_matching`, `isrc_reliability`
4. Preference Modelling Layer -> `content_based_profiles`, `single_user_modelling`, `feature_based_preference_representation`
5. Candidate Generation Layer -> `retrieval_efficiency`, `candidate_filtering_bias`, `coverage_vs_precision`
6. Feature Processing Layer -> `feature_engineering_music`, `normalization_effects`, `missing_data_handling`
7. Deterministic Scoring Layer -> `interpretable_scoring`, `similarity_measures`, `transparency_by_design`
8. Playlist Assembly Layer -> `playlist_coherence`, `diversity_controls`, `sequence_quality`
9. Output And Explanation Layer -> `explainability_faithfulness`, `user_trust`, `human_centered_xai`
10. Observability And Audit Layer -> `observability_in_recommenders`, `trace_logging`, `reproducibility`
11. Configuration And Execution Layer -> `experiment_reproducibility`, `parameter_sensitivity`, `run_comparability`

## Immediate Theme Candidates To Instantiate First
- `transparency.md`
- `controllability.md`
- `deterministic_systems.md`
- `music_recommenders.md`
- `evaluation_of_explainable_systems.md`

Guardrail: create each theme file only after at least 3 papers can be linked.