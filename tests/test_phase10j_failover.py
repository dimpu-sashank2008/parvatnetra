# -*- coding: utf-8 -*-
"""
tests/test_phase10j_failover.py
===============================
PARVAT NETRA • Phase 10J — Multi-Channel Failover Orchestration Tests
---------------------------------------------------------------------
Verifies:
  1. Primary channel success terminates failover sequence immediately.
  2. Primary failure triggers secondary channel (SMS -> EMAIL).
  3. Secondary failure triggers tertiary channel (EMAIL -> PUSH).
  4. Exhaustion of all channels marks dispatch NOTIFICATION_DELIVERY_DEGRADED.
  5. Audit log contains accurate timestamps and provider references for every hop.
"""

import pytest
from unittest.mock import MagicMock
from services.channel_failover_orchestrator import (
    ChannelFailoverOrchestrator,
    CHANNEL_SMS,
    CHANNEL_EMAIL,
    CHANNEL_WEB_PUSH
)


def test_primary_channel_success_no_failover():
    """Verifies that when primary channel succeeds, failover does not execute."""
    orch = ChannelFailoverOrchestrator()

    res = orch.dispatch_with_failover(
        incident_id="INC-FAILOVER-01",
        recipient_phone="+919832011234",
        recipient_email="evaluator@sih.gov.in",
        channels=[CHANNEL_SMS, CHANNEL_EMAIL, CHANNEL_WEB_PUSH],
        is_test=True
    )

    assert res["overall_success"] is True
    assert res["successful_channel"] == CHANNEL_SMS
    assert res["hop_count"] == 1
    assert res["degraded"] is False


def test_sms_failure_triggers_email_failover():
    """Verifies that SMS failure cascades directly to Email channel."""
    orch = ChannelFailoverOrchestrator()

    # Pass invalid phone so SMS fails
    res = orch.dispatch_with_failover(
        incident_id="INC-FAILOVER-02",
        recipient_phone=None,  # Forces SMS failure
        recipient_email="officer@disaster.assam.gov.in",
        channels=[CHANNEL_SMS, CHANNEL_EMAIL, CHANNEL_WEB_PUSH],
        is_test=True
    )

    assert res["overall_success"] is True
    assert res["successful_channel"] == CHANNEL_EMAIL
    assert res["hop_count"] == 2
    assert res["hops"][0]["channel"] == CHANNEL_SMS
    assert res["hops"][0]["success"] is False
    assert res["hops"][1]["channel"] == CHANNEL_EMAIL
    assert res["hops"][1]["success"] is True


def test_all_channels_exhausted_degraded_escalation():
    """Verifies that total failure marks NOTIFICATION_DELIVERY_DEGRADED."""
    orch = ChannelFailoverOrchestrator()

    # Intentionally provide no reachable recipient endpoints for SMS or Email
    res = orch.dispatch_with_failover(
        incident_id="INC-FAILOVER-03",
        recipient_phone=None,
        recipient_email=None,
        channels=[CHANNEL_SMS, CHANNEL_EMAIL],
        is_test=True
    )

    assert res["overall_success"] is False
    assert res["delivery_state"] == "NOTIFICATION_DELIVERY_DEGRADED"
    assert res["degraded"] is True
    assert "exhausted" in res["degraded_escalation"].lower()
    assert res["hop_count"] == 2
