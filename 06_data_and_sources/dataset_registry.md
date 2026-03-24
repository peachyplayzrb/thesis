# Dataset Registry

## DS-001: Music4All / Music4All-Onion

- decision_log_ref: `D-001`, `D-015`
- status: fallback baseline with restored access path — provider has released download credentials and local download is in progress; licensing/provenance details still pending formal capture
- date_registered: 2026-03-12
- last_updated: 2026-03-24

### Description
Research-grade music dataset providing rich audio features and metadata for a large catalogue of tracks. Used as the canonical candidate corpus for preference profiling, candidate retrieval, and deterministic scoring in the thesis pipeline.

Music4All-Onion covers 109,269 tracks and 252,984,396 listening records from 119,140 Last.fm users. It extends the base Music4All dataset with 26 additional audio, video, and metadata features.

### Important Distinction
- Music4All (base) and Music4All-Onion are different dataset artifacts, not interchangeable names.
- Music4All-Onion is an extension package built around the Music4All ecosystem, but practical access paths, file inventories, and feature availability can differ from the original base release.
- Governance and implementation decisions must record which artifact is actually used in each run (base, Onion, or combined).

### Source
- Music4All base dataset: Santana et al. (2020), ICMR — separate Zenodo record (search "Music4All Santana" on zenodo.org)
- Music4All-Onion: Moscati et al. (2022), RecSys — zenodo.org/records/15394646 (use latest version / v2)
- Music4All A+A (Artist and Album Dataset): NOT required — no album-level or artist-level feature weighting exists in the current pipeline design.

### Access and Version Control Update (2026-03-24)
- Provider response status: positive reply confirmed and dataset sharing path reopened.
- Delivery state: provider has released download credentials; local download is currently running.
- Delivery artifact clarification: current delivery is base Music4All (normal), not Music4All-Onion.
- License/usage state: pre-access confidentiality terms were accepted; post-access usage constraints still need explicit capture in thesis records.
- Provisional corpus role: DS-001 remains fallback/reference while DS-002 stays active until DS-001 files are locally available, identified, and governance checks pass.

### Local Placement and Export Target (2026-03-24)
- Raw provider archive export target: `06_data_and_sources/music4all_raw/`.
- Keep the full provider archive intact in this folder before any extraction.
- Current provider package type: base Music4All (normal), not Onion.
- Official contact-page slide copy is stored at `10_resources/dataset_docs/music4all/music4all_slide.pdf`.
- Official contact-page paper copy is stored at `10_resources/papers/Pegoraro Santana et al. - 2020 - Music4All A New Music Database and Its Applications (contact-site copy).pdf`.
- Existing library paper copy remains at `10_resources/papers/Pegoraro Santana et al. - 2020 - Music4All A New Music Database and Its Applications.pdf`.
- Hash comparison result between the two paper copies: different SHA256 values (both retained for provenance traceability).

#### Version and Access Conditions Register
| Field | Value (current) | Action to close |
| --- | --- | --- |
| Access response received | Yes (2026-03-22; credentials released 2026-03-24) | Archive exact reply text/date in admin evidence note |
| Pre-access agreement required | Yes - disclosure/confidentiality agreement requested by provider | Completed and accepted for access release |
| Dataset release target | Music4All base dataset release (Santana et al., 2020) | Confirm exact delivered release/version from provider or archive listing |
| Credential delivery | Yes - download path/password released by provider | Record exact delivery channel and any expiry conditions |
| Base Music4All inclusion | Unknown | Confirm whether base metadata is included or separate |
| Permitted use | Conditioned on signed disclosure/confidentiality agreement; detailed usage terms still pending explicit capture | Extract and record allowed-use text from signed agreement and/or provider follow-up |
| Redistribution right | Unknown | Confirm if derived subset/artifacts can be shared in repo |
| Citation requirement | Expected mandatory | Capture exact required citation wording if supplied |
| Retention period/deletion duty | Unknown | Confirm any post-thesis retention constraints |

#### Reactivation Gate (DS-001 -> active)
DS-001 may be switched from fallback to active only when all of the following are true:
1. Dataset files are received and checksummed locally.
2. Exact dataset version/release is documented.
3. Usage/license constraints are explicitly recorded and compatible with thesis submission workflow.
4. A quick BL-019 compatibility check confirms schema-to-pipeline fit without destabilizing current BL-020 work.

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

### Status Update (2026-03-21)
- DS-001 is no longer the active corpus-planning path for BL-019.
- Keep DS-001 artifacts as historical baseline evidence and fallback reference only.
- Active planning strategy is now DS-002 per `D-015`.

## DS-002: MSD Subset + Last.fm Tags + MusicBrainz Mapping

- decision_log_ref: `D-008`, `D-015`, `D-016`
- status: complete — BL-019 dataset built and verified (9330 tracks, all quality gates pass, two-run determinism confirmed)
- date_registered: 2026-03-19
- last_updated: 2026-03-21

### Description
Integrated dataset strategy built from three linked research assets:
- Million Song Dataset subset (10,000 songs) for core metadata and audio descriptors
- Last.fm tag dataset for semantic annotations
- MusicBrainz mapping for external identifiers and cross-source linking

The intent is to create a smaller but more explicitly documented candidate corpus with deterministic joins through `track_id` and clearer control over the final schema.

Reference artifact:
- `06_data_and_sources/ds_002_msd_information_sheet.md`

### Confirmed Local Sources (2026-03-21 inspection)
- Million Song Dataset: http://millionsongdataset.com/
- Last.fm tags for MSD: http://millionsongdataset.com/lastfm/
- Local files confirmed in-repo:
	- `06_data_and_sources/track_metadata.db`
	- `06_data_and_sources/millionsongsubset.tar.gz`
	- `06_data_and_sources/lastfm_subset.zip`
	- `06_data_and_sources/unique_tracks.txt`
	- `06_data_and_sources/unique_artists.txt`

### Confirmed Field Availability (2026-03-21 inspection)
- `track_metadata.db` (`songs` table): `track_id`, `title`, `artist_name`, `artist_mbid`, `duration`, `year`, plus related metadata fields.
- MSD HDF5 `analysis/songs`: `track_id`, `tempo`, `loudness`, `key`, `mode`, `duration`.
- MSD HDF5 `metadata/songs`: `artist_name`, `title`, `release`, `artist_mbid`, `song_id`.
- Last.fm subset JSON: `track_id`, `artist`, `title`, `tags`, `similars`, `timestamp`.
- MusicBrainz-related helper data currently confirms `artist_mbid`, not a clean track-level MusicBrainz recording identifier.

### Current Working Final Fields
| Field | Role |
| --- | --- |
| `track_id` | canonical key |
| `artist_name` | metadata / fallback matching |
| `title` | metadata / fallback matching |
| `release` | metadata tie-break / traceability |
| `year` | metadata feature |
| `duration` | metadata feature |
| `tempo` | transparent audio feature |
| `loudness` | transparent audio feature |
| `key` | transparent audio feature |
| `mode` | transparent audio feature |
| `tags` | semantic explanation and similarity signal |
| `artist_mbid` | artist-level external identifier / optional enrichment |

### Strengths
- Clean three-source integration story that is easy to explain in Chapter 3.
- Direct use of well-known MIR research assets.
- Human-readable features and tags fit transparency and explanation goals.
- Lower schema breadth may reduce implementation sprawl.

### Risks And Open Questions
- The described plan uses the MSD subset (10,000 songs), which is much smaller than the current Music4All-Onion path and may reduce candidate diversity.
- The proposed field list is narrower than the current Onion-first plan and removes several already-inspected features now available locally.
- Spotify alignment cannot currently use ISRC as the primary DS-002 match key because the inspected candidate assets do not expose a confirmed corpus-side track-level ISRC field.
- MusicBrainz enrichment currently resolves only to `artist_mbid`; exact track-level MusicBrainz matching remains an open future enhancement rather than an available MVP field.
- MSD extraction is now technically available in the environment (`h5py` installed), but BL-019 still needs explicit implementation and join validation.
- A corpus switch would require synchronized updates across thesis-state, objectives, assumptions, limitations, and active chapter drafts.

### Review Gate
- Review update completed on 2026-03-21.
- Outcome: DS-002 is activated as the current BL-019 planning and implementation path.
- Reason: user-selected strategy update and alignment with explicit deterministic integration workflow requirements.
- Current handling decision: implement DS-002 joins and quality-gated dataset build as the active track; use metadata-first Spotify matching with duration/release tie-breaks and retain DS-001 as fallback baseline.

### Build Completion Record (2026-03-21)
- Builder script: `07_implementation/implementation_notes/data_layer/build_bl019_ds002_dataset.py`
- Join mode: intersection — only tracks present in all three sources (HDF5 ∩ SQLite ∩ Last.fm)
- Output rows: 9330 (670 of 10000 HDF5 tracks excluded — no Last.fm match)
- All quality gates: pass
- Determinism: confirmed (two identical runs, matching SHA256)
- Dataset SHA256: `b9c729a2b0fc1ab9e533ca5126402f4aff7c2b1ee8357a16e773a7837ad40b9f`
- Experiment log: `07_implementation/experiment_log.md` (EXP-016)
- Test note: `07_implementation/test_notes.md` (TC-DATASET-001)

### Spotify Ingestion Status (2026-03-21)
- BL-002 Spotify API exporter implementation is complete, but live authenticated export is currently blocked by provider-side long cooldown (`HTTP 429`) at endpoint `/me`.
- Latest observed cooldown evidence:
	- `retry_after_seconds=84882`
	- `retry_at_utc=2026-03-22T02:40:32Z`
	- blocker artifact: `07_implementation/implementation_notes/ingestion/outputs/spotify_api_export/spotify_rate_limit_block.json`
- Operational handling: fail fast when cooldown exceeds threshold (`--max-retry-after-seconds`) and retry after cooldown expiry or with rotated app credentials.

