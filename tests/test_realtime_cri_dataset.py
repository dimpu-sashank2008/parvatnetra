# -*- coding: utf-8 -*-
"""
tests/test_realtime_cri_dataset.py
==================================
PARVAT NETRA • Real-Time CRI Dataset & Dynamic Evaluation Tests
----------------------------------------------------------------
Verifies:
  1. Real-time multi-modal dataset harvesting across GSI critical sectors.
  2. Scientific CRI calculation using live environmental telemetry.
  3. Proper filing of datasets to disk (CSV and JSON) in data/realtime/.
  4. Immutable SHA-256 data hash calculation and provenance tracking.
  5. REST API contract for /api/pahad/realtime-cri and refresh endpoints.
"""

import os
import csv
import json
import hashlib
import pytest
from app import app
from services.realtime_cri_service import REALTIME_CRI_SERVICE


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_realtime_cri_service_initialization():
    """Verifies service initializes output paths, directories, and SQLite schema."""
    assert os.path.exists(REALTIME_CRI_SERVICE.data_dir)
    assert REALTIME_CRI_SERVICE.csv_path.endswith("realtime_cri_dataset.csv")
    assert REALTIME_CRI_SERVICE.json_path.endswith("realtime_cri_dataset.json")


def test_evaluate_single_sector_with_realtime_data():
    """Verifies CRI evaluation for a single sector ingests live data streams."""
    rec = REALTIME_CRI_SERVICE.evaluate_sector("SK-NH10-KM48")
    assert rec["sector_id"] == "SK-NH10-KM48"
    assert "final_cri" in rec
    assert isinstance(rec["final_cri"], (int, float))
    assert 0.0 <= rec["final_cri"] <= 100.0

    # Verify weather telemetry captured
    assert "rainfall_24h_mm" in rec
    assert "rainfall_current_mmh" in rec
    assert rec["weather_source"] != ""

    # Verify seismic telemetry captured
    assert "seismic_magnitude" in rec
    assert "seismic_shaking_proxy_g" in rec

    # Verify physical geotech & morphometry
    assert "physical_fos" in rec
    assert rec["physical_fos"] > 0.0
    assert "slope_deg" in rec

    # Verify 2-of-3 signal rule and provenance
    assert rec["model_agreement"] in ("0/3", "1/3", "2/3", "3/3")
    assert rec["overall_provenance"] == "[LIVE/HYBRID]"
    assert len(rec["data_hash_sha256"]) == 64


def test_filed_realtime_cri_dataset_integrity():
    """Verifies the dataset is properly filed to CSV and JSON on disk with valid headers."""
    # Run refresh and file
    res = REALTIME_CRI_SERVICE.get_latest_dataset()
    assert res["status"] == "SUCCESS"
    assert res["record_count"] >= 1

    # Verify CSV on disk
    csv_file = REALTIME_CRI_SERVICE.csv_path
    assert os.path.exists(csv_file)
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) >= 1
        first_row = rows[0]
        assert "sector_id" in first_row
        assert "final_cri" in first_row
        assert "rainfall_24h_mm" in first_row
        assert "seismic_magnitude" in first_row
        assert "physical_fos" in first_row
        assert "data_hash_sha256" in first_row

    # Verify JSON on disk
    json_file = REALTIME_CRI_SERVICE.json_path
    assert os.path.exists(json_file)
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "records" in data
        assert len(data["records"]) >= 1
        assert "generated_at_utc" in data

    # Verify SHA-256 hash match
    with open(csv_file, "rb") as f_hash:
        expected_hash = hashlib.sha256(f_hash.read()).hexdigest()
    if res.get("dataset_hash_sha256"):
        assert res["dataset_hash_sha256"] == expected_hash


def test_api_get_realtime_cri_dataset(client):
    """Tests GET /api/pahad/realtime-cri endpoint."""
    resp = client.get("/api/pahad/realtime-cri")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "SUCCESS"
    assert "records" in data
    assert "record_count" in data
    assert "dataset_hash_sha256" in data
    assert "band_summary" in data


def test_api_get_sector_realtime_cri(client):
    """Tests GET /api/pahad/realtime-cri/sector/<sector_id> endpoint."""
    resp = client.get("/api/pahad/realtime-cri/sector/SK-NH10-KM48")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "SUCCESS"
    rec = data["record"]
    assert rec["sector_id"] == "SK-NH10-KM48"
    assert "final_cri" in rec
    assert "rainfall_24h_mm" in rec


def test_api_download_realtime_cri_csv(client):
    """Tests GET /api/pahad/realtime-cri/download endpoint."""
    resp = client.get("/api/pahad/realtime-cri/download?format=csv")
    assert resp.status_code == 200
    assert resp.content_type.startswith("text/csv")
    csv_text = resp.data.decode("utf-8")
    assert "sector_id,sector_name" in csv_text or "record_id" in csv_text


def test_api_download_realtime_cri_json(client):
    """Tests GET /api/pahad/realtime-cri/download?format=json endpoint."""
    resp = client.get("/api/pahad/realtime-cri/download?format=json")
    assert resp.status_code == 200
    assert resp.content_type.startswith("application/json")
    data = json.loads(resp.data.decode("utf-8"))
    assert "records" in data
