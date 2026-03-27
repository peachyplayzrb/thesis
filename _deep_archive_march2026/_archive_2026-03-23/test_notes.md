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
- Run evidence: `07_implementation/implementation_notes/bl001_bl002_ingestion/ingest_history_parser.py` + `07_implementation/implementation_notes/run_outputs/tc001_validation_summary.json`
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
	- `07_implementation/implementation_notes/bl004_profile/outputs/`

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
	- `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json`
- Seed trace:
	- `07_implementation/implementation_notes/bl004_profile/outputs/bl004_seed_trace.csv`
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
	- `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json`
- Filtered candidates:
	- `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_filtered_candidates.csv`
- Output directory:
	- `07_implementation/implementation_notes/bl006_scoring/outputs/`

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
	- `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv`
- Output directory:
	- `07_implementation/implementation_notes/bl007_playlist/outputs/`

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
- script artifact path: `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`

## Test Case TC-EXPLAIN-001: Transparency Explanation Payloads

- Date: 2026-03-19
- Backlog link: `BL-008`
- Purpose: Verify that every playlist track receives a complete, faithful explanation payload derived from BL-006 and BL-007 artifacts, with a human-readable selection sentence and a reconstructable score breakdown.

### Inputs
- Scored candidates:
	- `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv`
- Playlist:
	- `07_implementation/implementation_notes/bl007_playlist/outputs/bl007_playlist.json`
- Assembly trace:
	- `07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_trace.csv`
- Output directory:
	- `07_implementation/implementation_notes/bl008_transparency/outputs/`

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
- script artifact path: `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`

## Test Case TC-OBS-001: Run-Level Observability Logging

- Date: 2026-03-21
- Backlog link: `BL-009`
- Purpose: Verify that the bootstrap pipeline produces a complete run-level observability record linking stage configs, diagnostics, deferred-stage status, exclusions, and final artifact hashes.

### Inputs
- Data-layer coverage report:
	- `07_implementation/implementation_notes/bl000_data_layer/outputs/onion_join_coverage_report.json`
- Bootstrap manifest and inputs:
	- `07_implementation/implementation_notes/test_assets/bl016_asset_manifest.json`
	- `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`
	- `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
- Upstream stage outputs:
	- `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json`
	- `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_diagnostics.json`
	- `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json`
	- `07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_report.json`
	- `07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_summary.json`
- Output directory:
	- `07_implementation/implementation_notes/bl009_observability/outputs/`

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
- script artifact path: `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`

## Test Case TC-REPRO-001: Bootstrap Pipeline Replay Determinism

- Date: 2026-03-21
- Backlog link: `BL-010`
- Purpose: Verify that identical bootstrap inputs and configuration produce identical stable outputs across three full replays of BL-004 through BL-009.

### Inputs
- Fixed input artifacts:
	- `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`
	- `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
	- `07_implementation/implementation_notes/test_assets/bl016_asset_manifest.json`
	- `07_implementation/implementation_notes/bl000_data_layer/outputs/onion_join_coverage_report.json`
- Config artifact:
	- `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_config_snapshot.json`
	- `config_hash=B259CD10A428DD8DC5CF2EA8255807D28B6E771BDEDC24C32733982A6D47386F`
- Replay runner:
	- `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`

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
- script artifact path: `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`

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
	- Run evidence: `07_implementation/experiment_log.md` `EXP-013`; archived scenario `07_implementation/implementation_notes/bl011_controllability/outputs/scenarios/no_influence_tracks/`

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
	- Run evidence: `07_implementation/experiment_log.md` `EXP-013`; archived scenario `07_implementation/implementation_notes/bl011_controllability/outputs/scenarios/valence_weight_up/`

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
	- Run evidence: `07_implementation/experiment_log.md` `EXP-013`; archived scenarios `07_implementation/implementation_notes/bl011_controllability/outputs/scenarios/stricter_thresholds/` and `.../looser_thresholds/`

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
	- `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_report.json`
	- `07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_report.json`
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
	- `07_implementation/implementation_notes/bl000_data_layer/build_bl019_ds002_dataset.py`
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
	- `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`
- Command documentation:
	- `07_implementation/implementation_notes/bl013_entrypoint/bl013_run_command.md`
- Execution command:
	- `python 07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`

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
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`
- Runbook:
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/spotify_api_ingestion_runbook.md`
- Config:
	- scopes: `user-top-read user-library-read playlist-read-private playlist-read-collaborative user-read-private`
	- redirect URI: `http://127.0.0.1:8001/spotify/auth/callback`

### Expected Output
- OAuth authorization succeeds with requested scopes.
- Export artifacts are produced under `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/`.
- Summary includes endpoint counts and artifact hashes.

### Pass Criteria
- one successful end-to-end authenticated run
- non-zero results for at least one endpoint family
- run summary JSON and request log JSONL both present

### Actual Result
- Status: pass
- Run evidence: `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_export_run_summary.json` (run_id=`SPOTIFY-EXPORT-20260321-192533-881299`)
- Observed metrics:
	- `oauth.scope_granted=playlist-read-private|playlist-read-collaborative|user-library-read|user-top-read|user-read-private`
	- `top_tracks_short_term=598`
	- `top_tracks_medium_term=3021`
	- `top_tracks_long_term=5104`
	- `saved_tracks=170`
	- `playlists=4`
	- `playlist_items=31`
	- `unique_spotify_tracks=5592` (used downstream in BL-020)
	- `elapsed_seconds=46.711`
	- `request_log_present=yes`
	- `resilience_cache_enabled=yes`
- Output artifacts confirmed:
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_profile.json`
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_top_tracks_by_range.json`
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_top_tracks_flat.csv`
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_saved_tracks_flat.csv`
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_playlists.json`
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_playlists_flat.csv`
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_playlist_items_flat.csv`
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_playlist_items_flat.jsonl`
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_request_log.jsonl`

---

## Test Case TC-BL020-001: Real-Data BL-020 Alignment And Fallback Validation

- Date: 2026-03-21
- Backlog link: `BL-020`
- Purpose: Validate the first real-data BL-020 execution path by checking whether the user's Spotify Web API export can be aligned into the active DS-002 corpus, and if not, confirm that the semantic-only Last.fm fallback is correctly prepared.

### Inputs
- Real ingestion artifacts:
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_export_run_summary.json`
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_top_tracks_flat.csv`
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_saved_tracks_flat.csv`
- Active candidate corpus:
	- `07_implementation/implementation_notes/bl000_data_layer/outputs/bl019_ds002_integrated_candidate_dataset.csv`
- BL-020 code under test:
	- `07_implementation/implementation_notes/bl003_alignment/bl003_align_spotify_api_to_ds002.py`
	- `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`
	- `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`
	- `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`
	- `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`

### Expected Output
- Either:
	- a valid BL-003 alignment into DS-002 with genuine matches for real user seeds
- Or:
	- a documented fallback path with evidence that DS-002 alignment is not trustworthy and that semantic-only Last.fm enrichment is ready to replace it.

### Pass Criteria
- false positives are explicitly detected rather than silently accepted
- deprecation of Spotify audio-feature endpoints is reflected in the BL-020 execution path
- fallback code changes are present and auditable
- incomplete outputs are called out as incomplete rather than treated as finished evidence

### Actual Result
- Status: partial pass
- Run evidence: `07_implementation/experiment_log.md` `EXP-022`
- Observed metrics:
	- `spotify_export.unique_spotify_tracks=5592`
	- `fuzzy_run_1.matches=5318`
	- `fuzzy_run_2.matches=38`
	- `manual_false_positive_audit=38_of_38`
	- `lastfm_partial_cache_entries=100`
	- `lastfm_partial_cache.ok=10`
	- `lastfm_partial_cache.no_tags=84`
	- `lastfm_partial_cache.error=6`
	- `replacement_bl003_outputs_written=no`
- Interpretation:
	- The diagnostic objective passed: the repository now contains clear evidence that DS-002 fuzzy alignment is not valid for this user's real listening history.
	- The implementation objective is still incomplete: BL-003 replacement outputs remain stale, so downstream BL-004 through BL-009 reruns must not yet be treated as current evidence.

---

## Test Case TC-BL020-002: BL-003 Last.fm Enrichment Hardening And Runtime Visibility

- Date: 2026-03-21
- Backlog link: `BL-020`
- Purpose: Validate that BL-003 produces observable progress and resilient tag lookup behavior under real-data conditions after EXP-022 identified brittle `no_tags` outcomes.

### Inputs
- Script under test:
	- `07_implementation/implementation_notes/bl003_alignment/bl003_align_spotify_api_to_ds002.py`
- Data inputs:
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_top_tracks_flat.csv`
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_saved_tracks_flat.csv`
	- existing `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_lastfm_tag_cache.json`
- Runtime dependencies:
	- Last.fm API key
	- Last.fm methods `track.getTopTags`, `track.search`, `artist.getTopTags`

### Expected Output
- Script emits frequent progress lines during enrichment loop.
- Cache entries include current-schema markers for lookup provenance.
- Representative tracks previously returning `no_tags` can be resolved via fallback lookups where tags exist.

### Pass Criteria
- no syntax/runtime startup errors in BL-003 after patch
- fallback chain active and reachable in code path
- observable progress output confirmed in terminal
- at least one previously problematic track resolves via fallback source

### Actual Result
- Status: pass (in-progress run)
- Run evidence: `07_implementation/experiment_log.md` `EXP-023`
- Observed metrics:
	- `cache_schema_version=2`
	- `fallback_sources_present=track.getTopTags|track.search->track.getTopTags|artist.getTopTags`
	- `compile_check=no errors`
	- `probe_1='ABBA / The Visitors' status=ok source=artist.getTopTags`
	- `probe_2='Steve Winwood / While You See A Chance' status=ok source=artist.getTopTags`
	- `runtime_progress_output=visible`
	- `full_bl003_run_state=running_at_log_time`
- Interpretation:
	- The repair objective passed: lookup robustness and observability were materially improved.
	- Full BL-003 artifact regeneration remained in progress at logging time; final coverage numbers will be added when the run completes.

## Test Case TC-BL021-001: Source-Scope Controllability (Planned)

- Date: 2026-03-21
- Backlog link: `BL-021`
- Purpose: Verify that user-selected Spotify source scope (for example top tracks only vs include saved tracks) produces predictable runtime and profile-signal differences while preserving deterministic and auditable behavior.

### Inputs
- Baseline export artifacts:
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/`
- Planned control presets:
	- `preset_fast_top_tracks_only`
	- `preset_balanced_top_plus_saved`
	- `preset_full_all_enabled` (optional)

### Expected Output
- Run metadata includes explicit source-scope configuration.
- Source-level record counts are reported (`top_tracks`, `saved_tracks`, `playlist_items`).
- Runtime decreases under narrower scope presets.
- Profile summary shifts are interpretable and traceable to selected sources.

### Pass Criteria
- identical config repeat yields same source-selection manifest and profile hash
- narrower scope produces lower or equal runtime than broader scope
- source-level count and profile deltas are captured in run artifacts

### Actual Result
- Status: planned (deferred)
- Run evidence: `07_implementation/experiment_log.md` `EXP-024`
- Observed metrics: pending

## Test Case TC-BL020-003: BL-003 Interruption Safety And Partial Cache Replay

- Date: 2026-03-22
- Backlog link: `BL-020`
- Purpose: Verify that BL-003 progress can be safely reused for testing when enrichment is interrupted, and confirm BL-004 can execute on cache-derived partial aligned events.

### Inputs
- Last.fm cache snapshot:
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_lastfm_tag_cache.json`
- Spotify export inputs:
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_top_tracks_flat.csv`
	- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_saved_tracks_flat.csv`
- Script paths:
	- `07_implementation/implementation_notes/bl003_alignment/build_bl003_partial_from_cache.py`
	- `07_implementation/implementation_notes/bl003_alignment/bl003_align_spotify_api_to_ds002.py`
	- `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`

### Expected Output
- Partial aligned-events JSONL can be generated from cache without full Last.fm rerun.
- Active aligned-events input can be safely swapped with a backup retained.
- BL-004 runs successfully against partial aligned-events input.
- BL-003 script compiles after interruption-handling patch.

### Pass Criteria
- partial report includes non-zero `tracks_with_cache`
- partial aligned-events file exists and is readable
- BL-004 summary shows non-zero `matched_seed_count`
- `py_compile` on patched BL-003 script reports no errors

### Actual Result
- Status: pass
- Run evidence: `07_implementation/experiment_log.md` `EXP-025`
- Observed metrics:
	- `partial.unique_spotify_tracks=5592`
	- `partial.cache_entries=300`
	- `partial.tracks_with_cache=398`
	- `partial.tagged_with_lastfm=375`
	- `partial.no_tags=4`
	- `partial.errors=19`
	- `partial.coverage_over_total_tracks_pct=7.12`
	- `partial.tag_coverage_over_partial_pct=94.22`
	- `bl004.matched_seed_count=398`
	- `bl004.total_effective_weight=639.721055`
	- `bl003.py_compile=no errors`

## Test Case TC-BL020-005: BL-005 Semantic Candidate Filtering On Real Profile

- Date: 2026-03-22
- Backlog link: `BL-020` → `BL-005`
- Purpose: Validate BL-005 deterministic candidate filtering on the real enriched preference profile (BL-004) against the full DS-002 corpus, ensuring semantic filtering produces a manageable and auditable candidate subset ready for downstream scoring.

### Inputs
- Preference profile:
	- `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json` (run_id=`BL004-PROFILE-20260322-020511-252947`, 5,592 enriched seeds)
	- `07_implementation/implementation_notes/bl004_profile/outputs/bl004_seed_trace.csv` (seed track IDs)
- Candidate corpus:
	- `07_implementation/implementation_notes/bl000_data_layer/outputs/bl019_ds002_integrated_candidate_dataset.csv` (9,330 tracks with semantic tags/genres)
- Script under test:
	- `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`
- Configuration:
	- numeric_features_enabled=false (BL-004 profile has no numeric centers)
	- keep_rule: keep if not seed and semantic_score >= 1
	- semantic_score based on: lead_genre_match + genre_overlap_count + tag_overlap_count

### Expected Output
- Filtered candidate set (bl005_filtered_candidates.csv) with semantic overlap
- Complete decision audit trail (bl005_candidate_decisions.csv) showing reason for each keep/reject
- Diagnostics with rule hit counts and deterministic hashes
- Filtered candidates ready for BL-006 scoring stage

### Pass Criteria
- All 9,330 candidates evaluated with decision traced
- Filtered count between 500-3000 (reasonable narrowing from full corpus)
- No seed tracks found in candidate corpus (expected) or properly excluded (if any matched)
- Output determinism confirmed via SHA256 consistency
- Decision audit trail shows transparent sorting logic

### Actual Result
- Status: pass
- Run evidence: `07_implementation/experiment_log.md` `EXP-026`
- Observed metrics:
	- `total_candidates_evaluated=9330`
	- `kept_candidates=1740` (18.62%)
	- `rejected_candidates=7590` (81.38%)
	- `seed_tracks_in_corpus=0` (no Spotify import tracks matched DS-002, as expected)
	- `semantic_rule_distribution`:
		- `lead_genre_match=425`
		- `genre_overlap=1669`
		- `tag_overlap=1740`
	- `numeric_rule_hits=0` (disabled as expected)
	- `elapsed_seconds=0.236`
	- `output_hash_bl005_filtered_candidates.csv=3a476cf8...` (deterministic)
	- `output_hash_bl005_candidate_decisions.csv=5fdbfac2...` (deterministic)
	- `input_hash_profile=400019a4...` (BL-004 output)
	- `input_hash_corpus=b9c729a2...` (BL-019 output)

### Interpretation
- Semantic filtering condensed 9,330 candidates to 1,740 (18.62% pass rate)
- Decision logic is transparent and auditable (full reason codes in decisions CSV)
- Deterministic execution confirmed (repeat-safe with consistent output hashes)
- No numeric feature contribution (as expected due to Spotify audio-feature deprecation)
- Output ready for BL-006 scoring on 1,740 filtered candidates
- Test passes: filtering logic works correctly, determinism maintained, audit trail complete

## Test Case TC-BL020-006: BL-006 Semantic-Weighted Candidate Scoring On Filtered Set

- Date: 2026-03-22
- Backlog link: `BL-020` → `BL-006`
- Purpose: Validate BL-006 deterministic weighted-similarity scoring on the 1,740 filtered candidates using the real BL-004 preference profile in semantic-only mode, producing ranked scored candidates ready for playlist assembly (BL-007).

### Inputs
- Preference profile:
	- `07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json` (run_id=`BL004-PROFILE-20260322-020511-252947`, semantic centers only, numeric centers null/empty)
	- Profile dominant genres: classical (1019.05), classic rock (778.89), progressive rock (755.93), pop (522.76), rock (321.15)
- Candidate set:
	- `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_filtered_candidates.csv` (1,740 filtered candidates with genre/tag columns)
- Script under test:
	- `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`
- Configuration:
	- mode: semantic-only (numeric feature centers absent)
	- base_weights: tempo 0.18, loudness 0.12, key 0.10, mode 0.05, lead_genre 0.20, genre_overlap 0.17, tag_overlap 0.18
	- active_weights_after_normalization: lead_genre 0.363636, genre_overlap 0.309091, tag_overlap 0.327273
	- inactive_weights: tempo 0.0, loudness 0.0, key 0.0, mode 0.0

### Expected Output
- Scored candidates (bl006_scored_candidates.csv) with 0.0–1.0 similarity scores
- Score summary (bl006_score_summary.json) with statistics, top 10, input hashes, run metadata
- All 1,740 candidates ranked deterministically for downstream playlist assembly

### Pass Criteria
- All 1,740 candidates receive a final_score
- Scores span 0.0–1.0 range with interpretable distribution
- Top-ranked candidates show high semantic overlap with user's dominant genres (classical/classic rock/progressive rock)
- Deterministic output hash confirms repeat-safe execution
- Score statistics (mean, median, max, min) are sensible and reported

### Actual Result
- Status: pass
- Run evidence: `07_implementation/experiment_log.md` `EXP-027`
- Observed metrics:
	- `total_candidates_scored=1740`
	- `score_range_min=0.012159`
	- `score_range_max=0.770977`
	- `score_statistics`:
		- `mean=0.214394`
		- `median=0.182508`
		- `std_dev=(not reported in summary, but distribution visible in ranked list)`
	- `active_weights_applied`:
		- `lead_genre=0.363636` (36.36%)
		- `genre_overlap=0.309091` (30.91%)
		- `tag_overlap=0.327273` (32.73%)
	- `numeric_component_contribution=0.0` (all disabled, as expected in semantic-only mode)
	- `top_10_candidates_dominant_genre=classic rock` (9 of 10)
	- `top_candidate_track_id=TRBFMTO128F9322AE7`
	- `top_candidate_score=0.770977`
	- `top_candidate_matched_genres=6` (classic rock + overlaps)
	- `elapsed_seconds=0.113`
	- `output_hash_bl006_scored_candidates.csv=3faeb6d4...` (deterministic)
	- `input_hash_profile=400019a4...` (BL-004 output, confirms correct profile used)`
	- `input_hash_candidates=3a476cf8...` (BL-005 output, confirms correct candidate set)`

### Interpretation
- Semantic-weighted scoring successfully ranked all 1,740 candidates by similarity to user preference profile
- Score distribution naturally concentrates near user's dominant genres (classic rock heavy in top 10)
- Weights correctly re-normalized after disabling numeric components (sum = 1.0)
- Deterministic execution confirmed (consistent hashes across run_id and outputs)
- Scores transparent: high mean (0.214) reflects selective nature of filtered set; median (0.183) shows conservative central tendency
- Output ready for BL-007 playlist assembly with confidence in deterministic ranking
- Test passes: scoring logic works correctly, semantic-only mode handles missing numeric centers, determinism maintained, diagnostics transparent

## Test Case TC-BL020-007: BL-007 Rule-Based Playlist Assembly On Scored Candidates

- Date: 2026-03-22
- Backlog link: `BL-020` → `BL-007`
- Purpose: Validate BL-007 deterministic rule-based playlist assembly on the 1,740 score-ranked candidates from BL-006, ensuring four assembly rules (score threshold, genre cap, consecutive run, length cap) produce a coherent 10-track playlist with transparent diversity constraints.

### Inputs
- Scored candidates:
	- `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv` (1,740 candidates ranked by final_score, with lead_genre and component scores)
- Script under test:
	- `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`
- Configuration:
	- target_size=10 (fixed-length output)
	- min_score_threshold=0.35 (R1: score-based exclusion)
	- max_per_genre=4 (R2: cap per lead_genre)
	- max_consecutive=2 (R3: avoid 3+ consecutive same genre)

### Expected Output
- Final playlist (bl007_playlist.json) with 10 tracks
- Complete decision audit trail (bl007_assembly_trace.csv) showing inclusion/exclusion for all 1,740 candidates
- Diagnostics (bl007_assembly_report.json) with rule hits and genre distribution

### Pass Criteria
- All 10 playlist slots filled with score-ranked candidates
- Genre distribution balanced (no more than 4 of same genre)
- No 3 consecutive tracks share the same lead_genre
- All tracks meet min_score_threshold or are selected by rule hierarchy
- Output determinism confirmed via SHA256 consistency
- Decision audit trail is complete and traceable

### Actual Result
- Status: pass
- Run evidence: `07_implementation/experiment_log.md` `EXP-028`
- Observed metrics:
	- `playlist_length=10` (target met)
	- `candidates_evaluated=1740`
	- `candidates_included=10`
	- `candidates_excluded=1730`
	- `playlist_genre_mix`:
		- `classic rock=4` (at max cap)
		- `pop=3`
		- `progressive rock=2`
		- `rock=1`
	- `playlist_score_range`:
		- `max=0.770977` (top-ranked candidate TRBFMTO128F9322AE7, classic rock)
		- `min=0.595743` (10th candidate TRARIRG128F147FC96, pop)
	- `rule_hits_distribution`:
		- `R1_score_threshold=0` (no candidates excluded due to low score)
		- `R2_genre_cap=14` (14 candidates rejected for exceeding genre cap)
		- `R3_consecutive_run=1` (1 candidate rejected for consecutive-run rule)
		- `R4_length_cap=1715` (1,715 candidates excluded because playlist full)
	- `elapsed_seconds=0.011`
	- `output_hash_bl007_playlist.json=67C87948...` (deterministic)
	- `output_hash_bl007_assembly_trace.csv=933F7C69...` (deterministic)
	- `input_hash_bl006_scored_candidates.csv=3FAEB6D4...` (correct input verified)

### Interpretation
- Rule-based greedy assembly successfully produced a balanced 10-track playlist from 1,740 candidates
- Genre constraints enforced transparently: classic rock capped at 4 (user dominant), pop at 3, progressive rock at 2, rock at 1
- Score threshold rule (R1) did not exclude any selected candidates; all 10 tracks scored above threshold (min 0.596)
- Majority exclusions due to R4 (length cap) is expected: only 10 slots available from 1,740 candidates
- Genre cap rule (R2) hit 14 times, showing effective hard constraint on per-genre repetition
- Consecutive-run rule (R3) rarely triggered (1 hit), suggesting genre ordering naturally avoids same-genre runs with these rules
- Deterministic execution confirmed (consistent hashes); playlist is reproducible and auditable
- Test passes: assembly logic works correctly, diversity rules effective, determinism maintained, audit trail complete

## Test Case TC-BL020-008: BL-008 Transparency Explanation Generation On Playlist Tracks

- Date: 2026-03-22
- Backlog link: `BL-020` → `BL-008`
- Purpose: Validate BL-008 deterministic explanation payload generation on the 10-track final playlist, ensuring transparency explanations correctly display score component breakdowns and assembly rationale in both human-readable and machine-readable formats.

### Inputs
- Playlist and scoring artifacts:
	- `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv` (all component data for candidate lookup)
	- `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json` (active component weights and configuration)
	- `07_implementation/implementation_notes/bl007_playlist/outputs/bl007_playlist.json` (10-track final playlist)
	- `07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_trace.csv` (rule application trace)
- Script under test:
	- `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`
- Configuration:
	- Semantic-only component mode (4 numeric components inactive; 3 semantic active with redistributed weights)

### Expected Output
- Explanation payloads (bl008_explanation_payloads.json) with 10 explanation records
- Each explanation includes: why_selected text, top 3 contributors, complete score breakdown
- Summary (bl008_explanation_summary.json) with metadata and top contributor distribution

### Pass Criteria
- All 10 playlist tracks have explanation payloads
- Each payload includes human-readable why_selected sentence
- Top 3 score contributors correctly identified and ranked by contribution magnitude
- Score breakdown accounts for all component weights and similarities
- Component weights match active configuration from BL-006
- Deterministic output hash confirms reproducibility
- Input artifact hashes match upstream outputs (input validation)

### Actual Result
- Status: pass
- Run evidence: `07_implementation/experiment_log.md` `EXP-029`
- Observed metrics:
	- `playlist_tracks_explained=10` (all tracks covered)
	- `elapsed_seconds=0.011`
	- `top_contributor_distribution`:
		- `lead_genre_match=6` (tracks 1, 2, 4, 5, 7, 8)
		- `tag_overlap=3` (tracks 6, 10; one pop, one rock)
		- `genre_overlap=1` (track 9; rock)
	- `active_component_weights`:
		- `lead_genre=0.363636`
		- `genre_overlap=0.309091`
		- `tag_overlap=0.327273`
		- `numeric_inactive=4` (tempo, loudness, key, mode all 0.0)
	- `sample_explanation_track_1`:
		- `why_selected`: "Selected at playlist position 1 (score 0.7710) because it strongly matches the preference profile on Lead genre match, Genre overlap, Tag overlap. Lead genre is 'classic rock'."
		- `top_contributors`: [lead_genre 0.278, genre_overlap 0.249, tag_overlap 0.244]
		- `final_score_validation`: 0.770977 matches BL-006 ranking
	- `output_hash_bl008_explanation_payloads.json=D1ED9567...` (deterministic)
	- `input_hash_bl006_scored_candidates.csv=3FAEB6D4...`
	- `input_hash_bl007_playlist.json=67C87948...`

### Interpretation
- Transparency explanation generation successfully created complete payloads for all 10 tracks
- Top contributor distribution reflects user preferences: lead genre match dominant 6 times (classic rock tracks), semantic overlaps (tag/genre) for diversity genre tracks
- Score component breakdown shows correct weight redistribution (semantic-only mode confirmed active)
- why_selected sentences are template-generated but informative; they correctly identify top-matching components
- All input artifacts correctly linked via SHA256 hashes (round-trip integrity confirmed)
- Deterministic execution confirmed (consistent output hash); explanations are reproducible and auditable
- Test passes: explanation generation works correctly, transparency complete, determinism maintained, all score components accurately represented

## Test Case TC-BL020-009: BL-009 Observability And Audit Log Generation For Complete Pipeline

- Date: 2026-03-22
- Backlog link: `BL-020` → `BL-009`
- Purpose: Validate BL-009 deterministic observability log generation documenting the complete BL-020 pipeline execution with full stage traceability, configuration snapshots, diagnostics, and artifact hashes.

### Inputs
- All upstream stage artifacts (BL-004–BL-008) plus supporting dataset/bootstrap assets
- Script under test: `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`
- Configuration: bootstrap_mode=true

### Expected Output
- Structured observability log (bl009_run_observability_log.json) with complete run metadata and stage diagnostics
- Quick-lookup index (bl009_run_index.csv) with key metadata for reproducibility verification
- All upstream run IDs documented and linked

### Pass Criteria
- All BL-004–BL-008 artifacts successfully read
- Stage diagnostics counts match upstream outputs (1,740 candidates → 10 playlist → 10 explanations)
- Output artifact hashes match previously generated outputs
- Dataset and pipeline version fingerprints computed deterministically
- JSON and CSV outputs both generated without errors
- Output determinism confirmed

### Actual Result
- Status: pass
- Run evidence: `07_implementation/experiment_log.md` `EXP-030`
- Observed metrics:
	- `run_id=BL009-OBSERVE-20260322-023314-347594`
	- `elapsed_seconds=0.065`
	- `bootstrap_mode=true` (confirmed)
	- `dataset_version=2648A323...`
	- `pipeline_version=A20B7C5E...`
	- `upstream_run_ids_linked=5` (BL-004–BL-008 all documented)
	- `output_artifacts_documented=11` (2 primary, 4 trace, 5 supporting)
	- `stage_diagnostics`:
		- BL-004: 5,592 seeds, 6,712.96 weight
		- BL-005: 1,740 kept (18.62%)
		- BL-006: mean 0.214, max 0.771
		- BL-007: 10-track playlist, 4 classic rock + 3 pop + 2 prog rock + 1 rock
		- BL-008: 10 explanations, lead genre top contributor (6)
	- `artifact_hash_round_trip`: all documented hashes match upstream outputs
	- `index_csv_generated` with all fields populated
	- `output_hash_bl009_run_observability_log.json=664FE972...` (deterministic)

### Interpretation
- Observability log generation successfully compiled complete pipeline audit documentation across BL-004–BL-008
- Upstream run IDs correctly linked; all stage metadata successfully extracted and compiled
- Configuration snapshots preserve exact parameter settings from each stage
- Stage diagnostics align perfectly with upstream outputs, confirming round-trip integrity
- Output artifact hashes match documented outputs, proving connectivity and reproducibility
- Dataset and pipeline version fingerprints computed deterministically
- Quick-lookup index provides efficient metadata access for governance and troubleshooting
- Test passes: observability generation works correctly, complete pipeline traceability established, determinism maintained, all audit requirements satisfied

## Test Case TC-BL014-001: Automated Sanity Checks For BL-020 Artifacts

- Date: 2026-03-22
- Backlog link: `BL-014`
- Purpose: Validate that automated checks can enforce artifact schema presence, cross-stage hash-link integrity, and count/run-id continuity across BL-004 through BL-009 outputs.

### Inputs
- Script under test:
	- `07_implementation/implementation_notes/bl014_quality/run_bl014_sanity_checks.py`
- Artifact set under validation:
	- BL-004 profile + summary + seed trace
	- BL-005 filtered candidates + decisions + diagnostics
	- BL-006 scored candidates + summary
	- BL-007 playlist + trace + report
	- BL-008 explanation payloads + summary
	- BL-009 observability log + run index

### Expected Output
- `bl014_sanity_report.json` with full check list and pass/fail status.
- `bl014_sanity_run_matrix.csv` with run-level summary metrics and key hashes.
- `bl014_sanity_config_snapshot.json` capturing check scope and required artifacts.
- All checks pass for current BL-020 snapshot.

### Pass Criteria
- `overall_status=pass`
- `checks_failed=0`
- required schema checks pass for BL-004 through BL-009 artifacts
- hash-link checks pass between stage summaries/reports and actual artifact files
- continuity checks pass for BL-005 kept count, BL-006 scored count, BL-007 playlist length, BL-008 explanation count, and BL-009 run index linkage

### Actual Result
- Status: pass
- Run evidence: `07_implementation/experiment_log.md` `EXP-031`
- Observed metrics:
	- `run_id=BL014-SANITY-20260322-024523-652281`
	- `overall_status=pass`
	- `checks_total=21`
	- `checks_passed=21`
	- `checks_failed=0`
	- `elapsed_seconds=0.078`
	- `continuity.bl005_kept_candidates=1740`
	- `continuity.bl006_candidates_scored=1740`
	- `continuity.playlist_length=10`
	- `continuity.explanation_count=10`
	- `continuity.bl009_run_id=BL009-OBSERVE-20260322-023314-347594`
	- `sha256.bl014_sanity_report.json=63100EFE0129444500D44BCE48B4996C9F3B9307A2781234D96690E802037621`
	- `sha256.bl014_sanity_run_matrix.csv=6413404703DB1283E1BA9F32EA7D3EA9488DBD8B627FEA3A110874F27E485EFC`
	- `sha256.bl014_sanity_config_snapshot.json=627C3F0D9457B444FC7BAB8DF9B7C1148BBC948B662C4372B4CAD7C2E9C4F4CA`

### Interpretation
- BL-014 successfully automated sanity validation for the full BL-020 evidence chain.
- Schema checks confirm expected shape of key artifacts before downstream use.
- Hash-link checks prove that stage summaries/reports correctly reference real upstream/downstream files.
- Continuity checks confirm count and run-id integrity across filtering, scoring, playlist, transparency, and observability outputs.
- Test passes: automated quality gate is operational and can be reused as a regression check after future reruns.