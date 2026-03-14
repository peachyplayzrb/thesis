# Literature-Architecture Mapping

DOCUMENT STATUS: working justification map
CONFIDENCE: medium
ROLE: architecture justification and traceability
SCOPE BASIS: `00_admin/Artefact_MVP_definition.md`
EVALUATION BASIS: `00_admin/evaluation_plan.md`
LITERATURE BASIS: P-001..P-049

## 1) Architecture Layer Review Against Locked MVP

### Layers Confirmed In Scope
1. User Interaction Layer
2. Data Ingestion Layer
3. Track Alignment Layer
4. Preference Modelling Layer
5. Candidate Dataset Layer
6. Feature Processing Layer
7. Deterministic Candidate Scoring Engine
8. Playlist Assembly Layer
9. Output and Explanation Layer
10. Observability and Audit Layer
11. Configuration and Execution Layer

### MVP Fit Assessment
- Fits MVP: deterministic scoring, explanation linkage, controllability parameters, reproducibility logging.
- Needs scope discipline: ingestion should remain one practical adapter path in MVP.
- Potentially beyond MVP if implemented fully: advanced UI personalization, multi-adapter ingestion, extensive observability dashboarding.

## 2) Literature Justification Mapping

### Layer 1: User Interaction Layer
- Literature theme: controllability, transparency_and_scrutability
- Supporting papers: P-004, P-014, P-015, P-020, P-021, P-023, P-002
- Design requirement: user must influence recommendation behavior without opaque control logic
- System mechanism: influence tracks and a small set of interpretable control parameters

### Layer 2: Data Ingestion Layer
- Literature theme: music_recommender_challenges
- Supporting papers: P-005, P-006, P-011, P-012, P-013, P-019, P-041
- Design requirement: collect practical user-preference signals for pipeline input
- System mechanism: one selected ingestion path plus manual seed/influence support

### Layer 3: Track Alignment Layer
- Literature theme: cross_source_preference_data (candidate)
- Supporting papers: P-029, P-030, P-031 (direct entity-resolution support; music-domain specificity limited)
- Design requirement: map imported tracks into feature corpus consistently
- System mechanism: ISRC-first matching with metadata fallback

### Layer 4: Preference Modelling Layer
- Literature theme: feature_based_preference_representation (candidate)
- Supporting papers: P-007, P-015, P-018, P-019, P-020, P-026, P-006, P-005, P-043
- Design requirement: build interpretable user profile for deterministic ranking
- System mechanism: aggregate matched-track features plus influence tracks

### Layer 5: Candidate Dataset Layer
- Literature theme: music_recommenders, evaluation_challenges
- Supporting papers: P-006, P-008, P-009, P-018, P-024, P-028, P-005, P-041
- Design requirement: constrain candidate space for feasible deterministic evaluation
- System mechanism: fixed canonical corpus (Music4All) and filtered candidate subset

### Layer 6: Feature Processing Layer
- Literature theme: feature_engineering_music (candidate)
- Supporting papers: P-007, P-016, P-018, P-025, P-026, P-006, P-008
- Design requirement: ensure feature comparability and stable scoring behavior
- System mechanism: selection, normalization, missing-value handling, weight preparation

### Layer 7: Deterministic Candidate Scoring Engine
- Literature theme: explainable_recommenders, transparency_by_design, evaluation_of_explainable_systems
- Supporting papers: P-001, P-002, P-003
- Design requirement: recommendation logic must be inspectable and reproducible
- System mechanism: explicit weighted similarity with documented rule adjustments

### Layer 8: Playlist Assembly Layer
- Literature theme: music_recommender_challenges, playlist_generation
- Supporting papers: P-005, P-008, P-009, P-017, P-028
- Design requirement: recommendation output must satisfy playlist-level constraints beyond ranking
- System mechanism: rule-based assembly (length, artist repetition, diversity/order)

### Layer 9: Output and Explanation Layer
- Literature theme: explainable_recommenders, transparency_and_scrutability
- Supporting papers: P-001, P-002, P-003, P-042
- Design requirement: expose understandable reasons linked to actual ranking process
- System mechanism: per-track score contribution and rule-adjustment explanation output

### Layer 10: Observability and Audit Layer
- Literature theme: evaluation_of_explainable_systems (partial)
- Supporting papers: P-032, P-033, P-034, P-037, P-040, P-010, P-021, P-022, P-023, P-001, P-003, P-046
- Design requirement: make internal decisions inspectable and testable
- System mechanism: run logs for input, alignment, scoring configuration, and outputs

### Layer 11: Configuration and Execution Layer
- Literature theme: evaluation_of_explainable_systems (partial)
- Supporting papers: P-032, P-033, P-034, P-037, P-040, P-003, P-010, P-011, P-013, P-024, P-009 (method and reproducibility support)
- Design requirement: deterministic replay and parameter-effect testing
- System mechanism: explicit configuration profiles and repeatable execution controls

### Comparator Context (Out of Core MVP)
- Literature theme: multimodal_and_hybrid_tradeoff
- Supporting papers: P-044, P-045, P-047, P-048, P-049
- Design requirement: acknowledge stronger-complex methods without expanding MVP scope
- System mechanism: include comparator discussion in evaluation framing, not core implementation

## 3) Weak Justification Flags (Needs Additional Literature Support)
1. Track Alignment Layer
- Reason: now has direct entity-resolution support (P-029 to P-031), but still lacks music-specific ISRC/fallback reliability benchmarks.
2. Observability/Audit Layer
- Reason: recommender reproducibility support is now direct (P-032 to P-034), but implementation-level logging schema references remain limited.

## 4) Updated Support Strength Snapshot
- User Interaction Layer: medium-high
- Data Ingestion Layer: medium-high
- Track Alignment Layer: medium
- Preference Modelling Layer: medium-high
- Candidate Dataset Layer: high
- Feature Processing Layer: medium-high
- Deterministic Scoring Engine: high
- Playlist Assembly Layer: medium-high
- Output and Explanation Layer: high
- Observability/Audit Layer: medium-high
- Configuration/Execution Layer: medium-high

## 5) Targeted Literature Needs For Next Batch
- One direct music-domain study on ISRC/metadata alignment reliability and ambiguity/error handling.
- One recommender-system observability/logging practice paper with concrete schema or instrumentation guidance.
- One cross-platform music identity-resolution evaluation paper (for Spotify-like metadata fields).
- One independent third-party recommender study that uses Music4All (or equivalent) to strengthen external corpus-choice validation.
