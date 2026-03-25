# DS-001 Prepared Working Schema

## Purpose

Define the compact, ready-to-use DS-001 working dataset for the thesis runtime pipeline.

This schema is derived from the raw Music4All base files and keeps only the fields required for candidate scoring, semantic filtering, explanation, and Spotify alignment.

## Source Files

- 06_data_and_sources/music4all_raw/music4all/music4all/id_information.csv
- 06_data_and_sources/music4all_raw/music4all/music4all/id_metadata.csv
- 06_data_and_sources/music4all_raw/music4all/music4all/id_tags.csv
- 06_data_and_sources/music4all_raw/music4all/music4all/id_genres.csv
- 06_data_and_sources/music4all_raw/music4all/music4all/id_lang.csv (optional)

## Join Key

- Primary key: id
- Join type: inner join on id across identity, metadata, tags, genres
- Language join: left join on id (optional)

## Output Table

Suggested output path:
- 07_implementation/implementation_notes/bl000_data_layer/outputs/ds001_working_candidate_dataset.csv

Columns:

| Column | Type | Required | Source | Notes |
|---|---|---|---|---|
| id | string | yes | id_information, id_metadata | Canonical Music4All track id |
| spotify_id | string | yes | id_metadata | Primary Spotify alignment key for DS-001 |
| artist | string | yes | id_information | Track artist |
| song | string | yes | id_information | Track title |
| album_name | string | no | id_information | Album text field |
| release | int | no | id_metadata | Year-level release |
| duration_ms | int | no | id_metadata | Track duration milliseconds |
| popularity | float | no | id_metadata | Duplicated with Spotify, kept for candidate scoring context |
| danceability | float | no | id_metadata | Core BL-006 numeric feature |
| energy | float | no | id_metadata | Core BL-006 numeric feature |
| key | int | no | id_metadata | Core BL-006 numeric feature |
| mode | int | no | id_metadata | Core BL-006 numeric feature |
| valence | float | no | id_metadata | Core BL-006 numeric feature |
| tempo | float | no | id_metadata | Core BL-006 numeric feature |
| tags | string | no | id_tags | Comma-separated semantic tags |
| genres | string | no | id_genres | Comma-separated genres |
| lang | string | no | id_lang | Optional language code |

## Excluded From Working Dataset

- audios/
- lyrics/
- listening_history.csv (unless explicitly needed for corpus-internal user experiments)

## Quality Checks

Minimum checks for prepared output:

- row_count > 100000
- duplicate id count = 0
- null spotify_id count is reported
- hash of output file is recorded in a manifest

## Alignment Note

For DS-001, Spotify alignment should be spotify_id/track_id exact-match first. ISRC can be used as a supplementary confidence key when available from Spotify exports, but DS-001 base does not include ISRC in id_metadata.csv.
