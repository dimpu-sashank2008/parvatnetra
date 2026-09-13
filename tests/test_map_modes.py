"""
Unit Tests for GIS Map Viewport Sizing Modes & Elimination of Strobe Animations
PARVAT NETRA Operational Dashboard
"""
import unittest
import re


class TestMapModesAndAlertBanners(unittest.TestCase):
    def setUp(self):
        with open("templates/index.html", "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_01_map_mode_buttons_exist(self):
        """Verify #btn-map-compact, #btn-map-standard, and #btn-map-maximize exist."""
        self.assertIn('id="btn-map-compact"', self.html)
        self.assertIn('id="btn-map-standard"', self.html)
        self.assertIn('id="btn-map-maximize"', self.html)
        self.assertIn('onclick="setMapViewMode(\'compact\')"', self.html)
        self.assertIn('onclick="setMapViewMode(\'standard\')"', self.html)
        self.assertIn('onclick="setMapViewMode(\'maximize\')"', self.html)
        self.assertIn('id="btn-exit-fullscreen-map"', self.html)

    def test_02_set_map_view_mode_defined(self):
        """Verify setMapViewMode is defined in script block with required modes."""
        self.assertIn("function setMapViewMode(mode)", self.html)
        self.assertIn("window.setMapViewMode = setMapViewMode;", self.html)
        self.assertIn("window.map.invalidateSize()", self.html)
        self.assertIn("260px", self.html)
        self.assertIn("520px", self.html)
        self.assertIn("fixed", self.html)
        self.assertIn("inset-0", self.html)
        self.assertIn("z-[9999]", self.html)

    def test_03_no_rapid_blinking_classes_in_alert_banners(self):
        """Verify no rapid blinking classes (animate-ping, animate-bounce) exist in emergency banners."""
        # Check NIC marquee banner
        marquee_idx = self.html.find("<!-- NIC HIGH-ALERT MARQUEE TICKER -->")
        marquee_end = self.html.find("</marquee>", marquee_idx)
        marquee_html = self.html[marquee_idx:marquee_end]
        self.assertNotIn("animate-ping", marquee_html)
        self.assertNotIn("animate-bounce", marquee_html)
        self.assertNotIn("animate-pulse", marquee_html)

        # Check lockdown banner
        lockdown_idx = self.html.find('id="emergency-lockdown-banner"')
        lockdown_end = self.html.find("</div>\n    </div>", lockdown_idx)
        lockdown_html = self.html[lockdown_idx:lockdown_idx+1000]
        self.assertNotIn("animate-pulse", lockdown_html)
        self.assertNotIn("animate-ping", lockdown_html)
        self.assertNotIn("animate-bounce", lockdown_html)

        # Check citizen NH-10 arterial banner
        nh10_idx = self.html.find("<!-- NH-10 Arterial Banner -->")
        nh10_html = self.html[nh10_idx:nh10_idx+1200]
        self.assertNotIn("animate-pulse", nh10_html)
        self.assertNotIn("animate-ping", nh10_html)
        self.assertNotIn("animate-bounce", nh10_html)

    def test_04_scroll_wheel_trapping_prevention(self):
        """Verify Leaflet scrollWheelZoom is disabled by default and enabled only on click."""
        self.assertIn("scrollWheelZoom:false", self.html)
        self.assertIn("map.scrollWheelZoom.disable()", self.html)
        self.assertIn("window.map.scrollWheelZoom.enable()", self.html)
        self.assertIn("mouseleave", self.html)

    def test_05_strict_zero_emojis(self):
        """Assert zero unicode emojis in index.html."""
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F700-\U0001F77F"
            "\U0001F780-\U0001F7FF"
            "\U0001F800-\U0001F8FF"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FA6F"
            "\U0001FA70-\U0001FAFF"
            "\U00002702-\U000027B0"
            "\U0001F1E6-\U0001F1FF"
            "\U0001F200-\U0001F251]"
        )
        matches = emoji_pattern.findall(self.html)
        self.assertEqual(len(matches), 0, f"Found emojis: {matches[:10]}")
if __name__ == "__main__":
    unittest.main()