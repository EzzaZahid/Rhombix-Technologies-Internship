"""
Train/test splitter.
Always splits by TIME — never randomly — to prevent data leakage.
"""

import pandas as pd
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def time_split(
    df: pd.DataFrame,
    test_size: float = 0.20,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data into train and test sets by timestamp.

    WHY NOT RANDOM SPLIT?
    If you split randomly, a user's January events might land in training
    while their December events are in test. The model sees "future" behavior
    during training, giving falsely optimistic metrics. Time-based splitting
    mirrors the real deployment scenario: train on the past, predict the future.

    Args:
        df:        Full DataFrame with a 'play_start_time' column
        test_size: Fraction of the most recent events to use as test set

    Returns:
        (train_df, test_df)
    """
    df = df.sort_values("play_start_time").reset_index(drop=True)

    cutoff_idx = int(len(df) * (1 - test_size))
    cutoff_time = df.iloc[cutoff_idx]["play_start_time"]

    train = df[df["play_start_time"] <= cutoff_time].copy()
    test  = df[df["play_start_time"] >  cutoff_time].copy()

    logger.info(
        f"Train: {len(train):,} events up to {cutoff_time.date()} | "
        f"Test: {len(test):,} events after {cutoff_time.date()}"
    )
    logger.info(
        f"Train replay rate: {train['label'].mean():.1%} | "
        f"Test replay rate:  {test['label'].mean():.1%}"
    )

    # Warn about cold-start users in test
    train_users = set(train["user_id"].unique())
    test_users  = set(test["user_id"].unique())
    cold_start  = test_users - train_users
    if cold_start:
        logger.warning(
            f"{len(cold_start)} users in test set have no training history "
            f"(cold start). Their predictions will rely on song features only."
        )

    return train, test
