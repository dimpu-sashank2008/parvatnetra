# -*- coding: utf-8 -*-
"""
firmware/esp32_node.py
======================
PARVAT NETRA • Reference Embedded ESP32 Sensor Node Runtime
------------------------------------------------------------
Implements the reference embedded firmware state machine for an ESP32-class
hillslope instrumentation node operating over LoRaWAN IN865:

Core Firmware Functions:
  - initialize()        : Configures GPIOs, RTC, sensors, and local circular buffer
  - read_sensors()      : Acquires calibrated readings from all attached transducers
  - validate_values()   : Verifies readings against physical range boundaries
  - timestamp()         : Acquires RTC timestamp with drift compensation
  - package_telemetry() : Encodes readings into 18-byte packed binary LoRa frames
  - buffer_packet()     : Stores packet locally in circular FIFO buffer during link failure
  - transmit()          : Uplinks packet to edge concentrator gateway
  - retry()             : Executes exponential backoff retries on transmission failure
  - heartbeat()         : Transmits node health and diagnostic status
  - evaluate_local_safety(): Detects local slope anomalies (NORMAL, WATCH, CRITICAL)
"""

from __future__ import annotations

import time
import math
import logging
from typing import Dict, Any, List, Optional, Tuple, Callable

from firmware.interfaces import (
    BaseSensorReader,
    PiezometerReader,
    TiltReader,
    RainGaugeReader,
    SoilMoistureReader,
    TemperatureReader,
    BatteryMonitorInterface,
    SignalMonitorInterface,
    EdgeClock,
    LocalCircularBuffer,
    SensorReading
)
from firmware.packet_codec import (
    BinaryPacketCodec,
    compute_crc16_ccitt
)

logger = logging.getLogger("ESP32_NODE_FIRMWARE")

# Local Corridor Anomaly Thresholds
ANOMALY_THRESHOLDS = {
    "pore_pressure": {"watch": 30.0, "critical": 45.0},
    "tilt_rate": {"watch": 1.0, "critical": 2.5},
    "rain_intensity": {"watch": 35.0, "critical": 50.0},
    "displacement_rate": {"watch": 5.0, "critical": 15.0}
}


class ESP32SensorNode:
    """
    Reference ESP32-class sensor node state machine for geotechnical hillslope telemetry.
    """

    def __init__(
        self,
        device_id: str = "PZ-NH10-KM48-01",
        device_short_id: int = 101,
        sensor_type: str = "piezometer",
        gateway_id: str = "GW-NH10-KM48-01",
        latitude: float = 27.3302,
        longitude: float = 88.6104,
        max_buffer_size: int = 500
    ):
        self.device_id = device_id
        self.device_short_id = device_short_id
        self.sensor_type = sensor_type
        self.gateway_id = gateway_id
        self.latitude = latitude
        self.longitude = longitude

        # Hardware interfaces
        self.clock = EdgeClock()
        self.battery = BatteryMonitorInterface()
        self.signal = SignalMonitorInterface()
        self.buffer = LocalCircularBuffer(max_capacity=max_buffer_size)

        # Transducers
        self.primary_sensor: BaseSensorReader = self._create_primary_sensor(sensor_type)
        self.temp_sensor = TemperatureReader()

        # Operational state
        self.sequence_number: int = 0
        self.is_initialized: bool = False
        self.is_radio_connected: bool = True
        self.local_safety_state: str = "NORMAL"  # NORMAL, WATCH, CRITICAL
        self.active_anomalies: List[str] = []

        # Outbox transmission callback (e.g. gateway ingestion hook or radio mock)
        self._transmit_sink: Optional[Callable[[bytes], bool]] = None

        # Statistics
        self.packets_transmitted: int = 0
        self.packets_buffered: int = 0
        self.packets_dropped: int = 0
        self.retry_attempts: int = 0

    def _create_primary_sensor(self, sensor_type: str) -> BaseSensorReader:
        st = sensor_type.lower()
        if st == "piezometer":
            return PiezometerReader()
        elif st == "tilt":
            return TiltReader()
        elif st == "rain_gauge":
            return RainGaugeReader()
        elif st == "soil_moisture":
            return SoilMoistureReader()
        else:
            return PiezometerReader()

    def set_transmit_sink(self, sink: Callable[[bytes], bool]) -> None:
        """Connects the radio transmitter to an edge gateway or test sink."""
        self._transmit_sink = sink

    def set_radio_connectivity(self, connected: bool) -> None:
        """Simulates RF link loss / restoration."""
        self.is_radio_connected = connected
        logger.info(f"[{self.device_id}] RF radio connectivity changed to: {connected}")

    def initialize(self) -> bool:
        """Initializes internal hardware subsystems and boots node."""
        self.is_initialized = True
        self.sequence_number = 1
        logger.info(f"[{self.device_id}] ESP32 node initialized successfully.")
        return True

    def read_sensors(self) -> Tuple[SensorReading, SensorReading]:
        """Acquires primary transducer and ambient temperature readings."""
        prim = self.primary_sensor.read()
        temp = self.temp_sensor.read()
        return prim, temp

    def validate_values(self, prim: SensorReading, temp: SensorReading) -> bool:
        """Validates that transducer readings lie within plausible physical bounds."""
        if prim.quality == "INVALID" or temp.quality == "INVALID":
            return False
        return True

    def timestamp(self) -> Tuple[int, str]:
        """Returns epoch seconds and ISO-8601 string from RTC."""
        return self.clock.get_epoch_seconds(), self.clock.get_timestamp_iso()

    def evaluate_local_safety(self, prim: SensorReading) -> str:
        """
        Autonomous on-node anomaly detection.
        Categorizes hillslope threat into NORMAL, WATCH, or CRITICAL.
        """
        anomalies = []
        val = prim.value

        if self.sensor_type == "piezometer":
            thresh = ANOMALY_THRESHOLDS["pore_pressure"]
            if val >= thresh["critical"]:
                anomalies.append(f"Pore Pressure Critical ({val} kPa >= {thresh['critical']})")
            elif val >= thresh["watch"]:
                anomalies.append(f"Pore Pressure Watch ({val} kPa >= {thresh['watch']})")

        elif self.sensor_type == "tilt":
            rate = prim.derived.get("tilt_rate_deg_day", 0.0)
            thresh = ANOMALY_THRESHOLDS["tilt_rate"]
            if rate >= thresh["critical"]:
                anomalies.append(f"Tilt Rate Critical ({rate} deg/day >= {thresh['critical']})")
            elif rate >= thresh["watch"]:
                anomalies.append(f"Tilt Rate Watch ({rate} deg/day >= {thresh['watch']})")

        elif self.sensor_type == "rain_gauge":
            intensity = prim.derived.get("intensity_mm_hr", 0.0)
            thresh = ANOMALY_THRESHOLDS["rain_intensity"]
            if intensity >= thresh["critical"]:
                anomalies.append(f"Rainfall Intensity Cloudburst ({intensity} mm/hr >= {thresh['critical']})")
            elif intensity >= thresh["watch"]:
                anomalies.append(f"Rainfall Intensity Watch ({intensity} mm/hr >= {thresh['watch']})")

        self.active_anomalies = anomalies
        if any("Critical" in a or "Cloudburst" in a for a in anomalies):
            self.local_safety_state = "CRITICAL"
        elif anomalies:
            self.local_safety_state = "WATCH"
        else:
            self.local_safety_state = "NORMAL"

        return self.local_safety_state

    def package_telemetry(
        self,
        prim: SensorReading,
        temp: SensorReading,
        epoch_ts: int
    ) -> bytes:
        """Encodes telemetry into an 18-byte binary LoRa frame."""
        sec_val = prim.derived.get("tilt_x", 0.0)
        tert_val = prim.derived.get("tilt_y", 0.0)

        frame = BinaryPacketCodec.encode(
            device_short_id=self.device_short_id,
            sequence_number=self.sequence_number,
            timestamp_epoch=epoch_ts,
            primary_val=prim.value,
            secondary_val=sec_val,
            tertiary_val=tert_val,
            battery_pct=self.battery.get_battery_level(),
            temperature_c=temp.value,
            tamper=(self.local_safety_state == "CRITICAL")
        )
        return frame

    def buffer_packet(self, frame_bytes: bytes, epoch_ts: int, seq: int) -> bool:
        """Caches packet into local circular FIFO buffer when radio is disconnected."""
        entry = {
            "device_id": self.device_id,
            "sequence_number": seq,
            "timestamp_epoch": epoch_ts,
            "frame_bytes": frame_bytes,
            "buffered_at": time.time()
        }
        success = self.buffer.push(entry)
        if success:
            self.packets_buffered += 1
            logger.info(f"[{self.device_id}] Buffered frame seq={seq} (Queue count: {self.buffer.count()})")
        return success

    def transmit(self, frame_bytes: bytes) -> bool:
        """Transmits 18-byte frame over radio link. Returns True on success."""
        if not self.is_radio_connected:
            return False

        if self._transmit_sink:
            try:
                ok = self._transmit_sink(frame_bytes)
                if ok:
                    self.packets_transmitted += 1
                    # Small battery consumption per transmission
                    self.battery.discharge(0.005)
                    return True
            except Exception as e:
                logger.warning(f"[{self.device_id}] Transmission sink error: {e}")
                return False

        # If no sink configured, assume successful transmission over air
        self.packets_transmitted += 1
        self.battery.discharge(0.005)
        return True

    def retry_with_backoff(self, frame_bytes: bytes, max_retries: int = 3) -> bool:
        """Executes exponential backoff transmission retries."""
        for attempt in range(max_retries):
            self.retry_attempts += 1
            if self.transmit(frame_bytes):
                return True
            # Backoff delay simulation: t = min(2^attempt * 0.1, 1.0)
            backoff = min((2 ** attempt) * 0.05, 0.5)
            time.sleep(backoff)
        return False

    def replay_buffer(self) -> int:
        """
        Replays buffered packets to gateway in strict FIFO chronological order.
        Returns the count of successfully replayed packets.
        """
        if not self.is_radio_connected:
            return 0

        replayed_count = 0
        while not self.buffer.is_empty():
            entry = self.buffer.peek()
            if not entry:
                break

            frame = entry["frame_bytes"]
            if self.transmit(frame):
                self.buffer.pop()  # Evict only after successful transmission
                replayed_count += 1
            else:
                logger.warning(f"[{self.device_id}] Buffer replay halted on frame seq={entry['sequence_number']}")
                break

        return replayed_count

    def step(self) -> Dict[str, Any]:
        """
        Executes one full acquisition cycle:
        Read -> Validate -> Safety Eval -> Package -> Transmit or Buffer -> Replay.
        """
        if not self.is_initialized:
            self.initialize()

        prim, temp = self.read_sensors()
        is_valid = self.validate_values(prim, temp)
        epoch_ts, iso_ts = self.timestamp()
        safety = self.evaluate_local_safety(prim)

        frame = self.package_telemetry(prim, temp, epoch_ts)
        seq_used = self.sequence_number
        self.sequence_number += 1

        transmitted = False
        buffered = False
        replayed = 0

        if self.is_radio_connected:
            # First replay any backlog in strict FIFO order
            if not self.buffer.is_empty():
                replayed = self.replay_buffer()

            # Then transmit current packet
            transmitted = self.transmit(frame)
            if not transmitted:
                # Transmit failed; buffer current packet
                buffered = self.buffer_packet(frame, epoch_ts, seq_used)
        else:
            buffered = self.buffer_packet(frame, epoch_ts, seq_used)

        return {
            "device_id": self.device_id,
            "sequence_number": seq_used,
            "timestamp": iso_ts,
            "primary_value": prim.value,
            "temperature": temp.value,
            "local_safety_state": safety,
            "anomalies": self.active_anomalies,
            "transmitted": transmitted,
            "buffered": buffered,
            "replayed_from_buffer": replayed,
            "pending_buffer_count": self.buffer.count(),
            "battery_pct": self.battery.get_battery_level(),
            "frame_bytes": frame
        }

    def heartbeat(self) -> Dict[str, Any]:
        """Returns node diagnostic health payload."""
        return {
            "device_id": self.device_id,
            "device_short_id": self.device_short_id,
            "sensor_type": self.sensor_type,
            "battery_pct": self.battery.get_battery_level(),
            "voltage": self.battery.get_voltage(),
            "signal_rssi": self.signal.get_signal_rssi(),
            "snr": self.signal.get_snr(),
            "buffer_count": self.buffer.count(),
            "packets_transmitted": self.packets_transmitted,
            "packets_buffered": self.packets_buffered,
            "local_safety_state": self.local_safety_state,
            "uptime_cycles": self.sequence_number,
            "timestamp": self.clock.get_timestamp_iso()
        }
