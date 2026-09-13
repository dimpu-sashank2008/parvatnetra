"""
Test Suite: Emergency SMS Gateway Service (Phase 3.5)
Validates multilingual templates, strict < 160-char constraint,
privacy-preserving masked recipient handling, and DRY_RUN invariants.
"""
import os
import unittest

os.environ["PARVAT_TESTING"] = "1"

from services.sms_service import SMSService, MockSMSProvider, CDACSMSProvider, SMS_TEMPLATES


class TestSMSService(unittest.TestCase):
    """Tests SMS service template formatting and safe dispatch."""

    def setUp(self):
        self.service = SMSService(dry_run=True, provider_name="mock")

    def test_multilingual_templates_presence(self):
        """All required regional and national languages must be present."""
        for lang in ["en", "hi", "ne", "bh", "lp", "as"]:
            self.assertIn(lang, SMS_TEMPLATES)

    def test_sms_character_length_limit(self):
        """All rendered templates must be strictly under single-segment 160 chars."""
        test_alert_id = "ALT-202609-S14-001"
        test_level = "VERY HIGH WARNING"

        for lang, template in SMS_TEMPLATES.items():
            msg = self.service.format_sms_message(test_alert_id, test_level, language=lang)
            self.assertLessEqual(
                len(msg),
                160,
                f"Language '{lang}' exceeded single-segment 160 characters ({len(msg)} chars): {msg}"
            )
            self.assertIn(test_alert_id, msg)

    def test_sms_dispatch_dry_run_safety(self):
        """Emergency SMS dispatch in dry-run mode returns SIMULATED_SENT without live telecom calls."""
        record = self.service.send_emergency_sms(
            recipient_id="REC-SDRF-01",
            phone_masked="+91-XXXXX-1234",
            alert_id="ALT-TEST-99",
            level_name="EXTREME",
            language="ne"
        )
        self.assertEqual(record.status, "SIMULATED_SENT")
        self.assertTrue(record.dry_run)
        self.assertEqual(record.provenance, "[DRY RUN]")
        self.assertEqual(record.phone_masked, "+91-XXXXX-1234")
        self.assertEqual(record.language, "ne")

        # History log updated
        history = self.service.list_recent_sms()
        self.assertGreaterEqual(len(history), 1)
        self.assertEqual(history[0]["sms_id"], record.sms_id)

    def test_mock_sms_provider_direct(self):
        """Verify MockSMSProvider response contracts."""
        mock_p = MockSMSProvider()
        res = mock_p.send("+91-XXXXX-9999", "Test alert message")
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "SIMULATED_DELIVERY")
        self.assertGreater(res["chars_remaining"], 0)

    def test_cdac_sms_provider_unconfigured_safety(self):
        """Unconfigured CDAC provider safely rejects without crashing."""
        cdac = CDACSMSProvider(username="", password="")
        self.assertFalse(cdac.is_configured)
        res = cdac.send("+91-99999-99999", "Emergency Test")
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "FAILED_UNCONFIGURED_CREDENTIALS")


if __name__ == "__main__":
    unittest.main()
