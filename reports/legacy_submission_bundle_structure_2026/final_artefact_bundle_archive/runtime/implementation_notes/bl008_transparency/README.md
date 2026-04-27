# BL-008 Transparency

## Purpose
Generate per-track explanation payloads from playlist and scoring components.

## Inputs
- BL-007 playlist outputs
- BL-006 scoring details and profile context

## Outputs
- `outputs/bl008_explanation_payloads.json`
- `outputs/bl008_explanation_summary.json`

## Run
- `python bl008_transparency/build_bl008_explanation_payloads.py`

## Validation
- Confirm explanation count equals playlist track count and top contributors are present.
