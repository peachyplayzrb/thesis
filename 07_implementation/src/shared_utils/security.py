from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse


def ensure_trusted_https_url(url: str, *, allowed_hosts: set[str]) -> None:
    parsed = urlparse(url)
    scheme = (parsed.scheme or "").lower()
    host = (parsed.hostname or "").lower()
    if scheme != "https":
        raise ValueError(f"Untrusted URL scheme: {scheme or '<empty>'}")
    if host not in allowed_hosts:
        raise ValueError(f"Untrusted URL host: {host or '<empty>'}")


def ensure_subprocess_script_under_root(script_path: Path, *, root: Path) -> None:
    resolved_root = root.resolve()
    resolved_script = script_path.resolve()
    if not resolved_script.is_file():
        raise FileNotFoundError(f"Subprocess script path does not exist: {resolved_script}")
    if not resolved_script.is_relative_to(resolved_root):
        raise ValueError(
            f"Subprocess script path escapes root: script={resolved_script} root={resolved_root}"
        )


def ensure_subprocess_command_tokens(tokens: list[str]) -> None:
    if not tokens:
        raise ValueError("Subprocess command must not be empty")
    for token in tokens:
        if not isinstance(token, str) or not token.strip():
            raise ValueError("Subprocess command contains empty token")
        if "\x00" in token:
            raise ValueError("Subprocess command contains null-byte token")
