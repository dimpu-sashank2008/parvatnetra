# -*- coding: utf-8 -*-
"""
tests/test_notification_delivery.py
===================================
Unit tests for multi-channel notification dispatch tracking, recipient logging,
and receipt acknowledgement records.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.notification_orchestrator import (
    NotificationOrchestrator,
    CHANNELS
)


@pytest.fixture
def temp_orchestrator(tmp_path):
    db_file = str(tmp_path / "test_delivery.db")
    return NotificationOrchestrator(db_path=db_file)


def test_channels_authoritative_support(temp_orchestrator):
    assert "SMS" in CHANNELS
    assert "PUSH" in CHANNELS
    assert "CAP" in CHANNELS
    assert "WEB" in CHANNELS
    assert "MOBILE" in CHANNELS
    assert "LOCAL_GATEWAY" in CHANNELS
    assert "SIREN" in CHANNELS


def test_multi_channel_dispatch_tracking(temp_orchestrator):
    cap = temp_orchestrator.generate_cap_alert(
        alert_id="ALERT-DELIV-001",
        event="Slope Failure Warning",
        severity="High",
        urgency="Immediate",
        certainty="Observed",
        area_description="Km 48 Teesta Gorge",
        instruction="Evacuate"
    )

    res = temp_orchestrator.dispatch_alert(
        alert_id="ALERT-DELIV-001",
        cap_payload=cap,
        channels=["PUSH", "WEB", "MOBILE", "LOCAL_GATEWAY"]
    )
    assert len(res["channel_results"]) == 4

    notifs = temp_orchestrator.list_notifications(alert_id="ALERT-DELIV-001")
    assert len(notifs) == 4
    channels_logged = {n["channel"] for n in notifs}
    assert channels_logged == {"PUSH", "WEB", "MOBILE", "LOCAL_GATEWAY"}


def test_acknowledgement_receipt_recording(temp_orchestrator):
    cap = temp_orchestrator.generate_cap_alert(
        alert_id="ALERT-ACK-001",
        event="Rockfall Alert",
        severity="Moderate",
        urgency="Expected",
        certainty="Possible",
        area_description="Singtam Cut",
        instruction="Caution"
    )

    res = temp_orchestrator.dispatch_alert(
        alert_id="ALERT-ACK-001",
        cap_payload=cap,
        channels=["MOBILE"]
    )
    notif_id = res["channel_results"]["MOBILE"]["notification_id"]

    # Record acknowledgement
    ack = temp_orchestrator.record_acknowledgement(
        notification_id=notif_id,
        acknowledged_by="BRO_CONVOY_COMMANDER_01"
    )
    assert ack["notification_id"] == notif_id
    assert ack["acknowledged_by"] == "BRO_CONVOY_COMMANDER_01"
    assert ack["acknowledged_at"] is not None


def test_acknowledgement_nonexistent_notification_raises_keyerror(temp_orchestrator):
    with pytest.raises(KeyError):
        temp_orchestrator.record_acknowledgement(
            notification_id="NOTIF-NONEXISTENT",
            acknowledged_by="UNKNOWN"
        )
