# -*- coding: utf-8 -*-
"""
tests/test_gis_hazard_animation.py
===================================
PARVAT NETRA • PAHAD AI — GIS Hazard Map Animation & Visual Intelligence Test Suite
Phase 12 Verification Suite

Test Coverage:
  1. REST Endpoint Contract: GET /api/pahad/temporal-risk (200 OK, JSON schema).
  2. Provenance Integrity: Strict separation of [LIVE], [SIMULATED], [HISTORICAL].
  3. Zero Synthetic Live Fabrication: LIVE mode returns authoritative runtime snapshot
     without fabricating fake 24-hour historical curves.
  4. Multi-Corridor Support: Verifies canonical corridors across Sikkim, Manipur,
     Mizoram, Assam, Meghalaya, Nagaland, and Arunachal Pradesh.
  5. Scientific & CRI Consistency: CRI monotonic scaling of halo radii, opacity,
     risk bands, and FoS degradation during scenario drills.
  6. Historical Event Mapping: Correct linkage to documented GSI/NRSC disasters.
  7. Client-Side Script & DOM Contracts: Script presence in index.html, CSS animations,
     reduced-motion handling, and accessible legend elements.
  8. Safety & Alert Invariants: Confirm zero public dispatch side-effects.
"""

import os
import pytest
from app import app
from engine.pahad_gis_animation import (
    get_corridor_temporal_risk,
    compute_visual_parameters,
    cri_to_risk_band,
    list_animated_corridors,
    CORRIDOR_HISTORICAL_MAP
)
from engine.canonical_registry import CANONICAL_REGISTRY


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestGisHazardAnimationBackend:
    """Backend engine and API endpoint verification for Phase 12."""

    def test_cri_to_risk_band_mapping(self):
        """Verify authoritative CRI thresholds."""
        assert cri_to_risk_band(10.0) == "LOW"
        assert cri_to_risk_band(29.9) == "LOW"
        assert cri_to_risk_band(30.0) == "MODERATE"
        assert cri_to_risk_band(49.9) == "MODERATE"
        assert cri_to_risk_band(50.0) == "HIGH"
        assert cri_to_risk_band(64.9) == "HIGH"
        assert cri_to_risk_band(65.0) == "VERY HIGH"
        assert cri_to_risk_band(79.9) == "VERY HIGH"
        assert cri_to_risk_band(80.0) == "EXTREME"
        assert cri_to_risk_band(95.0) == "EXTREME"

    def test_compute_visual_parameters_scaling(self):
        """Verify halo radius, opacity, and pulse rate scale monotonically with CRI."""
        v_low = compute_visual_parameters(15.0, 1.4)
        v_med = compute_visual_parameters(40.0, 1.2)
        v_high = compute_visual_parameters(60.0, 1.0)
        v_crit = compute_visual_parameters(85.0, 0.8)

        # Monotonic radius growth
        assert v_low["halo_radius_m"] < v_med["halo_radius_m"] < v_high["halo_radius_m"] < v_crit["halo_radius_m"]
        assert 250 <= v_low["halo_radius_m"] <= 1400
        assert 250 <= v_crit["halo_radius_m"] <= 1400

        # Monotonic opacity scaling
        assert v_low["halo_opacity"] <= v_med["halo_opacity"] <= v_high["halo_opacity"] <= v_crit["halo_opacity"]

        # Pulse rate: static at low, faster at extreme
        assert v_low["pulse_rate_s"] == 0.0
        assert v_med["pulse_rate_s"] == 10.0
        assert v_high["pulse_rate_s"] == 4.0
        assert v_crit["pulse_rate_s"] == 2.0

    def test_live_mode_zero_fabrication(self):
        """Verify LIVE mode provides honest runtime telemetry without inventing past points."""
        res = get_corridor_temporal_risk("SK-NH10-KM48", mode="live")
        assert res["status"] == "SUCCESS"
        assert res["state_type"] == "LIVE"
        assert "[LIVE]" in res["provenance"]
        assert res["corridor_id"] == "SK-NH10-KM48"
        assert "timeline" in res
        # In live mode without past logger, exactly 1 authoritative current step is returned
        assert len(res["timeline"]) == 1
        step0 = res["timeline"][0]
        assert step0["step_id"] == "NOW"
        assert step0["state_type"] == "LIVE"
        assert "[LIVE]" in step0["provenance"]
        assert 0 <= step0["cri"] <= 100
        assert step0["fos"] > 0

    def test_scenario_mode_progression(self):
        """Verify SCENARIO mode generates a 4-stage progressive failure sequence."""
        res = get_corridor_temporal_risk("SK-NH10-KM48", mode="scenario")
        assert res["status"] == "SUCCESS"
        assert res["state_type"] == "SCENARIO"
        assert res["provenance"] == "[SIMULATED]"
        assert len(res["timeline"]) == 4

        steps = res["timeline"]
        # Expected progression: T-24h -> T-12h -> T-6h -> NOW
        assert steps[0]["step_id"] == "T-24h"
        assert steps[1]["step_id"] == "T-12h"
        assert steps[2]["step_id"] == "T-6h"
        assert steps[3]["step_id"] == "NOW"

        # Precipitation increases
        assert steps[0]["rainfall_mm"] < steps[1]["rainfall_mm"] < steps[2]["rainfall_mm"] < steps[3]["rainfall_mm"]
        # CRI increases
        assert steps[0]["cri"] < steps[1]["cri"] < steps[2]["cri"] < steps[3]["cri"]
        # FoS deteriorates
        assert steps[0]["fos"] > steps[1]["fos"] > steps[2]["fos"] > steps[3]["fos"]
        # Halo radius expands
        assert steps[0]["halo_radius_m"] < steps[3]["halo_radius_m"]

        # All steps must be explicitly badged [SIMULATED]
        for s in steps:
            assert s["provenance"] == "[SIMULATED]"
            assert s["state_type"] == "SCENARIO"

    def test_historical_mode_documented_events(self):
        """Verify HISTORICAL mode correctly resolves documented archival landslide events."""
        res_nh10 = get_corridor_temporal_risk("SK-NH10-KM48", mode="historical")
        assert res_nh10["status"] == "SUCCESS"
        assert res_nh10["state_type"] == "HISTORICAL"
        assert res_nh10["provenance"] == "[HISTORICAL]"
        assert res_nh10["disaster_id"] == "DIS-2024-NH10"

        res_tupul = get_corridor_temporal_risk("MN-TUPUL-RLY", mode="historical")
        assert res_tupul["status"] == "SUCCESS"
        assert res_tupul["disaster_id"] == "DIS-2022-NONEY"

        # Uncataloged corridor should return NO_HISTORICAL_RECORD gracefully
        res_uncat = get_corridor_temporal_risk("ML-CHERRA-01", mode="historical")
        assert res_uncat["status"] == "NO_HISTORICAL_RECORD"
        assert res_uncat["historical_available"] is False

    def test_multi_corridor_isolation_and_coverage(self):
        """Verify animation engine supports all canonical corridors across all NER states."""
        corridors = list_animated_corridors()
        assert len(corridors) >= 20

        state_set = set(c["state"] for c in corridors)
        # Must cover all 8 NER states
        for st in ["Sikkim", "Manipur", "Mizoram", "Assam", "Meghalaya", "Nagaland", "Arunachal Pradesh", "Tripura"]:
            assert st in state_set

        # Verify corridor isolation: Sikkim query returns Sikkim coordinates, Assam query returns Assam coordinates
        sk = get_corridor_temporal_risk("SK-NH10-KM48", mode="scenario")
        as_corr = get_corridor_temporal_risk("AS-HAFLONG-RLY", mode="scenario")
        assert sk["state"] == "Sikkim"
        assert as_corr["state"] == "Assam"
        assert abs(sk["latitude"] - as_corr["latitude"]) > 1.0


class TestGisHazardAnimationEndpoints:
    """REST API endpoint contract tests."""

    def test_endpoint_get_live_success(self, client):
        """GET /api/pahad/temporal-risk?corridor_id=SK-NH10-KM48&mode=live"""
        res = client.get("/api/pahad/temporal-risk?corridor_id=SK-NH10-KM48&mode=live")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["corridor_id"] == "SK-NH10-KM48"
        assert data["state_type"] == "LIVE"
        assert "timeline" in data
        assert "current_risk" in data
        assert "visual" in data["current_risk"]

    def test_endpoint_get_scenario_success(self, client):
        """GET /api/pahad/temporal-risk?corridor_id=MN-TUPUL-RLY&mode=scenario"""
        res = client.get("/api/pahad/temporal-risk?corridor_id=MN-TUPUL-RLY&mode=scenario")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["state_type"] == "SCENARIO"
        assert data["provenance"] == "[SIMULATED]"
        assert len(data["timeline"]) == 4

    def test_endpoint_get_historical_success(self, client):
        """GET /api/pahad/temporal-risk?corridor_id=MZ-MELTHUM-QRY&mode=historical"""
        res = client.get("/api/pahad/temporal-risk?corridor_id=MZ-MELTHUM-QRY&mode=historical")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["disaster_id"] == "DIS-2024-AIZAWL"

    def test_endpoint_invalid_corridor_fallback(self, client):
        """GET /api/pahad/temporal-risk with unknown corridor safely falls back or handles error."""
        res = client.get("/api/pahad/temporal-risk?corridor_id=NON-EXISTENT-CORR&mode=live")
        assert res.status_code == 200
        data = res.get_json()
        # Fallback to default NH-10 KM 48
        assert data["status"] == "SUCCESS"
        assert data["corridor_id"] == "SK-NH10-KM48"


class TestGisHazardAnimationFrontendContracts:
    """Verify HTML and static JS files satisfy Phase 12 requirements."""

    def test_script_in_index_html(self, client):
        """Verify pahad_gis_animation.js is included in index.html."""
        res = client.get("/")
        assert res.status_code == 200
        html = res.data.decode("utf-8")
        assert "pahad_gis_animation.js" in html

    def test_upgraded_map_legend_in_index_html(self, client):
        """Verify the 5-tier risk band and 4-tier provenance ontology in map footer."""
        res = client.get("/")
        html = res.data.decode("utf-8")
        # 5-tier bands
        assert "EXTREME" in html
        assert "VERY HIGH" in html
        assert "HIGH" in html
        assert "MODERATE" in html
        assert "LOW" in html
        # Provenance states
        assert "[LIVE]" in html
        assert "[HISTORICAL]" in html
        assert "[MODELLED]" in html
        assert "[SIMULATED]" in html

    def test_js_file_exists_and_contains_core_features(self):
        """Verify static/js/pahad_gis_animation.js defines essential methods and selectors."""
        path = os.path.join("static", "js", "pahad_gis_animation.js")
        assert os.path.exists(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "PahadGisAnimationController" in content
        assert "pahadHazardAnimationPane" in content
        assert "prefers-reduced-motion" in content
        assert "btn-anim-play" in content
        assert "anim-telemetry-bar" in content
        assert "showExplanationModal" in content

    def test_safety_invariants_preserved(self):
        """Verify safety environment variables remain strictly fail-closed."""
        assert os.environ.get("ENABLE_PUBLIC_DISPATCH", "0") == "0"
        assert os.environ.get("SIREN_DRY_RUN", "1") == "1"
        assert os.environ.get("CAP_PRODUCTION_DISPATCH", "0") == "0"
