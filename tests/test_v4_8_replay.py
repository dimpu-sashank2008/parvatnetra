# -*- coding: utf-8 -*-
"""
tests/test_v4_8_replay.py
=========================
Phase V4.8 Test Suite: Deterministic Packet Replay, REPLAYED_REAL Tagging & Mode Scenarios
"""

import os
import json
import pytest

from services.packet_replay_service import (
    PacketReplayEngine,
    SOURCE_CLASS_REPLAYED_REAL,
    SOURCE_CLASS_LIVE_PHYSICAL,
    MODE_NORMAL,
    MODE_OUT_OF_ORDER,
    MODE_DUPLICATE,
    MODE_PACKET_LOSS
)


@pytest.fixture
def replay_engine():
    return PacketReplayEngine()


@pytest.fixture
def sample_packets():
    return [
        {
            "packet_id": f"PKT-{i:03d}",
            "device_id": "PIEZO-NH10-KM48-01",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "sequence_number": i,
            "timestamp": f"2026-09-20T12:{i*5:02d}:00Z",
            "measurements": {"piezometer": {"value": 40.0 + i, "unit": "kPa"}},
            "crc_valid": True
        }
        for i in range(1, 6)
    ]


class TestPacketReplayModes:
    """Tests normal, out-of-order, duplicate, and loss replay modes."""

    def test_normal_replay_preserves_order_and_tags_replayed_real(self, replay_engine, sample_packets):
        out = replay_engine.replay_packets(sample_packets, mode=MODE_NORMAL)
        assert len(out) == 5
        for idx, p in enumerate(out):
            assert p["sequence_number"] == idx + 1
            assert p["provenance"] == "[REPLAYED_REAL]"
            assert p["source_class"] == SOURCE_CLASS_REPLAYED_REAL
            assert p["source_class"] != SOURCE_CLASS_LIVE_PHYSICAL

    def test_out_of_order_replay_mode(self, replay_engine, sample_packets):
        out = replay_engine.replay_packets(sample_packets, mode=MODE_OUT_OF_ORDER)
        assert len(out) == 5
        # First two packets should be inverted (2, then 1)
        assert out[0]["sequence_number"] == 2
        assert out[1]["sequence_number"] == 1

    def test_duplicate_replay_mode(self, replay_engine, sample_packets):
        out = replay_engine.replay_packets(sample_packets, mode=MODE_DUPLICATE)
        assert len(out) == 6  # 5 + 1 duplicate
        assert out[0]["sequence_number"] == 1
        assert out[1]["sequence_number"] == 1

    def test_packet_loss_replay_mode(self, replay_engine, sample_packets):
        # 50% loss drops every 2nd packet
        out = replay_engine.replay_packets(sample_packets, mode=MODE_PACKET_LOSS, loss_rate=0.5)
        assert len(out) < 5


class TestCaptureFileLoadingAndReplay:
    """Tests loading from data/raw/telemetry/sample_corridor_packets.json."""

    def test_load_sample_capture_file(self, replay_engine):
        packets, meta = replay_engine.load_capture_file("sample_corridor_packets.json")
        assert len(packets) == 5
        assert meta["sha256"] is not None
        assert meta["file_size_bytes"] > 0

        replayed = replay_engine.replay_packets(packets)
        assert len(replayed) == 5
        assert all(r["provenance"] == "[REPLAYED_REAL]" for r in replayed)
