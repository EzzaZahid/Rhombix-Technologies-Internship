"""Unit tests for evaluation metrics."""

import numpy as np
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.metrics import (
    compute_auc_roc, compute_log_loss,
    precision_at_k, recall_at_k, ndcg_at_k, compute_f1
)


def test_auc_roc_perfect():
    y = np.array([0, 0, 1, 1])
    scores = np.array([0.1, 0.2, 0.8, 0.9])
    assert compute_auc_roc(y, scores) == 1.0


def test_auc_roc_random():
    rng = np.random.default_rng(42)
    y = rng.integers(0, 2, 200)
    scores = rng.uniform(0, 1, 200)
    auc = compute_auc_roc(y, scores)
    assert 0.4 < auc < 0.6  # near random


def test_ndcg_perfect_ranking():
    y = np.array([1, 1, 0, 0, 0])
    scores = np.array([0.9, 0.8, 0.3, 0.2, 0.1])
    assert ndcg_at_k(y, scores, k=5) == pytest.approx(1.0)


def test_ndcg_worst_ranking():
    y = np.array([1, 1, 0, 0, 0])
    scores = np.array([0.1, 0.2, 0.8, 0.9, 0.95])
    assert ndcg_at_k(y, scores, k=5) < 0.5


def test_precision_at_k_all_correct():
    y = np.array([1, 1, 1, 0, 0])
    scores = np.array([0.9, 0.8, 0.7, 0.2, 0.1])
    assert precision_at_k(y, scores, k=3) == pytest.approx(1.0)


def test_recall_at_k():
    y = np.array([1, 1, 0, 0, 1])  # 3 positives
    scores = np.array([0.9, 0.8, 0.3, 0.2, 0.1])
    # Top-2 contains 2 out of 3 positives → recall = 2/3
    assert recall_at_k(y, scores, k=2) == pytest.approx(2/3, abs=0.01)


def test_log_loss_calibrated():
    y = np.array([0, 0, 1, 1])
    perfect = np.array([0.01, 0.01, 0.99, 0.99])
    random  = np.array([0.50, 0.50, 0.50, 0.50])
    assert compute_log_loss(y, perfect) < compute_log_loss(y, random)


def test_k_must_be_positive():
    with pytest.raises(ValueError):
        precision_at_k(np.array([1, 0]), np.array([0.9, 0.1]), k=0)
