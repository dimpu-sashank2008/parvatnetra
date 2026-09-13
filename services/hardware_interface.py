# -*- coding: utf-8 -*-
"""
services/hardware_interface.py
==============================
PARVAT NETRA • Hardware-In-The-Loop (HITL) & Physical Device Interface
----------------------------------------------------------------------
Manages physical serial/USB, TCP, and MQTT telemetry streams from bench or
field-deployed ESP32 and Raspberry Pi controllers.

State Classification:
  - NO_PHYSICAL_DEVICE        : No hardware port or device detected
  - BENCH_SIMULATOR           : Operating under isolated bench simulator harness
  - PHYSICAL_DEVICE_CONNECTED : Physical serial/USB port detected, but device not commissioned
  - PHYSICAL_DEVICE_ACTIVE    : Physical hardware connected, authenticated, and commissioned ACTIVE

Timekeeping & Drift:
  Calculates clock_offset_ms across device timestamp, gateway arrival, and central server.
  Rejects timestamp anomalies (>300s drift or future timestamps >10s).
"""

from __future__ import annotations

import os
import io
import time
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable

from firmware.packet_codec import (
    BinaryPacketCodec,
    FRAME_LENGTH_BYTES
)
from engine.sensor_registry import (
    GLOBAL_SENSOR_REGISTRY,
    STATUS_ACTIVE,
    STATUS_COMMISSIONING,
    STATUS_REGISTERED
)
from services.telemetry_contract import (
    GLOBAL_TELEMETRY_VALIDATOR,
    ValidationResult
)
from services.edge_gateway import (
    GLOBAL_EDGE_GATEWAY_SERVICE
)

logger = logging.getLogger("HARDWARE_INTERFACE")

# Optional PySerial import
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    serial = None
    SERIAL_AVAILABLE = False


# Physical Device States
STATE_NO_PHYSICAL_DEVICE = "NO_PHYSICAL_DEVICE"
STATE_BENCH_SIMULATOR = "BENCH_SIMULATOR"
STATE_PHYSICAL_DEVICE_CONNECTED = "PHYSICAL_DEVICE_CONNECTED"
STATE_PHYSICAL_DEVICE_ACTIVE = "PHYSICAL_DEVICE_ACTIVE"

# Max acceptable drift in seconds (5 minutes past, 10 seconds future)
MAX_CLOCK_DRIFT_PAST_SEC = 300.0
MAX_CLOCK_DRIFT_FUTURE_SEC = 10.0


class HardwareDetector:
    """Discovers attached hardware devices and determines operational state."""

    @staticmethod
    def list_serial_ports() -> List[Dict[str, str]]:
        """Enumerates connected serial and USB-to-UART ports."""
        ports_list = []
        if SERIAL_AVAILABLE and serial and hasattr(serial, "tools") and hasattr(serial.tools, "list_ports"):
            try:
                for p in serial.tools.list_ports.comports():
                    ports_list.append({
                        "device": p.device,
                        "description": p.description,
                        "hwid": p.hwid,
                        "manufacturer": getattr(p, "manufacturer", "Unknown") or "Unknown"
                    })
            except Exception as e:
                logger.warning(f"Error enumerating serial ports: {e}")
        return ports_list

    @classmethod
    def detect_status(cls, active_device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Determines current physical device attachment state.
        Never marks connected hardware as LIVE or ACTIVE unless certified in SensorRegistry.
        """
        is_bench_mode = (
            os.environ.get("PAHAD_HARDWARE_TEST_MODE") == "1" or
            os.environ.get("PAHAD_BENCH_MODE") == "1"
        )

        ports = cls.list_serial_ports()
        has_physical_port = len(ports) > 0 or os.environ.get("MOCK_PHYSICAL_PORT_ATTACHED") == "1"

        if is_bench_mode:
            state = STATE_BENCH_SIMULATOR
            provenance = "[SIMULATED]"
            detail = "Operating under isolated bench simulator harness"
        elif not has_physical_port:
            state = STATE_NO_PHYSICAL_DEVICE
            provenance = "[HISTORICAL]"
            detail = "No physical serial or USB instrumentation attached. Status: PHYSICAL_DEPLOYMENT_PENDING"
        else:
            # Physical port detected. Verify if device is commissioned in registry.
            if active_device_id:
                dev = GLOBAL_SENSOR_REGISTRY.get_device(active_device_id)
                if dev and dev.status == STATUS_ACTIVE:
                    state = STATE_PHYSICAL_DEVICE_ACTIVE
                    provenance = "[LIVE]"
                    detail = f"Physical device {active_device_id} active and certified on port."
                else:
                    state = STATE_PHYSICAL_DEVICE_CONNECTED
                    provenance = "[SIMULATED]"
                    detail = f"Hardware port detected, but device '{active_device_id}' is not commissioned ACTIVE."
            else:
                state = STATE_PHYSICAL_DEVICE_CONNECTED
                provenance = "[SIMULATED]"
                detail = "Hardware port detected. Commissioning required before live telemetry trust."

        return {
            "status": state,
            "provenance": provenance,
            "has_physical_port": has_physical_port,
            "port_count": len(ports),
            "ports": ports,
            "is_bench_mode": is_bench_mode,
            "detail": detail,
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }


class HardwareInTheLoopInterface:
    """
    Ingests and normalizes telemetry streams across Serial, USB, TCP, and MQTT transports.
    Calculates clock drift and enforces timestamp synchronization safety.
    """

    def __init__(self, gateway_id: str = "GW-NH10-KM48-01"):
        self.gateway_id = gateway_id
        self.detector = HardwareDetector()
        self.active_stream_type: str = "BENCH"  # SERIAL, USB, TCP, MQTT, BENCH
        self.last_clock_offset_ms: float = 0.0
        self.total_frames_processed: int = 0
        self.total_drift_rejections: int = 0

    def calculate_clock_offset(
        self, device_epoch_sec: float, gateway_epoch_sec: Optional[float] = None
    ) -> Tuple[float, bool, str]:
        """
        Calculates clock offset: offset_ms = (server_time - device_time) * 1000
        Returns (offset_ms, is_valid, reason)
        """
        now_server = time.time()
        gw_time = gateway_epoch_sec or now_server

        # Offset between server and device
        offset_sec = now_server - device_epoch_sec
        offset_ms = round(offset_sec * 1000.0, 2)

        # Future timestamp check (device is significantly ahead of server)
        if offset_sec < -MAX_CLOCK_DRIFT_FUTURE_SEC:
            return (
                offset_ms,
                False,
                f"Future timestamp detected: device clock is {-offset_sec:.1f}s ahead of server"
            )

        # Stale timestamp check (device is too far in the past)
        if offset_sec > MAX_CLOCK_DRIFT_PAST_SEC:
            return (
                offset_ms,
                False,
                f"Clock drift excessive: device timestamp is {offset_sec:.1f}s behind server"
            )

        return offset_ms, True, "OK"

    def process_binary_stream_frame(
        self,
        frame_bytes: bytes,
        sensor_type: str = "piezometer",
        transport: str = "SERIAL"
    ) -> Dict[str, Any]:
        """
        Decodes raw binary frame from serial or TCP, computes timekeeping offset,
        and forwards to EdgeGatewayService.
        """
        self.total_frames_processed += 1

        # 1. Decode frame
        try:
            decoded = BinaryPacketCodec.decode(frame_bytes)
        except Exception as e:
            logger.warning(f"Binary frame decode error: {e}")
            return {
                "status": "REJECTED_MALFORMED_FRAME",
                "message": f"Frame decoding error: {str(e)}",
                "transport": transport
            }

        dev_epoch = decoded["timestamp_epoch"]

        # 2. Clock Drift Analysis
        offset_ms, drift_ok, drift_reason = self.calculate_clock_offset(dev_epoch)
        self.last_clock_offset_ms = offset_ms

        if not drift_ok:
            self.total_drift_rejections += 1
            logger.warning(f"Rejected frame due to clock drift: {drift_reason}")
            return {
                "status": "REJECTED_CLOCK_DRIFT_EXCESSIVE",
                "message": drift_reason,
                "clock_offset_ms": offset_ms,
                "device_short_id": decoded["device_short_id"]
            }

        # 3. Build Canonical Packet
        det = self.detector.detect_status()
        prov = "[LIVE]" if det["status"] == STATE_PHYSICAL_DEVICE_ACTIVE else "[SIMULATED]"

        canonical = BinaryPacketCodec.to_canonical_packet(
            frame_bytes,
            sensor_type=sensor_type,
            gateway_id=self.gateway_id,
            provenance=prov
        )
        canonical["clock_offset_ms"] = offset_ms
        canonical["transport"] = transport

        # 4. Ingest via Edge Gateway
        ingest_res = GLOBAL_EDGE_GATEWAY_SERVICE.ingest_sensor_packet(canonical, transport=transport)
        ingest_res["clock_offset_ms"] = offset_ms
        ingest_res["device_hardware_state"] = det["status"]

        return ingest_res

    def process_json_stream_payload(
        self,
        raw_json: Dict[str, Any],
        transport: str = "SERIAL"
    ) -> Dict[str, Any]:
        """
        Processes newline-delimited JSON payload received over Serial/USB/TCP.
        """
        self.total_frames_processed += 1

        # Extract timestamp if present
        raw_ts = raw_json.get("timestamp")
        if raw_ts:
            try:
                dt = datetime.fromisoformat(str(raw_ts).replace("Z", "+00:00"))
                dev_epoch = dt.timestamp()
                offset_ms, drift_ok, drift_reason = self.calculate_clock_offset(dev_epoch)
                self.last_clock_offset_ms = offset_ms
                if not drift_ok:
                    self.total_drift_rejections += 1
                    return {
                        "status": "REJECTED_CLOCK_DRIFT_EXCESSIVE",
                        "message": drift_reason,
                        "clock_offset_ms": offset_ms
                    }
            except Exception:
                offset_ms = 0.0
        else:
            offset_ms = 0.0

        raw_json["gateway_id"] = self.gateway_id
        raw_json["clock_offset_ms"] = offset_ms

        det = self.detector.detect_status()
        if det["status"] != STATE_PHYSICAL_DEVICE_ACTIVE:
            raw_json["provenance"] = "[SIMULATED]"

        return GLOBAL_EDGE_GATEWAY_SERVICE.ingest_sensor_packet(raw_json, transport=transport)

    def get_status(self) -> Dict[str, Any]:
        """Returns HITL interface status and diagnostics."""
        det = self.detector.detect_status()
        return {
            "gateway_id": self.gateway_id,
            "hardware_state": det["status"],
            "provenance": det["provenance"],
            "has_physical_port": det["has_physical_port"],
            "ports": det["ports"],
            "is_bench_mode": det["is_bench_mode"],
            "total_frames_processed": self.total_frames_processed,
            "total_drift_rejections": self.total_drift_rejections,
            "last_clock_offset_ms": self.last_clock_offset_ms,
            "detail": det["detail"]
        }


# Global Singleton HITL Interface
GLOBAL_HARDWARE_INTERFACE = HardwareInTheLoopInterface()
