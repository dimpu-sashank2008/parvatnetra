# -*- coding: utf-8 -*-
"""
backend/edge/adapters.py
========================
PARVAT NETRA • Hardware Abstraction Layer & Simulated Edge Adapters
------------------------------------------------------------------
Implements Section 27, 28, 29: Concrete and mock hardware adapter interfaces:
  1. MockSensorAdapter (Simulates ESP32 in-situ sensor cluster)
  2. MockLoRaAdapter (Simulates SX1262/SX1276 sub-GHz transceiver)
  3. MockBLEAdapter (Simulates Nordic nRF52840 BLE 5.3 Long Range PHY)
  4. MockSirenAdapter (Simulates industrial 12V relay siren horn GPIO)
  5. MQTTAdapter (Optional lightweight pub/sub interface)

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger("EDGE_HARDWARE_ADAPTERS")


class BaseAdapter:
    """Abstract base class for physical/simulated edge peripherals."""
    def __init__(self, name: str, hardware_connected: bool = False) -> None:
        self.name = name
        self.hardware_connected = hardware_connected
        self.is_initialized = False

    def initialize(self) -> bool:
        self.is_initialized = True
        return True

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "hardware_connected": self.hardware_connected,
            "is_initialized": self.is_initialized,
            "mode": "[LIVE_HARDWARE]" if self.hardware_connected else "[SIMULATED / ADAPTER_STUB]"
        }


class MockSensorAdapter(BaseAdapter):
    """Simulates physical ESP32 analog/I2C sensor read cycles."""

    def __init__(self, node_id: str = "ESP32-NODE-01") -> None:
        super().__init__(name=f"MockSensorAdapter-{node_id}", hardware_connected=False)
        self.node_id = node_id

    def read_physical_sensors(self) -> Dict[str, Any]:
        """Returns physical sensor voltages scaled to geotechnical SI units."""
        return {
            "node_id": self.node_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "adc_soil_moisture_mv": 1820,
            "adc_pore_pressure_mv": 1240,
            "i2c_tilt_pitch_deg": 0.14,
            "i2c_tilt_roll_deg": 0.08,
            "pulse_rain_gauge_ticks": 3,
            "battery_mv": 3950,
            "mode": "[SIMULATED / ESP32_VIRTUAL]"
        }


class MockLoRaAdapter(BaseAdapter):
    """Simulates Semtech SX1262 LoRa SPI radio transceiver."""

    def __init__(self, frequency_mhz: float = 865.2) -> None:
        super().__init__(name="MockLoRaAdapter-SX1262", hardware_connected=False)
        self.frequency_mhz = frequency_mhz
        self.tx_power_dbm = 14
        self.spreading_factor = 7

    def transmit_rf(self, raw_bytes: bytes) -> Dict[str, Any]:
        """Simulates over-the-air radio transmission."""
        return {
            "status": "TRANSMITTED_SIMULATED",
            "bytes_sent": len(raw_bytes),
            "frequency_mhz": self.frequency_mhz,
            "tx_power_dbm": self.tx_power_dbm,
            "provenance": "[SIMULATED / LORA_RF_MOCK]"
        }


class MockBLEAdapter(BaseAdapter):
    """Simulates nRF52840 Bluetooth 5.3 Coded PHY radio."""

    def __init__(self) -> None:
        super().__init__(name="MockBLEAdapter-nRF52840", hardware_connected=False)
        self.paired_device: Optional[str] = None

    def send_notification(self, payload_bytes: bytes) -> bool:
        logger.info(f"[MockBLE] Transmitted {len(payload_bytes)} bytes over GATT characteristic.")
        return True


class MockSirenAdapter(BaseAdapter):
    """Simulates industrial emergency horn GPIO relay switch."""

    def __init__(self, gpio_pin: int = 18) -> None:
        super().__init__(name="MockSirenAdapter-GPIO", hardware_connected=False)
        self.gpio_pin = gpio_pin
        self.pin_state = "LOW_SILENT"

    def write_gpio(self, high: bool) -> bool:
        self.pin_state = "HIGH_SOUNDING" if high else "LOW_SILENT"
        logger.info(f"[MockSiren] GPIO Pin {self.gpio_pin} set to {self.pin_state}.")
        return True


class MQTTAdapter(BaseAdapter):
    """Optional decoupled MQTT pub/sub adapter interface (Section 29)."""

    def __init__(self, broker_host: str = "localhost", port: int = 1883) -> None:
        super().__init__(name="MQTTAdapter-Paho", hardware_connected=False)
        self.broker_host = broker_host
        self.port = port
        self.published_messages: List[Dict[str, Any]] = []

    def publish_sensor_reading(self, topic: str, reading: Dict[str, Any]) -> bool:
        """Publishes reading to configured MQTT topic without requiring active broker in tests."""
        msg = {
            "topic": topic,
            "payload": reading,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.published_messages.append(msg)
        logger.info(f"[MQTT] Published to {topic}: {reading.get('node_id')}")
        return True

    def subscribe_alerts(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        logger.info(f"[MQTT] Subscribed callback to {topic}.")
        return True
