# -*- coding: utf-8 -*-
"""
tests/test_phase8_sitrep.py
===========================
Tests for Checkpoint 8-21 & 8-22:
Structured 15-Section Operational SITREP Generator & Command Brief Screen.
"""

import pytest
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER
from services.eoc_service import EOC_SERVICE


def test_sitrep_15_sections_generation():
    """Verify structured SITREP contains all 15 required operational sections."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=79.2,
        risk_band="HIGH",
        model_probability=0.82,
        FoS=1.01,
        rainfall=162.0,
        seismic_state="MINOR_TREMOR_M3.2",
        sensor_state="HEALTHY",
        signal_agreement="3/3 Corroborated"
    )

    sitrep = EOC_SERVICE.generate_sitrep(inc.incident_id)
    assert sitrep["incident_id"] == inc.incident_id
    assert sitrep["provenance"] == "[DETERMINISTIC_MEASUREMENTS_VERIFIED]"

    sections = sitrep["sections"]
    required_section_keys = [
        "1_SUMMARY",
        "2_CURRENT_RISK",
        "3_DRIVERS",
        "4_CONFIDENCE",
        "5_AFFECTED_AREA",
        "6_POPULATION",
        "7_ROADS",
        "8_FIELD_STATUS",
        "9_WEATHER",
        "10_SEISMIC",
        "11_SENSORS",
        "12_SATELLITE",
        "13_ACTIONS",
        "14_PENDING_DECISIONS",
        "15_NEXT_REVIEW_TIME",
    ]
    for key in required_section_keys:
        assert key in sections, f"SITREP section {key} missing from report"
        assert len(sections[key]) > 0


def test_command_brief_fields():
    """Verify one-screen command briefing fields (Checkpoint 8-22)."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=84.0,
        risk_band="CRITICAL",
        model_probability=0.87,
        FoS=0.96,
        rainfall=178.0
    )
    brief = EOC_SERVICE.generate_command_brief(inc.incident_id)

    assert brief["active_incident"] is True
    assert brief["incident_id"] == inc.incident_id
    assert brief["cri"] == 84.0
    assert brief["fos"] == 0.96
    assert brief["rain_24h_mm"] == 178.0
    assert brief["dispatch_status"] == "LOCKED_DRY_RUN"
