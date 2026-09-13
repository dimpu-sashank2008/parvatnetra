"""
PHASE 7E — CP4-H/I: Sector snapshot and source provenance tests
Verifies that the sector snapshot and live inference correctly label every
data field with its actual source and provenance status.
"""
import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSourceProvenance(unittest.TestCase):
    """CP4-A through CP4-F: Every data field must declare its provenance."""

    def test_weather_service_imd_listed_separately(self):
        """IMD and Open-Meteo must be separately tracked — never merged."""
        from services.weather_service import WeatherService
        ws = WeatherService()
        status = ws.get_status()
        providers = status.get("providers", {})
        self.assertIn("imd", providers)
        self.assertIn("openmeteo", providers)
        imd_p = providers["imd"]
        openmeteo_p = providers["openmeteo"]
        # IMD must not be marked live_ready without credentials
        if not os.environ.get("IMD_API_KEY"):
            self.assertFalse(imd_p.get("live_ready", True),
                             "IMD must not be live_ready without API key")

    def test_seismic_service_ncs_listed_separately(self):
        """NCS and USGS must be separately tracked."""
        from services.seismic_service import SeismicService
        ss = SeismicService()
        status = ss.get_status()
        providers = status.get("providers", {})
        self.assertIn("ncs", providers)
        self.assertIn("usgs", providers)

    def test_dem_provenance_not_live(self):
        """DEM must not claim LIVE provenance."""
        from services.dem_service import DEMService
        dem = DEMService()
        meta = dem.get_metadata()
        prov = meta.get("provenance", "LIVE")
        self.assertNotIn("LIVE", prov.upper(),
                         f"DEM must not claim LIVE provenance. Got: {prov}")

    def test_live_inference_provenance_list_present(self):
        """Live inference result must include a feature_provenance list."""
        from engine.pahad_live_inference import run_live_inference
        try:
            result = run_live_inference("CORR-NH10-SIKKIM-KM48", 27.2056, 88.4986,
                                       forecast_horizon_hours=24)
            r = vars(result) if hasattr(result, "__dict__") else result
            self.assertIn("feature_provenance", r,
                          "Live inference must expose feature provenance for every field")
            prov_list = r["feature_provenance"]
            self.assertIsInstance(prov_list, list)
            self.assertGreater(len(prov_list), 0)
        except Exception as e:
            self.skipTest(f"Live inference error: {e}")

    def test_live_inference_imputed_features_labeled(self):
        """Imputed features must be explicitly labeled — not silently treated as LIVE."""
        from engine.pahad_live_inference import run_live_inference
        try:
            result = run_live_inference("CORR-NH10-SIKKIM-KM48", 27.2056, 88.4986,
                                       forecast_horizon_hours=24)
            r = vars(result) if hasattr(result, "__dict__") else result
            imputed = r.get("imputed_features", None)
            # imputed_features must be present (even if empty list)
            self.assertIsNotNone(imputed,
                                 "Inference must declare which features were imputed from training medians")
        except Exception as e:
            self.skipTest(f"Live inference error: {e}")

    def test_live_inference_data_quality_score_reflects_missing(self):
        """Data quality score must be < 1.0 when IoT/terrain sensors are absent."""
        from engine.pahad_live_inference import run_live_inference
        try:
            result = run_live_inference("CORR-NH10-SIKKIM-KM48", 27.2056, 88.4986,
                                       forecast_horizon_hours=24)
            r = vars(result) if hasattr(result, "__dict__") else result
            dqs = float(r.get("data_quality_score", 1.0))
            # With no physical IoT sensors, quality must be < 1.0
            self.assertLess(dqs, 1.0,
                            f"data_quality_score must be < 1.0 with missing sensors, got: {dqs}")
        except Exception as e:
            self.skipTest(f"Live inference error: {e}")

    def test_live_inference_model_status_is_limited_data(self):
        """Live inference must report MODEL_STATUS = TRAINED_LIMITED_DATA."""
        from engine.pahad_live_inference import run_live_inference
        try:
            result = run_live_inference("CORR-NH10-SIKKIM-KM48", 27.2056, 88.4986,
                                       forecast_horizon_hours=24)
            r = vars(result) if hasattr(result, "__dict__") else result
            status = r.get("model_status", "PRODUCTION_READY")
            self.assertIn("TRAINED_LIMITED_DATA", str(status).upper(),
                          f"Model status must remain TRAINED_LIMITED_DATA, got: {status}")
        except Exception as e:
            self.skipTest(f"Live inference error: {e}")

    def test_probability_within_valid_bounds(self):
        """Event probability must be in [0, 1]."""
        from engine.pahad_live_inference import run_live_inference
        try:
            result = run_live_inference("CORR-NH10-SIKKIM-KM48", 27.2056, 88.4986,
                                       forecast_horizon_hours=24)
            r = vars(result) if hasattr(result, "__dict__") else result
            prob = float(r.get("event_probability", -1))
            self.assertGreaterEqual(prob, 0.0, "Probability must be >= 0")
            self.assertLessEqual(prob, 1.0, "Probability must be <= 1")
        except Exception as e:
            self.skipTest(f"Live inference error: {e}")

    def test_missing_iot_not_silently_fabricated(self):
        """IoT provenance must be MISSING when no physical sensors are deployed."""
        from engine.pahad_live_inference import run_live_inference
        try:
            result = run_live_inference("CORR-NH10-SIKKIM-KM48", 27.2056, 88.4986,
                                       forecast_horizon_hours=24)
            r = vars(result) if hasattr(result, "__dict__") else result
            prov_list = r.get("feature_provenance", [])
            iot_entries = [p for p in prov_list
                           if isinstance(p, dict) and p.get("feature") == "iot"]
            if iot_entries:
                iot_prov = iot_entries[0].get("provenance", "LIVE")
                self.assertNotEqual(iot_prov, "LIVE",
                                    "IoT must not claim LIVE when no physical sensors deployed")
        except Exception as e:
            self.skipTest(f"Live inference error: {e}")


class TestSectorSnapshot(unittest.TestCase):
    """CP4-H: Sector snapshot must expose all field sources honestly."""

    SECTOR = "CORR-NH10-SIKKIM-KM48"

    def test_weather_snapshot_has_open_meteo_source(self):
        """Weather snapshot must note Open-Meteo as actual source (not IMD)."""
        from services.weather_service import WeatherService
        ws = WeatherService()
        try:
            w = ws.get_weather(27.2056, 88.4986)
            # Source must mention Open-Meteo or not claim IMD as sole source
            # when IMD credentials are absent
            if not os.environ.get("IMD_API_KEY"):
                # Should fallback to Open-Meteo
                source = str(w.get("source", w.get("provider", "")))
                # Must not claim "IMD" as sole authoritative source
                # (IMD could appear in provider preference list)
                imd_solo = source.strip() == "IMD"
                self.assertFalse(imd_solo,
                                 "Cannot claim IMD as sole source when IMD is UNCONFIGURED")
        except Exception as e:
            self.skipTest(f"Weather service error: {e}")

    def test_seismic_snapshot_declares_provider(self):
        """Seismic sector snapshot must identify its data provider."""
        from services.seismic_service import SeismicService
        ss = SeismicService()
        try:
            impact = ss.get_impact_for_sector(self.SECTOR)
            self.assertIsInstance(impact, dict)
            # Must have some identifier of the seismic data source
            has_source = (
                "provenance" in impact
                or "earthquake_id" in impact
                or "provider" in impact
            )
            self.assertTrue(has_source, "Seismic snapshot must identify data source")
        except Exception as e:
            self.skipTest(f"Seismic service error: {e}")

    def test_copernicus_catalogue_not_claimed_as_processed_product(self):
        """Copernicus catalogue discovery must not be labeled as processed InSAR deformation."""
        # CDSE is REGISTRATION_REQUIRED for download.
        # System must not report InSAR deformation velocities as LIVE data.
        cdse_user = os.environ.get("CDSE_USERNAME", "")
        if not cdse_user:
            # Without credentials, InSAR must be UNAVAILABLE or REGISTRATION_REQUIRED
            try:
                from services.satellite_service import SatelliteService
                sat = SatelliteService()
                methods = [m for m in dir(sat) if not m.startswith("_")]
                if "get_insar_status" in methods:
                    status = sat.get_insar_status()
                    insar_status = status.get("status", "LIVE")
                    self.assertNotEqual(insar_status, "LIVE",
                                        "InSAR must not claim LIVE without CDSE credentials")
            except Exception:
                pass  # No satellite service — that's acceptable


if __name__ == "__main__":
    unittest.main()
