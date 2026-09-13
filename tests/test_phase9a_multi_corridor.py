# -*- coding: utf-8 -*-
"""
tests/test_phase9a_multi_corridor.py
====================================
PARVAT NETRA • PAHAD AI — Phase 9A Multi-Corridor Automated Test Suite
----------------------------------------------------------------------
Validates:
  1. Unified Canonical Location Registry integrity across all 8 NER states.
  2. Alias mapping, spatial Haversine lookups, and GeoJSON export.
  3. GET /api/pahad/locations with State, District, Status, and Query filters.
  4. POST /api/pahad/location-risk across all 8 NER states.
  5. Arbitrary WGS84 coordinate evaluation and nearest corridor mapping.
  6. Cross-location data isolation (zero state bleed).
  7. Deterministic multi-state fallback in GET /api/ml/latest-risk.
  8. Safety invariants (ENABLE_PUBLIC_DISPATCH=0, SIREN_DRY_RUN=1, FoS/probability separation).
"""

import os
import sys
import unittest
from unittest.mock import patch

# Ensure application path is accessible
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app import app as flask_app
from engine.canonical_registry import CANONICAL_REGISTRY, CanonicalLocation


class TestPhase9ACanonicalRegistry(unittest.TestCase):
    """Tests for engine/canonical_registry.py singleton and data integrity."""

    def test_ner_eight_states_coverage(self):
        """Registry must contain surveyed corridors across all 8 NER states."""
        states = set(CANONICAL_REGISTRY.list_states())
        expected_ner_states = {
            "Sikkim", "Manipur", "Mizoram", "Assam",
            "Meghalaya", "Nagaland", "Arunachal Pradesh", "Tripura"
        }
        for st in expected_ner_states:
            self.assertIn(st, states, f"State '{st}' missing from canonical registry.")

    def test_strategic_locations_count(self):
        """Master registry must contain at least 25 canonical locations."""
        all_locs = CANONICAL_REGISTRY.list_locations()
        self.assertGreaterEqual(len(all_locs), 25)

    def test_alias_resolution(self):
        """Locations must resolve by primary canonical ID and legacy aliases."""
        # Primary lookup
        loc1 = CANONICAL_REGISTRY.get_location("SK-NH10-KM48")
        self.assertIsNotNone(loc1)
        self.assertEqual(loc1.state, "Sikkim")

        # Legacy alias lookup
        loc1_alias1 = CANONICAL_REGISTRY.get_location("CORR-NH10-SIKKIM-KM48")
        self.assertIsNotNone(loc1_alias1)
        self.assertEqual(loc1_alias1.id, "SK-NH10-KM48")

        loc1_alias2 = CANONICAL_REGISTRY.get_location("NH10-KM48")
        self.assertIsNotNone(loc1_alias2)
        self.assertEqual(loc1_alias2.id, "SK-NH10-KM48")

    def test_find_nearest_haversine(self):
        """Haversine nearest lookup finds closest corridor accurately."""
        # Coordinate near Gangtok / Singtam (27.24, 88.50)
        nearest_res = CANONICAL_REGISTRY.find_nearest(27.24, 88.50, max_radius_km=50.0)
        self.assertIsNotNone(nearest_res)
        loc, dist = nearest_res
        self.assertEqual(loc.id, "SK-SINGTAM-01")
        self.assertLess(dist, 5.0)

    def test_to_geojson_format(self):
        """GeoJSON export must conform to FeatureCollection standard."""
        fc = CANONICAL_REGISTRY.to_geojson(state="Manipur")
        self.assertEqual(fc["type"], "FeatureCollection")
        self.assertGreater(fc["count"], 0)
        self.assertEqual(len(fc["features"]), fc["count"])
        feat = fc["features"][0]
        self.assertEqual(feat["type"], "Feature")
        self.assertEqual(feat["geometry"]["type"], "Point")
        self.assertEqual(feat["properties"]["state"], "Manipur")


class TestPhase9ABackendEndpoints(unittest.TestCase):
    """Integration tests for Phase 9A REST APIs."""

    def setUp(self):
        self.client = flask_app.test_client()

    def test_get_locations_all(self):
        """GET /api/pahad/locations returns complete catalog with states and districts."""
        res = self.client.get("/api/pahad/locations")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertGreaterEqual(data["count"], 25)
        self.assertIn("states", data)
        self.assertIn("districts", data)
        self.assertIn("locations", data)

    def test_get_locations_filtered_by_state(self):
        """GET /api/pahad/locations?state=... filters accurately."""
        # Test Mizoram
        res_mz = self.client.get("/api/pahad/locations?state=Mizoram")
        self.assertEqual(res_mz.status_code, 200)
        data_mz = res_mz.get_json()
        self.assertGreater(data_mz["count"], 0)
        for loc in data_mz["locations"]:
            self.assertEqual(loc["state"], "Mizoram")

        # Test Nagaland
        res_nl = self.client.get("/api/pahad/locations?state=Nagaland")
        self.assertEqual(res_nl.status_code, 200)
        data_nl = res_nl.get_json()
        self.assertGreater(data_nl["count"], 0)
        for loc in data_nl["locations"]:
            self.assertEqual(loc["state"], "Nagaland")

    def test_get_locations_geojson(self):
        """GET /api/pahad/locations?format=geojson returns GeoJSON FeatureCollection."""
        res = self.client.get("/api/pahad/locations?format=geojson")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertIn("features", data)

    def test_location_risk_canonical_all_ner_states(self):
        """POST /api/pahad/location-risk evaluates corridors across all 8 NER states."""
        test_corridors = [
            ("SK-NH10-KM48", "Sikkim"),
            ("MN-TUPUL-RLY", "Manipur"),
            ("MZ-MELTHUM-QRY", "Mizoram"),
            ("AS-HAFLONG-RLY", "Assam"),
            ("ML-MAWSYNRAM", "Meghalaya"),
            ("NL-DZUKOU-KOH", "Nagaland"),
            ("AR-TAWANG-SELA", "Arunachal Pradesh"),
            ("TR-JAMPUI-HILLS", "Tripura"),
        ]

        for corr_id, expected_state in test_corridors:
            payload = {"location_id": corr_id, "horizon_hours": 24}
            res = self.client.post("/api/pahad/location-risk", json=payload)
            self.assertEqual(res.status_code, 200, f"Failed for corridor {corr_id}")
            data = res.get_json()
            self.assertEqual(data["status"], "SUCCESS")
            self.assertEqual(data["location"]["state"], expected_state)
            self.assertIn("inference", data)
            inf = data["inference"]
            self.assertIn("cri", inf)
            self.assertIn("risk_band", inf)
            self.assertIn("fos_physical", inf)
            self.assertIn("event_probability", inf)
            self.assertIn("forecast", data)
            self.assertIn("horizons", data["forecast"])
            for h in ["6h", "12h", "24h", "48h"]:
                self.assertIn(h, data["forecast"]["horizons"])

    def test_location_risk_custom_coordinates(self):
        """POST /api/pahad/location-risk evaluates arbitrary coordinates and resolves nearest corridor."""
        # Dzukou Valley coordinates: Lat 25.5800, Lon 94.1200
        payload = {
            "latitude": 25.5800,
            "longitude": 94.1200,
            "name": "Dzukou Field Site Test"
        }
        res = self.client.post("/api/pahad/location-risk", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        loc = data["location"]
        self.assertEqual(loc["status"], "DYNAMIC_COORDINATE")
        self.assertEqual(loc["lat"], 25.5800)
        self.assertEqual(loc["lon"], 94.1200)
        self.assertIsNotNone(loc.get("nearest_registered_corridor"))
        self.assertIsNotNone(loc.get("distance_to_nearest_km"))

        # Verify physics and ML fields present
        inf = data["inference"]
        self.assertGreater(inf["cri"], 0.0)
        self.assertGreater(inf["fos_physical"], 0.0)

    def test_location_risk_error_handling(self):
        """Endpoint rejects out-of-bounds coordinates and invalid payloads gracefully."""
        # Lat out of range
        res1 = self.client.post("/api/pahad/location-risk", json={"latitude": 95.0, "longitude": 88.0})
        self.assertEqual(res1.status_code, 422)

        # Missing both ID and coordinates
        res2 = self.client.post("/api/pahad/location-risk", json={"horizon_hours": 24})
        self.assertEqual(res2.status_code, 422)

        # Non-existent ID with no coordinates
        res3 = self.client.post("/api/pahad/location-risk", json={"location_id": "NON-EXISTENT-SECTOR-999"})
        self.assertEqual(res3.status_code, 404)

    def test_cross_location_isolation(self):
        """Data for one state must never bleed or contaminate another state's evaluation."""
        res_mn = self.client.post("/api/pahad/location-risk", json={"location_id": "MN-TUPUL-RLY"})
        res_sk = self.client.post("/api/pahad/location-risk", json={"location_id": "SK-NH10-KM48"})

        data_mn = res_mn.get_json()
        data_sk = res_sk.get_json()

        # Coordinate isolation
        self.assertNotEqual(data_mn["location"]["lat"], data_sk["location"]["lat"])
        self.assertNotEqual(data_mn["location"]["lon"], data_sk["location"]["lon"])
        self.assertEqual(data_mn["location"]["state"], "Manipur")
        self.assertEqual(data_sk["location"]["state"], "Sikkim")

        # Sector ID isolation
        self.assertEqual(data_mn["inference"]["sector_id"], "MN-TUPUL-RLY")
        self.assertEqual(data_sk["inference"]["sector_id"], "SK-NH10-KM48")

    def test_latest_risk_multi_state_fallback(self):
        """GET /api/ml/latest-risk deterministic fallback must cover multi-state corridors when DB offline."""
        with patch("app.get_db", side_effect=Exception("Database Offline Simulator")):
            res = self.client.get("/api/ml/latest-risk")
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertIn("evaluations", data)
            evals = data["evaluations"]
            self.assertGreaterEqual(len(evals), 8)

            states_represented = {e.get("state") for e in evals if e.get("state")}
            self.assertIn("Sikkim", states_represented)
            self.assertIn("Manipur", states_represented)
            self.assertIn("Mizoram", states_represented)
            self.assertIn("Assam", states_represented)
            self.assertIn("Meghalaya", states_represented)
            self.assertIn("Nagaland", states_represented)
            self.assertIn("Arunachal Pradesh", states_represented)
            self.assertIn("Tripura", states_represented)

    def test_safety_invariants_preserved(self):
        """Verify strict safety invariants remain intact."""
        # 1. Public dispatch disabled
        self.assertEqual(os.getenv("ENABLE_PUBLIC_DISPATCH", "0"), "0")

        # 2. Siren dry run enabled
        self.assertEqual(os.getenv("SIREN_DRY_RUN", "1"), "1")

        # 3. FoS physical is distinct from event ML probability
        res = self.client.post("/api/pahad/location-risk", json={"location_id": "SK-NH10-KM48"})
        data = res.get_json()
        inf = data["inference"]
        self.assertIn("fos_physical", inf)
        self.assertIn("event_probability", inf)
        self.assertNotEqual(inf["fos_physical"], inf["event_probability"])


if __name__ == "__main__":
    unittest.main()
