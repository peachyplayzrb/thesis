"""Very simple local web wrapper for thesis.py.

Runs from any working directory by resolving paths from this script location.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
THESIS_SCRIPT = BASE_DIR / "thesis.py"
INDEX_FILE = BASE_DIR / "web" / "index.html"
CONFIG_DIR = BASE_DIR / "config"


class ThesisWebHandler(BaseHTTPRequestHandler):
    """HTTP handler for the tiny thesis web app."""

    def do_GET(self) -> None:
        """Serve the single-page UI."""
        parsed = urlparse(self.path)
        route = parsed.path.strip()
        if route != "/" and route.endswith("/"):
            route = route[:-1]
        route = "/" + route.lstrip("/")

        if route.endswith("/api/configs"):
            self._send_json(200, {"configs": self._list_config_files()})
            return

        if route.endswith("/api/run-stream"):
            params = parse_qs(parsed.query)
            config_path = ""
            if "config_path" in params and params["config_path"]:
                config_path = params["config_path"][0]
            self._stream_thesis(config_path)
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

        result = self._run_thesis(config_path)
        self._send_json(200, result)

    def _read_json_body(self) -> dict[str, Any]:
        """Best-effort JSON body parse.

        Shell behavior: if request parsing fails, pass an empty config path through
        to thesis.py and let thesis.py report the error.
        """
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

    def _list_config_files(self) -> list[str]:
        """Return sorted config JSON paths from config folder."""
        try:
            names = [
                path.name
                for path in CONFIG_DIR.iterdir()
                if path.name.lower().endswith(".json") and path.is_file()
            ]
        except OSError:
            return []

        names.sort()
        return [f"config/{name}" for name in names]

    def _run_thesis(self, config_path: str) -> dict[str, Any]:
        """Run thesis.py and return terminal-like output text."""
        command = [sys.executable, str(THESIS_SCRIPT), config_path]
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=str(BASE_DIR),
        )

        # Mimic a simple terminal view: command line + combined stdout/stderr.
        command_line = " ".join(command)
        combined_output = f"$ {command_line}\n"
        if process.stdout:
            combined_output += process.stdout
        if process.stderr:
            combined_output += process.stderr

        return {
            "ok": process.returncode == 0,
            "exit_code": process.returncode,
            "terminal_output": combined_output,
        }

    def _stream_thesis(self, config_path: str) -> None:
        """Stream thesis output line-by-line using Server-Sent Events (SSE)."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        command = [sys.executable, "-u", str(THESIS_SCRIPT), config_path]
        self._sse_write("line", f"$ {' '.join(command)}")

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(BASE_DIR),
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
