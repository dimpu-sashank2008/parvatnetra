"""
tests/test_pahad_phase3.py
===========================
PAHAD Phase 3 Unit & Integration Tests
----------------------------------------
Tests:
  01  CAPAlertGenerator creates valid XML containing OASIS CAP v1.2 namespace (urn:oasis:names:tc:emergency:cap:1.2)
  02  CAP XML contains all mandatory elements: identifier, sender, sent, status, msgType, scope, info, area, polygon
  03  CAP XML polygon formatting properly formats coords and enforces closed polygon
  04  NERMultilingualSynthesizer outputs valid localized strings for all 9 NER dialects without missing keys
  05  All 9 NER dialect SMS alerts strictly respect character limits (< 160 chars)
  06  NERMultilingualSynthesizer includes English and Hindi baselines and rich push payloads
  07  POST /api/pahad/generate-cap -> HTTP 200 + valid JSON + CAP XML
  08  POST /api/pahad/multilingual-alert -> HTTP 200 + valid JSON + localized strings
  09  POST /api/pahad/generate-cap with missing fields -> HTTP 400
  10  POST /api/pahad/multilingual-alert with missing fields -> HTTP 400
"""

import sys
import os
import unittest
import json
import xml.etree.ElementTree as ET

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pahad_cap import CAPAlertGenerator, CAP_NAMESPACE
from engine.pahad_multilingual import (
    NERMultilingualSynthesizer,
    NER_DIALECT_CODES,
    ALL_SUPPORTED_LANGUAGES,
)
from app import app


class TestCAPAlertGenerator(unittest.TestCase):
    """Tests 01, 02, 03: OASIS CAP v1.2 XML generation tests."""

    def setUp(self):
        self.generator = CAPAlertGenerator()
        self.sample_payload = {
            "sector_id": "SK-NH10-KM48",
            "sector_name": "NH-10 Km 48 (29th Mile Sector)",
            "cri_score": 88.5,
            "band": "EXTREME",
            "coordinates_polygon": [
                [27.3300, 88.6100],
                [27.3400, 88.6100],
                [27.3400, 88.6200],
                [27.3300, 88.6200],
                [27.3300, 88.6100],
            ],
        }

    def test_01_cap_xml_namespace_and_validity(self):
        """CAPAlertGenerator creates valid XML containing the OASIS CAP v1.2 namespace."""
        xml_str = self.generator.build_cap_xml(self.sample_payload)
        self.assertIsInstance(xml_str, str)
        self.assertIn(CAP_NAMESPACE, xml_str)
        self.assertIn('xmlns="urn:oasis:names:tc:emergency:cap:1.2"', xml_str)

        # Parse with standard XML parser to guarantee well-formedness
        root = ET.fromstring(xml_str.encode("utf-8"))
        self.assertEqual(root.tag, f"{{{CAP_NAMESPACE}}}alert")
        print("\n[PASS] Test 01: OASIS CAP v1.2 namespace and well-formed XML verified.")

    def test_02_mandatory_cap_elements_present(self):
        """CAP XML contains mandatory elements: identifier, sender, sent, status, msgType, scope, info, area, polygon."""
        xml_str = self.generator.build_cap_xml(self.sample_payload)
        root = ET.fromstring(xml_str.encode("utf-8"))
        ns = {"cap": CAP_NAMESPACE}

        mandatory_top_level = [
            "identifier", "sender", "sent", "status", "msgType", "scope", "info"
        ]
        for tag in mandatory_top_level:
            elem = root.find(f"cap:{tag}", ns)
            self.assertIsNotNone(elem, f"Mandatory CAP tag missing: <{tag}>")
            self.assertTrue(len(elem.text or elem) > 0, f"Tag <{tag}> is empty")

        # Verify <info> child tags
        info = root.find("cap:info", ns)
        self.assertIsNotNone(info)
        for tag in ["category", "event", "urgency", "severity", "certainty", "area"]:
            elem = info.find(f"cap:{tag}", ns)
            self.assertIsNotNone(elem, f"Mandatory <info> tag missing: <{tag}>")

        # Verify <area> child tags
        area = info.find("cap:area", ns)
        self.assertIsNotNone(area)
        for tag in ["areaDesc", "polygon"]:
            elem = area.find(f"cap:{tag}", ns)
            self.assertIsNotNone(elem, f"Mandatory <area> tag missing: <{tag}>")
            self.assertTrue(elem.text and len(elem.text.strip()) > 0)

        # Check expected value mappings
        self.assertEqual(info.find("cap:severity", ns).text, "Extreme")
        self.assertEqual(info.find("cap:urgency", ns).text, "Immediate")
        print("\n[PASS] Test 02: All mandatory CAP v1.2 XML elements present and validated.")

    def test_03_polygon_formatting_closed_loop(self):
        """Polygon coords format as space-delimited lat,lon pairs with closed loop."""
        # Unclosed 4-point rectangle
        unclosed = [[27.33, 88.61], [27.34, 88.61], [27.34, 88.62], [27.33, 88.62]]
        poly_str = self.generator.format_polygon_coords(unclosed)
        points = poly_str.split(" ")
        self.assertEqual(len(points), 5, "Unclosed 4 points must become 5 to close loop")
        self.assertEqual(points[0], points[-1], "First and last polygon points must match")
        for pt in points:
            lat, lon = pt.split(",")
            self.assertGreater(float(lat), 0.0)
            self.assertGreater(float(lon), 0.0)
        print("\n[PASS] Test 03: Polygon formatting and closed loop validation confirmed.")


class TestNERMultilingualSynthesizer(unittest.TestCase):
    """Tests 04, 05, 06: NE-BERT Multilingual Alert Synthesis tests."""

    def setUp(self):
        self.synth = NERMultilingualSynthesizer()
        self.severity = "CRITICAL"
        self.sector = "NH-10 Km 48 (29th Mile Sector)"
        self.detour = "Detour via Kalimpong-Mungpoo route"

    def test_04_all_9_ner_dialects_present_without_missing_keys(self):
        """NERMultilingualSynthesizer outputs valid localized strings for all 9 NER dialects without missing keys."""
        res = self.synth.translate_alert(
            severity=self.severity,
            sector_name=self.sector,
            detour_info=self.detour,
        )
        self.assertEqual(res["status"], "SUCCESS")

        for code in NER_DIALECT_CODES:
            self.assertIn(code, res, f"NER dialect key missing from root: {code}")
            self.assertIn(code, res["translations"], f"NER dialect missing from translations: {code}")
            lang_obj = res[code]
            self.assertIn("sms", lang_obj)
            self.assertIn("push_title", lang_obj)
            self.assertIn("push_body", lang_obj)
            self.assertIn("voice_script", lang_obj)
            self.assertIn("rich_push", lang_obj)
            self.assertTrue(len(lang_obj["sms"]) > 10, f"SMS too short for {code}")
            self.assertTrue(len(lang_obj["push_title"]) > 5, f"Title too short for {code}")

        print(f"\n[PASS] Test 04: All 9 NER dialects present without missing keys: {NER_DIALECT_CODES}")

    def test_05_all_ner_sms_under_160_characters(self):
        """All 9 NER dialect SMS alerts strictly respect character limits (< 160 chars)."""
        res = self.synth.translate_alert(
            severity=self.severity,
            sector_name=self.sector,
            detour_info=self.detour,
        )
        for code in NER_DIALECT_CODES:
            sms = res[code]["sms"]
            self.assertLess(
                len(sms),
                160,
                f"SMS for dialect '{code}' ({len(sms)} chars) exceeded 160 char limit: {sms}"
            )
        print("\n[PASS] Test 05: All 9 NER dialect SMS messages strictly < 160 characters.")

    def test_06_baselines_and_rich_push_present(self):
        """English and Hindi baselines and rich push payloads are correctly synthesized."""
        res = self.synth.translate_alert(
            severity=self.severity,
            sector_name=self.sector,
            detour_info=self.detour,
        )
        for base in ("en", "hi"):
            self.assertIn(base, res)
            self.assertIn("rich_push", res[base])
            rp = res[base]["rich_push"]
            self.assertEqual(rp["action"], "EVACUATE")
            self.assertEqual(rp["severity"], "CRITICAL")
        print("\n[PASS] Test 06: English/Hindi baselines and rich push payloads verified.")


class TestPhase3Endpoints(unittest.TestCase):
    """Tests 07, 08, 09, 10: Flask API endpoints integration tests."""

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_07_post_generate_cap_success(self):
        """POST /api/pahad/generate-cap -> HTTP 200 + valid JSON + CAP XML string."""
        payload = {
            "sector_id": "SK-NH10-KM48",
            "sector_name": "NH-10 Km 48 (29th Mile Sector)",
            "cri_score": 85.2,
            "band": "EXTREME",
            "coordinates_polygon": [
                [27.33, 88.61],
                [27.34, 88.61],
                [27.34, 88.62],
                [27.33, 88.62],
                [27.33, 88.61],
            ],
        }
        resp = self.client.post(
            "/api/pahad/generate-cap",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["severity"], "Extreme")
        self.assertIn("cap_xml", data)
        self.assertIn(CAP_NAMESPACE, data["cap_xml"])
        self.assertIn("<identifier>", data["cap_xml"])
        self.assertIn("<polygon>", data["cap_xml"])

        # Parse CAP XML string from response to ensure it parses cleanly
        root = ET.fromstring(data["cap_xml"].encode("utf-8"))
        self.assertEqual(root.tag, f"{{{CAP_NAMESPACE}}}alert")
        print("\n[PASS] Test 07: /api/pahad/generate-cap -> 200 OK with valid CAP-XML.")

    def test_08_post_multilingual_alert_success(self):
        """POST /api/pahad/multilingual-alert -> HTTP 200 + valid JSON + localized strings."""
        payload = {
            "severity": "CRITICAL",
            "sector_name": "NH-10 Km 48",
            "detour_info": "Use Kalimpong-Mungpoo route",
        }
        resp = self.client.post(
            "/api/pahad/multilingual-alert",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "SUCCESS")

        # Verify all 9 NER dialects exist in response
        for code in NER_DIALECT_CODES:
            self.assertIn(code, data)
            self.assertIn("sms", data[code])
            self.assertLess(len(data[code]["sms"]), 160)

        self.assertIn("en", data)
        self.assertIn("hi", data)
        print("\n[PASS] Test 08: /api/pahad/multilingual-alert -> 200 OK with 9 NER dialects.")

    def test_09_generate_cap_missing_fields_returns_400(self):
        """POST /api/pahad/generate-cap without required sector identifier -> HTTP 400."""
        resp = self.client.post(
            "/api/pahad/generate-cap",
            data=json.dumps({"band": "EXTREME"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "ERROR")
        print("\n[PASS] Test 09: /api/pahad/generate-cap missing fields returns HTTP 400.")

    def test_10_multilingual_alert_missing_fields_returns_400(self):
        """POST /api/pahad/multilingual-alert without required fields -> HTTP 400."""
        resp = self.client.post(
            "/api/pahad/multilingual-alert",
            data=json.dumps({"severity": "CRITICAL"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "ERROR")
        print("\n[PASS] Test 10: /api/pahad/multilingual-alert missing fields returns HTTP 400.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
