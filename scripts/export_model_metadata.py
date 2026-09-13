# -*- coding: utf-8 -*-
"""
scripts/export_model_metadata.py
================================
PARVAT NETRA • Model Metadata & MLOps Exporter
----------------------------------------------
Exports and verifies canonical JSON artifacts:
  - models/pahad_feature_schema.json
  - models/pahad_event_metadata.json
  - models/pahad_training_metrics.json

Usage:
  python scripts/export_model_metadata.py
"""

from __future__ import annotations

import os
import sys
import json
import logging
from typing import Dict, Any

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

MODELS_DIR = os.path.join(REPO_ROOT, "models")


def export_metadata() -> Dict[str, Any]:
    schema_path = os.path.join(MODELS_DIR, "pahad_feature_schema.json")
    meta_path = os.path.join(MODELS_DIR, "pahad_event_metadata.json")
    metrics_path = os.path.join(MODELS_DIR, "pahad_training_metrics.json")

    summary = {
        "feature_schema_present": os.path.exists(schema_path),
        "event_metadata_present": os.path.exists(meta_path),
        "training_metrics_present": os.path.exists(metrics_path),
    }

    if not summary["event_metadata_present"]:
        from scripts.train_event_model import train_and_evaluate
        train_and_evaluate()
        summary["event_metadata_present"] = os.path.exists(meta_path)
        summary["training_metrics_present"] = os.path.exists(metrics_path)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    print("\n" + "=" * 70)
    print("PAHAD AI MODEL ARTIFACT EXPORT SUMMARY")
    print("=" * 70)
    print(f"Model:     {meta.get('model_name')} v{meta.get('version')}")
    print(f"Algorithm: {meta.get('algorithm')}")
    print(f"Status:    {meta.get('status')}")
    print(f"Features:  {len(meta.get('feature_schema', []))} canonical features")
    print(f"Files:")
    print(f"  - {schema_path}")
    print(f"  - {meta_path}")
    print(f"  - {metrics_path}")
    print("=" * 70)

    return summary


if __name__ == "__main__":
    export_metadata()
