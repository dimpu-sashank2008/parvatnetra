# -*- coding: utf-8 -*-
"""
tests/test_radar_nowcasting.py
==============================
Validates IMD Doppler Weather Radar (DWR) Nowcasting & NWP Forecast Horizons:
1. Marshall-Palmer Z-R conversion mechanics across stratiform and convective regimes.
2. Geospatial resolution of nearest DWR station across North Eastern Region (NER).
3. Monotonicity and consistency of forward-looking rainfall horizons (1h, 3h, 6h, 12h, 24h, 48h).
4. Cloudburst detection threshold and data provenance integrity.
"""

import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from services.imd_radar_service import (
    dbz_to_rainfall_rate,
    get_nearest_dwr_station,
    IMDRadarNowcastService,
    IMD_RADAR_SERVICE
)


class TestRadarNowcasting(unittest.TestCase):

    def test_01_marshall_palmer_conversion(self):
        """Test Z-R conversion from radar reflectivity factor dBZ to mm/h."""
        # 0 dBZ or negative gives 0.0 mm/h
        self.assertEqual(dbz_to_rainfall_rate(0.0), 0.0)
        self.assertEqual(dbz_to_rainfall_rate(-5.0), 0.0)

        # 30 dBZ in stratiform regime (moderate rain)
        rate_30 = dbz_to_rainfall_rate(30.0, regime="stratiform")
        self.assertGreater(rate_30, 2.0)
        self.assertLess(rate_30, 4.0)

        # 45 dBZ in convective regime (heavy cloudburst rain)
        rate_45 = dbz_to_rainfall_rate(45.0, regime="convective")
        self.assertGreater(rate_45, 20.0)
        self.assertLess(rate_45, 50.0)

    def test_02_nearest_dwr_station_resolution(self):
        """Test nearest DWR station haversine spatial resolution."""
        # Near Gangtok (27.33, 88.61) -> DWR-GANGTOK
        st_id, st_info, dist = get_nearest_dwr_station(27.33, 88.61)
        self.assertEqual(st_id, "DWR-GANGTOK")
        self.assertLess(dist, 10.0)

        # Near Shillong (25.57, 91.88) -> DWR-CHERRAPUNJI
        st_id_shillong, _, dist_sh = get_nearest_dwr_station(25.57, 91.88)
        self.assertEqual(st_id_shillong, "DWR-CHERRAPUNJI")
        self.assertLess(dist_sh, 50.0)

    def test_03_radar_nowcast_horizons_monotonic(self):
        """Test forward-looking forecast horizons are cumulative and non-decreasing."""
        service = IMD_RADAR_SERVICE
        res = service.get_radar_nowcast(27.33, 88.61, sector_id="SK-NH10-KM48", base_rainfall_24h=85.0)

        self.assertIsNotNone(res)
        self.assertEqual(res.station_id, "DWR-GANGTOK")
        self.assertGreater(res.reflectivity_dbz, 20.0)
        self.assertGreater(res.instantaneous_rain_rate_mmh, 0.0)

        # Cumulative horizons must be monotonically non-decreasing
        self.assertLessEqual(res.nowcast_1h_mm, res.nowcast_3h_mm)
        self.assertLessEqual(res.nowcast_3h_mm, res.nowcast_6h_mm)
        self.assertLessEqual(res.nowcast_6h_mm, res.forecast_12h_mm)
        self.assertLessEqual(res.forecast_12h_mm, res.forecast_24h_mm)
        self.assertLessEqual(res.forecast_24h_mm, res.forecast_48h_mm)

        # Provenance must be explicit
        self.assertTrue(res.provenance.startswith("[") and res.provenance.endswith("]"))

    def test_04_cloudburst_risk_detection(self):
        """Verify extreme reflectivity (>48 dBZ) triggers cloudburst warning flag."""
        service = IMD_RADAR_SERVICE
        # Simulate extreme deluge (base rainfall > 220 mm)
        res_deluge = service.get_radar_nowcast(27.50, 88.53, base_rainfall_24h=240.0)
        self.assertTrue(res_deluge.cloudburst_risk)
        self.assertGreaterEqual(res_deluge.reflectivity_dbz, 48.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
