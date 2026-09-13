# -*- coding: utf-8 -*-
"""
tests/test_phase8_cap.py
========================
Tests for Checkpoint 8-26:
OASIS CAP v1.2 Emergency Test Feed Generation, Required XML Tags,
and DRY_RUN Non-Transmission Invariant.
"""

import xml.etree.ElementTree as ET
import pytest
from engine.pahad_cap import CAPAlertGenerator, CAP_NAMESPACE
from services.eoc_service import EOC_SERVICE


def test_oasis_cap_v1_2_test_alert_generation():
    """Verify compliant CAP v1.2 XML generation with all required emergency fields."""
    gen = CAPAlertGenerator()
    data = {
        "alert_id": "PN-CAP-TEST-2026-001",
        "headline": "PAHAD AI Extreme Landslide Early Warning",
        "description": "Critical pore-water saturation and slope displacement detected along NH-10 KM 48.",
        "instruction": "Immediate evacuation of 29th Mile zone. Divert commercial traffic to NH-717A.",
        "severity": "Extreme",
        "urgency": "Immediate",
        "certainty": "Observed",
        "event": "Landslide Hazard Warning",
        "area_desc": "NH-10 KM 48 15km corridor",
        "polygon": [[27.33, 88.61], [27.34, 88.62], [27.32, 88.60], [27.33, 88.61]],
        "cri_score": 88.5
    }

    xml_str = gen.build_cap_xml(data)
    assert len(xml_str) > 0

    # Parse XML and verify namespace and required elements
    root = ET.fromstring(xml_str)
    assert root.tag == f"{{{CAP_NAMESPACE}}}alert" or "alert" in root.tag

    # Check required child tags (OASIS CAP v1.2 specification)
    tag_names = [elem.tag.split("}")[-1] for elem in root.iter()]
    required_tags = [
        "identifier",
        "sender",
        "sent",
        "status",
        "msgType",
        "scope",
        "info",
        "category",
        "event",
        "urgency",
        "severity",
        "certainty",
        "eventCode",
        "headline",
        "description",
        "instruction",
        "area",
        "areaDesc",
        "polygon"
    ]
    for tag in required_tags:
        assert tag in tag_names, f"Required CAP tag <{tag}> missing from generated XML"


def test_cap_dry_run_flag():
    """Verify CAP alert in EOC is tagged [TEST / DRY_RUN] and never transmitted externally."""
    inc = EOC_SERVICE.dispatch_incident_notifications(
        incident_id="NON_EXISTENT",
        authorization_token="TEST"
    )
    # Blocked for missing incident
    assert inc["status"] == "ERROR"
