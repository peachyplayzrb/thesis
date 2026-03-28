# BL-005 Retrieval

## Purpose
Filter DS-001 candidates against BL-004 profile constraints to produce keep/reject decisions.

This stage now supports optional language filtering and optional recency gating
as retrieval controls in addition to semantic and numeric proximity rules.

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
- When language filtering is enabled, verify `reject_language_filter` appears only
	for candidates outside the allowed language code set.
- When recency gating is enabled, verify `reject_recency_gate` and
	`release_year_distance` are populated as expected.
