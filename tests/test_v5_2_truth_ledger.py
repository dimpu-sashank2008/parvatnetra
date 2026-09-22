# -*- coding: utf-8 -*-
"""
tests/test_v5_2_truth_ledger.py
===============================
Phase V5.2 Test Suite: Scientific Truth Ledger Integration & REST Endpoints
"""

import json
import pytest
from app import app
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestV52TruthLedgerAndEndpoints:
    """Verifies scientific truth ledger reconciliation and V5.2 REST API endpoints."""

    def test_endpoint_data_sources_status(self, client):
        res = client.get("/api/data-sources/status")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["phase"] == "V5.2"
        assert data["physical_sensors_verified"] == 0
        assert data["physical_telemetry_status"] == "UNAVAILABLE_PENDING_INSTALLATION"
        assert len(data["sources"]) == 12

    def test_endpoint_data_sources_events(self, client):
        res = client.get("/api/data-sources/events")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["total_canonical_events"] == 42
        assert len(data["events"]) == 42
        assert data["verification_tier_counts"]["VERIFIED_PRIMARY"] >= 30

    def test_endpoint_data_sources_events_filter_by_state(self, client):
        res = client.get("/api/data-sources/events?state=Sikkim")
        assert res.status_code == 200
        data = res.get_json()
        assert data["total_filtered_events"] > 0
        for ev in data["events"]:
            assert ev["state"].lower() == "sikkim"

    def test_endpoint_data_sources_provenance(self, client):
        res = client.get("/api/data-sources/provenance")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["separation_audit"]["canonical_documented_events"] == 42
        assert data["separation_audit"]["canonical_negative_controls"] == 20
        assert data["separation_audit"]["synthetic_events_in_canonical"] == 0
        assert data["separation_audit"]["physical_iot_sensors_in_canonical"] == 0

    def test_endpoint_data_sources_quality(self, client):
        res = client.get("/api/data-sources/quality")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        metrics = data["quality_metrics"]
        assert metrics["coordinate_completeness_pct"] == 100.0
        assert metrics["timestamp_completeness_pct"] == 100.0
        assert metrics["official_citation_completeness_pct"] == 100.0

    def test_endpoint_data_sources_conflicts(self, client):
        res = client.get("/api/data-sources/conflicts")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["total_conflicts"] == 4
        assert set(data["conflict_ids"]) == {"SCON-01", "SCON-02", "SCON-03", "SCON-04"}
