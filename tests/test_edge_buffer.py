# -*- coding: utf-8 -*-
"""
tests/test_edge_buffer.py
=========================
Unit tests for Edge Gateway Local SQLite Buffer & Replay (Phase 6A).
Validates:
  - Local persistent storage of telemetry packets during backhaul disconnection
  - FIFO order preservation during forward replay
  - Idempotent deduplication (duplicate packet_id ignored)
  - Exponential backoff retry increment
  - Buffer state transitions: BUFFERED -> SYNCED
"""

import os
import tempfile
import pytest
from datetime import datetime, timezone

from services.edge_gateway import EdgeBuffer
from services.telemetry_contract import TelemetryPacket, MeasurementItem


@pytest.fixture
def temp_buffer():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_edge_buffer.db")
        buf = EdgeBuffer(db_path=db_path)
        yield buf


def make_test_packet(packet_id: str, seq: int, val: float = 20.0) -> TelemetryPacket:
    now_iso = datetime.now(timezone.utc).isoformat()
    return TelemetryPacket(
        packet_id=packet_id,
        device_id="DEV-BUF-01",
        sensor_id="PZ-01",
        timestamp=now_iso,
        received_at=now_iso,
        sequence_number=seq,
        latitude=27.33,
        longitude=88.61,
        measurements={"pore_pressure": MeasurementItem("pore_pressure", val, "kPa", "CALIBRATED")},
        battery=95.0,
        signal_quality=-70.0,
        gateway_id="GW-BUF-01"
    )


def test_buffer_packet_insertion(temp_buffer):
    pkt = make_test_packet("PKT-001", 1, 22.5)
    success = temp_buffer.buffer_packet(pkt)
    assert success is True
    assert temp_buffer.count_buffered() == 1


def test_buffer_deduplication(temp_buffer):
    pkt = make_test_packet("PKT-DUP-01", 1, 15.0)
    # Insert first time
    assert temp_buffer.buffer_packet(pkt) is True
    # Insert exact duplicate
    temp_buffer.buffer_packet(pkt)
    # Count should still be 1 due to UNIQUE constraint / INSERT OR IGNORE
    assert temp_buffer.count_buffered() == 1


def test_fifo_order_and_mark_synced(temp_buffer):
    pkt1 = make_test_packet("PKT-FIFO-01", 1)
    pkt2 = make_test_packet("PKT-FIFO-02", 2)
    pkt3 = make_test_packet("PKT-FIFO-03", 3)

    temp_buffer.buffer_packet(pkt1)
    temp_buffer.buffer_packet(pkt2)
    temp_buffer.buffer_packet(pkt3)

    assert temp_buffer.count_buffered() == 3

    # Fetch pending with limit 2
    pending = temp_buffer.get_pending_packets(limit=2)
    assert len(pending) == 2
    assert pending[0]["packet_id"] == "PKT-FIFO-01"
    assert pending[1]["packet_id"] == "PKT-FIFO-02"

    # Mark first packet synced
    temp_buffer.mark_synced(["PKT-FIFO-01"])
    assert temp_buffer.count_buffered() == 2

    # Next fetch gets PKT-FIFO-02 and PKT-FIFO-03
    next_pending = temp_buffer.get_pending_packets(limit=2)
    assert len(next_pending) == 2
    assert next_pending[0]["packet_id"] == "PKT-FIFO-02"
    assert next_pending[1]["packet_id"] == "PKT-FIFO-03"


def test_retry_count_increment(temp_buffer):
    pkt = make_test_packet("PKT-RETRY-01", 1)
    temp_buffer.buffer_packet(pkt)

    temp_buffer.increment_retry(["PKT-RETRY-01"])
    pending = temp_buffer.get_pending_packets(limit=1)
    assert pending[0]["retry_count"] == 1

    temp_buffer.increment_retry(["PKT-RETRY-01"])
    pending2 = temp_buffer.get_pending_packets(limit=1)
    assert pending2[0]["retry_count"] == 2
