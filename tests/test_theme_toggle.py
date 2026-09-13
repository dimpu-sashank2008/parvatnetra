# -*- coding: utf-8 -*-
"""
PARVAT NETRA - Light/Dark Theme Engine Verification Test Suite
SIH Problem Statement ID: 26001 (MDoNER)

Validates:
1. GIGW 3.0 body.light-mode CSS overrides in templates/index.html.
2. #theme-toggle-btn with theme icon and label in templates/index.html.
3. JavaScript functions toggleTheme, updateThemeUI, and initTheme in templates/index.html.
4. localStorage persistence ('parvat_theme') in templates/index.html.
5. Live Flask server returns HTTP 200 with working theme toggle button.
"""

import os
import unittest
import urllib.request
import urllib.error

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_PATH = os.path.join(REPO_ROOT, 'templates', 'index.html')


class TestThemeToggle(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            cls.html = f.read()

    def test_01_light_mode_css_rules(self):
        """Verify body.light-mode CSS override rules exist in templates/index.html."""
        self.assertIn('body.light-mode', self.html, "body.light-mode CSS selector missing")
        self.assertIn('background-color: #F8FAFC !important;', self.html, "Light mode background #F8FAFC missing")
        self.assertIn('body.light-mode .dark-card', self.html, "Light mode .dark-card override missing")
        self.assertIn('body.light-mode .kpi-card', self.html, "Light mode .kpi-card override missing")
        self.assertIn('body.light-mode .triage-table thead th', self.html, "Light mode table header override missing")
        self.assertIn('body.light-mode input', self.html, "Light mode input override missing")
        print("[PASS] Test 1: GIGW 3.0 body.light-mode CSS rules verified.")

    def test_02_theme_toggle_button_dom(self):
        """Verify theme toggle button exists with correct IDs and attributes."""
        self.assertIn('id="theme-toggle-btn"', self.html, "#theme-toggle-btn button missing")
        self.assertIn('onclick="toggleTheme()"', self.html, "onclick='toggleTheme()' trigger missing")
        self.assertIn('id="theme-icon"', self.html, "#theme-icon container missing")
        self.assertIn('id="theme-text"', self.html, "#theme-text container missing")
        print("[PASS] Test 2: #theme-toggle-btn DOM element and event triggers verified.")

    def test_03_theme_javascript_functions(self):
        """Verify toggleTheme, updateThemeUI, and initTheme are implemented."""
        self.assertIn('function toggleTheme()', self.html, "toggleTheme function missing")
        self.assertIn('function updateThemeUI(', self.html, "updateThemeUI function missing")
        self.assertIn('function initTheme()', self.html, "initTheme function missing")
        self.assertIn("localStorage.setItem('parvat_theme'", self.html, "localStorage persistence setItem missing")
        self.assertIn("localStorage.getItem('parvat_theme')", self.html, "localStorage getItem check missing")
        self.assertIn('initTheme()', self.html, "initTheme invocation missing from DOMContentLoaded")
        print("[PASS] Test 3: Theme controller functions and localStorage persistence verified.")

    def test_04_server_serves_theme_button(self):
        """Verify live Flask server serves index.html with theme toggle button."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8080/")
            with urllib.request.urlopen(req, timeout=5) as response:
                status_code = response.getcode()
                body = response.read().decode('utf-8')
                self.assertEqual(status_code, 200, f"Expected 200, got {status_code}")
                self.assertIn('id="theme-toggle-btn"', body, "#theme-toggle-btn missing from server response")
                self.assertIn('toggleTheme()', body, "toggleTheme() trigger missing from server response")
                print(f"[PASS] Test 4: Live server returns HTTP {status_code} with theme switcher.")
        except urllib.error.URLError as e:
            self.fail(f"Flask server unreachable: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
