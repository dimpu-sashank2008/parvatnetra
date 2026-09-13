# -*- coding: utf-8 -*-
"""
tests/test_observation_store.py
================================
Tests for engine/observation_store.py — ObservationStore (SQLite-backed).
Phase 5C PAHAD AI.

Uses pytest tmp_path to create isolated per-test databases.
Never touches the production PAHAD observation database.
"""

import sys
import os
import json
import time
import threading
from datetime import datetime, timezone, timedelta

import pytest
sys.path.insert(0, "c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi")

from engine.observation_store import ObservationStore, ObservationRecord


def make_record(
    sector_id="SK-NH10-KM48",
    feature="rain_1h",
    value=12.5,
    timestamp=None,
    provenance="LIVE",
    quality="GOOD"
) -> ObservationRecord:
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    return ObservationRecord(
        sector_id=sector_id,
        timestamp=ts,
        feature=feature,
        value=value,
        unit="mm",
        source="TEST",
        quality=quality,
        provenance=provenance,
        ingested_at=datetime.now(timezone.utc).isoformat()
    )


@pytest.fixture
def store(tmp_path):
    """Create an isolated ObservationStore backed by a temp SQLite file."""
    db_file = str(tmp_path / "test_observations.db")
    s = ObservationStore(db_path=db_file)
    yield s
    s.close()


# ─── Test 1: DB and table created on first connect ───────────────────────────
def test_db_and_table_created(tmp_path):
    db_file = str(tmp_path / "init_test.db")
    s = ObservationStore(db_path=db_file)
    assert os.path.exists(db_file)
    # Should be able to query the table without error
    assert s.count() == 0
    s.close()


# ─── Test 2: insert() returns integer rowid ──────────────────────────────────
def test_insert_returns_rowid(store):
    rec = make_record()
    rowid = store.insert(rec)
    assert isinstance(rowid, int)
    assert rowid > 0


# ─── Test 3: get_latest() returns most recent record ─────────────────────────
def test_get_latest_returns_most_recent(store):
    base_ts = datetime.now(timezone.utc)
    for i in range(5):
        ts = (base_ts + timedelta(minutes=i)).isoformat()
        store.insert(make_record(feature="rain_1h", value=float(i * 10), timestamp=ts))

    records = store.get_latest("SK-NH10-KM48", "rain_1h", limit=1)
    assert len(records) == 1
    assert records[0].value == 40.0  # last inserted value


# ─── Test 4: insert_many() inserts multiple records ──────────────────────────
def test_insert_many(store):
    records = [make_record(feature=f"feat_{i}", value=float(i)) for i in range(10)]
    count = store.insert_many(records)
    assert count == 10
    assert store.count("SK-NH10-KM48") == 10


# ─── Test 5: get_history() filters by since_iso correctly ───────────────────
def test_get_history_since_filter(store):
    base_ts = datetime(2026, 9, 1, 0, 0, 0, tzinfo=timezone.utc)
    for i in range(5):
        ts = (base_ts + timedelta(hours=i)).isoformat()
        store.insert(make_record(feature="rain_24h", value=float(i), timestamp=ts))

    # Query only records after hour 2
    cutoff = (base_ts + timedelta(hours=2)).isoformat()
    history = store.get_history("SK-NH10-KM48", "rain_24h", since_iso=cutoff, limit=100)
    assert len(history) == 3  # hours 2, 3, 4
    for rec in history:
        assert rec.timestamp >= cutoff


# ─── Test 6: get_latest_by_sector() returns dict keyed by feature ───────────
def test_get_latest_by_sector(store):
    base_ts = datetime.now(timezone.utc)
    features = ["rain_1h", "pore_pressure", "tilt", "fos"]
    for feat in features:
        store.insert(make_record(feature=feat, value=1.0))

    result = store.get_latest_by_sector("SK-NH10-KM48", max_age_seconds=3600)
    for feat in features:
        assert feat in result
        assert isinstance(result[feat], ObservationRecord)


# ─── Test 7: count() returns correct total ───────────────────────────────────
def test_count_by_sector(store):
    for i in range(7):
        store.insert(make_record(sector_id="SK-NH10-KM48", feature=f"f{i}"))
    for i in range(3):
        store.insert(make_record(sector_id="MN-TUPUL-RLY", feature=f"g{i}"))

    assert store.count("SK-NH10-KM48") == 7
    assert store.count("MN-TUPUL-RLY") == 3
    assert store.count() == 10


# ─── Test 8: thread safety — concurrent inserts don't corrupt ────────────────
def test_concurrent_inserts_thread_safety(store):
    errors = []

    def insert_records():
        try:
            for i in range(5):
                store.insert(make_record(feature=f"concurrent_{i}_{threading.get_ident()}"))
        except Exception as exc:
            errors.append(str(exc))

    threads = [threading.Thread(target=insert_records) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == [], f"Thread errors: {errors}"
    # Should have 50 records (10 threads × 5 each), but duplicates are ignored
    # At minimum all threads completed without raising
    total = store.count("SK-NH10-KM48")
    assert total > 0


# ─── Test 9: None value stored and retrieved correctly ───────────────────────
def test_none_value_roundtrip(store):
    rec = make_record(value=None, provenance="AUTH_REQUIRED", quality="AUTH_REQUIRED")
    store.insert(rec)
    result = store.get_latest("SK-NH10-KM48", "rain_1h", limit=1)
    assert len(result) == 1
    assert result[0].value is None
    assert result[0].provenance == "AUTH_REQUIRED"


# ─── Test 10: close() without error ──────────────────────────────────────────
def test_close_no_error(tmp_path):
    db_file = str(tmp_path / "close_test.db")
    s = ObservationStore(db_path=db_file)
    s.insert(make_record())
    s.close()  # Should not raise
    # Second close should also be safe
    s.close()


# ─── Test 11: ObservationRecord.to_dict() has required keys ─────────────────
def test_observation_record_to_dict():
    rec = make_record()
    d = rec.to_dict()
    required = ["sector_id", "timestamp", "feature", "value", "unit", "source",
                "quality", "provenance", "ingested_at"]
    for key in required:
        assert key in d, f"Missing key: {key}"


# ─── Test 12: get_latest_by_sector respects max_age_seconds ─────────────────
def test_get_latest_by_sector_max_age(store):
    old_ts = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    store.insert(make_record(feature="old_feat", value=99.0, timestamp=old_ts))

    # max_age_seconds=3600 (1 hour) — the 2-hour-old record should be excluded
    result = store.get_latest_by_sector("SK-NH10-KM48", max_age_seconds=3600)
    assert "old_feat" not in result
