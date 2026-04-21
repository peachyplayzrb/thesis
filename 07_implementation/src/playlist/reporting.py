"""Diagnostics builders for BL-007 playlist assembly."""

from __future__ import annotations

import math
from collections import Counter
from typing import NamedTuple

from shared_utils.parsing import safe_float, safe_int


class _GenreMetrics(NamedTuple):
    """Named return from _extract_genre_metrics."""

    genre_counts: Counter[str]
    dominant_genre_share: float
    genre_switch_rate: float


class _TransitionMetrics(NamedTuple):
    """Named return from _extract_transition_metrics."""

    mean_adjacent_transition_distance: float
    max_adjacent_transition_distance: float
    transition_pair_count: int


class _RankingMetrics(NamedTuple):
    """Named return from _extract_ranking_metrics."""

    mean_selected_rank: float
    median_selected_rank: int
    rank_span: int


class _ExclusionStats(NamedTuple):
    """Named return from _compute_top100_exclusion_stats."""

    top_100_exclusion_rate: float
    dominant_reason: str | None


def build_undersized_diagnostics(
    target_size: int,
    playlist_size: int,
    candidates_evaluated: int,
    trace_rows: list[dict[str, object]],
) -> dict[str, object]:
    """Build diagnostics for undersized playlist outcomes."""
    is_undersized = playlist_size < target_size
    exclusion_counts = Counter(
        str(row.get("exclusion_reason") or "")
        for row in trace_rows
        if row.get("decision") == "excluded" and row.get("exclusion_reason")
    )

    reasons: list[str] = []
    if is_undersized:
        shortfall = target_size - playlist_size
        reasons.append(
            f"final playlist length is {playlist_size}/{target_size} (shortfall={shortfall})"
        )
        if candidates_evaluated < target_size:
            reasons.append(
                f"candidate pool is smaller than target size ({candidates_evaluated} < {target_size})"
            )
        for reason, count in exclusion_counts.most_common(3):
            reasons.append(f"exclusion pressure: {reason} ({count} rows)")

    return {
        "is_undersized": is_undersized,
        "target_size": target_size,
        "actual_size": playlist_size,
        "shortfall": max(0, target_size - playlist_size),
        "exclusion_reason_counts": dict(exclusion_counts),
        "reasons": reasons,
    }


def build_rank_continuity_diagnostics(
    playlist: list[dict[str, object]],
) -> dict[str, object]:
    """Build rank continuity and rank-cliff diagnostics for selected tracks."""
    selected_ranks = [safe_int(track["score_rank"], 0) for track in playlist]
    selected_scores = [safe_float(track["final_score"], 0.0) for track in playlist]
    max_selected_rank = max(selected_ranks) if selected_ranks else 0
    median_selected_rank = (
        sorted(selected_ranks)[len(selected_ranks) // 2] if selected_ranks else 0
    )
    rank_2_to_3_gap = 0.0
    if len(selected_scores) >= 3:
        rank_2_to_3_gap = round(selected_scores[1] - selected_scores[2], 6)

    return {
        "selected_ranks": selected_ranks,
        "max_selected_rank": max_selected_rank,
        "median_selected_rank": median_selected_rank,
        "rank_2_to_3_score_gap": rank_2_to_3_gap,
        "rank_cliff_detected": rank_2_to_3_gap >= 0.1,
    }


def build_assembly_pressure_diagnostics(
    trace_rows: list[dict[str, object]],
) -> dict[str, object]:
    """Build diagnostics for exclusion pressure within the top-ranked window."""
    top_100_rows = [row for row in trace_rows if safe_int(row["score_rank"], 0) <= 100]
    top_100_excluded = [row for row in top_100_rows if row["decision"] == "excluded"]
    reason_counts = Counter(
        str(row.get("exclusion_reason") or "")
        for row in top_100_excluded
        if row.get("exclusion_reason")
    )
    return {
        "top_100_considered": len(top_100_rows),
        "top_100_excluded": len(top_100_excluded),
        "top_100_exclusion_reason_counts": dict(reason_counts),
        "dominant_top_100_exclusion_reason": (
            reason_counts.most_common(1)[0][0] if reason_counts else None
        ),
    }


def _extract_genre_metrics(
    playlist: list[dict[str, object]],
    playlist_size: int,
) -> _GenreMetrics:
    """Extract genre diversity metrics from playlist."""
    genre_counts = Counter(
        str(track.get("lead_genre", "")).strip().lower()
        for track in playlist
        if str(track.get("lead_genre", "")).strip()
    )
    adjacent_pairs = list(zip(playlist[:-1], playlist[1:], strict=False))
    switch_count = sum(
        1
        for left, right in adjacent_pairs
        if str(left.get("lead_genre", "")).strip().lower()
        != str(right.get("lead_genre", "")).strip().lower()
    )
    genre_switch_rate = (
        round(switch_count / max(1, len(adjacent_pairs)), 6)
        if adjacent_pairs
        else 0.0
    )
    dominant_genre_count = max(genre_counts.values()) if genre_counts else 0
    dominant_genre_share = (
        round(dominant_genre_count / max(1, playlist_size), 6)
        if playlist_size > 0
        else 0.0
    )
    return _GenreMetrics(
        genre_counts=genre_counts,
        dominant_genre_share=dominant_genre_share,
        genre_switch_rate=genre_switch_rate,
    )


def _compute_genre_entropy_metrics(
    genre_counts: Counter[str],
    playlist_size: int,
) -> float:
    """Compute normalized Shannon entropy for genre distribution."""
    entropy_bits = 0.0
    for count in genre_counts.values():
        probability = count / max(1, playlist_size)
        if probability > 0:
            entropy_bits += -probability * math.log2(probability)
    max_entropy_bits = math.log2(len(genre_counts)) if len(genre_counts) > 1 else 0.0
    normalized_entropy = (
        round(entropy_bits / max_entropy_bits, 6)
        if max_entropy_bits > 0
        else 0.0
    )
    return normalized_entropy


def _extract_transition_metrics(
    transition_diagnostics: dict[str, object],
) -> _TransitionMetrics:
    """Extract transition smoothness metrics from diagnostics."""
    mean_smoothness = safe_float(transition_diagnostics.get("mean_smoothness"), 0.0)
    min_smoothness = safe_float(transition_diagnostics.get("min_smoothness"), 0.0)
    max_adjacent_transition_distance = round(1.0 - min_smoothness, 6)
    mean_adjacent_transition_distance = round(1.0 - mean_smoothness, 6)
    transition_pair_count = safe_int(transition_diagnostics.get("pair_count"), 0)
    return _TransitionMetrics(
        mean_adjacent_transition_distance=mean_adjacent_transition_distance,
        max_adjacent_transition_distance=max_adjacent_transition_distance,
        transition_pair_count=transition_pair_count,
    )


def _extract_ranking_metrics(
    playlist: list[dict[str, object]],
) -> _RankingMetrics:
    """Extract ranking and score metrics from playlist."""
    selected_ranks = [safe_int(track.get("score_rank"), 0) for track in playlist]
    selected_ranks = [rank for rank in selected_ranks if rank > 0]
    mean_selected_rank = (
        round(sum(selected_ranks) / max(1, len(selected_ranks)), 6)
        if selected_ranks
        else 0.0
    )
    median_selected_rank = (
        sorted(selected_ranks)[len(selected_ranks) // 2]
        if selected_ranks
        else 0
    )
    rank_span = (
        max(selected_ranks) - min(selected_ranks)
        if selected_ranks
        else 0
    )
    return _RankingMetrics(
        mean_selected_rank=mean_selected_rank,
        median_selected_rank=median_selected_rank,
        rank_span=rank_span,
    )


def _compute_top100_exclusion_stats(
    trace_rows: list[dict[str, object]],
) -> _ExclusionStats:
    """Compute exclusion metrics for top-100 ranked candidates."""
    top_100_rows = [row for row in trace_rows if safe_int(row.get("score_rank"), 0) <= 100]
    top_100_excluded = [row for row in top_100_rows if str(row.get("decision", "")) == "excluded"]
    top_100_exclusion_rate = (
        round(len(top_100_excluded) / max(1, len(top_100_rows)), 6)
        if top_100_rows
        else 0.0
    )
    top_100_reason_counts = Counter(
        str(row.get("exclusion_reason") or "")
        for row in top_100_excluded
        if str(row.get("exclusion_reason") or "")
    )
    dominant_reason = (
        top_100_reason_counts.most_common(1)[0][0]
        if top_100_reason_counts
        else None
    )
    return _ExclusionStats(
        top_100_exclusion_rate=top_100_exclusion_rate,
        dominant_reason=dominant_reason,
    )


def _build_diversity_summary(
    genre_counts: Counter[str],
    dominant_genre_share: float,
    normalized_entropy: float,
    genre_switch_rate: float,
) -> dict[str, object]:
    """Build diversity_distribution_summary dict."""
    return {
        "genre_counts": dict(genre_counts),
        "unique_genre_count": len(genre_counts),
        "dominant_genre_share": dominant_genre_share,
        "normalized_genre_entropy": normalized_entropy,
        "genre_switch_rate": genre_switch_rate,
    }


def _build_novelty_summary(
    transition_pair_count: int,
    mean_adjacent_transition_distance: float,
    max_adjacent_transition_distance: float,
) -> dict[str, object]:
    """Build novelty_distance_summary dict."""
    return {
        "transition_pair_count": transition_pair_count,
        "mean_adjacent_transition_distance": mean_adjacent_transition_distance,
        "max_adjacent_transition_distance": max_adjacent_transition_distance,
    }


def _build_ordering_summary(
    mean_selected_rank: float,
    median_selected_rank: int,
    rank_span: int,
    top_100_exclusion_rate: float,
    dominant_top_100_exclusion_reason: str | None,
) -> dict[str, object]:
    """Build ordering_pressure_summary dict."""
    return {
        "mean_selected_rank": mean_selected_rank,
        "median_selected_rank": median_selected_rank,
        "selected_rank_span": rank_span,
        "top_100_exclusion_rate": top_100_exclusion_rate,
        "dominant_top_100_exclusion_reason": dominant_top_100_exclusion_reason,
    }


def build_tradeoff_metrics_summary(
    *,
    playlist: list[dict[str, object]],
    trace_rows: list[dict[str, object]],
    transition_diagnostics: dict[str, object],
) -> dict[str, object]:
    """Build compact cross-objective trade-off metrics for BL-007 evidence surfaces."""
    playlist_size = len(playlist)
    genre_counts, dominant_genre_share, genre_switch_rate = _extract_genre_metrics(playlist, playlist_size)
    normalized_entropy = _compute_genre_entropy_metrics(genre_counts, playlist_size)
    mean_adjacent_transition_distance, max_adjacent_transition_distance, transition_pair_count = _extract_transition_metrics(
        transition_diagnostics
    )
    mean_selected_rank, median_selected_rank, rank_span = _extract_ranking_metrics(playlist)
    top_100_exclusion_rate, dominant_top_100_exclusion_reason = _compute_top100_exclusion_stats(trace_rows)

    return {
        "playlist_size": playlist_size,
        "diversity_distribution_summary": _build_diversity_summary(
            genre_counts,
            dominant_genre_share,
            normalized_entropy,
            genre_switch_rate,
        ),
        "novelty_distance_summary": _build_novelty_summary(
            transition_pair_count,
            mean_adjacent_transition_distance,
            max_adjacent_transition_distance,
        ),
        "ordering_pressure_summary": _build_ordering_summary(
            mean_selected_rank,
            median_selected_rank,
            rank_span,
            top_100_exclusion_rate,
            dominant_top_100_exclusion_reason,
        ),
    }


def build_influence_effectiveness_diagnostics(
    trace_rows: list[dict[str, object]],
    *,
    influence_track_ids: set[str],
    candidate_track_ids: set[str],
    policy_mode: str,
    influence_enabled: bool,
    reserved_slot_target: int,
) -> dict[str, object]:
    """Summarize effectiveness of influence-policy controls for BL-007."""
    requested_count = len(influence_track_ids)
    matched_track_ids = {track_id for track_id in influence_track_ids if track_id in candidate_track_ids}
    matched_count = len(matched_track_ids)

    influence_included_rows = [
        row for row in trace_rows
        if row.get("decision") == "included" and bool(row.get("influence_requested", False))
    ]
    included_count = len(influence_included_rows)

    inclusion_path_counts = Counter(
        str(row.get("inclusion_path") or "competitive")
        for row in influence_included_rows
    )
    reserved_slot_included = int(inclusion_path_counts.get("reserved_slot", 0))

    effectiveness_rate = round(float(included_count) / float(matched_count), 6) if matched_count > 0 else 0.0
    slot_utilization = (
        round(float(reserved_slot_included) / float(reserved_slot_target), 6)
        if reserved_slot_target > 0
        else 0.0
    )

    return {
        "influence_enabled": bool(influence_enabled),
        "policy_mode": str(policy_mode),
        "requested_track_ids_count": requested_count,
        "matched_candidate_track_ids_count": matched_count,
        "included_track_ids_count": included_count,
        "effectiveness_rate": effectiveness_rate,
        "reserved_slot_target": int(reserved_slot_target),
        "reserved_slot_included_count": reserved_slot_included,
        "reserved_slot_utilization_rate": slot_utilization,
        "inclusion_path_counts": dict(inclusion_path_counts),
    }


def build_assembly_detail_log(
    trace_rows: list[dict[str, object]],
    *,
    top_k: int = 100,
) -> dict[str, object]:
    """Build detail rows for top-ranked candidate decisions."""
    top_window = max(1, int(top_k))
    top_100_rows = [row for row in trace_rows if safe_int(row["score_rank"], 0) <= top_window]
    included_ranks = sorted(
        safe_int(row["score_rank"], 0)
        for row in trace_rows
        if row["decision"] == "included"
    )

    detail_rows: list[dict[str, object]] = []
    for row in top_100_rows:
        current_rank = safe_int(row["score_rank"], 0)
        alternative_rank = next(
            (rank for rank in included_ranks if rank > current_rank),
            None,
        )
        detail_rows.append(
            {
                "score_rank": current_rank,
                "track_id": row["track_id"],
                "final_score": safe_float(row["final_score"], 0.0),
                "decision": row["decision"],
                "exclusion_reason": row.get("exclusion_reason", ""),
                "selected_alternative_rank": alternative_rank,
            }
        )

    return {
        "top_rank_window": top_window,
        "rows": detail_rows,
    }


def build_opportunity_cost_diagnostics(
    trace_rows: list[dict[str, object]],
    *,
    top_k_examples: int = 10,
) -> dict[str, object]:
    """Estimate score opportunity cost from excluded candidates by exclusion reason."""
    excluded_rows = [row for row in trace_rows if row.get("decision") == "excluded"]
    top_examples_limit = max(1, int(top_k_examples))
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in excluded_rows:
        reason = str(row.get("exclusion_reason") or "unspecified")
        grouped.setdefault(reason, []).append(row)

    summary: dict[str, dict[str, object]] = {}
    for reason, rows in grouped.items():
        score_values = [safe_float(row.get("final_score"), 0.0) for row in rows]
        score_values.sort(reverse=True)
        sorted_rows = sorted(
            rows,
            key=lambda row: (
                -safe_float(row.get("final_score"), 0.0),
                safe_int(row.get("score_rank"), 0),
                str(row.get("track_id", "")),
            ),
        )
        summary[reason] = {
            "count": len(rows),
            "mean_score": round(sum(score_values) / max(1, len(score_values)), 6),
            "max_score": round(score_values[0], 6) if score_values else 0.0,
            "top_examples": [
                {
                    "track_id": row.get("track_id", ""),
                    "score_rank": safe_int(row.get("score_rank"), 0),
                    "final_score": round(safe_float(row.get("final_score"), 0.0), 6),
                }
                for row in sorted_rows[:top_examples_limit]
            ],
        }

    first_blocking_reason = None
    ranked_excluded = sorted(
        excluded_rows,
        key=lambda row: (
            safe_int(row.get("score_rank"), 0),
            str(row.get("track_id", "")),
        ),
    )
    if ranked_excluded:
        first_blocking_reason = str(ranked_excluded[0].get("exclusion_reason") or "unspecified")

    return {
        "excluded_count": len(excluded_rows),
        "by_reason": summary,
        "fill_failure_frontier_reason": first_blocking_reason,
    }
