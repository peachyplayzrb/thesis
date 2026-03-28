# BL-001/BL-002 Ingestion

## Purpose
Collect Spotify source data and normalize listening history into validated event artifacts used by downstream alignment.

## Inputs
- Spotify API credentials/environment for export scripts
- Raw listening history CSV for parser workflow

## Outputs
- Export artifacts under `outputs/spotify_api_export/`
- Normalized events and ingestion summaries

## Run
- Export path: `python bl001_bl002_ingestion/export_spotify_max_dataset.py`
- Parser path: `python bl001_bl002_ingestion/ingest_history_parser.py --help`

## Validation
- Ensure export summary exists and parser summary reports expected row counts and quality flags.
