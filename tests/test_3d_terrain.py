# -*- coding: utf-8 -*-
"""
PARVAT NETRA - 3D Digital Elevation Model (DEM) & Contour Engine Test Suite
SIH Problem Statement ID: 26001 (MDoNER)

Validates:
1. Three.js r128 and OrbitControls CDN script tags in templates/index.html.
2. #modal-3d-terrain, #canvas-3d-container, HUD badge, and toolbar controls in DOM.
3. Three.js parametric terrain mesh, procedural contour shader, and slip plane engine.
4. Toggle functions for contours (toggle3DContours) and slip plane (toggle3DSlipPlane).
5. UI trigger buttons in Decision Intelligence Card and Leaflet GIS popups.
6. Flask web server response on http://127.0.0.1:8080/ serving 3D visualizer assets.
"""

import os
import unittest
import urllib.request
import urllib.error

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_PATH = os.path.join(REPO_ROOT, 'templates', 'index.html')


class Test3DTerrain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            cls.html = f.read()

    def test_01_threejs_and_orbitcontrols_cdns(self):
        """Verify Three.js r128 and OrbitControls libraries are included in <head>."""
        self.assertIn('three.min.js', self.html, "Three.js CDN script tag missing from templates/index.html")
        self.assertIn('OrbitControls.js', self.html, "OrbitControls CDN script tag missing from templates/index.html")
        self.assertIn('three.js/r128/three.min.js', self.html, "Three.js r128 CDN URL missing")
        self.assertIn('three@0.128.0/examples/js/controls/OrbitControls.js', self.html, "OrbitControls r128 CDN URL missing")
        print("[PASS] Test 1: Three.js r128 and OrbitControls CDN libraries verified.")

    def test_02_modal_3d_terrain_dom(self):
        """Verify #modal-3d-terrain, #canvas-3d-container, and toolbar controls exist in DOM."""
        self.assertIn('id="modal-3d-terrain"', self.html, "#modal-3d-terrain container missing")
        self.assertIn('id="canvas-3d-container"', self.html, "#canvas-3d-container viewport missing")
        self.assertIn('id="3d-modal-title"', self.html, "#3d-modal-title missing")
        self.assertIn('id="3d-modal-subtitle"', self.html, "#3d-modal-subtitle missing")
        self.assertIn('id="btn-toggle-contours"', self.html, "#btn-toggle-contours button missing")
        self.assertIn('id="btn-toggle-slipplane"', self.html, "#btn-toggle-slipplane button missing")
        self.assertIn('Terrain Geometrics', self.html, "HUD Terrain Geometrics badge missing")
        self.assertIn('Contour Interval', self.html, "HUD Contour Interval specification missing")
        print("[PASS] Test 2: #modal-3d-terrain DOM structure and HUD overlay verified.")

    def test_03_threejs_terrain_and_contour_shader(self):
        """Verify Three.js WebGL terrain, procedural contour shader, and slip plane engine."""
        self.assertIn('open3DTerrainModel', self.html, "open3DTerrainModel function missing")
        self.assertIn('close3DTerrainModal', self.html, "close3DTerrainModal function missing")
        self.assertIn('init3DScene', self.html, "init3DScene function missing")
        self.assertIn('THREE.PerspectiveCamera', self.html, "PerspectiveCamera initialization missing")
        self.assertIn('THREE.WebGLRenderer', self.html, "WebGLRenderer initialization missing")
        self.assertIn('THREE.OrbitControls', self.html, "OrbitControls initialization missing")
        self.assertIn('THREE.PlaneGeometry', self.html, "PlaneGeometry parametric terrain missing")
        self.assertIn('THREE.ShaderMaterial', self.html, "Custom procedural ShaderMaterial for contours missing")
        self.assertIn('contourInterval', self.html, "contourInterval uniform missing from shader")
        self.assertIn('slipPlaneMesh', self.html, "slipPlaneMesh subterranean failure plane missing")
        print("[PASS] Test 3: Three.js WebGL terrain geometry and procedural contour shader verified.")

    def test_04_toggle_functions_and_controls(self):
        """Verify toggle3DContours, toggle3DSlipPlane, and reset3DCamera logic."""
        self.assertIn('toggle3DContours', self.html, "toggle3DContours function missing")
        self.assertIn('toggle3DSlipPlane', self.html, "toggle3DSlipPlane function missing")
        self.assertIn('reset3DCamera', self.html, "reset3DCamera function missing")
        self.assertIn('showContours', self.html, "showContours state variable missing")
        self.assertIn('showSlipPlane', self.html, "showSlipPlane state variable missing")
        print("[PASS] Test 4: Dynamic contour toggles, slip plane toggles, and camera reset verified.")

    def test_05_ui_triggers_integration(self):
        """Verify 3D terrain triggers on Decision Card and in Leaflet hazard popups."""
        self.assertIn("open3DTerrainModel('NH-10 Km 48 (29th Mile Sector)', 0.745)", self.html,
                      "Decision Card 3D inspection trigger missing")
        self.assertIn('Inspect 3D Digital Elevation Model (DEM)', self.html,
                      "Inspect 3D Digital Elevation Model button text missing")
        self.assertIn('Open 3D Model', self.html,
                      "Leaflet popup 'Open 3D Model' button missing")
        print("[PASS] Test 5: UI triggers in Decision Intelligence Card and Leaflet popups verified.")

    def test_06_server_serves_3d_terrain(self):
        """Verify Flask web server serves index.html with 3D components on http://127.0.0.1:8080/."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8080/")
            with urllib.request.urlopen(req, timeout=5) as response:
                status_code = response.getcode()
                body = response.read().decode('utf-8')
                self.assertEqual(status_code, 200, f"Expected 200, got {status_code}")
                self.assertIn('modal-3d-terrain', body, "#modal-3d-terrain not found in live page response")
                self.assertIn('canvas-3d-container', body, "#canvas-3d-container not found in live page response")
                self.assertIn('three.min.js', body, "Three.js CDN script not found in live page response")
                print(f"[PASS] Test 6: Live server returns HTTP {status_code} with 3D DEM components.")
        except urllib.error.URLError as e:
            self.fail(f"Flask server at http://127.0.0.1:8080/ unreachable: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
