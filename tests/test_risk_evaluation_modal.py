# -*- coding: utf-8 -*-
"""
tests/test_risk_evaluation_modal.py
====================================
Test suite verifying the Risk Evaluation Dossier Modal and execution flow for any corridor dot:
  1. Verifies #modal-risk-evaluation exists with all telemetry & KPI fields.
  2. Verifies inspectSectorDeepRisk, openRiskEvaluationModal, executeRiskEvaluation,
     syncModalToDashboard, and centerMapOnSector are registered on window.
  3. Verifies GET /api/pahad/realtime-cri/sector/<sector_id> executes and returns
     authoritative records with FoS, CRI, 2-of-3 signals, and live telemetry for:
       - MN-JIRIBAM-01 (Imphal-Jiribam NH-37 Km 78 - from user report)
       - SK-NH10-KM48 (Sikkim NH-10 Corridor)
       - MZ-HUNTHAR-01 (Mizoram NH-6 Hunthar Slump)
  4. Verifies #risk-evaluation-panel exists on the dashboard for seamless sync.
"""

import os
import sys
import unittest

os.environ.setdefault("PARVAT_TESTING", "1")
os.environ.setdefault("PAHAD_DEMO_MODE", "1")
os.environ.setdefault("DRY_RUN", "true")
os.environ.setdefault("ENABLE_PUBLIC_DISPATCH", "0")
os.environ.setdefault("SIREN_DRY_RUN", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from app import app


class TestRiskEvaluationModalAndExecution(unittest.TestCase):
    """Verifies the Risk Evaluation Modal and sector execution engine."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

        # Load index.html template
        template_path = os.path.join(REPO_ROOT, "templates", "index.html")
        with open(template_path, "r", encoding="utf-8") as f:
            cls.index_html = f.read()

    def test_01_modal_risk_evaluation_markup_present(self):
        """Verify modal-risk-evaluation dialog and key structural elements exist in index.html."""
        self.assertIn('id="modal-risk-evaluation"', self.index_html)
        self.assertIn('id="re-modal-title"', self.index_html)
        self.assertIn('id="re-modal-sector-id-badge"', self.index_html)
        self.assertIn('id="re-modal-name"', self.index_html)
        self.assertIn('id="re-modal-location"', self.index_html)
        self.assertIn('id="re-modal-coords-elev"', self.index_html)
        self.assertIn('id="re-modal-risk-badge"', self.index_html)
        self.assertIn('id="re-modal-provenance-badge"', self.index_html)
        self.assertIn('id="re-modal-evaluated-at"', self.index_html)

    def test_02_modal_kpi_and_telemetry_fields_present(self):
        """Verify 4 core KPI fields and 4 telemetry breakdown sections exist."""
        # 4 Core KPI elements
        self.assertIn('id="re-val-cri"', self.index_html)
        self.assertIn('id="re-val-fos"', self.index_html)
        self.assertIn('id="re-val-prob"', self.index_html)
        self.assertIn('id="re-val-signals"', self.index_html)

        # Multi-modal telemetry streams
        self.assertIn('id="re-rain-24h"', self.index_html)
        self.assertIn('id="re-rain-72h"', self.index_html)
        self.assertIn('id="re-rain-threshold"', self.index_html)
        self.assertIn('id="re-seismic-event"', self.index_html)
        self.assertIn('id="re-insar-vel"', self.index_html)
        self.assertIn('id="re-vwc"', self.index_html)
        self.assertIn('id="re-pore-pressure"', self.index_html)
        self.assertIn('id="re-why-this-risk"', self.index_html)
        self.assertIn('id="re-rec-action"', self.index_html)
        self.assertIn('id="re-highway-status"', self.index_html)

    def test_03_javascript_functions_exposed(self):
        """Verify JavaScript execution functions are registered on window."""
        self.assertIn("window.openRiskEvaluationModal = openRiskEvaluationModal;", self.index_html)
        self.assertIn("window.closeRiskEvaluationModal = closeRiskEvaluationModal;", self.index_html)
        self.assertIn("window.executeRiskEvaluation = executeRiskEvaluation;", self.index_html)
        self.assertIn("window.inspectSectorDeepRisk = inspectSectorDeepRisk;", self.index_html)
        self.assertIn("window.centerMapOnSector = centerMapOnSector;", self.index_html)
        self.assertIn("window.syncModalToDashboard = syncModalToDashboard;", self.index_html)

    def test_04_execute_risk_evaluation_for_manipur_jiribam(self):
        """Verify live execution for MN-JIRIBAM-01 (Imphal-Jiribam NH-37 Km 78) returns authoritative record."""
        res = self.client.get("/api/pahad/realtime-cri/sector/MN-JIRIBAM-01")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        rec = data.get("record", {})
        self.assertEqual(rec.get("sector_id"), "MN-JIRIBAM-01")
        self.assertIn("Imphal-Jiribam", rec.get("sector_name", ""))
        self.assertEqual(rec.get("district"), "Tamenglong")
        self.assertEqual(rec.get("state"), "Manipur")
        self.assertIn("final_cri", rec)
        self.assertIn("physical_fos", rec)
        self.assertIn("event_probability_24h", rec)
        self.assertIn("rainfall_24h_mm", rec)
        self.assertIn("seismic_magnitude", rec)
        self.assertIn("insar_deformation_mm", rec)

    def test_05_execute_risk_evaluation_for_sikkim_nh10(self):
        """Verify live execution for SK-NH10-KM48 returns authoritative record."""
        res = self.client.get("/api/pahad/realtime-cri/sector/SK-NH10-KM48")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        rec = data.get("record", {})
        self.assertEqual(rec.get("sector_id"), "SK-NH10-KM48")
        self.assertEqual(rec.get("state"), "Sikkim")
        self.assertGreater(rec.get("final_cri", 0), 0)
        self.assertGreater(rec.get("physical_fos", 0), 0)

    def test_06_execute_risk_evaluation_for_mizoram_hunthar(self):
        """Verify live execution for MZ-HUNTHAR-01 returns authoritative record."""
        res = self.client.get("/api/pahad/realtime-cri/sector/MZ-HUNTHAR-01")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "SUCCESS")
        rec = data.get("record", {})
        self.assertEqual(rec.get("sector_id"), "MZ-HUNTHAR-01")
        self.assertEqual(rec.get("state"), "Mizoram")

    def test_07_decision_panel_container_id_exists(self):
        """Verify risk-evaluation-panel container exists on dashboard."""
        self.assertIn('id="risk-evaluation-panel"', self.index_html)

    def test_08_gis_header_legend_risk_levels(self):
        """Verify GIS hazard map header legend displays risk levels (CRITICAL, HIGH, MODERATE, LOW) instead of color names."""
        self.assertIn('CRITICAL', self.index_html)
        self.assertIn('MODERATE', self.index_html)
        self.assertIn('bg-red-600 mr-0.5"></span> CRITICAL', self.index_html)
        self.assertIn('bg-amber-500 mr-0.5"></span> HIGH', self.index_html)
        self.assertIn('bg-yellow-400 mr-0.5"></span> MODERATE', self.index_html)
        self.assertIn('bg-emerald-500 mr-0.5"></span> LOW', self.index_html)
        # Ensure raw color names are not used as standalone labels in the header legend
        self.assertNotIn('bg-red-600 mr-0.5"></span> RED', self.index_html)
        self.assertNotIn('bg-amber-500 mr-0.5"></span> ORANGE', self.index_html)


if __name__ == "__main__":
    unittest.main()

