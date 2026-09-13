# -*- coding: utf-8 -*-
"""
services/bench_simulator.py
===========================
PARVAT NETRA • Isolated Geotechnical Hardware Bench Simulator Harness
---------------------------------------------------------------------
Generates realistic multi-transducer test sequences and environmental stress profiles
for automated bench validation without physical field sensors.

CRITICAL INVARIANTS:
  1. Every single generated packet is strictly marked: provenance = "[SIMULATED]"
  2. Bench data must NEVER be exported or ingested into operational model training sets.
  3. All scenarios execute against isolated test buffers and observation stores.

Supported Simulation Scenarios:
  - BASELINE_NORMAL       : Calm conditions, minimal pore pressure, zero tilt creep
  - RAIN_SURGE            : Monsoonal cloudburst (>50 mm/hr) triggering rain alarm
  - PORE_PRESSURE_SPIKE   : Acute saturation spike (>45 kPa) crossing critical threshold
  - TILT_ACCELERATION     : Surface rotational displacement rate exceeding 2.5 deg/day
  - DISPLACEMENT_SLIP     : Inclinometer shear acceleration exceeding 15 mm/day
  - SENSOR_DROPOUT        : Transducer open-circuit / disconnection / zero telemetry
  - PACKET_LOSS           : Simulated radio propagation multipath loss (30-50% dropped)
  - GATEWAY_OUTAGE        : Backhaul disconnection testing offline SQLite FIFO buffer
"""

from __future__ import annotations

import os
import time
import random
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from firmware.packet_codec import BinaryPacketCodec
from services.edge_gateway import GLOBAL_EDGE_GATEWAY_SERVICE, EdgeGatewayService
from services.telemetry_contract import GLOBAL_TELEMETRY_VALIDATOR

logger = logging.getLogger("BENCH_SIMULATOR")

SCENARIOS = [
    "BASELINE_NORMAL",
    "RAIN_SURGE",
    "PORE_PRESSURE_SPIKE",
    "TILT_ACCELERATION",
    "DISPLACEMENT_SLIP",
    "SENSOR_DROPOUT",
    "PACKET_LOSS",
    "GATEWAY_OUTAGE"
]


class BenchSimulator:
    """Isolated hardware test harness for simulating hillslope instrumentation."""

    def __init__(
        self,
        default_device_id: str = "BENCH-NODE-01",
        default_gateway_id: str = "GW-NH10-KM48-01",
        sector_id: str = "SK-NH10-KM48"
    ):
        self.device_id = default_device_id
        self.gateway_id = default_gateway_id
        self.sector_id = sector_id
        self.current_sequence: int = 1
        self.last_run_scenario: Optional[str] = None
        self.total_generated: int = 0
        self.total_dropped_by_simulation: int = 0

    def generate_packet(
        self,
        scenario: str = "BASELINE_NORMAL",
        sequence: Optional[int] = None,
        sensor_type: str = "piezometer",
        device_id: Optional[str] = None,
        gateway_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes a single telemetry packet tailored to the selected scenario.
        Strict invariant: provenance is always "[SIMULATED]".
        """
        seq = sequence if sequence is not None else self.current_sequence
        self.current_sequence = seq + 1
        self.total_generated += 1

        dev_id = device_id or self.device_id
        gw_id = gateway_id or self.gateway_id
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        epoch_ts = int(now_dt.timestamp())

        measurements: Dict[str, Any] = {}
        st = sensor_type.lower()

        # Scenario values
        if scenario == "BASELINE_NORMAL":
            pore_kpa = round(15.0 + random.uniform(-0.5, 0.5), 2)
            tilt_deg = round(0.12 + random.uniform(-0.01, 0.01), 3)
            rain_mm = 0.0
            disp_mm = 0.5
            battery = 98.0
            rssi = -65.0

        elif scenario == "RAIN_SURGE":
            pore_kpa = round(32.0 + random.uniform(0.0, 2.0), 2)
            tilt_deg = round(0.45 + random.uniform(0.0, 0.05), 3)
            rain_mm = round(65.0 + random.uniform(0.0, 10.0), 1)  # Cloudburst (>50 mm/hr)
            disp_mm = 2.4
            battery = 95.0
            rssi = -78.0

        elif scenario == "PORE_PRESSURE_SPIKE":
            pore_kpa = round(48.5 + random.uniform(0.0, 3.0), 2)  # Critical (>45 kPa)
            tilt_deg = round(0.85 + random.uniform(0.0, 0.1), 3)
            rain_mm = 38.0
            disp_mm = 4.1
            battery = 94.0
            rssi = -72.0

        elif scenario == "TILT_ACCELERATION":
            pore_kpa = 34.0
            tilt_deg = round(2.85 + random.uniform(0.0, 0.2), 3)  # Critical (>2.5 deg/day)
            rain_mm = 20.0
            disp_mm = 6.2
            battery = 92.0
            rssi = -74.0

        elif scenario == "DISPLACEMENT_SLIP":
            pore_kpa = 42.0
            tilt_deg = 1.8
            rain_mm = 25.0
            disp_mm = round(18.5 + random.uniform(0.0, 2.0), 2)  # Critical (>15 mm/day)
            battery = 91.0
            rssi = -70.0

        elif scenario == "SENSOR_DROPOUT":
            # Out-of-bounds or zero reading simulating loose cable
            pore_kpa = -999.0
            tilt_deg = -999.0
            rain_mm = -1.0
            disp_mm = -999.0
            battery = 45.0
            rssi = -120.0

        else:
            # Default to baseline
            pore_kpa = 18.0
            tilt_deg = 0.2
            rain_mm = 0.0
            disp_mm = 1.0
            battery = 96.0
            rssi = -68.0

        # Construct measurements
        if st == "piezometer":
            measurements["pore_pressure"] = {"value": pore_kpa, "unit": "kPa", "quality": "GOOD"}
        elif st == "tilt":
            measurements["tilt"] = {"value": tilt_deg, "unit": "deg", "quality": "GOOD"}
        elif st == "rain_gauge":
            measurements["rain_1h"] = {"value": rain_mm, "unit": "mm", "quality": "GOOD"}
        elif st == "inclinometer":
            measurements["ground_displacement"] = {"value": disp_mm, "unit": "mm", "quality": "GOOD"}
        else:
            measurements[st] = {"value": pore_kpa, "unit": "raw", "quality": "GOOD"}

        measurements["temperature"] = {"value": 18.5, "unit": "C", "quality": "GOOD"}

        packet_id = f"{dev_id}_{seq}_{epoch_ts}"

        return {
            "packet_id": packet_id,
            "device_id": dev_id,
            "sensor_id": dev_id,
            "gateway_id": gw_id,
            "sequence_number": seq,
            "timestamp": now_iso,
            "received_at": now_iso,
            "latitude": 27.3302,
            "longitude": 88.6104,
            "battery": battery,
            "signal_quality": rssi,
            "firmware_version": "v2.1.0-bench-sim",
            "transport": "HTTP",
            "provenance": "[SIMULATED]",  # STRICT INVARIANT
            "scenario": scenario,
            "measurements": measurements
        }

    def generate_binary_frame(
        self,
        scenario: str = "BASELINE_NORMAL",
        sequence: Optional[int] = None,
        short_id: int = 101
    ) -> bytes:
        """Generates an 18-byte packed binary LoRa frame for the given scenario."""
        pkt = self.generate_packet(scenario=scenario, sequence=sequence)
        prim = 15.0
        sec = 0.1
        tert = 0.05
        tamper = False

        if scenario == "PORE_PRESSURE_SPIKE":
            prim = 48.5
            tamper = True
        elif scenario == "RAIN_SURGE":
            prim = 65.0
            tamper = True
        elif scenario == "TILT_ACCELERATION":
            prim = 2.85
            tamper = True

        epoch_ts = int(time.time())
        seq = pkt["sequence_number"]

        return BinaryPacketCodec.encode(
            device_short_id=short_id,
            sequence_number=seq,
            timestamp_epoch=epoch_ts,
            primary_val=prim,
            secondary_val=sec,
            tertiary_val=tert,
            battery_pct=pkt["battery"],
            temperature_c=18.0,
            tamper=tamper
        )

    def run_scenario(
        self,
        scenario: str,
        packet_count: int = 5,
        target_gateway: Optional[EdgeGatewayService] = None
    ) -> Dict[str, Any]:
        """
        Executes a sequence of packets for the specified scenario against an edge gateway.
        """
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario '{scenario}'. Available: {SCENARIOS}")

        gw = target_gateway or GLOBAL_EDGE_GATEWAY_SERVICE
        self.last_run_scenario = scenario
        results = []

        # Handle gateway outage scenario
        if scenario == "GATEWAY_OUTAGE":
            gw.set_cloud_connectivity(False)

        for i in range(packet_count):
            if scenario == "PACKET_LOSS" and (i % 2 == 1):
                # Simulate packet dropped over RF air interface
                self.total_dropped_by_simulation += 1
                results.append({"status": "DROPPED_BY_SIMULATION", "step": i + 1})
                continue

            pkt = self.generate_packet(scenario=scenario)
            res = gw.ingest_sensor_packet(pkt, transport="HTTP")
            results.append(res)

        # Restore gateway connectivity if outage scenario
        if scenario == "GATEWAY_OUTAGE":
            flush_res = gw.flush_buffer()
            gw.set_cloud_connectivity(True)
            return {
                "scenario": scenario,
                "packet_count": packet_count,
                "ingest_results": results,
                "flush_results": flush_res,
                "buffered_count_during_outage": packet_count,
                "provenance": "[SIMULATED]"
            }

        return {
            "scenario": scenario,
            "packet_count": packet_count,
            "ingest_results": results,
            "provenance": "[SIMULATED]"
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "simulator_name": "PAHAD Hardware Bench Simulator",
            "provenance": "[SIMULATED]",
            "available_scenarios": SCENARIOS,
            "last_run_scenario": self.last_run_scenario,
            "total_generated": self.total_generated,
            "total_dropped_by_simulation": self.total_dropped_by_simulation,
            "active_device_id": self.device_id,
            "active_gateway_id": self.gateway_id
        }


# Global Singleton Simulator
GLOBAL_BENCH_SIMULATOR = BenchSimulator()
