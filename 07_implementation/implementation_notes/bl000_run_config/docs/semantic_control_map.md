# Semantic Control-Layer Map

Schema version: run-config-v1
Document date: 2026-03-25
Purpose: stable, operator-facing map from semantic control groups to concrete run-config fields and stage implementations. Does not replace internal engineering naming; supplements it for thesis presentation and audit.

---

## Overview

The pipeline is controlled through a single JSON document (`configs/templates/run_config_template_v1.json`, schema `run-config-v1`). All stage scripts receive a resolved, validated copy of this document — either from an explicit file path passed as `BL_RUN_CONFIG_PATH` or from compiled defaults. No stage script holds its own separate configuration file.

Eight semantic control groups cover the full pipeline:

| Group | Semantic Name | run-config Section(s) | Primary Stage |
|---|---|---|---|
| 1 | Input Composition | `input_scope`, `interaction_scope`, `influence_tracks` | BL-003, BL-004 |
| 2 | Seed Gate | `seed_controls` | BL-003 |
| 3 | Profile Construction | `profile_controls` | BL-004 |
| 4 | Retrieval Filtering | `retrieval_controls` | BL-005 |
| 5 | Scoring | `scoring_controls` | BL-006 |
| 6 | Playlist Assembly | `assembly_controls` | BL-007 |
| 7 | Transparency | `transparency_controls` | BL-008 |
| 8 | Observability | `observability_controls` | BL-009 |

---

## Group 1 — Input Composition

**Semantic purpose:** Defines which Spotify data sources are included in the seed set and whether influence tracks participate in profile construction.

**run-config sections:** `input_scope`, `interaction_scope`, `influence_tracks`

**Fields:**

| Field | Type | Default | Effect |
|---|---|---|---|
| `input_scope.source_family` | string | `"spotify_api_export"` | Identifies the source adapter; currently fixed to the Spotify API export family |
| `input_scope.include_top_tracks` | bool | `true` | Includes top-played tracks per time range |
| `input_scope.top_time_ranges` | list[string] | `["short_term","medium_term","long_term"]` | Time horizons for top tracks; each adds a query window |
| `input_scope.include_saved_tracks` | bool | `true` | Includes tracks saved to the user library |
| `input_scope.saved_tracks_limit` | int or null | `null` (no cap) | Cap on saved tracks ingested |
| `input_scope.include_playlists` | bool | `true` | Includes tracks from user-owned playlists |
| `input_scope.playlists_limit` | int or null | `null` | Cap on number of playlists included |
| `input_scope.playlist_items_per_playlist_limit` | int or null | `null` | Cap on tracks per playlist |
| `input_scope.include_recently_played` | bool | `true` | Includes recently played history |
| `input_scope.recently_played_limit` | int | `50` | Maximum recently played events |
| `interaction_scope.include_interaction_types` | list[string] | `["history","influence"]` | Which interaction type labels are active |
| `influence_tracks.enabled` | bool | `true` | Whether influence tracks can participate in profile construction |
| `influence_tracks.track_ids` | list[string] | `[]` | Explicit track IDs designated as influence tracks |
| `influence_tracks.source` | string or null | `null` | Optional label for the source of influence track IDs |

**Consuming stages:**
- BL-003 (`07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`): applies source-scope filters and produces the enriched seed manifest; emits `bl003_source_scope_manifest.json`
- BL-004 (`build_bl004_preference_profile.py`): reads the seed manifest and splits tracks into history vs influence interaction types for weighted profile construction
- BL-009: records `execution_scope_summary.interaction_types_included`, `influence_tracks_included`, `history_track_count`, `influence_track_count`

**Resolver:** `resolve_input_scope_controls(run_config_path)` → `run_config_utils.py`

---

## Group 2 — Seed Gate

**Semantic purpose:** Controls seed-quality guardrails at BL-003 before profile construction proceeds.

**run-config section:** `seed_controls`

**Fields:**

| Field | Type | Default | Effect |
|---|---|---|---|
| `seed_controls.match_rate_min_threshold` | float | `0.0` | Minimum required matched-event rate for BL-003 (`matched / input_event_rows`) before allowing downstream stages |

**Consuming stage:** BL-003 (`07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`)

**Resolver:** `resolve_bl003_seed_controls(run_config_path)` → `run_config_utils.py`

---

## Group 3 — Profile Construction

**Semantic purpose:** Controls how many top tags, genres, and lead genres are retained when summarising the user's weighted preference profile.

**run-config section:** `profile_controls`

**Fields:**

| Field | Type | Default | Effect |
|---|---|---|---|
| `profile_controls.top_tag_limit` | int | `10` | Maximum DS-001 tag labels kept in the profile |
| `profile_controls.top_genre_limit` | int | `10` | Maximum genre labels kept in the profile |
| `profile_controls.top_lead_genre_limit` | int | `10` | Maximum lead-genre labels kept in the profile |

**Note:** Profile weighting is determined by interaction type (preference_weight = 1.0 per interaction event for history; configurable for influence). Aggregation method is fixed as weighted mean over numeric columns; genre/tag aggregation is sum(preference_weight).

**Consuming stage:** BL-004 (`build_bl004_preference_profile.py`)
Outputs: `bl004_preference_profile.json`, `bl004_profile_summary.json`, `bl004_seed_trace.csv`

**Resolver:** `resolve_bl004_controls(run_config_path)` → `run_config_utils.py`

---

## Group 4 — Retrieval Filtering

**Semantic purpose:** Controls the two-phase candidate filtering that decides which corpus tracks pass to scoring. Phase 1 is semantic tag/genre matching; Phase 2 is numeric proximity gating.

**run-config section:** `retrieval_controls`

**Fields:**

| Field | Type | Default | Effect |
|---|---|---|---|
| `retrieval_controls.profile_top_tag_limit` | int | `10` | How many profile tags are used as retrieval targets |
| `retrieval_controls.profile_top_genre_limit` | int | `8` | How many profile genres are used as retrieval targets |
| `retrieval_controls.profile_top_lead_genre_limit` | int | `6` | How many lead genres are used as retrieval targets |
| `retrieval_controls.semantic_strong_keep_score` | int | `2` | A track scoring this or above on semantic match is kept unconditionally |
| `retrieval_controls.semantic_min_keep_score` | int | `1` | Minimum semantic score before numeric gating applies |
| `retrieval_controls.numeric_support_min_pass` | int | `1` | Minimum number of numeric proximity tests a track must pass |
| `retrieval_controls.numeric_thresholds.tempo` | float | `20.0` | Maximum tempo difference (BPM) for numeric proximity pass |
| `retrieval_controls.numeric_thresholds.key` | float | `2.0` | Maximum key distance (semitones) for numeric proximity pass |
| `retrieval_controls.numeric_thresholds.mode` | float | `0.5` | Maximum mode distance for numeric proximity pass |
| `retrieval_controls.numeric_thresholds.duration_ms` | float | `45000.0` | Maximum duration difference (ms) for numeric proximity pass |

**Consuming stage:** BL-005 (`build_bl005_candidate_filter.py`)
Outputs: `bl005_filtered_candidates.csv`, `bl005_candidate_decisions.csv`, `bl005_candidate_diagnostics.json`

**Resolver:** `resolve_bl005_controls(run_config_path)` → `run_config_utils.py`

---

## Group 5 — Scoring

**Semantic purpose:** Controls the weighted multi-component scoring formula that ranks all candidates passing retrieval.

**run-config section:** `scoring_controls`

**Fields:**

| Field | Type | Default | Effect |
|---|---|---|---|
| `scoring_controls.component_weights.tempo` | float | `0.20` | Weight of tempo similarity in final score |
| `scoring_controls.component_weights.duration_ms` | float | `0.13` | Weight of duration similarity in final score |
| `scoring_controls.component_weights.key` | float | `0.13` | Weight of key similarity in final score |
| `scoring_controls.component_weights.mode` | float | `0.09` | Weight of mode similarity in final score |
| `scoring_controls.component_weights.lead_genre` | float | `0.17` | Weight of lead-genre match in final score |
| `scoring_controls.component_weights.genre_overlap` | float | `0.12` | Weight of genre set overlap in final score |
| `scoring_controls.component_weights.tag_overlap` | float | `0.16` | Weight of DS-001 tag set overlap in final score |
| `scoring_controls.numeric_thresholds.tempo` | float | `20.0` | Tolerance used to compute continuous numeric similarity during scoring |
| `scoring_controls.numeric_thresholds.key` | float | `2.0` | Tolerance for key similarity computation |
| `scoring_controls.numeric_thresholds.mode` | float | `0.5` | Tolerance for mode similarity computation |
| `scoring_controls.numeric_thresholds.duration_ms` | float | `45000.0` | Tolerance for duration similarity computation |

**Note:** Component weights must sum to 1.0. The numeric_thresholds here govern continuous similarity computation; the retrieval_controls.numeric_thresholds govern the Boolean pass/fail gate in BL-005. They share the same default values but are independently configurable.

**Consuming stage:** BL-006 (`build_bl006_scored_candidates.py`)
Outputs: `bl006_scored_candidates.csv`, `bl006_score_summary.json`

**Resolver:** `resolve_bl006_controls(run_config_path)` → `run_config_utils.py`

---

## Group 6 — Playlist Assembly

**Semantic purpose:** Controls the diversity and size constraints applied when selecting the final playlist from the scored candidate set.

**run-config section:** `assembly_controls`

**Fields:**

| Field | Type | Default | Effect |
|---|---|---|---|
| `assembly_controls.target_size` | int | `10` | Target number of tracks in the finished playlist |
| `assembly_controls.min_score_threshold` | float | `0.35` | Tracks scoring below this value are excluded before assembly |
| `assembly_controls.max_per_genre` | int | `4` | Maximum tracks from any single lead genre in the playlist |
| `assembly_controls.max_consecutive` | int | `2` | Maximum consecutive tracks with the same lead genre |

**Consuming stage:** BL-007 (`build_bl007_playlist.py`)
Outputs: `bl007_playlist.json`, `bl007_assembly_report.json`, `bl007_assembly_trace.csv`

**Resolver:** `resolve_bl007_controls(run_config_path)` → `run_config_utils.py`

---

## Group 7 — Transparency

**Semantic purpose:** Controls the depth of per-track explanations generated with the playlist.

**run-config section:** `transparency_controls`

**Fields:**

| Field | Type | Default | Effect |
|---|---|---|---|
| `transparency_controls.top_contributor_limit` | int | `3` | Number of top scoring components cited in each track's natural-language explanation |

**Consuming stage:** BL-008 (`build_bl008_explanation_payloads.py`)
Outputs: `bl008_explanation_payloads.json`, `bl008_explanation_summary.json`

**Resolver:** `resolve_bl008_controls(run_config_path)` → `run_config_utils.py`

---

## Group 8 — Observability

**Semantic purpose:** Controls the verbosity of diagnostic samples included in the observability audit log.

**run-config section:** `observability_controls`

**Fields:**

| Field | Type | Default | Effect |
|---|---|---|---|
| `observability_controls.diagnostic_sample_limit` | int | `5` | Maximum number of example rows included per diagnostic category in the BL-009 log |

**Consuming stage:** BL-009 (`build_bl009_observability_log.py`)
Outputs: `bl009_run_observability_log.json`, `bl009_run_index.csv`

**Resolver:** `resolve_bl009_controls(run_config_path)` → `run_config_utils.py`

---

## Resolver Entry Points (Engineering Reference)

All resolvers are in `run_config_utils.py`. Each function takes an optional `run_config_path` argument and returns a flat dict of coerced, validated controls ready for use by the consuming stage.

| Resolver | Group(s) covered | Called by |
|---|---|---|
| `resolve_input_scope_controls` | 1 | BL-003 |
| `resolve_bl003_seed_controls` | 2 | BL-003 |
| `resolve_bl004_controls` | 1, 3 | BL-004 |
| `resolve_bl005_controls` | 4 | BL-005 |
| `resolve_bl006_controls` | 5 | BL-006 |
| `resolve_bl007_controls` | 6 | BL-007 |
| `resolve_bl008_controls` | 7 | BL-008 |
| `resolve_bl009_controls` | 8 | BL-009 |
| `resolve_effective_run_config` | all | called internally by all resolvers |

---

## Artifact Lineage (Run Pair)

Every BL-013 orchestrated run emits a canonical artifact pair before any stage executes:

| Artifact | Schema version | Content |
|---|---|---|
| `bl000_run_config/outputs/run_intent_<timestamp>.json` | `run-intent-v1` | The requested configuration as provided (or implicit default if no run-config file was supplied) |
| `bl000_run_config/outputs/run_effective_config_<timestamp>.json` | `run-effective-config-v1` | The fully resolved, normalized configuration after all coercions and defaults are applied |

Both artifacts are linked from the BL-009 observability log under `run_config.canonical_config_artifacts` and `execution_scope_summary.canonical_config_artifact_pair_available`.

---

## Cross-Reference: Controllability Scenarios

The following controllability scenarios are documented in `07_implementation/implementation_notes/bl011_controllability/outputs/scenarios/` and each modifies one or more groups:

| Scenario | Groups modified |
|---|---|
| `baseline` | none (reference run at defaults) |
| `stricter_thresholds` | 3 (retrieval numeric thresholds tightened) |
| `looser_thresholds` | 3 (retrieval numeric thresholds relaxed) |
| `valence_weight_up` | 4 (component_weights — note: valence is not currently a scoring component; this scenario tests weight redistribution) |
| `no_influence_tracks` | 1 (influence_tracks.enabled = false) |
