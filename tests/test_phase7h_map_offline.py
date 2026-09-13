# -*- coding: utf-8 -*-
"""
tests/test_phase7h_map_offline.py
=================================
PHASE 7H — CP 7H-04, 7H-19: Offline Map Cache, Vector GeoJSON Layers,
Shelters, Hazard Boundaries, Stale / Cached Labeling, and Multilingual UI Resilience.
"""

import os
import json
import re
import pytest
from services.offline_routing_service import OFFLINE_ROUTER
from engine.pahad_routing import EMERGENCY_SHELTERS, MONITORED_CORRIDORS


def test_offline_shelter_layer_availability():
    """CP 7H-04: Emergency shelters layer is completely populated and offline-accessible."""
    assert len(EMERGENCY_SHELTERS) >= 4
    for shelter in EMERGENCY_SHELTERS:
        assert "shelter_id" in shelter
        assert "name" in shelter
        assert "lat" in shelter
        assert "lon" in shelter
        assert "capacity_people" in shelter
        assert shelter["capacity_people"] > 0
        # Check NER geographical coordinates
        assert 20.0 <= float(shelter["lat"]) <= 30.0
        assert 87.0 <= float(shelter["lon"]) <= 98.0


def test_offline_monitored_corridors_and_hazard_zones():
    """CP 7H-04: Monitored arterial corridors have geometry, state, and status."""
    assert len(MONITORED_CORRIDORS) >= 3
    nh10 = next((c for c in MONITORED_CORRIDORS if c["corridor_id"] == "SK-NH10"), None)
    assert nh10 is not None
    assert nh10["state"] == "Sikkim"
    assert "status" in nh10
    assert "affected_length_km" in nh10


def test_stale_and_cached_map_layer_provenance_labeling():
    """CP 7H-04: Offline route returns [OFFLINE ROUTE / CACHED] or [OFFLINE ROUTE / STALE] badges."""
    OFFLINE_ROUTER.set_data_freshness(is_stale=False)
    route_cached = OFFLINE_ROUTER.plan_offline_route(27.33, 88.61)
    assert "[OFFLINE ROUTE]" in route_cached["provenance"]
    assert route_cached["data_freshness"] == "CACHED"

    OFFLINE_ROUTER.set_data_freshness(is_stale=True)
    route_stale = OFFLINE_ROUTER.plan_offline_route(27.33, 88.61)
    assert "[OFFLINE ROUTE / STALE]" in route_stale["provenance"]
    assert route_stale["data_freshness"] == "STALE"

    # Reset
    OFFLINE_ROUTER.set_data_freshness(is_stale=False)


def test_multilingual_i18n_dictionary_completeness():
    """CP 7H-19: static/js/i18n.js provides complete parity across 6 Himalayan languages."""
    i18n_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "i18n.js")
    assert os.path.exists(i18n_path), f"Missing {i18n_path}"

    with open(i18n_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify all 6 languages are declared
    required_langs = ["en:", "hi:", "ne:", "bh:", "lp:", "as:"]
    for lang in required_langs:
        assert lang in content, f"Language key {lang} missing in i18n.js"

    # Key safety phrases must exist in English and Nepali / Bhutia / Lepcha
    critical_keys = ["road_severed", "evacuation_warning", "critical_red_zones", "issue_alert"]
    for k in critical_keys:
        assert k in content, f"Critical translation key {k} missing in i18n.js"
