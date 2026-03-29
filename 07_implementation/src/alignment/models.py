"""Typed data models used internally by BL-003 alignment stages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SourceEvent:
    source_type: str
    source_row_index: str
    spotify_track_id: str
    isrc: str
    track_name: str
    artist_names: str
    duration_ms: str
    event_time: str
    time_range: str
    rank: str
    playlist_id: str
    playlist_name: str
    playlist_position: str

    @classmethod
    def from_raw_row(cls, source_type: str, row_index: int, row: dict[str, str]) -> SourceEvent:
        event_time = ""
        if source_type in {"saved_tracks", "playlist_items"}:
            event_time = (row.get("added_at") or "").strip()
        elif source_type == "recently_played":
            event_time = (row.get("played_at") or "").strip()

        return cls(
            source_type=source_type,
            source_row_index=str(row_index),
            spotify_track_id=(row.get("track_id") or "").strip(),
            isrc=(row.get("isrc") or "").strip(),
            track_name=(row.get("track_name") or "").strip(),
            artist_names=(row.get("artist_names") or "").strip(),
            duration_ms=(row.get("duration_ms") or "").strip(),
            event_time=event_time,
            time_range=(row.get("time_range") or "").strip(),
            rank=(row.get("rank") or "").strip(),
            playlist_id=(row.get("playlist_id") or "").strip(),
            playlist_name=(row.get("playlist_name") or "").strip(),
            playlist_position=(row.get("playlist_position") or "").strip(),
        )

    @classmethod
    def from_dict(cls, payload: dict[str, str]) -> SourceEvent:
        return cls(
            source_type=str(payload.get("source_type", "")),
            source_row_index=str(payload.get("source_row_index", "")),
            spotify_track_id=str(payload.get("spotify_track_id", "")),
            isrc=str(payload.get("isrc", "")),
            track_name=str(payload.get("track_name", "")),
            artist_names=str(payload.get("artist_names", "")),
            duration_ms=str(payload.get("duration_ms", "")),
            event_time=str(payload.get("event_time", "")),
            time_range=str(payload.get("time_range", "")),
            rank=str(payload.get("rank", "")),
            playlist_id=str(payload.get("playlist_id", "")),
            playlist_name=str(payload.get("playlist_name", "")),
            playlist_position=str(payload.get("playlist_position", "")),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "source_type": self.source_type,
            "source_row_index": self.source_row_index,
            "spotify_track_id": self.spotify_track_id,
            "isrc": self.isrc,
            "track_name": self.track_name,
            "artist_names": self.artist_names,
            "duration_ms": self.duration_ms,
            "event_time": self.event_time,
            "time_range": self.time_range,
            "rank": self.rank,
            "playlist_id": self.playlist_id,
            "playlist_name": self.playlist_name,
            "playlist_position": self.playlist_position,
        }


@dataclass(slots=True)
class MatchTrace:
    source_type: str
    source_row_index: str
    spotify_track_id: str
    isrc: str
    track_name: str
    artist_names: str
    duration_ms: str
    event_time: str
    time_range: str
    rank: str
    playlist_id: str
    playlist_name: str
    playlist_position: str
    match_status: str = ""
    match_method: str = ""
    matched_ds001_id: str = ""
    matched_song: str = ""
    matched_artist: str = ""
    duration_delta_ms: str = ""
    fuzzy_title_score: str = ""
    fuzzy_artist_score: str = ""
    fuzzy_combined_score: str = ""
    reason: str = ""
    preference_weight: str = ""

    @classmethod
    def from_event(cls, event: SourceEvent, preference_weight: float) -> MatchTrace:
        return cls(
            source_type=event.source_type,
            source_row_index=event.source_row_index,
            spotify_track_id=event.spotify_track_id,
            isrc=event.isrc,
            track_name=event.track_name,
            artist_names=event.artist_names,
            duration_ms=event.duration_ms,
            event_time=event.event_time,
            time_range=event.time_range,
            rank=event.rank,
            playlist_id=event.playlist_id,
            playlist_name=event.playlist_name,
            playlist_position=event.playlist_position,
            preference_weight=f"{preference_weight:.6f}",
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "source_type": self.source_type,
            "source_row_index": self.source_row_index,
            "spotify_track_id": self.spotify_track_id,
            "isrc": self.isrc,
            "track_name": self.track_name,
            "artist_names": self.artist_names,
            "duration_ms": self.duration_ms,
            "event_time": self.event_time,
            "time_range": self.time_range,
            "rank": self.rank,
            "playlist_id": self.playlist_id,
            "playlist_name": self.playlist_name,
            "playlist_position": self.playlist_position,
            "match_status": self.match_status,
            "match_method": self.match_method,
            "matched_ds001_id": self.matched_ds001_id,
            "matched_song": self.matched_song,
            "matched_artist": self.matched_artist,
            "duration_delta_ms": self.duration_delta_ms,
            "fuzzy_title_score": self.fuzzy_title_score,
            "fuzzy_artist_score": self.fuzzy_artist_score,
            "fuzzy_combined_score": self.fuzzy_combined_score,
            "reason": self.reason,
            "preference_weight": self.preference_weight,
        }


@dataclass(slots=True)
class MatchedEvent:
    event_id: str
    source_type: str
    source_row_index: int
    source_timestamp: str
    spotify_track_id: str
    spotify_isrc: str
    spotify_track_name: str
    spotify_artist_names: str
    match_method: str
    duration_delta_ms: int | None
    fuzzy_title_score: float | None
    fuzzy_artist_score: float | None
    fuzzy_combined_score: float | None
    ds001_id: str
    ds001_spotify_id: str
    artist: str
    song: str
    release: str
    duration_ms: str
    popularity: str
    danceability: str
    energy: str
    key: str
    mode: str
    valence: str
    tempo: str
    genres: str
    tags: str
    lang: str
    preference_weight: float
    interaction_count: int
    interaction_type: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> MatchedEvent:
        def _as_int(raw: Any, default: int) -> int:
            try:
                return int(raw)
            except (TypeError, ValueError):
                return default

        def _as_float(raw: Any, default: float | None = None) -> float | None:
            if raw is None:
                return default
            try:
                return float(raw)
            except (TypeError, ValueError):
                return default

        return cls(
            event_id=str(payload.get("event_id", "")),
            source_type=str(payload.get("source_type", "")),
            source_row_index=_as_int(payload.get("source_row_index"), 0),
            source_timestamp=str(payload.get("source_timestamp", "")),
            spotify_track_id=str(payload.get("spotify_track_id", "")),
            spotify_isrc=str(payload.get("spotify_isrc", "")),
            spotify_track_name=str(payload.get("spotify_track_name", "")),
            spotify_artist_names=str(payload.get("spotify_artist_names", "")),
            match_method=str(payload.get("match_method", "")),
            duration_delta_ms=_as_int(payload.get("duration_delta_ms"), 0)
            if payload.get("duration_delta_ms") is not None
            else None,
            fuzzy_title_score=_as_float(payload.get("fuzzy_title_score"), None),
            fuzzy_artist_score=_as_float(payload.get("fuzzy_artist_score"), None),
            fuzzy_combined_score=_as_float(payload.get("fuzzy_combined_score"), None),
            ds001_id=str(payload.get("ds001_id", "")),
            ds001_spotify_id=str(payload.get("ds001_spotify_id", "")),
            artist=str(payload.get("artist", "")),
            song=str(payload.get("song", "")),
            release=str(payload.get("release", "")),
            duration_ms=str(payload.get("duration_ms", "")),
            popularity=str(payload.get("popularity", "")),
            danceability=str(payload.get("danceability", "")),
            energy=str(payload.get("energy", "")),
            key=str(payload.get("key", "")),
            mode=str(payload.get("mode", "")),
            valence=str(payload.get("valence", "")),
            tempo=str(payload.get("tempo", "")),
            genres=str(payload.get("genres", "")),
            tags=str(payload.get("tags", "")),
            lang=str(payload.get("lang", "")),
            preference_weight=float(payload.get("preference_weight", 0.0)),
            interaction_count=_as_int(payload.get("interaction_count"), 0),
            interaction_type=str(payload.get("interaction_type", "history")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "source_type": self.source_type,
            "source_row_index": self.source_row_index,
            "source_timestamp": self.source_timestamp,
            "spotify_track_id": self.spotify_track_id,
            "spotify_isrc": self.spotify_isrc,
            "spotify_track_name": self.spotify_track_name,
            "spotify_artist_names": self.spotify_artist_names,
            "match_method": self.match_method,
            "duration_delta_ms": self.duration_delta_ms,
            "fuzzy_title_score": self.fuzzy_title_score,
            "fuzzy_artist_score": self.fuzzy_artist_score,
            "fuzzy_combined_score": self.fuzzy_combined_score,
            "ds001_id": self.ds001_id,
            "ds001_spotify_id": self.ds001_spotify_id,
            "artist": self.artist,
            "song": self.song,
            "release": self.release,
            "duration_ms": self.duration_ms,
            "popularity": self.popularity,
            "danceability": self.danceability,
            "energy": self.energy,
            "key": self.key,
            "mode": self.mode,
            "valence": self.valence,
            "tempo": self.tempo,
            "genres": self.genres,
            "tags": self.tags,
            "lang": self.lang,
            "preference_weight": self.preference_weight,
            "interaction_count": self.interaction_count,
            "interaction_type": self.interaction_type,
        }


@dataclass(slots=True)
class AggregatedEvent:
    ds001_id: str
    spotify_id: str
    song: str
    artist: str
    release: str
    duration_ms: str
    popularity: str
    danceability: str
    energy: str
    key: str
    mode: str
    valence: str
    tempo: str
    genres: str
    tags: str
    lang: str
    matched_event_count: int = 0
    interaction_count_sum: int = 0
    preference_weight_sum: float = 0.0
    preference_weight_max: float = 0.0
    source_types: set[str] = field(default_factory=set)
    interaction_types: set[str] = field(default_factory=set)
    spotify_track_ids: set[str] = field(default_factory=set)

    @classmethod
    def from_matched_event(cls, event: MatchedEvent) -> AggregatedEvent:
        return cls(
            ds001_id=event.ds001_id,
            spotify_id=event.ds001_spotify_id,
            song=event.song,
            artist=event.artist,
            release=event.release,
            duration_ms=event.duration_ms,
            popularity=event.popularity,
            danceability=event.danceability,
            energy=event.energy,
            key=event.key,
            mode=event.mode,
            valence=event.valence,
            tempo=event.tempo,
            genres=event.genres,
            tags=event.tags,
            lang=event.lang,
        )

    def apply_event(self, event: MatchedEvent) -> None:
        self.matched_event_count += 1
        self.interaction_count_sum += int(event.interaction_count)
        self.preference_weight_sum += float(event.preference_weight)
        self.preference_weight_max = max(self.preference_weight_max, float(event.preference_weight))
        self.source_types.add(event.source_type)
        if event.spotify_track_id:
            self.spotify_track_ids.add(event.spotify_track_id)
        for interaction_type in str(event.interaction_type or "history").split(","):
            token = interaction_type.strip()
            if token:
                self.interaction_types.add(token)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ds001_id": self.ds001_id,
            "spotify_id": self.spotify_id,
            "song": self.song,
            "artist": self.artist,
            "release": self.release,
            "duration_ms": self.duration_ms,
            "popularity": self.popularity,
            "danceability": self.danceability,
            "energy": self.energy,
            "key": self.key,
            "mode": self.mode,
            "valence": self.valence,
            "tempo": self.tempo,
            "genres": self.genres,
            "tags": self.tags,
            "lang": self.lang,
            "matched_event_count": self.matched_event_count,
            "interaction_count_sum": self.interaction_count_sum,
            "preference_weight_sum": self.preference_weight_sum,
            "preference_weight_max": self.preference_weight_max,
            "source_types": self.source_types,
            "interaction_types": self.interaction_types,
            "spotify_track_ids": self.spotify_track_ids,
        }