# -*- coding: utf-8 -*-
"""
scripts/build_temporal_sequences.py
====================================
PARVAT NETRA • PAHAD AI — Multi-Horizon Temporal Sequence Builder
------------------------------------------------------------------
Builds location-aware temporal sequence datasets with missingness masks,
strictly isolated training normalization, and multi-horizon labels (6h, 12h, 24h, 48h).

Produces:
  data/manifests/temporal_sequence_manifest.json (with cryptographic SHA-256 hashes)

Usage:
  python scripts/build_temporal_sequences.py
"""

from __future__ import annotations

import os
import sys
import json
import hashlib
import logging
from datetime import datetime, timezone

import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BUILD_TEMPORAL_SEQUENCES")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from engine.pahad_sequence_pipeline import PahadSequencePipeline, CANONICAL_FEATURE_COLUMNS, HORIZONS

DATA_DIR = os.path.join(REPO_ROOT, "data", "processed")
MANIFEST_DIR = os.path.join(REPO_ROOT, "data", "manifests")


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def build_sequences():
    logger.info("=" * 65)
    logger.info("PARVAT NETRA • PAHAD AI — Building Temporal Observation Sequences")
    logger.info("=" * 65)

    os.makedirs(MANIFEST_DIR, exist_ok=True)

    train_path = os.path.join(DATA_DIR, "phase5b_temporal_train.csv")
    val_path = os.path.join(DATA_DIR, "phase5b_temporal_val.csv")
    test_path = os.path.join(DATA_DIR, "phase5b_temporal_test.csv")

    for p in [train_path, val_path, test_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing required temporal partition: {p}")

    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)

    train_hash = compute_sha256(train_path)
    val_hash = compute_sha256(val_path)
    test_hash = compute_sha256(test_path)

    pipeline = PahadSequencePipeline(feature_columns=CANONICAL_FEATURE_COLUMNS)

    # 1. Fit ONLY on train partition
    train_ds = pipeline.fit_transform(df_train, dataset_hash=train_hash)
    logger.info("Train partition transformed: N=%d, Features=%d", train_ds.sample_count, len(pipeline.feature_columns))

    # 2. Transform val and test using train statistics
    val_ds = pipeline.transform(df_val, partition_name="validation")
    logger.info("Validation partition transformed: N=%d", val_ds.sample_count)

    test_ds = pipeline.transform(df_test, partition_name="test")
    logger.info("Test partition transformed: N=%d", test_ds.sample_count)

    # 3. Build sector sequence sliding windows (window_size=6 steps)
    train_sector_seqs = pipeline.build_sector_sequences(train_ds, window_size=6)
    val_sector_seqs = pipeline.build_sector_sequences(val_ds, window_size=6)
    test_sector_seqs = pipeline.build_sector_sequences(test_ds, window_size=6)

    # 4. Generate and save Sequence Manifest
    manifest = {
        "manifest_version": "10.0.0-phase10",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "feature_schema": {
            "canonical_features": CANONICAL_FEATURE_COLUMNS,
            "feature_dim": len(CANONICAL_FEATURE_COLUMNS),
            "cri_target_leakage_prevented": True
        },
        "horizons": HORIZONS,
        "input_dataset_hashes": {
            "train_sha256": train_hash,
            "val_sha256": val_hash,
            "test_sha256": test_hash
        },
        "partitions": {
            "train": train_ds.to_dict(),
            "validation": val_ds.to_dict(),
            "test": test_ds.to_dict()
        },
        "sector_sequence_tensor_shapes": {
            "train_sectors": len(train_sector_seqs),
            "val_sectors": len(val_sector_seqs),
            "test_sectors": len(test_sector_seqs)
        },
        "normalization": {
            "method": "StandardScaler",
            "fitted_strictly_on": "train",
            "val_test_fitted": False
        },
        "missingness_mask": {
            "type": "binary_indicator",
            "values": "1=observed, 0=imputed/missing",
            "train_missing_rate": float(1.0 - np.mean(train_ds.missingness_masks)),
            "test_missing_rate": float(1.0 - np.mean(test_ds.missingness_masks))
        },
        "deep_lstm_eligibility": {
            "required_sequences": 500,
            "actual_train_sequences": train_ds.sample_count,
            "status": "NOT_TRAINED_DATA_INSUFFICIENT",
            "torch_available": False
        }
    }

    manifest_path = os.path.join(MANIFEST_DIR, "temporal_sequence_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.info("Manifest saved to %s", manifest_path)
    logger.info("=" * 65)
    logger.info("TEMPORAL SEQUENCE PIPELINE EXECUTION COMPLETED")
    logger.info("=" * 65)
    return manifest


if __name__ == "__main__":
    build_sequences()
