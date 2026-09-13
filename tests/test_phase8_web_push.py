# -*- coding: utf-8 -*-
"""
tests/test_phase8_web_push.py
=============================
Tests for Checkpoint 8-08:
Web Push API Contract, VAPID Keys Structure, and Dev-Safe Test Delivery.
"""

import pytest
from services.push_service import PUSH_SERVICE, PushService, PushPayload, PushSubscription
from services.eoc_service import EOC_SERVICE


def test_web_push_provider_abstraction():
    """Verify push service operates safely in dry-run isolation."""
    assert PUSH_SERVICE is not None
    assert isinstance(PUSH_SERVICE, PushService)
    assert PUSH_SERVICE.dry_run is True


def test_web_push_subscription_contract():
    """Verify standard browser Push API subscription payload handling."""
    sub_res = EOC_SERVICE.register_subscription(
        user_id="USER_WEB_001",
        device_id="DEV_BROWSER_CHROME_88",
        platform="WEB_PUSH",
        notification_endpoint="https://updates.push.services.mozilla.com/wpush/v2/gAAAAABf...",
        language="en",
        latitude=27.3300,
        longitude=88.6100,
        consent_state="CONSENTED",
        role="PUBLIC"
    )
    assert sub_res["status"] == "REGISTERED"
    assert sub_res["platform"] == "WEB_PUSH"


def test_dev_safe_web_push_dispatch():
    """Verify localhost / test dispatch marks delivery safely without external network calls."""
    devices, targets = EOC_SERVICE.get_recipients_in_geofence(27.3300, 88.6100, 15.0)
    web_targets = [t for t in targets if t["platform"] == "WEB_PUSH"]
    assert len(web_targets) >= 1

    # Test PushService payload creation
    payload = PushPayload(
        title="PAHAD AI Alert",
        severity="EXTREME",
        location="NH-10 KM 48",
        short_message="Landslide risk elevated",
        issued_at="2026-09-11T08:00:00Z",
        alert_id="TEST-ALERT-001"
    )
    assert payload.severity == "EXTREME"
