Engineering an Automated, Transparent, and Controllable Playlist Generation Pipeline

Chapter 2- Literature Review

Foundations, Scope, and Thesis Positioning

With music streaming platforms, the choice of tracks is never ending with millions of tracks for listeners to choose from. Most listeners do not have the time, and decision fatigue when it comes to choosing tracks. This is why recommender systems were introduced and developed. There has been substantial research focused on figuring out what a user is likely to value, even when the available data is limited or incomplete (Adomavicius and Tuzhilin, 2005; Lu et al., 2015). Framing this as utility estimation under uncertainty, rather than simple preference prediction, is useful. It makes explicit what recommendation behaviour actually depends on: the type of evidence collected, how users and items are represented, and the objective used to measure success.



From the listening history you are able to determine several factors that can contribute to one’s listening preferences such as play counts and sessions logs that can reflect attention and engagement, however these factors are not the same as a stated choice. Acting on these factors alone still requires careful decisions about how to aggregate it, what to filter out, and to fill in the missing information and other factors that the listening history cannot account for (Roy and Dutta, 2022).



This thesis is not proposing a new recommendation model or competing on benchmark performance. The goal is a playlist-generation pipeline that is transparent, controllable, observable, and reproducible. This matters because recommender evaluation is sensitive to how experiments are set up. Preprocessing decisions, metric framing, and protocol choices can all shift results substantially, and strong performance numbers under one set of conditions do not reliably transfer to contexts where inspectable engineering is the primary contribution (Herlocker et al., 2004; Ferrari Dacrema et al., 2021; Bauer et al., 2024). Architecture decisions in this kind of work should follow the contribution goals, not benchmark tables.



This chapter aims to investigate the general trade-offs in recommender systems, then moves on to issues around transparency and how systems are evaluated. After that, it looks at how user preferences are collected and how user profiles are built. It then discusses the specific challenges that come with music recommendation, explains why a deterministic approach was chosen, and finally looks at how data from different sources is managed,

Core Recommendation Paradigms and Their Trade-offs

Recommender systems are broadly grouped into content-based, collaborative, and hybrid families (Adomavicius and Tuzhilin, 2005; Lu et al., 2015). Although these systems are all working differently, recommender systems can all be evaluated through three fundamentals which are: the available data, the level of complexity of each model, and the level of transparency that the system wants, i.e. if the goal is to make the system easily explained or give the users some level of control.



Content-based methods are based on item attributes: in music settings, those are  metadata, tags, lyrics, and audio descriptors. In systems prioritising transparency, the practical advantage is that ranking depends on explicit features, and the reasoning behind any recommendation can usually be traced back to those same features (Deldjoo et al., 2024).



Collaborative filtering takes a different route, evaluating patterns of interaction across users and items and determining any relevance between them. That can work well with dense interaction histories, but interpretability tends to weaken when rankings are encoded in latent relationships rather than named feature comparisons (Adomavicius and Tuzhilin, 2005; Zhang and Chen, 2020).



Hybrid systems can combine the strengths of both, but the combination adds reasoning complexity that makes audit and explanation harder unless interpretability is deliberately engineered in from the start (Cano and Morisio, 2017).



There is a similarity in all these models but it can be seen that each model has focused on one of the fundamentals, and have traded-off on the other fundamentals. Distance metric, normalisation approach, and threshold settings all shape how candidates are ranked. These are real design decisions, not implementation details (Fkih, 2022). If these factors are not addressed correctly in the design stage of a recommender system, they make inspection difficult and would not be able to be tested and challenged correctly.



From a data perspective, collaborative and hybrid methods tend to rely on denser interaction logs, whereas feature-based approaches remain workable when those logs are sparse, uneven, or partially unmatched. In a cross-source pipeline, that kind of unevenness is anticipated rather than exceptional. Under those conditions, a theoretically stronger model may still be harder to justify than a simpler one whose inputs and failure cases are all readily examinable.



Feature selection, metric choice, normalisation, and weighting are better treated as determining factors in the design stage of a recommender system rather than defaults left implicit in implementation.

Transparency, Explainability, Controllability, Observability, and Evaluation

Research on recommender systems has increasingly recognised that predictive quality alone is not enough. Users and evaluators often need to understand and question what a system is doing, not just benefit from its outputs. Tintarev and Masthoff (2007) provided an early and influential treatment of this, identifying a range of goals that explanations can serve: transparency, trust, effectiveness, scrutability, and persuasiveness among them. Their later evaluation work showed that these goals do not always move together, and that systems capable of generating convincing explanations may not actually support genuine user understanding (Tintarev and Masthoff, 2012).



Four terms recur throughout this thesis and are worth keeping distinct. Transparency refers to visibility of recommendation logic. Explainability refers to understandable reasons for specific outputs. Controllability means the user can actively influence behaviour through explicit parameters or inputs (Jin et al., 2020). Observability, in the context of this thesis, means run-level visibility: execution state, intermediate diagnostics, and output traces captured well enough to support later inspection.



These goals can work against each other. Research consistently shows that explanations may raise perceived satisfaction without improving genuine understanding (Nauta et al., 2023). Post-hoc explanations can sound believable while remaining only loosely connected to the mechanism that actually produced the ranking (Zhang and Chen, 2020). In a system that prioritises transparency, that is a real risk. Explanations need to stay close to the actual scoring process, not be constructed after the fact. Usability work adds a separate pressure: even a technically faithful explanation still needs to be comprehensible to an audience who aren’t experts in the field (Knijnenburg et al., 2012; Afroogh et al., 2024).



Evaluation must reflect all of this. Claiming controllability is not enough: changing a control should produce interpretable effects downstream, and those effects should be documented (Jin et al., 2020; Nauta et al., 2023). Similarly, claiming transparency means explanation values should trace back to actual score components. Claiming reproducibility means runs need to be captured through recorded configuration and stage-level diagnostics, not just described in prose (Beel et al., 2016; Anelli et al., 2021; Cavenaghi et al., 2023).



An evaluation approach built around process and outcome evidence suits this kind of work well. Process evidence asks whether the pipeline behaved as intended at each stage — whether alignment paths were recorded, candidate thresholds produced expected pool sizes, score traces can be reconstructed, and assembly rules were enforced. Outcome evidence asks whether outputs changed in interpretable ways when controls were deliberately varied. Together, these lines of evidence produce defensible conclusions without requiring large-scale user studies, provided that explanation fidelity, parameter sensitivity, rule compliance, and replayability are all systematically documented.

Preference Evidence, Profile Construction, and Candidate Shaping

Profile construction tends to be treated as a data-preparation step rather than a design decision in its own right. In practice, it is where every subsequent ranking decision gets its starting conditions, and it deserves careful attention.



In systems that rely on imported listening history, the evidence is a reflection of what the user might want, rather than a direct statement of what they want (Adomavicius and Tuzhilin, 2005; Roy and Dutta, 2022). Because of that vagueness, building a user profile always involves interpretation. A more reliable approach is to aggregate that evidence through explicit, reviewable rules rather than treating play counts as objective ground truth.



Content-based music research supports this. Bogdanov et al. (2013) showed that preference representations can be built from explicit user examples using semantic audio descriptors, producing profiles that remain inspectable. Their work demonstrated that a profile constructed from user-selected examples could drive similarity-based ranking in a way that kept the underlying reasoning visible. Deldjoo et al. (2024) frame content-driven systems around explicit content layers and note ongoing challenges in transparency, sequence modelling, and efficiency. Together these point toward a preference model built from named feature aggregation rather than non transparent trained embeddings.



This matters in practice because profile construction sits between raw data and every later ranking decision. If the listening history is sparse, partially unmatched, or skewed toward recent sessions, the profile inherits those biases and so does every ranking that follows. A well-designed system should surface not only the final preference representation but also the evidence behind it: how many aligned tracks contributed, which weighting rules were applied, and whether any supplementary inputs shifted the baseline. Without that visibility, a difference in rankings that appears to stem from scoring might actually trace back to profile construction, with no way to tell the two apart.



Influence tracks fit naturally within this framing. Rather than treating them as optional, they give users an explicit way to adjust or supplement the profile when their listening history is incomplete or no longer reflects their current preferences. This is consistent with controllability research that treats user influence as useful when it is explicit, bounded, and testable (Jin et al., 2020; Andjelkovic et al., 2019).



Candidate generation raises the same issues and deserves the same treatment. Playlist systems do not score an entire catalogue. They build a candidate pool first, and what gets into that pool shapes everything downstream. Research has shown that outcomes depend heavily on how candidates are handled (Zamani et al., 2019). Thresholds that look like efficiency parameters actually determine coverage, diversity, and the range of playlists a system can produce. In an auditable pipeline, those thresholds should be logged and available for sensitivity testing, not buried in implementation defaults.



If a track was excluded before scoring due to a filter, a threshold, or a missing feature, that exclusion belongs in the audit trail. Explaining why certain tracks scored well, while staying silent about earlier exclusions, gives a partial and potentially misleading picture of how the final output came to be.

Music Recommendation and Playlist-Specific Challenges

Music recommendation does not map cleanly onto generic top-N logic. People experience listening sequentially, and they evaluate not just whether individual tracks are good but how they move together, that being transitions, pacing, repetition, overall shape. Schedl et al. (2018) make this point clearly, the distinctive characteristics of music consumption, including short track lengths, sequential listening patterns, and contextual variability, mean that individual item relevance is an insufficient basis for playlist evaluation. A set of individually well-ranked tracks can still produce a playlist that feels jarring or repetitive.



Coherence, novelty, diversity, and ordering tend to work against one another and show deliberate trade-offs when attempted to optimise together(Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015). Users perceive playlists as ordered structures, not collections of independent items.



Subjective similarity adds a separate difficulty. Flexer and Grill (2016) found limited inter-rater agreement on music similarity judgements, with considerable sensitivity to how the comparison task is framed. Low-level audio features and metadata do not capture what listeners mean by mood, atmosphere, or nostalgia. Listening context adds further instability: the same person may want a very different playlist for studying than for commuting, and often cannot articulate exactly why.



Datasets like Music4All provide metadata, tags, lyrics, and audio-related attributes that support reproducible content-driven experimentation (Pegoraro Santana et al., 2020). The dataset has also been used in independent multimodal recommendation work, which demonstrates its practical suitability for transparency-focused artefact research (Ru et al., 2023).



Explicit feature proxies are reasonable approximations for this kind of work. Claims that a system has captured the full complexity of listening intent are not.

Deterministic Feature-Based Design Rationale with Comparator Context

The core advantage of feature-based recommendation in this context is straightforward: ranking signals stay visible. When preference profiles and candidate scores are built from explicit descriptors, each decision can be traced back to the features that shaped it (Bogdanov et al., 2013). Making execution deterministic adds a further benefit. With fixed inputs and configuration, the same run should produce the same playlist — a basic requirement for any reproducibility claim.



Neural and hybrid recommenders can capture richer feature interactions and often achieve stronger predictive performance where training data is plentiful (Cano and Morisio, 2017; He et al., 2017; Liu et al., 2025). Choosing a deterministic feature-based design is not a claim that this approach is generally superior. It is a deliberate trade-off: in artefact-oriented research where inspectability, controllability, and reproducibility are the primary objectives, a theoretically simpler but fully auditable approach is often the more appropriate choice.



Metric sensitivity is also worth acknowledging directly. How similarity behaves in feature space depends on specific distance-function choices, and those choices matter (Fkih, 2022; Schweiger et al., 2025). Broad multi-dataset evidence isolating those effects across different playlist objectives is still limited, which reinforces the rationale rather than undermining it. Metric and weighting choices need to be explicit, logged parameters because their effects are real and should not be quietly absorbed into defaults.



Cross-Source Alignment Reliability, Reproducibility Governance, and Synthesis

Using cross-source preference data makes entity alignment a core engineering concern, not a preprocessing nicety. User-history records and item-corpus records come from different systems with partially inconsistent identifiers and uneven data quality. Standard entity-resolution practice addresses this through blocking, which narrows candidate pairs before detailed comparison, followed by staged matching with progressive refinement. The aim is to make alignment uncertainty progressively more visible rather than silently absorb it (Elmagarmid et al., 2007; Papadakis et al., 2021). Staged approaches such as ISRC-first matching with metadata fallback follow exactly that logic: exact identifiers offer high precision when present, and fallback routes recover additional matches when they are absent or inconsistent. Alignment uncertainty is not eliminated, but it becomes part of the audit trail.



Reproducibility in recommender research is a well-documented problem. Under-specified split definitions, preprocessing steps, and dependency versions routinely prevent results from being independently reconstructed (Ferrari Dacrema et al., 2021; Bellogin and Said, 2021; Zhu et al., 2022; Anelli et al., 2021). In an artefact thesis, reproducibility is part of what the work needs to demonstrate. Each run should preserve enough state for replay and inspection, including input summaries, alignment diagnostics, configuration records, candidate-pool statistics, score traces, and assembly outcomes. Recent music explainability work supports the same underlying principle, that explanations should expose how a decision was reached, not just what the outcome was (Sotirou et al., 2025).



Taken together, the literature points toward a consistent set of principles. Methods should be selected to match the contribution objective. Explanations should be tied directly to the mechanisms that produced them. Profile construction, candidate shaping, and alignment should all be treated as first-class design stages. Run-level governance should make the full pipeline inspectable and reproducible. What the literature does not provide is practical end-to-end guidance for integrating all of these concerns into a single pipeline that remains auditable and controllable under real cross-source data conditions. That gap is what this thesis addresses, and the contribution is a design-oriented demonstration of how such a pipeline can be built and evaluated,  not a new model class.



Two limitations carry forward. Music-specific alignment benchmark evidence is thinner than the broader entity-resolution literature, and the source set lacks wide multi-dataset isolation of deterministic similarity effects across different playlist objectives. These bound how far the findings can be generalised, but they do not undermine the core claim: the contribution is scoped engineering evidence, not a universal ranking of recommender methods.
