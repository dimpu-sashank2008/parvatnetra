# -*- coding: utf-8 -*-
"""
tests/test_phase10j_multilingual.py
==================================
PARVAT NETRA • Phase 10J — Multilingual Alert Localization Tests
----------------------------------------------------------------
Verifies:
  1. Complete template rendering across all 6 Himalayan languages:
     English (en), Hindi (hi), Nepali (ne), Assamese (as), Bhutia (bh), Lepcha (lp).
  2. UTF-8 and UCS-2 Unicode encoding validity.
  3. Preservation of critical evacuation instructions without truncating actions.
  4. Both Email and SMS render in all 6 languages.
"""

import pytest
from services.email_service import ProductionEmailService
from services.production_sms_service import SMSTemplateEngine, VALID_TEMPLATES

LANGUAGES = ["en", "hi", "ne", "as", "bh", "lp"]


def test_sms_all_six_languages_renderable():
    """Verifies that all 6 languages render valid SMS messages with critical actions."""
    for lang in LANGUAGES:
        rendered = SMSTemplateEngine.render(
            template_type="LANDSLIDE_WARNING",
            language=lang,
            area="Mangan",
            corridor="North Sikkim Highway",
            risk_level="EXTREME",
            action="Move to designated shelter immediately",
            incident_id=f"INC-MULTI-{lang.upper()}"
        )

        assert rendered["language"] == lang
        assert len(rendered["message"]) > 0
        assert f"INC-MULTI-{lang.upper()}" in rendered["message"]
        assert rendered["critical_action_preserved"] is True

        # Encoding assertion
        if lang == "en":
            assert rendered["encoding"] == "GSM-7 (Standard)"
        else:
            assert rendered["encoding"] == "UCS-2 (Unicode)"


def test_email_all_six_languages_renderable():
    """Verifies that all 6 languages render multipart HTML and Text emails."""
    svc = ProductionEmailService()
    critical_action = "Seek shelter at high ground away from drainage channels"

    for lang in LANGUAGES:
        subject, text_body, html_body = svc.render_email_template(
            template_type="EVACUATION_ADVISORY",
            language=lang,
            area="Pakyong",
            corridor="NH-10 Km 48",
            risk_level="CRITICAL",
            action=critical_action,
            incident_id=f"INC-EML-{lang.upper()}",
            is_test=True
        )

        assert len(subject) > 0
        assert len(text_body) > 0
        assert len(html_body) > 0
        assert critical_action in text_body
        assert critical_action in html_body
        assert f"INC-EML-{lang.upper()}" in text_body
        assert f"INC-EML-{lang.upper()}" in html_body


def test_safety_action_never_truncated():
    """Verifies that even when character constraints apply, critical action advice is preserved."""
    long_action = "CRITICAL: Immediate evacuation ordered for all residents within 500m of the Teesta riverbank"
    rendered = SMSTemplateEngine.render(
        template_type="EVACUATION_ADVISORY",
        language="en",
        action=long_action
    )
    assert long_action in rendered["message"]
    assert rendered["critical_action_preserved"] is True
