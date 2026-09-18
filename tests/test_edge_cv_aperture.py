"""Unit and integration tests for Edge Computer Vision & Drone/CCTV Crack Aperture Analyzer.

Validates Modality 5 of the Multimodal Evidence Fusion Invariant:
- Sub-pixel crack aperture measurement (w_crack)
- Dilation velocity (dw/dt)
- Shear displacement vector (dx, dy)
- Mudflow and runout kinematics
- Critical breach threshold enforcement (w >= 30.0 mm)
- 2-of-3 Triangulation Gate Signal 1 corroboration
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json
from app import app
from services.cv_analyzer import edge_cv_analyzer, CRITICAL_APERTURE_LIMIT_MM


class TestEdgeCVAnalyzer(unittest.TestCase):
    """Test suite for edge computer vision crack aperture analysis."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_get_cameras_inventory(self):
        """Verify GET /api/cv/cameras returns registered optical cameras and drones."""
        res = self.client.get("/api/cv/cameras")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertTrue(data.get("success"))
        self.assertIn("cameras", data)
        self.assertGreaterEqual(len(data["cameras"]), 3)

        cam_ids = [c["id"] for c in data["cameras"]]
        self.assertIn("CAM-NH10-KM48", cam_ids)
        self.assertIn("DRONE-MELTHUM-QUARRY", cam_ids)
        self.assertIn("CAM-SONAPUR-PORTAL", cam_ids)

        # Check camera schema
        c0 = data["cameras"][0]
        self.assertIn("name", c0)
        self.assertIn("sector_id", c0)
        self.assertIn("fps", c0)
        self.assertIn("resolution", c0)
        self.assertEqual(c0.get("aperture_threshold_limit_mm"), 30.0)

    def test_analyze_aperture_get_default(self):
        """Verify GET /api/cv/analyze-aperture returns telemetry for default camera."""
        res = self.client.get("/api/cv/analyze-aperture")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("camera_id"), "CAM-NH10-KM48")
        self.assertIn("aperture_mm", data)
        self.assertIn("dilation_velocity_mm_per_hr", data)
        self.assertIn("shear_vector_mm", data)
        self.assertIn("mudflow_runout_index", data)
        self.assertIn("contour_polygon_px", data)
        self.assertIn("bounding_box", data)
        self.assertIn("breach_threshold_exceeded", data)
        self.assertIn("provenance", data)
        self.assertEqual(data["provenance"], "[EDGE-CV / SENSOR-FEED]")

    def test_analyze_aperture_post_specific_camera(self):
        """Verify POST /api/cv/analyze-aperture with specific camera parameters."""
        payload = {
            "camera_id": "DRONE-MELTHUM-QUARRY",
            "simulated_stage": "SHEARING"
        }
        res = self.client.post("/api/cv/analyze-aperture", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("camera_id"), "DRONE-MELTHUM-QUARRY")
        self.assertEqual(data.get("current_stage"), "SHEARING")
        self.assertGreaterEqual(data["aperture_mm"], 10.0)

    def test_simulate_dilation_stages(self):
        """Verify POST /api/cv/simulate-dilation toggles NORMAL, SHEARING, and CRITICAL stages."""
        # Test NORMAL
        res_normal = self.client.post("/api/cv/simulate-dilation", json={
            "camera_id": "CAM-NH10-KM48",
            "stage": "NORMAL"
        })
        self.assertEqual(res_normal.status_code, 200)
        d_norm = res_normal.get_json()
        self.assertFalse(d_norm["breach_threshold_exceeded"])
        self.assertLess(d_norm["aperture_mm"], CRITICAL_APERTURE_LIMIT_MM)

        # Test CRITICAL
        res_crit = self.client.post("/api/cv/simulate-dilation", json={
            "camera_id": "CAM-NH10-KM48",
            "stage": "CRITICAL"
        })
        self.assertEqual(res_crit.status_code, 200)
        d_crit = res_crit.get_json()
        self.assertTrue(d_crit["breach_threshold_exceeded"])
        self.assertGreaterEqual(d_crit["aperture_mm"], CRITICAL_APERTURE_LIMIT_MM)
        self.assertIn("SIGNAL_1_PHYSICAL_RUPTURE", d_crit.get("triangulation_signal_contribution", ""))

    def test_simulate_dilation_invalid_stage(self):
        """Verify POST /api/cv/simulate-dilation rejects invalid stages with HTTP 400."""
        res = self.client.post("/api/cv/simulate-dilation", json={
            "camera_id": "CAM-NH10-KM48",
            "stage": "INVALID_STATE_XYZ"
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data.get("success"))
        self.assertIn("error", data)

    def test_direct_cv_analyzer_methods(self):
        """Test direct python methods in EdgeComputerVisionAnalyzer service."""
        cams = edge_cv_analyzer.get_registered_cameras()
        self.assertGreaterEqual(len(cams), 3)

        analysis = edge_cv_analyzer.analyze_frame("CAM-SONAPUR-PORTAL", stage="CRITICAL")
        self.assertTrue(analysis["breach_threshold_exceeded"])
        self.assertGreaterEqual(analysis["aperture_mm"], 30.0)
        self.assertIn("dx", analysis["shear_vector_mm"])
        self.assertIn("dy", analysis["shear_vector_mm"])
        self.assertIn("magnitude", analysis["shear_vector_mm"])
        self.assertGreater(len(analysis["contour_polygon_px"]), 3)


if __name__ == "__main__":
    unittest.main()
