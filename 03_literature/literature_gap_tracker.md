# Literature Gap Tracker

DOCUMENT STATUS: active gap tracker
CONFIDENCE: medium
ROLE: evidence-calibrated gap statement
SOURCE: chapter3 sheet + legacy literature extraction

## Current Gap Statement
Existing recommender literature strongly addresses accuracy and increasingly addresses explainability, but there is still limited system-level guidance on engineering deterministic, inspectable, and user-controllable playlist-generation pipelines that combine cross-source preference ingestion, transparent scoring, and audit-grade observability.

## Supporting Evidence
- Literature repeatedly reports opacity in complex recommender models and tensions between accuracy and interpretability.
- Explainability work often focuses on post-hoc explanations rather than faithful transparency-by-design.
- Music recommendation introduces playlist-level challenges (coherence/diversity/ordering) beyond top-N ranking.
- The architecture emphasis on inspectable deterministic stages maps to a comparatively under-specified engineering space.
- P-001 and P-002 reinforce that explanation/evaluation objectives must be explicitly designed, not assumed.
- P-005 reinforces that music recommendation requires treatment of sequence/playlist and context complexity.
- P-006 strengthens the content-layer and challenge framing for music recommendation design choices.
- P-007 provides direct support for feature-based, interpretable preference modelling via semantic audio descriptors.
- P-008 and P-009 reinforce that playlist continuation needs explicit candidate/sequence handling beyond naive ranking.
- P-010 strengthens the need for quantitative explanation evaluation protocols.
- P-011, P-012, and P-013 strengthen the position that architecture choices are context-dependent and must be goal-aligned.
- P-014, P-015, P-021, and P-023 strengthen user-facing transparency and trust design/evaluation requirements.
- P-016 and P-025 strengthen feature/similarity-method rigor and indicate metric-choice sensitivity.
- P-017 and P-028 strengthen playlist sequencing and continuation-level design requirements.
- P-018 and P-024 strengthen the trade-off framing between richer hybrid/multimodal performance and explainability complexity.
- P-019, P-020, and P-026 strengthen context, mood, and user-signal grounded controllability requirements in music recommendation.
- P-029 and P-030 provide direct entity-resolution methodology support for metadata fallback matching pipeline design.
- P-031 adds alignment-method alternatives and complexity trade-off framing for difficult matching scenarios.
- P-032, P-033, and P-034 provide recommender-specific reproducibility/accountability evidence, strengthening observability and execution-trace requirements.
- P-041 provides direct Music4All dataset grounding for thesis corpus selection.
- P-042 adds modern music-domain explainability evidence reinforcing mechanism-linked transparency goals.
- P-043 adds context-aware controllability evidence relevant to parameterized preference modeling discussion.
- P-044, P-045, and P-047 strengthen comparator-context pressure from modern multimodal/deep music models.
- P-046 adds evaluation-rigor cautions about benchmark quality and cross-dataset transfer in music tasks.
- P-050 adds third-party large-scale music preference/recommender dataset evidence useful for heterogeneity-aware evaluation framing.
- P-051 adds complementary music-domain timbre-similarity modeling evidence.
- P-052 and P-053 add implementation-level reproducibility framework/evidence support for recommender evaluation pipelines.
- P-054 adds diversity/filter-bubble evidence relevant to beyond-accuracy music-consumption interpretation.
- P-055 strengthens practical-value-aware recommender evaluation framing beyond metric-only interpretation.
- P-056 adds supplementary evaluation-method perspective from POI recommender literature with explicit domain-transfer caveat.
- P-057 strengthens current recommender evaluation-practice and reporting-rigor evidence.
- P-058 strengthens comparator-context evidence on modern self-supervised recommender method complexity and performance pressure.
- P-059 strengthens playlist-continuation benchmark synthesis evidence from challenge-level result analysis.
- P-060 adds team-level APC method composition evidence (candidate generation, collaborative components, rank fusion).
- P-061 adds direct playlist-generation survey and evaluation-design evidence, including popularity-effect cautions.
- P-062 adds large-scale music benchmark challenge context for baseline/protocol-aware interpretation.
- P-063 adds historical large-scale music dataset context support (secondary, task-transfer bounded).

## Challenging Evidence
- Existing explainable and hybrid recommender work may partially cover some proposed mechanisms.
- Deterministic feature-based systems may underperform in preference capture relative to richer ML approaches.
- Prior transparent user-model and control-oriented interface studies may reduce novelty if not differentiated clearly.
- P-003 shows explanation personalization can hurt effectiveness despite improving satisfaction, challenging simplistic transparency assumptions.
- P-004 shows controllability benefits are user-dependent, challenging one-size-fits-all control design.
- P-008 and P-009 indicate hybrid methods can yield strong continuation performance, challenging claims that deterministic transparency-first designs are universally superior.
- P-018, P-024, P-027, and P-028 further challenge deterministic-only assumptions by showing strong momentum and effectiveness of hybrid/neural methods.
- P-016 indicates ceiling effects in similarity modeling against human judgment, challenging overconfident claims about deterministic feature similarity precision.
- P-031 indicates stronger but more complex neural matching alternatives, challenging deterministic alignment simplicity claims.
- P-044, P-045, and P-047 reinforce that high-performing modern music models are often complex and less inspectable, challenging simplistic deterministic-superiority narratives.
- P-054 reinforces diversity-effect complexity in online music consumption, challenging simplistic one-metric evaluation narratives.
- P-056 is domain-shifted (POI), so it cannot be used as direct music-system evidence.
- P-058 reinforces competitive pressure from high-performing complex models, challenging deterministic-superiority narratives.

## Current Confidence
medium

## RQ Title Alignment Status
aligned

## Changes Since Last Review
- Added architecture-informed gap implications based on ingested Chapter 3 design sheet.
- Added caution that novelty claim depends on clear system-level integration argument, not single mechanism novelty.
- Added direct evidence from P-001 to P-005 processed from original BibTeX/PDF sources.
- Refined risk posture: controllability and explainability gains are conditional on careful design and evaluation.
- Added targeted evidence from P-006 to P-010 to strengthen weak architecture-justification layers.
- Refined gap position: contribution should emphasize transparent deterministic engineering rationale and evaluation rigor, not raw playlist performance superiority.
- Added remaining resource-pack evidence from P-011 to P-028 and recalibrated support/challenge balance.
- Refined gap interpretation: novelty should be positioned as transparent and controllable system integration with auditable behavior, not as a universal performance claim.
- Added targeted gap-closing evidence from P-029 to P-034 for alignment-method design and recommender reproducibility/accountability.
- Recalibrated weak-layer status: observability support is now stronger in recommender context; track-alignment evidence improved but remains only partially music-specific.
- Added Music4All bundle ingestion (P-041 to P-049) with keep/support screening and thesis-scope relevance filtering.
- Added new-bundle ingestion (P-050 to P-054) with duplicates/exclusions handled and protocol-linked note/QC updates.
- Added newest local-file ingestion (P-055 to P-058) and linked evidence to evaluation-rigor and comparator-context claims.
- Added APC benchmark bundle ingestion (P-059 to P-060) and linked challenge/method-composition evidence into Chapter 2 and QC maps.
- Added playlist-evaluation and benchmark-context extensions (P-061 to P-063) with bounded transfer notes.

## Research Gap Implications (For Design)
- Prioritize faithful explanation generation from actual scoring traces.
- Justify why deterministic architecture is chosen for thesis goals, not as universal best model.
- Define measurable controllability outcomes (parameter sensitivity and influence-track effect).
- Define observability minimum set required to support reproducibility claims.

## Actions Required
- Run a focused external search for music-domain ISRC/metadata alignment reliability and ambiguity/error-rate studies (still under-supported).
- Seek one additional recommender pipeline logging/schema source for triangulation (gap improved by P-052 Elliot framework).
- Compare deterministic alignment design against one neural matching baseline in a requirement-trade-off table (inspectability vs performance complexity).
- Add one music-domain study that compares similarity metrics under playlist-generation objectives.
- Add one independent third-party study using Music4All (or comparable corpus) for recommendation benchmarking to strengthen external dataset-choice validation.

## Last Reviewed
2026-03-14

## Processed Papers Snapshot (2026-03-14)
- P-001 `zhang_explainable_2020` (strengthens explainability-method framing)
- P-002 `tintarev_survey_2007` (strengthens evaluation beyond accuracy)
- P-003 `tintarev_evaluating_2012` (adds evaluation trade-off caution)
- P-004 `jin_effects_2020` (strengthens controllability with user-variation caveat)
- P-005 `schedl_current_2018` (strengthens music-domain challenge framing)
- P-006 `deldjoo_content-driven_2024` (strengthens content-layer and challenge framing)
- P-007 `bogdanov_semantic_2013` (strengthens feature and preference representation support)
- P-008 `vall_feature-combination_2019` (strengthens playlist continuation candidate handling context)
- P-009 `ferraro_automatic_2018` (adds modular playlist continuation benchmark context)
- P-010 `nauta_anecdotal_2023` (strengthens quantitative explainability evaluation posture)
- P-011 `adomavicius_toward_2005` (strengthens recommender foundations and design trade-off framing)
- P-012 `lu_recommender_2015` (strengthens application-context framing for recommender architecture)
- P-013 `roy_systematic_2022` (strengthens modern taxonomy and trend grounding)
- P-014 `tsai_explaining_2018` (strengthens explainable interface design principles)
- P-015 `balog_transparent_2019` (strengthens scrutable transparent user-model grounding)
- P-016 `flexer_problem_2016` (adds limits/caution in music similarity modeling)
- P-017 `neto_algorithmic_2023` (strengthens sequence-aware playlist assembly rationale)
- P-018 `liu_multimodal_2025` (strengthens multimodal trade-off framing)
- P-019 `assuncao_considering_2022` (strengthens emotion/context requirements in music recommendation)
- P-020 `andjelkovic_moodplay_2019` (strengthens interactive controllability evidence)
- P-021 `knijnenburg_explaining_2012` (strengthens user-experience explanation evaluation framing)
- P-022 `lopes_xai_2022` (strengthens XAI evaluation and observability-related methodology framing)
- P-023 `afroogh_trust_2024` (strengthens trust and adoption framing for transparent systems)
- P-024 `cano_hybrid_2017` (strengthens hybrid baseline comparison requirements)
- P-025 `fkih_similarity_2022` (strengthens metric-selection rigor for deterministic scoring)
- P-026 `bo_shao_music_2009` (adds feature plus access-pattern hybrid grounding in music recommendation)
- P-027 `he_neural_2017` (adds strong neural baseline pressure context)
- P-028 `gatzioura_hybrid_2019` (strengthens hybrid playlist continuation baseline context)
- P-029 `allam_improved_2018` (strengthens entity-resolution pipeline design for metadata fallback matching)
- P-030 `papadakis_blocking_2021` (strengthens blocking/filtering evidence for scalable alignment)
- P-031 `barlaug_neural_2021` (adds alignment-method trade-off context via neural entity matching)
- P-032 `beel_towards_2016` (strengthens recommender reproducibility grounding)
- P-033 `bellogin_improving_2021` (strengthens accountability-through-reproducibility rationale)
- P-034 `cavenaghi_systematic_2023` (strengthens recommender reproducibility risk evidence)
- P-041 `pegoraro_santana_music4all_2020` (strengthens canonical corpus justification)
- P-042 `sotirou_musiclime_2025` (strengthens modern music explainability context)
- P-043 `liu_aggregating_2025` (strengthens context-aware controllability framing)
- P-044 `ru_improving_2023` (adds multimodal comparator pressure context)
- P-045 `moysis_music_2023` (adds broad deep-music-method landscape context)
- P-046 `kang_are_2025` (adds benchmark and evaluation-quality caution context)
- P-047 `zhu_muq_2025` (adds advanced representation-learning comparator context)
- P-048 `knox_loss_2021` (adds tertiary task-transfer caution context)
- P-049 `pandeya_multi-modal_2021` (adds supplementary multimodal trend context)
- P-050 `schedl_investigating_2017` (adds third-party large-scale music preference/recommender dataset context)
- P-051 `siedenburg_modeling_2017` (adds complementary music similarity modeling evidence)
- P-052 `anelli_elliot_2021` (adds implementation-level reproducible evaluation framework support)
- P-053 `betello_reproducible_2025` (adds recent reproducibility and protocol-standardization evidence)
- P-054 `shakespeare_reframing_2025` (adds diversity/filter-bubble interpretation context in music consumption)
- P-055 `jannach_measuring_2019` (strengthens practical-value-aware evaluation interpretation)
- P-056 `sanchez_pointofinterest_2022` (adds transfer-level evaluation-method support with POI domain caveat)
- P-057 `bauer_exploring_2024` (strengthens modern recommender evaluation-practice and protocol-reporting rigor support)
- P-058 `yu_self_supervised_2024` (adds comparator-context evidence for self-supervised recommender complexity/performance trade-offs)
- P-059 `zamani_analysis_2019` (adds challenge-level APC benchmark and method-pattern synthesis)
- P-060 `teinemaa_composition_2018` (adds team-level APC implementation evidence from Team Latte report)
- P-061 `bonnin_automated_2015` (adds playlist-generation survey/evaluation-design and popularity-effect evidence)
- P-062 `mcfee_million_2012` (adds large-scale benchmark protocol/baseline interpretation context)
- P-063 `bertin_mahieux_million_2011` (adds historical large-scale dataset context support with bounded transfer)
