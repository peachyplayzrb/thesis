# Recommendation System Implementation

**Standalone, reproducible implementation of a systematic playlist recommendation system.**

This package contains the complete, self-contained implementation of a music recommendation pipeline that generates personalized playlists from embedded BL-002 Spotify export artifacts and an embedded DS-001 candidate dataset.

> **📝 Detailed setup and troubleshooting guidance is included in this README.**

## Quick Start

### 1. Extract and Setup

```bash
# Extract the package
unzip recommendation-implementation.zip
cd recommendation-implementation

# Create/activate Python virtual environment (Python 3.10+)
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Embedded Candidate Dataset

The submission package already includes the DS-001 working candidate dataset at `src/data_layer/outputs/ds001_working_candidate_dataset.csv`.

You do not need to supply the raw Music4All tables to run the packaged pipeline.

### 3. Run Pipeline

```bash
python main.py
```

Run with validation:

```bash
# Run pipeline with validation
python main.py --validate-only
```

The packaged run uses embedded inputs by default:

- DS-001 candidate dataset: `src/data_layer/outputs/ds001_working_candidate_dataset.csv`
- BL-002 Spotify export bundle: `src/ingestion/outputs/spotify_api_export/`

## Features

This implementation includes:

- **BL-003**: Alignment — Aligns Spotify user history to the embedded DS-001 candidate dataset using metadata/identifier matching with exact and optional fuzzy fallback paths
- **BL-004**: Profile — Builds deterministic user preference profile (semantic tags, genres, numeric audio features)
- **BL-005**: Retrieval — Filters candidate corpus using semantic and numeric controls
- **BL-006**: Scoring — Weights and scores candidates with hybrid component scoring
- **BL-007**: Playlist — Assembles final playlist with deterministic rule constraints
- **BL-008**: Transparency — Generates per-track explanation payloads (why each song was recommended)
- **BL-009**: Observability — Records decision logs and run-chain metadata
- **BL-010**: Reproducibility — Validates determinism and component testing
- **BL-011**: Controllability — Validates control path isolation
- **BL-014**: Quality — Sanity checks and system assertions

## Internal Layout

The operator-facing entrypoints remain stable, but the runtime code is now split into focused modules under `src/`:

- `src/orchestration/` keeps `main.py` as a thin BL-013 entrypoint over dedicated CLI, stage-runner, seed-freshness, and summary helpers.
- `src/controllability/` keeps `pipeline_runner.py` and `scenarios.py` as stable BL-011 entry surfaces while stage execution, pathing, and runtime-control resolution live in focused helper modules.
- `src/alignment/` now follows the same typed-stage architecture used by later stages: `models.py` contracts + `stage.py` orchestrator + thin wrapper `main.py`, with focused helpers for text matching, indexing, match-pipeline, writing, and validation.
- `src/profile/`, `src/retrieval/`, and `src/scoring/` follow a shared typed-stage structure (`models.py` contracts + `stage.py` orchestrator + thin wrapper `main.py`) so BL-004 to BL-006 remain API-compatible while reducing monolithic script logic.

Recent BL-003 alignment architecture updates:

- Introduced `AlignmentStage` orchestration shell (`src/alignment/stage.py`) and reduced `src/alignment/main.py` to a thin CLI wrapper.
- Added typed alignment run contracts (`AlignmentPaths`, `AlignmentSourceRows`, `AlignmentRunArtifacts`) in `src/alignment/models.py`.
- Migrated summary generation to a typed context contract (`AlignmentSummaryContext`) with a single context-based entrypoint in `src/alignment/writers.py`.
- Added stage and summary parity regression tests (`tests/test_alignment_stage.py`, `tests/test_alignment_summary_builder.py`).

This split preserves the existing package surface while reducing monolithic scripts and making control/runtime behavior easier to audit.

## Configuration

### Default Configuration

The pipeline uses a canonical baseline configuration (`run_config_ui013_tuning_v1f.json`):

```bash
# Default run (uses canonical config)
python main.py

# Or explicitly specify:
python main.py \
  --run-config config/profiles/run_config_ui013_tuning_v1f.json
```

### Alternative Configurations

Other baseline profiles are available in `config/profiles/`:

- `run_config_ui013_tuning_v1a.json` through `v1d.json` (historical v1 baseline variants)
- `run_config_ui013_tuning_v1e_hard_swing_influence.json` (historical v1 influence variant)
- `run_config_ui013_tuning_v2a_retrieval_tight.json` and `run_config_ui013_tuning_v2b_language_recency_gate.json` (v2 experimental variants)

```bash
python main.py \
  --run-config config/profiles/run_config_ui013_tuning_v2a_retrieval_tight.json
```

### Configuration Format

Configurations are JSON files with the schema:

```json
{
  "schema_version": "run-config-v1",
  "control_mode": {
    "validation_profile": "strict",
    "allow_threshold_decoupling": false,
    "allow_weight_auto_normalization": false
  },
  "input_scope": {
    "source_family": "spotify_api_export",
    "include_top_tracks": true,
    "top_time_ranges": ["short_term", "medium_term", "long_term"],
    "include_saved_tracks": true,
    "include_playlists": true,
    "include_recently_played": true
  },
  "profile_controls": {
    "top_tag_limit": 30,
    "top_genre_limit": 50,
    "top_lead_genre_limit": 10
  },
  "retrieval_controls": {
    "profile_top_tag_limit": 10,
    "profile_top_genre_limit": 8,
    "profile_top_lead_genre_limit": 6,
    "language_filter_enabled": true,
    "language_filter_codes": ["en"],
    "recency_years_min_offset": 8,
    "numeric_thresholds": {
      "danceability": 0.20,
      "energy": 0.20,
      "valence": 0.20,
      "tempo": 20.0,
      "key": 2.0,
      "mode": 0.5,
      "duration_ms": 45000.0,
      "release_year": 8.0
    }
  },
  "scoring_controls": {
    "component_weights": {
      "danceability": 0.10,
      "energy": 0.10,
      "valence": 0.10,
      "tempo": 0.05,
      "key": 0.05,
      "mode": 0.05,
      "duration_ms": 0.10,
      "release_year": 0.10,
      "genres": 0.15,
      "tags": 0.15
    },
    "numeric_thresholds": { }
  },
  "assembly_controls": {
    "target_size": 10,
    "min_score_threshold": 0.35,
    "max_per_genre": 4,
    "max_consecutive": 2
  }
}
```

## Outputs

After running the pipeline, outputs are saved in `src/*/outputs/`:

### Core Artifacts

- **Alignment**: `src/alignment/outputs/bl003_ds001_spotify_seed_table.csv` — Aligned seed tracks
- **Profile**: `src/profile/outputs/bl004_preference_profile.json` — User preference profile
- **Retrieval**: `src/retrieval/outputs/bl005_filtered_candidates.csv` — Filtered candidate set
- **Scoring**: `src/scoring/outputs/bl006_scored_candidates.csv` — Scored candidates
- **Playlist**: `src/playlist/outputs/playlist.json` — Final recommended playlist
- **Transparency**: `src/transparency/outputs/bl008_explanation_payloads.json` — Explanations per track
- **Observability**: `src/observability/outputs/bl009_run_observability_log.json` — Decision log

### Validation Outputs

- **Reproducibility**: `src/reproducibility/outputs/reproducibility_report.json` — Determinism verification
- **Controllability**: `src/controllability/outputs/controllability_report.json` — Control path isolation
- **Quality**: `src/quality/outputs/bl014_sanity_report.json` — Quality assertions

## Reproducibility

This implementation is **deterministic**:

- No randomness in algorithm logic
- Identical runs with same inputs produce identical outputs
- All scores and rankings are bit-for-bit reproducible
- The package entrypoint always refreshes BL-003 from the embedded DS-001 candidate dataset before downstream stages run

```bash
python main.py
```

## Spotify Integration (Optional)

The standalone package already includes a pre-exported BL-002 Spotify bundle at `src/ingestion/outputs/spotify_api_export/`, so credentials are not required for standard execution.

If you want to regenerate Spotify exports from live API data, set:

```bash
export SPOTIPY_CLIENT_ID=your_client_id
export SPOTIPY_CLIENT_SECRET=your_secret
```

Live-export behavior notes:

- Endpoint response caching is disabled for the ingestion runtime path.
- Token-cache persistence is disabled for the ingestion runtime path.
- Live export runs use a fresh OAuth flow each run.
- Playlist-item parsing uses an item-first policy and keeps track rows only (episodes and unavailable items are excluded).

## Troubleshooting

### Missing embedded dataset

```
ERROR: Cannot find embedded candidate dataset at .../src/data_layer/outputs/ds001_working_candidate_dataset.csv
```

**Solution**: Verify the packaged DS-001 dataset was extracted under `src/data_layer/outputs/`.

### Spotify credential errors

```
ERROR: Spotify credentials not found (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
```

**Solution**: For the packaged default run, verify the embedded export bundle exists at `src/ingestion/outputs/spotify_api_export/`. Set credentials only if you are regenerating exports from the live API.

### Path errors

```
ERROR: Cannot find src directory at ...
```

**Solution**: Run `main.py` from the package root directory.

## System Requirements

- **Python**: 3.10 or later
- **RAM**: 4 GB minimum
- **Disk**: package contents + outputs
- **Network**: Optional (for Spotify API, can work offline with pre-exported data)

## Citation

If you use this implementation in research, please cite:

```bibtex
@thesis{author2026recommendation,
  title={Systematic Playlist Recommendation with Transparency and Controllability},
  author={Author, A.},
  year={2026},
  school={University}
}
```

## License

This implementation is provided for academic and research purposes.

## Documentation

For detailed information:

- Review `src/` for the domain-organized pipeline packages
- Review `config/profiles/` for runnable baseline configurations
- Run `python main.py --help` for command-line options

## Support

For questions or issues:

1. Run `python test_standalone.py`
2. Review test outputs from `--validate-only` mode
3. Check individual stage outputs under `src/*/outputs/`

---

**Version**: 1.0
**Last Updated**: March 2026
**Compatibility**: Python 3.10+, Windows/macOS/Linux
