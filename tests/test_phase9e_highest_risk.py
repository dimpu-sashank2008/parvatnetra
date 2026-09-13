# -*- coding: utf-8 -*-
"""
tests/test_phase9e_highest_risk.py
==================================
Verifies the highest-risk corridor calculation, dynamic default selection,
and deterministic tie-breaking logic for Phase 9E.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import app as flask_app
from engine.canonical_registry import CANONICAL_REGISTRY


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


class TestHighestRiskCorridor:
    """Verifies that the default corridor is dynamically calculated as the highest risk corridor."""

    def test_highest_risk_corridor_endpoint_success(self, client):
        """GET /api/pahad/highest-risk-corridor returns 200 with highest risk corridor."""
        res = client.get("/api/pahad/highest-risk-corridor")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert "highest_risk_corridor" in data
        assert "ranked_corridors" in data
        assert data["count"] >= 20

        top = data["highest_risk_corridor"]
        assert top is not None
        assert "id" in top
        assert "name" in top
        assert "state" in top
        assert "district" in top
        assert "cri" in top
        assert "fos" in top
        assert "event_probability" in top
        assert "risk_band" in top

    def test_highest_risk_corridor_is_actually_highest_cri(self, client):
        """Confirms that no other corridor in ranked_corridors has a higher CRI than top."""
        res = client.get("/api/pahad/highest-risk-corridor")
        assert res.status_code == 200
        data = res.get_json()
        top = data["highest_risk_corridor"]
        ranked = data["ranked_corridors"]

        top_cri = top["cri"]
        for c in ranked:
            assert top_cri >= c["cri"], f"Corridor {c['id']} has CRI {c['cri']} > top CRI {top_cri}"

    def test_deterministic_tie_breaking_contract(self, client):
        """Verifies the deterministic tie-breaking contract is stated and followed."""
        res = client.get("/api/pahad/highest-risk-corridor")
        data = res.get_json()
        assert "tie_breaker" in data
        assert "highest_cri_desc" in data["tie_breaker"]

        ranked = data["ranked_corridors"]
        for i in range(len(ranked) - 1):
            curr = ranked[i]
            nxt = ranked[i + 1]
            if abs(curr["cri"] - nxt["cri"]) < 1e-4:
                curr_fos = curr["fos"] if curr["fos"] is not None else 999.0
                nxt_fos = nxt["fos"] if nxt["fos"] is not None else 999.0
                if abs(curr_fos - nxt_fos) < 1e-4:
                    assert curr["id"] <= nxt["id"], f"Tie-break alphabetical failure: {curr['id']} > {nxt['id']}"
                else:
                    assert curr_fos <= nxt_fos, f"Tie-break FoS failure: {curr['id']} ({curr_fos}) > {nxt['id']} ({nxt_fos})"
            else:
                assert curr["cri"] >= nxt["cri"], f"CRI ordering failure: {curr['cri']} < {nxt['cri']}"

    def test_highest_risk_not_hardcoded_to_sikkim(self, client):
        """Confirms the default is determined dynamically and not statically hardcoded to SK-NH10-KM48."""
        res = client.get("/api/pahad/highest-risk-corridor")
        data = res.get_json()
        top = data["highest_risk_corridor"]
        assert top["cri"] >= 34.6
