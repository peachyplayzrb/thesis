from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from bl000_shared_utils.io_utils import open_text_write

OUTPUT_FIELDNAMES = [
    "id",
    "spotify_id",
    "artist",
    "song",
    "album_name",
    "release",
    "duration_ms",
    "popularity",
    "danceability",
    "energy",
    "key",
    "mode",
    "valence",
    "tempo",
    "tags",
    "genres",
    "lang",
]


def parse_args() -> argparse.Namespace:
    import os
    script_path = Path(__file__).resolve()
    default_output_dir = script_path.parent / "outputs"
    
    # For standalone mode: dataset-root must be provided via --dataset-root or IMPL_DATASET_ROOT env var
    default_dataset_root = os.environ.get("IMPL_DATASET_ROOT")

    parser = argparse.ArgumentParser(
        description="Build a compact DS-001 working candidate dataset for runtime pipeline use."
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=default_dataset_root,
        required=(default_dataset_root is None),
        help="Path to music4all dataset root. Required unless IMPL_DATASET_ROOT is set.",
    )
    parser.add_argument("--output-dir", type=Path, default=default_output_dir)
    parser.add_argument(
        "--exclude-lang",
        action="store_true",
        help="If set, lang will be emitted as empty strings even when id_lang.csv exists.",
    )
    return parser.parse_args()


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_tsv_by_id(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            row_id = (row.get("id") or "").strip()
            if not row_id:
                continue
            rows[row_id] = {k: (v.strip() if isinstance(v, str) else "") for k, v in row.items()}
    return rows


def to_int_text(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    try:
        return str(int(float(text)))
    except ValueError:
        return ""


def to_float_text(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    try:
        number = float(text)
    except ValueError:
        return ""
    return f"{number:.6f}"


def build_output_row(
    row_id: str,
    info_row: dict[str, str],
    metadata_row: dict[str, str],
    tags_row: dict[str, str],
    genres_row: dict[str, str],
    lang_row: dict[str, str] | None,
    include_lang: bool,
) -> dict[str, str]:
    return {
        "id": row_id,
        "spotify_id": metadata_row.get("spotify_id", ""),
        "artist": info_row.get("artist", ""),
        "song": info_row.get("song", ""),
        "album_name": info_row.get("album_name", ""),
        "release": to_int_text(metadata_row.get("release", "")),
        "duration_ms": to_int_text(metadata_row.get("duration_ms", "")),
        "popularity": to_float_text(metadata_row.get("popularity", "")),
        "danceability": to_float_text(metadata_row.get("danceability", "")),
        "energy": to_float_text(metadata_row.get("energy", "")),
        "key": to_int_text(metadata_row.get("key", "")),
        "mode": to_int_text(metadata_row.get("mode", "")),
        "valence": to_float_text(metadata_row.get("valence", "")),
        "tempo": to_float_text(metadata_row.get("tempo", "")),
        "tags": tags_row.get("tags", ""),
        "genres": genres_row.get("genres", ""),
        "lang": (lang_row.get("lang", "") if (include_lang and lang_row is not None) else ""),
    }


def main() -> None:
    args = parse_args()

    dataset_root = args.dataset_root
    output_dir = args.output_dir
    include_lang = not args.exclude_lang

    id_information_path = dataset_root / "id_information.csv"
    id_metadata_path = dataset_root / "id_metadata.csv"
    id_tags_path = dataset_root / "id_tags.csv"
    id_genres_path = dataset_root / "id_genres.csv"
    id_lang_path = dataset_root / "id_lang.csv"

    required_paths = [id_information_path, id_metadata_path, id_tags_path, id_genres_path]
    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(f"Required input file not found: {path}")

    info_by_id = read_tsv_by_id(id_information_path)
    metadata_by_id = read_tsv_by_id(id_metadata_path)
    tags_by_id = read_tsv_by_id(id_tags_path)
    genres_by_id = read_tsv_by_id(id_genres_path)
    lang_by_id = read_tsv_by_id(id_lang_path) if (include_lang and id_lang_path.exists()) else {}

    working_ids = sorted(set(info_by_id) & set(metadata_by_id) & set(tags_by_id) & set(genres_by_id))

    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_output_path = output_dir / "ds001_working_candidate_dataset.csv"
    manifest_output_path = output_dir / "ds001_working_candidate_dataset_manifest.json"

    rows_written = 0
    null_spotify_id = 0

    with open_text_write(dataset_output_path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()

        for row_id in working_ids:
            row = build_output_row(
                row_id=row_id,
                info_row=info_by_id[row_id],
                metadata_row=metadata_by_id[row_id],
                tags_row=tags_by_id[row_id],
                genres_row=genres_by_id[row_id],
                lang_row=lang_by_id.get(row_id),
                include_lang=include_lang,
            )
            if not row["spotify_id"]:
                null_spotify_id += 1
            writer.writerow(row)
            rows_written += 1

    dataset_hash = sha256_of_file(dataset_output_path)

    manifest = {
        "task": "DS-001-working-dataset-build",
        "generated_at_utc": utc_now(),
        "inputs": {
            "id_information": str(id_information_path),
            "id_metadata": str(id_metadata_path),
            "id_tags": str(id_tags_path),
            "id_genres": str(id_genres_path),
            "id_lang": str(id_lang_path) if id_lang_path.exists() else None,
        },
        "join_policy": {
            "required_tables": ["id_information", "id_metadata", "id_tags", "id_genres"],
            "optional_tables": ["id_lang"],
            "join_key": "id",
            "join_type": "inner_required_plus_left_optional",
        },
        "stats": {
            "id_information_rows": len(info_by_id),
            "id_metadata_rows": len(metadata_by_id),
            "id_tags_rows": len(tags_by_id),
            "id_genres_rows": len(genres_by_id),
            "id_lang_rows": len(lang_by_id),
            "rows_written": rows_written,
            "null_spotify_id_rows": null_spotify_id,
        },
        "output": {
            "dataset_path": str(dataset_output_path),
            "dataset_sha256": dataset_hash,
            "manifest_path": str(manifest_output_path),
        },
    }

    with open_text_write(manifest_output_path) as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=True)

    print(f"rows_written={rows_written}")
    print(f"null_spotify_id_rows={null_spotify_id}")
    print(f"dataset_sha256={dataset_hash}")
    print(f"dataset_path={dataset_output_path}")
    print(f"manifest_path={manifest_output_path}")


if __name__ == "__main__":
    main()
