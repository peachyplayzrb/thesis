"""
Shared type definitions and data contracts for implementation stages.

Provides TypedDicts and other type hints for data structures that are used
across multiple stages.
"""

from typing import Any, TypedDict


class NumericFeatureSpec(TypedDict):
    """Specification for a numeric feature dimension.
    
    Attributes:
        candidate_column: Column name in candidate dataset
        threshold: Maximum allowed distance for matching
        circular: Whether this is a circular dimension (e.g., key/mode)
    """
    candidate_column: str
    threshold: float
    circular: bool


class RunConfigControls(TypedDict):
    """Run configuration controls resolved at runtime.
    
    Attributes:
        config_source: Source of configuration ("run_config" or "environment")
        run_config_path: Path to run config file or None
        run_config_schema_version: Schema version or None
        profile_top_lead_genre_limit: Max lead genres in profile
        profile_top_tag_limit: Max tags in profile
        profile_top_genre_limit: Max genres in profile
        semantic_strong_keep_score: Threshold for strong semantic keep
        semantic_min_keep_score: Threshold for minimum semantic keep
        numeric_support_min_pass: Minimum numeric feature support count
        numeric_thresholds: Dict of numeric threshold overrides
    """
    config_source: str
    run_config_path: str | None
    run_config_schema_version: str | None
    profile_top_lead_genre_limit: int
    profile_top_tag_limit: int
    profile_top_genre_limit: int
    semantic_strong_keep_score: int
    semantic_min_keep_score: int
    numeric_support_min_pass: int
    numeric_thresholds: dict[str, Any]


class CsvRow(TypedDict):
    """Base type for CSV row data.
    
    Maps column names to string values as parsed by csv.DictReader.
    """
    pass  # Dict[str, str] - subclasses will extend this
