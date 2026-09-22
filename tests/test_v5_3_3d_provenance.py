# -*- coding: utf-8 -*-
"""
tests/test_v5_3_3d_provenance.py
================================
PARVAT NETRA • PAHAD AI — Phase V5.3 3D Provenance Integrity Test Suite
"""

import os
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_v5_3_api_config_provenance_badge(client):
    """Verify that /api/gods-eye/config carries authoritative 3D GIS provenance."""
    res = client.get("/api/gods-eye/config")
    assert res.status_code == 200
    data = res.get_json()
    assert data["provenance"] == "[3D GIS / GEOSPATIAL PRESENTATION]"


def test_v5_3_js_entities_provenance_tags():
    """Verify that every 3D layer entity in static/js/gods_eye_3d.js carries strict provenance."""
    js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "gods_eye_3d.js")
    with open(js_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Weather: Open-Meteo
    assert "[LIVE / OPEN-METEO]" in code

    # Seismic: USGS
    assert "[LIVE / USGS-FDSNWS]" in code

    # InSAR: Satellite LOS
    assert "[HISTORICAL / INSAR-LOS]" in code

    # FoS: Mohr-Coulomb physics
    assert "[PHYSICS / MOHR-COULOMB]" in code

    # Sensors: Planned / Bench tested
    assert "[PLANNED / BENCH TESTED / PHYSICAL TELEMETRY PENDING]" in code

    # Lifeline highway: BRO records
    assert "[HISTORICAL / BRO RECORDS]" in code


def test_v5_3_zero_fake_live_sensor_claims():
    """Verify that 3D scene explicitly reports 0 live sensors and never claims [LIVE] for in-situ sensors."""
    js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "gods_eye_3d.js")
    with open(js_path, "r", encoding="utf-8") as f:
        code = f.read()

    assert "UNAVAILABLE_PENDING_INSTALLATION" in code
    assert "0 records (Zero Field Telemetry)" in code
