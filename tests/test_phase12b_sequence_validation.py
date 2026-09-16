# -*- coding: utf-8 -*-
"""
tests/test_phase12b_sequence_validation.py
===========================================
PARVAT NETRA • PAHAD AI — Phase 12B Sequence Engine & Gap Classification Tests
"""

import os
import pytest
import pandas as pd
from datetime import datetime, timezone

from engine.pahad_temporal_engine import (
    normalize_timestamp_utc,
    classify_time_gap,
    ProvenanceType,
    GapSeverity,
    CANONICAL_FEATURES,
    SequenceValidator,
    TemporalLeakageDetector,
)


def test_normalize_timestamp_utc():
    """Verify timestamp normalization across various ISO string formats and datetimes."""
    dt1 = normalize_timestamp_utc("2023-10-03T19:30:00Z")
    assert dt1.tzinfo == timezone.utc
    assert dt1.year == 2023 and dt1.month == 10 and dt1.day == 3

    dt2 = normalize_timestamp_utc("2023-10-03T19:30:00+00:00")
    assert dt2 == dt1

    naive = datetime(2023, 10, 3, 19, 30, 0)
    dt3 = normalize_timestamp_utc(naive)
    assert dt3.tzinfo == timezone.utc
    assert dt3 == dt1

    with pytest.raises(ValueError):
        normalize_timestamp_utc("")
    with pytest.raises(ValueError):
        normalize_timestamp_utc("invalid-date-xyz")


def test_classify_time_gap():
    """Verify classification of time gaps according to geotechnical tolerances."""
    assert classify_time_gap(3600.0, 3600.0) == GapSeverity.NO_GAP
    assert classify_time_gap(3900.0, 3600.0) == GapSeverity.NO_GAP
    assert classify_time_gap(5400.0, 3600.0) == GapSeverity.MINOR_GAP
    assert classify_time_gap(14400.0, 3600.0) == GapSeverity.MODERATE_GAP
    assert classify_time_gap(43200.0, 3600.0) == GapSeverity.CRITICAL_GAP
    assert classify_time_gap(100000.0, 3600.0) == GapSeverity.DISCONNECTED


def test_sequence_validator_synthetic_scenarios():
    """Verify SequenceValidator behavior on synthetic valid, out-of-order, and duplicate sequences."""
    df_valid = pd.DataFrame({
        "timestamp": [
            "2023-10-01T00:00:00Z",
            "2023-10-01T01:00:00Z",
            "2023-10-01T02:00:00Z",
            "2023-10-01T03:00:00Z",
        ],
        "rain_1h": [0.0, 5.2, 12.4, 8.1],
        "fos": [1.45, 1.32, 1.15, 1.08],
        "provenance": ["REAL", "REAL", "REAL", "REAL"],
    })
    res_valid = SequenceValidator.validate_sequence(df_valid, expected_cadence_hours=1.0)
    assert res_valid["valid"] is True
    assert res_valid["out_of_order_count"] == 0
    assert res_valid["exact_duplicates"] == 0
    assert res_valid["gap_classification"]["NO_GAP"] == 3
    assert res_valid["quality_score"] > 0.80

    df_ooo = pd.DataFrame({
        "timestamp": [
            "2023-10-01T00:00:00Z",
            "2023-10-01T03:00:00Z",
            "2023-10-01T01:00:00Z",
        ],
        "provenance": ["REAL", "REAL", "REAL"],
    })
    res_ooo = SequenceValidator.validate_sequence(df_ooo)
    assert res_ooo["valid"] is False
    assert res_ooo["out_of_order_count"] >= 1

    df_dup = pd.DataFrame({
        "timestamp": [
            "2023-10-01T00:00:00Z",
            "2023-10-01T01:00:00Z",
            "2023-10-01T01:00:00Z",
        ],
        "provenance": ["REAL", "REAL", "REAL"],
    })
    res_dup = SequenceValidator.validate_sequence(df_dup)
    assert res_dup["valid"] is False
    assert res_dup["exact_duplicates"] >= 1


def test_sequence_validator_historical_master_dataset():
    """Audit all 17 historical corridors in the repository master dataset."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "processed", "phase5b_temporal_full.csv")
    if not os.path.exists(data_path):
        pytest.skip("phase5b_temporal_full.csv not found, skipping historical check")

    df_master = pd.read_csv(data_path)
    corridors = df_master["sector_id"].unique()
    assert len(corridors) == 17

    for sector in corridors:
        df_sec = df_master[df_master["sector_id"] == sector].sort_values("timestamp")
        res = SequenceValidator.validate_sequence(df_sec)
        assert res["valid"] is True, f"Corridor {sector} has sequence integrity failure"
        assert res["out_of_order_count"] == 0, f"Corridor {sector} has out-of-order timestamps"
        assert res["exact_duplicates"] == 0, f"Corridor {sector} has duplicate timestamps"
        assert res["missing_feature_rate"] == 0.0, f"Corridor {sector} has unexpected missing features"
        assert res["quality_score"] < 0.85


def test_temporal_leakage_detector_partitions():
    """Verify that Train, Val, and Test partitions have zero temporal or identifier leakage."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    train_path = os.path.join(base_dir, "data", "processed", "phase5b_temporal_train.csv")
    val_path = os.path.join(base_dir, "data", "processed", "phase5b_temporal_val.csv")
    test_path = os.path.join(base_dir, "data", "processed", "phase5b_temporal_test.csv")

    if not (os.path.exists(train_path) and os.path.exists(val_path) and os.path.exists(test_path)):
        pytest.skip("Split datasets missing, skipping leakage audit")

    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)

    audit = TemporalLeakageDetector.audit_partitions(df_train, df_val, df_test)
    assert audit["zero_leakage_verified"] is True
    assert audit["temporal_holdout_respected"] is True
    assert audit["sample_id_overlap_count"] == 0
    assert audit["target_cri_leakage_detected"] is False
