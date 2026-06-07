"""
Run evaluation on the test set using a saved model.

Usage:
    python scripts/evaluate.py
    python scripts/evaluate.py --per-user    # Also show per-user NDCG breakdown
"""

import sys, argparse, logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.io import load_config
from src.utils.logger import setup_logger
from src.data.loader import load_events
from src.data.splitter import time_split
from src.features.interaction import run_feature_pipeline
from src.models.lgbm_model import MusicRecommenderLGBM
from src.evaluation.metrics import evaluate, print_report, per_user_ndcg


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--per-user", action="store_true")
    p.add_argument("--config", default="configs/config.yaml")
    args = p.parse_args()

    config = load_config(args.config)
    setup_logger(config["logging"]["level"])

    df = load_events(config["data"]["raw_path"])
    train_df, test_df = time_split(df, test_size=config["split"]["test_size"])
    _, _, X_test, y_test, feat_names, _, _ = run_feature_pipeline(train_df, test_df)

    model = MusicRecommenderLGBM.load(config["model"]["save_path"], config)
    scores = model.predict_proba(X_test)

    results = evaluate(y_test.values, scores,
                       k_values=config["evaluation"]["top_k"],
                       model_name="LightGBM")
    print_report(results, config["evaluation"]["top_k"])

    if args.per_user:
        user_ndcg = per_user_ndcg(test_df.reset_index(drop=True), scores, k=10)
        print("\nPer-user NDCG@10 distribution:")
        print(user_ndcg["ndcg_at_10"].describe().round(4).to_string())
        low = user_ndcg[user_ndcg["ndcg_at_10"] < 0.40]
        print(f"\nUsers with NDCG@10 < 0.40: {len(low)} "
              f"({len(low)/len(user_ndcg):.1%}) — likely cold-start or casual listeners")


if __name__ == "__main__":
    main()
