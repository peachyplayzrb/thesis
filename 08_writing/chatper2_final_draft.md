# Chapter 2: Literature Review

## 2.1 Foundations, Scope, and Thesis Positioning

Digital platforms increasingly ask users to make decisions in catalogs that are far larger than any person can evaluate directly. Music streaming is a clear case: listeners face millions of tracks, but time, attention, and context are limited. Recommender systems emerged as a practical response to this information-overload condition by helping users discover items they are likely to value [@adomavicius_toward_2005; @lu_recommender_2015; @roy_systematic_2022].

Foundational recommender literature frames recommendation as utility estimation under partial information. The core problem is not to retrieve a known correct answer, but to infer likely user value from sparse evidence [@adomavicius_toward_2005; @roy_systematic_2022]. This framing is important for the present thesis because it clarifies where design leverage actually sits: recommendation quality depends on evidence choice, representation choice, and objective choice.

A first implication is that listening history should be treated as implicit preference evidence, not as a direct statement of intent. Play counts and sessions reflect engagement signals, but they do not fully encode why a user listened or what they wanted next [@adomavicius_toward_2005; @roy_systematic_2022]. Any pipeline built on this evidence therefore requires explicit aggregation assumptions and explicit interpretation limits.

The thesis contribution is engineering-oriented rather than model-novelty-oriented. The goal is not to introduce a new recommender family or optimize leaderboard performance in isolation. The goal is to engineer an automated playlist-generation pipeline that is transparent, controllable, observable, and reproducible under BSc-level constraints. Evaluation literature warns that reported outcomes can vary with protocol design, preprocessing, and metric framing [@herlocker_evaluating_2004; @ferrari_dacrema_troubling_2021]. Reproducibility-oriented frameworks and surveys reinforce the same caution [@anelli_elliot_2021; @bauer_exploring_2024]. A method that wins in one benchmark setup is not automatically the most defensible choice when inspectability and replayability are primary design objectives.

This objective-first stance is consistent with work arguing that evaluation should be aligned with contribution goals rather than interpreted through single-score comparisons [@jannach_measuring_2019]. In this thesis, literature is therefore used as design evidence: not just to describe prior methods, but to constrain claims, expose trade-offs, and motivate concrete architecture commitments for Chapter 3.

The chapter follows a narrowing argument. It moves from broad recommender paradigms to explanation and control requirements, then to profile construction and candidate shaping, then to playlist-domain constraints, deterministic design rationale, and cross-source governance. The purpose is to reduce design uncertainty and bound claims before implementation and evaluation.

Taken together, the foundational literature supports a clear thesis position: architecture choices should be judged against transparency, controllability, observability, and reproducibility requirements, not predictive accuracy alone.

## 2.2 Core Recommendation Paradigms and Similarity Trade-offs

Most recommender systems are discussed through three high-level families: content-based, collaborative, and hybrid approaches [@adomavicius_toward_2005; @lu_recommender_2015; @cano_hybrid_2017]. This taxonomy is useful for orientation, but it should be treated as a trade-off map rather than a ranking.

Content-based methods model preference through item attributes. In music settings, those attributes can include metadata, tags, lyric features, and audio descriptors. Their practical advantage in a transparency-oriented project is mechanism visibility: if recommendations are driven by explicit features, the system can usually expose why an item scored well in terms of those same features [@bogdanov_semantic_2013; @deldjoo_content-driven_2024].

Collaborative methods infer relevance from interaction patterns across users and items. In data-rich settings they can perform strongly. Their explanation burden often increases when decision logic is represented through latent interactions rather than explicit feature comparisons [@adomavicius_toward_2005; @zhang_explainable_2020].

Hybrid systems combine signal families to exploit complementary strengths [@cano_hybrid_2017]. In many settings they are highly effective. The trade-off is reasoning complexity: once multiple components, weighting schemes, and interaction effects are combined, explanation and audit become harder unless traceability is engineered deliberately from the outset.

Similarity modelling makes these trade-offs concrete. Metric definitions, normalization steps, and thresholding decisions shape candidate neighborhoods and ranking behavior [@fkih_similarity_2022]. These are mechanism-level commitments, not implementation trivia. If made explicit, they can be inspected, challenged, and sensitivity-tested. If hidden in defaults, claims about explanation fidelity and user control become difficult to defend.

Data conditions add a second constraint. Collaborative and hybrid strategies often assume denser interaction coverage, whereas explicit feature-based methods can remain workable under sparse or uneven histories. In cross-source pipelines, unevenness is expected rather than exceptional. Under those conditions, a theoretically stronger model in ideal data regimes may still be less defensible than a simpler approach whose assumptions, failure modes, and outputs remain auditable.

For this thesis, paradigm selection is therefore goal-aligned and scope-bound. Deterministic feature-based scoring is selected because it better supports inspectability and replayability under constrained implementation scope. This is not a universal superiority claim over hybrid or neural alternatives; it is a constrained engineering choice under explicit objectives.

Design implication for Chapter 3: feature selection, similarity metric choice, normalization, and weighting should be treated as first-class configurable and logged mechanisms.

## 2.3 Transparency, Explainability, Controllability, Observability, and Evaluation

Explainable recommender research consistently argues that predictive quality alone is insufficient when users or evaluators need to understand, challenge, or influence system behavior [@tintarev_survey_2007; @tintarev_evaluating_2012; @zhang_explainable_2020]. For this thesis, four terms are kept distinct to avoid conceptual drift.

Transparency means visibility of recommendation logic. Explainability means understandable reasons for specific outputs. Controllability means user influence through explicit inputs or parameters [@tintarev_survey_2007; @balog_transparent_2019; @jin_effects_2020]. Observability, as used here, means run-level visibility of execution context, intermediate diagnostics, and output traces.

These distinctions are necessary because explanation goals can conflict. Prior work shows that explanations can increase trust or perceived satisfaction without necessarily improving genuine understanding [@tintarev_evaluating_2012; @nauta_anecdotal_2023]. An explanation that sounds persuasive is not automatically faithful to the mechanism that produced the ranking.

The distinction between post-hoc explanation and directly explainable mechanisms is therefore central [@zhang_explainable_2020]. Post-hoc narratives can be useful for communication, but they may only loosely correspond to the actual decision path. For a thesis that claims transparency, explanation artifacts should remain tightly linked to the scoring and rule-application process itself.

Interface and user-model research adds another requirement: even faithful explanations need to stay understandable for non-expert users. This usability requirement is well established in explanation-interface work [@tsai_explaining_2018; @knijnenburg_explaining_2012; @afroogh_trust_2024]. In practice, this implies dual quality criteria for explanation outputs: mechanism fidelity and human readability.

Controllability evidence in music recommendation is encouraging but mixed. User controls can improve interaction outcomes, yet effects vary by user characteristics and context [@jin_effects_2020; @andjelkovic_moodplay_2019; @liu_aggregating_2025]. Controls should therefore be treated as bounded and testable mechanisms, not as universal assumptions about user behavior.

Observability ties these concerns together. If control parameters change but stage-level effects are not recorded, controllability remains nominal. If explanation outputs are not traceable to score contributors and rule effects, transparency remains rhetorical. For an artefact thesis, observability is not optional instrumentation; it is part of evidence quality.

These arguments motivate a process-plus-outcome evaluation frame. Process evidence checks whether the pipeline behaved as designed at each stage: alignment paths, candidate shaping effects, score traces, and assembly rule enforcement. Outcome evidence checks whether outputs changed in interpretable ways after controlled variation: influence-track injections, parameter changes, or metric-switch settings.

This framing fits BSc constraints. It avoids overpromising large-scale user experimentation while still demanding disciplined evidence for explanation fidelity, parameter sensitivity, and replayability.

Design implication for Chapter 3: mechanism-linked explanations, explicit controls, and run-level diagnostics should be implemented from the outset so Chapter 4 can evaluate behavior rather than describe it post hoc.

## 2.4 Preference Evidence, Profile Construction, and Candidate Shaping

Profile construction is often treated as preprocessing. In this thesis, it is treated as a primary design stage because it sets the starting conditions for every downstream ranking decision.

The pipeline uses imported listening history as implicit preference evidence rather than explicit intent [@adomavicius_toward_2005; @roy_systematic_2022]. Because implicit evidence is ambiguous, profile construction necessarily involves interpretation. The defensible approach is to make aggregation rules explicit and auditable, rather than to treat interaction counts as objective ground truth.

Music-content literature supports this direction. Semantic-content work shows that preference representations can be built from explicit, inspectable descriptors rather than opaque latent states [@bogdanov_semantic_2013]. Content-driven survey work similarly positions explicit content layers as valuable for transparent recommendation while acknowledging ongoing challenges in sequence quality and efficiency [@deldjoo_content-driven_2024].

Within this design, recency weighting, play-frequency effects, and optional influence-track inputs are treated as declared configuration choices. That choice matters for interpretation: if output rankings change, the system should be able to separate profile-construction effects from similarity-scoring effects.

This separation is critical under cross-source conditions. When alignment coverage is partial, profile construction inherits uncertainty from linkage quality. Without profile-stage diagnostics, later score differences can be misattributed to ranking logic when they originate earlier in evidence aggregation.

Influence tracks fit this framework as a bounded control surface. They are not ad hoc overrides; they are explicit user-supplied evidence that can supplement stale or incomplete history. This aligns with control literature emphasizing explicit and testable user influence rather than unconstrained personalization claims [@jin_effects_2020; @andjelkovic_moodplay_2019; @liu_aggregating_2025].

Candidate shaping requires the same rigor. Playlist systems do not rank an entire corpus in practice; they construct candidate pools first. APC and challenge literature indicates that outcomes depend on component composition, including how candidates are prepared before final ranking [@zamani_analysis_2019; @teinemaa_composition_2018; @bonnin_automated_2015]. Threshold parameters therefore shape not only efficiency but also diversity headroom, coverage, and final assembly possibilities.

For transparent evaluation, candidate filters and exclusions should be treated as explainable decisions. If an item never reaches scoring due to thresholding or missing-feature constraints, that exclusion path should still be auditable. Otherwise, explanation outputs describe only selected-item success and conceal earlier pipeline decisions that shaped the final playlist.

Design implication for Chapter 3: profile aggregation logic, influence-track integration, and candidate-threshold behavior should be explicit, logged, and independently sensitivity-testable.

## 2.5 Music Recommendation and Playlist-Specific Constraints

Music recommendation does not transfer cleanly from generic top-N item ranking. Listening is session-based and sequential, and users evaluate flow properties in addition to item relevance [@schedl_current_2018].

Playlist quality therefore depends on transitions, pacing, repetition control, and coherence over order, not only on independent item relevance [@schedl_current_2018; @bonnin_automated_2015]. A playlist can contain individually strong tracks yet still fail if sequence dynamics are poor.

Playlist continuation research repeatedly discusses trade-offs among coherence, novelty, diversity, and ordering [@ferraro_automatic_2018; @vall_feature-combination_2019; @zamani_analysis_2019]. Improvements in one dimension can weaken another, which makes objective trade-off management central to playlist engineering.

Sequencing studies reinforce that playlists are experienced as ordered structures rather than unordered sets [@neto_algorithmic_2023]. This supports treating playlist assembly as a dedicated stage with explicit constraints instead of an afterthought to scoring.

Evaluation in this domain also requires caution. Challenge and benchmark studies show that reported results depend on protocol choices and method composition [@teinemaa_composition_2018; @bonnin_automated_2015; @mcfee_million_2012]. Comparative claims should therefore be interpreted with setup context, especially when offline metrics are used as partial proxies for subjective listening judgments.

A further constraint is subjective similarity. Music-similarity studies report limited inter-rater agreement and framing sensitivity, indicating that similarity metrics are useful approximations rather than objective truth conditions [@flexer_problem_2016; @siedenburg_modeling_2017].

The semantic-gap literature highlights the same limitation: low-level computable descriptors do not always map cleanly to higher-level human concepts such as mood, atmosphere, or nostalgia [@bogdanov_semantic_2013; @deldjoo_content-driven_2024].

Context dependence makes this concrete. The same listener may prefer very different playlists across focus, commute, exercise, and social contexts, even with the same catalog [@schedl_current_2018].

These findings do not invalidate computational recommendation. They define claim boundaries. In this thesis, deterministic similarity is treated as transparent decision support under partial representation, not as a claim to universal musical correctness.

Dataset choice follows the same logic. Music4All is suitable for this scope because it provides metadata, tags, lyrics, and audio-related attributes that support reproducible content-driven experimentation [@pegoraro_santana_music4all_2020]. It has also been used in independent multimodal recommendation experiments, with explicit task-transfer caveats [@ru_improving_2023].

Design implication for Chapter 3: playlist generation should be engineered as a staged sequence-construction process with explicit assembly constraints, and similarity outputs should be interpreted as auditable approximations.

## 2.6 Deterministic Feature-Based Design Rationale with Comparator Context

Given the thesis objectives, feature-based recommendation offers two practical benefits. First, score contributors remain inspectable when preferences and candidates are represented through explicit descriptors [@bogdanov_semantic_2013; @deldjoo_content-driven_2024]. Second, deterministic execution supports replayability under fixed inputs and fixed configuration.

Replayability is not a cosmetic property in this context. It supports clearer debugging and sensitivity analysis because output changes can be connected to explicit parameter changes rather than hidden run-to-run variation [@bellogin_improving_2021; @beel_towards_2016].

Comparator context remains essential. Hybrid and neural recommenders can capture richer interactions and often deliver strong predictive performance [@cano_hybrid_2017; @he_neural_2017; @liu_multimodal_2025; @yu_self_supervised_2024; @moysis_music_2023]. This thesis does not reject those methods; it optimizes for a different objective set under constrained scope.

The choice of deterministic feature-based scoring is therefore a trade-off in favor of inspectability, controllability, observability, and reproducibility. It is not positioned as a generally superior recommender strategy.

Metric sensitivity remains a central caveat. Similarity behavior depends on explicit distance-function and scaling choices [@fkih_similarity_2022]. APC-related evidence indicates that comparative outcomes can shift with model composition and evaluation framing [@zamani_analysis_2019; @teinemaa_composition_2018; @bonnin_automated_2015].

A bounded limitation should remain explicit: broad multi-dataset isolation studies focused specifically on deterministic similarity-function effects across multiple playlist objectives are still limited in the current source set [@schweiger_impact_2025]. This narrows generalization strength but does not undermine a scoped engineering contribution.

Design implication for Chapter 3: score components, metric choices, normalization choices, and weighting controls should be first-class configurable mechanisms, with downstream sensitivity checks in Chapter 4.

## 2.7 Cross-Source Alignment, Reproducibility Governance, and Chapter Synthesis

Because the research question explicitly targets cross-source music preference data, alignment is a core engineering concern. User-history records and candidate-corpus records originate from different systems with different identifier quality and missingness patterns. Entity-resolution literature commonly uses blocking/filtering stages before deeper matching steps [@elmagarmid_duplicate_2007; @allam_improved_2018; @papadakis_blocking_2021; @binette_almost_2022].

Within this scope, ISRC-first matching with metadata fallback follows that logic. Identifier matching offers high precision when identifiers are available and clean, while fallback routes recover additional links when identifiers are absent or inconsistent. This does not remove uncertainty, but it makes uncertainty inspectable.

Neural entity matching is relevant comparator context and can improve difficult linkage cases [@barlaug_neural_2021]. However, it also introduces additional complexity and can weaken straightforward auditability without substantial traceability layers. For an MVP centered on transparency and controllability, deterministic staged matching with explicit unmatched-case logging remains the more defensible trade-off.

Evidence depth must still be stated carefully: much alignment evidence is domain-general rather than music-benchmark-specific. This is an explicit limitation, not a reason to avoid staged alignment.

Alignment uncertainty is not only a data-cleaning issue; it affects recommendation semantics. If profile evidence is partially unmatched or linked through weaker fallback paths, downstream profile construction, candidate shaping, and ranking inherit that uncertainty. Logging alignment paths therefore improves inference quality by helping separate model behavior from linkage effects.

Reproducibility governance strengthens the same argument. Recommender literature repeatedly highlights comparability risks when split definitions, preprocessing details, and configuration state are weakly documented [@bellogin_improving_2021; @cavenaghi_systematic_2023; @ferrari_dacrema_troubling_2021; @zhu_bars_2022; @anelli_elliot_2021; @betello_reproducible_2025]. BARS-style benchmarking work makes the reporting issue explicit by emphasizing missing preprocessing and configuration details as a reproducibility barrier [@zhu_bars_2022]. For an artefact thesis, reproducibility is part of contribution quality.

Operationally, each run should preserve enough context for replay and audit: input summaries, alignment-route counts, configuration state, stage-level diagnostics, score traces, assembly outputs, and final artifacts. Recent work on explainability in music models supports the broader principle that useful explanations should expose contribution structure, not only final labels [@sotirou_musiclime_2025].

Synthesizing the chapter: the literature supports objective-aligned method selection, explicit similarity commitments, mechanism-linked explanation, bounded user control, sequence-aware playlist assembly, staged cross-source alignment, and run-level reproducibility controls. What remains underdeveloped in the source set is practical end-to-end guidance for integrating all of these constraints into one coherent engineering pipeline under transparent, controllable, and observable operation.

That integration gap is the contribution space of this thesis. The contribution is not a new model family; it is a design-oriented engineering demonstration of how a deterministic feature-based playlist pipeline can be built and evaluated under cross-source conditions while preserving inspectability, controllability, observability, and reproducibility.

Residual limitations remain explicit. Music-specific alignment benchmark evidence is less mature than broader ER evidence, and deterministic metric-isolation evidence across multiple playlist objectives remains limited in current sources. These limitations bound generalization but do not invalidate the scoped thesis contribution.

Overall, this chapter provides a defensible basis for the research question: what design considerations shape the engineering of a transparent, controllable, and observable automated playlist-generation pipeline using cross-source music preference data? Chapter 3 translates these conclusions into concrete architecture mechanisms, and Chapter 4 evaluates their behavior through replayability, fidelity, sensitivity, and rule-compliance evidence. The intended value is practical and testable: a pipeline whose behavior can be inspected, challenged, and reproduced under explicit scope boundaries.
