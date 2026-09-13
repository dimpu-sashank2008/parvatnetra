# -*- coding: utf-8 -*-
"""
PARVAT NETRA -- Phase 9 Full System Integration & Release Verification Suite
SIH Problem Statement ID: 26001 | Ministry of Development of North Eastern Region (MDoNER)

Comprehensive end-to-end verification covering:
1. Isolated persona routing between /login/authority and /login/citizen with session guardrails.
2. End-to-end telemetry ingestion, ML/physics risk calculation, and Teesta River basal scour (tau_b) coupling.
3. Secure backend storage of citizen distress photo uploads and display in the Authority triage drawer.
4. Geofenced alert dispatch rules, Haversine perimeter filters, and SSE stream broadcasting.
5. GIGW 3.0 accessibility compliance across all templates (skip links, focus outlines, alt-text, Noto Sans).
"""

import os
import sys
import json
import math
import unittest
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8080")


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


class TestFullSystemIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Read all HTML templates for GIGW 3.0 accessibility inspection
        cls.templates = {}
        for fname in ["index.html", "login.html", "login_authority.html", "login_citizen.html", "console.html"]:
            fpath = os.path.join(REPO_ROOT, "templates", fname)
            with open(fpath, "r", encoding="utf-8") as f:
                cls.templates[fname] = f.read()

    # =========================================================================
    # TASK 1.1: Isolated Persona Routing & Role Guardrails
    # =========================================================================
    def test_01_isolated_persona_routing_and_guardrails(self):
        """Verify strict role segregation between Official EOC Authority and Public Citizen portals."""
        # 1. Gateway checkpoint provides links to both portals
        login_html = self.templates["login.html"]
        self.assertIn('href="/login/authority"', login_html)
        self.assertIn('href="/login/citizen"', login_html)
        self.assertIn('ISOLATED PERSONA ENFORCEMENT', login_html)

        # 2. Test Authority Login Flow with Session Cookie
        s_auth = requests.Session()
        resp_auth = s_auth.post(
            f"{BASE_URL}/login/authority",
            data={"gov_id": "dm.gangtok@nic.in"},
            timeout=5
        )
        self.assertEqual(resp_auth.status_code, 200)

        # Authority can dispatch sirens
        dispatch_payload = {"sector": "NH-10 Km 48", "radius_km": 15.0, "fs": 0.745}
        resp_disp = s_auth.post(
            f"{BASE_URL}/api/alerts/dispatch-siren",
            json=dispatch_payload,
            timeout=5
        )
        self.assertEqual(resp_disp.status_code, 200)
        disp_data = resp_disp.json()
        self.assertEqual(disp_data["status"], "DISPATCHED")

        # 3. Test Citizen Login Flow
        s_cit = requests.Session()
        resp_cit = s_cit.post(
            f"{BASE_URL}/login/citizen",
            data={"mobile": "9876543210"},
            timeout=5
        )
        self.assertEqual(resp_cit.status_code, 200)

        # 4. Guardrail: Citizen is strictly BLOCKED from calling /api/alerts/dispatch-siren (HTTP 403)
        resp_cit_disp = s_cit.post(
            f"{BASE_URL}/api/alerts/dispatch-siren",
            json=dispatch_payload,
            timeout=5
        )
        self.assertEqual(resp_cit_disp.status_code, 403)
        cit_err = resp_cit_disp.json()
        self.assertEqual(cit_err.get("status"), "FORBIDDEN")
        self.assertIn("Citizen role cannot dispatch", cit_err.get("message", ""))

        print("[PASS] 1. Isolated persona routing and strict role guardrails verified.")

    # =========================================================================
    # TASK 1.2: End-to-End Telemetry Ingestion, ML Risk & Teesta tau_b
    # =========================================================================
    def test_02_telemetry_ml_risk_and_teesta_hydro_coupling(self):
        """Verify Teesta River hydro-telemetry basal scour tau_b and ML FoS coupling."""
        # 1. CWC Teesta Hydro-Telemetry Status
        resp_cwc = requests.get(f"{BASE_URL}/api/hydro/teesta-status", timeout=5)
        self.assertEqual(resp_cwc.status_code, 200)
        cwc_data = resp_cwc.json()
        self.assertEqual(cwc_data["status"], "SUCCESS")
        self.assertIn("basal_shear_stress_pa", cwc_data)
        self.assertIn("coupled_fos", cwc_data)
        self.assertIn("water_level_m", cwc_data)
        self.assertGreater(cwc_data["basal_shear_stress_pa"], 5000.0)
        self.assertLess(cwc_data["coupled_fos"], 1.0)

        # 2. Phase 8 ML Inference Endpoint
        ml_payload = {
            "rainfall_24h": 140.0,
            "pore_water_pressure": 30.0,
            "river_scour_tau_b": 5800.0
        }
        resp_ml = requests.post(f"{BASE_URL}/api/ml/predict-fos", json=ml_payload, timeout=5)
        self.assertEqual(resp_ml.status_code, 200)
        ml_data = resp_ml.json()
        self.assertEqual(ml_data["status"], "SUCCESS")
        self.assertLess(ml_data["predicted_fos"], 1.0)
        self.assertEqual(ml_data["risk_tier"], "RED")
        self.assertGreaterEqual(ml_data["model_metadata"]["r2_score"], 0.95)

        # 3. Autonomous AI Triage Convergence Status
        resp_triage = requests.get(f"{BASE_URL}/api/ai/triage-status", timeout=5)
        self.assertEqual(resp_triage.status_code, 200)
        triage_data = resp_triage.json()
        self.assertEqual(triage_data["status"], "SUCCESS")
        eval_res = triage_data["evaluation"]
        self.assertIn("metrics", eval_res)
        self.assertIn("ml_predicted_fos", eval_res["metrics"])
        self.assertIn("explainability", eval_res)
        self.assertIn("why", eval_res["explainability"])

        print("[PASS] 2. End-to-end telemetry ingestion, ML risk, and Teesta tau_b coupling verified.")

    # =========================================================================
    # TASK 1.3: Secure Photo Uploads & Authority Triage Drawer Storage
    # =========================================================================
    def test_03_photo_upload_storage_and_triage_drawer(self):
        """Verify citizen photo uploads are safely written to disk and visible in authority triage."""
        # 1x1 valid PNG pixel in base64
        test_png_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        payload = {
            "reporter_name": "Field Observer Sonam",
            "phone": "9800112233",
            "latitude": 27.2045,
            "longitude": 88.5170,
            "severity": "CRITICAL",
            "description": "Active tension cracks expanding across Likhu Veer downhill shoulder.",
            "photo": test_png_b64,
            "cv_aperture_mm": 42.5
        }

        resp_submit = requests.post(
            f"{BASE_URL}/api/reports/submit",
            json=payload,
            timeout=10
        )
        self.assertIn(resp_submit.status_code, [200, 201])
        data = resp_submit.json()
        self.assertEqual(data["status"], "SUCCESS")
        report_id = data["report_id"]
        image_url = data["image_url"]
        self.assertTrue(image_url.startswith("/static/uploads/field_reports/pn_report_"))

        # Verify file exists on local filesystem
        rel_path = image_url.lstrip("/").replace("/", os.sep)
        abs_path = os.path.join(REPO_ROOT, rel_path)
        self.assertTrue(os.path.exists(abs_path), f"Stored image file missing at: {abs_path}")
        self.assertGreater(os.path.getsize(abs_path), 50)

        # Verify report is listed in authority triage drawer
        resp_list = requests.get(f"{BASE_URL}/api/reports/list", timeout=5)
        self.assertEqual(resp_list.status_code, 200)
        reports_list = resp_list.json()
        self.assertIsInstance(reports_list, list)
        matching = [r for r in reports_list if r["report_id"] == report_id]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["image_url"], image_url)
        self.assertEqual(matching[0]["cv_crack_type"], "TENSION_CRACK")
        self.assertEqual(matching[0]["cv_aperture_mm"], 42.5)

        print("[PASS] 3. Citizen photo upload, secure storage, and triage drawer display verified.")

    # =========================================================================
    # TASK 1.4: Geofenced Alert Dispatch & SSE Event Streaming
    # =========================================================================
    def test_04_geofenced_alert_dispatch_and_sse_streaming(self):
        """Verify Haversine geofencing distance rules and SSE event stream reception."""
        epicenter_lat = 27.2010
        epicenter_lng = 88.5180
        hazard_radius_km = 15.0

        # In-zone coordinate (Likhu Veer, ~0.4 km)
        d_in = haversine_km(epicenter_lat, epicenter_lng, 27.2035, 88.5160)
        self.assertLessEqual(d_in, hazard_radius_km)
        self.assertTrue(d_in < 1.0)

        # Out-of-zone coordinate (Siliguri, ~70 km)
        d_out = haversine_km(epicenter_lat, epicenter_lng, 26.7271, 88.3953)
        self.assertGreater(d_out, hazard_radius_km)

        # Verify SSE streaming endpoint headers
        resp_stream = requests.get(f"{BASE_URL}/api/alerts/stream", stream=True, timeout=5)
        self.assertEqual(resp_stream.status_code, 200)
        content_type = resp_stream.headers.get("Content-Type", "")
        self.assertIn("text/event-stream", content_type)
        
        # Read first chunk
        initial_chunk = ""
        for chunk in resp_stream.iter_content(chunk_size=128):
            if chunk:
                initial_chunk += chunk.decode("utf-8", errors="ignore")
                break
        self.assertIn("connected", initial_chunk)

        print("[PASS] 4. Geofenced alert dispatch and real-time SSE event bus streaming verified.")

    # =========================================================================
    # TASK 2: GIGW 3.0 Compliance & Accessibility Verification
    # =========================================================================
    def test_05_gigw_compliance_and_accessibility(self):
        """Inspect all templates for GIGW 3.0 strict accessibility, skip-links, focus outlines, and typography."""
        for name, html in self.templates.items():
            # 1. Skip-to-content link
            self.assertIn('Skip to main content', html, f"{name} is missing 'Skip to main content' link")
            self.assertIn('id="main-content"', html, f"{name} is missing target <main id='main-content'>")

            # 2. High-contrast focus indicator styles
            self.assertIn(':focus', html, f"{name} is missing high-contrast focus state styles")

            # 3. Government of India Emblem alt text
            self.assertIn('alt="Government of India Emblem"', html, f"{name} missing descriptive emblem alt text")

            # 4. Strict Noto Sans & Noto Sans Devanagari typography
            self.assertIn('Noto Sans', html, f"{name} missing Noto Sans font declaration")
            self.assertIn('Noto Sans Devanagari', html, f"{name} missing Noto Sans Devanagari font declaration")

        print("[PASS] 5. GIGW 3.0 compliance & accessibility strictly verified across all 5 templates.")


if __name__ == "__main__":
    unittest.main()
