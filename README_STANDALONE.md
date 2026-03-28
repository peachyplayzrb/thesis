# Recommendation System Implementation

**Standalone, reproducible implementation of a systematic playlist recommendation system.**

This package contains the complete, self-contained implementation of a music recommendation pipeline that generates personalized playlists based on Spotify user listening history and the Music4All dataset.

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

### 2. Prepare Dataset

Download the Music4All dataset and extract it. You'll need these CSV files in one directory:

- `id_information.csv` (track metadata: artist, song, album, release)
- `id_metadata.csv` (audio features: danceability, energy, valence, tempo, key, mode, etc.)
- `id_tags.csv` (collaborative tags)
- `id_genres.csv` (genre assignments)
- `id_lang.csv` (optional: language metadata)

**Example layout:**
```
/path/to/music4all/
  ├── id_information.csv
  ├── id_metadata.csv
  ├── id_tags.csv
  ├── id_genres.csv
  └── id_lang.csv
```

### 3. Run Pipeline

```bash
python main.py --dataset-root /path/to/music4all/
```

With optional Spotify integration and validation:

```bash
# Set Spotify credentials (required for real user data from API)
export SPOTIPY_CLIENT_ID=your_spotify_client_id
export SPOTIPY_CLIENT_SECRET=your_spotify_client_secret

# Run pipeline with validation
python main.py --dataset-root /path/to/music4all/ --validate-only
```

## Features

This implementation includes:

- **BL-003**: Alignment — Aligns Spotify user history to Music4All dataset using ISRC matching
- **BL-004**: Profile — Builds deterministic user preference profile (semantic tags, genres, numeric audio features)
- **BL-005**: Retrieval — Filters candidate corpus using semantic and numeric controls
- **BL-006**: Scoring — Weights and scores candidates with hybrid component scoring
- **BL-007**: Playlist — Assembles final playlist with deterministic rule constraints
- **BL-008**: Transparency — Generates per-track explanation payloads (why each song was recommended)
- **BL-009**: Observability — Records decision logs and run-chain metadata
- **BL-010**: Reproducibility — Validates determinism and component testing
- **BL-011**: Controllability — Validates control path isolation
- **BL-014**: Quality — Sanity checks and system assertions

## Configuration

### Default Configuration

The pipeline uses a canonical baseline configuration (`run_config_ui013_tuning_v1f.json`):

```bash
# Default run (uses canonical config)
python main.py --dataset-root /path/to/music4all/

# Or explicitly specify:
python main.py --dataset-root /path/to/music4all/ \
  --run-config implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json
```

### Alternative Configurations

Other baseline profiles are available in `implementation_notes/bl000_run_config/configs/profiles/`:

- `run_config_ui013_tuning_v1a.json` through `v1f.json` (v1 baseline variants)
- `run_config_ui013_tuning_v2a.json` through `v2b.json` (v2 experimental variants)

```bash
python main.py --dataset-root /path/to/music4all/ \
  --run-config implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v2a.json
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

After running the pipeline, outputs are saved in `implementation_notes/bl*_*/outputs/`:

### Core Artifacts

- **BL-003**: `bl003_alignment/outputs/bl003_ds001_spotify_seed_table.csv` — Aligned seed tracks
- **BL-004**: `bl004_profile/outputs/bl004_preference_profile.json` — User preference profile
- **BL-005**: `bl005_retrieval/outputs/bl005_filtered_candidates.csv` — Filtered candidate set
- **BL-006**: `bl006_scoring/outputs/bl006_scored_candidates.csv` — Scored candidates
- **BL-007**: `bl007_playlist/outputs/bl007_playlist.json` — Final recommended playlist
- **BL-008**: `bl008_transparency/outputs/bl008_explanation_payloads.json` — Explanations per track
- **BL-009**: `bl009_observability/outputs/bl009_run_observability_log.json` — Decision log

### Validation Outputs

- **BL-010**: `bl010_reproducibility/outputs/bl010_reproducibility_report.json` — Determinism verification
- **BL-011**: `bl011_controllability/outputs/bl011_controllability_report.json` — Control path isolation
- **BL-014**: `bl014_quality/outputs/bl014_sanity_report.json` — Quality assertions

## Reproducibility

This implementation is **deterministic**:

- No randomness in algorithm logic
- Identical runs with same inputs produce identical outputs
- All scores and rankings are bit-for-bit reproducible
- Use `--refresh-seed` to re-align Spotify data on pipeline re-run

```bash
python main.py --dataset-root /path/to/music4all/ --refresh-seed
```

## Spotify Integration (Optional)

To use real Spotify user data:

1. Create a [Spotify Developer Application](https://developer.spotify.com/dashboard)
2. Get Client ID and Secret
3. Set environment variables:

```bash
export SPOTIPY_CLIENT_ID=your_client_id
export SPOTIPY_CLIENT_SECRET=your_secret
```

4. Run stages BL-001/BL-002 to export Spotify data (included in pipeline)

Or pre-provide Spotify export at: `implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/`

## Troubleshooting

### Missing dataset files

```
ERROR: Required dataset file missing: /path/to/music4all/id_information.csv
```

**Solution**: Verify all required CSV files are in the dataset-root directory.

### Spotify credential errors

```
ERROR: Spotify credentials not found (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
```

**Solution**: Set environment variables or provide pre-exported Spotify data.

### Path errors

```
ERROR: Cannot find implementation_notes directory at ...
```

**Solution**: Run `main.py` from the package root directory.

## System Requirements

- **Python**: 3.10 or later
- **RAM**: 4 GB minimum (8 GB recommended for full Music4All dataset)
- **Disk**: ~2 GB for Music4All dataset + outputs
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

For detailed information on each stage:

- See `implementation_notes/README.md` for implementation overview
- See `implementation_notes/<stage>/README.md` for stage-specific documentation
- See `implementation_notes/IMPLEMENTATION_CONTRACT.md` for I/O contracts
- Run `python main.py --help` for command-line options

## Support

For questions or issues:

1. Check `implementation_notes/CODEBASE_ISSUES_CURRENT.md` for known issues
2. Review test outputs from `--validate-only` mode
3. Check individual stage outputs for error messages

---

**Version**: 1.0
**Last Updated**: March 2026
**Compatibility**: Python 3.10+, Windows/macOS/Linux
