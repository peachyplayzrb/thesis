# BL-009 Observability

## Purpose
Build run-level observability artifacts including diagnostics, config lineage, and artifact hashes.

## Inputs
- BL-004 through BL-008 stage outputs
- Optional canonical run-config artifacts from BL-013

## Outputs
- `outputs/bl009_run_observability_log.json`
- `outputs/bl009_run_index.csv`

## Run
- `python bl009_observability/build_bl009_observability_log.py`

## Validation
- Verify required log sections exist and artifact hash map includes expected outputs.
