# -*- coding: utf-8 -*-
"""
tests/test_dem_service.py
=========================
Unit & Integration Tests for DEM Ingestion & Query Service
"""

import unittest
import numpy as np

from services.dem_service import DEMService, DEMMetadata


class TestDEMService(unittest.TestCase):

    def setUp(self):
        self.dem_service = DEMService()

    def test_crs_validation_valid(self):
        self.assertTrue(self.dem_service.validate_crs("EPSG:4326"))
        self.assertTrue(self.dem_service.validate_crs("EPSG:3857"))
        self.assertTrue(self.dem_service.validate_crs("WGS84"))

    def test_crs_validation_invalid(self):
        self.assertFalse(self.dem_service.validate_crs("INVALID:9999"))
        self.assertFalse(self.dem_service.validate_crs("LOCAL_GRID"))

    def test_metadata_and_bounds(self):
        meta = self.dem_service.get_metadata()
        self.assertIsInstance(meta, dict)
        self.assertIn("bounds", meta)
        self.assertIn("resolution_m", meta)
        self.assertEqual(meta["resolution_m"], 30.0)
        self.assertEqual(meta["status"], "AVAILABLE")
        self.assertIn(meta["provenance"], ["[LIVE]", "[CACHED]", "[HISTORICAL]"])
        bounds = meta["bounds"]
        self.assertLess(bounds["min_lat"], bounds["max_lat"])
        self.assertLess(bounds["min_lon"], bounds["max_lon"])

    def test_get_elevation_at_point(self):
        # Point inside Sikkim bounding box (Gangtok / 29th Mile corridor ~27.25, 88.55)
        elev = self.dem_service.get_elevation(27.25, 88.55)
        self.assertIsNotNone(elev)
        self.assertGreaterEqual(elev, 180.0)
        self.assertLessEqual(elev, 8848.0)

    def test_get_elevation_grid(self):
        grid, lats, lons = self.dem_service.get_elevation_grid(
            min_lat=27.2, max_lat=27.4, min_lon=88.4, max_lon=88.6, grid_rows=32, grid_cols=32
        )
        self.assertIsInstance(grid, np.ndarray)
        self.assertEqual(grid.shape, (32, 32))
        self.assertEqual(len(lats), 32)
        self.assertEqual(len(lons), 32)
        self.assertFalse(np.isnan(grid).any())
        self.assertGreater(float(np.max(grid)), float(np.min(grid)))


if __name__ == '__main__':
    unittest.main()
