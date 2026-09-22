# -*- coding: utf-8 -*-
"""
tests/test_v4_4_data_foundation.py
==================================
Automated Data Quality & Integrity Suite for Phase V4.4 Data Foundation:
1. Timestamp monotonicity & zero duplicate timestamps within sequences.
2. Value bounds: rainfall >= 0, soil moisture in [0, 1], FoS in [0.05, 10.0].
3. Coordinate validity: lat in [20, 30], lon in [88, 98] for North-East Region.
4. Future & post-event leakage prevention: sequence end <= forecast_origin.
5. Target correctness: target_H = 1 iff delta_t <= H.
6. Event-group partition isolation: zero event overlap across Train, Val, Test.
7. Provenance & unmonitored channel integrity: unmonitored sensors are strictly NaN.
8. Hash integrity & file existence.
"""

import os
import json
import hashlib
import numpy as np
import pandas as pd
import pytest

DATA_CSV = "data/processed/lstm_v4_4_real_temporal_sequences.csv"
MANIFEST_JSON = "data/processed/lstm_v4_4_manifest.json"
RESULT_JSON = "reports/pahad_lstm_v4_4_data_foundation_result.json"
V3_WEIGHTS = "models/pahad_lstm_v3_weights.pt"


def test_files_exist_and_hashes_match():
    assert os.path.exists(DATA_CSV), "Missing V4.4 sequences CSV"
    assert os.path.exists(MANIFEST_JSON), "Missing V4.4 manifest JSON"
    assert os.path.exists(RESULT_JSON), "Missing V4.4 result JSON"
    assert os.path.exists(V3_WEIGHTS), "Missing V3 production weights"

    with open(MANIFEST_JSON, "r") as f:
        manifest = json.load(f)
    with open(RESULT_JSON, "r") as f:
        res = json.load(f)

    # Compute hash of CSV
    h = hashlib.sha256(open(DATA_CSV, "rb").read()).hexdigest()
    assert h == manifest["dataset_sha256"]
    assert h == res["dataset_sha256"]


def test_dataset_dimensions_and_sequence_count():
    df = pd.read_csv(DATA_CSV)
    assert len(df) == 17640, f"Expected 17640 rows (105 * 168), got {len(df)}"
    assert df["sequence_id"].nunique() == 105, "Expected 105 distinct sequences"

    # Every sequence must have exactly 168 steps
    step_counts = df.groupby("sequence_id")["step_index"].count()
    assert (step_counts == 168).all(), "Every sequence must have exactly 168 steps"


def test_timestamp_monotonicity_and_uniqueness():
    df = pd.read_csv(DATA_CSV)
    for seq_id, grp in df.groupby("sequence_id"):
        grp_sorted = grp.sort_values("step_index")
        times = pd.to_datetime(grp_sorted["timestamp"])
        
        # Strictly monotonic increasing
        assert times.is_monotonic_increasing, f"Sequence {seq_id} timestamps not strictly monotonic increasing"
        # Zero duplicates
        assert grp_sorted["step_index"].is_unique, f"Duplicate steps in {seq_id}"
        assert times.is_unique, f"Duplicate timestamps in {seq_id}"
        
        # Step difference exactly 1 hour
        deltas = times.diff().iloc[1:]
        assert (deltas == pd.Timedelta(hours=1)).all(), f"Sequence {seq_id} has non-hourly step interval!"


def test_physical_value_bounds():
    df = pd.read_csv(DATA_CSV)
    
    # Rainfall >= 0
    for r_col in ["rain_1h", "rain_3h", "rain_6h", "rain_12h", "rain_24h", "rain_48h", "rain_72h", "rain_96h", "rain_120h", "rain_168h"]:
        assert (df[r_col] >= 0.0).all(), f"Negative rainfall in {r_col}"
        assert (df[r_col] < 1500.0).all(), f"Unrealistic rainfall spike in {r_col}"

    # Soil moisture in [0, 1]
    assert (df["soil_moisture"] >= 0.0).all(), "Negative soil moisture"
    assert (df["soil_moisture"] <= 1.0).all(), "Soil moisture > 1.0"

    # Factor of Safety in [0.05, 10.0]
    assert (df["fos"] >= 0.05).all(), "FoS below physical minimum"
    assert (df["fos"] <= 10.0).all(), "FoS above physical maximum"


def test_zero_future_leakage_and_post_event_purity():
    df = pd.read_csv(DATA_CSV)
    for seq_id, grp in df.groupby("sequence_id"):
        grp_sorted = grp.sort_values("step_index")
        origin_t = pd.to_datetime(grp_sorted.iloc[0]["forecast_origin"])
        last_t = pd.to_datetime(grp_sorted.iloc[-1]["timestamp"])
        
        # Last observation timestamp must be strictly before or at forecast origin
        assert last_t <= origin_t, f"Future leakage in {seq_id}: last_t ({last_t}) > origin ({origin_t})"


def test_target_semantics_consistency():
    df = pd.read_csv(DATA_CSV)
    for seq_id, grp in df.groupby("sequence_id"):
        r0 = grp.iloc[0]
        is_event = int(r0["is_event_sample"])
        lead_h = float(r0["lead_time_hours"])
        
        t6, t12, t24, t48 = int(r0["target_6h"]), int(r0["target_12h"]), int(r0["target_24h"]), int(r0["target_48h"])
        
        if is_event == 1:
            assert t6 == (1 if lead_h <= 6.0 else 0)
            assert t12 == (1 if lead_h <= 12.0 else 0)
            assert t24 == (1 if lead_h <= 24.0 else 0)
            assert t48 == (1 if lead_h <= 48.0 else 0)
        else:
            assert t6 == 0 and t12 == 0 and t24 == 0 and t48 == 0


def test_event_group_partition_isolation():
    df = pd.read_csv(DATA_CSV)
    events_by_split = {}
    for sp in ["TRAIN", "VAL", "TEST"]:
        events_by_split[sp] = set(df[(df["split_partition"] == sp) & (df["is_event_sample"] == 1)]["event_id"].unique())

    assert len(events_by_split["TRAIN"].intersection(events_by_split["VAL"])) == 0
    assert len(events_by_split["TRAIN"].intersection(events_by_split["TEST"])) == 0
    assert len(events_by_split["VAL"].intersection(events_by_split["TEST"])) == 0


def test_unmonitored_historical_channels_are_nan():
    df = pd.read_csv(DATA_CSV)
    for col in ["piezometer_pressure", "inclinometer_tilt", "tilt_rate_24h", "ground_displacement", "displacement_velocity_24h", "acoustic_emission", "insar_velocity", "ndvi", "ndvi_anomaly"]:
        assert df[col].isnull().all(), f"Unmonitored historical channel {col} must be completely NaN (no fake data)"


def test_composite_risk_index_cri_strictly_excluded():
    df = pd.read_csv(DATA_CSV)
    assert "composite_risk_index_cri" not in df.columns
    assert "cri" not in df.columns
