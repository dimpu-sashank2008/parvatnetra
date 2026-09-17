# -*- coding: utf-8 -*-
"""
tests/test_multi_source_terrain.py
==================================
Unit & Integration Tests for Multi-Source Terrain Ingestion,
Cross-Validation & Geotechnical Stability Envelope Engine.
"""

import os
os.environ["PARVAT_TESTING"] = "1"

import unittest
import numpy as np
from app import app
from services.dem_service import DEM_SERVICE, DEMService, MultiSourceElevationResult, MultiSourceTerrainResult
from engine.pahad_models import calculate_multi_source_slope_fs, MultiSourceSlopeResult


class TestMultiSourceTerrain(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.svc = DEMService()
        self.test_lat = 27.3300  # NH-10 Km 48 corridor
        self.test_lon = 88.6100

    def test_multi_source_elevation_structure(self):
        res = self.svc.get_multi_source_elevation(self.test_lat, self.test_lon)
        self.assertIsInstance(res, MultiSourceElevationResult)
        self.assertGreater(res.consensus_elevation_m, 100.0)
        self.assertGreater(res.median_elevation_m, 100.0)
        self.assertGreaterEqual(res.agreement_score, 0.0)
        self.assertLessEqual(res.agreement_score, 1.0)
        self.assertIn(res.confidence_tier, ["HIGH", "MODERATE", "LOW"])

        # Check that individual space agency sources are present
        sources = res.sources
        self.assertIn("isro_cartodem", sources)
        self.assertIn("copernicus_glo30", sources)
        self.assertIn("nasa_srtm", sources)
        self.assertIn("jaxa_alos", sources)

        # Confirm all elevations are positive and realistic for the Himalayas
        for sid in ["isro_cartodem", "copernicus_glo30", "nasa_srtm", "jaxa_alos"]:
            elev = sources[sid]["elevation_m"]
            self.assertGreaterEqual(elev, 200.0)
            self.assertLessEqual(elev, 8848.0)

    def test_multi_source_terrain_derivatives(self):
        res = self.svc.get_multi_source_terrain(self.test_lat, self.test_lon)
        self.assertIsInstance(res, MultiSourceTerrainResult)

        # Check slope statistics
        self.assertGreaterEqual(res.consensus_slope_deg, 0.0)
        self.assertLessEqual(res.consensus_slope_deg, 90.0)
        self.assertGreaterEqual(res.worst_case_slope_deg, res.consensus_slope_deg - 0.01)
        self.assertLessEqual(res.slope_min_deg, res.consensus_slope_deg + 0.01)
        self.assertGreaterEqual(res.slope_std_dev_deg, 0.0)

        # Check source slopes
        for sid in ["isro_cartodem", "copernicus_glo30", "nasa_srtm", "jaxa_alos"]:
            self.assertIn(sid, res.source_slopes)
            sl = res.source_slopes[sid]
            self.assertGreaterEqual(sl, 0.0)
            self.assertLessEqual(sl, 90.0)

        # Confirm TRI and relief
        self.assertGreaterEqual(res.terrain_ruggedness_index, 0.0)
        self.assertGreaterEqual(res.relative_relief_m, 0.0)
        self.assertIn("ISRO CartoDEM (30m)", res.sources_consulted)

    def test_stability_envelope_calculation(self):
        env = self.svc.get_stability_envelope(
            lat=self.test_lat,
            lon=self.test_lon,
            cohesion_kpa=16.0,
            friction_deg=28.0,
            soil_depth_m=3.5,
            water_table_ratio=0.5
        )
        self.assertIsInstance(env, dict)
        self.assertIn("consensus_fos", env)
        self.assertIn("conservative_fos", env)
        self.assertIn("optimistic_fos", env)
        self.assertIn("slope_sensitivity_per_deg", env)
        self.assertIn("envelope_status", env)

        # In physics: conservative FoS (steepest slope) <= consensus FoS <= optimistic FoS (gentlest slope)
        self.assertLessEqual(env["conservative_fos"], env["consensus_fos"] + 0.001)
        self.assertGreaterEqual(env["optimistic_fos"], env["consensus_fos"] - 0.001)
        self.assertGreaterEqual(env["slope_sensitivity_per_deg"], 0.0)

    def test_calculate_multi_source_slope_fs_physics(self):
        res = calculate_multi_source_slope_fs(
            cohesion_kpa=18.0,
            friction_deg=30.0,
            slope_consensus_deg=35.0,
            slope_max_deg=39.0,
            slope_min_deg=32.0,
            soil_depth_m=3.0,
            water_table_ratio=0.3,
            soil_sat_weight=19.0
        )
        self.assertIsInstance(res, MultiSourceSlopeResult)
        self.assertLess(res.conservative_fs, res.consensus_fs)
        self.assertGreater(res.optimistic_fs, res.consensus_fs)
        self.assertGreater(res.slope_sensitivity_per_deg, 0.0)
        self.assertEqual(res.consensus_slope_deg, 35.0)
        self.assertEqual(res.worst_case_slope_deg, 39.0)

    def test_api_terrain_point_endpoint(self):
        resp = self.client.get(f"/api/terrain/point?lat={self.test_lat}&lon={self.test_lon}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("consensus", data)
        self.assertIn("sources", data)
        self.assertIn("stability_envelope", data)
        self.assertIn("elevation_m", data["consensus"])
        self.assertIn("slope_deg", data["consensus"])
        self.assertIn("isro_cartodem", data["sources"]["slopes"])
        self.assertIn("copernicus_glo30", data["sources"]["slopes"])

    def test_api_terrain_multi_source_endpoint(self):
        resp = self.client.get(f"/api/terrain/multi-source?lat={self.test_lat}&lon={self.test_lon}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("elevation_analysis", data)
        self.assertIn("terrain_analysis", data)
        self.assertIn("summary", data)
        self.assertIn("elevation_agreement_score", data["summary"])
        self.assertIn("slope_agreement_score", data["summary"])

    def test_api_geospatial_dem_multi_source_enhancement(self):
        resp = self.client.get(f"/api/geospatial/dem?lat={self.test_lat}&lon={self.test_lon}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("multi_source_elevation", data)
        multi = data["multi_source_elevation"]
        self.assertIn("consensus_elevation_m", multi)
        self.assertIn("sources", multi)
        self.assertIn("isro_cartodem", multi["sources"])


if __name__ == "__main__":
    unittest.main()
