# -*- coding: utf-8 -*-
"""
tests/test_v4_7_telemetry_chain.py
==================================
Phase V4.7 Test Suite: End-to-End Telemetry Chain, CRC16, Offline Store-and-Forward,
Sequence Monotonicity, and Anomaly Detection
"""

import os
import time
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
    MeasurementItem,
    QUALITY_GOOD,
    QUALITY_DEGRADED,
    QUALITY_INVALID
)
from services.edge_gateway import EdgeBuffer
from engine.telemetry_trust_engine import (
    TelemetryTrustEngine,
    TRUST_VERIFIED,
    TRUST_DEGRADED,
    TRUST_UNVERIFIED,
    REASON_CRC_FAILURE,
    REASON_DUPLICATE,
    REASON_SEQUENCE_GAP,
    REASON_OUT_OF_RANGE,
    REASON_FUTURE_TIMESTAMP
)


@pytest.fixture
def validator():
    return TelemetryValidator()


@pytest.fixture
def edge_buffer(tmp_path):
    db_file = str(tmp_path / "test_edge_buffer.db")
    return EdgeBuffer(db_path=db_file)


@pytest.fixture
def trust_engine():
    return TelemetryTrustEngine()


class TestBinaryFrameCodecAndCRC:
    """Tests 18-byte binary frame packing, CRC16-CCITT validation, and corruption detection."""

    def test_valid_binary_frame_roundtrip(self):
        now_epoch = int(datetime.now(timezone.utc).timestamp())
        frame = BinaryPacketCodec.encode(
            device_short_id=101,
            sequence_number=1,
            timestamp_epoch=now_epoch,
            primary_val=42.8,       # 42.8 kPa
            secondary_val=1.25,     # 1.25 deg
            tertiary_val=0.0,
            battery_pct=95.0,
            temperature_c=22.0,
            tamper=False
        )
        assert len(frame) == FRAME_LENGTH_BYTES

        decoded = BinaryPacketCodec.decode(frame)
        assert decoded["device_short_id"] == 101
        assert decoded["sequence_number"] == 1
        assert decoded["timestamp_epoch"] == now_epoch
        assert pytest.approx(decoded["primary_reading"], 0.1) == 42.8
        assert pytest.approx(decoded["secondary_reading"], 0.01) == 1.25
        assert decoded["battery_pct"] == 95.0
        assert decoded["tamper_flag"] is False
        assert decoded["crc_valid"] is True

    def test_crc16_corruption_rejection(self):
        now_epoch = int(datetime.now(timezone.utc).timestamp())
        frame = bytearray(BinaryPacketCodec.encode(
            device_short_id=202,
            sequence_number=5,
            timestamp_epoch=now_epoch,
            primary_val=10.0
        ))
        # Corrupt 1 byte in payload (byte index 8 is primary reading)
        frame[8] ^= 0xFF

        with pytest.raises(ValueError) as exc:
            BinaryPacketCodec.decode(bytes(frame))
        assert "CRC mismatch" in str(exc.value)


class TestSequenceIntegrityAndReplayAttacks:
    """Tests sequence tracking, duplicate detection, and sequence gap handling."""

    def test_duplicate_packet_rejected(self, validator):
        now_iso = datetime.now(timezone.utc).isoformat()
        packet_payload = {
            "device_id": "PIEZO-NH10-KM48-01",
            "sequence_number": 10,
            "timestamp": now_iso,
            "latitude": 27.18,
            "longitude": 88.51,
            "battery": 90.0,
            "measurements": {"piezometer": {"value": 45.0, "unit": "kPa"}}
        }
        res1 = validator.validate_and_normalize(packet_payload)
        assert res1.is_valid is True
        assert res1.status == "ACCEPTED"

        # Replay identical packet
        res2 = validator.validate_and_normalize(packet_payload)
        assert res2.is_valid is False
        assert res2.status == "REJECTED_DUPLICATE"

    def test_sequence_monotonicity_and_gaps(self, validator):
        # Use past timestamps to prevent future timestamp rejection
        base_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        for seq in [1, 2, 5]:  # Gap between 2 and 5
            ts = (base_time + timedelta(seconds=seq * 60)).isoformat()
            payload = {
                "device_id": "INCL-TEST-SEQ",
                "sequence_number": seq,
                "timestamp": ts,
                "latitude": 27.18,
                "longitude": 88.51,
                "measurements": {"inclinometer": {"value": float(seq) * 2.0, "unit": "mm"}}
            }
            res = validator.validate_and_normalize(payload)
            assert res.is_valid is True


class TestStoreAndForwardEdgeBuffer:
    """Tests offline buffering during network outage and chronological FIFO replay."""

    def test_offline_buffering_and_chronological_replay(self, edge_buffer):
        now = datetime.now(timezone.utc) - timedelta(minutes=10)
        # Create 3 packets during simulated outage
        packets = []
        for i in range(1, 4):
            ts = (now + timedelta(minutes=i)).isoformat()
            pkt = TelemetryPacket(
                packet_id=f"PKT-OFFLINE-{i}",
                device_id="TILT-NH10-KM48-01",
                sensor_id="TILT-NH10-KM48-01",
                timestamp=ts,
                received_at=ts,
                sequence_number=i,
                latitude=27.18,
                longitude=88.51,
                measurements={"tilt": MeasurementItem(value=0.5 * i, unit="deg")},
                battery=95.0,
                signal_quality=-75.0,
                gateway_id="GW-NH10-KM48-01",
                transport="LORA"
            )
            packets.append(pkt)
            ok = edge_buffer.buffer_packet(pkt)
            assert ok is True

        assert edge_buffer.count_buffered() == 3

        # Replay packets in chronological FIFO order
        replayed = edge_buffer.get_pending_packets(limit=10)
        assert len(replayed) == 3
        # Verify chronological sequence order
        seqs = [r["sequence_number"] for r in replayed]
        assert seqs == [1, 2, 3]

        # Mark replayed and verify buffer drains
        edge_buffer.mark_synced([r["packet_id"] for r in replayed])
        assert edge_buffer.count_buffered() == 0


class TestSensorAnomaliesAndHealth:
    """Tests rate-of-change anomalies, flatline detection, and physical boundaries."""

    def test_impossible_physical_value_rejected(self, validator):
        now_iso = datetime.now(timezone.utc).isoformat()
        # Pore pressure cannot physically be 9999 kPa
        payload = {
            "device_id": "PIEZO-ANOMALY-01",
            "sequence_number": 1,
            "timestamp": now_iso,
            "latitude": 27.18,
            "longitude": 88.51,
            "measurements": {"piezometer": {"value": 9999.0, "unit": "kPa"}}
        }
        res = validator.validate_and_normalize(payload)
        assert res.is_valid is False
        assert res.status == "REJECTED_IMPOSSIBLE_VALUE"

    def test_rate_of_change_anomaly_degrades_quality(self, validator):
        base_time = datetime.now(timezone.utc)
        # Normal observation
        p1 = {
            "device_id": "PIEZO-RATE-01",
            "sequence_number": 1,
            "timestamp": base_time.isoformat(),
            "latitude": 27.18,
            "longitude": 88.51,
            "measurements": {"piezometer": {"value": 20.0, "unit": "kPa"}}
        }
        res1 = validator.validate_and_normalize(p1)
        assert res1.is_valid is True
        assert res1.overall_quality == QUALITY_GOOD

        # Sudden impossible jump within 5 seconds (> 120 kPa/h)
        p2 = {
            "device_id": "PIEZO-RATE-01",
            "sequence_number": 2,
            "timestamp": (base_time + timedelta(seconds=5)).isoformat(),
            "latitude": 27.18,
            "longitude": 88.51,
            "measurements": {"piezometer": {"value": 150.0, "unit": "kPa"}}
        }
        res2 = validator.validate_and_normalize(p2)
        assert res2.is_valid is True
        # Quality degrades due to abnormal rate of change
        assert res2.overall_quality == QUALITY_DEGRADED


class TestDualStreamDegradationSafety:
    """Tests fail-closed behavior when kinematic stream is unavailable or degraded."""

    def test_dual_stream_fails_closed_without_physical_sensors(self):
        from services.kinematic_telemetry_service import GLOBAL_KINEMATIC_SERVICE
        # Verify corridor kinematic stream status defaults to UNAVAILABLE / PENDING
        status = GLOBAL_KINEMATIC_SERVICE.get_corridor_status()
        assert status["corridor"]["telemetry_status"] == "PHYSICAL_TELEMETRY_PENDING"
        assert status["freshness"]["overall_status"] == "UNAVAILABLE"
        assert status["corridor"]["field_deployment_pending"] is True
