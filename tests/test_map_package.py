# -*- coding: utf-8 -*-
"""
PARVAT NETRA - Offline Map Package Validation Test Suite
Phase 3.2: Offline-First Web, Map Resilience & Data Synchronization
"""

import os
import json
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PACKAGE_PATH = os.path.join(REPO_ROOT, 'static', 'data', 'offline_core_package.json')


class TestOfflineMapPackage(unittest.TestCase):
    """Validates the pre-bundled standalone core vector map package."""

    @classmethod
    def setUpClass(cls):
        cls.assertTrue = unittest.TestCase.assertTrue
        if not os.path.exists(PACKAGE_PATH):
            raise FileNotFoundError(f"Offline core package missing: {PACKAGE_PATH}")
        with open(PACKAGE_PATH, 'r', encoding='utf-8') as f:
            cls.package = json.load(f)

    def test_01_package_structure_and_metadata(self):
        """Verify package envelope contains mandatory metadata fields."""
        self.assertEqual(self.package.get("type"), "FeatureCollection")
        self.assertIn("package_metadata", self.package)
        meta = self.package["package_metadata"]
        self.assertEqual(meta.get("package_id"), "ner-core-v1")
        self.assertEqual(meta.get("version"), "1.0")
        self.assertIn("bounding_box", meta)
        self.assertIn("feature_counts", meta)
        self.assertIn("features", self.package)

    def test_02_feature_layers_comprehensiveness(self):
        """Verify core features include boundaries, roads, rivers, shelters, landslides, sectors."""
        features = self.package.get("features", [])
        self.assertGreaterEqual(len(features), 30, "Package must contain at least 30 core features")

        layer_groups = {feat.get("properties", {}).get("layer_group") for feat in features}
        expected_groups = {
            "ADMIN_BOUNDARIES",
            "ROADS",
            "HYDROLOGY",
            "PAHAD_SECTORS",
            "SHELTERS",
            "HISTORICAL_LANDSLIDES"
        }
        for expected in expected_groups:
            self.assertIn(expected, layer_groups, f"Missing mandatory offline map layer group: {expected}")

    def test_03_ner_state_boundaries_coverage(self):
        """Verify presence of Northeast Region state administrative polygons."""
        states = [
            f["properties"].get("name")
            for f in self.package["features"]
            if f["properties"].get("layer_group") == "ADMIN_BOUNDARIES"
        ]
        self.assertGreaterEqual(len(states), 8, "All 8 NER states must be bundled")
        for st in ["Sikkim", "Assam", "Arunachal Pradesh", "Meghalaya"]:
            self.assertIn(st, states, f"State {st} missing from offline boundaries")

    def test_04_strategic_mountain_corridors(self):
        """Verify lifeline mountain roads (NH-10, NH-717A bypass, etc.) are present."""
        corridors = [
            f["properties"].get("corridor_id") or f["properties"].get("name")
            for f in self.package["features"]
            if f["properties"].get("layer_group") == "ROADS"
        ]
        self.assertGreaterEqual(len(corridors), 4, "Must bundle primary NER highway lifelines")
        corridor_str = " ".join(str(c) for c in corridors)
        self.assertIn("NH-10", corridor_str)

    def test_05_critical_pahad_sectors(self):
        """Verify critical sectors include hazard ratings and identifiers."""
        sectors = [
            f for f in self.package["features"]
            if f["properties"].get("layer_group") == "PAHAD_SECTORS"
        ]
        self.assertGreaterEqual(len(sectors), 10, "Must bundle at least 10 critical pilot sectors")
        for s in sectors:
            props = s["properties"]
            self.assertIn("sector_id", props)
            self.assertIn("hazard_rating", props)
            self.assertIn("name", props)

    def test_06_geometry_and_coordinate_bounds(self):
        """Verify all coordinates fall within NER geographic envelope (Lat: 21-30, Lon: 87-98)."""
        for feat in self.package["features"]:
            geom = feat.get("geometry", {})
            geom_type = geom.get("type")
            coords = geom.get("coordinates")
            self.assertIn(geom_type, ["Point", "LineString", "Polygon", "MultiPolygon"])
            self.assertIsNotNone(coords)

            if geom_type == "Point":
                lon, lat = coords[0], coords[1]
                self.assertTrue(87.0 <= lon <= 98.0, f"Point longitude {lon} out of NER bounds")
                self.assertTrue(21.0 <= lat <= 30.5, f"Point latitude {lat} out of NER bounds")

    def test_07_package_file_size_efficiency(self):
        """Verify offline package is lightweight (< 250 KB) for instant zero-lag rendering."""
        size_bytes = os.path.getsize(PACKAGE_PATH)
        self.assertLess(size_bytes, 250 * 1024, f"Package size {size_bytes} exceeds 250KB limit")
        self.assertGreater(size_bytes, 10 * 1024, f"Package size {size_bytes} too small")


if __name__ == '__main__':
    unittest.main(verbosity=2)
