# -*- coding: utf-8 -*-
"""
tests/test_siren_test_mode.py
=============================
Unit tests for acoustic siren safety locks, DRY_RUN default execution,
HMAC authorization gate, and audit logging.
"""

import sys
import os
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.test_siren import execute_siren_test


@pytest.fixture
def temp_db(tmp_path):
    return str(tmp_path / "test_siren.db")


def test_siren_default_dry_run(temp_db):
    res = execute_siren_test(
        siren_id="SIREN-TEST-01",
        corridor_id="CORR-NH10-SIKKIM-KM48",
        mode="DRY_RUN",
        duration_s=2.0,
        db_path=temp_db
    )
    assert res["mode"] == "DRY_RUN"
    assert res["hardware_actuated"] is False
    assert res["status"] == "COMPLETED_DRY_RUN"
    assert "Simulated acoustic test" in res["note"]


def test_siren_physical_test_auth_failure(temp_db):
    res = execute_siren_test(
        siren_id="SIREN-TEST-02",
        corridor_id="CORR-NH10-SIKKIM-KM48",
        mode="AUTHORIZED_PHYSICAL_TEST",
        duration_s=3.0,
        auth_token="UNAUTHORIZED_TOKEN",
        db_path=temp_db
    )
    assert res["mode"] == "AUTHORIZED_PHYSICAL_TEST"
    assert res["hardware_actuated"] is False
    assert res["status"] == "AUTH_FAILED"
    assert "rejected" in res["error"]


def test_siren_physical_test_hardware_disarmed_by_default(temp_db, monkeypatch):
    monkeypatch.delenv("SIREN_HARDWARE_ENABLED", raising=False)
    res = execute_siren_test(
        siren_id="SIREN-TEST-03",
        corridor_id="CORR-NH10-SIKKIM-KM48",
        mode="AUTHORIZED_PHYSICAL_TEST",
        duration_s=2.5,
        auth_token="SIH-NDMA-AUTH-2026",
        db_path=temp_db
    )
    assert res["status"] == "HARDWARE_DISARMED"
    assert res["hardware_actuated"] is False
    assert "Refused physical actuation" in res["note"]


def test_siren_physical_test_actuates_when_authorized_and_enabled(temp_db, monkeypatch):
    monkeypatch.setenv("SIREN_HARDWARE_ENABLED", "1")
    res = execute_siren_test(
        siren_id="SIREN-TEST-04",
        corridor_id="CORR-NH10-SIKKIM-KM48",
        mode="AUTHORIZED_PHYSICAL_TEST",
        duration_s=3.0,
        auth_token="SIH-NDMA-AUTH-2026",
        db_path=temp_db
    )
    assert res["status"] == "PHYSICAL_ACTIVATION_COMPLETE"
    assert res["hardware_actuated"] is True


def test_siren_duration_capped_at_5_seconds(temp_db):
    res = execute_siren_test(
        siren_id="SIREN-TEST-05",
        corridor_id="CORR-NH10-SIKKIM-KM48",
        mode="DRY_RUN",
        duration_s=45.0,  # Request excessive 45s
        db_path=temp_db
    )
    assert res["duration_seconds"] == 5.0  # Capped at 5.0 seconds


def test_siren_audit_log_persisted(temp_db):
    execute_siren_test(
        siren_id="SIREN-AUDIT-01",
        corridor_id="CORR-NH10-SIKKIM-KM48",
        mode="DRY_RUN",
        duration_s=2.0,
        db_path=temp_db
    )

    conn = sqlite3.connect(temp_db)
    cur = conn.cursor()
    cur.execute("SELECT siren_id, mode, status FROM siren_test_audit_log WHERE siren_id = ?", ("SIREN-AUDIT-01",))
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "SIREN-AUDIT-01"
    assert row[1] == "DRY_RUN"
    assert row[2] == "COMPLETED_DRY_RUN"
