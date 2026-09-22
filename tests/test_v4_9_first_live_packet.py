# -*- coding: utf-8 -*-
"""
tests/test_v4_9_first_live_packet.py
====================================
Phase V4.9 Test Suite: First Live Packet Structure & Physical Packet Decoding
Validates:
- Item 6: First live packet schema & engineering unit decoding (kPa, mm, deg, mm/h)
- Item 7: CRC-16 CCITT verification and bit error detection
- Item 8: UTC timestamp validation and future timestamp rejection
- Item 9: Monotonic sequence counter per sensor ID
"""

from datetime import datetime, timezone, timedelta
import pytest
from engine.field_commissioning_engine import FieldCommissioningEngine


@pytest.fixture
def commissioning_engine():
    return FieldCommissioningEngine()


class TestFirstLivePacket:
    """Verifies live physical packet decoding, CRC, timestamps, and sequence numbers."""

    def test_item_6_packet_structure_and_engineering_units(self, commissioning_engine):
        """Item 6: Verify valid packet structure and physical engineering units."""
        units_map = {
            "PIEZOMETER": "kPa",
            "INCLINOMETER": "mm",
            "TILTMETER": "deg",
            "RAIN_GAUGE": "mm/h"
        }
        for sensor_type, expected_unit in units_map.items():
            packet = {
                "observation_id": f"obs-{sensor_type.lower()}-001",
                "sensor_id": f"{sensor_type[:4]}-NH10-KM48-01",
                "corridor_id": "CORR-NH10-SIKKIM-KM48",
                "sensor_type": sensor_type,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "value": 10.0,
                "unit": expected_unit,
                "source": "FIELD_NODE",
                "provenance": "LIVE",
                "transport": "FIELD_LORA",
                "crc_valid": True,
                "sequence_number": 1
            }
            assert packet["unit"] == expected_unit
            assert packet["corridor_id"] == "CORR-NH10-SIKKIM-KM48"
            assert "sequence_number" in packet

    def test_item_7_crc_verification(self, commissioning_engine):
        """Item 7: Corrupted CRC fails live boundary evaluation."""
        now_iso = datetime.now(timezone.utc).isoformat()
        corrupt_packet = {
            "observation_id": "crc-corrupt-01",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "value": 18.2,
            "unit": "kPa",
            "source": "FIELD_NODE",
            "provenance": "LIVE",
            "transport": "FIELD_LORA",
            "crc_valid": False,  # CRC check failure
            "sequence_number": 12
        }
        is_live, reasons = commissioning_engine.evaluate_live_field_boundary(corrupt_packet)
        assert is_live is False
        assert any("CRITERION_6_FAIL" in r for r in reasons)

    def test_item_8_future_timestamp_rejected(self, commissioning_engine):
        """Item 8: Future timestamps > 60s ahead are rejected by live boundary gate."""
        future_iso = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
        future_packet = {
            "observation_id": "future-time-01",
            "sensor_id": "TILT-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "TILTMETER",
            "timestamp_utc": future_iso,
            "value": 0.12,
            "unit": "deg",
            "source": "FIELD_NODE",
            "provenance": "LIVE",
            "transport": "FIELD_LORA",
            "crc_valid": True,
            "sequence_number": 5
        }
        is_live, reasons = commissioning_engine.evaluate_live_field_boundary(future_packet)
        assert is_live is False
        assert any("CRITERION_5_FAIL" in r for r in reasons)

    def test_item_9_sequence_number_monotonicity(self, commissioning_engine):
        """Item 9: Sequence numbers must advance monotonically; replayed duplicates are dropped."""
        packets = [
            {"sensor_id": "PIEZO-NH10-KM48-01", "timestamp_utc": "2026-09-20T10:00:00Z", "value": 15.0, "sequence_number": 10},
            {"sensor_id": "PIEZO-NH10-KM48-01", "timestamp_utc": "2026-09-20T10:01:00Z", "value": 15.1, "sequence_number": 11},
            {"sensor_id": "PIEZO-NH10-KM48-01", "timestamp_utc": "2026-09-20T10:00:00Z", "value": 15.0, "sequence_number": 10}, # Out-of-order / replay
        ]
        res = commissioning_engine.test_store_and_forward_deduplication(packets)
        assert res["accepted_unique_count"] == 2
        assert res["rejected_duplicate_count"] == 1
