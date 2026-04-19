# Run Config Reference

This document is the operator-facing reference for active run-config controls.

Authoritative source:
- `src/run_config/control_registry.py`
- Schema authority: `src/run_config/schemas/run_config-v1.schema.json`
- Active baseline profile: `config/profiles/run_config_ui013_tuning_v1f.json`

## How To Use This Reference

- `section`: top-level run-config object where the key belongs.
- `stage`: primary pipeline stage affected by the control.
- `type`: expected control shape.
- `valid_values` or `valid_range`: accepted values.
- `default`: value applied when key is omitted.
- `effect_surface`: what behavior changes when you vary the control.

## Unified Control Table

| name | section | stage | type | valid_values | valid_range | default | effect_surface |
|---|---|---|---|---|---|---|---|
| confidence_weighting_mode | profile_controls | BL-004 | enum | linear_half_bias, direct_confidence, none | - | linear_half_bias | weights profile signal by seed match confidence; affects numeric feature contribution strength |
| confidence_bin_high_threshold | profile_controls | BL-004 | fraction | - | [0.0, 1.0] | 0.90 | boundary that separates high-confidence from medium-confidence seeds in profile aggregation |
| top_tag_limit | profile_controls | BL-004 | positive_int | - | >= 1 | 10 | tag vocabulary size retained in preference profile; larger values increase semantic breadth |
| top_lead_genre_limit | profile_controls | BL-004 | positive_int | - | >= 1 | 6 | number of lead genres retained in preference profile; affects genre-match scoring weight |
| interaction_attribution_mode | profile_controls | BL-004 | enum | split_selected_types_equal_share, primary_type_only | - | split_selected_types_equal_share | governs how history vs influence interaction types share attribution weight in profile aggregation |
| semantic_strong_keep_score | retrieval_controls | BL-005 | positive_int | - | >= 0 | 2 | minimum semantic score for unconditional candidate keep; raising this tightens semantic filter |
| semantic_min_keep_score | retrieval_controls | BL-005 | positive_int | - | >= 0 | 1 | minimum semantic score to pass for numeric check; raising this increases semantic strictness |
| numeric_support_min_pass | retrieval_controls | BL-005 | positive_int | - | >= 0 | 1 | minimum number of numeric dimensions that must pass threshold; raising reduces candidate pool |
| use_weighted_semantics | retrieval_controls | BL-005 | bool | true, false | - | false | enables tag-weighted semantic overlap scoring in retrieval; false = unweighted overlap |
| use_continuous_numeric | retrieval_controls | BL-005 | bool | true, false | - | false | switches numeric comparison from threshold-pass to continuous distance scoring |
| recency_years_min_offset | retrieval_controls | BL-005 | optional_int | - | >= 0 or null | null | minimum release year offset for recency gate; null disables recency filtering |
| component_weights | scoring_controls | BL-006 | dict | - | per-feature float in [0.0, 1.0]; values normalized to sum to 1.0 | DEFAULT_SCORING_COMPONENT_WEIGHTS | relative weight per audio/semantic feature in composite score; changes track rank ordering |
| lead_genre_strategy | scoring_controls | BL-006 | enum | single_anchor, weighted_top_lead_genres | - | weighted_top_lead_genres | genre score uses single highest-weight genre or weighted blend of top genres |
| semantic_overlap_strategy | scoring_controls | BL-006 | enum | overlap_only, precision_aware | - | precision_aware | semantic scoring method; precision_aware adjusts for profile tag concentration |
| enable_numeric_confidence_scaling | scoring_controls | BL-006 | bool | true, false | - | true | scales numeric component scores by profile confidence; false = unscaled numeric contributions |
| apply_bl003_influence_tracks | scoring_controls | BL-006 | bool | true, false | - | false | applies a score bonus to nominated influence tracks; false = no bonus applied |
| target_size | assembly_controls | BL-007 | positive_int | - | >= 1 | 10 | desired playlist length; controls assembly length gate |
| min_score_threshold | assembly_controls | BL-007 | fraction | - | [0.0, 1.0] | 0.35 | minimum composite score for inclusion; raising this tightens quality gate |
| max_per_genre | assembly_controls | BL-007 | positive_int | - | >= 1 | 4 | maximum tracks per genre in playlist; controls genre diversity constraint |
| utility_strategy | assembly_controls | BL-007 | enum | rank_round_robin, utility_greedy | - | rank_round_robin | selection ordering method; rank_round_robin interleaves genres, utility_greedy selects by utility score |
| utility_decay_factor | assembly_controls | BL-007 | fraction | - | [0.0, 1.0] | 0.0 | rank decay pressure in utility-greedy mode; 0.0 disables decay |
| influence_policy_mode | assembly_controls | BL-007 | enum | competitive, reserved_slots, hybrid_override | - | competitive | governs how influence tracks compete or are reserved in playlist assembly |
| transition_smoothness_weight | assembly_controls | BL-007 | fraction | - | [0.0, 1.0] | 0.0 | weight for sequential transition coherence scoring; 0.0 disables smoothness optimization |
| top_contributor_limit | transparency_controls | BL-008 | positive_int | - | >= 1 | 3 | number of scoring contributors surfaced per track in explanation output |
| stricter_threshold_scale | controllability_controls | BL-011 | float | - | (0.0, 1.0] | 0.75 | scale factor applied to numeric thresholds in stricter-threshold controllability scenarios |
| looser_threshold_scale | controllability_controls | BL-011 | float | - | >= 1.0 | 1.25 | scale factor applied to numeric thresholds in looser-threshold controllability scenarios |

## Notes

- `component_weights` default is inherited from `shared_utils.constants.DEFAULT_SCORING_COMPONENT_WEIGHTS`.
- Runtime controls may still be overridden by approved environment channels captured in run-effective artifacts.
- For strict schema validation and coercion behavior, use `validation_profile=strict` and inspect BL-013 run-effective outputs.
