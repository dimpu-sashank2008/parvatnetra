# -*- coding: utf-8 -*-
"""
PARVAT NETRA - Siren and Google Maps Integration Verification Test Suite
SIH Problem Statement ID: 26001 (MDoNER)

Validates:
1. getGoogleMapsUrl function with Lava 45T and Mungpoo 18.5T waypoints exists in templates/index.html.
2. Waypoints 'Damdim%7CGorubathan%7CLava' and 'Sevoke%7CMungpoo%7CJorebungalow' exist in templates/index.html.
3. playEmergencySiren, navigator.vibrate, and id="landslide-lockdown-modal" exist in templates/index.html.
4. Authority test siren button and Citizen emergency evacuation siren button exist in templates/index.html.
5. Local Flask server is responsive and returns HTTP 200 on http://127.0.0.1:8080/.
"""

import os
import unittest
import urllib.request
import urllib.error

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_PATH = os.path.join(REPO_ROOT, 'templates', 'index.html')


class TestSirenAndGMaps(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            cls.html = f.read()

    def test_01_google_maps_waypoints_and_helper(self):
        """Verify getGoogleMapsUrl and explicit mountain waypoints are present."""
        self.assertIn('getGoogleMapsUrl', self.html, "getGoogleMapsUrl function missing from templates/index.html")
        self.assertIn('BYPASS-LAVA', self.html, "Lava corridor code missing from templates/index.html")
        self.assertIn('BYPASS-MUNGPOO', self.html, "Mungpoo corridor code missing from templates/index.html")
        
        # Verify Lava waypoints in citizen card and helper
        self.assertIn('Damdim%7CGorubathan%7CLava', self.html, "Lava waypoints Damdim%7CGorubathan%7CLava missing")
        # Verify Mungpoo waypoints in citizen card and helper
        self.assertIn('Sevoke%7CMungpoo%7CJorebungalow', self.html, "Mungpoo waypoints Sevoke%7CMungpoo%7CJorebungalow missing")
        
        # Verify destination and origin
        self.assertIn('Siliguri,West+Bengal', self.html, "Siliguri origin missing")
        self.assertIn('Gangtok,Sikkim', self.html, "Gangtok destination missing")
        print("[PASS] Test 1: getGoogleMapsUrl and mountain corridor waypoints verified.")

    def test_02_emergency_siren_and_haptics(self):
        """Verify Web Audio API siren, frequencies, and mobile vibration."""
        self.assertIn('playEmergencySiren', self.html, "playEmergencySiren function missing")
        self.assertIn('AudioContext', self.html, "AudioContext initialization missing")
        self.assertIn('navigator.vibrate', self.html, "navigator.vibrate mobile haptic call missing")
        self.assertIn('853', self.html, "853 Hz dual-tone frequency missing")
        self.assertIn('960', self.html, "960 Hz dual-tone frequency missing")
        self.assertIn('stopSirenToneOnly', self.html, "stopSirenToneOnly helper missing")
        self.assertIn('stopEmergencyAlarm', self.html, "stopEmergencyAlarm helper missing")
        print("[PASS] Test 2: Web Audio API dual-tone siren (853 Hz + 960 Hz) and vibration verified.")

    def test_03_landslide_lockdown_modal(self):
        """Verify full-screen landslide lockdown modal markup and components."""
        self.assertIn('id="landslide-lockdown-modal"', self.html, "Modal #landslide-lockdown-modal missing")
        self.assertIn('ACTIVE LANDSLIDE IN PROGRESS', self.html, "Lockdown modal header text missing")
        self.assertIn('Evacuation Order', self.html, "Lockdown modal evacuation order text missing")
        self.assertIn('triggerFullLandslideAlarm', self.html, "triggerFullLandslideAlarm function missing")
        print("[PASS] Test 3: Full-screen landslide lockdown modal markup verified.")

    def test_04_siren_trigger_buttons(self):
        """Verify presence of test/trigger buttons in Authority and Citizen views."""
        # Authority operations card trigger button
        self.assertIn('Test Phone Siren', self.html, "Authority 'Test Phone Siren' button missing")
        # Citizen road closure hero banner trigger button
        self.assertIn('Sound Emergency Evacuation Siren', self.html, "Citizen 'Sound Emergency Evacuation Siren' button missing")
        print("[PASS] Test 4: Both Authority and Citizen alarm trigger buttons verified.")

    def test_05_local_server_health(self):
        """Verify Flask web server is active and returns HTTP 200."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8080/")
            with urllib.request.urlopen(req, timeout=5) as response:
                status_code = response.getcode()
                body = response.read().decode('utf-8')
                self.assertEqual(status_code, 200, f"Expected 200, got {status_code}")
                self.assertIn('PARVAT NETRA', body, "Page title/header PARVAT NETRA missing in server response")
                self.assertIn('Sound Emergency Evacuation Siren', body, "Citizen siren button not in rendered page response")
                print(f"[PASS] Test 5: Server responding on http://127.0.0.1:8080/ with HTTP {status_code}.")
        except urllib.error.URLError as e:
            self.fail(f"Flask server at http://127.0.0.1:8080/ is unreachable: {e}")

    def test_06_two_step_safety_siren_and_geofencing(self):
        """Verify Two-Step physical safety lock, client-side geofencing, and backend dispatch API."""
        self.assertIn('id="authority-siren-modal"', self.html, "Modal #authority-siren-modal missing")
        self.assertIn('id="slider-track"', self.html, "Slider track missing")
        self.assertIn('id="slider-thumb"', self.html, "Slider thumb missing")
        self.assertIn('openAuthoritySirenArmModal', self.html, "openAuthoritySirenArmModal missing")
        self.assertIn('calculateDistanceKm', self.html, "calculateDistanceKm missing")
        self.assertIn('checkZoneProximity', self.html, "checkZoneProximity missing")
        self.assertIn('handleIncomingEmergencyAlert', self.html, "handleIncomingEmergencyAlert missing")
        self.assertIn('broadcastSirenToCorridor', self.html, "broadcastSirenToCorridor missing")

        # Test backend API
        import json
        req = urllib.request.Request(
            "http://127.0.0.1:8080/api/alerts/dispatch-siren",
            data=json.dumps({"sector": "NH-10 Km 48", "radius_km": 15.0, "fs": 0.745}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            self.assertEqual(response.getcode(), 200)
            res_data = json.loads(response.read().decode("utf-8"))
            self.assertEqual(res_data.get("status"), "DISPATCHED")
            self.assertEqual(res_data.get("sector"), "NH-10 Km 48")
            self.assertEqual(res_data.get("radius_km"), 15.0)
        print("[PASS] Test 6: Two-step physical safety lock, Haversine geofencing, and dispatch API verified.")

    def test_07_sse_stream_and_client_wiring(self):
        """Verify Server-Sent Events (SSE) notification stream and client-side listeners."""
        self.assertIn('initAlertEventSource', self.html, "initAlertEventSource missing from templates/index.html")
        self.assertIn('setUserPosition', self.html, "setUserPosition missing from templates/index.html")
        self.assertIn('/api/alerts/stream', self.html, "SSE endpoint URL missing from templates/index.html")
        self.assertIn('siren_dispatch', self.html, "siren_dispatch SSE event listener missing")

        # Test SSE backend streaming endpoint
        req = urllib.request.Request("http://127.0.0.1:8080/api/alerts/stream")
        with urllib.request.urlopen(req, timeout=5) as stream_resp:
            self.assertEqual(stream_resp.getcode(), 200)
            content_type = stream_resp.headers.get("Content-Type", "")
            self.assertIn("text/event-stream", content_type, f"Expected text/event-stream, got {content_type}")
            
            # Read first chunk of SSE stream
            initial_chunk = stream_resp.readline().decode("utf-8")
            self.assertTrue(initial_chunk.startswith(":") or "ping" in initial_chunk, f"Unexpected initial chunk: {initial_chunk}")
        print("[PASS] Test 7: Real-time SSE alert bus streaming endpoint and client listeners verified.")


if __name__ == '__main__':
    unittest.main(verbosity=2)
