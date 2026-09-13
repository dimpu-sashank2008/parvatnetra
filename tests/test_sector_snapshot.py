# -*- coding: utf-8 -*-
"""
tests/test_sector_snapshot.py
==============================
Tests for engine/sector_snapshot.py — SectorSnapshotBuilder.
Phase 5C PAHAD AI.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, "c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi")

from engine.sector_snapshot import (
    SectorSnapshotBuilder, SectorSnapshot,
    SECTOR_REGISTRY, PHASE5B_FEATURE_COLUMNS
)
from engine.observation_store import ObservationRecord
from datetime import datetime, timezone


def _make_obs_record(feature: str, value: float = 1.0) -> ObservationRecord:
    return ObservationRecord(
        sector_id="SK-NH10-KM48",
        timestamp=datetime.now(timezone.utc).isoformat(),
        feature=feature,
        value=value,
        unit="mm",
        source="TEST",
        quality="GOOD",
        provenance="LIVE",
        ingested_at=datetime.now(timezone.utc).isoformat()
    )


# ─── Test 1: SectorSnapshot.to_dict() has all required keys ──────────────────
def test_snapshot_to_dict_required_keys():
    builder = SectorSnapshotBuilder()
    with patch("engine.sector_snapshot.GLOBAL_OBSERVATION_STORE") as mock_store:
        mock_store.get_latest_by_sector.return_value = {}
        snap = builder.build("SK-NH10-KM48")

    d = snap.to_dict()
    required = ["sector_id", "features", "feature_completeness",
                "provenance_summary", "freshness_by_modality",
                "data_quality_score", "missing_features"]
    for key in required:
        assert key in d, f"Missing key: {key}"


# ─── Test 2: Unknown sector_id falls back to default coords ──────────────────
def test_unknown_sector_uses_default_coords():
    builder = SectorSnapshotBuilder()
    with patch("engine.sector_snapshot.GLOBAL_OBSERVATION_STORE") as mock_store:
        mock_store.get_latest_by_sector.return_value = {}
        snap = builder.build("UNKNOWN-SECTOR-ID")

    # Should not raise; should have default lat/lon
    assert snap.latitude is not None
    assert snap.longitude is not None
    assert isinstance(snap.latitude, float)


# ─── Test 3: feature_completeness is 0.0 when store is empty ────────────────
def test_feature_completeness_zero_when_empty():
    builder = SectorSnapshotBuilder()
    with patch("engine.sector_snapshot.GLOBAL_OBSERVATION_STORE") as mock_store:
        mock_store.get_latest_by_sector.return_value = {}
        snap = builder.build("SK-NH10-KM48")

    assert snap.feature_completeness == 0.0
    assert len(snap.missing_features) == len(PHASE5B_FEATURE_COLUMNS)


# ─── Test 4: feature_completeness is 1.0 when all 26 features present ────────
def test_feature_completeness_one_when_all_present():
    builder = SectorSnapshotBuilder()
    full_obs = {feat: _make_obs_record(feat, value=1.0) for feat in PHASE5B_FEATURE_COLUMNS}
    with patch("engine.sector_snapshot.GLOBAL_OBSERVATION_STORE") as mock_store:
        mock_store.get_latest_by_sector.return_value = full_obs
        snap = builder.build("SK-NH10-KM48")

    assert snap.feature_completeness == 1.0
    assert snap.missing_features == []


# ─── Test 5: missing_features contains absent features exactly ───────────────
def test_missing_features_list_correct():
    builder = SectorSnapshotBuilder()
    # Only provide 3 features
    partial_obs = {
        "rain_1h": _make_obs_record("rain_1h", 5.0),
        "fos": _make_obs_record("fos", 1.2),
        "slope": _make_obs_record("slope", 35.0),
    }
    with patch("engine.sector_snapshot.GLOBAL_OBSERVATION_STORE") as mock_store:
        mock_store.get_latest_by_sector.return_value = partial_obs
        snap = builder.build("SK-NH10-KM48")

    expected_missing = [f for f in PHASE5B_FEATURE_COLUMNS
                        if f not in partial_obs]
    assert set(snap.missing_features) == set(expected_missing)
    assert snap.feature_completeness == pytest.approx(3 / len(PHASE5B_FEATURE_COLUMNS), abs=1e-4)


# ─── Test 6: provenance_summary contains MISSING count ───────────────────────
def test_provenance_summary_contains_missing_count():
    builder = SectorSnapshotBuilder()
    with patch("engine.sector_snapshot.GLOBAL_OBSERVATION_STORE") as mock_store:
        mock_store.get_latest_by_sector.return_value = {}
        snap = builder.build("SK-NH10-KM48")

    assert "MISSING" in snap.provenance_summary
    missing_count = len(PHASE5B_FEATURE_COLUMNS)
    assert str(missing_count) in snap.provenance_summary


# ─── Test 7: data_quality_score is float between 0.0 and 1.0 ────────────────
def test_data_quality_score_bounds():
    builder = SectorSnapshotBuilder()
    with patch("engine.sector_snapshot.GLOBAL_OBSERVATION_STORE") as mock_store:
        mock_store.get_latest_by_sector.return_value = {}
        snap = builder.build("SK-NH10-KM48")

    assert isinstance(snap.data_quality_score, float)
    assert 0.0 <= snap.data_quality_score <= 1.0


# ─── Test 8: build_all() returns dict keyed by sector_id ────────────────────
def test_build_all_returns_dict():
    builder = SectorSnapshotBuilder()
    with patch("engine.sector_snapshot.GLOBAL_OBSERVATION_STORE") as mock_store:
        mock_store.get_latest_by_sector.return_value = {}
        result = builder.build_all()

    assert isinstance(result, dict)
    assert len(result) >= len(SECTOR_REGISTRY)
    for sid in SECTOR_REGISTRY:
        assert sid in result
        assert isinstance(result[sid], SectorSnapshot)


# ─── Test 9: Sector registry has minimum expected sectors ────────────────────
def test_sector_registry_completeness():
    expected = [
        "SK-NH10-KM48", "MN-TUPUL-RLY", "MZ-MELTHUM-QRY",
        "AS-HAFLONG-RLY", "ML-MAWSYNRAM"
    ]
    for sid in expected:
        assert sid in SECTOR_REGISTRY, f"Expected sector {sid} in SECTOR_REGISTRY"


# ─── Test 10: PHASE5B_FEATURE_COLUMNS has exactly 26 features ────────────────
def test_phase5b_feature_columns_count():
    assert len(PHASE5B_FEATURE_COLUMNS) == 26, (
        f"Expected 26 feature columns, got {len(PHASE5B_FEATURE_COLUMNS)}"
    )


# ─── Test 11: snapshot_time is set in ISO format ─────────────────────────────
def test_snapshot_time_is_iso():
    builder = SectorSnapshotBuilder()
    with patch("engine.sector_snapshot.GLOBAL_OBSERVATION_STORE") as mock_store:
        mock_store.get_latest_by_sector.return_value = {}
        snap = builder.build("SK-NH10-KM48")

    assert snap.snapshot_time
    # Should parse without exception
    dt = datetime.fromisoformat(snap.snapshot_time.replace("Z", "+00:00"))
    assert dt is not None
