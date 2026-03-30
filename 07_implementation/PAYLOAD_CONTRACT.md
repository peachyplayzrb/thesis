# BL_STAGE_CONFIG_JSON Payload Contract

## Overview

The `BL_STAGE_CONFIG_JSON` environment variable carries orchestration-resolved controls to stages as a JSON serialized dictionary. This is the **Phase 3+** architecture for config handoff.

**Precedence** (enforced by all stages):
1. `BL_STAGE_CONFIG_JSON` (orchestration-injected payload) ← **NEW (Phase 3)**
2. `BL_RUN_CONFIG_PATH` (legacy file path) ← **LEGACY (Phase 1/2)**
3. Stage-local env defaults (individual `BL00X_*` vars) ← **LEGACY FALLBACK**

---

## Payload Format by Stage

### BL-003 (Alignment)

**Source**: `orchestration/config_resolver.py::resolve_stage_control_payload("BL-003")`

```json
{
  "input_scope_controls": {
    "include_top_tracks": bool,
    "include_saved_tracks": bool,
    "include_playlists": bool,
    "include_recently_played": bool,
    "top_tracks_ranges": ["short_term", "medium_term", "long_term"],
    "saved_tracks_limit": int | null,
    "playlists_limit": int | null,
    "items_per_playlist_limit": int | null
  },
  "seed_controls": {
    "top_range_weights": {"short_term": float, "medium_term": float, "long_term": float},
    "source_base_weights": {
      "top_tracks": float,
      "saved_tracks": float,
      "playlist_items": float,
      "recently_played": float
    },
    "fuzzy_matching": {
      "enabled": bool,
      "artist_threshold": float,
      "title_threshold": float,
      "combined_threshold": float,
      "max_duration_delta_ms": int,
      "max_artist_candidates": int
    },
    "match_strategy": {
      "enable_spotify_id_match": bool,
      "enable_metadata_match": bool,
      "enable_fuzzy_match": bool
    },
    "match_strategy_order": ["spotify_id_exact", "metadata_fallback", "fuzzy_title_artist"],
    "temporal_controls": { ... },
    "aggregation_policy": { ... },
    "decay_half_lives": {
      "recently_played": float,
      "saved_tracks": float
    },
    "match_rate_min_threshold": float
  },
  "weighting_policy": {
    "min_event_weight": float,
    ...
  } | null,
  "influence_controls": {
    "influence_enabled": bool,
    "influence_track_ids": [str, ...],
    "influence_preference_weight": float
  }
}
```

**Consumed By**: `alignment/resolved_context.py::resolve_alignment_context()`

---

### BL-004 (Profile)

**Source**: `orchestration/config_resolver.py::resolve_stage_control_payload("BL-004")`

```json
{
  "top_tag_limit": int,
  "top_genre_limit": int,
  "top_lead_genre_limit": int,
  "confidence_weighting_mode": "linear_half_bias" | "direct_confidence" | "none",
  "confidence_bin_high_threshold": float,
  "confidence_bin_medium_threshold": float,
  "interaction_attribution_mode": "split_selected_types_equal_share" | "primary_type_only",
  "emit_profile_policy_diagnostics": bool,
  "include_interaction_types": [str, ...],
  "user_id": str,
  "input_scope": { ... }
}
```

**Consumed By**: `profile/runtime_controls.py::resolve_bl004_runtime_controls()` via shared resolver

---

### BL-005 (Retrieval)

**Source**: `orchestration/config_resolver.py::resolve_stage_control_payload("BL-005")`

```json
{
  "candidate_pool_size": int,
  "diversity_factor": float,
  "recency_window_days": int,
  ...
}
```

**Consumed By**: `retrieval/runtime_controls.py::resolve_bl005_runtime_controls()` via shared resolver

---

### BL-006 (Scoring)

**Source**: `orchestration/config_resolver.py::resolve_stage_control_payload("BL-006")`

```json
{
  "signal_mode": { ... },
  "component_weights": {
    "popularity_score": float,
    "recency_score": float,
    "diversity_score": float,
    ...
  },
  "numeric_thresholds": { ... },
  "lead_genre_strategy": "weighted_top_lead_genres" | "frequency_top_lead_genres",
  "semantic_overlap_strategy": "precision_aware" | "recall_aware",
  "semantic_precision_alpha_mode": "profile_adaptive" | "fixed",
  "semantic_precision_alpha_fixed": float,
  "enable_numeric_confidence_scaling": bool,
  "numeric_confidence_floor": float,
  "profile_numeric_confidence_mode": "direct" | "scaled",
  "profile_numeric_confidence_blend_weight": float,
  "emit_confidence_impact_diagnostics": bool,
  "emit_semantic_precision_diagnostics": bool,
  "apply_bl003_influence_tracks": bool,
  "influence_track_bonus_scale": float
}
```

**Consumed By**: `scoring/runtime_controls.py::resolve_bl006_runtime_controls()`

---

### BL-007 (Playlist)

**Source**: `orchestration/config_resolver.py::resolve_stage_control_payload("BL-007")`

```json
{
  "target_size": int,
  "min_score_threshold": float,
  "max_per_genre": int,
  "max_consecutive": int,
  ...
}
```

**Consumed By**: `playlist/runtime_controls.py::resolve_bl007_runtime_controls()` via shared resolver

---

### BL-008 (Transparency)

**Source**: `orchestration/config_resolver.py::resolve_stage_control_payload("BL-008")`

```json
{
  "explanation_depth": "summary" | "detailed" | "comprehensive",
  "include_confidence_scores": bool,
  "include_source_attribution": bool,
  ...
}
```

**Consumed By**: `transparency/runtime_controls.py::resolve_bl008_runtime_controls()` via shared resolver

---

### BL-009 (Observability)

**Source**: `orchestration/config_resolver.py::resolve_stage_control_payload("BL-009")`

```json
{
  "diagnostic_sample_limit": int,
  "bootstrap_mode": bool,
  "control_mode": { ... },
  "input_scope": { ... }
}
```

**Consumed By**: `observability/main.py::resolve_bl009_runtime_controls()` via shared resolver

---

### BL-011 (Controllability)

**Source**: `orchestration/config_resolver.py::resolve_stage_control_payload("BL-011")`

```json
{
  "scenario_policy": "baseline" | "conservative" | "aggressive",
  "scenario_definitions": { ... },
  "query_mode": "direct" | "guided",
  ...
}
```

**Consumed By**: `controllability/runtime_controls.py::resolve_bl011_runtime_controls()` via shared resolver

---

## Testing Payload-Based Controls

### Phase 4: Fixture Helper Example

```python
def make_bl003_payload_fixture(
    top_range_weights: dict | None = None,
    match_strategy_order: list | None = None,
) -> dict[str, object]:
    """Test helper: build a minimal BL-003 payload for fixture injection."""
    return {
        "input_scope_controls": {...},
        "seed_controls": {...},
        "weighting_policy": {...},
        "influence_controls": {...},
    }

# In test:
payload = make_bl003_payload_fixture(
    top_range_weights={"short_term": 0.8, "medium_term": 0.15, "long_term": 0.05}
)
monkeypatch.setenv("BL_STAGE_CONFIG_JSON", json.dumps(payload))
```

See: `tests/test_orchestration_stage_payload_handoff.py` for complete examples

---

## Migration Guide: Legacy → Payload

### Old Approach (Phase 1/2):
```python
# Stage reads env vars or file path
monkeypatch.setenv("BL004_TOP_TAG_LIMIT", "50")
monkeypatch.setenv("BL004_USER_ID", "user123")
stage.run()
```

### New Approach (Phase 3+):
```python
# Orchestration resolves and injects payload
payload = {
    "top_tag_limit": 50,
    "user_id": "user123",
    ...
}
monkeypatch.setenv("BL_STAGE_CONFIG_JSON", json.dumps(payload))
stage.run()
```

---

## Backward Compatibility

All stages support **all three resolution methods simultaneously**:

1. ✅ **Payload (BL_STAGE_CONFIG_JSON)** - New Phase 3 approach (preferred by orchestration)
2. ✅ **File path (BL_RUN_CONFIG_PATH)** - Legacy Phase 1/2 (still works)
3. ✅ **Env vars (BL00X_*)** - Legacy fallback (always works)

**Resolution always prefers payload first**, then falls back to file path, then to env vars.

This ensures:
- Existing code using legacy approaches continues to work
- New orchestration-driven code uses payload handoff
- Gradual migration possible without breaking changes

---

## Why Payload Handoff?

### Benefits Over Legacy Approaches

| Aspect | Legacy Env Vars | Legacy File Path | **Payload Handoff** |
|--------|-----------------|------------------|---------------------|
| **Centralization** | Scattered across stages | Single file, multiple resolvers | Single orchestration point |
| **Performance** | Many env var reads | Single file I/O | JSON in memory |
| **Explicitness** | Implicit, unclear precedence | Implicit file discovery | Explicit injection |
| **Testing** | Many monkeypatch calls | Complex path management | Single JSON string |
| **Validation** | Per-stage validation | Per-stage validation | Single validation point |
| **Traceability** | Hard to trace | Hard to trace | **Clear audit trail** |

---

## See Also

- [orchestration/config_resolver.py](src/orchestration/config_resolver.py) - Payload generation
- [orchestration/stage_runner.py](src/orchestration/stage_runner.py) - Payload injection
- [tests/test_orchestration_stage_payload_handoff.py](tests/test_orchestration_stage_payload_handoff.py) - Handoff validation
- [tests/test_alignment_resolved_context.py](tests/test_alignment_resolved_context.py) - Payload consumption example
