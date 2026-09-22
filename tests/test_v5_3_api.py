# -*- coding: utf-8 -*-
"""
tests/test_v5_3_api.py
======================
Phase V5.3 Test Suite: Localhost API Endpoints Contract Verification
Tests:
- GET /api/data/events/verification
- GET /api/data/events/evidence
- GET /api/data/events/evidence/<id>
- GET /api/data/events/lineage
- GET /api/data/events/quality
"""

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestV53API:
    """Verifies all Phase V5.3 REST endpoints on localhost."""

    def test_events_verification_endpoint(self, client):
        res = client.get("/api/data/events/verification")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["phase"] == "V5.3"
        gt = data["ground_truth_status"]
        assert gt["authoritative_verified_count"] == 37
        assert gt["research_candidate_count"] == 5

    def test_events_evidence_endpoint(self, client):
        res = client.get("/api/data/events/evidence")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["total_count"] == 42
        assert len(data["events"]) == 42

    def test_events_evidence_filtered_by_status(self, client):
        res = client.get("/api/data/events/evidence?status=RESEARCH_CANDIDATE")
        assert res.status_code == 200
        data = res.get_json()
        assert data["total_count"] == 5

    def test_events_evidence_by_id_endpoint(self, client):
        res = client.get("/api/data/events/evidence/EV-01")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        ev = data["event_evidence"]
        assert ev["event_id"] == "EV-01"
        assert ev["evidence_count"] >= 1

    def test_events_evidence_by_invalid_id_returns_404(self, client):
        res = client.get("/api/data/events/evidence/NON-EXISTENT-ID")
        assert res.status_code == 404

    def test_events_lineage_endpoint(self, client):
        res = client.get("/api/data/events/lineage")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["authoritative_verified_count"] == 37
        assert data["research_candidate_count"] == 5
        assert len(data["events"]) == 42

    def test_events_quality_endpoint(self, client):
        res = client.get("/api/data/events/quality")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        metrics = data["quality_metrics"]
        assert metrics["coordinate_completeness_pct"] == 100.0
        assert metrics["timestamp_completeness_pct"] == 100.0
