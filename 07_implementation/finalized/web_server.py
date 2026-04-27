"""Minimal local web + API wrapper for the thesis pipeline.

Runs from any working directory by resolving paths from this script location.
This wrapper does not modify core pipeline logic under src.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from copy import deepcopy
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent
IMPL_ROOT = BASE_DIR.parent
THESIS_WRAPPER = IMPL_ROOT / "main.py"
INDEX_FILE = BASE_DIR / "web" / "index.html"
CONFIG_DIR = IMPL_ROOT / "config" / "profiles"
RUN_CONFIG_TEMPLATE_PATH = IMPL_ROOT / "src" / "run_config" / "configs" / "templates" / "run_config_template_v1.json"

BL013_LATEST_PATH = IMPL_ROOT / "src" / "orchestration" / "outputs" / "bl013_orchestration_run_latest.json"
BL014_LATEST_PATH = IMPL_ROOT / "src" / "quality" / "outputs" / "bl014_sanity_report.json"

ARTIFACT_PATHS: dict[str, Path] = {
    "bl013_latest": BL013_LATEST_PATH,
    "bl014_latest": BL014_LATEST_PATH,
    "bl003_summary": IMPL_ROOT / "src" / "alignment" / "outputs" / "bl003_ds001_spotify_summary.json",
    "bl004_profile": IMPL_ROOT / "src" / "profile" / "outputs" / "bl004_preference_profile.json",
    "bl005_filtered": IMPL_ROOT / "src" / "retrieval" / "outputs" / "bl005_filtered_candidates.csv",
    "bl006_scored": IMPL_ROOT / "src" / "scoring" / "outputs" / "bl006_scored_candidates.csv",
    "bl007_playlist": IMPL_ROOT / "src" / "playlist" / "outputs" / "playlist.json",
    "bl008_payloads": IMPL_ROOT / "src" / "transparency" / "outputs" / "bl008_explanation_payloads.json",
    "bl009_log": IMPL_ROOT / "src" / "observability" / "outputs" / "bl009_run_observability_log.json",
}

STAGE_EXPLAINER_MAP: dict[str, dict[str, Any]] = {
    "bl003": {
        "label": "BL-003 Alignment",
        "script": "src/alignment/main.py",
        "description": "Align imported Spotify interactions to DS-001 seed tracks.",
        "artifacts": ["bl003_summary"],
    },
    "bl004": {
        "label": "BL-004 Profile",
        "script": "src/profile/main.py",
        "description": "Build a deterministic preference profile from aligned seed data.",
        "artifacts": ["bl004_profile"],
    },
    "bl005": {
        "label": "BL-005 Retrieval",
        "script": "src/retrieval/main.py",
        "description": "Filter candidate corpus against profile and control thresholds.",
        "artifacts": ["bl005_filtered"],
    },
    "bl006": {
        "label": "BL-006 Scoring",
        "script": "src/scoring/main.py",
        "description": "Score retained candidates using weighted scoring components.",
        "artifacts": ["bl006_scored"],
    },
    "bl007": {
        "label": "BL-007 Playlist",
        "script": "src/playlist/main.py",
        "description": "Assemble final playlist with deterministic rule checks.",
        "artifacts": ["bl007_playlist"],
    },
    "bl008": {
        "label": "BL-008 Transparency",
        "script": "src/transparency/main.py",
        "description": "Build mechanism-linked explanations for selected tracks.",
        "artifacts": ["bl008_payloads"],
    },
    "bl009": {
        "label": "BL-009 Observability",
        "script": "src/observability/main.py",
        "description": "Record run-level observability and lineage diagnostics.",
        "artifacts": ["bl009_log"],
    },
}

PREVIEW_MAX_CHARS = 20000
EXPLAINER_TRACK_LIMIT = 10
EXPLAINER_TRACK_LIMIT_MAX = 50


def _iso_utc_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat()


def _config_choices() -> list[str]:
    try:
        names = [
            path.name
            for path in CONFIG_DIR.iterdir()
            if path.name.lower().endswith(".json") and path.is_file()
        ]
    except OSError:
        return []

    names.sort()
    return [f"config/profiles/{name}" for name in names]


def _resolve_config_path(config_path: str) -> tuple[Path | None, str | None]:
    normalized = str(config_path).strip()
    if not normalized:
        return None, None

    safe_normalized = normalized.replace("\\", "/")
    if ".." in safe_normalized:
        return None, "Invalid config path"

    if not safe_normalized.lower().endswith(".json"):
        return None, "Config must be a JSON file"

    if safe_normalized.startswith("config/"):
        candidate = IMPL_ROOT / safe_normalized
    else:
        candidate = CONFIG_DIR / safe_normalized

    try:
        resolved = candidate.resolve()
    except OSError:
        return None, "Invalid config path"

    config_root = CONFIG_DIR.resolve()
    if config_root not in resolved.parents or not resolved.is_file():
        return None, "Config file not found under config/profiles"

    return resolved, None


def _build_run_command(
    *,
    resolved_config: Path | None,
    validate_only: bool,
    continue_on_error: bool,
) -> list[str]:
    command = [sys.executable, str(THESIS_WRAPPER)]
    if resolved_config is not None:
        command.extend(["--run-config", str(resolved_config)])
    if validate_only:
        command.append("--validate-only")
    if continue_on_error:
        command.append("--continue-on-error")
    return command


def _artifact_manifest() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for name, path in ARTIFACT_PATHS.items():
        exists = path.is_file()
        items.append(
            {
                "name": name,
                "path": str(path.relative_to(IMPL_ROOT)).replace("\\", "/"),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else None,
                "modified_utc": _iso_utc_mtime(path) if exists else None,
            }
        )
    return items


def _load_json_or_none(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _strip_comment_fields(payload: Any) -> Any:
    if isinstance(payload, dict):
        stripped: dict[str, Any] = {}
        for key, value in payload.items():
            if str(key).endswith("_comment"):
                continue
            stripped[str(key)] = _strip_comment_fields(value)
        return stripped
    if isinstance(payload, list):
        return [_strip_comment_fields(item) for item in payload]
    return payload


def _extract_comment_fields(payload: Any, prefix: list[str] | None = None) -> dict[str, str]:
    comments: dict[str, str] = {}
    path_prefix = list(prefix) if prefix else []
    if not isinstance(payload, dict):
        return comments

    for key, value in payload.items():
        key_text = str(key)
        if key_text.endswith("_comment") and isinstance(value, str):
            target_key = key_text[: -len("_comment")]
            target_path = ".".join(path_prefix + [target_key])
            comments[target_path] = value
            continue
        if isinstance(value, dict):
            comments.update(_extract_comment_fields(value, path_prefix + [key_text]))
    return comments


def _load_template_config_payload() -> dict[str, Any]:
    payload = _load_json_or_none(RUN_CONFIG_TEMPLATE_PATH)
    if payload is None:
        return {}
    stripped = _strip_comment_fields(payload)
    return stripped if isinstance(stripped, dict) else {}


def _load_default_run_config_payload() -> dict[str, Any]:
    src_root = IMPL_ROOT / "src"
    inserted = False
    src_root_text = str(src_root)
    if src_root_text not in sys.path:
        sys.path.insert(0, src_root_text)
        inserted = True

    try:
        from run_config.run_config_utils import DEFAULT_RUN_CONFIG  # type: ignore

        if isinstance(DEFAULT_RUN_CONFIG, dict):
            return deepcopy(DEFAULT_RUN_CONFIG)
    except Exception:
        pass
    finally:
        if inserted:
            try:
                sys.path.remove(src_root_text)
            except ValueError:
                pass

    return _load_template_config_payload()


def _flatten_config_settings(payload: Any, prefix: str = "") -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        for key in sorted(payload):
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            items.extend(_flatten_config_settings(payload[key], next_prefix))
        return items

    setting_type = "string"
    if isinstance(payload, bool):
        setting_type = "bool"
    elif isinstance(payload, int):
        setting_type = "int"
    elif isinstance(payload, float):
        setting_type = "float"
    elif isinstance(payload, list):
        setting_type = "list"
    elif isinstance(payload, dict):
        setting_type = "object"
    elif payload is None:
        setting_type = "null"

    items.append({"path": prefix, "default": payload, "type": setting_type})
    return items


def _setting_choices(path: str) -> list[str] | None:
    if path.endswith("_validation_policy"):
        return ["allow", "warn", "strict"]
    if path == "control_mode.validation_profile":
        return ["strict", "explore"]
    if path == "assembly_controls.utility_strategy":
        return ["rank_round_robin", "utility_greedy"]
    if path == "assembly_controls.influence_policy_mode":
        return ["competitive", "reserved_slots", "hybrid_override"]
    if path.endswith("profile_numeric_confidence_mode"):
        return ["direct", "blended"]
    if path == "seed_controls.temporal_controls.reference_mode":
        return ["system", "fixed"]
    if path == "orchestration_controls.refresh_seed_policy":
        return ["auto_if_stale", "always", "never"]
    return None


def _setting_description(path: str, comments: dict[str, str]) -> str:
    if path in comments and comments[path].strip():
        return comments[path].strip()
    name = path.split(".")[-1].replace("_", " ")
    section = path.split(".")[0].replace("_", " ")
    return f"Controls {name} in {section}."


def _config_builder_schema_payload() -> dict[str, Any]:
    defaults = _load_default_run_config_payload()
    template_with_comments = _load_json_or_none(RUN_CONFIG_TEMPLATE_PATH) or {}
    comments = _extract_comment_fields(template_with_comments)
    registry_metadata = _control_registry_metadata_by_path()

    settings = _flatten_config_settings(defaults)
    for row in settings:
        path = str(row.get("path", ""))
        metadata = registry_metadata.get(path, {})
        row["description"] = metadata.get("effect_surface") or _setting_description(path, comments)
        row["section"] = path.split(".")[0] if path else ""
        row["stage"] = metadata.get("stage") or _stage_for_setting_path(path)
        row["valid_range"] = metadata.get("valid_range")
        row["advanced"] = _is_advanced_setting_path(path)
        choices = metadata.get("valid_values") or _setting_choices(path)
        if choices is not None:
            row["choices"] = choices

    return {
        "schema_version": defaults.get("schema_version", "run-config-v1"),
        "setting_count": len(settings),
        "settings": settings,
        "defaults": defaults,
    }


def _stage_for_setting_path(path: str) -> str:
    section = path.split(".")[0] if path else ""
    mapping = {
        "input_scope": "BL-001/BL-002",
        "interaction_scope": "BL-003",
        "influence_tracks": "BL-003",
        "seed_controls": "BL-003",
        "ingestion_controls": "BL-001/BL-002",
        "profile_controls": "BL-004",
        "retrieval_controls": "BL-005",
        "scoring_controls": "BL-006",
        "assembly_controls": "BL-007",
        "transparency_controls": "BL-008",
        "observability_controls": "BL-009",
        "reporting_controls": "BL-008",
        "controllability_controls": "BL-011",
        "orchestration_controls": "BL-013",
    }
    return mapping.get(section, "Global")


def _is_advanced_setting_path(path: str) -> bool:
    basic_paths = {
        "control_mode.validation_profile",
        "input_scope.include_top_tracks",
        "input_scope.include_saved_tracks",
        "input_scope.include_playlists",
        "input_scope.include_recently_played",
        "interaction_scope.include_interaction_types",
        "influence_tracks.enabled",
        "influence_tracks.track_ids",
        "influence_tracks.preference_weight",
        "seed_controls.match_rate_min_threshold",
        "seed_controls.fuzzy_matching.enabled",
        "seed_controls.fuzzy_matching.artist_threshold",
        "seed_controls.fuzzy_matching.title_threshold",
        "seed_controls.fuzzy_matching.combined_threshold",
        "profile_controls.top_tag_limit",
        "profile_controls.top_genre_limit",
        "profile_controls.top_lead_genre_limit",
        "retrieval_controls.semantic_strong_keep_score",
        "retrieval_controls.semantic_min_keep_score",
        "retrieval_controls.numeric_support_min_pass",
        "retrieval_controls.numeric_thresholds",
        "scoring_controls.component_weights",
        "scoring_controls.numeric_thresholds",
        "scoring_controls.apply_bl003_influence_tracks",
        "assembly_controls.target_size",
        "assembly_controls.min_score_threshold",
        "assembly_controls.max_per_genre",
        "assembly_controls.max_consecutive",
        "assembly_controls.influence_policy_mode",
        "transparency_controls.top_contributor_limit",
        "observability_controls.diagnostic_sample_limit",
        "orchestration_controls.continue_on_error",
        "orchestration_controls.refresh_seed_policy",
    }
    return path not in basic_paths


def _control_registry_metadata_by_path() -> dict[str, dict[str, Any]]:
    src_root = IMPL_ROOT / "src"
    inserted = False
    src_root_text = str(src_root)
    if src_root_text not in sys.path:
        sys.path.insert(0, src_root_text)
        inserted = True

    try:
        from run_config.control_registry import CONTROL_REGISTRY  # type: ignore

        metadata: dict[str, dict[str, Any]] = {}
        for entry in CONTROL_REGISTRY:
            section = str(entry.get("section", "")).strip()
            name = str(entry.get("name", "")).strip()
            if not section or not name:
                continue
            metadata[f"{section}.{name}"] = dict(entry)
        return metadata
    except Exception:
        return {}
    finally:
        if inserted:
            try:
                sys.path.remove(src_root_text)
            except ValueError:
                pass


def _validate_run_config_payload(payload: Any) -> tuple[bool, dict[str, Any]]:
    if not isinstance(payload, dict):
        return False, {"ok": False, "errors": ["Config must be a JSON object"], "warnings": []}

    temp_path: Path | None = None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
            json.dump(payload, handle, ensure_ascii=True, indent=2)
            temp_path = Path(handle.name)

        src_root = IMPL_ROOT / "src"
        inserted = False
        src_root_text = str(src_root)
        if src_root_text not in sys.path:
            sys.path.insert(0, src_root_text)
            inserted = True
        try:
            from run_config.run_config_utils import RunConfigError, load_run_config  # type: ignore

            effective = load_run_config(temp_path)
        except RunConfigError as exc:
            return False, {"ok": False, "errors": [str(exc)], "warnings": []}
        finally:
            if inserted:
                try:
                    sys.path.remove(src_root_text)
                except ValueError:
                    pass

        warnings = _config_guardrail_warnings(effective or payload)
        return True, {
            "ok": True,
            "errors": [],
            "warnings": warnings,
            "effective_config": effective,
        }
    except Exception as exc:
        return False, {"ok": False, "errors": [f"Validation failed: {exc}"], "warnings": []}
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def _config_guardrail_warnings(config: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    input_scope = config.get("input_scope") if isinstance(config.get("input_scope"), dict) else {}
    if not any(
        bool(input_scope.get(key))
        for key in ("include_top_tracks", "include_saved_tracks", "include_playlists", "include_recently_played")
    ):
        warnings.append("At least one input source should be enabled.")

    profile_controls = config.get("profile_controls") if isinstance(config.get("profile_controls"), dict) else {}
    retrieval_controls = config.get("retrieval_controls") if isinstance(config.get("retrieval_controls"), dict) else {}
    for suffix in ("tag", "genre", "lead_genre"):
        profile_key = f"top_{suffix}_limit"
        retrieval_key = f"profile_top_{suffix}_limit"
        if retrieval_controls.get(retrieval_key, 0) > profile_controls.get(profile_key, 0):
            warnings.append(f"{retrieval_key} should not exceed {profile_key}.")

    control_mode = config.get("control_mode") if isinstance(config.get("control_mode"), dict) else {}
    scoring_controls = config.get("scoring_controls") if isinstance(config.get("scoring_controls"), dict) else {}
    retrieval_thresholds = retrieval_controls.get("numeric_thresholds")
    scoring_thresholds = scoring_controls.get("numeric_thresholds")
    if (
        control_mode.get("allow_threshold_decoupling") is False
        and isinstance(retrieval_thresholds, dict)
        and isinstance(scoring_thresholds, dict)
        and retrieval_thresholds != scoring_thresholds
    ):
        warnings.append("Retrieval and scoring numeric thresholds should match unless threshold decoupling is enabled.")

    assembly_controls = config.get("assembly_controls") if isinstance(config.get("assembly_controls"), dict) else {}
    target_size = assembly_controls.get("target_size")
    max_per_genre = assembly_controls.get("max_per_genre")
    if isinstance(target_size, int | float) and isinstance(max_per_genre, int | float) and max_per_genre > target_size:
        warnings.append("max_per_genre is larger than target_size, so the diversity limit will not constrain the playlist.")

    return warnings


def _normalize_config_save_name(raw_name: str) -> tuple[str | None, str | None]:
    name = raw_name.strip()
    if not name:
        return None, "A file name is required."
    name = name.replace("\\", "/").split("/")[-1]
    if not name.lower().endswith(".json"):
        name = f"{name}.json"
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    if any(char not in safe_chars for char in name):
        return None, "Use only letters, numbers, dots, underscores, and hyphens in the file name."
    if name in {".json", "..json"} or name.startswith("."):
        return None, "Use a normal JSON file name."
    return name, None


def _save_config_builder_profile(file_name: str, payload: Any) -> tuple[int, dict[str, Any]]:
    ok, validation = _validate_run_config_payload(payload)
    if not ok:
        return 400, validation

    safe_name, error = _normalize_config_save_name(file_name)
    if error is not None or safe_name is None:
        return 400, {"ok": False, "errors": [error or "Invalid file name"], "warnings": []}

    target = CONFIG_DIR / safe_name
    try:
        target.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    except OSError as exc:
        return 500, {"ok": False, "errors": [f"Could not save config: {exc}"], "warnings": []}

    return 200, {
        "ok": True,
        "path": str(target.relative_to(IMPL_ROOT)).replace("\\", "/"),
        "warnings": validation.get("warnings", []),
    }


def _config_builder_profile_payload(config_name: str) -> tuple[int, dict[str, Any]]:
    resolved, error = _resolve_config_path(config_name)
    if error is not None or resolved is None:
        return 404, {"error": error or "Profile not found"}

    profile = _load_json_or_none(resolved)
    if profile is None:
        return 500, {"error": "Profile file is missing or malformed"}

    return 200, {
        "config_path": str(resolved.relative_to(IMPL_ROOT)).replace("\\", "/"),
        "profile": profile,
    }


def _csv_row_count(path: Path) -> int | None:
    if not path.is_file():
        return None
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            # Exclude the header row for user-facing data counts.
            return max(sum(1 for _ in reader) - 1, 0)
    except Exception:
        return None


def _json_array_count(path: Path, key: str) -> int | None:
    payload = _load_json_or_none(path)
    if payload is None:
        return None
    value = payload.get(key)
    if isinstance(value, list):
        return len(value)
    return None


def _stage_metrics(stage_id: str) -> dict[str, Any]:
    if stage_id == "bl003":
        payload = _load_json_or_none(ARTIFACT_PATHS["bl003_summary"]) or {}
        return {
            "matched_events": payload.get("matched_events"),
            "match_rate": payload.get("match_rate"),
        }
    if stage_id == "bl004":
        payload = _load_json_or_none(ARTIFACT_PATHS["bl004_profile"]) or {}
        top_genres = payload.get("top_lead_genres")
        return {
            "top_lead_genres_count": len(top_genres) if isinstance(top_genres, list) else None,
        }
    if stage_id == "bl005":
        return {"filtered_candidates": _csv_row_count(ARTIFACT_PATHS["bl005_filtered"])}
    if stage_id == "bl006":
        return {"scored_candidates": _csv_row_count(ARTIFACT_PATHS["bl006_scored"])}
    if stage_id == "bl007":
        return {"playlist_track_count": _json_array_count(ARTIFACT_PATHS["bl007_playlist"], "tracks")}
    if stage_id == "bl008":
        return {"explanations_count": _json_array_count(ARTIFACT_PATHS["bl008_payloads"], "explanations")}
    if stage_id == "bl009":
        payload = _load_json_or_none(ARTIFACT_PATHS["bl009_log"]) or {}
        return {
            "run_id": payload.get("run_id"),
            "overall_status": payload.get("overall_status"),
        }
    return {}


def _pipeline_flow_payload() -> dict[str, Any]:
    stages: list[dict[str, Any]] = []
    for stage_id, spec in STAGE_EXPLAINER_MAP.items():
        artifact_names = spec["artifacts"]
        artifacts = []
        for artifact_name in artifact_names:
            path = ARTIFACT_PATHS[artifact_name]
            exists = path.is_file()
            artifacts.append(
                {
                    "name": artifact_name,
                    "path": str(path.relative_to(IMPL_ROOT)).replace("\\", "/"),
                    "exists": exists,
                }
            )
        stages.append(
            {
                "stage_id": stage_id,
                "label": spec["label"],
                "script": spec["script"],
                "description": spec["description"],
                "artifacts": artifacts,
                "ready": all(item["exists"] for item in artifacts),
            }
        )
    return {"stages": stages}


def _stage_explainer_payload(stage_id: str) -> tuple[int, dict[str, Any]]:
    normalized_stage_id = stage_id.strip().lower()
    if normalized_stage_id not in STAGE_EXPLAINER_MAP:
        return 404, {"error": f"Unknown stage: {stage_id}"}

    spec = STAGE_EXPLAINER_MAP[normalized_stage_id]
    artifacts: list[dict[str, Any]] = []
    for artifact_name in spec["artifacts"]:
        path = ARTIFACT_PATHS[artifact_name]
        exists = path.is_file()
        artifacts.append(
            {
                "name": artifact_name,
                "path": str(path.relative_to(IMPL_ROOT)).replace("\\", "/"),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else None,
                "modified_utc": _iso_utc_mtime(path) if exists else None,
            }
        )

    return 200, {
        "stage_id": normalized_stage_id,
        "label": spec["label"],
        "script": spec["script"],
        "description": spec["description"],
        "artifacts": artifacts,
        "metrics": _stage_metrics(normalized_stage_id),
    }


def _explanation_view_payload(limit: int = EXPLAINER_TRACK_LIMIT) -> tuple[int, dict[str, Any]]:
    payload = _load_json_or_none(ARTIFACT_PATHS["bl008_payloads"])
    if payload is None:
        return 404, {"error": "BL-008 explanation payload is not available"}

    explanations = payload.get("explanations")
    if not isinstance(explanations, list):
        return 500, {"error": "BL-008 explanations field is malformed"}

    normalized_limit = min(max(1, limit), EXPLAINER_TRACK_LIMIT_MAX)
    items: list[dict[str, Any]] = []
    contributor_distribution: dict[str, int] = {}
    for row in explanations[:normalized_limit]:
        if not isinstance(row, dict):
            continue
        narrative_driver = row.get("narrative_driver")
        narrative_label = None
        if isinstance(narrative_driver, dict):
            narrative_label = narrative_driver.get("label")
        if isinstance(narrative_label, str) and narrative_label.strip():
            contributor_distribution[narrative_label] = contributor_distribution.get(narrative_label, 0) + 1
        top_contributors = row.get("top_score_contributors")
        top_labels: list[str] = []
        if isinstance(top_contributors, list):
            for contributor in top_contributors[:3]:
                if isinstance(contributor, dict):
                    label = contributor.get("label")
                    if isinstance(label, str) and label.strip():
                        top_labels.append(label)

        items.append(
            {
                "playlist_position": row.get("playlist_position"),
                "track_id": row.get("track_id"),
                "final_score": row.get("final_score"),
                "why_selected": row.get("why_selected"),
                "narrative_driver": narrative_label,
                "top_score_labels": top_labels,
            }
        )

    return 200, {
        "run_id": payload.get("run_id"),
        "generated_at_utc": payload.get("generated_at_utc"),
        "playlist_track_count": payload.get("playlist_track_count"),
        "returned_track_count": len(items),
        "driver_distribution": contributor_distribution,
        "tracks": items,
    }


def _evidence_dashboard_payload() -> dict[str, Any]:
    bl013 = _load_json_or_none(ARTIFACT_PATHS["bl013_latest"]) or {}
    bl014 = _load_json_or_none(ARTIFACT_PATHS["bl014_latest"]) or {}
    bl009 = _load_json_or_none(ARTIFACT_PATHS["bl009_log"]) or {}

    bl013_available = bool(bl013)
    bl014_available = bool(bl014)
    bl009_available = bool(bl009)

    failed_checks: list[dict[str, Any]] = []
    checks = bl014.get("checks")
    if isinstance(checks, list):
        for check in checks:
            if isinstance(check, dict) and check.get("status") == "fail":
                failed_checks.append(
                    {
                        "id": check.get("id"),
                        "details": check.get("details"),
                    }
                )

    stage_results = bl013.get("stage_results")
    stage_statuses: list[dict[str, Any]] = []
    if isinstance(stage_results, list):
        for row in stage_results:
            if isinstance(row, dict):
                stage_statuses.append(
                    {
                        "stage_id": row.get("stage_id"),
                        "status": row.get("status"),
                        "elapsed_seconds": row.get("elapsed_seconds"),
                        "return_code": row.get("return_code"),
                    }
                )

    run_metadata = bl009.get("run_metadata") if isinstance(bl009.get("run_metadata"), dict) else {}
    validity_boundaries = bl009.get("validity_boundaries") if isinstance(bl009.get("validity_boundaries"), dict) else {}

    return {
        "bl013": {
            "available": bl013_available,
            "run_id": bl013.get("run_id"),
            "overall_status": bl013.get("overall_status"),
            "executed_stage_count": bl013.get("executed_stage_count"),
            "failed_stage_count": bl013.get("failed_stage_count"),
            "stage_statuses": stage_statuses,
            "note": None if bl013_available else "BL-013 latest orchestration artifact is missing",
        },
        "bl014": {
            "available": bl014_available,
            "run_id": bl014.get("run_id"),
            "overall_status": bl014.get("overall_status"),
            "checks_total": bl014.get("checks_total"),
            "checks_passed": bl014.get("checks_passed"),
            "checks_failed": bl014.get("checks_failed"),
            "advisories_total": bl014.get("advisories_total"),
            "failed_checks": failed_checks,
            "note": None if bl014_available else "BL-014 latest sanity artifact is missing",
        },
        "bl009": {
            "available": bl009_available,
            "run_id": run_metadata.get("run_id"),
            "dataset_version": run_metadata.get("dataset_version"),
            "pipeline_version": run_metadata.get("pipeline_version"),
            "signal_mode_name": run_metadata.get("signal_mode_name"),
            "validity_boundaries": validity_boundaries,
            "note": None if bl009_available else "BL-009 latest observability artifact is missing",
        },
    }


def _guide_payload() -> dict[str, Any]:
    bl013 = _load_json_or_none(ARTIFACT_PATHS["bl013_latest"]) or {}
    bl014 = _load_json_or_none(ARTIFACT_PATHS["bl014_latest"]) or {}
    bl008 = _load_json_or_none(ARTIFACT_PATHS["bl008_payloads"]) or {}
    bl009 = _load_json_or_none(ARTIFACT_PATHS["bl009_log"]) or {}

    bl013_ok = bl013.get("overall_status") == "pass"
    bl014_ok = bl014.get("overall_status") == "pass"
    bl008_ready = isinstance(bl008.get("explanations"), list)
    bl009_ready = isinstance(bl009.get("run_metadata"), dict)

    steps: list[dict[str, Any]] = [
        {
            "id": "run_pipeline",
            "title": "Run pipeline",
            "status": "done" if bl013_ok else ("ready" if bool(bl013) else "pending"),
            "message": "BL-013 latest run is available and passing" if bl013_ok else "Run from the UI to generate fresh artifacts",
        },
        {
            "id": "check_quality",
            "title": "Check quality",
            "status": "done" if bl014_ok else ("attention" if bool(bl014) else "pending"),
            "message": "BL-014 sanity checks are passing" if bl014_ok else "Review BL-014 failed checks in the evidence dashboard",
        },
        {
            "id": "inspect_explanations",
            "title": "Inspect explanations",
            "status": "done" if bl008_ready else "pending",
            "message": "BL-008 explanation payload is available" if bl008_ready else "Generate BL-008 outputs first",
        },
        {
            "id": "inspect_evidence",
            "title": "Inspect evidence",
            "status": "done" if bl009_ready else "pending",
            "message": "BL-009 observability payload is available" if bl009_ready else "Generate BL-009 outputs first",
        },
    ]

    next_step = "run_pipeline"
    for step in steps:
        if step["status"] in {"pending", "attention", "ready"}:
            next_step = step["id"]
            break

    return {
        "summary": {
            "bl013_status": bl013.get("overall_status"),
            "bl014_status": bl014.get("overall_status"),
            "next_step": next_step,
        },
        "steps": steps,
    }


def _status_payload() -> dict[str, Any]:
    bl013 = _load_json_or_none(BL013_LATEST_PATH)
    bl014 = _load_json_or_none(BL014_LATEST_PATH)
    return {
        "bl013": {
            "exists": bl013 is not None,
            "run_id": bl013.get("run_id") if bl013 else None,
            "overall_status": bl013.get("overall_status") if bl013 else None,
            "generated_at_utc": bl013.get("generated_at_utc") if bl013 else None,
        },
        "bl014": {
            "exists": bl014 is not None,
            "run_id": bl014.get("run_id") if bl014 else None,
            "overall_status": bl014.get("overall_status") if bl014 else None,
            "checks_total": bl014.get("checks_total") if bl014 else None,
            "checks_passed": bl014.get("checks_passed") if bl014 else None,
            "checks_failed": bl014.get("checks_failed") if bl014 else None,
            "generated_at_utc": bl014.get("generated_at_utc") if bl014 else None,
        },
    }


def _artifact_preview(name: str) -> tuple[int, dict[str, Any]]:
    artifact_name = str(name).strip()
    if artifact_name not in ARTIFACT_PATHS:
        return 404, {"error": f"Unknown artifact: {artifact_name}"}

    path = ARTIFACT_PATHS[artifact_name]
    if not path.is_file():
        return 404, {"error": "Artifact not generated yet", "name": artifact_name}

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return 500, {"error": f"Could not read artifact: {exc}"}

    content_type = "text"
    preview = text
    if path.suffix.lower() == ".json":
        content_type = "json"
        try:
            parsed = json.loads(text)
            preview = json.dumps(parsed, indent=2, ensure_ascii=True)
        except Exception:
            preview = text
    elif path.suffix.lower() == ".csv":
        content_type = "csv"

    truncated = len(preview) > PREVIEW_MAX_CHARS
    preview_text = preview[:PREVIEW_MAX_CHARS]
    return 200, {
        "name": artifact_name,
        "path": str(path.relative_to(IMPL_ROOT)).replace("\\", "/"),
        "content_type": content_type,
        "truncated": truncated,
        "preview": preview_text,
    }


class ThesisWebHandler(BaseHTTPRequestHandler):
    """HTTP handler for the tiny thesis web app."""

    def do_GET(self) -> None:
        """Serve the UI and lightweight API endpoints."""
        parsed = urlparse(self.path)
        route = parsed.path.strip()
        if route != "/" and route.endswith("/"):
            route = route[:-1]
        route = "/" + route.lstrip("/")

        if route.endswith("/api/configs"):
            self._send_json(200, {"configs": _config_choices()})
            return

        if route.endswith("/api/config-builder/schema"):
            self._send_json(200, _config_builder_schema_payload())
            return

        if route.endswith("/api/config-builder/profile"):
            params = parse_qs(parsed.query)
            config_name = ""
            if "name" in params and params["name"]:
                config_name = params["name"][0]
            status_code, payload = _config_builder_profile_payload(config_name)
            self._send_json(status_code, payload)
            return

        if route.endswith("/api/status"):
            self._send_json(200, _status_payload())
            return

        if route.endswith("/api/artifacts"):
            self._send_json(200, {"artifacts": _artifact_manifest()})
            return

        if route.endswith("/api/explainer/flow"):
            self._send_json(200, _pipeline_flow_payload())
            return

        if route.endswith("/api/explainer/stage"):
            params = parse_qs(parsed.query)
            stage_id = ""
            if "stage" in params and params["stage"]:
                stage_id = params["stage"][0]
            status_code, payload = _stage_explainer_payload(stage_id)
            self._send_json(status_code, payload)
            return

        if route.endswith("/api/explainer/explanations"):
            params = parse_qs(parsed.query)
            limit = EXPLAINER_TRACK_LIMIT
            if "limit" in params and params["limit"]:
                try:
                    limit = int(params["limit"][0])
                except ValueError:
                    limit = EXPLAINER_TRACK_LIMIT
            status_code, payload = _explanation_view_payload(limit=limit)
            self._send_json(status_code, payload)
            return

        if route.endswith("/api/explainer/evidence"):
            self._send_json(200, _evidence_dashboard_payload())
            return

        if route.endswith("/api/explainer/guide"):
            self._send_json(200, _guide_payload())
            return

        if route.endswith("/api/artifact"):
            params = parse_qs(parsed.query)
            name = ""
            if "name" in params and params["name"]:
                name = params["name"][0]
            status_code, payload = _artifact_preview(name)
            self._send_json(status_code, payload)
            return

        if route.endswith("/api/run-stream"):
            params = parse_qs(parsed.query)
            config_path = ""
            if "config_path" in params and params["config_path"]:
                config_path = params["config_path"][0]
            validate_only = False
            if "validate_only" in params and params["validate_only"]:
                validate_only = params["validate_only"][0].lower() in {"1", "true", "yes"}
            continue_on_error = False
            if "continue_on_error" in params and params["continue_on_error"]:
                continue_on_error = params["continue_on_error"][0].lower() in {"1", "true", "yes"}
            self._stream_thesis(
                config_path,
                validate_only=validate_only,
                continue_on_error=continue_on_error,
            )
            return

        if route not in ("/", "/index.html"):
            self._send_json(404, {"error": "Not found"})
            return

        try:
            with INDEX_FILE.open("r", encoding="utf-8") as handle:
                content = handle.read()
        except OSError:
            self._send_json(500, {"error": f"Missing UI file: {INDEX_FILE}"})
            return

        payload = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self) -> None:
        """Handle run requests from the browser UI."""
        parsed = urlparse(self.path)
        route = parsed.path.rstrip("/") or "/"

        if route == "/api/config-builder/validate":
            request_json = self._read_json_body()
            ok, payload = _validate_run_config_payload(request_json.get("config"))
            self._send_json(200 if ok else 400, payload)
            return

        if route == "/api/config-builder/save":
            request_json = self._read_json_body()
            status_code, payload = _save_config_builder_profile(
                str(request_json.get("file_name", "")),
                request_json.get("config"),
            )
            self._send_json(status_code, payload)
            return

        if route != "/api/run":
            self._send_json(404, {"error": "Not found"})
            return

        request_json = self._read_json_body()
        config_path = str(request_json.get("config_path", "")).strip()
        validate_only = bool(request_json.get("validate_only", False))
        continue_on_error = bool(request_json.get("continue_on_error", False))

        result = self._run_thesis(
            config_path,
            validate_only=validate_only,
            continue_on_error=continue_on_error,
        )
        self._send_json(200, result)

    def _read_json_body(self) -> dict[str, Any]:
        """Best-effort JSON body parse."""
        raw_length = self.headers.get("Content-Length", "0").strip()
        if not raw_length.isdigit():
            return {}

        body_size = int(raw_length)
        raw_body = self.rfile.read(body_size)

        try:
            parsed = json.loads(raw_body.decode("utf-8"))
        except Exception:
            return {}

        if not isinstance(parsed, dict):
            return {}

        return parsed

    def _run_thesis(self, config_path: str, *, validate_only: bool, continue_on_error: bool) -> dict[str, Any]:
        """Run top-level main.py and return terminal-like output text."""
        resolved_config, error = _resolve_config_path(config_path)
        if error is not None:
            return {
                "ok": False,
                "exit_code": 2,
                "terminal_output": error,
            }

        command = _build_run_command(
            resolved_config=resolved_config,
            validate_only=validate_only,
            continue_on_error=continue_on_error,
        )
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=str(IMPL_ROOT),
        )

        command_line = " ".join(command)
        combined_output = f"$ {command_line}\n"
        if process.stdout:
            combined_output += process.stdout
        if process.stderr:
            combined_output += process.stderr

        return {
            "ok": process.returncode == 0,
            "exit_code": process.returncode,
            "status": _status_payload(),
            "terminal_output": combined_output,
        }

    def _stream_thesis(self, config_path: str, *, validate_only: bool, continue_on_error: bool) -> None:
        """Stream wrapper output line-by-line using Server-Sent Events (SSE)."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        resolved_config, error = _resolve_config_path(config_path)
        if error is not None:
            self._sse_write("line", error)
            self._sse_write("done", json.dumps({"ok": False, "exit_code": 2}, ensure_ascii=True))
            return

        command = _build_run_command(
            resolved_config=resolved_config,
            validate_only=validate_only,
            continue_on_error=continue_on_error,
        )
        command.insert(1, "-u")
        self._sse_write("line", f"$ {' '.join(command)}")

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(IMPL_ROOT),
        )

        if process.stdout is not None:
            for line in process.stdout:
                self._sse_write("line", line.rstrip("\n"))

        return_code = process.wait()
        self._sse_write(
            "done",
            json.dumps(
                {
                    "ok": return_code == 0,
                    "exit_code": return_code,
                    "status": _status_payload(),
                },
                ensure_ascii=True,
            ),
        )

    def _sse_write(self, event_name: str, payload: str) -> None:
        """Write one SSE event record to the response stream."""
        safe_payload = payload.replace("\r", "")
        message = f"event: {event_name}\n"
        for line in safe_payload.split("\n"):
            message += f"data: {line}\n"
        message += "\n"
        self.wfile.write(message.encode("utf-8"))
        self.wfile.flush()

    def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
        """Write JSON response with proper headers."""
        encoded = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main() -> int:
    """Start local server for the thesis UI."""
    host = "127.0.0.1"
    port = 8000
    server = HTTPServer((host, port), ThesisWebHandler)
    print(f"Thesis web server running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
