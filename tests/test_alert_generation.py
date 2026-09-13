# -*- coding: utf-8 -*-
"""
tests/test_alert_generation.py
==============================
Unit tests for OASIS CAP v1.2 alert payload generation and public safety gate enforcement.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.notification_orchestrator import (
    NotificationOrchestrator,
    STATUS_DELIVERED,
    STATUS_SUPPRESSED
)


@pytest.fixture
def temp_orchestrator(tmp_path):
    db_file = str(tmp_path / "test_notif.db")
    return NotificationOrchestrator(db_path=db_file)


def test_generate_cap_v1_2_payload(temp_orchestrator):
    cap = temp_orchestrator.generate_cap_alert(
        alert_id="ALERT-CAP-001",
        event="Imminent Hillslope Failure",
        severity="Extreme",
        urgency="Immediate",
        certainty="Observed",
        area_description="NH-10 Km 48 Teesta Gorge (Pakyong District)",
        instruction="Suspend vehicular traffic immediately. Divert to NH-717A."
    )
    assert cap["identifier"] == "ALERT-CAP-001"
    assert cap["status"] == "Actual"
    assert cap["msgType"] == "Alert"
    assert cap["info"]["category"] == "Geo"
    assert cap["info"]["severity"] == "Extreme"
    assert cap["info"]["urgency"] == "Immediate"
    assert "NH-10 Km 48" in cap["info"]["area"]["areaDesc"]


def test_public_dispatch_safety_gate_suppressed_by_default(temp_orchestrator, monkeypatch):
    monkeypatch.setenv("PUBLIC_DISPATCH", "DISABLED")
    cap = temp_orchestrator.generate_cap_alert(
        alert_id="ALERT-GATE-001",
        event="Debris Flow",
        severity="Severe",
        urgency="Expected",
        certainty="Likely",
        area_description="Tupul Railway Cut",
        instruction="Hold trains"
    )

    res = temp_orchestrator.dispatch_alert(
        alert_id="ALERT-GATE-001",
        cap_payload=cap,
        channels=["SMS", "SIREN", "CAP", "MOBILE", "WEB"]
    )

    # Public channels MUST be suppressed by default
    assert res["channel_results"]["SMS"]["status"] == STATUS_SUPPRESSED
    assert res["channel_results"]["SIREN"]["status"] == STATUS_SUPPRESSED
    assert res["channel_results"]["CAP"]["status"] == STATUS_SUPPRESSED

    # Internal operational channels are delivered to on-duty responders
    assert res["channel_results"]["MOBILE"]["status"] == STATUS_DELIVERED
    assert res["channel_results"]["WEB"]["status"] == STATUS_DELIVERED


def test_public_dispatch_delivered_when_authorized_and_enabled(temp_orchestrator, monkeypatch):
    monkeypatch.setenv("PUBLIC_DISPATCH", "ENABLED")
    cap = temp_orchestrator.generate_cap_alert(
        alert_id="ALERT-AUTH-001",
        event="Active Shear Slip",
        severity="Extreme",
        urgency="Immediate",
        certainty="Observed",
        area_description="Melthum Quarry",
        instruction="Evacuate downslope residences"
    )

    res = temp_orchestrator.dispatch_alert(
        alert_id="ALERT-AUTH-001",
        cap_payload=cap,
        channels=["SMS", "SIREN", "CAP"],
        authorization_token="NDMA-AUTH-SECURE-2026"
    )

    assert res["channel_results"]["SMS"]["status"] == STATUS_DELIVERED
    assert res["channel_results"]["SIREN"]["status"] == STATUS_DELIVERED
    assert res["channel_results"]["CAP"]["status"] == STATUS_DELIVERED
