# Spotify API Ingestion Runbook

## Purpose
Collect the maximum practical personal Spotify ingestion dataset for BL-001/BL-002 using the Spotify Web API Authorization Code flow.

## API References Used
- Authorization Code flow: https://developer.spotify.com/documentation/web-api/tutorials/code-flow
- Get User's Top Items: https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks
- Get User's Saved Tracks: https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks
- Get Current User's Playlists: https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists
- Get Playlist Items: https://developer.spotify.com/documentation/web-api/reference/get-playlists-items

## Required Scopes
- user-top-read
- user-library-read
- playlist-read-private
- playlist-read-collaborative
- user-read-private

## Setup
1. In Spotify developer dashboard, confirm redirect URI exactly matches:
   - http://127.0.0.1:8001/spotify/auth/callback
2. Set environment variables in terminal (recommended):

```powershell
$env:SPOTIFY_CLIENT_ID = "<your_client_id>"
$env:SPOTIFY_CLIENT_SECRET = "<your_client_secret>"
$env:SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8001/spotify/auth/callback"
```

## Run Command
```powershell
python 07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py
```

Recommended when PowerShell blocks script sourcing:

```powershell
python 07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py --env-ps1 07_implementation/implementation_notes/ingestion/spotify_env_template.ps1
```

Recommended rate-limit-safe run (smaller batches + explicit throttling):

```powershell
python 07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py --env-ps1 07_implementation/implementation_notes/ingestion/spotify_env_template.ps1 --batch-size-top-tracks 25 --batch-size-saved-tracks 25 --batch-size-playlists 25 --batch-size-playlist-items 25 --batch-pause-ms 500 --min-request-interval-ms 600 --max-requests-per-minute 70 --max-retries 10
```

## First-Run Behavior
- Script opens a browser authorization URL.
- After approval, Spotify redirects to local callback.
- Script exchanges code for access token and saves token cache.

## Output Artifacts
Directory:
- 07_implementation/implementation_notes/ingestion/outputs/spotify_api_export/

Files:
- spotify_profile.json
- spotify_top_tracks_by_range.json
- spotify_top_tracks_flat.csv
- spotify_saved_tracks.json
- spotify_saved_tracks_flat.csv
- spotify_playlists.json
- spotify_playlists_flat.csv
- spotify_playlist_items_flat.jsonl
- spotify_playlist_items_flat.csv
- spotify_request_log.jsonl
- spotify_export_run_summary.json
- spotify_token_cache.json

## Notes
- Keep client secret out of repository files.
- Token cache is sensitive and should stay local only.
- For a fresh OAuth run, pass --force-auth.
- `--env-ps1` reads credentials directly from the template file and avoids `Set-ExecutionPolicy` requirements.
- Batch controls (`--batch-size-*`) are clamped to API limits (1-50) and applied per endpoint.
- Proactive throttling applies before each request via `--min-request-interval-ms` and `--max-requests-per-minute`.
- If Spotify still returns `429`, the script logs `retry_after_seconds` and applies additional backoff before retry.
