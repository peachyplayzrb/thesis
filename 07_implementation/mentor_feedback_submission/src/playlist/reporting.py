"""Diagnostics builders for BL-007 playlist assembly outputs."""

from __future__ import annotations

from collections import Counter

from shared_utils.parsing import safe_float, safe_int


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


def build_influence_effectiveness_diagnostics(
    trace_rows: list[dict[str, object]],
    *,
    influence_track_ids: set[str],
    candidate_track_ids: set[str],
    policy_mode: str,
    influence_enabled: bool,
    reserved_slot_target: int,
) -> dict[str, object]:
    """Summarize how influence-policy controls affected BL-007 inclusion outcomes."""
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
