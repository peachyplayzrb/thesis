"""
Type contracts for the newingestion stage.

The ingestion base uses immutable domain models so acquisition, normalization,
validation, and serialization can stay cleanly separated.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    return value


@dataclass(frozen=True)
class NewingestionPaths:
    root: Path
    outputs_dir: Path

    @classmethod
    def resolve(cls, root: Path) -> "NewingestionPaths":
        outputs_dir = root / "outputs"
        return cls(root=root, outputs_dir=outputs_dir)


@dataclass(frozen=True)
class NewingestionControls:
    source_type: str = "spotify_api"
    include_top_tracks: bool = True
    include_saved_tracks: bool = True
    include_playlists: bool = True
    include_recently_played: bool = False
    max_top_tracks: int = 0
    max_saved_tracks: int = 0
    max_playlist_items: int = 0
    max_recently_played: int = 0
    cache_ttl_seconds: int = 3600
    throttle_sleep_seconds: float = 0.1
    max_retries: int = 3
    base_backoff_delay_seconds: float = 1.0
    fail_on_missing_scope: bool = False
    fail_on_collection_error: bool = False
    emit_summary_json: bool = True
    emit_flat_csvs: bool = True
    include_raw_response_payloads: bool = False
    enable_interactive_oauth: bool = False
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_redirect_uri: str = "http://127.0.0.1:8888/callback"
    oauth_timeout_seconds: int = 600
    oauth_no_browser: bool = False

    def as_mapping(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type,
            "include_top_tracks": self.include_top_tracks,
            "include_saved_tracks": self.include_saved_tracks,
            "include_playlists": self.include_playlists,
            "include_recently_played": self.include_recently_played,
            "max_top_tracks": self.max_top_tracks,
            "max_saved_tracks": self.max_saved_tracks,
            "max_playlist_items": self.max_playlist_items,
            "max_recently_played": self.max_recently_played,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "throttle_sleep_seconds": self.throttle_sleep_seconds,
            "max_retries": self.max_retries,
            "base_backoff_delay_seconds": self.base_backoff_delay_seconds,
            "fail_on_missing_scope": self.fail_on_missing_scope,
            "fail_on_collection_error": self.fail_on_collection_error,
            "emit_summary_json": self.emit_summary_json,
            "emit_flat_csvs": self.emit_flat_csvs,
            "include_raw_response_payloads": self.include_raw_response_payloads,
            "enable_interactive_oauth": self.enable_interactive_oauth,
            "oauth_client_id": self.oauth_client_id,
            "oauth_client_secret": self.oauth_client_secret,
            "oauth_redirect_uri": self.oauth_redirect_uri,
            "oauth_timeout_seconds": self.oauth_timeout_seconds,
            "oauth_no_browser": self.oauth_no_browser,
        }


@dataclass(frozen=True)
class SpotifyTrack:
    track_id: str
    name: str
    album_id: Optional[str] = None
    duration_ms: Optional[int] = None
    explicit: bool = False
    isrc: Optional[str] = None
    popularity: Optional[int] = None
    is_local: bool = False
    uri: Optional[str] = None
    external_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_value(asdict(self))


@dataclass(frozen=True)
class SpotifyArtist:
    artist_id: str
    name: str
    uri: Optional[str] = None
    external_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_value(asdict(self))


@dataclass(frozen=True)
class SpotifyAlbum:
    album_id: str
    name: str
    album_type: Optional[str] = None
    release_date: Optional[str] = None
    release_date_precision: Optional[str] = None
    total_tracks: Optional[int] = None
    uri: Optional[str] = None
    external_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_value(asdict(self))


@dataclass(frozen=True)
class SpotifyPlaylist:
    playlist_id: str
    name: str
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    description: Optional[str] = None
    snapshot_id: Optional[str] = None
    collaborative: bool = False
    public: Optional[bool] = None
    tracks_total: Optional[int] = None
    uri: Optional[str] = None
    external_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_value(asdict(self))


@dataclass(frozen=True)
class SpotifyAccountProfile:
    user_id: str
    country: Optional[str] = None
    product: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    uri: Optional[str] = None
    external_url: Optional[str] = None
    followers_total: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_value(asdict(self))


@dataclass(frozen=True)
class TrackArtistRelation:
    track_id: str
    artist_id: str
    artist_order: int

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_value(asdict(self))


@dataclass(frozen=True)
class TopTrackMembership:
    track_id: str
    time_range: str
    rank: int

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_value(asdict(self))


@dataclass(frozen=True)
class SavedTrackMembership:
    track_id: str
    added_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_value(asdict(self))


@dataclass(frozen=True)
class PlaylistTrackMembership:
    playlist_id: str
    track_id: str
    position: int
    added_at: Optional[datetime] = None
    added_by_id: Optional[str] = None
    added_by_uri: Optional[str] = None
    is_local: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_value(asdict(self))


@dataclass(frozen=True)
class RecentlyPlayedEvent:
    track_id: str
    played_at: Optional[datetime] = None
    context_type: Optional[str] = None
    context_uri: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_value(asdict(self))


@dataclass(frozen=True)
class IngestionDomainBundle:
    run_id: str
    generated_at_utc: datetime
    source_type: str
    account_profile: Optional[SpotifyAccountProfile] = None
    tracks: List[SpotifyTrack] = field(default_factory=list)
    artists: List[SpotifyArtist] = field(default_factory=list)
    albums: List[SpotifyAlbum] = field(default_factory=list)
    playlists: List[SpotifyPlaylist] = field(default_factory=list)
    track_artist_relations: List[TrackArtistRelation] = field(default_factory=list)
    top_track_memberships: List[TopTrackMembership] = field(default_factory=list)
    saved_track_memberships: List[SavedTrackMembership] = field(default_factory=list)
    playlist_track_memberships: List[PlaylistTrackMembership] = field(default_factory=list)
    recently_played_events: List[RecentlyPlayedEvent] = field(default_factory=list)
    selection_flags: Dict[str, bool] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    duplicate_track_locations: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    @property
    def user_id(self) -> Optional[str]:
        return self.account_profile.user_id if self.account_profile else None

    @property
    def account_country(self) -> Optional[str]:
        return self.account_profile.country if self.account_profile else None

    @property
    def account_product(self) -> Optional[str]:
        return self.account_profile.product if self.account_profile else None

    def counts(self) -> Dict[str, int]:
        top_short = sum(1 for item in self.top_track_memberships if item.time_range == "short_term")
        top_medium = sum(1 for item in self.top_track_memberships if item.time_range == "medium_term")
        top_long = sum(1 for item in self.top_track_memberships if item.time_range == "long_term")
        unique_membership_track_ids = {
            item.track_id for item in self.top_track_memberships
        } | {
            item.track_id for item in self.saved_track_memberships
        } | {
            item.track_id for item in self.playlist_track_memberships
        } | {
            item.track_id for item in self.recently_played_events
        }
        return {
            "top_tracks_short": top_short,
            "top_tracks_medium": top_medium,
            "top_tracks_long": top_long,
            "saved_tracks": len(self.saved_track_memberships),
            "playlist_items": len(self.playlist_track_memberships),
            "recently_played": len(self.recently_played_events),
            "total_unique_tracks": len(unique_membership_track_ids),
            "track_entities": len(self.tracks),
            "artist_entities": len(self.artists),
            "album_entities": len(self.albums),
            "playlist_entities": len(self.playlists),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "generated_at_utc": self.generated_at_utc.isoformat(),
            "source_type": self.source_type,
            "account_profile": self.account_profile.to_dict() if self.account_profile else None,
            "tracks": [item.to_dict() for item in self.tracks],
            "artists": [item.to_dict() for item in self.artists],
            "albums": [item.to_dict() for item in self.albums],
            "playlists": [item.to_dict() for item in self.playlists],
            "track_artist_relations": [item.to_dict() for item in self.track_artist_relations],
            "top_track_memberships": [item.to_dict() for item in self.top_track_memberships],
            "saved_track_memberships": [item.to_dict() for item in self.saved_track_memberships],
            "playlist_track_memberships": [item.to_dict() for item in self.playlist_track_memberships],
            "recently_played_events": [item.to_dict() for item in self.recently_played_events],
            "selection_flags": dict(self.selection_flags),
            "warnings": list(self.warnings),
            "duplicate_track_locations": _serialize_value(self.duplicate_track_locations),
        }


@dataclass(frozen=True)
class NewingestionArtifacts:
    run_id: str
    generated_at_utc: datetime
    source_type: str
    manifest_artifact_path: Path
    artifact_paths: Dict[str, Path] = field(default_factory=dict)
    compatibility_export_paths: Dict[str, Path] = field(default_factory=dict)
    counts: Dict[str, int] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    artifact_hashes: Dict[str, str] = field(default_factory=dict)

    @property
    def summary_artifact_path(self) -> Path:
        return self.manifest_artifact_path

    @property
    def duplicate_track_locations_path(self) -> Optional[Path]:
        return self.artifact_paths.get("duplicate_track_locations")


DEFAULT_NEWINGESTION_CONTROLS = NewingestionControls()
