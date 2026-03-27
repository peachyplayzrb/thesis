# BL-010 and BL-011 Baseline Pinning Manifest

Last updated: 2026-03-27
Owner: Governance sync pass (docs-only)

## Purpose
This manifest records why BL-010 and BL-011 can show different pinned baseline snapshots while still remaining valid for their own reproducibility/controllability claims.

## Policy Status
- Canonical reporting baseline: `run_config_ui013_tuning_v1f.json` (D-033)
- BL-010 and BL-011 pinned snapshots: retained as intentional historical evaluation baselines
- Promotion or unification action: not applied in this pass

## BL-010 Pinned Snapshot
- run_id: `BL010-REPRO-20260327-001916`
- candidate-count context: `70680` (historical pinned state)
- deterministic claim: `deterministic_match=true`
- primary artifact:
  - `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_report.json`
- config hash (latest report): `9D87F287D0A6826CF2B2896F14F25086D6DE9B4786E48141A6AE0DC5FCB059D1`

## BL-011 Pinned Snapshot
- run_id: `BL011-CTRL-20260327-002019`
- candidate-count context: `33096` (historical pinned state)
- controllability claim: `status=pass`, 5 scenarios
- primary artifact:
  - `07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_report.json`
- config hash reference:
  - baseline hash in report metadata: `9D87F287D0A6826CF2B2896F14F25086D6DE9B4786E48141A6AE0DC5FCB059D1`

## Canonical Baseline Contrast
- Canonical v1f chain candidate count reference (active implementation reporting): `46776`
- Rationale for keeping divergence documented:
  - BL-010 and BL-011 evidence remains valid for the exact pinned snapshots they executed against.
  - Canonical implementation reporting remains anchored to D-033 (v1f).

## Governance Guardrail
Any future convergence of BL-010 and BL-011 onto one canonical candidate-count snapshot must be logged as a new decision entry and accompanied by refreshed evidence artifacts.