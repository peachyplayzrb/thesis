# Dataset Registry

## DS-001: Music4All / Music4All-Onion

- decision_log_ref: `D-001`
- status: accepted — primary candidate corpus
- date_registered: 2026-03-12
- last_updated: 2026-03-19

### Description
Research-grade music dataset providing rich audio features and metadata for a large catalogue of tracks. Used as the canonical candidate corpus for preference profiling, candidate retrieval, and deterministic scoring in the thesis pipeline.

Music4All-Onion covers 109,269 tracks and 252,984,396 listening records from 119,140 Last.fm users. It extends the base Music4All dataset with 26 additional audio, video, and metadata features.

### Source
- Music4All base dataset: Santana et al. (2020), ICMR — separate Zenodo record (search "Music4All Santana" on zenodo.org)
- Music4All-Onion: Moscati et al. (2022), RecSys — zenodo.org/records/15394646 (use latest version / v2)
- Music4All A+A (Artist and Album Dataset): NOT required — no album-level or artist-level feature weighting exists in the current pipeline design.

### Access Status Update (2026-03-19)
- Base Music4All record is currently inaccessible in the user environment.
- Operational interpretation: the original `base + Onion` combined plan is redundant for the MVP while base access remains blocked.
- Active path: proceed with Onion-only canonical data layer using `track_id` as the join key and defer base-metadata-dependent enrichments.
- Next required implementation todo: `BL-017` in `07_implementation/backlog.md`.

### Extraction Strategy
- Do not fully extract `15394646.zip`.
- First inspect schemas in-place.
- Then selectively extract only files classified as `USE` or `INSPECT-FURTHER`.
- Do not extract files classified as `SKIP` unless a later design change requires them.

### Files to Extract First — USE (6 files from Onion + base metadata)

From Music4All-Onion (zenodo.org/records/15394646):
| File | Layer | Decision | Reason |
| --- | --- | --- | --- |
| `userid_trackid_timestamp.tsv.bz2` | Listening events | **USE** | Recency-weighted preference profiling (252M records, 119k users) |
| `userid_trackid_count.tsv.bz2` | Listening events | **USE** | Frequency-weighted preference profiling (50M entries) |
| `id_essentia.tsv.bz2` | Audio | **USE** | Real schema confirmed: 1035 named Essentia columns including interpretable fields like loudness/rhythm/tonal descriptors |
| `id_lyrics_sentiment_functionals.tsv.bz2` | EMD (lyrics) | **USE** | Valence, arousal, dominance per track from ANEW lexicon — transparent mood scoring |
| `id_tags_dict.tsv.bz2` | UGC | **USE** | Raw Last.fm tags with weights — human-readable, direct explanation material |
| `id_genres_tf-idf.tsv.bz2` | EGC | **USE** | Real schema confirmed: 686 named genre columns; interpretable for genre filtering and scoring |

From Music4All base dataset (Santana et al. 2020):
| File | Decision | Reason |
| --- | --- | --- |
| Base metadata file (e.g. `id_metadata.tsv`) | **USE** | track_name, artist_name, ISRC, tempo, energy, valence, danceability, loudness, acousticness, instrumentalness |

### Files to Extract Later — useful, but defer active use for now

| File(s) | Category | Current view |
| --- | --- | --- |
| `userid_trackid_timestamp.tsv.bz2` | Listening events | Reviewed and extracted. Simple 3-column schema (`user_id`, `track_id`, `timestamp`). Keep for later recency weighting once the count-based profile path is stable. |

### Files Reviewed But Not For Mainline Use — already checked, keep skipped

| File(s) | Category | Current view |
| --- | --- | --- |
| `id_gems.tsv.bz2` | Audio embedding | Reviewed and extracted. Only 9 numeric dimensions after `id`. Compact, but still opaque and not explanation-friendly. Do not use in the main thesis pipeline. |
| `id_musicnn.tsv.bz2` | Audio embedding | Reviewed and extracted. 50 numeric dimensions after `id`. Better suited to black-box similarity experiments than transparent scoring. Do not use in the main thesis pipeline. |

### Files Definitely Skip — do not extract for current thesis design

| File(s) | Category | Reason |
| --- | --- | --- |
| `id_blf_correlation`, `id_blf_deltaspectral`, `id_blf_logfluc`, `id_blf_spectral`, `id_blf_spectralcontrast`, `id_blf_vardeltaspectral` | Audio (BLF) | High-dimensional opaque spectral vectors — not explainable or controllable |
| `id_compare_audspec_stats`, `id_compare_f0_stats`, `id_compare_hnr_stats`, `id_compare_jitter_stats`, `id_compare_mfcc_stats`, `id_compare_pcm_stats`, `id_compare_shimmer_stats`, `id_compare_voice_stats` | Audio (ComParE) | Multi-dimensional OpenSMILE vectors — Essentia covers what is needed more transparently |
| `id_emobase_bow`, `id_emobase_f0_stats`, `id_emobase_lsp_stats`, `id_emobase_mfcc_stats`, `id_emobase_pcm_stats`, `id_emobase_voice_stats` | Audio (emobase) | Emotion audio vectors — opaque; sentiment_functionals covers mood more transparently |
| `id_ivec256`, `id_ivec512`, `id_ivec1024` | Audio (I-vector) | Audio fingerprints via factor analysis — black-box, not explainable |
| `id_mfcc_bow`, `id_mfcc_stats` | Audio (MFCC) | Timbral vectors — not interpretable in scoring context |
| `id_chroma_bow` | Audio (chroma) | Pitch BoAW — musical key already covered by Essentia as named value |
| `id_bert`, `id_maest`, `id_jukebox` | Deep embeddings | Real schema confirmed: pure numeric embedding matrices (769, 769, and 4801 fields including `id`) with no interpretable dimensions |
| `id_incp`, `id_resnet`, `id_vgg19` | DC (visual) | Deep vision embeddings from video frames — irrelevant to audio-first deterministic playlist pipeline |
| `processed_lyrics.tar.gz` | EMD (lyrics) | Raw text — use derived feature files instead |
| `id_lyrics_tf-idf`, `id_lyrics_word2vec` | EMD (lyrics) | High-dimensional text vectors — not explainable |
| `id_vad_bow` | EMD (lyrics) | VADER sentiment BoW — redundant with sentiment_functionals |
| `id_tags_tf-idf` | UGC | TF-IDF of tags loses interpretable weight scale — raw tag dict is better |
| `README.md` | Documentation | Read in-place from archive; no need to extract separately unless you want a local copy |

### Key Columns Expected (post-download mapping required)
| Column | Type | Source file | Role |
| --- | --- | --- | --- |
| `m4a_track_id` | string | base metadata | Unique track identifier |
| `isrc` | string | base metadata | ISRC for alignment matching |
| `track_name` | string | base metadata | Track title |
| `artist_name` | string | base metadata | Primary artist |
| `tempo` | float | base metadata | BPM — scoring feature |
| `energy` | float | base metadata | 0–1 energy level — scoring feature |
| `valence` | float | base metadata | 0–1 positivity — scoring feature |
| `danceability` | float | base metadata | 0–1 danceability — scoring feature |
| `loudness` | float | base metadata | dB loudness — scoring feature |
| `acousticness` | float | base metadata | 0–1 acoustic probability — scoring feature |
| `instrumentalness` | float | base metadata | 0–1 instrumental probability — scoring feature |
| Essentia columns (TBD) | float | id_essentia | BPM, key, mode, rhythm — confirm column names after download |
| `lyrics_valence`, `lyrics_arousal`, `lyrics_dominance` | float | id_lyrics_sentiment_functionals | Mood from lyrics (ANEW) — confirm column names after download |
| `tags` (dict) | dict | id_tags_dict | Human-readable Last.fm tags with weights |
| Genre columns (TBD) | float | id_genres_tf-idf | Named genre TF-IDF values — confirm coverage and column names |

### Real Schema Findings (2026-03-19 in-place ZIP inspection)
- `id_essentia.tsv.bz2` has 1035 tab-separated fields in the header row, all named.
- `id_lyrics_sentiment_functionals.tsv.bz2` has 65 fields and includes named V/A/D/P summary statistics such as `V_mean`, `A_mean`, `D_mean`.
- `id_tags_dict.tsv.bz2` has 2 columns: `id` and a raw `(tag, weight)` dictionary payload.
- `id_genres_tf-idf.tsv.bz2` has 686 columns with human-readable genre names.
- `userid_trackid_count.tsv.bz2` and `userid_trackid_timestamp.tsv.bz2` both have simple 3-column schemas.
- `id_gems.tsv.bz2`, `id_musicnn.tsv.bz2`, `id_bert.tsv.bz2`, `id_maest.tsv.bz2`, and `id_jukebox.tsv.bz2` use numeric column names only, which makes them embedding-style representations rather than interpretable features.

### First-Pass Columns To Use

From `userid_trackid_count.tsv.bz2`:
- `user_id`
- `track_id`
- `count`

From `userid_trackid_timestamp.tsv.bz2` later:
- `user_id`
- `track_id`
- `timestamp`

From `id_essentia.tsv.bz2` first-pass interpretable columns:
- `id`
- `lowlevel.average_loudness`
- `lowlevel.loudness_ebu128.integrated`
- `rhythm.danceability`
- `rhythm.bpm`
- `rhythm.onset_rate`
- `rhythm.beats_count`
- `rhythm.beats_loudness.mean`
- `lowlevel.spectral_energy.mean`
- `lowlevel.spectral_centroid.mean`
- `lowlevel.spectral_complexity.mean`
- `tonal.chords_changes_rate`
- `tonal.key_edma.strength`
- `tonal.key_krumhansl.strength`
- `tonal.key_temperley.strength`

From `id_lyrics_sentiment_functionals.tsv.bz2` first-pass interpretable columns:
- `id`
- `V_mean`
- `A_mean`
- `D_mean`
- `P_mean`
- `V_std`
- `A_std`
- `D_std`

From `id_tags_dict.tsv.bz2`:
- `id`
- `(tag, weight)`

From `id_genres_tf-idf.tsv.bz2`:
- `id`
- retain sparse named genre columns and surface only non-zero top genres per track

### Caveats
- `id_genres_tf-idf` and `id_tags_dict` track counts are not listed in README — coverage may be partial. Confirm after download.
- `id_essentia.tsv.bz2` column names differ from Spotify-style base names — mapping/renaming step required before BL-004/BL-006.
- `id_lyrics_sentiment_functionals` provides a second, independent valence signal (lyrics-derived) separate from the base metadata's Spotify-derived valence. These may disagree; note this in BL-006 scoring design.

### Notes
- The 4-row stub at `07_implementation/implementation_notes/test_assets/sample_music4all_candidates.csv` is a synthetic test asset only.
- **This dataset must be available before BL-004 (preference profile) can run on real data.**
- File selection rationale: all skipped files are either opaque high-dimensional vectors incompatible with the transparency and controllability design requirements, or visual/textual features irrelevant to the audio-based pipeline.

### Change Review Note (2026-03-19)
- DS-001 remains the accepted baseline.
- The review of `DS-002` is complete. Result: keep DS-001 active for MVP execution.
- Do not wait for base Music4All before proceeding. Treat base-only fields as optional future enrichments.

## DS-002: MSD Subset + Last.fm Tags + MusicBrainz Mapping

- decision_log_ref: `D-008`
- status: future reference / reviewed fallback only — not accepted as replacement corpus
- date_registered: 2026-03-19
- last_updated: 2026-03-19

### Description
Integrated dataset strategy built from three linked research assets:
- Million Song Dataset subset (10,000 songs) for core metadata and audio descriptors
- Last.fm tag dataset for semantic annotations
- MusicBrainz mapping for external identifiers and cross-source linking

The intent is to create a smaller but more explicitly documented candidate corpus with deterministic joins through `track_id` and clearer control over the final schema.

Reference artifact:
- `06_data_and_sources/ds_002_msd_information_sheet.md`

### Proposed Sources
- Million Song Dataset: http://millionsongdataset.com/
- Last.fm tags for MSD: http://millionsongdataset.com/lastfm/
- MusicBrainz mapping from MSD additional datasets

### Proposed Final Fields
| Field | Role |
| --- | --- |
| `track_id` | canonical key |
| `artist_name` | metadata / fallback matching |
| `title` | metadata / fallback matching |
| `year` | metadata feature |
| `duration` | metadata feature |
| `tempo` | transparent audio feature |
| `loudness` | transparent audio feature |
| `key` | transparent audio feature |
| `mode` | transparent audio feature |
| `tags` | semantic explanation and similarity signal |
| `mbid` | external identifier / enrichment aid |

### Strengths
- Clean three-source integration story that is easy to explain in Chapter 3.
- Direct use of well-known MIR research assets.
- Human-readable features and tags fit transparency and explanation goals.
- Lower schema breadth may reduce implementation sprawl.

### Risks And Open Questions
- The described plan uses the MSD subset (10,000 songs), which is much smaller than the current Music4All-Onion path and may reduce candidate diversity.
- The proposed field list is narrower than the current Onion-first plan and removes several already-inspected features now available locally.
- Spotify alignment may weaken because the current thesis plan is ISRC-first, while the proposed sheet lists ISRC only on the Spotify side and not as a confirmed corpus field.
- MSD extraction requires `.h5` parsing work and join validation that has not yet been implemented in this repository.
- A corpus switch would require synchronized updates across thesis-state, objectives, assumptions, limitations, and active chapter drafts.

### Review Gate
- Review completed on 2026-03-19.
- Outcome: DS-002 is retained as a documented fallback option only.
- Reason: the main blocker is unusable base-Music4All access, but Music4All-Onion already provides enough interpretable data to support MVP implementation with less rework than a corpus switch.
- Current handling decision: preserve this option as future work and do not spend active MVP implementation time on it now.

