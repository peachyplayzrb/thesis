# Architecture

DOCUMENT STATUS: implementation-synchronized architecture specification
LAST SYNCHRONIZED: 2026-03-29 UTC
CONFIDENCE: high for module ownership and stage behavior, medium for future extensibility
ROLE: code-grounded architecture record for BL-003 to BL-009
SOURCE OF TRUTH: `07_implementation/src/*` stage modules and shared runtime-control infrastructure

## 1) Purpose and Scope
This document describes the implemented architecture of the deterministic recommendation pipeline, focusing on stage ownership, runtime control flow, artifact contracts, and cross-stage dependencies.

In scope:
- BL-003 through BL-009 stage architecture and data flow.
- Runtime control resolution patterns and provenance behavior.
- Transparency and observability surfaces as implemented.

Out of scope:
- Historical conceptual alternatives not present in code.
- Unimplemented future features (for example counterfactual explanation generation).

## 2) Implemented Stage Map

| Stage | Module Surface | Core Responsibility | Primary Outputs |
|---|---|---|---|
| BL-003 Alignment | `src/alignment` | Align Spotify/export events to DS-001 candidates and construct weighted seed surface | Seed table CSV, alignment summary JSON, scope manifest |
| BL-004 Profile | `src/profile` | Build deterministic user-preference profile from aligned seeds | Profile JSON, seed trace CSV, profile summary JSON |
| BL-005 Retrieval | `src/retrieval` | Filter candidate corpus using semantic and numeric controls | Filtered candidates CSV, candidate decisions CSV, diagnostics JSON |
| BL-006 Scoring | `src/scoring` | Compute deterministic weighted similarity scores for retained candidates | Scored candidates CSV, score diagnostics JSON, score summary JSON |
| BL-007 Playlist | `src/playlist` | Assemble final playlist using rule-gated deterministic selection | Playlist JSON, assembly trace CSV, assembly report JSON |
| BL-008 Transparency | `src/transparency` | Generate per-track explanation payloads from scored and assembled outputs | Explanation payloads JSON, explanation summary JSON |
| BL-009 Observability | `src/observability` | Aggregate run diagnostics, hashes, and stage metadata for auditability | Run observability log JSON |

## 3) Stage Architecture Details

### 3.1 BL-003 Alignment
Entrypoint: `alignment/stage.py` (`AlignmentStage`).

Implemented flow:
1. Resolve paths and load source event rows.
2. Resolve runtime scope and behavior controls.
3. Apply source-scope filtering and matching pipeline.
4. Aggregate matched events into weighted seed surface.
5. Emit seed table, summary, and source-scope manifest.

Key contracts:
- Typed behavior and structural contracts in `alignment/models.py`.
- Alignment summary/context contracts for deterministic reporting.

### 3.2 BL-004 Profile
Entrypoint: `profile/stage.py` (`ProfileStage`).

Implemented flow:
1. Resolve typed paths and runtime controls.
2. Load BL-003 artifacts and contracts.
3. Aggregate numeric and semantic preference signals.
4. Build canonical profile blocks (`numeric_confidence`, `profile_signal_vector`, attribution diagnostics).
5. Emit profile payload, seed trace, and profile summary.

Key contracts:
- `ProfileControls`, `ProfilePaths`, `ProfileInputs`, `ProfileAggregation`, `ProfileArtifacts` in `profile/models.py`.

### 3.3 BL-005 Retrieval
Entrypoint: `retrieval/stage.py` (`RetrievalStage`).

Implemented flow:
1. Resolve controls and build retrieval runtime context from BL-004 profile signal.
2. Evaluate candidate rows with semantic and numeric keep/reject logic.
3. Emit filtered candidates, detailed candidate decisions, and diagnostics with distributions and rule-hit summaries.

Key contracts:
- Typed controls/context/results in `retrieval/models.py`.
- Decision-surface fields are treated as a downstream compatibility contract.

### 3.4 BL-006 Scoring
Entrypoint: `scoring/stage.py` (`ScoringStage`).

Implemented flow:
1. Resolve scoring controls and active component weights.
2. Build scoring context from BL-004 profile and BL-005 filtered candidates.
3. Compute per-component similarities and weighted contributions.
4. Rank candidates and emit scored CSV plus diagnostics and summary artifacts.

Key contracts:
- `SCORED_CANDIDATE_FIELDS` and typed controls/context contracts in `scoring/models.py`.

### 3.5 BL-007 Playlist
Entrypoint: `playlist/stage.py` (`PlaylistStage`).

Implemented flow:
1. Resolve controls and candidate inputs from BL-006.
2. Apply assembly rules with deterministic ordering and configurable thresholds/limits.
3. Emit playlist payload, assembly trace, and report diagnostics.

Configurability status:
- Tunable at runtime: `target_size`, `min_score_threshold`, `max_per_genre`, `max_consecutive`, utility strategy/weights, adaptive limits, controlled relaxation.
- Fixed residuals: rule order (R1 to R4) and selected helper heuristics remain code-fixed.

### 3.6 BL-008 Transparency
Entrypoint: `transparency/main.py`.

Implemented flow:
1. Join BL-006 scored candidates with BL-007 playlist and trace context.
2. Build per-track explanation payloads (`why_selected`, `top_score_contributors`, `score_breakdown`, assembly context).
3. Emit explanation payloads and summary with provenance hashes.

### 3.7 BL-009 Observability
Entrypoint: `observability/main.py`.

Implemented flow:
1. Load required upstream artifacts via registry.
2. Aggregate stage diagnostics, scope/config metadata, and exclusion samples.
3. Compute and emit hash/provenance index and run-level observability log.

## 4) Runtime Control Architecture

### 4.1 Orchestration Precedence
At BL-013 orchestration level, stage execution order precedence is:
1. CLI flags (`--stages`) when provided.
2. Run-config orchestration controls.
3. Default stage order.

### 4.2 Stage Control Resolution Pattern
Most stage runtime controls follow this pattern via shared resolver infrastructure:
1. If `BL_RUN_CONFIG_PATH` is present, load stage controls from run-config.
2. Otherwise resolve from stage environment variables.
3. Apply stage-specific sanitization and bounds checks.
4. Persist control provenance (`config_source`, `run_config_path`, schema/version metadata where supported).

### 4.3 Stage-Specific Caveats
- BL-003 includes additional fallback behavior tied to export-selection/input-scope semantics.
- BL-007 is partially configurable: thresholds and strategies are tunable, but rule order remains fixed.
- Some environment JSON overrides are less strict than run-config schema validation and rely on stage sanitizers.

## 5) Artifact and Contract Dependencies

### 5.1 Cross-Stage Flow
1. BL-003 emits aligned seed surface consumed by BL-004.
2. BL-004 emits profile and trace artifacts consumed by BL-005 and BL-006.
3. BL-005 emits filtered candidates consumed by BL-006.
4. BL-006 emits scored candidates consumed by BL-007 and BL-008.
5. BL-007 emits playlist and trace context consumed by BL-008.
6. BL-009 consumes BL-003 to BL-008 artifacts through required-path registry contracts.

### 5.2 De Facto Interface Surfaces
- BL-005 candidate decision fields are used as downstream diagnostics/observability interfaces.
- BL-006 scored candidate columns are consumed directly by BL-007 and BL-008.
- BL-007 assembly trace/report fields are consumed by BL-008 and BL-009.
- BL-009 required paths in `shared_utils/artifact_registry.py` are an explicit pipeline contract.

## 6) Transparency and Observability Architecture

### 6.1 Implemented Transparency Behavior
- BL-008 provides deterministic explanation payloads per playlist track.
- Explanations include ranked contributors, score breakdown, and concise selection rationale.
- Assembly context is joined from BL-007 trace/report artifacts.

### 6.2 Implemented Observability Behavior
- BL-009 aggregates stage-level diagnostics, run metadata, config provenance, and hash surfaces.
- Hashing and artifact provenance are standardized through shared hashing utilities.
- Observability output is structured as a run-level audit surface for reproducibility and post-run inspection.

## 7) Known Implementation Limitations
The following limitations are currently true in code and should be treated as architecture constraints:

1. Influence-track effect remains weak and indirect in the current pipeline behavior.
2. BL-007 control surface is partial: configurable thresholds/strategies with fixed rule order residuals.
3. BL-008/BL-009 do not emit counterfactual what-if explanation payloads.
4. Unified per-track control-causality tracing is not implemented as a cross-stage contract.

## 8) Scope Boundary Notes
This architecture is intentionally scoped to a deterministic single-user pipeline and thesis-aligned engineering evidence.

Not claimed by this architecture:
- Universal recommendation quality across user populations.
- Collaborative/deep-learning recommendation behavior.
- Fully user-programmable policy ordering across all playlist rules.

Future-work items should be documented as optional extensions and must not be represented as active implemented behavior unless reflected in stage code and artifact contracts.
