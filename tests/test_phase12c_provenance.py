"""
Phase 12C Automated Test Suite: Live Data Truth, Provenance & Provider Status
Tests the 9 data providers, fallback flags, and temporal deep learning honesty.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.pahad_explanation_engine import LiveDataStatusAuditor
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


class TestPhase12CProvenanceAndProviders:
    def test_auditor_all_nine_providers(self):
        auditor = LiveDataStatusAuditor()
        status = auditor.get_provider_statuses()
        
        expected_providers = [
            "IMD AWS Precipitation",
            "Open-Meteo Weather NWP",
            "National Center for Seismology (NCS)",
            "USGS Global Seismic Hazards",
            "Copernicus Sentinel-1/2 (InSAR/DEM)",
            "ISRO NRSC / Bhoonidhi Earth Observation",
            "In-Situ Geotechnical IoT Telemetry",
            "PostGIS Geospatial Engine",
            "SQLite Embedded Operational Database"
        ]
        
        for p in expected_providers:
            assert p in status["providers"], f"Provider missing: {p}"
            p_data = status["providers"][p]
            assert any(s in p_data["status"] for s in ["LIVE", "SIMULATED", "HISTORICAL", "DEMO", "UNAVAILABLE", "ONLINE", "AUTH_REQUIRED", "CATALOG_AVAILABLE", "HEALTHY", "DEGRADED"])
            assert "latency" in p_data
            assert "fallback_active" in p_data

    def test_fallback_flags_presence(self):
        auditor = LiveDataStatusAuditor()
        status = auditor.get_provider_statuses()
        flags = status.get("fallback_flags", {})
        
        assert "weather_fallback_active" in flags
        assert "seismic_fallback_active" in flags
        assert "sqlite_fallback_active" in flags

    def test_temporal_deep_learning_transparency(self):
        auditor = LiveDataStatusAuditor()
        status = auditor.get_provider_statuses()
        ml_gov = status.get("temporal_ml_governance", {})
        
        assert ml_gov.get("lstm_model_status") == "PHYSICS-INFORMED TEMPORAL SURROGATE / NOT TRAINED"
        assert ml_gov.get("continuous_sensor_sequences") == 0
        assert ml_gov.get("training_eligibility") == "DATA_COLLECTION_REQUIRED"
        assert "GradientBoostingClassifier" in ml_gov.get("operational_event_classifier", "")

    def test_api_data_status_endpoint(self, client):
        resp = client.get("/api/pahad/data-status")
        assert resp.status_code == 200
        data = resp.get_json()
        
        # Verify backward-compatibility keys
        assert "data_streams" in data or "providers" in data
        assert "overall_data_completeness_score" in data or "providers" in data
        assert len(data.get("providers", {})) >= 9
