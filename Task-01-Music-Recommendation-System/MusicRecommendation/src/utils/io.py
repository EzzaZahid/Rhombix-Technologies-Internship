"""Save/load helpers for features and model artifacts."""

import pandas as pd
import joblib
import yaml
from pathlib import Path


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def save_features(df: pd.DataFrame, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def load_features(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)
