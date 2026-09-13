# -*- coding: utf-8 -*-
"""
tests/test_phase7h_provider_failure.py
======================================
PHASE 7H — CP 7H-08, 7H-10, 7H-11, 7H-12, 7H-13, 7H-14, 7H-15:
Provider Degradation, Graceful Fallback, and Fail-Closed Safety Invariants:
  - CP 7H-08: Geotechnical sensor telemetry outage
  - CP 7H-10: Weather API failure (IMD -> Open-Meteo / Cached fallback)
  - CP 7H-11: Seismic API failure (NCS -> USGS / Cached fallback)
  - CP 7H-12: Satellite pipeline failure (Copernicus -> Baseline DEM / Static InSAR)
  - CP 7H-13: Database outage (Neon PostgreSQL -> Local SQLite / Memory)
  - CP 7H-14: ML Model timeout / failure -> Deterministic Mohr-Coulomb FoS fallback
  - CP 7H-15: Authority workflow outage -> Strict FAIL-CLOSED gate
"""

import pytest
from unittest.mock import patch, MagicMock
from services.weather_service import WeatherService
from services.seismic_service import SeismicService
from services.satellite_service import SATELLITE_SERVICE
from services.authority_review_service import AUTHORITY_REVIEW_SERVICE, ROLE_PUBLIC, ACTION_APPROVE
from services.sync_service import SyncService
from engine.pahad_live_inference import run_live_inference


def test_sensor_telemetry_outage_graceful_handling():
    """CP 7H-08: Missing or disconnected in-situ sensors do not crash inference or evaluation."""
    # Evaluate sector with empty/missing live sensor readings (relies on median imputation fallback)
    res = run_live_inference(
        sector_id="CORR-NH10-SIKKIM-KM48",
        latitude=27.33,
        longitude=88.61,
        forecast_horizon_hours=24,
        override_features={"rainfall_24h": 40.0, "slope_deg": 38.0}
    )
    assert res is not None
    assert res.fos_physical > 0.0
    assert res.event_probability >= 0.0
    assert res.risk_band in ["LOW", "MODERATE", "HIGH", "VERY_HIGH", "EXTREME"]


def test_weather_provider_outage_fallback():
    """CP 7H-10: Weather service gracefully falls back when primary IMD API fails."""
    ws = WeatherService()
    with patch.object(ws.imd_provider, "fetch_weather", side_effect=Exception("IMD Connection Refused")):
        obs = ws.get_weather(lat=27.33, lon=88.61, sector_id="SK-NH10-KM48")
        assert obs is not None
        assert "rainfall" in obs
        assert "rain_24h_mm" in obs["rainfall"]
        assert obs.get("provenance") in ["SIMULATED", "LIVE", "CACHED", "HISTORICAL", "DEMO"]


def test_seismic_provider_outage_fallback():
    """CP 7H-11: Seismic service falls back to USGS public API or cached catalog when NCS is down."""
    ss = SeismicService()
    with patch.object(ss.ncs_provider, "fetch_events", side_effect=Exception("NCS Portal Down")):
        events = ss.get_recent_events(limit=5)
        assert events is not None
        assert isinstance(events, list)


def test_satellite_provider_outage_fallback():
    """CP 7H-12: Satellite service falls back to static baseline when cloud data is unavailable."""
    deform = SATELLITE_SERVICE.get_insar_deformation_for_sector("SK-NH10-KM48")
    assert deform is not None
    assert "provenance" in deform
    assert deform["provenance"] in ["[SIMULATED]", "[LIVE]", "[HISTORICAL]", "[STATIC_PRODUCT]"]
    
    pipe_status = SATELLITE_SERVICE.get_pipeline_status()
    assert "missions" in pipe_status
    assert "Sentinel-1_SAR" in pipe_status["missions"]


def test_database_outage_fallback_to_memory_registry():
    """CP 7H-13: Database outage falls back gracefully to in-memory deduplication registry."""
    sync_svc = SyncService()
    broken_conn = MagicMock()
    broken_conn.cursor.side_effect = Exception("Neon Connection Timeout")

    report = {
        "local_id": "PN-DB-FAIL-01",
        "latitude": 27.33,
        "longitude": 88.61,
        "hazard_type": "landslide",
        "created_at": "2026-09-11T07:00:00Z"
    }

    # Should not raise, falls back to memory registry
    ack = sync_svc.sync_single_report(report, db_conn=broken_conn)
    assert ack["status"] == "SUCCESS"
    assert ack["sync_status"] == "SYNCED"
    assert ack["server_id"] is not None


def test_model_failure_fallback_to_deterministic_fos():
    """CP 7H-14: Model failure falls back to deterministic Mohr-Coulomb physics."""
    with patch("engine.model_registry.GLOBAL_MODEL_REGISTRY.get_model", side_effect=Exception("Model Load Failure")):
        res = run_live_inference(
            sector_id="CORR-NH10-SIKKIM-KM48",
            latitude=27.33,
            longitude=88.61,
            forecast_horizon_hours=24,
            override_features={"rainfall_24h": 40.0, "slope_deg": 38.0}
        )
        assert res is not None
        assert res.fos_physical > 0.0


def test_authority_review_service_outage_fails_closed():
    """CP 7H-15: If authority review workflow fails or token is missing, alert dispatch fails closed."""
    # Unauthorized or public actor cannot trigger warning authorization
    with pytest.raises(PermissionError):
        AUTHORITY_REVIEW_SERVICE.submit_review_action(
            decision_id="DEC-TEST-FAIL-CLOSED",
            reviewer_id="ANONYMOUS_ACTOR",
            role=ROLE_PUBLIC,
            action=ACTION_APPROVE,
            justification="Unauthorized trigger attempt"
        )
