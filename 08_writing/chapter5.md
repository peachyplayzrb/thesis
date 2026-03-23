# Chapter 5

## 5.1 Evaluation Interpretation and Comparator Framing
Evaluation results in this thesis are interpreted as evidence for design-goal alignment (transparency, controllability, observability, and reproducibility), not as claims of universal recommendation superiority. This interpretation follows literature showing that practical value and scientific validity depend on explicit objective-metric alignment and clear reporting of protocol assumptions [@jannach_measuring_2019; @bauer_exploring_2024; @anelli_elliot_2021; @ferrari_dacrema_troubling_2021].

Accordingly, complex hybrid and self-supervised recommender families are treated as comparator context that motivates careful scope positioning rather than direct implementation requirements for this locked MVP artefact [@liu_multimodal_2025; @yu_self_supervised_2024].

## 5.2 Scope-Bounded Claim Discipline
The contribution claim is scoped to deterministic pipeline engineering under explicit transparency and observability constraints. Any discussion of performance trade-offs is framed as conditional on objectives, data conditions, and protocol choices, consistent with the chapter-level citation risk controls.

## 5.3 Findings in Relation to the Research Question
The research question asks what design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data. Based on the literature synthesis and current implementation evidence, the key design considerations are:

1. Goal-aligned method selection over model-family absolutism. Method choice should be driven by target qualities (inspectability, controllability, observability, reproducibility) rather than assumed universal superiority of any single recommender family [@roy_systematic_2022; @jannach_measuring_2019].
2. Staged cross-source preference extraction with explicit uncertainty handling. Under current API constraints, metadata normalization plus semantic enrichment (Last.fm tags) is a practical and inspectable design, but unmatched/ambiguous/no-tag cases must be surfaced as first-class outputs [@papadakis_blocking_2021; @allam_improved_2018].
3. Deterministic scoring and rule-based assembly for traceability. Explicit feature contributions and rule effects make explanation outputs and debugging behavior auditable in ways that opaque pipelines do not [@zhang_explainable_2020; @tintarev_survey_2007].
4. Evaluation protocol discipline as part of system design. Reproducibility and interpretation quality depend on logging, configuration traceability, and clear metric-objective alignment [@beel_towards_2016; @bauer_exploring_2024; @anelli_elliot_2021].
5. Comparator-awareness without scope drift. Hybrid and self-supervised systems are relevant context for trade-off discussion, but not required for validating this locked MVP contribution [@liu_multimodal_2025; @yu_self_supervised_2024].

Current implementation evidence now includes deterministic replay checks (BL-010) and controllability sensitivity tests (BL-011) on the bootstrap pipeline, plus BL-020 real-data diagnostics that exposed a candidate-corpus mismatch and required a semantic-enrichment fallback. This supports consideration 4 directly and gives practical evidence for considerations 1 to 3 under real cross-source constraints.

## 5.4 Limitations
This thesis has explicit limits that bound how the results should be interpreted.

1. Bootstrap-data limitation: BL-011 confirmed controllability at candidate and ranking layers, but threshold variants did not change final playlist membership under the synthetic pool used for those runs.
2. Reproducibility interpretation limitation: BL-010 showed semantic replay determinism, while some raw JSON hashes still varied because those artifacts include per-run metadata by design.
3. Corpus-feature limitation: recommendation behavior is constrained by DS-002 candidate composition and feature availability.
4. Scope limitation: the artefact is single-user and deterministic, so findings are not generalized to collaborative or adaptive multi-user systems.
5. Comparator limitation: no implemented deep or hybrid baseline is included in the MVP, so that comparison remains literature-grounded.
6. External-API limitation: Spotify audio-feature endpoints are deprecated, so user-side `tempo`, `loudness`, `key`, and `mode` are not directly available from Spotify in the current implementation.
7. External-validity limitation: evaluation remains BSc-feasible and does not include long-horizon user studies.
8. Alignment-quality limitation: direct fuzzy alignment into DS-002 can produce false positives when user listening history has weak corpus overlap; fallback semantic enrichment is required in this regime.

These limitations do not invalidate the contribution, but they bound it to design evidence for transparent deterministic recommender engineering under a constrained evaluation setting.

## 5.5 Future Work
Future work should extend this artefact in ways that preserve traceability while strengthening evidence.

1. Complete BL-020 real-data rerun end-to-end (BL-003 through BL-013) and compare outcomes against prior bootstrap evidence.
2. Add a focused music-domain alignment reliability benchmark study (for example ISRC/metadata ambiguity and error-rate analysis) to reduce current evidence risk.
3. Expand controllability experiments beyond OFAT by testing interaction effects between control surfaces while keeping auditability.
4. Add at least one comparator pipeline (for example a lightweight hybrid baseline) with protocol-matched evaluation to improve trade-off analysis without scope inflation.
5. Evaluate one audio-grounded extension path for user-side features (local extraction from a bounded user track subset) to recover direct user-side tempo/key/loudness evidence without relying on deprecated APIs.

Collectively, these steps would strengthen external validity and comparative depth while keeping the thesis contribution centered on transparent, controllable, and observable engineering design.

