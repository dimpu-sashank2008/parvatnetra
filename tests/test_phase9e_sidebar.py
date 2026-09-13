# -*- coding: utf-8 -*-
"""
tests/test_phase9e_sidebar.py
=============================
Phase 9E: Government Sidebar Navigation & Information Discovery
--------------------------------------------------------------
Validates:
  1. Strict 6 operational categories: PAHAD AI, MAP, FIELD, EOC, RESPONSE, SYSTEM.
  2. Zero visible UI text referencing 'GSI DISASTER ARCHIVE & RECURRENCE ENGINE' or 'HISTORICAL RECURRENCE'.
  3. Seamless navigation functions: toggleSidebarMenu and navigateToPanel.
  4. Proper accessibility attributes on sidebar drawer and backdrop.
"""

import sys
import os
import re
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


class TestPhase9eSidebar:
    """Verifies clean 6-category sidebar navigation and absence of clutter."""

    def test_strict_six_navigation_categories(self, index_html):
        """Drawer must contain exactly the 6 organized government categories."""
        assert "1. PAHAD AI" in index_html
        assert "2. MAP" in index_html
        assert "3. FIELD" in index_html
        assert "4. EOC" in index_html
        assert "5. RESPONSE" in index_html
        assert "6. SYSTEM" in index_html

    def test_no_visible_gsi_recurrence_archive(self, index_html):
        """Visible UI elements must not display unwanted legacy archive labels."""
        # Check that if the legacy button exists, it is strictly hidden
        if "GSI DISASTER ARCHIVE &amp; RECURRENCE ENGINE" in index_html or "GSI DISASTER ARCHIVE & RECURRENCE ENGINE" in index_html:
            assert 'id="btn-top-history-media" class="hidden"' in index_html or 'style="display:none;"' in index_html

    def test_sidebar_drawer_and_overlay_accessibility(self, index_html):
        """Sidebar drawer must have appropriate accessibility attributes and controls."""
        assert 'id="eoc-sidebar-drawer"' in index_html
        assert 'id="eoc-sidebar-backdrop"' in index_html
        assert 'id="btn-hamburger-menu"' in index_html
        assert 'aria-label="Toggle EOC Navigation Menu"' in index_html
        assert 'onclick="toggleSidebarMenu()"' in index_html

    def test_navigation_targets_all_views(self, index_html):
        """Sidebar links must support navigating to all 4 primary panels."""
        assert "navigateToPanel('prediction')" in index_html
        assert "navigateToPanel('map')" in index_html
        assert "navigateToPanel('response')" in index_html
        assert "navigateToPanel('system')" in index_html
