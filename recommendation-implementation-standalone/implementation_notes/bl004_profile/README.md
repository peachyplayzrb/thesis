# BL-004 Profile

## Purpose
Build a deterministic user preference profile from aligned seed interactions.

## Inputs
- BL-003 seed table and trace outputs
- Active run-config profile controls

## Outputs
- `outputs/bl004_preference_profile.json`
- `outputs/bl004_profile_summary.json`
- `outputs/bl004_seed_trace.csv`

## Run
- `python bl004_profile/build_bl004_preference_profile.py`

## Validation
- Confirm profile summary includes expected semantic and numeric feature centers.
