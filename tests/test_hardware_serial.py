# -*- coding: utf-8 -*-
"""
tests/test_hardware_serial.py
=============================
Phase 6C Test Suite: Hardware-In-The-Loop Serial/USB Interface & Port Detection
"""

import sys
import os
import time
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.hardware_interface import (
    HardwareDetector,
    HardwareInTheLoopInterface,
    STATE_NO_PHYSICAL_DEVICE,
    STATE_BENCH_SIMULATOR,
    STATE_PHYSICAL_DEVICE_CONNECTED,
    STATE_PHYSICAL_DEVICE_ACTIVE
)
from firmware.packet_codec import BinaryPacketCodec
from engine.sensor_registry import (
    SensorRegistry,
    SensorDevice,
    STATUS_ACTIVE,
    STATUS_REGISTERED
)


@pytest.fixture
def hitl_env():
    # Clean env
    old_bench = os.environ.pop("PAHAD_HARDWARE_TEST_MODE", None)
    old_mock = os.environ.pop("MOCK_PHYSICAL_PORT_ATTACHED", None)
    yield
    if old_bench is not None:
        os.environ["PAHAD_HARDWARE_TEST_MODE"] = old_bench
    if old_mock is not None:
        os.environ["MOCK_PHYSICAL_PORT_ATTACHED"] = old_mock


class TestHardwareSerialDetection:

    def test_no_physical_device_default(self, hitl_env):
        with patch.object(HardwareDetector, "list_serial_ports", return_value=[]):
            status = HardwareDetector.detect_status()
            assert status["status"] == STATE_NO_PHYSICAL_DEVICE
            assert "PHYSICAL_DEPLOYMENT_PENDING" in status["detail"]
            assert status["has_physical_port"] is False

    def test_bench_simulator_mode_env_flag(self, hitl_env):
        os.environ["PAHAD_HARDWARE_TEST_MODE"] = "1"
        status = HardwareDetector.detect_status()
        assert status["status"] == STATE_BENCH_SIMULATOR
        assert status["provenance"] == "[SIMULATED]"

    def test_physical_port_connected_uncommissioned_node(self, hitl_env):
        os.environ["MOCK_PHYSICAL_PORT_ATTACHED"] = "1"
        status = HardwareDetector.detect_status(active_device_id="UNCOMMISSIONED-DEV")
        assert status["status"] == STATE_PHYSICAL_DEVICE_CONNECTED
        assert status["provenance"] == "[SIMULATED]"  # Not marked LIVE!

    def test_physical_device_active_when_commissioned(self, hitl_env):
        os.environ["MOCK_PHYSICAL_PORT_ATTACHED"] = "1"
        from engine.sensor_registry import GLOBAL_SENSOR_REGISTRY
        dev = SensorDevice(
            device_id="SERIAL-ACTIVE-01",
            sensor_id="SERIAL-ACTIVE-01",
            sensor_type="piezometer",
            latitude=27.33,
            longitude=88.61,
            sector_id="SK-NH10-KM48",
            status=STATUS_ACTIVE
        )
        GLOBAL_SENSOR_REGISTRY.register_device(dev)

        status = HardwareDetector.detect_status(active_device_id="SERIAL-ACTIVE-01")
        assert status["status"] == STATE_PHYSICAL_DEVICE_ACTIVE
        assert status["provenance"] == "[LIVE]"


class TestHardwareInTheLoopInterface:

    def test_clock_offset_calculation_nominal(self):
        hitl = HardwareInTheLoopInterface()
        now_ts = time.time()
        offset_ms, is_valid, reason = hitl.calculate_clock_offset(now_ts)
        assert is_valid is True
        assert abs(offset_ms) < 2000.0  # within 2 seconds

    def test_future_timestamp_rejected(self):
        hitl = HardwareInTheLoopInterface()
        future_ts = time.time() + 60.0  # 1 minute in the future
        offset_ms, is_valid, reason = hitl.calculate_clock_offset(future_ts)
        assert is_valid is False
        assert "Future timestamp detected" in reason

    def test_stale_timestamp_rejected(self):
        hitl = HardwareInTheLoopInterface()
        stale_ts = time.time() - 600.0  # 10 minutes in the past
        offset_ms, is_valid, reason = hitl.calculate_clock_offset(stale_ts)
        assert is_valid is False
        assert "Clock drift excessive" in reason

    def test_process_binary_stream_frame(self, hitl_env):
        hitl = HardwareInTheLoopInterface()
        frame = BinaryPacketCodec.encode(
            device_short_id=101,
            sequence_number=1,
            timestamp_epoch=int(time.time()),
            primary_val=34.5,
            battery_pct=95.0,
            temperature_c=19.0
        )
        res = hitl.process_binary_stream_frame(frame, sensor_type="piezometer", transport="SERIAL")
        assert res["status"] == "ACCEPTED"
        assert res["device_id"] == "SN-NODE-0101"

    def test_process_malformed_binary_stream(self):
        hitl = HardwareInTheLoopInterface()
        bad_frame = b"\x00" * 10
        res = hitl.process_binary_stream_frame(bad_frame, transport="SERIAL")
        assert res["status"] == "REJECTED_MALFORMED_FRAME"

    def test_process_json_stream_payload(self):
        hitl = HardwareInTheLoopInterface()
        from datetime import datetime, timezone
        payload = {
            "device_id": "HITL-DEV-JSON-01",
            "sequence_number": 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": 27.3302,
            "longitude": 88.6104,
            "battery": 94.0,
            "signal_quality": -70.0,
            "measurements": {
                "pore_pressure": {"value": 31.5, "unit": "kPa"}
            }
        }
        res = hitl.process_json_stream_payload(payload, transport="SERIAL")
        assert res["status"] == "ACCEPTED"
