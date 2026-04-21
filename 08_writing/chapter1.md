# Chapter 1: Introduction

## 1.1 Project Motivation
Music streaming platforms give users access to large music catalogues. While this increases choice, it also makes it harder to find tracks that match user preferences. Recommender systems support music discovery and playlist generation.

Many practical systems measure recommendation quality primarily by predictive accuracy. Accuracy alone does not meet the needs of users or evaluators who need to understand, adjust, and verify system behaviour. This project addresses transparency, controllability, observability, and reproducibility requirements.

These requirements become especially important when preference evidence comes from implicit signals such as listening history. Listening history remains useful yet uncertain: it may reflect habit, convenience, or interface effects rather than genuine preference. A recommendation pipeline that treats it as direct ground truth can produce outputs that users and evaluators cannot inspect or challenge.

Further complications arise when user-side listening data and the candidate track corpus come from different sources, use different identifiers, and have varying metadata quality. This cross-source condition introduces alignment gaps and coverage uncertainty that can affect every stage of the pipeline, from profiling through to final playlist assembly. This project directly responds to that challenge.

## 1.2 Recommender Systems and Music Recommendation
A recommender system functions as a computational tool that filters and ranks items according to estimated user relevance (Adomavicius and Tuzhilin, 2005; Lu et al., 2015). It predicts which items users will likely find useful based on available evidence such as prior interactions, metadata, and context. In music settings, this typically means selecting tracks from a large corpus based on inferred listening preferences.

Music recommendation remains a well-established application of recommender systems. Unlike simple item retrieval, playlist generation involves collection-level properties including coherence, diversity, novelty, and ordering (Bonnin and Jannach, 2015; Schedl et al., 2018). A good playlist includes more than a set of individually relevant tracks; it needs to work as a sequence.

Users and evaluators also need to understand why the system selected specific tracks and how control changes affect the output. This interpretability need sits at the center of this system design.

## 1.3 Cross-Source Data, Transparency, and Controllability
In this project, cross-source data refers to combining user listening history evidence with a separate candidate-track corpus and its associated audio and metadata features. This practical arrangement introduces uncertainty at the alignment stage: some records will not match, some matches remain ambiguous, and metadata completeness will vary across sources.

Transparency and controllability provide the main responses to that uncertainty. In this project, transparency means users and evaluators can trace and verify system behaviour at each stage. Controllability means users and evaluators can adjust settings and directly observe output changes. Together with observability and reproducibility, these properties define the quality standard used throughout this project.

Figure 1.1 illustrates the high-level structure of the pipeline developed in this thesis.

![Figure 1.1. High-level pipeline logic: Cross-source listening evidence -> Alignment and uncertainty handling -> Preference profiling -> Candidate shaping -> Deterministic scoring -> Playlist assembly -> Explanation and observability outputs.](figures/figure_1_1_pipeline.svg)

## 1.4 Research Question, Aim, and Objectives

### Research Question

How can we design and assess a deterministic playlist generation pipeline that remains transparent, controllable, and reproducible when user preference data and candidate tracks come from different sources?

### Aim

This project aims to build and assess a playlist generation pipeline whose stages users and evaluators can inspect, adjust, and reproduce, even when user data and candidate tracks come from different sources.

### Objectives

1. Design a preference profiling approach from user listening history across different data sources.
2. Build cross-source alignment and candidate filtering with explicit uncertainty handling.
3. Build deterministic scoring and playlist assembly with controls for coherence, diversity, novelty, and ordering.
4. Produce explanation and logging outputs that show pipeline decision logic.
5. Assess how well the pipeline reproduces results and how playlist quality changes when settings change.
6. Identify the limits of the results and the conditions under which the conclusions apply.

## 1.5 Scope and Boundaries
This project focuses on a single-user content-based pipeline using a fixed candidate corpus based on Music4All (Pegoraro Santana et al., 2020). It does not include collaborative filtering, deep learning models, multi-user personalisation, or large-scale user studies. These boundaries keep the project tractable and allow the evaluation to focus on transparency and controllability.

## 1.6 Contribution of the Project
This project contributes a transparent, controllable, and reproducible playlist generation pipeline. It shows how users and evaluators can inspect, adjust, and assess recommendation behaviour when user listening data and candidate tracks come from different sources. Each stage produces outputs that support verification, and setting changes produce measurable effects.

## 1.7 Report Framework
This report has the following structure:

- **Chapter 2** reviews the literature on recommender systems, music recommendation, transparency, implicit preference evidence, and cross-source data issues.
- **Chapter 3** presents the design approach and system architecture, grounded in the gaps and requirements identified in Chapter 2.
- **Chapter 4** describes the implementation of the pipeline artefact and the evidence it produces.
- **Chapter 5** presents the evaluation results, covering reproducibility, controllability, and playlist trade-off behaviour.
- **Chapter 6** discusses the findings, contribution boundaries, limitations, and directions for future work.

## 1.8 Chapter Summary
This chapter has introduced the motivation, research question, aim, objectives, scope, and structure of the project. Chapter 2 now reviews the literature on recommender systems, implicit preference signals, and transparency requirements that inform the design developed in Chapter 3.
