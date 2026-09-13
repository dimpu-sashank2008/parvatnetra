# -*- coding: utf-8 -*-
"""
tests/test_pahad_inputs.py
==========================
Unit & Integration Tests for PAHAD Unified Input Contract & Feature Vector Synthesizer
"""

import unittest
from engine.pahad_inputs import (
    build_pahad_feature_vector,
    resolve_sector_geotech,
    PahadUnifiedInputContract,
    ClimateDimension,
    TerrainDimension,
    GroundDimension,
    SeismicDimension,
    SatelliteDimension,
    HistoryDimension,
    InfrastructureDimension,
    FieldDimension
)


class TestPahadInputs(unittest.TestCase):

    def test_geotech_lithology_resolver(self):
        # Quartzite should have higher cohesion and friction than shale
        q_props = resolve_sector_geotech("Daling quartzites and sheared fault gouge")
        s_props = resolve_sector_geotech("Fissile clay shale and siltstone")
        self.assertGreater(q_props["cohesion"], s_props["cohesion"])
        self.assertGreater(q_props["friction"], s_props["friction"])

    def test_build_pahad_feature_vector_known_sector(self):
        vector = build_pahad_feature_vector("SK-NH10-KM48")
        self.assertEqual(vector["sector_id"], "SK-NH10-KM48")
        self.assertIn("features", vector)
        self.assertIn("feature_sources", vector)
        self.assertIn("data_quality", vector)
        self.assertIn("overall_provenance", vector)
        self.assertIn("raw_contract", vector)

        features = vector["features"]
        # Required core physics features
        self.assertIn("slope_deg", features)
        self.assertIn("cohesion_kpa", features)
        self.assertIn("friction_deg", features)
        self.assertIn("rainfall_24h_mm", features)
        self.assertIn("pore_water_pressure_kpa", features)
        self.assertIn("seismic_shaking_proxy_g", features)

        # Provenance sanity check
        self.assertIsInstance(vector["overall_provenance"], list)
        self.assertGreater(len(vector["overall_provenance"]), 0)

    def test_data_quality_classification(self):
        # High-traffic known sector with live or valid simulated data
        v1 = build_pahad_feature_vector("SK-NH10-KM48")
        self.assertIn(v1["data_quality"], ["HIGH", "MEDIUM", "LOW"])

        # Unknown sector should have missing_features noted
        v_unk = build_pahad_feature_vector("UNKNOWN-SECTOR-99")
        self.assertIn("sector_metadata", v_unk["missing_features"])

    def test_unified_contract_serialization(self):
        v = build_pahad_feature_vector("SK-SINGTAM-01")
        raw = v["raw_contract"]
        self.assertIn("climate", raw)
        self.assertIn("terrain", raw)
        self.assertIn("ground", raw)
        self.assertIn("seismic", raw)
        self.assertIn("satellite", raw)
        self.assertIn("history", raw)
        self.assertIn("infrastructure", raw)
        self.assertIn("field", raw)

        # Check provenance badge inside sub-dimensions
        self.assertIn("provenance", raw["climate"])
        self.assertIn("provenance", raw["seismic"])
        self.assertIn("provenance", raw["ground"])


if __name__ == "__main__":
    unittest.main()
