"""BL-007 playlist assembly stage executor for BL-011 controllability scenarios."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, cast

from shared_utils.io_utils import canonical_json_hash, sha256_of_text
from controllability.reporting import csv_text, json_text


def execute_playlist_stage(scoring_stage: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    scenario_id = str(scenario["scenario_id"])
    assembly_config = cast(dict[str, Any], scenario["assembly"])
    candidates = cast(list[dict[str, object]], scoring_stage["scored_rows"])

    playlist: list[dict[str, object]] = []
    trace_rows: list[dict[str, object]] = []
    rule_hits = {"R1_score_threshold": 0, "R2_genre_cap": 0, "R3_consecutive_run": 0, "R4_length_cap": 0}

    for cand in candidates:
        track_id = str(cand["track_id"])
        lead_genre = str(cand["lead_genre"])
        final_score = float(cast(Any, cand["final_score"]))
        score_rank = int(cast(Any, cand["rank"]))
        decision = "included"
        exclusion_reason = ""

        if len(playlist) >= int(assembly_config["target_size"]):
            decision = "excluded"
            exclusion_reason = "length_cap_reached"
            rule_hits["R4_length_cap"] += 1
        elif final_score < float(assembly_config["min_score_threshold"]):
            decision = "excluded"
            exclusion_reason = "below_score_threshold"
            rule_hits["R1_score_threshold"] += 1
        elif sum(1 for track in playlist if track["lead_genre"] == lead_genre) >= int(
            assembly_config["max_per_genre"]
        ):
            decision = "excluded"
            exclusion_reason = "genre_cap_exceeded"
            rule_hits["R2_genre_cap"] += 1
        elif len(playlist) >= int(assembly_config["max_consecutive"]) and all(
            track["lead_genre"] == lead_genre
            for track in playlist[-int(assembly_config["max_consecutive"]):]
        ):
            decision = "excluded"
            exclusion_reason = "consecutive_genre_run"
            rule_hits["R3_consecutive_run"] += 1

        playlist_position: int | str = ""
        if decision == "included":
            playlist_position = len(playlist) + 1
            playlist.append(
                {
                    "playlist_position": playlist_position,
                    "track_id": track_id,
                    "lead_genre": lead_genre,
                    "final_score": round(final_score, 6),
                    "score_rank": score_rank,
                }
            )

        trace_rows.append(
            {
                "score_rank": score_rank,
                "track_id": track_id,
                "lead_genre": lead_genre,
                "final_score": round(final_score, 6),
                "decision": decision,
                "playlist_position": playlist_position,
                "exclusion_reason": exclusion_reason,
            }
        )

    playlist_obj = {
        "run_id": f"BL011-{scenario_id.upper()}-BL007-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}",
        "task": "BL-007",
        "scenario_id": scenario_id,
        "config": dict(assembly_config),
        "playlist_length": len(playlist),
        "tracks": playlist,
    }
    run_id = str(playlist_obj["run_id"])
    report = {
        "run_id": run_id,
        "task": "BL-007",
        "scenario_id": scenario_id,
        "config": dict(assembly_config),
        "counts": {
            "candidates_evaluated": len(candidates),
            "tracks_included": len(playlist),
            "tracks_excluded": len(trace_rows) - len(playlist),
        },
        "rule_hits": rule_hits,
        "playlist_genre_mix": {
            genre: sum(1 for track in playlist if track["lead_genre"] == genre)
            for genre in sorted(str(track["lead_genre"]) for track in playlist)
        },
        "playlist_score_range": {
            "max": round(max(float(cast(Any, track["final_score"])) for track in playlist), 6) if playlist else 0.0,
            "min": round(min(float(cast(Any, track["final_score"])) for track in playlist), 6) if playlist else 0.0,
        },
    }

    playlist_text = json_text(playlist_obj)
    trace_text = csv_text(
        [
            "score_rank",
            "track_id",
            "lead_genre",
            "final_score",
            "decision",
            "playlist_position",
            "exclusion_reason",
        ],
        trace_rows,
    )
    report_text = json_text(report)

    return {
        "playlist": playlist_obj,
        "trace_rows": trace_rows,
        "report": report,
        "texts": {
            "playlist.json": playlist_text,
            "bl007_assembly_trace.csv": trace_text,
            "bl007_assembly_report.json": report_text,
        },
        "stable_hashes": {
            "assembly_trace_hash": sha256_of_text(trace_text),
            "playlist_output_hash": canonical_json_hash(playlist),
        },
    }
