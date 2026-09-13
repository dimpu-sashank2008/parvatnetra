# -*- coding: utf-8 -*-
"""
tests/test_sensor_acceptance.py
===============================
Phase 6B Test Suite: Physical Sensor Acceptance & 8-Stage Commissioning
"""

import sys
import os
import subprocess
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.sensor_registry import (
    SensorRegistry,
    SensorDevice,
    STATUS_REGISTERED,
    STATUS_COMMISSIONING,
    STATUS_ACTIVE,
    COMMISSIONING_STAGES
)
from app import app as flask_app


@pytest.fixture
def isolated_registry(tmp_path):
    db_path = str(tmp_path / "test_commissioning.db")
    return SensorRegistry(db_path=db_path)


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


class TestSensorAcceptanceWorkflow:

    def test_eight_stages_defined(self):
        expected = [
            "REGISTER", "INSTALL", "CALIBRATE", "CONNECT",
            "HEARTBEAT", "TELEMETRY", "VALIDATE", "ACCEPT"
        ]
        assert COMMISSIONING_STAGES == expected

    def test_full_acceptance_pipeline_happy_path(self, isolated_registry):
        reg = isolated_registry
        dev_id = "DEV-ACCEPT-01"

        # 1. Register
        dev = SensorDevice(
            device_id=dev_id,
            sensor_id=dev_id,
            sensor_type="piezometer",
            latitude=27.33,
            longitude=88.61,
            sector_id="SK-NH10-KM48",
            status=STATUS_REGISTERED
        )
        reg.register_device(dev)
        r1 = reg.advance_commissioning(dev_id, "REGISTER")
        assert r1["status"] == "SUCCESS"
        assert reg.get_device(dev_id).status == STATUS_COMMISSIONING

        # 2-7. Intermediate stages
        for stage in ("INSTALL", "CALIBRATE", "CONNECT", "HEARTBEAT", "TELEMETRY", "VALIDATE"):
            r = reg.advance_commissioning(dev_id, stage)
            assert r["status"] == "SUCCESS"
            assert reg.get_device(dev_id).status == STATUS_COMMISSIONING

        # 8. Accept
        r8 = reg.advance_commissioning(dev_id, "ACCEPT")
        assert r8["status"] == "SUCCESS"
        accepted_dev = reg.get_device(dev_id)
        assert accepted_dev.status == STATUS_ACTIVE
        assert accepted_dev.commissioned_at is not None

    def test_prerequisite_stage_missing_rejected(self, isolated_registry):
        reg = isolated_registry
        dev_id = "DEV-OUT-OF-ORDER"

        dev = SensorDevice(
            device_id=dev_id,
            sensor_id=dev_id,
            sensor_type="tilt",
            latitude=27.33,
            longitude=88.61,
            sector_id="SK-NH10-KM48"
        )
        reg.register_device(dev)

        # Attempt TELEMETRY without INSTALL, CALIBRATE, CONNECT, etc.
        res = reg.advance_commissioning(dev_id, "TELEMETRY")
        assert res["status"] == "REJECTED_PREREQUISITE_MISSING"
        assert "Missing prerequisite" in res["message"]
        assert reg.get_device(dev_id).status != STATUS_ACTIVE

    def test_invalid_stage_name_rejected(self, isolated_registry):
        reg = isolated_registry
        dev_id = "DEV-STAGE-TEST"
        dev = SensorDevice(
            device_id=dev_id, sensor_id=dev_id, sensor_type="piezometer",
            latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48"
        )
        reg.register_device(dev)
        res = reg.advance_commissioning(dev_id, "NON_EXISTENT_STAGE")
        assert res["status"] == "ERROR"

    def test_readiness_reporting(self, isolated_registry):
        reg = isolated_registry
        dev_id = "DEV-READINESS"
        dev = SensorDevice(
            device_id=dev_id, sensor_id=dev_id, sensor_type="piezometer",
            latitude=27.33, longitude=88.61, sector_id="SK-NH10-KM48"
        )
        reg.register_device(dev)
        reg.advance_commissioning(dev_id, "REGISTER")
        reg.advance_commissioning(dev_id, "INSTALL")

        readiness = reg.get_commissioning_readiness(dev_id)
        assert readiness["status"] == "SUCCESS"
        data = readiness["readiness"]
        assert data["stages"]["REGISTERED"] is True
        assert data["stages"]["INSTALLED"] is True
        assert data["stages"]["ACCEPTED"] is False
        assert data["readiness_pct"] < 100.0


class TestCommissioningCLI:

    def test_commission_sensor_cli_execution(self):
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "scripts",
            "commission_sensor.py"
        )
        result = subprocess.run(
            [sys.executable, script_path, "--device-id", "CLI-TEST-PZ-99", "--sensor-type", "piezometer", "--auto"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "ACCEPTED" in result.stdout
        assert "Digital Certificate" in result.stdout

    def test_api_commissioning_readiness_endpoint(self, client):
        resp = client.get("/api/iot/commissioning/readiness")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "SUCCESS"
        assert "total_devices" in data
        assert "devices" in data
