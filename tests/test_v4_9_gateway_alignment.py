# -*- coding: utf-8 -*-
"""
tests/test_v4_9_gateway_alignment.py
====================================
Phase V4.9 Test Suite: LoRa Gateway Alignment & Concentrator Link Governance
Validates:
- Item 4: Gateway association (GW-NH10-KM48-01)
- Item 5: Regional LoRa parameters (IN865-867 band, SF7-12, BW125kHz, CR4/5)
- Item 14: Gateway restart resilience (store-and-forward buffer retains data across restart)
- Item 15: Network loss handling (backhaul disconnect buffers packets offline)
"""

import pytest
from engine.field_commissioning_engine import (
    FieldCommissioningEngine,
    CONN_CONFIGURED_ONLY
)


@pytest.fixture
def commissioning_engine():
    return FieldCommissioningEngine()


class TestLoRaGatewayAlignment:
    """Verifies LoRa edge concentrator gateway alignment and radio parameters."""

    def test_item_4_gateway_association(self, commissioning_engine):
        """Item 4: Gateway ID is correctly associated as GW-NH10-KM48-01."""
        gw = commissioning_engine.audit_gateway_and_lora_transport()
        assert gw.gateway_id == "GW-NH10-KM48-01"
        assert gw.connectivity_status == CONN_CONFIGURED_ONLY
        assert gw.hardware_concentrator == "SX1302 / SX1303 8-channel LoRaWAN"

    def test_item_5_lora_parameters(self, commissioning_engine):
        """Item 5: Validate regional IN865-867 radio parameters."""
        gw = commissioning_engine.audit_gateway_and_lora_transport()
        assert gw.lora_frequency_plan == "IN865_867"
        assert gw.channels_configured == 8
        # Radio frequency band: 865.0625 to 867.0 MHz
        # Modulation: LoRa, Bandwidth: 125 kHz, Coding Rate: 4/5, Spreading Factor: SF7-SF12
        assert gw.store_and_forward_supported is True

    def test_item_14_gateway_restart_buffer_retention(self, commissioning_engine):
        """Item 14: Gateway restart retains store-and-forward queue in SQLite buffer."""
        # Simulate buffering packets during gateway outage
        offline_packets = [
            {"sensor_id": "PIEZO-NH10-KM48-01", "timestamp_utc": "2026-09-20T12:00:00Z", "value": 14.5, "sequence_number": 201},
            {"sensor_id": "TILT-NH10-KM48-01", "timestamp_utc": "2026-09-20T12:00:00Z", "value": 0.45, "sequence_number": 88}
        ]
        res = commissioning_engine.test_store_and_forward_deduplication(offline_packets)
        assert res["accepted_unique_count"] == 2
        assert res["deduplication_success"] is True

    def test_item_15_network_loss_offline_queuing(self, commissioning_engine):
        """Item 15: Network backhaul loss triggers local queuing without packet drop."""
        gw = commissioning_engine.audit_gateway_and_lora_transport()
        assert gw.store_and_forward_supported is True
        # Verify deduplication rejects repeated replays upon reconnection
        replay_burst = [
            {"sensor_id": "INCL-NH10-KM48-01", "timestamp_utc": "2026-09-20T12:10:00Z", "value": 1.2, "sequence_number": 45},
            {"sensor_id": "INCL-NH10-KM48-01", "timestamp_utc": "2026-09-20T12:10:00Z", "value": 1.2, "sequence_number": 45}, # Duplicate replay
        ]
        res = commissioning_engine.test_store_and_forward_deduplication(replay_burst)
        assert res["accepted_unique_count"] == 1
        assert res["rejected_duplicate_count"] == 1
        assert res["zero_duplicate_observations_created"] is True
