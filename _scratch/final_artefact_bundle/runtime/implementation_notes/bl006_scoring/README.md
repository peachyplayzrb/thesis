# BL-006 Scoring

## Purpose
Score filtered candidates using the hybrid semantic plus numeric scoring model.

## Inputs
- BL-004 profile
- BL-005 filtered candidates
- Scoring weights and thresholds from run-config

## Outputs
- `outputs/bl006_scored_candidates.csv`
- `outputs/bl006_score_summary.json`

## Run
- `python bl006_scoring/build_bl006_scored_candidates.py`

## Validation
- Confirm score summary totals and component contribution fields are populated.
