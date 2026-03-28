# Submission Manifest

Last updated: 2026-03-28

## Intent
This manifest lists what is considered part of the active, submission-ready implementation package under `07_implementation/implementation_notes`.

## Included
- Active stage scripts BL-003 through BL-009
- Active orchestration BL-013
- Validation/evaluation harnesses BL-010, BL-011, BL-014
- Run-config system (`bl000_run_config`)
- Shared utilities (`bl000_shared_utils`)
- Standalone submission entry surface (`../final_artefact.py` and `../final_artefact/`)
- Current implementation health snapshot (`CODEBASE_ISSUES_CURRENT.md`)
- Canonical setup/run instructions (`../RUN_GUIDE.md`)
- Canonical baseline authority (`../ACTIVE_BASELINE.md`)
- Canonical submission package structure authority (`../ARTEFACT_SUBMISSION_STRUCTURE_FINAL.md`)
- Stage state logs listed in `README.md`

## Included Canonical Outputs
- Latest BL-007 playlist output(s)
- Latest BL-008 explanation output(s)
- Latest BL-009 observability output(s)
- Latest BL-014 verification output(s)

## Historical But Retained
- `_archive_cleanup_2026-03-26/` remains as historical evidence and is not part of the active runtime contract.

## Excluded From Runtime Contract
- `__pycache__/` folders
- Ad hoc scratch/test artifacts outside the active scripts listed in `README.md`

## Reproduction Entry Point
Primary command source of truth:
- `../RUN_GUIDE.md`

Executable orchestration entrypoint:
- `bl013_entrypoint/run_bl013_pipeline_entrypoint.py`

## Verification Requirement
A submission bundle is considered valid when BL-013 orchestration completes and BL-014 sanity checks pass.
