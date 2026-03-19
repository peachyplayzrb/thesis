# Chapter 3: Design and Methodology

## 3.1 Design Methodology
This chapter takes a Design Science Research position in which the literature synthesis is converted into explicit engineering requirements and then into an implementable artefact architecture. The workflow remains the thesis sequence established in Chapter 1: literature -> requirements -> design -> implementation -> evaluation. The key methodological point is that Chapter 3 does not claim validated outcomes. It defines design commitments that are intended to be tested in Chapter 4.

This distinction is important because the chapter is not trying to prove a universally best recommendation method. It is establishing an architecture that is defensible under the project constraints and contribution goals. In that sense, the value of this chapter is design justification and traceability: why each mechanism is included, what it is expected to do, and how later evaluation can challenge or confirm those expectations.

## 3.2 Literature-Driven Design Requirements
The Chapter 2 synthesis is translated here into a small set of practical design requirements that can be implemented and tested. The first requirement is inspectability: recommendation outputs should be traceable to concrete scoring contributors and rule effects, not explained only through persuasive post-hoc language (Tintarev and Masthoff, 2007; Tintarev and Masthoff, 2012; Zhang and Chen, 2020).

The second requirement is practical controllability. The system should expose explicit user influence paths, but those controls should remain understandable and methodologically testable rather than open-ended or opaque (Andjelkovic et al., 2019; Jin et al., 2020). The third requirement is playlist-aware behavior. Item relevance alone is insufficient in music settings where ordering, repetition, and collection-level coherence shape user experience (Schedl et al., 2018; Gkatzioura and Halkidi, 2019; Neto et al., 2023).

The fourth requirement is governance at run level: observability, reproducibility, and auditability should be engineered directly into execution through configuration capture and structured diagnostics (Beel et al., 2016; Bellogin et al., 2021; Cavenaghi et al., 2023). The fifth is corpus defensibility. Music4All provides a documented multi-signal base suitable for content-driven experimentation under this scope, so it is used as the canonical candidate corpus (Pegoraro et al., 2020).

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
10. observability/audit,
11. configuration/execution control.

This layout is chosen to keep causal traceability from user input to playlist output. Each stage has a clearly defined role and emits intermediate artifacts that can be inspected independently. That separation is important for evaluation because it allows later analysis to distinguish profile effects, candidate-pool effects, scoring effects, and assembly effects rather than collapsing everything into a single black-box outcome.

The architecture also reflects deliberate scope discipline. It is single-user, deterministic, and content-driven, with one practical ingestion path and no deep-model complexity in the core pipeline. Those limits are not treated as missing sophistication; they are methodological choices that keep the artefact auditable and feasible within thesis constraints.

## 3.4 Data Ingestion and Alignment
The ingestion boundary is intentionally narrow: one practical listening-history source plus optional manual influence tracks. Imported tracks are aligned to the canonical feature corpus using ISRC-first matching, followed by metadata fallback matching when ISRC is unavailable or inconsistent.

This staged strategy follows entity-resolution practice that treats matching as a sequence of explicit steps with explicit trade-offs, rather than a single hidden operation (Allam et al., 2018; Papadakis et al., 2021). Neural matching remains a relevant comparator for difficult cases, but sits outside this artefact's inspectability and complexity boundary (Barlaug and Thorvaldsen, 2021). Unmatched tracks are therefore treated as an acknowledged limitation and reported directly.

At this stage, it is also important to make data assumptions explicit. Imported rows are expected to contain minimally usable artist-title metadata even when identifiers are missing, and the ingestion layer is expected to surface malformed or incomplete records rather than silently discarding them. In practice, cross-source music data can contain duplicated entries, inconsistent naming conventions, remaster/version suffixes, and partial metadata, all of which can affect fallback matching confidence. For design purposes, these are treated as manageable sources of uncertainty that must be made visible through diagnostics instead of being hidden behind aggregate success rates. This keeps method interpretation honest in Chapter 4 because alignment quality is reported as a property of both data conditions and matching logic.

In line with the cautious evidence language used in Chapter 2, this design treats alignment reliability as methodologically grounded but still uncertain because much entity-resolution evidence is cross-domain rather than music-specific.

## 3.5 Preference Modelling and Candidate Preparation
The preference model is built from aligned listening history and influence tracks using interpretable feature representations. Candidate generation then restricts the searchable set before scoring to preserve tractability and maintain deterministic behavior.

Feature processing standardizes values, handles missingness, and prepares weighted attributes for comparable similarity computation. This design uses content-driven framing from music recommender literature while keeping mechanism transparency explicit (Bogdanov et al., 2013; Deldjoo et al., 2024).

The intended flow is straightforward: aligned listening events provide baseline preference evidence, influence tracks provide explicit user-priority signals, and both are combined into a unified profile in the same feature space as candidate tracks. The contribution here is not a new profile algorithm. It is making these profile inputs and transformations visible enough that downstream ranking behavior can be interpreted without guesswork.

Candidate shaping is treated with the same discipline. Filters and thresholds are not only efficiency settings; they determine which tracks are even eligible for scoring. That distinction matters in later analysis, because a track can be absent from final output either because it was never considered or because it was scored and ranked lower. Keeping that boundary explicit improves explanation fidelity and reduces the risk of attributing retrieval effects to scoring logic.

This section also acknowledges that richer context-aware or multimodal models can achieve strong performance in adjacent tasks, but they are treated as comparator context rather than core implementation because of inspectability and complexity constraints in the MVP boundary defined for this project (Ru et al., 2023; Liu et al., 2025).

## 3.6 Deterministic Scoring and Playlist Assembly
Candidate scoring is performed using explicit deterministic similarity functions plus documented rule adjustments. Playlist assembly then enforces collection-level constraints, including playlist length, artist repetition limits, and diversity or ordering controls.

The rationale is goal-aligned rather than absolutist: deterministic scoring is selected to maximize inspectability and replayability under thesis scope, not to claim universal accuracy superiority over hybrid or neural alternatives (Cano and Morisio, 2017; He et al., 2017; Liu et al., 2025).

Metric and feature-weight selections are treated as explicit design parameters rather than hidden implementation defaults. In methodological terms, this makes scoring behavior testable rather than assumed.

For governance, this means parameters should be documented as first-class configuration choices rather than embedded constants. During evaluation, non-target parameters should remain fixed when one setting is varied so observed output differences remain interpretable. This is especially relevant when comparing metric or weight choices, because multiple simultaneous parameter changes would make causal interpretation weak. Keeping this discipline at design level ensures Chapter 4 can present parameter effects as interpretable and traceable rather than anecdotal.

## 3.7 Explanation, Observability, and Reproducibility
Explanation outputs are generated directly from scoring contributors and rule adjustments so that explanation statements remain mechanism-linked. In parallel, observability captures run-level artifacts (input summary, alignment statistics, configuration, ranking outputs, and playlist-rule outcomes).

This coupling supports both user-facing transparency and developer-facing inspectability, and enables deterministic replay tests required by the evaluation plan (Beel et al., 2016; Bellogin et al., 2021).

A minimum run record should therefore capture: input metadata summary, configuration snapshot and hash, alignment pathway counts (ISRC and fallback), unmatched counts with reason categories, score-trace summaries for ranked outputs, playlist-assembly rule outcomes, and final output identifiers. This does not require production-grade telemetry; it requires a consistent artifact bundle that can be reviewed and compared across runs. Defining this record format in Chapter 3 improves evaluation quality in Chapter 4 because replay checks, sensitivity checks, and explanation-fidelity checks all depend on the same observable execution footprint.

Modern music explainability work further reinforces this approach by emphasizing that explanation quality depends on exposing meaningful contribution structure rather than post-hoc narrative alone (Sotirou et al., 2025).

## 3.8 Configuration and Execution Control
A persistent configuration profile defines feature weights, constraints, filtering controls, and execution parameters. This enables controlled parameter-sensitivity experiments and exact reruns for reproducibility checks.

The intended execution protocol has two complementary modes. Baseline replay mode keeps inputs and configuration fixed to check deterministic consistency across repeated runs. Controlled-variation mode changes one selected parameter at a time while holding other settings constant, so observed differences can be interpreted in relation to that specific control. Together, these modes convert configuration from a convenience feature into a methodological instrument for evaluating reproducibility and controllability.

The chapter scope remains design-only. The purpose here is to define what should be implemented and why, not to claim that the implementation has already achieved those outcomes. Empirical behavior, failure cases, and test results are therefore deferred to Chapter 4.

## 3.9 Decision Traceability
The chapter centers on four linked architecture decisions. The first is corpus choice: Music4All is used as the canonical candidate space for feature-based retrieval and scoring. The second is scope discipline: the system remains within a single-user deterministic MVP boundary so behavior stays inspectable and feasible. The third is staged alignment: ISRC-first matching is combined with metadata fallback and explicit unmatched reporting. The fourth is mechanism-level transparency: deterministic scoring is paired with explanation linkage and run-level observability/reproducibility controls. Taken together, these decisions connect the Chapter 2 rationale to implementation commitments that can be tested directly in Chapter 4.

## 3.10 Chapter 2 to Chapter 3 Handoff Mapping
This section makes the literature-to-design handoff explicit by mapping each Chapter 2 section-level consequence to a concrete Chapter 3 commitment.

Table 3.1 documents this section-level handoff mapping from Chapter 2 consequences to Chapter 3 commitments.

| Chapter 2 source | Chapter 2 design consequence | Chapter 3 design commitment |
| --- | --- | --- |
| Section 2.1 (Foundations Scope and Thesis Positioning) | Architecture choices should be justified against transparency, controllability, observability, and reproducibility objectives instead of benchmark-only framing. | The architecture rationale in Sections 3.2 to 3.8 is written as objective-aligned engineering justification under MVP constraints defined for this project.
| Section 2.2 (Core Recommendation Paradigms and Their Trade-offs) | Deterministic design should be positioned as a goal-aligned trade-off choice rather than a universal best-model claim. | Sections 3.3 and 3.6 justify a deterministic layered pipeline while retaining comparator-context discipline.
| Section 2.3 (Transparency Explainability Controllability Observability and Evaluation) | Expose explicit user controls and keep explanation outputs mechanism-linked and evaluable. | Sections 3.2, 3.7, and 3.8 define controllability requirements, explanation linkage, and configuration-based controls for sensitivity testing.
| Section 2.4 (Preference Evidence Profile Construction and Candidate Shaping) | Use interpretable preference-profile construction and explicit candidate shaping before scoring. | Section 3.5 defines profile construction and candidate preparation as explicit, auditable pre-scoring stages.
| Section 2.5 (Music Recommendation and Playlist-Specific Challenges) | Keep playlist assembly as a distinct stage and treat similarity as decision support, not ground truth. | Section 3.6 separates playlist assembly from item scoring and encodes explicit playlist-level constraints.
| Section 2.6 (Deterministic Feature-Based Design Rationale with Comparator Context) | Make metric and feature-weight choices explicit and include sensitivity checks. | Sections 3.5 and 3.6 use explicit deterministic feature-based scoring and document parameterization for later sensitivity evaluation.
| Section 2.7 (Cross-Source Alignment Reliability Reproducibility Governance and Synthesis) | Add staged alignment diagnostics, unmatched-rate reporting, and run-level configuration logging under governance-oriented evaluation criteria. | Sections 3.4 and 3.7 define staged alignment, unmatched-track reporting, and run-level observability artifacts aligned with Chapter 4 governance checks.

This handoff mapping keeps the Chapter 2 conclusions operational and reduces drift between literature interpretation and architecture specification.

Overall, this chapter operationalizes the Chapter 2 argument into implementable commitments while keeping claims appropriately scoped: deterministic choices are justified as scope- and objective-aligned engineering decisions, not universal model-superiority claims.

## 3.11 Requirement-Mechanism-Evidence Mapping
To keep design and evaluation aligned, each requirement group is mapped to a concrete architecture mechanism and a specific Chapter 4 evidence target.

Table 3.2 provides this requirement-to-mechanism-to-evidence mapping.

| Requirement group | Architecture mechanism (Chapter 3) | Planned Chapter 4 evidence artifact |
| --- | --- | --- |
| Inspectability and explanation fidelity | Deterministic scoring with score decomposition plus mechanism-linked explanation payloads (Sections 3.6 and 3.7) | Score-trace reconstruction table showing explanation fidelity and mandatory explanation-field completeness |
| Practical controllability | Influence-track input path plus parameterized metric/weight/rule controls with configuration capture (Sections 3.5, 3.6, and 3.8) | One-factor-at-a-time sensitivity comparison tables with configuration-diff snapshots and ranked-output deltas |
| Playlist-level quality constraints | Distinct assembly stage with explicit length, repetition, and diversity/ordering rules (Section 3.6) | Rule-compliance summary tables with explicit pass/fail outcomes and violation logs where constraints are not met |
| Cross-source alignment reliability visibility | ISRC-first matching with metadata fallback and unmatched diagnostics (Section 3.4) | Alignment diagnostics summary showing ISRC matches, fallback matches, unmatched rate, and unmatched-reason categories |
| Observability and reproducibility | Run-level artifact schema linking input, configuration, alignment, scoring, assembly, and outputs (Sections 3.7 and 3.8) | Replay-consistency hash comparison table plus run-schema completeness checklist across repeated runs |

This mapping fixes the evaluation contract before implementation reporting and keeps Chapter 4 focused on evidence of designed properties rather than ad hoc result narratives.

## 3.12 Diagram Drafts For Core Decision Logic
Figure 3.3 and Figure 3.4 draft the most decision-critical parts of the architecture: cross-source alignment and the scoring-to-assembly transition.

Figure 3.3 shows the ISRC-first alignment decision flow with fallback and unmatched handling.

```text
Imported listening record
  -> Required fields valid?
     -> No: Mark invalid record and log reason
            -> Alignment diagnostics summary
     -> Yes: ISRC present?
            -> Yes: ISRC exists in canonical corpus?
                   -> Yes: Match by ISRC -> Aligned record output -> Alignment diagnostics summary
                   -> No: Proceed to metadata fallback
            -> No: Proceed to metadata fallback

Metadata fallback
  -> Artist and title usable?
     -> No: Mark unmatched and log reason -> Alignment diagnostics summary
     -> Yes: Fallback similarity above threshold?
            -> Yes: Match by metadata fallback -> Aligned record output -> Alignment diagnostics summary
            -> No: Mark unmatched and log reason -> Alignment diagnostics summary
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
     -> No: Violation log plus bounded fallback handling -> Explanation payload -> Run-level observability artifacts
```

Design consequence: the diagrammed decision points define the minimum implementation checkpoints that Chapter 4 should test for replayability, controllability, and rule-compliance visibility.

