# -*- coding: utf-8 -*-
"""
tests/test_v4_6_telemetry.py
============================
Phase V4.6 Test Suite: In-Situ Telemetry Ingestion, Validation & High-Frequency Kinematics
"""

import os
import json
import time
from datetime import datetime, timezone, timedelta
import pytest

from services.kinematic_telemetry_service import (
    KinematicTelemetryService,
    CORRIDOR_ID_NH10,
    DEFAULT_FRESHNESS_THRESHOLDS
)
from firmware.packet_codec import BinaryPacketCodec, compute_crc16_ccitt, FRAME_LENGTH_BYTES


@pytest.fixture
def telemetry_service(tmp_path):
    """Provides an isolated KinematicTelemetryService instance."""
    # Write a test registry
    reg_data = {
        "corridor_id": "CORR-NH10-SIKKIM-KM48",
        "corridor_name": "NH-10 Test Corridor",
        "physical_status": "BENCH_VALIDATED",
        "telemetry_status": "PHYSICAL_TELEMETRY_PENDING",
        "field_deployment_pending": True,
        "freshness_thresholds_seconds": {
            "PIEZOMETER": 900,
            "INCLINOMETER": 900,
            "TILTMETER": 900,
            "RAIN_GAUGE": 900,
            "GATEWAY": 300
        },
        "sensors": [
            {
                "sensor_id": "PIEZO-NH10-KM48-01",
                "sensor_type": "PIEZOMETER",
                "unit": "kPa",
                "range_min": -50.0,
                "range_max": 500.0,
                "physical_status": "BENCH_VALIDATED",
                "telemetry_status": "PHYSICAL_TELEMETRY_PENDING"
            },
            {
                "sensor_id": "INCL-NH10-KM48-01",
                "sensor_type": "INCLINOMETER",
                "unit": "mm",
                "range_min": -100.0,
                "range_max": 100.0,
                "physical_status": "BENCH_VALIDATED",
                "telemetry_status": "PHYSICAL_TELEMETRY_PENDING"
            },
            {
                "sensor_id": "TILT-NH10-KM48-01",
                "sensor_type": "TILTMETER",
                "unit": "deg",
                "range_min": -45.0,
                "range_max": 45.0,
                "physical_status": "BENCH_VALIDATED",
                "telemetry_status": "PHYSICAL_TELEMETRY_PENDING"
            },
            {
                "sensor_id": "RAIN-NH10-KM48-01",
                "sensor_type": "RAIN_GAUGE",
                "unit": "mm/h",
                "range_min": 0.0,
                "range_max": 250.0,
                "physical_status": "BENCH_VALIDATED",
                "telemetry_status": "PHYSICAL_TELEMETRY_PENDING"
            },
            {
                "sensor_id": "GW-NH10-KM48-01",
                "sensor_type": "GATEWAY",
                "unit": "V",
                "range_min": 9.0,
                "range_max": 15.0,
                "physical_status": "BENCH_VALIDATED",
                "telemetry_status": "PHYSICAL_TELEMETRY_PENDING"
            }
        ]
    }
    reg_file = str(tmp_path / "test_corridor_registry.json")
    with open(reg_file, "w", encoding="utf-8") as f:
        json.dump(reg_data, f)

    svc = KinematicTelemetryService(registry_path=reg_file)
    return svc


class TestTelemetryValidation:
    """Tests validation, normalization, and bounds enforcement."""

    def test_default_status_is_pending_and_unavailable(self, telemetry_service):
        status = telemetry_service.get_corridor_status()
        assert status["corridor"]["physical_status"] == "BENCH_VALIDATED"
        assert status["corridor"]["telemetry_status"] == "PHYSICAL_TELEMETRY_PENDING"
        assert status["freshness"]["overall_status"] == "UNAVAILABLE"

    def test_accept_valid_bench_observation(self, telemetry_service):
        now_iso = datetime.now(timezone.utc).isoformat()
        obs = {
            "observation_id": "obs-test-001",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "site_id": "SITE-NH10-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "value": 18.5,
            "unit": "kPa",
            "quality": "GOOD",
            "source": "BENCH_SIMULATOR",
            "provenance": "SIMULATED",
            "status": "SIMULATED",
            "sequence_number": 1
        }
        res = telemetry_service.ingest_canonical_observation(obs)
        assert res.is_valid is True
        assert res.status == "ACCEPTED"

    def test_reject_counterfeit_live_provenance(self, telemetry_service):
        """Zero-counterfeit rule: synthetic or bench data cannot claim LIVE provenance."""
        now_iso = datetime.now(timezone.utc).isoformat()
        counterfeit_obs = {
            "observation_id": "obs-counterfeit-001",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "site_id": "SITE-NH10-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "value": 22.0,
            "unit": "kPa",
            "quality": "GOOD",
            "source": "BENCH_SIMULATOR",
            "provenance": "LIVE",  # FRAUDULENT ATTEMPT
            "status": "LIVE",
            "sequence_number": 1
        }
        res = telemetry_service.ingest_canonical_observation(counterfeit_obs)
        assert res.is_valid is False
        assert res.status == "REJECTED_PROVENANCE_COUNTERFEIT"

    def test_reject_future_timestamp(self, telemetry_service):
        """Rejects timestamps more than 30 seconds into the future."""
        future_iso = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        obs = {
            "observation_id": "obs-future-001",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "site_id": "SITE-NH10-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": future_iso,
            "value": 20.0,
            "unit": "kPa",
            "quality": "GOOD",
            "source": "BENCH_SIMULATOR",
            "provenance": "SIMULATED",
            "status": "SIMULATED",
            "sequence_number": 1
        }
        res = telemetry_service.ingest_canonical_observation(obs)
        assert res.is_valid is False
        assert res.status == "REJECTED_FUTURE_TIMESTAMP"

    def test_reject_duplicate_sequence(self, telemetry_service):
        now_iso = datetime.now(timezone.utc).isoformat()
        obs = {
            "observation_id": "obs-dup-001",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "site_id": "SITE-NH10-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "value": 15.0,
            "unit": "kPa",
            "quality": "GOOD",
            "source": "BENCH_SIMULATOR",
            "provenance": "SIMULATED",
            "status": "SIMULATED",
            "sequence_number": 10
        }
        res1 = telemetry_service.ingest_canonical_observation(obs)
        assert res1.is_valid is True

        # Ingest exact same again -> duplicate rejected
        res2 = telemetry_service.ingest_canonical_observation(obs)
        assert res2.is_valid is False
        assert res2.status in ["REJECTED_DUPLICATE", "REJECTED_DUPLICATE_SEQUENCE"]

    def test_reject_out_of_physical_bounds(self, telemetry_service):
        now_iso = datetime.now(timezone.utc).isoformat()
        # Range is -50 to 500 kPa. Try 999.0 kPa
        obs = {
            "observation_id": "obs-bounds-001",
            "sensor_id": "PIEZO-NH10-KM48-01",
            "corridor_id": "CORR-NH10-SIKKIM-KM48",
            "site_id": "SITE-NH10-KM48",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "value": 999.0,
            "unit": "kPa",
            "quality": "GOOD",
            "source": "BENCH_SIMULATOR",
            "provenance": "SIMULATED",
            "status": "SIMULATED",
            "sequence_number": 1
        }
        res = telemetry_service.ingest_canonical_observation(obs)
        assert res.is_valid is False
        assert res.status == "REJECTED_IMPOSSIBLE_VALUE"


class TestHILBinaryLoRaCodec:
    """Hardware-in-the-Loop 18-byte LoRa frame tests."""

    def test_valid_binary_lora_frame(self, telemetry_service):
        epoch = int(time.time())
        frame = BinaryPacketCodec.encode(
            device_short_id=101,
            sequence_number=1,
            timestamp_epoch=epoch,
            primary_val=24.5,
            secondary_val=1.2,
            tertiary_val=0.5,
            battery_pct=95.0,
            temperature_c=18.0
        )
        assert len(frame) == FRAME_LENGTH_BYTES

        res = telemetry_service.ingest_binary_lora_frame(
            frame_bytes=frame,
            sensor_type="PIEZOMETER",
            sensor_id="PIEZO-NH10-KM48-01",
            provenance="BENCH"
        )
        assert res.is_valid is True
        assert res.status == "ACCEPTED"

    def test_corrupted_crc_rejected(self, telemetry_service):
        epoch = int(time.time())
        frame = bytearray(BinaryPacketCodec.encode(
            device_short_id=101,
            sequence_number=2,
            timestamp_epoch=epoch,
            primary_val=25.0
        ))
        # Corrupt one payload byte
        frame[5] ^= 0xFF

        res = telemetry_service.ingest_binary_lora_frame(
            frame_bytes=bytes(frame),
            sensor_type="PIEZOMETER",
            sensor_id="PIEZO-NH10-KM48-01"
        )
        assert res.is_valid is False
        assert res.status == "REJECTED_CRC_ERROR"

    def test_invalid_frame_length_rejected(self, telemetry_service):
        short_frame = b"\x00\x01\x02\x03\x04"
        res = telemetry_service.ingest_binary_lora_frame(
            frame_bytes=short_frame,
            sensor_type="PIEZOMETER"
        )
        assert res.is_valid is False
        assert res.status == "REJECTED_FRAME_LENGTH"


class TestKinematicFeatureDerivation:
    """Tests feature generation: deltas, velocities, accelerations."""

    def test_piezometer_derivatives(self, telemetry_service):
        now = datetime.now(timezone.utc)
        # Ingest 3 observations over 30 minutes
        # t0: 10 kPa, t1: 15 kPa (15m later), t2: 25 kPa (30m later)
        t0 = (now - timedelta(minutes=30)).isoformat()
        t1 = (now - timedelta(minutes=15)).isoformat()
        t2 = now.isoformat()

        telemetry_service.ingest_canonical_observation({
            "observation_id": "p0", "sensor_id": "PIEZO-NH10-KM48-01", "corridor_id": CORRIDOR_ID_NH10,
            "site_id": "S1", "sensor_type": "PIEZOMETER", "timestamp_utc": t0, "value": 10.0,
            "unit": "kPa", "quality": "GOOD", "source": "BENCH_SIMULATOR", "provenance": "SIMULATED",
            "status": "SIMULATED", "sequence_number": 1
        })
        telemetry_service.ingest_canonical_observation({
            "observation_id": "p1", "sensor_id": "PIEZO-NH10-KM48-01", "corridor_id": CORRIDOR_ID_NH10,
            "site_id": "S1", "sensor_type": "PIEZOMETER", "timestamp_utc": t1, "value": 15.0,
            "unit": "kPa", "quality": "GOOD", "source": "BENCH_SIMULATOR", "provenance": "SIMULATED",
            "status": "SIMULATED", "sequence_number": 2
        })
        telemetry_service.ingest_canonical_observation({
            "observation_id": "p2", "sensor_id": "PIEZO-NH10-KM48-01", "corridor_id": CORRIDOR_ID_NH10,
            "site_id": "S1", "sensor_type": "PIEZOMETER", "timestamp_utc": t2, "value": 25.0,
            "unit": "kPa", "quality": "GOOD", "source": "BENCH_SIMULATOR", "provenance": "SIMULATED",
            "status": "SIMULATED", "sequence_number": 3
        })

        features = telemetry_service.compute_kinematic_features()
        p_feat = features["sensors"]["PIEZO-NH10-KM48-01"]
        m = p_feat["metrics"]

        assert m is not None
        assert m["pressure"] == 25.0
        assert m["pressure_delta_15m"] > 0
        assert m["pressure_velocity"] > 0
        assert p_feat["lineage"]["sample_count"] == 3
        assert p_feat["lineage"]["provenance"] == "SIMULATED"

    def test_inclinometer_derivatives(self, telemetry_service):
        now = datetime.now(timezone.utc)
        t0 = (now - timedelta(minutes=15)).isoformat()
        t1 = now.isoformat()

        telemetry_service.ingest_canonical_observation({
            "observation_id": "i0", "sensor_id": "INCL-NH10-KM48-01", "corridor_id": CORRIDOR_ID_NH10,
            "site_id": "S1", "sensor_type": "INCLINOMETER", "timestamp_utc": t0, "value": 2.0,
            "unit": "mm", "quality": "GOOD", "source": "BENCH_SIMULATOR", "provenance": "SIMULATED",
            "status": "SIMULATED", "sequence_number": 1
        })
        telemetry_service.ingest_canonical_observation({
            "observation_id": "i1", "sensor_id": "INCL-NH10-KM48-01", "corridor_id": CORRIDOR_ID_NH10,
            "site_id": "S1", "sensor_type": "INCLINOMETER", "timestamp_utc": t1, "value": 3.5,
            "unit": "mm", "quality": "GOOD", "source": "BENCH_SIMULATOR", "provenance": "SIMULATED",
            "status": "SIMULATED", "sequence_number": 2
        })

        features = telemetry_service.compute_kinematic_features()
        i_feat = features["sensors"]["INCL-NH10-KM48-01"]
        m = i_feat["metrics"]

        assert m["displacement"] == 3.5
        assert m["velocity"] > 0  # 1.5mm / 0.25h = 6.0 mm/h


class TestTelemetryAPIRoutes:
    """Flask client route tests for /api/telemetry/* and /api/pahad/*."""

    @pytest.fixture
    def client(self):
        import app
        return app.app.test_client()

    def test_api_telemetry_status(self, client):
        res = client.get("/api/telemetry/status")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert "telemetry_system" in data

    def test_api_telemetry_sensors(self, client):
        res = client.get("/api/telemetry/sensors")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["total_sensors"] >= 5

    def test_api_telemetry_sensor_detail(self, client):
        res = client.get("/api/telemetry/sensors/PIEZO-NH10-KM48-01")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["sensor"]["sensor_id"] == "PIEZO-NH10-KM48-01"

    def test_api_telemetry_freshness(self, client):
        res = client.get("/api/telemetry/freshness")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert "freshness" in data

    def test_api_telemetry_ingest_via_rest(self, client):
        now_iso = datetime.now(timezone.utc).isoformat()
        obs = {
            "observation_id": f"obs-rest-{int(time.time()*1000)}",
            "sensor_id": "RAIN-NH10-KM48-01",
            "corridor_id": CORRIDOR_ID_NH10,
            "site_id": "SITE-NH10-KM48",
            "sensor_type": "RAIN_GAUGE",
            "timestamp_utc": now_iso,
            "value": 12.5,
            "unit": "mm/h",
            "quality": "GOOD",
            "source": "BENCH_SIMULATOR",
            "provenance": "SIMULATED",
            "status": "SIMULATED",
            "sequence_number": int(time.time()) % 100000
        }
        res = client.post("/api/telemetry/ingest", json=obs)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "ACCEPTED"
