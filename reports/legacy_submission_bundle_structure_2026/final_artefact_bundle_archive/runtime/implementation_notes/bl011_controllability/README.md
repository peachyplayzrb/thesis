# BL-011 Controllability

## Purpose
Evaluate controlled scenario variations and measure expected behavioral shifts across pipeline stages.

## Inputs
- BL-010 baseline snapshot context
- Active stage outputs and controllability runtime controls

## Outputs
- `outputs/bl011_controllability_report.json`
- Scenario run matrices and supporting artifacts in `outputs/`

## Run
- `python bl011_controllability/run_bl011_controllability_check.py --help`

## Validation
- Confirm controllability report status pass and scenario deltas are populated.
