  # Chapter 3: Design and Methodology

  ## 3.1 Introduction
  This chapter outlines how the playlist-generation pipeline is designed and structured. Building on Chapter 2, it translates requirements into concrete design decisions and moves from methodological position through overall architecture to each main design area in turn: alignment, preference profiling, candidate shaping, scoring, playlist assembly, and run-level observability.

  ## 3.2 Design Methodology
  This chapter takes a Design Science Research position in which the Chapter 2 literature synthesis is translated into explicit engineering requirements and then into an implementable artefact architecture (Peffers et al., 2007). The workflow follows the thesis sequence established in Chapter 1, moving from literature to requirements, design, implementation, and evaluation. Chapter 3 therefore defines the intended design of the artefact, while later chapters assess how well that design is realized.

  This distinction matters because the chapter is not trying to establish a universally best recommendation method. Instead, it defines an architecture that is defensible within the contribution boundary established at the end of Chapter 2: a transparent and controllable playlist-generation pipeline under cross-source data conditions, evaluated through explicit engineering evidence rather than model-family novelty.

  ## 3.3 Literature-Driven Design Requirements
  Chapter 2 points to six design requirements that should shape the artefact.

  | Requirement | Design rationale |
  | --- | --- |
  | Uncertainty-aware preference evidence | Interaction history should be treated as useful but imperfect evidence rather than direct preference truth (Adomavicius and Tuzhilin, 2005; Roy and Dutta, 2022). |
  | Inspectability | Rankings should be traceable to explicit scoring, candidate-selection, and assembly decisions rather than persuasive post-hoc language alone (Tintarev and Masthoff, 2007, 2012; Zhang and Chen, 2020). |
  | Practical controllability | The system should expose clear user influence paths and decision-relevant controls whose effects can later be examined (Andjelkovic et al., 2019; Jin et al., 2020). |
  | Candidate-generation visibility | Profile construction and candidate shaping should be treated as substantive modelling stages, not hidden preprocessing (Zamani et al., 2019; Ferraro et al., 2018). |
  | Playlist-aware trade-offs | The design should make coherence, diversity, novelty, and ordering explicit rather than treating playlist quality as a single objective (Bonnin and Jannach, 2015; Vall et al., 2019; Schweiger et al., 2025). |
  | Run-level auditability | Observability, reproducibility, and configuration traceability should be part of the design rather than added after the fact (Beel et al., 2016; Bellogin and Said, 2021; Cavenaghi et al., 2023). |

  Taken together, these requirements point toward a pipeline with explicit stages and evidence surfaces. While the requirements emerge from the Chapter 2 literature synthesis, the objectives below were established in Chapter 1; the design must therefore satisfy both.

  The six thesis objectives guide the main design decisions summarized below, linking the chapter structure to the stated research goals while keeping the design narrative readable.

  | Chapter 1 objective | Chapter 3 design response |
  | --- | --- |
  | O1. Design preference profiling from cross-source listening history | Sections 3.6 and 3.7 define uncertainty-aware alignment and interpretable profile construction from aligned evidence and influence inputs. |
  | O2. Implement cross-source alignment and candidate filtering with uncertainty handling | Sections 3.6 and 3.8 specify confidence-aware matching, unmatched/ambiguous handling, and explicit candidate-shaping controls. |
  | O3. Implement deterministic scoring and playlist assembly controls | Sections 3.9, 3.10, and 3.12 define deterministic scoring, assembly trade-offs, and controlled-variation protocol. |
  | O4. Produce explanation and logging outputs | Section 3.11 defines mechanism-linked explanations plus run-level observability artefacts. |
  | O5. Evaluate reproducibility and quality shifts under settings changes | Section 3.12 defines baseline replay and one-parameter-at-a-time controlled variation for interpretable effect testing. |
  | O6. Identify limits and applicability boundaries | Sections 3.4 and 3.13 maintain explicit single-user, deterministic, bounded-scope framing for later limitation analysis. |

  ### 3.3.1 Design Option Space and Selected-Design Rationale
  The Chapter 2 synthesis supports more than one technically plausible architecture, so the selected design is justified by objective alignment rather than by assuming a universal best model family. Three realistic options were considered.

  | Option | Main strengths | Main risk under this thesis scope | Selection outcome |
  | --- | --- | --- | --- |
  | Hybrid or neural-first recommender core | Strong representational power and broad benchmark relevance (Cano and Morisio, 2017; He et al., 2017). | Reduced mechanism inspectability and weaker causal traceability of score drivers under bounded single-user scope. | Not selected as primary architecture; retained as comparator context. |
  | Context-rich multimodal adaptive stack | Potential gains in richer preference representation and context sensitivity (Ru et al., 2023; Liu et al., 2025). | Higher modelling and data-dependency complexity, making reproducibility and control-effect interpretation harder to defend in this project boundary. | Not selected as primary architecture; positioned as future-work extension path. |
  | Deterministic feature-based staged pipeline | High transparency, controllability, and replay interpretability across explicit stages (Tintarev and Masthoff, 2007; Beel et al., 2016; Zamani et al., 2019). | Bounded representational flexibility compared with richer adaptive model families. | Selected as the primary architecture. |

  The selected option is therefore a deliberate fit to the research question and objectives rather than a claim that deterministic design dominates all alternatives. It is chosen because the thesis contribution is engineering evidence quality under cross-source uncertainty: explicit uncertainty handling at intake, inspectable candidate-space shaping, decomposable scoring, playlist-level rule visibility, and run-level reproducibility diagnostics. Those requirements are methodologically easier to satisfy and evaluate when the architecture remains deterministic and stage-explicit.

  ## 3.4 Design Scope and Overall Architecture
  The proposed architecture is a deterministic pipeline with seven main stages:

  1. user interaction,
  2. cross-source data intake and alignment,
  3. preference profiling,
  4. candidate shaping,
  5. deterministic scoring,
  6. playlist assembly,
  7. explanation, observability, and control.

  Figure 3.1 shows how these stages connect and where the main evidence artefacts are produced.

  ![Figure 3.1. Deterministic pipeline architecture with stage outputs and run-level observability linkage.](figures/figure_3_1_architecture.png)

  This layout is chosen to preserve causal traceability from user input to playlist output. Each stage has a clearly defined role and produces intermediate artefacts that can be inspected independently. That separation matters because it allows later evaluation to distinguish profile effects, candidate-space effects, scoring effects, and assembly effects rather than collapsing everything into a single black-box outcome.

  Each stage is therefore intended to emit inspectable intermediate outputs rather than only a final playlist. This makes it possible to examine how evidence enters the pipeline, how it is transformed, and where uncertainty, exclusion, or trade-off pressure is introduced as the run progresses.

  The architecture also reflects deliberate scope discipline. It is single-user, deterministic, and content-driven, with bounded complexity and explicit contribution limits. These are not treated as missing sophistication. They are methodological choices that keep the artefact auditable and aligned to the research gap identified in Chapter 2.

  ### 3.4.1 Assumptions and Boundaries
  The design rests on a small set of explicit assumptions that bound what later evaluation can claim.

  - The user-data basis is a fixed local listening-history export rather than an open-ended live stream of behaviour.
  - Candidate tracks are drawn from a fixed offline corpus with available metadata and feature descriptors.
  - Preference evidence is useful but incomplete, so alignment uncertainty and missingness must remain visible rather than being treated as negligible.
  - The artefact is engineered for single-user inspectability under deterministic execution, not for large-scale personalization or online adaptation.
  - Control effects are interpreted within this bounded pipeline, so later results should be read as engineering evidence under fixed conditions rather than as universal recommendation performance claims.

  Alternative design directions were considered but not adopted as the primary architecture. Latent collaborative and neural approaches were not selected because they weaken direct inspectability of ranking drivers under the thesis scope, even though they may perform strongly in richer multi-user settings (Cano and Morisio, 2017; He et al., 2017; Liu et al., 2025). Probabilistic or heavily stochastic ranking approaches were also not selected because they would make control effects and replay behaviour harder to interpret. The design therefore commits to a deterministic, feature-based pipeline because that choice best fits the transparency, controllability, and reproducibility objectives established in Chapters 1 and 2.

  ## 3.5 Technology Choices and Realisation Context
  The design assumes a lightweight, locally executable environment chosen to support traceability and reproducibility rather than platform scale. A scripted pipeline language is preferred over a distributed or service-heavy architecture because the contribution lies in auditable recommendation behaviour, not deployment infrastructure. This choice supports traceability and a human-centered trust model in which deterministic, locally editable logic is often easier to inspect and justify than opaque remote or hybrid execution paths (Afroogh et al., 2024).

  At the data intake boundary, the design requires that user-side listening evidence be available as a pre-acquired local artefact rather than retrieved through live network calls at recommendation time. This keeps the core recommendation run independent of external availability, authentication state, and endpoint drift — all of which would introduce variability that is orthogonal to the contribution.

  For cross-source identifier matching, the design calls for bounded fuzzy fallback comparison when strong identifiers are absent. This is preferable to exact-only matching under cross-source conditions, but the fallback must remain transparent and bounded rather than delegating the matching decision to an opaque learned model. Stage inputs, outputs, and diagnostics should be stored in directly inspectable artefact formats rather than in a database layer, so that intermediate decisions remain portable and reviewable across runs.

  ## 3.6 Cross-Source Preference Evidence and Alignment
  The intake boundary is intentionally narrow: one primary listening-history source plus optional user-steerable influence inputs. Imported tracks are transformed into an inspectable preference signal through staged alignment and explicit uncertainty handling.

  Following the Chapter 2 conclusion that cross-source evidence is structurally uncertain, alignment is treated as an explicit design stage rather than a hidden preprocessing step. It distinguishes confident matches, ambiguous cases, and unmatched records rather than treating all imported records as equally reliable profile evidence (Elmagarmid et al., 2007; Papadakis et al., 2021).

  In practical terms, the alignment stage follows a fixed evidence order. It first checks whether the imported row contains the minimum fields needed for reliable downstream handling. If it does, it attempts the strongest available identifier-based match. Structured identifiers such as track or recording IDs are prioritized because they are less susceptible to naming variation, version suffixes, and transliteration differences than string-based metadata, making them more reliable anchors for cross-source record linkage (Elmagarmid et al., 2007). Only when that path is unavailable or insufficient does it fall back to bounded metadata comparison over title, artist, and related descriptive fields. If one candidate is clearly strongest, the row is treated as a confident match. If several plausible candidates remain close under the fallback logic, the row is retained as ambiguous rather than being forced into certainty. If no acceptable candidate is found, the row is retained as unmatched with an explicit reason category. Imported rows that fail minimum validity checks are surfaced separately as invalid rather than silently discarded.

  Cross-source music data can contain duplicated entries, naming variation, version suffixes, missing fields, and identifier mismatch. These are treated as manageable but irreducible sources of uncertainty that must be made visible through diagnostics rather than hidden behind aggregate success rates.

  Alignment outcomes are therefore represented in three broad categories. Confident matches contribute directly to downstream profile construction. Ambiguous matches remain visible with explicit uncertainty markers so they can be reviewed rather than silently absorbed as certain evidence. Unmatched or invalid records are retained in diagnostics with reason categories so that data-coverage limitations remain observable at the point where evidence enters the system.

  In line with Chapter 2, alignment reliability is treated as methodologically grounded but still uncertain because much entity-resolution evidence is cross-domain rather than music-specific. The design consequence is that uncertainty should remain visible at the point where evidence enters the system, not only after final outputs are produced.

  Figure 3.2 shows the intended evidence-handling logic.

  ![Figure 3.2. Alignment evidence-handling flow with matched, ambiguous, unmatched, and invalid pathways.](figures/figure_3_2_alignment_logic.png)

  ## 3.7 Preference Profiling
  The preference model is built from aligned listening evidence and explicit influence signals using interpretable feature representations. This stage defines what counts as meaningful preference evidence before any candidate is admitted for ranking.

  The interpretable feature space in this design is explicitly defined in three groups. Rhythmic and harmonic features include tempo, key, and mode. Affective and intensity-related features include danceability, energy, and valence. Semantic and contextual features include lead genre, genre overlap, and tag overlap (Bogdanov et al., 2013; Deldjoo et al., 2024). These features are selected because they jointly support playlist-level trade-offs: tempo, key, and mode support rhythmic-harmonic compatibility; danceability, energy, and valence provide controllable intensity and affect proxies; and genre- and tag-based features provide interpretable semantic coherence and diversity control.

  Feature preparation standardizes values, handles missingness, and prepares weighted attributes for comparable similarity computation. Profile construction is therefore not neutral preprocessing — it is a normative modelling decision that determines which traces count as preference evidence and how strongly they shape downstream behaviour (Bogdanov et al., 2013; Deldjoo et al., 2024; Roy and Dutta, 2022). However, the correspondence between feature-space similarity and listener-perceived preference remains incomplete; feature selection alone cannot fully capture affective or situational preference dimensions that depend on context and framing (Flexer and Grill, 2016). Interpretable features are therefore auditable but not assumed to be sufficient proxies for all preference aspects.

  The flow is straightforward: aligned listening events provide baseline evidence, optional influence-track inputs provide explicit correction or emphasis, and both are combined into weighted feature summaries in the same interpretable feature space as candidate tracks.

  The resulting profile is designed to make later ranking decisions traceable to explicit feature relationships rather than hidden latent representations. In practical terms, it becomes a bounded weighted summary of aligned evidence in the same candidate-facing feature space used for shaping and scoring. The contribution here is not a novel preference model but a profile representation whose assumptions remain visible enough for downstream ranking behaviour to be interpreted without guesswork.

  ## 3.8 Candidate Shaping
  Candidate shaping restricts the searchable set before scoring so that the later ranking stage operates over an explicit, inspectable candidate space rather than the full corpus. Similarity thresholds, exclusions, and corpus-side filters are therefore treated as modelling decisions rather than mere efficiency settings.

  Candidate absence in the final playlist can arise for two fundamentally different reasons: a track may never have entered the candidate set, or it may have entered and then been outranked or excluded later. Preserving that distinction matters because explanation systems that collapse these two pathways risk attributing candidate-space filtering to scoring logic, which degrades the accuracy of any mechanism-linked explanation (Tintarev and Masthoff, 2007, 2012). Candidate shaping also gives the design a clear place to represent threshold strictness, influence-track expansion, and corpus-side exclusions as explicit controls whose effects can later be observed in candidate counts, exclusion diagnostics, and downstream score opportunities.

  The shaping step is designed to combine profile-similarity thresholds with metadata-based exclusions and bounded influence-track expansion so that the candidate set remains both relevant to the current preference signal and auditable before ranking begins.

  Exposing candidate shaping as its own evidence surface is therefore a central design goal. It should show how many items were retained, why other items were filtered out, and how strongly the current profile settings determined the reachable search space. This makes candidate-generation visibility concrete rather than rhetorical and keeps the Chapter 2 observation that candidate-generation stages are often the most consequential but least visible part of a recommendation pipeline directly reflected in the architecture (Zamani et al., 2019; Ferraro et al., 2018).

  ## 3.9 Deterministic Scoring
  Candidate scoring uses explicit deterministic similarity functions with documented component-level weighting. This stage is responsible for ranking the already-shaped candidate set, not for silently redefining that set.

  The rationale is goal-aligned rather than absolutist: deterministic scoring is selected to maximize inspectability, replayability, and clear control effects under thesis scope, not to claim universal superiority over collaborative, hybrid, or neural alternatives (Cano and Morisio, 2017; He et al., 2017; Liu et al., 2025).

  At design level, scoring combines weighted feature-similarity contributions so that final rankings can be decomposed into named components.

  Metric and feature-weight selections are treated as explicit design parameters rather than hidden implementation defaults. Metric family, normalization, and thresholding are first-order determinants of ranking geometry (Herlocker et al., 2004); this follows Chapter 2's specific warning that these choices materially reshape recommendation behaviour (Fkih, 2022). In methodological terms, this makes scoring behaviour testable rather than assumed.

  The intended scoring output is therefore not just a ranked list but an inspectable score decomposition showing how feature relationships contributed to candidate ordering. That makes the stage interpretable at track level and gives later explanation and evaluation logic a concrete mechanism surface to reference.

  ## 3.10 Playlist Assembly
  Playlist assembly remains a distinct stage rather than a thin post-processing layer. Coherence, diversity, novelty, and ordering are competing objectives at playlist level, and how they are weighted against one another materially affects perceived quality and user experience (Bonnin and Jannach, 2015; Vall et al., 2019; Schweiger et al., 2025). Collection-level quality is therefore represented as an explicit trade-off rather than a single optimization target.

  The assembly stage takes a ranked candidate list as input and applies playlist-level rules that can preserve, relax, or redirect simple score order when collection quality would otherwise degrade. These rules govern configurable assembly constraints covering repetition, diversity pressure, novelty allowance, score admissibility, and ordering behaviour, and they include a relaxation pathway for when constraints would otherwise prevent the target playlist size from being met. Treating assembly separately matters because it creates a clear boundary between track-level merit and list-level construction.

  Figure 3.3 shows the intended relationship between scoring and assembly.

  ![Figure 3.3. Scoring-to-assembly relationship with constraint checks, fallback recording, and observability output.](figures/figure_3_3_scoring_assembly.png)

  ## 3.11 Explanation and Run-Level Observability
  Explanation outputs are generated directly from scoring contributors, candidate-shaping logic, and assembly-rule effects so that explanation statements remain mechanism-linked. In parallel, observability captures run-level artefacts spanning input intake, alignment diagnostics, profile construction, candidate shaping, scoring, assembly, and configuration state. Together, these surfaces make the full execution footprint inspectable rather than only the final output.

  Both user-facing transparency and developer-facing inspectability depend on this coupling. While mechanism-linked explanation increases auditability and fidelity relative to post-hoc narratives, it does not guarantee improved user-perceived utility or trust, which remain dependent on user context and characteristics (Knijnenburg et al., 2012). Explanation mechanisms are therefore treated as engineering evidence rather than automatic quality guarantees. The same coupling also creates the evidence bundle required for deterministic replay and control-effect evaluation, because reproducibility claims are only defensible when the same run surfaces can be inspected and compared across repeated executions (Beel et al., 2016; Bellogin and Said, 2021; Sotirou et al., 2025).

  At minimum, the run record captures the input basis, configuration state, alignment and uncertainty summaries, profile outputs, candidate-space decisions, score-trace summaries, playlist-rule outcomes, explanation artefacts, and final output identifiers. This does not require production-grade telemetry. It requires a consistent evidence bundle that can be reviewed and compared across runs. Defining this record format in Chapter 3 matters because replay, sensitivity, and explanation-fidelity checks all depend on the same observable execution footprint.

  ## 3.12 Configuration and Experimental Control
  A persistent configuration profile defines feature weights, constraints, filtering controls, trade-off parameters, and execution settings. This converts configuration from a convenience mechanism into a methodological instrument for evaluating reproducibility and controllability.

  Two complementary execution modes are defined. Baseline replay mode keeps inputs and configuration fixed and uses repeated fixed-configuration replays as a bounded consistency check across the main evidence surfaces, not only the final playlist. The purpose is to confirm that stable behaviour is not an artefact of a single execution, while keeping the check scoped to what the deterministic design can defensibly claim rather than invoking broader reproducibility standards. The comparison spans alignment summaries, candidate-pool counts, score-trace outputs, playlist artefacts, and final output identifiers, because reproducibility claims weaken when protocol and configuration are specified only at the result level rather than across the full execution record (Bellogin and Said, 2021; Cavenaghi et al., 2023).

  Controlled-variation mode changes one selected parameter or one bounded policy switch at a time. All other settings remain fixed so observed differences can be interpreted against that single actuation. A meaningful variation is therefore not an arbitrary new profile but a predeclared change whose expected effect can be examined at candidate-space, ranking, assembly, or explanation level. Evidence that the control surface is behaving as intended includes stable fixed-baseline replays, observable shifts in intermediate diagnostics under one-factor changes, and traceable downstream differences in playlist composition or constraint-pressure records when later-stage effects occur. In this way, the protocol remains aligned to Chapter 1 objective O5 by treating reproducibility and controllability as evidence-bearing properties of the design rather than as informal run impressions.

  ## 3.13 Chapter Summary
  This chapter has translated the Chapter 2 literature review into a design for a transparent and controllable playlist-generation pipeline. The central design choices are to make uncertainty visible at the point where evidence enters the system, separate profile construction from candidate shaping and track-level scoring from playlist assembly, keep explanations mechanism-linked, and support later evaluation through configuration control and run-level observability. The following chapter examines how closely the implemented artefact matches this blueprint and where these design properties become visible in execution.
