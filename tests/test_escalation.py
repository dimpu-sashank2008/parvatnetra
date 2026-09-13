# -*- coding: utf-8 -*-
"""
tests/test_escalation.py
========================
Unit tests for timeout-driven alert acknowledgement escalation and
multi-tier authority chain routing.
"""

import sys
import os
import time
import pytest
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.escalation_engine import EscalationEngine
from services.notification_orchestrator import NotificationOrchestrator


@pytest.fixture
def temp_engines(tmp_path):
    db_file = str(tmp_path / "test_escalation.db")
    notif_orch = NotificationOrchestrator(db_path=db_file)
    esc_engine = EscalationEngine(db_path=db_file)
    return notif_orch, esc_engine


def test_manual_escalation_tier_progression(temp_engines):
    _, esc_engine = temp_engines

    # Escalation from FIELD_OPERATOR -> DISTRICT_AUTHORITY
    e1 = esc_engine.manual_escalate("ALERT-01", "FIELD_OPERATOR", "Field unit radio silence")
    assert e1["from_tier"] == "FIELD_OPERATOR"
    assert e1["to_tier"] == "DISTRICT_AUTHORITY"

    # Escalation from DISTRICT_AUTHORITY -> STATE_AUTHORITY
    e2 = esc_engine.manual_escalate("ALERT-01", "DISTRICT_AUTHORITY", "Inter-district highway severing imminent")
    assert e2["from_tier"] == "DISTRICT_AUTHORITY"
    assert e2["to_tier"] == "STATE_AUTHORITY"


def test_unacknowledged_timeout_escalation(temp_engines, monkeypatch):
    notif_orch, esc_engine = temp_engines
    monkeypatch.setattr("services.escalation_engine.NOTIFICATION_ORCHESTRATOR", notif_orch)

    cap = notif_orch.generate_cap_alert(
        alert_id="ALERT-ESC-01",
        event="Rapid Creep",
        severity="High",
        urgency="Immediate",
        certainty="Likely",
        area_description="Km 48",
        instruction="Hold"
    )

    # Dispatch notification
    dispatched = notif_orch.dispatch_alert(
        alert_id="ALERT-ESC-01",
        cap_payload=cap,
        channels=["MOBILE"]
    )
    notif_id = dispatched["channel_results"]["MOBILE"]["notification_id"]

    # Check timeout with 0s threshold to trigger immediately
    escalated = esc_engine.check_and_escalate_unacknowledged(timeout_seconds=0)
    assert len(escalated) >= 1
    assert any(e["notification_id"] == notif_id for e in escalated)
    assert escalated[0]["to_tier"] == "DISTRICT_AUTHORITY"


def test_acknowledged_notification_is_not_escalated(temp_engines, monkeypatch):
    notif_orch, esc_engine = temp_engines
    monkeypatch.setattr("services.escalation_engine.NOTIFICATION_ORCHESTRATOR", notif_orch)

    cap = notif_orch.generate_cap_alert(
        alert_id="ALERT-ESC-02",
        event="Rapid Creep",
        severity="High",
        urgency="Immediate",
        certainty="Likely",
        area_description="Km 48",
        instruction="Hold"
    )

    dispatched = notif_orch.dispatch_alert(
        alert_id="ALERT-ESC-02",
        cap_payload=cap,
        channels=["MOBILE"]
    )
    notif_id = dispatched["channel_results"]["MOBILE"]["notification_id"]

    # Acknowledge immediately
    notif_orch.record_acknowledgement(notif_id, "RESPONDER_01")

    # Check escalation with 0s threshold - must NOT escalate because it is acknowledged!
    escalated = esc_engine.check_and_escalate_unacknowledged(timeout_seconds=0)
    assert not any(e["notification_id"] == notif_id for e in escalated)
