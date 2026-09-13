import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
from engine.pahad_fusion import PahadFusionEngine, PAHAD_FUSION_ENGINE


class TestPahadFusion(unittest.TestCase):
    """Tests PAHAD AI Multimodal Fusion Engine and 2-of-3 Safety Invariant."""

    def setUp(self):
        self.engine = PahadFusionEngine()

    def test_default_weights_and_constants(self):
        """Verify standard CRI weights alpha=0.40, beta=0.35, gamma=0.25 sum to 1.0."""
        self.assertAlmostEqual(self.engine.alpha + self.engine.beta + self.engine.gamma, 1.0)
        self.assertEqual(self.engine.alpha, 0.40)
        self.assertEqual(self.engine.beta, 0.35)
        self.assertEqual(self.engine.gamma, 0.25)

    def test_two_of_three_agreement_confirmed_extreme_alert(self):
        """When 2 or more signals agree (e.g. FoS <= 1.0 and Rain Exceeded), EXTREME alert is confirmed."""
        result = self.engine.fuse(
            sector_id="S14",
            susceptibility_score=0.88,
            rainfall_mm=140.0,
            rainfall_threshold_exceeded=True,
            fos_physical=0.89,  # Unstable (< 1.0) -> Signal 1
            event_probability_24h=0.84,  # High ML (> 0.80) -> Signal 2
            vulnerability_score=0.92,
        )

        self.assertIn("cri", result)
        self.assertGreaterEqual(result["cri"], 80.0)
        self.assertEqual(result["risk_band"], "EXTREME")
        self.assertIn("3/3", result["model_agreement"])  # All three signals confirmed
        self.assertTrue(result["agreement_confirmed"])

    def test_two_of_three_unconfirmed_downgrade(self):
        """When CRI >= 80 but ONLY 1 signal is met, alert must be downgraded to VERY_HIGH <= 79.9."""
        result = self.engine.fuse(
            sector_id="S02",
            raw_cri=84.0,
            susceptibility_score=0.95,
            rainfall_mm=15.0,
            rainfall_threshold_exceeded=False,  # Rain normal
            fos_physical=1.45,  # Physically stable (> 1.0)
            event_probability_24h=0.88,  # Only ML is elevated -> Only 1 of 3!
            vulnerability_score=0.95,
        )

        # Safety invariant enforces downgrade
        self.assertLessEqual(result["cri"], 79.9, "Unconfirmed EXTREME must be capped at 79.9")
        self.assertEqual(result["risk_band"], "VERY_HIGH")
        self.assertFalse(result["agreement_confirmed"])
        self.assertTrue(result.get("downgraded_by_safety_policy", False))
        self.assertIn("1/3", result["model_agreement"])

    def test_top_drivers_explainability_non_causal(self):
        """Ensure explainability drivers do not claim causal certainty ('caused the landslide')."""
        result = self.engine.fuse(
            sector_id="S05",
            susceptibility_score=0.75,
            rainfall_mm=95.0,
            rainfall_threshold_exceeded=True,
            fos_physical=0.92,
            event_probability_24h=0.76,
        )

        drivers = result.get("top_drivers", [])
        self.assertGreater(len(drivers), 0)
        for d in drivers:
            name = d.get("driver", "").lower()
            desc = d.get("description", "").lower()
            self.assertNotIn("caused the landslide", name)
            self.assertNotIn("caused the landslide", desc)
            self.assertIn(d.get("category"), ["CRITICAL", "PRIMARY", "SECONDARY", "SUPPORTING"])

    def test_singleton_engine_availability(self):
        """Verify module singleton is initialized and responsive."""
        self.assertIsNotNone(PAHAD_FUSION_ENGINE)
        res = PAHAD_FUSION_ENGINE.fuse(sector_id="S_TEST")
        self.assertIn("risk_band", res)
        self.assertIn("data_provenance", res)


if __name__ == "__main__":
    unittest.main()
