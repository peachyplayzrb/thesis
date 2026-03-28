from __future__ import annotations

import argparse
import threading

import pytest

from ingestion import spotify_auth


def _auth_args() -> argparse.Namespace:
    return argparse.Namespace(
        redirect_uri="http://127.0.0.1:8001/spotify/auth/callback",
        client_id="client-id",
        client_secret="client-secret",
        scopes="user-top-read",
        no_browser=True,
        oauth_timeout_seconds=1,
        request_timeout_seconds=5,
    )


class _FakeServer:
    def __init__(self, *_args, **_kwargs) -> None:
        self.shutdown_called = False

    def serve_forever(self) -> None:
        return

    def shutdown(self) -> None:
        self.shutdown_called = True


class _FakeThread:
    def __init__(self, target=None, daemon=False) -> None:
        self.target = target
        self.daemon = daemon

    def start(self) -> None:
        return


def _patch_server_and_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(spotify_auth, "HTTPServer", _FakeServer)
    monkeypatch.setattr(spotify_auth.threading, "Thread", _FakeThread)


def test_complete_oauth_flow_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_server_and_thread(monkeypatch)

    class _NeverSetEvent:
        def wait(self, timeout: float) -> bool:
            return False

    callback_state = spotify_auth.OAuthCallbackState()
    callback_state.event = _NeverSetEvent()  # type: ignore[assignment]

    monkeypatch.setattr(spotify_auth, "OAuthCallbackState", lambda: callback_state)

    with pytest.raises(TimeoutError, match="Timed out"):
        spotify_auth.complete_oauth_flow(_auth_args())


def test_complete_oauth_flow_callback_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_server_and_thread(monkeypatch)

    callback_state = spotify_auth.OAuthCallbackState()
    callback_state.error = "access_denied"
    callback_state.event = threading.Event()
    callback_state.event.set()

    monkeypatch.setattr(spotify_auth, "OAuthCallbackState", lambda: callback_state)

    with pytest.raises(RuntimeError, match="authorization error"):
        spotify_auth.complete_oauth_flow(_auth_args())


def test_complete_oauth_flow_state_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_server_and_thread(monkeypatch)

    callback_state = spotify_auth.OAuthCallbackState()
    callback_state.state = "wrong-state"
    callback_state.code = "auth-code"
    callback_state.event = threading.Event()
    callback_state.event.set()

    monkeypatch.setattr(spotify_auth, "OAuthCallbackState", lambda: callback_state)
    monkeypatch.setattr(spotify_auth.secrets, "token_urlsafe", lambda _n: "expected-state")

    with pytest.raises(RuntimeError, match="state mismatch"):
        spotify_auth.complete_oauth_flow(_auth_args())


def test_complete_oauth_flow_missing_code(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_server_and_thread(monkeypatch)

    callback_state = spotify_auth.OAuthCallbackState()
    callback_state.state = "expected-state"
    callback_state.code = None
    callback_state.event = threading.Event()
    callback_state.event.set()

    monkeypatch.setattr(spotify_auth, "OAuthCallbackState", lambda: callback_state)
    monkeypatch.setattr(spotify_auth.secrets, "token_urlsafe", lambda _n: "expected-state")

    with pytest.raises(RuntimeError, match="Missing authorization code"):
        spotify_auth.complete_oauth_flow(_auth_args())
