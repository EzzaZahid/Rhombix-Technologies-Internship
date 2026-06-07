"""
Evaluation metrics for the music recommendation system.

Primary metrics (in order of importance):
  1. AUC-ROC       — Does the model rank replay songs above non-replay songs?
  2. NDCG@K        — Are the best songs ranked highest in the recommendation list?
  3. Log loss      — Are the predicted probabilities well-calibrated?
  4. Precision@K   — Of the top-K songs shown, how many did the user replay?
  5. Recall@K      — Of all songs the user would replay, how many are in top-K?
  6. F1 Score      — Harmonic mean of precision and recall (threshold-dependent)

Why NOT accuracy?
  The dataset is imbalanced — most songs are NOT replayed (label=0).
  A model that always predicts 0 gets high accuracy but is completely useless.
  AUC-ROC and NDCG are threshold-free and handle imbalance correctly.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score,
    log_loss,
    f1_score,
    precision_score,
    recall_score,
    average_precision_score,
    roc_curve,
)
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# 1. AUC-ROC
# ─────────────────────────────────────────────
def compute_auc_roc(y_true: np.ndarray, y_scores: np.ndarray) -> float:
    """
    Area Under the ROC Curve.

    Interpretation:
      0.5  = random guessing (coin flip)
      0.70 = acceptable
      0.80 = good
      0.90 = excellent
      1.0  = perfect (likely overfitting)

    For recommendation: "Given a randomly chosen replayed song and a randomly
    chosen non-replayed song, how often does the model rank the replayed one higher?"
    """
    return float(roc_auc_score(y_true, y_scores))


# ─────────────────────────────────────────────
# 2. Log Loss
# ─────────────────────────────────────────────
def compute_log_loss(y_true: np.ndarray, y_scores: np.ndarray) -> float:
    """
    Cross-entropy loss on predicted probabilities.

    Penalises confident wrong predictions heavily.
    A model that says "90% chance of replay" but the song isn't replayed
    is punished much more than one that says "55% chance".

    Lower is better. A random model gives log_loss ≈ 0.693 (log(2)).
    Target: < 0.45 is good, < 0.35 is excellent.
    """
    return float(log_loss(y_true, y_scores))


# ─────────────────────────────────────────────
# 3. Precision@K and Recall@K
# ─────────────────────────────────────────────
def precision_at_k(y_true: np.ndarray, y_scores: np.ndarray, k: int) -> float:
    """
    Precision@K: Of the top-K ranked songs, what fraction did the user replay?

    Example (K=5):
      Recommended: [Song A✓, Song B✗, Song C✓, Song D✗, Song E✓]
      Precision@5 = 3/5 = 0.60

    Best: 1.0 (every recommendation was a replay)
    Worst: 0.0 (none of the recommendations were replayed)
    """
    if k <= 0:
        raise ValueError("k must be positive")
    top_k_idx = np.argsort(y_scores)[::-1][:k]
    return float(np.mean(y_true[top_k_idx]))


def recall_at_k(y_true: np.ndarray, y_scores: np.ndarray, k: int) -> float:
    """
    Recall@K: Of all songs the user would have replayed, what fraction
    appear in the top-K recommendations?

    Example (K=5, user has 10 total replay songs):
      Recommended top-5 contains 3 replay songs
      Recall@5 = 3/10 = 0.30

    Precision and Recall trade off: higher K → higher recall, lower precision.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    total_positives = np.sum(y_true)
    if total_positives == 0:
        return 0.0
    top_k_idx = np.argsort(y_scores)[::-1][:k]
    hits = np.sum(y_true[top_k_idx])
    return float(hits / total_positives)


# ─────────────────────────────────────────────
# 4. NDCG@K
# ─────────────────────────────────────────────
def ndcg_at_k(y_true: np.ndarray, y_scores: np.ndarray, k: int) -> float:
    """
    Normalized Discounted Cumulative Gain at K.

    Like Precision@K but POSITION-AWARE: a replay song ranked #1
    is worth more than the same song ranked #5.

    The "discount" is log2(rank + 1) — higher rank = bigger discount.

    DCG@K  = sum over top-K of: relevance_i / log2(i + 2)
    IDCG@K = DCG of the perfect ranking (all positives first)
    NDCG@K = DCG@K / IDCG@K

    Range: 0.0 (worst) to 1.0 (perfect ordering)
    Target: > 0.60 is good, > 0.75 is excellent.
    """
    if k <= 0:
        raise ValueError("k must be positive")

    top_k_idx = np.argsort(y_scores)[::-1][:k]
    top_k_labels = y_true[top_k_idx]

    # DCG: sum of rel_i / log2(i+2) for i in 0..k-1
    positions = np.arange(1, len(top_k_labels) + 1)
    dcg = float(np.sum(top_k_labels / np.log2(positions + 1)))

    # IDCG: the perfect DCG (put all positives first)
    n_positives = int(np.sum(y_true))
    ideal_labels = np.zeros(k)
    ideal_labels[:min(n_positives, k)] = 1
    idcg = float(np.sum(ideal_labels / np.log2(positions + 1)))

    return dcg / idcg if idcg > 0 else 0.0


# ─────────────────────────────────────────────
# 5. F1 Score (at optimal threshold)
# ─────────────────────────────────────────────
def compute_f1(y_true: np.ndarray, y_scores: np.ndarray) -> Dict[str, float]:
    """
    F1 score at the threshold that maximises F1.

    Since the data is imbalanced, the default 0.5 threshold is usually wrong.
    This function searches for the best threshold from the ROC curve.

    Returns both the best F1 and the threshold used.
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    precision = tpr / (tpr + fpr + 1e-9)
    recall = tpr
    f1_scores = 2 * precision * recall / (precision + recall + 1e-9)
    best_idx = np.argmax(f1_scores)
    return {
        "f1":        float(f1_scores[best_idx]),
        "threshold": float(thresholds[best_idx]),
        "precision": float(precision[best_idx]),
        "recall":    float(recall[best_idx]),
    }


# ─────────────────────────────────────────────
# 6. Per-user metrics (important for fairness)
# ─────────────────────────────────────────────
def per_user_ndcg(
    df: pd.DataFrame,
    y_scores: np.ndarray,
    k: int = 10,
) -> pd.DataFrame:
    """
    Compute NDCG@K separately for each user.

    Useful for diagnosing:
      - Do casual listeners get worse recommendations than power users?
      - Are new users (cold start) penalised?

    Returns a DataFrame with user_id and their individual NDCG@K.
    """
    df = df.copy()
    df["score"] = y_scores
    results = []

    for user_id, group in df.groupby("user_id"):
        u_scores = group["score"].values
        u_labels = group["label"].values
        ndcg = ndcg_at_k(u_labels, u_scores, k=min(k, len(group)))
        results.append({"user_id": user_id, f"ndcg_at_{k}": ndcg, "n_songs": len(group)})

    return pd.DataFrame(results)


# ─────────────────────────────────────────────
# Master evaluation function
# ─────────────────────────────────────────────
def evaluate(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    k_values: List[int] = [5, 10, 20],
    model_name: str = "model",
) -> Dict:
    """
    Run the full evaluation suite and return a results dictionary.

    Args:
        y_true:     Ground truth labels (0 or 1)
        y_scores:   Predicted probabilities from the model
        k_values:   List of K values for ranking metrics
        model_name: Name shown in the results table (e.g. "LightGBM")

    Returns:
        Dictionary of all metric values
    """
    y_true = np.array(y_true)
    y_scores = np.array(y_scores)

    results = {"model": model_name}

    # --- Core metrics ---
    results["auc_roc"]  = compute_auc_roc(y_true, y_scores)
    results["log_loss"] = compute_log_loss(y_true, y_scores)

    # --- Ranking metrics at each K ---
    for k in k_values:
        results[f"precision_at_{k}"] = precision_at_k(y_true, y_scores, k)
        results[f"recall_at_{k}"]    = recall_at_k(y_true, y_scores, k)
        results[f"ndcg_at_{k}"]      = ndcg_at_k(y_true, y_scores, k)

    # --- F1 at best threshold ---
    f1_result = compute_f1(y_true, y_scores)
    results["f1"]              = f1_result["f1"]
    results["best_threshold"]  = f1_result["threshold"]

    # --- Average precision (area under PR curve) ---
    results["avg_precision"] = float(average_precision_score(y_true, y_scores))

    return results


def print_report(results: Dict, k_values: List[int] = [5, 10, 20]):
    """Pretty-print the evaluation results."""
    sep = "─" * 46
    print(f"\n{sep}")
    print(f"  Evaluation Report — {results['model']}")
    print(sep)
    print(f"  {'AUC-ROC':<28} {results['auc_roc']:.4f}")
    print(f"  {'Log loss':<28} {results['log_loss']:.4f}")
    print(f"  {'Avg precision (PR-AUC)':<28} {results['avg_precision']:.4f}")
    print(f"  {'F1 (best threshold)':<28} {results['f1']:.4f}  [threshold={results['best_threshold']:.2f}]")
    print(sep)
    for k in k_values:
        print(f"  {'Precision@' + str(k):<28} {results[f'precision_at_{k}']:.4f}")
        print(f"  {'Recall@' + str(k):<28} {results[f'recall_at_{k}']:.4f}")
        print(f"  {'NDCG@' + str(k):<28} {results[f'ndcg_at_{k}']:.4f}")
        if k != k_values[-1]:
            print()
    print(sep)


def compare_models(results_list: List[Dict], k: int = 10) -> pd.DataFrame:
    """
    Compare multiple models side by side in a DataFrame.

    Usage:
        baseline_results = evaluate(y_test, baseline_scores, model_name="Baseline")
        lgbm_results     = evaluate(y_test, lgbm_scores,     model_name="LightGBM")
        compare_models([baseline_results, lgbm_results])
    """
    rows = []
    for r in results_list:
        rows.append({
            "Model":              r["model"],
            "AUC-ROC":            f"{r['auc_roc']:.4f}",
            "Log loss":           f"{r['log_loss']:.4f}",
            f"Precision@{k}":     f"{r[f'precision_at_{k}']:.4f}",
            f"Recall@{k}":        f"{r[f'recall_at_{k}']:.4f}",
            f"NDCG@{k}":          f"{r[f'ndcg_at_{k}']:.4f}",
            "F1":                 f"{r['f1']:.4f}",
        })
    return pd.DataFrame(rows).set_index("Model")
