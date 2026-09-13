# -*- coding: utf-8 -*-
"""
firmware package
================
PARVAT NETRA • In-Situ Geotechnical Sensor Firmware Abstraction
"""

from firmware.interfaces import (
    SensorReading,
    BaseSensorReader,
    PiezometerReader,
    TiltReader,
    RainGaugeReader,
    SoilMoistureReader,
    TemperatureReader,
    BatteryMonitorInterface,
    SignalMonitorInterface,
    EdgeClock,
    LocalCircularBuffer
)
from firmware.packet_codec import (
    BinaryPacketCodec,
    compute_crc16_ccitt,
    FRAME_LENGTH_BYTES
)
from firmware.esp32_node import (
    ESP32SensorNode,
    ANOMALY_THRESHOLDS
)

__all__ = [
    "SensorReading",
    "BaseSensorReader",
    "PiezometerReader",
    "TiltReader",
    "RainGaugeReader",
    "SoilMoistureReader",
    "TemperatureReader",
    "BatteryMonitorInterface",
    "SignalMonitorInterface",
    "EdgeClock",
    "LocalCircularBuffer",
    "BinaryPacketCodec",
    "compute_crc16_ccitt",
    "FRAME_LENGTH_BYTES",
    "ESP32SensorNode",
    "ANOMALY_THRESHOLDS"
]
