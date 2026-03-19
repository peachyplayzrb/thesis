# Dataset Registry

## DS-001: Music4All / Music4All-Onion

- decision_log_ref: `D-001`
- status: accepted — primary candidate corpus
- date_registered: 2026-03-12

### Description
Research-grade music dataset providing rich audio features and metadata for a large catalogue of tracks. Used as the canonical candidate corpus for preference profiling, candidate retrieval, and deterministic scoring in the thesis pipeline.

### Source
- Music4All: Santana et al. (2020), ICMR
- Music4All-Onion: Moscati et al. (2022), RecSys

### Key Columns Expected
| Column | Type | Role |
| --- | --- | --- |
| `m4a_track_id` | string | Unique track identifier |
| `isrc` | string | ISRC for alignment matching |
| `track_name` | string | Track title |
| `artist_name` | string | Primary artist |
| `tempo` | float | BPM — scoring feature |
| `energy` | float | 0–1 energy level — scoring feature |
| `valence` | float | 0–1 positivity — scoring feature |
| `danceability` | float | 0–1 danceability — scoring feature |
| `loudness` | float | dB loudness — scoring feature |
| `acousticness` | float | 0–1 acoustic probability — scoring feature |
| `instrumentalness` | float | 0–1 instrumental probability — scoring feature |

### Access
- Location: to be placed at `10_resources/datasets/music4all/` once downloaded.
- Format: CSV (tracks metadata file + optional onion layer feature files).
- Download source: Zenodo / original dataset authors (see paper citations above).

### Notes
- The 4-row stub at `07_implementation/implementation_notes/test_assets/sample_music4all_candidates.csv` is a synthetic test asset only. It does not represent real Music4All data.
- Feature column names and normalisation ranges must be confirmed against the actual downloaded CSV before BL-004 and BL-006 are implemented.
- **This dataset must be available before BL-004 (preference profile) can run on real data.**

