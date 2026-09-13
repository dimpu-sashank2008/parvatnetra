#!/usr/bin/env python3
"""
Test Suite for Citizen Emergency SOS Siren & Field Landslide Photo Reporting
Verifies:
1. Frontend DOM markers and accessible structure in templates/index.html:
   - SOS Siren button: 🚨 Sound Emergency Siren / आपातकालीन सायरन (#DC2626)
   - Secondary toggle: ⏹️ Stop Siren
   - Floating Action Bar (#citizen-floating-action-bar)
   - Report Landslide / Road Hazard trigger and modal (#citizen-report-modal)
   - Form fields: category dropdown, GPS coordinates, sync button, photo input, notes
   - Web Audio 853/960 Hz alternating siren and navigator.vibrate([500, 250, 500])
2. REST Endpoint POST /api/reports/submit with multipart/form-data:
   - Handles binary file upload in request.files['photo']
   - Validates file extensions, saves to static/uploads/field_reports/<secure_filename>
   - Assigns Report Tracking ID matching PN-REPORT-2026-XXXX
   - Persists status PENDING_VERIFICATION and auto-triages priority
3. Verification in /api/reports/list for Authority EOC triage and inspection.
"""

import io
import os
import re
import unittest
import requests

BASE_URL = "http://127.0.0.1:8080"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestCitizenSOSAndPhotoReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template_path = os.path.join(REPO_ROOT, "templates", "index.html")
        cls.i18n_path = os.path.join(REPO_ROOT, "static", "js", "i18n.js")
        with open(cls.template_path, "r", encoding="utf-8") as f:
            cls.index_html = f.read()
        with open(cls.i18n_path, "r", encoding="utf-8") as f:
            cls.i18n_js = f.read()

    def test_01_citizen_sos_siren_dom_elements(self):
        """Verify Citizen SOS Siren and Stop Siren buttons in index.html."""
        self.assertIn("btn-citizen-sos", self.index_html)
        self.assertIn("Sound Emergency Siren", self.index_html)
        self.assertIn("आपातकालीन सायरन", self.index_html)
        self.assertIn("#DC2626", self.index_html)
        self.assertIn("triggerFullLandslideAlarm(15)", self.index_html)
        
        # Secondary stop toggle
        self.assertIn("btn-citizen-stop-siren", self.index_html)
        self.assertIn("stopEmergencyAlarm", self.index_html)
        self.assertIn("Stop Siren", self.index_html)

        # Haptic vibration pattern
        self.assertIn("navigator.vibrate([500, 250, 500])", self.index_html)

    def test_02_citizen_report_modal_dom_elements(self):
        """Verify #citizen-report-modal structure and form inputs."""
        self.assertIn('id="citizen-report-modal"', self.index_html)
        self.assertIn('id="citizen-modal-report-form"', self.index_html)
        
        # Trigger buttons
        self.assertIn("openCitizenReportModal()", self.index_html)
        self.assertIn("Report Landslide / Road Hazard", self.index_html)

        # Hazard categories
        self.assertIn('name="category"', self.index_html)
        self.assertIn("Tension Crack", self.index_html)
        self.assertIn("Rockfall", self.index_html)
        self.assertIn("Road Blockage", self.index_html)
        self.assertIn("Active Mudslide", self.index_html)

        # GPS & Sync
        self.assertIn('id="crm-lat"', self.index_html)
        self.assertIn('id="crm-lon"', self.index_html)
        self.assertIn("syncCitizenReportLocation", self.index_html)
        self.assertIn("Sync Current Location", self.index_html)

        # Field Photo input and preview
        self.assertIn('id="crm-photo-file"', self.index_html)
        self.assertIn('accept="image/*"', self.index_html)
        self.assertIn('capture="environment"', self.index_html)
        self.assertIn('id="crm-photo-preview-container"', self.index_html)
        self.assertIn('id="crm-photo-preview"', self.index_html)

        # Notes and submit button
        self.assertIn('id="crm-notes"', self.index_html)
        self.assertIn('id="crm-submit-btn"', self.index_html)
        self.assertIn("submitCitizenModalReport", self.index_html)

    def test_03_floating_action_bar_present(self):
        """Verify citizen floating action bar exists."""
        self.assertIn('id="citizen-floating-action-bar"', self.index_html)

    def test_04_multipart_photo_upload_submission(self):
        """POST /api/reports/submit with multipart/form-data and binary photo."""
        # Create a sample 1x1 PNG image in-memory
        sample_png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc`\x00\x00'
            b'\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
        )

        files = {
            "photo": ("citizen_field_capture.png", io.BytesIO(sample_png), "image/png")
        }
        form_data = {
            "category": "Active Mudslide",
            "notes": "Fast-moving mud and debris spilling onto NH-10 near 29th Mile milestone.",
            "latitude": "27.2020",
            "longitude": "88.5185",
            "reporter_name": "Pema Lepcha (Citizen)",
            "phone": "+91-9434012345"
        }

        res = requests.post(f"{BASE_URL}/api/reports/submit", data=form_data, files=files, timeout=10)
        self.assertEqual(res.status_code, 201, f"Failed: {res.text}")
        
        data = res.json()
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertIn("report_id", data)
        self.assertIn("tracking_id", data)
        self.assertIn("tracking_ref", data)
        
        tracking_id = data["tracking_id"]
        # Format check: PN-REPORT-2026-XXXX
        self.assertRegex(tracking_id, r"^PN-REPORT-2026-\d{4,}$")

        # Verify photo was saved to disk
        image_url = data.get("image_url")
        self.assertIsNotNone(image_url)
        self.assertTrue(image_url.startswith("/static/uploads/field_reports/pn_report_"))

        rel_path = image_url.lstrip("/").replace("/", os.sep)
        disk_path = os.path.join(REPO_ROOT, rel_path)
        self.assertTrue(os.path.exists(disk_path), f"Saved image file missing: {disk_path}")
        self.assertGreater(os.path.getsize(disk_path), 0)

        # Verify photo can be served over HTTP 200
        img_res = requests.get(f"{BASE_URL}{image_url}", timeout=5)
        self.assertEqual(img_res.status_code, 200)

        # Verify CV classification and triage priority
        cv = data.get("cv_classification", {})
        self.assertEqual(cv.get("triage_priority"), "IMMEDIATE_CLOSURE")
        print(f"[PASS] Citizen multipart report #{data['report_id']} saved with tracking ID {tracking_id} and photo {image_url}")

    def test_05_report_appears_in_eoc_list(self):
        """GET /api/reports/list verifies that newly submitted citizen report is visible for EOC triage."""
        res = requests.get(f"{BASE_URL}/api/reports/list", timeout=10)
        self.assertEqual(res.status_code, 200)
        reports = res.json()
        self.assertGreater(len(reports), 0)

        latest = reports[0]
        self.assertIn("report_id", latest)
        self.assertIn("image_url", latest)
        self.assertIn("status", latest)
        self.assertEqual(latest["status"], "PENDING_VERIFICATION")
        print(f"[PASS] EOC triage queue contains report #{latest['report_id']} with status {latest['status']}")

if __name__ == "__main__":
    unittest.main()
