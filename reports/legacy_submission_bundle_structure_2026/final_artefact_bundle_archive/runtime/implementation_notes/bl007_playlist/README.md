# BL-007 Playlist

## Purpose
Assemble final playlist tracks from scored candidates under explicit rule constraints.

## Inputs
- BL-006 scored candidates
- Assembly controls (target size, thresholds, genre constraints)

## Outputs
- `outputs/bl007_playlist.json`
- `outputs/bl007_assembly_trace.csv`
- `outputs/bl007_assembly_report.json`

## Run
- `python bl007_playlist/build_bl007_playlist.py`

## Validation
- Ensure playlist size meets target and constraint diagnostics indicate pass.
