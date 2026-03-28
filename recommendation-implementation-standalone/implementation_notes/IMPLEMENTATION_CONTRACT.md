# Implementation Contract

Last updated: 2026-03-27

## Purpose
This document is the master contract for pipeline inputs, stage boundaries, and output artifacts for the active deterministic implementation.

For canonical baseline evidence chains and run posture, see:
- 07_implementation/ACTIVE_BASELINE.md

## System Contract Summary
- Deterministic single-user content-based pipeline
- Active execution corpus: DS-001
- Orchestration entrypoint: BL-013
- Validation gates: BL-010, BL-011, BL-014

## Contracted Stage Flow
1. BL-001/BL-002 ingestion exports and normalizes source data.
2. BL-003 aligns source evidence to DS-001 and emits seed artifacts.
3. BL-004 builds deterministic user preference profile.
4. BL-005 filters candidate corpus under semantic and numeric controls.
5. BL-006 scores filtered candidates using weighted hybrid components.
6. BL-007 assembles playlist under rule constraints.
7. BL-008 emits explanation payloads.
8. BL-009 emits observability artifacts.
9. BL-010/BL-011/BL-014 validate reproducibility, controllability, and sanity/freshness.

## Input Contract
- Source family: spotify_api_export path through BL-001/BL-002 outputs.
- Alignment target: DS-001 working candidate dataset.
- Runtime controls: run-config resolved through BL-000 run-config layer.

Reference docs:
- 07_implementation/implementation_notes/bl001_bl002_ingestion/docs/spotify_api_ingestion_runbook.md
- 07_implementation/implementation_notes/bl000_run_config/docs/semantic_control_map.md
- 07_implementation/implementation_notes/bl000_data_layer/bl000_state_log_2026-03-25.md

## Output Contract (Canonical Retained)
- BL-007 playlist output
- BL-008 explanation payload output
- BL-009 observability log/index output
- BL-014 sanity and quality reports

Submission reference:
- 07_implementation/implementation_notes/SUBMISSION_MANIFEST.md

## Determinism and Evidence Contract
- Repeated runs with unchanged code, data, and run-config must preserve deterministic stable artifact hashes.
- Baseline evidence references are maintained in ACTIVE_BASELINE.md.
- Run-specific artifacts are canonical evidence; latest pointers are convenience pointers.

## Stage Boundary Contracts
- BL-003 to BL-004: seed table and trace artifacts must remain parse-compatible.
- BL-004 to BL-005: preference profile schema and numeric feature profile keys must remain stable unless versioned.
- BL-005 to BL-006: filtered candidate schema and key score-support fields must remain stable unless versioned.
- BL-006 to BL-007: scored candidate rank and score fields are required for assembly.
- BL-007 to BL-008/BL-009: playlist and scoring traces required for explanations and observability linkage.

## Contract Change Policy
- Non-breaking changes:
  - Additive fields with backward-compatible defaults
  - Additional diagnostics outputs that do not alter required output artifacts
- Breaking changes require:
  - explicit schema/version marker
  - migration notes in stage state logs
  - baseline re-pin decision and evidence chain update

## Related References
- Canonical run guide: 07_implementation/RUN_GUIDE.md
- Baseline authority: 07_implementation/ACTIVE_BASELINE.md
- Current implementation status sheet: 07_implementation/implementation_notes/CODEBASE_ISSUES_CURRENT.md
