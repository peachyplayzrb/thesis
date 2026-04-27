# BL-010 Reproducibility

## Purpose
Replay BL-004 through BL-009 multiple times and compare stable artifact hashes for determinism.

## Inputs
- Current active outputs from BL-004 through BL-009
- Replay count and execution settings

## Outputs
- Reproducibility report and run matrix in `outputs/`
- Replay archive folders for each replay iteration

## Run
- `python bl010_reproducibility/run_bl010_reproducibility_check.py --help`

## Validation
- Require `deterministic_match=true` in BL-010 report.
