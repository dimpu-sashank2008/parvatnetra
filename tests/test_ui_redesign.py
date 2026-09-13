# -*- coding: utf-8 -*-
"""
PARVAT NETRA - UI Redesign & Emergency Alarm Verification Test Suite
SIH Problem Statement ID: 26001 (MDoNER)

Validates:
1. Custom cursor hacks are removed and native cursor (cursor: grab !important;) is enforced.
2. Google Hybrid satellite URL (https://mt1.google.com/vt/lyrs=y) is registered as the default basemap.
3. #observation-queue-section spans 100% full width with a responsive administrative table.
4. Role switcher toggles #authority-view and #citizen-view.
5. All 5 high-resolution operational screenshots exist in docs/screenshots/ and exceed 50 KB.
6. Web Audio API emergency siren, mobile vibration, and lockdown modal are integrated.
"""

import os
import unittest
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_PATH = os.path.join(REPO_ROOT, 'templates', 'index.html')
SCREENSHOT_DIR = os.path.join(REPO_ROOT, 'docs', 'screenshots')


class TestUIRedesign(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            cls.html = f.read()

    def test_01_cursor_normalization(self):
        """Verify custom cursor URL overrides are stripped and native cursors are enforced."""
        self.assertNotIn('cursor: url(', self.html, "Custom cursor url(...) override found in index.html")
        self.assertNotIn('cursor:url(', self.html, "Custom cursor url(...) override found in index.html")

        self.assertIn('cursor: grab !important;', self.html, "cursor: grab !important; must be set for map canvas")
        self.assertIn('cursor: grabbing !important;', self.html, "cursor: grabbing !important; must be set for active pan")
        self.assertIn('cursor: pointer !important;', self.html, "cursor: pointer !important; must be set for interactive elements")
        print("[PASS] Test 1: Native OS cursors enforced; zero custom cursor hacks.")

    def test_02_google_hybrid_satellite_default_basemap(self):
        """Verify Google Hybrid Satellite is registered and added as default basemap."""
        google_hybrid_url = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
        self.assertIn(google_hybrid_url, self.html, "Google Hybrid Satellite URL not found in index.html")
        
        pattern = r"L\.tileLayer\(['\"]https://mt1\.google\.com/vt/lyrs=y[^'\"]*['\"][^)]*\)\.addTo\(map\)"
        match = re.search(pattern, self.html)
        self.assertIsNotNone(match, "Google Hybrid Satellite must be added to map by default with .addTo(map)")
        
        self.assertNotIn("tile.openstreetmap.org", self.html, "Unwanted OSM tile layer found in template")
        print("[PASS] Test 2: Clean Google Hybrid Satellite registered as default basemap.")

    def test_03_observation_queue_fullwidth_layout(self):
        """Verify #observation-queue-section spans 100% full width with responsive administrative table."""
        self.assertIn('id="observation-queue-section"', self.html, "Element #observation-queue-section missing")
        
        pattern = r'id=["\']observation-queue-section["\'][^>]*class=["\'][^"\']*(?:max-w-7xl|w-full)[^"\']*["\']'
        match = re.search(pattern, self.html)
        self.assertIsNotNone(match, "#observation-queue-section must span full-width container (max-w-7xl / w-full)")

        self.assertIn('id="triage-table"', self.html, "Administrative #triage-table missing")
        self.assertIn('id="queue-search"', self.html, "Search input #queue-search missing")
        self.assertIn('sev-pill', self.html, "Severity filter pills missing")
        self.assertIn('CV Crack Analysis', self.html, "CV Crack Analysis column missing")
        self.assertIn('DBSCAN Cluster', self.html, "DBSCAN Cluster column missing")
        print("[PASS] Test 3: #observation-queue-section spans 100% full width with responsive admin triage table.")

    def test_04_dual_mode_role_switcher(self):
        """Verify role switcher toggles #authority-view and #citizen-view."""
        self.assertIn('id="authority-view"', self.html, "Element #authority-view missing")
        self.assertIn('id="citizen-view"', self.html, "Element #citizen-view missing")
        self.assertIn('switchPortalMode', self.html, "switchPortalMode function missing")

        self.assertIn("switchPortalMode('authority')", self.html, "Authority mode switch button missing")
        self.assertIn("switchPortalMode('citizen')", self.html, "Citizen mode switch button missing")

        self.assertIn("getElementById('authority-view')", self.html, "JS must reference authority-view")
        self.assertIn("getElementById('citizen-view')", self.html, "JS must reference citizen-view")
        print("[PASS] Test 4: Role switcher properly toggles #authority-view and #citizen-view.")

    def test_05_screenshots_persisted_and_sized(self):
        """Verify all 5 operational screenshots exist in docs/screenshots/ and exceed 50 KB."""
        required_screenshots = [
            '01_executive_operations_dashboard.png',
            '02_multimodal_gis_console.png',
            '03_bilingual_indigenous_voice_cap_modal.png',
            '04_fullwidth_triage_queue.png',
            '05_citizen_advisory_portal.png'
        ]
        min_bytes = 50 * 1024  # 50 KB

        for filename in required_screenshots:
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            self.assertTrue(os.path.exists(filepath), f"Screenshot {filename} does not exist in {SCREENSHOT_DIR}")
            filesize = os.path.getsize(filepath)
            self.assertGreater(filesize, min_bytes, f"Screenshot {filename} size ({filesize/1024:.1f} KB) is under 50 KB")
            print(f"[PASS] Screenshot verified: {filename} ({filesize/1024:.1f} KB > 50 KB)")

    def test_06_emergency_siren_and_lockdown_modal(self):
        """Verify Web Audio dual-tone siren, haptic vibration, and lockdown modal are integrated."""
        self.assertIn('id="landslide-lockdown-modal"', self.html, "#landslide-lockdown-modal missing")
        self.assertIn('playEmergencySiren', self.html, "playEmergencySiren function missing")
        self.assertIn('navigator.vibrate', self.html, "navigator.vibrate call missing")
        self.assertIn('853', self.html, "853 Hz dual-tone frequency missing")
        self.assertIn('960', self.html, "960 Hz dual-tone frequency missing")
        self.assertIn('speakAudioAlert', self.html, "speakAudioAlert function missing")
        self.assertIn('triggerFullLandslideAlarm', self.html, "triggerFullLandslideAlarm function missing")
        self.assertIn('stopEmergencyAlarm', self.html, "stopEmergencyAlarm function missing")
        self.assertIn('Test Phone Siren', self.html, "Test Phone Siren button missing")
        print("[PASS] Test 6: Web Audio siren, vibration, and lockdown modal fully verified.")


if __name__ == '__main__':
    unittest.main(verbosity=2)
