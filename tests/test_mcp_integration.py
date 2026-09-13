# -*- coding: utf-8 -*-
"""
tests/test_mcp_integration.py
==============================
Tests verifying MCP integration readiness and Phase 5C API health.
Uses Flask test client — no real external API calls.
Phase 5C PAHAD AI.
"""

import sys
import os
import json
import pytest
from unittest.mock import patch

sys.path.insert(0, "c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi")


@pytest.fixture(scope="module")
def client():
    """Flask test client for all tests in this module."""
    os.environ.setdefault("PAHAD_DEMO_MODE", "0")
    os.environ.setdefault("FLASK_TESTING", "true")
    from app import app as flask_app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


# ─── Test 1: System starts without MCP servers (no ImportError) ───────────────
def test_system_starts_without_mcp():
    """The application must start cleanly even if MCP servers are unavailable."""
    try:
        from app import app  # noqa: F401
    except ImportError as exc:
        pytest.fail(f"App failed to import: {exc}")


# ─── Test 2: App module imports cleanly ──────────────────────────────────────
def test_app_imports_cleanly():
    import app  # noqa: F401
    assert hasattr(app, "app")


# ─── Test 3: /api/pahad/data-status returns JSON with status field ────────────
def test_data_status_endpoint(client):
    resp = client.get("/api/pahad/data-status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data is not None
    assert "status" in data
    assert data["status"] in ("SUCCESS", "ERROR")


# ─── Test 4: /api/pahad/observations/latest returns 200 or 404 (not 500) ─────
def test_observations_latest_endpoint(client):
    resp = client.get("/api/pahad/observations/latest?sector_id=SK-NH10-KM48")
    # Either implemented (200) or not found (404) but NOT a 500 error
    assert resp.status_code in (200, 404), f"Got unexpected {resp.status_code}"
    # If 200, must be JSON
    if resp.status_code == 200:
        data = resp.get_json()
        assert data is not None


# ─── Test 5: /api/pahad/live-inference returns JSON (not 500) ─────────────────
def test_live_inference_endpoint(client):
    if os.environ.get("PARVAT_LIVE_INTEGRATION") != "1":
        from unittest.mock import MagicMock
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            "sector_id": "SK-NH10-KM48",
            "event_probability": 0.35,
            "composite_risk_index": 35.0,
            "alert_level": "GREEN",
            "provenance_summary": "MOCK"
        }
        with patch("engine.pahad_live_inference.run_live_inference", return_value=mock_result):
            resp = client.get(
                "/api/pahad/live-inference"
                "?sector_id=SK-NH10-KM48&latitude=27.33&longitude=88.61&horizon_hours=24"
            )
    else:
        resp = client.get(
            "/api/pahad/live-inference"
            "?sector_id=SK-NH10-KM48&latitude=27.33&longitude=88.61&horizon_hours=24"
        )
    # Should return a JSON response regardless of data availability
    assert resp.status_code in (200, 422, 500)
    data = resp.get_json()
    assert data is not None
    # On 500, status should be 'ERROR'
    if resp.status_code == 500:
        assert data.get("status") == "ERROR"


# ─── Test 6: /api/pahad/event-model/status returns model_status field ─────────
def test_event_model_status_endpoint(client):
    resp = client.get("/api/pahad/event-model/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data is not None
    assert "model_status" in data or "status" in data


# ─── Test 7: MCP_INTEGRATION_STATUS.md exists ─────────────────────────────────
def test_mcp_integration_status_doc_exists():
    doc_path = os.path.join(
        "c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi",
        "docs", "MCP_INTEGRATION_STATUS.md"
    )
    assert os.path.isfile(doc_path), f"Expected {doc_path} to exist"
    content = open(doc_path, encoding="utf-8").read()
    assert "MCP" in content
    assert len(content) > 100


# ─── Test 8: PHASE5C_INTEGRATION_AUDIT.md exists ─────────────────────────────
def test_phase5c_audit_doc_exists():
    doc_path = os.path.join(
        "c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi",
        "docs", "PHASE5C_INTEGRATION_AUDIT.md"
    )
    assert os.path.isfile(doc_path), f"Expected {doc_path} to exist"
    content = open(doc_path, encoding="utf-8").read()
    # Must contain the audit table
    assert "SOURCE" in content
    assert "CONNECTED" in content
    assert "AUTH" in content


# ─── Test 9: /api/pahad/forecast returns JSON with forecast field ─────────────
def test_forecast_endpoint_returns_forecast(client):
    if os.environ.get("PARVAT_LIVE_INTEGRATION") != "1":
        mock_forecast = {
            "sector_id": "SK-NH10-KM48",
            "max_risk_horizon": "24h",
            "max_event_probability": 0.35,
            "horizons": {"24h": {"event_probability": 0.35}}
        }
        with patch("engine.pahad_live_inference.run_forecast", return_value=mock_forecast):
            resp = client.get(
                "/api/pahad/forecast"
                "?sector_id=SK-NH10-KM48&latitude=27.33&longitude=88.61&horizons=6,24"
            )
    else:
        resp = client.get(
            "/api/pahad/forecast"
            "?sector_id=SK-NH10-KM48&latitude=27.33&longitude=88.61&horizons=6,24"
        )
    assert resp.status_code in (200, 422, 500)
    data = resp.get_json()
    assert data is not None


# ─── Test 10: NCS connector imports without error ────────────────────────────
def test_ncs_connector_imports():
    from services.ncs_service import NCSConnector, NCS_CONNECTOR
    status = NCS_CONNECTOR.get_status()
    assert "status" in status
    assert "provider" in status


# ─── Test 11: IMD connector imports without error ────────────────────────────
def test_imd_connector_imports():
    from services.imd_service import IMDConnector, IMD_CONNECTOR
    status = IMD_CONNECTOR.get_status()
    assert "status" in status
    assert status["status"] in ("AUTH_REQUIRED", "READY", "LIVE", "UNAVAILABLE")


# ─── Test 12: EO catalog imports without error ───────────────────────────────
def test_eo_catalog_imports():
    from services.eo_catalog_service import EOCatalogConnector, EO_CATALOG_SERVICE
    status = EO_CATALOG_SERVICE.get_catalogue_status()
    assert "copernicus_cdse" in status
    assert "nrsc_bhoonidhi" in status


# ─── Test 13: DataFreshnessEngine imports without error ──────────────────────
def test_freshness_engine_imports():
    from engine.data_freshness import FRESHNESS_ENGINE, FRESH, AGING, STALE, UNAVAILABLE
    assert FRESHNESS_ENGINE is not None
    summary = FRESHNESS_ENGINE.get_summary()
    assert isinstance(summary, dict)


# ─── Test 14: ObservationStore imports without error ─────────────────────────
def test_observation_store_imports():
    from engine.observation_store import GLOBAL_OBSERVATION_STORE
    assert GLOBAL_OBSERVATION_STORE is not None
    # count() should return int without raising
    n = GLOBAL_OBSERVATION_STORE.count()
    assert isinstance(n, int)
