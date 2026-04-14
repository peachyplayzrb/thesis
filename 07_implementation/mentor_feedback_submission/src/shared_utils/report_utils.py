"""
Small helpers for writing the report-style artifacts used in the later stages.

I kept these together so the JSON and CSV output formatting stays consistent
without making every reporting script reimplement the same write logic.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

from shared_utils.io_utils import open_text_write


def write_text(path: Path, text: str) -> None:
    """Write UTF-8 text, creating parent directories when needed."""
    with open_text_write(path) as handle:
        handle.write(text)


def write_json_ascii(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    """Write pretty JSON with ASCII escaping, creating parent directories when needed."""
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=True))


def write_csv_rows(path: Path, rows: list[dict[str, object]]) -> None:
    """Write matrix rows to CSV with LF line endings, creating parent directories when needed."""
    if not rows:
        raise ValueError("rows must not be empty")
    with open_text_write(path, newline="") as handle:
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
