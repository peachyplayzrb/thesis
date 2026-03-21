# Schema Notes

## BL-001 Ingestion Schema (MVP Draft)

### Scope
- One practical ingestion path for exported listening history.
- Normalized output supports downstream deterministic alignment using ISRC when available and metadata fallback when the active corpus does not expose candidate-side ISRC.

### Input File Assumption (Raw)
- Format: CSV
- One row per listening event.
- Raw columns expected from source export:
	- `track_name`
	- `artist_name`
	- `album_name` (optional)
	- `isrc` (optional but preferred)
	- `played_at` (timestamp)
	- `ms_played` (milliseconds)
	- `platform` (optional)

### Normalized Event Schema (Output)
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `event_id` | string | yes | Deterministic row identifier (for traceability). |
| `track_name` | string | yes | Raw track title after trim/normalization. |
| `artist_name` | string | yes | Primary artist string after trim/normalization. |
| `album_name` | string | no | Album title when available. |
| `isrc` | string | no | Uppercased ISRC if present and valid pattern. |
| `played_at` | string | yes | ISO-8601 timestamp in UTC when possible. |
| `ms_played` | integer | yes | Playback duration in milliseconds. |
| `source_platform` | string | yes | Ingestion source identifier (for provenance). |
| `ingest_run_id` | string | yes | Run-level ID linking all rows in one ingest. |
| `row_quality_flag` | string | yes | `ok`, `missing_isrc`, `missing_core_field`, `invalid_timestamp`, etc. |

### Validation Rules (MVP)
- Hard fail row if any core field is missing: `track_name`, `artist_name`, `played_at`, `ms_played`.
- Soft warning if `isrc` is missing; row remains usable for fallback matching.
- Convert `played_at` to ISO-8601 UTC where parseable; otherwise mark `invalid_timestamp`.
- Require `ms_played >= 0`; negative values are invalid.

### Example Mapping
| Raw Input | Normalized Output |
| --- | --- |
| `track_name=Blinding Lights` | `track_name=blinding lights` (normalized casing strategy to be finalized) |
| `artist_name=The Weeknd` | `artist_name=the weeknd` |
| `isrc=USUG11904298` | `isrc=USUG11904298` |
| `played_at=2025-11-21 23:16:02` | `played_at=2025-11-21T23:16:02Z` |
| `ms_played=184000` | `ms_played=184000` |

### Open Decisions
- Confirm canonical text normalization rule (lowercase vs preserve display form + normalized shadow columns).
- Confirm exact `source_platform` value taxonomy.
- Confirm whether partial listens below threshold are excluded at ingestion or later profiling stage.

## BL-003 Alignment Output Schema (MVP Draft)

### Inputs
- Normalized event JSONL from ingestion stage.
- Candidate corpus table containing at least: `candidate_track_id`, `track_name`, `artist_name`; for DS-002 also prefer `duration_seconds` and `release_name`; `candidate_isrc` is optional and may be absent.

### Matching Policy
- If the active corpus exposes a confirmed candidate-side ISRC field, primary matching may use ISRC exact match (`event.isrc` -> `candidate.candidate_isrc`).
- Current DS-002 handling: metadata-first exact match on normalized `(track_name, artist_name)` because inspected candidate sources do not expose a confirmed track-level ISRC field.
- Tie-break identical metadata matches with duration proximity first, then album/release comparison when available.
- Default behavior: skip hard-invalid rows flagged by ingestion (`missing_core_field`, `invalid_timestamp`, `invalid_ms_played`).

### Alignment Output Fields
| Field | Type | Description |
| --- | --- | --- |
| `event_id` | string | Original ingestion event identifier. |
| `ingest_run_id` | string | Run-level provenance link to ingestion output. |
| `candidate_track_id` | string | Candidate corpus track identifier when matched. |
| `matched_isrc` | string | Matched ISRC value when available. |
| `match_method` | string | `isrc`, `metadata`, `metadata_plus_duration`, or `none`. |
| `track_name` | string | Normalized track name used in matching. |
| `artist_name` | string | Normalized artist name used in matching. |
| `duration_delta_ms` | integer | Absolute duration difference when duration was used as a tie-break. |
| `row_quality_flag` | string | Ingestion quality flag passed through for traceability. |

### Alignment Summary Metrics
- `rows_total`
- `rows_considered`
- `rows_skipped_invalid`
- `matched_total`
- `matched_isrc`
- `matched_metadata`
- `matched_metadata_plus_duration`
- `unmatched`
- `match_rate`
- `alignment_output_hash`

## BL-016 Synthetic Pre-Aligned Asset Schema (Bootstrap)

### Purpose
- Provide deterministic bootstrap assets for BL-004 through BL-012 before real ingestion and alignment are reinstated.
- These assets are synthetic and pre-aligned by `track_id`, so they bypass BL-001 to BL-003 during Phase A.

### Synthetic Aligned Event JSONL
One row per synthetic preference signal for a single test user.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `event_id` | string | yes | Deterministic synthetic event identifier. |
| `user_id` | string | yes | Synthetic single-user identifier. |
| `track_id` | string | yes | Canonical Onion track identifier from BL-017 output. |
| `interaction_type` | string | yes | `history` or `influence`. |
| `signal_source` | string | yes | `synthetic_history` or `synthetic_influence`. |
| `interaction_count` | integer | yes | Synthetic interaction strength or imported count proxy. |
| `preference_weight` | float | yes | Deterministic weighting hint for BL-004 profile construction. |
| `seed_rank` | integer | yes | Deterministic ordering of synthetic seeds. |
| `lead_genre` | string | no | First genre surfaced from the candidate stub row. |
| `top_tag` | string | no | First tag surfaced from the candidate stub row. |

### Candidate Stub CSV
- The candidate stub CSV reuses the BL-017 canonical table schema so downstream stages can read the same feature columns later used by the full corpus.
- Expected columns are the canonical-layer output columns from `07_implementation/implementation_notes/data_layer/outputs/onion_canonical_track_table.csv`.
- Additional bootstrap selection metadata should be written to a separate manifest file, not appended to the candidate stub schema.

### Bootstrap Constraints
- All synthetic seed tracks must exist in the candidate stub.
- Prefer tracks with full source coverage (`has_user_track_counts=1`, `has_essentia=1`, `has_lyrics=1`, `has_tags=1`, `has_genres=1`).
- Keep the stub small enough for fast iteration, but large enough to include both preference-consistent and contrast candidates.

## BL-004 Preference Profile Artifact Schema (Bootstrap)

### Purpose
- Build a deterministic single-user preference profile from pre-aligned synthetic events and the BL-016 candidate stub.
- Produce one inspectable profile artifact that BL-005 and BL-006 can consume directly.

### Primary Profile JSON
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `run_id` | string | yes | Deterministic run identifier for the profile build. |
| `user_id` | string | yes | Synthetic or imported user identifier. |
| `input_artifacts` | object | yes | Paths and hashes for the aligned-event JSONL and candidate stub CSV. |
| `config` | object | yes | Explicit deterministic weighting and aggregation rules used in the run. |
| `diagnostics` | object | yes | Matched/missing event counts and total effective weight. |
| `seed_summary` | object | yes | Counts and weight totals by interaction type. |
| `numeric_feature_profile` | object | yes | Weighted means for selected numeric feature columns. |
| `semantic_profile` | object | yes | Top weighted tags and genres plus lead-genre distribution. |

### Summary JSON
- Smaller, citation-friendly overview of the same run.
- Should include the dominant genres/tags, selected numeric centers, matched seed count, and artifact paths.

### Seed Trace CSV
- One row per input seed after event-to-candidate join.
- Should include `event_id`, `track_id`, `interaction_type`, `preference_weight`, `effective_weight`, and compact semantic trace fields.

### Bootstrap Constraints
- BL-004 must not use randomness.
- The effective seed weighting rule must be explicit and stable.
- Missing track joins must be recorded in diagnostics even if the expected count is zero.

## BL-005 Candidate Retrieval And Filtering Artifact Schema (Bootstrap)

### Purpose
- Reduce the candidate pool to a smaller, profile-aligned set before deterministic scoring.
- Keep all filtering rules explicit so rejections and retentions are inspectable.

### Filtered Candidate CSV
- Reuses the BL-016 candidate stub schema for kept rows.
- Should contain only non-seed candidates retained by the BL-005 rules.

### Candidate Decision Trace CSV
One row per candidate considered by BL-005.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `track_id` | string | yes | Candidate identifier. |
| `is_seed_track` | integer | yes | `1` if the candidate was used in BL-004 seed construction. |
| `lead_genre` | string | no | Candidate lead genre from the stub. |
| `semantic_score` | integer | yes | Count of passed semantic overlap rules. |
| `numeric_pass_count` | integer | yes | Count of passed numeric closeness checks. |
| `decision` | string | yes | `keep` or `reject`. |
| `decision_reason` | string | yes | Human-readable reason summary. |

### Diagnostics JSON
- Must record candidate counts before and after filtering.
- Must record seed exclusions, semantic-rule hit counts, numeric-rule hit counts, and kept/rejected totals.
- Should include output hashes for replayability once the run completes.

### Bootstrap Constraints
- BL-005 must exclude seed tracks from the kept output.
- BL-005 must not use randomness.
- Filtering thresholds and keep rules must be explicit in the diagnostics artifact.

## BL-006 Deterministic Scoring Artifact Schema (Bootstrap)

### Purpose
- Score BL-005 filtered candidates against the BL-004 preference profile using explicit, reproducible component weights.
- Produce a ranked score breakdown table that BL-007 can consume directly.

### Scored Candidate CSV
One row per retained candidate from BL-005.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `rank` | integer | yes | Final deterministic rank after sorting by score desc then `track_id`. |
| `track_id` | string | yes | Candidate identifier. |
| `final_score` | float | yes | Weighted final score in $[0,1]$. |
| `*_similarity` | float | yes | Normalized component-level similarity for each scoring component. |
| `*_contribution` | float | yes | Weighted contribution of each component to the final score. |
| `lead_genre` | string | no | Candidate lead genre for traceability. |
| `matched_genres` | string | no | Overlapping profile genres surfaced during scoring. |
| `matched_tags` | string | no | Overlapping profile tags surfaced during scoring. |

### Score Summary JSON
- Must record component weights, input artifact hashes, candidate count, and top-ranked track ids.
- Should include top-score findings and min/max/mean score statistics.

### Bootstrap Constraints
- BL-006 must not use randomness.
- Component weights must sum to 1.
- Final ranking must be reproducible under fixed inputs.

---

## BL-007 Playlist Assembly Artifact Schema (Bootstrap)

### Purpose
- Apply deterministic rules to the BL-006 ranked candidates and assemble a fixed-length playlist.
- Produce a rule compliance trace and assembly report for transparency and thesis evidence.

### Assembly Rules (applied in greedy ranked-order traversal)
| Rule | ID | Condition |
| --- | --- | --- |
| Score threshold | R1 | skip if `final_score < min_score_threshold` |
| Genre cap | R2 | skip if `lead_genre` count in playlist has reached `max_per_genre` |
| Consecutive run | R3 | skip if the last `max_consecutive` playlist slots share this genre |
| Length cap | R4 | stop once `target_size` tracks have been added |

### Default Config (Bootstrap)
| Parameter | Value |
| --- | --- |
| `target_size` | 10 |
| `min_score_threshold` | 0.35 |
| `max_per_genre` | 4 |
| `max_consecutive` | 2 |

### Playlist JSON (`bl007_playlist.json`)
| Field | Type | Description |
| --- | --- | --- |
| `run_id` | string | Deterministic run identifier. |
| `generated_at_utc` | string | ISO-8601 timestamp. |
| `config` | object | Assembly rule parameters used. |
| `playlist_length` | integer | Number of tracks assembled. |
| `tracks` | array | Ordered playlist entries. |
| `tracks[].playlist_position` | integer | 1-based position in playlist. |
| `tracks[].track_id` | string | Candidate identifier. |
| `tracks[].lead_genre` | string | Lead genre for traceability. |
| `tracks[].final_score` | float | BL-006 scoring score. |
| `tracks[].score_rank` | integer | Original BL-006 rank. |

### Assembly Trace CSV (`bl007_assembly_trace.csv`)
One row per BL-006 candidate.
| Field | Type | Description |
| --- | --- | --- |
| `score_rank` | integer | BL-006 rank. |
| `track_id` | string | Candidate identifier. |
| `lead_genre` | string | Lead genre. |
| `final_score` | float | BL-006 score. |
| `decision` | string | `included` or `excluded`. |
| `playlist_position` | integer or blank | Position if included. |
| `exclusion_reason` | string | e.g. `genre_cap_exceeded`, `consecutive_genre_run`, `below_score_threshold`, `length_cap_reached`. |

### Assembly Report JSON (`bl007_assembly_report.json`)
- Must record config, candidate counts, per-rule hit counts, playlist genre mix, score range, and artifact hashes.

### Bootstrap Constraints
- BL-007 must not use randomness.
- Rule evaluation order is fixed and deterministic.
- Final playlist must be reproducible under fixed inputs and config.

---

## BL-008 Transparency Output Schema (Bootstrap)

### Purpose
- Produce per-track explanation payloads for every track in the BL-007 playlist, derived directly from BL-006 scoring and BL-007 assembly artifacts.
- Provide both machine-readable component breakdowns and human-readable `why_selected` sentences.

### Explanation Payloads JSON (`bl008_explanation_payloads.json`)
One entry per playlist track.

| Field | Type | Description |
| --- | --- | --- |
| `playlist_position` | integer | 1-based position in the playlist. |
| `track_id` | string | Track identifier. |
| `lead_genre` | string | Lead genre for context. |
| `final_score` | float | BL-006 weighted score. |
| `score_rank` | integer | BL-006 rank before assembly rules. |
| `why_selected` | string | Human-readable explanation sentence. |
| `top_score_contributors` | array | Top 3 components by weighted contribution (label, weight, similarity, contribution). |
| `score_breakdown` | array | All 9 scoring components with similarity and contribution values. |
| `assembly_context` | object | Assembly rule decision, admission label, and genre at position. |

### Explanation Summary JSON (`bl008_explanation_summary.json`)
- Must record run ID, track count, top-contributor distribution, input artifact hashes, and output artifact hash.

### Bootstrap Constraints
- BL-008 must not apply any new scoring or ranking logic.
- All values must be derived directly from BL-006 and BL-007 artifacts.
- Output must be reproducible under fixed inputs.

---

## BL-009 Observability Log Schema (Bootstrap)

### Purpose
- Produce a single canonical run-level audit record covering the active bootstrap pipeline from BL-017 through BL-008.
- Make configuration, stage diagnostics, exclusions, artifact hashes, and deferred-stage status inspectable from one place.

### Primary Run Log JSON (`bl009_run_observability_log.json`)

#### Required Top-Level Sections
| Field | Type | Description |
| --- | --- | --- |
| `run_metadata` | object | BL-009 run id, timestamps, dataset/pipeline versions, bootstrap-mode flag, upstream run ids. |
| `run_config` | object | Stage-level config snapshot copied from BL-017, BL-016, BL-004, BL-005, BL-006, BL-007, BL-008 artifacts. |
| `ingestion_alignment_diagnostics` | object | Explicit status block for BL-001 to BL-003; must state whether these stages were executed or deferred. |
| `stage_diagnostics` | object | Per-stage diagnostic summary for data layer, bootstrap assets, profile, retrieval, scoring, assembly, transparency. |
| `exclusion_diagnostics` | object | Retrieval and assembly exclusion counts plus representative examples. |
| `output_artifacts` | object | Paths, hashes, and selected file sizes for primary and trace artifacts. |

#### `run_metadata`
| Field | Type | Description |
| --- | --- | --- |
| `run_id` | string | Deterministic BL-009 run identifier. |
| `task` | string | Must be `BL-009`. |
| `generated_at_utc` | string | ISO-8601 UTC timestamp. |
| `elapsed_seconds` | float | BL-009 generation time. |
| `observability_scope` | string | Human-readable statement of observability boundary. |
| `bootstrap_mode` | boolean | `true` when BL-001 to BL-003 are intentionally bypassed. |
| `dataset_version` | string | Deterministic combined hash of bootstrap input data components. |
| `pipeline_version` | string | Deterministic combined hash of participating pipeline scripts. |
| `dataset_component_hashes` | object | Hashes for the files used to derive `dataset_version`. |
| `pipeline_script_hashes` | object | Hashes for BL-016 to BL-009 scripts used to derive `pipeline_version`. |
| `upstream_stage_run_ids` | object | Run ids recorded by BL-004 through BL-008 artifacts. |

#### `ingestion_alignment_diagnostics`
- Must always be present.
- If BL-001 to BL-003 are deferred, record:
	- `stage_status=deferred_bootstrap_mode`
	- explicit reason
	- surrogate input paths
	- conceptual fields marked not applicable

#### `stage_diagnostics`
- `data_layer`: track universe, source counts, join intersections, availability counts
- `bootstrap_assets`: seed/candidate counts and selected synthetic ids
- `profile`: run id, diagnostics, seed summary, dominant tags/genres
- `retrieval`: counts, rule hits, top kept track ids
- `scoring`: counts, score statistics, top candidates
- `assembly`: counts, rule hits, genre mix, score range, playlist length
- `transparency`: run id, explanation count, top-contributor distribution

#### `exclusion_diagnostics`
- `retrieval`: seed exclusions, rejected non-seed count, sample rejected rows with reasons
- `assembly`: excluded track count, rule hits, first length-cap boundary, sample exclusions grouped by rule

#### `output_artifacts`
- `primary_outputs`: final playlist and explanation payloads
- `trace_outputs`: seed trace, candidate decisions, scored candidates, assembly trace
- `supporting_outputs`: data-layer coverage, bootstrap manifest, profile, diagnostics, summaries

### Run Index CSV (`bl009_run_index.csv`)
One row per BL-009 observability build.

| Field | Type | Description |
| --- | --- | --- |
| `run_id` | string | BL-009 run identifier. |
| `generated_at_utc` | string | UTC timestamp. |
| `dataset_version` | string | Combined bootstrap data hash. |
| `pipeline_version` | string | Combined pipeline script hash. |
| `bootstrap_mode` | integer | `1` for bootstrap mode, else `0`. |
| `profile_run_id` | string | BL-004 run id. |
| `retrieval_run_id` | string | BL-005 run id. |
| `scoring_run_id` | string | BL-006 run id. |
| `assembly_run_id` | string | BL-007 run id. |
| `transparency_run_id` | string | BL-008 run id. |
| `kept_candidates` | integer | BL-005 retained candidate count. |
| `candidates_scored` | integer | BL-006 scored candidate count. |
| `playlist_length` | integer | BL-007 playlist length. |
| `explanation_count` | integer | BL-008 explanation count. |
| `playlist_sha256` | string | Playlist hash for quick lookup. |
| `explanation_payloads_sha256` | string | Explanation-payload hash for quick lookup. |
| `observability_log_sha256` | string | Hash of the paired run log JSON. |

### Bootstrap Constraints
- BL-009 must not introduce new selection, scoring, or ranking logic.
- All recorded values must be derived from existing stage artifacts.
- The run log must always declare whether ingestion and alignment were executed or deferred.
- Required sections must be validated before final output is written.

