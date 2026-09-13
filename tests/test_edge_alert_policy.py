# -*- coding: utf-8 -*-
"""
tests/test_edge_alert_policy.py
===============================
Unit tests for Autonomous Edge Corridor Safety & Local Alert Policy (Phase 6A).
Validates:
  - Deterministic physical hazard thresholds (pore pressure, tilt rate, shear velocity, rain intensity)
  - Severity classification: NORMAL, WARNING, CRITICAL
  - Autonomous siren recommendation logic (1 CRITICAL or 2 WARNING signals)
  - Edge alert event persistence to local store
"""

import os
import tempfile
import sqlite3
import pytest

from engine.edge_alert_policy import EdgeAlertPolicy, CORRIDOR_THRESHOLDS


@pytest.fixture
def alert_policy():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_alerts.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS edge_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL,
                gateway_id TEXT NOT NULL,
                sector_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                trigger_source TEXT NOT NULL,
                details_json TEXT,
                siren_activated INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

        policy = EdgeAlertPolicy(db_path=db_path)
        yield policy


def test_normal_sensor_readings(alert_policy):
    measurements = {
        "pore_pressure": 12.0,       # Normal (< 30 kPa)
        "tilt_rate": 0.2,           # Normal (< 1.0 deg/day)
        "rain_intensity": 10.0      # Normal (< 35 mm/hr)
    }
    res = alert_policy.evaluate_reading(measurements, sector_id="SK-NH10-KM48")
    assert res["severity"] == "NORMAL"
    assert res["siren_trigger_recommended"] is False
    assert res["bypass_recommended"] is False
    assert res["alert_record"] is None


def test_single_warning_reading(alert_policy):
    measurements = {
        "pore_pressure": 35.0,  # Warning (>= 30 kPa, < 45 kPa)
        "tilt_rate": 0.3        # Normal
    }
    res = alert_policy.evaluate_reading(measurements, sector_id="SK-NH10-KM48")
    assert res["severity"] == "WARNING"
    # Single warning does NOT immediately sound siren (prevents false alarms)
    assert res["siren_trigger_recommended"] is False
    assert len(res["warning_signals"]) == 1
    assert res["alert_record"] is not None


def test_dual_warning_triggers_siren(alert_policy):
    # Two converging warning signals (pore pressure + rainfall)
    measurements = {
        "pore_pressure": 32.0,   # Warning
        "rain_intensity": 40.0   # Warning (>= 35 mm/hr, < 50 mm/hr)
    }
    res = alert_policy.evaluate_reading(measurements, sector_id="SK-NH10-KM48")
    assert res["severity"] == "CRITICAL"
    assert res["siren_trigger_recommended"] is True
    assert res["bypass_recommended"] is True
    assert len(res["warning_signals"]) == 2


def test_single_critical_triggers_siren(alert_policy):
    # One acute critical signal (pore pressure >= 45 kPa)
    measurements = {
        "pore_pressure": 48.5,
        "tilt_rate": 0.1
    }
    res = alert_policy.evaluate_reading(measurements, sector_id="SK-NH10-KM48")
    assert res["severity"] == "CRITICAL"
    assert res["siren_trigger_recommended"] is True
    assert len(res["critical_signals"]) == 1


def test_edge_alert_persistence(alert_policy):
    measurements = {"pore_pressure": 50.0}
    res = alert_policy.evaluate_reading(measurements, sector_id="SK-NH10-KM48", gateway_id="GW-TEST-01")

    assert res["alert_record"] is not None
    alert_id = res["alert_record"]["alert_id"]

    conn = sqlite3.connect(alert_policy.db_path)
    cur = conn.cursor()
    cur.execute("SELECT severity, siren_activated FROM edge_alerts WHERE alert_id = ?", (alert_id,))
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "CRITICAL"
    assert row[1] == 1  # Siren activated flag recorded
