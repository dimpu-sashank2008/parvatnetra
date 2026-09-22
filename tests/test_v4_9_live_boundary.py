# -*- coding: utf-8 -*-
"""
tests/test_v4_9_live_boundary.py
================================
Phase V4.9 Test Suite: 10-Criteria LIVE_FIELD_TELEMETRY Boundary Gate
"""

from datetime import datetime, timezone, timedelta
import pytest
from engine.field_commissioning_engine import FieldCommissioningEngine


@pytest.fixture
def commissioning_engine():
    return FieldCommissioningEngine()


class TestLiveFieldBoundary:
    """Verifies strict 10-criteria enforcement for LIVE_FIELD_TELEMETRY assignment."""

    def test_simulated_packet_fails_boundary_gate(self, commissioning_engine):
        now_iso = datetime.now(timezone.utc).isoformat()
        obs = {
            "observation_id": "test-sim-01",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "value": 15.0,
            "unit": "kPa",
            "source": "SIMULATED_GENERATOR",
            "provenance": "LIVE",  # FRAUDULENT
            "transport": "HTTP_POST",
            "crc_valid": True
        }
        is_live, reasons = commissioning_engine.evaluate_live_field_boundary(obs)
        assert is_live is False
        assert any("CRITERION_3_FAIL" in r for r in reasons)

    def test_unverified_physical_sensor_fails_boundary_gate(self, commissioning_engine):
        now_iso = datetime.now(timezone.utc).isoformat()
        obs = {
            "observation_id": "test-unverified-01",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "value": 22.0,
            "unit": "kPa",
            "source": "FIELD_NODE",
            "provenance": "LIVE",
            "transport": "FIELD_LORA",
            "crc_valid": True
        }
        is_live, reasons = commissioning_engine.evaluate_live_field_boundary(obs)
        assert is_live is False
        assert any("CRITERION_1_FAIL" in r for r in reasons)
        assert any("CRITERION_2_FAIL" in r for r in reasons)

    def test_future_timestamp_fails_boundary_gate(self, commissioning_engine):
        future_iso = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        obs = {
            "observation_id": "test-future-01",
            "sensor_id": "INCL-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "INCLINOMETER",
            "timestamp_utc": future_iso,
            "value": 2.5,
            "unit": "mm",
            "source": "FIELD_NODE",
            "provenance": "LIVE",
            "transport": "FIELD_LORA",
            "crc_valid": True
        }
        is_live, reasons = commissioning_engine.evaluate_live_field_boundary(obs)
        assert is_live is False
        assert any("CRITERION_5_FAIL" in r for r in reasons)

    def test_crc_failure_fails_boundary_gate(self, commissioning_engine):
        now_iso = datetime.now(timezone.utc).isoformat()
        obs = {
            "observation_id": "test-crc-fail-01",
            "sensor_id": "TILT-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "TILTMETER",
            "timestamp_utc": now_iso,
            "value": 0.5,
            "unit": "deg",
            "source": "FIELD_NODE",
            "provenance": "LIVE",
            "transport": "FIELD_LORA",
            "crc_valid": False
        }
        is_live, reasons = commissioning_engine.evaluate_live_field_boundary(obs)
        assert is_live is False
        assert any("CRITERION_6_FAIL" in r for r in reasons)

    def test_item_10_duplicate_packet_rejected(self, commissioning_engine):
        """Item 10: Duplicate packets with identical sensor, sequence, and timestamp are rejected."""
        packets = [
            {"sensor_id": "PIEZO-NH10-KM48-01", "timestamp_utc": "2026-09-20T10:00:00Z", "value": 15.0, "sequence_number": 5},
            {"sensor_id": "PIEZO-NH10-KM48-01", "timestamp_utc": "2026-09-20T10:00:00Z", "value": 15.0, "sequence_number": 5}
        ]
        res = commissioning_engine.test_store_and_forward_deduplication(packets)
        assert res["accepted_unique_count"] == 1
        assert res["rejected_duplicate_count"] == 1

    def test_item_11_replay_packet_rejected(self, commissioning_engine):
        """Item 11: Replay of historical packets cannot forge current live telemetry."""
        packets = [
            {"sensor_id": "INCL-NH10-KM48-01", "timestamp_utc": "2026-09-19T08:00:00Z", "value": 1.1, "sequence_number": 1},
            {"sensor_id": "INCL-NH10-KM48-01", "timestamp_utc": "2026-09-19T08:00:00Z", "value": 1.1, "sequence_number": 1}
        ]
        res = commissioning_engine.test_store_and_forward_deduplication(packets)
        assert res["zero_duplicate_observations_created"] is True

    def test_item_19_provenance_marker_strictly_enforced(self, commissioning_engine):
        """Item 19: Records containing BENCH, HIL, or SIMULATED markers cannot be assigned LIVE."""
        now_iso = datetime.now(timezone.utc).isoformat()
        bench_obs = {
            "observation_id": "bench-marker-01",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "value": 14.8,
            "unit": "kPa",
            "source": "BENCH_HIL_SIMULATED",
            "provenance": "LIVE", # Attempt to forge
            "transport": "FIELD_LORA",
            "crc_valid": True
        }
        is_live, reasons = commissioning_engine.evaluate_live_field_boundary(bench_obs)
        assert is_live is False
        assert any("CRITERION_10_FAIL" in r for r in reasons)

    def test_item_24_fail_closed_on_unverified_telemetry(self, commissioning_engine):
        """Item 24: Fail-closed architecture halts live status when sensor physical presence is unverified."""
        now_iso = datetime.now(timezone.utc).isoformat()
        unverified_obs = {
            "observation_id": "obs-unverified-node",
            "sensor_id": "UNKNOWN-SENSOR-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "value": 20.0,
            "unit": "kPa",
            "source": "FIELD_NODE",
            "provenance": "LIVE",
            "transport": "FIELD_LORA",
            "crc_valid": True
        }
        is_live, reasons = commissioning_engine.evaluate_live_field_boundary(unverified_obs)
        assert is_live is False
        assert len(reasons) > 0
