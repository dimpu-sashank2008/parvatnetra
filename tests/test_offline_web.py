# -*- coding: utf-8 -*-
"""
tests/test_offline_web.py
=========================
PARVAT NETRA • Phase 5D Web Offline & PWA Infrastructure Test Suite
-------------------------------------------------------------------
Validates:
  1. Web App Manifest (static/manifest.json) properties & PWA compliance
  2. Service Worker (static/sw.js) precache configuration and cache policies
  3. Security isolation and sensitive route bypassing
  4. Core application shell HTTP status and static asset accessibility
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import json
import unittest
from app import app


class TestOfflineWebPWA(unittest.TestCase):
    """Verifies PWA manifest and Service Worker compliance."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_01_manifest_validity_and_pwa_fields(self):
        """Manifest contains mandatory PWA fields with national authority theme."""
        manifest_path = os.path.join(self.base_dir, "static", "manifest.json")
        self.assertTrue(os.path.exists(manifest_path), "manifest.json must exist in static/")

        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("name", data)
        self.assertIn("short_name", data)
        self.assertEqual(data.get("display"), "standalone")
        self.assertEqual(data.get("background_color"), "#070B10")
        self.assertEqual(data.get("theme_color"), "#070B10")
        self.assertIn("icons", data)
        self.assertGreaterEqual(len(data["icons"]), 2)

        icon_sizes = [i.get("sizes") for i in data["icons"]]
        self.assertIn("192x192", icon_sizes)
        self.assertIn("512x512", icon_sizes)

    def test_02_service_worker_structure_and_precaches(self):
        """Service worker specifies versioned caches and precaches core shell assets."""
        sw_path = os.path.join(self.base_dir, "static", "sw.js")
        self.assertTrue(os.path.exists(sw_path), "sw.js must exist in static/")

        with open(sw_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("CACHE_NAME", content)
        self.assertIn("PRECACHE_ASSETS", content)
        self.assertIn("/static/manifest.json", content)
        self.assertIn("/static/data/offline_core_package.json", content)
        self.assertIn("/static/js/offline_routing.js", content)
        self.assertIn("caches.open", content)

    def test_03_service_worker_security_exclusions(self):
        """Service worker explicitly bypasses auth routes and push sync."""
        sw_path = os.path.join(self.base_dir, "static", "sw.js")
        with open(sw_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("EXCLUDED_URL_PATTERNS", content)
        self.assertIn("login", content)
        self.assertIn("auth", content)
        self.assertIn("sync\\/push", content)

    def test_04_app_shell_endpoints_accessible(self):
        """Application shell endpoints return 200 OK."""
        res_root = self.client.get("/")
        self.assertEqual(res_root.status_code, 200)

        res_manifest = self.client.get("/static/manifest.json")
        self.assertEqual(res_manifest.status_code, 200)

        res_pkg = self.client.get("/static/data/offline_core_package.json")
        self.assertEqual(res_pkg.status_code, 200)
        data = res_pkg.get_json()
        self.assertIn("features", data)


if __name__ == "__main__":
    unittest.main()
