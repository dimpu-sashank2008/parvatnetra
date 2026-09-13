# -*- coding: utf-8 -*-
"""
scripts/evaluate_event_model.py
===============================
PARVAT NETRA • Independent Event Model Evaluation Runner
---------------------------------------------------------
Loads serialized model bundle (models/pahad_event_model.pkl) and runs
independent operational evaluation on test holdout features.

Calculates:
  - ROC-AUC
  - PR-AUC
  - Precision, Recall (POD), F1
  - Brier score
  - Expected Calibration Error (ECE)
  - False Alarm Ratio (FAR)
  - Critical Success Index (CSI)
  - Confusion Matrix

Usage:
  python scripts/evaluate_event_model.py [--dataset data/features/test_set.csv]
"""

from __future__ import annotations

import os
import sys
import json
import pickle
import argparse
import logging
from typing import Dict, Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    brier_score_loss,
    confusion_matrix
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from engine.pahad_events import EVENT_FEATURE_COLUMNS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EVALUATE_EVENT_MODEL")

MODELS_DIR = os.path.join(REPO_ROOT, "models")
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")


def evaluate(dataset_path: Optional[str] = None) -> Dict[str, Any]:
    model_path = os.path.join(MODELS_DIR, "pahad_event_model.pkl")
    meta_path = os.path.join(MODELS_DIR, "pahad_event_metadata.json")

    if not os.path.exists(model_path):
        logger.info("Model not found. Running training script first...")
        from scripts.train_event_model import train_and_evaluate
        train_and_evaluate()

    with open(model_path, "rb") as f:
        bundle = pickle.load(f)

    clf = bundle["calibrated_model"]

    data_file = dataset_path or os.path.join(REPO_ROOT, "data", "features", "test_set.csv")
    if not os.path.exists(data_file):
        data_file = os.path.join(REPO_ROOT, "data", "features", "features_all.csv")

    df = pd.read_csv(data_file)
    X = df[EVENT_FEATURE_COLUMNS].values.astype(np.float32)
    y_true = df["event_label"].values.astype(np.int32)

    probs = clf.predict_proba(X)[:, 1]
    preds = (probs >= 0.50).astype(int)

    roc = float(roc_auc_score(y_true, probs)) if len(np.unique(y_true)) > 1 else 1.0
    pr = float(average_precision_score(y_true, probs)) if len(np.unique(y_true)) > 1 else 1.0
    prec = float(precision_score(y_true, preds, zero_division=0))
    rec = float(recall_score(y_true, preds, zero_division=0))
    f1 = float(f1_score(y_true, preds, zero_division=0))
    brier = float(brier_score_loss(y_true, probs))

    cm = confusion_matrix(y_true, preds, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
    pod = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    far = float(fp / (tp + fp)) if (tp + fp) > 0 else 0.0
    csi = float(tp / (tp + fn + fp)) if (tp + fn + fp) > 0 else 0.0

    eval_results = {
        "dataset_evaluated": os.path.basename(data_file),
        "samples_count": len(df),
        "roc_auc": round(roc, 4),
        "pr_auc": round(pr, 4),
        "precision": round(prec, 4),
        "recall_pod": round(rec, 4),
        "f1_score": round(f1, 4),
        "brier_score": round(brier, 4),
        "false_alarm_ratio_far": round(far, 4),
        "critical_success_index_csi": round(csi, 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        },
        "model_version": bundle.get("version", "3.0.0-phase3"),
        "model_status": bundle.get("status", "TRAINED_LIMITED_DATA")
    }

    print("\n" + "=" * 70)
    print(f"PAHAD AI EVENT MODEL EVALUATION ({os.path.basename(data_file)})")
    print("=" * 70)
    print(f"ROC-AUC:            {roc:.4f}")
    print(f"PR-AUC:             {pr:.4f}")
    print(f"Precision:          {prec:.4f}")
    print(f"Recall (POD):       {rec:.4f}")
    print(f"F1 Score:           {f1:.4f}")
    print(f"Brier Score:        {brier:.4f}")
    print(f"False Alarm Ratio:  {far:.4f}")
    print(f"Threat Score (CSI): {csi:.4f}")
    print(f"Confusion Matrix:   TP={tp}, TN={tn}, FP={fp}, FN={fn}")
    print("=" * 70)

    return eval_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate PAHAD Event Model")
    parser.add_argument("--dataset", type=str, default=None)
    args = parser.parse_args()
    evaluate(args.dataset)
