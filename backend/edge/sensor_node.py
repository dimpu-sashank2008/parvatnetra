# -*- coding: utf-8 -*-
"""
backend/edge/sensor_node.py
===========================
PARVAT NETRA • In-Situ Geotechnical IoT Sensor Node Model
---------------------------------------------------------
Implements Section 3: Sensor node data structure and telemetry synthesis.
Supports Volumetric Water Content (VWC %), piezometric pore-water pressure (kPa),
borehole inclinometer tilt (°), rainfall (mm/h), battery, temperature,
humidity, crack aperture (mm), and vibration (g).

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import time
import random
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.edge.packet import EdgePacket


class SensorNode:
    """Represents a physical or emulated remote geotechnical sensor station."""

    def __init__(
        self,
        node_id: str,
        location: str = "NH-10 Km 48",
        role: str = "SENSOR",
        initial_battery: int = 95,
        is_demo: bool = False
    ) -> None:
        self.node_id = str(node_id)
        self.location = location
        self.role = role.upper()
        self.battery = max(0, min(100, initial_battery))
        self.is_demo = is_demo
        self.sequence_number = 0

        # Baseline Geotechnical Sensor State
        self.soil_moisture = 34.5 # VWC %
        self.pore_pressure = 8.2 # kPa
        self.tilt = 0.12 # degrees
        self.rainfall = 2.4 # mm/h
        self.temperature = 18.5 # C
        self.humidity = 72 # %
        self.crack_aperture = 2.0 # mm
        self.vibration = 0.02 # g

    def generate_reading(
        self,
        soil_moisture: Optional[float] = None,
        pore_pressure: Optional[float] = None,
        tilt: Optional[float] = None,
        rainfall: Optional[float] = None,
        is_demo: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes a geotechnically coherent sensor observation.
        Updates monotonic sequence counter.
        """
        self.sequence_number += 1
        demo_flag = self.is_demo if is_demo is None else is_demo

        if soil_moisture is not None:
            self.soil_moisture = float(soil_moisture)
        else:
            self.soil_moisture = round(max(10.0, min(65.0, self.soil_moisture + random.uniform(-0.3, 0.4))), 2)

        if pore_pressure is not None:
            self.pore_pressure = float(pore_pressure)
        else:
            self.pore_pressure = round(max(0.0, min(50.0, self.pore_pressure + random.uniform(-0.2, 0.3))), 2)

        if tilt is not None:
            self.tilt = float(tilt)
        else:
            self.tilt = round(max(0.0, min(10.0, self.tilt + random.uniform(-0.02, 0.03))), 3)

        if rainfall is not None:
            self.rainfall = float(rainfall)
        else:
            self.rainfall = round(max(0.0, min(120.0, self.rainfall + random.uniform(-0.5, 0.5))), 2)

        # Subtle battery drain
        if self.sequence_number % 100 == 0:
            self.battery = max(5, self.battery - 1)

        now_iso = datetime.now(timezone.utc).isoformat()
        prov = "[DEMO]" if demo_flag else "[LIVE]"

        return {
            "node_id": self.node_id,
            "sequence_number": self.sequence_number,
            "sequence": self.sequence_number,
            "timestamp": now_iso,
            "soil_moisture": self.soil_moisture,
            "pore_pressure": self.pore_pressure,
            "tilt": self.tilt,
            "rainfall": self.rainfall,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "battery": self.battery,
            "signal_strength": -78.0,
            "crack_aperture": self.crack_aperture,
            "vibration": self.vibration,
            "source": "ESP32_LORA_NODE",
            "provenance": prov,
            "is_demo": demo_flag
        }

    def generate_packet(self, is_demo: Optional[bool] = None) -> EdgePacket:
        """Constructs EdgePacket ready for binary framing or transmission."""
        reading = self.generate_reading(is_demo=is_demo)
        return EdgePacket.from_dict(reading)

    def inject_hazard_scenario(self, stage: str = "WARNING") -> Dict[str, Any]:
        """
        Infiltration scenario for SIH evaluators.
        Simulates torrential precipitation causing pore-pressure surge and shear tilt.
        """
        stage_upper = stage.upper()
        if stage_upper == "CRITICAL":
            self.rainfall = 65.0 # Extreme rainfall surge mm/h
            self.soil_moisture = 58.4 # Saturated VWC %
            self.pore_pressure = 42.1 # Piezometric spike kPa
            self.tilt = 3.45 # Inclinometer shear acceleration degrees
            self.crack_aperture = 28.5 # mm
        elif stage_upper == "WARNING":
            self.rainfall = 35.0
            self.soil_moisture = 51.2
            self.pore_pressure = 31.0
            self.tilt = 1.85
            self.crack_aperture = 12.0
        elif stage_upper == "WATCH":
            self.rainfall = 15.0
            self.soil_moisture = 44.0
            self.pore_pressure = 18.5
            self.tilt = 0.65
        else:
            # NORMAL
            self.rainfall = 1.5
            self.soil_moisture = 32.0
            self.pore_pressure = 5.0
            self.tilt = 0.08

        return self.generate_reading(is_demo=True)
