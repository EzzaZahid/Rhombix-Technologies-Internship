"""
Logistic Regression baseline.
Always train and compare against this before claiming LightGBM is better.
A model that barely beats logistic regression is not a good model.
"""

import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)


class MusicRecommenderBaseline:

    def __init__(self, config: dict):
        cfg = config["model"]["baseline"]
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(
                max_iter=cfg["max_iter"],
                class_weight=cfg["class_weight"],
                random_state=42,
            )),
        ])
        self.feature_names: List[str] = []

    def train(self, X_train, y_train, X_val=None, y_val=None, feature_names=None):
        self.feature_names = feature_names or list(X_train.columns)
        logger.info(f"Training Logistic Regression baseline on {len(X_train):,} samples...")
        self.pipeline.fit(X_train, y_train)
        logger.info("Baseline training complete.")
        return self

    def predict_proba(self, X) -> np.ndarray:
        return self.pipeline.predict_proba(X)[:, 1]

    def feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        coefs = self.pipeline.named_steps["lr"].coef_[0]
        return (
            pd.DataFrame({"feature": self.feature_names, "importance": np.abs(coefs)})
            .sort_values("importance", ascending=False)
            .head(top_n)
        )

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.pipeline, "feature_names": self.feature_names}, path)
        logger.info(f"Baseline saved to {path}")

    @classmethod
    def load(cls, path: str, config: dict) -> "MusicRecommenderBaseline":
        payload = joblib.load(path)
        instance = cls(config)
        instance.pipeline = payload["model"]
        instance.feature_names = payload["feature_names"]
        return instance
