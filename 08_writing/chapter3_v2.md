# Chapter 3: Design and Methodology (V2)

## 3.1 Methodological Position and Chapter Role
This thesis follows a Design Science Research (DSR) stance in which literature findings are translated into engineering requirements, those requirements are operationalized as artefact design decisions, and the resulting artefact is later evaluated against the qualities named in the research question [@jannach_measuring_2019; @anelli_elliot_2021]. Within the locked thesis method flow, Chapter 2 established the literature basis for a transparent, controllable, and observable playlist-generation pipeline using cross-source music preference data. Chapter 3 converts that basis into an implementable design.

The chapter therefore serves two purposes. First, it explains why the proposed artefact architecture is appropriate for the problem and thesis contribution. Second, it defines the concrete design commitments that later chapters will implement and test. In keeping with the methodology definition, these commitments are treated as design hypotheses rather than proven outcomes until Chapter 4 supplies implementation and evaluation evidence.

This distinction matters for claim discipline. The chapter does not argue that deterministic feature-based recommendation is universally superior to hybrid or neural alternatives. It argues that, under the locked artefact scope, deterministic feature-based design is the most defensible way to engineer a pipeline whose behavior can be inspected, controlled, logged, and replayed [@zhang_explainable_2020; @beel_towards_2016]. The contribution of the thesis is thus design knowledge about how such an artefact can be engineered, not model-family novelty.

Method consequence: every major design commitment in this chapter must remain traceable to literature evidence, scope controls, and later implementation/testing artifacts.

## 3.2 Literature-Derived Design Requirements
The proposed artefact design is driven by five requirement groups derived from the literature review and the locked thesis scope.

First, recommendation behavior must be inspectable. Explainability literature shows that recommendation quality cannot be judged by predictive performance alone when users or evaluators must understand how outputs were produced [@tintarev_survey_2007; @tintarev_evaluating_2012; @zhang_explainable_2020]. For this artefact, inspectability means that recommendation outputs can be traced back to concrete feature values, scoring contributions, and rule adjustments rather than only to a post-hoc narrative.

Second, the artefact must expose practical controllability. Music recommender studies suggest that explicit user influence can be useful, but control mechanisms should be understandable and evaluated through observable effects rather than assumed to be universally beneficial [@jin_effects_2020; @andjelkovic_moodplay_2019]. In this thesis, controllability is therefore implemented through bounded, explicit inputs such as influence tracks and configurable scoring or assembly parameters.

Third, the design must respect playlist-specific quality constraints. Music recommendation is not reducible to isolated item ranking because playlists involve sequencing, diversity, repetition management, and flow [@schedl_current_2018; @neto_algorithmic_2023; @gatzioura_hybrid_2019]. The artefact therefore requires a distinct playlist-assembly stage rather than treating top-ranked items as a complete final output.

Fourth, cross-source track alignment must be treated as a first-class engineering problem. The research question explicitly depends on combining externally sourced listening history with a canonical feature corpus. Entity-resolution literature supports staged matching pipelines with diagnosable steps and explicit failure reporting [@allam_improved_2018; @papadakis_blocking_2021; @elmagarmid_duplicate_2007]. This makes alignment design integral to the architecture rather than a hidden preprocessing detail.

Fifth, observability and reproducibility must be engineered directly into execution. Recommender-system reproducibility literature consistently shows that weak protocol and configuration reporting undermine accountability and make results difficult to interpret or compare [@beel_towards_2016; @bellogin_improving_2021; @cavenaghi_systematic_2023; @ferrari_dacrema_troubling_2021]. For this artefact, observability means that run context, parameter settings, diagnostics, and outputs are captured in a way that makes the system replayable and critique-ready.

These requirements jointly constrain the design space. They favor a deterministic pipeline with explicit intermediate representations, explicit control surfaces, staged data handling, and persistent run logging over a more opaque architecture optimized primarily for predictive performance.

Design consequence: the artefact architecture must separate major pipeline stages clearly enough that each requirement group can later be tested in Chapter 4.

## 3.3 Artefact Architecture Overview
The artefact is designed as a layered deterministic pipeline composed of the following stages:

1. user input and execution configuration,
2. data ingestion,
3. cross-source track alignment,
4. preference-profile construction,
5. candidate retrieval and filtering,
6. feature preparation,
7. deterministic scoring,
8. playlist assembly,
9. explanation generation,
10. observability and audit logging.

This layered structure is chosen to preserve traceability from input to output. Each stage performs a bounded transformation and emits artifacts that can be inspected directly or consumed by the next stage. This supports the thesis contribution in two ways. It makes the pipeline understandable as an engineered artefact, and it allows later evaluation to attribute behavior to identifiable mechanisms rather than to an inseparable monolithic process.

The architecture also remains aligned with the locked MVP boundary. It is single-user, deterministic, content-based, and limited to one practical ingestion path plus optional influence tracks. It does not attempt to implement collaborative filtering, end-to-end deep learning, or broad multi-adapter coverage. Those omissions are not treated as missing sophistication but as deliberate scope control preserving the artefact’s inspectability and feasibility.

At a high level, the artefact flow is:

external listening history plus optional influence tracks -> normalized events -> aligned canonical tracks -> user preference profile -> candidate pool -> deterministic ranking -> playlist assembly -> explanation artifacts plus run logs.

This flow ensures that the core qualities named in the research question are not confined to the final interface. Transparency, controllability, and observability are distributed across the architecture itself.

Design consequence: each stage should emit enough intermediate structure to support explanation, debugging, and replay rather than acting as an opaque internal step.

## 3.4 Input Boundary, Ingestion, and Cross-Source Alignment
The artefact deliberately constrains its input boundary to a single practical listening-history source format and optional manual influence tracks. This narrow ingestion scope is a design decision, not a weakness. It keeps the artefact within BSc feasibility while still addressing the real engineering challenge of importing user preference signals from an external source.

After ingestion, track records must be aligned to the canonical corpus used for candidate retrieval and scoring. The design adopts an ISRC-first matching strategy with metadata fallback. This follows the staged entity-resolution logic supported by the literature: prefer a precise identifier path where available, then use controlled fallback logic where identifier coverage is incomplete [@allam_improved_2018; @papadakis_blocking_2021].

The alignment stage therefore has three explicit responsibilities:

1. normalize imported records into a stable internal schema,
2. attempt exact identifier matching using ISRC where available,
3. attempt bounded metadata fallback matching for remaining eligible records.

This stage must also produce diagnostics rather than only matched outputs. At minimum, the system should record how many rows were ingested, how many were valid for matching, how many matched by ISRC, how many matched by fallback, and how many remained unmatched. This is necessary because the literature support for alignment is stronger at the domain-general entity-resolution level than at the music-specific benchmark level. The artefact must therefore expose uncertainty rather than hide it.

More advanced neural matching methods remain acknowledged comparator context [@barlaug_neural_2021], but they are excluded from the core artefact because they would increase complexity and reduce direct inspectability without being necessary to answer the research question.

Design consequence: the alignment stage must emit both aligned outputs and bounded-risk diagnostics so later chapters can evaluate not only success cases but also failure visibility.

## 3.5 Preference Profile Construction and Candidate Preparation
Once matched tracks are available in the canonical feature space, the artefact constructs a deterministic user preference profile. This profile is the central representation linking raw user history to candidate ranking behavior. For the design to remain interpretable, the profile must be derived from explicit, reviewable operations over aligned listening data and optional influence tracks rather than from opaque latent training.

The profile-construction stage is therefore designed around interpretable feature aggregation. Listening history contributes observed preference evidence, while manually supplied influence tracks provide an explicit way for the user to bias or refine the profile. This aligns with the thesis requirement for controllability: user influence should not exist only as hidden model-side data, but as an intentional and inspectable part of the pipeline.

Candidate preparation then restricts the search space before scoring. This is necessary both for tractability and for methodological clarity. A smaller, explicitly defined candidate pool makes it easier to understand why a track was or was not considered, and it reduces the risk that hidden retrieval heuristics dominate the behavior later attributed to scoring.

Feature preparation is treated as a distinct design step. Feature scaling, missing-value handling, and attribute selection must be explicit because these decisions materially affect deterministic similarity outcomes. Even where literature support for individual preprocessing choices is weaker than for the broader design rationale, the thesis can justify explicit preprocessing as a requirement of auditability and metric discipline rather than as a claim that one preprocessing setup is universally optimal.

Design consequence: preference construction and candidate preparation should preserve feature-level visibility so that downstream scores can be reconstructed and challenged.

## 3.6 Deterministic Scoring Design
The scoring stage ranks prepared candidates using deterministic similarity functions and explicit weighting rules. This is one of the core design commitments of the thesis because scoring is where transparency, controllability, and observability converge most directly.

The literature reviewed in Chapter 2 supports feature-based and deterministic scoring as a goal-aligned design choice for artefacts emphasizing inspectability and replayability [@deldjoo_content-driven_2024; @bogdanov_semantic_2013; @zhang_explainable_2020]. The design consequence is that no critical ranking decision should depend on hidden learned representations or unlogged stochastic behavior. Under fixed inputs and configuration, the scoring stage should produce the same outputs repeatedly.

This stage is parameterized rather than hard-coded. Metric choice, feature weights, and rule-based adjustments are treated as design parameters that can later be varied in controllability tests. This is important because the literature shows that metric choice can materially alter ranking behavior and that metric effects should not be hidden as accidental defaults [@fkih_similarity_2022; @flexer_problem_2016; @siedenburg_modeling_2017; @furini_social_2024; @schweiger_impact_2025].

The design also requires score decomposition. For each candidate, the system should be able to expose the main contributing components of the final score so that explanation outputs are faithful to the ranking logic. This prevents explanation from becoming a disconnected descriptive layer.

Design consequence: the scoring stage must expose explicit metric, weight, and contribution information so that Chapter 4 can test replayability, parameter sensitivity, and explanation fidelity.

## 3.7 Playlist Assembly and Rule-Based Output Construction
The artefact does not treat ranking as equivalent to playlist generation. Instead, playlist assembly is a separate stage that applies explicit collection-level rules after scoring. This follows the playlist literature showing that ordering, repetition control, diversity, and coherence are central to playlist quality and cannot be reduced to item-level relevance alone [@schedl_current_2018; @neto_algorithmic_2023; @vall_feature-combination_2019].

At minimum, the assembly stage should enforce:

1. playlist length,
2. artist repetition limits,
3. at least one diversity or ordering control.

This separation matters for both engineering and evaluation. Engineering-wise, it clarifies where sequence-level decisions are made. Evaluation-wise, it allows Chapter 4 to inspect rule compliance independently of scoring quality. If a playlist violates a configured constraint, the system should report that explicitly rather than silently absorbing the inconsistency.

The assembly stage is also a key site of controllability. Some controls should affect candidate scoring, while others should affect assembly behavior. Keeping these locations explicit allows the thesis to show not only that controls exist, but where they act in the pipeline and how their effects propagate.

Design consequence: playlist assembly must remain a distinct, auditable stage with explicit rule definitions and violation visibility.

## 3.8 Explanation, Observability, and Reproducibility Controls
Explanation and observability are not appended after the main recommendation pipeline; they are coupled to it. The design requires explanation outputs to be generated directly from score contributors and rule adjustments so that explanation remains mechanism-linked rather than narrative-only. This is the primary transparency safeguard of the artefact.

Observability extends that safeguard from individual recommendations to whole-run behavior. The artefact should log enough structured information to reconstruct what happened during execution: input summaries, alignment diagnostics, configuration state, score traces, ranked outputs, playlist outputs, and rule-compliance outcomes. These logs serve three purposes.

First, they support user- and evaluator-facing transparency by showing how outputs were obtained. Second, they support developer-facing debugging and bounded failure analysis. Third, they support reproducibility by making repeated runs under fixed configuration directly comparable.

This stage operationalizes the thesis meaning of observability. Observability here is not production telemetry in the software-operations sense. It is artefact-level execution visibility sufficient for audit, replay, and evaluative interpretation. That narrower definition fits the thesis scope while remaining technically meaningful.

The design therefore requires a persistent configuration profile and run-level artifact capture. Without these, Chapter 4 could only report outputs, not the conditions under which those outputs were produced.

Design consequence: every evaluation-critical run should generate a traceable artifact set that links configuration, intermediate behavior, and final outputs.

## 3.9 Configuration and Execution Model
The artefact needs a controlled execution model to make both development and evaluation coherent. A persistent configuration profile should define feature weights, filter thresholds, rule parameters, and execution settings. This profile acts as the interface between design intention and actual system behavior.

From a methodology perspective, configuration capture is what turns controllability from a conceptual property into a testable one. If a parameter cannot be saved, replayed, and compared across runs, then its effect cannot be reliably evaluated. For this reason, configuration is not treated as incidental implementation detail. It is part of the artefact’s methodologically relevant design.

The execution model should therefore support two modes:

1. baseline replay, where fixed input and fixed configuration are rerun to verify deterministic behavior,
2. controlled variation, where one selected parameter is changed at a time to observe interpretable effects.

This structure aligns directly with the Chapter 4 evaluation plan and ensures that controllability and reproducibility can be tested as designed qualities rather than discussed only in theory.

Design consequence: saved configuration and disciplined execution control are mandatory architecture elements, not convenience features.

## 3.10 Design Traceability and Chapter Handoff
The design in this chapter is traceable back to the literature review and forward to implementation and evaluation evidence. Its key commitments can be summarized as follows:

1. use a deterministic, feature-based pipeline because the thesis prioritizes inspectability, controllability, observability, and replayability,
2. treat cross-source alignment as a staged, diagnosable process with explicit uncertainty reporting,
3. represent user preference through explicit and interpretable profile construction,
4. separate candidate retrieval, scoring, and playlist assembly so behavior remains attributable to distinct mechanisms,
5. generate explanation outputs and run logs directly from actual pipeline behavior,
6. persist configuration state so sensitivity and replay experiments are possible.

These commitments operationalize the Chapter 2 synthesis without claiming that the design has already been validated. Validation is the responsibility of later implementation and evaluation chapters. If implementation evidence later contradicts a design assumption, the correct response is refinement and explicit discussion, not retrospective overclaiming.

Overall, Chapter 3 frames the artefact as a transparent, controllable, and observable engineering pipeline rather than a black-box recommender. The chapter therefore bridges the literature review and the evaluation chapter by making the research question implementable.

Chapter transition: Chapter 4 should test whether the implemented artefact actually exhibits the properties designed here, with particular attention to alignment diagnostics, profile construction behavior, deterministic replay, explanation fidelity, control sensitivity, and playlist rule compliance.