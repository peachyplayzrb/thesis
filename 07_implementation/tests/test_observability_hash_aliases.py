from __future__ import annotations

from observability.main import _build_output_hash_aliases


def test_build_output_hash_aliases_preserves_compatibility_and_semantic_aliases() -> None:
    aliases = _build_output_hash_aliases(
        playlist_artifact_sha256="playlist_sha",
        run_config_payload_sha256="run_config_sha",
        scored_candidates_sha256="scored_sha",
        seed_trace_sha256="seed_sha",
    )

    assert aliases["playlist_track_ids_sha256"] == "playlist_sha"
    assert aliases["playlist_artifact_sha256"] == "playlist_sha"
    assert aliases["run_config_payload_sha256"] == "run_config_sha"
    assert aliases["bl006_scored_candidates_sha256"] == "scored_sha"
    assert aliases["scoring_records_sha256"] == "scored_sha"
    assert aliases["bl004_seed_trace_sha256"] == "seed_sha"
    assert aliases["profile_seed_trace_sha256"] == "seed_sha"
