"""
Data loader — reads raw play events from CSV (synthetic or real Spotify export)
and validates the schema before passing to the feature pipeline.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Minimum required columns for the pipeline to work
REQUIRED_COLUMNS = [
    "user_id",
    "song_id",
    "play_start_time",
    "play_duration_sec",
    "song_duration_sec",
    "label",
]

OPTIONAL_AUDIO_FEATURES = [
    "song_energy", "song_valence", "song_tempo",
    "song_danceability", "song_acousticness",
]


def load_events(path: str) -> pd.DataFrame:
    """
    Load raw play events CSV.
    Works with both synthetic data and real Spotify exports.

    Args:
        path: Path to play_events.csv

    Returns:
        Validated DataFrame ready for feature engineering
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Data file not found: {path}\n"
            "Run: python scripts/train.py --generate-data  to create synthetic data\n"
            "Or:  python scripts/fetch_spotify_data.py    to use real Spotify history"
        )

    logger.info(f"Loading data from {path}")
    df = pd.read_csv(path, parse_dates=["play_start_time"])

    df = _validate_schema(df)
    df = _clean(df)

    logger.info(
        f"Loaded {len(df):,} events | "
        f"{df['user_id'].nunique():,} users | "
        f"{df['song_id'].nunique():,} songs | "
        f"Replay rate: {df['label'].mean():.1%}"
    )
    return df


def _validate_schema(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns: {missing}\n"
            f"Your file has: {list(df.columns)}"
        )

    # Warn (don't crash) if audio features are absent — model degrades gracefully
    missing_audio = [c for c in OPTIONAL_AUDIO_FEATURES if c not in df.columns]
    if missing_audio:
        logger.warning(
            f"Optional audio features missing: {missing_audio}. "
            "Model will skip those features."
        )
    return df


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # Remove rows with null user/song/timestamp
    df = df.dropna(subset=["user_id", "song_id", "play_start_time"])

    # Duration sanity: must be positive and not longer than 2× the full song
    df = df[df["play_duration_sec"] > 0]
    if "song_duration_sec" in df.columns:
        df = df[df["play_duration_sec"] <= df["song_duration_sec"] * 2]

    # Label must be 0 or 1
    df = df[df["label"].isin([0, 1])]
    df["label"] = df["label"].astype(int)

    # Ensure types
    df["play_start_time"] = pd.to_datetime(df["play_start_time"])
    df["user_id"] = df["user_id"].astype(str)
    df["song_id"] = df["song_id"].astype(str)

    # Compute completion_rate if missing
    if "completion_rate" not in df.columns and "song_duration_sec" in df.columns:
        df["completion_rate"] = (
            df["play_duration_sec"] / df["song_duration_sec"]
        ).clip(0, 1).round(3)

    removed = before - len(df)
    if removed > 0:
        logger.warning(f"Removed {removed:,} invalid rows during cleaning.")

    return df.reset_index(drop=True)


def load_sample(config: dict) -> pd.DataFrame:
    """Load a small sample for quick iteration and testing."""
    sample_path = config["data"]["sample_path"]
    if not Path(sample_path).exists():
        logger.info("Sample not found, creating from full dataset...")
        df = load_events(config["data"]["raw_path"])
        sample = df.sample(min(5000, len(df)), random_state=42)
        Path(sample_path).parent.mkdir(parents=True, exist_ok=True)
        sample.to_csv(sample_path, index=False)
        return sample
    return load_events(sample_path)
