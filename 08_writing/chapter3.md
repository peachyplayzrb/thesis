# Chapter 3: Design and Methodology

## 3.1 Design Methodology
This chapter follows a Design Science Research stance in which literature insights are translated into engineering requirements, then into an implementable architecture, and later validated through implementation and evaluation. The flow is consistent with the locked thesis method definition: literature -> requirements -> design -> implementation -> evaluation. At this stage, architecture decisions are treated as design hypotheses constrained by MVP feasibility rather than as proven outcomes.

## 3.2 Literature-Driven Design Requirements
The design requirements come directly from the literature synthesis and the locked thesis scope.

First, recommendation logic must be inspectable and explanation outputs must remain faithful to actual mechanisms, not only persuasive post-hoc narratives [@zhang_explainable_2020; @tintarev_survey_2007; @tintarev_evaluating_2012].

Second, users need practical influence over recommendation behavior. Prior work supports controllability mechanisms but also indicates user-dependent effects, so controls should be explicit without becoming unnecessarily complex for MVP delivery [@jin_effects_2020; @andjelkovic_moodplay_2019].

Third, playlist generation requires constraints beyond item-level relevance because sequence and collection-level quality matter [@schedl_current_2018; @gatzioura_hybrid_2019; @neto_algorithmic_2023].

Fourth, observability, reproducibility, and auditability must be engineered as system properties through explicit configuration capture and run-level logging [@beel_towards_2016; @bellogin_improving_2021; @cavenaghi_systematic_2023].

Finally, canonical corpus choice should remain evidence-backed: Music4All is a documented multi-signal dataset suitable for content-driven music experimentation, which supports its use as the thesis candidate-track corpus [@pegoraro_santana_music4all_2020].

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
10. observability/audit,
11. configuration/execution control.

This structure preserves traceability from user input to final playlist while remaining within the locked MVP boundary (single-user, single practical ingestion path, deterministic core, no deep-model complexity).

## 3.4 Data Ingestion and Alignment
The ingestion boundary is intentionally narrow: one practical listening-history source plus optional manual influence tracks. Imported tracks are aligned to the canonical feature corpus using ISRC-first matching, followed by metadata fallback matching when ISRC is unavailable or inconsistent.

This staged strategy is supported by entity-resolution literature that emphasizes blocking/filtering/matching pipelines and explicit quality-efficiency trade-offs [@allam_improved_2018; @papadakis_blocking_2021]. More advanced neural matching remains an acknowledged alternative for difficult cases, but is outside core MVP complexity and inspectability priorities [@barlaug_neural_2021]. Unmatched tracks are excluded and reported as explicit limitations.

In line with Chapter 2 evidence-bounding language, this design treats alignment reliability as methodologically grounded but uncertainty-bounded because much entity-resolution evidence is cross-domain rather than music-specific.

## 3.5 Preference Modelling and Candidate Preparation
The preference model is built from aligned listening history and influence tracks using interpretable feature representations. Candidate generation then restricts the searchable set before scoring to preserve tractability and maintain deterministic behavior.

Feature processing standardizes values, handles missingness, and prepares weighted attributes for comparable similarity computation. This design uses content-driven framing from music recommender literature while keeping mechanism transparency explicit [@deldjoo_content-driven_2024; @bogdanov_semantic_2013].

This section also acknowledges that richer context-aware or multimodal models can achieve strong performance in adjacent tasks, but they are treated as comparator context rather than core implementation because of inspectability and complexity constraints in the locked MVP [@liu_aggregating_2025; @ru_improving_2023].

## 3.6 Deterministic Scoring and Playlist Assembly
Candidate scoring is performed using explicit deterministic similarity functions plus documented rule adjustments. Playlist assembly then enforces collection-level constraints, including playlist length, artist repetition limits, and diversity or ordering controls.

The rationale is goal-aligned rather than absolutist: deterministic scoring is selected to maximize inspectability and replayability under thesis scope, not to claim universal accuracy superiority over hybrid or neural alternatives [@cano_hybrid_2017; @he_neural_2017; @liu_multimodal_2025].

Metric and feature-weight selections are treated as explicit design parameters rather than hidden implementation defaults, enabling later sensitivity checks in Chapter 4.

## 3.7 Explanation, Observability, and Reproducibility
Explanation outputs are generated directly from scoring contributors and rule adjustments so that explanation statements remain mechanism-linked. In parallel, observability captures run-level artifacts (input summary, alignment statistics, configuration, ranking outputs, and playlist-rule outcomes).

This coupling supports both user-facing transparency and developer-facing inspectability, and enables deterministic replay tests required by the evaluation plan [@beel_towards_2016; @bellogin_improving_2021].

Modern music explainability work further reinforces this approach by emphasizing that explanation quality depends on exposing meaningful contribution structure rather than post-hoc narrative alone [@sotirou_musiclime_2025].

## 3.8 Configuration and Execution Control
A persistent configuration profile defines feature weights, constraints, filtering controls, and execution parameters. This enables controlled parameter-sensitivity experiments and exact reruns for reproducibility checks.

The chapter scope is design-only. It defines the intended architecture and rationale, while implementation behavior and empirical results are reported in later chapters.

## 3.9 Decision Traceability
Key architecture choices in this chapter are anchored to accepted design-log entries:

- `D-001`: canonical candidate corpus decision (Music4All / Music4All-Onion) supporting feature-based candidate generation.
- `D-002`: locked MVP scope and evaluation-focus decision constraining architecture breadth and methodology feasibility.
- `D-003`: ISRC-first alignment with metadata fallback and unmatched-track reporting.
- `D-004`: deterministic scoring, mechanism-linked explanations, and run-level observability/reproducibility controls.

This mapping ensures Chapter 3 claims are traceable to explicit decisions with documented context, alternatives, rationale, and evidence basis in `00_admin/decision_log.md`.

## 3.10 Chapter 2 to Chapter 3 Handoff Mapping
To preserve literature-to-design continuity, each Chapter 2 section-level design consequence is translated into a concrete Chapter 3 design commitment.

Table 3.1 documents this section-level handoff mapping from Chapter 2 consequences to Chapter 3 commitments.

| Chapter 2 source | Chapter 2 design consequence | Chapter 3 design commitment |
| --- | --- | --- |
| Section 2.1 (Foundations and scope positioning) | Architecture choices should be justified against transparency, controllability, observability, and reproducibility objectives instead of benchmark-only framing. | The architecture rationale in Sections 3.2 to 3.8 is written as objective-aligned engineering justification under locked MVP constraints.
| Section 2.2 (Transparency, explainability, controllability) | Expose explicit user controls and evaluate sensitivity rather than assuming a universal control strategy. | Section 3.2 defines controllability requirements and Section 3.8 defines configuration-based parameter control to support sensitivity testing.
| Section 2.3 (Music and playlist challenges) | Keep playlist assembly as a distinct stage and treat similarity as decision support, not ground truth. | Section 3.6 separates playlist assembly from item scoring and encodes explicit playlist-level constraints.
| Section 2.4 (Deterministic design rationale) | Make metric and feature-weight choices explicit and include sensitivity checks. | Sections 3.5 and 3.6 use explicit deterministic feature-based scoring and document parameterization for later sensitivity evaluation.
| Section 2.5 (Alignment reliability and reproducibility) | Add staged alignment diagnostics, unmatched-rate reporting, and run-level config logging. | Sections 3.4 and 3.7 define staged alignment, unmatched-track reporting, and run-level observability artifacts.
| Section 2.6 (Gap and chapter conclusion) | Evaluate artefact quality against transparency, controllability, observability, reproducibility, and rule compliance rather than SOTA competition. | Sections 3.1 and 3.7 frame Chapter 4 evaluation around governance and inspectability criteria aligned with the locked evaluation direction.

This handoff mapping keeps the Chapter 2 conclusions operational and prevents drift between literature interpretation and architecture specification.

Overall, this chapter operationalizes the Chapter 2 argument into implementable commitments while preserving claim discipline: deterministic choices are justified as scope- and objective-aligned engineering decisions, not universal model-superiority claims.

