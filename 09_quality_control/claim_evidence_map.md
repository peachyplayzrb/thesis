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
- Source: P-005 (`schedl_current_2018`), P-039 (`kowald_support_2021`), P-050 (`schedl_investigating_2017`), P-054 (`shakespeare_reframing_2025`)
- Exact support summary: Core survey and empirical studies reinforce that music-consumption heterogeneity and diversity effects complicate single-objective ranking assumptions.
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
- Source: P-006 (`deldjoo_content-driven_2024`), P-041 (`pegoraro_santana_music4all_2020`)
- Exact support summary: Survey evidence identifies challenge categories and content layers; Music4All dataset paper supports practical multi-signal corpus availability for content-driven experimentation.
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
- Source: P-008 (`vall_feature-combination_2019`), P-009 (`ferraro_automatic_2018`), P-059 (`zamani_analysis_2019`), P-060 (`teinemaa_composition_2018`)
- Exact support summary: Playlist continuation studies, challenge-level synthesis, and team-level implementation reports consistently indicate that multi-component candidate/scoring composition materially affects continuation quality.
- Confidence: medium
- Theme: playlist_generation
- Used in chapter: Chapter 2, Chapter 3
- Needs stronger citation?: no (bounded caveat retained: direct deterministic-versus-hybrid controlled comparison remains limited)
- Conflicting sources?: none identified in current set

## C-CLM-022
- Claim: Challenge-level APC evidence supports protocol-aware interpretation of leaderboard outcomes rather than model-family-only conclusions.
- Source: P-059 (`zamani_analysis_2019`), P-061 (`bonnin_automated_2015`), P-055 (`jannach_measuring_2019`), P-057 (`bauer_exploring_2024`)
- Exact support summary: Challenge and playlist-survey evidence plus evaluation-practice literature show that outcomes are sensitive to setup, metric framing, popularity effects, and method composition; interpretation must remain protocol-aware.
- Confidence: high
- Theme: benchmarking_and_protocol_rigor
- Used in chapter: Chapter 2, Chapter 5
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-023
- Claim: Music recommendation benchmark outcomes should be interpreted with baseline/protocol awareness because dataset and challenge setup can materially affect reported performance.
- Source: P-062 (`mcfee_million_2012`), P-059 (`zamani_analysis_2019`), P-057 (`bauer_exploring_2024`)
- Exact support summary: Large-scale music benchmark and challenge analyses, aligned with modern evaluation-practice evidence, indicate that reported improvements depend on benchmark protocol and baseline context.
- Confidence: medium-high
- Theme: benchmarking_and_protocol_rigor
- Used in chapter: Chapter 2, Chapter 5
- Needs stronger citation?: no
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
- Source: P-011 (`adomavicius_toward_2005`), P-012 (`lu_recommender_2015`), P-013 (`roy_systematic_2022`), P-024 (`cano_hybrid_2017`), P-038 (`herlocker_evaluating_2004`), P-055 (`jannach_measuring_2019`)
- Exact support summary: Broad surveys show method-family trade-offs; foundational and later evaluation-focused work supports explicit objective/metric alignment and practical-value framing rather than one-size-fits-all assumptions.
- Confidence: high
- Theme: recommender_foundations
- Used in chapter: Chapter 2, Chapter 3
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-011
- Claim: Transparent and scrutable recommendation interfaces require explicit user-facing design principles and user-experience evaluation.
- Source: P-014 (`tsai_explaining_2018`), P-015 (`balog_transparent_2019`), P-021 (`knijnenburg_explaining_2012`), P-023 (`afroogh_trust_2024`), P-042 (`sotirou_musiclime_2025`)
- Exact support summary: Classical RS explanation studies and modern music-domain explainability evidence jointly support transparent and inspectable explanation design.
- Confidence: medium
- Theme: transparency_and_scrutability
- Used in chapter: Chapter 2, Chapter 3, Chapter 5
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-012
- Claim: Music similarity has inherent human-agreement limits, so deterministic similarity-based ranking should include uncertainty-aware interpretation.
- Source: P-016 (`flexer_problem_2016`), P-051 (`siedenburg_modeling_2017`)
- Exact support summary: Music-similarity studies show perceptual limits and multi-factor dependence, supporting cautious interpretation of deterministic similarity scores.
- Confidence: medium
- Theme: feature_engineering_music
- Used in chapter: Chapter 3, Chapter 5
- Needs stronger citation?: maybe (one more playlist-objective metric comparison would further strengthen)
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
- Source: P-018 (`liu_multimodal_2025`), P-024 (`cano_hybrid_2017`), P-027 (`he_neural_2017`), P-028 (`gatzioura_hybrid_2019`), P-044 (`ru_improving_2023`), P-045 (`moysis_music_2023`), P-047 (`zhu_muq_2025`), P-058 (`yu_self_supervised_2024`)
- Exact support summary: Existing surveys and model papers are reinforced by recent music-domain and self-supervised recommender evidence that shows strong performance momentum alongside higher complexity and lower inspectability.
- Confidence: medium
- Theme: multimodal_and_hybrid_tradeoff
- Used in chapter: Chapter 2, Chapter 3
- Needs stronger citation?: maybe (add one direct transparency-vs-performance empirical comparison)
- Conflicting sources?: none identified in current set

## C-CLM-015
- Claim: User controllability in music recommendation is feasible through interactive preference signals such as mood-based and parameterized controls.
- Source: P-020 (`andjelkovic_moodplay_2019`), P-004 (`jin_effects_2020`), P-043 (`liu_aggregating_2025`)
- Exact support summary: Interactive controllability studies plus context-aware music recommendation evidence support exposing controllable preference/context signals.
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
- Source: P-029 (`allam_improved_2018`), P-030 (`papadakis_blocking_2021`), P-036 (`elmagarmid_duplicate_2007`), P-035 (`binette_almost_2022`)
- Exact support summary: Foundational and modern entity-resolution evidence consistently shows that multi-stage blocking/filtering/matching design drives both linkage quality and computational feasibility.
- Confidence: high
- Theme: entity_resolution
- Used in chapter: Chapter 3
- Needs stronger citation?: maybe (add one music-domain identity-resolution benchmark)
- Conflicting sources?: none identified in current set

## C-CLM-018
- Claim: Recommender-system accountability depends on reproducibility controls, including explicit protocol/configuration reporting and traceable experiment context.
- Source: P-032 (`beel_towards_2016`), P-033 (`bellogin_improving_2021`), P-034 (`cavenaghi_systematic_2023`), P-037 (`ferrari_dacrema_troubling_2021`), P-040 (`zhu_bars_2022`), P-052 (`anelli_elliot_2021`), P-053 (`betello_reproducible_2025`)
- Exact support summary: Recommender reproducibility analyses plus framework papers jointly support explicit protocol reporting, standardized preprocessing, configuration traceability, and comparable evaluation pipelines as prerequisites for accountable claims.
- Confidence: high
- Theme: reproducibility_in_recommenders
- Used in chapter: Chapter 2, Chapter 5
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-020
- Claim: Open, standardized benchmark frameworks improve comparability and reproducibility in recommender evaluation, but require careful protocol reporting to avoid false comparability.
- Source: P-040 (`zhu_bars_2022`), P-037 (`ferrari_dacrema_troubling_2021`), P-038 (`herlocker_evaluating_2004`), P-052 (`anelli_elliot_2021`), P-053 (`betello_reproducible_2025`), P-057 (`bauer_exploring_2024`)
- Exact support summary: BARS and Elliot operationalize benchmarking infrastructure, while reproducibility analyses and recent evaluation-landscape evidence show that protocol and preprocessing specification are necessary for valid cross-study comparison.
- Confidence: high
- Theme: benchmarking_and_protocol_rigor
- Used in chapter: Chapter 4, Chapter 5
- Needs stronger citation?: no
- Conflicting sources?: none identified in current set

## C-CLM-021
- Claim: Choosing Music4All as canonical corpus is defensible for this thesis because it provides multi-signal music metadata/audio resources suitable for reproducible content-driven experimentation.
- Source: P-041 (`pegoraro_santana_music4all_2020`), P-006 (`deldjoo_content-driven_2024`), P-044 (`ru_improving_2023`), P-063 (`bertin_mahieux_million_2011`)
- Exact support summary: Dataset paper documents Music4All resource breadth, content-driven survey frames why multi-signal corpora are relevant, independent third-party model work confirms Music4All usage as benchmark context, and historical MSD evidence adds supplementary dataset-scale context (with task-transfer caveat).
- Confidence: medium
- Theme: dataset_foundation
- Used in chapter: Chapter 2, Chapter 3
- Needs stronger citation?: no (for corpus defensibility claim; task-transfer caveat still applies)
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

