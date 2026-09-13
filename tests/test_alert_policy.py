"""
Test Suite: PAHAD AI Alert Policy (Phase 3.5)
Validates alert level escalation, 2-of-3 signal concordance, hysteresis,
and multi-modal 'Why this alert?' explainability.
"""
import os
import unittest

os.environ["PARVAT_TESTING"] = "1"

from engine.pahad_alert_policy import (
    PahadAlertPolicyEngine,
    AlertPolicyDecision,
    ALERT_LEVEL_MAPPINGS,
)


class TestPahadAlertPolicy(unittest.TestCase):
    """Tests multi-signal alert policy, 2-of-3 signal gate, and explainability."""

    def setUp(self):
        self.engine = PahadAlertPolicyEngine(deescalation_hysteresis_cycles=3)

    def test_low_risk_evaluation(self):
        """Stable slope, low rainfall, low ML prob -> LOW / monitoring."""
        res = self.engine.evaluate(
            cri=15.0,
            event_probability=0.15,
            factor_of_safety=1.85,
            rainfall_trigger=False,
            signal_agreement="0/3",
            sector_id="S01_PELLING",
        )
        self.assertEqual(res.recommended_alert_level, "LOW")
        self.assertEqual(res.alert_level_name, "monitoring")
        self.assertFalse(res.authorization_required)
        self.assertFalse(res.public_dispatch_allowed)
        self.assertEqual(res.signal_agreement_count, 0)

    def test_moderate_risk_evaluation(self):
        """Elevated moisture or moderate prob -> MODERATE / watch."""
        res = self.engine.evaluate(
            cri=32.0,
            event_probability=0.38,
            factor_of_safety=1.35,
            rainfall_trigger=False,
            signal_agreement="0/3",
            sector_id="S02_GANGTOK",
        )
        self.assertEqual(res.recommended_alert_level, "MODERATE")
        self.assertEqual(res.alert_level_name, "watch")
        self.assertFalse(res.authorization_required)

    def test_high_risk_evaluation(self):
        """Elevated pore pressure or CRI >= 40 -> HIGH / warning."""
        res = self.engine.evaluate(
            cri=52.0,
            event_probability=0.55,
            factor_of_safety=1.10,
            rainfall_trigger=False,
            signal_agreement="1/3",
            sector_id="S03_NAMCHI",
        )
        self.assertEqual(res.recommended_alert_level, "HIGH")
        self.assertEqual(res.alert_level_name, "warning")
        self.assertTrue(res.authorization_required)
        self.assertFalse(res.public_dispatch_allowed)

    def test_two_of_three_signal_rule_extreme_risk(self):
        """2 or more signals concordant with CRI >= 80 and ML prob >= 0.75 -> EXTREME."""
        res = self.engine.evaluate(
            cri=88.0,
            event_probability=0.85,
            factor_of_safety=0.72,
            rainfall_trigger="EXCEEDED",
            signal_agreement="3/3",
            ground_anomaly=0.82,
            sector_id="S14_NH10_KM48",
        )
        self.assertEqual(res.recommended_alert_level, "EXTREME")
        self.assertEqual(res.alert_level_name, "extreme alert")
        self.assertTrue(res.authorization_required)
        self.assertTrue(res.public_dispatch_allowed)
        self.assertFalse(res.downgraded)
        self.assertGreaterEqual(res.signal_agreement_count, 2)
        self.assertIn("Critical", " ".join(res.dominant_drivers))
        self.assertIn("Rainfall Threshold Exceeded", " ".join(res.dominant_drivers))

    def test_downgrade_when_lacking_second_signal(self):
        """If raw level would be EXTREME but signal agreement < 2, downgrade to VERY_HIGH."""
        res = self.engine.evaluate(
            cri=85.0,
            event_probability=0.82,
            factor_of_safety=1.60,  # stable physical slope
            rainfall_trigger=False,  # no rainfall breach
            signal_agreement=1,     # only ML signal
            sector_id="S05_TEST",
        )
        self.assertEqual(res.recommended_alert_level, "VERY_HIGH")
        self.assertTrue(res.downgraded)
        self.assertIsNotNone(res.downgrade_reason)
        self.assertIn("2-of-3 independent confirmation rule", res.downgrade_reason)

    def test_explainability_dominant_drivers(self):
        """Verify non-causal explainability text contains specific triggers."""
        res = self.engine.evaluate(
            cri=78.0,
            event_probability=0.74,
            factor_of_safety=0.82,
            rainfall_trigger="EXCEEDED",
            signal_agreement="2/3",
            sector_id="S14_NH10_KM48",
        )
        self.assertGreaterEqual(len(res.dominant_drivers), 2)
        driver_str = " ".join(res.dominant_drivers)
        self.assertIn("FoS Critical", driver_str)
        self.assertIn("Rainfall", driver_str)

    def test_hysteresis_and_de_escalation(self):
        """De-escalation from EXTREME to LOW must step down gradually when history has high entries."""
        sector = "S14_HYST_TEST"
        # Simulate 3 high/extreme readings
        for _ in range(3):
            self.engine.evaluate(
                cri=85.0,
                event_probability=0.85,
                factor_of_safety=0.70,
                rainfall_trigger=True,
                signal_agreement=3,
                sector_id=sector,
            )

        # Candidate now drops to LOW
        step_down = self.engine.evaluate_deescalation(sector, "LOW")
        # Should step down gradually (e.g. VERY_HIGH or HIGH) rather than crashing straight to LOW
        self.assertIn(step_down, ["VERY_HIGH", "HIGH", "EXTREME"])


if __name__ == "__main__":
    unittest.main()
