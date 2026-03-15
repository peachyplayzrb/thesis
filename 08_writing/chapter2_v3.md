# Chapter 2: Literature Review (V3)

## 2.1 Foundations and Thesis Position
Recommender systems are a standard response to information overload in large digital catalogues [@adomavicius_toward_2005; @lu_recommender_2015; @roy_systematic_2022]. Across domains, systems are commonly grouped into content-based, collaborative, and hybrid families [@adomavicius_toward_2005; @cano_hybrid_2017]. This taxonomy is useful, but literature across recommender evaluation warns that method family alone does not determine suitability. Outcomes depend on data conditions, objective choice, metric framing, preprocessing assumptions, and protocol design [@herlocker_evaluating_2004; @jannach_measuring_2019; @ferrari_dacrema_troubling_2021; @anelli_elliot_2021].

That framing is especially important for this thesis because the contribution is artefact-based. The goal is not to propose a new model class. The goal is to engineer and evaluate a transparent, controllable, and observable playlist-generation pipeline using deterministic feature-based recommendation methods under BSc-feasible constraints. The literature review therefore serves as design evidence: it identifies which engineering choices are justified, which trade-offs are unavoidable, and which claims should remain bounded.

Within this scope, deterministic and inspectable pipeline design is treated as a goal-aligned choice, not as a universal superiority claim. Hybrid and neural approaches remain important comparator context, but this thesis prioritizes inspectability, controllability, observability, and replayability over benchmark maximization in isolation [@zhang_explainable_2020; @beel_towards_2016; @bauer_exploring_2024].

Design consequence: Chapter 3 should justify architecture decisions against transparency, controllability, observability, and reproducibility requirements rather than accuracy claims alone.

## 2.2 Transparency, Explainability, Controllability, and Observability
Explainable recommender literature shows that predictive performance is not sufficient when users or evaluators need to understand and scrutinize recommendation behavior [@tintarev_survey_2007; @tintarev_evaluating_2012; @zhang_explainable_2020]. For this thesis, that means recommendation quality is assessed not only by output relevance, but also by whether decisions can be traced and interpreted.

To keep terminology clear, the chapter uses these distinctions. Transparency refers to visibility of recommendation logic. Explainability refers to human-understandable reasons for outputs. Controllability refers to user influence over behavior through explicit inputs or parameters. Observability refers to run-level visibility for audit and diagnosis, including configuration state, intermediate diagnostics, and output traces.

The literature also shows that explanation goals can conflict. Explanations may increase trust or satisfaction without necessarily improving true understanding [@tintarev_evaluating_2012]. This is why explanation must be tied to declared purpose, not treated as generic interface polish.

A core design issue is the difference between post-hoc explanation and transparency-by-design [@zhang_explainable_2020]. Post-hoc approaches may generate plausible narratives after ranking, but those narratives are not always tightly coupled to actual decision mechanisms. Transparency-by-design instead keeps explanations linked to the same signals used in scoring and rule application. For an artefact claiming transparency, this mechanism linkage is the stronger position.

Controllability evidence in music recommendation suggests explicit user influence can be valuable, but effects are user-dependent and context-dependent [@jin_effects_2020; @andjelkovic_moodplay_2019; @liu_aggregating_2025]. Therefore, this thesis does not assume one control strategy works for all users. It treats controls as bounded and testable engineering elements.

Observability is what makes those controls evaluable. If a parameter changes but intermediate effects are not logged, controllability remains nominal. In this thesis, observability is operationalized as traceable records of inputs, configuration, stage-level diagnostics, and outputs, so that behavior can be audited and replayed.

Design consequence: Chapter 3 should implement mechanism-linked explanations, explicit controls, and run-level observability so Chapter 4 can test explanation fidelity and parameter sensitivity.

## 2.3 Music Recommendation and Playlist-Specific Constraints
Music recommendation has domain characteristics that limit direct transfer from generic top-$N$ recommendation framing [@schedl_current_2018; @deldjoo_content-driven_2024]. Songs are consumed sequentially, often in sessions, and playlist quality depends on transitions, pacing, coherence, and diversity, not only item-level relevance [@neto_algorithmic_2023; @gatzioura_hybrid_2019; @vall_feature-combination_2019].

This implies that playlist generation should be treated as a staged process. Ranking quality still matters, but final output quality also depends on assembly constraints such as playlist length, artist repetition limits, ordering logic, and diversity controls. Challenge-level studies reinforce that results are sensitive to protocol and method composition, not only to the scoring model [@zamani_analysis_2019; @teinemaa_composition_2018; @bonnin_automated_2015; @mcfee_million_2012].

A second domain issue is similarity subjectivity. Music-similarity studies report limited agreement and context-sensitive judgment, indicating that similarity signals are useful but not absolute ground truth [@flexer_problem_2016; @siedenburg_modeling_2017]. This supports bounded claim language in later chapters: deterministic similarity can provide auditable decision support, but should not be presented as objective musical truth.

The semantic-gap problem further supports interpretable design. Low-level descriptors do not map perfectly to higher-level listener meaning [@bogdanov_semantic_2013; @deldjoo_content-driven_2024]. Practical systems therefore rely on transparent feature proxies and documented limitations.

The corpus decision is also literature-backed. Music4All provides multi-signal resources suitable for reproducible content-driven experimentation [@pegoraro_santana_music4all_2020], and independent usage supports its practical defensibility for benchmark-informed contexts [@ru_improving_2023]. The claim remains bounded: corpus suitability for this scoped artefact, not universal task optimality.

Design consequence: Chapter 3 should separate scoring from playlist assembly, treat similarity as bounded decision support, and justify Music4All as the canonical corpus under thesis scope.

## 2.4 Deterministic Feature-Based Design Rationale
Feature-based recommendation is attractive for this thesis because it can expose what influenced an output and by how much [@deldjoo_content-driven_2024; @bogdanov_semantic_2013]. In practice, this supports inspectable preference profiles, traceable score components, and explainable rule adjustments.

Deterministic execution strengthens that benefit. Under fixed input and fixed configuration, deterministic pipelines should produce replayable outputs. This improves debugging clarity and evidence quality, because observed output changes can be attributed to explicit parameter changes rather than hidden stochastic effects [@beel_towards_2016; @bellogin_improving_2021].

Comparator context remains important. Hybrid and neural methods often deliver strong predictive results and richer representations [@cano_hybrid_2017; @he_neural_2017; @liu_multimodal_2025; @yu_self_supervised_2024; @moysis_music_2023; @zhu_muq_2025]. The thesis does not reject these methods categorically. Instead, it adopts a different optimization target: inspectability, controllability, observability, and reproducibility under bounded scope.

Metric choice is a key caveat within deterministic design. Literature shows that distance and similarity definitions can materially alter behavior [@fkih_similarity_2022; @flexer_problem_2016; @siedenburg_modeling_2017; @furini_social_2024; @schweiger_impact_2025]. Therefore, metric, normalization, and weighting choices must be explicit and reviewable rather than hidden defaults.

The current evidence base supports this design direction strongly enough for thesis scope, while retaining one bounded limitation: broad multi-dataset studies isolating deterministic similarity-function effects across multiple playlist-objective outcomes remain limited in the current source set.

Design consequence: Chapter 3 should make feature, metric, weight, and rule-adjustment choices explicit so Chapter 4 can test replayability, sensitivity, and explanation fidelity.

## 2.5 Cross-Source Alignment and Reproducibility Governance
Because the research question explicitly concerns cross-source music preference data, alignment is a central engineering problem. Imported listening histories and candidate-corpus records differ in identifiers, completeness, and data quality. Entity-resolution literature supports staged matching pipelines with diagnosable intermediate steps over one-pass fuzzy matching [@elmagarmid_duplicate_2007; @allam_improved_2018; @papadakis_blocking_2021; @binette_almost_2022].

Within this thesis scope, ISRC-first matching with metadata fallback follows that staged rationale. The design prioritizes precise identifier matching when available and bounded fallback for missing or inconsistent identifiers. This does not remove uncertainty, but it keeps uncertainty visible and auditable.

Neural entity matching remains relevant comparator context [@barlaug_neural_2021], yet is out of core MVP scope because it adds complexity and can reduce straightforward inspectability without additional interpretability controls.

The evidence base is stronger for domain-general ER than for music-specific alignment benchmarks. This is treated as a bounded evidence risk, not ignored. As a result, alignment diagnostics such as matched-by-ISRC, matched-by-fallback, unmatched counts, and failure-case logging are required for responsible interpretation.

Reproducibility literature strengthens this governance approach. Recommender claims become hard to trust when preprocessing, protocol, and configuration are weakly reported [@beel_towards_2016; @bellogin_improving_2021; @cavenaghi_systematic_2023; @ferrari_dacrema_troubling_2021; @zhu_bars_2022; @anelli_elliot_2021; @betello_reproducible_2025]. For an artefact-based thesis, reproducibility is part of the contribution quality itself, not post-hoc hygiene.

Design consequence: Chapter 3 should define staged alignment diagnostics and run-level configuration logging as mandatory artefact mechanisms.

## 2.6 Literature Gap, Synthesis, and Chapter Conclusion
The literature strongly covers individual elements needed by this thesis: explainability, controllability, music-specific recommendation challenges, feature-based recommendation, entity-resolution strategy, and reproducibility governance. What is less developed in the current source set is practical end-to-end guidance for engineering a single pipeline that integrates these elements under explicit transparency, controllability, and observability constraints.

That is the gap this thesis addresses. The contribution is not a new recommender model, but an artefact-engineering demonstration of how a deterministic playlist-generation pipeline can be designed and evaluated so that behavior remains inspectable, controllable, observable, and reproducible when operating on cross-source preference data.

The synthesis from this review is clear. Method choice should be goal-aligned rather than benchmark-driven in isolation [@roy_systematic_2022; @jannach_measuring_2019]. Explanation should stay mechanism-linked [@zhang_explainable_2020; @tintarev_evaluating_2012]. Controllability should be evidenced through interpretable parameter effects [@jin_effects_2020; @nauta_anecdotal_2023]. Playlist constraints should be engineered explicitly [@schedl_current_2018; @neto_algorithmic_2023]. Alignment should be staged and uncertainty-aware [@papadakis_blocking_2021; @allam_improved_2018]. Reproducibility and observability should be treated as evidence-quality requirements [@beel_towards_2016; @anelli_elliot_2021; @betello_reproducible_2025].

Residual limitations remain explicit: music-specific alignment benchmark evidence is less mature than domain-general ER evidence, and broad isolation studies on deterministic similarity-function effects across playlist objectives remain limited. These are bounded evidence-depth constraints, not blockers for the scoped contribution.

Overall, this chapter provides a defensible literature basis for the research question and contribution framing. It justifies a scoped, artefact-based design direction while setting strict boundaries on later claims: successful results support scope-specific engineering viability, not universal superiority over hybrid or neural paradigms.

Chapter transition: Chapter 3 translates these design consequences into concrete architecture commitments for preference modelling, candidate preparation, deterministic scoring, playlist assembly, explanation generation, staged alignment diagnostics, and observability controls.