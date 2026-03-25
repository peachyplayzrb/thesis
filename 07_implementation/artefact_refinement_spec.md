# Artefact Refinement Spec

Status: R1, R2, and R3 complete — all refinements delivered
Date: 2026-03-25 (updated 2026-03-25 after all refinements validated)
Scope: pipeline artefact only; website/UI intentionally excluded

## 1. Purpose

This document defines the current artefact refinement state after the BL-009, BL-010, BL-011 alignment cycle and BL-021 source-scope implementation.

The objective is no longer to define the entire control surface from scratch. That foundation is now in place. The objective is to harden, normalize, and operationalize what already exists so the artefact remains explainable, controllable, and auditable under thesis defense conditions.

## 2. Current Baseline (As Implemented)

### 2.1 Run-Config Contract Exists

Implemented:

1. canonical run-config utilities and schema template are active
2. stage scripts consume run-config values rather than only stage-local constants
3. effective run metadata is persisted into stage outputs

Key implementation evidence:

1. 07_implementation/implementation_notes/run_config/run_config_utils.py
2. 07_implementation/implementation_notes/run_config/run_config_template_v1.json
3. 07_implementation/IMPLEMENTATION_STATE_2026-03-24.md

### 2.2 Source-Scope Control (BL-021) Is Actuated

Implemented:

1. source-family inclusion and per-source limits are represented in run config
2. BL-003 applies scope filters and emits source-scope manifest evidence
3. BL-004 and BL-009 persist effective input scope in run outputs

Status:

1. BL-021 is complete at artefact level (not deferred)

### 2.3 BL-009, BL-010, BL-011 Active-Mode Compatibility Is Complete

Implemented:

1. BL-009 observability no longer hard-fails on legacy BL-016/BL-017 assets
2. BL-010 reproducibility supports active pipeline outputs as fixed-input source
3. BL-011 controllability supports active schemas and mode-compatible normalization

Current behavior:

1. legacy surrogate artefacts are optional
2. active BL-004 to BL-009 chain is the primary validated path

### 2.4 Canonical Run Pair Artifacts (R1) Are Implemented

Implemented:

1. run-intent and run-effective-config artifacts are emitted as a deterministic pair on every top-level BL-013 run
2. BL-013 emits both artifacts before any stage executes and propagates paths via BL_RUN_INTENT_PATH and BL_RUN_EFFECTIVE_CONFIG_PATH env vars
3. BL-009 ingests the artifact pair, checks availability, computes SHA256, and records a canonical_config_artifacts block in the observability log
4. artifact schema versions: run-intent-v1, run-effective-config-v1

Key implementation evidence:

1. 07_implementation/implementation_notes/run_config/run_config_utils.py — write_run_config_artifact_pair and builder functions
2. 07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py — emit_run_config_artifact_pair, --run-config-artifact-dir, env var propagation
3. 07_implementation/implementation_notes/observability/build_bl009_observability_log.py — canonical_config_artifacts block, safe_relpath, BL_RUN_INTENT_PATH/BL_RUN_EFFECTIVE_CONFIG_PATH ingestion
4. 07_implementation/implementation_notes/run_config/outputs/ — timestamped and _latest artifact files

### 2.5 Validated Recent Baseline Runs

1. BL-010 reproducibility pass: BL010-REPRO-20260324-234322
2. BL-011 controllability pass: BL011-CTRL-20260324-235114
3. BL-013 orchestrated pass (pre-R1): BL013-ENTRYPOINT-20260324-235248-642823
4. BL-013 orchestrated pass (R1 validation): BL013-ENTRYPOINT-20260325-000545-164768

## 3. Control Inventory (Current Practical Surface)

### 3.1 Input Composition Controls

Current controls include:

1. source-scope toggles and limits (top tracks, saved tracks, playlists, recently played)
2. interaction type inclusion
3. influence-track participation in profile construction

### 3.2 Profile Controls (BL-004)

Current controls include:

1. top tag, genre, and lead-genre limits
2. profile weighting behavior such as influence and recency factors

### 3.3 Retrieval Controls (BL-005)

Current controls include:

1. semantic keep thresholds
2. numeric support threshold
3. numeric tolerance thresholds for tempo/key/mode/duration proximity

### 3.4 Scoring Controls (BL-006)

Current controls include:

1. component weights
2. numeric thresholds used during scoring similarity calculations

### 3.5 Assembly, Transparency, and Observability Controls (BL-007 to BL-009)

Current controls include:

1. playlist size and diversity constraints
2. explanation depth limit
3. observability diagnostic sample limit and stage/run metadata capture

## 4. What Is Still Weak (Remaining Refinement)

This section lists only unresolved gaps after the 2026-03-24 stabilization.

### 4.1 ~~Run Intent vs Effective Config Is Not Yet Canonicalized Per Run Artifact Pair~~ — RESOLVED (R1)

Resolution:

1. deterministic run-intent and run-effective artifact pairs are now emitted on every BL-013 run
2. lineage references are propagated to BL-009 via environment variables and recorded in the observability log with SHA256 verification
3. validated in run BL013-ENTRYPOINT-20260325-000545-164768

### ~~4.2 Control Naming Is Still Stage-Centric For External Explanation~~ — RESOLVED (R2)

Resolution:

1. semantic control-layer map produced and stored at 07_implementation/implementation_notes/run_config/semantic_control_map.md
2. seven semantic groups defined: Input Composition, Profile Construction, Retrieval Filtering, Scoring, Playlist Assembly, Transparency, Observability
3. each group maps to its run-config section(s), individual field names with types and defaults, consuming stage(s), resolver function, and implementation output paths
4. engineering names retained internally; semantic map is the thesis/operator-facing layer only

### 4.3 ~~BL-009 Schema Can Be Upgraded To Become The Single Canonical Execution Record~~ — RESOLVED (R3)

Resolution:

1. BL009_OBSERVABILITY_SCHEMA_VERSION = "bl009-observability-v1" constant added and recorded in run_metadata.observability_schema_version
2. execution_scope_summary top-level block added: source family, interaction types included, seed count, history/influence track counts, influence participation flag, canonical config artifact pair availability
3. first-class lineage links to run-intent and run-effective artifacts already present from R1
4. validated in run BL013-ENTRYPOINT-20260325-001552-538292

## 5. Updated Refinement Plan

### R1 (P0): Canonical Run Pair Artifacts — COMPLETE

Deliverables (all delivered):

1. run_intent_<timestamp>.json — schema version run-intent-v1
2. run_effective_config_<timestamp>.json — schema version run-effective-config-v1
3. strict schema validation and version tagging
4. _latest copies maintained alongside timestamped files
5. BL-009 observability log links to both artifacts with SHA256 and availability flags

Validated in: BL013-ENTRYPOINT-20260325-000545-164768

### R2 (P1): Semantic Control-Layer Mapping — COMPLETE

Deliverables (all delivered):

1. semantic_control_map.md at 07_implementation/implementation_notes/run_config/semantic_control_map.md
2. seven semantic control groups with full field-level mapping from run-config schema to stage implementation
3. cross-reference table of resolver entry points and artifact lineage notes
4. controllability scenario cross-reference

### R3 (P1): BL-009 Schema Promotion — COMPLETE

Deliverables (all delivered):

1. BL009_OBSERVABILITY_SCHEMA_VERSION = "bl009-observability-v1" constant in build_bl009_observability_log.py
2. observability_schema_version field in run_metadata
3. execution_scope_summary top-level block with source family, interaction types, seed counts, influence participation, and canonical artifact pair availability flag
4. direct lineage links to run-intent and run-effective artifacts (delivered by R1, retained)

Validated in: BL013-ENTRYPOINT-20260325-001552-538292

## 6. Definition Of Done (Revised)

Refinement is complete when:

1. every run emits run-intent and run-effective artifacts as a deterministic pair
2. BL-009 links directly to that pair and all downstream stage artefacts
3. control-layer documentation maps semantic controls to concrete stage fields
4. reproducibility and controllability comparisons reference canonical config artifacts rather than inferred overrides

## 7. Out Of Scope For This Pass

1. website UX flow redesign
2. new ingestion adapters
3. corpus fallback policy expansion beyond already tracked backlog commitments
4. recommendation model expansion beyond current deterministic architecture

## 8. Status: All Refinements Complete

R1, R2, and R3 are all delivered and validated. The artefact refinement cycle is closed.

Summary of what was delivered:

1. R1: canonical run-intent / run-effective-config artifact pair emitted on every BL-013 run with SHA256 verification and BL-009 lineage links
2. R2: semantic_control_map.md documenting all seven control groups with field-level mapping from run-config schema to stage implementation
3. R3: BL-009 observability log promoted to versioned schema (bl009-observability-v1) with execution_scope_summary top-level block

## 9. Historical Note

Sections in older versions that marked BL-021 and active-mode BL-009/10/11 compatibility as missing are now historical and superseded by the current implementation baseline.
