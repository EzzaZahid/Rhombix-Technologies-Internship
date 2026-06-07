"""Unit tests for the feature pipeline."""

import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.features.user_features import build_user_features
from src.features.song_features import build_song_features
from src.data.splitter import time_split


def _make_dummy_df(n=200, seed=0):
    rng = np.random.default_rng(seed)
    n_users, n_songs = 10, 20
    dates = pd.date_range("2024-01-01", periods=n, freq="2h")
    return pd.DataFrame({
        "user_id": [f"u_{rng.integers(0, n_users):02d}" for _ in range(n)],
        "song_id": [f"s_{rng.integers(0, n_songs):02d}" for _ in range(n)],
        "artist_id": [f"a_{rng.integers(0, 5):01d}" for _ in range(n)],
        "genre": rng.choice(["pop", "rock", "jazz"], size=n),
        "play_start_time": dates,
        "play_duration_sec": rng.integers(30, 250, size=n),
        "song_duration_sec": np.full(n, 240),
        "completion_rate": rng.uniform(0.1, 1.0, size=n).round(3),
        "label": rng.integers(0, 2, size=n),
    })


def test_user_features_shape():
    df = _make_dummy_df()
    feats = build_user_features(df)
    assert "user_id" in feats.columns
    assert "user_replay_rate" in feats.columns
    assert len(feats) == df["user_id"].nunique()


def test_user_features_no_nan():
    df = _make_dummy_df()
    feats = build_user_features(df)
    numeric = feats.select_dtypes(include="number")
    assert not numeric.isna().any().any(), "User features contain NaN"


def test_song_features_shape():
    df = _make_dummy_df()
    feats = build_song_features(df)
    assert "song_id" in feats.columns
    assert "song_global_replay_rate" in feats.columns
    assert len(feats) == df["song_id"].nunique()


def test_time_split_order():
    df = _make_dummy_df(n=400)
    train, test = time_split(df, test_size=0.2)
    assert train["play_start_time"].max() <= test["play_start_time"].min()


def test_time_split_sizes():
    df = _make_dummy_df(n=100)
    train, test = time_split(df, test_size=0.2)
    assert len(train) + len(test) == len(df)
    assert 15 <= len(test) <= 25  # roughly 20%
