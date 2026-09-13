# -*- coding: utf-8 -*-
"""
tests/test_vegetation_service.py
================================
Unit & Integration Tests for Vegetation Intelligence & NDVI Service
"""

import unittest
from services.vegetation_service import VegetationService, calculate_ndvi


class TestVegetationService(unittest.TestCase):

    def setUp(self):
        self.veg_service = VegetationService()

    def test_calculate_ndvi_healthy(self):
        # Dense vegetation: high NIR (0.468), low RED (0.082)
        # NDVI = (0.468 - 0.082) / (0.468 + 0.082) = 0.386 / 0.550 = 0.7018
        ndvi = calculate_ndvi(nir_band=0.468, red_band=0.082)
        self.assertAlmostEqual(ndvi, 0.7018, places=3)

    def test_calculate_ndvi_water_or_shadow(self):
        # Water/Shadow: very low NIR, higher RED
        ndvi = calculate_ndvi(nir_band=0.04, red_band=0.10)
        self.assertLess(ndvi, 0.0)

    def test_get_vegetation_for_known_sector(self):
        # 29th Mile sector
        feats = self.veg_service.get_vegetation_for_sector("SK-NH10-KM48")
        self.assertIsInstance(feats, dict)
        self.assertIn("ndvi", feats)
        self.assertIn("previous_ndvi", feats)
        self.assertIn("ndvi_change", feats)
        self.assertIn("vegetation_status", feats)
        self.assertIn("bare_soil_increase_pct", feats)
        self.assertIn("source", feats)
        self.assertIn("data_age_days", feats)
        self.assertIn(feats["provenance"], ["[LIVE]", "[CACHED]", "[HISTORICAL]", "[DEGRADED]"])
        self.assertGreaterEqual(feats["ndvi"], -1.0)
        self.assertLessEqual(feats["ndvi"], 1.0)

    def test_get_vegetation_for_bbox(self):
        res = self.veg_service.get_vegetation_for_bbox(
            min_lat=27.2, max_lat=27.4, min_lon=88.4, max_lon=88.6
        )
        self.assertIsInstance(res, dict)
        self.assertIn("ndvi", res)
        self.assertIn("previous_ndvi", res)
        self.assertIn("ndvi_change", res)
        self.assertIn("vegetation_status", res)
        self.assertIn("provenance", res)


if __name__ == '__main__':
    unittest.main()
