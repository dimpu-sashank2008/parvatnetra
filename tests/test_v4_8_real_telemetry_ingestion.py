# -*- coding: utf-8 -*-
"""
tests/test_v4_8_real_telemetry_ingestion.py
===========================================
Phase V4.8 Test Suite: Real In-Situ Telemetry Ingestion, Protocol Decoding & QC Verification
"""

import os
import json
import pytest
from datetime import datetime, timezone, timedelta

from firmware.packet_codec import (
    BinaryPacketCodec,
    compute_crc16_ccitt,
    FRAME_LENGTH_BYTES
)
from services.telemetry_contract import (
    TelemetryValidator,
    TelemetryPacket,
    QUALITY_GOOD,
    QUALITY_DEGRADED,
    QUALITY_INVALID
)
from engine.sensor_acceptance_engine import (
    GLOBAL_ACCEPTANCE_ENGINE,
    STATE_BENCH_ACCEPTED,
    STATE_UNVERIFIED_IDENTITY
)
from engine.telemetry_trust_engine import (
    GLOBAL_TELEMETRY_TRUST_ENGINE,
    TRUST_VERIFIED,
    TRUST_DEGRADED,
    TRUST_UNVERIFIED,
    REASON_CRC_FAILURE,
    REASON_DUPLICATE,
    REASON_OUT_OF_RANGE
)


@pytest.fixture
def validator():
    return TelemetryValidator()


class TestRealPacketDecodingAndCRC:
    """Tests 18-byte packed binary decoding, CRC verification, and bitflip rejection."""

    def test_decode_valid_18byte_frame(self):
        epoch = int(datetime.now(timezone.utc).timestamp())
        frame = BinaryPacketCodec.encode(
            device_short_id=101,
            sequence_number=42,
            timestamp_epoch=epoch,
            primary_val=55.4,   # 55.4 kPa pore pressure
            secondary_val=0.85, # 0.85 deg tilt
            tertiary_val=0.0,
            battery_pct=92.0,
            temperature_c=18.0,
            tamper=False
        )
        assert len(frame) == FRAME_LENGTH_BYTES

        decoded = BinaryPacketCodec.decode(frame)
        assert decoded["device_short_id"] == 101
        assert decoded["sequence_number"] == 42
        assert pytest.approx(decoded["primary_reading"], 0.1) == 55.4
        assert pytest.approx(decoded["secondary_reading"], 0.01) == 0.85
        assert decoded["battery_pct"] == 92.0
        assert decoded["crc_valid"] is True

    def test_reject_corrupted_crc_frame(self):
        epoch = int(datetime.now(timezone.utc).timestamp())
        raw = bytearray(BinaryPacketCodec.encode(
            device_short_id=101,
            sequence_number=1,
            timestamp_epoch=epoch,
            primary_val=30.0
        ))
        # Flip bit in primary reading payload
        raw[8] ^= 0x01

        with pytest.raises(ValueError) as exc:
            BinaryPacketCodec.decode(bytes(raw))
        assert "CRC mismatch" in str(exc.value)


class TestSensorIdentityAndSerialVerification:
    """Tests that packet device ID and serial number match registered identity."""

    def test_registered_sensor_accepted(self, validator):
        past_ts = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        payload = {
            "device_id": "PIEZO-NH10-KM48-01",
            "sequence_number": 1,
            "timestamp": past_ts,
            "latitude": 27.2023,
            "longitude": 88.5147,
            "measurements": {"piezometer": {"value": 45.0, "unit": "kPa"}},
            "battery": 95.0
        }
        res = validator.validate_and_normalize(payload)
        assert res.is_valid is True
        assert res.status == "ACCEPTED"

    def test_unregistered_sensor_rejected_under_strict_mode(self, validator):
        past_ts = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        payload = {
            "device_id": "ROGUE-DEVICE-999",
            "sequence_number": 1,
            "timestamp": past_ts,
            "latitude": 27.2023,
            "longitude": 88.5147,
            "measurements": {"piezometer": {"value": 45.0, "unit": "kPa"}}
        }
        res = validator.validate_and_normalize(payload, enforce_registered=True)
        assert res.is_valid is False
        assert "REJECTED_UNKNOWN_DEVICE" in res.status


class TestSequenceIntegrityAndDeduplication:
    """Tests deduplication and monotonic sequence checking."""

    def test_duplicate_sequence_rejection(self, validator):
        past_ts = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        payload = {
            "device_id": "TILT-NH10-KM48-01",
            "sequence_number": 100,
            "timestamp": past_ts,
            "latitude": 27.2023,
            "longitude": 88.5147,
            "measurements": {"tilt": {"value": 1.2, "unit": "deg"}}
        }
        res1 = validator.validate_and_normalize(payload)
        assert res1.is_valid is True

        res2 = validator.validate_and_normalize(payload)
        assert res2.is_valid is False
        assert res2.status == "REJECTED_DUPLICATE"


class TestSensorQualityControlStates:
    """Tests QC classifications: VALID, DEGRADED, INVALID."""

    def test_degraded_on_stale_or_marginal_battery(self, validator):
        past_ts = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        payload = {
            "device_id": "INCL-NH10-KM48-01",
            "sequence_number": 200,
            "timestamp": past_ts,
            "latitude": 27.2023,
            "longitude": 88.5147,
            "measurements": {"inclinometer": {"value": 5.0, "unit": "mm"}},
            "battery": 8.0,  # Critical low battery (< 15%)
            "signal_quality": -98.0
        }
        res = validator.validate_and_normalize(payload)
        assert res.is_valid is True
        assert res.overall_quality == QUALITY_DEGRADED

    def test_invalid_on_impossible_physical_value(self, validator):
        past_ts = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        payload = {
            "device_id": "PIEZO-NH10-KM48-01",
            "sequence_number": 300,
            "timestamp": past_ts,
            "latitude": 27.2023,
            "longitude": 88.5147,
            "measurements": {"piezometer": {"value": 99999.0, "unit": "kPa"}}  # Impossible
        }
        res = validator.validate_and_normalize(payload)
        assert res.is_valid is False
        assert res.status == "REJECTED_IMPOSSIBLE_VALUE"
