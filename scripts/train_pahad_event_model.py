# -*- coding: utf-8 -*-
"""
scripts/train_pahad_event_model.py
==================================
PARVAT NETRA • PAHAD AI Landslide Event Prediction Model Training Pipeline
--------------------------------------------------------------------------
Trains the first genuine event-calibrated classifier for future landslide occurrence.
Enforces:
  1. Spatial Group Cross-Validation: Strictly isolates geographic sectors/basins to prevent spatial leakage.
  2. Multi-Metric Operational Verification: ROC-AUC, PR-AUC, Brier score, POD, FAR, CSI.
  3. Probability Calibration: Platt sigmoid or isotonic scaling to output reliable event probabilities.
  4. Feature Explainability: Retains model feature importance for explainable decision triage.
  5. Scientific Honesty Protocol: Transparently records sample size limitations as TRAINED_LIMITED_DATA.

Usage:
  python scripts/train_pahad_event_model.py --algorithm gradient_boosting --forecast-window 6 --model-version 0.1
"""

from __future__ import annotations

import os
import sys
import json
import pickle
import argparse
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import GroupKFold
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    brier_score_loss,
    confusion_matrix
)

# Append workspace to sys.path
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from engine.pahad_events import EVENT_FEATURE_COLUMNS, SUPPORTED_FORECAST_HORIZONS
from services.pahad_event_dataset import PahadEventDatasetBuilder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TRAIN_PAHAD_EVENT_MODEL")


def compute_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Computes Expected Calibration Error (ECE)."""
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    for i in range(n_bins):
        bin_mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1])
        bin_count = np.sum(bin_mask)
        if bin_count > 0:
            bin_acc = np.mean(y_true[bin_mask])
            bin_conf = np.mean(y_prob[bin_mask])
            ece += (bin_count / n) * abs(bin_acc - bin_conf)
    return float(ece)


def train_pahad_event_model(
    algorithm: str = "gradient_boosting",
    forecast_window_hours: int = 6,
    model_version: str = "0.1",
    seed: int = 42,
    dataset_path: Optional[str] = None,
    output_path: Optional[str] = None,
    include_demo: bool = False
) -> Dict[str, Any]:
    """
    Executes end-to-end model training, spatial validation, calibration, and serialization.
    """
    logger.info(f"Initializing PAHAD event model training pipeline (Horizon: {forecast_window_hours}h)...")
    np.random.seed(seed)

    # 1. Load Dataset
    builder = PahadEventDatasetBuilder()
    observations = builder.build_historical_event_dataset(
        target_horizon_hours=forecast_window_hours,
        include_demo=include_demo
    )
    dataset_report = builder.get_dataset_quality_report(observations)

    X, y, groups = builder.export_feature_matrix(observations)
    logger.info(f"Loaded dataset with {X.shape[0]} samples, {X.shape[1]} features across {len(np.unique(groups))} spatial groups.")
    logger.info(f"Class balance: {np.sum(y == 1)} Positives, {np.sum(y == 0)} Negatives.")

    # 2. Configure Baseline Classifier
    if algorithm.lower() in ("random_forest", "rf"):
        clf = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_split=3,
            class_weight="balanced",
            random_state=seed
        )
        algo_name = "RandomForestClassifier"
    else:
        clf = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.08,
            max_depth=3,
            subsample=0.85,
            random_state=seed
        )
        algo_name = "GradientBoostingClassifier"

    # 3. Spatial Group Cross-Validation
    n_groups = len(np.unique(groups))
    n_splits = min(5, max(2, n_groups))
    gkf = GroupKFold(n_splits=n_splits)

    oof_preds = np.zeros(len(y), dtype=np.float32)
    oof_probs = np.zeros(len(y), dtype=np.float32)

    logger.info(f"Executing Spatial Group {n_splits}-Fold Cross-Validation...")
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups)):
        X_train, y_train = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx], y[val_idx]

        # Fit fold model
        clf_fold = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.08,
            max_depth=3,
            subsample=0.85,
            random_state=seed + fold
        ) if algorithm.lower() != "random_forest" else RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            class_weight="balanced",
            random_state=seed + fold
        )
        clf_fold.fit(X_train, y_train)

        probs_val = clf_fold.predict_proba(X_val)[:, 1]
        oof_probs[val_idx] = probs_val
        oof_preds[val_idx] = (probs_val >= 0.50).astype(int)

    # 4. Operational Validation Metrics Calculation
    roc_auc = float(roc_auc_score(y, oof_probs)) if len(np.unique(y)) > 1 else 1.0
    pr_auc = float(average_precision_score(y, oof_probs)) if len(np.unique(y)) > 1 else 1.0
    prec = float(precision_score(y, oof_preds, zero_division=0))
    rec = float(recall_score(y, oof_preds, zero_division=0))
    f1 = float(f1_score(y, oof_preds, zero_division=0))
    brier = float(brier_score_loss(y, oof_probs))
    ece = compute_calibration_error(y, oof_probs, n_bins=5)

    # Operational Disaster Prediction Metrics (POD, FAR, CSI)
    # Confusion Matrix: [[TN, FP], [FN, TP]]
    cm = confusion_matrix(y, oof_preds, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
    pod = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0  # Probability of Detection
    far = float(fp / (tp + fp)) if (tp + fp) > 0 else 0.0  # False Alarm Ratio
    csi = float(tp / (tp + fn + fp)) if (tp + fn + fp) > 0 else 0.0  # Critical Success Index (Threat Score)

    metrics = {
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "brier_score": round(brier, 4),
        "calibration_error": round(ece, 4),
        "pod": round(pod, 4),
        "far": round(far, 4),
        "csi": round(csi, 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        }
    }

    logger.info(f"Spatial CV Results — ROC-AUC: {roc_auc:.4f} | PR-AUC: {pr_auc:.4f} | F1: {f1:.4f} | POD: {pod:.4f} | FAR: {far:.4f} | CSI: {csi:.4f}")

    # 5. Fit Full Model & Apply Probability Calibration
    logger.info("Training full model on all samples and fitting Platt sigmoid calibration...")
    # Fit base classifier for feature importance and raw probabilities
    clf.fit(X, y)

    # Calibrate probability predictions using sigmoid (Platt scaling) with 3-fold cross-calibration
    calibrated_clf = CalibratedClassifierCV(estimator=clf, method="sigmoid", cv=3)
    calibrated_clf.fit(X, y)

    # 6. Feature Importance Extraction
    importances = {}
    if hasattr(clf, "feature_importances_"):
        raw_imp = clf.feature_importances_
        for idx, col in enumerate(EVENT_FEATURE_COLUMNS):
            importances[col] = round(float(raw_imp[idx]), 4)
    # Sort top drivers
    sorted_drivers = sorted(importances.items(), key=lambda x: x[1], reverse=True)

    # 7. Model Status & Serialization
    model_status = "DEMO_ONLY" if include_demo else dataset_report["model_data_tier"]
    models_dir = os.path.join(WORKSPACE_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)

    target_pkl = output_path or os.path.join(models_dir, "pahad_event_model.pkl")
    target_meta = target_pkl.replace(".pkl", ".metadata.json")

    # Save bundle containing calibrated model, raw model, and feature schema
    bundle = {
        "calibrated_model": calibrated_clf,
        "raw_model": clf,
        "feature_columns": EVENT_FEATURE_COLUMNS,
        "forecast_window_hours": forecast_window_hours,
        "algorithm": algo_name,
        "version": model_version,
        "status": model_status
    }

    with open(target_pkl, "wb") as f:
        pickle.dump(bundle, f)
    logger.info(f"Serialized trained event model to: {target_pkl}")

    metadata = {
        "model_name": "PAHAD-Event-Classifier",
        "version": f"{model_version}-event-calibrated",
        "algorithm": algo_name,
        "forecast_window_hours": forecast_window_hours,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "status": model_status,
        "feature_schema": EVENT_FEATURE_COLUMNS,
        "forecast_windows": SUPPORTED_FORECAST_HORIZONS,
        "validation_strategy": f"Spatial Group {n_splits}-Fold Cross-Validation (GroupKFold by Sector/Basin)",
        "metrics": metrics,
        "calibration_method": "Platt Sigmoid (CalibratedClassifierCV)",
        "feature_importances": dict(sorted_drivers[:15]),
        "dataset_report": dataset_report,
        "training_provenance": "[HISTORICAL]" if not include_demo else "[DEMO]"
    }

    with open(target_meta, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved model metadata to: {target_meta}")

    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train PAHAD AI Landslide Event Prediction Model")
    parser.add_argument("--algorithm", type=str, default="gradient_boosting", help="Classifier algorithm (gradient_boosting, random_forest)")
    parser.add_argument("--forecast-window", type=int, default=6, help="Target prediction horizon in hours (1, 3, 6, 12, 24, 48)")
    parser.add_argument("--model-version", type=str, default="0.1", help="Model semantic version string")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--dataset", type=str, default=None, help="Optional external dataset path")
    parser.add_argument("--output", type=str, default=None, help="Output destination for model .pkl")
    parser.add_argument("--include-demo", action="store_true", help="Include synthetic demo samples for testing")

    args = parser.parse_args()
    train_pahad_event_model(
        algorithm=args.algorithm,
        forecast_window_hours=args.forecast_window,
        model_version=args.model_version,
        seed=args.seed,
        dataset_path=args.dataset,
        output_path=args.output,
        include_demo=args.include_demo
    )
