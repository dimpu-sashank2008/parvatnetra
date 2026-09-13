"""
Unit Tests for GIS Map Viewport Sizing Modes and Scroll-Trap Prevention
PARVAT NETRA Operational Dashboard
"""
import unittest
import re


class TestMapViewportModes(unittest.TestCase):
    def setUp(self):
        with open("templates/index.html", "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_01_map_card_and_selectors_preserved(self):
        """Preserve all IDs: #gis-map-card, #gis-map, #map, #btn-reset-view."""
        self.assertIn('id="gis-map-card"', self.html)
        self.assertIn('id="gis-map"', self.html)
        self.assertIn('id="map"', self.html)
        self.assertIn('id="btn-reset-view"', self.html)

    def test_02_viewport_toggle_buttons_present(self):
        """Verify COMPACT, STANDARD, MAXIMIZE buttons and exit fullscreen button."""
        self.assertIn('id="btn-map-compact"', self.html)
        self.assertIn('onclick="setMapViewMode(\'compact\')"', self.html)
        self.assertIn("COMPACT", self.html)

        self.assertIn('id="btn-map-standard"', self.html)
        self.assertIn('onclick="setMapViewMode(\'standard\')"', self.html)
        self.assertIn("STANDARD", self.html)

        self.assertIn('id="btn-map-maximize"', self.html)
        self.assertIn('onclick="setMapViewMode(\'maximize\')"', self.html)
        self.assertIn("MAXIMIZE", self.html)

        self.assertIn('id="btn-exit-fullscreen-map"', self.html)
        self.assertIn("EXIT FULLSCREEN", self.html)

    def test_03_javascript_set_map_view_mode_defined(self):
        """Verify setMapViewMode, currentMapViewMode, and invalidateSize resizing."""
        self.assertIn("function setMapViewMode(mode)", self.html)
        self.assertIn("window.setMapViewMode = setMapViewMode;", self.html)
        self.assertIn("window.map.invalidateSize()", self.html)
        self.assertIn("compact", self.html)
        self.assertIn("maximize", self.html)
        self.assertIn("260px", self.html)
        self.assertIn("fixed", self.html)
        self.assertIn("inset-0", self.html)
        self.assertIn("z-[9999]", self.html)

    def test_04_keyboard_escape_listener(self):
        """Verify Escape key listener reverts maximized map back to standard."""
        self.assertIn("e.key === 'Escape'", self.html)
        self.assertIn("setMapViewMode('standard')", self.html)

    def test_05_scroll_wheel_trapping_prevention(self):
        """Verify scroll-wheel trapping prevention via scrollWheelZoom disable/enable."""
        self.assertIn("scrollWheelZoom:false", self.html)
        self.assertIn("map.scrollWheelZoom.disable()", self.html)
        self.assertIn("window.map.scrollWheelZoom.enable()", self.html)
        self.assertIn("mouseleave", self.html)

    def test_06_strict_zero_emojis(self):
        """Strict GIGW 3.0 Standard: zero unicode emojis in templates/index.html."""
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