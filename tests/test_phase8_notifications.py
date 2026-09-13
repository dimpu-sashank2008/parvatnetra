# -*- coding: utf-8 -*-
"""
tests/test_phase8_notifications.py
==================================
Tests for Checkpoint 8-07 & 8-13:
Subscription Registry, Channel Fan-out, and Independent Channel State Tracking.
"""

import pytest
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_NEW, STATE_AUTHORIZED
from services.eoc_service import EOC_SERVICE


def test_subscription_registry():
    """Verify registration and querying of subscriptions across platforms."""
    # Register 1 Web Push and 1 Mobile Push subscriber within geofence
    sub1 = EOC_SERVICE.register_subscription(
        user_id="CITIZEN_01",
        device_id="DEV_CHROME_01",
        platform="WEB_PUSH",
        notification_endpoint="https://fcm.googleapis.com/fcm/send/sub1",
        language="ne",
        latitude=27.3300,
        longitude=88.6100,
        consent_state="CONSENTED",
        role="PUBLIC"
    )
    assert sub1["status"] == "REGISTERED"

    sub2 = EOC_SERVICE.register_subscription(
        user_id="CITIZEN_02",
        device_id="DEV_FLUTTER_02",
        platform="MOBILE_PUSH",
        notification_endpoint="https://fcm.googleapis.com/fcm/send/sub2",
        language="hi",
        latitude=27.3310,
        longitude=88.6120,
        consent_state="CONSENTED",
        role="PUBLIC"
    )
    assert sub2["status"] == "REGISTERED"

    devices, targets = EOC_SERVICE.get_recipients_in_geofence(27.3300, 88.6100, radius_km=15.0)
    assert "DEV_CHROME_01" in devices
    assert "DEV_FLUTTER_02" in devices


def test_multi_channel_fanout_and_independent_states():
    """Verify single authorized incident fans out to channels with independent status."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=88.0,
        risk_band="CRITICAL",
        model_probability=0.91,
        FoS=0.92,
        rainfall=190.0
    )
    # Transition to AUTHORIZED
    EOC_INCIDENT_MANAGER.transition_state(inc.incident_id, STATE_AUTHORIZED, "DISTRICT_AUTHORITY", "DM_01", force=True)

    disp = EOC_SERVICE.dispatch_incident_notifications(
        incident_id=inc.incident_id,
        authorization_token="AUTH_TOKEN_TEST",
        channels=["WEB", "MOBILE", "SMS", "CAP", "EOC_SIREN"],
        test_mode=True
    )

    assert disp["status"] == "DISPATCHED"
    channels = disp["channels"]

    # Channel 1: WEB
    assert "WEB" in channels
    assert channels["WEB"]["status"] in ("SENT", "QUEUED")

    # Channel 2: MOBILE
    assert "MOBILE" in channels
    assert channels["MOBILE"]["status"] in ("SENT", "QUEUED")
    assert "payload_contract" in channels["MOBILE"]

    # Channel 3: SMS - Strictly SIMULATED, never DELIVERED
    assert "SMS" in channels
    assert channels["SMS"]["status"] == "SIMULATED"
    assert channels["SMS"]["status"] != "DELIVERED"
    assert "[SIMULATED SMS]" in channels["SMS"]["badge"]

    # Channel 4: CAP
    assert "CAP" in channels
    assert channels["CAP"]["status"] == "GENERATED"
    assert "[TEST / DRY_RUN]" in channels["CAP"]["badge"]

    # Channel 5: SIREN
    assert "SIREN" in channels
    assert channels["SIREN"]["status"] == "DRY_RUN"
    assert "[SIREN_DRY_RUN_LOCKED]" in channels["SIREN"]["badge"]
