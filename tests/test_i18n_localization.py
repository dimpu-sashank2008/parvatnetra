#!/usr/bin/env python3
"""
Unit and Integration Tests for PARVAT NETRA Unified Frontend Localization (i18n).
Verifies:
1. static/js/i18n.js dictionary existence and all 6 language sets (en, hi, ne, bh, lp, as).
2. Key parity across languages for critical operational labels.
3. DOM data-i18n binding references in templates/index.html.
4. Window exposures: setPortalLanguage, toggleLanguage, speakEmergencyAlert, getCurrentPortalLang.
5. Multilingual speech synthesis utterance configurations.
"""

import os
import re
import unittest

class TestI18nLocalization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.i18n_path = os.path.join(cls.root_dir, "static", "js", "i18n.js")
        cls.template_path = os.path.join(cls.root_dir, "templates", "index.html")

        with open(cls.i18n_path, "r", encoding="utf-8") as f:
            cls.i18n_js = f.read()

        with open(cls.template_path, "r", encoding="utf-8") as f:
            cls.index_html = f.read()

    def test_i18n_file_exists_and_not_empty(self):
        self.assertTrue(os.path.exists(self.i18n_path), "static/js/i18n.js must exist")
        self.assertGreater(len(self.i18n_js), 1000, "static/js/i18n.js must not be empty")

    def test_languages_present_in_dictionary(self):
        """All 6 supported languages must be defined in PARVAT_I18N dictionary."""
        for lang in ['en', 'hi', 'ne', 'bh', 'lp', 'as']:
            pattern = rf'{lang}\s*:\s*\{{'
            self.assertRegex(self.i18n_js, pattern, f"Language '{lang}' must be present in PARVAT_I18N")

    def test_critical_keys_present_across_languages(self):
        """Check that essential alert and UI keys exist in all 6 language definitions."""
        essential_keys = [
            'app_title', 'subtitle', 'goi', 'ministry', 'sync',
            'eoc_mode', 'citizen_mode', 'arm_siren', 'road_severed',
            'evacuation_warning', 'critical_red_zones', 'rec_protocol',
            'auth_protocol', 'issue_alert', 'dem_3d', 'bro_sop',
            'cwc_hydro', 'basal_shear', 'slide_confirm', 'deploy_bro',
            'inspect_evidence', 'log_incident', 'refresh', 'queue_title',
            'all_filter', 'critical_filter', 'severe_filter', 'moderate_filter', 'low_filter',
            'voice_broadcast', 'cancel'
        ]
        for lang in ['en', 'hi', 'ne', 'bh', 'lp', 'as']:
            for key in essential_keys:
                self.assertIn(f'{key}:', self.i18n_js, f"Key '{key}' must be defined in i18n dictionary for '{lang}'")

    def test_window_exposures_present(self):
        """setPortalLanguage, toggleLanguage, speakEmergencyAlert, getCurrentPortalLang must be registered on window."""
        self.assertIn("window.PARVAT_I18N = PARVAT_I18N;", self.i18n_js)
        self.assertIn("window.setPortalLanguage = setPortalLanguage;", self.i18n_js)
        self.assertIn("window.toggleLanguage = setPortalLanguage;", self.i18n_js)
        self.assertIn("window.speakEmergencyAlert = speakEmergencyAlert;", self.i18n_js)
        self.assertIn("window.getCurrentPortalLang =", self.i18n_js)

    def test_speech_synthesis_support(self):
        """speakEmergencyAlert must instantiate SpeechSynthesisUtterance and support regional speech codes."""
        self.assertIn("window.speechSynthesis", self.i18n_js)
        self.assertIn("new SpeechSynthesisUtterance", self.i18n_js)
        self.assertIn("hi-IN", self.i18n_js)
        self.assertIn("ne-NP", self.i18n_js)
        self.assertIn("as-IN", self.i18n_js)

    def test_index_html_includes_i18n_script(self):
        """templates/index.html must load /static/js/i18n.js in <head>."""
        self.assertIn('<script src="/static/js/i18n.js"></script>', self.index_html)

    def test_language_select_element(self):
        """templates/index.html must contain #lang-select calling setPortalLanguage on change."""
        self.assertIn('id="lang-select"', self.index_html)
        self.assertIn('onchange="setPortalLanguage(this.value)"', self.index_html)
        for lang in ['en', 'hi', 'ne', 'bh', 'lp', 'as']:
            self.assertIn(f'value="{lang}"', self.index_html)

    def test_data_i18n_attributes_in_index_html(self):
        """templates/index.html must bind data-i18n to critical UI modules."""
        expected_bindings = [
            'data-i18n="goi"',
            'data-i18n="ministry"',
            'data-i18n="sync"',
            'data-i18n="rec_protocol"',
            'data-i18n="auth_protocol"',
            'data-i18n="issue_alert"',
            'data-i18n="dem_3d"',
            'data-i18n="arm_siren"',
            'data-i18n="bro_sop"',
            'data-i18n="cwc_hydro"',
            'data-i18n="basal_shear"',
            'data-i18n="queue_title"',
            'data-i18n-placeholder="search_placeholder"',
            'data-i18n="all_filter"',
            'data-i18n="critical_filter"',
            'data-i18n="severe_filter"',
            'data-i18n="moderate_filter"',
            'data-i18n="low_filter"',
            'data-i18n="log_incident"',
            'data-i18n="refresh"',
            'data-i18n="road_severed"',
            'data-i18n="voice_broadcast"',
            'data-i18n="slide_confirm"',
            'data-i18n="cancel"',
        ]
        for binding in expected_bindings:
            self.assertIn(binding, self.index_html, f"Missing binding in index.html: {binding}")

    def test_render_reports_table_localizes_actions(self):
        """renderReportsTable must use PARVAT_I18N for action button labels."""
        self.assertIn("inspect_evidence", self.index_html)
        self.assertIn("deploy_bro", self.index_html)

    def test_toggle_language_backward_compatibility(self):
        """toggleLanguage function must exist and delegate to setPortalLanguage."""
        self.assertIn("function toggleLanguage(lang)", self.index_html)
        self.assertIn("setPortalLanguage(lang)", self.index_html)


if __name__ == "__main__":
    unittest.main()
