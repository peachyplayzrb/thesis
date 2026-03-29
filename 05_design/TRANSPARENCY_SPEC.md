# Transparency Specifications

## Purpose
Define what information each stage must produce to explain decisions to users.
Thesis requirement: Every decision must be transparent and traceable to explicit system rules.

## Current Transparency by Stage

### BL-004: Profile Building
**Current Outputs**
- bl004_preference_profile.json: numeric centers, top tags/genres, lead genres
- bl004_seed_trace.csv: per-seed weights and characteristics
- profile_summary.json: dominant features

**Current Explanation**
- Shows WHAT the profile is (danceability=0.65, top genres=[pop, rock])
- Shows HOW seeds were aggregated (weighted means)

**Gap**: Does NOT explain user control application
- *Needed*: Show which seeds came from influence_tracks
- *Needed*: Explain weight applied to influence seeds vs. history

### BL-005: Retrieval Filtering
**Current Outputs**
- bl005_filtered_candidates.csv: which candidates passed
- decision_fields: lead_genre_match, tag_overlap_count, numeric_pass_count

**Current Explanation**
- Shows which rule admitted/rejected each candidate

**Gap**: Does NOT explain user control application
- *Needed*: Show how numeric_threshold values affected filtering
- *Needed*: Show why language_filter included/excluded candidates

### BL-007: Playlist Assembly
**Current Outputs**
- playlist.json: ordered final tracks
- bl007_assembly_trace.csv: which rule admitted/rejected each candidate

**Current Explanation**
- Shows which R1-R4 rule admitted each track
- Shows genre distribution, consecutive runs

**Gap**: Does NOT explain user control application
- *Clarification*: BL-007 emits effective config snapshots and rule-hit diagnostics, but does not emit per-track control-causality statements
- *Needed*: Show influence_tracks impact path (currently weak and indirect)
- *Needed*: Show what would happen with different rule parameters

### BL-008: Explanation Payloads (Transparency Output)
**Current Outputs**
- bl008_explanation_payloads.json: per-track explanation

**Current Explanation**
- top_score_contributors: which components (danceability, genre, etc.) drove selection
- score_breakdown: full contribution from each component
- why_selected: concise human summary

**Gap**: Does NOT trace back user controls
- *Needed*: "This track was selected because [your genre preference] drove the score up"
- *Needed*: "This track would NOT have been selected if you'd used looser numeric thresholds"

## Known Limitations (Current Implementation)

- Control-causality is not emitted as a unified `user_controls_applied` block.
- Counterfactual reasoning is not emitted in BL-008 or BL-009 outputs.
- Influence-track impact is visible only indirectly through aggregation behavior and downstream result deltas.

## Future Work (Optional, Out of Current Scope)
- Add stage-level control-causality blocks linking accepted/rejected outcomes to concrete control values.
- Add what-if/counterfactual summaries for major control families (thresholds, language filter, assembly limits).
- Add stronger influence-track traceability once control-effect behavior changes from weak indirect influence.

## Next Steps
- Keep limitations explicit in thesis claims and evaluation framing.
- Avoid describing future-work transparency features as implemented behavior.
