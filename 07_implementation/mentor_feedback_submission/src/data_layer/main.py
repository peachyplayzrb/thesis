"""BL-002 data layer entry point for the embedded DS-001 candidate dataset.

This stage just checks that the bundled dataset is present and, when a manifest
is available, that the file hash still matches what the bundle expects.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from shared_utils.io_utils import sha256_of_file


def _mapping(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def count_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for _ in reader)


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "outputs"
    dataset_output_path = output_dir / "ds001_working_candidate_dataset.csv"
    manifest_output_path = output_dir / "ds001_working_candidate_dataset_manifest.json"

    # I check the embedded dataset up front so downstream stages fail early with
    # a clear cause instead of breaking later for harder-to-read reasons.
    if not dataset_output_path.is_file():
        raise FileNotFoundError(f"Embedded candidate dataset not found: {dataset_output_path}")

    dataset_hash = sha256_of_file(dataset_output_path)
    rows_written = count_rows(dataset_output_path)

    manifest_payload: dict[str, object] | None = None
    manifest_hash_matches = None
    if manifest_output_path.is_file():
        # The bundle can still run without the manifest; when it exists, I use it
        # as a quick integrity check against accidental file drift.
        with manifest_output_path.open("r", encoding="utf-8") as handle:
            manifest_payload = json.load(handle)
        expected_hash = _mapping(_mapping(manifest_payload).get("output")).get("dataset_sha256")
        if isinstance(expected_hash, str) and expected_hash.strip():
            manifest_hash_matches = expected_hash.strip().upper() == dataset_hash

    print("task=DS-001-embedded-candidate-dataset")
    print(f"rows_written={rows_written}")
    print(f"dataset_sha256={dataset_hash}")
    print(f"dataset_path={dataset_output_path}")
    print(f"manifest_path={manifest_output_path if manifest_output_path.is_file() else 'missing'}")
    if manifest_hash_matches is not None:
        print(f"manifest_hash_matches={str(manifest_hash_matches).lower()}")


if __name__ == "__main__":
    main()
