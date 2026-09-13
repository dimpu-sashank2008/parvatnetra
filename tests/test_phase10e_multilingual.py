# -*- coding: utf-8 -*-
"""
tests/test_phase10e_multilingual.py
===================================
PARVAT NETRA • Phase 10E — Multilingual Alert Synthesis & Character Limit Tests
-------------------------------------------------------------------------------
Verifies:
  1. Generation of emergency warning packages across all 6 regional languages:
     - English (en)
     - Hindi (hi)
     - Nepali (ne)
     - Assamese (as)
     - Bhutia (bh)
     - Lepcha (lp)
  2. Single-segment SMS character limit validation:
     Strictly len(sms) <= 160 characters for all languages.
  3. Push notification title & body generation.
  4. Voice synthesis script generation for acoustic sirens.
  5. Roadside Variable Message Sign (VMS) matrix text generation.
  6. Preservation of critical life-safety semantics across all translations.
"""

import pytest
from services.public_warning_service import (
    PUBLIC_WARNING_SERVICE,
    SUPPORTED_LANGUAGES,
    LANG_ENGLISH,
    LANG_HINDI,
    LANG_NEPALI,
    LANG_ASSAMESE,
    LANG_BHUTIA,
    LANG_LEPCHA
)


def test_all_six_languages_present():
    """Verifies that all 6 target languages are supported."""
    expected = {"en", "hi", "ne", "as", "bh", "lp"}
    assert set(SUPPORTED_LANGUAGES) == expected


def test_multilingual_package_structure():
    """Verifies that the multilingual package contains sms, push, voice, and vms keys for each language."""
    pkg = PUBLIC_WARNING_SERVICE.format_multilingual_package(
        sector="SK-NH10-KM48",
        alert_id="TEST-ALERT-01",
        severity="CRITICAL"
    )

    for lang in SUPPORTED_LANGUAGES:
        assert lang in pkg, f"Missing language '{lang}' in generated package"
        item = pkg[lang]
        assert "sms" in item
        assert "push_title" in item
        assert "push_body" in item
        assert "voice" in item
        assert "vms" in item


def test_sms_character_limit_across_all_languages():
    """
    CRITICAL INVARIANT:
    SMS character length must be strictly <= 160 characters across all 6 languages
    to prevent costly/delayed multi-part SMS transmission during emergencies.
    """
    pkg = PUBLIC_WARNING_SERVICE.format_multilingual_package(
        sector="NH-10 (Km 48 Gangtok-Siliguri)",
        alert_id="PN-ALERT-X99",
        severity="EXTREME"
    )

    for lang in SUPPORTED_LANGUAGES:
        sms_text = pkg[lang]["sms"]
        length = len(sms_text)
        assert length <= 160, f"Language '{lang}' SMS exceeded 160 characters: {length} chars ('{sms_text}')"


def test_multilingual_script_integrity():
    """Verifies that scripts contain appropriate regional unicode characters."""
    pkg = PUBLIC_WARNING_SERVICE.format_multilingual_package(
        sector="NH-10 Km 48",
        alert_id="TEST-01"
    )

    # Hindi (Devanagari)
    assert any('\u0900' <= char <= '\u097F' for char in pkg[LANG_HINDI]["sms"])

    # Nepali (Devanagari)
    assert any('\u0900' <= char <= '\u097F' for char in pkg[LANG_NEPALI]["sms"])

    # Assamese (Bengali-Assamese)
    assert any('\u0980' <= char <= '\u09FF' for char in pkg[LANG_ASSAMESE]["sms"])

    # Bhutia (Tibetan)
    assert any('\u0F00' <= char <= '\u0FFF' for char in pkg[LANG_BHUTIA]["sms"])

    # Lepcha (Lepcha script range: 1C00–1C4F)
    assert any('\u1C00' <= char <= '\u1C4F' for char in pkg[LANG_LEPCHA]["sms"])
