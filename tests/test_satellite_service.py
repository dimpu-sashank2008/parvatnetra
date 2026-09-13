# -*- coding: utf-8 -*-
"""
tests/test_satellite_service.py
===============================
Unit & Integration Tests for Satellite Intelligence & InSAR Provenance Service
"""

import unittest
from services.satellite_service import SatelliteService, SatelliteAcquisitionRecord


class TestSatelliteService(unittest.TestCase):

    def setUp(self):
        self.satellite_service = SatelliteService()

    def test_satellite_latest_acquisition(self):
        latest_optical = self.satellite_service.get_latest_acquisition("OPTICAL")
        self.assertIsNotNone(latest_optical)
        self.assertEqual(latest_optical["sensor_type"], "OPTICAL")
        self.assertIn("Sentinel-2", latest_optical["mission_name"])
        self.assertIn("footprint_geojson", latest_optical)
        self.assertIn(latest_optical["provenance"], ["[LIVE]", "[CACHED]", "[HISTORICAL]"])

        latest_sar = self.satellite_service.get_latest_acquisition("SAR_C_BAND")
        self.assertIsNotNone(latest_sar)
        self.assertEqual(latest_sar["sensor_type"], "SAR_C_BAND")

    def test_satellite_scene_footprints(self):
        footprints = self.satellite_service.get_footprints_geojson()
        self.assertEqual(footprints.get("type"), "FeatureCollection")
        self.assertIn("features", footprints)
        self.assertGreater(len(footprints["features"]), 0)

        for feature in footprints["features"]:
            self.assertEqual(feature.get("type"), "Feature")
            self.assertEqual(feature["geometry"]["type"], "Polygon")
            props = feature["properties"]
            self.assertIn("mission_name", props)
            self.assertIn("sensor_id", props)
            self.assertIn("acquisition_time", props)
            self.assertIn("deformation_source_tier", props)
            self.assertIn(props["deformation_source_tier"], ["[PROCESSED_LIVE]", "[STATIC_PRODUCT]", "[SIMULATED]", "[DEMO]"])

    def test_get_insar_deformation_source_honesty(self):
        # Must return valid provenance, and must NOT pretend live if no live interferogram pipeline
        def_data = self.satellite_service.get_insar_deformation_for_sector("SK-NH10-KM48")
        self.assertIsInstance(def_data, dict)
        self.assertIn("sector_id", def_data)
        self.assertIn("status", def_data)
        self.assertIn("deformation_source_tier", def_data)
        self.assertIn("provenance", def_data)
        self.assertIn("analysis", def_data)
        self.assertIn(def_data["deformation_source_tier"], ["[PROCESSED_LIVE]", "[STATIC_PRODUCT]", "[SIMULATED]", "[DEMO]"])


if __name__ == '__main__':
    unittest.main()
