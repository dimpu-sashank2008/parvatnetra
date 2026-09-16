"""
Unit and Integration Tests for PARVAT NETRA - Phase 14: Top-1 Final Polish, Evaluator-Proofing & Submission Freeze.
"""
import json
import os
import sys
import unittest
from pptx import Presentation

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)
from app import app


class TestPhase14SubmissionFreeze(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs_dir = os.path.join(REPO_ROOT, "docs")
        cls.deck_path = os.path.join(cls.docs_dir, "PARVAT_NETRA_SIH_Winning_Deck.pptx")
        cls.index_path = os.path.join(REPO_ROOT, "templates", "index.html")
        cls.manifest_path = os.path.join(REPO_ROOT, "data", "manifests", "phase14_final_submission_manifest.json")
        cls.baseline_path = os.path.join(cls.docs_dir, "PHASE14_BASELINE.md")

    def test_01_baseline_freeze_report_exists_and_valid(self):
        """Assert PHASE14_BASELINE.md exists and contains Git branch, HEAD, commit metadata, and safety flags."""
        self.assertTrue(os.path.exists(self.baseline_path), "PHASE14_BASELINE.md missing")
        with open(self.baseline_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("main", content)
        self.assertIn("95b2ad440e4a34a676274fe27d3963df0a3e26c2", content)
        self.assertIn("ENABLE_PUBLIC_DISPATCH = 0", content)
        self.assertIn("SIREN_DRY_RUN = 1", content)

    def test_02_all_four_phase14_docs_exist_and_substantive(self):
        """Assert all 4 Phase 14 markdown documents exist, are >1500 bytes, and contain >200 words."""
        required_docs = [
            "PHASE14_TOP1_POLISH_REPORT.md",
            "PHASE14_EVALUATOR_CLARITY_REPORT.md",
            "PHASE14_PPT_FORENSIC_AUDIT.md",
            "PHASE14_FINAL_SUBMISSION_CHECKLIST.md"
        ]
        for doc in required_docs:
            path = os.path.join(self.docs_dir, doc)
            self.assertTrue(os.path.exists(path), f"Missing required document: {doc}")
            size = os.path.getsize(path)
            self.assertGreater(size, 1500, f"Document {doc} is too small ({size} bytes)")
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                words = len(content.split())
                self.assertGreater(words, 200, f"Document {doc} lacks sufficient words ({words} words)")

    def test_03_submission_manifest_valid_and_consistent(self):
        """Assert phase14_final_submission_manifest.json exists, is valid JSON, and contains all required keys."""
        self.assertTrue(os.path.exists(self.manifest_path), "Final submission manifest missing")
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_keys = [
            "git_commit",
            "model_hash",
            "dataset_hashes",
            "provider_status",
            "model_status",
            "iot_status",
            "safety_state",
            "remaining_limitations",
            "verdict"
        ]
        for k in required_keys:
            self.assertIn(k, data, f"Manifest missing key: {k}")

        self.assertEqual(data["verdict"], "SUBMISSION_FREEZE_READY")
        self.assertEqual(data["model_status"]["status"] if "status" in data["model_status"] else data["model_status"]["event_classifier"], "TRAINED_LIMITED_DATA")
        self.assertIn("SURROGATE", data["model_status"]["lstm_temporal"])
        self.assertEqual(data["iot_status"]["overall"], "SIMULATED")

    def test_04_ui_sensor_truth_and_no_ambiguous_online_tags(self):
        """Assert templates/index.html uses unambiguous sensor truth terminology."""
        with open(self.index_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Telemetry truth badges
        self.assertIn("[SIMULATED: DEPLOYMENT NOT VERIFIED]", html)
        self.assertIn("BENCH SIMULATION", html)
        self.assertIn("18/20 (Bench)", html)
        self.assertIn("Local Siren", html)
        self.assertIn("DRY RUN", html)

    def test_05_ui_pipeline_ribbon_and_truth_matrix_and_cards(self):
        """Assert 8-stage decision ribbon, Data Truth Matrix modal, and limitation cards in index.html."""
        with open(self.index_path, "r", encoding="utf-8") as f:
            html = f.read()

        # 8-Stage Ribbon
        self.assertIn('id="pahad-pipeline-ribbon"', html)
        self.assertIn("DATA", html)
        self.assertIn("PHYSICS", html)
        self.assertIn("MULTI-SOURCE EVIDENCE", html)
        self.assertIn("PAHAD AI", html)
        self.assertIn("CORROBORATION", html)
        self.assertIn("AUTHORITY DECISION", html)

        # Modals
        self.assertIn('id="modal-data-truth-matrix"', html)
        self.assertIn('id="modal-scientific-expl"', html)

        # Cards
        self.assertIn('id="card-why-parvat-netra"', html)
        self.assertIn('id="card-current-limitations"', html)

    def test_06_ppt_deck_forensic_parity_and_provenance(self):
        """Assert presentation deck has 8 slides and contains honest provenance terms."""
        self.assertTrue(os.path.exists(self.deck_path), f"Deck not found at {self.deck_path}")
        prs = Presentation(self.deck_path)
        self.assertEqual(len(prs.slides), 8, f"Expected 8 slides, found {len(prs.slides)}")

        full_deck_text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    full_deck_text += " " + shape.text_frame.text

        # Verify critical scientific honesty terms
        self.assertIn("SIMULATED", full_deck_text)
        self.assertIn("TRAINED_LIMITED_DATA", full_deck_text)
        self.assertIn("SURROGATE", full_deck_text)
        self.assertIn("LIVE", full_deck_text)
        self.assertIn("HISTORICAL", full_deck_text)
        self.assertIn("17 Events / N=8 Test", full_deck_text)

    def test_07_safety_environment_interlocks(self):
        """Assert all six emergency safety environment flags default to locked fail-safe values."""
        self.assertEqual(int(os.getenv("ENABLE_PUBLIC_DISPATCH", "0")), 0)
        self.assertEqual(int(os.getenv("SIREN_DRY_RUN", "1")), 1)
        self.assertEqual(int(os.getenv("CAP_PRODUCTION_DISPATCH", "0")), 0)
        self.assertEqual(int(os.getenv("SACHET_PRODUCTION_DISPATCH", "0")), 0)
        self.assertEqual(int(os.getenv("CELL_BROADCAST_PRODUCTION", "0")), 0)
        self.assertEqual(int(os.getenv("PUBLIC_DEMO_TEST_ONLY", "1")), 1)

    def test_08_rbac_authority_mode_tamper_proofing(self):
        """Assert unauthenticated requests with ?mode=authority render the safe public interface."""
        client = app.test_client()
        res = client.get("/?mode=authority")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        # Authority actionable buttons should be hidden for unauthenticated visitor
        self.assertIn("PARVAT NETRA", html)


if __name__ == "__main__":
    unittest.main()
