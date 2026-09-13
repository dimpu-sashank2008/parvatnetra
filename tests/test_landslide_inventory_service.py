# -*- coding: utf-8 -*-
"""
tests/test_landslide_inventory_service.py
=========================================
Unit & Integration Tests for Historical Landslide Inventory Service
"""

import unittest
from services.landslide_inventory_service import LandslideInventoryService


class TestLandslideInventoryService(unittest.TestCase):

    def setUp(self):
        self.inventory_service = LandslideInventoryService()

    def test_query_geojson_default(self):
        geojson = self.inventory_service.get_geojson(limit=25)
        self.assertEqual(geojson.get("type"), "FeatureCollection")
        self.assertIn("features", geojson)
        self.assertGreater(len(geojson["features"]), 0)
        self.assertLessEqual(len(geojson["features"]), 25)

        for feature in geojson["features"]:
            self.assertEqual(feature.get("type"), "Feature")
            self.assertIn("geometry", feature)
            self.assertEqual(feature["geometry"]["type"], "Point")
            props = feature["properties"]
            self.assertIn("location", props)
            self.assertIn("severity", props)
            self.assertIn("source", props)
            self.assertEqual(props["provenance"], "[HISTORICAL]")

    def test_query_by_state(self):
        geojson = self.inventory_service.get_geojson(state="Sikkim", limit=50)
        for feature in geojson["features"]:
            self.assertEqual(feature["properties"]["state"], "Sikkim")

    def test_query_by_bbox(self):
        geojson = self.inventory_service.get_geojson(
            min_lat=27.15, max_lat=27.35, min_lon=88.45, max_lon=88.65
        )
        for feature in geojson["features"]:
            lon, lat = feature["geometry"]["coordinates"]
            self.assertGreaterEqual(lat, 27.15 - 0.05)
            self.assertLessEqual(lat, 27.35 + 0.05)
            self.assertGreaterEqual(lon, 88.45 - 0.05)
            self.assertLessEqual(lon, 88.65 + 0.05)

    def test_evaluate_sector_history(self):
        density = self.inventory_service.evaluate_sector_history(
            sector_id="SK-NH10-KM48", lat=27.33, lon=88.61
        )
        self.assertIsInstance(density, dict)
        self.assertIn("events_within_1km", density)
        self.assertIn("events_within_5km", density)
        self.assertIn("nearest_event_distance_km", density)
        self.assertIn("nearest_event", density)
        self.assertIn("event_density_per_km2", density)
        self.assertIn("historical_susceptibility_signal", density)
        self.assertEqual(density["provenance"], "[HISTORICAL]")
        self.assertIn(density["historical_susceptibility_signal"], ["LOW", "MODERATE", "HIGH", "VERY_HIGH"])


if __name__ == '__main__':
    unittest.main()
