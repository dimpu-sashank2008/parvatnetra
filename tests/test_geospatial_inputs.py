# -*- coding: utf-8 -*-
"""
tests/test_geospatial_inputs.py
===============================
Tests for PAHAD Unified Feature Inputs with Phase 2C Geospatial Dimensions
"""

import unittest

from engine.pahad_inputs import (
    PahadUnifiedInputContract,
    TerrainDimension,
    SatelliteDimension,
    HistoryDimension,
    InfrastructureDimension,
    ClimateDimension,
    SeismicDimension,
    GroundDimension,
    FieldDimension,
    build_pahad_feature_vector
)
from engine.anthropogenic_slope_service import AnthropogenicSlopeService
from engine.geospatial_registry import GeospatialRegistry


class TestGeospatialInputs(unittest.TestCase):

    def test_terrain_dimension_fields(self):
        td = TerrainDimension(
            slope_deg=34.5,
            aspect_deg=210.0,
            elevation_m=620.0,
            cohesion_kpa=18.0,
            friction_deg=29.0,
            source="DEM",
            provenance="[LIVE]",
            plan_curvature=-0.04,
            profile_curvature=0.08,
            hillshade=178,
            terrain_resolution="30m",
            terrain_source="Copernicus DEM 30m GLO-30"
        )
        self.assertEqual(td.elevation_m, 620.0)
        self.assertEqual(td.slope_deg, 34.5)
        self.assertEqual(td.aspect_deg, 210.0)
        self.assertEqual(td.terrain_resolution, "30m")
        self.assertEqual(td.provenance, "[LIVE]")

    def test_satellite_vegetation_fields(self):
        sd = SatelliteDimension(
            insar_velocity_mm_yr=-14.2,
            insar_coherence=0.78,
            acquisition_age_days=12,
            ndvi_mean=0.48,
            vegetation_loss_pct=29.4,
            source="Sentinel",
            provenance="[LIVE]",
            ndvi=0.48,
            previous_ndvi=0.68,
            ndvi_change=-0.20,
            vegetation_loss=29.4,
            vegetation_source="Sentinel-2 MSI",
            vegetation_acquisition_age=3,
            deformation_source="[SIMULATED]"
        )
        self.assertEqual(sd.ndvi, 0.48)
        self.assertEqual(sd.ndvi_change, -0.20)
        self.assertEqual(sd.vegetation_loss, 29.4)
        self.assertEqual(sd.vegetation_source, "Sentinel-2 MSI")
        self.assertEqual(sd.deformation_source, "[SIMULATED]")

    def test_history_dimension_fields(self):
        hd = HistoryDimension(
            nearby_events_count_5km=6,
            nearest_event_distance_km=0.85,
            recurrence_interval_years=4.0,
            historical_max_rainfall_24h=140.0,
            source="GSI",
            provenance="[HISTORICAL]",
            historical_events_5km=6,
            events_within_1km=2,
            nearest_historical_dist_km=0.85
        )
        self.assertEqual(hd.events_within_1km, 2)
        self.assertEqual(hd.historical_events_5km, 6)
        self.assertEqual(hd.nearest_historical_dist_km, 0.85)

    def test_anthropogenic_slope_service(self):
        service = AnthropogenicSlopeService()
        dist = service.evaluate_sector("SK-NH10-KM48")
        self.assertIsInstance(dist, dict)
        self.assertIn("anthropogenic_disturbance_score", dist)
        self.assertGreaterEqual(dist["anthropogenic_disturbance_score"], 0.0)
        self.assertLessEqual(dist["anthropogenic_disturbance_score"], 1.0)
        self.assertIn(dist["provenance"], ["[LIVE]", "[CACHED]", "[HISTORICAL]"])

    def test_build_pahad_feature_vector_geospatial_fusion(self):
        fvec_dict = build_pahad_feature_vector("SK-NH10-KM48")
        self.assertIsInstance(fvec_dict, dict)
        self.assertIn("features", fvec_dict)
        self.assertIn("sources", fvec_dict)
        self.assertIn("provenance", fvec_dict)
        self.assertIn("data_quality", fvec_dict)

        feats = fvec_dict["features"]
        self.assertIn("slope_deg", feats)
        self.assertIn("elevation_m", feats)
        self.assertIn("aspect_deg", feats)
        self.assertIn("plan_curvature", feats)
        self.assertIn("profile_curvature", feats)
        self.assertIn("ndvi", feats)
        self.assertIn("ndvi_change", feats)
        self.assertIn("historical_events_5km", feats)
        self.assertIn("events_within_1km", feats)
        self.assertIn("anthropogenic_disturbance_score", feats)

    def test_geospatial_registry_and_manifest(self):
        registry = GeospatialRegistry()
        datasets = registry.list_datasets()
        self.assertGreaterEqual(len(datasets), 5)

        manifest = registry.export_manifest()
        self.assertEqual(manifest["status"], "OPERATIONAL")
        self.assertIn("datasets", manifest)
        self.assertIn("manifest_generated_at", manifest)


if __name__ == '__main__':
    unittest.main()
