# System Architecture

DOCUMENT STATUS: implementation-synchronized system architecture
LAST SYNCHRONIZED: 2026-03-29 UTC
CONFIDENCE: high for implemented surfaces, medium for extension design
ROLE: end-to-end architecture record for BL-003 through BL-009

## 1) Purpose
Define the implemented system architecture for deterministic playlist generation, including stage ownership, interface boundaries, runtime control behavior, and auditability surfaces.

## 2) Architecture Layers to Stage Mapping
The conceptual stack is implemented as an explicit BL stage chain.

1. Data ingestion and canonical candidate preparation: BL-001 and BL-002 (upstream inputs).
2. Alignment and seed construction: BL-003 (`src/alignment`).
3. Preference modelling: BL-004 (`src/profile`).
4. Candidate filtering/retrieval: BL-005 (`src/retrieval`).
5. Deterministic scoring: BL-006 (`src/scoring`).
6. Playlist assembly: BL-007 (`src/playlist`).
7. Track-level explanations: BL-008 (`src/transparency`).
8. Run-level observability and audit index: BL-009 (`src/observability`).

## 3) Core Execution Flow
1. BL-003 aligns source events to DS-001-backed candidates and emits weighted seed artifacts.
2. BL-004 aggregates profile signals from aligned seeds and emits profile and summary artifacts.
3. BL-005 filters corpus candidates using semantic and numeric controls.
4. BL-006 computes weighted deterministic similarity scores for retained candidates.
5. BL-007 assembles a playlist using rule-based constraints over scored candidates.
6. BL-008 builds explanation payloads using BL-006 scoring and BL-007 assembly context.
7. BL-009 aggregates diagnostics, provenance, and artifact hashes across BL-003 to BL-008.

## 4) Runtime Control Architecture
### 4.1 Control Precedence
At orchestration and stage levels, control resolution follows a deterministic precedence:
1. CLI (where applicable at orchestration level).
2. Run-config controls (via `BL_RUN_CONFIG_PATH` and stage resolvers).
3. Environment variables.
4. Stage defaults.
5. Stage-specific sanitization and bounds enforcement.

### 4.2 Control Surface Position
1. BL-003: input scope and matching behavior controls.
2. BL-004: profile aggregation and attribution controls.
3. BL-005: retrieval thresholds, damping, and quality-penalty controls.
4. BL-006: component weights and semantic/numeric scoring controls.
5. BL-007: assembly limits and strategy controls (partial tunability).
6. BL-008/BL-009: explanation and diagnostic verbosity controls.

### 4.3 Important Caveat
BL-007 is partially configurable: thresholds/limits and strategy knobs are tunable, while rule order and selected helper heuristics remain fixed in code.

## 5) Interface and Artifact Boundaries
Cross-stage communication is artifact-based and file-contract driven.

1. BL-003 -> BL-004: aligned seed table + summary/contracts.
2. BL-004 -> BL-005 and BL-006: profile payload + seed trace/summary.
3. BL-005 -> BL-006: filtered candidate set + decision diagnostics.
4. BL-006 -> BL-007 and BL-008: scored candidates and summary diagnostics.
5. BL-007 -> BL-008 and BL-009: playlist payload + assembly trace/report.
6. BL-008 -> BL-009: explanation payload summary and detail outputs.

BL-009 enforces required upstream path contracts via shared artifact registry helpers.

## 6) Determinism and Auditability
The implemented architecture is designed for reproducibility and inspectability:

1. Stage outputs are deterministic under fixed inputs and effective controls.
2. Config provenance is persisted through run intent/effective config artifacts and stage metadata.
3. Artifact hash surfaces are generated and aggregated for run-chain integrity checks.

## 7) Known Architectural Limits
1. Influence-track effect remains weak and indirect in current control behavior.
2. BL-007 policy ordering is fixed despite expanded tunable controls.
3. Counterfactual explanation outputs are not implemented.
4. Unified per-track control-causality traces are not implemented as a pipeline contract.

## 8) Boundary Statement
This architecture is scoped to a deterministic single-user thesis artefact and does not claim production-scale monitoring, collaborative/deep recommendation behavior, or universal playlist quality guarantees.
