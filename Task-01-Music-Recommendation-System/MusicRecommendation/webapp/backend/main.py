"""
FastAPI backend for the Music Recommendation System web app.
Exposes REST endpoints consumed by the React frontend.

Endpoints:
  POST /api/generate-data     — generate synthetic dataset
  POST /api/train             — train the model
  GET  /api/status            — pipeline status + metrics
  GET  /api/recommend/{uid}   — top-K recommendations for a user
  GET  /api/users             — list all users
  GET  /api/feature-importance— top feature importances
  GET  /api/metrics-history   — evaluation metrics over training
  POST /api/reset             — wipe model + data
"""

import sys, os, asyncio, json, traceback
from pathlib import Path
from typing import Optional
import numpy as np

# //sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

print("PROJECT ROOT =", Path(__file__).resolve().parents[3])


from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# ── internal modules ──────────────────────────────────────────────────
from src.utils.io import load_config
from src.utils.logger import setup_logger
import src.data.generator as generator
from src.data.loader import load_events
from src.data.splitter import time_split
from src.features.interaction import run_feature_pipeline
from src.features.user_features import build_user_features
from src.features.song_features import build_song_features
from src.models.lgbm_model import MusicRecommenderLGBM
from src.models.baseline import MusicRecommenderBaseline
from src.models.predictor import RecommendationPredictor
from src.evaluation.metrics import evaluate

setup_logger("INFO")
app = FastAPI(title="Music Recommendation API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── in-memory state (small demo app — no DB needed) ───────────────────
STATE = {
    "status": "idle",          # idle | generating | training | ready | error
    "progress": 0,
    "message": "No model trained yet. Generate data and train to begin.",
    "metrics": None,
    "baseline_metrics": None,
    "feature_importance": None,
    "n_users": 0,
    "n_songs": 0,
    "n_events": 0,
    "replay_rate": 0.0,
    "error": None,
}

ARTIFACTS = {
    "model": None,
    "user_feats": None,
    "song_feats": None,
    "predictor": None,
    "test_df": None,
    "config": None,
}

CONFIG_PATH = Path(__file__).parent.parent.parent / "configs" / "config.yaml"


# ─────────────────────────────────────────────────────────────────────
# Background training task
# ─────────────────────────────────────────────────────────────────────
async def _run_pipeline(n_users: int, n_songs: int, n_events: int):
    try:
        config = load_config(str(CONFIG_PATH))
        config["data"]["n_synthetic_users"] = n_users
        config["data"]["n_synthetic_songs"] = n_songs
        config["data"]["n_synthetic_events"] = n_events
        ARTIFACTS["config"] = config

        # 1 — generate
        STATE.update(status="generating", progress=5, message="Generating synthetic dataset…")
        await asyncio.sleep(0.1)
        os.makedirs("data/raw", exist_ok=True)
        os.makedirs("data/sample", exist_ok=True)
        os.makedirs("models", exist_ok=True)
        events = await asyncio.to_thread(generator.run, config)

        STATE.update(progress=25, message="Data generated. Loading & cleaning…")

        # 2 — load + split
        df = await asyncio.to_thread(load_events, config["data"]["raw_path"])
        train_df, test_df = await asyncio.to_thread(time_split, df, config["split"]["test_size"])
        ARTIFACTS["test_df"] = test_df

        STATE.update(
            status="training", progress=40, message="Engineering features…",
            n_users=int(df["user_id"].nunique()),
            n_songs=int(df["song_id"].nunique()),
            n_events=len(df),
            replay_rate=float(df["label"].mean()),
        )

        # 3 — features
        result = await asyncio.to_thread(run_feature_pipeline, train_df, test_df)
        X_train, y_train, X_test, y_test, feat_names, user_feats, song_feats = result
        ARTIFACTS["user_feats"] = user_feats
        ARTIFACTS["song_feats"] = song_feats

        STATE.update(progress=60, message="Training LightGBM model…")

        # 4 — baseline
        baseline = MusicRecommenderBaseline(config)
        await asyncio.to_thread(
            baseline.train, X_train, y_train, None, None, feat_names
        )
        b_scores = await asyncio.to_thread(baseline.predict_proba, X_test)
        b_results = evaluate(y_test.values, b_scores,
                             k_values=config["evaluation"]["top_k"],
                             model_name="Logistic Regression")
        STATE["baseline_metrics"] = b_results

        STATE.update(progress=75, message="Training LightGBM…")

        # 5 — lgbm
        lgbm = MusicRecommenderLGBM(config)
        await asyncio.to_thread(
            lgbm.train, X_train, y_train, X_test, y_test, feat_names
        )
        lgbm.save(config["model"]["save_path"])
        ARTIFACTS["model"] = lgbm

        STATE.update(progress=90, message="Evaluating model…")

        scores = await asyncio.to_thread(lgbm.predict_proba, X_test)
        metrics = evaluate(y_test.values, scores,
                           k_values=config["evaluation"]["top_k"],
                           model_name="LightGBM")
        STATE["metrics"] = metrics

        # 6 — feature importance
        imp_df = lgbm.feature_importance(top_n=15)
        STATE["feature_importance"] = imp_df.to_dict(orient="records")

        # 7 — predictor
        predictor = RecommendationPredictor(lgbm, user_feats, song_feats, config)
        ARTIFACTS["predictor"] = predictor

        STATE.update(
            status="ready", progress=100,
            message=f"Model ready! AUC-ROC: {metrics['auc_roc']:.4f} | NDCG@10: {metrics['ndcg_at_10']:.4f}",
            error=None,
        )

    except Exception as e:
        STATE.update(
            status="error", progress=0,
            message="Pipeline failed. See error below.",
            error=traceback.format_exc(),
        )


# ─────────────────────────────────────────────────────────────────────
# Request / Response models
# ─────────────────────────────────────────────────────────────────────
class TrainRequest(BaseModel):
    n_users: int = 300
    n_songs: int = 1000
    n_events: int = 50000


# ─────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────
@app.get("/api/status")
def get_status():
    return STATE


@app.post("/api/train")
async def train(req: TrainRequest, background_tasks: BackgroundTasks):
    if STATE["status"] in ("generating", "training"):
        raise HTTPException(400, "Pipeline already running.")
    STATE.update(status="generating", progress=0, error=None,
                 metrics=None, baseline_metrics=None, feature_importance=None)
    background_tasks.add_task(_run_pipeline, req.n_users, req.n_songs, req.n_events)
    return {"message": "Pipeline started."}


@app.post("/api/reset")
def reset():
    STATE.update(status="idle", progress=0,
                 message="Reset. Generate data and train to begin.",
                 metrics=None, baseline_metrics=None,
                 feature_importance=None, n_users=0, n_songs=0,
                 n_events=0, replay_rate=0.0, error=None)
    ARTIFACTS.update(model=None, user_feats=None, song_feats=None,
                     predictor=None, test_df=None)
    return {"message": "Reset complete."}


@app.get("/api/users")
def list_users(limit: int = 100):
    if ARTIFACTS["user_feats"] is None:
        raise HTTPException(400, "Model not trained yet.")
    uids = ARTIFACTS["user_feats"]["user_id"].tolist()[:limit]
    return {"users": uids}


@app.get("/api/recommend/{user_id}")
def recommend(user_id: str, top_k: int = 10):
    if ARTIFACTS["predictor"] is None:
        raise HTTPException(400, "Model not trained yet.")
    try:
        recs = ARTIFACTS["predictor"].recommend(user_id, top_k=top_k)
        # Enrich with song metadata if available
        song_feats = ARTIFACTS["song_feats"]
        recs = recs.merge(
            song_feats[["song_id", "song_energy", "song_valence",
                         "song_danceability", "song_tempo"]].drop_duplicates("song_id"),
            on="song_id", how="left"
        )
        # Replace NaN with None for JSON
        recs = recs.where(pd.notnull(recs), None)
        return {"user_id": user_id, "recommendations": recs.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/feature-importance")
def feature_importance():
    if STATE["feature_importance"] is None:
        raise HTTPException(400, "Model not trained yet.")
    return {"features": STATE["feature_importance"]}


@app.get("/api/metrics")
def get_metrics():
    if STATE["metrics"] is None:
        raise HTTPException(400, "Model not trained yet.")
    return {
        "lgbm": STATE["metrics"],
        "baseline": STATE["baseline_metrics"],
    }


@app.get("/")
def root():
    return {"message": "Music Recommendation API is running. Visit /docs for API explorer."}
