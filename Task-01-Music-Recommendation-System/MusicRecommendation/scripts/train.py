"""
Training pipeline entry point.

Usage:
    python scripts/train.py                  # Train on existing data
    python scripts/train.py --generate-data  # Generate synthetic data first
    python scripts/train.py --sample         # Quick run on small sample
    python scripts/train.py --model baseline # Train logistic regression instead
"""

import sys
import argparse
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.io import load_config, save_features
from src.utils.logger import setup_logger
from src.data.loader import load_events, load_sample
from src.data.splitter import time_split
from src.features.interaction import run_feature_pipeline
from src.models.lgbm_model import MusicRecommenderLGBM
from src.models.baseline import MusicRecommenderBaseline
from src.evaluation.metrics import evaluate, print_report, compare_models
import src.data.generator as generator


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--generate-data", action="store_true",
                   help="Generate synthetic dataset before training")
    p.add_argument("--sample", action="store_true",
                   help="Use small sample for fast iteration")
    p.add_argument("--model", choices=["lgbm", "baseline", "both"],
                   default="both", help="Which model(s) to train")
    p.add_argument("--config", default="configs/config.yaml")
    return p.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)
    setup_logger(config["logging"]["level"], config["logging"]["log_file"])
    logger = logging.getLogger(__name__)

    # ── Step 1: Data ──────────────────────────────────────────────────
    if args.generate_data:
        logger.info("Generating synthetic dataset...")
        generator.run(config)

    if args.sample:
        df = load_sample(config)
    else:
        df = load_events(config["data"]["raw_path"])

    # ── Step 2: Train/test split ──────────────────────────────────────
    train_df, test_df = time_split(df, test_size=config["split"]["test_size"])

    # ── Step 3: Feature engineering ───────────────────────────────────
    logger.info("Running feature engineering pipeline...")
    X_train, y_train, X_test, y_test, feat_names, user_feats, song_feats = \
        run_feature_pipeline(train_df, test_df)

    # Save processed features for later inspection
    save_features(
        X_train.assign(label=y_train.values),
        config["data"]["processed_path"]
    )

    all_results = []

    # ── Step 4a: Baseline ─────────────────────────────────────────────
    if args.model in ("baseline", "both"):
        baseline = MusicRecommenderBaseline(config)
        baseline.train(X_train, y_train, feature_names=feat_names)
        baseline_scores = baseline.predict_proba(X_test)
        baseline_results = evaluate(
            y_test.values, baseline_scores,
            k_values=config["evaluation"]["top_k"],
            model_name="Logistic Regression"
        )
        print_report(baseline_results, config["evaluation"]["top_k"])
        all_results.append(baseline_results)
        baseline.save("models/baseline_model.pkl")

    # ── Step 4b: LightGBM ─────────────────────────────────────────────
    if args.model in ("lgbm", "both"):
        lgbm = MusicRecommenderLGBM(config)
        lgbm.train(X_train, y_train, X_test, y_test, feat_names)
        lgbm_scores = lgbm.predict_proba(X_test)
        lgbm_results = evaluate(
            y_test.values, lgbm_scores,
            k_values=config["evaluation"]["top_k"],
            model_name="LightGBM"
        )
        print_report(lgbm_results, config["evaluation"]["top_k"])
        all_results.append(lgbm_results)
        lgbm.save(config["model"]["save_path"])

        # Feature importance
        logger.info("\nTop 15 most important features:")
        imp = lgbm.feature_importance(top_n=15)
        print(imp.to_string(index=False))

    # ── Step 5: Comparison table ──────────────────────────────────────
    if len(all_results) > 1:
        print("\n── Model Comparison ──")
        print(compare_models(all_results, k=10).to_string())

    logger.info("Training pipeline complete.")


if __name__ == "__main__":
    main()
