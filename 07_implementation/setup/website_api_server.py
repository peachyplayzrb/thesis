from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
import urllib.parse
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
        self.export_root = self.implementation_notes_root / "ingestion" / "outputs" / "spotify_api_export"
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
            "ingestion.export_spotify_max_dataset",
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


class WebsiteApiHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, directory: str | None = None, **kwargs: Any) -> None:
        super().__init__(*args, directory=directory, **kwargs)

    def _send_json(self, payload: Dict[str, Any], status: int = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/spotify/export/status":
            query = urllib.parse.parse_qs(parsed.query)
            after = int(query.get("after", ["0"])[0])
            self._send_json(self.server.export_job.snapshot(after=after))
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/spotify/export/start":
            self._send_json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
            payload = json.loads(raw or "{}")
            self.server.export_job.start(payload)
        except RuntimeError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.CONFLICT)
            return
        except Exception as exc:
            self._send_json({"error": f"Unable to start ingestion: {exc}"}, status=HTTPStatus.BAD_REQUEST)
            return

        self._send_json(self.server.export_job.snapshot(), status=HTTPStatus.ACCEPTED)


class WebsiteApiServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], handler_class: type[WebsiteApiHandler], serve_root: Path, export_job: SpotifyExportJob) -> None:
        self.serve_root = serve_root
        self.export_job = export_job
        super().__init__(server_address, lambda *args, **kwargs: handler_class(*args, directory=str(serve_root), **kwargs))


def main() -> None:
    bind = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5501

    setup_dir = Path(__file__).resolve().parent
    implementation_root = setup_dir.parent
    repo_root = implementation_root.parent
    export_job = SpotifyExportJob(repo_root=repo_root)

    server = WebsiteApiServer((bind, port), WebsiteApiHandler, implementation_root, export_job)
    print(f"Serving website + API on http://{bind}:{port}/", flush=True)
    print(f"Import page: http://{bind}:{port}/website/import.html", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()