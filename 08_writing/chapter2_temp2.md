# Chapter 2: Literature Review

## 2.1 Foundations, Scope, and Thesis Positioning
Digital platforms ask users to choose from very large catalogs. In music streaming, that often means selecting from millions of tracks with limited time and attention. Recommender systems emerged as a practical response to this information-overload problem by helping users discover items they are likely to value [@adomavicius_toward_2005; @lu_recommender_2015; @roy_systematic_2022].

Foundational recommender research frames this as utility estimation under partial information: from sparse preference evidence, infer which items are likely to be useful [@adomavicius_toward_2005; @roy_systematic_2022]. That framing is still useful because recommendation is not mere retrieval. It is inference shaped by data quality, representation choices, and objective functions.

The goal of this work is not to introduce a new model family or chase leaderboard results. Instead, it focuses on engineering an automated playlist pipeline that stays transparent, controllable, and observable within BSc-level constraints. Because of that, the key literature question is not which model performs best in general, but which design choices are most defensible for this specific goal.

Evaluation studies support this objective-first stance. Recommender outcomes can vary substantially with protocol definitions, preprocessing decisions, and metric framing [@herlocker_evaluating_2004; @anelli_elliot_2021; @bauer_exploring_2024]. Strong results under one benchmark setup do not automatically transfer to projects where inspectability and replayability are primary goals. Method choice should follow contribution goals, not benchmark scores in isolation [@jannach_measuring_2019].

I structure this chapter as a narrowing argument: foundations first, then music-specific constraints, then engineering implications for the research question. The aim is to reduce design uncertainty step by step, not just collect citations.

Taken together, the literature suggests that architecture choices should be judged against transparency, controllability, observability, and reproducibility, not accuracy alone.

## 2.2 Core Recommendation Paradigms and Their Trade-offs
Recommender systems are usually grouped into three families: content-based, collaborative, and hybrid approaches [@adomavicius_toward_2005; @lu_recommender_2015; @cano_hybrid_2017]. This taxonomy is useful for orientation, but labels alone do not decide what is suitable.

Content-based methods model preference through item attributes. In music applications, these include metadata, tags, and audio descriptors. A major advantage is mechanism visibility: when scoring relies on explicit features, recommendation rationales can often be traced to those features [@deldjoo_content-driven_2024; @bogdanov_semantic_2013].

Collaborative methods infer preference from interaction structure across users and items. They can perform very well at scale with rich histories, but direct interpretability may decrease when ranking logic is embedded in latent factors [@adomavicius_toward_2005; @zhang_explainable_2020].

Hybrid systems combine strategies to exploit complementary strengths [@cano_hybrid_2017]. The trade-off is complexity: combining components can improve predictive performance while making explanation harder unless interpretability controls are built in from the start.

Similarity modelling makes these trade-offs concrete. Metric definitions, normalization choices, and threshold settings all shape neighbourhood construction and ranking behaviour [@fkih_similarity_2022]. These are mechanism-level decisions, not implementation trivia. When choices are explicit, behaviour can be challenged and audited; when they are buried in defaults, explanation and control claims weaken.

Data conditions add another constraint. Collaborative and hybrid methods often need denser interaction logs, while transparent feature-based approaches can still work when interaction history is sparse, incomplete, or missing for part of the user base.

In cross-source pipelines, uneven data quality is normal. Under those conditions, a method that looks stronger in ideal settings may be less defensible than one that is easier to audit with imperfect inputs. I treat this as a scope-bound engineering choice, not a universal ranking of recommender paradigms.

For Chapter 3, feature selection, similarity metrics, normalization, and weighting need to be explicit and auditable.

## 2.3 Transparency, Explainability, Controllability, and Observability
Explainable recommender research has long argued that predictive quality alone is insufficient when users or evaluators need to understand and question system behaviour [@tintarev_survey_2007; @tintarev_evaluating_2012; @zhang_explainable_2020]. A system can score well while still failing to communicate why outputs were produced.

To avoid conceptual blur, I separate four terms. Transparency means visibility of recommendation logic. Explainability means understandable reasons for specific outputs. Controllability means using explicit controls that can steer recommendation behaviour [@tintarev_survey_2007; @balog_transparent_2019; @jin_effects_2020]. Observability, in this thesis, means run-level visibility of execution state, intermediate diagnostics, and output traces.

These distinctions matter because explanation goals can conflict. Explanations may increase trust or satisfaction without improving genuine understanding [@tintarev_evaluating_2012; @nauta_anecdotal_2023]. So evaluation should be purpose-specific, not based on one generic criterion.

A related distinction concerns post-hoc versus directly explainable mechanisms [@zhang_explainable_2020]. Post-hoc narratives can be persuasive yet weakly coupled to the mechanism that produced the ranking. For this reason, explanation artefacts should stay as close as possible to the scoring process itself.

Interface research adds an additional constraint: faithful explanations must still be understandable to non-experts [@tsai_explaining_2018; @knijnenburg_explaining_2012; @afroogh_trust_2024]. Fidelity without usability is not enough.

Evidence on controllability in music recommenders is mixed. User controls can improve experience, but effects vary by user profile and context [@jin_effects_2020; @andjelkovic_moodplay_2019]. Controls should therefore be treated as bounded, testable mechanisms rather than universal behavioural assumptions.

Observability ties these ideas together. If control parameters change but stage-level effects are not recorded, controllability remains nominal and explanation claims are difficult to verify.

Methodologically, this leads to a process-plus-outcome evaluation frame: process evidence checks whether the pipeline behaved as designed at each stage, while outcome evidence checks whether recommendation outputs changed in interpretable ways after parameter adjustments.

This fits BSc scope. It does not require large-scale user studies, but it does require disciplined reporting of inputs, intermediate effects, and outputs.

So Chapter 3 should implement mechanism-linked explanations, explicit control parameters, and run-level diagnostics that can be tested in Chapter 4.

## 2.4 Music Recommendation and Playlist-Specific Challenges
Music recommendation does not transfer cleanly from generic top-N logic. Listening is often session-based and sequential, and users judge not only individual tracks but transitions, pacing, repetition, and overall flow [@schedl_current_2018].

Playlist quality therefore depends on sequence construction, not only item relevance [@schedl_current_2018; @bonnin_automated_2015]. A playlist of individually strong tracks can still fail if transitions are abrupt, artist repetition is high, or diversity disrupts coherence [@ferraro_automatic_2018; @vall_feature-combination_2019].

Playlist continuation studies repeatedly show tension among coherence, novelty, diversity, and ordering [@ferraro_automatic_2018; @vall_feature-combination_2019; @zamani_analysis_2019]. Gains in one dimension often weaken another. Sequencing analyses reinforce that users perceive playlists as ordered structures, not isolated items [@neto_algorithmic_2023]. Also, these dimensions are mostly tested with offline metrics, and those metrics do not always capture how listeners actually judge playlist quality, which makes direct method comparisons more difficult [@anelli_elliot_2021; @bauer_exploring_2024].

Benchmark analyses also caution against decontextualized claims. Reported improvements depend on protocol choices and method composition [@teinemaa_composition_2018; @bonnin_automated_2015; @mcfee_million_2012]. Results should therefore be interpreted together with their evaluation setup.

A second challenge is subjective similarity. Music-similarity research reports limited inter-rater agreement and framing sensitivity, indicating that similarity estimates are useful approximations rather than objective truth [@flexer_problem_2016; @siedenburg_modeling_2017]. The semantic gap sharpens this point: low-level computable features do not fully capture human concepts such as mood, nostalgia, or atmosphere [@bogdanov_semantic_2013; @deldjoo_content-driven_2024].

Context dependence makes this concrete. The same listener can prefer very different playlists for focus, commuting, exercise, or social settings, even with the same catalog.

These observations do not invalidate computational recommendation, but they do set important interpretation boundaries. Context claims should be bounded by what the system can actually observe and represent. In this thesis, that means using explicit proxies where possible, reporting contextual coverage as partial, and avoiding claims that the system captures the full complexity of listening intent.

Dataset choice follows the same logic. Music4All is suitable here because it offers metadata, tags, lyrics, and audio-related attributes for content-driven experimentation [@pegoraro_santana_music4all_2020]. Third-party usage in multimodal studies provides additional support while transfer limits remain explicit [@ru_improving_2023].

Taken together, these findings point toward a staged playlist-assembly design where similarity scores function as inspectable evidence rather than objective truth.

## 2.5 Deterministic Feature-Based Design Rationale with Comparator Context
Given the thesis objectives, feature-based recommendation has a practical advantage: ranking signals remain inspectable. When profiles and candidate scores are built from explicit descriptors, the system can report what contributed to each decision and by how much [@bogdanov_semantic_2013; @deldjoo_content-driven_2024].

Deterministic execution adds a second benefit: with fixed input and fixed configuration, outputs should be replayable.

Comparator context remains essential. Hybrid and neural recommenders can capture richer interactions and often deliver strong predictive performance [@cano_hybrid_2017; @he_neural_2017; @liu_multimodal_2025; @yu_self_supervised_2024; @moysis_music_2023]. Choosing a deterministic feature-based design here is not a claim of general superiority. It is a constrained trade-off in favour of inspectability, controllability, observability, and reproducibility.

Metric sensitivity remains a key caveat. Similarity behaviour depends on explicit distance-function choices in feature space [@fkih_similarity_2022; @furini_social_2024]. APC studies also indicate that outcomes vary with model composition and evaluation setup [@zamani_analysis_2019; @teinemaa_composition_2018; @bonnin_automated_2015]. Metric and weighting choices should therefore be treated as first-order design commitments.

A limitation remains: despite improved music-domain evidence, broad multi-dataset isolation studies focused specifically on deterministic similarity-function effects across multiple playlist objectives are still limited. This narrows generalization claims but does not undermine the scoped thesis contribution.

Chapter 3 therefore needs configurable score components, metric choices, and weighting controls, followed by sensitivity analysis in Chapter 4.

## 2.6 Cross-Source Alignment Reliability and Reproducibility Governance
Because this project uses cross-source preference data, alignment is a core engineering issue. User-history records and candidate-corpus records come from different systems, so identifiers and data quality are not always consistent. Entity-resolution research usually handles this with blocking and filtering to narrow the candidate set, followed by staged matching and refinement [@elmagarmid_duplicate_2007; @allam_improved_2018; @papadakis_blocking_2021; @binette_almost_2022].

Within this scope, ISRC-first matching with metadata fallback is consistent with that staged logic. Identifier matching offers high precision when identifiers are present and clean, while fallback paths recover additional links when identifiers are missing or inconsistent. Uncertainty is not removed, but it becomes inspectable.

Neural entity matching remains a relevant comparator [@barlaug_neural_2021]. However, it introduces additional complexity and can reduce straightforward auditability unless substantial traceability layers are added. For this MVP, the complexity-auditability trade-off favors deterministic staged matching with explicit unmatched-case logging.

Evidence strength still needs to be stated clearly: much alignment evidence is cross-domain rather than music-specific benchmark evidence. I treat this as an evidence-depth limitation, not a reason to discard staged alignment.

Alignment uncertainty is not only a cleaning issue. It changes the interpretation of recommendation outputs. If preference records are unmatched, or matched only through weaker fallback routes, profile construction and ranking inherit that uncertainty.

Treating alignment diagnostics as first-class evidence improves inference quality in later chapters. It helps separate model behaviour from linkage effects and limits overconfident claims when input linkage is partial.

Reproducibility literature reports recurring barriers: missing split details, incomplete hyperparameter reporting, hidden dependency constraints, and unclear configuration state [@bellogin_improving_2021; @cavenaghi_systematic_2023; @ferrari_dacrema_troubling_2021; @zhu_bars_2022; @anelli_elliot_2021]. In an artefact thesis, reproducibility is part of the contribution, not post-hoc polish.

Operationally, each run should capture enough context for replay and audit: input summaries, alignment-path counts, configuration state, stage-level diagnostics, score traces, and output artefacts. For example, if a user-history track fails ISRC matching and enters metadata fallback, that path should be logged and carried into explanation output so later ranking differences are interpretable rather than opaque. Recent explainability work in music models supports the same broader principle: explanations should expose contribution structure, not only final outcomes [@sotirou_musiclime_2025].

For Chapter 3, staged alignment diagnostics and run-level configuration logging should be mandatory architectural mechanisms.

## 2.7 Literature Gap, Synthesis, and Chapter Conclusion
The literature provides strong support for the individual components relevant to this work: recommender paradigm trade-offs, explainability and control concerns, playlist-specific constraints, feature-based representation, and reproducibility governance. What is less mature in the current source set is practical, end-to-end guidance for integrating these concerns into one coherent engineering pipeline under explicit transparency, controllability, and observability objectives.

That is the gap addressed in this thesis. The contribution is not a new model class. It is a design-oriented demonstration of how a deterministic, feature-based playlist pipeline can be engineered and evaluated so that behaviour remains inspectable, controllable, observable, and reproducible under cross-source input conditions.

The synthesis is consistent. Method choice should be objective-aligned rather than benchmark-driven in isolation. Explanations should stay tightly linked to recommendation logic [@zhang_explainable_2020; @tintarev_evaluating_2012], and controls should be assessed through measurable downstream effects rather than interface presence alone [@jin_effects_2020; @nauta_anecdotal_2023]. Playlist constraints should be explicitly engineered [@schedl_current_2018; @vall_feature-combination_2019]. Alignment should report staged blocking/filtering and candidate-match paths [@allam_improved_2018]. Reproducibility should be treated as an evidence-quality requirement [@anelli_elliot_2021].

Residual limitations remain explicit. Music-specific alignment benchmarks are less mature than cross-domain ER evidence, and broad deterministic metric-isolation evidence across multiple playlist objectives remains limited in current sources. These constraints bound generalization. They do not invalidate the scoped contribution.

Overall, this chapter provides a clear basis for the research question: What design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data?

Chapter transition: Chapter 3 operationalises these conclusions into concrete mechanisms for ingestion and alignment, preference modelling, deterministic scoring, playlist assembly, explanation artefacts, and observability controls.
