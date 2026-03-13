# Claim Evidence Map

## C-CLM-001
- Claim: Accuracy-only evaluation is insufficient for recommender systems when transparency and user understanding matter.
- Source: P-002 (`tintarev_survey_2007`), P-003 (`tintarev_evaluating_2012`), P-001 (`zhang_explainable_2020`)
- Exact support summary: These works explicitly discuss explanation aims and evaluation dimensions beyond predictive accuracy.
- Confidence: high
- Theme: explainable_recommenders
- Used in chapter: Chapter 2, Chapter 5
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-002
- Claim: Explanation goals can conflict, so evaluation must declare which objective is being optimized.
- Source: P-003 (`tintarev_evaluating_2012`)
- Exact support summary: The paper reports trade-offs (for example satisfaction vs effectiveness) and methodological constraints.
- Confidence: high
- Theme: evaluation_of_explainable_systems
- Used in chapter: Chapter 2, Chapter 5
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-003
- Claim: Control-oriented music recommender interfaces should account for user differences rather than one-size-fits-all controls.
- Source: P-004 (`jin_effects_2020`)
- Exact support summary: Experimental results indicate user characteristics (for example musical sophistication) influence acceptance and diversity outcomes.
- Confidence: medium
- Theme: controllability
- Used in chapter: Chapter 3
- Needs stronger citation?: maybe (add at least one replication/complement study)
- Conflicting sources?: none identified in current set

## C-CLM-004
- Claim: Music recommender systems face playlist/sequence and context-related challenges not captured by simple item-level ranking formulations.
- Source: P-005 (`schedl_current_2018`)
- Exact support summary: Survey identifies domain-specific challenges and future research directions in music recommendation.
- Confidence: medium
- Theme: music_recommenders
- Used in chapter: Chapter 2, Chapter 3
- Needs stronger citation?: maybe (add one playlist-focused empirical paper)
- Conflicting sources?: none identified in current set

## C-CLM-005
- Claim: Explainable recommendation includes both post-hoc and inherently explainable approaches; this distinction is critical for architecture decisions.
- Source: P-001 (`zhang_explainable_2020`)
- Exact support summary: Survey taxonomy distinguishes explanation mechanisms and information sources with different implications.
- Confidence: high
- Theme: transparency_by_design
- Used in chapter: Chapter 2, Chapter 3
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-006
- Claim: Content-driven music recommendation requires explicit handling of multiple content layers and still faces open challenges in transparency, sequence recommendation, and efficiency.
- Source: P-006 (`deldjoo_content-driven_2024`)
- Exact support summary: Survey of 55 studies proposes onion-model content layers and identifies persistent challenge set.
- Confidence: high
- Theme: content_driven_music_recommendation
- Used in chapter: Chapter 2, Chapter 3
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-007
- Claim: Audio-semantic descriptor approaches can support interpretable preference modelling in content-based music recommendation.
- Source: P-007 (`bogdanov_semantic_2013`)
- Exact support summary: Demonstrates semantic user representation built from audio-derived descriptors with positive preliminary evaluation.
- Confidence: medium
- Theme: feature_engineering_music
- Used in chapter: Chapter 3
- Needs stronger citation?: maybe (add newer replication/contextual paper)
- Conflicting sources?: none identified in current set

## C-CLM-008
- Claim: Playlist continuation quality benefits from explicit feature-aware candidate handling, especially under long-tail item distributions.
- Source: P-008 (`vall_feature-combination_2019`), P-009 (`ferraro_automatic_2018`)
- Exact support summary: Hybrid playlist continuation studies report performance gains from combining collaborative/context/audio features.
- Confidence: medium
- Theme: playlist_generation
- Used in chapter: Chapter 2, Chapter 3
- Needs stronger citation?: yes (add deterministic playlist-continuation evidence)
- Conflicting sources?: none identified in current set

## C-CLM-009
- Claim: Explainability evaluation should use explicit quantitative methods where possible, not anecdotal-only assessment.
- Source: P-010 (`nauta_anecdotal_2023`), P-003 (`tintarev_evaluating_2012`)
- Exact support summary: Both works emphasize structured evaluation goals/methods and caution against simplistic evaluation claims.
- Confidence: high
- Theme: evaluation_of_explainable_systems
- Used in chapter: Chapter 5
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-010
- Claim: Recommender-system design is context-dependent; architecture choices should be justified against thesis goals rather than assuming one universal best model.
- Source: P-011 (`adomavicius_toward_2005`), P-012 (`lu_recommender_2015`), P-013 (`roy_systematic_2022`), P-024 (`cano_hybrid_2017`)
- Exact support summary: Broad surveys consistently show method families with scenario-dependent strengths and trade-offs.
- Confidence: high
- Theme: recommender_foundations
- Used in chapter: Chapter 2, Chapter 3
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-011
- Claim: Transparent and scrutable recommendation interfaces require explicit user-facing design principles and user-experience evaluation.
- Source: P-014 (`tsai_explaining_2018`), P-015 (`balog_transparent_2019`), P-021 (`knijnenburg_explaining_2012`), P-023 (`afroogh_trust_2024`)
- Exact support summary: These papers collectively connect interface design, user modeling transparency, and trust-related outcomes.
- Confidence: medium
- Theme: transparency_and_scrutability
- Used in chapter: Chapter 2, Chapter 3, Chapter 5
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-012
- Claim: Music similarity has inherent human-agreement limits, so deterministic similarity-based ranking should include uncertainty-aware interpretation.
- Source: P-016 (`flexer_problem_2016`)
- Exact support summary: The study reports limited inter-rater agreement, constraining achievable agreement with human judgments.
- Confidence: medium
- Theme: feature_engineering_music
- Used in chapter: Chapter 3, Chapter 5
- Needs stronger citation?: yes (add one complementary similarity-evaluation paper)
- Conflicting sources?: none identified in current set

## C-CLM-013
- Claim: Playlist assembly should model sequence-level structure, not only item relevance.
- Source: P-017 (`neto_algorithmic_2023`), P-028 (`gatzioura_hybrid_2019`), P-008 (`vall_feature-combination_2019`)
- Exact support summary: Sequence regularity evidence plus playlist-continuation studies support explicit playlist-level constraints.
- Confidence: medium
- Theme: playlist_generation
- Used in chapter: Chapter 3
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-014
- Claim: Hybrid and multimodal recommenders can improve performance, but add complexity that can reduce inspectability unless explicitly managed.
- Source: P-018 (`liu_multimodal_2025`), P-024 (`cano_hybrid_2017`), P-027 (`he_neural_2017`), P-028 (`gatzioura_hybrid_2019`)
- Exact support summary: Survey and model papers indicate performance gains from richer models while increasing modeling and explanation complexity.
- Confidence: medium
- Theme: multimodal_and_hybrid_tradeoff
- Used in chapter: Chapter 2, Chapter 3
- Needs stronger citation?: maybe (add one direct transparency-vs-performance empirical comparison)
- Conflicting sources?: none identified in current set

## C-CLM-015
- Claim: User controllability in music recommendation is feasible through interactive preference signals such as mood-based and parameterized controls.
- Source: P-020 (`andjelkovic_moodplay_2019`), P-004 (`jin_effects_2020`)
- Exact support summary: Interactive studies show control mechanisms can affect perceived recommendation experience and outcomes.
- Confidence: medium
- Theme: controllability_in_music_rs
- Used in chapter: Chapter 3, Chapter 5
- Needs stronger citation?: maybe (add one additional replication/modern system paper)
- Conflicting sources?: none identified in current set

## C-CLM-016
- Claim: Similarity-metric choice materially affects recommender behavior, so metric selection must be explicit and justified in deterministic scoring pipelines.
- Source: P-025 (`fkih_similarity_2022`)
- Exact support summary: Review and experiments compare similarity measures and show non-trivial performance differences across settings.
- Confidence: medium
- Theme: similarity_measures
- Used in chapter: Chapter 3, Chapter 5
- Needs stronger citation?: yes (add one music-domain metric comparison if available)
- Conflicting sources?: none identified in current set

## C-CLM-017
- Claim: Metadata-based track alignment should be engineered as a staged entity-resolution pipeline (blocking, candidate filtering, and final matching) rather than a single fuzzy-match step.
- Source: P-029 (`allam_improved_2018`), P-030 (`papadakis_blocking_2021`)
- Exact support summary: Entity-resolution literature shows that blocking/filtering strategy strongly affects both linkage quality and computational feasibility.
- Confidence: high
- Theme: entity_resolution
- Used in chapter: Chapter 3
- Needs stronger citation?: maybe (add one music-domain identity-resolution benchmark)
- Conflicting sources?: none identified in current set

## C-CLM-018
- Claim: Recommender-system accountability depends on reproducibility controls, including explicit protocol/configuration reporting and traceable experiment context.
- Source: P-032 (`beel_towards_2016`), P-033 (`bellogin_improving_2021`), P-034 (`cavenaghi_systematic_2023`)
- Exact support summary: Recommender-focused reproducibility studies report instability and emphasize transparent reporting as prerequisite for reliable claims and accountability.
- Confidence: high
- Theme: reproducibility_in_recommenders
- Used in chapter: Chapter 2, Chapter 5
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-019
- Claim: Advanced alignment methods (for example neural entity matching) may improve difficult matching cases, but they increase complexity and can reduce inspectability unless additional traceability controls are added.
- Source: P-031 (`barlaug_neural_2021`), P-030 (`papadakis_blocking_2021`)
- Exact support summary: Surveys highlight method trade-offs between matching capability, implementation complexity, and evaluation rigor.
- Confidence: medium
- Theme: alignment_method_tradeoffs
- Used in chapter: Chapter 3, Chapter 5
- Needs stronger citation?: maybe (add direct music-track identity comparison across deterministic vs neural matching)
- Conflicting sources?: none identified in current set

