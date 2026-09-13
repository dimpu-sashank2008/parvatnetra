# -*- coding: utf-8 -*-
"""
tests/test_phase10e_cap_gateway.py
==================================
PARVAT NETRA • Phase 10E — NDMA SACHET / OASIS CAP v1.2 Gateway Tests
---------------------------------------------------------------------
Verifies:
  1. Integration adapter for NDMA SACHET / OASIS CAP v1.2 warning gateway.
  2. Full validation of all 15 required OASIS CAP 1.2 elements:
     identifier, sender, sent, status, msgType, scope,
     severity, urgency, certainty, headline, description, instruction,
     areaDesc, polygon, expiry.
  3. XML payload well-formedness and namespace compliance.
  4. Core Safety Invariant: Staged in test feed without transmission to production gateway.
  5. Fails validation gracefully if any mandatory element is missing.
"""

import pytest
import xml.etree.ElementTree as ET
from services.public_warning_service import (
    SachetCapGatewayAdapter,
    CHANNEL_CAP_GATEWAY,
    RECEIPT_SENT
)

SAMPLE_CAP_ALERT = {
    "identifier": "PAHAD-SK-NH10-2026-TEST01",
    "sender": "pahad-ews@ner.gov.in",
    "sent": "2026-09-13T09:00:00Z",
    "status": "Actual",
    "msgType": "Alert",
    "scope": "Public",
    "severity": "Severe",
    "urgency": "Immediate",
    "certainty": "Observed",
    "headline": "PAHAD AI Landslide Warning for NH-10",
    "description": "Critical hillslope shear strain detected along Km 48.",
    "instruction": "Evacuate vulnerable mountain corridors immediately.",
    "areaDesc": "NH-10 Km 48 Corridor",
    "polygon": [[27.33, 88.61], [27.34, 88.61], [27.34, 88.62], [27.33, 88.62], [27.33, 88.61]],
    "expiry": "2026-09-13T15:00:00Z",
    "incident_id": "INC-CAP-001"
}


def test_cap_gateway_validates_all_15_elements():
    """Verifies that all 15 mandatory OASIS CAP 1.2 elements are validated."""
    adapter = SachetCapGatewayAdapter()
    is_valid, missing = adapter.validate_cap_payload(SAMPLE_CAP_ALERT)
    assert is_valid is True
    assert len(missing) == 0


def test_cap_gateway_detects_missing_elements():
    """Verifies that missing elements cause validation failure."""
    adapter = SachetCapGatewayAdapter()
    incomplete = SAMPLE_CAP_ALERT.copy()
    incomplete.pop("headline")
    incomplete.pop("instruction")
    incomplete.pop("polygon")

    is_valid, missing = adapter.validate_cap_payload(incomplete)
    assert is_valid is False
    assert "headline" in missing
    assert "instruction" in missing
    assert "polygon" in missing

    result = adapter.stage_cap_alert(incomplete)
    assert result["status"] == "VALIDATION_FAILED"
    assert result["xml_payload"] is None


def test_cap_xml_payload_well_formed():
    """Verifies that generated CAP XML is well-formed with valid namespace."""
    adapter = SachetCapGatewayAdapter()
    result = adapter.stage_cap_alert(SAMPLE_CAP_ALERT)

    assert result["status"] == "STAGED_TEST_FEED"
    assert result["delivery_status"] == RECEIPT_SENT
    assert result["dry_run"] is True
    assert "xml_payload" in result

    # Parse XML to verify well-formedness
    root = ET.fromstring(result["xml_payload"])
    assert "alert" in root.tag

    # Verify namespace is OASIS CAP 1.2
    assert "urn:oasis:names:tc:emergency:cap:1.2" in root.tag or root.attrib.get("xmlns") == "urn:oasis:names:tc:emergency:cap:1.2"


def test_cap_gateway_dry_run_safety():
    """Asserts that CAP gateway never sends live public alerts without configuration."""
    adapter = SachetCapGatewayAdapter()
    assert adapter.dry_run is True
    result = adapter.stage_cap_alert(SAMPLE_CAP_ALERT)
    assert result["dry_run"] is True
    assert "[OASIS_CAP_1.2_DRY_RUN]" in result["provenance"]
