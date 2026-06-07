"""
Feature assembly pipeline.

Takes raw events + precomputed user/song features and produces the
final feature matrix used for training and prediction.

Also computes User x Song interaction features — signals that are
specific to a particular (user, song) pair, not just the user or song alone.
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple, List

from src.features.user_features import build_user_features
from src.features.song_features import build_song_features

logger = logging.getLogger(__name__)


def build_feature_matrix(
    df: pd.DataFrame,
    user_features: pd.DataFrame,
    song_features: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    Assemble the full feature matrix for a dataset split.

    Args:
        df:            Raw events DataFrame (train or test)
        user_features: Precomputed user-level features (from training data only)
        song_features: Precomputed song-level features (from training data only)

    Returns:
        (X, y, feature_names)
    """
    logger.info("Assembling feature matrix...")

    result = df[["user_id", "song_id", "play_start_time", "label"]].copy()

    # --- Temporal features (computed from the event itself, not history) ---
    result["hour_of_day"]  = result["play_start_time"].dt.hour
    result["day_of_week"]  = result["play_start_time"].dt.dayofweek
    result["is_weekend"]   = (result["day_of_week"] >= 5).astype(int)
    result["month"]        = result["play_start_time"].dt.month

    # --- User x Song interaction features ---
    if "completion_rate" in df.columns:
        result["event_completion"] = df["completion_rate"]
    if "play_duration_sec" in df.columns:
        result["play_duration_sec"] = df["play_duration_sec"]

    # How many times has this user played this specific song before?
    # (computed within the split to avoid leakage)
    play_counts = (
        df.groupby(["user_id", "song_id"])
        .cumcount()  # 0-indexed; 0 = first time they've played it
        .rename("times_played_before")
    )
    result = result.join(play_counts)

    # Days since first play of this song by this user
    first_play = df.groupby(["user_id", "song_id"])["play_start_time"].transform("min")
    result["days_since_first_play"] = (
        (df["play_start_time"] - first_play).dt.total_seconds() / 86400
    ).round(1)

    # How many songs by the same artist has this user played?
    if "artist_id" in df.columns:
        artist_plays = (
            df.groupby(["user_id", "artist_id"])
            .cumcount()
            .rename("same_artist_plays_before")
        )
        result = result.join(artist_plays)
    else:
        result["same_artist_plays_before"] = 0

    # How many songs in the same genre has this user played?
    if "genre" in df.columns:
        genre_plays = (
            df.groupby(["user_id", "genre"])
            .cumcount()
            .rename("same_genre_plays_before")
        )
        result = result.join(genre_plays)
    else:
        result["same_genre_plays_before"] = 0

    # --- Merge user features ---
    result = result.merge(user_features, on="user_id", how="left")

    # --- Merge song features ---
    result = result.merge(song_features, on="song_id", how="left")

    # --- Final cleanup ---
    # Drop non-feature columns
    drop_cols = ["user_id", "song_id", "play_start_time", "label"]
    feature_cols = [c for c in result.columns if c not in drop_cols]

    X = result[feature_cols].copy()
    y = result["label"].copy()

    # Fill NaNs for unseen users/songs (cold start → use median)
    X = X.fillna(X.median(numeric_only=True))

    logger.info(
        f"Feature matrix: {X.shape[0]:,} rows x {X.shape[1]} features | "
        f"Positive rate: {y.mean():.1%}"
    )
    return X, y, feature_cols


def run_feature_pipeline(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> Tuple:
    """
    Full feature pipeline entry point.
    User and song statistics are always computed from training data only.
    """
    user_feats = build_user_features(train_df)
    song_feats = build_song_features(train_df)

    X_train, y_train, feature_names = build_feature_matrix(train_df, user_feats, song_feats)
    X_test,  y_test,  _             = build_feature_matrix(test_df,  user_feats, song_feats)

    return X_train, y_train, X_test, y_test, feature_names, user_feats, song_feats
