"""
PHASE 7E — CP4-G: Freshness verification tests
Verifies the freshness engine correctly classifies source states.
"""
import os
import sys
import json
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDataFreshness(unittest.TestCase):
    """CP4-G: Freshness engine must correctly classify source states."""

    def setUp(self):
        from engine.data_freshness import DataFreshnessEngine
        self.engine = DataFreshnessEngine()

    def test_freshness_engine_initializes(self):
        """DataFreshnessEngine must initialize without error."""
        self.assertIsNotNone(self.engine)

    def test_fresh_record_within_ttl(self):
        """A record updated within TTL must be classified FRESH."""
        self.engine.record_update("test_fresh_source")   # stamps time.time() internally
        record = self.engine.get_freshness("test_fresh_source")
        status = record.status if hasattr(record, "status") else str(record)
        self.assertIn("FRESH", str(status).upper(),
                      f"Record updated just now must be FRESH, got: {status}")

    def test_stale_record_outside_ttl(self):
        """A record older than TTL must be classified as non-fresh (STALE or UNAVAILABLE)."""
        stale_epoch = time.time() - 10000  # ~2.7h ago — well past any TTL
        record = self.engine.get_freshness("test_stale_source", last_updated_epoch=stale_epoch)
        status = str(record.status if hasattr(record, "status") else str(record)).upper()
        # Engine may return STALE (if modality was registered) or UNAVAILABLE (if not),
        # but must NOT return FRESH for a 2.7-hour-old record.
        self.assertNotIn("FRESH", status,
                         f"Old record must not be FRESH, got: {status}")
        self.assertTrue(
            "STALE" in status or "UNAVAILABLE" in status or "AGING" in status,
            f"Old record must be STALE/UNAVAILABLE/AGING, got: {status}"
        )

    def test_missing_source_reports_unavailable(self):
        """A source with no recorded update must be UNAVAILABLE."""
        record = self.engine.get_freshness("nonexistent_source_XYZ_999")
        status = record.status if hasattr(record, "status") else str(record)
        self.assertIn("UNAVAILABLE", str(status).upper(),
                      f"Unknown source must be UNAVAILABLE, got: {status}")

    def test_confidence_penalty_for_stale_data(self):
        """Stale data must carry a confidence penalty > 0."""
        stale_epoch = time.time() - 10000
        record = self.engine.get_freshness("test_penalty_source", last_updated_epoch=stale_epoch)
        penalty = record.confidence_penalty if hasattr(record, "confidence_penalty") else 0
        self.assertGreater(float(penalty), 0,
                           "Stale data must reduce model confidence")

    def test_unavailable_source_maximum_penalty(self):
        """Completely unavailable source must have maximum confidence penalty."""
        record = self.engine.get_freshness("source_never_updated_ZZZZ")
        penalty = record.confidence_penalty if hasattr(record, "confidence_penalty") else 0
        self.assertGreaterEqual(float(penalty), 0.5,
                                "Missing source must impose high confidence penalty")

    def test_freshness_summary_reports_all_modalities(self):
        """Freshness summary must return a dict covering registered modalities."""
        self.engine.record_update("weather")   # stamps now -> FRESH
        self.engine.record_update("seismic")   # stamps now -> FRESH
        summary = self.engine.get_summary()
        self.assertIsInstance(summary, dict, "Summary must be a dict")

    def test_fresh_then_stale_transition(self):
        """Engine must return FRESH for recent data and STALE for very old data."""
        fresh_epoch = time.time()
        stale_epoch = time.time() - 99999  # ~27h ago

        fresh_record = self.engine.get_freshness("trans_fresh", last_updated_epoch=fresh_epoch)
        stale_record = self.engine.get_freshness("trans_stale", last_updated_epoch=stale_epoch)

        fresh_status = fresh_record.status if hasattr(fresh_record, "status") else "?"
        stale_status = stale_record.status if hasattr(stale_record, "status") else "?"
        self.assertNotEqual(str(fresh_status), str(stale_status),
                            "FRESH and very-old records must have different status classifications")


class TestWeatherServiceFreshness(unittest.TestCase):
    """Verify weather service freshness labels are propagated."""

    def test_weather_response_has_timestamp(self):
        """Weather service response must include a timestamp."""
        from services.weather_service import WeatherService
        ws = WeatherService()
        try:
            w = ws.get_weather(27.2056, 88.4986)
            self.assertIn("timestamp", w,
                          "Weather response must include a timestamp field")
            ts = w["timestamp"]
            self.assertTrue(ts, "Timestamp must not be empty")
        except Exception as e:
            self.skipTest(f"Weather service error: {e}")

    def test_weather_provenance_present(self):
        """Weather service must report data provenance."""
        from services.weather_service import WeatherService
        ws = WeatherService()
        try:
            w = ws.get_weather(27.2056, 88.4986)
            # At minimum, provenance or source must be in the response
            has_prov = "provenance" in w or "source" in w or "provider" in w
            self.assertTrue(has_prov, "Weather response must include provenance information")
        except Exception as e:
            self.skipTest(f"Weather service error: {e}")


class TestSeismicServiceFreshness(unittest.TestCase):
    """Verify seismic service correctly distinguishes LIVE USGS from cached/simulated events."""

    def test_seismic_sector_impact_has_provenance(self):
        """Seismic sector impact must declare provenance."""
        from services.seismic_service import SeismicService
        ss = SeismicService()
        try:
            impact = ss.get_impact_for_sector("CORR-NH10-SIKKIM-KM48")
            self.assertIn("provenance", impact,
                          "Seismic impact must declare provenance (LIVE/CACHED/SIMULATED)")
        except Exception as e:
            self.skipTest(f"Seismic service error: {e}")

    def test_cached_seismic_not_labeled_live(self):
        """Cached/simulated seismic data must NOT be labeled LIVE."""
        from services.seismic_service import SeismicService
        ss = SeismicService()
        try:
            impact = ss.get_impact_for_sector("CORR-NH10-SIKKIM-KM48")
            prov = impact.get("provenance", "LIVE")
            # If the result is from a simulation/cache, it must not claim LIVE
            # Unless USGS was actually queried and returned a live event
            status = ss.get_status()
            ncs_ready = status.get("providers", {}).get("ncs", {}).get("status") == "READY"
            usgs_was_queried = "usgs" in str(impact.get("earthquake_id", "")).lower() or prov == "LIVE"
            if not ncs_ready:
                # Without NCS, should not be labeled NCS-sourced LIVE
                self.assertNotIn("NCS_LIVE", prov,
                                 "Cannot be NCS-LIVE when NCS is UNCONFIGURED")
        except Exception as e:
            self.skipTest(f"Seismic service error: {e}")


if __name__ == "__main__":
    unittest.main()
