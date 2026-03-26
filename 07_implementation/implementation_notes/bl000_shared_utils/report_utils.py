"""
Shared helpers for writing report and matrix artifacts.

These helpers keep JSON/CSV output behavior consistent across BL010-BL014
without changing stage-specific report schemas.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any


def write_text(path: Path, text: str) -> None:
    """Write UTF-8 text, creating parent directories when needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json_ascii(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    """Write pretty JSON with ASCII escaping, creating parent directories when needed."""
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=True))


def write_csv_rows(path: Path, rows: list[dict[str, object]]) -> None:
    """Write matrix rows to CSV with LF line endings, creating parent directories when needed."""
    if not rows:
        raise ValueError("rows must not be empty")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def render_csv_text(fieldnames: list[str], rows: list[dict[str, object]]) -> str:
    """Render CSV rows to UTF-8 text with LF line endings."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()