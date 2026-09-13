# -*- coding: utf-8 -*-
"""
tests/test_iot_api.py
=====================
Integration tests for Phase 6A IoT & Field Edge Gateway REST Endpoints.
Validates HTTP request and response contracts for all /api/iot/*, /api/edge/*, and /api/siren/* routes.
"""

import json
import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_api_iot_devices_list(client):
    res = client.get("/api/iot/devices")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "devices" in data
    assert isinstance(data["devices"], list)


def test_api_iot_gateways_list(client):
    res = client.get("/api/iot/gateways")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "gateways" in data


def test_api_iot_health(client):
    res = client.get("/api/iot/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "health" in data
    assert "overall_health" in data["health"]


def test_api_iot_metrics(client):
    res = client.get("/api/iot/metrics")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "telemetry_metrics" in data


def test_api_iot_telemetry_ingress(client):
    payload = {
        "device_id": "SN-TEST-REST-01",
        "sequence_number": 1,
        "latitude": 27.33,
        "longitude": 88.61,
        "measurements": {"pore_pressure": 18.5}
    }
    res = client.post("/api/iot/telemetry", json=payload)
    assert res.status_code in (200, 202)
    data = res.get_json()
    assert data["status"] in ("ACCEPTED", "BUFFERED_OFFLINE", "SUCCESS")


def test_api_iot_commissioning(client):
    payload = {
        "device_id": "SN-NEW-DEV-99",
        "stage": "REGISTER",
        "sensor_type": "tilt",
        "latitude": 27.33,
        "longitude": 88.61,
        "sector_id": "SK-NH10-KM48"
    }
    res = client.post("/api/iot/commission", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert data["stage_completed"] == "REGISTER"


def test_api_iot_calibration_upload(client):
    payload = {
        "sensor_id": "SN-CAL-API-01",
        "zero_offset": 2.0,
        "scale_factor": 1.05,
        "calibration_source": "FIELD_RIG"
    }
    res = client.post("/api/iot/calibration", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert data["calibration"]["sensor_id"] == "SN-CAL-API-01"


def test_api_edge_alert_test(client):
    payload = {
        "measurements": {"pore_pressure": 48.0},
        "sector_id": "SK-NH10-KM48",
        "trigger_siren_test": True
    }
    res = client.post("/api/edge/alert/test", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert data["evaluation"]["severity"] == "CRITICAL"
    assert data["siren_test"] is not None
    assert data["siren_test"]["dry_run"] is True


def test_api_edge_health(client):
    res = client.get("/api/edge/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "edge_gateway" in data


def test_api_siren_status(client):
    res = client.get("/api/siren/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert data["siren"]["dry_run"] is True


def test_api_siren_activate_and_disarm(client):
    # Activate in dry-run
    res_act = client.post("/api/siren/activate", json={"level": "WARNING", "reason": "Test route"})
    assert res_act.status_code == 200
    data_act = res_act.get_json()
    assert data_act["event"]["dry_run"] is True

    # Disarm
    res_dis = client.post("/api/siren/disarm")
    assert res_dis.status_code == 200
    data_dis = res_dis.get_json()
    assert data_dis["siren"]["is_armed"] is False
