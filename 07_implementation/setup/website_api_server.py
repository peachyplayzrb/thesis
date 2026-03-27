from __future__ import annotations

import os
import json
import hashlib
import subprocess
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional

import uvicorn
from fastapi.exceptions import RequestValidationError
from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RuntimeConfigValidateRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    stage_params: Dict[str, Any] = Field(default_factory=dict)


class PipelineRunStartRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    stage_ids: Optional[List[str]] = None
    stage_params: Dict[str, Any] = Field(default_factory=dict)


class EvidenceBundleRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    run_id: Optional[str] = None


class SpotifyExportStartRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    spotify: Dict[str, Any] = Field(default_factory=dict)


@dataclass
class ExportRunState:
    status: str = "idle"
    started_at_utc: Optional[str] = None
    completed_at_utc: Optional[str] = None
    exit_code: Optional[int] = None
    current_step: str = "idle"
    current_message: str = "No ingestion run started yet."
    oauth_url: Optional[str] = None
    request_config: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    line_count: int = 0
    summary: Optional[Dict[str, Any]] = None


class SpotifyExportJob:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.implementation_root = repo_root / "07_implementation"
        self.implementation_notes_root = self.implementation_root / "implementation_notes"
        self.export_root = self.implementation_notes_root / "bl001_bl002_ingestion" / "outputs" / "spotify_api_export"
        self.summary_path = self.export_root / "spotify_export_run_summary.json"
        self.python_executable = Path(sys.executable)
        self.lock = threading.Lock()
        self.process: Optional[subprocess.Popen[str]] = None
        self.state = ExportRunState(summary=self._load_summary_if_available())

    def _load_summary_if_available(self) -> Optional[Dict[str, Any]]:
        if not self.summary_path.exists():
            return None
        try:
            return json.loads(self.summary_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _append_log(self, line: str) -> None:
        clean = line.rstrip("\r\n")
        with self.lock:
            self.state.line_count += 1
            self.state.logs.append({
                "index": self.state.line_count,
                "timestamp_utc": now_utc(),
                "line": clean,
            })
            if len(self.state.logs) > 600:
                self.state.logs = self.state.logs[-600:]

            if clean.startswith("https://accounts.spotify.com/authorize?"):
                self.state.oauth_url = clean
                self.state.current_step = "oauth"
                self.state.current_message = "Waiting for Spotify authorization."
            elif clean.startswith("[auth]"):
                self.state.current_step = "auth"
                self.state.current_message = clean
            elif clean.startswith("[profile]"):
                self.state.current_step = "profile"
                self.state.current_message = clean
            elif clean.startswith("[top_tracks]"):
                self.state.current_step = "top_tracks"
                self.state.current_message = clean
            elif clean.startswith("[saved_tracks]"):
                self.state.current_step = "saved_tracks"
                self.state.current_message = clean
            elif clean.startswith("[playlists]"):
                self.state.current_step = "playlists"
                self.state.current_message = clean
            elif clean.startswith("[playlist_items]"):
                self.state.current_step = "playlist_items"
                self.state.current_message = clean
            elif clean.startswith("[recently_played]"):
                self.state.current_step = "recently_played"
                self.state.current_message = clean
            elif clean.startswith("[write]"):
                self.state.current_step = "write"
                self.state.current_message = clean
            elif clean.startswith("[blocked]"):
                self.state.current_step = "blocked"
                self.state.current_message = clean
            elif clean.startswith("Spotify export complete"):
                self.state.current_step = "completed"
                self.state.current_message = clean

    def _build_command(self, config: Dict[str, Any]) -> List[str]:
        spotify = config.get("spotify", {}) if isinstance(config, dict) else {}
        top = spotify.get("top_tracks", {}) if isinstance(spotify, dict) else {}
        saved = spotify.get("saved_tracks", {}) if isinstance(spotify, dict) else {}
        playlists = spotify.get("playlists", {}) if isinstance(spotify, dict) else {}
        recently = spotify.get("recently_played", {}) if isinstance(spotify, dict) else {}

        include_top = bool(top.get("enabled"))
        include_saved = bool(saved.get("enabled"))
        include_playlists = bool(playlists.get("enabled"))
        include_recently = bool(recently.get("enabled"))

        scopes = ["user-read-private"]
        if include_top:
            scopes.append("user-top-read")
        if include_saved:
            scopes.append("user-library-read")
        if include_playlists:
            scopes.extend(["playlist-read-private", "playlist-read-collaborative"])
        if include_recently:
            scopes.append("user-read-recently-played")

        command = [
            str(self.python_executable),
            "-u",
            "-m",
            "bl001_bl002_ingestion.export_spotify_max_dataset",
            "--scopes",
            " ".join(scopes),
        ]

        if include_top:
            command.append("--include-top-tracks")
            ranges = top.get("ranges", {}) if isinstance(top, dict) else {}
            enabled_ranges: List[str] = []
            for time_range in ("short_term", "medium_term", "long_term"):
                range_config = ranges.get(time_range, {}) if isinstance(ranges, dict) else {}
                if bool(range_config.get("enabled")):
                    enabled_ranges.append(time_range)
                    max_items = range_config.get("limit")
                    if isinstance(max_items, int) and max_items > 0:
                        command.extend([f"--top-max-items-{time_range.replace('_', '-')}", str(max_items)])
            command.extend(["--top-time-ranges", ",".join(enabled_ranges or ["short_term", "medium_term", "long_term"])])

        if include_saved:
            command.append("--include-saved-tracks")
            max_items = saved.get("max_items")
            if isinstance(max_items, int) and max_items > 0:
                command.extend(["--saved-max-items", str(max_items)])

        if include_playlists:
            command.append("--include-playlists")
            max_playlists = playlists.get("max_playlists")
            max_per_playlist = playlists.get("max_items_per_playlist")
            if isinstance(max_playlists, int) and max_playlists > 0:
                command.extend(["--playlists-max-items", str(max_playlists)])
            if isinstance(max_per_playlist, int) and max_per_playlist > 0:
                command.extend(["--playlist-items-max-per-playlist", str(max_per_playlist)])

        if include_recently:
            command.append("--include-recently-played")
            limit = recently.get("limit")
            if isinstance(limit, int) and limit > 0:
                command.extend(["--recently-played-limit", str(limit)])

        return command

    def start(self, config: Dict[str, Any]) -> None:
        with self.lock:
            if self.process is not None and self.process.poll() is None:
                raise RuntimeError("An ingestion run is already in progress.")

            self.state = ExportRunState(
                status="running",
                started_at_utc=now_utc(),
                current_step="starting",
                current_message="Starting Spotify ingestion run...",
                request_config=config,
                summary=self._load_summary_if_available(),
            )

            command = self._build_command(config)
            self.process = subprocess.Popen(
                command,
                cwd=str(self.implementation_notes_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

        threading.Thread(target=self._monitor_process, daemon=True).start()

    def cancel(self) -> None:
        with self.lock:
            if self.process is None or self.process.poll() is not None:
                raise RuntimeError("No ingestion run is currently in progress.")
            self.state.current_step = "cancelling"
            self.state.current_message = "Cancelling Spotify ingestion run..."
            self.state.status = "running"
            process = self.process

        process.terminate()

    def _monitor_process(self) -> None:
        process = self.process
        if process is None or process.stdout is None:
            return

        for line in process.stdout:
            self._append_log(line)

        exit_code = process.wait()
        summary = self._load_summary_if_available()
        with self.lock:
            self.state.exit_code = exit_code
            self.state.completed_at_utc = now_utc()
            self.state.summary = summary
            if self.state.current_step == "cancelling":
                self.state.status = "cancelled"
                self.state.current_step = "cancelled"
                self.state.current_message = "Spotify ingestion was cancelled by user request."
                return

            self.state.status = "completed" if exit_code == 0 else "failed"
            if exit_code == 0:
                self.state.current_step = "completed"
                self.state.current_message = "Spotify ingestion completed successfully."
            else:
                self.state.current_step = "failed"
                self.state.current_message = f"Spotify ingestion failed with exit code {exit_code}."

    def snapshot(self, after: int = 0) -> Dict[str, Any]:
        with self.lock:
            logs = [entry for entry in self.state.logs if entry["index"] > after]
            summary = self._load_summary_if_available()
            return {
                "server_time_utc": now_utc(),
                "run": {
                    "status": self.state.status,
                    "started_at_utc": self.state.started_at_utc,
                    "completed_at_utc": self.state.completed_at_utc,
                    "exit_code": self.state.exit_code,
                    "current_step": self.state.current_step,
                    "current_message": self.state.current_message,
                    "oauth_url": self.state.oauth_url,
                    "request_config": self.state.request_config,
                    "line_count": self.state.line_count,
                    "logs": logs,
                    "summary": summary,
                    "artifacts_ready": summary is not None,
                },
            }


@dataclass
class PipelineStageState:
    stage_id: str
    label: str
    script_path: str
    status: str = "queued"
    started_at_utc: Optional[str] = None
    completed_at_utc: Optional[str] = None
    exit_code: Optional[int] = None
    current_message: str = "Queued"
    log_start_index: Optional[int] = None
    log_end_index: Optional[int] = None


@dataclass
class PipelineRunState:
    status: str = "idle"
    run_id: Optional[str] = None
    started_at_utc: Optional[str] = None
    completed_at_utc: Optional[str] = None
    current_stage: str = "idle"
    current_message: str = "No pipeline run started yet."
    cancel_requested: bool = False
    request_config: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    line_count: int = 0
    stages: List[PipelineStageState] = field(default_factory=list)
    artifact_summary: Dict[str, Any] = field(default_factory=dict)


class PipelineJob:
    STAGE_SPECS: List[Dict[str, str]] = [
        {
            "stage_id": "bl003",
            "label": "BL-003 Alignment",
            "script": "bl003_alignment/build_bl003_ds001_spotify_seed_table.py",
            "description": "Align imported Spotify interactions to DS-001 seed tracks.",
        },
        {
            "stage_id": "bl004",
            "label": "BL-004 Profile",
            "script": "bl004_profile/build_bl004_preference_profile.py",
            "description": "Build deterministic preference profile from aligned seed data.",
        },
        {
            "stage_id": "bl005",
            "label": "BL-005 Retrieval",
            "script": "bl005_retrieval/build_bl005_candidate_filter.py",
            "description": "Filter candidate corpus against profile signals and keep rules.",
        },
        {
            "stage_id": "bl006",
            "label": "BL-006 Scoring",
            "script": "bl006_scoring/build_bl006_scored_candidates.py",
            "description": "Score retained candidates with weighted components.",
        },
        {
            "stage_id": "bl007",
            "label": "BL-007 Playlist",
            "script": "bl007_playlist/build_bl007_playlist.py",
            "description": "Assemble final playlist with deterministic rule checks.",
        },
        {
            "stage_id": "bl008",
            "label": "BL-008 Transparency",
            "script": "bl008_transparency/build_bl008_explanation_payloads.py",
            "description": "Generate explanation payloads and summary transparency outputs.",
        },
        {
            "stage_id": "bl009",
            "label": "BL-009 Observability",
            "script": "bl009_observability/build_bl009_observability_log.py",
            "description": "Record run-chain observability metadata and index outputs.",
        },
    ]

    STAGE_PARAM_SCHEMA: Dict[str, List[Dict[str, Any]]] = {
        "bl003": [
            {"key": "input_scope", "type": "json"},
            {"key": "allow_missing_selected_sources", "type": "bool", "default": False},
        ],
        "bl004": [
            {"key": "top_tag_limit", "type": "int", "min": 1, "max": 100, "default": 10},
            {"key": "top_genre_limit", "type": "int", "min": 1, "max": 100, "default": 8},
            {"key": "top_lead_genre_limit", "type": "int", "min": 1, "max": 100, "default": 6},
            {"key": "user_id", "type": "string", "default": "21zsn42xecjhogne4kghyw5hq"},
            {"key": "include_interaction_types", "type": "json_array"},
        ],
        "bl005": [
            {"key": "semantic_strong_keep_score", "type": "int", "min": 0, "max": 10, "default": 2},
            {"key": "semantic_min_keep_score", "type": "int", "min": 0, "max": 10, "default": 1},
            {"key": "numeric_support_min_pass", "type": "int", "min": 0, "max": 10, "default": 1},
            {"key": "profile_top_lead_genre_limit", "type": "int", "min": 1, "max": 30, "default": 6},
            {"key": "profile_top_tag_limit", "type": "int", "min": 1, "max": 50, "default": 10},
            {"key": "profile_top_genre_limit", "type": "int", "min": 1, "max": 50, "default": 8},
            {"key": "numeric_thresholds", "type": "json"},
        ],
        "bl006": [
            {"key": "component_weights", "type": "json"},
            {"key": "numeric_thresholds", "type": "json"},
        ],
        "bl007": [
            {"key": "target_size", "type": "int", "min": 1, "max": 100, "default": 10},
            {"key": "min_score_threshold", "type": "float", "min": 0, "max": 1, "default": 0.35},
            {"key": "max_per_genre", "type": "int", "min": 1, "max": 20, "default": 4},
            {"key": "max_consecutive", "type": "int", "min": 1, "max": 10, "default": 2},
        ],
        "bl008": [
            {"key": "top_contributor_limit", "type": "int", "min": 1, "max": 20, "default": 3},
            {"key": "blend_primary_contributor_on_near_tie", "type": "bool", "default": False},
            {"key": "primary_contributor_tie_delta", "type": "float", "min": 0, "max": 1, "default": 0.02},
        ],
        "bl009": [
            {"key": "diagnostic_sample_limit", "type": "int", "min": 1, "max": 50, "default": 5},
            {"key": "bootstrap_mode", "type": "bool", "default": True},
        ],
    }

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.implementation_notes_root = repo_root / "07_implementation" / "implementation_notes"
        self.observability_output_root = self.implementation_notes_root / "bl009_observability" / "outputs"
        self.python_executable = Path(sys.executable)
        self.lock = threading.Lock()
        self.process: Optional[subprocess.Popen[str]] = None
        self.history: Deque[Dict[str, Any]] = deque(maxlen=30)
        self._track_lookup: Optional[Dict[str, Dict[str, str]]] = None
        self._track_lookup_lock = threading.Lock()
        self.state = PipelineRunState(
            stages=[
                PipelineStageState(
                    stage_id=spec["stage_id"],
                    label=spec["label"],
                    script_path=spec["script"],
                )
                for spec in self.STAGE_SPECS
            ]
        )

    def _new_run_id(self) -> str:
        return datetime.now(timezone.utc).strftime("PIPELINE-RUN-%Y%m%d-%H%M%S-%f")

    def _append_log(self, line: str, stage_id: Optional[str] = None) -> None:
        clean = line.rstrip("\r\n")
        with self.lock:
            self.state.line_count += 1
            entry = {
                "index": self.state.line_count,
                "timestamp_utc": now_utc(),
                "stage_id": stage_id,
                "line": clean,
            }
            self.state.logs.append(entry)
            if len(self.state.logs) > 1200:
                self.state.logs = self.state.logs[-1200:]

    def _find_stage(self, stage_id: str) -> PipelineStageState:
        for stage in self.state.stages:
            if stage.stage_id == stage_id:
                return stage
        raise KeyError(f"Unknown stage id: {stage_id}")

    def _stage_command(self, script_relative: str, stage_id: str, stage_params: Dict[str, Any]) -> List[str]:
        script_path = self.implementation_notes_root / script_relative
        command = [str(self.python_executable), "-u", str(script_path)]
        if stage_id == "bl003" and bool(stage_params.get("allow_missing_selected_sources")):
            command.append("--allow-missing-selected-sources")
        return command

    def _stage_env_overrides(self, stage_id: str, stage_params: Dict[str, Any]) -> Dict[str, str]:
        if not isinstance(stage_params, dict):
            return {}

        env: Dict[str, str] = {}

        if stage_id == "bl003":
            input_scope = stage_params.get("input_scope")
            if isinstance(input_scope, dict) and input_scope:
                try:
                    env["BL003_INPUT_SCOPE_JSON"] = json.dumps(input_scope, ensure_ascii=True)
                except Exception:
                    pass
            if "allow_missing_selected_sources" in stage_params:
                env["BL003_ALLOW_MISSING_SELECTED_SOURCES"] = "1" if bool(stage_params.get("allow_missing_selected_sources")) else "0"

        if stage_id == "bl004":
            mapping = {
                "top_tag_limit": "BL004_TOP_TAG_LIMIT",
                "top_genre_limit": "BL004_TOP_GENRE_LIMIT",
                "top_lead_genre_limit": "BL004_TOP_LEAD_GENRE_LIMIT",
            }
            for key, env_key in mapping.items():
                value = stage_params.get(key)
                if isinstance(value, (int, float)):
                    env[env_key] = str(value)

            user_id = stage_params.get("user_id")
            if isinstance(user_id, str) and user_id.strip():
                env["BL004_USER_ID"] = user_id.strip()

            interaction_types = stage_params.get("include_interaction_types")
            if isinstance(interaction_types, list):
                cleaned = [str(item).strip() for item in interaction_types if str(item).strip()]
                if cleaned:
                    env["BL004_INCLUDE_INTERACTION_TYPES"] = ",".join(cleaned)

        if stage_id == "bl005":
            mapping = {
                "profile_top_lead_genre_limit": "BL005_PROFILE_TOP_LEAD_GENRE_LIMIT",
                "profile_top_tag_limit": "BL005_PROFILE_TOP_TAG_LIMIT",
                "profile_top_genre_limit": "BL005_PROFILE_TOP_GENRE_LIMIT",
                "semantic_strong_keep_score": "BL005_SEMANTIC_STRONG_KEEP_SCORE",
                "semantic_min_keep_score": "BL005_SEMANTIC_MIN_KEEP_SCORE",
                "numeric_support_min_pass": "BL005_NUMERIC_SUPPORT_MIN_PASS",
            }
            for key, env_key in mapping.items():
                value = stage_params.get(key)
                if isinstance(value, (int, float)):
                    env[env_key] = str(value)

            threshold_overrides = stage_params.get("numeric_thresholds")
            if isinstance(threshold_overrides, dict) and threshold_overrides:
                try:
                    env["BL005_NUMERIC_THRESHOLDS_JSON"] = json.dumps(threshold_overrides, ensure_ascii=True)
                except Exception:
                    pass

        if stage_id == "bl006":
            weights = stage_params.get("component_weights")
            if isinstance(weights, dict) and weights:
                try:
                    env["BL006_COMPONENT_WEIGHTS_JSON"] = json.dumps(weights, ensure_ascii=True)
                except Exception:
                    pass

            threshold_overrides = stage_params.get("numeric_threshold_overrides")
            if not isinstance(threshold_overrides, dict) or not threshold_overrides:
                threshold_overrides = stage_params.get("numeric_thresholds")
            if isinstance(threshold_overrides, dict) and threshold_overrides:
                try:
                    env["BL006_NUMERIC_THRESHOLDS_JSON"] = json.dumps(threshold_overrides, ensure_ascii=True)
                except Exception:
                    pass

        if stage_id == "bl007":
            mapping = {
                "target_size": "BL007_TARGET_SIZE",
                "min_score_threshold": "BL007_MIN_SCORE_THRESHOLD",
                "max_per_genre": "BL007_MAX_PER_GENRE",
                "max_consecutive": "BL007_MAX_CONSECUTIVE",
            }
            for key, env_key in mapping.items():
                value = stage_params.get(key)
                if isinstance(value, (int, float)):
                    env[env_key] = str(value)

        if stage_id == "bl008":
            top_limit = stage_params.get("top_contributor_limit")
            if isinstance(top_limit, (int, float)):
                env["BL008_TOP_CONTRIBUTOR_LIMIT"] = str(top_limit)
            if "blend_primary_contributor_on_near_tie" in stage_params:
                env["BL008_BLEND_PRIMARY_CONTRIBUTOR_ON_NEAR_TIE"] = "1" if bool(stage_params.get("blend_primary_contributor_on_near_tie")) else "0"
            tie_delta = stage_params.get("primary_contributor_tie_delta")
            if isinstance(tie_delta, (int, float)):
                env["BL008_PRIMARY_CONTRIBUTOR_TIE_DELTA"] = str(tie_delta)

        if stage_id == "bl009":
            sample_limit = stage_params.get("diagnostic_sample_limit")
            if isinstance(sample_limit, (int, float)):
                env["BL009_DIAGNOSTIC_SAMPLE_LIMIT"] = str(sample_limit)
            if "bootstrap_mode" in stage_params:
                env["BL009_BOOTSTRAP_MODE"] = "1" if bool(stage_params.get("bootstrap_mode")) else "0"

        return env

    def stage_catalog(self) -> Dict[str, Any]:
        return {
            "server_time_utc": now_utc(),
            "stages": [
                {
                    "stage_id": spec["stage_id"],
                    "label": spec["label"],
                    "script_path": spec["script"],
                    "description": spec.get("description", ""),
                }
                for spec in self.STAGE_SPECS
            ],
        }

    def runtime_config_snapshot(self) -> Dict[str, Any]:
        return {
            "server_time_utc": now_utc(),
            "pipeline": {
                "stages": [
                    {
                        "stage_id": spec["stage_id"],
                        "label": spec["label"],
                        "script_path": spec["script"],
                        "description": spec.get("description", ""),
                    }
                    for spec in self.STAGE_SPECS
                ],
                "stage_parameter_schema": self.STAGE_PARAM_SCHEMA,
                "history_limit": self.history.maxlen,
                "pipeline_log_retention": 1200,
                "export_log_retention": 600,
            },
        }

    def validate_stage_params_payload(self, payload: Any) -> Dict[str, Any]:
        source = payload if isinstance(payload, dict) else {}
        stage_params = source.get("stage_params", source)
        errors: List[str] = []
        normalized: Dict[str, Dict[str, Any]] = {}

        if stage_params in (None, {}):
            return {
                "valid": True,
                "errors": [],
                "normalized_stage_params": {},
            }

        if not isinstance(stage_params, dict):
            return {
                "valid": False,
                "errors": ["stage_params must be an object keyed by stage id."],
                "normalized_stage_params": {},
            }

        for stage_id, raw_params in stage_params.items():
            sid = str(stage_id).strip().lower()
            schema = self.STAGE_PARAM_SCHEMA.get(sid)
            if schema is None:
                errors.append(f"Unknown stage id for stage_params: {sid}")
                continue
            if not isinstance(raw_params, dict):
                errors.append(f"stage_params.{sid} must be an object.")
                continue

            defs = {item["key"]: item for item in schema}
            stage_out: Dict[str, Any] = {}

            for key, value in raw_params.items():
                spec = defs.get(key)
                if spec is None:
                    errors.append(f"Unknown parameter for {sid}: {key}")
                    continue

                value_type = spec.get("type")
                if value_type == "string":
                    if not isinstance(value, str):
                        errors.append(f"{sid}.{key} must be a string.")
                        continue
                    clean = value.strip()
                    if not clean:
                        errors.append(f"{sid}.{key} cannot be empty.")
                        continue
                    stage_out[key] = clean
                    continue

                if value_type == "bool":
                    if isinstance(value, bool):
                        stage_out[key] = value
                        continue
                    if isinstance(value, str):
                        lowered = value.strip().lower()
                        if lowered in {"true", "1", "yes", "on"}:
                            stage_out[key] = True
                            continue
                        if lowered in {"false", "0", "no", "off"}:
                            stage_out[key] = False
                            continue
                    errors.append(f"{sid}.{key} must be a boolean.")
                    continue

                if value_type in ("int", "float"):
                    if isinstance(value, bool):
                        errors.append(f"{sid}.{key} must be a number.")
                        continue
                    number: Optional[float] = None
                    if isinstance(value, (int, float)):
                        number = float(value)
                    elif isinstance(value, str):
                        try:
                            number = float(value.strip())
                        except Exception:
                            number = None
                    if number is None:
                        errors.append(f"{sid}.{key} must be a number.")
                        continue

                    if value_type == "int":
                        if abs(number - round(number)) > 1e-9:
                            errors.append(f"{sid}.{key} must be an integer.")
                            continue
                        final_value: Any = int(round(number))
                    else:
                        final_value = float(number)

                    min_value = spec.get("min")
                    max_value = spec.get("max")
                    if isinstance(min_value, (int, float)) and final_value < min_value:
                        errors.append(f"{sid}.{key} must be >= {min_value}.")
                        continue
                    if isinstance(max_value, (int, float)) and final_value > max_value:
                        errors.append(f"{sid}.{key} must be <= {max_value}.")
                        continue

                    stage_out[key] = final_value
                    continue

                if value_type == "json":
                    if not isinstance(value, dict):
                        errors.append(f"{sid}.{key} must be a JSON object.")
                        continue
                    stage_out[key] = value
                    continue

                if value_type == "json_array":
                    if not isinstance(value, list):
                        errors.append(f"{sid}.{key} must be a JSON array.")
                        continue
                    stage_out[key] = value
                    continue

            if stage_out:
                normalized[sid] = stage_out

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "normalized_stage_params": normalized,
        }

    def _resolve_stage_selection(self, config: Dict[str, Any]) -> List[Dict[str, str]]:
        selected_raw = config.get("stage_ids", []) if isinstance(config, dict) else []
        all_ids = [spec["stage_id"] for spec in self.STAGE_SPECS]

        if not selected_raw:
            return list(self.STAGE_SPECS)

        if not isinstance(selected_raw, list):
            raise RuntimeError("stage_ids must be an array of stage identifiers.")

        selected_set = {str(item).strip().lower() for item in selected_raw if str(item).strip()}
        if not selected_set:
            raise RuntimeError("At least one valid stage id is required.")

        unknown = sorted(selected_set.difference(all_ids))
        if unknown:
            raise RuntimeError(f"Unknown stage_ids: {', '.join(unknown)}")

        return [spec for spec in self.STAGE_SPECS if spec["stage_id"] in selected_set]

    def _file_sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest().upper()

    def _safe_json_load(self, path: Path) -> Any:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _load_track_lookup(self) -> Dict[str, Dict[str, str]]:
        with self._track_lookup_lock:
            if self._track_lookup is not None:
                return self._track_lookup
            corpus_path = self.implementation_notes_root / "bl000_data_layer" / "outputs" / "ds001_working_candidate_dataset.csv"
            lookup: Dict[str, Dict[str, str]] = {}
            if corpus_path.exists():
                import csv as _csv
                try:
                    with corpus_path.open(encoding="utf-8", newline="") as fh:
                        reader = _csv.DictReader(fh)
                        for record in reader:
                            tid = record.get("id", "").strip()
                            if tid:
                                lookup[tid] = {
                                    "song": record.get("song", "").strip(),
                                    "artist": record.get("artist", "").strip(),
                                }
                except Exception:
                    pass
            self._track_lookup = lookup
            return lookup

    def _playlist_preview(self, payload: Any, max_items: int = 10) -> List[Dict[str, Any]]:
        rows: List[Any]
        if isinstance(payload, dict) and isinstance(payload.get("tracks"), list):
            rows = payload.get("tracks", [])
        elif isinstance(payload, list):
            rows = payload
        else:
            rows = []

        track_lookup = self._load_track_lookup()

        preview: List[Dict[str, Any]] = []
        for row in rows[:max_items]:
            if not isinstance(row, dict):
                continue
            track_id = row.get("track_id") or row.get("id") or "-"
            meta = track_lookup.get(track_id, {}) if track_id != "-" else {}
            preview.append({
                "track_id": track_id,
                "title": row.get("title") or row.get("track_name") or meta.get("song") or "-",
                "artist": row.get("artist") or row.get("artist_name") or meta.get("artist") or "-",
                "score": row.get("final_score") or row.get("score"),
            })
        return preview

    def _artifact_summary(self) -> Dict[str, Any]:
        targets = {
            "bl003_seed_table": self.implementation_notes_root / "bl003_alignment" / "outputs" / "bl003_ds001_spotify_seed_table.csv",
            "bl003_summary": self.implementation_notes_root / "bl003_alignment" / "outputs" / "bl003_ds001_spotify_summary.json",
            "bl004_profile": self.implementation_notes_root / "bl004_profile" / "outputs" / "bl004_preference_profile.json",
            "bl005_candidates": self.implementation_notes_root / "bl005_retrieval" / "outputs" / "bl005_filtered_candidates.csv",
            "bl006_scores": self.implementation_notes_root / "bl006_scoring" / "outputs" / "bl006_scored_candidates.csv",
            "bl007_playlist": self.implementation_notes_root / "bl007_playlist" / "outputs" / "bl007_playlist.json",
            "bl008_explanations": self.implementation_notes_root / "bl008_transparency" / "outputs" / "bl008_explanation_payloads.json",
            "bl008_explanation_summary": self.implementation_notes_root / "bl008_transparency" / "outputs" / "bl008_explanation_summary.json",
            "bl009_observability": self.implementation_notes_root / "bl009_observability" / "outputs" / "bl009_run_observability_log.json",
        }
        summary: Dict[str, Any] = {}
        for key, path in targets.items():
            if path.exists():
                stat = path.stat()
                summary[key] = {
                    "path": str(path.relative_to(self.repo_root)).replace("\\", "/"),
                    "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "size_bytes": stat.st_size,
                    "sha256": self._file_sha256(path),
                }
            else:
                summary[key] = {
                    "path": str(path.relative_to(self.repo_root)).replace("\\", "/"),
                    "missing": True,
                }
        return summary

    def _build_compare(self, newer: Dict[str, Any], older: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not older:
            return {
                "baseline_run_id": None,
                "changed_artifacts": [],
                "unchanged_artifacts": [],
                "changed_count": 0,
            }

        changed: List[str] = []
        unchanged: List[str] = []
        newer_artifacts = newer.get("artifact_summary", {}) if isinstance(newer, dict) else {}
        older_artifacts = older.get("artifact_summary", {}) if isinstance(older, dict) else {}

        all_keys = sorted(set(newer_artifacts.keys()) | set(older_artifacts.keys()))
        for key in all_keys:
            n = newer_artifacts.get(key, {})
            o = older_artifacts.get(key, {})
            if n.get("sha256") and o.get("sha256") and n.get("sha256") == o.get("sha256"):
                unchanged.append(key)
            elif n.get("missing") and o.get("missing"):
                unchanged.append(key)
            else:
                changed.append(key)

        return {
            "baseline_run_id": older.get("run_id"),
            "changed_artifacts": changed,
            "unchanged_artifacts": unchanged,
            "changed_count": len(changed),
        }

    def _record_history_locked(self) -> None:
        record = {
            "run_id": self.state.run_id,
            "status": self.state.status,
            "started_at_utc": self.state.started_at_utc,
            "completed_at_utc": self.state.completed_at_utc,
            "current_stage": self.state.current_stage,
            "current_message": self.state.current_message,
            "request_config": self.state.request_config,
            "line_count": self.state.line_count,
            "stages": [
                {
                    "stage_id": stage.stage_id,
                    "label": stage.label,
                    "status": stage.status,
                    "started_at_utc": stage.started_at_utc,
                    "completed_at_utc": stage.completed_at_utc,
                    "exit_code": stage.exit_code,
                    "current_message": stage.current_message,
                }
                for stage in self.state.stages
            ],
            "artifact_summary": self.state.artifact_summary,
        }
        self.history.append(record)

    def _terminalize_locked(self, status: str, current_stage: str, message: str) -> None:
        self.state.status = status
        self.state.current_stage = current_stage
        self.state.current_message = message
        self.state.completed_at_utc = now_utc()
        self.state.artifact_summary = self._artifact_summary()
        self.process = None
        self._record_history_locked()

    def start(self, config: Dict[str, Any]) -> None:
        selected_specs = self._resolve_stage_selection(config if isinstance(config, dict) else {})
        with self.lock:
            if self.process is not None and self.process.poll() is None:
                raise RuntimeError("A pipeline run is already in progress.")

            self.state = PipelineRunState(
                status="running",
                run_id=self._new_run_id(),
                started_at_utc=now_utc(),
                current_stage="starting",
                current_message="Starting deterministic BL-003 to BL-009 run...",
                request_config=config,
                stages=[
                    PipelineStageState(
                        stage_id=spec["stage_id"],
                        label=spec["label"],
                        script_path=spec["script"],
                    )
                    for spec in selected_specs
                ],
            )

        threading.Thread(target=self._run_pipeline, args=(selected_specs,), daemon=True).start()

    def cancel(self) -> None:
        with self.lock:
            if self.state.status != "running":
                raise RuntimeError("No pipeline run is currently in progress.")
            self.state.cancel_requested = True
            self.state.current_message = "Cancellation requested. Stopping active stage..."
            process = self.process

        if process is not None and process.poll() is None:
            process.terminate()

    def _run_pipeline(self, selected_specs: List[Dict[str, str]]) -> None:
        for spec in selected_specs:
            with self.lock:
                if self.state.cancel_requested:
                    self._terminalize_locked(
                        status="cancelled",
                        current_stage="cancelled",
                        message="Pipeline run cancelled by user request.",
                    )
                    return

            stage_id = spec["stage_id"]
            stage = self._find_stage(stage_id)
            with self.lock:
                stage.status = "running"
                stage.started_at_utc = now_utc()
                stage.current_message = f"Running {stage.label}"
                stage.log_start_index = self.state.line_count + 1
                self.state.current_stage = stage_id
                self.state.current_message = f"Running {stage.label}"

            stage_params = {}
            try:
                stage_params = (self.state.request_config.get("stage_params", {}) or {}).get(stage_id, {})
            except Exception:
                stage_params = {}

            command = self._stage_command(spec["script"], stage_id, stage_params)

            env = os.environ.copy()
            env.update(self._stage_env_overrides(stage_id, stage_params))
            process = subprocess.Popen(
                command,
                cwd=str(self.repo_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            with self.lock:
                self.process = process

            assert process.stdout is not None
            for line in process.stdout:
                self._append_log(line, stage_id=stage_id)

            exit_code = process.wait()

            with self.lock:
                stage.completed_at_utc = now_utc()
                stage.exit_code = exit_code
                stage.log_end_index = self.state.line_count

                if self.state.cancel_requested:
                    stage.status = "cancelled"
                    stage.current_message = f"{stage.label} cancelled."
                    self._terminalize_locked(
                        status="cancelled",
                        current_stage="cancelled",
                        message="Pipeline run cancelled by user request.",
                    )
                    return

                if exit_code != 0:
                    stage.status = "failed"
                    stage.current_message = f"{stage.label} failed with exit code {exit_code}."
                    self._terminalize_locked(
                        status="failed",
                        current_stage=stage_id,
                        message=stage.current_message,
                    )
                    return

                stage.status = "completed"
                stage.current_message = f"{stage.label} completed successfully."

            time.sleep(0.05)

        with self.lock:
            self._terminalize_locked(
                status="completed",
                current_stage="completed",
                message="Pipeline run completed successfully.",
            )

    def history_snapshot(self, limit: int = 10) -> Dict[str, Any]:
        with self.lock:
            limit = max(1, min(limit, 50))
            ordered = list(self.history)[-limit:]
            ordered.reverse()

            enriched: List[Dict[str, Any]] = []
            for index, record in enumerate(ordered):
                older = ordered[index + 1] if index + 1 < len(ordered) else None
                compare = self._build_compare(record, older)
                item = dict(record)
                item["compare_to_previous"] = compare
                enriched.append(item)

            return {
                "server_time_utc": now_utc(),
                "history_count": len(self.history),
                "runs": enriched,
            }

    def _pick_run_locked(self, run_id: Optional[str]) -> Optional[Dict[str, Any]]:
        if run_id:
            if self.state.run_id == run_id:
                return {
                    "run_id": self.state.run_id,
                    "status": self.state.status,
                    "started_at_utc": self.state.started_at_utc,
                    "completed_at_utc": self.state.completed_at_utc,
                    "current_stage": self.state.current_stage,
                    "current_message": self.state.current_message,
                    "request_config": self.state.request_config,
                    "selected_stage_ids": [stage.stage_id for stage in self.state.stages],
                    "available_stage_ids": [spec["stage_id"] for spec in self.STAGE_SPECS],
                    "line_count": self.state.line_count,
                    "stages": [
                        {
                            "stage_id": stage.stage_id,
                            "label": stage.label,
                            "status": stage.status,
                            "started_at_utc": stage.started_at_utc,
                            "completed_at_utc": stage.completed_at_utc,
                            "exit_code": stage.exit_code,
                            "current_message": stage.current_message,
                        }
                        for stage in self.state.stages
                    ],
                    "artifact_summary": self.state.artifact_summary,
                }

            for record in reversed(self.history):
                if record.get("run_id") == run_id:
                    return dict(record)
            return None

        if self.history:
            return dict(self.history[-1])

        if self.state.run_id:
            return {
                "run_id": self.state.run_id,
                "status": self.state.status,
                "started_at_utc": self.state.started_at_utc,
                "completed_at_utc": self.state.completed_at_utc,
                "current_stage": self.state.current_stage,
                "current_message": self.state.current_message,
                "request_config": self.state.request_config,
                "line_count": self.state.line_count,
                "stages": [
                    {
                        "stage_id": stage.stage_id,
                        "label": stage.label,
                        "status": stage.status,
                        "started_at_utc": stage.started_at_utc,
                        "completed_at_utc": stage.completed_at_utc,
                        "exit_code": stage.exit_code,
                        "current_message": stage.current_message,
                    }
                    for stage in self.state.stages
                ],
                "artifact_summary": self.state.artifact_summary,
            }

        return None

    def results_snapshot(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        with self.lock:
            selected = self._pick_run_locked(run_id)

        playlist_path = self.implementation_notes_root / "bl007_playlist" / "outputs" / "bl007_playlist.json"
        explanation_summary_path = self.implementation_notes_root / "bl008_transparency" / "outputs" / "bl008_explanation_summary.json"
        observability_path = self.implementation_notes_root / "bl009_observability" / "outputs" / "bl009_run_observability_log.json"

        playlist_payload = self._safe_json_load(playlist_path)
        explanation_summary = self._safe_json_load(explanation_summary_path)
        observability_payload = self._safe_json_load(observability_path)

        playlist_preview = self._playlist_preview(playlist_payload, max_items=10)
        compare = None
        if selected and self.history:
            selected_id = selected.get("run_id")
            ordered = list(self.history)
            ordered.reverse()
            target_index = next((idx for idx, item in enumerate(ordered) if item.get("run_id") == selected_id), None)
            if target_index is not None:
                older = ordered[target_index + 1] if target_index + 1 < len(ordered) else None
                compare = self._build_compare(ordered[target_index], older)

        return {
            "server_time_utc": now_utc(),
            "run": selected,
            "playlist_preview": playlist_preview,
            "playlist_payload": playlist_payload,
            "explanation_summary": explanation_summary,
            "observability_summary": observability_payload,
            "compare_to_previous": compare,
        }

    def create_evidence_bundle(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        with self.lock:
            selected = self._pick_run_locked(run_id)

        if selected is None:
            raise RuntimeError("No pipeline run evidence is available yet.")

        results = self.results_snapshot(run_id=selected.get("run_id"))
        manifest = {
            "bundle_generated_at_utc": now_utc(),
            "bundle_type": "website_pipeline_evidence",
            "run": results.get("run"),
            "compare_to_previous": results.get("compare_to_previous"),
            "playlist_preview": results.get("playlist_preview"),
            "explanation_summary": results.get("explanation_summary"),
            "artifact_summary": (results.get("run") or {}).get("artifact_summary", {}),
        }

        run_key = (selected.get("run_id") or "unknown").replace(":", "-")
        output_path = self.observability_output_root / f"website_evidence_bundle_{run_key}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")

        return {
            "server_time_utc": now_utc(),
            "run_id": selected.get("run_id"),
            "bundle_path": str(output_path.relative_to(self.repo_root)).replace("\\", "/"),
            "bundle": manifest,
        }

    def snapshot(self, after: int = 0) -> Dict[str, Any]:
        with self.lock:
            logs = [entry for entry in self.state.logs if entry["index"] > after]
            return {
                "server_time_utc": now_utc(),
                "run": {
                    "status": self.state.status,
                    "run_id": self.state.run_id,
                    "started_at_utc": self.state.started_at_utc,
                    "completed_at_utc": self.state.completed_at_utc,
                    "current_stage": self.state.current_stage,
                    "current_message": self.state.current_message,
                    "cancel_requested": self.state.cancel_requested,
                    "request_config": self.state.request_config,
                    "line_count": self.state.line_count,
                    "selected_stage_ids": [stage.stage_id for stage in self.state.stages],
                    "available_stage_ids": [spec["stage_id"] for spec in self.STAGE_SPECS],
                    "logs": logs,
                    "history_count": len(self.history),
                    "stages": [
                        {
                            "stage_id": stage.stage_id,
                            "label": stage.label,
                            "script_path": stage.script_path,
                            "status": stage.status,
                            "started_at_utc": stage.started_at_utc,
                            "completed_at_utc": stage.completed_at_utc,
                            "exit_code": stage.exit_code,
                            "current_message": stage.current_message,
                            "log_start_index": stage.log_start_index,
                            "log_end_index": stage.log_end_index,
                        }
                        for stage in self.state.stages
                    ],
                    "artifact_summary": self.state.artifact_summary,
                },
            }


# ---------------------------------------------------------------------------
# Path constants — resolved once at import time
# ---------------------------------------------------------------------------
_SETUP_DIR = Path(__file__).resolve().parent   # 07_implementation/setup/
_IMPL_ROOT = _SETUP_DIR.parent                 # 07_implementation/
_REPO_ROOT = _IMPL_ROOT.parent                 # thesis-main/
_WEBSITE_ROOT = _IMPL_ROOT / "website"         # 07_implementation/website/

# ---------------------------------------------------------------------------
# Runtime state — populated by main() before uvicorn starts
# ---------------------------------------------------------------------------
app = FastAPI(title="Playlist Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(127\.0\.0\.1|localhost)(:\d+)?$",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/website", StaticFiles(directory=str(_WEBSITE_ROOT), html=True), name="website")


def initialize_app_state(bind: str, port: int, repo_root: Optional[Path] = None) -> None:
    resolved_repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
    app.state.bind = bind
    app.state.port = port
    app.state.started_at_utc = now_utc()
    app.state.started_monotonic = time.time()
    app.state.export_job = SpotifyExportJob(repo_root=resolved_repo_root)
    app.state.pipeline_job = PipelineJob(repo_root=resolved_repo_root)


def _get_pipeline_job(request: Request) -> PipelineJob:
    pipeline_job = getattr(request.app.state, "pipeline_job", None)
    if pipeline_job is None:
        raise HTTPException(status_code=503, detail="Pipeline job is not initialized.")
    return pipeline_job


def _get_export_job(request: Request) -> SpotifyExportJob:
    export_job = getattr(request.app.state, "export_job", None)
    if export_job is None:
        raise HTTPException(status_code=503, detail="Spotify export job is not initialized.")
    return export_job


def _error_response(detail: Any, status_code: int) -> JSONResponse:
    if isinstance(detail, str):
        content: Dict[str, Any] = {"error": detail}
    elif isinstance(detail, dict):
        content = detail
    else:
        content = {"error": str(detail)}
    return JSONResponse(status_code=status_code, content=content)


@app.exception_handler(HTTPException)
def _http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return {"error": "..."} for app-raised HTTPExceptions so the JS can read payload.error."""
    return _error_response(exc.detail, exc.status_code)


@app.exception_handler(StarletteHTTPException)
def _starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return _error_response(exc.detail, exc.status_code)


@app.exception_handler(RequestValidationError)
def _request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return _error_response({"error": "Request validation failed.", "details": exc.errors()}, 422)


@app.get("/")
def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/website/import.html")


# ---------------------------------------------------------------------------
# GET routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
def api_health(request: Request) -> Dict[str, Any]:
    pipeline_state = _get_pipeline_job(request).snapshot().get("run", {})
    export_state = _get_export_job(request).snapshot().get("run", {})
    uptime_seconds = max(0, int(time.time() - request.app.state.started_monotonic))
    return {
        "server_time_utc": now_utc(),
        "status": "ok",
        "uptime_seconds": uptime_seconds,
        "started_at_utc": request.app.state.started_at_utc,
        "server": {
            "bind": request.app.state.bind,
            "port": request.app.state.port,
            "serve_root": str(_IMPL_ROOT).replace("\\", "/"),
        },
        "services": {
            "pipeline": {
                "status": pipeline_state.get("status", "idle"),
                "run_id": pipeline_state.get("run_id"),
            },
            "spotify_export": {
                "status": export_state.get("status", "idle"),
                "line_count": export_state.get("line_count", 0),
            },
        },
    }


@app.get("/api/runtime/config")
def api_runtime_config(request: Request) -> Dict[str, Any]:
    payload = _get_pipeline_job(request).runtime_config_snapshot()
    payload["server"] = {
        "bind": request.app.state.bind,
        "port": request.app.state.port,
        "started_at_utc": request.app.state.started_at_utc,
    }
    return payload


@app.get("/api/pipeline/stages")
def api_pipeline_stages(request: Request) -> Dict[str, Any]:
    return _get_pipeline_job(request).stage_catalog()


@app.get("/api/pipeline/run/history")
def api_pipeline_run_history(request: Request, limit: int = Query(default=10, le=50)) -> Dict[str, Any]:
    return _get_pipeline_job(request).history_snapshot(limit=limit)


@app.get("/api/pipeline/run/status")
def api_pipeline_run_status(request: Request, after: int = Query(default=0)) -> Dict[str, Any]:
    return _get_pipeline_job(request).snapshot(after=max(0, after))


@app.get("/api/pipeline/run/results")
def api_pipeline_run_results(request: Request, run_id: Optional[str] = None) -> Dict[str, Any]:
    return _get_pipeline_job(request).results_snapshot(run_id=run_id)


@app.get("/api/spotify/export/status")
def api_spotify_export_status(request: Request, after: int = Query(default=0)) -> Dict[str, Any]:
    return _get_export_job(request).snapshot(after=max(0, after))


# ---------------------------------------------------------------------------
# POST routes
# ---------------------------------------------------------------------------

@app.post("/api/runtime/config/validate")
def api_runtime_config_validate(request: Request, payload: RuntimeConfigValidateRequest = Body(default_factory=RuntimeConfigValidateRequest)) -> JSONResponse:
    try:
        result = _get_pipeline_job(request).validate_stage_params_payload(payload.model_dump(exclude_none=True))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to validate runtime config: {exc}")
    status_code = 200 if result.get("valid") else 400
    return JSONResponse(content={"server_time_utc": now_utc(), **result}, status_code=status_code)


@app.post("/api/pipeline/run/start", status_code=202)
def api_pipeline_run_start(request: Request, payload: PipelineRunStartRequest = Body(default_factory=PipelineRunStartRequest)) -> Dict[str, Any]:
    try:
        _get_pipeline_job(request).start(payload.model_dump(exclude_none=True))
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to start pipeline run: {exc}")
    return _get_pipeline_job(request).snapshot()


@app.post("/api/pipeline/run/cancel", status_code=202)
def api_pipeline_run_cancel(request: Request) -> Dict[str, Any]:
    try:
        _get_pipeline_job(request).cancel()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return _get_pipeline_job(request).snapshot()


@app.post("/api/pipeline/run/evidence_bundle", status_code=202)
def api_pipeline_run_evidence_bundle(request: Request, payload: EvidenceBundleRequest = Body(default_factory=EvidenceBundleRequest)) -> Dict[str, Any]:
    try:
        bundle = _get_pipeline_job(request).create_evidence_bundle(run_id=payload.run_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to create evidence bundle: {exc}")
    return bundle


@app.post("/api/spotify/export/start", status_code=202)
def api_spotify_export_start(request: Request, payload: SpotifyExportStartRequest = Body(default_factory=SpotifyExportStartRequest)) -> Dict[str, Any]:
    try:
        _get_export_job(request).start(payload.model_dump(exclude_none=True))
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to start ingestion: {exc}")
    return _get_export_job(request).snapshot()


@app.post("/api/spotify/export/cancel", status_code=202)
def api_spotify_export_cancel(request: Request) -> Dict[str, Any]:
    try:
        _get_export_job(request).cancel()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return _get_export_job(request).snapshot()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    bind = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5501
    initialize_app_state(bind=bind, port=port)

    print(f"Serving website + API on http://{bind}:{port}/", flush=True)
    print(f"Import page: http://{bind}:{port}/website/import.html", flush=True)
    print(f"API docs:    http://{bind}:{port}/docs", flush=True)
    uvicorn.run(app, host=bind, port=port, log_level="warning")


if __name__ == "__main__":
    main()
