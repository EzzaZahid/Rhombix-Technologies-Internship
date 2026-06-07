"""
Generate recommendations for a specific user.

Usage:
    python scripts/predict.py --user-id u_0001 --top-k 10
    python scripts/predict.py --user-id new_user_123   # triggers cold start
"""

import sys, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.io import load_config
from src.utils.logger import setup_logger
from src.data.loader import load_events
from src.data.splitter import time_split
from src.features.interaction import run_feature_pipeline
from src.models.lgbm_model import MusicRecommenderLGBM
from src.models.predictor import RecommendationPredictor


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--user-id", required=True)
    p.add_argument("--top-k", type=int, default=10)
    p.add_argument("--config", default="configs/config.yaml")
    args = p.parse_args()

    config = load_config(args.config)
    setup_logger(config["logging"]["level"])

    df = load_events(config["data"]["raw_path"])
    train_df, _ = time_split(df, test_size=config["split"]["test_size"])

    from src.features.user_features import build_user_features
    from src.features.song_features import build_song_features
    user_feats = build_user_features(train_df)
    song_feats = build_song_features(train_df)

    model = MusicRecommenderLGBM.load(config["model"]["save_path"], config)
    predictor = RecommendationPredictor(model, user_feats, song_feats, config)

    recs = predictor.recommend(args.user_id, top_k=args.top_k)
    print(f"\nTop {args.top_k} recommendations for user '{args.user_id}':\n")
    print(recs.to_string(index=False))


if __name__ == "__main__":
    main()
