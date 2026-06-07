"""
LightGBM model — the primary recommendation model.
Handles training, early stopping, feature importance, and serialization.
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
import joblib
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class MusicRecommenderLGBM:
    """
    LightGBM binary classifier that predicts replay probability.
    Output score is a probability in [0, 1] — higher = more likely to replay.
    """

    def __init__(self, config: dict):
        cfg = config["model"]["lgbm"]
        self.params = {
            "objective":          "binary",
            "metric":             ["auc", "binary_logloss"],
            "n_estimators":       cfg["n_estimators"],
            "learning_rate":      cfg["learning_rate"],
            "num_leaves":         cfg["num_leaves"],
            "max_depth":          cfg["max_depth"],
            "min_child_samples":  cfg["min_child_samples"],
            "subsample":          cfg["subsample"],
            "colsample_bytree":   cfg["colsample_bytree"],
            "class_weight":       cfg["class_weight"],
            "verbose":            cfg["verbose"],
            "random_state":       42,
        }
        self.early_stopping_rounds = cfg["early_stopping_rounds"]
        self.model: Optional[lgb.LGBMClassifier] = None
        self.feature_names: List[str] = []

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        feature_names: List[str],
    ):
        """Train with early stopping on the validation set."""
        self.feature_names = feature_names
        logger.info(
            f"Training LightGBM | "
            f"Train: {len(X_train):,} | Val: {len(X_val):,} | "
            f"Features: {len(feature_names)}"
        )

        self.model = lgb.LGBMClassifier(**self.params)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[
                lgb.early_stopping(self.early_stopping_rounds, verbose=True),
                lgb.log_evaluation(period=50),
            ],
        )

        best_iter = self.model.best_iteration_
        logger.info(f"Training complete. Best iteration: {best_iter}")
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Return replay probabilities (0–1) for each row."""
        if self.model is None:
            raise RuntimeError("Model not trained. Call .train() first.")
        return self.model.predict_proba(X)[:, 1]

    def feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """Return a sorted DataFrame of feature importances."""
        if self.model is None:
            raise RuntimeError("Model not trained.")
        imp = pd.DataFrame({
            "feature":    self.feature_names,
            "importance": self.model.feature_importances_,
        }).sort_values("importance", ascending=False).head(top_n)
        return imp

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "feature_names": self.feature_names}, path)
        logger.info(f"Model saved to {path}")

    @classmethod
    def load(cls, path: str, config: dict) -> "MusicRecommenderLGBM":
        payload = joblib.load(path)
        instance = cls(config)
        instance.model = payload["model"]
        instance.feature_names = payload["feature_names"]
        logger.info(f"Model loaded from {path}")
        return instance
