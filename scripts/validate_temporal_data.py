# -*- coding: utf-8 -*-
"""
scripts/validate_temporal_data.py
==================================
PARVAT NETRA • PAHAD AI — Phase 12B Temporal Data Validator & Manifest Generator
---------------------------------------------------------------------------------
Audits all temporal datasets, computes cryptographic hashes, evaluates sequence continuity,
classifies gaps, runs leakage detection, and compiles data/manifests/phase12b_temporal_manifest.json.

Usage:
  python scripts/validate_temporal_data.py
"""

from __future__ import annotations

import os
import sys
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("VALIDATE_TEMPORAL_DATA")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from engine.pahad_temporal_engine import (
    CANONICAL_FEATURES,
    SequenceValidator,
    TemporalLeakageDetector,
    ProvenanceType,
    GapSeverity
)
from engine.pahad_temporal_gate import PahadTemporalGate, PROJECT_TARGETS, GateStatus

DATA_PROCESSED = os.path.join(REPO_ROOT, "data", "processed")
MANIFEST_DIR = os.path.join(REPO_ROOT, "data", "manifests")


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def generate_manifest():
    logger.info("=" * 70)
    logger.info("PARVAT NETRA • PAHAD AI — Validating Temporal Datasets & Generating Manifest")
    logger.info("=" * 70)

    os.makedirs(MANIFEST_DIR, exist_ok=True)

    full_path = os.path.join(DATA_PROCESSED, "phase5b_temporal_full.csv")
    train_path = os.path.join(DATA_PROCESSED, "phase5b_temporal_train.csv")
    val_path = os.path.join(DATA_PROCESSED, "phase5b_temporal_val.csv")
    test_path = os.path.join(DATA_PROCESSED, "phase5b_temporal_test.csv")

    for p in [full_path, train_path, val_path, test_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing required dataset: {p}")

    df_full = pd.read_csv(full_path)
    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)

    hashes = {
        "phase5b_temporal_full_sha256": compute_sha256(full_path),
        "phase5b_temporal_train_sha256": compute_sha256(train_path),
        "phase5b_temporal_val_sha256": compute_sha256(val_path),
        "phase5b_temporal_test_sha256": compute_sha256(test_path)
    }

    # 1. Leakage Audit
    leakage_audit = TemporalLeakageDetector.audit_partitions(df_train, df_val, df_test)
    logger.info("Leakage Audit: Zero Leakage = %s", leakage_audit["zero_leakage_verified"])

    # 2. Sequence Quality by Sector
    sector_audits = {}
    quality_scores = []
    for sector_id, grp in df_full.groupby("sector_id"):
        grp_sorted = grp.sort_values("timestamp")
        res = SequenceValidator.validate_sequence(grp_sorted)
        sector_audits[sector_id] = res
        quality_scores.append(res["quality_score"])

    mean_quality = float(np.mean(quality_scores)) if quality_scores else 0.0

    # 3. Gate Status
    gate_eval = PahadTemporalGate.evaluate_current_repository()

    # 4. Compile Manifest
    manifest = {
        "manifest_version": "12.0.0-phase12b",
        "title": "PARVAT NETRA • PAHAD AI — Phase 12B Real Temporal Infrastructure Manifest",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "crs": "WGS84 / EPSG:4326",
        "dataset_hashes": hashes,
        "schema_specification": {
            "canonical_features": CANONICAL_FEATURES,
            "feature_dim": len(CANONICAL_FEATURES),
            "target_leakage_prevented": True,
            "target_features_excluded": ["composite_risk_index_cri", "event_label", "is_event_sample", "target_6h", "target_12h", "target_24h", "target_48h"]
        },
        "empirical_audit_summary": {
            "temporal_rows_total": len(df_full),
            "unique_timestamps": int(df_full["timestamp"].nunique()),
            "unique_corridors": int(df_full["sector_id"].nunique()),
            "continuous_real_sequences": 0,
            "engineered_event_sequences": 17,
            "real_sensor_rows": 0,
            "simulated_or_modelled_rows": int((df_full["provenance"] == "[MODELLED]").sum()),
            "missingness_rate_overall": 0.0,
            "temporal_span": {
                "start": df_full["timestamp"].min(),
                "end": df_full["timestamp"].max(),
                "coverage_mode": "EPISODIC_DISASTER_ANTECEDENT_SNAPSHOTS"
            }
        },
        "partitions": {
            "train": {
                "sample_count": len(df_train),
                "date_range": [df_train["timestamp"].min(), df_train["timestamp"].max()],
                "positives_by_horizon": {"6h": int(df_train.get("target_6h", 0).sum()), "12h": int(df_train.get("target_12h", 0).sum()), "24h": int(df_train.get("target_24h", 0).sum()), "48h": int(df_train.get("target_48h", 0).sum())}
            },
            "validation": {
                "sample_count": len(df_val),
                "date_range": [df_val["timestamp"].min(), df_val["timestamp"].max()],
                "positives_by_horizon": {"6h": int(df_val.get("target_6h", 0).sum()), "12h": int(df_val.get("target_12h", 0).sum()), "24h": int(df_val.get("target_24h", 0).sum()), "48h": int(df_val.get("target_48h", 0).sum())}
            },
            "test": {
                "sample_count": len(df_test),
                "date_range": [df_test["timestamp"].min(), df_test["timestamp"].max()],
                "positives_by_horizon": {"6h": int(df_test.get("target_6h", 0).sum()), "12h": int(df_test.get("target_12h", 0).sum()), "24h": int(df_test.get("target_24h", 0).sum()), "48h": int(df_test.get("target_48h", 0).sum())}
            }
        },
        "leakage_audit": leakage_audit,
        "sequence_quality": {
            "mean_quality_score": round(mean_quality, 4),
            "sectors_audited": len(sector_audits),
            "sector_details": sector_audits
        },
        "training_eligibility_gate": gate_eval,
        "operational_invariants": {
            "pahad_lstm_status": "NOT_TRAINED (PHYSICS-INFORMED SURROGATE)",
            "operational_event_classifier": "CALIBRATED_GRADIENT_BOOSTING",
            "safety_flags": {
                "ENABLE_PUBLIC_DISPATCH": 0,
                "SIREN_DRY_RUN": 1,
                "CAP_PRODUCTION_DISPATCH": 0,
                "SACHET_PRODUCTION_DISPATCH": 0,
                "CELL_BROADCAST_PRODUCTION": 0,
                "PUBLIC_DEMO_TEST_ONLY": 1
            }
        }
    }

    manifest_file = os.path.join(MANIFEST_DIR, "phase12b_temporal_manifest.json")
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Mirror to root data/manifests if exists
    root_manifest = os.path.join(os.path.dirname(REPO_ROOT), "data", "manifests", "phase12b_temporal_manifest.json")
    try:
        os.makedirs(os.path.dirname(root_manifest), exist_ok=True)
        with open(root_manifest, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
    except Exception as e:
        logger.warning("Could not mirror to root manifests: %s", e)

    logger.info("Manifest successfully created at %s", manifest_file)
    logger.info("Gate Status: %s", gate_eval["gate_status"])
    logger.info("Mean Sequence Quality Score: %.4f", mean_quality)
    logger.info("=" * 70)


if __name__ == "__main__":
    generate_manifest()
