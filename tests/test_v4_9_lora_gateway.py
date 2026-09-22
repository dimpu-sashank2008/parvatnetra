# -*- coding: utf-8 -*-
"""
tests/test_v4_9_lora_gateway.py
===============================
Phase V4.9 Test Suite: LoRa Concentrator Gateway Validation & Store-and-Forward Replay
"""

import pytest
from engine.field_commissioning_engine import (
    FieldCommissioningEngine,
    CONN_CONFIGURED_ONLY
)


@pytest.fixture
def commissioning_engine():
    return FieldCommissioningEngine()


class TestLoRaGatewayValidation:
    """Verifies edge concentrator gateway audit and offline store-and-forward behavior."""

    def test_gateway_classified_as_configured_only(self, commissioning_engine):
        gw = commissioning_engine.audit_gateway_and_lora_transport()
        assert gw.gateway_id == "GW-NH10-KM48-01"
        assert gw.connectivity_status == CONN_CONFIGURED_ONLY
        assert gw.physical_presence_verified is False
        assert gw.store_and_forward_supported is True

    def test_store_and_forward_deduplication_prevents_duplicate_observations(self, commissioning_engine):
        # Create a burst of replayed packets including duplicates
        packets = [
            {"sensor_id": "PIEZO-NH10-KM48-01", "timestamp_utc": "2026-09-20T10:00:00Z", "value": 15.2, "sequence_number": 101},
            {"sensor_id": "PIEZO-NH10-KM48-01", "timestamp_utc": "2026-09-20T10:01:00Z", "value": 15.4, "sequence_number": 102},
            {"sensor_id": "PIEZO-NH10-KM48-01", "timestamp_utc": "2026-09-20T10:00:00Z", "value": 15.2, "sequence_number": 101},  # REPLAY DUPLICATE
            {"sensor_id": "INCL-NH10-KM48-01", "timestamp_utc": "2026-09-20T10:00:00Z", "value": 1.1, "sequence_number": 55},
            {"sensor_id": "PIEZO-NH10-KM48-01", "timestamp_utc": "2026-09-20T10:01:00Z", "value": 15.4, "sequence_number": 102},  # REPLAY DUPLICATE
        ]

        res = commissioning_engine.test_store_and_forward_deduplication(packets)
        assert res["total_replayed_packets"] == 5
        assert res["accepted_unique_count"] == 3
        assert res["rejected_duplicate_count"] == 2
        assert res["zero_duplicate_observations_created"] is True
        assert res["deduplication_success"] is True

    def test_unique_packets_all_accepted(self, commissioning_engine):
        packets = [
            {"sensor_id": "RAIN-NH10-KM48-01", "timestamp_utc": "2026-09-20T11:00:00Z", "value": 0.2, "sequence_number": 1},
            {"sensor_id": "RAIN-NH10-KM48-01", "timestamp_utc": "2026-09-20T11:05:00Z", "value": 0.4, "sequence_number": 2},
        ]
        res = commissioning_engine.test_store_and_forward_deduplication(packets)
        assert res["accepted_unique_count"] == 2
        assert res["rejected_duplicate_count"] == 0
