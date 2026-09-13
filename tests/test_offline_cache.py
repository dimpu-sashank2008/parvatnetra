# -*- coding: utf-8 -*-
"""
PARVAT NETRA - Service Worker, PWA Manifest & Cache Strategy Test Suite
Phase 3.2: Offline-First Web, Map Resilience & Data Synchronization
"""

import os
import json
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SW_PATH = os.path.join(REPO_ROOT, 'static', 'sw.js')
MANIFEST_PATH = os.path.join(REPO_ROOT, 'static', 'manifest.json')
CORE_PKG_PATH = os.path.join(REPO_ROOT, 'static', 'data', 'offline_core_package.json')


class TestOfflineCache(unittest.TestCase):
    """Validates the Progressive Web App manifest, service worker caching policies, and security isolation."""

    def test_01_pwa_manifest_validity(self):
        """Verify static/manifest.json contains valid JSON with required PWA metadata."""
        self.assertTrue(os.path.exists(MANIFEST_PATH), "static/manifest.json must exist")
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        self.assertIn("PARVAT NETRA", manifest.get("name"))
        self.assertEqual(manifest.get("short_name"), "ParvatNetra")
        self.assertEqual(manifest.get("display"), "standalone")
        self.assertEqual(manifest.get("theme_color"), "#070B10")
        self.assertEqual(manifest.get("background_color"), "#070B10")
        self.assertIn("icons", manifest)
        self.assertGreaterEqual(len(manifest["icons"]), 1)

    def test_02_service_worker_file_presence(self):
        """Verify static/sw.js exists and is populated."""
        self.assertTrue(os.path.exists(SW_PATH), "static/sw.js must exist")
        size = os.path.getsize(SW_PATH)
        self.assertGreater(size, 1000, "Service worker file is too small or incomplete")

    def test_03_service_worker_cache_policies(self):
        """Verify sw.js implements Cache-First, Stale-While-Revalidate, and Network-First policies."""
        with open(SW_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # Cache name versioning
        self.assertIn("CACHE_NAME", content)
        self.assertIn("parvat-netra-v", content)

        # Core pre-cached assets
        self.assertIn("offline_core_package.json", content)
        self.assertIn("network_state.js", content)
        self.assertIn("local_store.js", content)
        self.assertIn("sync_manager.js", content)
        self.assertIn("offline_manager.js", content)
        self.assertIn("manifest.json", content)

        # Cache-First logic
        self.assertIn("CACHE-FIRST", content)

        # Network-First with Cache Fallback
        self.assertIn("NETWORK-FIRST", content)

        # Stale-While-Revalidate
        self.assertIn("STALE-WHILE-REVALIDATE", content)

    def test_04_service_worker_security_isolation(self):
        """Verify service worker never caches passwords, credentials, login, or POST requests."""
        with open(SW_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # Must ignore non-GET requests
        self.assertIn("request.method !== 'GET'", content)

        # Must explicitly exclude sensitive authentication endpoints
        self.assertIn("EXCLUDED_URL_PATTERNS", content)
        self.assertIn("/login", content)
        self.assertIn("/logout", content)

    def test_05_prebundled_offline_package_accessible(self):
        """Verify pre-bundled core package file is present for service worker pre-caching."""
        self.assertTrue(os.path.exists(CORE_PKG_PATH), "Pre-bundled core map package must exist")
        with open(CORE_PKG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data.get("type"), "FeatureCollection")
        self.assertGreaterEqual(len(data.get("features", [])), 30)


if __name__ == '__main__':
    unittest.main(verbosity=2)
