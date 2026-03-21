# Test Notes

## Test Case TC-001: Ingestion Schema Validation (MVP)

- Date: 2026-03-13
- Backlog link: `BL-001`, `BL-002`
- Purpose: Verify that raw listening-history export is transformed into the normalized ingestion schema and invalid rows are flagged.

### Inputs
- Dataset/sample: `sample_listening_history.csv` (to be added under implementation test assets).
- Config assumptions:
	- Required raw Spotify fields: `master_metadata_track_name`, `master_metadata_album_artist_name`, `ts`, `ms_played`
	- Optional raw fields: `master_metadata_album_album_name`, `platform`, `isrc` (if enriched)

### Expected Output
- Every valid row has all normalized required fields populated.
- Missing `isrc` rows are kept and flagged `missing_isrc`.
- Invalid timestamp rows are flagged `invalid_timestamp`.
- Summary metrics produced:
	- `rows_total`
	- `rows_valid`
	- `rows_invalid`
	- `rows_missing_isrc`

### Pass Criteria
- Parser completes without crash on mixed-quality input.
- Output schema matches `06_data_and_sources/schema_notes.md`.
- Validation summary metrics are emitted and internally consistent.

### Actual Result
- Status: pass
- Run evidence: `07_implementation/implementation_notes/ingestion/ingest_history_parser.py` + `07_implementation/implementation_notes/run_outputs/tc001_validation_summary.json`
- Observed metrics:
	- `ingest_run_id=BL002-INGEST-C87E2315871F`
	- `rows_total=7`
	- `rows_valid=4`
	- `rows_invalid=3`
	- `rows_missing_isrc=1`
	- `rows_by_quality_flag.ok=3`
	- `rows_by_quality_flag.missing_isrc=1`
	- `rows_by_quality_flag.missing_core_field=1`
	- `rows_by_quality_flag.invalid_timestamp=1`
	- `rows_by_quality_flag.invalid_ms_played=1`
	- `sha256.normalized_events=5BEF104D3350EBCADDA71D3EC08D9A06C3A9071E757474146950E87D18771B28`
	- `sha256.invalid_rows=53C3F73E31FFE78058B242A44EE802F4CE09EDEC77CCE8EFDF87D86982B527EC`

## Test Case TC-002: ISRC-First Alignment With Metadata Fallback

- Date: 2026-03-13
- Backlog link: `BL-003`
- Purpose: Verify deterministic alignment behavior where ISRC-first matching is used and metadata fallback covers events without ISRC.

### Inputs
- Normalized events:
	- `07_implementation/implementation_notes/run_outputs/tc001_normalized_events.jsonl`
- Candidate corpus sample:
	- `07_implementation/implementation_notes/test_assets/sample_music4all_candidates.csv`

### Expected Output
- Valid events are considered for alignment.
- Hard-invalid rows are skipped by default.
- ISRC matches are preferred when available.
- Metadata fallback can match missing-ISRC rows by normalized `track_name` + `artist_name`.

### Pass Criteria
- Alignment script executes without failure.
- Summary reports `matched_isrc` and `matched_fallback` counts.
- Deterministic repeat run yields same `alignment_output_hash`.

### Actual Result
- Status: pending (implementation deleted 2026-03-19 for clean restart; prior run logged in `experiment_log.md` EXP-002)
- Run evidence: n/a
- Observed metrics: n/a

## Test Case TC-BOOT-001: Synthetic Bootstrap Asset Validation

- Date: 2026-03-19
- Backlog link: `BL-016`
- Purpose: Verify that the synthetic pre-aligned assets are internally consistent and ready to drive BL-004 through BL-006.

### Inputs
- Synthetic aligned events:
	- `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`
- Candidate stub:
	- `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
- Manifest:
	- `07_implementation/implementation_notes/test_assets/bl016_asset_manifest.json`

### Expected Output
- JSONL contains exactly 11 synthetic events.
- Event mix is `8 history + 3 influence`.
- Every synthetic `track_id` exists in the candidate stub.
- Candidate stub contains both preference-aligned and contrast candidates.
- Selection rules are explicitly recorded in the manifest.

### Pass Criteria
- Asset counts match the manifest summary.
- No seed track is missing from candidate stub.
- Manifest includes the exact seed and candidate track lists.

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` EXP-005
- Observed metrics:
	- `aligned_event_count=11`
	- `history_count=8`
	- `influence_count=3`
	- `candidate_count=60`
	- `core_candidate_count=45`
	- `contrast_candidate_count=15`
	- `sha256.aligned_events=F22C31F512CB9DC1708858419923C46E8D65895CB582BFE019F869CF34333771`
	- `sha256.candidate_stub=66505924A3BC9A627122310B6C4108BD397F4DD3E5FF9924991977A4C9574678`

## Test Case TC-PROFILE-001: Deterministic Preference Profile Build

- Date: 2026-03-19
- Backlog link: `BL-004`
- Purpose: Verify that the synthetic aligned seeds can be joined to the candidate stub and converted into a stable user preference profile.

### Inputs
- Synthetic aligned events:
	- `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`
- Candidate stub:
	- `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
- Output directory:
	- `07_implementation/implementation_notes/profile/outputs/`

### Expected Output
- All 11 events match candidate rows.
- Profile JSON is generated with numeric and semantic aggregates.
- Seed trace contains one row per matched event.
- Dominant genres and tags align with the BL-016 seed design.

### Pass Criteria
- `matched_seed_count=11`
- `missing_seed_count=0`
- profile, summary, and seed-trace artifacts all exist
- output hashes recorded in `experiment_log.md`

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` EXP-006
- Observed metrics:
	- `events_total=11`
	- `matched_seed_count=11`
	- `missing_seed_count=0`
	- `total_effective_weight=16.0276`
	- `top_lead_genre_1=indie rock`
	- `top_lead_genre_2=alternative rock`
	- `top_lead_genre_3=indie pop`
	- `top_genre_1=indie rock`
	- `top_genre_2=indie pop`
	- `top_genre_3=rock`
	- `top_tag_1=indie`
	- `top_tag_2=alternative`
	- `top_tag_3=rock`
	- `feature_center.rhythm.bpm=117.84215`
	- `feature_center.V_mean=5.741829`
	- `feature_center.A_mean=4.278339`
	- `feature_center.D_mean=5.371368`
	- `sha256.profile=8C9747BF5CF8A4CAC5C900D2346C54E82D1E24E9CAAF3AD0ADE6794AFFA3D10E`
	- `sha256.summary=1685A266C61C68183DA6E97AAD1D571DC25DE3C2198496AC85A70C1CF68F29C7`
	- `sha256.seed_trace=C47D4FBC6F0D9CCDD33699AF2D62AA37368FE335883FFCE96CEACC1D0DA55584`

## Test Case TC-CAND-001: Candidate Retrieval And Filtering

- Date: 2026-03-19
- Backlog link: `BL-005`
- Purpose: Verify that the profile-driven retrieval stage excludes seed tracks, narrows the candidate set, and records per-candidate filter decisions.

### Inputs
- Preference profile:
	- `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
- Seed trace:
	- `07_implementation/implementation_notes/profile/outputs/bl004_seed_trace.csv`
- Candidate stub:
	- `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`

### Expected Output
- Seed tracks are excluded from retrieval output.
- Filtered candidate set is smaller than the original stub.
- Every candidate receives a decision trace row.
- Diagnostics artifact records rule thresholds and kept/rejected counts.

### Pass Criteria
- `seed_tracks_excluded=11`
- `kept_candidates < 60`
- decision trace contains 60 candidate rows plus header
- diagnostics file exists and includes rule counts

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` EXP-007
- Observed metrics:
	- `candidate_rows_total=60`
	- `seed_tracks_excluded=11`
	- `kept_candidates=42`
	- `rejected_non_seed_candidates=7`
	- `decision_trace_line_count=61`
	- `filtered_candidate_line_count=43`
	- `sha256.filtered_candidates=4C7341830731A285DBA71A7FDD34C983AD77A459B040A993A90880AA8F0971E1`
	- `sha256.candidate_decisions=F814C1EBED4E145B4AD94BCE37D9DA42BBD9399A08187DFB8D515BC7FA1D49D0`
	- `sha256.candidate_diagnostics=867402AE26522A723D237F5755D30F66AF0811DEA665DB6DE580D9268EDA4686`

## Test Case TC-SCORE-001: Deterministic Candidate Scoring

- Date: 2026-03-19
- Backlog link: `BL-006`
- Purpose: Verify that every BL-005 retained candidate receives a transparent weighted score and that the ranking reflects the BL-004 profile structure.

### Inputs
- Preference profile:
	- `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
- Filtered candidates:
	- `07_implementation/implementation_notes/retrieval/outputs/bl005_filtered_candidates.csv`
- Output directory:
	- `07_implementation/implementation_notes/scoring/outputs/`

### Expected Output
- All 42 BL-005 retained candidates are scored.
- Final scores include both numeric and semantic contribution columns.
- Summary artifact reports score distribution and top-ranked candidates.
- Highest-ranked rows should align with the indie-oriented profile established in BL-004.

### Pass Criteria
- `candidates_scored=42`
- scored CSV contains 42 candidate rows plus header
- summary JSON exists and records score statistics
- output hashes recorded in `experiment_log.md`

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` EXP-008
- Observed metrics:
	- `candidates_scored=42`
	- `scored_candidate_line_count=43`
	- `max_score=0.724318`
	- `min_score=0.20486`
	- `mean_score=0.490817`
	- `median_score=0.501178`
	- `top_candidate_1=jPv1Tj4Mgo4l2Oue|indie rock|0.724318`
	- `top_candidate_2=POdgTSLBnoFJaj2x|indie rock|0.702439`
	- `top_candidate_3=PvGcoMH6vGWBaoXh|indie rock|0.669177`
	- `top10_lead_genre_mix.indie_rock=9`
	- `top10_lead_genre_mix.indie_pop=1`
	- `sha256.scored_candidates=BF9AB8A4FE27596276F8B1868FC1246BCA4B04B6315DFBB6FEF673DDF53E1AA2`
	- `sha256.score_summary=64CF9165AFB670E40E450C363A7DB61BA188A682226C1A73B2957077AA6F2A51`

## Test Case TC-PLAYLIST-001: Rule-Based Playlist Assembly

- Date: 2026-03-19
- Backlog link: `BL-007`
- Purpose: Verify that the assembler produces a deterministic fixed-length playlist with enforced genre diversity and a complete per-candidate decision trace.

### Inputs
- Scored candidates:
	- `07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv`
- Output directory:
	- `07_implementation/implementation_notes/playlist/outputs/`

### Expected Output
- Playlist contains exactly `target_size=10` tracks.
- No single genre exceeds `max_per_genre=4` slots.
- No more than `max_consecutive=2` consecutive tracks share the same genre.
- Assembly trace contains one row for every BL-006 candidate.
- Assembly report records per-rule hit counts and artifact hashes.

### Pass Criteria
- `playlist_length=10`
- `max_genre_count <= 4`
- `consecutive_run_rule_respected=True`
- `trace_line_count=43` (header + 42)
- output hashes recorded in `experiment_log.md`

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` EXP-009
- Observed metrics:
	- `playlist_length=10`
	- `candidates_evaluated=42`
	- `tracks_excluded=32`
	- `R1_score_threshold_hits=0`
	- `R2_genre_cap_hits=5`
	- `R3_consecutive_run_hits=4`
	- `R4_length_cap_hits=23`
	- `playlist_genre_mix.indie_rock=4`
	- `playlist_genre_mix.indie_pop=2`
	- `playlist_genre_mix.alternative_rock=2`
	- `playlist_genre_mix.pop=1`
	- `playlist_genre_mix.folk=1`
	- `playlist_score_range.max=0.724318`
	- `playlist_score_range.min=0.510916`
	- `trace_line_count=43`
	- `sha256.playlist=8B53B03D23F241EB102AD48E98395C34140356BCE3640348F2AF4C7EC44009FB`
	- `sha256.trace=9F432BC31CCF158909F2488A2D3A85EB073E76FB562F924A1C51324B66C32193`
	- `sha256.report=9975141AF1C3E3A33D2298A07148E6584056588EE5CDD3884DA4C17B85DF2333`
- Full ordered playlist (10 tracks):
	- pos=1  | jPv1Tj4Mgo4l2Oue | indie rock       | final_score=0.724318 | score_rank=1
	- pos=2  | POdgTSLBnoFJaj2x | indie rock       | final_score=0.702439 | score_rank=2
	- pos=3  | yUa5uu5wFCGwl2PK | indie pop        | final_score=0.643423 | score_rank=7
	- pos=4  | j8qrlsfqWAPqzqD9 | indie rock       | final_score=0.631517 | score_rank=8
	- pos=5  | 8keAhBJumHlc8qe9 | indie rock       | final_score=0.606053 | score_rank=9
	- pos=6  | Nyb0YqqyaSvWThIG | indie pop        | final_score=0.592793 | score_rank=11
	- pos=7  | 0X9aluHlz6iKWBMR | alternative rock | final_score=0.559544 | score_rank=13
	- pos=8  | ql2191d6uNCVM932 | alternative rock | final_score=0.548263 | score_rank=15
	- pos=9  | 9ZtfD8gBZXonrJKX | pop              | final_score=0.51886  | score_rank=18
	- pos=10 | PZEgbQhTHMMrKRLv | folk             | final_score=0.510916 | score_rank=19
- R3 exclusion examples (consecutive-run block — score was high enough but genre already appeared twice in a row):
	- rank=3  PvGcoMH6vGWBaoXh indie rock 0.669177
	- rank=5  hn1Z3OcZ4HM3hcIi indie rock 0.655572
- R2 exclusion examples (genre cap — indie rock filled at 4 slots):
	- rank=10 xr1HkbplUycZcEZX indie rock 0.602369
	- rank=12 CiLFjUJvYWGmyr2d indie rock 0.583893
- R4 exclusion boundary: rank=20 (B7SJXdcP0HhDMyfm, indie rock, 0.507858) was first track cut by length cap
- script artifact path: `07_implementation/implementation_notes/playlist/build_bl007_playlist.py`

## Test Case TC-EXPLAIN-001: Transparency Explanation Payloads

- Date: 2026-03-19
- Backlog link: `BL-008`
- Purpose: Verify that every playlist track receives a complete, faithful explanation payload derived from BL-006 and BL-007 artifacts, with a human-readable selection sentence and a reconstructable score breakdown.

### Inputs
- Scored candidates:
	- `07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv`
- Playlist:
	- `07_implementation/implementation_notes/playlist/outputs/bl007_playlist.json`
- Assembly trace:
	- `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_trace.csv`
- Output directory:
	- `07_implementation/implementation_notes/transparency/outputs/`

### Expected Output
- One payload per playlist track (10 total).
- Each payload contains `why_selected`, `top_score_contributors` (3), `score_breakdown` (9 components), `assembly_context`.
- Score breakdown contributions sum to `final_score` for each track.
- Summary records top-contributor distribution and input artifact hashes.

### Pass Criteria
- `playlist_track_count=10`
- `score_breakdown_entry_count=9` per track
- contributions reconstructable to BL-006 final_score
- input hashes in summary match BL-006/BL-007 artifact hashes
- output hashes recorded in `experiment_log.md`

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` EXP-010
- Observed metrics:
	- `playlist_track_count=10`
	- `top_contributor_distribution.lead_genre_match=5`
	- `top_contributor_distribution.tag_overlap=2`
	- `top_contributor_distribution.valence=3`
- Spot-check pos=1 (`jPv1Tj4Mgo4l2Oue`):
	- `final_score=0.724318` matches BL-006 rank=1
	- `top_1=Lead genre match | similarity=1.0 | contribution=0.12`
	- `top_2=Valence | similarity=0.972885 | contribution=0.116746`
	- `top_3=Tag overlap | similarity=0.71644 | contribution=0.11463`
	- `assembly_context.admission_rule=Admitted on first evaluation`
	- `why_selected=Selected at playlist position 1 (score 0.7243) because it strongly matches the preference profile on Lead genre match, Valence, Tag overlap. Lead genre is 'indie rock'.`
- Observed file footprint:
	- `bl008_explanation_payloads.json=29200 bytes`
	- `bl008_explanation_summary.json=748 bytes`
	- `sha256.payloads=C9AA6D930D11295E458C6C5B516AE9FFDF8AD2136E6057AD8A181C1BC0B50F24`
	- `sha256.summary=49CAC879496E1AEEA4821BF97A5FE09FE30FC16DEDBA629E4DD3861A7D0A431E`
- script artifact path: `07_implementation/implementation_notes/transparency/build_bl008_explanation_payloads.py`

## Test Case TC-OBS-001: Run-Level Observability Logging

- Date: 2026-03-21
- Backlog link: `BL-009`
- Purpose: Verify that the bootstrap pipeline produces a complete run-level observability record linking stage configs, diagnostics, deferred-stage status, exclusions, and final artifact hashes.

### Inputs
- Data-layer coverage report:
	- `07_implementation/implementation_notes/data_layer/outputs/onion_join_coverage_report.json`
- Bootstrap manifest and inputs:
	- `07_implementation/implementation_notes/test_assets/bl016_asset_manifest.json`
	- `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`
	- `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
- Upstream stage outputs:
	- `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
	- `07_implementation/implementation_notes/retrieval/outputs/bl005_candidate_diagnostics.json`
	- `07_implementation/implementation_notes/scoring/outputs/bl006_score_summary.json`
	- `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_report.json`
	- `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_summary.json`
- Output directory:
	- `07_implementation/implementation_notes/observability/outputs/`

### Expected Output
- One canonical JSON run log with required top-level sections.
- One CSV run index row summarizing the observability build.
- Log explicitly states that BL-001 to BL-003 are deferred in bootstrap mode.
- Run index contains upstream run ids and hashes for the playlist, explanation payloads, and observability log.

### Pass Criteria
- required sections present in the JSON log
- `ingestion_alignment_diagnostics.stage_status=deferred_bootstrap_mode`
- `playlist_sha256` and `explanation_payloads_sha256` in the CSV index match BL-007 and BL-008 artifact hashes
- `observability_log_sha256` in the CSV index matches the actual log hash
- output hashes recorded in `experiment_log.md`

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` EXP-011
- Observed metrics:
	- `run_id=BL009-OBSERVE-20260320-232943`
	- `generated_at_utc=2026-03-20T23:29:43Z`
	- `bootstrap_mode=true`
	- `dataset_version=2648A3237AA62F9E4C667C93178D482A5ACCDA0461299472E4FC1697786A993B`
	- `pipeline_version=4863D9868F15E220FD329B8B68248E95C8A7DB689E9353D2E60218713541DD9F`
	- `upstream_run_count=5`
	- `kept_candidates=42`
	- `candidates_scored=42`
	- `playlist_length=10`
	- `explanation_count=10`
	- `retrieval.rejected_non_seed_candidates=7`
	- `assembly.tracks_excluded=32`
	- `bl009_run_observability_log.json=23069 bytes`
	- `bl009_run_index.csv=830 bytes`
	- `sha256.log=AD3C1E632EADA20696B0B26AE01D4971071C3A76F7560DCFF84970930E1B38C4`
	- `sha256.index=EC5D3D72B1DE5D483E7EAA3C614075FD5CD2994C5304DC60520BFB7390A01811`
- Spot-checks:
	- required sections present in `bl009_run_observability_log.json`
	- `ingestion_alignment_diagnostics.stage_status=deferred_bootstrap_mode`
	- CSV `playlist_sha256=8B53B03D23F241EB102AD48E98395C34140356BCE3640348F2AF4C7EC44009FB` matches BL-007
	- CSV `explanation_payloads_sha256=C9AA6D930D11295E458C6C5B516AE9FFDF8AD2136E6057AD8A181C1BC0B50F24` matches BL-008
	- CSV `observability_log_sha256` matches actual JSON log hash
- script artifact path: `07_implementation/implementation_notes/observability/build_bl009_observability_log.py`

## Test Case TC-REPRO-001: Bootstrap Pipeline Replay Determinism

- Date: 2026-03-21
- Backlog link: `BL-010`
- Purpose: Verify that identical bootstrap inputs and configuration produce identical stable outputs across three full replays of BL-004 through BL-009.

### Inputs
- Fixed input artifacts:
	- `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`
	- `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
	- `07_implementation/implementation_notes/test_assets/bl016_asset_manifest.json`
	- `07_implementation/implementation_notes/data_layer/outputs/onion_join_coverage_report.json`
- Config artifact:
	- `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_config_snapshot.json`
	- `config_hash=B259CD10A428DD8DC5CF2EA8255807D28B6E771BDEDC24C32733982A6D47386F`
- Replay runner:
	- `07_implementation/implementation_notes/reproducibility/run_bl010_reproducibility_check.py`

### Expected Output
- Three archived replay directories with BL-004 to BL-009 outputs.
- One final reproducibility report and one replay run matrix.
- Identical stable hashes for ranked candidates, playlist content, explanation content, and normalized observability content across all replays.
- Unique stage run ids for each replayed stage execution.

### Pass Criteria
- `deterministic_match=true` in the BL-010 report
- all three `ranked_output_hash` values match
- all three `playlist_output_hash` values match
- all three `explanation_output_hash` values match
- all three `observability_output_hash` values match
- playlist track-id order and explanation track-id order are identical across all replays
- stage run ids are unique across replays
- output hashes recorded in `experiment_log.md`

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` EXP-012
- Observed metrics:
	- `run_id=BL010-REPRO-20260320-233937`
	- `replay_count=3`
	- `deterministic_match=true`
	- `config_hash=B259CD10A428DD8DC5CF2EA8255807D28B6E771BDEDC24C32733982A6D47386F`
	- `ranked_output_hash=BF9AB8A4FE27596276F8B1868FC1246BCA4B04B6315DFBB6FEF673DDF53E1AA2`
	- `playlist_output_hash=589920D4EB9C862F010F9C516BF7199D187F82A88265ACCC0B26FFD03E85A651`
	- `explanation_output_hash=568D6099CF8D7B035B67309143EF783E54B102505909A0EE2D01E22ECF6B4161`
	- `observability_output_hash=FA765EFEAEB7A0B49AC3DF3DC87A4DF8504FCF866731AE1F6872820CB2CAC2E0`
	- `dataset_version=2648A3237AA62F9E4C667C93178D482A5ACCDA0461299472E4FC1697786A993B`
	- `pipeline_version=E622A5784035EAEA845636DFA9C9991A8096D39ECCE18D9DBFA071832158FCB8`
	- `unique_stage_run_ids=18`
	- `bl010_reproducibility_report.json=34044 bytes`
	- `bl010_reproducibility_run_matrix.csv=2929 bytes`
	- `bl010_reproducibility_config_snapshot.json=4743 bytes`
	- `sha256.report=E222B832E97CE1FA1C8EC2C76528C583E7CFFDBC301E1D849CB0522B7350678C`
	- `sha256.run_matrix=2458924F133CE1363FB8D9BD95448402650D160339F39FDE732F18682BB6B594`
	- `sha256.config_snapshot=0A3737348AAE95960D52AF0671A62530A2CDAC3B148A75DDB2DBD8354315428F`
- Spot-checks:
	- replay matrix rows 1 to 3 have identical stable hashes for ranked, playlist, explanation, and observability outputs
	- replay matrix rows 1 to 3 have different raw hashes for `bl007_playlist.json`, `bl008_explanation_payloads.json`, and `bl009_run_observability_log.json`, which matches the report note about run-specific metadata volatility
	- archived replay directories exist for `replay_01`, `replay_02`, and `replay_03`
	- stage run ids are unique after the BL-004 to BL-009 run-id precision fix
- script artifact path: `07_implementation/implementation_notes/reproducibility/run_bl010_reproducibility_check.py`

## Reusable Evaluation Templates (Chapter 4)

Use these templates for consistent evidence capture across reproducibility, controllability, traceability, and rule-compliance tests.

### Template A: Reproducibility Replay Test

- `test_id`: `TC-REPRO-XXX`
- `date`: `YYYY-MM-DD`
- `purpose`: Verify identical outputs for identical inputs/config.
- `input_artifacts`:
	- `input_history_path:`
	- `influence_tracks_path:`
	- `candidate_corpus_snapshot:`
- `config_artifact`:
	- `config_path:`
	- `config_hash:`
- `runs`:
	- `run_1_id:`
	- `run_2_id:`
	- `run_3_id:`
- `output_hashes`:
	- `ranked_output_hash_run1:`
	- `ranked_output_hash_run2:`
	- `playlist_output_hash_run1:`
	- `playlist_output_hash_run2:`
- `result`:
	- `deterministic_match:` `True/False`
	- `status:` `pass/fail`
- `notes`:
	- If fail, record first mismatch artifact and likely cause.

### Template B: Parameter Sensitivity Test

- `test_id`: `TC-SENS-XXX`
- `date`: `YYYY-MM-DD`
- `parameter_under_test:`
- `baseline_value:`
- `variant_values:`
	- `v1:`
	- `v2:`
- `fixed_controls`:
	- List all parameters held constant.
- `comparison_metrics`:
	- `top_k_overlap:`
	- `rank_shift_summary:`
	- `playlist_rule_effects:`
- `interpretation`:
	- `directionally_consistent_with_intent:` `True/False`
	- `status:` `pass/fail`
- `notes`:
	- Record non-intuitive shifts and suspected mechanism-level cause.

### Template C: Explanation Fidelity Check

- `test_id`: `TC-EXPL-XXX`
- `date`: `YYYY-MM-DD`
- `sample_tracks_checked:`
	- `track_1_id:`
	- `track_2_id:`
	- `track_3_id:`
- `verification_fields`:
	- `raw_feature_values_present:` `True/False`
	- `feature_contributions_present:` `True/False`
	- `rule_adjustments_present:` `True/False`
	- `final_score_reconstructable:` `True/False`
- `reconstruction_error_tolerance:`
- `status:` `pass/fail`
- `notes`:
	- If fail, document which explanation field is missing or inconsistent.

### Template D: Playlist Rule-Compliance Check

- `test_id`: `TC-RULE-XXX`
- `date`: `YYYY-MM-DD`
- `playlist_id_or_run_id:`
- `configured_rules`:
	- `playlist_length:`
	- `artist_repeat_limit:`
	- `diversity_constraint:`
	- `ordering_constraint:`
- `observed_outcomes`:
	- `actual_playlist_length:`
	- `max_artist_repeats_observed:`
	- `diversity_signal_summary:`
	- `ordering_checks_summary:`
- `violations_detected:` `yes/no`
- `status:` `pass/fail`
- `notes`:
	- If fail, include violating track positions and rule IDs.

### Template E: Alignment Diagnostics Snapshot

- `test_id`: `TC-ALIGN-XXX`
- `date`: `YYYY-MM-DD`
- `events_total:`
- `events_considered:`
- `matched_isrc:`
- `matched_fallback:`
- `unmatched_count:`
- `unmatched_rate:`
- `known_causes`:
	- `missing_isrc_count:`
	- `metadata_conflict_count:`
- `status:` `pass/fail/bounded-risk`
- `notes`:
	- Track whether unmatched behavior stays within accepted MVP limitation bounds.

## Chapter 4 Execution Pack (From Evaluation Matrix EP-1)

Use these as the next priority run set. Keep artifacts under `07_implementation/implementation_notes/run_outputs/`.

## Test Case TC-003: Deterministic Replay (EP-REPRO-001)

- Purpose: Validate deterministic replay under fixed inputs and configuration.
- Inputs:
	- fixed normalized events artifact
	- fixed influence tracks artifact
	- fixed config profile (`config_hash` recorded)
- Procedure:
	1. Run pipeline three times with identical artifacts/config.
	2. Record ranked and playlist output hashes for each run.
	3. Compare run1/run2/run3 hashes.
- Expected:
	- all ranked hashes identical
	- all playlist hashes identical
- Pass criteria:
	- `ranked_output_hash_match=True`
	- `playlist_output_hash_match=True`

## Test Case TC-004: Explanation Fidelity Reconstruction (EP-EXPL-001)

- Purpose: Verify explanation payload is faithful to score traces.
- Inputs:
	- one completed run with score traces and explanation payloads
	- 5 sampled recommended tracks
- Procedure:
	1. Reconstruct final score from stored components for each sampled track.
	2. Compare reconstructed and reported final scores.
	3. Check mandatory explanation fields are present.
- Expected:
	- reconstruction error within tolerance
	- no missing mandatory fields
- Pass criteria:
	- `final_score_reconstructable=True`
	- `reconstruction_error <= defined_tolerance`

## Test Case TC-005: Influence Track Sensitivity (EP-CTRL-001)

- Purpose: Validate controllability through influence tracks.
- Baseline:
	- BL-010 fixed baseline with the three synthetic influence tracks included
- Variant:
	- remove the three synthetic influence tracks while keeping all other inputs and parameters fixed
- Procedure:
	1. Keep all non-target parameters fixed.
	2. Compare top-k overlap and rank shifts.
	3. Trace shifts to profile and score components.
- Pass criteria:
	- non-trivial, interpretable rank or composition shift
	- mechanism-level explanation available in traces
- Actual result:
	- `repeat_consistent=True` for both baseline and no-influence scenario
	- candidate pool changed from `42` to `47` (`delta=+5`)
	- top-10 overlap = `9/10`; playlist overlap = `7/10`
	- profile lead-genre summary shifted from `indie rock, alternative rock, indie pop, electronic, trip hop` to `indie rock, indie pop, electronic, trip hop, pop`
	- top-10 added track: `KxryDZFfi0mkMMiM`; removed track: `8keAhBJumHlc8qe9`
	- playlist added tracks: `xr1HkbplUycZcEZX`, `KxryDZFfi0mkMMiM`, `GB9LkV8pTLXCCvX6`
	- playlist removed tracks: `j8qrlsfqWAPqzqD9`, `0X9aluHlz6iKWBMR`, `ql2191d6uNCVM932`
	- mean absolute rank shift across common candidates = `2.619`
	- Result: pass. Influence-track removal produced a visible and explainable profile/ranking/playlist shift.
	- Run evidence: `07_implementation/experiment_log.md` `EXP-013`; archived scenario `07_implementation/implementation_notes/controllability/outputs/scenarios/no_influence_tracks/`

## Test Case TC-006: Feature Weight Sensitivity (EP-CTRL-002)

- Purpose: Validate controllability through feature-weight changes.
- Baseline:
	- default feature-weight profile
- Variants:
	- increase one selected feature weight
- Procedure:
	1. Hold all other parameters fixed.
	2. Compare score-component deltas and rank shifts.
	3. Confirm direction matches expected feature emphasis.
- Pass criteria:
	- observed score/rank effects are directionally consistent
	- effects are traceable in score components
- Actual result:
	- raw `V_mean` weight increased from `0.12` to `0.20`, then all scoring weights were renormalized to keep total weight = `1.0`
	- `repeat_consistent=True` for both baseline and `valence_weight_up` scenario
	- candidate pool stayed at `42`, but top-10 overlap dropped to `9/10`
	- top-10 added track: `Nyb0YqqyaSvWThIG`; removed track: `xr1HkbplUycZcEZX`
	- playlist overlap remained `10/10`, showing score/rank sensitivity without final playlist membership change under the current assembly rules
	- mean component delta for `V_mean` = `+0.038908`
	- mean absolute rank shift across common candidates = `1.048`
	- Result: pass. Raising valence emphasis increased valence contribution and changed score ordering in the expected direction.
	- Run evidence: `07_implementation/experiment_log.md` `EXP-013`; archived scenario `07_implementation/implementation_notes/controllability/outputs/scenarios/valence_weight_up/`

## Test Case TC-007: Candidate Threshold Sensitivity (EP-CTRL-003)

- Purpose: Validate controllability at candidate-generation stage.
- Variants:
	- stricter threshold
	- looser threshold
- Procedure:
	1. Compare candidate pool size across variants.
	2. Compare final playlist overlap with baseline.
	3. Check output changes remain interpretable.
- Pass criteria:
	- candidate pool size changes with threshold direction
	- downstream changes are explainable from diagnostics
- Actual result:
	- `repeat_consistent=True` for baseline, stricter, and looser threshold scenarios
	- stricter thresholds (`0.75x` baseline numeric thresholds) reduced the candidate pool from `42` to `40` (`delta=-2`) and produced a mean absolute rank shift of `0.25`
	- looser thresholds (`1.25x` baseline numeric thresholds) increased the candidate pool from `42` to `44` (`delta=+2`) and produced a mean absolute rank shift of `0.024`
	- top-10 overlap remained `10/10` and playlist overlap remained `10/10` for both threshold variants
	- Result: pass with bounded effect. Threshold direction changed the candidate pool exactly as expected, but downstream playlist membership stayed fixed under the current synthetic bootstrap candidate stub.
	- Run evidence: `07_implementation/experiment_log.md` `EXP-013`; archived scenarios `07_implementation/implementation_notes/controllability/outputs/scenarios/stricter_thresholds/` and `.../looser_thresholds/`

## Test Case TC-008: Playlist Rule Compliance (EP-RULE-001 / EP-RULE-002)

- Purpose: Validate playlist assembly constraints.
- Controls tested:
	- playlist length target
	- artist repetition limit
- Procedure:
	1. Run baseline and rule-variant configurations.
	2. Inspect rule logs and final playlists.
	3. Record any rule violations.
- Pass criteria:
	- actual length equals configured target
	- artist repeats do not exceed limit
	- if violated, explicit violation diagnostics exist

## Test Case TC-009: Observability Completeness (EP-OBS-001)

- Purpose: Validate required run-log schema completeness.
- Procedure:
	1. Execute one end-to-end run.
	2. Verify presence of required sections:
		- run metadata
		- run config
		- ingestion/alignment diagnostics
		- scoring traces
		- assembly diagnostics
		- final outputs
- Pass criteria:
	- all required sections present and linked by `run_id`

## Test Case TC-010: Alignment Path Visibility (EP-ALIGN-001)

- Purpose: Validate ISRC-first/fallback/unmatched reporting quality.
- Procedure:
	1. Execute alignment with mixed ISRC availability sample.
	2. Record `matched_isrc`, `matched_fallback`, and `unmatched_count`.
	3. Record unmatched reason categories.
- Pass criteria:
	- all match-path counts reported
	- unmatched reasons recorded for all unmatched entries

## Test Case TC-ENV-001: Python Environment Bootstrap Validation

- Date: 2026-03-21
- Backlog link: environment bootstrap / session closure
- Purpose: Verify that a new machine can create and reuse a repo-local Python environment using the tracked bootstrap assets.

### Inputs
- Requirements file:
	- `requirements.txt`
- Bootstrap assets:
	- `07_implementation/setup/bootstrap_python_environment.ps1`
	- `07_implementation/setup/bootstrap_python_environment.cmd`
	- `07_implementation/setup/python_environment_setup.md`

### Expected Output
- `.venv` exists under repository root.
- Required packages install in `.venv`.
- The bootstrap command completes from repo root without manual path edits.
- Import verification for `h5py`, `pypdf`, and `rapidfuzz` succeeds.

### Pass Criteria
- `workspace_python_type=venv`
- `required_imports_verified=yes`
- `bootstrap_command_verified=yes`

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` `EXP-020`
- Observed metrics:
	- `workspace_python_type=venv`
	- `workspace_python_version=3.14.3`
	- `pip_version=26.0.1`
	- `required_imports_verified=yes`
	- `bootstrap_command_verified=yes`

## Test Case TC-LIMIT-001: Limitation And Failure-Mode Traceability (BL-012)

- Date: 2026-03-21
- Backlog link: `BL-012`
- Purpose: Verify that thesis limitations are explicitly grounded in observed BL-010 and BL-011 outcomes and mirrored in both foundation and Chapter 5.

### Inputs
- Evidence sources:
	- `07_implementation/experiment_log.md` (`EXP-012`, `EXP-013`, `EXP-014`)
	- `07_implementation/test_notes.md` (`TC-REPRO-001`, `TC-005`, `TC-006`, `TC-007`)
	- `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_report.json`
	- `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_report.json`
- Target documentation artifacts:
	- `02_foundation/limitations.md`
	- `08_writing/chapter5.md`

### Expected Output
- `02_foundation/limitations.md` includes concrete limitations and failure modes observed in BL-010 and BL-011.
- `08_writing/chapter5.md` Section 5.4 reflects the same bounded interpretation logic.
- Chapter 5 future-work items are updated to target unresolved evidence gaps rather than already completed backlog work.

### Pass Criteria
- at least one BL-010-derived limitation is explicitly documented
- at least one BL-011-derived limitation is explicitly documented
- at least one observed failure mode is documented with mitigation context
- no contradiction between `02_foundation/limitations.md` and `08_writing/chapter5.md` limitation framing

### Actual Result
- Status: pass
- Run evidence: `07_implementation/experiment_log.md` `EXP-014`
- Observed checks:
	- BL-010-derived bound documented: semantic reproducibility vs raw metadata hash variability
	- BL-011-derived bound documented: threshold controls change candidate/rank layers but may not shift final playlist under bootstrap data
	- observed failure modes documented: run-id collision risk and volatile-metadata false instability in repeat checks
	- `02_foundation/limitations.md` and `08_writing/chapter5.md` Section 5.4 are aligned on scope and interpretation boundaries

## Test Case TC-DATASET-001: BL-019 DS-002 Dataset Build Determinism

- Date: 2026-03-21
- Backlog link: `BL-019`
- Purpose: Verify that the DS-002 integration build produces a stable, quality-gated candidate dataset from MSD subset + Last.fm tags + MusicBrainz (artist_mbid), and that identical runs yield identical output hashes.

### Inputs
- Builder script:
	- `07_implementation/implementation_notes/data_layer/build_bl019_ds002_dataset.py`
- Source data:
	- `06_data_and_sources/millionsongsubset.tar.gz` (10000 HDF5 files)
	- `06_data_and_sources/track_metadata.db` (1000000 rows, `songs` table)
	- `06_data_and_sources/lastfm_subset.zip` (9330 JSON records)
- Join mode: intersection — only tracks present in all three sources

### Expected Output
- CSV dataset with 17 columns (track_id, artist_name, title, release, year, duration, tempo, loudness, key, mode, tags_json, tag_count, artist_mbid, song_id, has_msd, has_lastfm, has_musicbrainz)
- JSON manifest with source hashes, join policy, output hashes
- Quality checks CSV with nine gate results
- Integration report JSON with coverage metrics and run diagnostics

### Pass Criteria
- `rows >= 8000`
- `metadata_coverage == 1.0`
- `lastfm_coverage == 1.0`
- All null rates `<= 0.01`
- SHA256 of dataset CSV identical between run 1 and run 2

### Actual Result
- Status: pass
- Run evidence: `07_implementation/experiment_log.md` `EXP-016`
- Observed metrics:
	- `rows=9330`
	- `tracks_excluded=670` (no Last.fm match)
	- `metadata_coverage=1.0`
	- `lastfm_coverage=1.0`
	- `musicbrainz_coverage=0.9359`
	- `duration_null_rate=0.0`
	- `tempo_null_rate=0.0`
	- `loudness_null_rate=0.0`
	- `key_null_rate=0.0`
	- `mode_null_rate=0.0`
	- `year_null_rate=0.0`
	- `elapsed_seconds=26.984`
	- `all_quality_gates_pass=true`
	- `run_1.csv_sha256=b9c729a2b0fc1ab9e533ca5126402f4aff7c2b1ee8357a16e773a7837ad40b9f`
	- `run_2.csv_sha256=b9c729a2b0fc1ab9e533ca5126402f4aff7c2b1ee8357a16e773a7837ad40b9f`
	- `hash_match=yes`

---

## Test Case TC-CLI-001: BL-013 Lightweight Entrypoint Repeatability

- Date: 2026-03-21
- Backlog link: `BL-013`
- Purpose: Verify that a single command can execute BL-004 through BL-009 in order, fail fast on stage error, and provide stable-hash evidence for deterministic repeat runs.

### Inputs
- Entrypoint script:
	- `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py`
- Command documentation:
	- `07_implementation/implementation_notes/entrypoint/bl013_run_command.md`
- Execution command:
	- `python 07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py`

### Expected Output
- Two successful orchestration summaries from repeated default runs.
- Each run executes all six stages (`BL-004` to `BL-009`) with `failed_stage_count=0`.
- Stable tracked artifact hashes match between run 1 and run 2.

### Pass Criteria
- `overall_status=pass` for both runs
- `executed_stage_count=6` and `failed_stage_count=0` for both runs
- all `stable_artifact_hashes` entries identical across both run summaries

### Actual Result
- Status: pass
- Run evidence: `07_implementation/experiment_log.md` `EXP-015`
- Observed metrics:
	- `run_1_id=BL013-ENTRYPOINT-20260321-000958-043140`
	- `run_2_id=BL013-ENTRYPOINT-20260321-001004-434656`
	- `run_1.executed_stage_count=6`
	- `run_2.executed_stage_count=6`
	- `run_1.failed_stage_count=0`
	- `run_2.failed_stage_count=0`
	- `stable_hash_match.bl004_seed_trace=yes`
	- `stable_hash_match.bl005_filtered_candidates=yes`
	- `stable_hash_match.bl005_candidate_decisions=yes`
	- `stable_hash_match.bl006_scored_candidates=yes`
	- `stable_hash_match.bl007_assembly_trace=yes`
	- `sha256.run_summary_1=56585FF293F39C088F0700ACA5B7573E4CF37A9399FBA0B04D24E34F127B1DD2`
	- `sha256.run_summary_2=E98D5B905546B3D31CC23A5E1E99BB40487FD4DAE36AD5E668F76730811B5CB7`

## Test Case TC-SPOTIFY-API-001: Spotify Web API Maximum Ingestion Export

- Date: 2026-03-21
- Backlog link: `BL-002`
- Purpose: Verify that the Spotify API ingestion exporter covers top tracks, saved tracks, playlists, and playlist items with OAuth, pagination, and request logging.

### Inputs
- Export script:
	- `07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py`
- Runbook:
	- `07_implementation/implementation_notes/ingestion/spotify_api_ingestion_runbook.md`
- Config:
	- scopes: `user-top-read user-library-read playlist-read-private playlist-read-collaborative user-read-private`
	- redirect URI: `http://127.0.0.1:8001/spotify/auth/callback`

### Expected Output
- OAuth authorization succeeds with requested scopes.
- Export artifacts are produced under `07_implementation/implementation_notes/ingestion/outputs/spotify_api_export/`.
- Summary includes endpoint counts and artifact hashes.

### Pass Criteria
- one successful end-to-end authenticated run
- non-zero results for at least one endpoint family
- run summary JSON and request log JSONL both present

### Actual Result
- Status: bounded-risk
- Run evidence:
	- `python -m py_compile 07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py` (pass)
	- `python 07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py --help` (pass)
	- `python 07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py --max-retry-after-seconds 120 --batch-size-top-tracks 25 --batch-size-saved-tracks 25 --batch-size-playlists 25 --batch-size-playlist-items 25 --batch-pause-ms 500 --min-request-interval-ms 700 --max-requests-per-minute 60 --max-retries 10` (authenticated run, blocked by provider cooldown)
- Observed metrics:
	- script syntax validation: pass
	- CLI contract validation: pass
	- authenticated API execution: blocked by `HTTP 429`
	- `path=/me`
	- `retry_after_seconds=84882`
	- `max_retry_after_seconds=120`
	- `retry_at_utc=2026-03-22T02:40:32Z`
	- block report artifact: `07_implementation/implementation_notes/ingestion/outputs/spotify_api_export/spotify_rate_limit_block.json`

### Updated Result (2026-03-21) — Status: pass
- All blockers resolved and full end-to-end live run completed successfully.
- Fixes applied before passing run:
	1. `spotify_env_template.ps1` reformatted with `$env:` prefix so credentials load correctly (C-059)
	2. Stale token cache cleared to force fresh OAuth flow
	3. 403 Forbidden crash on inaccessible playlists fixed (skip-and-continue pattern, C-060)
- Final run_id: `SPOTIFY-EXPORT-20260321-192533-881299`
- Observed metrics:
	- top_tracks_long_term: 5,104
	- top_tracks_medium_term: 3,021
	- top_tracks_short_term: 598
	- saved_tracks: 170
	- playlists: 4
	- playlist_items: 31 (one playlist skipped with 403)
	- elapsed_seconds: 46.711
	- cache_enabled: true
	- SQLite cache size: 18 MB (populated for fast reruns)
- Output artifacts verified with SHA256 in `spotify_export_run_summary.json`
- All pass criteria met: OAuth succeeded with full scopes; non-zero results for all endpoint families; run summary JSON and request log JSONL both present.

