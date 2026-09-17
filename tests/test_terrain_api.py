# -*- coding: utf-8 -*-
"""
tests/test_terrain_api.py
=========================
Integration Tests for Phase 2C Geospatial REST Endpoints
"""

import os
os.environ["PARVAT_TESTING"] = "1"

import unittest
from app import app


class TestTerrainAPI(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_get_dem_endpoint(self):
        res = self.client.get("/api/geospatial/dem")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("source", data)
        self.assertIn("provenance", data)
        self.assertIn("resolution_m", data)
        self.assertIn("bounds", data)
        self.assertTrue(data.get("available"))

    def test_get_terrain_elevation_product(self):
        res = self.client.get("/api/geospatial/terrain?product=elevation&bbox=88.4,27.2,88.6,27.4")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("product"), "elevation")
        self.assertIn("metadata", data)
        self.assertIn("min_elevation_m", data["metadata"])

    def test_get_terrain_slope_product(self):
        res = self.client.get("/api/geospatial/terrain?product=slope&bbox=88.4,27.2,88.6,27.4")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("product"), "slope")
        self.assertIn("metadata", data)
        self.assertIn("mean_slope_deg", data["metadata"])

    def test_get_terrain_curvature_product(self):
        res = self.client.get("/api/geospatial/terrain?product=curvature&bbox=88.4,27.2,88.6,27.4")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("product"), "curvature")
        self.assertIn("plan_curvature", data)
        self.assertIn("profile_curvature", data)

    def test_get_terrain_hillshade_product(self):
        res = self.client.get("/api/geospatial/terrain?product=hillshade&bbox=88.4,27.2,88.6,27.4")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("product"), "hillshade")

    def test_get_terrain_contours_product(self):
        res = self.client.get("/api/geospatial/terrain?product=contours&bbox=88.45,27.20,88.60,27.35&interval=20")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("product"), "contours")
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertIn("geojson", data)
        self.assertEqual(data["geojson"].get("type"), "FeatureCollection")

    def test_get_vegetation_endpoint(self):
        res = self.client.get("/api/geospatial/vegetation?sector_id=1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("ndvi", data)
        self.assertIn("previous_ndvi", data)
        self.assertIn("ndvi_change", data)
        self.assertIn("vegetation_status", data)
        self.assertIn("source", data)
        self.assertIn("provenance", data)

    def test_get_historical_landslides_endpoint(self):
        res = self.client.get("/api/geospatial/historical-landslides?state=Sikkim&limit=20")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("type"), "FeatureCollection")
        self.assertIn("features", data)

    def test_get_satellite_status_endpoint(self):
        res = self.client.get("/api/geospatial/satellite/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn(data.get("status"), ["SUCCESS", "OPERATIONAL"])
        self.assertIn("scenes", data)

    def test_get_satellite_footprints_endpoint(self):
        res = self.client.get("/api/geospatial/satellite/footprints")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("type"), "FeatureCollection")
        self.assertIn("features", data)

    def test_get_offline_manifest_endpoint(self):
        res = self.client.get("/api/geospatial/offline-manifest")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn(data.get("status"), ["SUCCESS", "OPERATIONAL"])
        self.assertIn("available_layers", data)

    def test_terrain_3d_page(self):
        res = self.client.get("/terrain-3d")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn("PARVATNETRA", html)
        self.assertIn("3D TERRAIN INTELLIGENCE", html)
        self.assertIn("PAHAD AI", html)


    def test_terrain_difference_product(self):
        res = self.client.get("/api/geospatial/terrain?product=difference&source_a=isro_cartodem&source_b=copernicus_glo30&grid_size=16")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertEqual(data.get("product"), "difference")
        self.assertEqual(data.get("source_a"), "isro_cartodem")
        self.assertEqual(data.get("source_b"), "copernicus_glo30")
        self.assertIn("mae_m", data)
        self.assertIn("agreement_within_2m_pct", data)
        self.assertIn("matrix", data)
        self.assertEqual(len(data["matrix"]), 16)


if __name__ == '__main__':
    unittest.main()
