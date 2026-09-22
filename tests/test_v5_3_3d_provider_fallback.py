# -*- coding: utf-8 -*-
"""
tests/test_v5_3_3d_provider_fallback.py
========================================
PARVAT NETRA • PAHAD AI — Phase V5.3 3D Provider Hierarchy & Fallback Test Suite
"""

import os
import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_v5_3_default_fallback_without_credentials(client):
    """Verify that absent credentials defaults gracefully to OPEN_TERRAIN_FALLBACK."""
    env_clean = {k: v for k, v in os.environ.items() if k not in ("GOOGLE_MAPS_API_KEY", "CESIUM_ION_TOKEN")}
    with patch.dict(os.environ, env_clean, clear=True):
        res = client.get("/api/gods-eye/config")
        assert res.status_code == 200
        data = res.get_json()

        assert data["provider_status"] == "AUTH_REQUIRED"
        assert data["active_provider"] == "OPEN_TERRAIN_FALLBACK"
        assert "AUTH_REQUIRED FOR GOOGLE 3D TILES" in data["provider_badge"]
        assert data["google_maps_api_key_configured"] is False
        assert data["cesium_ion_token_configured"] is False


def test_v5_3_google_3d_tiles_provider_when_key_present(client):
    """Verify that presence of GOOGLE_MAPS_API_KEY elevates provider to GOOGLE_PHOTOREALISTIC_3D."""
    with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "AIzaSyFakeKeyTestOnly1234567890"}):
        res = client.get("/api/gods-eye/config")
        assert res.status_code == 200
        data = res.get_json()

        assert data["provider_status"] == "CONFIGURED"
        assert data["active_provider"] == "GOOGLE_PHOTOREALISTIC_3D"
        assert "GOOGLE PHOTOREALISTIC 3D TILES" in data["provider_badge"]
        assert data["google_maps_api_key_configured"] is True


def test_v5_3_cesium_world_terrain_when_ion_token_present(client):
    """Verify that presence of CESIUM_ION_TOKEN elevates provider to CESIUM_WORLD_TERRAIN."""
    env_patch = {
        "GOOGLE_MAPS_API_KEY": "",
        "CESIUM_ION_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fakeCesiumToken"
    }
    with patch.dict(os.environ, env_patch):
        res = client.get("/api/gods-eye/config")
        assert res.status_code == 200
        data = res.get_json()

        assert data["provider_status"] == "CONFIGURED"
        assert data["active_provider"] == "CESIUM_WORLD_TERRAIN"
        assert "CESIUM WORLD TERRAIN" in data["provider_badge"]
        assert data["cesium_ion_token_configured"] is True


def test_v5_3_zero_secret_leakage_in_api_response(client):
    """Verify that raw API keys or tokens are never leaked in the JSON response."""
    test_key = "AIzaSySuperSecretGoogleMapsKey999"
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.SuperSecretCesiumToken999"

    with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": test_key, "CESIUM_ION_TOKEN": test_token}):
        res = client.get("/api/gods-eye/config")
        assert res.status_code == 200
        raw_response = res.get_data(as_text=True)

        assert test_key not in raw_response
        assert test_token not in raw_response
