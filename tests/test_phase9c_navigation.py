# -*- coding: utf-8 -*-
"""
tests/test_phase9c_navigation.py
================================
Phase 9C: EOC Navigation Drawer and Workspace Switching Test Suite.

Verifies:
1. Hamburger menu button with aria attributes.
2. Slide-out EOC navigation drawer and backdrop.
3. Six organized operational navigation categories:
   - PAHAD AI CORE
   - MAP & TERRAIN INTELLIGENCE
   - FIELD OPERATIONS & SITREP
   - EOC COMMAND & INCIDENTS
   - EMERGENCY RESPONSE & ACTION
   - SYSTEM & AUDIT
4. Workspace view containers:
   - #view-prediction
   - #view-map
   - #view-response
   - #view-system
5. Client-side navigation functions (toggleSidebarMenu, navigateToPanel).
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


class TestPhase9cNavigation:
    """Tests navigation drawer, hamburger controls, and workspace panel transitions."""

    def test_hamburger_button_exists(self, index_html):
        """Hamburger button must be present in header before the national emblem."""
        assert 'id="btn-hamburger-menu"' in index_html
        assert "toggleSidebarMenu()" in index_html
        assert 'aria-label="Toggle EOC Navigation Menu"' in index_html
        assert 'aria-expanded="false"' in index_html

    def test_eoc_sidebar_drawer_and_backdrop(self, index_html):
        """Sidebar drawer and backdrop overlay must exist."""
        assert 'id="eoc-sidebar-drawer"' in index_html
        assert 'id="eoc-sidebar-backdrop"' in index_html
        assert "eoc-sidebar-drawer" in index_html

    def test_six_navigation_categories_present(self, index_html):
        """Sidebar must contain all 6 organized operational categories."""
        assert "PAHAD AI" in index_html
        assert "MAP &amp; TERRAIN" in index_html or "MAP & TERRAIN" in index_html
        assert "FIELD OPERATIONS" in index_html
        assert "EOC COMMAND" in index_html
        assert "RESPONSE" in index_html
        assert "SYSTEM" in index_html

    def test_workspace_view_containers(self, index_html):
        """All 4 workspace views must be defined in the DOM."""
        assert 'id="view-prediction"' in index_html
        assert 'id="view-map"' in index_html
        assert 'id="view-response"' in index_html
        assert 'id="view-system"' in index_html

    def test_navigation_js_functions(self, index_html):
        """JavaScript functions toggleSidebarMenu and navigateToPanel must be defined and exported."""
        assert "function toggleSidebarMenu(" in index_html
        assert "function navigateToPanel(" in index_html
        assert "window.toggleSidebarMenu = toggleSidebarMenu;" in index_html
        assert "window.navigateToPanel = navigateToPanel;" in index_html

    def test_sidebar_links_have_navigation_triggers(self, index_html):
        """Sidebar items must trigger navigateToPanel."""
        assert "navigateToPanel('prediction')" in index_html
        assert "navigateToPanel('map')" in index_html
        assert "navigateToPanel('response')" in index_html
        assert "navigateToPanel('system')" in index_html
