# -*- coding: utf-8 -*-
"""
tests/test_phase9c_corridor.py
==============================
Phase 9C: Cascading Corridor Selector and Spatial Footprint Test Suite.

Verifies:
1. Cascading State -> District -> Strategic Corridor hierarchy.
2. Canonical 8 NER states coverage in registry and select elements.
3. "Use Map Location" button for arbitrary point picking.
4. Embedded mini-map container and coordinates display.
5. JavaScript functions for cascading filter synchronization.
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


class TestPhase9cCorridorSelector:
    """Verifies cascading corridor selector structure and JavaScript handlers."""

    def test_state_filter_element(self, index_html):
        """State filter select must exist with onchange handler."""
        assert 'id="pahad-state-filter"' in index_html
        assert "onStateFilterChanged(this.value)" in index_html
        # All 8 NER States present as options
        for state in ["Sikkim", "Manipur", "Mizoram", "Assam", "Meghalaya", "Nagaland", "Arunachal Pradesh", "Tripura"]:
            assert state in index_html

    def test_district_filter_element(self, index_html):
        """District filter select must exist between state and corridor."""
        assert 'id="pahad-district-filter"' in index_html
        assert "onDistrictFilterChanged(this.value)" in index_html

    def test_corridor_select_element(self, index_html):
        """Strategic corridor select must exist with onchange handler."""
        assert 'id="pahad-corridor-select"' in index_html
        assert "onCorridorSelectionChanged(this.value)" in index_html

    def test_use_map_location_button(self, index_html):
        """Use Map Location button must exist and invoke picker."""
        assert 'id="btn-pick-map-loc"' in index_html
        assert "Use Map Location" in index_html
        assert "toggleMapPointPicker()" in index_html

    def test_mini_map_footprint_container(self, index_html):
        """Mini-map footprint container and coordinates display must exist."""
        assert 'id="pahad-prediction-minimap"' in index_html
        assert 'id="pahad-minimap-coords"' in index_html

    def test_cascading_js_functions(self, index_html):
        """JavaScript functions for cascading filtering and mini-map must exist."""
        assert "function populateDistrictSelectOptions(" in index_html
        assert "function onDistrictFilterChanged(" in index_html
        assert "function populateCorridorSelectOptions(" in index_html
        assert "function updatePredictionMiniMap(" in index_html
        assert "window.populateDistrictSelectOptions = populateDistrictSelectOptions;" in index_html
        assert "window.onDistrictFilterChanged = onDistrictFilterChanged;" in index_html
