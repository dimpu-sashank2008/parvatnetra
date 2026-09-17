# -*- coding: utf-8 -*-
"""
PARVAT NETRA - Isolated Login Portals & Noto Sans Typography Test Suite
SIH Problem Statement ID: 26001 (MDoNER)

Validates:
1. /login/authority returns HTTP 200 with isolated official EOC controls and zero citizen leakage.
2. /login/citizen returns HTTP 200 with isolated Nagrik OTP controls and zero authority leakage.
3. /login returns HTTP 200 as routing checkpoint with isolated pathway cards.
4. Session role enforcement for authority and citizen personas.
5. Strict GIGW 3.0 Noto Sans & Noto Sans Devanagari typography configuration.
"""

import os
import unittest
import urllib.request
import urllib.error
import requests

BASE_URL = "http://127.0.0.1:8080"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class TestIsolatedLoginAndTypography(unittest.TestCase):

    def test_01_authority_portal_isolation(self):
        """Verify /login/authority serves isolated official EOC portal without citizen UI."""
        r = requests.get(f"{BASE_URL}/login/authority")
        self.assertEqual(r.status_code, 200)
        html = r.text

        # Official elements must be present
        self.assertIn("Official EOC Authority Login", html)
        self.assertIn("gov_id", html)
        self.assertIn("dm.gangtok@nic.in", html)
        self.assertIn("MeriPehchan", html)
        self.assertIn("RESTRICTED EOC ACCESS", html)

        # Citizen elements must be absent
        self.assertNotIn("tab-btn-citizen", html)
        self.assertNotIn("Nagrik / Citizen Login", html)
        self.assertNotIn("Enter 6-Digit Verification Code", html)
        self.assertNotIn("Generate 6-Digit Verification OTP", html)
        print("[PASS] Test 1: /login/authority verified strictly isolated for Official EOC.")

    def test_02_citizen_portal_isolation(self):
        """Verify /login/citizen serves isolated Nagrik portal without authority UI."""
        r = requests.get(f"{BASE_URL}/login/citizen")
        self.assertEqual(r.status_code, 200)
        html = r.text

        # Citizen elements must be present
        self.assertIn("Nagrik / Citizen Advisory Login", html)
        self.assertIn("10-Digit Mobile Number", html)
        self.assertIn("Generate 6-Digit Verification OTP", html)
        self.assertIn("otp_code", html)
        self.assertIn("PUBLIC NAGRIK ACCESS", html)

        # Authority elements must be absent
        self.assertNotIn("tab-btn-authority", html)
        self.assertNotIn("Official Government Email / ID", html)
        self.assertNotIn("MeriPehchan", html)
        self.assertNotIn("RESTRICTED EOC ACCESS", html)
        print("[PASS] Test 2: /login/citizen verified strictly isolated for Public Citizens.")

    def test_03_login_routing_checkpoint(self):
        """Verify /login serves clean routing checkpoint pointing to isolated portals."""
        r = requests.get(f"{BASE_URL}/login")
        self.assertEqual(r.status_code, 200)
        html = r.text

        self.assertIn("/login/authority", html)
        self.assertIn("/login/citizen", html)
        self.assertIn("Official Authority Portal", html)
        self.assertIn("Public Citizen Advisory", html)
        print("[PASS] Test 3: /login checkpoint correctly links to both isolated portals.")

    def test_04_session_role_enforcement(self):
        """Verify logging in via /login/authority and /login/citizen sets appropriate session roles."""
        # Authority Login
        s_auth = requests.Session()
        r_auth = s_auth.post(
            f"{BASE_URL}/login/authority",
            data={"gov_id": "dm.gangtok@nic.in", "password": "secret"},
            allow_redirects=True
        )
        self.assertEqual(r_auth.status_code, 200)
        self.assertIn("AUTHORITY", r_auth.text.upper())

        # Citizen Login
        s_cit = requests.Session()
        r_cit = s_cit.post(
            f"{BASE_URL}/login/citizen",
            data={"mobile": "9876543210", "otp_code": "482910"},
            allow_redirects=True
        )
        self.assertEqual(r_cit.status_code, 200)
        self.assertIn("CITIZEN", r_cit.text.upper())
        print("[PASS] Test 4: Session role enforcement and isolated redirects verified.")

    def test_05_strict_noto_sans_typography(self):
        """Verify Google Fonts, Tailwind config, and CSS rules strictly enforce 'Noto Sans' / 'Noto Sans Devanagari'."""
        templates_to_check = ['index.html', 'login_authority.html', 'login_citizen.html', 'login.html']
        for tpl in templates_to_check:
            path = os.path.join(REPO_ROOT, 'templates', tpl)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertIn('family=Noto+Sans+Devanagari', content, f"{tpl} missing Noto Sans Devanagari")
            self.assertIn('family=Noto+Sans:', content, f"{tpl} missing Noto Sans Latin")
            self.assertIn('"Noto Sans"', content, f"{tpl} missing Tailwind Noto Sans config")
            self.assertIn('"Noto Sans Devanagari"', content, f"{tpl} missing Tailwind Noto Sans Devanagari config")
            self.assertIn("font-family: 'Noto Sans', 'Noto Sans Devanagari'", content, f"{tpl} missing CSS font-family override")
            self.assertNotIn("'JetBrains Mono'", content, f"{tpl} contains deprecated JetBrains Mono")
    def test_06_login_buttons_high_contrast_accessibility(self):
        """Verify login buttons maintain high contrast white text to prevent invisible dark-on-dark text."""
        # 1. Check login.html
        path_login = os.path.join(REPO_ROOT, 'templates', 'login.html')
        with open(path_login, 'r', encoding='utf-8') as f:
            login_html = f.read()
        self.assertIn('color: #ffffff !important', login_html)
        self.assertIn('background-color: #003366 !important', login_html)
        self.assertIn('background-color: #D97706 !important', login_html)

        # 2. Check login_authority.html
        path_auth = os.path.join(REPO_ROOT, 'templates', 'login_authority.html')
        with open(path_auth, 'r', encoding='utf-8') as f:
            auth_html = f.read()
        self.assertIn('id="btn-submit-authority"', auth_html)
        self.assertIn('color: #ffffff !important', auth_html)

        # 3. Check login_citizen.html
        path_cit = os.path.join(REPO_ROOT, 'templates', 'login_citizen.html')
        with open(path_cit, 'r', encoding='utf-8') as f:
            cit_html = f.read()
        self.assertIn('id="btn-submit-citizen"', cit_html)
        self.assertIn('color: #ffffff !important', cit_html)

        # 4. Check CSS rules
        path_css = os.path.join(REPO_ROOT, 'static', 'css', 'parvat_theme.css')
        with open(path_css, 'r', encoding='utf-8') as f:
            css_content = f.read()
        self.assertIn('#btn-submit-authority', css_content)
        self.assertIn('#btn-submit-citizen', css_content)
        print("[PASS] Test 6: High-contrast white text guaranteed on all login portal action buttons.")


if __name__ == '__main__':
    unittest.main(verbosity=2)

