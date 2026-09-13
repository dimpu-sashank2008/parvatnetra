# -*- coding: utf-8 -*-
"""
tests/test_phase9e_ui_theme.py
==============================
Phase 9E: Government-Style Black-Only Visual System Verification
-----------------------------------------------------------------
Validates:
  1. Strict black-only palette: #050505, #0A0A0A, #111111, #171717, #1D1D1D.
  2. Neutral typography: White / Off-white / Muted Gray.
  3. Risk-only accent colors (green, amber, orange, red).
  4. No white dashboard: light-mode neutralized to prevent white canvas flashing.
  5. High-contrast dark accessibility variant support (#000000).
  6. Institutional government header with 2px tricolor accent.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app as flask_app


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


class TestPhase9eUITheme:
    """Verifies strict black-only palette and accessible government styling."""

    def test_black_canvas_and_cards_css(self, index_html):
        """Root and body styles must enforce #050505 canvas and #111111 cards."""
        assert "--bg-canvas: #050505;" in index_html
        assert "--bg-header: #0A0A0A;" in index_html
        assert "--bg-card: #111111;" in index_html
        assert "--bg-subcard: #171717;" in index_html
        assert "background-color: #050505 !important;" in index_html

    def test_neutral_typography_definitions(self, index_html):
        """Typography variables must define pure white, off-white, and muted gray."""
        assert "--text-heading: #FFFFFF;" in index_html
        assert "--text-body: #E5E5E5;" in index_html
        assert "--text-muted: #A3A3A3;" in index_html

    def test_risk_only_color_variables(self, index_html):
        """Palette must reserve chromatic accents strictly for hazard levels."""
        assert "--risk-low: #16a34a;" in index_html
        assert "--risk-moderate: #d97706;" in index_html
        assert "--risk-high: #ea580c;" in index_html
        assert "--risk-extreme: #b91c1c;" in index_html or "--risk-extreme: #dc2626;" in index_html

    def test_no_white_dashboard_enforced(self, index_html):
        """Light-mode overrides must be neutralized to dark charcoal, never white."""
        assert "body.light-mode" in index_html
        assert "body.light-mode {\n            background-color: #0A0A0A !important;" in index_html or \
               "background-color: #0A0A0A !important;" in index_html

    def test_high_contrast_dark_mode_supported(self, index_html):
        """High-contrast accessibility mode must use #000000 background."""
        assert "body.high-contrast-mode" in index_html
        assert "background-color: #000000 !important;" in index_html

    def test_institutional_header_tricolor_accent(self, index_html):
        """Institutional header must feature 2px tricolor divider accent."""
        assert "#system-header-bar" in index_html
        assert "#FF9933" in index_html
        assert "#138808" in index_html
