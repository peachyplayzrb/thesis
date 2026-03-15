# Chapter 5

## 5.1 Evaluation Interpretation and Comparator Framing
Evaluation results in this thesis are interpreted as evidence for design-goal alignment (transparency, controllability, observability, and reproducibility), not as claims of universal recommendation superiority. This interpretation follows literature showing that practical value and scientific validity depend on explicit objective-metric alignment and clear reporting of protocol assumptions [@jannach_measuring_2019; @bauer_exploring_2024; @anelli_elliot_2021; @ferrari_dacrema_troubling_2021].

Accordingly, complex hybrid and self-supervised recommender families are treated as comparator context that motivates careful scope positioning rather than direct implementation requirements for this locked MVP artefact [@liu_multimodal_2025; @yu_self_supervised_2024].

## 5.2 Scope-Bounded Claim Discipline
The contribution claim is scoped to deterministic pipeline engineering under explicit transparency and observability constraints. Any discussion of performance trade-offs is framed as conditional on objectives, data conditions, and protocol choices, consistent with the chapter-level citation risk controls.

## 5.3 Findings in Relation to the Research Question
The research question asks what design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data. Based on the literature synthesis and current implementation evidence, the key design considerations are:

1. Goal-aligned method selection over model-family absolutism. Method choice should be driven by target qualities (inspectability, controllability, observability, reproducibility) rather than assumed universal superiority of any single recommender family [@roy_systematic_2022; @jannach_measuring_2019].
2. Staged cross-source alignment with explicit uncertainty handling. ISRC-first matching with metadata fallback is a practical and inspectable design, but unmatched/ambiguous cases must be surfaced as first-class outputs [@papadakis_blocking_2021; @allam_improved_2018].
3. Deterministic scoring and rule-based assembly for traceability. Explicit feature contributions and rule effects make explanation outputs and debugging behavior auditable in ways that opaque pipelines do not [@zhang_explainable_2020; @tintarev_survey_2007].
4. Evaluation protocol discipline as part of system design. Reproducibility and interpretation quality depend on logging, configuration traceability, and clear metric-objective alignment [@beel_towards_2016; @bauer_exploring_2024; @anelli_elliot_2021].
5. Comparator-awareness without scope drift. Hybrid and self-supervised systems are relevant context for trade-off discussion, but not required for validating this locked MVP contribution [@liu_multimodal_2025; @yu_self_supervised_2024].

Current implementation tests (ingestion schema validation and ISRC-first alignment with deterministic-repeat checks) provide early support for feasibility of considerations 2 and 4. Full end-to-end evidence for candidate generation, deterministic scoring, playlist assembly, and controllability outcomes remains pending and is required for complete RQ closure.

## 5.4 Limitations
This thesis has several explicit limitations that constrain interpretation of results.

1. Scope limitation: The artefact is single-user, content-based, and deterministic by design, so findings are not generalized to collaborative, deep, or large-scale production recommenders.
2. Data alignment limitation: Some imported tracks may not align reliably to the canonical corpus; current support is strongest for staged ER methods in general, with weaker music-specific benchmark evidence.
3. Evaluation-stage limitation: At present, implemented and tested evidence is concentrated on ingestion and alignment; complete empirical validation of scoring, assembly, and controllability is not yet finalized.
4. Comparator limitation: No implemented deep/hybrid baseline is included in MVP, so comparisons against modern high-capacity models remain literature-grounded rather than experimentally demonstrated in this artefact.
5. External-validity limitation: Evaluation is BSc-feasible and does not include large-scale user studies or long-horizon behavioral outcomes.

These limitations do not invalidate the contribution, but they bound it to system-design guidance under transparent deterministic constraints.

## 5.5 Future Work
Future work should extend this artefact in ways that preserve traceability while strengthening evidence.

1. Complete the remaining P0 implementation and evaluation backlog items (`BL-004` to `BL-012`) to produce full end-to-end design evidence.
2. Add a focused music-domain alignment reliability benchmark study (for example ISRC/metadata ambiguity and error-rate analysis) to reduce current evidence risk.
3. Execute structured controllability experiments (parameter-sensitivity matrix) and integrate outcomes into run-level observability logs.
4. Add at least one comparator pipeline (for example a lightweight hybrid baseline) with protocol-matched evaluation to improve trade-off analysis without scope inflation.
5. Expand from one ingestion adapter to additional adapters only after MVP evidence is complete, so comparability and reproducibility are maintained.

Collectively, these steps would strengthen external validity and comparative depth while keeping the thesis contribution centered on transparent, controllable, and observable engineering design.

