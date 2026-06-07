"""
Song-level features.
Combines global popularity/engagement stats with audio features.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

AUDIO_COLS = [
    "song_energy", "song_valence", "song_tempo",
    "song_danceability", "song_acousticness", "song_loudness",
    "song_speechiness",
]


def build_song_features(train_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-song features from training data.
    Audio features (if present) are passed through directly.
    """
    logger.info("Building song features...")

    g = train_df.groupby("song_id")

    features = pd.DataFrame({
        "song_total_plays":       g["user_id"].count(),
        "song_unique_listeners":  g["user_id"].nunique(),
        "song_global_replay_rate": g["label"].mean(),
    }).reset_index()

    # Average completion rate per song
    if "completion_rate" in train_df.columns:
        avg_comp = g["completion_rate"].mean().reset_index()
        avg_comp.columns = ["song_id", "song_avg_completion"]
        features = features.merge(avg_comp, on="song_id", how="left")
    else:
        features["song_avg_completion"] = 0.5

    # Popularity tier (log-scaled because song play counts follow a power law)
    features["song_log_plays"] = np.log1p(features["song_total_plays"])

    # Merge audio features if they exist in the data
    present_audio = [c for c in AUDIO_COLS if c in train_df.columns]
    if present_audio:
        audio = train_df.groupby("song_id")[present_audio].first().reset_index()
        features = features.merge(audio, on="song_id", how="left")
        logger.info(f"Included audio features: {present_audio}")
    else:
        logger.warning("No audio features found. Content-based signals unavailable.")

    numeric_cols = features.select_dtypes(include="number").columns
    features[numeric_cols] = features[numeric_cols].fillna(features[numeric_cols].median())

    logger.info(f"Built song features for {len(features):,} songs.")
    return features
