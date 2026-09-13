#!/usr/bin/env python3
"""
Test Suite: End-to-End Field Evidence Photo Pipeline
Verifies:
1. POST /api/reports/submit with base64 image and explicit edge CV aperture
2. Image file written to disk under static/uploads/field_reports/pn_report_*
3. GET /api/reports/list contains image_url and Edge CV attributes
4. Public image asset is servable over HTTP 200
"""

import os
import sys
import base64
import requests
import unittest

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8080")

class TestFieldEvidencePipeline(unittest.TestCase):
    def test_01_photo_upload_and_storage(self):
        sample_png_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        payload = {
            "reporter_name": "Sub-Inspector Karma Bhutia",
            "phone": "9876543210",
            "latitude": 27.2015,
            "longitude": 88.5182,
            "severity": "CRITICAL",
            "description": "Active tension crack opening across NH-10 near Km 48 with transverse shear fissures.",
            "photo": sample_png_b64,
            "image_base64": sample_png_b64,
            "cv_aperture_mm": 41.5,
            "edge_cv_aperture": 41.5
        }

        res = requests.post(f"{BASE_URL}/api/reports/submit", json=payload, timeout=10)
        self.assertEqual(res.status_code, 201, f"Failed submitting report: {res.text}")
        data = res.json()
        
        self.assertEqual(data.get("status"), "SUCCESS")
        self.assertIn("report_id", data)
        self.assertIn("image_url", data)
        
        image_url = data["image_url"]
        self.assertTrue(image_url.startswith("/static/uploads/field_reports/pn_report_"), f"Unexpected image_url: {image_url}")
        
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rel_path = image_url.lstrip("/").replace("/", os.sep)
        disk_path = os.path.join(repo_root, rel_path)
        self.assertTrue(os.path.exists(disk_path), f"File was not saved to disk at {disk_path}")
        self.assertGreater(os.path.getsize(disk_path), 0, f"Saved file is empty at {disk_path}")

        img_res = requests.get(f"{BASE_URL}{image_url}", timeout=5)
        self.assertEqual(img_res.status_code, 200, f"Image URL returned non-200: {img_res.status_code}")

        cv_info = data.get("cv_classification", {})
        self.assertEqual(cv_info.get("cv_crack_type"), "TENSION_CRACK")
        self.assertEqual(cv_info.get("cv_aperture_mm"), 41.5)
        self.assertEqual(cv_info.get("triage_priority"), "IMMEDIATE_CLOSURE")
        print(f"[PASS] Successfully ingested report #{data['report_id']} with stored photo {image_url} ({os.path.getsize(disk_path)} bytes)")

    def test_02_reports_list_contains_evidence(self):
        res = requests.get(f"{BASE_URL}/api/reports/list", timeout=10)
        self.assertEqual(res.status_code, 200)
        reports = res.json()
        self.assertIsInstance(reports, list)
        self.assertGreater(len(reports), 0)

        top_report = reports[0]
        self.assertIn("report_id", top_report)
        self.assertIn("image_url", top_report)
        self.assertIn("cv_crack_type", top_report)
        self.assertIn("cv_aperture_mm", top_report)
        self.assertIn("cv_confidence_pct", top_report)
        print(f"[PASS] /api/reports/list includes Edge CV attributes: type={top_report.get('cv_crack_type')}, aperture={top_report.get('cv_aperture_mm')}mm, conf={top_report.get('cv_confidence_pct')}%")

if __name__ == "__main__":
    unittest.main()
