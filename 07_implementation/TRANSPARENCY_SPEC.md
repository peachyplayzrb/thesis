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
- *Needed*: Show influence_tracks reservation (once redesigned)
- *Needed*: Show how assembly_rules config shaped selection
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

## Planned Enhancements

### Control Traceability
Add to all stages:
```json
{
  "user_controls_applied": {
    "influence_tracks": {
      "enabled": true,
      "request_count": 2,
      "fulfilled_count": 2,
      "effect": "reserved 2 playlist slots"
    },
    "numeric_thresholds": {
      "danceability_distance": 0.25,
      "effect": "rejected N candidates outside this threshold"
    }
  }
}
```

### Counterfactual Reasoning
Add to transparency outputs:
```json
{
  "what_if_analysis": {
    "if_no_influence_tracks": "playlist would be: [track_ids], rank changes: [...]",
    "if_stricter_thresholds": "pool would shrink to N candidates",
    "if_looser_genre_cap": "could fit more pop tracks, genre mix would be: [...]"
  }
}
```

## Next Steps
- Update BL-004 to differentiate influence seed sources
- Update BL-007 trace to show influence_tracks reservation
- Add control_application block to all explanations
- Implement what-if analysis in observability
