# Chapter 2: Literature Review (Final Draft)

## 2.1 Foundations, Scope, and Thesis Positioning
Digital platforms now require users to make choices within very large catalogs. In music streaming, this means selecting from millions of tracks with limited attention and time. Recommender systems emerged as a practical response to this information-overload problem by helping users discover items they are likely to value [@adomavicius_toward_2005; @lu_recommender_2015; @roy_systematic_2022].

Foundational recommender literature frames the task as utility estimation under partial information: given sparse evidence about user preferences, infer which items are most likely to be useful [@adomavicius_toward_2005; @roy_systematic_2022].

This framing still matters because it clarifies why recommendation is not just retrieval from a database. It is an inference process shaped by data quality, feature representation, and objective choice.

For this thesis, that point is central. The target is not to propose a novel model family or to compete for state-of-the-art leaderboard performance. The target is to engineer an automated playlist pipeline whose behavior is transparent, controllable, and observable under BSc-feasible constraints. This shifts the literature question from "Which model is best overall?" to "Which design choices are most defensible for this specific objective set?"

Evaluation research supports this objective-aligned view. Recommender outcomes can be sensitive to protocol definitions, preprocessing choices, and metric framing [@herlocker_evaluating_2004; @ferrari_dacrema_troubling_2021; @anelli_elliot_2021; @bauer_exploring_2024]. A strong result in one benchmark configuration does not automatically imply the best fit for a project that prioritizes inspectability and replayability. In other words, method selection should follow contribution goals, not benchmark scores in isolation [@jannach_measuring_2019].

This objective-first framing also explains the structure of the chapter itself. The review moves from broad recommender foundations to domain-specific constraints, then narrows to the engineering decisions required by the research question. That progression is intentional: each section builds a rationale for why the artefact should be transparent, controllable, and observable by design, rather than relying on opaque optimization alone.

The chapter therefore functions as an argument chain, not just a catalogue of prior work. It treats literature as design evidence by reviewing what is known, where uncertainty remains, and what these findings imply for architecture choices in Chapter 3.

Design consequence: architecture decisions should be justified against transparency, controllability, observability, and reproducibility objectives, not accuracy claims alone.

## 2.2 Core Recommendation Paradigms and Their Trade-offs
Recommender systems are commonly described through three families: content-based, collaborative, and hybrid approaches [@adomavicius_toward_2005; @lu_recommender_2015; @cano_hybrid_2017]. The taxonomy is useful, but the literature repeatedly shows that these labels do not, by themselves, determine suitability.

Content-based methods model preference through item attributes. In music settings, this can include metadata, tags, and audio descriptors. A key strength is mechanism visibility: when the model relies on explicit features, recommendations can often be explained through those same features [@deldjoo_content-driven_2024; @bogdanov_semantic_2013].

Collaborative methods infer preference from interaction structure across users and items. They can perform strongly at scale, especially with rich interaction histories, but they may reduce direct interpretability when decision logic is encoded in latent representations [@adomavicius_toward_2005; @zhang_explainable_2020].

Hybrid approaches combine multiple signals and are often effective because they reduce weaknesses of single-family methods [@cano_hybrid_2017]. At the same time, combining components can increase reasoning complexity and make explanations harder unless interpretability controls are designed into the pipeline.

Similarity modeling illustrates these trade-offs clearly. Similarity-measure choices, including metric definitions and threshold settings, can affect neighborhood selection and ranking behavior [@fkih_similarity_2022]. These are not minor implementation details; they are mechanism-level design decisions. If metric and weighting choices are explicit, behavior can be examined and challenged. If they remain hidden defaults, explanation and control claims may weaken.

A second practical issue is data structure. Collaborative and hybrid methods often depend on richer interaction logs, while a transparent feature-based approach can remain workable when interaction history is sparse, incomplete, or unavailable for some users.

In cross-source settings, this matters because data quality is rarely uniform across all entities and stages. A method that is theoretically strong under ideal interaction density may be harder to justify when the pipeline must remain auditable under uneven input conditions. For this thesis, design defensibility under realistic data constraints is prioritized over maximizing abstract model capacity.

For this thesis, paradigm selection is therefore treated as conditional and scope-bound. Deterministic feature-based scoring is chosen because it offers clearer mechanism visibility and easier replay under the thesis objectives. This is not a claim that content-based deterministic methods are universally superior to hybrid or neural alternatives.

Design consequence: Chapter 3 should make feature selection, similarity metric choice, normalization, and weighting explicitly documented and auditable.

## 2.3 Transparency, Explainability, Controllability, and Observability
Explainable recommender research has long argued that predictive quality alone is not enough when users or evaluators need to understand and question system behavior [@tintarev_survey_2007; @tintarev_evaluating_2012; @zhang_explainable_2020]. A system can score well on ranking metrics while still failing to communicate why outputs were produced.

To keep this chapter precise, four related terms are used with distinct meanings. Transparency refers to visibility of recommendation logic. Explainability refers to understandable reasons for specific outputs. Controllability refers to user influence through explicit inputs or parameters [@tintarev_survey_2007; @balog_transparent_2019; @jin_effects_2020]. Observability, as used in this thesis, refers to run-level visibility of execution state, intermediate diagnostics, and output traces.

These distinctions matter because explanation goals often conflict. An explanation may increase trust or satisfaction without improving true user understanding [@tintarev_evaluating_2012; @nauta_anecdotal_2023]. As a result, explanation quality should not be judged by one generic criterion. It should be evaluated against declared purpose.

A further distinction is critical for thesis design: post-hoc explanation versus transparency-by-design [@zhang_explainable_2020]. Post-hoc approaches can produce plausible narratives after ranking, but those narratives are not always tightly coupled to the mechanism that generated the recommendation. This supports keeping explanations as close as possible to the actual scoring and decision process.

Interface research adds a practical constraint: faithful explanations still need to be understandable for non-expert users [@tsai_explaining_2018; @knijnenburg_explaining_2012; @afroogh_trust_2024]. In practice, this means explanation should preserve mechanism fidelity while using a representation users can interpret without advanced technical knowledge.

Controllability evidence in music recommenders supports cautious implementation. User control can improve experience, but effects vary by user characteristics and context [@jin_effects_2020; @andjelkovic_moodplay_2019; @liu_aggregating_2025]. For this reason, the thesis treats controls as explicit, bounded, and testable engineering mechanisms rather than universal behavior assumptions.

Observability connects all of these ideas. If parameters change but stage-level effects are not recorded, controllability remains nominal and explanation claims are hard to verify. For an artefact-based contribution, observability is therefore not optional instrumentation; it is part of evidence quality.

This has a direct methodological implication for evaluation. The chapter adopts a process-plus-outcome view: process evidence checks whether the system behaved as designed at each stage, while outcome evidence checks whether recommendations changed in interpretable ways after control adjustments.

This approach is well suited to BSc scope. It does not require large-scale user experiments to produce useful evidence, but it still requires disciplined reporting of inputs, intermediate effects, and final outputs. Without that trace, claims about transparency or control remain rhetorical.

Design consequence: Chapter 3 should implement mechanism-linked explanation outputs, explicit control parameters, and run-level diagnostics so that Chapter 4 can evaluate explanation fidelity and parameter sensitivity.

## 2.4 Music Recommendation and Playlist-Specific Challenges
Music recommendation is not a simple transfer of generic top-N logic. Listening is often session-based and sequential, and users evaluate not only individual songs but also transitions, pacing, repetition, and overall flow [@schedl_current_2018].

This matters because playlist quality is a sequence property as much as it is an item-relevance property [@schedl_current_2018; @bonnin_automated_2015]. A playlist with individually strong tracks can still feel poor if transitions are abrupt, artist repetition is excessive, or diversity disrupts coherence [@ferraro_automatic_2018; @vall_feature-combination_2019].

Studies on playlist continuation consistently report tensions among coherence, novelty, diversity, and ordering [@ferraro_automatic_2018; @vall_feature-combination_2019; @zamani_analysis_2019]. Improving one dimension often weakens another.

Sequencing analyses further highlight that music collections are perceived as ordered sequences rather than isolated items [@neto_algorithmic_2023].

Challenge and benchmark analyses show that outcomes can depend on protocol and method composition [@teinemaa_composition_2018; @bonnin_automated_2015; @mcfee_million_2012]. This supports cautious interpretation of performance claims: reported improvements are context-dependent and should not be detached from evaluation setup.

A second domain challenge is subjective similarity. Music-similarity research shows limited inter-rater agreement and sensitivity to framing, indicating that similarity estimates are useful approximations rather than objective truth [@flexer_problem_2016; @siedenburg_modeling_2017]. The semantic gap reinforces this: low-level computable features do not perfectly capture human concepts such as mood, nostalgia, or atmosphere [@bogdanov_semantic_2013; @deldjoo_content-driven_2024].

Context dependence makes this challenge more concrete. The same listener may prefer very different playlists for focus, commuting, exercise, or social settings, even when the underlying catalog is unchanged.

This does not mean context-aware recommendation is impossible; it means context claims should be bounded by what the system can actually observe and represent. In this thesis, that leads to a practical compromise: use explicit, inspectable proxies where possible, report contextual coverage as partial, and avoid suggesting that the system captures the full complexity of human listening intent.

These findings do not invalidate computational recommendation. Instead, they define responsible interpretation boundaries. Deterministic similarity can still be valuable as a transparent decision-support mechanism, provided claims avoid universal language and acknowledge subjective limits.

Corpus choice follows the same logic. Music4All is defensible here because it provides a multi-signal dataset with metadata, tags, lyrics, and audio-related attributes suitable for content-driven experimentation [@pegoraro_santana_music4all_2020]. Independent third-party usage in multimodal music experiments provides additional context support, while task-transfer limits remain explicit [@ru_improving_2023]. The claim is practical suitability under scope, not universal dataset optimality.

Design consequence: playlist generation should be engineered as a staged process with explicit assembly constraints, and similarity outputs should be interpreted as auditable decision support rather than ground truth.

## 2.5 Deterministic Feature-Based Design Rationale with Comparator Context
Given the thesis objectives, feature-based recommendation offers a direct practical advantage: it keeps ranking signals inspectable. When preference profiles and candidate scores are built from explicit descriptors, the system can report what contributed to each decision and how much [@bogdanov_semantic_2013; @deldjoo_content-driven_2024].

Deterministic execution adds a second advantage. Under fixed input and fixed configuration, output should be replayable. This can strengthen debugging clarity, support sensitivity analysis, and improve evidence quality because observed output changes can be attributed to explicit parameter changes [@bellogin_improving_2021].

Comparator context remains essential. Hybrid and neural recommenders can deliver strong predictive performance and capture richer interactions [@cano_hybrid_2017; @he_neural_2017; @liu_multimodal_2025; @yu_self_supervised_2024; @moysis_music_2023]. This thesis does not dismiss those methods. Instead, it prioritizes a different goal set: inspectability, controllability, observability, and reproducibility in a constrained artefact context.

Metric sensitivity is a key caveat within this choice. Similarity computation depends on explicit distance-function choices in feature space [@fkih_similarity_2022; @furini_social_2024].

Playlist-level and APC evidence also indicates that protocol and metric framing can shift comparative conclusions [@zamani_analysis_2019; @teinemaa_composition_2018; @bonnin_automated_2015]. Therefore, metric and weighting choices must be surfaced as explicit design commitments.

A bounded limitation remains: while the source set now includes direct music-domain metric-comparison evidence, broad multi-dataset isolation studies focused specifically on deterministic similarity-function effects across multiple playlist objectives are still limited. This limitation narrows generalization strength but does not block the scoped thesis argument.

Design consequence: Chapter 3 should expose score components, metric choices, and weighting controls as first-class configurable mechanisms with sensitivity testing in Chapter 4.

## 2.6 Cross-Source Alignment Reliability and Reproducibility Governance
The research question explicitly concerns cross-source music preference data, making alignment a core engineering issue. User-history records and candidate-corpus records come from different systems with different identifiers and quality profiles. Entity-resolution research supports blocking, filtering, and staged matching workflows as practical approaches for large-scale linkage [@elmagarmid_duplicate_2007; @allam_improved_2018; @papadakis_blocking_2021; @binette_almost_2022].

Within this thesis scope, ISRC-first matching with metadata fallback is consistent with that staged rationale. Exact identifier matching provides high precision when identifiers are available and clean, while fallback matching recovers additional links when identifiers are missing or inconsistent. This does not eliminate uncertainty, but it keeps uncertainty visible.

Neural entity-matching work is relevant comparator context and can improve difficult cases [@barlaug_neural_2021]. However, it also introduces additional complexity and may reduce straightforward inspectability unless extensive traceability layers are added. For this MVP, the complexity-auditability trade-off favors deterministic staged matching with explicit unmatched-case logging.

Evidence strength should still be bounded. Much alignment evidence is domain-general rather than music-specific benchmark evidence. This is an evidence-depth limitation, not a reason to abandon staged alignment, and it should remain explicit in interpretation.

Alignment uncertainty is not only a data-cleaning concern; it changes what recommendation outputs mean. If some preference records cannot be matched or are matched through weaker fallback routes, profile construction and candidate ranking inherit that uncertainty.

Treating alignment diagnostics as first-class evidence therefore improves interpretation quality. It allows later chapters to distinguish model behavior from data-linkage effects and helps prevent overconfident conclusions about recommendation quality when input linkage is partial.

Reproducibility literature in recommender systems reinforces the same governance principle: weak reporting of protocol, preprocessing, and configuration can undermine claim credibility [@bellogin_improving_2021; @cavenaghi_systematic_2023; @ferrari_dacrema_troubling_2021; @zhu_bars_2022; @anelli_elliot_2021]. For an artefact thesis, reproducibility is part of contribution quality, not post-hoc polish.

Operationally, this means each run should capture enough context to be replayed and audited: input summaries, alignment-path counts, configuration state, stage-level diagnostics, score traces, and output artifacts. Recent explainability work in music models supports the same broader principle: explanations should expose contribution structure rather than only final outcomes [@sotirou_musiclime_2025].

Design consequence: Chapter 3 should treat staged alignment diagnostics and run-level configuration logging as mandatory architectural mechanisms.

## 2.7 Literature Gap, Synthesis, and Chapter Conclusion
The literature strongly supports individual building blocks relevant to this thesis: recommender paradigm trade-offs, explainability and control concerns, music-specific playlist constraints, feature-based representation, and reproducibility governance. What is less fully developed in the current source set is practical, end-to-end guidance for integrating these concerns into one coherent engineering pipeline under explicit transparency, controllability, and observability objectives.

That is the gap this thesis addresses. The contribution is not a new model family. It is a design-oriented engineering demonstration of how a deterministic, feature-based playlist-generation pipeline can be constructed and evaluated so that behavior remains inspectable, controllable, observable, and reproducible when handling cross-source preference data.

The synthesis from this review is consistent. Method choice should be objective-aligned rather than benchmark-driven in isolation. Explanations should remain linked to recommendation logic as closely as possible [@zhang_explainable_2020; @tintarev_evaluating_2012]. Controls should be judged by interpretable downstream effect rather than by interface presence alone [@jin_effects_2020; @nauta_anecdotal_2023]. Playlist constraints should be engineered explicitly [@schedl_current_2018; @vall_feature-combination_2019]. Alignment should use staged blocking and filtering practices with explicit uncertainty reporting [@papadakis_blocking_2021; @allam_improved_2018]. Reproducibility should be treated as an evidence-quality requirement [@anelli_elliot_2021].

Residual limitations remain explicit. Music-specific alignment benchmark evidence is less mature than cross-domain ER evidence, and broad deterministic metric-isolation evidence across multiple playlist objectives remains limited in current sources. These constraints bound generalization but do not invalidate the thesis contribution under current scope.

Overall, this chapter provides a coherent and defensible basis for the locked research question: What design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data? It connects evidence to design consequences while maintaining claim discipline, allowing Chapter 3 to translate literature conclusions into concrete architectural commitments without scope drift.

Chapter transition: Chapter 3 operationalizes these conclusions into implementable mechanisms for ingestion and alignment, preference modelling, deterministic scoring, playlist assembly, explanation artifacts, and observability controls.