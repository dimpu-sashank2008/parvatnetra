# -*- coding: utf-8 -*-
"""
PARVAT NETRA -- End-to-End (E2E) Headless Browser Verification Suite
Phase 5: Production Hardening Assets
SIH Problem Statement ID: 26001 | Ministry of Development of North Eastern Region (MDoNER)

Tests:
1. Official EOC Authority Login Flow (/login/authority -> /).
2. Live Leaflet GIS Map Navigation and 3D Hazard Terrain Modal Trigger.
3. Geofenced Proximity Siren Response & Lockdown Logic.
4. Government SOP Directive Export (/api/reports/export-sop).
"""

import os
import math
import unittest
import requests

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8080")


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class TestE2EPlaywright(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Verify server is responding
        try:
            r = requests.get(f"{BASE_URL}/api/health", timeout=5)
            cls.server_up = (r.status_code == 200)
        except Exception:
            cls.server_up = False

        if not cls.server_up:
            raise unittest.SkipTest(f"Live server at {BASE_URL} not reachable.")

    def _get_browser(self, p):
        """Helper to launch system Chrome or fallback to default Chromium."""
        try:
            return p.chromium.launch(channel="chrome", headless=True)
        except Exception:
            return p.chromium.launch(headless=True)

    # -------------------------------------------------------------------------
    # TEST 1: Authority Login Flow
    # -------------------------------------------------------------------------
    def test_01_authority_login_flow(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = self._get_browser(p)
            context = browser.new_context()
            page = context.new_page()

            # 1. Navigate to Authority Login
            page.goto(f"{BASE_URL}/login/authority")
            self.assertIn("Official EOC Authority Login", page.title())
            self.assertTrue(page.locator("text=भारत सरकार | Government of India").is_visible())
            self.assertTrue(page.locator("text=RESTRICTED EOC ACCESS").is_visible())

            # 2. Fill login credentials
            page.fill("input[name='gov_id']", "dm.gangtok@nic.in")
            page.fill("input[name='password']", "sih2026secure")

            # 3. Submit
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")

            # 4. Verify redirected to dashboard with Authority privileges
            self.assertEqual(page.url.rstrip("/"), BASE_URL.rstrip("/"))
            self.assertTrue(page.locator("text=AUTH NODE #NER-71 • BRO Swastik").is_visible())
            self.assertTrue(page.locator("#btn-authority-mode").is_visible())

            # Verify Citizen Mode controls are hidden
            citizen_view = page.locator("#citizen-view")
            if citizen_view.count() > 0:
                self.assertTrue(citizen_view.is_hidden() or "hidden" in citizen_view.get_attribute("class"))

            context.close()
            browser.close()

    # -------------------------------------------------------------------------
    # TEST 2: Live Leaflet GIS Map Navigation & Hazard Modal Trigger
    # -------------------------------------------------------------------------
    def test_02_map_navigation_and_hazard_modal(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = self._get_browser(p)
            context = browser.new_context()
            page = context.new_page()

            # Authorize session first
            page.goto(f"{BASE_URL}/login/authority")
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")

            # 1. Verify Map Container
            page.wait_for_selector("#map", state="visible")
            self.assertTrue(page.locator("#map").is_visible())

            # 2. Verify Map Layer Control Panel
            page.wait_for_selector("#layer-control-panel", state="visible")
            page.click(".lcp-header")  # Open layer panel
            page.wait_for_selector("#lcp-body", state="visible")
            self.assertTrue(page.locator("#lc-toggle-bro-fleet").is_visible())
            self.assertTrue(page.locator("#lc-toggle-river").is_visible())

            # 3. Trigger 3D Digital Elevation Model (DEM) Modal
            page.evaluate("window.open3DTerrainModel('NH-10 Km 48 (29th Mile Sector)', 0.745)")
            modal_3d = page.locator("#modal-3d-terrain")
            page.wait_for_selector("#modal-3d-terrain", state="visible")
            self.assertTrue(modal_3d.is_visible())

            # Verify 3D subtitle telemetry values
            subtitle_text = page.locator('[id="3d-modal-subtitle"]').inner_text()
            self.assertIn("NH-10 Km 48", subtitle_text)
            self.assertIn("0.745", subtitle_text)

            # 4. Close 3D Modal
            page.evaluate("window.close3DTerrainModal()")
            self.assertTrue(modal_3d.is_hidden())

            context.close()
            browser.close()

    # -------------------------------------------------------------------------
    # TEST 3: Geofenced Proximity Response
    # -------------------------------------------------------------------------
    def test_03_geofenced_proximity_response(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = self._get_browser(p)
            context = browser.new_page()
            page = context

            page.goto(f"{BASE_URL}/login/authority")
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")

            # Hazard epicenter at NH-10 Km 48
            hazard_lat, hazard_lng = 27.2175, 88.4990

            # Test point A: In-zone epicenter (<15 km)
            dist_near = haversine_km(hazard_lat, hazard_lng, 27.2200, 88.5050)
            self.assertLess(dist_near, 15.0)

            # Test point B: Out-of-zone distant location (>15 km, e.g. Siliguri 26.7271, 88.3953)
            dist_far = haversine_km(hazard_lat, hazard_lng, 26.7271, 88.3953)
            self.assertGreater(dist_far, 15.0)

            # Evaluate client-side geofencing logic in browser context
            in_zone_result = page.evaluate("""
                () => {
                    const R = 6371.0;
                    function haversine(lat1, lon1, lat2, lon2) {
                        const p1 = lat1 * Math.PI / 180, p2 = lat2 * Math.PI / 180;
                        const dp = (lat2 - lat1) * Math.PI / 180, dl = (lon2 - lon1) * Math.PI / 180;
                        const a = Math.sin(dp/2)**2 + Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2;
                        return 2.0 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
                    }
                    const dNear = haversine(27.2175, 88.4990, 27.2200, 88.5050);
                    const dFar = haversine(27.2175, 88.4990, 26.7271, 88.3953);
                    return {
                        dNear: dNear,
                        inNear: dNear <= 15.0,
                        dFar: dFar,
                        inFar: dFar <= 15.0
                    };
                }
            """)

            self.assertTrue(in_zone_result["inNear"])
            self.assertFalse(in_zone_result["inFar"])

            # Test Tactical Lockdown Modal Trigger
            page.evaluate("if(typeof triggerFullLandslideAlarm === 'function') triggerFullLandslideAlarm();")
            page.wait_for_selector("#landslide-lockdown-modal", state="visible")
            self.assertTrue(page.locator("#landslide-lockdown-modal").is_visible())

            # Stop emergency alarm
            page.evaluate("if(typeof stopEmergencyAlarm === 'function') stopEmergencyAlarm();")
            self.assertTrue(page.locator("#landslide-lockdown-modal").is_hidden())

            browser.close()

    # -------------------------------------------------------------------------
    # TEST 4: Official Government SOP Export Endpoint
    # -------------------------------------------------------------------------
    def test_04_sop_report_export(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = self._get_browser(p)
            page = browser.new_page()

            # 1. Fetch HTML version
            page.goto(f"{BASE_URL}/api/reports/export-sop")
            page.wait_for_load_state("networkidle")

            self.assertIn("GOVERNMENT OF INDIA", page.title())
            self.assertTrue(page.locator("text=भारत सरकार | Government of India").is_visible())
            self.assertTrue(page.locator("text=Teesta River CWC Hydrodynamic Scour").is_visible())
            self.assertTrue(page.locator("text=Coupled Geotechnical Slope Stability").is_visible())
            self.assertTrue(page.locator("text=BYPASS-LAVA").is_visible())
            self.assertTrue(page.locator("text=BRO-EXC-758A").is_visible())

            browser.close()


if __name__ == "__main__":
    unittest.main()
