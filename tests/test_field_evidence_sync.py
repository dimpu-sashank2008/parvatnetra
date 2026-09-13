# -*- coding: utf-8 -*-
"""
tests/test_field_evidence_sync.py
=================================
Integration tests for mobile offline field commissioning batch synchronization,
idempotency, and REST API contracts.
"""

import sys
import os
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from engine.sensor_inventory import SENSOR_INVENTORY, PhysicalSensorAsset, STATUS_PLANNED


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_batch_sync_offline_evidence_api(client):
    # Pre-register asset in inventory
    asset = PhysicalSensorAsset(
        device_id="SN-PIEZ-SYNC-01",
        sensor_id="PIEZ-SYNC-01",
        sensor_type="piezometer",
        serial_number="VW-SYNC-001",
        manufacturer="Geokon",
        model="4500S",
        firmware_version="v1.0",
        calibration_certificate=None,
        installation_location={"corridor_id": "CORR-NH10-SIKKIM-KM48"},
        status=STATUS_PLANNED
    )
    SENSOR_INVENTORY.register_asset(asset)

    payload = {
        "records": [
            {
                "evidence_id": "EV-SYNC-01",
                "device_id": "SN-PIEZ-SYNC-01",
                "stage": "REGISTER",
                "technician_name": "Field Lead B",
                "gps_coords": {"accuracy_m": 4.0},
                "notes": "Verified against staging bill"
            },
            {
                "evidence_id": "EV-SYNC-02",
                "device_id": "SN-PIEZ-SYNC-01",
                "stage": "LOCATE",
                "technician_name": "Field Lead B",
                "gps_coords": {"latitude": 27.3301, "longitude": 88.6102, "accuracy_m": 3.2},
                "notes": "Surveyed borehole collar"
            },
            {
                "evidence_id": "EV-SYNC-03",
                "device_id": "SN-PIEZ-SYNC-01",
                "stage": "INSTALL",
                "technician_name": "Field Lead B",
                "gps_coords": {"accuracy_m": 3.2},
                "photo_hashes": ["e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"],
                "notes": "Grouting complete with bentonite seal"
            }
        ]
    }

    res = client.post("/api/field/evidence/sync", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SYNCED"
    assert data["result"]["synced_count"] == 3


def test_batch_sync_idempotency(client):
    payload = {
        "records": [
            {
                "evidence_id": "EV-IDEMP-01",
                "device_id": "SN-PIEZ-IDEMP-01",
                "stage": "REGISTER",
                "technician_name": "Field Tech",
                "gps_coords": {"accuracy_m": 5.0}
            }
        ]
    }

    # First post
    res1 = client.post("/api/field/evidence/sync", json=payload)
    assert res1.status_code == 200
    assert res1.get_json()["result"]["synced_count"] == 1

    # Re-post same batch
    res2 = client.post("/api/field/evidence/sync", json=payload)
    assert res2.status_code == 200
    assert res2.get_json()["result"]["synced_count"] == 1


def test_batch_sync_malformed_payload(client):
    res = client.post("/api/field/evidence/sync", json={"records": "not-a-list"})
    assert res.status_code == 400


def test_get_commissioning_history_api(client):
    res = client.get("/api/field/commissioning?device_id=SN-PIEZ-SYNC-01")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert data["evidence_count"] >= 3
    assert data["device_id"] == "SN-PIEZ-SYNC-01"


def test_get_commissioning_missing_device_id_fails(client):
    res = client.get("/api/field/commissioning")
    assert res.status_code == 400
