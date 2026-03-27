# Artifact Lifecycle Policy

Last updated: 2026-03-27

## Purpose
This document defines artifact classification, retention, and archive handling for active implementation outputs.

## Classification
- Canonical: run artifacts tied to the active reporting baseline.
- Experimental: run artifacts tied to non-canonical profiles or probes.
- Historical retained: evidence snapshots preserved for audit traceability.
- Archived: superseded bundles moved out of active working paths.

## Canonical Artifact Set
- BL-007 playlist outputs
- BL-008 explanation outputs
- BL-009 observability outputs
- BL-014 sanity/quality outputs
- BL-013 run summary outputs used to verify orchestration and stable hashes

## Retention Rules
1. Keep canonical baseline evidence chains referenced by ACTIVE_BASELINE.md.
2. Keep latest canonical run plus enough prior canonical runs to support reproducibility comparison.
3. Keep experimental run waves only when referenced by backlog decisions or experiment log entries.
4. Keep historical retained artifacts when cited by submission, decision logs, or thesis narrative evidence.
5. Move superseded non-required artifacts to archive folders instead of deleting immediately.

## Archive Handling
- Active archive location for consolidated historical waves:
  - _deep_archive_march2026/
- Admin archive support location:
  - 00_admin/archives/

When moving artifacts:
- preserve run identifiers
- preserve manifest references
- update references in active docs that pointed to moved paths

## Authority and Precedence
- Baseline authority: 07_implementation/ACTIVE_BASELINE.md
- Submission retention scope: 07_implementation/implementation_notes/SUBMISSION_MANIFEST.md
- BL-013 run-wave retention detail: 07_implementation/implementation_notes/bl013_entrypoint/outputs/BL013_RUN_MANIFEST.md
- Run-config retention detail: 07_implementation/implementation_notes/bl000_run_config/outputs/RUN_CONFIG_RETENTION_POLICY.md

If retention guidance conflicts across documents, this policy and ACTIVE_BASELINE.md take precedence for active cleanup decisions.

## Operational Checklist
1. Confirm artifact category (canonical, experimental, historical retained, archived).
2. Confirm whether artifact is referenced by baseline authority, backlog, experiment log, or submission manifest.
3. If not required in active scope, move to archive with run ID intact.
4. Update documentation references after movement.
5. Re-run sanity/freshness checks if active artifact paths changed.
