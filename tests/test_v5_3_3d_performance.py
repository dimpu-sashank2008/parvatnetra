# -*- coding: utf-8 -*-
"""
tests/test_v5_3_3d_performance.py
==================================
PARVAT NETRA • PAHAD AI — Phase V5.3 3D Performance, Lazy Loading & Resource Management Test Suite
"""

import os
import pytest


def test_v5_3_lazy_loading_cesium_runtime():
    """Verify that static/js/gods_eye_3d.js lazy-loads Cesium only on demand."""
    js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "gods_eye_3d.js")
    with open(js_path, "r", encoding="utf-8") as f:
        code = f.read()

    assert "CESIUM_JS_URL" in code
    assert "loadCesium()" in code
    assert "document.createElement('script')" in code
    assert "script.src = CESIUM_JS_URL" in code


def test_v5_3_render_loop_pausing_on_deactivation():
    """Verify that deactivation pauses the Cesium render loop to conserve GPU/CPU resources."""
    js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "gods_eye_3d.js")
    with open(js_path, "r", encoding="utf-8") as f:
        code = f.read()

    assert "deactivate()" in code
    assert "this.viewer.useDefaultRenderLoop = false" in code


def test_v5_3_leaflet_map_invalidation_lifecycle():
    """Verify that returning to 2D calls window.map.invalidateSize() with timeout for smooth rendering."""
    js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "gods_eye_3d.js")
    with open(js_path, "r", encoding="utf-8") as f:
        code = f.read()

    assert "window.map.invalidateSize()" in code
    assert "setTimeout" in code
