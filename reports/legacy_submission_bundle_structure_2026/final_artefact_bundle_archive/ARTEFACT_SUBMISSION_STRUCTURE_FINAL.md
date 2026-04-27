# Artefact Submission Structure (Final Placeholder Authority)

Last updated: 2026-03-28
Status: Placeholder skeleton with initial standalone entrypoint implementation

## Purpose
This file defines the final hand-in structure for the thesis artefact package.
It is the packaging authority for submission assembly and examiner usability.

## Scope and Non-Scope
- In scope: submission folder structure, required placeholder slots, verification checklist, traceability placeholders.
- Out of scope: pipeline behavior changes, algorithm changes, run-config semantics, stage contract changes.

## Authority Alignment
- Submission requirements authority: 01_requirements/submission_requirements.md
- MVP scope authority: 00_admin/Artefact_MVP_definition.md
- Baseline evidence authority: 07_implementation/ACTIVE_BASELINE.md
- Stage contract authority: 07_implementation/implementation_notes/IMPLEMENTATION_CONTRACT.md

## Final Layout (Placeholder)

## Implemented Standalone Entry Surface (Initial)
- `final_artefact.py` (root-level standalone entrypoint with `run`, `validate`, `bundle`, and `show-paths` commands)
- `final_artefact/README.md` (standalone quickstart)
- `final_artefact/config/default_config.json` (default standalone profile pointers)
- `final_artefact/requirements.txt` (standalone runtime dependency list)
- `final_artefact/SUBMISSION_BUNDLE_MANIFEST.md` (include/exclude guidance for hand-in bundle)

### A. Minimum Submission Set (Mandatory)
- artefact/
- artefact/README.md
- artefact/requirements.txt
- artefact/final_artefact.py
- artefact/run/
- artefact/run/ENTRY_COMMAND_PLACEHOLDER.md
- artefact/config/
- artefact/config/default_config.json
- artefact/outputs/
- artefact/outputs/playlist/PLAYLIST_OUTPUT_PLACEHOLDER.md
- artefact/outputs/explanations/EXPLANATION_OUTPUT_PLACEHOLDER.md
- artefact/outputs/observability/OBSERVABILITY_OUTPUT_PLACEHOLDER.md
- artefact/outputs/quality/QUALITY_REPORT_PLACEHOLDER.md
- artefact/evidence/
- artefact/evidence/BASELINE_CHAIN_PLACEHOLDER.md
- artefact/evidence/RUN_MANIFEST_PLACEHOLDER.md
- artefact/docs/
- artefact/docs/QUICKSTART_PLACEHOLDER.md
- artefact/docs/LIMITATIONS_PLACEHOLDER.md

### B. Full Archive Set (Optional, Retained)
- artefact_archive/
- artefact_archive/stage_outputs/
- artefact_archive/state_logs/
- artefact_archive/experimental_runs/
- artefact_archive/historical_snapshots/

## Submission Buckets (Mandatory vs Optional)
- Run: Mandatory
- Config: Mandatory
- Outputs: Mandatory
- Evidence: Mandatory
- Docs: Mandatory
- Governance: Mandatory
- Optional Archive: Optional

## Artifact Inventory Template (Placeholder)
| Artifact Name | Stage Owner | Source Path | Submission Path | Mandatory (Y/N) | Verification Status |
| --- | --- | --- | --- | --- | --- |
| ARTIFACT_NAME_PLACEHOLDER | BL-XXX | SOURCE_PATH_PLACEHOLDER | SUBMISSION_PATH_PLACEHOLDER | Y | NOT_VERIFIED |

## Reproducibility Template (Placeholder)
### Environment
- ENVIRONMENT_PLACEHOLDER

### Entry Command
- ENTRY_COMMAND_PLACEHOLDER

### Validation Command
- VALIDATION_COMMAND_PLACEHOLDER

### Expected Outputs
- EXPECTED_OUTPUTS_PLACEHOLDER

### Determinism Check
- DETERMINISM_CHECK_PLACEHOLDER

### Known Limits
- KNOWN_LIMITS_PLACEHOLDER

## Examiner Quick-Start (5-Minute Flow Placeholder)
1. Setup: SETUP_PLACEHOLDER
2. Run: RUN_PLACEHOLDER
3. Verify: VERIFY_PLACEHOLDER
4. Inspect: INSPECT_PLACEHOLDER
5. Troubleshoot references: TROUBLESHOOT_PLACEHOLDER

## Scope Guardrails (Placeholder)
- Exclude scratch artifacts by default.
- Exclude __pycache__ folders.
- Exclude superseded archives unless explicitly cited as evidence.
- Do not duplicate full run tables when baseline authority already exists.

## Thesis Traceability Map (Placeholder)
| Research Objective or RQ | Stage Evidence | Output Artifact | Report Chapter Reference |
| --- | --- | --- | --- |
| RQ_PLACEHOLDER | STAGE_EVIDENCE_PLACEHOLDER | ARTIFACT_PLACEHOLDER | CHAPTER_REF_PLACEHOLDER |

## Final Checklist (Pass/Fail Placeholder)
- [ ] BL-013 orchestration pass evidence attached
- [ ] BL-014 sanity pass evidence attached
- [ ] Active baseline chain citation attached
- [ ] Submission manifest completeness confirmed
- [ ] Required docs and quickstart included

## Notes
This file is intentionally placeholder-only in this pass.
A subsequent fill pass should replace placeholders with final paths and commands without changing section structure.
