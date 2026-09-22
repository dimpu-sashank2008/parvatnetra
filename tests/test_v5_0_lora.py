# -*- coding: utf-8 -*-
"""
tests/test_v5_0_lora.py
=======================
Phase V5.0 Test Suite: LoRa Concentrator Gateway & Replay Deduplication
"""

import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestLoRaGateway:
    """Verifies LoRa concentrator gateway configuration and deduplication."""

    def test_gateway_configuration_status(self, deployment_engine):
        gw = deployment_engine.audit_gateway_transport()
        assert gw["gateway_id"] == "GW-NH10-KM48-01"
        assert gw["status"] == "CONFIGURED_ONLY"
        assert gw["physical_presence_verified"] is False
        assert gw["store_and_forward_buffer_supported"] is True

    def test_store_and_forward_deduplication_exactness(self, deployment_engine):
        packets = [
            {
                "sensor_id": "TILT-NH10-KM48-01",
                "timestamp_utc": "2026-09-20T12:00:00Z",
                "value": 0.42,
                "sequence_number": 101
            },
            {
                "sensor_id": "TILT-NH10-KM48-01",
                "timestamp_utc": "2026-09-20T12:00:00Z",
                "value": 0.42,
                "sequence_number": 101
            },  # Duplicate
            {
                "sensor_id": "TILT-NH10-KM48-01",
                "timestamp_utc": "2026-09-20T12:01:00Z",
                "value": 0.45,
                "sequence_number": 102
            }
        ]
        res = deployment_engine.test_store_and_forward_deduplication(packets)
        assert res["total_packets"] == 3
        assert res["accepted_count"] == 2
        assert res["duplicate_count"] == 1
        assert res["zero_duplicate_observations_created"] is True
