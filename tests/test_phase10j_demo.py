# -*- coding: utf-8 -*-
"""
tests/test_phase10j_demo.py
===========================
PARVAT NETRA • Phase 10J — Final Judge Demo End-to-End Tests
------------------------------------------------------------
Verifies:
  1. Recipient input handling (Email, Phone, Name, Language).
  2. Scenario hazard extraction with real system values (Sonapur CRI 40.6, FoS 0.926).
  3. No values invented: unconfigured features marked 'Data unavailable'.
  4. Judge-friendly professional alert message generation in 6 languages.
  5. Both channels independently reported without generic success masking.
"""

import pytest
from services.unified_notification_service import UNIFIED_NOTIFICATION_SERVICE


def test_scenario_hazard_resolution_sonapur():
    """Verifies Sonapur scenario resolves real system values without fabrication."""
    sc = UNIFIED_NOTIFICATION_SERVICE.resolve_scenario_hazard_condition("ML-SONAPUR-01")
    assert sc["sector_id"] == "ML-SONAPUR-01"
    assert "Sonapur" in sc["corridor_name"]
    assert sc["risk_level"] == "HIGH"
    assert sc["cri"] == 40.6
    assert sc["fos"] == 0.926
    assert "68.4" in sc["rainfall"]
    assert "Avoid unnecessary travel" in sc["action"]


def test_scenario_hazard_resolution_nh10():
    """Verifies NH-10 Km 48 scenario resolves extreme risk state."""
    sc = UNIFIED_NOTIFICATION_SERVICE.resolve_scenario_hazard_condition("SK-NH10-KM48")
    assert sc["sector_id"] == "SK-NH10-KM48"
    assert "NH-10" in sc["corridor_name"]
    assert sc["risk_level"] == "EXTREME"
    assert sc["cri"] == 86.2
    assert sc["fos"] == 0.890


def test_scenario_unknown_shows_data_unavailable():
    """Verifies unknown corridor does not invent data, shows 'Data unavailable'."""
    sc = UNIFIED_NOTIFICATION_SERVICE.resolve_scenario_hazard_condition("UNKNOWN-CORRIDOR-99")
    assert sc["cri"] == "Data unavailable"
    assert sc["fos"] == "Data unavailable"
    assert sc["rainfall"] == "Data unavailable"


def test_judge_message_multilingual_all_six():
    """Verifies message rendering preserves exact numbers across all 6 languages."""
    hazard = {
        "sector_id": "ML-SONAPUR-01",
        "corridor_name": "Sonapur Tunnel Corridor, Meghalaya",
        "risk_level": "HIGH",
        "cri": 40.6,
        "fos": 0.926,
        "rainfall": "68.4 mm/24h",
        "action": "Avoid unnecessary travel through the affected corridor and follow authority guidance."
    }
    inc_id = "PN-TEST-DEMO01"

    languages = ["en", "hi", "ne", "as", "bh", "lp"]
    for lang in languages:
        rendered = UNIFIED_NOTIFICATION_SERVICE.render_judge_demo_message(hazard, inc_id, language=lang)
        assert len(rendered["subject"]) > 0
        body = rendered["body_text"]
        assert len(body) > 0

        # Verify numerical invariants are NEVER translated or corrupted
        assert "40.6" in body
        assert "0.926" in body
        assert "68.4" in body
        assert inc_id in body
        assert "Sonapur" in body or "ML-SONAPUR-01" in body or "Location" in body or "स्थान" in body or "གནས་ཡུལ།" in body or "ᰜᰤᰵ" in body


def test_dual_test_dispatch_runs_both_channels():
    """Verifies dual test notification executes email and SMS independently."""
    res = UNIFIED_NOTIFICATION_SERVICE.dispatch_dual_test_notification(
        email_address="evaluator@sih.gov.in",
        phone_number="+919832011234",
        recipient_name="SIH Judge",
        language="en",
        scenario_id="ML-SONAPUR-01",
        is_test=True
    )

    assert res["success"] is True
    assert res["incident_id"].startswith("PN-TEST-")
    assert "EMAIL" in res["channels"]
    assert "SMS" in res["channels"]
    assert res["channels"]["EMAIL"]["status"] in ("SENT", "SIMULATED")
    assert res["channels"]["SMS"]["status"] in ("SENT", "SIMULATED")
    assert "[PARVAT NETRA TEST ALERT]" in res["test_banner"]
