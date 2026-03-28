# Submission Bundle Manifest (Standalone Surface)

## Include
- `final_artefact.py`
- `final_artefact/README.md`
- `final_artefact/requirements.txt`
- `final_artefact/config/default_config.json`
- `07_implementation/ACTIVE_BASELINE.md`
- `07_implementation/RUN_GUIDE.md`
- Runtime code required for BL-013 generation and BL-014 validation

## Exclude
- `_scratch/`
- `__pycache__/`
- `_deep_archive_march2026/`
- ad hoc run debris outside declared outputs

## Required Evidence
- BL-013 run id
- BL-014 run id
- sanity status summary
- deterministic hash summary reference

## Validation Gate
A bundle is valid when:
1. `final_artefact.py run --refresh-seed --validate-only` exits with code 0
2. BL-013 and BL-014 pass artifacts are generated
3. output and evidence locations match README documentation
