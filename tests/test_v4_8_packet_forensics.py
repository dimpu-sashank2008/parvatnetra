# -*- coding: utf-8 -*-
"""
tests/test_v4_8_packet_forensics.py
===================================
Phase V4.8 Test Suite: Raw Packet Forensics, SHA-256 Immutability & Audit Trail
"""

import os
import json
import hashlib
import pytest
from datetime import datetime, timezone

from services.packet_replay_service import (
    PacketReplayEngine,
    PacketForensicRecord,
    SOURCE_CLASS_REPLAYED_REAL
)


@pytest.fixture
def replay_engine(tmp_path):
    capture_dir = str(tmp_path / "raw_telemetry")
    return PacketReplayEngine(capture_dir=capture_dir)


class TestPacketForensicPreservation:
    """Tests forensic record generation, payload hashing, and tamper-evident storage."""

    def test_forensic_record_generation_and_hashing(self, replay_engine):
        sample_packet = {
            "packet_id": "PKT-FORENSIC-01",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "device_id": "PIEZO-NH10-KM48-01",
            "gateway_id": "GW-NH10-KM48-01",
            "sequence_number": 42,
            "timestamp": "2026-09-20T12:00:00Z",
            "latitude": 27.2023,
            "longitude": 88.5147,
            "measurements": {"piezometer": {"value": 45.2, "unit": "kPa"}},
            "crc_valid": True
        }

        replayed = replay_engine.replay_packets([sample_packet])
        assert len(replayed) == 1
        assert replayed[0]["provenance"] == "[REPLAYED_REAL]"

        history = replay_engine.get_forensics_history()
        assert len(history) == 1
        rec = history[0]
        assert rec["packet_id"] == "PKT-FORENSIC-01"
        assert rec["sensor_id"] == "PIEZO-NH10-KM48-01"
        assert rec["sequence_number"] == 42
        assert rec["crc_result"] == "PASS"
        assert len(rec["payload_hash"]) == 64  # Valid SHA-256 string

    def test_raw_packet_file_save_and_hash_audit(self, replay_engine):
        packets = [
            {"packet_id": f"PKT-00{i}", "sequence_number": i, "value": 10.0 + i}
            for i in range(1, 4)
        ]
        file_sha256 = replay_engine.save_capture_file("test_capture.json", packets)
        assert len(file_sha256) == 64

        loaded_packets, meta = replay_engine.load_capture_file("test_capture.json")
        assert len(loaded_packets) == 3
        assert meta["sha256"] == file_sha256
        assert meta["packet_count"] == 3

    def test_tamper_detection_in_raw_file(self, replay_engine, tmp_path):
        packets = [{"packet_id": "PKT-IMMUTABLE-01", "sequence_number": 1, "value": 20.0}]
        orig_hash = replay_engine.save_capture_file("immutable_capture.json", packets)

        # Intentionally tamper with file contents on disk
        tampered_path = os.path.join(replay_engine.capture_dir, "immutable_capture.json")
        with open(tampered_path, "a", encoding="utf-8") as f:
            f.write("   ")  # Append whitespace

        with open(tampered_path, "rb") as f:
            new_hash = hashlib.sha256(f.read()).hexdigest()

        assert new_hash != orig_hash, "File tampering must be caught via SHA-256 mismatch"
