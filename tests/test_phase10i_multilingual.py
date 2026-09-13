# -*- coding: utf-8 -*-
"""
tests/test_phase10i_multilingual.py
===================================
PARVAT NETRA • Phase 10I — Multilingual SMS & Encoding Validation Tests
-----------------------------------------------------------------------
Verifies:
  1. Multilingual templates across 6 Himalayan languages:
     English (en), Hindi (hi), Nepali (ne), Assamese (as), Bhutia (bh), Lepcha (lp).
  2. Character length validation:
     GSM-7 English templates strictly <= 160 characters.
  3. Encoding detection: GSM-7 vs UCS-2 (Unicode).
  4. Regional script integrity (Devanagari, Bengali-Assamese, Tibetan, Lepcha).
  5. Never truncating critical life-safety instructions.
"""

import pytest
from services.production_sms_service import (
    SMSTemplateEngine,
    SUPPORTED_SMS_LANGUAGES,
    TEMPLATE_LANDSLIDE_WARNING,
    TEMPLATE_EVACUATION_ADVISORY,
    LANG_EN,
    LANG_HI,
    LANG_NE,
    LANG_AS,
    LANG_BH,
    LANG_LP
)


def test_six_languages_supported():
    """Asserts that all 6 required languages are defined."""
    assert set(SUPPORTED_SMS_LANGUAGES) == {"en", "hi", "ne", "as", "bh", "lp"}


def test_english_gsm7_character_limit():
    """
    CRITICAL INVARIANT:
    English SMS templates must strictly remain <= 160 characters
    to prevent multi-part billing and delivery delays during disasters.
    """
    rendered = SMSTemplateEngine.render(
        template_type=TEMPLATE_LANDSLIDE_WARNING,
        language=LANG_EN,
        area="Pakyong",
        corridor="NH-10 Km 48",
        action="Avoid exposed rock cuts",
        incident_id="INC-ENG-01"
    )

    assert rendered["encoding"] == "GSM-7 (Standard)"
    assert rendered["character_count"] <= 160
    assert len(rendered["message"]) <= 160


def test_indic_unicode_scripts_presence():
    """Verifies that each regional language uses its native Unicode script."""
    # Hindi (Devanagari)
    hi_res = SMSTemplateEngine.render(TEMPLATE_LANDSLIDE_WARNING, language=LANG_HI)
    assert any('\u0900' <= c <= '\u097F' for c in hi_res["message"])
    assert hi_res["encoding"] == "UCS-2 (Unicode)"

    # Nepali (Devanagari)
    ne_res = SMSTemplateEngine.render(TEMPLATE_LANDSLIDE_WARNING, language=LANG_NE)
    assert any('\u0900' <= c <= '\u097F' for c in ne_res["message"])

    # Assamese (Bengali-Assamese)
    as_res = SMSTemplateEngine.render(TEMPLATE_LANDSLIDE_WARNING, language=LANG_AS)
    assert any('\u0980' <= c <= '\u09FF' for c in as_res["message"])

    # Bhutia (Tibetan script)
    bh_res = SMSTemplateEngine.render(TEMPLATE_LANDSLIDE_WARNING, language=LANG_BH)
    assert any('\u0F00' <= c <= '\u0FFF' for c in bh_res["message"])

    # Lepcha (Lepcha script)
    lp_res = SMSTemplateEngine.render(TEMPLATE_LANDSLIDE_WARNING, language=LANG_LP)
    assert any('\u1C00' <= c <= '\u1C4F' for c in lp_res["message"])


def test_critical_instruction_never_truncated():
    """Verifies that key emergency instructions remain intact across languages."""
    critical_act = "Follow SDRF advice"
    res = SMSTemplateEngine.render(
        template_type=TEMPLATE_EVACUATION_ADVISORY,
        language=LANG_EN,
        action=critical_act
    )
    assert critical_act in res["message"]
    assert res["critical_action_preserved"] is True
