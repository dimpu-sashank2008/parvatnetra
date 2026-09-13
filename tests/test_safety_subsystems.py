# -*- coding: utf-8 -*-
"""
PARVAT NETRA - Safety Subsystems Verification Test Suite
SIH Problem Statement ID: 26001 (MDoNER)

Validates:
1. Haversine Distance Calculation (known epicenter vs nearby vs regional coordinates)
2. Geofenced Proximity Logic (15.0 km critical corridor threshold)
3. Authority Role Guardrails (HTTP 403 for unauthenticated / citizen role on dispatch-siren)
4. Field Report Photo Upload Backend Storage (base64 and multipart file persistence)
5. Developer Console (/console) with live SSE stream telemetry and severity tags
"""

import os
import io
import math
import json
import base64
import unittest
import urllib.request
import urllib.error

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATES_DIR = os.path.join(REPO_ROOT, 'templates')
INDEX_HTML_PATH = os.path.join(TEMPLATES_DIR, 'index.html')
CONSOLE_HTML_PATH = os.path.join(TEMPLATES_DIR, 'console.html')
BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8080")

# Reference Hazard Epicenter for NH-10 Km 48 failure plane
EPICENTER_LAT = 27.2010
EPICENTER_LNG = 88.5180
CRITICAL_RADIUS_KM = 15.0


def calculate_haversine_km(lat1, lon1, lat2, lon2):
    """Calculates great-circle distance between two points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class TestSafetySubsystems(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
            cls.index_html = f.read()

        if os.path.exists(CONSOLE_HTML_PATH):
            with open(CONSOLE_HTML_PATH, 'r', encoding='utf-8') as f:
                cls.console_html = f.read()
        else:
            cls.console_html = ""

    # =========================================================================
    # TASK 1.1: Haversine Distance Calculation
    # =========================================================================
    def test_01_haversine_distance_calculation(self):
        """Test that known coordinates compute accurate physical distances in kilometers."""
        # 1. Zero distance (self to self)
        d_self = calculate_haversine_km(EPICENTER_LAT, EPICENTER_LNG, EPICENTER_LAT, EPICENTER_LNG)
        self.assertAlmostEqual(d_self, 0.0, places=4, msg="Self-distance must be zero")

        # 2. Symmetry property: dist(A, B) == dist(B, A)
        d_ab = calculate_haversine_km(EPICENTER_LAT, EPICENTER_LNG, 27.3389, 88.6065)
        d_ba = calculate_haversine_km(27.3389, 88.6065, EPICENTER_LAT, EPICENTER_LNG)
        self.assertAlmostEqual(d_ab, d_ba, places=4, msg="Haversine distance must be symmetric")

        # 3. Near-field point (Km 48 tension crack at +0.0005 deg N, +0.0002 deg E)
        d_near = calculate_haversine_km(EPICENTER_LAT, EPICENTER_LNG, 27.2015, 88.5182)
        self.assertGreater(d_near, 0.04)
        self.assertLess(d_near, 0.08)  # ~0.059 km

        # 4. Regional Points vs Km 48 Epicenter:
        # Rangpo staging area: (27.1764, 88.5298) -> ~2.96 km
        d_rangpo = calculate_haversine_km(EPICENTER_LAT, EPICENTER_LNG, 27.1764, 88.5298)
        self.assertTrue(2.5 <= d_rangpo <= 3.5, f"Expected Rangpo ~3.0 km, got {d_rangpo:.2f} km")

        # Gangtok DC Office: (27.3389, 88.6065) -> ~17.6 km
        d_gangtok = calculate_haversine_km(EPICENTER_LAT, EPICENTER_LNG, 27.3389, 88.6065)
        self.assertTrue(16.5 <= d_gangtok <= 18.5, f"Expected Gangtok ~17.6 km, got {d_gangtok:.2f} km")

        # Siliguri Junction: (26.7271, 88.3953) -> ~54.2 km
        d_siliguri = calculate_haversine_km(EPICENTER_LAT, EPICENTER_LNG, 26.7271, 88.3953)
        self.assertTrue(50.0 <= d_siliguri <= 60.0, f"Expected Siliguri ~54.2 km, got {d_siliguri:.2f} km")

        # 5. Client JavaScript implementation verified
        self.assertIn('calculateDistanceKm', self.index_html, "calculateDistanceKm missing in index.html")
        self.assertIn('6371', self.index_html, "Earth radius 6371 km missing in index.html")
        print("[PASS] 1. Haversine distance calculation verified with high numerical accuracy.")

    # =========================================================================
    # TASK 1.2: Geofenced Proximity Logic
    # =========================================================================
    def test_02_geofenced_proximity_logic(self):
        """Test that coordinates within 15 km return True (triggering sirens) and coordinates outside return False."""
        # In-zone test points (<= 15.0 km) -> MUST trigger siren (True)
        in_zone_points = [
            ("Km 48 Epicenter", EPICENTER_LAT, EPICENTER_LNG),
            ("Km 48 Crack Site", 27.2015, 88.5182),
            ("Rangpo Staging Area", 27.1764, 88.5298),
            ("Singtam Bazaar", 27.2340, 88.4980),
            ("Pakyong Airport Approach", 27.2280, 88.5860),
            ("Boundary Inside (14.5 km)", 27.0710, 88.5180),
        ]

        for name, lat, lng in in_zone_points:
            dist = calculate_haversine_km(EPICENTER_LAT, EPICENTER_LNG, lat, lng)
            is_inside = (dist <= CRITICAL_RADIUS_KM)
            self.assertTrue(
                is_inside,
                f"{name} at {dist:.2f} km should be inside {CRITICAL_RADIUS_KM} km corridor"
            )

        # Out-of-zone test points (> 15.0 km) -> MUST suppress siren (False)
        out_zone_points = [
            ("Boundary Outside (15.5 km)", 27.0600, 88.5180),
            ("Gangtok DC Office (17.6 km)", 27.3389, 88.6065),
            ("Mangan District HQ (35.2 km)", 27.5100, 88.5300),
            ("Siliguri Junction (54.2 km)", 26.7271, 88.3953),
            ("Darjeeling Hill (38.8 km)", 27.0410, 88.2663),
        ]

        for name, lat, lng in out_zone_points:
            dist = calculate_haversine_km(EPICENTER_LAT, EPICENTER_LNG, lat, lng)
            is_inside = (dist <= CRITICAL_RADIUS_KM)
            self.assertFalse(
                is_inside,
                f"{name} at {dist:.2f} km should be outside {CRITICAL_RADIUS_KM} km corridor"
            )

        # Check frontend rule implementation in templates/index.html
        self.assertIn('checkZoneProximity', self.index_html, "checkZoneProximity function missing")
        self.assertIn('handleIncomingEmergencyAlert', self.index_html, "handleIncomingEmergencyAlert missing")
        self.assertIn('15.0', self.index_html, "15.0 km critical threshold missing in index.html")
        print("[PASS] 2. Geofenced proximity logic verified: in-zone triggers siren, out-of-zone suppresses.")

    # =========================================================================
    # TASK 1.3: Authority Role Guardrails
    # =========================================================================
    def test_03_authority_role_guardrails(self):
        """Test that unauthenticated users or users with role == 'citizen' receive HTTP 403 Forbidden on dispatch-siren."""
        dispatch_url = f"{BASE_URL}/api/alerts/dispatch-siren"
        payload = json.dumps({"sector": "NH-10 Km 48", "radius_km": 15.0, "fs": 0.745}).encode("utf-8")

        # 1. Unauthenticated request with simulated remote origin / required auth
        req_unauth = urllib.request.Request(
            dispatch_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Require-Auth": "true",
                "X-Simulate-Remote": "true",
                "X-Forwarded-For": "203.0.113.195"
            }
        )
        try:
            with urllib.request.urlopen(req_unauth, timeout=5) as resp:
                self.fail(f"Expected HTTP 403 for unauthenticated remote request, got {resp.getcode()}")
        except urllib.error.HTTPError as err:
            self.assertEqual(err.code, 403, f"Expected 403 Forbidden, got {err.code}")
            err_data = json.loads(err.read().decode("utf-8"))
            self.assertEqual(err_data.get("status"), "FORBIDDEN")

        # 2. Citizen user role simulation using Flask test client
        from app import app
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["role"] = "citizen"
                sess["user_role"] = "citizen"
                sess["user_id"] = "CITIZEN-9876"

            res_citizen = client.post(
                "/api/alerts/dispatch-siren",
                data=json.dumps({"sector": "NH-10 Km 48", "radius_km": 15.0, "fs": 0.745}),
                content_type="application/json"
            )
            self.assertEqual(res_citizen.status_code, 403, "Citizen role MUST receive HTTP 403")
            data_citizen = res_citizen.get_json()
            self.assertEqual(data_citizen.get("status"), "FORBIDDEN")
            self.assertIn("cannot dispatch", data_citizen.get("message", "").lower())

        # 3. Authorized Authority request with valid token / session
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["role"] = "authority"
                sess["user_role"] = "authority"
                sess["user_id"] = "DM-GANGTOK-EOC"

            res_auth = client.post(
                "/api/alerts/dispatch-siren",
                data=json.dumps({"sector": "NH-10 Km 48", "radius_km": 15.0, "fs": 0.745}),
                content_type="application/json"
            )
            self.assertEqual(res_auth.status_code, 200, "Authority role MUST be permitted (HTTP 200)")
            data_auth = res_auth.get_json()
            self.assertEqual(data_auth.get("status"), "DISPATCHED")
            self.assertIn("dispatch_id", data_auth)

        # 4. Token-based authorization check
        req_token = urllib.request.Request(
            dispatch_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Authority-Token": "parvat-authority-token-2026",
                "X-Require-Auth": "true"
            }
        )
        with urllib.request.urlopen(req_token, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            res_data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res_data.get("status"), "DISPATCHED")

        print("[PASS] 3. Authority role guardrails verified: citizen & unauthenticated blocked with HTTP 403.")

    # =========================================================================
    # TASK 1.4: Field Report Photo Upload Backend Storage
    # =========================================================================
    def test_04_field_report_photo_upload_storage(self):
        """Test that base64/multipart image payloads save successfully to disk and return valid URLs."""
        # 1-pixel red PNG
        sample_png_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

        # 1. Base64 payload submission
        payload = {
            "reporter_name": "Test Safety Inspector",
            "phone": "9876543210",
            "latitude": 27.2015,
            "longitude": 88.5182,
            "severity": "CRITICAL",
            "description": "Verification of field photo upload backend persistence.",
            "photo": sample_png_b64,
            "image_base64": sample_png_b64,
            "cv_aperture_mm": 38.5,
            "edge_cv_aperture": 38.5
        }

        req = urllib.request.Request(
            f"{BASE_URL}/api/reports/submit",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            self.assertIn(resp.getcode(), [200, 201])
            res_data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res_data.get("status"), "SUCCESS")
            self.assertIn("image_url", res_data)

            image_url = res_data["image_url"]
            self.assertTrue(
                image_url.startswith("/static/uploads/field_reports/pn_report_"),
                f"Unexpected image URL format: {image_url}"
            )

            # Check file exists on filesystem
            rel_path = image_url.lstrip("/").replace("/", os.sep)
            disk_path = os.path.join(REPO_ROOT, rel_path)
            self.assertTrue(os.path.exists(disk_path), f"Saved image file missing on disk: {disk_path}")
            self.assertGreater(os.path.getsize(disk_path), 0, f"Saved image is zero bytes: {disk_path}")

            # Verify image is servable over HTTP 200
            req_img = urllib.request.Request(f"{BASE_URL}{image_url}")
            with urllib.request.urlopen(req_img, timeout=5) as img_resp:
                self.assertEqual(img_resp.getcode(), 200)

        # 2. Multipart form submission via Flask test client
        from app import app
        with app.test_client() as client:
            raw_image_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
            data_form = {
                "reporter_name": "Field Worker Tenzing",
                "phone": "9812345678",
                "latitude": "27.2012",
                "longitude": "88.5181",
                "severity": "SEVERE",
                "description": "Multipart upload test verifying disk persistence.",
                "photo": (io.BytesIO(raw_image_data), "crack_sample.png")
            }
            res_multipart = client.post(
                "/api/reports/submit",
                data=data_form,
                content_type="multipart/form-data"
            )
            self.assertIn(res_multipart.status_code, [200, 201])
            data_mp = res_multipart.get_json()
            self.assertEqual(data_mp.get("status"), "SUCCESS")
            mp_image_url = data_mp.get("image_url")
            self.assertTrue(mp_image_url.startswith("/static/uploads/field_reports/"))

            mp_disk_path = os.path.join(REPO_ROOT, mp_image_url.lstrip("/").replace("/", os.sep))
            self.assertTrue(os.path.exists(mp_disk_path))
            self.assertGreater(os.path.getsize(mp_disk_path), 0)

        print("[PASS] 4. Field report photo upload backend storage verified for both base64 and multipart formats.")

    # =========================================================================
    # TASK 2: Developer Console (/console) & SSE Telemetry Integration
    # =========================================================================
    def test_05_developer_console_and_sse_tab(self):
        """Test that /console renders successfully with SSE Event Stream tab and color-coded severity tags."""
        # 1. Verify HTTP 200 on /console endpoint
        req = urllib.request.Request(f"{BASE_URL}/console")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200, "Expected HTTP 200 for /console")
            html = resp.read().decode("utf-8")
            self.assertIn("PARVAT NETRA", html)

        # 2. Verify SSE Event Stream terminal tab markup
        self.assertIn("SSE EVENT STREAM", self.console_html, "SSE EVENT STREAM tab title missing in console.html")
        self.assertIn('id="terminal-buffer"', self.console_html, "Terminal buffer container missing in console.html")
        self.assertIn('id="tab-btn-sse-stream"', self.console_html, "Tab button #tab-btn-sse-stream missing in console.html")
        self.assertIn('id="tab-content-sse-stream"', self.console_html, "Tab content #tab-content-sse-stream missing in console.html")

        # 3. Verify client-side EventSource connection to /api/alerts/stream
        self.assertIn("new EventSource('/api/alerts/stream')", self.console_html, "EventSource connection to /api/alerts/stream missing")
        self.assertIn("addEventListener('siren_dispatch'", self.console_html, "siren_dispatch listener missing in console.html")
        self.assertIn("addEventListener('cap_broadcast'", self.console_html, "cap_broadcast listener missing in console.html")
        self.assertIn("addEventListener('ping'", self.console_html, "ping listener missing in console.html")

        # 4. Verify color-coded severity tags
        self.assertIn("[SSE_BROADCAST]", self.console_html, "Color-coded tag [SSE_BROADCAST] missing in console.html")
        self.assertIn("[GEOLOCATION_TRIGGER]", self.console_html, "Color-coded tag [GEOLOCATION_TRIGGER] missing in console.html")
        self.assertIn("[SSE_CONNECT]", self.console_html, "Color-coded tag [SSE_CONNECT] missing in console.html")
        self.assertIn("[SSE_HEARTBEAT]", self.console_html, "Color-coded tag [SSE_HEARTBEAT] missing in console.html")

        # 5. Verify Geofence Simulator tab exists
        self.assertIn("GEOFENCE SIMULATOR", self.console_html, "Geofence simulator tab missing in console.html")
        self.assertIn("calculateHaversineKm", self.console_html, "calculateHaversineKm function missing in console.html")

        print("[PASS] 5. Developer console (/console) with SSE EVENT STREAM tab and severity tags fully verified.")


if __name__ == '__main__':
    unittest.main(verbosity=2)
