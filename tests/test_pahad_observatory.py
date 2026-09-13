# -*- coding: utf-8 -*-
"""
tests/test_pahad_observatory.py
===============================
Automated test suite for PAHAD AI Observatory UI and Multimodal Intelligence Command.
Covers:
- /pahad-ai route availability and 200 OK status
- 3D terrain canvas viewport (Three.js GLO-30 DEM container)
- 6 converging evidence telemetry streams
- 8-Stage Interactive Model Stepper (Ingest -> Fuse -> Forecast -> Verify -> Explain -> Warn -> Route -> Respond)
- AI Mathematics display blocks (Mohr-Coulomb FoS, Composite Risk Index CRI, Mandal-Sarkar I-D curve)
- Interactive AI Calculation Visualizer / Simulator with 7 sliders and real-time meters
- Live Inference Trace streaming log
- Model Transparency & Honest Limitations disclosures (GBDT status, surrogate LSTM label)
"""

import os
import unittest

os.environ["PARVAT_TESTING"] = "1"

from app import app


class TestPahadObservatory(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_pahad_ai_route_status(self):
        """Verify GET /pahad-ai returns HTTP 200 OK."""
        resp = self.client.get("/pahad-ai")
        self.assertEqual(resp.status_code, 200)

    def test_observatory_branding_and_title(self):
        """Verify institutional branding lockup and official titles."""
        resp = self.client.get("/pahad-ai")
        html = resp.get_data(as_text=True)
        self.assertIn("PAHAD AI OBSERVATORY", html)
        self.assertIn("PARVAT NETRA", html)
        self.assertIn("Predictive Hillslope Intelligence Observatory", html)

    def test_threejs_3d_terrain_canvas_present(self):
        """Verify Three.js DEM 3D canvas viewport and controls exist."""
        resp = self.client.get("/pahad-ai")
        html = resp.get_data(as_text=True)
        self.assertIn('id="observatory-three-canvas"', html)
        self.assertIn("three.min.js", html)
        self.assertIn("OrbitControls.js", html)
        self.assertIn("Reset 3D View", html)
        self.assertIn("Full 3D Terrain Studio", html)

    def test_converging_multimodal_evidence_streams(self):
        """Verify the 6 converging evidence streams are present."""
        resp = self.client.get("/pahad-ai")
        html = resp.get_data(as_text=True)
        self.assertIn("CLIMATE STREAM", html)
        self.assertIn("TERRAIN STREAM", html)
        self.assertIn("GROUND IN-SITU", html)
        self.assertIn("SATELLITE EO", html)
        self.assertIn("SEISMIC STREAM", html)
        self.assertIn("HISTORICAL ARCHIVE", html)

    def test_eight_stage_model_stepper(self):
        """Verify the 8-stage interactive model stepper is present."""
        resp = self.client.get("/pahad-ai")
        html = resp.get_data(as_text=True)
        stages = [
            "01 • INGEST",
            "02 • FUSE",
            "03 • FORECAST",
            "04 • VERIFY",
            "05 • EXPLAIN",
            "06 • WARN",
            "07 • ROUTE",
            "08 • RESPOND"
        ]
        for st in stages:
            self.assertIn(st, html)

    def test_mathematics_display_blocks(self):
        """Verify exact physical and statistical mathematics formula cards exist."""
        resp = self.client.get("/pahad-ai")
        html = resp.get_data(as_text=True)
        # Mohr-Coulomb FoS equation
        self.assertIn("1. Mohr-Coulomb Stability (FoS)", html)
        self.assertIn("cos²β", html)
        # Composite Risk Index
        self.assertIn("2. Composite Risk Index (CRI)", html)
        self.assertIn("CRI = H × V × 100", html)
        # Mandal-Sarkar I-D curve
        self.assertIn("3. Mandal-Sarkar Rainfall I-D", html)
        self.assertIn("API_30d", html)

    def test_interactive_simulator_sliders_and_meters(self):
        """Verify interactive calculation visualizer sliders and output gauges exist."""
        resp = self.client.get("/pahad-ai")
        html = resp.get_data(as_text=True)
        self.assertIn('id="sim-rain-slider"', html)
        self.assertIn('id="sim-moist-slider"', html)
        self.assertIn('id="sim-pore-slider"', html)
        self.assertIn('id="sim-slope-slider"', html)
        self.assertIn('id="sim-tilt-slider"', html)
        self.assertIn('id="sim-disp-slider"', html)
        self.assertIn('id="sim-seis-slider"', html)

        # Output readouts
        self.assertIn('id="sim-out-fos"', html)
        self.assertIn('id="sim-out-prob"', html)
        self.assertIn('id="sim-out-cri"', html)
        self.assertIn('id="sim-agree-status"', html)

    def test_live_inference_trace_feed(self):
        """Verify live chronological inference trace feed is rendered."""
        resp = self.client.get("/pahad-ai")
        html = resp.get_data(as_text=True)
        self.assertIn("PAHAD AI Inference Trace", html)
        self.assertIn("[STREAMING 1.0 Hz]", html)
        self.assertIn("[INGEST]", html)
        self.assertIn("[PHYSICS]", html)

    def test_model_transparency_and_honest_limitations(self):
        """Verify strict adherence to honest limitations: FoS, GBDT, and surrogate LSTM labeling."""
        resp = self.client.get("/pahad-ai")
        html = resp.get_data(as_text=True)
        self.assertIn("Scientific Rigor", html)
        self.assertIn("TRAINED_LIMITED_DATA", html)
        self.assertIn("NOT TRAINED (Surrogate)", html)
        self.assertIn("TRAINED (v1.0)", html)
        self.assertIn("Honest Limitation Protocol", html)


if __name__ == "__main__":
    unittest.main()
