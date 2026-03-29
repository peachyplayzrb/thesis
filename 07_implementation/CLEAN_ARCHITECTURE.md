# Clean Architecture Blueprint (07_implementation)

## Document Status

- Scope: Implementation-local architecture for the standalone package under `07_implementation/`
- Last updated: 2026-03-30
- Intended audience: Reviewers, maintainers, and contributors working on runtime execution and evidence generation
- Canonical runtime entrypoint: `main.py`
- Canonical orchestration runner: `src/orchestration/main.py`

## Purpose

This document defines the architecture that the implementation should follow to stay predictable, reproducible, and easy to operate.

The main objective is a single control plane:

- Users control runs through orchestration and run-config.
- Stages remain independently testable modules.
- Artifact contracts connect stages in a deterministic pipeline.

## Architecture Principles

1. Single user-facing execution surface
- User runs `main.py` (wrapper) or orchestration directly.
- Direct stage scripts are internal/debug surfaces, not the primary user workflow.

2. Deterministic stage contracts
- Every stage consumes explicit artifacts and emits explicit artifacts.
- Inter-stage communication is file-contract based, not in-memory coupling.

3. Explicit control precedence
- Runtime behavior should follow a stable precedence model.
- Controls must be visible in artifacts and traceable after execution.

4. Separation of responsibilities
- Orchestration decides ordering and failure behavior.
- Stages implement domain logic only.
- Shared utilities provide stable infrastructure primitives.

5. Evidence-first execution
- Runs should generate operational outputs and evaluation evidence in one coherent lifecycle.

## Layer Model

This implementation uses a practical layered model.

1. Entry Layer
- `main.py` validates package shape and launches orchestration with run-config context.

2. Orchestration Layer
- `src/orchestration/*`
- Resolves stage order, seed refresh policy, continue-on-error policy, and summary emission.

3. Stage Layer
- `src/alignment`, `src/profile`, `src/retrieval`, `src/scoring`, `src/playlist`, `src/transparency`, `src/observability`, `src/reproducibility`, `src/controllability`, `src/quality`
- Each stage is responsible for one bounded function and known artifact outputs.

4. Shared Runtime Infrastructure Layer
- `src/shared_utils/*` and `src/run_config/*`
- Path resolution, config loading, control resolution, hashing, IO, and schema-like control normalization.

5. Artifact Layer
- `src/*/outputs/*`
- Durable contracts used across stages and for post-run verification.

## Stage Lifecycle (Primary Flow)

Primary architecture lifecycle includes production, observability, evidence, and validation stages.

1. BL-003 Alignment
- Runner: `src/alignment/main.py`
- Role: Build aligned seed artifacts from embedded candidate dataset and ingestion export bundle.
- Influence policy: Emit influence contract metadata (enabled flag, track IDs, preference weight) only; do not let influence tracks alter profile-generation event rows.

2. BL-004 Profile
- Runner: `src/profile/main.py`
- Role: Build preference profile and seed trace from BL-003 outputs.
- Influence policy: Profile reflects listening-history evidence (and configured interaction scope), not direct influence-track row injection.

3. BL-005 Retrieval
- Runner: `src/retrieval/main.py`
- Role: Filter candidate corpus using profile-driven semantic and numeric controls.

4. BL-006 Scoring
- Runner: `src/scoring/main.py`
- Role: Score retained candidates with weighted components and diagnostics.
- Note: BL-006 is the owner of influence steering. Influence tracks should steer candidate ranking via candidate-to-influence similarity features, not by direct ID bonus that forces those tracks to the top.
- Required behavior: Influence tracks are optional style anchors, not guaranteed playlist members. Similar candidates can be promoted even when anchor tracks themselves are absent from the final playlist.

## Influence Steering Policy (Target)

1. Profile independence
- Influence tracks must not mutate BL-004 profile-generation rows.
- BL-004 profile outputs should remain stable under fixed listening history when only influence lists change.

2. Scoring-time steering
- BL-006 computes influence similarity signals for each retained candidate (for example from genre/tag overlap and numeric affinity relative to influence anchors).
- Final rank uses a tunable blend between profile-match score and influence-similarity score.

3. No forced inclusion
- Do not apply direct per-track ID bonus in BL-006.
- Influence anchors can be absent from final BL-007 output if they do not survive constraints and competition.

4. Transparency requirement
- BL-006/BL-008 outputs should expose influence-steering contributions so reviewers can distinguish profile-fit vs influence-steer effects.

## Migration Plan To Enforce This Logic

1. Remove profile-shaping injection path
- Stop mutating `matched_events` with synthetic influence rows in BL-003.
- Keep influence contract fields in BL-003 summary for downstream BL-006 use.

2. Replace direct ID bonus with similarity steering
- In BL-006, remove direct `track_id in influence_track_ids` additive bonus behavior.
- Add candidate-to-influence similarity computation and blend it into final scoring components.

3. Update controls schema
- Replace/retire controls that imply forced inclusion (for example direct ID bonus scale).
- Introduce explicit steering controls (for example steering enabled flag and steering weight) in run-config and runtime summaries.

4. Validate expected behavior
- With identical listening history, changing influence anchors should shift ranking toward similar songs without requiring anchors themselves in output.
- Verify BL-004 profile artifact diffs remain unchanged when only influence track list changes.

5. Keep BL-007 assembly-only boundary
- BL-007 continues applying deterministic assembly constraints over BL-006 ranked candidates only.

5. BL-007 Playlist
- Runner: `src/playlist/main.py`
- Role: Assemble final playlist under deterministic rule constraints.

6. BL-008 Transparency
- Runner: `src/transparency/main.py`
- Role: Build explanation payloads for each playlist track.

7. BL-009 Observability
- Runner: `src/observability/main.py`
- Role: Record run metadata, diagnostics, and artifact traceability.

8. BL-010 Reproducibility
- Runner: `src/reproducibility/main.py`
- Role: Replay BL-004..BL-009 outputs and verify repeatability via stable hashes and run matrix.

9. BL-011 Controllability
- Runner: `src/controllability/main.py`
- Role: Evaluate expected behavior shifts under controlled scenario perturbations.

10. BL-014 Quality/Sanity
- Runner: `src/quality/sanity_checks.py`
- Role: Validate schema, continuity, and hash-link integrity across produced artifacts.

## Orchestration Control Plane

### Current behavior

- Wrapper (`main.py`) resolves package paths, validates embedded dataset, sets `BL_RUN_CONFIG_PATH`, and launches BL-013 orchestration.
- Wrapper currently forces BL-003 refresh using `--refresh-seed` during standard runs.
- BL-013 default stage order currently covers BL-004..BL-009, with BL-003 optionally/explicitly run as seed refresh.

### Target behavior

- Users control all execution through orchestration CLI + run-config.
- Full lifecycle stage selection should include BL-003..BL-014 when requested.
- Orchestration summary should remain the canonical run narrative.

## Configuration Model

### Control sources

1. Orchestration CLI flags
2. Run-config (`config/profiles/*.json`)
3. Environment-based stage fallbacks (legacy/internal)
4. Stage defaults and sanitization

### Recommended precedence model

For user-facing runs, treat this as canonical:

1. Explicit orchestration CLI arguments
2. Run-config controls
3. Stage defaults

Environment overrides should be considered internal/debug controls and phased out from user-facing operation where practical.

### Canonical config artifacts

BL-013 emits paired artifacts:

- `src/run_config/outputs/run_intent_*.json`
- `src/run_config/outputs/run_effective_config_*.json`

Plus latest pointers:

- `src/run_config/outputs/run_intent_latest.json`
- `src/run_config/outputs/run_effective_config_latest.json`

These artifacts should remain part of every orchestrated run for auditability.

## Artifact Contract Model

Core output contracts:

- BL-003 seed and summary outputs under `src/alignment/outputs/`
- BL-004 profile and seed trace outputs under `src/profile/outputs/`
- BL-005 filtered candidates and decisions under `src/retrieval/outputs/`
- BL-006 scored candidates and scoring summaries under `src/scoring/outputs/`
- BL-007 playlist and assembly reports under `src/playlist/outputs/`
- BL-008 explanation payloads under `src/transparency/outputs/`
- BL-009 run observability log/index under `src/observability/outputs/`
- BL-010 reproducibility reports under `src/reproducibility/outputs/`
- BL-011 controllability reports under `src/controllability/outputs/`
- BL-014 sanity reports under `src/quality/outputs/`

Canonical path contracts are centralized in:

- `src/shared_utils/artifact_registry.py`

## Operational Run Modes

1. Standard production run
- Wrapper-driven execution of orchestration production chain with embedded dataset.

2. Subset-stage run
- Orchestration with explicit stage subset (for targeted iteration).

3. Evidence-inclusive run
- Orchestration flow plus reproducibility, controllability, and sanity validation.

## Known Constraints and Non-Goals

1. Mixed control channels still exist
- Some stage behavior can still be influenced by environment variables.
- This is a cleanup target, not the desired end state.

2. Direct stage executables remain available
- They are useful for debugging but should not be the primary operational interface.

3. BL-007 has fixed rule-order behavior
- Not all assembly behavior is intended to be externally tunable.

4. Causality trace granularity has limits
- Control effect interpretation should rely on current diagnostics outputs rather than claiming perfect per-control causality traces.

## Cleanup Roadmap (Implementation-Local)

1. Make orchestration the only documented user entry surface.
2. Expand BL-013 stage registry to support full BL-003..BL-014 lifecycle selection.
3. Migrate stage env-path/env-control overrides into run-config-backed controls.
4. Keep direct stage mains as internal/testing entrypoints.
5. Maintain one canonical run summary narrative under orchestration outputs.

## Implementation Source of Truth

For this document, architecture claims are implementation-grounded in:

- `main.py`
- `src/orchestration/main.py`
- `src/orchestration/cli.py`
- `src/orchestration/stage_registry.py`
- `src/orchestration/summary_builder.py`
- `src/shared_utils/artifact_registry.py`
- `src/shared_utils/stage_runtime_resolver.py`
- `src/run_config/run_config_utils.py`
