# -*- coding: utf-8 -*-
"""
tests/test_hardware_pahad_pipeline.py
=====================================
Phase 6C Test Suite: End-to-End Sensor -> Gateway -> ObservationStore -> PAHAD -> Safety Gate
"""

import sys
import os
import time
import pytest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firmware.packet_codec import BinaryPacketCodec
from services.edge_gateway import GLOBAL_EDGE_GATEWAY_SERVICE
from engine.observation_store import GLOBAL_OBSERVATION_STORE
from engine.sector_snapshot import SECTOR_SNAPSHOT_BUILDER
from engine.edge_alert_policy import GLOBAL_EDGE_ALERT_POLICY
from services.siren_controller import GLOBAL_SIREN_CONTROLLER
from engine.sensor_registry import (
    GLOBAL_SENSOR_REGISTRY,
    SensorDevice,
    STATUS_ACTIVE
)


@pytest.fixture(autouse=True)
def setup_registered_devices():
    # Register corridor test devices
    dev_pz = SensorDevice(
        device_id="PZ-PIPELINE-01",
        sensor_id="PZ-PIPELINE-01",
        sensor_type="piezometer",
        latitude=27.3302,
        longitude=88.6104,
        sector_id="SK-NH10-KM48",
        status=STATUS_ACTIVE
    )
    GLOBAL_SENSOR_REGISTRY.register_device(dev_pz)


class TestHardwarePahadPipeline:

    def test_full_pipeline_sensor_to_observation_store(self):
        # 1. Produce 18-byte binary frame from piezometer
        epoch_ts = int(time.time())
        frame = BinaryPacketCodec.encode(
            device_short_id=101,
            sequence_number=1,
            timestamp_epoch=epoch_ts,
            primary_val=34.2,  # 34.2 kPa pore pressure
            battery_pct=95.0,
            temperature_c=18.5
        )

        # 2. Decode and convert to canonical telemetry packet
        packet = BinaryPacketCodec.to_canonical_packet(
            frame,
            device_id_map={101: "PZ-PIPELINE-01"},
            sensor_type="piezometer",
            gateway_id="GW-NH10-KM48-01",
            sector_id="SK-NH10-KM48" if hasattr(BinaryPacketCodec, "sector_id") else None,
            provenance="[LIVE]"
        )

        # 3. Ingest into Edge Gateway
        ingest_res = GLOBAL_EDGE_GATEWAY_SERVICE.ingest_sensor_packet(packet, transport="LORA")
        assert ingest_res["status"] == "ACCEPTED"
        assert ingest_res["records_stored"] > 0

        # 4. Verify presence in ObservationStore
        latest = GLOBAL_OBSERVATION_STORE.get_latest("SK-NH10-KM48", "pore_pressure", limit=1)
        assert len(latest) > 0
        latest_rec = latest[0]
        assert latest_rec.feature == "pore_pressure"
        assert latest_rec.value == 34.2
        assert latest_rec.unit == "kPa"

    def test_sector_snapshot_incorporates_sensor_telemetry(self):
        # Build snapshot for SK-NH10-KM48
        snapshot = SECTOR_SNAPSHOT_BUILDER.build("SK-NH10-KM48")
        assert snapshot.sector_id == "SK-NH10-KM48"
        assert "pore_pressure" in snapshot.features
        # Pore pressure should be populated from our recent test insertion
        assert snapshot.features["pore_pressure"] is not None

    def test_edge_corridor_anomaly_detection_and_siren_safety_gate(self):
        # Test acute reading that exceeds corridor thresholds
        acute_reading = {
            "pore_pressure": {"value": 48.0, "unit": "kPa"},        # Critical: >45.0 kPa
            "inclinometer_velocity": {"value": 16.5, "unit": "mm/day"} # Critical: >15.0 mm/day
        }

        eval_res = GLOBAL_EDGE_ALERT_POLICY.evaluate_reading(
            acute_reading,
            sector_id="SK-NH10-KM48",
            gateway_id="GW-NH10-KM48-01"
        )
        assert eval_res["severity"] == "CRITICAL"
        assert eval_res["siren_recommended"] is True
        assert eval_res["bypass_recommended"] is True

        # Verify siren controller dry-run safety invariant
        assert GLOBAL_SIREN_CONTROLLER.dry_run is True
        siren_res = GLOBAL_SIREN_CONTROLLER.activate(
            level="CRITICAL",
            reason="Acute Corridor Pore Pressure Spike"
        )
        assert siren_res["status"] == "SOUNDING_SIMULATED"
        assert siren_res["dry_run"] is True
        assert siren_res["physical_actuation"] is False  # ZERO audible output!
