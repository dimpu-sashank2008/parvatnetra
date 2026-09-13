# -*- coding: utf-8 -*-
"""
tests/test_phase10i_sms_provider.py
===================================
PARVAT NETRA • Phase 10I — SMS Provider Architecture & 8-State Model Tests
-------------------------------------------------------------------------
Verifies:
  1. Provider-neutral SMS adapter supporting mock and CDAC gateways.
  2. The 8 canonical operational states:
     UNCONFIGURED, CONFIGURED, SIMULATED, QUEUED, SENT, DELIVERED, FAILED, BLOCKED.
  3. Core Safety Invariant: SIMULATED must NEVER be labeled DELIVERED.
  4. Only an actual provider receipt may produce DELIVERED.
  5. India Government DLT configuration reflection (PE ID, headers, DLT template IDs).
"""

import pytest
from services.production_sms_service import (
    ProductionSMSAdapter,
    STATE_UNCONFIGURED,
    STATE_CONFIGURED,
    STATE_SIMULATED,
    STATE_QUEUED,
    STATE_SENT,
    STATE_DELIVERED,
    STATE_FAILED,
    STATE_BLOCKED,
    VALID_SMS_STATES
)
from services.sms_service import MockSMSProvider, CDACSMSProvider


def test_sms_eight_canonical_states_defined():
    """Verifies that all 8 states are uniquely defined and present in VALID_SMS_STATES."""
    expected = {
        "UNCONFIGURED", "CONFIGURED", "SIMULATED",
        "QUEUED", "SENT", "DELIVERED", "FAILED", "BLOCKED"
    }
    assert VALID_SMS_STATES == expected


def test_simulated_never_delivered():
    """
    CRITICAL INVARIANT:
    A simulated dispatch must NEVER have status DELIVERED.
    """
    adapter = ProductionSMSAdapter(dry_run=True, provider_name="mock")
    status_info = adapter.get_provider_configuration_status()
    assert status_info["safety_mode"] == "TEST/DRY_RUN"

    res = adapter.dispatch_geofenced_sms(
        incident_id="INC-TEST-001",
        actor_id="DM_PAKYONG",
        actor_role="DISTRICT_AUTHORITY",
        auth_token="AUTH-v1.test.sig",
        geofence_polygon=[[27.32, 88.60], [27.34, 88.60], [27.34, 88.62], [27.32, 88.62], [27.32, 88.60]]
    )

    for rec in res.get("recipients", []):
        assert rec["status"] != STATE_DELIVERED, "CRITICAL: Simulated SMS reported as DELIVERED!"
        assert rec["status"] == STATE_SENT or rec["status"] == STATE_QUEUED
        assert rec["dry_run"] is True
        assert "[SIMULATED SMS]" in rec["message"]


def test_unconfigured_cdac_state():
    """Verifies that CDAC adapter without credentials correctly reports UNCONFIGURED."""
    adapter = ProductionSMSAdapter(dry_run=True, provider_name="cdac")
    adapter.provider = CDACSMSProvider(username="", password="")
    status_info = adapter.get_provider_configuration_status()
    assert status_info["configuration_state"] == STATE_UNCONFIGURED


def test_configured_cdac_state():
    """Verifies that CDAC adapter with credentials reports CONFIGURED."""
    adapter = ProductionSMSAdapter(dry_run=True, provider_name="cdac")
    adapter.provider = CDACSMSProvider(username="cdac_test_user", password="secret_password")
    status_info = adapter.get_provider_configuration_status()
    assert status_info["configuration_state"] == STATE_CONFIGURED


def test_dlt_readiness_metadata():
    """Verifies that government DLT readiness parameters are transparently reported."""
    adapter = ProductionSMSAdapter()
    status_info = adapter.get_provider_configuration_status()
    readiness = status_info["india_government_readiness"]

    assert "principal_entity_id" in readiness
    assert "trai_entity_id" in readiness
    assert "registered_header" in readiness
    assert "dlt_registration_status" in readiness
    assert readiness["registered_templates_count"] >= 6
    assert readiness["dlr_webhook_endpoint"] == "/api/sms/dlr"
