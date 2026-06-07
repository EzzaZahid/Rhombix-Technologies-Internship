"""
Synthetic dataset generator.
Produces realistic listening history without needing Spotify credentials.
Saves to data/raw/play_events.csv in the same schema as real Spotify data.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

GENRES = ["pop", "rock", "hip_hop", "electronic", "jazz", "classical",
          "r_and_b", "country", "indie", "metal"]

PERSONA_TEMPLATES = {
    "casual_listener":   {"plays_per_day": (1, 5),  "replay_prob": 0.10, "skip_prob": 0.35},
    "moderate_listener": {"plays_per_day": (5, 15), "replay_prob": 0.20, "skip_prob": 0.25},
    "power_listener":    {"plays_per_day": (15, 40),"replay_prob": 0.30, "skip_prob": 0.15},
}


def generate_songs(n_songs: int, seed: int = 42) -> pd.DataFrame:
    """Generate a catalog of synthetic songs with audio features."""
    rng = np.random.default_rng(seed)

    songs = pd.DataFrame({
        "song_id": [f"s_{i:05d}" for i in range(n_songs)],
        "artist_id": [f"a_{rng.integers(0, n_songs // 4):04d}" for _ in range(n_songs)],
        "genre": rng.choice(GENRES, size=n_songs),
        "duration_sec": rng.integers(120, 360, size=n_songs),
        # Spotify-style audio features (all 0–1 except tempo and loudness)
        "song_energy":       rng.uniform(0.1, 1.0, size=n_songs).round(3),
        "song_valence":      rng.uniform(0.0, 1.0, size=n_songs).round(3),
        "song_tempo":        rng.uniform(60, 200, size=n_songs).round(1),
        "song_danceability": rng.uniform(0.1, 1.0, size=n_songs).round(3),
        "song_acousticness": rng.uniform(0.0, 1.0, size=n_songs).round(3),
        "song_loudness":     rng.uniform(-20, 0, size=n_songs).round(2),
        "song_speechiness":  rng.uniform(0.0, 0.5, size=n_songs).round(3),
        # Popularity (power-law: most songs are niche, few are mega-popular)
        "popularity": (rng.power(0.3, size=n_songs) * 100).astype(int),
    })
    return songs


def generate_users(n_users: int, seed: int = 42) -> pd.DataFrame:
    """Generate user profiles with listening personas."""
    rng = np.random.default_rng(seed)
    persona_names = list(PERSONA_TEMPLATES.keys())
    personas = rng.choice(persona_names, size=n_users,
                          p=[0.50, 0.35, 0.15])  # Realistic distribution

    users = pd.DataFrame({
        "user_id": [f"u_{i:04d}" for i in range(n_users)],
        "persona": personas,
        # Each user has 1–3 preferred genres
        "preferred_genres": [
            list(rng.choice(GENRES, size=rng.integers(1, 4), replace=False))
            for _ in range(n_users)
        ],
    })
    return users


def generate_play_events(
    users: pd.DataFrame,
    songs: pd.DataFrame,
    n_events: int,
    replay_window_days: int = 30,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate play events with realistic replay labels.

    Label = 1 if the user plays the same song again within `replay_window_days`.
    """
    rng = np.random.default_rng(seed)
    random.seed(seed)

    song_dict = songs.set_index("song_id").to_dict("index")
    events = []
    start_date = datetime(2024, 1, 1)

    logger.info(f"Generating {n_events:,} play events...")

    for user_row in users.itertuples():
        persona = PERSONA_TEMPLATES[user_row.persona]
        plays_per_day = rng.integers(*persona["plays_per_day"])
        total_days = int(n_events / (len(users) * plays_per_day)) + 1
        total_days = max(total_days, 60)

        # Song pool: mix of preferred-genre and random songs
        preferred = songs[songs["genre"].isin(user_row.preferred_genres)]
        preferred_ids = preferred["song_id"].tolist()
        all_ids = songs["song_id"].tolist()

        user_play_log: dict[str, list[datetime]] = {}  # song_id → list of play datetimes

        for day_offset in range(total_days):
            day_plays = rng.integers(max(1, plays_per_day - 3), plays_per_day + 3)
            for _ in range(int(day_plays)):
                # 70% chance of picking from preferred genre
                if rng.random() < 0.70 and preferred_ids:
                    song_id = rng.choice(preferred_ids)
                else:
                    song_id = rng.choice(all_ids)

                ts = start_date + timedelta(
                    days=day_offset,
                    hours=int(rng.integers(6, 23)),
                    minutes=int(rng.integers(0, 59)),
                )

                # Completion rate: higher if genre matches preferences
                genre_match = song_dict[song_id]["genre"] in user_row.preferred_genres
                skip_adj = -0.15 if genre_match else 0.10
                skip_prob = persona["skip_prob"] + skip_adj
                completion = rng.uniform(0.05, 0.20) if rng.random() < skip_prob \
                             else rng.uniform(0.70, 1.0)
                play_duration = int(song_dict[song_id]["duration_sec"] * completion)

                if song_id not in user_play_log:
                    user_play_log[song_id] = []
                user_play_log[song_id].append(ts)

                events.append({
                    "user_id": user_row.user_id,
                    "song_id": song_id,
                    "play_start_time": ts,
                    "play_duration_sec": play_duration,
                    "song_duration_sec": song_dict[song_id]["duration_sec"],
                    "completion_rate": round(completion, 3),
                    "genre": song_dict[song_id]["genre"],
                    "artist_id": song_dict[song_id]["artist_id"],
                })

    df = pd.DataFrame(events)

    # --- Build labels ---
    # Sort by user and time, then check if replayed within window
    df = df.sort_values(["user_id", "song_id", "play_start_time"]).reset_index(drop=True)

    # For each (user, song) pair, find first play time
    first_play = (
        df.groupby(["user_id", "song_id"])["play_start_time"]
        .min()
        .reset_index()
        .rename(columns={"play_start_time": "first_play_time"})
    )
    df = df.merge(first_play, on=["user_id", "song_id"])

    # Label = 1 if there's a play more than 1 second after first play AND within window
    def has_replay(group):
        first = group["first_play_time"].iloc[0]
        window_end = first + timedelta(days=replay_window_days)
        replays = group[
            (group["play_start_time"] > first + timedelta(seconds=1))
            & (group["play_start_time"] <= window_end)
        ]
        return int(len(replays) > 0)

    labels = (
        df.groupby(["user_id", "song_id"])
        .apply(has_replay)
        .reset_index()
        .rename(columns={0: "label"})
    )

    # Keep only the first play per user-song (the event we're predicting for)
    df_first = df.drop_duplicates(subset=["user_id", "song_id"], keep="first").copy()
    df_first = df_first.merge(labels, on=["user_id", "song_id"])

    logger.info(
        f"Generated {len(df_first):,} unique user-song events. "
        f"Replay rate: {df_first['label'].mean():.1%}"
    )
    return df_first.drop(columns=["first_play_time"])


def run(config: dict, output_path: str = "data/raw/play_events.csv"):
    """Generate and save a full synthetic dataset."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    songs = generate_songs(config["data"]["n_synthetic_songs"])
    users = generate_users(config["data"]["n_synthetic_users"])
    events = generate_play_events(
        users, songs,
        n_events=config["data"]["n_synthetic_events"],
        replay_window_days=config["data"]["replay_window_days"],
    )

    # Merge audio features into events
    song_features = songs.drop(columns=["artist_id", "genre", "popularity"])
    events = events.merge(song_features, on="song_id", how="left")

    events.to_csv(output_path, index=False)
    songs.to_csv("data/raw/songs_catalog.csv", index=False)
    users.to_csv("data/raw/users.csv", index=False)

    logger.info(f"Saved {len(events):,} events to {output_path}")
    return events
