# BL-014 Quality

## Purpose
Run sanity and quality suites that validate schema, linkage, and freshness/reproducibility requirements.

## Inputs
- Active outputs from BL-003 through BL-013
- BL-010 and BL-011 outputs for freshness mode

## Outputs
- Sanity and quality reports under `outputs/`
- Run matrices and config snapshots

## Run
- `python bl014_quality/run_bl014_sanity_checks.py`
- `python bl014_quality/run_bl014_quality_suite.py --help`

## Validation
- Require full sanity pass and expected suite status for selected mode.
