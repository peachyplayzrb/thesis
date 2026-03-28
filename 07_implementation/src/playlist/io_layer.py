"""I/O helpers for BL-007 playlist assembly."""

from __future__ import annotations

import csv
from pathlib import Path

from shared_utils.env_utils import env_path
from shared_utils.io_utils import open_text_write, write_json
from shared_utils.path_utils import impl_root


DEFAULT_SCORED_CANDIDATES_PATH = Path("scoring/outputs/bl006_scored_candidates.csv")
DEFAULT_OUTPUT_DIR = Path("playlist/outputs")
REQUIRED_CANDIDATE_COLUMNS = ("rank", "track_id", "lead_genre", "final_score")


def resolve_bl007_paths() -> tuple[Path, Path]:
    """Resolve BL-007 input and output paths from environment or defaults."""
    scored_candidates_path = env_path(
        "BL007_SCORED_CANDIDATES_PATH",
        impl_root() / DEFAULT_SCORED_CANDIDATES_PATH,
    )
    output_dir = env_path("BL007_OUTPUT_DIR", impl_root() / DEFAULT_OUTPUT_DIR)
    return scored_candidates_path, output_dir


def read_scored_candidates(path: Path) -> list[dict[str, str]]:
    """Read BL-006 scored candidates with required-column validation."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("BL-007 scored candidates CSV has no header row.")
        missing_columns = [
            column
            for column in REQUIRED_CANDIDATE_COLUMNS
            if column not in set(reader.fieldnames)
        ]
        if missing_columns:
            raise ValueError(
                "BL-007 scored candidates CSV is missing required column(s): "
                + ", ".join(missing_columns)
            )
        return list(reader)


def write_assembly_trace(path: Path, trace_rows: list[dict[str, object]]) -> None:
    """Write BL-007 assembly trace CSV."""
    trace_fields = [
        "score_rank",
        "track_id",
        "lead_genre",
        "final_score",
        "decision",
        "playlist_position",
        "exclusion_reason",
    ]
    with open_text_write(path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=trace_fields)
        writer.writeheader()
        writer.writerows(trace_rows)


def write_playlist(path: Path, payload: dict[str, object]) -> None:
    """Write playlist.json payload."""
    write_json(path, payload)


def write_report(path: Path, payload: dict[str, object]) -> None:
    """Write bl007_assembly_report.json payload."""
    write_json(path, payload)


def write_detail_log(path: Path, payload: dict[str, object]) -> None:
    """Write bl007_assembly_detail_log.json payload."""
    write_json(path, payload)
