# BL-003 Alignment

## Purpose
Align Spotify interaction evidence to DS-001 candidate tracks and produce seed-table artifacts.

## Inputs
- DS-001 candidate dataset CSV
- BL-001/BL-002 export artifacts
- Optional run-config via `BL_RUN_CONFIG_PATH`

## Outputs
- `outputs/bl003_ds001_spotify_seed_table.csv`
- Alignment trace and summary JSON artifacts

## Run
- `python bl003_alignment/build_bl003_ds001_spotify_seed_table.py --help`

## Validation
- Check match-rate and matched/unmatched counts in BL-003 summary.
