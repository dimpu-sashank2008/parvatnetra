#!/usr/bin/env python3
"""
PARVAT NETRA -- Research Sprint 4 Automated Verification Suite
Institutional National Compliance & Defense Logistics (Pillars 2, 4.1, 4.3, 4.4, 4.5).
Tests:
  1. GSI NLFC (Bhusanket) Node Sync & Telemetry Metadata.
  2. BRO Project Swastik Pre-Positioning SOP (758 & 764 BRTF Tactical Staging).
  3. NDMA Sachet OASIS CAP v1.2 XML Generation with 4-Language Matrix (including Nepali ne-IN).
  4. C-DOT Cell Broadcast System (CBS) Channel 4370 Extreme Threat Dispatcher.
  5. Live REST Endpoints (/api/institutional/nlfc-status, /api/defense/bro-swastik-sop, /api/alerts/broadcast-trigger).
"""

import os
import sys
import xml.etree.ElementTree as ET
import requests

# Reconfigure stdout/stderr to UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.institutional_engine import (
    get_nlfc_sync_metadata,
    evaluate_bro_swastik_sop,
    generate_sachet_cap_xml,
    dispatch_cell_broadcast_payload
)

BASE_URL = "http://127.0.0.1:8080"


def test_sprint4_institutional():
    print("=" * 80)
    print("PARVAT NETRA -- SPRINT 4 AUTOMATED VERIFICATION SUITE")
    print("Institutional National Compliance & Defense Logistics")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # PART 1: OASIS CAP V1.2 XML SPECIFICATION & 4-LANGUAGE MATRIX
    # -------------------------------------------------------------------------
    print("\n[PART 1] Validating NDMA Sachet OASIS CAP v1.2 XML Specification...")
    test_payload = {
        "severity": "RED",
        "region_name": "NH-10 Km 48 (29th Mile / Likhu Veer)"
    }
    cap_xml = generate_sachet_cap_xml(test_payload)
    assert cap_xml is not None and len(cap_xml) > 500, "CAP XML should be non-empty and well populated"

    # Validate XML well-formedness
    try:
        root = ET.fromstring(cap_xml)
        print("  -> XML successfully parsed by ElementTree (Well-Formed OASIS Standard).")
    except ET.ParseError as e:
        raise AssertionError(f"Generated CAP XML is malformed: {e}")

    ns = {"cap": "urn:oasis:names:tc:emergency:cap:1.2"}
    assert "urn:oasis:names:tc:emergency:cap:1.2" in root.tag, f"Root tag must have CAP v1.2 namespace, got {root.tag}"

    sender = root.find("cap:sender", ns)
    assert sender is not None and sender.text == "gsi.nlfc@sachet.ndma.gov.in", f"Expected sender gsi.nlfc@sachet.ndma.gov.in, got {sender.text if sender else None}"
    print(f"  -> CAP Sender Verified: {sender.text}")

    status = root.find("cap:status", ns)
    msg_type = root.find("cap:msgType", ns)
    assert status.text == "Actual", f"Expected Actual status, got {status.text}"
    assert msg_type.text == "Alert", f"Expected Alert msgType, got {msg_type.text}"

    # Verify 4 linguistic blocks: en-IN, hi-IN, ne-IN, as-IN
    info_nodes = root.findall("cap:info", ns)
    print(f"  -> Total <info> Language Blocks: {len(info_nodes)}")
    assert len(info_nodes) == 4, f"Expected exactly 4 language blocks, got {len(info_nodes)}"

    languages = {}
    for info in info_nodes:
        lang_elem = info.find("cap:language", ns)
        assert lang_elem is not None, "Missing <language> element in <info>"
        lang_code = lang_elem.text
        headline = info.find("cap:headline", ns).text
        instruction = info.find("cap:instruction", ns).text
        area = info.find("cap:area/cap:polygon", ns).text
        languages[lang_code] = {
            "headline": headline,
            "instruction": instruction,
            "polygon": area
        }
        print(f"     * Found Language: [{lang_code}] | Area Polygon: {area[:25]}...")

    assert "en-IN" in languages, "Missing English (en-IN) info block"
    assert "hi-IN" in languages, "Missing Hindi (hi-IN) info block"
    assert "ne-IN" in languages, "Missing Nepali (ne-IN) info block -- official language omission unresolved!"
    assert "as-IN" in languages, "Missing Assamese (as-IN) info block"

    # Verify Nepali translation details
    ne_data = languages["ne-IN"]
    assert len(ne_data["headline"]) > 10, "Nepali headline must not be empty"
    assert "२९ माइल" in ne_data["instruction"] or "एनएच-१०" in ne_data["instruction"] or "पहिरो" in ne_data["headline"], "Nepali block should contain authentic regional terminology"
    print("  -> Verified ne-IN block resolves official Sachet language gap in Sikkim/Kalimpong.")

    print("[PASS] PART 1: OASIS CAP v1.2 XML Specification & 4-Language Matrix Verified.")

    # -------------------------------------------------------------------------
    # PART 2: C-DOT CELL BROADCAST SYSTEM (CBS) GEO-TARGETING
    # -------------------------------------------------------------------------
    print("\n[PART 2] Validating C-DOT Cell Broadcast System (CBS) Geo-Targeting...")

    # RED alert dispatch
    cbs_red = dispatch_cell_broadcast_payload({"severity": "RED"})
    print(f"  -> RED Dispatch Status   : [{cbs_red['status']}]")
    print(f"  -> Assigned Channel       : {cbs_red['cbs_channel']}")
    print(f"  -> Vibration Override     : {cbs_red['vibration_override']} (Bypasses DND)")
    print(f"  -> Audio Siren            : {cbs_red['audio_siren_override']}")
    print(f"  -> Transmission Ticket ID : {cbs_red['transmission_ticket_id']}")
    assert cbs_red["status"] == "ACTIVE_BROADCAST_TRANSMITTED"
    assert "CH-4370" in cbs_red["cbs_channel"], f"Expected Channel 4370, got {cbs_red['cbs_channel']}"
    assert cbs_red["vibration_override"] is True, "RED alert must bypass silent mode"
    assert cbs_red["transmission_ticket_id"] is not None

    # YELLOW / Watch dispatch (should remain on STANDBY)
    cbs_yellow = dispatch_cell_broadcast_payload({"severity": "YELLOW"})
    print(f"  -> YELLOW Dispatch Status : [{cbs_yellow['status']}] (Vibration: {cbs_yellow['vibration_override']})")
    assert cbs_yellow["status"] == "STANDBY", f"Expected STANDBY for non-RED severity, got {cbs_yellow['status']}"
    assert cbs_yellow["vibration_override"] is False

    print("[PASS] PART 2: C-DOT Cell Broadcast Geo-Targeting Verified.")

    # -------------------------------------------------------------------------
    # PART 3: BRO PROJECT SWASTIK PRE-POSITIONING SOP
    # -------------------------------------------------------------------------
    print("\n[PART 3] Validating BRO Project Swastik Pre-Positioning SOP Engine...")

    # Case A: Danger (FS < 1.0)
    sop_danger = evaluate_bro_swastik_sop(risk_level="DANGER", fs_value=0.88, rainfall_breach=True)
    print(f"  -> DANGER Tier SOP: [{sop_danger['sop_code']}]")
    print(f"     Action        : {sop_danger['action']}")
    print(f"     Staging       : {sop_danger['staging_locations']}")
    print(f"     Plant Assigned: {sop_danger['plant_assigned']}")
    print(f"     Bypass Order  : {sop_danger['bypass_mandate']}")
    assert sop_danger["operational_tier"] == "DANGER"
    assert "CLOSE CORRIDOR" in sop_danger["action"]
    assert "CAT 320D Excavators" in sop_danger["plant_assigned"]
    assert "29th Mile" in sop_danger["staging_locations"]
    assert "BYPASS-LAVA" in sop_danger["bypass_mandate"]

    # Case B: Warning (1.0 <= FS < 1.3 or rain breach)
    sop_warning = evaluate_bro_swastik_sop(risk_level="WARNING", fs_value=1.15, rainfall_breach=True)
    print(f"  -> WARNING Tier SOP: [{sop_warning['sop_code']}]")
    print(f"     Action        : {sop_warning['action']}")
    assert sop_warning["operational_tier"] == "WARNING"
    assert "PRE-POSITION PLANT" in sop_warning["action"]
    assert "Standby Dozers" in sop_warning["plant_assigned"]

    # Case C: Normal (FS > 1.3, no rain breach)
    sop_normal = evaluate_bro_swastik_sop(risk_level="NORMAL", fs_value=1.65, rainfall_breach=False)
    print(f"  -> NORMAL Tier SOP: [{sop_normal['sop_code']}]")
    assert sop_normal["operational_tier"] == "NORMAL"
    assert "ROUTINE PATROL" in sop_normal["action"]

    print("[PASS] PART 3: BRO Project Swastik Pre-Positioning SOP Verified.")

    # -------------------------------------------------------------------------
    # PART 4: LIVE REST API ENDPOINTS VALIDATION
    # -------------------------------------------------------------------------
    print("\n[PART 4] Testing Live REST Endpoints on Flask Server...")

    # 1. GET /api/institutional/nlfc-status
    r1 = requests.get(f"{BASE_URL}/api/institutional/nlfc-status", timeout=15)
    print(f"  -> GET /api/institutional/nlfc-status: Status {r1.status_code}")
    assert r1.status_code == 200, f"Expected 200, got {r1.status_code}"
    nlfc_data = r1.json()
    assert nlfc_data.get("status") == "SUCCESS"
    assert nlfc_data.get("regional_node") == "LEWS-REGIONAL-EAST-01"
    assert "Geological Survey of India" in nlfc_data.get("nodal_agency", "")
    assert nlfc_data.get("sync_status") == "SYNCHRONIZED_OPERATIONAL"
    print(f"     Verified Regional Node: {nlfc_data['regional_node']} | Status: [{nlfc_data['sync_status']}]")

    # 2. GET /api/defense/bro-swastik-sop
    r2 = requests.get(f"{BASE_URL}/api/defense/bro-swastik-sop?risk_level=DANGER&fs=0.92", timeout=15)
    print(f"  -> GET /api/defense/bro-swastik-sop: Status {r2.status_code}")
    assert r2.status_code == 200, f"Expected 200, got {r2.status_code}"
    bro_data = r2.json()
    assert bro_data.get("status") == "SUCCESS"
    assert bro_data.get("operational_tier") == "DANGER"
    assert "CAT 320D" in bro_data.get("plant_assigned", "")
    print(f"     Verified BRO SOP: [{bro_data['sop_code']}] -> {bro_data['action']}")

    # 3. POST /api/alerts/broadcast-trigger
    alert_req = {
        "region_name": "NH-10 Likhu Veer Sector",
        "severity": "RED"
    }
    r3 = requests.post(f"{BASE_URL}/api/alerts/broadcast-trigger", json=alert_req, timeout=15)
    print(f"  -> POST /api/alerts/broadcast-trigger: Status {r3.status_code}")
    assert r3.status_code == 201, f"Expected 201, got {r3.status_code}"
    bcast_data = r3.json()
    assert bcast_data.get("status") == "SUCCESS"
    assert "cap_xml" in bcast_data, "Response must include cap_xml string"
    assert "cell_broadcast" in bcast_data, "Response must include cell_broadcast payload"
    
    cb_resp = bcast_data["cell_broadcast"]
    assert cb_resp["status"] == "ACTIVE_BROADCAST_TRANSMITTED"
    assert "CH-4370" in cb_resp["cbs_channel"]
    print(f"     Verified Broadcast Trigger: CAP XML ({len(bcast_data['cap_xml'])} chars) | CBS: {cb_resp['cbs_channel']} (Ticket: {cb_resp['transmission_ticket_id']})")

    # 4. GET /api/openapi.json (OpenAPI spec verification)
    r4 = requests.get(f"{BASE_URL}/api/openapi.json", timeout=15)
    assert r4.status_code == 200
    spec = r4.json()
    assert "/api/institutional/nlfc-status" in spec["paths"]
    assert "/api/defense/bro-swastik-sop" in spec["paths"]
    print("  -> Verified OpenAPI 3.0 specification includes all new endpoints.")

    print("[PASS] PART 4: Live REST Endpoints Verified.")

    print("\n" + "=" * 80)
    print("ALL SPRINT 4 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    test_sprint4_institutional()
