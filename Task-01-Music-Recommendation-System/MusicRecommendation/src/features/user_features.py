"""
User-level features.
All features are computed from TRAINING data only, then joined onto both
train and test to prevent leakage.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def build_user_features(train_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute aggregated per-user features from the training set.

    Returns a DataFrame indexed by user_id with one row per user.
    These features describe WHO the user is as a listener.
    """
    logger.info("Building user features...")

    g = train_df.groupby("user_id")

    features = pd.DataFrame({
        # --- Volume signals ---
        "user_total_plays":      g["song_id"].count(),
        "user_unique_songs":     g["song_id"].nunique(),
        "user_unique_artists":   g["artist_id"].nunique() if "artist_id" in train_df.columns
                                 else g["song_id"].nunique(),

        # --- Engagement quality ---
        "user_replay_rate":      g["label"].mean(),
        "user_avg_completion":   g["completion_rate"].mean()
                                 if "completion_rate" in train_df.columns
                                 else pd.Series(dtype=float),

        # --- Skip behavior ---
        # Skip = completion < 30% of the song
        "user_skip_rate": (
            (train_df["completion_rate"] < 0.30)
            .groupby(train_df["user_id"]).mean()
        ) if "completion_rate" in train_df.columns else pd.Series(dtype=float),

        # --- Temporal activity ---
        "user_active_days": g["play_start_time"].apply(
            lambda x: x.dt.date.nunique()
        ),
    }).reset_index()

    # Derived: average plays per active day
    features["user_avg_daily_plays"] = (
        features["user_total_plays"] / features["user_active_days"].clip(lower=1)
    ).round(2)

    # Genre diversity: entropy of genre distribution
    if "genre" in train_df.columns:
        def genre_entropy(genres):
            counts = genres.value_counts(normalize=True)
            return float(-np.sum(counts * np.log2(counts + 1e-9)))

        genre_div = train_df.groupby("user_id")["genre"].apply(genre_entropy).reset_index()
        genre_div.columns = ["user_id", "user_genre_diversity"]
        features = features.merge(genre_div, on="user_id", how="left")
    else:
        features["user_genre_diversity"] = 0.0

    # Fill any NaNs (users with very few events)
    numeric_cols = features.select_dtypes(include="number").columns
    features[numeric_cols] = features[numeric_cols].fillna(0)

    logger.info(f"Built user features for {len(features):,} users.")
    return features
