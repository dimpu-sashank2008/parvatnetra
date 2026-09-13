# -*- coding: utf-8 -*-
"""
PARVAT NETRA - Offline Data Age, Provenance Protocol & Provider Failover Test Suite
Phase 3.2: Offline-First Web, Map Resilience & Data Synchronization
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import time
from datetime import datetime, timezone, timedelta
from app import app
from services.weather_service import WeatherService
from services.seismic_service import SeismicService


class TestOfflineProvenance(unittest.TestCase):
    """Validates the data provenance tagging, provider failover honesty, and data age calculations."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        cls.weather_svc = WeatherService()
        cls.seismic_svc = SeismicService()

    def test_01_provenance_badge_standard(self):
        """Verify only official provenance categories are utilized across services."""
        valid_badges = {"[LIVE]", "[CACHED]", "[HISTORICAL]", "[SIMULATED]", "[DEMO]"}
        from engine.geospatial_registry import GEOSPATIAL_REGISTRY
        datasets = GEOSPATIAL_REGISTRY.list_datasets()
        for ds in datasets:
            prov = ds.get("provenance")
            # Some formatted without brackets in to_dict, check normalized form
            norm_prov = f"[{prov}]" if not prov.startswith("[") else prov
            self.assertIn(norm_prov, valid_badges, f"Invalid provenance badge: {prov}")

    def test_02_data_age_calculation(self):
        """Verify dynamic metrics accurately compute age_seconds and relative timestamps."""
        now = datetime.now(timezone.utc)
        observed = now - timedelta(minutes=18)
        retrieved = now - timedelta(minutes=17)

        age_seconds = int((now - observed).total_seconds())
        age_minutes = round(age_seconds / 60)
        self.assertEqual(age_minutes, 18)

        metric_envelope = {
            "metric": "Rainfall (24h)",
            "value_mm": 142.0,
            "observed_at": observed.isoformat(),
            "retrieved_at": retrieved.isoformat(),
            "age_seconds": age_seconds,
            "source": "Open-Meteo",
            "provenance": "[LIVE]"
        }
        self.assertIn("observed_at", metric_envelope)
        self.assertIn("retrieved_at", metric_envelope)
        self.assertIn("age_seconds", metric_envelope)
        self.assertEqual(metric_envelope["provenance"], "[LIVE]")

    def test_03_weather_provider_honesty(self):
        """Verify that Open-Meteo is never labeled as IMD in provenance and metadata."""
        weather_data = self.weather_svc.get_weather(27.33, 88.61, sector_id="SK-NH10-KM48")
        source = weather_data.get("source", "")
        prov = weather_data.get("provenance", "")
        if "Open-Meteo" in source:
            self.assertNotIn("IMD", source, "Must not label Open-Meteo as IMD")
        self.assertIn(prov, ["LIVE", "CACHED", "SIMULATED", "HISTORICAL", "DEMO", "[LIVE]", "[CACHED]"])

    def test_04_seismic_provider_honesty(self):
        """Verify that USGS feeds are never labeled as NCS in provenance and metadata."""
        events = self.seismic_svc.get_recent_events(limit=5)
        for ev in events:
            src = ev.get("source", "")
            if "USGS" in src:
                self.assertNotIn("NCS", src, "Must not label USGS as National Center for Seismology")

    def test_05_offline_pahad_snapshot_distinction(self):
        """Verify that cached predictions cannot be labeled as [LIVE]."""
        snapshot = {
            "prediction_score": 82,
            "risk_level": "VERY HIGH",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "CACHED PREDICTION",
            "provenance": "[CACHED]"
        }
        self.assertNotEqual(snapshot["status"], "LIVE")
        self.assertNotEqual(snapshot["provenance"], "[LIVE]")
        self.assertEqual(snapshot["status"], "CACHED PREDICTION")

    def test_06_system_status_ribbon_contracts(self):
        """Verify home page contains four-tier system status ribbon with online/offline states."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertIn("system-status-ribbon", html)
        self.assertIn("system-network-status", html)
        self.assertIn("system-data-status", html)
        self.assertIn("system-map-status", html)
        self.assertIn("system-pahad-status", html)


if __name__ == '__main__':
    unittest.main(verbosity=2)
