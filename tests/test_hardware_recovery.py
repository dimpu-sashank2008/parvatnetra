# -*- coding: utf-8 -*-
"""
tests/test_hardware_recovery.py
===============================
Phase 6C Test Suite: Power Failure, Gateway Reboot & Network Outage Recovery
"""

import sys
import os
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.edge_gateway import EdgeGatewayService
from services.bench_simulator import BenchSimulator
from engine.observation_store import ObservationStore
from firmware.esp32_node import ESP32SensorNode


@pytest.fixture
def isolated_gateway(tmp_path):
    buf_path = str(tmp_path / "edge_buffer_test.db")
    return EdgeGatewayService(gateway_id="GW-RECOVERY-TEST", sector_id="SK-NH10-KM48")


class TestHardwareRecovery:

    def test_network_outage_local_buffering_and_restoration_flush(self, isolated_gateway):
        gw = isolated_gateway
        sim = BenchSimulator(default_device_id="DEV-OUTAGE-01", default_gateway_id=gw.gateway_id)

        # 1. Sever backhaul connectivity
        gw.set_cloud_connectivity(False)
        assert gw.is_cloud_connected is False

        # Ingest 5 packets during network partition
        for i in range(5):
            pkt = sim.generate_packet()
            res = gw.ingest_sensor_packet(pkt)
            assert res["status"] == "BUFFERED_OFFLINE"

        assert gw.buffer.count_buffered() == 5

        # 2. Restore backhaul connectivity
        gw.set_cloud_connectivity(True)
        assert gw.is_cloud_connected is True

        # Flush buffer to observation store
        flush_res = gw.flush_buffer(batch_size=10)
        assert flush_res["status"] == "SUCCESS"
        assert flush_res["synced_count"] == 5
        assert flush_res["remaining_count"] == 0

    def test_gateway_restart_preserves_offline_buffer(self, tmp_path):
        db_path = str(tmp_path / "restart_persist.db")
        old_path = os.environ.get("EDGE_BUFFER_DB_PATH")
        os.environ["EDGE_BUFFER_DB_PATH"] = db_path

        try:
            gw1 = EdgeGatewayService(gateway_id="GW-PERSIST", sector_id="SK-NH10-KM48")
            gw1.set_cloud_connectivity(False)

            sim = BenchSimulator(default_device_id="DEV-REBOOT-01", default_gateway_id="GW-PERSIST")
            pkt = sim.generate_packet()
            res = gw1.ingest_sensor_packet(pkt)
            assert res["status"] == "BUFFERED_OFFLINE"
            assert gw1.buffer.count_buffered() == 1

            # Simulate gateway power cycle / process restart
            gw2 = EdgeGatewayService(gateway_id="GW-PERSIST", sector_id="SK-NH10-KM48")
            assert gw2.buffer.count_buffered() == 1  # Retained across restart!

            # Sync after reboot
            flush_res = gw2.flush_buffer()
            assert flush_res["synced_count"] == 1
            assert gw2.buffer.count_buffered() == 0
        finally:
            if old_path:
                os.environ["EDGE_BUFFER_DB_PATH"] = old_path
            else:
                os.environ.pop("EDGE_BUFFER_DB_PATH", None)

    def test_node_reboot_sequence_continuity(self):
        node = ESP32SensorNode(device_id="DEV-RESTART-01")
        node.initialize()
        node.step()
        node.step()
        last_seq = node.sequence_number

        # Simulate power cut and restart
        restarted_node = ESP32SensorNode(device_id="DEV-RESTART-01")
        restarted_node.initialize()
        # Fast-forward sequence counter to prevent replay collisions
        restarted_node.sequence_number = last_seq

        res = restarted_node.step()
        assert res["sequence_number"] == last_seq
        assert res["sequence_number"] > 1
