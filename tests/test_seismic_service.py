# -*- coding: utf-8 -*-
"""
tests/test_seismic_service.py
==============================
Unit & Integration Tests for PAHAD AI Seismic Intelligence & Trigger Service
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import time

from services.seismic_service import (
    SeismicService,
    SeismicCache,
    NCSSeismicProvider,
    DemoSimulatedSeismicProvider,
    haversine_distance_km,
    deduplicate_seismic_events,
    calculate_seismic_trigger_score,
    NER_BBOX
)


class TestSeismicService(unittest.TestCase):

    def setUp(self):
        self.service = SeismicService()
        self.service.cache.clear()

    def test_haversine_distance(self):
        # Known distance: Gangtok (27.33, 88.61) to Singtam (27.234, 88.498) is approx 15-18 km
        dist = haversine_distance_km(27.33, 88.61, 27.234, 88.498)
        self.assertGreaterEqual(dist, 13.0)
        self.assertLessEqual(dist, 20.0)

    def test_ncs_unconfigured_safety(self):
        provider = NCSSeismicProvider()
        with patch.dict(os.environ, {"NCS_API_BASE_URL": ""}):
            self.assertFalse(provider._is_configured())
            status = provider.status()
            self.assertEqual(status["status"], "UNCONFIGURED")
            events = provider.fetch_events()
            self.assertEqual(events, [])

    def test_demo_simulated_seismic_events(self):
        provider = DemoSimulatedSeismicProvider()
        events = provider.fetch_events(min_mag=2.5)
        self.assertGreaterEqual(len(events), 2)
        for ev in events:
            self.assertIn("event_id", ev)
            self.assertIn("magnitude", ev)
            self.assertIn("latitude", ev)
            self.assertIn("longitude", ev)
            # Verify coordinates are inside NER BBOX
            self.assertGreaterEqual(ev["latitude"], NER_BBOX["min_lat"])
            self.assertLessEqual(ev["latitude"], NER_BBOX["max_lat"])
            self.assertGreaterEqual(ev["longitude"], NER_BBOX["min_lon"])
            self.assertLessEqual(ev["longitude"], NER_BBOX["max_lon"])

    def test_deduplicate_seismic_events(self):
        # Two events within 5 km: one M4.2, one M4.6
        raw_events = [
            {
                "event_id": "EQ-01",
                "latitude": 27.40,
                "longitude": 88.60,
                "magnitude": 4.2,
                "origin_time": "2026-09-08T12:00:00Z"
            },
            {
                "event_id": "EQ-02",
                "latitude": 27.42,
                "longitude": 88.61,
                "magnitude": 4.6,
                "origin_time": "2026-09-08T12:00:30Z"
            },
            {
                "event_id": "EQ-03",
                "latitude": 25.50,
                "longitude": 91.80,
                "magnitude": 3.8,
                "origin_time": "2026-09-08T12:00:00Z"
            }
        ]
        deduped = deduplicate_seismic_events(raw_events)
        self.assertEqual(len(deduped), 2)
        # Should keep the higher magnitude 4.6
        mags = [e["magnitude"] for e in deduped]
        self.assertIn(4.6, mags)
        self.assertIn(3.8, mags)

    def test_calculate_seismic_trigger_score(self):
        # Strong earthquake close to sector: M5.4 at 25 km
        event_strong = {
            "event_id": "TEST-EQ-STRONG",
            "latitude": 27.40,
            "longitude": 88.65,
            "magnitude": 5.4,
            "depth_km": 10.0,
            "provenance": "LIVE"
        }
        impact_strong = calculate_seismic_trigger_score("SK-NH10-KM48", event_strong)
        self.assertIn(impact_strong["seismic_trigger_level"], ["HIGH", "VERY_HIGH"])
        self.assertGreaterEqual(impact_strong["risk_adjustment"], 0.15)
        self.assertGreater(impact_strong["shaking_proxy_g"], 0.10)

        # Distant minor earthquake: M2.8 at 250 km
        event_minor = {
            "event_id": "TEST-EQ-MINOR",
            "latitude": 25.00,
            "longitude": 93.00,
            "magnitude": 2.8,
            "depth_km": 20.0,
            "provenance": "LIVE"
        }
        impact_minor = calculate_seismic_trigger_score("SK-NH10-KM48", event_minor)
        self.assertEqual(impact_minor["seismic_trigger_level"], "LOW")
        self.assertEqual(impact_minor["risk_adjustment"], 0.0)

    def test_seismic_service_end_to_end(self):
        recent = self.service.get_recent_events(limit=5)
        self.assertGreaterEqual(len(recent), 1)
        latest = self.service.get_latest_event()
        self.assertIsNotNone(latest)
        self.assertIn("event_id", latest)
        self.assertIn("provenance", latest)

        # Sector impact
        impact = self.service.get_impact_for_sector("SK-NH10-KM48")
        self.assertEqual(impact["sector_id"], "SK-NH10-KM48")
        self.assertIn("seismic_trigger_level", impact)


if __name__ == "__main__":
    unittest.main()
