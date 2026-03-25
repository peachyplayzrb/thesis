# Dataset Information Sheet — DS-001: Music4All Base (Raw)

## Deterministic Playlist Generation System (Thesis)

---

## 1. Purpose

This dataset acts as the primary candidate song corpus for the thesis pipeline. It provides track-level audio features, metadata, tags, genre labels, and a user listening history for use in preference profiling, candidate retrieval, and deterministic scoring.

**Version note:** This is the raw Music4All base release only — it is NOT the Onion-enriched version. The Music4All-Onion extension files (Moscati et al., 2022) are stored separately at `10_resources/datasets/music4all_onion/selected/` as `.tsv.bz2` archives but have NOT been merged with the base. They are available for future enrichment but are not part of the current working dataset.

The dataset was obtained directly from the Music4All research team via a request to contact4Music4All@gmail.com. The provider-delivered archive was placed at `06_data_and_sources/music4all_raw/` (excluded from version control).

---

## 2. Citation

> Igor André Pegoraro Santana, Fabio Pinhelli, Juliano Donini, Leonardo Catharin, Rafael Biazus Mangolin, Yandre Maldonado e Gomes da Costa, Valéria Delisandra Feltrim, and Marcos Aurélio Domingues. *Music4All: A New Music Database and its Applications*. In: 27th International Conference on Systems, Signals and Image Processing (IWSSIP 2020), Niterói, Brazil. pp. 399–404.

---

## 3. Dataset Overview

| Property | Value |
|---|---|
| Total tracks | 109,269 |
| Audio clips | 109,269 × 30-second MP3 files |
| Lyrics | 109,269 × plain text files |
| Listening history events | 5,109,592 |
| Delimiter in CSV files | Tab (`\t`) |
| Date received | 2026-03-24 |
| Archive placed at | `06_data_and_sources/music4all_raw/music4all/music4all/` |

---

## 4. File Inventory

### 4.1 `id_information.csv` — Core Track Identity

| Column | Type | Description |
|---|---|---|
| `id` | string | Unique Music4All track ID (e.g. `0009fFIM1eYThaPg`) |
| `artist` | string | Artist name |
| `song` | string | Track title |
| `album_name` | string | Album name |

- Rows: 109,269
- Primary key for all other CSV joins: `id`
- Sample: `0009fFIM1eYThaPg | Cheryl | Rain on Me | 3 Words`

---

### 4.2 `id_metadata.csv` — Spotify Audio Features

| Column | Type | Description |
|---|---|---|
| `id` | string | Music4All track ID (join key) |
| `spotify_id` | string | Spotify track URI/ID — enables direct Spotify API alignment |
| `popularity` | float | Spotify popularity score (0–100) |
| `release` | int | Release year |
| `danceability` | float | 0–1 danceability (Spotify) |
| `energy` | float | 0–1 energy level (Spotify) |
| `key` | float | Musical key (0–11) |
| `mode` | float | Major (1) or minor (0) |
| `valence` | float | 0–1 musical positivity (Spotify) |
| `tempo` | float | BPM |
| `duration_ms` | int | Track duration in milliseconds |

- Rows: 109,269
- **This is the primary scoring file** — all audio features used by the pipeline scoring stage are present here.
- Note: `acousticness`, `instrumentalness`, `loudness`, `speechiness` are NOT present — these are Spotify API features not included in this release.
- `spotify_id` enables direct alignment with user Spotify history without a fuzzy title/artist match.

---

### 4.3 `id_tags.csv` — User-Generated Tags

| Column | Type | Description |
|---|---|---|
| `id` | string | Music4All track ID |
| `tags` | string | Comma-separated list of Last.fm-style tags |

- Rows: 109,269
- Sample: `0009fFIM1eYThaPg | pop,british,female vocalists,dance,cheryl cole`
- Tags are unweighted comma-separated strings (unlike Onion's `id_tags_dict.tsv.bz2` which has explicit weights).
- Useful for explanation output and semantic similarity.

---

### 4.4 `id_genres.csv` — Genre Labels

| Column | Type | Description |
|---|---|---|
| `id` | string | Music4All track ID |
| `genres` | string | Comma-separated genre labels |

- Rows: 109,269
- Sample: `0009fFIM1eYThaPg | pop`
- Some tracks have multiple genres: `002Jyd0vN4HyCpqL | hard rock,rock,classic rock`
- Flat comma-separated string (not TF-IDF weighted like Onion's `id_genres_tf-idf.tsv.bz2`).

---

### 4.5 `id_lang.csv` — Lyrics Language

| Column | Type | Description |
|---|---|---|
| `id` | string | Music4All track ID |
| `lang` | string | ISO 639-1 language code (e.g. `en`, `pt`, `es`) |

- Rows: 109,269
- Useful for optional language-based filtering in candidate retrieval.

---

### 4.6 `listening_history.csv` — User Listening Events

| Column | Type | Description |
|---|---|---|
| `user` | string | Anonymised user ID (e.g. `user_007XIjOr`) |
| `song` | string | Music4All track ID |
| `timestamp` | string | ISO-format datetime (e.g. `2019-02-20 12:28`) |

- Rows: 5,109,592
- This is significantly smaller than Music4All-Onion's 252,984,396 listening records.
- The timestamp format `YYYY-MM-DD HH:MM` supports recency weighting.
- Supports both frequency-based and recency-based user preference profiling.

---

### 4.7 `audios/` — 30-Second MP3 Audio Clips

- 109,269 files, each named `<id>.mp3`
- 30-second clips of each track
- Not used by the current pipeline (feature-based scoring only, no raw audio processing)
- Excluded from version control via `.gitignore`

---

### 4.8 `lyrics/` — Lyrics Text Files

- 109,269 files, each named `<id>.txt`
- Plain text lyrics
- Not used in current pipeline but available for future lyrics-sentiment enrichment
- Excluded from version control via `.gitignore`

---

## 5. Comparison with DS-002 (MSD + Last.fm)

| Property | DS-001 Music4All Base | DS-002 MSD + Last.fm |
|---|---|---|
| Track count | 109,269 | 9,330 (intersection) |
| Audio features | Spotify-native (danceability, energy, valence, tempo, key, mode) | MSD HDF5 (tempo, loudness, key, mode) — different scale/source |
| Spotify ID | **Yes** — direct alignment possible | No — fuzzy title/artist match only |
| Tags | Comma-separated, unweighted | Last.fm JSON with weights |
| Genres | Comma-separated labels | Not a separate file |
| Listening history | 5.1M events | Not included |
| Coverage | Much wider candidate pool | Smaller, fully verified intersection |

---

## 6. Comparison with Music4All-Onion (separate extension, unmerged)

Music4All-Onion (Moscati et al., 2022, RecSys) is an extension of the Music4All ecosystem. The Onion `.tsv.bz2` files are locally available at `10_resources/datasets/music4all_onion/selected/` but have **not** been merged with the base. The current working dataset is raw base only. Using Onion features in the pipeline would require an explicit join on the shared track `id` key.

| Property | Music4All Base (this file) | Music4All-Onion |
|---|---|---|
| Track count | 109,269 | 109,269 |
| Audio features | Spotify-native (7 features) | Essentia (1035 columns) |
| Tags | Comma-separated, unweighted | Weighted dict `(tag, weight)` |
| Genres | Comma-separated labels | 686-column TF-IDF matrix |
| Listening history | 5.1M events | 252M events, 119k users |
| `spotify_id` | **Yes** | No |
| Lyrics sentiment | Not directly (raw lyrics only) | Yes — `id_lyrics_sentiment_functionals` (V/A/D/P stats) |

The base dataset has `spotify_id` for direct alignment and uses Spotify-native audio features that directly match the pipeline's scoring schema. However, it has fewer listening events and simpler (unweighted) tags and genres compared to Onion.

---

## 7. Pipeline Compatibility

### 7.1 Scoring Stage (BL-006)

Pipeline scoring uses: `danceability`, `energy`, `valence`, `tempo`, `key`, `mode`.

All six are present in `id_metadata.csv`. **Full compatibility.**

Missing from this dataset vs pipeline's optional features: `acousticness`, `instrumentalness`, `loudness`, `speechiness`. These should **not** be treated as a live Spotify enrichment dependency for this thesis, because Spotify audio-feature access is now externally constrained/deprecated in the current pipeline context. If these dimensions become necessary later, the realistic path is candidate-side enrichment from local datasets such as Music4All-Onion/Essentia rather than operational dependence on Spotify API backfill.

### 7.2 Alignment Stage (BL-003)

`id_metadata.csv` provides `spotify_id` — this enables direct Spotify ID matching rather than fuzzy title/artist fallback. **Significant improvement over DS-002.**

### 7.3 Preference Profiling (BL-004)

`listening_history.csv` provides `user`, `song`, `timestamp` — compatible with both frequency and recency weighting. **Fully compatible.**

### 7.4 Tags and Explanation (BL-008 / transparency)

`id_tags.csv` and `id_genres.csv` provide human-readable labels for explanation output. Tags are unweighted comma-separated (requires parsing). **Compatible with minor pre-processing.**

---

## 8. Known Gaps and Limitations

| Gap | Impact | Mitigation |
|---|---|---|
| Missing `acousticness`, `instrumentalness`, `loudness`, `speechiness` | Reduced scoring dimension vs full Spotify feature set | Use the available Music4All base features for MVP; if richer numeric coverage is later required, prefer local enrichment from Music4All-Onion/Essentia rather than live Spotify API backfill |
| Tags are unweighted | Cannot rank tags by importance directly | Treat all tags as equal weight, or use position/frequency heuristic |
| Genres are flat labels | Less nuanced than 686-column TF-IDF (Onion) | Suitable for simple genre filtering; Onion genres available if needed |
| Listening history is 5.1M events vs Onion's 252M | Smaller user pool, potentially less diverse for profiling | Sufficient for thesis MVP; Onion listener data available as supplement |
| `release` column is year only, not full date | Less precise recency weighting | Year-level granularity is sufficient for most scoring use cases |

---

## 8.1 Practical Spotify Retention Decision

The realistic role of Spotify in this thesis is **user-side evidence and cross-source identity**, not full candidate-side feature storage. DS-001 already holds most of the candidate-track metadata and numeric features needed for deterministic scoring. Spotify should therefore be retained only for the parts it uniquely contributes or materially improves.

| Spotify field group | Present in Spotify export/API | Already in DS-001 | Keep for thesis core? | Rationale |
|---|---|---|---|---|
| `track_id` / `track_uri` / `spotify_id` | Yes | Yes (`spotify_id`) | **Yes** | Primary cross-source identifier for linking user-side Spotify evidence to Music4All tracks |
| `isrc` | Yes | No | **Yes** | Best high-confidence linkage key when available; more robust than title/artist matching |
| `track_name`, `artist_names`, `album_name` | Yes | Yes | **Yes, but compactly** | Keep in normalized artifacts for traceability and match inspection; avoid treating Spotify as the canonical copy |
| `artist_ids`, `album_id` | Yes | No | Optional | Useful for audit/debug and possible future artist-level enrichment, but not required for core MVP scoring |
| `release_date`, `release_date_precision` | Yes | Partly (`release` year only) | **Yes** | Adds finer temporal provenance than DS-001's year-only field and supports better tie-break/audit logic |
| `duration_ms` | Yes | Yes | **Yes** | Useful for alignment sanity checks and duration tie-breaks even though DS-001 already includes it |
| `played_at`, `added_at`, playlist membership, `time_range`, rank, context | Yes | No | **Yes** | These are the main user-preference signals Spotify uniquely contributes |
| `popularity` | Yes | Yes | Optional | Duplicated by DS-001, volatile, and marked deprecated in Spotify docs; keep in raw export if desired, but do not depend on it as a core retained field |
| `explicit`, `is_playable`, `restriction_reason`, `linked_from_track_id` | Yes | No | Optional | Operational/debug metadata; useful for audit or market-availability analysis, not required for core recommendation logic |
| `preview_url`, `available_markets`, `href`, `external_url`, images | Yes/partly deprecated | No | No | Adds little value to the thesis pipeline and introduces policy/UI concerns rather than recommendation value |
| Artist genres/popularity/followers via artist endpoint | Yes (with extra calls; several fields deprecated) | DS-001 already has track genres/tags | Generally no | Extra API cost for coarser artist-level semantics that are weaker than local track-level genres/tags already present in Music4All |
| Audio features beyond DS-001 (`acousticness`, `instrumentalness`, `loudness`, `speechiness`, etc.) | Not a reliable live dependency in current pipeline context | No | No as Spotify dependency | Do not architect the thesis around Spotify numeric backfill; use local dataset enrichment instead if richer features are needed |

### Recommended Minimum Spotify Retained Schema

If the goal is to keep Spotify realistically and minimally, the retained thesis-core fields should be:

- Identity/alignment: `track_id`, `isrc`, `track_name`, `artist_names`, `album_name`, `release_date`, `release_date_precision`, `duration_ms`
- User evidence: `played_at`, `added_at`, `playlist_id`, `playlist_name`, `playlist_position`, `time_range`, `rank`, `context_type`, `context_uri`
- Provenance/debug: `source_type`, `source_run_id`, optionally `artist_ids` and `album_id`

Everything else is either already covered by DS-001, volatile/deprecated on the Spotify side, or operationally secondary for the thesis.

### Practical Thesis Rule

Use **Music4All as the canonical candidate corpus** and **Spotify as the user-profile and identity-resolution layer**. In other words:

- Keep Spotify for who the user listened to, saved, ranked, or placed in playlists
- Keep Spotify identifiers needed to align those interactions to Music4All
- Do **not** keep Spotify as a second full metadata warehouse when Music4All already provides the candidate-side features, tags, genres, and durations needed for the thesis

---

## 8.2 Ready-To-Use Dataset Subset

To make DS-001 immediately usable in the thesis pipeline, the practical approach is **not** to delete parts of the raw dataset. Instead, keep the raw provider folder intact as the provenance copy and define a smaller **working subset** for loading, joining, and scoring.

### Keep As Core Working Files

These are the files that should be treated as the active DS-001 working dataset:

| Keep | Why |
|---|---|
| `id_information.csv` | Canonical track identity: `id`, artist, song, album |
| `id_metadata.csv` | Core numeric scoring features plus `spotify_id` for exact Spotify alignment |
| `id_tags.csv` | Human-readable semantic tags for preference matching and explanations |
| `id_genres.csv` | Genre filtering, diversity control, and explanation support |
| `id_lang.csv` | Optional but lightweight and useful for language-aware filtering |

### Keep Only If Needed For Specific Analyses

| Keep conditionally | Why |
|---|---|
| `listening_history.csv` | Keep if you want dataset-side user-history experiments, recency/frequency profiling, or corpus-internal validation; otherwise it is not required for the Spotify-to-candidate recommendation path |
| Onion selected files in `10_resources/datasets/music4all_onion/selected/` | Keep if you plan richer local enrichment later (`id_essentia`, weighted tags, TF-IDF genres, lyrics sentiment, user counts) |

### Remove From Active Working Set

These should not be part of the default loaded pipeline dataset for the current thesis MVP:

| Remove from active working set | Why |
|---|---|
| `audios/` | Large storage cost; not used by the feature-based pipeline |
| `lyrics/` | Large storage cost; not used by the current pipeline |
| `readme.txt` | Keep for provenance, but not as a runtime data dependency |

"Remove" here means **exclude from the active processed dataset and joins**, not necessarily delete from disk. The safest practice is to preserve the raw folder unchanged and only omit these from the prepared working layer.

### Recommended Column-Level Keep List

If you build a single prepared table from the base files, keep these columns:

| Source file | Keep columns |
|---|---|
| `id_information.csv` | `id`, `artist`, `song`, `album_name` |
| `id_metadata.csv` | `id`, `spotify_id`, `release`, `duration_ms`, `popularity`, `danceability`, `energy`, `key`, `mode`, `valence`, `tempo` |
| `id_tags.csv` | `id`, `tags` |
| `id_genres.csv` | `id`, `genres` |
| `id_lang.csv` | `id`, `lang` |

### Recommended Column-Level Drop List

At the current thesis stage, there are no obvious redundant columns inside the base CSVs that need deletion. The reduction should happen mainly at the **file level**, not by trimming the already small column sets. The only practical omission is:

- Do not carry `listening_history.csv` into the default candidate table unless you explicitly need dataset-side user modeling

### Practical Prepared-Dataset Rule

For the thesis MVP, the ready-to-use DS-001 working layer should therefore be:

- Base identity: `id_information.csv`
- Base numeric features: `id_metadata.csv`
- Base semantics: `id_tags.csv`, `id_genres.csv`
- Optional language filter: `id_lang.csv`
- Exclude `audios/`, `lyrics/`, and dataset-side listening history from the default runtime candidate table
- Keep Onion files separate until you explicitly decide to enrich the base via a documented join on `id`

This gives you a compact, thesis-appropriate candidate dataset without losing raw provenance or blocking later enrichment.

---

## 8.3 Build Artifacts and Command

The DS-001 working-layer build assets are now present in the repository:

- Working schema spec: `06_data_and_sources/ds_001_prepared_working_schema.md`
- Build script: `07_implementation/implementation_notes/bl000_data_layer/build_ds001_working_dataset.py`
- DS-001 to Spotify join plan: `07_implementation/implementation_notes/bl003_alignment/ds001_spotify_join_plan.md`

Run command from repo root:

```powershell
".venv/Scripts/python.exe" "07_implementation/implementation_notes/bl000_data_layer/build_ds001_working_dataset.py"
```

Generated outputs:

- `07_implementation/implementation_notes/bl000_data_layer/outputs/ds001_working_candidate_dataset.csv`
- `07_implementation/implementation_notes/bl000_data_layer/outputs/ds001_working_candidate_dataset_manifest.json`

Latest run snapshot (2026-03-24):

- `rows_written=109269`
- `null_spotify_id_rows=0`

---

## 9. Local File Locations

| File | Local Path |
|---|---|
| Track identity | `06_data_and_sources/music4all_raw/music4all/music4all/id_information.csv` |
| Spotify features | `06_data_and_sources/music4all_raw/music4all/music4all/id_metadata.csv` |
| Tags | `06_data_and_sources/music4all_raw/music4all/music4all/id_tags.csv` |
| Genres | `06_data_and_sources/music4all_raw/music4all/music4all/id_genres.csv` |
| Language | `06_data_and_sources/music4all_raw/music4all/music4all/id_lang.csv` |
| Listening history | `06_data_and_sources/music4all_raw/music4all/music4all/listening_history.csv` |
| Audio clips | `06_data_and_sources/music4all_raw/music4all/music4all/audios/<id>.mp3` |
| Lyrics | `06_data_and_sources/music4all_raw/music4all/music4all/lyrics/<id>.txt` |
| Official readme | `06_data_and_sources/music4all_raw/music4all/music4all/readme.txt` |

All files in `06_data_and_sources/music4all_raw/` are excluded from version control (`.gitignore`). This sheet is tracked in its place as the provenance record.

---

## 10. Schema Inspection Date

Confirmed: 2026-03-24 via live inspection of extracted archive.
