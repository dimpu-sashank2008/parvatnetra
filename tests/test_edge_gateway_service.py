# -*- coding: utf-8 -*-
"""
tests/test_edge_gateway_service.py
==================================
Unit tests for Edge Gateway Service Concentrator & Reconnect Synchronization (Phase 6A).
Validates:
  - Concentrator lifecycle and metadata
  - Online ingestion and immediate observation store forwarding
  - Offline backhaul disconnection and automatic local buffering
  - Reconnect forward-sync replay of buffered packets in strict sequence
  - Gateway health telemetry
"""

import os
import tempfile
import pytest
from datetime import datetime, timezone

from services.edge_gateway import EdgeGatewayService, EdgeBuffer
from engine.sensor_registry import SensorRegistry


@pytest.fixture
def test_edge_service():
    with tempfile.TemporaryDirectory() as tmpdir:
        buf_path = os.path.join(tmpdir, "edge_buf.db")
        service = EdgeGatewayService(
            gateway_id="GW-TEST-CONC-01",
            name="Test Concentrator",
            latitude=27.33,
            longitude=88.61,
            sector_id="SK-NH10-KM48"
        )
        service.buffer = EdgeBuffer(db_path=buf_path)
        yield service


def test_edge_service_initial_status(test_edge_service):
    status = test_edge_service.get_status()
    assert status["gateway_id"] == "GW-TEST-CONC-01"
    assert status["is_cloud_connected"] is True
    assert status["buffered_packet_count"] == 0
    assert status["status"] == "ONLINE"


def test_online_ingestion_and_forwarding(test_edge_service):
    now_iso = datetime.now(timezone.utc).isoformat()
    raw = {
        "device_id": "SN-PZ-EDGE-01",
        "sequence_number": 1,
        "timestamp": now_iso,
        "latitude": 27.33,
        "longitude": 88.61,
        "measurements": {"pore_pressure": 18.0}
    }
    res = test_edge_service.ingest_sensor_packet(raw)
    assert res["status"] == "ACCEPTED"
    assert test_edge_service.buffer.count_buffered() == 0


def test_offline_buffering_on_disconnect(test_edge_service):
    # Simulate mountain backhaul fiber cut
    test_edge_service.set_cloud_connectivity(False)
    assert test_edge_service.is_cloud_connected is False

    now_iso = datetime.now(timezone.utc).isoformat()
    raw1 = {
        "device_id": "SN-PZ-EDGE-01",
        "sequence_number": 2,
        "timestamp": now_iso,
        "latitude": 27.33,
        "longitude": 88.61,
        "measurements": {"pore_pressure": 22.0}
    }
    raw2 = {
        "device_id": "SN-PZ-EDGE-01",
        "sequence_number": 3,
        "timestamp": now_iso,
        "latitude": 27.33,
        "longitude": 88.61,
        "measurements": {"pore_pressure": 23.5}
    }

    res1 = test_edge_service.ingest_sensor_packet(raw1)
    assert res1["status"] == "BUFFERED_OFFLINE"

    res2 = test_edge_service.ingest_sensor_packet(raw2)
    assert res2["status"] == "BUFFERED_OFFLINE"

    assert test_edge_service.buffer.count_buffered() == 2


def test_reconnect_and_replay(test_edge_service):
    # Buffer 2 packets while offline
    test_edge_service.set_cloud_connectivity(False)
    now_iso = datetime.now(timezone.utc).isoformat()

    test_edge_service.ingest_sensor_packet({
        "device_id": "SN-DEV-REPLAY",
        "sequence_number": 10,
        "timestamp": now_iso,
        "latitude": 27.33,
        "longitude": 88.61,
        "measurements": {"pore_pressure": 25.0}
    })
    test_edge_service.ingest_sensor_packet({
        "device_id": "SN-DEV-REPLAY",
        "sequence_number": 11,
        "timestamp": now_iso,
        "latitude": 27.33,
        "longitude": 88.61,
        "measurements": {"pore_pressure": 26.0}
    })

    assert test_edge_service.buffer.count_buffered() == 2

    # Restore backhaul
    test_edge_service.set_cloud_connectivity(True)

    # Flush buffered queue
    flush_res = test_edge_service.flush_buffered_packets()
    assert flush_res["status"] == "SUCCESS"
    assert flush_res["synced_count"] == 2
    assert flush_res["remaining_count"] == 0
    assert test_edge_service.buffer.count_buffered() == 0
