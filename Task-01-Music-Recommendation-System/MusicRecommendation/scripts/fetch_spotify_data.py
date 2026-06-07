"""
(Optional) Fetch your real Spotify listening history via the Spotify Web API.

SETUP (one-time):
  1. Go to https://developer.spotify.com/dashboard
  2. Create an app → copy Client ID and Client Secret
  3. Add http://localhost:8080 as a Redirect URI in the app settings
  4. Copy .env.example to .env and fill in your credentials:
       SPOTIFY_CLIENT_ID=your_client_id
       SPOTIFY_CLIENT_SECRET=your_client_secret
       SPOTIFY_REDIRECT_URI=http://localhost:8080

Usage:
    python scripts/fetch_spotify_data.py --output data/raw/play_events.csv

IMPORTANT LIMITATION:
  Spotify's API only provides your 50 most recently played tracks.
  It does NOT expose your full listening history.
  For a larger dataset, you need to:
    - Request your data via: https://www.spotify.com/account/privacy
      (Account → Privacy settings → Download your data)
      This gives you up to 1 year of streaming history as JSON files.
    - Then use --from-export to load those JSON files instead.

Usage with downloaded export:
    python scripts/fetch_spotify_data.py --from-export ~/Downloads/my_spotify_data/
"""

import os
import json
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


def fetch_recent_tracks(output_path: str, limit: int = 50):
    """Fetch up to 50 recent tracks via spotipy."""
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth
    except ImportError:
        print("Install spotipy: pip install spotipy")
        return

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="user-read-recently-played",
    ))

    results = sp.current_user_recently_played(limit=limit)
    rows = []
    for item in results["items"]:
        track = item["track"]
        played_at = datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))
        rows.append({
            "user_id": "spotify_me",
            "song_id": track["id"],
            "song_name": track["name"],
            "artist_id": track["artists"][0]["id"],
            "play_start_time": played_at,
            "song_duration_sec": track["duration_ms"] // 1000,
            "play_duration_sec": track["duration_ms"] // 1000,  # API doesn't give actual play time
            "completion_rate": 1.0,
            "genre": "unknown",
        })

    df = pd.DataFrame(rows)
    # No replay labels possible from 50 tracks alone — mark all as 0, needs manual labeling
    df["label"] = 0
    print(f"WARNING: Spotify API only returns 50 recent tracks. "
          f"All labels set to 0. Use --from-export for real training data.")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} tracks to {output_path}")


def load_from_export(export_dir: str, output_path: str):
    """
    Load listening history from Spotify's 'Download My Data' export.
    The export contains files named StreamingHistory_music_0.json, _1.json, etc.
    """
    export_dir = Path(export_dir)
    json_files = list(export_dir.glob("StreamingHistory_music_*.json"))

    if not json_files:
        print(f"No StreamingHistory_music_*.json files found in {export_dir}")
        print("Request your data at: https://www.spotify.com/account/privacy")
        return

    all_rows = []
    for f in sorted(json_files):
        with open(f) as fp:
            data = json.load(fp)
        all_rows.extend(data)
        print(f"Loaded {len(data):,} events from {f.name}")

    df = pd.DataFrame(all_rows)

    # Rename Spotify's column names to our schema
    df = df.rename(columns={
        "ts":           "play_start_time",
        "master_metadata_track_name": "song_name",
        "master_metadata_album_artist_name": "artist_name",
        "spotify_track_uri": "song_id",
        "ms_played":    "play_duration_ms",
    })

    df["play_start_time"] = pd.to_datetime(df["play_start_time"])
    df["play_duration_sec"] = (df["play_duration_ms"] / 1000).astype(int)
    df["user_id"] = "spotify_me"
    df["artist_id"] = df.get("artist_name", "unknown")
    df["song_duration_sec"] = 210  # Spotify export doesn't include this
    df["completion_rate"] = (df["play_duration_sec"] / df["song_duration_sec"]).clip(0, 1)
    df["genre"] = "unknown"

    # Build replay labels: 1 if user played the same song again within 30 days
    df = df.sort_values("play_start_time").reset_index(drop=True)
    df["label"] = 0

    for song_id, group in df.groupby("song_id"):
        if len(group) < 2:
            continue
        times = group["play_start_time"].tolist()
        first = times[0]
        replayed = any(
            t > first and (t - first).days <= 30
            for t in times[1:]
        )
        if replayed:
            df.loc[group.index[0], "label"] = 1

    df = df.drop_duplicates(subset=["song_id"], keep="first")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\nSaved {len(df):,} unique song events to {output_path}")
    print(f"Replay rate: {df['label'].mean():.1%}")
    print("\nNOTE: For a better model, request at least 3–6 months of history "
          "from Spotify's privacy page.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="data/raw/play_events.csv")
    p.add_argument("--from-export", metavar="DIR",
                   help="Load from Spotify data export directory")
    args = p.parse_args()

    if args.from_export:
        load_from_export(args.from_export, args.output)
    else:
        fetch_recent_tracks(args.output)


if __name__ == "__main__":
    main()
