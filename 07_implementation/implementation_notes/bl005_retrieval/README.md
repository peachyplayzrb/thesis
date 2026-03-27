# BL-005 Retrieval

## Purpose
Filter DS-001 candidates against BL-004 profile constraints to produce keep/reject decisions.

## Inputs
- BL-004 profile artifacts
- DS-001 candidate dataset
- Retrieval controls from run-config

## Outputs
- `outputs/bl005_filtered_candidates.csv`
- `outputs/bl005_candidate_decisions.csv`
- `outputs/bl005_candidate_diagnostics.json`

## Run
- `python bl005_retrieval/build_bl005_candidate_filter.py`

## Validation
- Verify kept-candidate count and decision reason distribution are sensible.
