from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def count_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for _ in reader)


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "outputs"
    dataset_output_path = output_dir / "ds001_working_candidate_dataset.csv"
    manifest_output_path = output_dir / "ds001_working_candidate_dataset_manifest.json"

    if not dataset_output_path.is_file():
        raise FileNotFoundError(f"Embedded candidate dataset not found: {dataset_output_path}")

    dataset_hash = sha256_of_file(dataset_output_path)
    rows_written = count_rows(dataset_output_path)

    manifest_payload: dict[str, object] | None = None
    manifest_hash_matches = None
    if manifest_output_path.is_file():
        with manifest_output_path.open("r", encoding="utf-8") as handle:
            manifest_payload = json.load(handle)
        expected_hash = (
            (manifest_payload.get("output") or {}).get("dataset_sha256")
            if isinstance(manifest_payload, dict)
            else None
        )
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
