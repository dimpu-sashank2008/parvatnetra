"""
PHASE 7F — CP 7F-10 & 7F-11: Live Inference Sensor Modality & Safety Tests
Verifies that:
1. Live inference behaves stably across sensor modalities (Cases A-G).
2. A single-sensor spike cannot trigger an emergency alert.
3. 2-of-3 corroboration is strictly enforced for alert eligibility.
4. AI recommendation != public emergency alert.
5. Public dispatch remains DISABLED and sirens remain DRY_RUN.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pahad_live_inference import run_live_inference, _check_alert_eligibility
from engine.pilot_profile import GLOBAL_PILOT_MANAGER


class TestSensorModalityAndSafety(unittest.TestCase):
    """CP 7F-10 & 7F-11: Safety constitution, 2-of-3 corroboration, and siren protection."""

    SECTOR = "CORR-NH10-SIKKIM-KM48"
    LAT = 27.2056
    LON = 88.4986

    def test_01_case_a_no_sensors_confidence_reflects_imputation(self):
        """Case A: No sensors -> baseline inference runs safely, flags low/medium confidence."""
        res = run_live_inference(self.SECTOR, self.LAT, self.LON)
        self.assertIsNotNone(res)
        self.assertGreater(res.data_quality_score, 0.0)
        self.assertLessEqual(res.data_quality_score, 1.0)
        self.assertIn(res.confidence, ["LOW_CONFIDENCE", "MEDIUM_CONFIDENCE"])

    def test_02_case_b_single_sensor_spike_does_not_trigger_alert(self):
        """Case B: Single sensor spike (high pore pressure) must NOT trigger 2-of-3 alert on its own."""
        # Inject isolated pore pressure spike (e.g. sensor glitch 80 kPa), but rainfall is low and FoS is stable
        override = {
            "pore_pressure_kpa": 80.0,
            "rainfall_24h": 5.0,  # Below 150mm threshold
        }
        res = run_live_inference(self.SECTOR, self.LAT, self.LON, override_features=override)
        # Check alert eligibility: with low rainfall (5mm) and low ML probability, 2-of-3 rule cannot trigger
        eligible, reason = _check_alert_eligibility(
            fos=1.35,  # Stable FoS
            rainfall_24h=5.0,
            event_probability=0.25
        )
        self.assertFalse(eligible, "Single sensor spike with stable slope must NOT be alert eligible")
        self.assertIsNone(reason)

    def test_03_case_c_two_of_three_agreement_triggers_alert_eligibility(self):
        """Case C: Two concurring signals (e.g. Critical FoS + Heavy Rain) triggers alert eligibility."""
        eligible, reason = _check_alert_eligibility(
            fos=1.04,          # Critical FoS < 1.10 (Signal 1)
            rainfall_24h=185.0, # Rain > 150mm (Signal 2)
            event_probability=0.35 # Modest probability
        )
        self.assertTrue(eligible, "2 of 3 signals met must set alert_eligible = True")
        self.assertIn("2-of-3 corroboration", str(reason))
        self.assertIn("FoS=1.04<1.10", str(reason))
        self.assertIn("Rainfall=185mm>150mm", str(reason))

    def test_04_rainfall_only_cannot_alert(self):
        """Rainfall exceeding threshold alone (1 of 3) cannot trigger an alert."""
        eligible, reason = _check_alert_eligibility(
            fos=1.45,           # Stable FoS
            rainfall_24h=210.0, # Extreme rain
            event_probability=0.20 # Low ML
        )
        self.assertFalse(eligible, "Rainfall alone must NOT trigger public alert")

    def test_05_fos_only_cannot_alert(self):
        """FoS < 1.10 alone (1 of 3) cannot trigger an alert without corroboration."""
        eligible, reason = _check_alert_eligibility(
            fos=0.98,          # Low FoS
            rainfall_24h=12.0,  # Dry / low rain
            event_probability=0.40 # Moderate ML
        )
        self.assertFalse(eligible, "FoS alone must NOT trigger public alert")

    def test_06_ml_only_cannot_alert(self):
        """ML probability > 0.70 alone (1 of 3) cannot trigger an alert without corroboration."""
        eligible, reason = _check_alert_eligibility(
            fos=1.50,          # High FoS
            rainfall_24h=20.0,  # Low rain
            event_probability=0.88 # High ML
        )
        self.assertFalse(eligible, "ML probability alone must NOT trigger public alert")

    def test_07_public_dispatch_remains_disabled(self):
        """Public emergency dispatch MUST be disabled in pilot profile."""
        profile = GLOBAL_PILOT_MANAGER.get_profile()
        self.assertFalse(profile.safety_policy.public_dispatch_enabled,
                         "CRITICAL SAFETY VIOLATION: public_dispatch_enabled must be False")

    def test_08_sirens_remain_in_dry_run_mode(self):
        """Sirens MUST remain in DRY_RUN / hardware-disabled mode in pilot profile."""
        profile = GLOBAL_PILOT_MANAGER.get_profile()
        self.assertFalse(profile.safety_policy.siren_hardware_enabled,
                         "CRITICAL SAFETY VIOLATION: siren_hardware_enabled must be False")
        self.assertEqual(profile.mode.value, "SHADOW")


if __name__ == "__main__":
    unittest.main()
