# -*- coding: utf-8 -*-
"""
tests/test_freshness.py
========================
Tests for engine/data_freshness.py — DataFreshnessEngine.
Phase 5C PAHAD AI.
"""

import sys
import time
import pytest
sys.path.insert(0, "c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi")

from engine.data_freshness import (
    DataFreshnessEngine,
    FreshnessRecord,
    FRESH, AGING, STALE, UNAVAILABLE,
    DEFAULT_TTL_SECONDS, AGING_RATIO
)


@pytest.fixture
def engine():
    """Fresh engine instance for each test."""
    return DataFreshnessEngine()


# ─── Test 1: FRESH when age < 75% of TTL ─────────────────────────────────────
def test_fresh_status_young_data(engine):
    ttl = DEFAULT_TTL_SECONDS.get("imd", 900)
    # Set last_updated to 10% of TTL ago — should be FRESH
    epoch = time.time() - (ttl * 0.10)
    fr = engine.get_freshness("imd", last_updated_epoch=epoch)
    assert fr.status == FRESH
    assert fr.confidence_penalty == 0.0


# ─── Test 2: AGING when 75% <= age < 100% of TTL ────────────────────────────
def test_aging_status_middle_age(engine):
    ttl = DEFAULT_TTL_SECONDS.get("imd", 900)
    # Set last_updated to 80% of TTL ago — should be AGING
    epoch = time.time() - (ttl * 0.80)
    fr = engine.get_freshness("imd", last_updated_epoch=epoch)
    assert fr.status == AGING
    assert 0.0 < fr.confidence_penalty <= 0.3


# ─── Test 3: STALE when age >= TTL ──────────────────────────────────────────
def test_stale_status_expired_data(engine):
    ttl = DEFAULT_TTL_SECONDS.get("ncs", 300)
    # Set last_updated to 110% of TTL ago — should be STALE
    epoch = time.time() - (ttl * 1.10)
    fr = engine.get_freshness("ncs", last_updated_epoch=epoch)
    assert fr.status == STALE
    assert fr.confidence_penalty == 0.5


# ─── Test 4: UNAVAILABLE when no record exists ───────────────────────────────
def test_unavailable_when_no_record(engine):
    fr = engine.get_freshness("satellite")  # No update recorded
    assert fr.status == UNAVAILABLE
    assert fr.age_seconds is None
    assert fr.confidence_penalty == 1.0


# ─── Test 5: confidence_penalty is 0.0 for FRESH ─────────────────────────────
def test_no_penalty_for_fresh(engine):
    ttl = DEFAULT_TTL_SECONDS.get("iot", 120)
    epoch = time.time() - (ttl * 0.50)  # Half TTL
    fr = engine.get_freshness("iot", last_updated_epoch=epoch)
    assert fr.status == FRESH
    assert fr.confidence_penalty == 0.0


# ─── Test 6: confidence_penalty between 0 and 0.3 for AGING ─────────────────
def test_penalty_bounds_for_aging(engine):
    ttl = DEFAULT_TTL_SECONDS.get("weather", 900)
    epoch = time.time() - (ttl * 0.85)
    fr = engine.get_freshness("weather", last_updated_epoch=epoch)
    assert fr.status == AGING
    assert 0.0 < fr.confidence_penalty <= 0.3


# ─── Test 7: confidence_penalty is exactly 0.5 for STALE ────────────────────
def test_penalty_is_half_for_stale(engine):
    ttl = DEFAULT_TTL_SECONDS.get("usgs", 300)
    epoch = time.time() - (ttl * 1.5)
    fr = engine.get_freshness("usgs", last_updated_epoch=epoch)
    assert fr.status == STALE
    assert fr.confidence_penalty == 0.5


# ─── Test 8: aggregate penalty returns float 0–1 ─────────────────────────────
def test_aggregate_penalty_is_float_0_to_1(engine):
    # Record some updates to mix FRESH and UNAVAILABLE
    engine.record_update("imd")
    penalty = engine.compute_aggregate_confidence_penalty(["imd", "satellite", "ncs"])
    assert isinstance(penalty, float)
    assert 0.0 <= penalty <= 1.0


# ─── Test 9: get_summary returns dict of strings ─────────────────────────────
def test_get_summary_returns_string_values(engine):
    summary = engine.get_summary()
    assert isinstance(summary, dict)
    assert len(summary) > 0
    for k, v in summary.items():
        assert isinstance(k, str)
        assert v in (FRESH, AGING, STALE, UNAVAILABLE)


# ─── Test 10: record_update causes FRESH ─────────────────────────────────────
def test_record_update_causes_fresh(engine):
    engine.record_update("iot")
    fr = engine.get_freshness("iot")
    assert fr.status == FRESH
    assert fr.age_seconds is not None
    assert fr.age_seconds < 2.0  # Should be essentially 0 seconds


# ─── Test 11: FreshnessRecord.to_dict has required keys ─────────────────────
def test_freshness_record_to_dict(engine):
    fr = engine.get_freshness("ncs")
    d = fr.to_dict()
    assert "modality" in d
    assert "status" in d
    assert "confidence_penalty" in d
    assert "ttl_seconds" in d


# ─── Test 12: UNAVAILABLE when age >= 3x TTL ─────────────────────────────────
def test_unavailable_when_very_old(engine):
    ttl = DEFAULT_TTL_SECONDS.get("imd", 900)
    epoch = time.time() - (ttl * 4)  # 4x TTL ago
    fr = engine.get_freshness("imd", last_updated_epoch=epoch)
    assert fr.status == UNAVAILABLE
    assert fr.confidence_penalty == 1.0
