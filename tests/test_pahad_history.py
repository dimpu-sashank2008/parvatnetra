"""
Unit Tests for PAHAD Historical Landslide Media & Recurrence Hotspot Engine
PARVAT NETRA Scientific Modeling Core
GSI NLFC & ISRO NRSC Landslide Atlas Baseline
"""
import unittest
import json
from engine.pahad_history import (
    HISTORICAL_LANDSLIDES_CATALOG,
    HistoricalRecurrencePredictor,
    RECURRENCE_SECTORS_DATA,
)
from app import app


class TestPAHADHistoryEngine(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.predictor = HistoricalRecurrencePredictor()

    def test_01_catalog_contains_verified_disasters(self):
        """Test that catalog contains verified disasters (Noney 2022, Remal Aizawl 2024, Mizoram 2025, NH-10, Dima Hasao, Sankalang 2025)."""
        self.assertIn("DIS-2022-NONEY", HISTORICAL_LANDSLIDES_CATALOG)
        self.assertIn("DIS-2024-AIZAWL", HISTORICAL_LANDSLIDES_CATALOG)
        self.assertIn("DIS-2025-MIZORAM", HISTORICAL_LANDSLIDES_CATALOG)
        self.assertIn("DIS-2024-NH10", HISTORICAL_LANDSLIDES_CATALOG)
        self.assertIn("DIS-2022-DIMAHASAO", HISTORICAL_LANDSLIDES_CATALOG)
        self.assertIn("DIS-2025-SIKKIM", HISTORICAL_LANDSLIDES_CATALOG)
        self.assertEqual(len(HISTORICAL_LANDSLIDES_CATALOG), 6)

        noney = HISTORICAL_LANDSLIDES_CATALOG["DIS-2022-NONEY"]
        self.assertIn("Manipur", noney["name"])
        self.assertEqual(noney["fatalities"], 58)

        remal = HISTORICAL_LANDSLIDES_CATALOG["DIS-2024-AIZAWL"]
        self.assertIn("Mizoram", remal["name"])
        self.assertGreaterEqual(remal["fatalities"], 27)

        mizoram = HISTORICAL_LANDSLIDES_CATALOG["DIS-2025-MIZORAM"]
        self.assertIn("Mizoram", mizoram["name"])
        self.assertGreaterEqual(mizoram["trigger_rainfall_mm"], 200.0)

        sikkim = HISTORICAL_LANDSLIDES_CATALOG["DIS-2025-SIKKIM"]
        self.assertIn("Sankalang", sikkim["name"])
        self.assertEqual(sikkim["state"], "Sikkim")
        self.assertEqual(sikkim["fatalities"], 6)
        self.assertEqual(sikkim["coordinates"], [27.5021, 88.5318])
        self.assertEqual(sikkim["trigger_rainfall_mm"], 175.0)

    def test_02_entries_include_valid_coordinates_mechanisms_and_media(self):
        """Test that all catalog entries include valid coordinates, failure mechanisms, and media assets."""
        for dis_id, item in HISTORICAL_LANDSLIDES_CATALOG.items():
            # Coordinates
            self.assertIn("coordinates", item)
            coords = item["coordinates"]
            self.assertEqual(len(coords), 2)
            lat, lon = coords
            self.assertTrue(20.0 <= lat <= 30.0, f"Lat {lat} out of bounds for {dis_id}")
            self.assertTrue(85.0 <= lon <= 98.0, f"Lon {lon} out of bounds for {dis_id}")

            # Failure mechanism
            self.assertIn("geological_failure", item)
            self.assertTrue(len(item["geological_failure"]) > 5)

            # Triggering rainfall
            self.assertIn("trigger_rainfall_mm", item)
            self.assertGreater(item["trigger_rainfall_mm"], 50.0)

            # Media assets
            self.assertIn("media_assets", item)
            media = item["media_assets"]
            self.assertIn("photos", media)
            self.assertGreaterEqual(len(media["photos"]), 1)
            self.assertIn("video_url", media)
            self.assertIn("aerial_briefing_summary", media)

    def test_03_recurrence_predictor_ranks_chronic_repeat_zones(self):
        """Test that recurrence predictor correctly ranks chronic repeat zones (return period <= 2.0 years)."""
        hotspots = self.predictor.get_ranked_hotspots()
        self.assertGreaterEqual(len(hotspots), 5)

        # Top 3 hotspots should be chronic repeat zones with return period <= 2.0 years
        chronic_zones = self.predictor.get_chronic_repeat_zones(max_return_period=2.0)
        self.assertEqual(len(chronic_zones), 3)

        top_zone = hotspots[0]
        self.assertEqual(top_zone["sector_id"], "SK-NH10-KM48")
        self.assertLessEqual(top_zone["return_period_years"], 1.5)
        self.assertGreaterEqual(top_zone["recurrence_score"], 0.90)

        # Sorted in ascending order of return period
        for i in range(len(hotspots) - 1):
            self.assertLessEqual(hotspots[i]["return_period_years"], hotspots[i + 1]["return_period_years"])

    def test_04_live_nowcast_correlation_computes_exceedance_ratio(self):
        """Test that live nowcast correlation correctly computes ratio against historical collapse pulse."""
        # 1. Normal below threshold
        corr_normal = self.predictor.correlate_with_live_nowcast("SK-NH10-KM48", 45.0)
        self.assertEqual(corr_normal["warning_level"], "GREEN_STABLE")
        self.assertAlmostEqual(corr_normal["exceedance_ratio"], round(45.0 / 110.0, 3), places=2)
        self.assertLess(corr_normal["percentage_of_historical"], 50.0)

        # 2. Elevated watch
        corr_watch = self.predictor.correlate_with_live_nowcast("SK-NH10-KM48", 65.0)
        self.assertEqual(corr_watch["warning_level"], "YELLOW_ELEVATED_WATCH")

        # 3. Orange pre-failure saturation (ratio >= 0.75)
        corr_orange = self.predictor.correlate_with_live_nowcast("SK-NH10-KM48", 95.0)
        self.assertEqual(corr_orange["warning_level"], "ORANGE_PRE_FAILURE_SATURATION")

        # 4. Red high collapse risk (ratio >= 1.0)
        corr_red = self.predictor.correlate_with_live_nowcast("SK-NH10-KM48", 135.0)
        self.assertEqual(corr_red["warning_level"], "RED_HIGH_COLLAPSE_RISK")
        self.assertGreater(corr_red["exceedance_ratio"], 1.0)
        self.assertGreater(corr_red["percentage_of_historical"], 100.0)

    def test_05_rest_endpoints_return_http_200_with_valid_schemas(self):
        """Test that all three new REST endpoints return HTTP 200 OK with valid schemas."""
        # 1. GET /api/pahad/history/catalog
        res_cat = self.client.get("/api/pahad/history/catalog")
        self.assertEqual(res_cat.status_code, 200)
        data_cat = res_cat.get_json()
        self.assertEqual(data_cat["status"], "SUCCESS")
        self.assertIn("catalog", data_cat)
        self.assertGreaterEqual(data_cat["total_records"], 6)
        self.assertIn("DIS-2022-NONEY", data_cat["catalog"])
        self.assertIn("DIS-2025-SIKKIM", data_cat["catalog"])

        # 2. GET /api/pahad/history/hotspots
        res_hot = self.client.get("/api/pahad/history/hotspots")
        self.assertEqual(res_hot.status_code, 200)
        data_hot = res_hot.get_json()
        self.assertEqual(data_hot["status"], "SUCCESS")
        self.assertIn("hotspots", data_hot)
        self.assertGreaterEqual(data_hot["total_hotspots"], 5)
        self.assertEqual(data_hot["hotspots"][0]["sector_id"], "SK-NH10-KM48")

        # 3. POST /api/pahad/history/correlate-nowcast
        payload = {
            "sector_id": "SK-NH10-KM48",
            "current_rainfall_mm": 125.0
        }
        res_corr = self.client.post(
            "/api/pahad/history/correlate-nowcast",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res_corr.status_code, 200)
        data_corr = res_corr.get_json()
        self.assertEqual(data_corr["status"], "SUCCESS")
        self.assertIn("correlation", data_corr)
        c = data_corr["correlation"]
        self.assertEqual(c["sector_id"], "SK-NH10-KM48")
        self.assertEqual(c["warning_level"], "RED_HIGH_COLLAPSE_RISK")
        # 4. GET /api/pahad/history/hotspots?state=Sikkim
        res_state = self.client.get("/api/pahad/history/hotspots?state=Sikkim")
        self.assertEqual(res_state.status_code, 200)
        data_state = res_state.get_json()
        self.assertEqual(data_state["status"], "SUCCESS")
        self.assertEqual(data_state["state_filter"], "Sikkim")
        for h in data_state["hotspots"]:
            self.assertEqual(h["state"], "Sikkim")

    def test_06_get_hotspot_rankings_and_correlate_live_telemetry(self):
        """Test get_hotspot_rankings and correlate_live_telemetry aliases and state filter."""
        all_rankings = self.predictor.get_hotspot_rankings()
        self.assertGreaterEqual(len(all_rankings), 5)
        for h in all_rankings:
            self.assertIn("recorded_events_count", h)
            self.assertIn("return_period_years", h)
            self.assertIn("recurrence_score", h)
            self.assertIn("threat_classification", h)

        sk_rankings = self.predictor.get_hotspot_rankings(state_filter="Sikkim")
        self.assertEqual(len(sk_rankings), 2)
        for h in sk_rankings:
            self.assertEqual(h["state"], "Sikkim")

        # Telemetry correlation alias
        corr = self.predictor.correlate_live_telemetry("SK-NH10-KM48", 125.0)
        self.assertEqual(corr["sector_id"], "SK-NH10-KM48")
        self.assertEqual(corr["warning_level"], "RED_HIGH_COLLAPSE_RISK")
        self.assertIn("threat_classification", corr)
        self.assertIn("recorded_events_count", corr)

    def test_07_historical_modal_and_trigger_dom_present(self):
        """Verify top ribbon trigger button, modal, tabs, table and GIGW 3.0 elements in index.html."""
        with open("templates/index.html", "r", encoding="utf-8") as f:
            html = f.read()

        # Trigger button
        self.assertIn('id="btn-top-history-media"', html)
        self.assertIn("openHistoricalMediaModal()", html)
        self.assertIn("bg-[#002147]", html)
        self.assertIn("GSI DISASTER ARCHIVE &amp; RECURRENCE ENGINE", html)
        self.assertIn("HISTORICAL RECURRENCE", html)

        # Modal
        self.assertIn('id="modal-historical-media"', html)
        self.assertIn('id="history-modal-title"', html)
        self.assertIn("GEOLOGICAL SURVEY OF INDIA &amp; NRSC", html)

        # Tabs
        self.assertIn('id="tab-btn-history-media"', html)
        self.assertIn('id="tab-btn-history-hotspots"', html)
        self.assertIn('id="tab-btn-history-correlate"', html)

        # Tab contents
        self.assertIn('id="history-catalog-grid"', html)
        self.assertIn('id="table-history-hotspots"', html)
        self.assertIn('id="history-hotspots-body"', html)
        self.assertIn("Corridor ID", html)
        self.assertIn("Mean Return Period", html)
        self.assertIn("Recurrence Category", html)
        self.assertIn('id="history-correlate-sector"', html)
        self.assertIn('id="history-correlate-rainfall"', html)
        self.assertIn('id="btn-run-history-correlate"', html)
        self.assertIn('id="history-correlate-result"', html)

        # Client-side JavaScript functions
        self.assertIn("openHistoricalMediaModal", html)
        self.assertIn("closeHistoricalMediaModal", html)
        self.assertIn("switchHistoryTab", html)
        self.assertIn("renderHistoricalCatalog", html)
        self.assertIn("renderHistoricalHotspots", html)
        self.assertIn("plotHotspotOnMap", html)
        self.assertIn("runHistoricalNowcastCorrelation", html)
        self.assertIn("ARCHIVE COUNT: 6 VERIFIED DISASTERS", html)

    def test_08_verify_zero_emojis_in_templates_and_modal(self):
        """Strict GIGW 3.0 Compliance: Assert ZERO unicode emojis across templates/index.html and engine/pahad_history.py."""
        import re
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # geometric shapes extended
            "\U0001F800-\U0001F8FF"  # supplemental arrows-C
            "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
            "\U0001FA00-\U0001FA6F"  # chess symbols
            "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
            "\U00002702-\U000027B0"  # dingbats
            "\U0001F1E6-\U0001F1FF"  # flags (regional indicator symbols)
            "\U0001F200-\U0001F251]"  # enclosed ideographic supplement
        )
        with open("templates/index.html", "r", encoding="utf-8") as f:
            html = f.read()
        html_emojis = emoji_pattern.findall(html)
        self.assertEqual(len(html_emojis), 0, f"Found emojis in templates/index.html: {html_emojis[:10]}")

        with open("engine/pahad_history.py", "r", encoding="utf-8") as f:
            engine_code = f.read()
        engine_emojis = emoji_pattern.findall(engine_code)
        self.assertEqual(len(engine_emojis), 0, f"Found emojis in engine/pahad_history.py: {engine_emojis[:10]}")


if __name__ == "__main__":
    unittest.main()
