"""
Shared hashing utilities for deterministic artifact verification.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_of_text(text: str, *, uppercase: bool = False) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return digest.upper() if uppercase else digest


def sha256_of_file(path: Path, *, uppercase: bool = False) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    result = digest.hexdigest()
    return result.upper() if uppercase else result


def canonical_json_hash(
    payload: Any,
    *,
    uppercase: bool = False,
    ensure_ascii: bool = True,
) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=ensure_ascii, separators=(",", ":"))
    return sha256_of_text(canonical, uppercase=uppercase)
