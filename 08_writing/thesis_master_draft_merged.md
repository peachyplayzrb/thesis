# Final Project Report

University of Wolverhampton

BSc (Hons) Computer Science

Student Name: Timothy Spiteri

Student Number: 2460123

Location/Site: STC Higher Education Malta (Pembroke Campus)

Module Code: 6CS007

Module Name: Project and Professionalism

Project Title: Engineering an Automated, Transparent, and Controllable Playlist Generation Pipeline 

Supervisor Name: Thomas Xuereb

Reader Name: Another Lecturer

Submission Date: 01/05/2026

Award Title: BSc (Hons) Computer Science

## Declaration Sheet

Presented in partial fulfilment of the assessment requirements for the above award.

This work or any part thereof has not previously been presented in any form to the University or to any other institutional body whether for assessment or for other purposes. Save for any express acknowledgements, references and/or bibliographies cited in the work. I confirm that the intellectual contents of the work is the result of my own efforts and of no other person.

It is acknowledged that the author of any project work shall own the copyright. However, by submitting such copyright work for assessment, the author grants to the University a perpetual royalty-free licence to do all or any of those things referred to in section 16(i) of the Copyright Designs and Patents Act 1988. (viz: to copy work; to issue copies to the public; to perform or show or play the work in public; to broadcast the work or to make an adaptation of the work).

Student Name (Print): Timothy Spiteri

Student Number: 2460123

Signature: …………………………………………  

Date: 01/05/2026

## Abstract

Music recommender systems are widely used to help listeners navigate large catalogues, but many practical recommendation pipelines remain difficult to inspect, tune, and reproduce. This is a serious issue, because if behaviour is opaque, design decisions are harder to justify and evaluation is harder to trust. This thesis addresses that problem by engineering a single user playlist generation pipeline that is automated but also transparent, controllable, observable, and reproducible, whilst using cross source music preference data.

The implemented artefact is a deterministic, content-based pipeline that imports listening history from one practical source, enriches imported tracks with Last.fm semantic tags when direct corpus alignment is unreliable, builds an interpretable preference profile, generates and filters candidates from DS-002 (MSD subset plus Last.fm tags), scores tracks using deterministic feature-based similarity, and assembles playlists using rule-based constraints. The approach of this thesis is based on Design Science Research: literature is translated into requirements, requirements shape the architecture, and the implementation is tested using explicit run-level evaluation checks.

Evaluation is structured around reproducibility, traceability, controllability, constraint compliance, and testing quality under thesis constraints. The thesis does not claim a novel recommender model or universal superiority. Instead, its contribution is engineering evidence that an automated playlist pipeline can be made auditable, testable, and practically controllable end-to-end. Current implementation evidence includes BL-020 real-data execution through BL-009 observability and BL-014 automated sanity checks (21/21 pass), providing a complete and traceable evidence chain for the implemented scope.

## Table of Contents

[Generate automatically in Word if required for the final submission format.]

## List of Figures

[Generate automatically in Word if required for the final submission format.]

## List of Tables

[Generate automatically in Word if required for the final submission format.]

## List of Abbreviations

- DSR: Design Science Research
- ISRC: International Standard Recording Code
- MVP: Minimum Viable Product

# Chapter 1: Introduction

## 1.1 Background and Context

Music streaming platforms place millions of tracks in front of listeners who have neither the time nor the tools to evaluate them directly. Recommender systems exist to reduce this overload by selecting and ordering items that are likely to be useful or appealing. In music contexts, however, recommendation is not only about identifying individually relevant tracks. Playlist generation also has to deal with sequence, repetition, variety, coherence, and the practical difficulty of representing user preference from incomplete evidence.

This project sits within that problem space, but its emphasis is not on maximising benchmark accuracy. The thesis is concerned with how a playlist-generation pipeline can be engineered so that its behaviour remains inspectable and defensible. In practical recommendation systems, outputs are often produced by complex model pipelines whose intermediate reasoning is difficult to observe directly. That creates difficulty for both users and evaluators: if recommendation behaviour cannot be clearly traced, then it becomes harder to justify design choices, diagnose failure cases, and relate evaluation outcomes to explicit system mechanisms.

The challenge becomes more pronounced when the system combines preference evidence and item data from different sources. Listening history imported from an external platform must be aligned with a separate canonical music corpus before it can support scoring and playlist assembly. That alignment step introduces uncertainty, potential data loss, and methodological questions about how unmatched items, fallback decisions, and configuration changes should be surfaced. For a final-year engineering project, these are not peripheral concerns. They are part of the artefact design itself.

Against that background, this thesis develops a deterministic, single-user, content-based playlist-generation pipeline using cross-source music preference data. The project is framed as an artefact-engineering contribution whose value lies in transparent mechanisms, controllable execution, traceable outputs, and reproducible evaluation.

## 1.2 Problem Statement

Contemporary music recommender systems can generate useful suggestions, but they are often difficult for users and evaluators to inspect, tune, and reproduce. In many practical settings, recommendation outputs are produced by complex model pipelines where the contribution of individual factors is not easily visible, and where small configuration or data changes can alter outcomes without clear traceability.

This creates a problem for an artefact-focused undergraduate engineering project: it is difficult to produce recommendation evidence that is simultaneously automated, technically rigorous, and transparent enough to support critical evaluation. When recommendation behaviour cannot be clearly inspected or controlled, it becomes challenging to justify design decisions, diagnose errors, and connect results to explicit system rules.

The problem is further amplified when user preference data is collected from external music platforms and aligned to a separate feature corpus. Cross-source alignment introduces matching uncertainty and potential data loss, while recommendation quality depends on available feature descriptors in the target dataset. Without explicit engineering choices for alignment, scoring, and assembly, playlist generation can become opaque and inconsistent.

Accordingly, the thesis addresses the following engineering problem:

How can a single-user playlist generation pipeline be engineered so that it remains automated while also being transparent, controllable, observable, and reproducible when using cross-source music preference data?

This problem is addressed within a bounded MVP scope:

- single-user recommendation context
- deterministic, content-based methods rather than machine-learning model novelty
- DS-002 (MSD subset plus Last.fm tags) as the active candidate track corpus
- one practical ingestion path with staged metadata handling and semantic enrichment fallback
- explicit rule-based scoring and playlist assembly with inspectable run logs

Solving this problem contributes design and implementation evidence for building recommendation pipelines whose behaviour can be explained and audited, rather than only judged by output quality. The intended outcome is a defensible artefact and evaluation basis that aligns with the research question on design considerations for transparent, controllable, and observable playlist generation.

## 1.3 Research Question

What design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data?

## 1.4 Research Objectives

1. Design an automated pipeline that generates playlists from user listening histories.
2. Build cross-source preference evidence from imported listening history using staged metadata handling and Last.fm semantic enrichment where direct matching is unreliable.
3. Construct a deterministic user preference profile based on imported listening data and manually selected influence tracks.
4. Generate candidate tracks from the DS-002 corpus using deterministic feature-based filtering.
5. Score candidate tracks using deterministic similarity functions and rule-based adjustments.
6. Assemble playlists using playlist-level rules that ensure diversity, coherence, and ordering.
7. Provide transparent explanations and observability mechanisms for recommendation decisions.
8. Evaluate the system with respect to transparency, controllability, inspectability, and reproducibility.

## 1.5 Scope and Delimitations

The thesis is bounded to a locked MVP artefact: a single-user, deterministic, content-based playlist-generation pipeline with one practical ingestion path and DS-002 as the active canonical candidate corpus. Transparency, controllability, observability, and reproducibility are treated as mandatory system qualities rather than optional enhancements.

Several exclusions are deliberate. The project does not attempt to build or benchmark collaborative filtering, deep-learning, or large-scale hybrid recommender models. It does not extend to multi-user experimentation, production deployment, or a broad ecosystem of ingestion adapters. Evaluation is also constrained to BSc-feasible testing rather than large-scale user studies or longitudinal behavioral analysis.

These delimitations are methodological rather than accidental. They keep the artefact auditable, make explanation outputs mechanism-linked, and allow the evaluation to test concrete engineering properties without overstating generality. As a result, any claims made in later chapters must be interpreted as scoped design evidence for a transparent deterministic pipeline under these project conditions.

## 1.6 Research Contributions

This thesis contributes an artefact-based demonstration of how a transparent, controllable, and observable automated playlist-generation pipeline can be engineered using deterministic feature-based recommendation methods. The contribution is not a new recommendation algorithm. It is a structured engineering response to the difficulty of producing recommendation behaviour that can be inspected, tuned, replayed, and critically evaluated.

The contribution has three parts. First, it provides a layered architecture for cross-source playlist generation that keeps ingestion, alignment, profile construction, scoring, assembly, explanation, and run logging distinct and auditable. Second, it provides design traceability linking literature consequences to architecture mechanisms and evaluation criteria. Third, it provides an evaluation frame that tests reproducibility, traceability, controllability, and playlist-rule compliance in a way that fits the scope of an undergraduate artefact thesis.

## 1.7 Thesis Structure

Chapter 1 introduces the problem context, research question, scope, and contribution framing.

Chapter 2 reviews the literature on recommender paradigms, transparency and explainability, preference evidence, music and playlist-specific challenges, deterministic design rationale, and cross-source alignment governance.

Chapter 3 translates those literature findings into explicit design commitments through a Design Science Research methodology, defining the system architecture, the pipeline stages, and the traceability relationship between design requirements and later evidence.

Chapter 4 reports the implementation and evaluation approach for the artefact, setting out the testing criteria, the evidence structure, and the result tables used to assess reproducibility, controllability, explanation fidelity, observability, and rule compliance.

Chapter 5 interprets the findings against the research question, critically evaluates the artefact and the evidence, states the principal limitations, and identifies future work.

The report ends with references and appendices containing supporting diagrams, configuration examples, test evidence, and project-management extracts where needed.

## 1.8 Chapter Summary

This chapter has framed the project as an artefact-engineering response to the difficulty of producing transparent and controllable recommendation behaviour under cross-source data conditions. It has defined the research question, the project objectives, and the bounded scope within which the work should be interpreted. The next chapter reviews the literature needed to justify the design choices that follow.

# Chapter 2: Literature Review

## 2.1 Foundations, Scope, and Thesis Positioning

Music streaming platforms place millions of tracks in front of listeners who have neither the time nor the tools to evaluate them directly. Recommender systems emerged to address this problem, and a substantial body of research has since built up around how to estimate what a user is likely to value from sparse, incomplete evidence (Adomavicius and Tuzhilin, 2005; Lu et al., 2015). Framing this as utility estimation under uncertainty, rather than simple preference prediction, is useful. It makes explicit what recommendation behaviour actually depends on: the type of evidence collected, how users and items are represented, and the objective used to measure success.

One implication is worth drawing out early. Listening history is implicit preference evidence, not explicit preference. Play counts and session logs reflect attention and engagement, but they are not the same as a stated choice. Acting on that evidence still requires deliberate choices about how to aggregate it, what to filter out, and how to account for what it cannot tell you (Roy and Dutta, 2022).

This thesis is not proposing a new recommendation model or competing on benchmark performance. The goal is a playlist-generation pipeline that is transparent, controllable, observable, and reproducible. This matters because recommender evaluation is sensitive to how experiments are set up. Preprocessing decisions, metric framing, and protocol choices can all shift results substantially, and strong performance numbers under one set of conditions do not reliably transfer to contexts where inspectable engineering is the primary contribution (Herlocker et al., 2004; Ferrari Dacrema et al., 2021; Bauer et al., 2024). Architecture decisions in this kind of work should follow the contribution goals, not benchmark tables.

The chapter moves through a narrowing argument: general recommender trade-offs first, then transparency and evaluation concerns, preference evidence and profile construction, music-specific challenges, the rationale for a deterministic design, and cross-source governance.

## 2.2 Core Recommendation Paradigms and Their Trade-offs

Recommender systems are broadly grouped into content-based, collaborative, and hybrid families (Adomavicius and Tuzhilin, 2005; Lu et al., 2015). The taxonomy is a useful starting point, but no family is categorically best. What matters is what data is available, how much complexity is justified, and — in a transparency-focused context — whether the design needs to support explanation or user control.

Content-based methods work from item attributes: in music settings, those are metadata, tags, lyrics, and audio descriptors. In systems prioritising transparency, the practical advantage is that ranking depends on explicit features, and the reasoning behind any recommendation can usually be traced back to those same features (Deldjoo et al., 2024). Collaborative filtering takes a different route, inferring relevance from patterns of interaction across users and items. That can work well with dense interaction histories, but interpretability tends to weaken when rankings are encoded in latent relationships rather than named feature comparisons (Adomavicius and Tuzhilin, 2005; Zhang and Chen, 2020). Hybrid systems can combine the strengths of both, but the combination adds reasoning complexity that makes audit and explanation harder unless interpretability is deliberately engineered in from the start (Cano and Morisio, 2017).

Similarity modelling sits at the centre of these trade-offs. Distance metric, normalisation approach, and threshold settings all shape how candidates are ranked. These are real design decisions, not implementation details (Fkih, 2022). Left implicit, they make inspection difficult; stated explicitly, they can be tested and challenged.

There is also a data argument. Collaborative and hybrid methods tend to rely on denser interaction logs, whereas feature-based approaches remain workable when those logs are sparse, uneven, or partially unmatched. In a cross-source pipeline, that kind of unevenness is expected rather than exceptional. Under those conditions, a theoretically stronger model may still be harder to justify than a simpler one whose inputs and failure cases are all readily examinable.

Feature selection, metric choice, normalisation, and weighting are better treated as explicit, reviewable commitments rather than defaults left implicit in implementation.

## 2.3 Transparency, Explainability, Controllability, Observability, and Evaluation

Research on recommender systems has increasingly recognised that predictive quality alone is not enough. Users and evaluators often need to understand and question what a system is doing, not just benefit from its outputs. Tintarev and Masthoff (2007) provided an early and influential treatment of this, identifying a range of goals that explanations can serve: transparency, trust, effectiveness, scrutability, and persuasiveness among them. Their later evaluation work showed that these goals do not always move together, and that systems capable of generating convincing explanations may not actually support genuine user understanding (Tintarev and Masthoff, 2012).

Four terms recur throughout this thesis and are worth keeping distinct. Transparency refers to visibility of recommendation logic. Explainability refers to understandable reasons for specific outputs. Controllability means the user can actively influence behaviour through explicit parameters or inputs (Jin et al., 2020). Observability, in the context of this thesis, means run-level visibility — execution state, intermediate diagnostics, and output traces captured well enough to support later inspection.

These goals can pull against each other. Research consistently shows that explanations may raise perceived satisfaction without improving genuine understanding (Nauta et al., 2023). Post-hoc explanations can sound plausible while remaining only loosely connected to the mechanism that actually produced the ranking (Zhang and Chen, 2020). In a system that prioritises transparency, that is a real risk. Explanations need to stay close to the actual scoring process, not be constructed after the fact. Usability work adds a separate pressure: even a technically faithful explanation still needs to be comprehensible to a non-expert audience (Knijnenburg et al., 2012; Afroogh et al., 2024).

Evaluation must reflect all of this. Claiming controllability is not enough: changing a control should produce interpretable effects downstream, and those effects should be documented (Jin et al., 2020; Nauta et al., 2023). Similarly, claiming transparency means explanation values should trace back to actual score components. Claiming reproducibility means runs need to be captured through recorded configuration and stage-level diagnostics, not just described in prose (Beel et al., 2016; Anelli et al., 2021; Cavenaghi et al., 2023).

An evaluation approach built around process and outcome evidence suits this kind of work well. Process evidence asks whether the pipeline behaved as intended at each stage — whether alignment paths were recorded, candidate thresholds produced expected pool sizes, score traces can be reconstructed, and assembly rules were enforced. Outcome evidence asks whether outputs changed in interpretable ways when controls were deliberately varied. Together, these lines of evidence produce defensible conclusions without requiring large-scale user studies, provided that explanation fidelity, parameter sensitivity, rule compliance, and replayability are all systematically documented.

## 2.4 Preference Evidence, Profile Construction, and Candidate Shaping

Profile construction tends to be treated as a data-preparation step rather than a design decision in its own right. In practice, it is where every subsequent ranking decision gets its starting conditions, and it deserves careful attention.

In systems that rely on imported listening history, the evidence is implicit rather than a direct statement of what the user wants (Adomavicius and Tuzhilin, 2005; Roy and Dutta, 2022). Because of that ambiguity, building a user profile always involves interpretation. A more reliable approach is to aggregate that evidence through explicit, reviewable rules rather than treating play counts as objective ground truth.

Content-based music research supports this. Bogdanov et al. (2013) showed that preference representations can be built from explicit user examples using semantic audio descriptors, producing profiles that remain inspectable. Their work demonstrated that a profile constructed from user-selected examples could drive similarity-based ranking in a way that kept the underlying reasoning visible. Deldjoo et al. (2024) frame content-driven systems around explicit content layers and note ongoing challenges in transparency, sequence modelling, and efficiency. Together these point toward a preference model built from named feature aggregation rather than opaque trained embeddings.

This matters in practice because profile construction sits between raw data and every later ranking decision. If the listening history is sparse, partially unmatched, or skewed toward recent sessions, the profile inherits those biases and so does every ranking that follows. A well-designed system should surface not only the final preference representation but also the evidence behind it: how many aligned tracks contributed, which weighting rules were applied, and whether any supplementary inputs shifted the baseline. Without that visibility, a difference in rankings that appears to stem from scoring might actually trace back to profile construction, with no way to tell the two apart.

Influence tracks fit naturally within this framing. Rather than treating them as optional, they give users an explicit way to adjust or supplement the profile when their listening history is incomplete or no longer reflects their current preferences. This is consistent with controllability research that treats user influence as useful when it is explicit, bounded, and testable (Jin et al., 2020; Andjelkovic et al., 2019).

Candidate generation raises the same issues and deserves the same treatment. Playlist systems do not score an entire catalogue. They build a candidate pool first, and what gets into that pool shapes everything downstream. Research has shown that outcomes depend heavily on how candidates are handled (Zamani et al., 2019). Thresholds that look like efficiency parameters actually determine coverage, diversity, and the range of playlists a system can produce. In an auditable pipeline, those thresholds should be logged and available for sensitivity testing, not buried in implementation defaults.

If a track was excluded before scoring — due to a filter, a threshold, or a missing feature — that exclusion belongs in the audit trail. Explaining why certain tracks scored well, while staying silent about earlier exclusions, gives a partial and potentially misleading picture of how the final output came to be.

## 2.5 Music Recommendation and Playlist-Specific Challenges

Music recommendation does not map cleanly onto generic top-N logic. People experience listening sequentially, and they evaluate not just whether individual tracks are good but how they move together — transitions, pacing, repetition, overall shape. Schedl et al. (2018) make this point clearly: the distinctive characteristics of music consumption, including short track lengths, sequential listening patterns, and contextual variability, mean that individual item relevance is an insufficient basis for playlist evaluation. A set of individually well-ranked tracks can still produce a playlist that feels jarring or repetitive.

Coherence, novelty, diversity, and ordering tend to pull against one another and rarely optimise together without deliberate trade-offs (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015). Users perceive playlists as ordered structures, not collections of independent items.

Subjective similarity adds a separate difficulty. Flexer and Grill (2016) found limited inter-rater agreement on music similarity judgements, with considerable sensitivity to how the comparison task is framed. Low-level audio features and metadata do not capture what listeners mean by mood, atmosphere, or nostalgia. Listening context adds further instability: the same person may want a very different playlist for studying than for commuting, and often cannot articulate exactly why.

Datasets like Music4All provide metadata, tags, lyrics, and audio-related attributes that support reproducible content-driven experimentation (Pegoraro Santana et al., 2020). The dataset has also been used in independent multimodal recommendation work, which demonstrates its practical suitability for transparency-focused artefact research (Ru et al., 2023).

Explicit feature proxies are reasonable approximations for this kind of work. Claims that a system has captured the full complexity of listening intent are not.

## 2.6 Deterministic Feature-Based Design Rationale with Comparator Context

The core advantage of feature-based recommendation in this context is straightforward: ranking signals stay visible. When preference profiles and candidate scores are built from explicit descriptors, each decision can be traced back to the features that shaped it (Bogdanov et al., 2013). Making execution deterministic adds a further benefit. With fixed inputs and configuration, the same run should produce the same playlist — a basic requirement for any reproducibility claim.

Neural and hybrid recommenders can capture richer feature interactions and often achieve stronger predictive performance where training data is plentiful (Cano and Morisio, 2017; He et al., 2017; Liu et al., 2025). Choosing a deterministic feature-based design is not a claim that this approach is generally superior. It is a deliberate trade-off: in artefact-oriented research where inspectability, controllability, and reproducibility are the primary objectives, a theoretically simpler but fully auditable approach is often the more appropriate choice.

Metric sensitivity is also worth acknowledging directly. How similarity behaves in feature space depends on specific distance-function choices, and those choices matter (Fkih, 2022; Schweiger et al., 2025). Broad multi-dataset evidence isolating those effects across different playlist objectives is still limited, which reinforces the rationale rather than undermining it. Metric and weighting choices need to be explicit, logged parameters because their effects are real and should not be quietly absorbed into defaults.

## 2.7 Cross-Source Alignment Reliability, Reproducibility Governance, and Synthesis

Using cross-source preference data makes entity alignment a core engineering concern, not a preprocessing nicety. User-history records and item-corpus records come from different systems with partially inconsistent identifiers and uneven data quality. Standard entity-resolution practice addresses this through blocking, which narrows candidate pairs before detailed comparison, followed by staged matching with progressive refinement. The aim is to make alignment uncertainty progressively more visible rather than silently absorb it (Elmagarmid et al., 2007; Papadakis et al., 2021). Staged approaches such as ISRC-first matching with metadata fallback follow exactly that logic: exact identifiers offer high precision when present, and fallback routes recover additional matches when they are absent or inconsistent. Alignment uncertainty is not eliminated, but it becomes part of the audit trail.

Two caveats are worth noting here. Most of the entity-resolution literature addresses cross-domain settings rather than music specifically. Neural matching is a relevant alternative for difficult cases (Barlaug and Gulla, 2021), but neural approaches reduce traceability unless substantial logging infrastructure is built around them — a poor trade-off in systems whose primary claim is transparency. In transparency-focused systems, that balance tends to favour staged deterministic matching with explicit logging of unmatched cases.

Reproducibility in recommender research is a well-documented problem. Under-specified split definitions, preprocessing steps, and dependency versions routinely prevent results from being independently reconstructed (Ferrari Dacrema et al., 2021; Bellogin and Said, 2021; Zhu et al., 2022; Anelli et al., 2021). In an artefact thesis, reproducibility is part of what the work needs to demonstrate. Each run should preserve enough state for replay and inspection — including input summaries, alignment diagnostics, configuration records, candidate-pool statistics, score traces, and assembly outcomes. Recent music explainability work supports the same underlying principle — that explanations should expose how a decision was reached, not just what the outcome was (Sotirou et al., 2025).

Taken together, the literature points toward a consistent set of principles. Methods should be selected to match the contribution objective. Explanations should be tied directly to the mechanisms that produced them. Profile construction, candidate shaping, and alignment should all be treated as first-class design stages. Run-level governance should make the full pipeline inspectable and reproducible. What the literature does not provide is practical end-to-end guidance for integrating all of these concerns into a single pipeline that remains auditable and controllable under real cross-source data conditions. That gap is what this thesis addresses, and the contribution is a design-oriented demonstration of how such a pipeline can be built and evaluated — not a new model class.

Two limitations carry forward. Music-specific alignment benchmark evidence is thinner than the broader entity-resolution literature, and the source set lacks wide multi-dataset isolation of deterministic similarity effects across different playlist objectives. These bound how far the findings can be generalised, but they do not undermine the core claim: the contribution is scoped engineering evidence, not a universal ranking of recommender methods.

# Chapter 3: Design and Methodology

## 3.1 Design Methodology

This chapter takes a Design Science Research position in which the literature synthesis is converted into explicit engineering requirements and then into an implementable artefact architecture. The workflow remains the defined thesis sequence: literature -> requirements -> design -> implementation -> evaluation. The key methodological point is that Chapter 3 does not claim validated outcomes. It defines design commitments that are intended to be tested in Chapter 4.

This distinction is important because the chapter is not trying to prove a universally best recommendation method. It is establishing an architecture that is defensible under the project constraints and contribution goals. In that sense, the value of this chapter is design justification and traceability: why each mechanism is included, what it is expected to do, and how later evaluation can challenge or confirm those expectations.

## 3.2 Literature-Driven Design Requirements

The Chapter 2 synthesis is translated here into a small set of practical design requirements that can be implemented and tested. The first requirement is inspectability: recommendation outputs should be traceable to concrete scoring contributors and rule effects, not explained only through persuasive post-hoc language (Tintarev and Masthoff, 2007; Tintarev and Masthoff, 2012; Zhang and Chen, 2020).

The second requirement is practical controllability. The system should expose explicit user influence paths, but those controls should remain understandable and methodologically testable rather than open-ended or opaque (Andjelkovic et al., 2019; Jin et al., 2020). The third requirement is playlist-aware behavior. Item relevance alone is insufficient in music settings where ordering, repetition, and collection-level coherence shape user experience (Schedl et al., 2018; Gatzioura et al., 2019; Neto et al., 2023).

The fourth requirement is governance at run level: observability, reproducibility, and auditability should be engineered directly into execution through configuration capture and structured diagnostics (Beel et al., 2016; Bellogin and Said, 2021; Cavenaghi et al., 2023). The fifth is corpus defensibility. DS-002 is the active implementation corpus because it provides deterministic candidate-side feature coverage under current scope constraints; Music4All remains a baseline literature reference for corpus-family suitability (Pegoraro Santana et al., 2020).

Taken together, these requirements constrain the architecture toward explicit stages and explicit artifacts, because if a property cannot be observed, replayed, or stress-tested later, it should not be treated as a core design claim now.

## 3.3 Overall System Architecture

The proposed architecture is a layered deterministic pipeline:
1. user interaction,
2. data ingestion,
3. track alignment,
4. preference modelling,
5. candidate generation,
6. feature processing,
7. deterministic scoring,
8. playlist assembly,
9. explanation output,
10. observability and audit,
11. configuration and execution control.

This layout is chosen to keep causal traceability from user input to playlist output. Each stage has a clearly defined role and emits intermediate artifacts that can be inspected independently. That separation is important for evaluation because it allows later analysis to distinguish profile effects, candidate-pool effects, scoring effects, and assembly effects rather than collapsing everything into a single black-box outcome.

The architecture also reflects deliberate scope discipline. It is single-user, deterministic, and content-driven, with one practical ingestion path and no deep-model complexity in the core pipeline. Those limits are not treated as missing sophistication; they are methodological choices that keep the artefact auditable and feasible within thesis constraints.

## 3.4 Data Ingestion and Alignment

The ingestion boundary is intentionally narrow: one practical listening-history source plus optional manual influence tracks. Imported tracks are normalized and transformed into an inspectable preference signal using staged metadata handling and semantic enrichment.

This staged strategy follows entity-resolution practice that treats matching as a sequence of explicit steps with explicit trade-offs, rather than a single hidden operation (Allam et al., 2018; Papadakis et al., 2021). In BL-020 real-data execution, direct DS-002 fuzzy alignment produced false positives for the user's dominant repertoire, so the active path moved to Last.fm semantic enrichment with explicit ok/no_tags/error diagnostics. Neural matching remains a relevant comparator for difficult cases, but sits outside this artefact's inspectability and complexity boundary (Barlaug and Gulla, 2021).

At this stage, it is also important to make data assumptions explicit. Imported rows are expected to contain minimally usable artist-title metadata even when identifiers are missing, and the ingestion layer is expected to surface malformed or incomplete records rather than silently discarding them. In practice, cross-source music data can contain duplicated entries, inconsistent naming conventions, remaster or version suffixes, and partial metadata, all of which can affect fallback matching confidence. For design purposes, these are treated as manageable sources of uncertainty that must be made visible through diagnostics instead of being hidden behind aggregate success rates. This keeps method interpretation honest in Chapter 4 because alignment quality is reported as a property of both data conditions and matching logic.

In line with Chapter 2 evidence-limiting language, this design treats alignment reliability as methodologically grounded but still uncertain because much entity-resolution evidence is cross-domain rather than music-specific.

## 3.5 Preference Modelling and Candidate Preparation

The preference model is built from aligned listening history and influence tracks using interpretable feature representations. Candidate generation then restricts the searchable set before scoring to preserve tractability and maintain deterministic behavior.

Feature processing standardizes values, handles missingness, and prepares weighted attributes for comparable similarity computation. This design uses content-driven framing from music recommender literature while keeping mechanism transparency explicit (Bogdanov et al., 2013; Deldjoo et al., 2024).

The intended flow is straightforward: aligned listening events provide baseline preference evidence, influence tracks provide explicit user-priority signals, and both are combined into a unified profile in the same feature space as candidate tracks. The contribution here is not a new profile algorithm. It is making these profile inputs and transformations visible enough that downstream ranking behavior can be interpreted without guesswork.

Candidate shaping is treated with the same discipline. Filters and thresholds are not only efficiency settings; they determine which tracks are even eligible for scoring, and this distinction matters in later analysis because a track can be absent from final output either because it was never considered or because it was scored and ranked lower. Keeping that boundary explicit improves explanation fidelity and reduces the risk of attributing retrieval effects to scoring logic.

This section also acknowledges that richer context-aware or multimodal models can achieve strong performance in adjacent tasks, but they are treated as comparator context rather than core implementation because of inspectability and complexity constraints in the MVP boundary defined for this project (Ru et al., 2023; Liu et al., 2025).

## 3.6 Deterministic Scoring and Playlist Assembly

Candidate scoring is performed using explicit deterministic similarity functions plus documented rule adjustments. Playlist assembly then enforces collection-level constraints, including playlist length, artist repetition limits, and diversity or ordering controls.

The rationale is goal-aligned rather than absolutist: deterministic scoring is selected to maximize inspectability and replayability under thesis scope, not to claim universal accuracy superiority over hybrid or neural alternatives (Cano and Morisio, 2017; He et al., 2017; Liu et al., 2025).

Metric and feature-weight selections are treated as explicit design parameters rather than hidden implementation defaults. In methodological terms, this makes scoring behavior testable rather than assumed.

For governance, this means parameters should be documented as first-class configuration choices rather than embedded constants. During evaluation, non-target parameters should remain fixed when one setting is varied so observed output differences remain interpretable. This is especially relevant when comparing metric or weight choices, because multiple simultaneous parameter changes would make causal interpretation weak. Keeping this discipline at design level ensures Chapter 4 can present parameter effects as clear and traceable rather than anecdotal.

## 3.7 Explanation, Observability, and Reproducibility

Explanation outputs are generated directly from scoring contributors and rule adjustments so that explanation statements remain mechanism-linked. In parallel, observability captures run-level artifacts including input summary, alignment statistics, configuration, ranking outputs, and playlist-rule outcomes.

This coupling supports both user-facing transparency and developer-facing inspectability, and enables deterministic replay tests required by the evaluation plan (Beel et al., 2016; Bellogin and Said, 2021).

A minimum run record should therefore capture input metadata summary, configuration snapshot and hash, semantic-enrichment coverage counts, no-tag/error categories, score-trace summaries for ranked outputs, playlist-assembly rule outcomes, and final output identifiers. This does not require production-grade telemetry. It requires a consistent artifact bundle that can be reviewed and compared across runs. Defining this record format in Chapter 3 improves evaluation quality in Chapter 4 because replay checks, sensitivity checks, and explanation-fidelity checks all depend on the same observable execution footprint.

Modern music explainability work further reinforces this approach by emphasizing that explanation quality depends on exposing meaningful contribution structure rather than post-hoc narrative alone (Sotirou et al., 2025).

## 3.8 Configuration and Execution Control

A persistent configuration profile defines feature weights, constraints, filtering controls, and execution parameters. This enables controlled parameter-sensitivity experiments and exact reruns for reproducibility checks.

The intended execution protocol has two complementary modes. Baseline replay mode keeps inputs and configuration fixed to check deterministic consistency across repeated runs. Controlled-variation mode changes one selected parameter at a time while holding other settings constant, so observed differences can be interpreted in relation to that specific control. Together, these modes convert configuration from a convenience feature into a methodological instrument for evaluating reproducibility and controllability.

The chapter scope remains design-only. The purpose here is to define what should be implemented and why, not to claim that the implementation has already achieved those outcomes. Empirical behavior, failure cases, and test results are therefore deferred to Chapter 4.

## 3.9 Decision Traceability

The chapter centers on four linked architecture decisions. The first is corpus choice: DS-002 is used as the active canonical candidate space for feature-based retrieval and scoring. The second is scope discipline: the system remains within a single-user deterministic MVP boundary so behaviour stays inspectable and feasible. The third is staged cross-source preference extraction: direct alignment uncertainty is surfaced and semantic enrichment fallback is used when corpus mismatch prevents trustworthy direct matches. The fourth is mechanism-level transparency: deterministic scoring is paired with explanation linkage and run-level observability and reproducibility controls. Taken together, these decisions connect the Chapter 2 rationale to implementation commitments tested in Chapter 4.

## 3.10 Literature-to-Design Traceability

This section makes the literature-to-design handoff explicit by mapping each Chapter 2 section-level consequence to a concrete Chapter 3 commitment.

Table 3.1 documents this section-level handoff mapping from Chapter 2 consequences to Chapter 3 commitments.

| Chapter 2 source | Chapter 2 design consequence | Chapter 3 design commitment |
| --- | --- | --- |
| Section 2.1 | Architecture choices should be justified against transparency, controllability, observability, and reproducibility objectives instead of benchmark-only framing. | The architecture rationale in Sections 3.2 to 3.8 is written as objective-aligned engineering justification under MVP constraints defined for this project. |
| Section 2.2 | Deterministic design should be positioned as a goal-aligned trade-off choice rather than a universal best-model claim. | Sections 3.3 and 3.6 justify a deterministic layered pipeline while retaining comparator-context discipline. |
| Section 2.3 | Expose explicit user controls and keep explanation outputs mechanism-linked and evaluable. | Sections 3.2, 3.7, and 3.8 define controllability requirements, explanation linkage, and configuration-based controls for sensitivity testing. |
| Section 2.4 | Use interpretable preference-profile construction and explicit candidate shaping before scoring. | Section 3.5 defines profile construction and candidate preparation as explicit, auditable pre-scoring stages. |
| Section 2.5 | Keep playlist assembly as a distinct stage and treat similarity as decision support, not ground truth. | Section 3.6 separates playlist assembly from item scoring and encodes explicit playlist-level constraints. |
| Section 2.6 | Make metric and feature-weight choices explicit and include sensitivity checks. | Sections 3.5 and 3.6 use explicit deterministic feature-based scoring and document parameterization for later sensitivity evaluation. |
| Section 2.7 | Add staged alignment diagnostics, unmatched-rate reporting, and run-level configuration logging under governance-oriented evaluation criteria. | Sections 3.4 and 3.7 define staged alignment, unmatched-track reporting, and run-level observability artifacts aligned with Chapter 4 governance checks. |

This handoff mapping keeps the Chapter 2 conclusions operational and reduces drift between literature interpretation and architecture specification.

Overall, this chapter operationalizes the Chapter 2 argument into implementable commitments while keeping the wording cautious: deterministic choices are justified as scope- and objective-aligned engineering decisions, not universal model-superiority claims.

## 3.11 Requirement, Mechanism, and Evidence Mapping

To keep design and evaluation aligned, each requirement group is mapped to a concrete architecture mechanism and a specific Chapter 4 evidence target.

Table 3.2 provides this requirement-to-mechanism-to-evidence mapping.

| Requirement group | Architecture mechanism | Planned Chapter 4 evidence artifact |
| --- | --- | --- |
| Inspectability and explanation fidelity | Deterministic scoring with score decomposition plus mechanism-linked explanation payloads | Score-trace reconstruction table showing explanation fidelity and mandatory explanation-field completeness |
| Practical controllability | Influence-track input path plus parameterized metric, weight, and rule controls with configuration capture | One-factor-at-a-time sensitivity comparison tables with configuration-diff snapshots and ranked-output deltas |
| Playlist-level quality constraints | Distinct assembly stage with explicit length, repetition, and diversity or ordering rules | Rule-compliance summary tables with explicit pass or fail outcomes and violation logs where constraints are not met |
| Cross-source alignment reliability visibility | Staged metadata handling with semantic enrichment fallback and unmatched/no-tag diagnostics | Alignment diagnostics summary showing direct-match quality checks, semantic enrichment coverage, no-tag rate, and unmatched-reason categories |
| Observability and reproducibility | Run-level artifact schema linking input, configuration, alignment, scoring, assembly, and outputs | Replay-consistency hash comparison table plus run-schema completeness checklist across repeated runs |

This mapping fixes the evaluation contract before implementation reporting and keeps Chapter 4 focused on evidence of designed properties rather than ad hoc result narratives.

## 3.12 Core Decision Logic Diagrams

Figure 3.3 and Figure 3.4 illustrate the most decision-critical parts of the architecture: cross-source alignment and the scoring-to-assembly transition.

Figure 3.3 shows the staged cross-source preference extraction flow with semantic fallback and unmatched/no-tag handling.

```text
Imported listening record
  -> Required fields valid?
     -> No: Mark invalid record and log reason -> Alignment diagnostics summary
     -> Yes: Build normalized artist/title representation
            -> Attempt direct alignment path quality check
               -> Trustworthy match? yes -> Emit matched seed
               -> Trustworthy match? no  -> Semantic fallback path

Semantic fallback path (Last.fm)
  -> Query track tags
     -> Tags found? yes -> Emit semantic seed with status=ok
     -> Tags found? no  -> Try fallback lookup path
            -> Tags found? yes -> Emit semantic seed with status=ok
            -> Tags found? no  -> Emit seed with status=no_tags
  -> API failure? -> Emit seed with status=error

All paths -> Alignment/enrichment diagnostics summary
```

Figure 3.4 shows deterministic scoring, rule adjustment, and playlist assembly interaction.

```text
Preference profile
  -> Candidate pool
  -> Feature preparation
  -> Base similarity scoring
  -> Score component breakdown
  -> Rule adjustments
  -> Final ranked list
  -> Playlist assembly rules
  -> All constraints satisfied?
     -> Yes: Final playlist output -> Explanation payload -> Run-level observability artifacts
     -> No: Violation log plus fallback handling with logged violations -> Explanation payload -> Run-level observability artifacts
```

The decision points shown above represent the core implementation checkpoints that Chapter 4 will evaluate for replayability, controllability, and rule compliance.

## 3.13 Chapter Summary

Chapter 3 has translated the Chapter 2 literature consequences into a concrete deterministic system design. The architecture makes each major pipeline stage explicit, preserves traceability from design rationale to implementation mechanism, and fixes an evaluation contract before empirical reporting begins. Chapter 4 now examines whether the implemented artefact and the supporting evidence actually satisfy these design commitments.

# Chapter 4: Implementation, Testing and Evaluation

## 4.1 Chapter Aim and Scope

This chapter reports how the designed artefact is implemented and how it is evaluated under the locked MVP scope. The chapter does not claim state-of-the-art recommendation accuracy. Instead, it evaluates whether the system delivers deterministic behaviour, transparent and inspectable recommendation logic, practical controllability, and playlist-rule compliance under BSc-feasible conditions.

Scope boundaries remain consistent with the locked thesis state: single-user pipeline, one practical ingestion path, deterministic scoring core, and no deep-model baseline benchmarking.

Chapter 4 now has implementation evidence available from BL-020 and BL-014 runs. Where a table still appears in placeholder form, it should be populated directly from the logged artifacts in `07_implementation/experiment_log.md`, `07_implementation/test_notes.md`, and the corresponding stage output files.

## 4.2 Evaluation Criteria and Success Conditions

Evaluation follows the locked evaluation plan and uses five criteria.

Table 4.1 defines the evaluation criteria, operational checks, and minimum success conditions used in this chapter.

| Criterion | Operational check | Minimum success condition |
| --- | --- | --- |
| Reproducibility | Replay identical input and configuration across multiple runs | Identical ranked output and playlist output for repeated runs |
| Traceability | Inspect score-contribution and rule-adjustment outputs per recommended track | Every recommended track has readable mechanism-linked explanation fields |
| Controllability | Change one parameter at a time and observe output differences | Output changes are interpretable and directionally consistent with control intent |
| Constraint compliance | Verify playlist-level rules such as length, repetition, and diversity or ordering | Generated playlists satisfy the configured rule set or produce explicit violation logs |
| Testing quality | Document method, setup, outputs, and critical interpretation | Reproducible test notes with failures and limitations explicitly discussed |

## 4.3 Design-to-Evaluation Traceability

To prevent design-evaluation drift, each Chapter 3 commitment is tied to a Chapter 4 evaluation check.

Table 4.2 provides the design-to-evaluation continuity mapping used to keep Chapter 4 evidence aligned with Chapter 3 commitments.

| Chapter 3 design commitment | Chapter 4 evaluation check | Evidence artifact |
| --- | --- | --- |
| Objective-aligned deterministic architecture under MVP constraints | Verify implemented pipeline stages and scope boundary compliance | Implementation summary and scope-conformance checklist |
| Explicit user control and parameterized execution | One-factor-at-a-time sensitivity tests | Parameter sweep table and output delta summary |
| Distinct playlist assembly stage with rule constraints | Rule-compliance checks per generated playlist | Constraint pass or fail table with violation diagnostics |
| Explicit feature and metric-based deterministic scoring | Explanation-fidelity checks against raw score components | Track-level score breakdown snapshots |
| Staged alignment with unmatched reporting | Alignment diagnostics and unmatched-rate reporting | Matching summary including ISRC hits, fallback hits, unmatched count, and unmatched rate |
| Run-level observability and replayability | Deterministic replay tests with run logs | Re-run comparison logs and configuration snapshots |

This mapping provides the direct handoff from design rationale to evaluable system behaviour.

## 4.4 Implementation Overview

Implementation reporting is organized by pipeline stage to preserve inspectability.

1. Ingestion and input normalization.
2. ISRC-first alignment and metadata fallback logic.
3. Preference-profile construction from matched history and influence tracks.
4. Candidate filtering and feature preparation.
5. Deterministic scoring with rule adjustments.
6. Playlist assembly and post-assembly validation.
7. Explanation rendering and run-level logging.

The implemented behavior across these stages is evidenced by BL-020 runs and supporting quality checks. Ingestion uses one practical Spotify path with deterministic normalization. Alignment-quality checks showed that direct DS-002 fuzzy matching was unreliable for the user's dominant repertoire, so the active execution path moved to semantic enrichment with explicit `ok/no_tags/error` diagnostics. Profile construction and candidate preparation are deterministic and artifact-linked (BL-004 and BL-005), with scoring in semantic-only mode where user-side Spotify numeric audio features are unavailable under current API constraints (BL-006). Playlist assembly enforces explicit diversity and length rules with auditable rule-hit traces (BL-007). Explanations and observability are mechanism-linked through component breakdowns and run-level hashes (BL-008 and BL-009), and BL-014 confirms cross-stage schema/hash/count continuity.

## 4.5 Testing and Evaluation Procedure

The evaluation procedure uses a staged protocol to keep results interpretable.

1. Baseline reproducibility run:
- fix input history, influence tracks, and configuration;
- execute repeated runs;
- compare ranked candidates and final playlists for identity.

2. Alignment-quality diagnostics:
- record ISRC matches, metadata fallback matches, and unmatched tracks;
- analyse whether unmatched items are bounded and transparently reported.

3. Explanation-fidelity validation:
- select sample recommendations from baseline runs;
- verify explanation values against deterministic score components and rule adjustments.

4. Controllability sensitivity tests:
- vary one control parameter at a time such as feature weights or diversity controls;
- record rank and playlist deltas and assess directional interpretability.

5. Constraint-compliance verification:
- check playlist outputs against configured rules;
- log any violations with likely causes.

## 4.6 Evidence Package and Artefact Demonstration Basis

The evaluation evidence is structured around reproducible, cross-referenced artefacts that link observed system behaviour to named test conditions, saved configurations, and stage-level diagnostics. This ensures the artefact demonstration rests on inspectable records rather than informal screenshots alone.

The evidence package used in this chapter includes: (1) BL-010 reproducibility logs and replay matrix with fixed-config stable hashes across three runs; (2) BL-020 alignment/enrichment diagnostics including coverage and error/no-tag categories; (3) BL-008 explanation payloads and summary with component-level contributor data and hash-link checks; (4) BL-011 controllability scenario outputs for one-factor-at-a-time parameter variation; and (5) BL-007 rule-compliance traces plus BL-014 automated sanity outputs validating schema and cross-stage linkage integrity. Primary references are maintained in `07_implementation/test_notes.md`, `07_implementation/experiment_log.md`, and stage-level output directories.

## 4.7 Evaluation Results Matrix

This section reports outcomes for the execution matrix defined in the evaluation plan.

**Table 4.3: Evaluation results matrix.** Populated from test notes and experiment logs.

| EP Test ID | Related Test Note ID | Status | Key Metric Summary | Evidence Artefact(s) | Interpretation Note |
| --- | --- | --- | --- | --- | --- |
| EP-REPRO-001 | TC-003 | pass | `ranked_hash_match=True`, `playlist_hash_match=True`, `replay_count=3` | BL-010 reproducibility report + run matrix | Deterministic replay confirmed under fixed inputs/config; volatile metadata hashes documented separately. |
| EP-EXPL-001 | TC-004 | pass | `fields_complete=10/10`, `reconstruction_error=0.000000` on validated sampled track | BL-008 explanation payloads + summary | Explanation outputs are mechanism-linked and complete for playlist tracks; sampled score reconstruction matched exactly. |
| EP-CTRL-001 | TC-005 | pass | `top10_overlap_delta=1`, `playlist_overlap=7/10`, `mean_abs_rank_shift=2.619` | BL-011 no-influence scenario outputs | Influence-track removal caused interpretable profile/rank/playlist shifts, consistent with control intent. |
| EP-CTRL-002 | TC-006 | pass | `mean_component_delta.V_mean=+0.038908`, `top10_overlap_delta=1`, `mean_abs_rank_shift=1.048` | BL-011 valence-weight scenario outputs | Increased valence emphasis raised valence contribution and shifted ranking directionally as expected. |
| EP-CTRL-003 | TC-007 | pass | `candidate_pool_delta=-2/+2` (stricter/looser), `playlist_overlap=10/10` | BL-011 threshold scenarios + diagnostics | Threshold control changed candidate-pool size as expected; final playlist remained stable under current bootstrap regime. |
| EP-RULE-001 | TC-008 | pass | `length_target=10`, `length_actual=10` | BL-007 playlist + assembly report | Length rule satisfied exactly with full traceability. |
| EP-RULE-002 | TC-008 | pass | `max_artist_repeats=4` (cap respected) | BL-007 assembly report + trace | Artist/genre repetition constraints were enforced with explicit rule-hit diagnostics. |
| EP-OBS-001 | TC-009 | pass | `required_sections_present=True`, `upstream_run_ids_linked=5` | BL-009 observability log + BL-014 sanity report | Observability schema complete and linked across BL-004 to BL-008 outputs. |
| EP-ALIGN-001 | TC-010 | partial pass | Direct fuzzy path not trusted (`38/38` audited false positives); semantic enrichment `tag_coverage=95.87%`, `no_tags=204`, `errors=27` | BL-020 alignment report + EXP-022 + TC-BL020-001 | Alignment visibility objective passed, but direct-match reliability was insufficient; semantic fallback became active path. |

## 4.8 Reproducibility, Observability, and Alignment Results

**Table 4.4: Reproducibility, observability, and alignment results.** Populated from BL-010, BL-009, BL-020, and BL-014 evidence.

| Check | Baseline Run | Repeat Run(s) | Result | Notes |
| --- | --- | --- | --- | --- |
| Ranked output identity | `BL010-REPRO-20260320-233937` | replay_01/replay_02/replay_03 | pass | Stable `ranked_output_hash` matched across all three replays. |
| Playlist output identity | `BL010-REPRO-20260320-233937` | replay_01/replay_02/replay_03 | pass | Stable playlist fingerprint matched across replays; raw JSON hash variation attributed to per-run metadata fields. |
| Run schema completeness | `BL009-OBSERVE-20260322-023314-347594` | `BL014-SANITY-20260322-024523-652281` | pass | BL-014 reported `checks_passed=21/21`, including schema/link/continuity checks. |
| Alignment diagnostics completeness | `BL003-ALIGN-20260322-020126-080489` | N/A (single full real-data run) | pass | Report includes total seeds, tagged/no-tag/error counts, failure examples, and output linkage (`5592`, `5361`, `204`, `27`). |

## 4.9 Controllability and Rule-Compliance Results

**Table 4.5: Parameter-sensitivity and assembly-rule compliance results.** Populated from BL-011 and BL-020 rule evidence.

| Control Under Test | Baseline Value | Variant Value | Observed Effect | Directionally Consistent | Status |
| --- | --- | --- | --- | --- | --- |
| Influence tracks | 3 synthetic influence tracks enabled | all influence tracks removed | Candidate pool `42 -> 47`; playlist overlap `7/10`; mean abs rank shift `2.619` | yes | pass |
| Feature weight | `V_mean=0.12` (raw) | `V_mean=0.20` (raw, renormalized set) | Mean `V_mean` component `+0.038908`; top-10 overlap `9/10`; mean abs rank shift `1.048` | yes | pass |
| Candidate threshold | baseline numeric thresholds (`1.0x`) | stricter `0.75x` and looser `1.25x` | Candidate pool `42 -> 40` (stricter), `42 -> 44` (looser); playlist overlap `10/10` | yes | pass (bounded effect) |
| Playlist length rule | target size `10` | compliance verification on BL-020 run | Actual playlist length `10`; no length-rule violation | yes | pass |
| Artist repetition rule | max per lead genre `4` | compliance verification on BL-020 run | Max observed per-genre count `4` (`classic rock`); no cap violation | yes | pass |

## 4.10 Explanation Fidelity Results

**Table 4.6: Explanation fidelity verification results.** Populated from BL-008 transparency outputs and validation checks.

| Sampled Track Count | Reconstructable Scores | Missing Explanation Fields | Max Reconstruction Error | Status |
| --- | --- | --- | --- | --- |
| 10 | 10/10 with component-linked breakdowns (explicit score reconstruction validated on sampled track) | 0 | 0.000000 (validated sample) | pass |

## 4.11 Evaluation Limits and Interpretation

Results in this chapter should be interpreted as design evidence for a scoped deterministic pipeline, not as universal recommender-superiority claims. Any weak or mixed outcomes such as high unmatched rate or unstable sensitivity behaviour should be explicitly documented and carried into the Chapter 5 limitations section.

The observed limitations should be interpreted using the completed evidence chain: direct DS-002 alignment reliability varies by user-corpus overlap, semantic enrichment quality depends on external tag coverage and API reliability, and external validity remains bounded by single-user MVP scope.

## 4.12 Project Management and Process Evidence

Project management evidence for the artefact is maintained through the supporting project records in the workspace, including the timeline, decision log, implementation plan, experiment log, mentor feedback log, and unresolved-issues tracking. Within the report itself, the role of this section is to show that scope control, design decisions, and evaluation activities were managed through explicit artefacts rather than through undocumented iteration.

At minimum, the final version of this section should summarize how the MVP scope was locked, how design changes were justified, how testing tasks were scheduled and recorded, and how unresolved issues were tracked or bounded. This keeps the project-management criterion visible without turning the main thesis into a logbook.

## 4.13 Chapter Summary

Chapter 4 now presents both the evaluation framework and populated implementation evidence for the artefact. Reproducibility, inspectability, controllability, and playlist-rule compliance are evidenced through BL-010, BL-011, BL-020, and BL-014 artifacts, with explicit interpretation of both successful checks and bounded limitations. Chapter 5 interprets these outcomes under the thesis' scope-bounded contribution framing.

# Chapter 5: Discussion, Critical Evaluation and Conclusion

## 5.1 Interpretation of Results and Comparator Framing

Evaluation results in this thesis are interpreted as evidence for design-goal alignment rather than as claims of universal recommendation superiority. The relevant design goals are transparency, controllability, observability, and reproducibility. This interpretation is consistent with literature showing that practical value and scientific validity depend on explicit objective-metric alignment and clear reporting of protocol assumptions (Jannach and Jugovac, 2019; Bauer et al., 2024; Anelli et al., 2021; Ferrari Dacrema et al., 2021).

Accordingly, complex hybrid and self-supervised recommender families are treated as comparator context that motivates careful scope positioning rather than direct implementation requirements for this locked MVP artefact (Liu et al., 2025; Yu et al., 2024).

## 5.2 Scope-Bounded Claims

The contribution claim is scoped to deterministic pipeline engineering under explicit transparency and observability constraints. Any discussion of performance trade-offs should therefore be framed as conditional on objectives, data conditions, and protocol choices. The point of the thesis is not that deterministic content-based playlist generation is universally best. It is that, under the defined project scope, it is the most defensible way to operationalize inspectability, user control, and reproducible evaluation.

This scope discipline matters because it prevents the discussion from drifting into unfair or unsupported comparisons with systems designed for different objectives. It also ensures that negative findings, partial findings, or mixed evaluation outcomes can still support a useful contribution, provided they are interpreted honestly as evidence about the design constraints and trade-offs of this artefact.

## 5.3 Findings in Relation to the Research Question

The research question asks what design considerations shape the engineering of a transparent, controllable, and observable automated playlist-generation pipeline using cross-source music preference data. Based on the literature synthesis and the current implementation evidence, five design considerations emerge as central.

First, method selection should be goal-aligned rather than model-family absolutist. The choice of recommendation method should be driven by the target qualities of inspectability, controllability, observability, and reproducibility rather than by an assumed universal superiority of any one recommender family (Roy and Dutta, 2022; Jannach and Jugovac, 2019).

Second, cross-source preference extraction must be staged and uncertainty-aware. Under current API constraints, metadata normalization plus semantic enrichment is a practical and inspectable design, but unmatched, no-tag, or ambiguous cases must be surfaced as first-class outputs rather than hidden inside preprocessing (Papadakis et al., 2021; Allam et al., 2018).

Third, deterministic scoring and rule-based playlist assembly support traceability. Explicit feature contributions and rule effects make explanation outputs and debugging behaviour auditable in ways that opaque pipelines do not (Zhang and Chen, 2020; Tintarev and Masthoff, 2007).

Fourth, evaluation protocol discipline is itself part of system design. Reproducibility and interpretation quality depend on logging, configuration traceability, and clear metric-objective alignment (Beel et al., 2016; Bauer et al., 2024; Anelli et al., 2021).

Fifth, comparator awareness must be maintained without allowing scope drift. Hybrid and self-supervised systems are relevant context for trade-off discussion, but they are not required to validate the contribution of this locked MVP artefact (Liu et al., 2025; Yu et al., 2024).

Current evaluation evidence supports these considerations directly. BL-020 completed real-data execution from BL-003 through BL-009 with explicit stage-level diagnostics, deterministic artifact hashes, and full observability linkage. BL-014 automated sanity checks then validated schema integrity, cross-stage hash linkage, and count/run-id continuity across the full evidence chain (21/21 checks passed). The research question can therefore be answered within a qualified, scope-bounded frame: transparent and controllable playlist generation is achievable with deterministic mechanisms when governance and artifact traceability are engineered as first-class requirements.

## 5.4 Critical Evaluation

The strongest aspect of the artefact design is its discipline. The system architecture is deliberately layered, deterministic, and auditable, which means each major stage can be inspected and challenged in isolation. That is a better fit for the project aims than a more powerful but less transparent pipeline would have been. The design also shows clear methodological consistency: literature findings are translated into requirements, requirements into mechanisms, and mechanisms into planned evidence checks.

A second strength is the decision to treat explanation, observability, and reproducibility as engineering mechanisms rather than as presentation features. This avoids one of the common weaknesses in explainable recommendation work, where explanations are added after the ranking process in a way that sounds plausible but is poorly grounded in the real recommendation mechanism.

The main weakness is external validity rather than evidencing completeness. The Chapter 4 evidence base is now populated for the implemented pipeline path, but claims remain bounded by the single-user scope, DS-002 corpus composition, and reliance on semantic enrichment when direct alignment is unreliable.

Another weakness is the dependence on the underlying corpus and alignment path. Recommendation behaviour can only be as complete as the aligned preference evidence and available feature descriptors allow. If track matching fails or if the corpus does not capture the most relevant aspects of listening intent, the transparency of the system will help diagnose the problem, but it will not remove the problem.

Overall, the artefact is strongest as an engineering demonstration of how recommendation pipelines can be made inspectable and reproducible under a bounded scope. It is weaker as a basis for any broader claim about recommendation quality beyond that scope. That distinction should remain explicit in the final submission.

## 5.5 Limitations

This thesis has several explicit limitations that constrain interpretation of results.

1. Scope limitation: the artefact is single-user, content-based, and deterministic by design, so findings are not generalized to collaborative, deep, or large-scale production recommenders.
2. Data alignment limitation: some imported tracks may not align reliably to the canonical corpus, and the strongest methodological support remains in staged entity-resolution research rather than in music-specific alignment benchmarks.
3. Corpus-feature limitation: recommendation behaviour and output quality are constrained by DS-002 candidate composition and feature availability.
4. External-API limitation: Spotify audio-feature endpoints are deprecated, so user-side tempo/loudness/key/mode are not directly available from Spotify in the current implementation.
5. Alignment-quality limitation: direct fuzzy alignment into DS-002 can produce false positives for users with weak corpus overlap; semantic enrichment fallback is required in this regime.
6. Comparator limitation: no implemented deep or hybrid baseline is included in the MVP, so broader trade-off comparisons remain literature-grounded rather than experimentally demonstrated.
7. Evaluation-boundary limitation: evaluation is BSc-feasible and does not include large-scale user studies, longitudinal behaviour, or production-scale deployment evidence.

These limitations do not invalidate the contribution, but they bound it to system-design guidance under transparent deterministic constraints.

## 5.6 Future Work

Future work should extend this artefact in ways that preserve traceability while strengthening evidence.

1. Complete a full BL-020 rerun refresh (BL-003 through BL-013) on a later snapshot and compare outputs against the current evidence baseline.
2. Add a focused music-domain alignment reliability study on corpus-overlap failure regimes and semantic-fallback quality.
3. Execute broader controllability experiments and integrate their outcomes into run-level observability logs.
4. Add at least one comparator pipeline, such as a lightweight hybrid baseline, using protocol-matched evaluation so trade-off analysis improves without inflating scope.
5. Evaluate one audio-grounded extension path for user-side features (local extraction from a bounded track subset) to mitigate Spotify audio-feature endpoint deprecation.

Collectively, these steps would strengthen external validity and comparative depth while keeping the thesis contribution centred on transparent, controllable, and observable engineering design.

## 5.7 Final Conclusion

This thesis has argued that the engineering of a transparent, controllable, and observable automated playlist-generation pipeline is shaped less by the pursuit of maximum model complexity and more by the disciplined design of explicit mechanisms. Under the locked scope of a single-user, deterministic, content-based artefact, the key design considerations are staged cross-source alignment, interpretable preference construction, explicit feature-based scoring, rule-aware playlist assembly, mechanism-linked explanation outputs, and run-level observability and reproducibility controls. The contribution is therefore not a new recommender model, but a structured demonstration of how these qualities can be engineered into a playlist pipeline and evaluated in a way that remains open to inspection and critical challenge.

# References

Adomavicius, G. and Tuzhilin, A. (2005) 'Toward the next generation of recommender systems: a survey of the state-of-the-art and possible extensions', IEEE Transactions on Knowledge and Data Engineering, 17(6), pp. 734-749. doi: 10.1109/TKDE.2005.99.

Afroogh, S., Akbari, A., Malone, E., Kargar, M. and Alambeigi, H. (2024) 'Trust in AI: progress, challenges, and future directions', Humanities and Social Sciences Communications, 11(1), p. 1568. doi: 10.1057/s41599-024-04044-8.

Allam, A., Salloum, S., Fahmy, A. and El-Desouky, A. (2018) 'Improved suffix blocking for record linkage and entity resolution', Data and Knowledge Engineering. doi: 10.1016/j.datak.2018.07.005.

Andjelkovic, I., Parra, D. and O'Donovan, J. (2019) 'Moodplay: Interactive music recommendation based on artists' mood similarity', International Journal of Human-Computer Studies, 121, pp. 142-159. doi: 10.1016/j.ijhcs.2018.04.004.

Anelli, V.W., Bellogin, A., Ferrara, A., Malitesta, D., Merra, F.A., Pomo, C., Donini, F.M. and Di Noia, T. (2021) 'Elliot: A comprehensive and rigorous framework for reproducible recommender systems evaluation', in Proceedings of the 44th International ACM SIGIR Conference on Research and Development in Information Retrieval. doi: 10.1145/3404835.3463245.

Assuncao, W.G., Piccolo, L.S.G. and Zaina, L.A.M. (2022) 'Considering emotions and contextual factors in music recommendation: a systematic literature review', Multimedia Tools and Applications, 81(6), pp. 8367-8407. doi: 10.1007/s11042-022-12110-z.

Balog, K., Radlinski, F. and Arakelyan, S. (2019) 'Transparent, scrutable and explainable user models for personalized recommendation', in Proceedings of the 42nd International ACM SIGIR Conference on Research and Development in Information Retrieval, pp. 265-274. doi: 10.1145/3331184.3331211.

Barlaug, N. and Gulla, J.A. (2021) 'Neural networks for entity matching: a survey', ACM Transactions on Knowledge Discovery from Data. doi: 10.1145/3442200.

Bauer, C., Zangerle, E. and Said, A. (2024) 'Exploring the landscape of recommender systems evaluation: practices and perspectives', ACM Transactions on Recommender Systems. doi: 10.1145/3629170.

Beel, J., Breitinger, C., Langer, S. and Gipp, B. (2016) 'Towards reproducibility in recommender-systems research', User Modeling and User-Adapted Interaction. doi: 10.1007/s11257-016-9174-x.

Bellogin, A. and Said, A. (2021) 'Improving accountability in recommender systems research through reproducibility', User Modeling and User-Adapted Interaction. doi: 10.1007/s11257-021-09302-x.

Bertin-Mahieux, T., Ellis, D.P.W., Whitman, B. and Lamere, P. (2011) 'The Million Song Dataset', in Proceedings of the 12th International Society for Music Information Retrieval Conference (ISMIR 2011).

Betello, F., Purificato, A., Siciliano, F., Trappolini, G., Bacciu, A., Tonellotto, N. and Silvestri, F. (2025) 'A reproducible analysis of sequential recommender systems', IEEE Access. doi: 10.1109/ACCESS.2024.3522049.

Binette, O. and Steorts, R.C. (2022) '(Almost) all of entity resolution', Science Advances. doi: 10.1126/sciadv.abi8021.

Bogdanov, D., Haro, M., Fuhrmann, F., Xambo, A., Gomez, E. and Herrera, P. (2013) 'Semantic audio content-based music recommendation and visualization based on user preference examples', Information Processing and Management, 49(1), pp. 13-33. doi: 10.1016/j.ipm.2012.06.004.

Bonnin, G. and Jannach, D. (2015) 'Automated generation of music playlists: survey and experiments', ACM Computing Surveys, 47(2), pp. 1-35. doi: 10.1145/2652481.

Bo Shao, Ogihara, M., Dingding Wang and Tao Li (2009) 'Music recommendation based on acoustic features and user access patterns', IEEE Transactions on Audio, Speech, and Language Processing, 17(8), pp. 1602-1611. doi: 10.1109/TASL.2009.2020893.

Cano, E. and Morisio, M. (2017) 'Hybrid recommender systems: a systematic literature review', Intelligent Data Analysis, 21(6), pp. 1487-1524. doi: 10.3233/IDA-163209.

Cavenaghi, E., Sottocornola, S., Stella, F. and Zanker, M. (2023) 'A systematic study on reproducibility of reinforcement learning in recommendation systems', ACM Transactions on Recommender Systems. doi: 10.1145/3596519.

Deldjoo, Y., Schedl, M. and Knees, P. (2024) 'Content-driven music recommendation: evolution, state of the art, and challenges', Computer Science Review, 51, p. 100618. doi: 10.1016/j.cosrev.2024.100618.

Elmagarmid, A.K., Ipeirotis, P.G. and Verykios, V.S. (2007) 'Duplicate record detection: a survey', IEEE Transactions on Knowledge and Data Engineering. doi: 10.1109/TKDE.2007.250581.

Ferrari Dacrema, M., Boglio, S., Cremonesi, P. and Jannach, D. (2021) 'A troubling analysis of reproducibility and progress in recommender systems research', ACM Transactions on Information Systems. doi: 10.1145/3434185.

Ferraro, A., Bogdanov, D., Yoon, J., Kim, K. and Serra, X. (2018) 'Automatic playlist continuation using a hybrid recommender system combining features from text and audio', in Proceedings of the ACM Recommender Systems Challenge 2018. doi: 10.1145/3267471.3267473.

Fkih, F. (2022) 'Similarity measures for collaborative filtering-based recommender systems: review and experimental comparison', Journal of King Saud University - Computer and Information Sciences, 34(9), pp. 7645-7669. doi: 10.1016/j.jksuci.2021.09.014.

Flexer, A. and Grill, T. (2016) 'The problem of limited inter-rater agreement in modelling music similarity', Journal of New Music Research, 45(3), pp. 239-251. doi: 10.1080/09298215.2016.1200631.

Furini, M. and Fragnelli, F. (2024) 'Social music discovery: an ethical recommendation system based on friend's preferred songs', Multimedia Tools and Applications, 84(14), pp. 13469-13483. doi: 10.1007/s11042-024-19505-0.

Gatzioura, A., Vinagre, J., Jorge, A.M. and Sanchez-Marre, M. (2019) 'A hybrid recommender system for improving automatic playlist continuation', IEEE Transactions on Knowledge and Data Engineering. doi: 10.1109/TKDE.2019.2952099.

He, X., Liao, L., Zhang, H., Nie, L., Hu, X. and Chua, T.-S. (2017) 'Neural collaborative filtering', in Proceedings of the 26th International Conference on World Wide Web, pp. 173-182. doi: 10.1145/3038912.3052569.

Herlocker, J.L., Konstan, J.A., Terveen, L.G. and Riedl, J.T. (2004) 'Evaluating collaborative filtering recommender systems', ACM Transactions on Information Systems. doi: 10.1145/963770.963772.

Jannach, D. and Jugovac, M. (2019) 'Measuring the business value of recommender systems', ACM Transactions on Management Information Systems. doi: 10.1145/3370082.

Jin, Y., Tintarev, N., Htun, N.N. and Verbert, K. (2020) 'Effects of personal characteristics in control-oriented user interfaces for music recommender systems', User Modeling and User-Adapted Interaction, 30(2), pp. 199-249. doi: 10.1007/s11257-019-09247-2.

Kang, J. and Herremans, D. (2025) 'Are we there yet? A brief survey of music emotion prediction datasets, models and outstanding challenges', IEEE Transactions on Affective Computing. doi: 10.1109/TAFFC.2025.3583505.

Knijnenburg, B.P., Willemsen, M.C., Gantner, Z., Soncu, H. and Newell, C. (2012) 'Explaining the user experience of recommender systems', User Modeling and User-Adapted Interaction, 22(4), pp. 441-504. doi: 10.1007/s11257-011-9118-4.

Knox, D., Greer, T., Ma, B., Kuo, E., Somandepalli, K. and Narayanan, S. (2021) 'Loss function approaches for multi-label music tagging', in 2021 International Conference on Content-Based Multimedia Indexing (CBMI). doi: 10.1109/CBMI50038.2021.9461913.

Kowald, D., Muellner, P., Zangerle, E., Bauer, C., Schedl, M. and Lex, E. (2021) 'Support the underground: characteristics of beyond-mainstream music listeners', EPJ Data Science. doi: 10.1140/epjds/s13688-021-00268-9.

Liu, J. (2025) 'Aggregating contextual information for multi-criteria online music recommendations', IEEE Access. doi: 10.1109/ACCESS.2025.3527512.

Liu, Q., Hu, J., Xiao, Y., Zhao, X., Gao, J., Wang, W., Li, Q. and Tang, J. (2025) 'Multimodal recommender systems: a survey', ACM Computing Surveys, 57(2), pp. 1-17. doi: 10.1145/3695461.

Lopes, P., Silva, E., Braga, C., Oliveira, T. and Rosado, L. (2022) 'XAI systems evaluation: a review of human and computer-centred methods', Applied Sciences, 12(19), p. 9423. doi: 10.3390/app12199423.

Lu, J., Wu, D., Mao, M., Wang, W. and Zhang, G. (2015) 'Recommender system application developments: a survey', Decision Support Systems, 74, pp. 12-32. doi: 10.1016/j.dss.2015.03.008.

McFee, B., Bertin-Mahieux, T., Ellis, D.P.W. and Lanckriet, G.R.G. (2012) 'The million song dataset challenge', in Proceedings of the 21st International Conference on World Wide Web, pp. 909-916. doi: 10.1145/2187980.2188222.

Moysis, L., Iliadis, L.A., Sotiroudis, S.P., Boursianis, A.D., Papadopoulou, M.S., Kokkinidis, K.-I.D., Volos, C., Sarigiannidis, P., Nikolaidis, S. and Goudos, S.K. (2023) 'Music deep learning: deep learning methods for music signal processing - a review of the state-of-the-art', IEEE Access. doi: 10.1109/ACCESS.2023.3244620.

Nauta, M., Trienes, J., Pathak, S., Nguyen, E., Peters, M., Schmitt, Y., Schlotterer, J., Van Keulen, M. and Seifert, C. (2023) 'From anecdotal evidence to quantitative evaluation methods: a systematic review on evaluating explainable AI', ACM Computing Surveys, 55(13), pp. 1-42. doi: 10.1145/3583558.

Neto, P.A.S.O., Hartmann, M., Luck, G. and Toiviainen, P. (2023) 'The algorithmic nature of song-sequencing: statistical regularities in music albums', Journal of New Music Research, 52(5), pp. 410-424. doi: 10.1080/09298215.2024.2423610.

Pandeya, Y.R., You, J., Bhattarai, B. and Lee, J. (2021) 'Multi-modal, multi-task and multi-label for music genre classification and emotion regression', in 2021 International Conference on Information and Communication Technology Convergence (ICTC). doi: 10.1109/ICTC52510.2021.9620826.

Papadakis, G., Skoutas, D., Thanos, E. and Palpanas, T. (2021) 'Blocking and filtering techniques for entity resolution: a survey', ACM Computing Surveys. doi: 10.1145/3377455.

Pegoraro Santana, I.A., Pinhelli, F., Donini, J., Catharin, L., Mangolin, R.B., Da Costa, Y.M.E.G., Delisandra Feltrim, V. and Domingues, M.A. (2020) 'Music4All: a new music database and its applications', in 2020 International Conference on Systems, Signals and Image Processing (IWSSIP). doi: 10.1109/IWSSIP48289.2020.9145170.

Roy, D. and Dutta, M. (2022) 'A systematic review and research perspective on recommender systems', Journal of Big Data, 9(1), p. 59. doi: 10.1186/s40537-022-00592-5.

Ru, G., Zhang, X., Wang, J., Cheng, N. and Xiao, J. (2023) 'Improving music genre classification from multi-modal properties of music and genre correlations perspective', in ICASSP 2023 - 2023 IEEE International Conference on Acoustics, Speech and Signal Processing. doi: 10.1109/ICASSP49357.2023.10097241.

Sanchez, P.M. and Bellogin, A. (2022) 'Point-of-interest recommender systems based on location-based social networks: a survey from an experimental perspective', ACM Computing Surveys. doi: 10.1145/3510409.

Schedl, M. (2017) 'Investigating country-specific music preferences and music recommendation algorithms with the LFM-1b dataset', International Journal of Multimedia Information Retrieval. doi: 10.1007/s13735-017-0118-y.

Schedl, M., Zamani, H., Chen, C.-W., Deldjoo, Y. and Elahi, M. (2018) 'Current challenges and visions in music recommender systems research', International Journal of Multimedia Information Retrieval, 7(2), pp. 95-116. doi: 10.1007/s13735-018-0154-2.

Schweiger, H., Parada-Cabaleiro, E. and Schedl, M. (2025) 'The impact of playlist characteristics on coherence in user-curated music playlists', EPJ Data Science, 14(1), p. 24. doi: 10.1140/epjds/s13688-025-00531-3.

Shakespeare, D., Chareyron, V. and Roth, C. (2025) 'Reframing the filter bubble through diverse scale effects in online music consumption', Scientific Reports. doi: 10.1038/s41598-024-75967-0.

Siedenburg, K. and Mullensiefen, D. (2017) 'Modeling timbre similarity of short music clips', Frontiers in Psychology. doi: 10.3389/fpsyg.2017.00639.

Sotirou, T., Lyberatos, V., Mastromichalakis, O.M. and Stamou, G. (2025) 'MusicLIME: explainable multimodal music understanding', in ICASSP 2025 - 2025 IEEE International Conference on Acoustics, Speech and Signal Processing. doi: 10.1109/ICASSP49660.2025.10889771.

Teinemaa, I., Tax, N., Bentes, C., Semikin, M., Treimann, M.L. and Safka, C. (2018) 'Automatic playlist continuation through a composition of collaborative filters', RecSys Challenge 2018 Team Latte report.

Tintarev, N. and Masthoff, J. (2007) 'A survey of explanations in recommender systems', in 2007 IEEE 23rd International Conference on Data Engineering Workshop, pp. 801-810. doi: 10.1109/ICDEW.2007.4401070.

Tintarev, N. and Masthoff, J. (2012) 'Evaluating the effectiveness of explanations for recommender systems: methodological issues and empirical studies on the impact of personalization', User Modeling and User-Adapted Interaction, 22(4), pp. 399-439. doi: 10.1007/s11257-011-9117-5.

Tsai, C.-H. and Brusilovsky, P. (2018) 'Explaining social recommendations to casual users: design principles and opportunities', in Companion Proceedings of the 23rd International Conference on Intelligent User Interfaces, pp. 1-2. doi: 10.1145/3180308.3180368.

Vall, A., Dorfer, M., Eghbal-zadeh, H., Schedl, M., Burjorjee, K. and Widmer, G. (2019) 'Feature-combination hybrid recommender systems for automated music playlist continuation', User Modeling and User-Adapted Interaction, 29(2), pp. 527-572. doi: 10.1007/s11257-018-9215-8.

Yu, R., Yin, X., Xia, L., Chen, T., Li, Z. and Huang, C. (2024) 'Self-supervised learning for recommender systems: a survey', IEEE Transactions on Knowledge and Data Engineering. doi: 10.1109/TKDE.2023.3282907.

Zamani, H., Schedl, M., Lamere, P. and Chen, C.-W. (2019) 'An analysis of approaches taken in the ACM RecSys Challenge 2018 for automatic music playlist continuation', ACM Transactions on Intelligent Systems and Technology, 10(5), pp. 1-21. doi: 10.1145/3344257.

Zhang, Y. and Chen, X. (2020) 'Explainable recommendation: a survey and new perspectives', Foundations and Trends in Information Retrieval, 14(1), pp. 1-101. doi: 10.1561/1500000066.

Zhu, H., Zhou, Y., Chen, H., Yu, J., Ma, Z., Gu, R., Luo, Y., Tan, W. and Chen, X. (2025) 'MuQ: self-supervised music representation learning with Mel residual vector quantization', IEEE Transactions on Audio, Speech, and Language Processing. doi: 10.1109/TASLPRO.2025.3602320.

Zhu, J., Dai, Q., Su, L., Ma, R., Liu, J., Cai, G., Xiao, X. and Zhang, R. (2022) 'BARS', in Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval. doi: 10.1145/3477495.3531723.

# Bibliography

This section is intentionally omitted in the final version if all listed sources are cited in the main text.

# Appendices

## Appendix A: System Architecture Diagrams

[Insert full architecture diagrams and any expanded versions of Chapter 3 figures.]

## Appendix B: Configuration Profiles and Example Runs

[Insert representative configuration files, parameter sets, and run metadata examples.]

## Appendix C: Experiment Logs and Test Evidence

[Insert supporting logs, hashes, screenshots, and detailed result tables if too large for Chapter 4.]

## Appendix D: Extended Mapping Tables

[Insert any expanded requirement-mechanism-evidence tables or chapter handoff tables that are too large for the main body.]

## Appendix E: Additional Figures and Tables

[Insert supplementary tables, diagrams, or output examples.]

## Appendix F: Project Management Evidence Extracts

[Insert selected logbook pages, milestone snapshots, supervision record extracts, replanning evidence, or timeline artefacts if these are not already submitted separately and if including them strengthens the report evidence.]
