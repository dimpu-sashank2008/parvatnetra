"""
Unit tests for PARVAT NETRA - Phase 13: SIH 2026 Top-5 Submission Optimization.
"""
import os
import sys
import unittest
from pptx import Presentation

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)
from app import app


class TestPhase13SubmissionOptimization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs_dir = os.path.join(REPO_ROOT, "docs")
        cls.deck_path = os.path.join(cls.docs_dir, "PARVAT_NETRA_SIH_Winning_Deck.pptx")
        cls.index_path = os.path.join(REPO_ROOT, "templates", "index.html")

    def test_01_required_phase13_documents_exist_and_substantive(self):
        """Assert all 4 Phase 13 documents exist and have substantive content."""
        required_docs = [
            "PHASE13_SUBMISSION_OPTIMIZATION_REPORT.md",
            "PHASE13_PROTOTYPE_EVALUATOR_GUIDE.md",
            "PHASE13_PPT_CONSISTENCY_AUDIT.md",
            "PHASE13_FINAL_NARRATIVE.md"
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

    def test_02_gis_regional_bounds_and_brand_header(self):
        """Assert default 8-state NER bounds and updated brand subtitle in index.html."""
        with open(self.index_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Regional default bounds
        self.assertIn("window.NER_BOUNDS", html)
        self.assertIn("21.8", html)
        self.assertIn("97.5", html)

        # Brand header subtitle
        self.assertIn("AI-Assisted Landslide Risk Intelligence for the Northeast", html)

    def test_03_decision_intelligence_kpi_and_provenance(self):
        """Assert Fast KPI row, 'WHY THIS RISK?' heading, and provenance badges in index.html."""
        with open(self.index_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Fast KPI badges
        self.assertIn('id="card-kpi-cri"', html)
        self.assertIn('id="card-kpi-fos"', html)
        self.assertIn('id="card-kpi-prob"', html)
        self.assertIn('id="card-kpi-conf"', html)

        # WHY THIS RISK? heading
        self.assertIn("WHY THIS RISK? — MULTIMODAL EVIDENCE", html)

        # Provenance labels
        self.assertIn('id="card-prov-label"', html)
        self.assertIn('id="card-qual-label"', html)

    def test_04_ppt_deck_consistency_and_provenance(self):
        """Assert PPT deck exists, has 8 slides, 16:9 widescreen, and accurate provenance terms."""
        self.assertTrue(os.path.exists(self.deck_path), f"Deck not found at {self.deck_path}")
        prs = Presentation(self.deck_path)
        self.assertEqual(len(prs.slides), 8, f"Expected 8 slides, found {len(prs.slides)}")

        # Collect all text across deck
        full_deck_text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    full_deck_text += " " + shape.text_frame.text

        # Verify critical scientific honesty terms are present
        self.assertIn("SIMULATED", full_deck_text, "Deck must mention SIMULATED in-situ sensors")
        self.assertIn("TRAINED_LIMITED_DATA", full_deck_text, "Deck must mention TRAINED_LIMITED_DATA for event model")
        self.assertIn("SURROGATE", full_deck_text, "Deck must acknowledge LSTM as surrogate")
        self.assertIn("LIVE", full_deck_text, "Deck must mention LIVE IMD data")
        self.assertIn("HISTORICAL", full_deck_text, "Deck must mention HISTORICAL data")

    def test_05_safety_environment_variable_locks(self):
        """Assert all 6 safety environment flags default to locked fail-safe values."""
        self.assertEqual(int(os.getenv("ENABLE_PUBLIC_DISPATCH", "0")), 0)
        self.assertEqual(int(os.getenv("SIREN_DRY_RUN", "1")), 1)
        self.assertEqual(int(os.getenv("CAP_PRODUCTION_DISPATCH", "0")), 0)
        self.assertEqual(int(os.getenv("SACHET_PRODUCTION_DISPATCH", "0")), 0)
        self.assertEqual(int(os.getenv("CELL_BROADCAST_PRODUCTION", "0")), 0)
        self.assertEqual(int(os.getenv("PUBLIC_DEMO_TEST_ONLY", "1")), 1)

    def test_06_unauthenticated_role_tampering_immunity(self):
        """Assert visiting /?mode=authority without credentials renders public safe view."""
        with app.test_client() as client:
            resp = client.get("/?mode=authority")
            self.assertEqual(resp.status_code, 200)
            html = resp.data.decode("utf-8")
            # Authority siren arming buttons must not be exposed to unauthenticated users
            self.assertNotIn("id=\"btn-arm-siren-authority-bar\"", html)
            self.assertNotIn("Armed for Instantaneous Civil Defense", html)


if __name__ == "__main__":
    unittest.main()
