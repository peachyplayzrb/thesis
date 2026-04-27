# Chapter 4: Implementation Architecture and Evidence Surfaces

## 4.1 Chapter Aim and Scope

This chapter reports how the design committed in Chapter 3 was realised as an executable pipeline and identifies the evidence outputs produced by each stage. It does not evaluate whether outputs meet quality criteria. Instead, it specifies what was implemented, how design properties (transparency, controllability, reproducibility) become visible in concrete evidence surfaces, and how information flows from alignment through playlist assembly.

The chapter follows the pipeline architecture in sequence: alignment, profiling, candidate shaping, scoring, assembly, explanation, and observability. For each stage, it describes the design intent, the implementation realisation, and the evidence artefacts produced. Together, these stages show that the implemented system is not only functionally staged; it is instrumented so that transparency and controllability objectives remain visible in the execution record itself.

## 4.2 Design-to-Implementation Bridge

Chapter 3 committed to a deterministic 7-stage pipeline where each stage produces intermediate outputs. This section maps that commitment to the implemented stages and explains the technology positioning that supports auditable behaviour.

The implementation adopts a deliberately lightweight, locally executable architecture chosen to support traceability and reproducibility over platform scale. This aligns with Chapter 3's position that "the contribution lies in auditable recommendation behaviour, not deployment infrastructure" (Section 3.5). All intermediate results and diagnostics are stored as directly inspectable JSON or CSV artefacts in the local filesystem rather than in opaque database layers or remote services. This choice supports a human-centred trust model in which deterministic, locally reviewable logic is often easier to justify than remote or hybrid execution paths.

By keeping the pipeline locally executable and artefact-based, intermediate decisions remain portable and reviewable across runs. A researcher or evaluator can inspect alignment diagnostics at the point where evidence enters, follow preference profile construction, observe candidate-space decisions before ranking begins, and trace final outputs back to active mechanisms.

**Implementation scope:** The implementation is organised into nine implementation layers, identified as BL-003 through BL-011: seven core pipeline stages (alignment, profiling, candidate shaping, scoring, assembly, explanation, and observability) plus two evaluation-support layers (reproducibility and controllability instrumentation). See Figure 3.1 for the overall pipeline architecture; the implementation follows this design blueprint with each stage producing explicit evidence artefacts.

**Section weighting note:** Alignment receives the most detailed treatment in Section 4.3 because it is the first point where evidence uncertainty enters the pipeline; understanding how uncertainty is classified and preserved at intake is foundational to all downstream stages.

## 4.3 BL-003: Cross-Source Alignment and Evidence Intake

**Why does alignment matter? Because uncertainty enters here.**

Chapter 3 treated alignment as an explicit design stage rather than hidden preprocessing (Section 3.6). The alignment stage receives imported listening-history records and systematically matches them against a fixed offline track corpus. Rather than forcing all records into certainty, it follows a fixed evidence order: (1) check minimum field validity, (2) attempt structured identifier matching (track ID, recording ID), (3) fall back to bounded metadata comparison (title, artist), and (4) classify outcomes as confident match, ambiguous match, unmatched, or invalid.

A confident match occurs when a strong identifier-based match is found or when metadata comparison yields one clearly strongest candidate. An ambiguous match occurs when multiple candidates score close enough to remain plausible — these are retained with uncertainty flags rather than silently forced into certainty. Unmatched records are retained with explicit reason categories (no title provided, fuzzy comparison failed, etc.) rather than discarded. Invalid records are surfaced separately.

This stage also preserves absence causality in the final playlist: a track either never entered the candidate set (alignment failure) or entered and was later excluded during filtering or ranking. This prevents explanation output from attributing candidate-space decisions to scoring logic.

**Evidence artefact:** `bl003_ds001_spotify_summary.json` records match-rate statistics (counts matched by Spotify ID, by metadata fallback, ambiguous matches, unmatched records), match-rate validation against a minimum threshold, unmatched/invalid reason visibility, and cross-source identifier utilisation. This artefact exposes alignment uncertainty at intake. A real match rate of 24.7% against 9,902 input events — exceeding the 15% minimum threshold — is recorded alongside unmatched and ambiguous-category counters, so downstream stages understand the evidence profile passed forward.

## 4.4 BL-004: Preference Profiling from Aligned Evidence

**Why expose the profile? Because influence and attribution must be reviewable.**

The profiling stage takes confident and ambiguous alignment outcomes and builds a weighted feature summary in a defined interpretable space (Section 3.7). Features are organized in three groups: Rhythmic/Harmonic (tempo, key, mode), Affective/Intensity (danceability, energy, valence), and Semantic/Contextual (lead genre, genre overlap, tag overlap).

For each feature, the implementation computes weighted statistics (mean, standard deviation, attribution tracking) from aligned listening events. Optional influence-track inputs (explicit user-provided preference corrections) are incorporated into the same feature space so that influence and historical evidence remain commensurable. Feature preparation standardises values, handles missingness explicitly, and prepares weighted attributes for downstream similarity computation.

**Evidence artefact:** `bl004_preference_profile.json` contains per-feature statistics for all three feature groups, influence-track contributions clearly marked, uncertainty markers for features with high missingness, and attribution breakdowns. This profile makes preference structure transparent. An evaluator can directly inspect what feature weights define the profile, identify which genres dominate, and see how much influence-driven edits shifted the baseline evidence profile.

## 4.5 BL-005: Candidate Shaping and Search-Space Definition

**Why explicit exclusion? Because candidate-space decisions must be traceable.**

The candidate-shaping stage restricts the searchable set before scoring so that ranking operates over an explicit, inspectable candidate space (Section 3.8). The stage combines profile-similarity thresholds with metadata-based exclusions and bounded influence-track expansion to define the searchable candidate set.

The implementation enforces three mechanisms in sequence:
1. Profile-similarity thresholds: candidates retained only if their feature distance to the profile falls within defined tolerance
2. Metadata-based exclusions: candidates explicitly marked as ineligible (e.g., bonus tracks, live versions, user-excluded artists)
3. Influence-track expansion: influence inputs can nominate additional candidates to be retained even if they fall below the similarity threshold

The stage records all three pathways separately so that downstream diagnostics can distinguish whether a candidate was excluded due to similarity, metadata policy, or was explicitly marked ineligible.

**Evidence artefact:** `bl005_candidate_diagnostics.json` contains retained candidate count, exclusion breakdown by reason, threshold stringency metrics, influence-track contribution, and feature-range statistics for the retained set. This artefact records the search-space boundary directly. With typical retention rates around 20% of the corpus, the ranking stage operates over a highly filtered space. The artefact separates two cases: alternatives that were ranked lower versus tracks that never entered the candidate set.

## 4.6 BL-006: Deterministic Scoring with Decomposable Components

**Component decomposition ensures rankings stay traceable to named logic.**

The scoring stage applies deterministic similarity functions to each candidate in the shaped set (Section 3.9). Scores are built as weighted sums of named feature-similarity components so that final rankings can be decomposed into named mechanisms.

The implementation computes three feature-similarity scores (rhythmic/harmonic, affective/intensity, semantic/contextual) normalized to a 0–1 scale, then combines group scores using configurable weights so that users can emphasise (e.g.) semantic similarity over affective properties. Crucially, the stage outputs both raw final scores and per-component contributions, so that explanation logic can reference which mechanisms drove specific ranking decisions.

**Evidence artefact:** `bl006_score_summary.json` records score distribution statistics (mean, median, min, max) for the full scored set, active component weight snapshot, and top-ranked candidates. `bl006_scored_candidates.csv` records individual score breakdowns and component contributions. Together, these make score-distribution behaviour directly auditable in the run artefacts.

## 4.7 BL-007: Playlist Assembly with Explicit Trade-offs

**Assembly rules make trade-off pressure visible at the playlist level.**

Playlist assembly remains a distinct stage rather than a thin post-processing layer (Section 3.10). The assembly stage takes the ranked candidate list and applies playlist-level rules that can preserve, relax, or redirect simple score order when collection quality would otherwise degrade.

The implementation enforces configurable constraints covering repetition control (limits on consecutive artist/genre appearance), diversity pressure (targets for feature distribution), novelty allowance (budget to include lower-ranked tracks if they offer novel features), and score admissibility (constraints on minimum acceptable scores). When constraints cannot be satisfied within the target playlist size, the stage activates a relaxation pathway that explicitly records which constraints were relaxed and by how much.

**Evidence artefact:** `bl007_assembly_report.json` contains constraint satisfaction record, rule-activation counts, playlist trace with decision record (for each position, what candidate was selected and why), and trade-off metrics summary. This artefact records assembly decisions as explicit data rather than hidden post-processing. The run now captures not only the final playlist but also explicit relaxation records showing where constraints were loosened and by how much.

## 4.8 BL-008: Mechanism-Linked Explanations

**Explanation payloads map each selection back to scoring contributors.**

The explanation stage generates structured rationale payloads for each track in the final playlist (Section 3.11). For each track, the payload records score breakdown (which feature-group similarities drove the ranking decision), component attribution (how much each of the three feature groups contributed), rule effects (how assembly constraints modified the simple score-based ordering if at all), and confidence marker (how confident was the alignment stage in the source evidence for this track).

These elements are compiled into a structured rationale that can be presented to a user in natural language form but remains grounded in active mechanisms. The payload includes the track's `score_percentile` within the shaped candidate set (its rank expressed as a percentile across the full scored population before assembly) and a `score_band` classification (strong, moderate, or weak) derived from percentile thresholds.

**Evidence artefact:** `bl008_explanation_payloads.json` contains per-candidate record for all scored tracks. `bl008_explanation_summary.json` records the distribution of primary explanation drivers across the playlist. The per-candidate payloads record score breakdowns and component contributions for every scored candidate, providing the basis for post-hoc inspection of why any candidate was included or excluded. This makes the distinction between score-driven selection effects and assembly-rule effects directly visible.

## 4.9 BL-009: Run-Level Observability and Full Execution Footprint

All prior stages feed their outputs and the active configuration into a consolidation step that produces a single run-level artefact. This synthesises evidence from alignment through to final explanation, creating a run record suitable for reproducibility verification and controlled-variation comparison.

The run record captures input summary (what listening history was imported, alignment quality), configuration snapshot (all active parameters), stage sequence (which stages executed in what order), intermediate diagnostics (key metrics from each stage), output identifiers (final playlist hash, final artefact hashes), reproducibility markers (run ID, timestamp), and validity boundaries (explicit non-claims about what the results apply to).

**Evidence artefact:** `bl009_run_observability_log.json` serves as the central repository for run-level evidence. It records run metadata, input summary, configuration snapshot, stage-execution record, and output hashes (including named SHA-256 digests for each key artefact). This record allows a later reviewer to identify which configuration and input produced a given playlist, with upstream stage run IDs linking each stage's execution and hashed component files showing which data versions were active.

## 4.10 BL-010 and BL-011: Reproducibility and Controllability Instrumentation

Two optional evaluation-support layers extend the implementation to enable reproducibility and controllability assessment.

**BL-010 (Reproducibility Layer)** repeats the main pipeline execution under fixed input and configuration and compares intermediate outputs to verify deterministic stability. It compares alignment summaries, candidate-pool counts, score distributions, playlist ordering, and final output hashes across independent runs. Output: `reproducibility_report.json` records the comparison results and verdict (Pass if all outputs identical; Fail with differences recorded).

**BL-011 (Controllability Layer)** executes the pipeline under controlled single-parameter variations and records how changes cascade through the system. For each variation (e.g., increasing the diversity-pressure setting), it captures output changes at candidate-space, ranking, assembly, and explanation levels. Output: `controllability_report.json` records the parameter-variation matrix and output deltas for each tested variation.

The implementation also includes two automated verification components: BL-013 (pipeline orchestration entrypoint) that governs stage execution order and validates stage-completion signals; and BL-014 (36-check automated sanity layer) that validates explanation fidelity, output-hash stability, cross-stage candidate-count consistency, and assembly-constraint satisfaction.

## 4.13 Evidence Packaging and Artefact Surface

All evidence artefacts produced by stages BL-003 through BL-009 resolve through a consistent output surface in `07_implementation/src/`. The table below maps each Chapter 3 objective to the Chapter 4 evidence surfaces that Chapter 5 will assess:

| Objective | Chapter 3 Design | Chapter 4 Evidence Surface | Chapter 5 Focus |
|-----------|------------------|---------------------------|-----------------|
| O1: Uncertainty-aware profiling | Section 3.7 | bl004_preference_profile.json + bl003 diagnostics | Uncertainty visibility, attribution clarity |
| O2: Confidence-aware alignment & candidate shaping | Sections 3.6, 3.8 | bl003_ds001_spotify_summary.json + bl005_candidate_diagnostics.json | Alignment confidence, exclusion pathways |
| O3: Controllable trade-offs | Sections 3.9, 3.10 | bl006_score_summary.json + bl007_assembly_report.json | Parameter sensitivity, constraint interaction |
| O4: Mechanism-linked explanation fidelity | Section 3.11 | bl008_explanation_payloads.json | Score attribution accuracy, contributor identification |
| O5: Reproducibility and controllability | Throughout Ch3 | BL-010 and BL-011 outputs + verification metadata | Replay consistency, parameter-variation signal |
| O6: Bounded-guidance surfaces | Sections 3.12, 3.10 | bl009_run_observability_log.json + BL-007 validity reporting | Boundary visibility, execution scope clarity |

## 4.14 Chapter Summary

This chapter has described how the design committed in Chapter 3 was implemented as an executable, evidence-producing pipeline. The implementation realised the design intent in each of the seven pipeline stages and included evaluation-support instrumentation layers to verify reproducibility and controllability. Collectively, these stages make the pipeline's transparency and controllability objectives visible in concrete evidence artefacts rather than remaining latent in the execution. Formal evaluation of these surfaces — whether evidence meets intended quality criteria — is presented in Chapter 5.
