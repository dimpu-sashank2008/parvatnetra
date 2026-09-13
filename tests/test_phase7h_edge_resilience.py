# -*- coding: utf-8 -*-
"""
tests/test_phase7h_edge_resilience.py
=====================================
PHASE 7H — CP 7H-01, 7H-02, 7H-09: Edge Gateway Resilience, Offline Buffering,
Packet Checksumming, Capacity Tracking, Power Failure & Recovery.
"""

import os
import pytest
from datetime import datetime, timezone
from backend.edge.edge_store import EdgeStore
from backend.edge.sync import EdgeSync

@pytest.fixture
def edge_env(tmp_path):
    db_file = str(tmp_path / "edge_resilience.db")
    store = EdgeStore(db_path=db_file)
    sync = EdgeSync(store=store)
    return store, sync

def test_offline_buffering_when_wan_disconnected(edge_env):
    """CP 7H-01 & 7H-02: Telemetry continues buffering locally when cloud backhaul is down."""
    store, sync = edge_env
    sync.set_cloud_connectivity(False)
    assert sync.is_cloud_connected is False

    reading_ts = "2026-09-11T07:00:00Z"
    r1 = {
        "node_id": "PZ-01",
        "sequence": 101,
        "timestamp": reading_ts,
        "pore_pressure": 45.2,
        "battery": 92
    }
    r2 = {
        "node_id": "PZ-01",
        "sequence": 102,
        "timestamp": "2026-09-11T07:01:00Z",
        "pore_pressure": 46.1,
        "battery": 91
    }
    store.register_reading(r1, buffer_for_cloud=True)
    store.register_reading(r2, buffer_for_cloud=True)

    stats = store.get_queue_stats()
    assert stats["buffered_count"] == 2
    assert stats["synced_count"] == 0
    assert stats["oldest_queued_at"] is not None
    assert stats["newest_queued_at"] is not None

    # Flush attempt while offline safely leaves items in local buffer
    flush_res = sync.flush_sync_queue()
    assert flush_res["status"] == "BUFFERED_OFFLINE"
    assert flush_res["buffered_count"] == 2

    # Verify original timestamps preserved
    pending = store.get_pending_sync_items()
    assert len(pending) == 2
    import json
    p1 = json.loads(pending[0]["payload_json"])
    assert p1["timestamp"] == reading_ts
    assert p1["sequence"] == 101

def test_reconnect_and_idempotent_draining(edge_env):
    """CP 7H-01 & 7H-02: Reconnecting drains buffer, marks synced, and avoids duplication."""
    store, sync = edge_env
    sync.set_cloud_connectivity(False)

    store.register_reading({"node_id": "PZ-02", "sequence": 1, "timestamp": "2026-09-11T07:00:00Z"}, buffer_for_cloud=True)
    store.register_reading({"node_id": "PZ-02", "sequence": 2, "timestamp": "2026-09-11T07:02:00Z"}, buffer_for_cloud=True)

    # Reconnect backhaul
    sync.set_cloud_connectivity(True)
    assert sync.is_cloud_connected is True

    flush_res = sync.flush_sync_queue()
    assert flush_res["status"] == "SYNCED"
    assert flush_res["flushed_count"] == 2

    # Second flush should report up to date (idempotent)
    second_flush = sync.flush_sync_queue()
    assert second_flush["status"] == "UP_TO_DATE"
    assert second_flush["buffered_count"] == 0

def test_storage_capacity_and_overflow_tracking(edge_env):
    """CP 7H-02: Edge storage capacity and overflow boundaries are tracked."""
    store, sync = edge_env
    stats = store.get_queue_stats()
    assert "capacity_bytes" in stats
    assert "used_storage_bytes" in stats
    assert "storage_used_pct" in stats
    assert stats["is_overflow"] is False
    assert stats["overflow_policy"] == "OLDEST_DROP_WITH_QUARANTINE"

def test_packet_checksum_validation():
    """CP 7H-02: 16-bit CRC / checksum is verified on incoming raw packets."""
    payload = b"\x01\x02\x03\x04\x05"
    expected_crc = sum(payload) & 0xFFFF
    assert EdgeStore.verify_packet_checksum(payload, expected_crc) is True
    assert EdgeStore.verify_packet_checksum(payload, expected_crc + 1) is False
    assert EdgeStore.verify_packet_checksum(b"") is False

def test_edge_gateway_power_telemetry(edge_env):
    """CP 7H-09: Tracks gateway battery, shutdown signals, and recovery."""
    store, _ = edge_env
    normal = store.set_gateway_power("NORMAL", 95)
    assert normal["power_status"] == "NORMAL"
    assert normal["is_critical"] is False

    crit = store.set_gateway_power("BATTERY_CRITICAL", 12)
    assert crit["is_critical"] is True

    down = store.set_gateway_power("SHUTDOWN", 4)
    assert down["safe_shutdown_engaged"] is True

    recovered = store.set_gateway_power("RECOVERED", 100)
    assert recovered["power_status"] == "RECOVERED"
    assert recovered["is_critical"] is False
