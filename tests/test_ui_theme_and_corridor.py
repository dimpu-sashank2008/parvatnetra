# -*- coding: utf-8 -*-
"""
tests/test_ui_theme_and_corridor.py
===================================
Tests verifying:
1. CRI circular indicator CSS variables, contrast rules, and risk band classes.
2. Theme toggle DOM markup, sun/moon icon elements, accessible tooltips, and theme persistence logic.
3. Corridor selector dropdown containing the 8 canonical SECTOR_REGISTRY entries.
4. /api/pahad/live-inference response schema and real calculation integrity.
5. Zero fake data behavior and error boundaries.
"""

import os
import re
import pytest
from app import app as flask_app
from engine.sector_snapshot import SECTOR_REGISTRY

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")


@pytest.fixture
def index_html():
    """Load index.html content."""
    assert os.path.exists(TEMPLATE_PATH), f"Template not found at {TEMPLATE_PATH}"
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def client():
    """Flask test client."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


class TestCriCircleContrast:
    """Verifies that the CRI circle is fully accessible in both Light and Dark modes."""

    def test_theme_aware_css_variables_defined(self, index_html):
        """Root and body:not(.light-mode) must define CRI theme variables."""
        assert "--cri-track-bg" in index_html
        assert "--cri-inner-bg" in index_html
        assert "--cri-inner-border" in index_html
        assert "--cri-score-color" in index_html
        assert "--cri-unit-color" in index_html
        assert "--cri-ring-shadow" in index_html

    def test_light_mode_inner_circle_contrast_fix(self, index_html):
        """Light mode must explicitly set a light background for .pahad-ai-ring:before."""
        assert "body.light-mode .pahad-ai-ring:before" in index_html
        assert "#ffffff !important" in index_html or "background:#ffffff" in index_html
        assert "body.light-mode .pahad-ai-score-num" in index_html
        assert "color:#0f172a !important" in index_html

    def test_risk_band_accessible_classes(self, index_html):
        """Accessible contrast classes for all 5 risk tiers must be defined."""
        assert ".pahad-band-low" in index_html
        assert ".pahad-band-moderate" in index_html
        assert ".pahad-band-high" in index_html
        assert ".pahad-band-very-high" in index_html
        assert ".pahad-band-extreme" in index_html


class TestThemeToggleUI:
    """Verifies the professional government theme toggle button and JS behavior."""

    def test_theme_toggle_button_dom(self, index_html):
        """Header must contain an accessible theme toggle button."""
        assert 'id="theme-toggle-btn"' in index_html
        assert 'id="theme-icon"' in index_html
        assert 'id="theme-text"' in index_html
        assert "toggleTheme()" in index_html
        assert 'aria-label="Switch to light mode"' in index_html

    def test_theme_toggle_js_functions(self, index_html):
        """JS must define toggleTheme, updateThemeUI, and initTheme with clean symbol toggles."""
        assert "function toggleTheme()" in index_html
        assert "function updateThemeUI(isLight)" in index_html
        assert "function initTheme()" in index_html
        assert "ph-sun" in index_html
        assert "ph-moon" in index_html
        assert "localStorage.setItem('parvat_theme'" in index_html


class TestCorridorSelectorUI:
    """Verifies the corridor selection dropdown in the Highest-Risk Prediction card."""

    def test_corridor_select_element_exists(self, index_html):
        """Card must contain #pahad-corridor-select with onchange handler."""
        assert 'id="pahad-corridor-select"' in index_html
        assert "onCorridorSelectionChanged(this.value)" in index_html

    def test_all_eight_canonical_sectors_present(self, index_html):
        """All 8 sectors from canonical SECTOR_REGISTRY must be selectable."""
        expected_sectors = [
            "SK-NH10-KM48",
            "MN-TUPUL-RLY",
            "MZ-MELTHUM-QRY",
            "AS-HAFLONG-RLY",
            "ML-MAWSYNRAM",
            "NL-DZUKOU-KOH",
            "AR-TAWANG-SELA",
            "TR-JAMPUI-HILLS"
        ]
        for sec_id in expected_sectors:
            assert f'value="{sec_id}"' in index_html, f"Sector {sec_id} missing from dropdown"

    def test_corridor_status_elements(self, index_html):
        """Corridor loading indicator and timestamp elements must exist."""
        assert 'id="pahad-corridor-loading"' in index_html
        assert 'id="pahad-corridor-timestamp"' in index_html

    def test_js_corridor_handler_and_map_sync(self, index_html):
        """JS must define PAHAD_SECTOR_REGISTRY, onCorridorSelectionChanged, and flyTo map sync."""
        assert "const PAHAD_SECTOR_REGISTRY =" in index_html
        assert "async function onCorridorSelectionChanged(sectorId)" in index_html
        assert "window.map.flyTo" in index_html


class TestLiveInferenceEndpoint:
    """Verifies backend live inference endpoint supports corridor querying."""

    def test_live_inference_sikkim_corridor(self, client):
        """GET /api/pahad/live-inference for SK-NH10-KM48 returns 200 with valid schema."""
        sec = SECTOR_REGISTRY["SK-NH10-KM48"]
        res = client.get(f"/api/pahad/live-inference?sector_id=SK-NH10-KM48&latitude={sec['lat']}&longitude={sec['lon']}&horizon_hours=24")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        inf = data["inference"]
        assert "cri" in inf
        assert "risk_band" in inf
        assert "fos_physical" in inf
        assert "event_probability" in inf
        assert 0 <= inf["cri"] <= 100
        assert inf["sector_id"] == "SK-NH10-KM48"

    def test_live_inference_manipur_corridor(self, client):
        """GET /api/pahad/live-inference for MN-TUPUL-RLY returns 200 with valid schema."""
        sec = SECTOR_REGISTRY["MN-TUPUL-RLY"]
        res = client.get(f"/api/pahad/live-inference?sector_id=MN-TUPUL-RLY&latitude={sec['lat']}&longitude={sec['lon']}&horizon_hours=24")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["inference"]["sector_id"] == "MN-TUPUL-RLY"

    def test_live_inference_invalid_coords_boundary(self, client):
        """GET /api/pahad/live-inference handles invalid coordinates gracefully (422)."""
        res = client.get("/api/pahad/live-inference?sector_id=INVALID&latitude=bad_lat&longitude=bad_lon")
        assert res.status_code == 422
        data = res.get_json()
        assert data["status"] == "ERROR"


class TestPipelineRibbonCleanUI:
    """Verifies that the PAHAD AI Pipeline Ribbon uses clean, simple text without boxed badges or rainbow colors."""

    def test_pipeline_ribbon_structure(self, index_html):
        """Pipeline ribbon container exists with faded saffron styling."""
        assert 'id="pahad-pipeline-ribbon"' in index_html
        assert "PAHAD AI Pipeline:" in index_html

    def test_pipeline_steps_have_no_boxes_or_bg_colors(self, index_html):
        """Step spans must be clean text without background pill boxes or multiple background colors."""
        # Find the pipeline ribbon inner HTML
        match = re.search(r'id="pahad-pipeline-ribbon".*?<\/div>\s*<\/div>\s*<\/div>', index_html, re.DOTALL)
        assert match is not None, "Could not locate pahad-pipeline-ribbon markup"
        ribbon_html = match.group(0)

        # All 8 canonical steps must exist as clean pipeline-step elements
        steps = ["DATA", "PHYSICS (FoS)", "ML (P_event)", "EVIDENCE", "PAHAD AI", "CRI", "2-of-3 CORROBORATION", "AUTHORITY DECISION"]
        for step in steps:
            assert step in ribbon_html, f"Step '{step}' missing from ribbon"

        # Assert no pill box classes on step spans
        assert 'bg-blue-950' not in ribbon_html
        assert 'bg-purple-950' not in ribbon_html
        assert 'bg-rose-950' not in ribbon_html
        assert 'bg-indigo-950' not in ribbon_html
        assert 'bg-amber-950' not in ribbon_html
        assert 'bg-emerald-950' not in ribbon_html
        assert 'pipeline-step' in ribbon_html
        assert 'pipeline-arrow' in ribbon_html

