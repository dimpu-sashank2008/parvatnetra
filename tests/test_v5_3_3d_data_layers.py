# -*- coding: utf-8 -*-
"""
tests/test_v5_3_3d_data_layers.py
=================================
PARVAT NETRA • PAHAD AI — Phase V5.3 3D Synchronized Data Layers Test Suite
"""

import os
import pytest


def test_v5_3_gods_eye_js_contains_all_core_layers():
    """Verify that static/js/gods_eye_3d.js defines all required 3D layers."""
    js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "gods_eye_3d.js")
    assert os.path.exists(js_path)

    with open(js_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Corridor polyline
    assert "corridorPolyline" in code
    assert "NH-10 Teesta Corridor Polyline" in code

    # FoS slip plane
    assert "fosMarker" in code
    assert "KM48 ESCARPMENT" in code
    assert "FoS: 1.04" in code

    # Weather layer
    assert "weatherMarker" in code
    assert "WEATHER [LIVE]" in code

    # Seismic layer
    assert "seismicMarker" in code
    assert "SEISMIC [LIVE]" in code

    # InSAR layer
    assert "insarMarker" in code
    assert "InSAR LOS" in code

    # Sensor markers
    assert "sensorMarkers" in code
    assert "Piezometer Borehole" in code
    assert "Biaxial Tiltmeter" in code
    assert "Inclinometer Casing" in code


def test_v5_3_cri_5_tier_color_bands_in_legend():
    """Verify that 3D HUD legend displays CRI 5-tier risk classifications."""
    js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "gods_eye_3d.js")
    with open(js_path, "r", encoding="utf-8") as f:
        code = f.read()

    assert "3D TERRAIN LAYERS" in code
    assert "CRI Extreme" in code
    assert "FoS &lt; 1.10" in code or "FoS < 1.10" in code
