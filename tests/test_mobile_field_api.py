# tests/test_mobile_field_api.py
# ==============================
# PARVAT NETRA • Phase 5E Flutter Mobile Client Backend API Contract Test Suite
# Verifies all endpoints consumed by parvat_netra_mobile:
# 1. /api/pahad/live-inference
# 2. /api/pahad/forecast
# 3. /api/pahad/data-status
# 4. /api/pahad/observations/latest
# 5. /api/sync/push
# 6. /api/sync/pull
# 7. /api/sync/status
# 8. /api/reports/verify
# 9. /api/routing/evacuation-plan

import os
import sys
import unittest
import json

# Ensure testing environment isolation
os.environ["PARVAT_TESTING"] = "1"
os.environ["PAHAD_DEMO_MODE"] = "1"
os.environ["DRY_RUN"] = "true"

# Add silly-fermi root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app


class TestMobileFieldApiContracts(unittest.TestCase):
    """Verifies that backend APIs strictly conform to Flutter mobile client contracts."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_01_live_inference_contract_for_mobile_home(self):
        """Flutter MobileHomeScreen consumes /api/pahad/live-inference for current location risk."""
        payload = {
            "sector_id": "SK-NH10-KM48",
            "latitude": 27.33,
            "longitude": 88.61,
            "horizon_hours": 24
        }
        res = self.client.post("/api/pahad/live-inference", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        
        inf = data.get("inference", {})
        # Verify mandatory mobile home attributes
        self.assertTrue("composite_risk_score" in inf or "cri" in inf)
        self.assertTrue("alert_band" in inf or "risk_band" in inf)
        self.assertTrue("factor_of_safety" in inf or "fos_physical" in inf or "fos" in inf)
        self.assertIn("event_probability", inf)
        self.assertIn("confidence", inf)
        self.assertIn("top_drivers", inf)
        self.assertTrue("provenance" in inf or "feature_provenance" in inf or "demo_mode" in inf)
        self.assertIn("model_version", inf)

        # Invariant checks: FoS > 0, Probability in [0, 1]
        fos_val = float(inf.get("factor_of_safety") or inf.get("fos_physical") or inf.get("fos", 1.0))
        self.assertGreater(fos_val, 0.0)
        self.assertGreaterEqual(float(inf["event_probability"]), 0.0)
        self.assertLessEqual(float(inf["event_probability"]), 1.0)

    def test_02_forecast_multi_horizon_contract_for_mobile(self):
        """Flutter ForecastScreen consumes /api/pahad/forecast for 6h, 12h, 24h, 48h."""
        res = self.client.post("/api/pahad/forecast", json={
            "sector_id": "SK-NH10-KM48",
            "latitude": 27.33,
            "longitude": 88.61,
            "horizons": "6,12,24,48"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        
        fc = data.get("forecast", {})
        self.assertIn("horizons", fc)
        horizons = fc["horizons"]
        
        for h in ["6", "12", "24", "48"]:
            h_key = f"{h}h" if f"{h}h" in horizons else h
            self.assertIn(h_key, horizons)
            h_obj = horizons[h_key]
            self.assertIn("event_probability", h_obj)
            self.assertIn("confidence", h_obj)
            self.assertIn("model_version", h_obj)

        # Scientific limitation statement must be present
        limitation_text = fc.get("model_limitation") or fc.get("limitation") or ""
        self.assertTrue(len(limitation_text) > 0)
        model_st = fc.get("model_status") or fc.get("horizons", {}).get("24h", {}).get("model_status") or data.get("model_status")
        self.assertIn(model_st, ["TRAINED_LIMITED_DATA", "VALIDATED_RESEARCH_PROTOTYPE"])

    def test_03_data_status_contract_for_mobile(self):
        """Flutter DataStatusScreen consumes /api/pahad/data-status."""
        res = self.client.get("/api/pahad/data-status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        
        self.assertIn("status", data)
        streams = data.get("data_streams") or data.get("streams") or {}
        
        # Verify all required modalities exist
        self.assertIn("weather", streams)
        self.assertIn("seismic", streams)
        self.assertTrue("provenance_summary" in data or "data_provenance_note" in data)

    def test_04_observations_latest_contract(self):
        """Flutter client queries /api/pahad/observations/latest for persistent telemetry."""
        res = self.client.get("/api/pahad/observations/latest?sector_id=SK-NH10-KM48&max_age=3600")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertIn("observations", data)

    def test_05_sync_push_and_idempotency_from_mobile(self):
        """Flutter SyncService pushes queued reports from SQLite to /api/sync/push."""
        local_id = f"PN-TEST-MOB-{os.getpid()}"
        report_payload = {
            "local_id": local_id,
            "created_at": "2026-09-10T06:30:00Z",
            "updated_at": "2026-09-10T06:30:00Z",
            "lat": 27.2410,
            "lon": 88.5140,
            "latitude": 27.2410,
            "longitude": 88.5140,
            "hazard_type": "TENSION_CRACK",
            "severity": "SEVERE",
            "description": "Continuous tension crack across NH-10 road shoulder.",
            "photo_paths": ["/data/user/0/app/cache/crack1.jpg"],
            "reporter_role": "FIELD_OPERATOR"
        }
        
        # First Push
        res1 = self.client.post("/api/sync/push", json={"reports": [report_payload]})
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertEqual(data1.get("status"), "SUCCESS")
        self.assertEqual(data1.get("records_uploaded"), 1)
        acks1 = data1.get("acknowledgements", [])
        self.assertEqual(len(acks1), 1)
        self.assertEqual(acks1[0]["local_id"], local_id)
        self.assertIn(acks1[0]["status"], ["SYNCED", "SUCCESS"])

        # Duplicate Idempotent Push
        res2 = self.client.post("/api/sync/push", json={"reports": [report_payload]})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        acks2 = data2.get("acknowledgements", [])
        self.assertEqual(len(acks2), 1)
        self.assertIn(acks2[0]["status"], ["SYNCED", "DUPLICATE", "SUCCESS"])

    def test_06_sync_pull_authoritative_state(self):
        """Flutter SyncService pulls authoritative alerts and critical sectors upon reconnect."""
        res = self.client.get("/api/sync/pull?sector_id=SK-NH10-KM48")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertTrue("alerts" in data or "active_alerts" in data)
        self.assertTrue("critical_sectors" in data or "critical_snapshots" in data)
        self.assertTrue("road_blockages" in data or "road_corridors" in data)
        self.assertIn("shelters", data)

    def test_07_sync_status_metric(self):
        """Flutter SyncService verifies /api/sync/status."""
        res = self.client.get("/api/sync/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("status", data)
        self.assertIn("offline_bundle_version", data)

    def test_08_reports_verify_by_authority(self):
        """Flutter IncidentVerificationScreen calls /api/reports/verify."""
        # 1. Valid Verification
        payload = {
            "report_id": 9999,
            "status": "CONFIRMED",
            "operator": "Sub-Inspector Dorjee Lepcha",
            "operator_role": "FIELD_OPERATOR",
            "notes": "Field inspected at 29th Mile. Confirmed 18mm aperture crack on shoulder.",
            "location": {"latitude": 27.2410, "longitude": 88.5140}
        }
        res = self.client.post("/api/reports/verify", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertEqual(data.get("verification_status"), "CONFIRMED")
        self.assertTrue(data.get("preserved_citizen_evidence"))

        # 2. Rejection Action
        payload_reject = {
            "report_id": 9999,
            "status": "REJECTED",
            "operator": "SDMA Controller",
            "notes": "Spurious report; normal surface weathering."
        }
        res_rej = self.client.post("/api/reports/verify", json=payload_reject)
        self.assertEqual(res_rej.status_code, 200)
        data_rej = res_rej.get_json()
        self.assertEqual(data_rej.get("verification_status"), "REJECTED")

        # 3. Invalid Status Rejection
        bad_payload = {"report_id": 9999, "status": "INVALID_STATE"}
        res_bad = self.client.post("/api/reports/verify", json=bad_payload)
        self.assertEqual(res_bad.status_code, 422)

    def test_09_routing_evacuation_plan_contract(self):
        """Flutter SafetyRoutingScreen calls /api/routing/evacuation-plan."""
        res = self.client.get("/api/routing/evacuation-plan?gvw_class=LIGHT_UTILITY")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue("primary_corridor" in data or "primary_road" in data)
        self.assertTrue("recommended_route" in data or "recommended_detour" in data)

        # Also verify offline routing plan endpoint used when network is partitioned
        res_off = self.client.post("/api/routing/offline-plan", json={"origin_lat": 27.33, "origin_lon": 88.61})
        self.assertEqual(res_off.status_code, 200)
        data_off = res_off.get_json()
        self.assertTrue("recommended_route" in data_off or "bypass_recommendation" in data_off)
        self.assertEqual(data_off.get("provenance"), "[OFFLINE ROUTE]")


if __name__ == "__main__":
    unittest.main()
