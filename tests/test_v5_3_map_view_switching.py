# -*- coding: utf-8 -*-
"""
tests/test_v5_3_map_view_switching.py
======================================
PARVAT NETRA • PAHAD AI — Phase V5.3 2D <-> 3D Map View Switching Test Suite
"""

import os
import pytest


def test_v5_3_template_contains_gods_eye_container():
    """Verify that templates/index.html contains #gods-eye-3d-container inside #gis-map."""
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
    assert os.path.exists(template_path)

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert 'id="gods-eye-3d-container"' in content
    assert 'class="hidden absolute inset-0 w-full h-full z-[300]"' in content


def test_v5_3_template_contains_gods_eye_switcher_button():
    """Verify that templates/index.html includes God's Eye 3D button in the Map Style panel."""
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert 'id="mb-gods-eye"' in content
    assert "switchMainBasemap('gods-eye-3d')" in content
    assert "God's Eye 3D" in content


def test_v5_3_switch_main_basemap_javascript_logic():
    """Verify that switchMainBasemap() properly handles 'gods-eye-3d' activation and deactivation."""
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "if (type === 'gods-eye-3d')" in content
    assert "window.GodsEye3D.activate()" in content
    assert "window.GodsEye3D.deactivate()" in content
    assert "mb-gods-eye" in content


def test_v5_3_gods_eye_script_tag_included():
    """Verify that static/js/gods_eye_3d.js is loaded in index.html."""
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert '<script src="/static/js/gods_eye_3d.js"></script>' in content


def test_v5_3_gods_eye_exit_opens_primary_map():
    """Verify that exiting God's Eye 3D mode directly opens the primary map (ISRO Bhuvan satellite)."""
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "function exitGodsEye3D()" in content
    assert "window.exitGodsEye3D = exitGodsEye3D" in content
    assert "exitGodsEye3D()" in content
    assert "gis-map-card" in content

    # Check that static/js/gods_eye_3d.js also exits to primary map
    js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "gods_eye_3d.js")
    with open(js_path, "r", encoding="utf-8") as f:
        js_content = f.read()

    assert "exitGodsEye3D" in js_content
    assert "switchMainBasemap('bhuvan')" in js_content
