# -*- coding: utf-8 -*-
"""
tests/test_v5_0_gateway_commissioning.py
========================================
Phase V5.0 Test Suite: LoRa Gateway Identity, Radio Parameters & Commissioning State
"""

import pytest
from engine.physical_deployment_engine import PhysicalDeploymentEngine


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestGatewayCommissioning:
    """Verifies LoRa concentrator gateway configuration, identity, and transport status."""

    def test_gateway_identity_and_specifications(self, deployment_engine):
        gw = deployment_engine.audit_gateway_transport()
        assert gw["gateway_id"] == "GW-NH10-KM48-01"
        assert "IP67" in gw["model"]
        assert gw["serial_number"] == "PN-GW-2026-0038"
        assert "v3.0.1" in gw["firmware_version"]

    def test_gateway_commissioning_status_is_configured_only(self, deployment_engine):
        gw = deployment_engine.audit_gateway_transport()
        assert gw["status"] == "CONFIGURED_ONLY"
        assert gw["physical_presence_verified"] is False
        assert gw["mqtt_broker_connected"] is True
        assert gw["store_and_forward_buffer_supported"] is True

    def test_gateway_route_configured_in_sensor_provenance(self, deployment_engine):
        audits = deployment_engine.audit_sensor_hardware_provenance()
        assert "GW-NH10-KM48-01" in audits
        gw_record = audits["GW-NH10-KM48-01"]
        assert gw_record.gateway_route_verified is True
        assert gw_record.gateway_status == "CONFIGURED_ONLY"
        assert gw_record.live_telemetry_active is False
