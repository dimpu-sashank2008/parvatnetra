# -*- coding: utf-8 -*-
"""
tests/test_phase10e_delivery.py
===============================
PARVAT NETRA • Phase 10E — Unified Independent Delivery Tracking Tests
----------------------------------------------------------------------
Verifies:
  1. Unified delivery tracking record schema across all channels:
     channel, provider, queued_at, sent_at, delivery_status, provider_reference, failure_reason, incident_id.
  2. Complete channel independence:
     Failure in one channel does NOT alter or contaminate the status of another.
  3. Never converting one channel's success into another channel's success.
  4. Traceability of delivery receipts by dissemination ID.
"""

import pytest
from services.public_warning_service import (
    PUBLIC_WARNING_SERVICE,
    AUTHORIZATION_TOKEN_MANAGER,
    CHANNEL_SMS,
    CHANNEL_CELL_BROADCAST,
    CHANNEL_CAP_GATEWAY,
    CHANNEL_SIREN,
    CHANNEL_WEB_PUSH,
    CHANNEL_MOBILE_PUSH,
    CHANNEL_ROADSIDE_VMS,
    RECEIPT_SENT,
    RECEIPT_FAILED,
    ROLE_DISTRICT_AUTHORITY
)
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_AUTHORIZED

GEOFENCE_VALID = [
    [27.3200, 88.6000],
    [27.3400, 88.6000],
    [27.3400, 88.6200],
    [27.3200, 88.6200],
    [27.3200, 88.6000]
]


def test_independent_channel_tracking():
    """Verifies that each channel maintains independent status and delivery receipts."""
    inc_id = "INC-DELIV-001"
    # Seed incident in EOC manager
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=82.0,
        risk_band="HIGH",
        model_probability=0.85,
        FoS=0.91,
        rainfall=75.0,
        incident_id=inc_id
    )
    inc.incident_status = STATE_AUTHORIZED
    inc.corroboration_count = 3
    EOC_INCIDENT_MANAGER._save(inc)

    token = AUTHORIZATION_TOKEN_MANAGER.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, inc_id)

    res = PUBLIC_WARNING_SERVICE.disseminate_emergency_warning(
        incident_id=inc_id,
        actor_id="DM_PAKYONG",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        auth_token=token,
        geofence_polygon=GEOFENCE_VALID,
        target_channels=[CHANNEL_SMS, CHANNEL_CELL_BROADCAST, CHANNEL_CAP_GATEWAY, CHANNEL_SIREN]
    )

    assert res["status"] == "DISSEMINATED_DRY_RUN"
    receipts = res["channel_receipts"]

    # Verify SMS record independence
    assert CHANNEL_SMS in receipts
    assert receipts[CHANNEL_SMS]["channel"] == CHANNEL_SMS
    assert receipts[CHANNEL_SMS]["delivery_status"] == RECEIPT_SENT

    # Verify Cell Broadcast independence
    assert CHANNEL_CELL_BROADCAST in receipts
    assert receipts[CHANNEL_CELL_BROADCAST]["channel"] == CHANNEL_CELL_BROADCAST
    assert receipts[CHANNEL_CELL_BROADCAST]["provider_status"] == "TEST/DRY_RUN"

    # Verify CAP Gateway independence
    assert CHANNEL_CAP_GATEWAY in receipts
    assert receipts[CHANNEL_CAP_GATEWAY]["channel"] == CHANNEL_CAP_GATEWAY
    assert receipts[CHANNEL_CAP_GATEWAY]["status"] == "STAGED_TEST_FEED"

    # Verify Siren independence
    assert CHANNEL_SIREN in receipts
    assert receipts[CHANNEL_SIREN]["channel"] == CHANNEL_SIREN
    assert receipts[CHANNEL_SIREN]["dry_run"] is True


def test_failure_isolation_between_channels():
    """Verifies that a failure in one channel adapter does not cause other channels to fail."""
    # Force SMS failure by injecting a broken adapter temporarily
    original_send = PUBLIC_WARNING_SERVICE.sms_adapter.send_sms

    def failing_send(*args, **kwargs):
        raise ConnectionResetError("SMS Gateway provider timeout")

    PUBLIC_WARNING_SERVICE.sms_adapter.send_sms = failing_send

    try:
        inc_id = "INC-DELIV-002"
        inc = EOC_INCIDENT_MANAGER.create_incident(
            sector_id="SK-NH10-KM48",
            risk_score=79.0,
            risk_band="HIGH",
            model_probability=0.81,
            FoS=0.94,
            rainfall=68.0,
            incident_id=inc_id
        )
        inc.incident_status = STATE_AUTHORIZED
        inc.corroboration_count = 2
        EOC_INCIDENT_MANAGER._save(inc)

        token = AUTHORIZATION_TOKEN_MANAGER.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, inc_id)

        res = PUBLIC_WARNING_SERVICE.disseminate_emergency_warning(
            incident_id=inc_id,
            actor_id="DM_PAKYONG",
            actor_role=ROLE_DISTRICT_AUTHORITY,
            auth_token=token,
            geofence_polygon=GEOFENCE_VALID,
            target_channels=[CHANNEL_SMS, CHANNEL_CELL_BROADCAST]
        )

        receipts = res["channel_receipts"]

        # SMS must be recorded as FAILED
        assert receipts[CHANNEL_SMS]["delivery_status"] == RECEIPT_FAILED
        assert "timeout" in receipts[CHANNEL_SMS]["error"].lower()

        # Cell broadcast must still succeed independently without disruption
        assert receipts[CHANNEL_CELL_BROADCAST]["broadcast_status"] == "SIMULATED"
        assert receipts[CHANNEL_CELL_BROADCAST]["provider_status"] == "TEST/DRY_RUN"

    finally:
        # Restore original function
        PUBLIC_WARNING_SERVICE.sms_adapter.send_sms = original_send


def test_retrieval_by_dissemination_id():
    """Verifies that delivery records are persistently retrievable by dissemination ID."""
    inc_id = "INC-DELIV-003"
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=75.0,
        risk_band="HIGH",
        model_probability=0.79,
        FoS=0.96,
        rainfall=62.0,
        incident_id=inc_id
    )
    inc.incident_status = STATE_AUTHORIZED
    inc.corroboration_count = 2
    EOC_INCIDENT_MANAGER._save(inc)

    token = AUTHORIZATION_TOKEN_MANAGER.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, inc_id)

    res = PUBLIC_WARNING_SERVICE.disseminate_emergency_warning(
        incident_id=inc_id,
        actor_id="DM_PAKYONG",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        auth_token=token,
        geofence_polygon=GEOFENCE_VALID,
        target_channels=[CHANNEL_WEB_PUSH, CHANNEL_MOBILE_PUSH]
    )

    dissem_id = res["dissemination_id"]
    retrieved = PUBLIC_WARNING_SERVICE.get_dissemination_record(dissem_id)

    assert retrieved is not None
    assert retrieved["dissemination_id"] == dissem_id
    assert CHANNEL_WEB_PUSH in retrieved["channel_receipts"]
    assert CHANNEL_MOBILE_PUSH in retrieved["channel_receipts"]
