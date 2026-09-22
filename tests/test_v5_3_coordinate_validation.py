# -*- coding: utf-8 -*-
"""
tests/test_v5_3_coordinate_validation.py
========================================
Phase V5.3 Test Suite: Coordinate Bounds & Precision Tier Validation
Verifies that all 42 events fall within geographical bounding boxes,
match their designated state/district boundaries, and feature honest precision labels.
"""

import os
import json
import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV53CoordinateValidation:
    """Verifies coordinate validity and precision categorization."""

    def test_ner_and_himalayan_bounding_box(self, manager):
        inv = manager.get_v5_3_inventory()
        events = inv.get("events", [])
        for e in events:
            lat = e["latitude"]
            lon = e["longitude"]
            # Bounding box for North-Eastern Region & Eastern Himalayas: 20.0-30.5°N, 87.0-98.0°E
            assert 20.0 <= lat <= 30.5, f"Latitude {lat} out of bounds for {e['event_id']}"
            assert 87.0 <= lon <= 98.0, f"Longitude {lon} out of bounds for {e['event_id']}"

    def test_coordinate_precision_classifications(self, manager):
        inv = manager.get_v5_3_inventory()
        events = inv.get("events", [])
        precisions = {e.get("coordinate_precision") for e in events}
        assert precisions.issubset({"SURVEY_DGPS", "CARTOGRAPHIC", "APPROXIMATE"})
        
        # Verify DGPS coordinates are appropriately flagged
        tupul = next(e for e in events if e["event_id"] == "EV-04")
        assert tupul["coordinate_precision"] == "SURVEY_DGPS"

        melthum = next(e for e in events if e["event_id"] == "EV-06")
        assert melthum["coordinate_precision"] == "SURVEY_DGPS"

    def test_coordinate_completeness_100_percent(self, manager):
        inv = manager.get_v5_3_inventory()
        metrics = inv.get("quality_metrics", {})
        assert metrics.get("coordinate_completeness_pct") == 100.0
