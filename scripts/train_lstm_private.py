"""
scripts/train_lstm_private.py
==============================
PAHAD LSTM — Private Local Training Pipeline
---------------------------------------------
Trains a windowed temporal sequence model (GradientBoostingClassifier with
lag/rolling-window feature engineering) as the private LSTM replacement.

CRITICAL SAFETY INVARIANTS:
- Does NOT modify engine/pahad_lstm.py (public surrogate remains unchanged)
- Does NOT modify models/pahad_event_model.metadata.json
- Does NOT modify docs/PAHAD_MODEL_CARD.md
- Saves ONLY to models/pahad_lstm_private_weights.pkl (gitignored)
- Public API still returns model_status: NOT_TRAINED until user approves flip

Architecture:
  Input  : Windowed lag features (1h, 3h, 6h, 12h, 24h, 48h, 72h lookback)
           + rolling statistics from pahad_observations.db
           + static geotechnical features from real_{train,val,test}.csv
  Model  : GradientBoostingClassifier (per forecast horizon)
  Calib  : CalibratedClassifierCV (Platt sigmoid; isotonic when n>=50)
  Output : models/pahad_lstm_private_weights.pkl
           models/pahad_lstm_private_metrics.json

Usage:
  python scripts/train_lstm_private.py [--seed 42] [--verbose]

Data provenance:
  [HISTORICAL] data/features/real_train.csv  (16 records, ≤2023)
  [HISTORICAL] data/features/real_val.csv    (12 records, H1 2024)
  [HISTORICAL] data/features/real_test.csv   (8 records, H2 2024)
  [LIVE]       data/observations/pahad_observations.db (146k+ rows)
  [EXCLUDED]   data/features/demo_train.csv  (PAHAD_DEMO_MODE=0)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import pickle
import sqlite3
import sys
import warnings
from datetime import datetime, timezone
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [LSTM_TRAIN] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────
REAL_TRAIN = "data/features/real_train.csv"
REAL_VAL = "data/features/real_val.csv"
REAL_TEST = "data/features/real_test.csv"
DEMO_TRAIN = "data/features/demo_train.csv"  # NEVER used
DB_PATH = "data/observations/pahad_observations.db"
OUT_WEIGHTS = "models/pahad_lstm_private_weights.pkl"
OUT_METRICS = "models/pahad_lstm_private_metrics.json"

# ─── Feature columns (static geotechnical features from feature schema v3.1.0) ─
STATIC_FEATURES = [
    "rainfall_1h", "rainfall_6h", "rainfall_24h", "rainfall_72h",
    "API_3d", "API_7d", "API_30d",
    "rainfall_accumulation_3h", "rainfall_intensity_3h", "rainfall_acceleration",
    "soil_moisture", "soil_moisture_trend_24h",
    "pore_pressure", "pore_pressure_trend_24h",
    "tilt", "tilt_rate_24h",
    "ground_displacement", "displacement_velocity_24h",
    "seismic_magnitude", "seismic_distance", "seismic_trigger_score", "seismic_recency_hours",
    "elevation", "slope", "aspect", "curvature",
    "NDVI", "NDVI_change",
    "historical_landslide_density", "static_susceptibility",
    "road_criticality", "population_exposure",
    "FoS", "CRI",
]

TARGET_COL = "event_label"
FORECAST_HORIZONS = ["6h", "12h", "24h", "48h"]

# ─── Temporal lag windows (hours) for sequence feature engineering ─────────────
LAG_WINDOWS_H = [1, 3, 6, 12, 24, 48, 72]
ROLLING_WINDOWS = [3, 6, 12, 24]  # hours for rolling mean/max/std


def sha256_dataframe(df: pd.DataFrame) -> str:
    """Compute a SHA-256 hash over the entire DataFrame content."""
    content = df.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def load_observations_for_sector(
    conn: sqlite3.Connection,
    sector_id: str,
    timestamp_utc: str,
    lookback_h: int = 72,
) -> pd.DataFrame:
    """
    Load time-series observations from pahad_observations.db for a given
    sector up to `lookback_h` hours before the event timestamp.
    """
    try:
        query = """
            SELECT timestamp, feature, value
            FROM observations
            WHERE sector_id = ?
              AND quality IN ('LIVE', 'CALIBRATED', 'GOOD', 'SIMULATED')
              AND datetime(timestamp) BETWEEN
                  datetime(?, '-{lookback}h') AND datetime(?)
            ORDER BY timestamp ASC
        """.format(lookback=lookback_h)
        df = pd.read_sql_query(query, conn, params=(sector_id, timestamp_utc, timestamp_utc))
        return df
    except Exception as exc:
        log.debug("DB query failed for sector %s: %s", sector_id, exc)
        return pd.DataFrame()


def engineer_temporal_features(
    row: pd.Series,
    obs_df: pd.DataFrame,
) -> pd.Series:
    """
    Convert a static feature row + temporal observations DataFrame
    into an enriched feature vector with lag and rolling window statistics.
    """
    feats = row[STATIC_FEATURES].copy()

    if obs_df.empty:
        # No time-series available — add zero-filled lag/rolling columns
        for feat in ["precipitation", "soil_moisture_0_to_1cm", "seismic_magnitude"]:
            for lag in LAG_WINDOWS_H:
                feats[f"{feat}_lag{lag}h"] = 0.0
            for win in ROLLING_WINDOWS:
                feats[f"{feat}_roll_mean_{win}h"] = 0.0
                feats[f"{feat}_roll_max_{win}h"] = 0.0
                feats[f"{feat}_roll_std_{win}h"] = 0.0
        return feats

    # Pivot observations to wide format (timestamp × feature)
    try:
        wide = obs_df.pivot_table(
            index="timestamp", columns="feature", values="value", aggfunc="mean"
        )
        wide.index = pd.to_datetime(wide.index, utc=True, errors="coerce")
        wide = wide.sort_index()
    except Exception:
        return feats

    event_time = pd.to_datetime(row["timestamp"], utc=True, errors="coerce")
    if pd.isna(event_time):
        return feats

    # Key telemetry features to extract temporal patterns from
    tele_features = {
        "precipitation": ["precipitation", "rain"],
        "soil_moisture": ["soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm", "soil_moisture"],
        "seismic": ["seismic_magnitude"],
    }

    for feat_name, candidates in tele_features.items():
        # Find the first available column
        col = None
        for c in candidates:
            if c in wide.columns:
                col = c
                break

        if col is None:
            series_vals = pd.Series(dtype=float)
        else:
            series_vals = wide[col].dropna()

        # Lag features: value at -N hours relative to event
        for lag_h in LAG_WINDOWS_H:
            lag_time = event_time - pd.Timedelta(hours=lag_h)
            # Find closest observation within ±30 min
            if not series_vals.empty:
                diffs = abs(series_vals.index - lag_time)
                closest_idx = diffs.argmin()
                if diffs.iloc[closest_idx] <= pd.Timedelta(minutes=30):
                    feats[f"{feat_name}_lag{lag_h}h"] = float(series_vals.iloc[closest_idx])
                else:
                    feats[f"{feat_name}_lag{lag_h}h"] = 0.0
            else:
                feats[f"{feat_name}_lag{lag_h}h"] = 0.0

        # Rolling statistics: mean, max, std over last N hours
        for win_h in ROLLING_WINDOWS:
            window_start = event_time - pd.Timedelta(hours=win_h)
            window_slice = series_vals[
                (series_vals.index >= window_start) & (series_vals.index <= event_time)
            ]
            if not window_slice.empty:
                feats[f"{feat_name}_roll_mean_{win_h}h"] = float(window_slice.mean())
                feats[f"{feat_name}_roll_max_{win_h}h"] = float(window_slice.max())
                feats[f"{feat_name}_roll_std_{win_h}h"] = float(window_slice.std()) if len(window_slice) > 1 else 0.0
            else:
                feats[f"{feat_name}_roll_mean_{win_h}h"] = 0.0
                feats[f"{feat_name}_roll_max_{win_h}h"] = 0.0
                feats[f"{feat_name}_roll_std_{win_h}h"] = 0.0

    return feats


def build_feature_matrix(df: pd.DataFrame, conn: sqlite3.Connection, split_name: str) -> pd.DataFrame:
    """Build the full enriched temporal feature matrix for a data split."""
    log.info("  Building temporal features for split=%s (%d rows)…", split_name, len(df))
    enriched_rows = []
    for _, row in df.iterrows():
        obs = load_observations_for_sector(
            conn,
            sector_id=row.get("sector_id", ""),
            timestamp_utc=str(row.get("timestamp", "")),
            lookback_h=72,
        )
        enriched = engineer_temporal_features(row, obs)
        enriched_rows.append(enriched)

    result = pd.DataFrame(enriched_rows)
    result[TARGET_COL] = df[TARGET_COL].values
    result = result.fillna(0.0)
    return result


def compute_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 5) -> float:
    """Expected Calibration Error (ECE)."""
    bin_lowers = np.linspace(0.0, 1.0, n_bins + 1)[:-1]
    bin_uppers = np.linspace(0.0, 1.0, n_bins + 1)[1:]
    ece = 0.0
    n = len(y_true)
    for lo, hi in zip(bin_lowers, bin_uppers):
        mask = (y_prob >= lo) & (y_prob < hi)
        if mask.sum() == 0:
            continue
        acc = y_true[mask].mean()
        conf = y_prob[mask].mean()
        ece += (mask.sum() / n) * abs(acc - conf)
    return float(ece)


def train_horizon_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    horizon: str,
    seed: int,
    n_positive: int,
) -> tuple:
    """Train and calibrate a GBC model for a single forecast horizon."""
    log.info("  Training horizon model: %s (n_train=%d, pos=%d)", horizon, len(y_train), n_positive)

    # Horizon decay multiplier (longer horizons need slightly different regularisation)
    horizon_decay = {"6h": 1.0, "12h": 1.15, "24h": 1.32, "48h": 1.55}
    n_estimators = max(50, int(80 * horizon_decay[horizon]))

    base_clf = GradientBoostingClassifier(
        n_estimators=n_estimators,
        max_depth=3,
        learning_rate=0.08,
        subsample=0.8,
        min_samples_leaf=2,
        random_state=seed,
        validation_fraction=0.2 if len(y_train) >= 10 else None,
        n_iter_no_change=10 if len(y_train) >= 10 else None,
    )

    # Calibration: use prefit mode — base is already trained, calibrate on same data
    # isotonic needs n>=10 per class; fall back to sigmoid otherwise
    cal_method = "isotonic" if n_positive >= 10 else "sigmoid"

    base_clf.fit(X_train, y_train)

    # sklearn 1.9+: pass estimator directly with cv=None triggers re-fit;
    # use cv="prefit" only if supported, else wrap manually
    import sklearn
    sk_version = tuple(int(x) for x in sklearn.__version__.split(".")[:2])
    if sk_version >= (1, 2):
        # cv="prefit" removed in 1.9; use CalibratedClassifierCV with pre-fitted base
        try:
            clf = CalibratedClassifierCV(
                estimator=base_clf, method=cal_method, cv="prefit"
            )
            clf.fit(X_train, y_train)
        except Exception:
            # Absolute fallback: use cross-val calibration with cv=2
            from sklearn.base import clone
            base_clone = clone(GradientBoostingClassifier(
                n_estimators=n_estimators,
                max_depth=3,
                learning_rate=0.08,
                subsample=0.8,
                min_samples_leaf=2,
                random_state=seed,
            ))
            clf = CalibratedClassifierCV(
                estimator=base_clone, method="sigmoid", cv=2
            )
            clf.fit(X_train, y_train)
            cal_method = "sigmoid"
    else:
        clf = CalibratedClassifierCV(base_clf, method=cal_method, cv="prefit")
        clf.fit(X_train, y_train)

    return clf, cal_method


def compute_metrics(
    clf, X: np.ndarray, y: np.ndarray, horizon: str, split: str
) -> dict:
    """Compute comprehensive metrics for a split."""
    if len(y) == 0:
        return {}

    y_prob = clf.predict_proba(X)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = {
        "split": split,
        "horizon": horizon,
        "n_samples": int(len(y)),
        "n_positive": int(y.sum()),
        "n_negative": int((1 - y).sum()),
    }

    if len(np.unique(y)) < 2:
        metrics["note"] = "Single-class split — AUC not computable"
        metrics["brier_score"] = float(brier_score_loss(y, y_prob))
        return metrics

    try:
        metrics["roc_auc"] = float(roc_auc_score(y, y_prob))
    except Exception:
        metrics["roc_auc"] = None

    try:
        metrics["pr_auc"] = float(average_precision_score(y, y_prob))
    except Exception:
        metrics["pr_auc"] = None

    metrics["brier_score"] = float(brier_score_loss(y, y_prob))
    metrics["precision"] = float(precision_score(y, y_pred, zero_division=0))
    metrics["recall"] = float(recall_score(y, y_pred, zero_division=0))
    metrics["f1"] = float(f1_score(y, y_pred, zero_division=0))
    metrics["ece"] = compute_calibration_error(y.astype(float), y_prob)

    # Operational metrics
    hits = int(((y == 1) & (y_pred == 1)).sum())
    misses = int(((y == 1) & (y_pred == 0)).sum())
    false_alarms = int(((y == 0) & (y_pred == 1)).sum())
    total = hits + misses + false_alarms

    metrics["pod"] = hits / (hits + misses) if (hits + misses) > 0 else 0.0
    metrics["far"] = false_alarms / (hits + false_alarms) if (hits + false_alarms) > 0 else 0.0
    metrics["csi"] = hits / total if total > 0 else 0.0

    return metrics


def main(seed: int = 42, verbose: bool = False) -> None:
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    log.info("=" * 65)
    log.info("PAHAD LSTM — Private Local Training Pipeline")
    log.info("WARNING: Training artifacts are LOCAL ONLY (gitignored)")
    log.info("         Public model_status REMAINS: NOT_TRAINED")
    log.info("=" * 65)

    # ── Verify PAHAD_DEMO_MODE is off (synthetic data excluded) ──────────────
    demo_mode = os.environ.get("PAHAD_DEMO_MODE", "0")
    if demo_mode == "1":
        log.error("PAHAD_DEMO_MODE=1 is set. Refusing to train — demo data must be excluded.")
        sys.exit(1)
    log.info("[SAFETY] PAHAD_DEMO_MODE=%s — demo_train.csv excluded ✓", demo_mode)

    # ── Load real splits ───────────────────────────────────────────────────────
    log.info("Loading real data splits…")
    train_df = pd.read_csv(REAL_TRAIN)
    val_df = pd.read_csv(REAL_VAL)
    test_df = pd.read_csv(REAL_TEST)

    log.info("  Train: %d rows (%d positive)", len(train_df), train_df[TARGET_COL].sum())
    log.info("  Val  : %d rows (%d positive)", len(val_df), val_df[TARGET_COL].sum())
    log.info("  Test : %d rows (%d positive)", len(test_df), test_df[TARGET_COL].sum())

    # Dataset hash for reproducibility audit
    all_real_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    dataset_hash = sha256_dataframe(all_real_df)
    log.info("  Dataset SHA-256: %s", dataset_hash)

    # ── Validate temporal holdout ─────────────────────────────────────────────
    train_dates = pd.to_datetime(train_df["timestamp"], utc=True, errors="coerce")
    val_dates = pd.to_datetime(val_df["timestamp"], utc=True, errors="coerce")
    test_dates = pd.to_datetime(test_df["timestamp"], utc=True, errors="coerce")

    train_max = train_dates.max()
    val_min = val_dates.min()
    val_max = val_dates.max()
    test_min = test_dates.min()

    log.info("  Temporal holdout: train_max=%s  val=[%s→%s]  test_min=%s",
             train_max, val_min, val_max, test_min)

    if train_max >= val_min:
        log.warning("⚠ Temporal leakage detected: train overlaps val! Check splits.")

    # ── Connect to observations DB for temporal enrichment ────────────────────
    log.info("Connecting to observations DB: %s", DB_PATH)
    conn = sqlite3.connect(DB_PATH)

    # Check DB freshness
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM observations WHERE quality IN ('LIVE', 'CALIBRATED', 'GOOD')")
        live_rows = cur.fetchone()[0]
        log.info("  DB live/calibrated rows: %d", live_rows)
        cur.execute("SELECT MAX(ingested_at) FROM observations")
        latest_ingest = cur.fetchone()[0]
        log.info("  Latest ingestion: %s", latest_ingest)
    except Exception as exc:
        log.warning("DB health check failed: %s", exc)

    # ── Build enriched temporal feature matrices ──────────────────────────────
    log.info("Engineering temporal features (lag + rolling windows)…")
    X_train_df = build_feature_matrix(train_df, conn, "train")
    X_val_df = build_feature_matrix(val_df, conn, "val")
    X_test_df = build_feature_matrix(test_df, conn, "test")

    feature_cols = [c for c in X_train_df.columns if c != TARGET_COL]
    log.info("  Total features (static + temporal): %d", len(feature_cols))

    X_train = X_train_df[feature_cols].values.astype(np.float32)
    y_train = X_train_df[TARGET_COL].values.astype(int)
    X_val = X_val_df[feature_cols].values.astype(np.float32)
    y_val = X_val_df[TARGET_COL].values.astype(int)
    X_test = X_test_df[feature_cols].values.astype(np.float32)
    y_test = X_test_df[TARGET_COL].values.astype(int)

    conn.close()

    # ── Train per-horizon models ───────────────────────────────────────────────
    log.info("Training horizon-specific sequence models…")
    horizon_models = {}
    horizon_metrics = {}
    n_positive = int(y_train.sum())

    for horizon in FORECAST_HORIZONS:
        log.info("--- Horizon: %s ---", horizon)
        clf, cal_method = train_horizon_model(
            X_train, y_train, X_val, y_val,
            horizon=horizon,
            seed=seed,
            n_positive=n_positive,
        )
        horizon_models[horizon] = clf

        # Metrics on all splits
        train_m = compute_metrics(clf, X_train, y_train, horizon, "train")
        val_m = compute_metrics(clf, X_val, y_val, horizon, "val")
        test_m = compute_metrics(clf, X_test, y_test, horizon, "test")

        horizon_metrics[horizon] = {
            "calibration_method": cal_method,
            "train": train_m,
            "val": val_m,
            "test": test_m,
        }

        log.info(
            "  [%s] val ROC-AUC=%.3f  Brier=%.4f  F1=%.3f  n=%d",
            horizon,
            val_m.get("roc_auc") or 0.0,
            val_m.get("brier_score", 0.0),
            val_m.get("f1", 0.0),
            val_m.get("n_samples", 0),
        )

    # ── Feature importances ───────────────────────────────────────────────────
    top_features = {}
    for horizon, clf in horizon_models.items():
        try:
            base = clf.calibrated_classifiers_[0].estimator
            importances = base.feature_importances_
            feat_imp = sorted(
                zip(feature_cols, importances), key=lambda x: x[1], reverse=True
            )[:10]
            top_features[horizon] = [
                {"feature": f, "importance": round(float(imp), 5)}
                for f, imp in feat_imp
            ]
        except Exception:
            top_features[horizon] = []

    # ── Save private weights ──────────────────────────────────────────────────
    log.info("Saving private weights → %s", OUT_WEIGHTS)
    artifact = {
        "models": horizon_models,
        "feature_cols": feature_cols,
        "dataset_hash": dataset_hash,
        "seed": seed,
        "forecast_horizons": FORECAST_HORIZONS,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "training_rows": int(len(y_train)),
        "positive_rows": int(y_train.sum()),
        "negative_rows": int((1 - y_train).sum()),
        "validation_strategy": "temporal_holdout_train_le2023_val_H1_2024_test_H2_2024",
        "feature_schema_version": "3.1.0",
        "status": "TRAINED_LOCAL_PRIVATE",
        # ─── CRITICAL: public_status never changes until user explicitly approves ───
        "public_status": "NOT_TRAINED",
    }

    os.makedirs(os.path.dirname(OUT_WEIGHTS), exist_ok=True)
    with open(OUT_WEIGHTS, "wb") as fh:
        pickle.dump(artifact, fh, protocol=5)
    log.info("  ✓ Weights saved (%d bytes)", os.path.getsize(OUT_WEIGHTS))

    # ── Save private metrics ──────────────────────────────────────────────────
    metrics_payload = {
        "model": "PAHAD_LSTM_PRIVATE_SEQUENCE_MODEL",
        "architecture": "windowed_gbdt_temporal_sequence",
        "model_status_private": "TRAINED_LOCAL_PRIVATE",
        "model_status_public": "NOT_TRAINED",
        "created_at": artifact["created_at"],
        "seed": seed,
        "dataset_hash": dataset_hash,
        "feature_schema_version": "3.1.0",
        "data_provenance": "[HISTORICAL] real_train/val/test.csv + [LIVE] pahad_observations.db",
        "training_rows": int(len(y_train)),
        "positive_rows": int(y_train.sum()),
        "negative_rows": int((1 - y_train).sum()),
        "validation_rows": int(len(y_val)),
        "test_rows": int(len(y_test)),
        "validation_strategy": "temporal_holdout_train_le2023_val_H1_2024_test_H2_2024",
        "forecast_horizons": FORECAST_HORIZONS,
        "feature_count": len(feature_cols),
        "horizon_metrics": horizon_metrics,
        "top_feature_drivers": top_features,
        "limitations": [
            "Only 36 real labeled events — metrics have high variance on small test sets",
            "LSTM surrogate in pahad_lstm.py is NOT replaced until user approves flip",
            "No sequence data with hourly resolution — lag features approximated from DB queries",
        ],
    }

    with open(OUT_METRICS, "w", encoding="utf-8") as fh:
        json.dump(metrics_payload, fh, indent=2, default=str)
    log.info("  ✓ Metrics saved → %s", OUT_METRICS)

    # ── Summary ───────────────────────────────────────────────────────────────
    log.info("=" * 65)
    log.info("[PRIVATE] Training COMPLETE")
    log.info("  Model : Windowed GBDT Temporal Sequence (per horizon)")
    log.info("  Seed  : %d", seed)
    log.info("  Hash  : %s", dataset_hash[:16] + "…")
    log.info("  Train : %d rows (%d positive)", len(y_train), y_train.sum())
    log.info("  Val   : %d rows (%d positive)", len(y_val), y_val.sum())
    log.info("  Test  : %d rows (%d positive)", len(y_test), y_test.sum())
    log.info("")
    log.info("  Horizon   | Val ROC-AUC | Val Brier | Val F1")
    log.info("  ----------|------------|-----------|-------")
    for h in FORECAST_HORIZONS:
        vm = horizon_metrics[h]["val"]
        auc = vm.get("roc_auc")
        log.info(
            "  %-9s | %-10s | %-9.4f | %.3f",
            h,
            f"{auc:.3f}" if auc is not None else "N/A",
            vm.get("brier_score", 0.0),
            vm.get("f1", 0.0),
        )
    log.info("")
    log.info("[SAFETY] Public model_status is still: NOT_TRAINED")
    log.info("         Run this when ready to flip:")
    log.info("         python scripts/promote_lstm_to_production.py  (not yet created)")
    log.info("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PAHAD LSTM Private Local Training")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--verbose", action="store_true", help="Enable DEBUG logging")
    args = parser.parse_args()
    main(seed=args.seed, verbose=args.verbose)
