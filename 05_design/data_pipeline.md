# Data Pipeline

DOCUMENT STATUS: implementation-synchronized data pipeline design
LAST SYNCHRONIZED: 2026-04-19 UTC
ROLE: code-grounded data and artifact flow reference

## 1) Purpose
Describe data flow, artifact contracts, and integrity checkpoints across active stages.

## 2) Active Stage Sequence
BL-003 -> BL-004 -> BL-005 -> BL-006 -> BL-007 -> BL-008 -> BL-009 -> BL-010 -> BL-011 -> BL-013 -> BL-014

Note: BL-012 is currently unassigned in the active sequence.

## 3) Stage-by-Stage Data Flow
1. BL-003 Alignment:
	source events + candidate reference -> aligned seeds, alignment summary, scope manifest.
2. BL-004 Profile:
	BL-003 artifacts -> preference profile, seed trace, profile summary.
3. BL-005 Retrieval:
	BL-004 profile + candidate corpus -> filtered candidates, decision rows, diagnostics.
4. BL-006 Scoring:
	BL-005 filtered candidates + profile context -> scored candidates, score diagnostics/summary.
5. BL-007 Playlist:
	BL-006 scored candidates -> playlist payload, assembly trace, assembly report.
6. BL-008 Transparency:
	BL-006 + BL-007 outputs -> per-track explanation payloads and summary.
7. BL-009 Observability:
	BL-003..BL-008 outputs -> run-level observability log and provenance summaries.
8. BL-010 Reproducibility:
	replay inputs + prior artifacts -> reproducibility report (`deterministic_match`, interpretation boundaries).
9. BL-011 Controllability:
	scenario controls + baseline artifacts -> scenario matrix/report and interaction coverage summaries.
10. BL-013 Orchestration:
	 run config + stage plan -> stage execution outputs and summary metadata.
11. BL-014 Sanity:
	 full artifact set -> contract/gate/advisory integrity report.

## 4) Integrity and Provenance Controls
1. BL-009 consolidates lineage/provenance context.
2. BL-013 emits `stage_execution` to prevent hidden execution-order drift.
3. BL-014 validates handshake, schema, hash, and continuity constraints.
4. BL-010 bounds replay interpretation via explicit non-claim framing.

## 5) Known Pipeline Issues
1. Optional-stage presence can vary by run intent, requiring careful interpretation of missing optional artifacts.
2. Environment overrides may be looser than strict schema validation in some control paths.
3. Full counterfactual rerun comparison is not an always-on default pipeline behavior.

## 6) Boundary Statement
Pipeline behavior and claims are deterministic and single-user scoped; conclusions are valid only within declared input/config/runtime boundaries.
