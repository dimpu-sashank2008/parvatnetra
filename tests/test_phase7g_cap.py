# -*- coding: utf-8 -*-
"""
tests/test_phase7g_cap.py
=========================
Tests Checkpoints 7G-11 & 7G-12: OASIS CAP v1.2 Engine & Multi-Channel Notification Orchestration.
Verifies:
  1. Valid OASIS CAP v1.2 XML with authorizationReference parameter and closed polygon.
  2. Structured CAP v1.2 dictionary schema compliance.
  3. Multi-channel dispatch suppression when public dispatch is disabled.
  4. Multi-channel dispatch dry-run simulation (never delivered to real public).
  5. Siren hardware isolation invariant (strictly simulated/dry-run).
  6. Operator acknowledgement recording.
"""

import xml.etree.ElementTree as ET
import pytest
from engine.pahad_cap import CAPAlertGenerator, CAP_NAMESPACE
from services.notification_orchestrator import (
    NotificationOrchestrator,
    STATUS_SUPPRESSED,
    STATUS_SIMULATED,
    STATUS_DELIVERED
)

def test_cap_v1_2_xml_generation_with_auth_ref():
    generator = CAPAlertGenerator()
    alert_data = {
        "identifier": "PAHAD-SK-NH10-KM48-2026-TEST01",
        "sender": "pahad-ews@ner.gov.in",
        "sent": "2026-09-11T06:00:00Z",
        "status": "Actual",
        "msgType": "Alert",
        "scope": "Public",
        "category": "Geo",
        "event": "Landslide Hazard Warning",
        "urgency": "Immediate",
        "severity": "Extreme",
        "certainty": "Observed",
        "effective": "2026-09-11T06:00:00Z",
        "expires": "2026-09-11T12:00:00Z",
        "language": "en-IN",
        "headline": "PAHAD AI Critical Landslide Warning: NH-10 Km 48",
        "description": "Active slope failure detected. Evacuation required.",
        "instruction": "Divert traffic via NH-717A bypass corridor.",
        "authorization_reference": "AUTH-v1.SAMPLE_SIG",
        "areaDesc": "NH-10 Km 48 Pakyong Sector",
        "coordinates_polygon": [
            [27.3300, 88.6100],
            [27.3350, 88.6100],
            [27.3350, 88.6150],
            [27.3300, 88.6150]
        ]
    }

    xml_str = generator.build_cap_xml(alert_data)
    assert xml_str.startswith("<?xml")

    root = ET.fromstring(xml_str.encode("utf-8"))
    ns = {"cap": CAP_NAMESPACE}

    assert root.find("cap:identifier", ns).text == "PAHAD-SK-NH10-KM48-2026-TEST01"
    assert root.find("cap:msgType", ns).text == "Alert"

    info = root.find("cap:info", ns)
    assert info is not None
    assert info.find("cap:category", ns).text == "Geo"
    assert info.find("cap:severity", ns).text == "Extreme"
    assert info.find("cap:language", ns).text == "en-IN"

    # Verify authorizationReference parameter
    param_found = False
    for param in info.findall("cap:parameter", ns):
        vn = param.find("cap:valueName", ns)
        val = param.find("cap:value", ns)
        if vn is not None and vn.text == "authorizationReference":
            assert val.text == "AUTH-v1.SAMPLE_SIG"
            param_found = True
    assert param_found is True

    # Verify closed polygon
    area = info.find("cap:area", ns)
    poly = area.find("cap:polygon", ns).text.strip().split()
    assert len(poly) >= 4
    assert poly[0] == poly[-1], "Polygon must be closed (first == last point)"

def test_cap_dict_structure():
    generator = CAPAlertGenerator()
    data = {
        "sector_id": "SK-NH10-KM48",
        "severity": "Severe",
        "authorization_reference": "AUTH-TEST-REF"
    }
    res = generator.build_cap_dict(data)
    assert "identifier" in res
    assert res["status"] == "Actual"
    assert res["info"]["severity"] == "Severe"
    assert res["info"]["authorization_reference"] == "AUTH-TEST-REF"
    assert res["info"]["language"] == "en-IN"

def test_public_dispatch_suppressed_when_disabled(tmp_path):
    db_path = str(tmp_path / "notif_suppress.db")
    orch = NotificationOrchestrator(db_path=db_path)
    cap_data = orch.generate_cap_alert(
        alert_id="ALT-001",
        event="Test Event",
        severity="Severe",
        urgency="Expected",
        certainty="Likely",
        area_description="Test Area",
        instruction="Evacuate"
    )

    res = orch.dispatch_alert(
        alert_id="ALT-001",
        cap_payload=cap_data,
        channels=["SMS", "SIREN", "CAP", "PUSH"],
        public_dispatch_enabled=False
    )

    results = res["channel_results"]
    assert results["SMS"]["status"] == STATUS_SUPPRESSED
    assert results["SIREN"]["status"] == STATUS_SUPPRESSED
    assert results["CAP"]["status"] == STATUS_SUPPRESSED
    # Operational channel remains delivered or simulated
    assert results["PUSH"]["status"] in [STATUS_DELIVERED, STATUS_SIMULATED]

def test_dry_run_dispatch_simulation_and_siren_isolation(tmp_path):
    db_path = str(tmp_path / "notif_dryrun.db")
    orch = NotificationOrchestrator(db_path=db_path)
    cap_data = orch.generate_cap_alert(
        alert_id="ALT-002",
        event="Test Landslide",
        severity="Extreme",
        urgency="Immediate",
        certainty="Observed",
        area_description="NH10 Km 48",
        instruction="Immediate Evacuation"
    )

    res = orch.dispatch_alert(
        alert_id="ALT-002",
        cap_payload=cap_data,
        channels=["SMS", "SIREN", "PUSH"],
        authorization_token="AUTH-VALID-TOKEN",
        public_dispatch_enabled=True,
        dry_run=True
    )

    results = res["channel_results"]
    # SMS in dry_run must be SIMULATED, NEVER delivered to real carrier
    assert results["SMS"]["status"] == STATUS_SIMULATED
    # SIREN must ALWAYS be SIMULATED (hardware disabled)
    assert results["SIREN"]["status"] == STATUS_SIMULATED
    assert "hardware simulation" in results["SIREN"]["note"] or "Dry-run" in results["SIREN"]["note"]

def test_operator_acknowledgement_tracking(tmp_path):
    db_path = str(tmp_path / "notif_ack.db")
    orch = NotificationOrchestrator(db_path=db_path)
    cap_data = orch.generate_cap_alert(
        alert_id="ALT-003",
        event="Debris Flow",
        severity="Severe",
        urgency="Immediate",
        certainty="Likely",
        area_description="Pakyong",
        instruction="Deploy team"
    )

    res = orch.dispatch_alert(
        alert_id="ALT-003",
        cap_payload=cap_data,
        channels=["PUSH"],
        public_dispatch_enabled=False
    )
    notif_id = res["channel_results"]["PUSH"]["notification_id"]

    ack_res = orch.record_acknowledgement(
        notification_id=notif_id,
        acknowledged_by="OPERATOR_DUTY_DESK"
    )
    assert ack_res["notification_id"] == notif_id
    assert ack_res["acknowledged_by"] == "OPERATOR_DUTY_DESK"
    assert ack_res["acknowledged_at"] is not None
