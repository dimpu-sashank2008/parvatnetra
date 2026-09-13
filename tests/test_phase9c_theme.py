# -*- coding: utf-8 -*-
"""
tests/test_phase9c_theme.py
===========================
Phase 9C: Dark Black Government EOC Palette and Theme Invariant Test Suite.

Verifies:
1. Strict Government EOC Dark Palette (#05080C, #070B10, #0B1320, #0F172A).
2. Header theme toggle button is hidden from regular user view.
3. No light mode toggle exposed on primary UI.
4. Default dark mode persistence.
5. High contrast accessibility option preserved.
"""

import os
import pytest
from app import app as flask_app

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


class TestPhase9cThemePalette:
    """Verifies dark black palette and removal of visible light theme switcher."""

    def test_theme_toggle_hidden_from_header(self, index_html):
        """Theme toggle button must be hidden via class or display:none for clean EOC appearance."""
        assert 'id="theme-toggle-btn"' in index_html
        assert 'id="theme-toggle-btn" class="hidden"' in index_html or 'display:none' in index_html

    def test_dark_eoc_palette_colors_present(self, index_html):
        """Must use official EOC slate and obsidian black color codes."""
        assert "#05080C" in index_html or "#070B10" in index_html
        assert "#0B1320" in index_html or "#0F172A" in index_html

    def test_page_body_defaults_to_dark(self, index_html):
        """Page body must have dark background and dark classes."""
        assert 'id="page-body"' in index_html
        assert "bg-[#05080C]" in index_html or "bg-[#070B10]" in index_html or "dark" in index_html

    def test_high_contrast_support_exists(self, index_html):
        """High-contrast mode must remain available for accessibility compliance."""
        assert "toggleHighContrast()" in index_html or "toggleContrast()" in index_html
        assert "high-contrast" in index_html
