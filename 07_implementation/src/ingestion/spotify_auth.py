from __future__ import annotations

import base64
import json
import secrets
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional, Tuple

ACCOUNTS_BASE_URL = "https://accounts.spotify.com"


class OAuthCallbackState:
    def __init__(self) -> None:
        self.code: Optional[str] = None
        self.state: Optional[str] = None
        self.error: Optional[str] = None
        self.event = threading.Event()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    shared_state: OAuthCallbackState

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)

        OAuthCallbackHandler.shared_state.code = query.get("code", [None])[0]
        OAuthCallbackHandler.shared_state.state = query.get("state", [None])[0]
        OAuthCallbackHandler.shared_state.error = query.get("error", [None])[0]
        OAuthCallbackHandler.shared_state.event.set()

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            (
                "<html><body><h3>Spotify authorization received.</h3>"
                "<p>You can close this tab and return to the terminal.</p>"
                "</body></html>"
            ).encode("utf-8")
        )

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def parse_redirect_bind(redirect_uri: str) -> Tuple[str, int]:
    parsed = urllib.parse.urlparse(redirect_uri)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 80
    return host, port


def build_authorize_url(client_id: str, redirect_uri: str, scopes: str, state: str) -> str:
    query = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": scopes,
            "state": state,
            "show_dialog": "true",
        }
    )
    return f"{ACCOUNTS_BASE_URL}/authorize?{query}"


def request_token(
    client_id: str,
    client_secret: str,
    body_fields: Dict[str, str],
    timeout_seconds: int,
) -> Dict[str, Any]:
    payload = urllib.parse.urlencode(body_fields).encode("utf-8")
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    req = urllib.request.Request(
        url=f"{ACCOUNTS_BASE_URL}/api/token",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def complete_oauth_flow(args: Any) -> Dict[str, Any]:
    bind_host, bind_port = parse_redirect_bind(args.redirect_uri)
    state = secrets.token_urlsafe(24)

    callback_state = OAuthCallbackState()
    OAuthCallbackHandler.shared_state = callback_state

    server = HTTPServer((bind_host, bind_port), OAuthCallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    authorize_url = build_authorize_url(args.client_id, args.redirect_uri, args.scopes, state)
    print("Open this URL to authorize:")
    print(authorize_url)

    if not args.no_browser:
        webbrowser.open(authorize_url)

    try:
        deadline = time.time() + float(args.oauth_timeout_seconds)
        while True:
            remaining = max(0.0, deadline - time.time())
            if remaining <= 0.0 or not callback_state.event.wait(timeout=remaining):
                raise TimeoutError("Timed out waiting for Spotify OAuth callback.")

            if callback_state.error:
                raise RuntimeError(f"Spotify authorization error: {callback_state.error}")
            if callback_state.state != state:
                # Ignore stale callbacks from prior auth attempts and keep waiting.
                print("[auth] ignored stale OAuth callback state", flush=True)
                callback_state.code = None
                callback_state.state = None
                callback_state.error = None
                callback_state.event.clear()
                continue
            if not callback_state.code:
                raise RuntimeError("Missing authorization code in callback.")
            break

        token_response = request_token(
            client_id=args.client_id,
            client_secret=args.client_secret,
            body_fields={
                "grant_type": "authorization_code",
                "code": callback_state.code,
                "redirect_uri": args.redirect_uri,
            },
            timeout_seconds=args.request_timeout_seconds,
        )
        expires_in = int(token_response.get("expires_in", 3600))
        token_response["expires_at_epoch"] = int(time.time()) + expires_in
        return token_response
    finally:
        server.shutdown()
