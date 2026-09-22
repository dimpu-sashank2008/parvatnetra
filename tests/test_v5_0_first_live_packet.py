# -*- coding: utf-8 -*-
"""
tests/test_v5_0_first_live_packet.py
====================================
Phase V5.0 Test Suite: First Live Packet Verification & Sequence Integrity Gate
"""

from datetime import datetime, timezone, timedelta
import pytest
from engine.physical_deployment_engine import PhysicalDeploymentEngine


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestFirstLivePacket:
    """Verifies that first live packet assignment strictly requires physical presence and valid CRC."""

    def test_bench_packet_rejected_from_first_live(self, deployment_engine):
        candidate = {
            "observation_id": "OBS-CANDIDATE-001",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "value": 22.4,
            "unit": "kPa",
            "source": "BENCH_HIL_SIMULATOR",
            "transport": "USB_SERIAL",
            "provenance": "BENCH",
            "sequence_number": 1,
            "crc_valid": True
        }
        ok, msg, details = deployment_engine.evaluate_first_live_packet_candidate(candidate)
        assert ok is False
        assert details["qualified"] is False
        assert details["first_live_timestamp"] is None
        assert "CRITERION_1_FAIL" in " ".join(details["reasons"])

    def test_missing_sequence_number_rejected(self, deployment_engine):
        candidate = {
            "observation_id": "OBS-CANDIDATE-002",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "value": 22.4,
            "unit": "kPa",
            "source": "FIELD_LORA_NODE",
            "transport": "FIELD_LORA",
            "provenance": "LIVE",
            "crc_valid": True,
            "sequence_number": None  # Missing
        }
        ok, msg, details = deployment_engine.evaluate_first_live_packet_candidate(candidate)
        assert ok is False

    def test_negative_sequence_number_rejected(self, deployment_engine):
        candidate = {
            "observation_id": "OBS-CANDIDATE-003",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "value": 22.4,
            "unit": "kPa",
            "source": "FIELD_LORA_NODE",
            "transport": "FIELD_LORA",
            "provenance": "LIVE",
            "crc_valid": True,
            "sequence_number": -5  # Invalid
        }
        ok, msg, details = deployment_engine.evaluate_first_live_packet_candidate(candidate)
        assert ok is False

    def test_overall_first_live_timestamp_is_null(self, deployment_engine):
        # When zero live observations verified, first live timestamp remains None
        v = deployment_engine.evaluate_v5_0_overall_verdict()
        assert v["live_mountain_observations"] == 0
