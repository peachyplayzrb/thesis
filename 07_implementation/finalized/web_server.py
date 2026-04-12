"""Minimal local web + API wrapper for the thesis pipeline.

Runs from any working directory by resolving paths from this script location.
This wrapper does not modify core pipeline logic under src.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
IMPL_ROOT = BASE_DIR.parent
THESIS_WRAPPER = IMPL_ROOT / "main.py"
INDEX_FILE = BASE_DIR / "web" / "index.html"
CONFIG_DIR = IMPL_ROOT / "config" / "profiles"

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

PREVIEW_MAX_CHARS = 20000


def _iso_utc_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


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

        if route.endswith("/api/status"):
            self._send_json(200, _status_payload())
            return

        if route.endswith("/api/artifacts"):
            self._send_json(200, {"artifacts": _artifact_manifest()})
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
        if self.path != "/api/run":
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
