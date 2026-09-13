# -*- coding: utf-8 -*-
"""
tests/test_terrain_analysis.py
==============================
Unit & Integration Tests for Geotechnical Terrain Analysis Engine
"""

import unittest
import numpy as np

from engine.terrain_analysis import (
    calculate_slope,
    calculate_aspect,
    calculate_curvature,
    generate_hillshade,
    generate_contours
)


class TestTerrainAnalysis(unittest.TestCase):

    def setUp(self):
        # Create a synthetic 20x20 sloping plane: elevation increases from west to east
        x = np.arange(20)
        y = np.arange(20)
        xx, yy = np.meshgrid(x, y)
        self.plane = 100.0 + (xx * 30.0 * np.tan(np.radians(30.0)))
        self.bounds = {
            "min_lat": 27.20,
            "max_lat": 27.30,
            "min_lon": 88.40,
            "max_lon": 88.50
        }

    def test_calculate_slope_sloping_plane(self):
        slope_deg = calculate_slope(self.plane, cell_size_m=30.0)
        self.assertEqual(slope_deg.shape, self.plane.shape)
        inner_slope = slope_deg[2:-2, 2:-2]
        self.assertAlmostEqual(float(np.mean(inner_slope)), 30.0, delta=1.5)
        self.assertTrue(np.all(slope_deg >= 0.0))
        self.assertTrue(np.all(slope_deg <= 90.0))

    def test_calculate_slope_flat_plane(self):
        flat = np.full((15, 15), 500.0)
        slope_deg = calculate_slope(flat, cell_size_m=30.0)
        self.assertTrue(np.allclose(slope_deg, 0.0))

    def test_calculate_aspect_east_slope(self):
        aspect_deg = calculate_aspect(self.plane, cell_size_m=30.0)
        self.assertEqual(aspect_deg.shape, self.plane.shape)
        inner_aspect = aspect_deg[2:-2, 2:-2]
        self.assertTrue(np.all(inner_aspect >= 0.0))
        self.assertTrue(np.all(inner_aspect <= 360.0))

    def test_calculate_curvature(self):
        plan_curv, prof_curv = calculate_curvature(self.plane, cell_size_m=30.0)
        self.assertEqual(plan_curv.shape, self.plane.shape)
        self.assertEqual(prof_curv.shape, self.plane.shape)
        self.assertTrue(np.all(np.abs(plan_curv[2:-2, 2:-2]) < 0.1))
        self.assertTrue(np.all(np.abs(prof_curv[2:-2, 2:-2]) < 0.1))

    def test_generate_hillshade(self):
        hillshade = generate_hillshade(self.plane, cell_size_m=30.0, azimuth_deg=315.0, altitude_deg=45.0)
        self.assertEqual(hillshade.shape, self.plane.shape)
        self.assertTrue(np.all(hillshade >= 0))
        self.assertTrue(np.all(hillshade <= 255))
        self.assertGreater(float(np.mean(hillshade)), 0)

    def test_generate_contours_interval(self):
        step_terrain = np.linspace(500, 700, 25).reshape(5, 5)
        geojson = generate_contours(step_terrain, self.bounds, interval_m=50.0)
        self.assertIsInstance(geojson, dict)
        self.assertEqual(geojson.get("type"), "FeatureCollection")
        self.assertIn("features", geojson)
        for feature in geojson["features"]:
            self.assertEqual(feature.get("type"), "Feature")
            self.assertIn("elevation_m", feature["properties"])
            self.assertIn("interval_m", feature["properties"])
            self.assertEqual(feature["geometry"]["type"], "MultiLineString")


if __name__ == '__main__':
    unittest.main()
