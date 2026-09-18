# -*- coding: utf-8 -*-
"""
tests/test_insar_creep.py
=========================
Validates Sentinel-1 / NISAR InSAR Ground Deformation & Creep Acceleration Engine:
1. Spatial coverage of Persistent Scatterers across all 8 North Eastern states.
2. Coordinate resolution via get_insar_for_coords.
3. Tertiary creep acceleration and Fukuzono (1985) inverse-velocity (1/v) mechanics.
4. Coherence reliability gating and anomaly factor boundaries [0.0, 1.0].
"""

import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from engine.pahad_insar import (
    PERSISTENT_SCATTERER_POINTS,
    InSARDeformationProcessor,
    INSAR_PROCESSOR,
    get_insar_for_coords,
    COHERENCE_THRESHOLD
)


class TestInSARCreep(unittest.TestCase):

    def test_01_persistent_scatterer_inventory_spans_ner(self):
        """Verify PS network covers key NER disaster corridors."""
        points = PERSISTENT_SCATTERER_POINTS
        self.assertGreaterEqual(len(points), 10)

        states = {p["state"] for p in points.values()}
        self.assertIn("Sikkim", states)
        self.assertIn("Meghalaya", states)
        self.assertIn("Mizoram", states)
        self.assertIn("Manipur", states)
        self.assertIn("Nagaland", states)
        self.assertIn("Arunachal Pradesh", states)

    def test_02_insar_coordinate_resolution(self):
        """Verify coordinate lookup resolves nearest station and returns valid result."""
        # Query near NH-10 Likhu Veer (27.28, 88.58)
        res_km48 = get_insar_for_coords(27.28, 88.58)
        self.assertIsNotNone(res_km48)
        self.assertLess(res_km48.velocity_mm_year, -15.0)  # Subsiding rapidly
        self.assertGreaterEqual(res_km48.coherence, COHERENCE_THRESHOLD)
        self.assertTrue(res_km48.coherence_reliable)
        self.assertIn("nearest_ps", res_km48.metadata)

    def test_03_fukuzono_tertiary_creep_analysis(self):
        """Verify time-series generation calculates inverse velocity 1/v."""
        processor = INSAR_PROCESSOR
        # Point 501 is Likhu Veer (Critical Acceleration)
        details = processor.get_ps_point_details(501)
        self.assertIsNotNone(details)
        self.assertEqual(details["status"], "SUCCESS")

        ts = details["timeseries"]
        self.assertEqual(ts["total_epochs"], 24)
        self.assertEqual(ts["repeat_cycle_days"], 12.0)

        # Check inverse-velocity was computed on final accelerating epochs
        final_epochs = ts["epochs"][-3:]
        for ep in final_epochs:
            self.assertIn("inverse_velocity_day_mm", ep)
            self.assertIn("incremental_velocity_mm_day", ep)
            self.assertGreater(ep["incremental_velocity_mm_day"], 0.0)

    def test_04_anomaly_factor_bounds(self):
        """Verify insar_anomaly_factor is strictly bounded in [0.0, 1.0]."""
        for pid in PERSISTENT_SCATTERER_POINTS.keys():
            details = INSAR_PROCESSOR.get_ps_point_details(pid)
            c = details["creep_analysis"]
            factor = c["insar_anomaly_factor"]
            self.assertGreaterEqual(factor, 0.0)
            self.assertLessEqual(factor, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
