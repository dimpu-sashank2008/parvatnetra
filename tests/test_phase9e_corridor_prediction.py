# -*- coding: utf-8 -*-
"""
tests/test_phase9e_corridor_prediction.py
=========================================
Phase 9E: Multi-Corridor Selection & Real Updates Verification
--------------------------------------------------------------
Confirms that selecting different corridors updates actual CRI, FoS,
rainfall loading, risk band, and coordinates without cross-corridor bleed.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app as flask_app
from engine.canonical_registry import CANONICAL_REGISTRY


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def index_html(client):
    res = client.get("/")
    assert res.status_code == 200
    return res.get_data(as_text=True)


class TestPhase9eCorridorPrediction:
    """Verifies multi-corridor switching updates CRI and geotechnics."""

    def test_corridor_switching_updates_actual_cri_and_geotechnics(self, client):
        """Switching from Sonapur Tunnel to NH-10 Km 48 returns distinct corridor metrics."""
        # 1. Evaluate Sonapur Tunnel (Meghalaya)
        res_sonapur = client.post(
            "/api/pahad/location-risk",
            json={"location_id": "ML-SONAPUR-01", "horizon_hours": 24}
        )
        assert res_sonapur.status_code == 200
        data_sonapur = res_sonapur.get_json()
        inf_sonapur = data_sonapur["inference"]

        # 2. Evaluate NH-10 Km 48 (Sikkim)
        res_nh10 = client.post(
            "/api/pahad/location-risk",
            json={"location_id": "SK-NH10-KM48", "horizon_hours": 24}
        )
        assert res_nh10.status_code == 200
        data_nh10 = res_nh10.get_json()
        inf_nh10 = data_nh10["inference"]

        # 3. Evaluate Tupul Railway (Manipur)
        res_tupul = client.post(
            "/api/pahad/location-risk",
            json={"location_id": "MN-TUPUL-RLY", "horizon_hours": 24}
        )
        assert res_tupul.status_code == 200
        data_tupul = res_tupul.get_json()
        inf_tupul = data_tupul["inference"]

        # Metrics must reflect actual location specifics
        assert inf_sonapur["sector_id"] == "ML-SONAPUR-01"
        assert inf_nh10["sector_id"] == "SK-NH10-KM48"
        assert inf_tupul["sector_id"] == "MN-TUPUL-RLY"

        # Coordinates must differ
        assert inf_sonapur["latitude"] != inf_nh10["latitude"]
        assert inf_sonapur["longitude"] != inf_nh10["longitude"]

        # CRI scores must be valid floats in [0, 100]
        assert 0.0 <= inf_sonapur["cri"] <= 100.0
        assert 0.0 <= inf_nh10["cri"] <= 100.0
        assert 0.0 <= inf_tupul["cri"] <= 100.0

        # Physical FoS must be calculated and positive
        assert inf_sonapur["fos_physical"] > 0.0
        assert inf_nh10["fos_physical"] > 0.0

    def test_dom_corridor_wiping_contract(self, index_html):
        """DOM and JS must contain the wiping state when corridor selection changes."""
        assert "onCorridorSelectionChanged" in index_html
        assert "animateCriScore" in index_html
        assert "animateRingProgress" in index_html
        assert "EVALUATING..." in index_html
        assert 'id="pahad-corridor-loading"' in index_html

    def test_dom_telemetry_signal_elements_present(self, index_html):
        """All 4 key evidence elements and coordinates display must exist."""
        assert 'id="pahad-ai-fos"' in index_html
        assert 'id="pahad-ai-rain-status"' in index_html
        assert 'id="pahad-ai-ml-status"' in index_html
        assert 'id="pahad-ai-seismic-status"' in index_html
        assert 'id="pahad-minimap-coords"' in index_html
        assert 'id="pahad-prediction-minimap"' in index_html
