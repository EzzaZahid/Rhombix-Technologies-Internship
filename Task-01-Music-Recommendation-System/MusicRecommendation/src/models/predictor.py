"""
Predictor — loads a trained model and generates top-K recommendations for a user.
"""

import pandas as pd
import numpy as np
import logging
from typing import List

logger = logging.getLogger(__name__)


class RecommendationPredictor:
    """
    Given a trained model + precomputed feature stores, generates
    ranked song recommendations for any user.
    """

    def __init__(self, model, user_features: pd.DataFrame, song_features: pd.DataFrame, config: dict):
        self.model = model
        self.user_features = user_features
        self.song_features = song_features
        self.config = config

    def recommend(self, user_id: str, top_k: int = 10) -> pd.DataFrame:
        """
        Return the top-K songs most likely to be replayed by this user.

        For known users: uses their full behavioral feature profile.
        For cold-start users: falls back to globally popular songs.
        """
        known_users = set(self.user_features["user_id"].tolist())

        if user_id not in known_users:
            logger.warning(
                f"User '{user_id}' has no history (cold start). "
                f"Falling back to global popularity ranking."
            )
            return self._cold_start_recommendations(top_k)

        # Build candidate feature rows for this user × all songs
        user_row = self.user_features[self.user_features["user_id"] == user_id]
        candidates = self.song_features.copy()

        # Cross join user features onto every song
        user_row_broadcast = pd.concat(
            [user_row] * len(candidates), ignore_index=True
        )
        candidate_matrix = pd.concat(
            [candidates.reset_index(drop=True),
             user_row_broadcast.drop(columns=["user_id"]).reset_index(drop=True)],
            axis=1,
        )

        # Add default temporal features
        candidate_matrix["hour_of_day"] = 12
        candidate_matrix["day_of_week"] = 2
        candidate_matrix["is_weekend"] = 0
        candidate_matrix["month"] = 6
        candidate_matrix["times_played_before"] = 0
        candidate_matrix["days_since_first_play"] = 0
        candidate_matrix["same_artist_plays_before"] = 0
        candidate_matrix["same_genre_plays_before"] = 0
        candidate_matrix["event_completion"] = 0.85
        candidate_matrix["play_duration_sec"] = 210

        # Align feature columns to what the model was trained on
        feature_cols = self.model.feature_names
        for col in feature_cols:
            if col not in candidate_matrix.columns:
                candidate_matrix[col] = 0
        X = candidate_matrix[feature_cols].fillna(0)

        scores = self.model.predict_proba(X)
        candidates = candidates.copy()
        candidates["replay_probability"] = scores
        candidates = candidates.sort_values("replay_probability", ascending=False)

        return candidates[["song_id", "replay_probability",
                            "song_global_replay_rate", "song_total_plays"]].head(top_k)

    def _cold_start_recommendations(self, top_k: int) -> pd.DataFrame:
        """For new users: recommend the most globally-replayed songs."""
        return (
            self.song_features
            .sort_values("song_global_replay_rate", ascending=False)
            .head(top_k)[["song_id", "song_global_replay_rate", "song_total_plays"]]
        )
