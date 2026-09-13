# -*- coding: utf-8 -*-
"""
tests/test_phase9e_forecast.py
==============================
PARVAT NETRA - PAHAD AI Phase 9E Multi-Horizon Forecast Demarcation Audit
------------------------------------------------------------------------
Validates:
  1. Strict visual and conceptual demarcation between CURRENT RISK (0-6h) and FORECAST RISK (6h-48h).
  2. Multi-horizon coverage for 6h, 12h, 24h, and 48h horizons.
  3. Structure of current_risk: cri, risk_band, fos_physical, state_description.
  4. Structure of forecast_risk: max_risk_horizon, summary, horizons dict.
"""

import os
import sys
import unittest

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from engine.pahad_live_inference import run_forecast


class TestPhase9EForecastDemarcation(unittest.TestCase):
    """Audit multi-horizon forecast structure and current vs forecast risk demarcation."""

    def test_current_and_forecast_risk_demarcation(self):
        """Forecast response must separate immediate current_risk from future forecast_risk."""
        fc = run_forecast("SK-NH10-KM48", latitude=27.33, longitude=88.61)

        # 1. Current Risk Block (0-6h immediate geotechnical state)
        self.assertIn("current_risk", fc)
        cr = fc["current_risk"]
        self.assertIn("cri", cr)
        self.assertIn("risk_band", cr)
        self.assertIn("fos_physical", cr)
        self.assertIn("state_description", cr)
        self.assertGreaterEqual(cr["cri"], 0.0)
        self.assertLessEqual(cr["cri"], 100.0)

        # 2. Forecast Risk Block (6h-48h forward projections)
        self.assertIn("forecast_risk", fc)
        fr = fc["forecast_risk"]
        self.assertIn("max_risk_horizon", fr)
        self.assertIn("summary", fr)
        self.assertIn(fr["max_risk_horizon"], ["6h", "12h", "24h", "48h"])

        # 3. Horizon probabilities
        self.assertIn("horizons", fc)
        for h in ["6h", "12h", "24h", "48h"]:
            self.assertIn(h, fc["horizons"])
            p = fc["horizons"][h]["p_event"]
            self.assertGreaterEqual(p, 0.0)
            self.assertLessEqual(p, 1.0)


if __name__ == "__main__":
    unittest.main()
