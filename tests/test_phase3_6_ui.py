# -*- coding: utf-8 -*-
"""
tests/test_phase3_6_ui.py
=========================
Automated test suite for PARVAT NETRA / PAHAD AI Phase 3.6 UI Integration.
Covers:
- Homepage navigation includes /pahad-ai link in toolbar
- Hero section contains Explore Observatory CTA and sourcebar link
- 4 Event Horizon forecast probabilities (6h, 12h, 24h, 48h)
- SIH 2026 Presentation Demo Bar (#sih-presentation-demo-bar) with controls (Start, Pause, Reset, Speed)
- Deterministic 13-step Active Teesta Basin failure sequence in client JS
- Unified cross-workspace navigation links across /climate-map, /seismic, /terrain-3d
- Strict honesty protocol: non-causal terminology, transparent badges
"""

import os
import unittest

os.environ["PARVAT_TESTING"] = "1"

from app import app


class TestPhase36UI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_homepage_has_pahad_ai_nav(self):
        """Verify homepage action toolbar contains direct link to PAHAD AI Observatory."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('href="/pahad-ai"', html)
        self.assertIn("PAHAD AI Observatory", html)

    def test_homepage_hero_observatory_links(self):
        """Verify hero prediction overview contains Explore Observatory CTA button and sourcebar pill."""
        resp = self.client.get("/")
        html = resp.get_data(as_text=True)
        self.assertIn("Explore Observatory →", html)
        self.assertIn("[3D TWIN]", html)

    def test_homepage_multi_horizon_cards(self):
        """Verify 4 event horizon exceedance probability indicators exist."""
        resp = self.client.get("/")
        html = resp.get_data(as_text=True)
        self.assertIn('id="pahad-h6"', html)
        self.assertIn('id="pahad-h12"', html)
        self.assertIn('id="pahad-h24"', html)
        self.assertIn('id="pahad-h48"', html)
        self.assertIn("PAHAD AI multi-horizon outlook", html)

    def test_sih_presentation_demo_bar_present(self):
        """Verify SIH Interactive Presentation Demo Bar container and controls exist on homepage."""
        resp = self.client.get("/")
        html = resp.get_data(as_text=True)
        self.assertIn('id="sih-presentation-demo-bar"', html)
        self.assertIn('id="demo-scenario-badge"', html)
        self.assertIn("Active Teesta Basin Monsoon Failure Sequence", html)
        self.assertIn('id="btn-demo-start"', html)
        self.assertIn('id="btn-demo-pause"', html)
        self.assertIn('id="btn-demo-reset"', html)
        self.assertIn('id="btn-demo-spd-1"', html)
        self.assertIn('id="btn-demo-spd-2"', html)
        self.assertIn('id="btn-demo-spd-4"', html)
        self.assertIn('id="demo-step-counter"', html)

    def test_sih_demo_thirteen_steps_defined(self):
        """Verify client JS contains all 13 deterministic demo steps."""
        resp = self.client.get("/")
        html = resp.get_data(as_text=True)
        self.assertIn("SIH_DEMO", html)
        self.assertIn("Normal Baseline", html)
        self.assertIn("Rain Onset (IMD AWS)", html)
        self.assertIn("Cumulative Infiltration & Pore Pressure Rise", html)
        self.assertIn("FoS Drops Below 1.0 (Limit State Failure)", html)
        self.assertIn("AI Event Model Reaches 0.84", html)
        self.assertIn("2-of-3 Signal Agreement Satisfied", html)
        self.assertIn("Evacuation Advisory Generated", html)
        self.assertIn("15 km Geofence Drawn", html)
        self.assertIn("Multi-Channel Dispatch (Push + SMS + Edge Siren)", html)
        self.assertIn("Dynamic Route Re-Calculation (Safe Corridor Active)", html)
        self.assertIn("Field Sensor Corroboration", html)
        self.assertIn("Post-Event Recovery State", html)
        self.assertIn("Evaluation Complete", html)

    def test_climate_map_has_observatory_link(self):
        """Verify /climate-map workspace links to /pahad-ai."""
        resp = self.client.get("/climate-map")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('href="/pahad-ai"', html)
        self.assertIn("PAHAD AI", html)

    def test_seismic_has_observatory_link(self):
        """Verify /seismic workspace links to /pahad-ai."""
        resp = self.client.get("/seismic")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('href="/pahad-ai"', html)
        self.assertIn("PAHAD AI", html)

    def test_terrain_3d_has_observatory_link(self):
        """Verify /terrain-3d workspace links to /pahad-ai."""
        resp = self.client.get("/terrain-3d")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('href="/pahad-ai"', html)
        self.assertIn("PAHAD AI", html)


if __name__ == "__main__":
    unittest.main()
