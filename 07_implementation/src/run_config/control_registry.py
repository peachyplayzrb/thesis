"""
Machine-readable control registry for the playlist generation pipeline.

Provides a single authoritative listing of user-facing controls, covering:
  control name → section → stage → type → valid range/values → default → expected effect surface

This module supports UNDO-N (Chapter 3 Section 3.12 configuration-as-method instrument claim).
It is purely declarative; importing it has no side effects.
"""

from __future__ import annotations

from typing import Any

from shared_utils.constants import DEFAULT_SCORING_COMPONENT_WEIGHTS

CONTROL_REGISTRY_SCHEMA_VERSION = "control-registry-v1"

# Each entry maps one control parameter to its audit metadata.
# Keys:
#   name          – the run-config key
#   section       – top-level run-config section (e.g. "profile_controls")
#   stage         – primary pipeline stage (e.g. "BL-004")
#   type          – "enum", "fraction", "positive_int", "bool", "float", "dict", "optional_int"
#   valid_values  – list of allowed values for enum/bool types; None for continuous types
#   valid_range   – human-readable range string for numeric/dict types; None for enum/bool
#   default       – the default value applied when the key is absent from run-config
#   effect_surface – brief description of what changes when this control is varied
CONTROL_REGISTRY: list[dict[str, Any]] = [
    # ── BL-004 profile_controls ──────────────────────────────────────────────
    {
        "name": "confidence_weighting_mode",
        "section": "profile_controls",
        "stage": "BL-004",
        "type": "enum",
        "valid_values": ["linear_half_bias", "direct_confidence", "none"],
        "valid_range": None,
        "default": "linear_half_bias",
        "effect_surface": "weights profile signal by seed match confidence; affects numeric feature contribution strength",
    },
    {
        "name": "confidence_bin_high_threshold",
        "section": "profile_controls",
        "stage": "BL-004",
        "type": "fraction",
        "valid_values": None,
        "valid_range": "[0.0, 1.0]",
        "default": 0.90,
        "effect_surface": "boundary that separates high-confidence from medium-confidence seeds in profile aggregation",
    },
    {
        "name": "top_tag_limit",
        "section": "profile_controls",
        "stage": "BL-004",
        "type": "positive_int",
        "valid_values": None,
        "valid_range": ">= 1",
        "default": 10,
        "effect_surface": "tag vocabulary size retained in preference profile; larger values increase semantic breadth",
    },
    {
        "name": "top_lead_genre_limit",
        "section": "profile_controls",
        "stage": "BL-004",
        "type": "positive_int",
        "valid_values": None,
        "valid_range": ">= 1",
        "default": 6,
        "effect_surface": "number of lead genres retained in preference profile; affects genre-match scoring weight",
    },
    {
        "name": "interaction_attribution_mode",
        "section": "profile_controls",
        "stage": "BL-004",
        "type": "enum",
        "valid_values": ["split_selected_types_equal_share", "primary_type_only"],
        "valid_range": None,
        "default": "split_selected_types_equal_share",
        "effect_surface": "governs how history vs influence interaction types share attribution weight in profile aggregation",
    },
    # ── BL-005 retrieval_controls ────────────────────────────────────────────
    {
        "name": "semantic_strong_keep_score",
        "section": "retrieval_controls",
        "stage": "BL-005",
        "type": "positive_int",
        "valid_values": None,
        "valid_range": ">= 0",
        "default": 2,
        "effect_surface": "minimum semantic score for unconditional candidate keep; raising this tightens semantic filter",
    },
    {
        "name": "semantic_min_keep_score",
        "section": "retrieval_controls",
        "stage": "BL-005",
        "type": "positive_int",
        "valid_values": None,
        "valid_range": ">= 0",
        "default": 1,
        "effect_surface": "minimum semantic score to pass for numeric check; raising this increases semantic strictness",
    },
    {
        "name": "numeric_support_min_pass",
        "section": "retrieval_controls",
        "stage": "BL-005",
        "type": "positive_int",
        "valid_values": None,
        "valid_range": ">= 0",
        "default": 1,
        "effect_surface": "minimum number of numeric dimensions that must pass threshold; raising reduces candidate pool",
    },
    {
        "name": "use_weighted_semantics",
        "section": "retrieval_controls",
        "stage": "BL-005",
        "type": "bool",
        "valid_values": [True, False],
        "valid_range": None,
        "default": False,
        "effect_surface": "enables tag-weighted semantic overlap scoring in retrieval; False = unweighted overlap",
    },
    {
        "name": "use_continuous_numeric",
        "section": "retrieval_controls",
        "stage": "BL-005",
        "type": "bool",
        "valid_values": [True, False],
        "valid_range": None,
        "default": False,
        "effect_surface": "switches numeric comparison from threshold-pass to continuous distance scoring",
    },
    {
        "name": "recency_years_min_offset",
        "section": "retrieval_controls",
        "stage": "BL-005",
        "type": "optional_int",
        "valid_values": None,
        "valid_range": ">= 0 or null",
        "default": None,
        "effect_surface": "minimum release year offset for recency gate; null disables recency filtering",
    },
    # ── BL-006 scoring_controls ──────────────────────────────────────────────
    {
        "name": "component_weights",
        "section": "scoring_controls",
        "stage": "BL-006",
        "type": "dict",
        "valid_values": None,
        "valid_range": "per-feature float in [0.0, 1.0]; values normalized to sum to 1.0",
        "default": dict(DEFAULT_SCORING_COMPONENT_WEIGHTS),
        "effect_surface": "relative weight per audio/semantic feature in composite score; changes track rank ordering",
    },
    {
        "name": "lead_genre_strategy",
        "section": "scoring_controls",
        "stage": "BL-006",
        "type": "enum",
        "valid_values": ["single_anchor", "weighted_top_lead_genres"],
        "valid_range": None,
        "default": "weighted_top_lead_genres",
        "effect_surface": "genre score uses single highest-weight genre (single_anchor) or weighted blend of top genres",
    },
    {
        "name": "semantic_overlap_strategy",
        "section": "scoring_controls",
        "stage": "BL-006",
        "type": "enum",
        "valid_values": ["overlap_only", "precision_aware"],
        "valid_range": None,
        "default": "precision_aware",
        "effect_surface": "semantic scoring method; precision_aware adjusts for profile tag concentration",
    },
    {
        "name": "enable_numeric_confidence_scaling",
        "section": "scoring_controls",
        "stage": "BL-006",
        "type": "bool",
        "valid_values": [True, False],
        "valid_range": None,
        "default": True,
        "effect_surface": "scales numeric component scores by profile confidence; False = unscaled numeric contributions",
    },
    {
        "name": "apply_bl003_influence_tracks",
        "section": "scoring_controls",
        "stage": "BL-006",
        "type": "bool",
        "valid_values": [True, False],
        "valid_range": None,
        "default": False,
        "effect_surface": "applies a score bonus to nominated influence tracks; False = no bonus applied",
    },
    # ── BL-007 assembly_controls ─────────────────────────────────────────────
    {
        "name": "target_size",
        "section": "assembly_controls",
        "stage": "BL-007",
        "type": "positive_int",
        "valid_values": None,
        "valid_range": ">= 1",
        "default": 10,
        "effect_surface": "desired playlist length; controls assembly length gate",
    },
    {
        "name": "min_score_threshold",
        "section": "assembly_controls",
        "stage": "BL-007",
        "type": "fraction",
        "valid_values": None,
        "valid_range": "[0.0, 1.0]",
        "default": 0.35,
        "effect_surface": "minimum composite score for inclusion; raising this tightens quality gate",
    },
    {
        "name": "max_per_genre",
        "section": "assembly_controls",
        "stage": "BL-007",
        "type": "positive_int",
        "valid_values": None,
        "valid_range": ">= 1",
        "default": 4,
        "effect_surface": "maximum tracks per genre in playlist; controls genre diversity constraint",
    },
    {
        "name": "utility_strategy",
        "section": "assembly_controls",
        "stage": "BL-007",
        "type": "enum",
        "valid_values": ["rank_round_robin", "utility_greedy"],
        "valid_range": None,
        "default": "rank_round_robin",
        "effect_surface": "selection ordering method; rank_round_robin interleaves genres, utility_greedy selects by utility score",
    },
    {
        "name": "utility_decay_factor",
        "section": "assembly_controls",
        "stage": "BL-007",
        "type": "fraction",
        "valid_values": None,
        "valid_range": "[0.0, 1.0]",
        "default": 0.0,
        "effect_surface": "rank decay pressure in utility-greedy mode; 0.0 disables decay",
    },
    {
        "name": "influence_policy_mode",
        "section": "assembly_controls",
        "stage": "BL-007",
        "type": "enum",
        "valid_values": ["competitive", "reserved_slots", "hybrid_override"],
        "valid_range": None,
        "default": "competitive",
        "effect_surface": "governs how influence tracks compete or are reserved in playlist assembly",
    },
    {
        "name": "transition_smoothness_weight",
        "section": "assembly_controls",
        "stage": "BL-007",
        "type": "fraction",
        "valid_values": None,
        "valid_range": "[0.0, 1.0]",
        "default": 0.0,
        "effect_surface": "weight for sequential transition coherence scoring; 0.0 disables smoothness optimization",
    },
    # ── BL-008 transparency_controls ────────────────────────────────────────
    {
        "name": "top_contributor_limit",
        "section": "transparency_controls",
        "stage": "BL-008",
        "type": "positive_int",
        "valid_values": None,
        "valid_range": ">= 1",
        "default": 3,
        "effect_surface": "number of scoring contributors surfaced per track in explanation output",
    },
    # ── BL-011 controllability_controls ──────────────────────────────────────
    {
        "name": "stricter_threshold_scale",
        "section": "controllability_controls",
        "stage": "BL-011",
        "type": "float",
        "valid_values": None,
        "valid_range": "(0.0, 1.0]",
        "default": 0.75,
        "effect_surface": "scale factor applied to numeric thresholds in stricter-threshold controllability scenarios",
    },
    {
        "name": "looser_threshold_scale",
        "section": "controllability_controls",
        "stage": "BL-011",
        "type": "float",
        "valid_values": None,
        "valid_range": ">= 1.0",
        "default": 1.25,
        "effect_surface": "scale factor applied to numeric thresholds in looser-threshold controllability scenarios",
    },
]


def build_control_registry_snapshot() -> dict[str, Any]:
    """Return a structured snapshot of the control registry for audit inclusion.

    The snapshot is suitable for embedding in a BL-009 run log or emitting as
    a standalone artefact.  It is generated from the static CONTROL_REGISTRY
    list and contains no run-time state.
    """
    sections: list[str] = []
    stages: list[str] = []
    for entry in CONTROL_REGISTRY:
        section = str(entry.get("section", ""))
        stage = str(entry.get("stage", ""))
        if section and section not in sections:
            sections.append(section)
        if stage and stage not in stages:
            stages.append(stage)

    return {
        "schema_version": CONTROL_REGISTRY_SCHEMA_VERSION,
        "entry_count": len(CONTROL_REGISTRY),
        "sections": sections,
        "stages": stages,
        "controls": list(CONTROL_REGISTRY),
    }
